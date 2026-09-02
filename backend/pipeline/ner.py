import spacy

_nlp = None

# Gazetteer — Indian localities, landmarks, departments
# Add more as needed for your seed tweets
GAZETTEER = {
    # Delhi localities
    "Mayur Vihar": "GPE",
    "Uttam Nagar": "GPE",
    "Rohini": "GPE",
    "Dwarka": "GPE",
    "Lajpat Nagar": "GPE",
    "Vasant Kunj": "GPE",
    "Connaught Place": "GPE",
    "CP": "GPE",
    "Akbar Road": "GPE",
    "Janpath": "GPE",
    "Karol Bagh": "GPE",
    "Saket": "GPE",
    "Noida": "GPE",
    "Gurgaon": "GPE",
    "Faridabad": "GPE",
    # Mumbai
    "Dharavi": "GPE",
    "Andheri": "GPE",
    "Bandra": "GPE",
    "Dadar": "GPE",
    # Bangalore
    "Koramangala": "GPE",
    "Indiranagar": "GPE",
    "Whitefield": "GPE",
    # Departments
    "PWD": "DEPARTMENT",
    "NDMC": "DEPARTMENT",
    "MCD": "DEPARTMENT",
    "Jal Board": "DEPARTMENT",
    "BSES": "DEPARTMENT",
    "BESCOM": "DEPARTMENT",
    "MCGM": "DEPARTMENT",
    "BBMP": "DEPARTMENT",
}

ENTITY_RULER_PATTERNS = [
    {"label": label, "pattern": name}
    for name, label in GAZETTEER.items()
]

def load_ner():
    global _nlp
    if _nlp is None:
        print("[ner] Loading spaCy model...")
        _nlp = spacy.load("en_core_web_sm")
        ruler = _nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(ENTITY_RULER_PATTERNS)
        print("[ner] spaCy model loaded.")

def extract_entities(text: str) -> dict:
    """
    Returns dict with extracted entities.
    Example: {"location": "Mayur Vihar", "department": "PWD", "date": None}
    """
    if _nlp is None:
        load_ner()

    doc = _nlp(text)

    location = None
    department = None
    date = None

    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"] and location is None:
            location = ent.text
        if ent.label_ == "DEPARTMENT" and department is None:
            department = ent.text
        if ent.label_ == "DATE" and date is None:
            date = ent.text

    # Fallback: substring match on gazetteer
    if location is None:
        text_lower = text.lower()
        for name, label in GAZETTEER.items():
            if label == "GPE" and name.lower() in text_lower:
                location = name
                break

    return {
        "location": location,
        "department_mentioned": department,
        "date": date
    }