from transformers import pipeline as hf_pipeline

# Load once at module level — never reload during demo
_classifier = None

def load_classifier():
    global _classifier
    if _classifier is None:
        print("[classifier] Loading BART zero-shot model...")
        _classifier = hf_pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        print("[classifier] Model loaded.")

LABELS = [
    "Infrastructure",
    "Sanitation",
    "Healthcare",
    "Utilities",
    "Education",
    "Law and Order",
    "Environment"
]

def classify(text: str) -> tuple[str, float]:
    """
    Returns (category, confidence_score)
    Example: ("Infrastructure", 0.87)
    """
    if _classifier is None:
        load_classifier()

    result = _classifier(text, candidate_labels=LABELS)
    category = result["labels"][0]
    confidence = round(result["scores"][0], 3)
    return category, confidence