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
    Process incoming evidence (citizen submission, tweet, field report)
    through the complete NLP pipeline and persist results to the database.

    Input evidence_data:
    {
        "source": "citizen" | "twitter" | "social" | "field_agent",
        "raw_text": "...",
        "submitted_lat": float | None,
        "submitted_lng": float | None,
        "title": str | None,
        "location": str | None
    }
    """
    raw_text = evidence_data.get("raw_text") or evidence_data.get("description") or ""
    title_hint = evidence_data.get("title")
    source = evidence_data.get("source", "citizen")
    submitted_lat = evidence_data.get("submitted_lat")
    submitted_lng = evidence_data.get("submitted_lng")
    loc_hint = evidence_data.get("location")
    
    # Prepend title or location hint if given to enrich NLP context
    combined_input = f"{title_hint + '. ' if title_hint else ''}{raw_text}{' at ' + loc_hint if loc_hint and loc_hint not in raw_text else ''}".strip()
    
    # 1. Clean Text
    clean_txt = clean_text(combined_input)
    
    # 2. Zero-Shot Domain & Subdomain Classification
    class_res = classify(clean_txt)
    domain = class_res["domain"]
    subdomain = class_res.get("subdomain")
    
    # 3. Location Extraction via spaCy & Jharkhand Gazetteer
    loc_metadata = {"latitude": submitted_lat, "longitude": submitted_lng}
    loc_res = extract_entities(clean_txt, loc_metadata)
    district = loc_res.get("district")
    block = loc_res.get("block")
    res_lat = loc_res.get("latitude") or submitted_lat
    res_lng = loc_res.get("longitude") or submitted_lng
    
    resolved_location = f"{block or ''}{', ' if block and district else ''}{district or loc_hint or 'Jharkhand'}".strip()
    if not resolved_location:
        resolved_location = loc_hint or "Jharkhand"
    
    # 4. Dense Semantic Vector Embeddings (384d)
    embed_text = f"[{domain}] {clean_txt}"
    embedding = get_embedding(embed_text)
    
    # 5. Semantic Deduplication / Similarity Clustering
    candidate_records = db.query(Challenge).filter(
        Challenge.domain == domain
    )
    if district:
        candidate_records = candidate_records.filter(
            (Challenge.district == district) | (Challenge.location.ilike(f"%{district}%"))
        )
    candidate_records = candidate_records.all()
    
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
    sim_score = dedup_res.get("similarity_score", 0.0)
    
    # 6. Challenge Linking / Creation
    challenge = None
    if action == "link" and matched_id:
        challenge = db.query(Challenge).filter(Challenge.id == matched_id).first()
    
    if not challenge:
        # new_challenge or flag_related
        challenge_id = "CHL-" + datetime.utcnow().strftime("%Y") + "-" + str(uuid.uuid4().hex[:6]).upper()
        challenge = Challenge(
            id=challenge_id,
            title=title_hint or "AI Processing Summary...",
            official_description=raw_text,
            ai_generated_summary=raw_text,
            domain=domain,
            department=domain,
            district=district,
            block=block,
            location=resolved_location,
            lat=res_lat,
            lng=res_lng,
            status="pending_verification",
            source_counts={"citizen": 0, "social": 0},
            duplicate_risk=round(sim_score, 2) if sim_score else 0.05,
            verified=False,
            created_at=datetime.utcnow()
        )
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
        
    # Persist New Evidence Row
    evidence_id = "EV-" + str(uuid.uuid4().hex[:8]).upper()
    evidence = ChallengeEvidence(
        id=evidence_id,
        challenge_id=challenge.id,
        source=source,
        raw_text=raw_text,
        clean_text=clean_txt,
        embedding_json=embedding,
        submitted_lat=res_lat,
        submitted_lng=res_lng,
        created_at=datetime.utcnow()
    )
    db.add(evidence)
    
    # Record Candidate Duplicate Relations if flagged
    if action == "flag_related" and dedup_res.get("candidate_relations"):
        for rel in dedup_res["candidate_relations"]:
            cr = ChallengeRelation(
                id="CR-" + str(uuid.uuid4().hex[:8]).upper(),
                source_challenge_id=challenge.id,
                target_challenge_id=rel["challenge_id"],
                similarity_score=rel["score"],
                status="pending"
            )
            db.add(cr)
            
    db.commit()
    
    # 7. Multi-Source Canonical Summarization
    all_evidences = db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == challenge.id).all()
    combined_ev_text = "\n".join([e.clean_text for e in all_evidences])
    
    existing_summary = {
        "title": challenge.title,
        "description": challenge.ai_generated_summary or challenge.official_description or ""
    } if challenge.ai_generated_summary else None
    
    summary_res = generate_summary(existing_summary, combined_ev_text, domain, challenge.location)
    challenge.title = summary_res.get("title") or challenge.title
    challenge.ai_generated_summary = summary_res.get("description") or challenge.ai_generated_summary
    
    # Update source counts and complaint counts
    social_sources = sum(1 for e in all_evidences if e.source in ["twitter", "social"])
    citizen_sources = sum(1 for e in all_evidences if e.source in ["citizen", "field_agent", "unknown"])
    challenge.source_counts = {
        "social": social_sources,
        "citizen": citizen_sources
    }
    challenge.complaint_count = len(all_evidences)
    
    # 8. Explainable Multi-Factor Priority Scoring
    ev_count = len(all_evidences)
    ev_conf = 0.90 if (social_sources > 0 and citizen_sources > 0) else (0.80 if ev_count > 1 else 0.65)
    trend = "increasing" if ev_count > 2 else "stable"
    
    pri_res = calculate_priority(domain, ev_count, ev_conf, trend)
    challenge.priority_score = pri_res["priority_score"]
    challenge.ai_confidence = pri_res["evidence_confidence"]
    challenge.trend = pri_res["trend"]
    
    if district and not challenge.district:
        challenge.district = district
    if block and not challenge.block:
        challenge.block = block
    if res_lat and not challenge.lat:
        challenge.lat = res_lat
    if res_lng and not challenge.lng:
        challenge.lng = res_lng
        
    # 9. Upsert ChallengeAnalysis Audit Record
    analysis = db.query(ChallengeAnalysis).filter(ChallengeAnalysis.challenge_id == challenge.id).first()
    if not analysis:
        analysis = ChallengeAnalysis(
            id="CA-" + str(uuid.uuid4().hex[:8]).upper(),
            challenge_id=challenge.id
        )
        db.add(analysis)
        
    analysis.domain = domain
    analysis.subdomain = subdomain
    analysis.domain_scores = class_res.get("domain_scores")
    analysis.priority_score = pri_res["priority_score"]
    analysis.priority_factors = pri_res["priority_factors"]
    analysis.evidence_confidence = pri_res["evidence_confidence"]
    analysis.trend = pri_res["trend"]
    analysis.explanation = pri_res["explanation"]
    analysis.model_versions = {
        "classification": class_res.get("model_version", "facebook/bart-large-mnli"),
        "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
        "summarization": "groq/compound-mini"
    }
    analysis.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(challenge)
    db.refresh(analysis)
    
    return {
        "status": "success",
        "action": action,
        "challenge_id": challenge.id,
        "priority_score": challenge.priority_score,
        "domain": domain,
        "subdomain": subdomain,
        "district": challenge.district,
        "block": challenge.block,
        "summary_title": challenge.title,
        "summary_description": challenge.ai_generated_summary,
        "confidence": challenge.ai_confidence,
        "similarity_score": sim_score,
        "candidate_relations": dedup_res.get("candidate_relations", []),
        "analysis": {
            "id": analysis.id,
            "challenge_id": analysis.challenge_id,
            "domain": analysis.domain,
            "subdomain": analysis.subdomain,
            "domain_scores": analysis.domain_scores,
            "priority_score": analysis.priority_score,
            "priority_factors": analysis.priority_factors,
            "evidence_confidence": analysis.evidence_confidence,
            "trend": analysis.trend,
            "explanation": analysis.explanation,
            "model_versions": analysis.model_versions,
            "updated_at": analysis.updated_at
        }
    }


def analyze_challenge(challenge_id: str, db: Session) -> dict:
    """
    On-demand re-analysis of an existing Challenge using its full evidence history.
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        return {"status": "error", "message": f"Challenge {challenge_id} not found"}
        
    evidences = db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == challenge_id).all()
    if evidences:
        combined_text = "\n".join([e.clean_text or e.raw_text for e in evidences])
    else:
        combined_text = f"{challenge.title}. {challenge.official_description or challenge.ai_generated_summary or challenge.location}"
        # Create an initial evidence row from current challenge info if none exists
        ev = ChallengeEvidence(
            id="EV-" + str(uuid.uuid4().hex[:8]).upper(),
            challenge_id=challenge.id,
            source="citizen",
            raw_text=combined_text,
            clean_text=clean_text(combined_text),
            submitted_lat=challenge.lat,
            submitted_lng=challenge.lng,
            created_at=challenge.created_at or datetime.utcnow()
        )
        db.add(ev)
        db.commit()
        evidences = [ev]
        
    clean_txt = clean_text(combined_text)
    class_res = classify(clean_txt)
    domain = class_res["domain"]
    subdomain = class_res.get("subdomain")
    
    loc_metadata = {"latitude": challenge.lat, "longitude": challenge.lng}
    loc_res = extract_entities(clean_txt, loc_metadata)
    district = loc_res.get("district") or challenge.district
    block = loc_res.get("block") or challenge.block
    
    summary_res = generate_summary(
        {"title": challenge.title, "description": challenge.ai_generated_summary or ""},
        clean_txt,
        domain,
        challenge.location
    )
    
    challenge.title = summary_res.get("title") or challenge.title
    challenge.ai_generated_summary = summary_res.get("description") or challenge.ai_generated_summary
    challenge.domain = domain
    if district:
        challenge.district = district
    if block:
        challenge.block = block
        
    ev_count = len(evidences)
    social_sources = sum(1 for e in evidences if e.source in ["twitter", "social"])
    citizen_sources = sum(1 for e in evidences if e.source in ["citizen", "field_agent", "unknown"])
    challenge.source_counts = {"social": social_sources, "citizen": citizen_sources}
    challenge.complaint_count = ev_count
    
    ev_conf = 0.90 if (social_sources > 0 and citizen_sources > 0) else (0.80 if ev_count > 1 else 0.65)
    trend = "increasing" if ev_count > 2 else "stable"
    
    pri_res = calculate_priority(domain, ev_count, ev_conf, trend)
    challenge.priority_score = pri_res["priority_score"]
    challenge.ai_confidence = pri_res["evidence_confidence"]
    challenge.trend = pri_res["trend"]
    
    analysis = db.query(ChallengeAnalysis).filter(ChallengeAnalysis.challenge_id == challenge.id).first()
    if not analysis:
        analysis = ChallengeAnalysis(
            id="CA-" + str(uuid.uuid4().hex[:8]).upper(),
            challenge_id=challenge.id
        )
        db.add(analysis)
        
    analysis.domain = domain
    analysis.subdomain = subdomain
    analysis.domain_scores = class_res.get("domain_scores")
    analysis.priority_score = pri_res["priority_score"]
    analysis.priority_factors = pri_res["priority_factors"]
    analysis.evidence_confidence = pri_res["evidence_confidence"]
    analysis.trend = pri_res["trend"]
    analysis.explanation = pri_res["explanation"]
    analysis.model_versions = {
        "classification": class_res.get("model_version", "facebook/bart-large-mnli"),
        "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
        "summarization": "groq/compound-mini"
    }
    analysis.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(challenge)
    db.refresh(analysis)
    
    return {
        "status": "success",
        "challenge_id": challenge.id,
        "priority_score": challenge.priority_score,
        "domain": domain,
        "subdomain": subdomain,
        "district": challenge.district,
        "block": challenge.block,
        "summary_title": challenge.title,
        "summary_description": challenge.ai_generated_summary,
        "confidence": challenge.ai_confidence,
        "analysis": {
            "id": analysis.id,
            "challenge_id": analysis.challenge_id,
            "domain": analysis.domain,
            "subdomain": analysis.subdomain,
            "domain_scores": analysis.domain_scores,
            "priority_score": analysis.priority_score,
            "priority_factors": analysis.priority_factors,
            "evidence_confidence": analysis.evidence_confidence,
            "trend": analysis.trend,
            "explanation": analysis.explanation,
            "model_versions": analysis.model_versions,
            "updated_at": analysis.updated_at
        }
    }