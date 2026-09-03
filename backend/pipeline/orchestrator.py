import uuid
import json
from datetime import datetime
from sqlalchemy.orm import Session

from db.models import Challenge, ChallengeEvidence, ChallengeAnalysis, ChallengeRelation
from ingestion.normaliser import clean_text

from pipeline.classification import classify
from pipeline.location_extraction import extract_entities
from pipeline.embeddings import get_embedding
from pipeline.deduplication import resolve
from pipeline.summarization import generate_summary
from pipeline.priority_scoring import calculate_priority

def load_all_models():
    """Call this at FastAPI startup to warm all models before first request."""
    print("[orchestrator] Warming up all models...")
    from pipeline.classification import load_classifier
    from pipeline.location_extraction import load_ner
    from pipeline.embeddings import load_embedder
    load_classifier()
    load_ner()
    load_embedder()
    print("[orchestrator] All models ready.")

def process_evidence(evidence_data: dict, db: Session) -> dict:
    """
    Input evidence_data:
    {
        "source": "twitter" | "citizen",
        "raw_text": "...",
        "submitted_lat": float | None,
        "submitted_lng": float | None
    }
    """
    raw_text = evidence_data.get("raw_text", "")
    source = evidence_data.get("source", "unknown")
    submitted_lat = evidence_data.get("submitted_lat")
    submitted_lng = evidence_data.get("submitted_lng")
    
    # 1. Clean
    clean_txt = clean_text(raw_text)
    
    # 2. Classify
    class_res = classify(clean_txt)
    domain = class_res["domain"]
    
    # 3. Location Extraction
    loc_metadata = {"latitude": submitted_lat, "longitude": submitted_lng}
    loc_res = extract_entities(clean_txt, loc_metadata)
    district = loc_res.get("district")
    block = loc_res.get("block")
    
    # 4. Embeddings
    embed_text = f"[{domain}] {clean_txt}"
    embedding = get_embedding(embed_text)
    
    # 5. Deduplication
    candidate_records = db.query(Challenge).filter(
        Challenge.domain == domain,
        Challenge.district == district
    ).all()
    
    candidates_for_dedup = []
    for c in candidate_records:
        latest_ev = db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == c.id).first()
        canonical_emb = latest_ev.embedding_json if latest_ev else None
        
        candidates_for_dedup.append({
            "id": c.id,
            "domain": c.domain,
            "district": c.district,
            "canonical_embedding": canonical_emb
        })
        
    dedup_res = resolve(embedding, domain, district, candidates_for_dedup)
    action = dedup_res["action"]
    matched_id = dedup_res["matched_challenge_id"]
    
    # 6. Branch Logic
    challenge = None
    if action == "link" and matched_id:
        challenge = db.query(Challenge).filter(Challenge.id == matched_id).first()
    else: 
        # new_challenge or flag_related
        challenge_id = "HC-" + str(uuid.uuid4())[:8]
        challenge = Challenge(
            id=challenge_id,
            title="Processing AI Summary...",
            domain=domain,
            district=district,
            block=block,
            location=f"{block or ''} {district or ''}".strip()
        )
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
        
    # Persist Evidence
    evidence_id = "EV-" + str(uuid.uuid4())[:8]
    evidence = ChallengeEvidence(
        id=evidence_id,
        challenge_id=challenge.id,
        source=source,
        raw_text=raw_text,
        clean_text=clean_txt,
        embedding_json=embedding,
        submitted_lat=submitted_lat,
        submitted_lng=submitted_lng
    )
    db.add(evidence)
    
    if action == "flag_related" and dedup_res["candidate_relations"]:
        for rel in dedup_res["candidate_relations"]:
            cr = ChallengeRelation(
                id="CR-" + str(uuid.uuid4())[:8],
                source_challenge_id=challenge.id,
                target_challenge_id=rel["challenge_id"],
                similarity_score=rel["score"]
            )
            db.add(cr)
            
    db.commit()
    
    # 7. Summarization 
    all_evidences = db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == challenge.id).all()
    combined_text = "\n".join([e.clean_text for e in all_evidences])
    
    existing_summary = {"title": challenge.title, "description": challenge.ai_generated_summary} if challenge.ai_generated_summary else None
    summary_res = generate_summary(existing_summary, combined_text, domain, challenge.location)
    
    challenge.title = summary_res["title"]
    challenge.ai_generated_summary = summary_res["description"]
    
    # 8. Priority Scoring
    ev_count = len(all_evidences)
    ev_conf = 0.8 if ev_count > 1 else 0.5 
    trend = "increasing" if ev_count > 2 else "stable"
    
    pri_res = calculate_priority(domain, ev_count, ev_conf, trend)
    challenge.priority_score = pri_res["priority_score"]
    
    # 9. Upsert Analysis
    analysis = db.query(ChallengeAnalysis).filter(ChallengeAnalysis.challenge_id == challenge.id).first()
    if not analysis:
        analysis = ChallengeAnalysis(
            id="CA-" + str(uuid.uuid4())[:8],
            challenge_id=challenge.id
        )
        db.add(analysis)
        
    analysis.domain = domain
    analysis.subdomain = class_res["subdomain"]
    analysis.domain_scores = class_res["domain_scores"]
    analysis.priority_score = pri_res["priority_score"]
    analysis.priority_factors = pri_res["priority_factors"]
    analysis.evidence_confidence = pri_res["evidence_confidence"]
    analysis.trend = pri_res["trend"]
    analysis.explanation = pri_res["explanation"]
    analysis.model_versions = {"classification": class_res["model_version"]}
    
    db.commit()
    
    return {
        "status": "success",
        "action": action,
        "challenge_id": challenge.id,
        "priority_score": challenge.priority_score
    }