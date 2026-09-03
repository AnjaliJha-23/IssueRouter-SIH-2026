from transformers import pipeline as hf_pipeline
from pipeline.config import DOMAINS, SUBDOMAIN_MAP, CLASSIFICATION_THRESHOLDS

# Load once at module level — never reload during demo
_classifier = None
MODEL_VERSION = "facebook/bart-large-mnli"

def load_classifier():
    global _classifier
    if _classifier is None:
        print("[classification] Loading BART zero-shot model...")
        _classifier = hf_pipeline(
            "zero-shot-classification",
            model=MODEL_VERSION
        )
        print("[classification] Model loaded.")

def classify(text: str) -> dict:
    """
    Returns dict matching the pipeline output contract.
    """
    if _classifier is None:
        load_classifier()

    # Top-level domain classification
    result = _classifier(text, candidate_labels=DOMAINS)
    
    top_domain = result["labels"][0]
    top_confidence = result["scores"][0]
    
    domain_scores = {label: round(score, 3) for label, score in zip(result["labels"], result["scores"])}
    
    subdomain = None
    # Subdomain second-pass if confidence clears threshold
    if top_confidence >= CLASSIFICATION_THRESHOLDS["top_domain_confidence_min"] and top_domain in SUBDOMAIN_MAP:
        sub_labels = SUBDOMAIN_MAP[top_domain]
        sub_result = _classifier(text, candidate_labels=sub_labels)
        sub_confidence = sub_result["scores"][0]
        if sub_confidence >= CLASSIFICATION_THRESHOLDS["subdomain_confidence_min"]:
            subdomain = sub_result["labels"][0]
            
    return {
        "domain": top_domain,
        "subdomain": subdomain,
        "domain_scores": domain_scores,
        "model_version": MODEL_VERSION
    }