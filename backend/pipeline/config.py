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

# Decision-Model (TypeSafe JEV) Rubrics
# Human-readable criteria attached to each domain option. These disambiguate
# domains that share vocabulary (e.g. "water" in Healthcare vs Water &
# Sanitation) and measurably improve Jev's Choice accuracy. Keys must stay in
# sync with DOMAINS above.
DOMAIN_CRITERIA = {
    "Healthcare": "Hospitals, health centres, PHC/CHC, doctors, nurses, medicines, ambulances, disease and treatment",
    "Education": "Schools, colleges, universities, teachers, students, exams, scholarships, mid-day meals",
    "Water & Sanitation": "Drinking water, taps, handpumps, wells, pipelines, toilets, sewage, drains, garbage collection",
    "Environment": "Air/water/noise pollution, forests, trees, rivers, illegal mining, wildlife, land degradation",
    "Energy": "Electricity supply, power cuts, load shedding, transformers, meters, billing, street lights, solar",
    "Urban Development": "Municipal services, housing, slums, encroachment, parks, urban footpaths and layout",
    "Accessibility": "Disability access: ramps, wheelchairs, Braille, sign language, accessibility of public buildings",
    "Public Administration": "Certificates, ration cards, pensions, welfare schemes, land records, official corruption",
    "Rural Livelihoods": "Farming, crops, MGNREGA wages, labour, livestock, fishing, rural employment",
    "Infrastructure/Transport": "Roads, bridges, culverts, buses, railways, traffic signals, public transport",
}

# Ordered severity rubric for the Jev Score question (2-10 levels allowed).
# Index 0 is least severe; the last level is most severe. Jev returns a
# probability-weighted position on this scale.
SEVERITY_LEVELS = [
    "Minor inconvenience with no health or safety impact",
    "Noticeable problem affecting daily routine",
    "Significant hardship for the affected community",
    "Serious risk to health or safety",
    "Life-threatening emergency requiring immediate action",
]

# Summarization / External LLM Configuration
# Single source of truth for the canonical-summary model. Overridable at runtime
# via the NVIDIA_MODEL environment variable (SUMMARIZATION_BACKEND=nvidia).
#
# The model must exist in the NIM catalog. NVIDIA retires models from
# integrate.api.nvidia.com without warning and an unknown ID returns a bare
# "404 page not found", which silently degrades summarization to the extractive
# fallback. Confirm any change with:
#   curl -s https://integrate.api.nvidia.com/v1/models/nvidia/nemotron-3.5-lightning-30b-a3b
# A retired model answers 410 Gone; an unknown one answers 404.
SUMMARIZATION_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"

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
