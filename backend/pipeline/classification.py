"""
Domain and subdomain classification for the IssueRouter NLP pipeline.

One of three interchangeable backends is selected with the ``CLASSIFIER_BACKEND``
environment variable:

``jev`` (default)
    TypeSafe "System One" (Jev) hosted decision model. Calibrated probabilities
    from a single HTTP call. Falls back to ``keyword`` if ``TYPESAFE_API_KEY``
    is missing or the call fails, so the pipeline never hard-fails on a
    third-party dependency.

``transformers``
    Local ``facebook/bart-large-mnli`` zero-shot pipeline (legacy). Holds ~1.6 GB
    of weights in RAM, so it is imported and loaded only when this backend is
    explicitly selected.

``keyword``
    Deterministic lexicon matcher (:mod:`pipeline.keyword_classifier`). No
    network, no model weights — the offline safety net.

All three return the same contract::

    {
      "domain":        str,              # one of config.DOMAINS
      "subdomain":     str | None,       # one of config.SUBDOMAIN_MAP[domain]
      "domain_scores": {label: float},   # probabilities, sum ~= 1
      "model_version": str,              # e.g. "jev-1.13.0"
      # additive extras, not yet consumed by priority scoring:
      "severity":      float | None,     # 0..1, Jev Score or domain baseline
      "urgency":       float | None,     # 0..1, Jev Noul
      "confidence":    float | None,     # Jev Choice confidence
    }
"""

import logging
import os

from pipeline import jev_client
from pipeline.keyword_classifier import classify as keyword_classify
from pipeline.config import (
    CLASSIFICATION_THRESHOLDS,
    DOMAINS,
    DOMAIN_CRITERIA,
    DOMAIN_SEVERITY,
    SEVERITY_LEVELS,
    SUBDOMAIN_MAP,
)

logger = logging.getLogger(__name__)

# --- Backend selection -------------------------------------------------------
CLASSIFIER_BACKEND = os.getenv("CLASSIFIER_BACKEND", "jev").strip().lower()

# Legacy local model, only used by the "transformers" backend.
TRANSFORMERS_MODEL = os.getenv("CLASSIFICATION_MODEL", "facebook/bart-large-mnli")
MODEL_VERSION = TRANSFORMERS_MODEL  # kept for backward compatibility

_classifier = None  # lazily loaded local zero-shot pipeline


def load_classifier():
    """Warm the local zero-shot model.

    This is a no-op unless the ``transformers`` backend is selected. That
    no-op is what keeps ~1.6 GB of BART weights off a 1.75 GB App Service B1
    instance when the backend is ``jev`` or ``keyword``.
    """
    global _classifier
    if CLASSIFIER_BACKEND != "transformers":
        return
    if _classifier is None:
        # Imported here rather than at module scope so torch/transformers are
        # never imported for the jev or keyword backends.
        from transformers import pipeline as hf_pipeline

        print("[classification] Loading BART zero-shot model...")
        _classifier = hf_pipeline("zero-shot-classification", model=TRANSFORMERS_MODEL)
        print("[classification] Model loaded.")


def classify(text: str) -> dict:
    """Classify free text into a domain, and a subdomain when confident."""
    if CLASSIFIER_BACKEND == "transformers":
        return _classify_transformers(text)

    if CLASSIFIER_BACKEND == "jev":
        result = _classify_jev(text)
        if result is not None:
            return result
        logger.warning("[classification] Jev unavailable - using keyword fallback.")
    elif CLASSIFIER_BACKEND != "keyword":
        logger.warning(
            "[classification] Unknown CLASSIFIER_BACKEND=%r - using keyword fallback.",
            CLASSIFIER_BACKEND,
        )

    return keyword_classify(text)


