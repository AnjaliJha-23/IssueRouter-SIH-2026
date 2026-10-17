"""
Deterministic, dependency-free domain & subdomain classifier.

This is the guaranteed offline path: no network, no model weights, no torch. It
is used when ``CLASSIFIER_BACKEND=keyword``, and as the automatic fallback when
the Jev backend is selected but the API key is missing or the call fails.

Matching is deliberately boring:

* single tokens are matched as whole words, so ``nal`` never fires inside
  ``final``;
* multi-word phrases are matched as substrings;
* phrases carry double weight because they are far more specific than a lone
  keyword.

It is a triage heuristic, not an oracle. Its job is to keep the demo and the
test suite green when the decision model is unreachable.
"""

import re

from pipeline.config import (
    CLASSIFICATION_THRESHOLDS,
    DOMAINS,
    DOMAIN_SEVERITY,
    SUBDOMAIN_MAP,
)

MODEL_VERSION = "keyword-lexicon-v1"

# Domain used when nothing at all matches: the lowest-severity catch-all.
_DEFAULT_DOMAIN = "Public Administration"

_WORD_RE = re.compile(r"[a-z0-9]+")

# Tokens that hint at urgency, used only by the offline path.
_URGENCY_TERMS = [
    "urgent", "urgently", "immediately", "emergency", "immediate",
    "turant", "jaldi", "abhi", "aaj", "khatra", "khatarnak", "danger",
    "dangerous", "dying", "death", "died", "critical", "severe", "badly",
]


