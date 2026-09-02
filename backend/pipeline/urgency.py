URGENCY_KEYWORDS = {
    "critical": [
        "fire", "gas leak", "collapse", "explosion", "casualty",
        "flooding", "accident", "electric shock", "sewage overflow",
        "emergency", "dead", "death", "serious injury"
    ],
    "high": [
        "pothole", "broken", "damaged", "water cut", "power cut",
        "stray dog", "bite", "garbage overflow", "road damage",
        "no water", "no electricity", "burst pipe", "dangerous"
    ],
    "medium": [
        "maintenance", "leaking", "noise", "missing", "dirty",
        "complaint", "problem", "issue", "bad condition"
    ],
    "low": [
        "suggestion", "painting", "trimming", "minor", "request",
        "feedback", "improvement"
    ]
}

URGENCY_WEIGHTS = {
    "critical": 200,
    "high": 100,
    "medium": 40,
    "low": 10
}

def score_urgency(text: str, retweets: int = 0) -> str:
    """
    Returns urgency level: "critical", "high", "medium", or "low"
    Boosts urgency based on retweet count (social signal).
    """
    text_lower = text.lower()
    base = "medium"  # default

    for level in ["critical", "high", "medium", "low"]:
        if any(kw in text_lower for kw in URGENCY_KEYWORDS[level]):
            base = level
            break

    # Social signal boost
    if retweets > 500 and base == "high":
        base = "critical"
    elif retweets > 100 and base == "medium":
        base = "high"

    return base

def get_urgency_weight(urgency: str) -> int:
    return URGENCY_WEIGHTS.get(urgency, 40)