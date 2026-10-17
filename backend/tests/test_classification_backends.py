"""
Backend-selection tests for the domain classifier.

``backend/conftest.py`` pins ``CLASSIFIER_BACKEND=keyword`` and clears
``TYPESAFE_API_KEY`` unless ``JEV_LIVE_TEST`` is set, so this module runs fully
offline and deterministically. The live Jev test at the bottom is opt-in.
"""

import os

import pytest

from pipeline import jev_client
from pipeline.classification import CLASSIFIER_BACKEND, classify, load_classifier
from pipeline.config import DOMAINS
from pipeline.keyword_classifier import classify as keyword_classify

# The real citizen corpus is transliterated Hindi/English (Hinglish).
DOMAIN_SAMPLES = [
    ("Water & Sanitation", "Gaon me paani nahi aa raha, handpump kharab hai aur nali ka paani sadak par"),
    ("Healthcare", "Namkum PHC me doctor nahi hai aur dawai khatam ho gayi hai"),
    ("Education", "School me shikshak nahi hai, bachchon ko kitab bhi nahi mili"),
    ("Energy", "Bijli 3 din se nahi hai, transformer jal gaya hai"),
    ("Infrastructure/Transport", "Sadak me bade gaddhe hain, bus bhi nahi chalti"),
    ("Public Administration", "Ration card nahi bana, panchayat me babu paisa maang raha hai"),
    ("Rural Livelihoods", "Kheti ke liye khad nahi mili, mgnrega ki mazdoori bhi pending hai"),
    ("Environment", "Nadi me pradushan hai, illegal mining se paani ganda ho gaya"),
    ("Accessibility", "Divyang ke liye ramp nahi hai school me"),
]


class TestKeywordBackend:
    @pytest.mark.parametrize("expected,text", DOMAIN_SAMPLES)
    def test_hinglish_samples_route_to_expected_domain(self, expected, text):
        assert keyword_classify(text)["domain"] == expected

    def test_contract_shape(self):
        res = keyword_classify(DOMAIN_SAMPLES[0][1])
        assert set(("domain", "subdomain", "domain_scores", "model_version")).issubset(res)
        assert res["domain"] in DOMAINS
        assert isinstance(res["domain_scores"], dict)
        assert isinstance(res["model_version"], str)
        assert abs(sum(res["domain_scores"].values()) - 1.0) < 0.05

    def test_subdomain_only_for_domains_that_have_one(self):
        res = keyword_classify("Namkum PHC me doctor nahi hai, staff ki kami hai")
        assert res["domain"] == "Healthcare"
        assert res["subdomain"] == "PHC Staffing"

    def test_empty_and_gibberish_text_do_not_raise(self):
        for text in ("", "   ", "zzzz qqqq xxxx"):
            res = keyword_classify(text)
            assert res["domain"] in DOMAINS


class TestPublicContract:
    """`classify()` must always return the pipeline contract, whatever the backend."""

    def test_classify_contract(self):
        res = classify("Severe shortage of clean drinking water and broken handpumps in rural village")
        assert res["domain"] in DOMAINS
        assert isinstance(res["domain_scores"], dict)
        assert res["model_version"]

    def test_empty_text_does_not_raise(self):
        assert classify("")["domain"] in DOMAINS


class TestJevFallback:
    """The Jev backend degrades gracefully instead of raising."""

    def test_jev_client_reports_missing_key(self, monkeypatch):
        monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
        assert jev_client.is_configured() is False

    def test_jev_classify_returns_none_without_key(self, monkeypatch):
        # conftest already cleared the key; be explicit anyway.
        monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
        from pipeline.classification import _classify_jev

        assert _classify_jev("Namkum PHC me doctor nahi hai") is None

    def test_classify_falls_back_to_keyword_when_jev_unavailable(self, monkeypatch):
        monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
        res = classify("Gaon me paani nahi aa raha, handpump kharab hai")
        assert res["domain"] == "Water & Sanitation"
        assert res["model_version"] == "keyword-lexicon-v1"


class TestModelLoading:
    """The whole point of the migration: no BART weights for non-transformers backends."""

    def test_load_classifier_is_a_noop_unless_transformers_selected(self):
        if CLASSIFIER_BACKEND == "transformers":
            pytest.skip("transformers backend selected; BART is expected to load")
        from pipeline import classification

        classification._classifier = None
        load_classifier()
        assert classification._classifier is None, "BART must not be loaded for this backend"


# ---------------------------------------------------------------------------
# Opt-in live test: JEV_LIVE_TEST=1 python -m pytest tests/test_classification_backends.py
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    os.getenv("JEV_LIVE_TEST", "").strip().lower() not in ("1", "true", "yes"),
    reason="set JEV_LIVE_TEST=1 (with a real TYPESAFE_API_KEY) to run live Jev tests",
)
class TestJevLive:
    def test_live_domain_decision(self):
        from dotenv import load_dotenv

        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        if not jev_client.is_configured():
            pytest.skip("TYPESAFE_API_KEY not set")

        res = jev_client.ask(
            "Namkum Ranchi me PHC me doctor nahi hai, dawai khatam ho gayi hai",
            {
                "domain": {
                    "type": "choice",
                    "instructions": "Which single government domain does this citizen complaint belong to?",
                    "criteria": {d: None for d in DOMAINS},
                }
            },
        )
        assert res["answers"]["domain"]["choice"] in DOMAINS