# domain -> list of terms. Terms containing a space are phrases.
_LEXICON = {
    "Healthcare": [
        "health", "hospital", "aspatal", "aspataal", "clinic", "dispensary",
        "doctor", "daktar", "daaktar", "nurse", "nursing", "medicine",
        "medicines", "dawa", "dawai", "dawaa", "treatment", "ilaj", "ilaaj",
        "upchar", "patient", "mareez", "mariz", "ambulance", "emergency",
        "phc", "chc", "pharmacy", "chemist", "vaccine", "vaccination",
        "teeka", "tika", "fever", "bukhar", "dengue", "malaria", "typhoid",
        "cholera", "diarrhea", "diarrhoea", "dast", "maternity", "delivery",
        "pregnancy", "pregnant", "blood", "oxygen", "icu", "bed", "surgery",
        "operation", "injection", "tablet", "tablets", "xray", "cancer",
        "malnutrition", "nutrition", "dehydration", "anaemia", "anemia",
        "health center", "health centre", "primary health", "health post",
        "health sub", "asha worker",
    ],
    "Education": [
        "school", "schools", "vidyalaya", "pathshala", "college", "university",
        "student", "students", "chhatra", "teacher", "teachers", "shikshak",
        "adhyapak", "class", "classroom", "exam", "exams", "pariksha",
        "result", "admission", "dropout", "dropouts", "book", "books",
        "kitab", "kitaben", "scholarship", "chhatravritti", "uniform", "fee",
        "fees", "syllabus", "hostel", "library", "degree", "diploma", "iti",
        "polytechnic", "neet", "jee", "madhyamik", "matric", "tuition",
        "mid day meal", "mid-day meal", "midday meal", "primary school",
        "high school", "middle school", "higher secondary",
        "anganwadi centre", "anganwadi center", "digital divide",
        "teacher shortage",
    ],
    "Water & Sanitation": [
        "water", "pani", "paani", "jal", "handpump", "handpumps", "tap",
        "taps", "nal", "nalkup", "well", "wells", "kuan", "kua", "kuwa",
        "borewell", "boring", "pipeline", "pipelines", "tank", "tanki",
        "sewage", "sewer", "gutter", "nali", "nalii", "drain", "drains",
        "drainage", "toilet", "toilets", "shauchalay", "shouchalay",
        "latrine", "sanitation", "swachh", "swachhta", "garbage", "kachra",
        "kachara", "waste", "dump", "dumping", "contamination",
        "contaminated", "arsenic", "fluoride", "chlorination", "stp",
        "drinking water", "hand pump", "hand pumps", "dirty water",
        "clean water", "water supply", "water tank", "open defecation",
        "sewage treatment",
    ],
    "Environment": [
        "pollution", "pradushan", "smog", "tree", "trees", "ped", "pedon",
        "forest", "forests", "jungle", "deforestation", "wildlife", "mining",
        "quarry", "quarrying", "river", "nadi", "dam", "flood", "floods",
        "drought", "sukha", "erosion", "plastic", "plastics", "climate",
        "emission", "emissions", "effluent", "effluents", "industrial",
        "air pollution", "water pollution", "noise pollution",
        "illegal mining", "tree cutting", "land degradation",
        "river pollution",
    ],
    "Energy": [
        "electricity", "bijli", "power", "transformer", "transformers",
        "feeder", "feeders", "voltage", "meter", "meters", "blackout",
        "solar", "kerosene", "gas", "lpg", "cylinder", "coal", "grid",
        "substation", "electrification", "pole", "poles", "streetlight",
        "streetlights", "power cut", "power cuts", "load shedding",
        "street light", "street lights", "electricity bill", "no power",
    ],
    "Urban Development": [
        "municipal", "municipality", "nagar", "ward", "slum", "slums",
        "basti", "bastee", "housing", "colony", "encroachment",
        "encroachments", "urban", "park", "parks", "footpath", "footpaths",
        "pavement", "demolition", "zoning", "township", "ews", "awas",
        "dwelling", "urban development", "nagar nigam",
        "municipal corporation", "master plan", "slum area",
    ],
    "Accessibility": [
        "disability", "disabilities", "disabled", "divyang", "divyangjan",
        "handicap", "handicapped", "wheelchair", "ramp", "ramps", "braille",
        "tactile", "prosthetics", "prosthetic", "crutches", "accessible",
        "accessibility", "blind", "deaf", "mute", "sign language",
        "wheelchair access", "specially abled", "differently abled",
    ],
    "Public Administration": [
        "certificate", "certificates", "ration", "aadhaar", "aadhar",
        "adhar", "pension", "pensions", "yojana", "scheme", "schemes",
        "subsidy", "bribe", "bribery", "rishwat", "corruption", "tehsil",
        "panchayat", "revenue", "jamabandi", "khata", "khasra", "domicile",
        "caste", "birth", "death", "babu", "clerk", "sarkari", "ration card",
        "pan card", "birth certificate", "death certificate",
        "caste certificate", "income certificate", "residence certificate",
        "land record", "land records", "government office", "block office",
    ],
    "Rural Livelihoods": [
        "farmer", "farmers", "kisan", "kisanon", "agriculture",
        "agricultural", "kheti", "khet", "crop", "crops", "fasal",
        "mgnrega", "mnrega", "nrega", "wages", "wage", "mazdoori",
        "majdoori", "labour", "labor", "labourers", "laborers",
        "employment", "rozgar", "livelihood", "dairy", "milk", "cattle",
        "pashu", "poultry", "fish", "fishing", "fisherman", "seed", "seeds",
        "beej", "fertilizer", "fertilizers", "khad", "irrigation",
        "sinchai", "mandi", "msp", "livestock", "goat", "goats", "cow",
        "buffalo", "bhains", "murgi", "minimum wage", "self help group",
        "self-help group", "animal husbandry", "crop insurance",
        "kisan credit",
    ],
    "Infrastructure/Transport": [
        "road", "roads", "sadak", "sadke", "highway", "highways", "pothole",
        "potholes", "gaddha", "gaddhe", "gaddhon", "bridge", "bridges", "pul", "culvert",
        "culverts", "bus", "buses", "transport", "transportation", "rail",
        "railway", "railways", "train", "trains", "station", "flyover",
        "toll", "traffic", "signal", "signals", "parking", "roadways",
        "commute", "conductor", "bus stand", "bus stop", "bus service",
        "railway station", "traffic light", "traffic signal",
        "foot over bridge", "public transport", "road repair",
        "road condition",
    ],
}

