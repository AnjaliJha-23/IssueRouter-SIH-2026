from pipeline.config import DOMAIN_SEVERITY, PRIORITY_WEIGHTS, TREND_MULTIPLIERS

def calculate_priority(
    domain: str,
    evidence_volume: int,
    evidence_confidence: float,
    trend: str
) -> dict:
    """
    Calculates priority score based on weighted factors.
    Returns the required priority contract dictionary.
    """
    severity = DOMAIN_SEVERITY.get(domain, 0.5)
    
    # Volume normalization (cap at 100 items for max factor)
    volume_factor = min(evidence_volume / 100.0, 1.0)
    
    trend_factor = TREND_MULTIPLIERS.get(trend, 0.5)
    
    # Weighted Score (out of 100)
    score = (
        (severity * PRIORITY_WEIGHTS["severity"]) + 
        (volume_factor * PRIORITY_WEIGHTS["volume"]) + 
        (evidence_confidence * PRIORITY_WEIGHTS["confidence"]) + 
        (trend_factor * PRIORITY_WEIGHTS["trend"])
    )
    
    priority_score = int(round(score))
    
    explanation = (
        f"Priority {priority_score}/100: "
        f"Domain severity ({domain}) is {severity:.2f}. "
        f"Backed by {evidence_volume} evidence items (confidence {evidence_confidence:.2f}). "
        f"Report trend is {trend}."
    )
    
    return {
        "priority_score": priority_score,
        "priority_factors": {
            "severity": severity,
            "evidence_volume": volume_factor,
            "confidence": evidence_confidence,
            "trend": trend_factor
        },
        "evidence_confidence": evidence_confidence,
        "trend": trend,
        "explanation": explanation
    }