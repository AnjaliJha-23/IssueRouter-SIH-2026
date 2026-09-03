"""
Configuration file for the NLP Pipeline.
Centralizes all tunables: labels, thresholds, weights, and rules.
"""

# Classification Configuration
DOMAINS = [
    "Healthcare",
    "Education",
    "Water & Sanitation",
    "Environment",
    "Energy",
    "Urban Development",
    "Accessibility",
    "Public Administration",
    "Rural Livelihoods",
    "Infrastructure/Transport"
]

SUBDOMAIN_MAP = {
    "Healthcare": ["Rural Access", "PHC Staffing", "Diagnostics", "Maternal Health", "Waterborne Disease"],
    "Education": ["Primary Education", "Higher Education", "Digital Divide", "Teacher Shortage", "Infrastructure"],
    "Water & Sanitation": ["Drinking Water", "Sewage", "Waste Management", "Pollution"],
}

CLASSIFICATION_THRESHOLDS = {
    "top_domain_confidence_min": 0.55,
    "subdomain_confidence_min": 0.40
}

# Deduplication / Clustering Configuration
DEDUP_THRESHOLDS = {
    "auto_link": 0.80,         # >= this score auto-links evidence to challenge
    "flag_related": 0.60       # >= this score flags as a potential duplicate
}

# Priority Scoring Configuration
DOMAIN_SEVERITY = {
    "Law and Order": 0.95,
    "Healthcare": 0.90,
    "Water & Sanitation": 0.85,
    "Infrastructure/Transport": 0.80,
    "Energy": 0.75,
    "Education": 0.70,
    "Rural Livelihoods": 0.70,
    "Environment": 0.65,
    "Urban Development": 0.60,
    "Accessibility": 0.60,
    "Public Administration": 0.50
}

PRIORITY_WEIGHTS = {
    "severity": 30,
    "volume": 25,
    "confidence": 25,
    "trend": 20
}

TREND_MULTIPLIERS = {
    "increasing": 1.0,
    "stable": 0.5,
    "decreasing": 0.2
}
