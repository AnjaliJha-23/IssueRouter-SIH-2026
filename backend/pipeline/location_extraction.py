import spacy
import json
import os

_nlp = None
_gazetteer = None

def load_gazetteer():
    global _gazetteer
    if _gazetteer is None:
        file_path = os.path.join(os.path.dirname(__file__), "data", "jharkhand_gazetteer.json")
        with open(file_path, "r", encoding="utf-8") as f:
            _gazetteer = json.load(f)

def load_ner():
    global _nlp, _gazetteer
    if _nlp is None:
        print("[location_extraction] Loading spaCy model...")
        _nlp = spacy.load("en_core_web_sm")
        
        load_gazetteer()
        
        # Build patterns from gazetteer
        patterns = []
        for district, blocks in _gazetteer.items():
            patterns.append({"label": "DISTRICT", "pattern": district})
            for block in blocks:
                patterns.append({"label": "BLOCK", "pattern": block})
                
        ruler = _nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(patterns)
        print("[location_extraction] spaCy model loaded.")

def extract_entities(text: str, evidence_metadata: dict = None) -> dict:
    """
    Returns dict with extracted location entities matching the pipeline contract.
    evidence_metadata can contain {"latitude": float, "longitude": float}
    """
    if _nlp is None:
        load_ner()

    if evidence_metadata is None:
        evidence_metadata = {}

    doc = _nlp(text)

    district = None
    block = None
    resolution_method = None
    confidence = 0.0

    # 1. EntityRuler exact match
    for ent in doc.ents:
        if ent.label_ == "DISTRICT" and district is None:
            district = ent.text
            resolution_method = "gazetteer_match"
            confidence = 0.9
        if ent.label_ == "BLOCK" and block is None:
            block = ent.text
            resolution_method = "gazetteer_match"
            confidence = 0.85

    # 2. Fallback to substring if no EntityRuler match found
    if district is None and block is None:
        text_lower = text.lower()
        for d, b_list in _gazetteer.items():
            if d.lower() in text_lower:
                district = d
                resolution_method = "fuzzy_gazetteer"
                confidence = 0.7
                break
            for b in b_list:
                if b.lower() in text_lower:
                    block = b
                    district = d # Infer district from block
                    resolution_method = "fuzzy_gazetteer"
                    confidence = 0.7
                    break
            if district:
                break

    # 3. Fallback to evidence metadata for lat/long if provided
    latitude = evidence_metadata.get("latitude")
    longitude = evidence_metadata.get("longitude")
    
    if district is None and block is None and (latitude is not None and longitude is not None):
        resolution_method = "metadata_coords"
        confidence = 0.95
        
    if district is None and block is None and resolution_method is None:
        resolution_method = "unresolved"
        confidence = 0.0

    return {
        "district": district,
        "block": block,
        "village_ward": None, # Not currently resolving below block level
        "latitude": latitude,
        "longitude": longitude,
        "resolution_method": resolution_method,
        "confidence": confidence
    }