# subdomain label -> terms. Only labels listed in config.SUBDOMAIN_MAP matter.
_SUBDOMAIN_LEXICON = {
    "Rural Access": [
        "village", "gaon", "rural", "remote", "distance", "far", "travel",
        "no road",
    ],
    "PHC Staffing": [
        "doctor", "nurse", "staff", "staffing", "vacancy", "absent",
        "posted", "shortage", "no doctor",
    ],
    "Diagnostics": [
        "test", "tests", "lab", "laboratory", "diagnostic", "diagnostics",
        "xray", "x-ray", "sample", "equipment", "machine", "ultrasound",
    ],
    "Maternal Health": [
        "maternity", "pregnancy", "pregnant", "delivery", "newborn", "child",
        "anc", "labour room", "labour ward",
    ],
    "Waterborne Disease": [
        "diarrhea", "diarrhoea", "dast", "typhoid", "cholera", "jaundice",
        "waterborne", "water borne", "water-born",
    ],
    "Primary Education": [
        "primary", "school", "class", "student", "middle", "anganwadi",
    ],
    "Higher Education": [
        "college", "university", "degree", "admission", "hostel", "campus",
    ],
    "Digital Divide": [
        "internet", "computer", "computers", "digital", "online",
        "smart class", "laptop", "network", "connectivity",
    ],
    "Teacher Shortage": [
        "teacher", "teachers", "shikshak", "vacancy", "post", "staffing",
    ],
    "Infrastructure": [
        "building", "classroom", "wall", "roof", "toilet", "bench",
        "furniture", "boundary", "boundary wall",
    ],
    "Drinking Water": [
        "drinking", "pani", "paani", "tap", "taps", "handpump", "hand pump",
        "well", "kuan", "water supply", "pipeline", "tank",
    ],
    "Sewage": [
        "sewage", "sewer", "gutter", "nali", "drain", "drains", "overflow",
        "manhole", "overflowing",
    ],
    "Waste Management": [
        "garbage", "kachra", "kachara", "waste", "dump", "dustbin",
        "sweeping", "collection",
    ],
    "Pollution": [
        "pollution", "pradushan", "contaminated", "contamination",
        "dirty water", "effluent", "arsenic", "fluoride",
    ],
}


def _score(text_lower: str, tokens: set, terms) -> float:
    total = 0.0
    for term in terms:
        if " " in term or "-" in term:
            if term in text_lower:
                total += 2.0
        elif term in tokens:
            total += 1.0
    return total


def _urgency(text_lower: str, tokens: set) -> float:
    hits = _score(text_lower, tokens, _URGENCY_TERMS)
    return round(min(1.0, 0.25 * hits), 3)


def _pick_subdomain(text_lower: str, tokens: set, domain: str):
    labels = SUBDOMAIN_MAP.get(domain)
    if not labels:
        return None

    best_label, best_score, total = None, 0.0, 0.0
    for label in labels:
        score = _score(text_lower, tokens, _SUBDOMAIN_LEXICON.get(label, []))
        total += score
        if score > best_score:
            best_label, best_score = label, score

    if best_label is None or total <= 0:
        return None
    if best_score / total < CLASSIFICATION_THRESHOLDS["subdomain_confidence_min"]:
        return None
    return best_label


def classify(text: str) -> dict:
    """Return the pipeline's classification contract using the lexicon."""
    text_lower = (text or "").lower()
    tokens = set(_WORD_RE.findall(text_lower))

    scores = {domain: _score(text_lower, tokens, terms) for domain, terms in _LEXICON.items()}
    total = sum(scores.values())

    if total <= 0:
        # Nothing matched: fall back to the catch-all with a flat distribution.
        uniform = round(1 / len(DOMAINS), 3)
        return {
            "domain": _DEFAULT_DOMAIN,
            "subdomain": None,
            "domain_scores": {domain: uniform for domain in DOMAINS},
            "model_version": MODEL_VERSION,
            "severity": DOMAIN_SEVERITY.get(_DEFAULT_DOMAIN, 0.5),
            "urgency": _urgency(text_lower, tokens),
            "confidence": uniform,
        }

    domain_scores = {domain: round(score / total, 3) for domain, score in scores.items()}
    domain = max(scores, key=scores.get)

    return {
        "domain": domain,
        "subdomain": _pick_subdomain(text_lower, tokens, domain),
        "domain_scores": domain_scores,
        "model_version": MODEL_VERSION,
        "severity": DOMAIN_SEVERITY.get(domain, 0.5),
        "urgency": _urgency(text_lower, tokens),
        "confidence": domain_scores[domain],
    }