# ---------------------------------------------------------------------------
# Backend: Jev (TypeSafe System One)
# ---------------------------------------------------------------------------
def _classify_jev(text: str) -> dict | None:
    """One Jev call for domain/severity/urgency, plus a gated subdomain call.

    Returns ``None`` (rather than raising) on any problem so the caller can
    fall back to the deterministic keyword classifier.
    """
    if not jev_client.is_configured():
        return None

    questions = {
        "domain": {
            "type": "choice",
            "instructions": "Which single government domain does this citizen complaint belong to?",
            "criteria": DOMAIN_CRITERIA,
        },
        "severity": {
            "type": "score",
            "instructions": "How severe is the impact of this issue on citizens?",
            "criteria": SEVERITY_LEVELS,
        },
        "urgency": {
            "type": "noul",
            "instructions": "Does this complaint need action within 24 hours?",
            "criteria": {
                "true": "Time-sensitive: risk to life, health or safety, or an ongoing outage",
                "false": "No immediate time pressure",
            },
        },
    }

    try:
        response = jev_client.ask(text, questions)
    except Exception as exc:  # noqa: BLE001 - any failure must fall back
        logger.warning("[classification] Jev call failed: %s", exc)
        return None

    answers = response.get("answers") or {}
    domain_answer = answers.get("domain") or {}
    probabilities = domain_answer.get("probabilities") or {}
    domain = domain_answer.get("choice")
    confidence = domain_answer.get("confidence")

    # Only trust an answer that matches our own label set.
    if domain not in DOMAINS:
        logger.warning("[classification] Jev returned unknown domain %r.", domain)
        return None

    return {
        "domain": domain,
        "subdomain": _jev_subdomain(text, domain, confidence),
        "domain_scores": {d: round(float(probabilities.get(d, 0.0)), 3) for d in DOMAINS},
        "model_version": response.get("model") or jev_client.default_model(),
        "severity": _jev_severity(answers.get("severity")),
        "urgency": _jev_noul(answers.get("urgency")),
        "confidence": confidence,
    }


def _jev_subdomain(text: str, domain: str, domain_confidence) -> str | None:
    """Second Jev call, only for domains that have a subdomain taxonomy.

    Skipped when the domain itself is not confident, so we never ask a
    follow-up question about a domain we are unsure of. A failure here is not
    fatal: the domain answer is still usable and the subdomain stays None.
    """
    labels = SUBDOMAIN_MAP.get(domain)
    if not labels:
        return None

    if (
        domain_confidence is not None
        and domain_confidence < CLASSIFICATION_THRESHOLDS["top_domain_confidence_min"]
    ):
        return None

    questions = {
        "subdomain": {
            "type": "choice",
            "instructions": f"Within the {domain} domain, which specific sub-issue is described?",
            "criteria": {label: None for label in labels},
        }
    }

    try:
        response = jev_client.ask(text, questions)
    except Exception as exc:  # noqa: BLE001 - subdomain is optional
        logger.warning("[classification] Jev subdomain call failed: %s", exc)
        return None

    answer = (response.get("answers") or {}).get("subdomain") or {}
    subdomain = answer.get("choice")
    if subdomain not in labels:
        return None
    if (answer.get("confidence") or 0.0) < CLASSIFICATION_THRESHOLDS["subdomain_confidence_min"]:
        return None
    return subdomain


def _jev_severity(answer) -> float | None:
    """Convert a Jev Score answer into a 0..1 severity, or None."""
    if not answer or answer.get("score") is None:
        return None
    try:
        raw = float(answer["score"])
    except (TypeError, ValueError):
        return None
    levels = len(SEVERITY_LEVELS)
    if levels < 2:
        return None
    return round(min(max(raw / (levels - 1), 0.0), 1.0), 3)


def _jev_noul(answer) -> float | None:
    """Extract a Noul probability, or None."""
    if not answer or answer.get("noul") is None:
        return None
    try:
        return round(float(answer["noul"]), 3)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Backend: local transformers zero-shot pipeline (legacy)
# ---------------------------------------------------------------------------
def _classify_transformers(text: str) -> dict:
    if _classifier is None:
        load_classifier()

    result = _classifier(text, candidate_labels=DOMAINS)

    top_domain = result["labels"][0]
    top_confidence = result["scores"][0]
    domain_scores = {label: round(score, 3) for label, score in zip(result["labels"], result["scores"])}

    subdomain = None
    if top_confidence >= CLASSIFICATION_THRESHOLDS["top_domain_confidence_min"] and top_domain in SUBDOMAIN_MAP:
        sub_result = _classifier(text, candidate_labels=SUBDOMAIN_MAP[top_domain])
        if sub_result["scores"][0] >= CLASSIFICATION_THRESHOLDS["subdomain_confidence_min"]:
            subdomain = sub_result["labels"][0]

    return {
        "domain": top_domain,
        "subdomain": subdomain,
        "domain_scores": domain_scores,
        "model_version": TRANSFORMERS_MODEL,
        "severity": DOMAIN_SEVERITY.get(top_domain, 0.5),
        "urgency": None,
        "confidence": round(top_confidence, 3),
    }
