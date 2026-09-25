"""
pipeline/lightweight_orchestrator.py
Zero-heavy-dependency fallback pipeline for production deployment.

Provides deterministic heuristic domain classification, Jharkhand gazetteer
location extraction, 384-dimensional hashed embeddings, deduplication,
extractive summarization, and explainable priority scoring.
Preserves the exact interface and response contracts of pipeline.orchestrator.
"""
import os
import re
import json
import uuid
import math
import hashlib
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from db.models import Challenge, ChallengeEvidence, ChallengeAnalysis, ChallengeRelation
from ingestion.normaliser import clean_text
from pipeline.config import DOMAINS, SUBDOMAIN_MAP
from pipeline.deduplication import resolve
from pipeline.priority_scoring import calculate_priority
from pipeline.summarization import generate_summary

logger = logging.getLogger(__name__)

# ── Cached Jharkhand Gazetteer ──────────────────────────────────────────────
_gazetteer = None

def load_gazetteer() -> dict:
    global _gazetteer
    if _gazetteer is None:
        gazetteer_path = os.path.join(os.path.dirname(__file__), "data", "jharkhand_gazetteer.json")
        try:
            with open(gazetteer_path, "r", encoding="utf-8") as f:
                _gazetteer = json.load(f)
        except Exception as e:
            logger.warning(f"[lightweight_orchestrator] Could not load gazetteer from {gazetteer_path}: {e}")
            _gazetteer = {}
    return _gazetteer

# ── Heuristic Keyword Dictionaries for Classification ───────────────────────
DOMAIN_KEYWORDS = {
    "Healthcare": [
        "hospital", "doctor", "health", "medicine", "clinic", "phc", "patient", "medical",
        "disease", "treatment", "antivenom", "nurse", "ambulance", "vaccine", "fever",
        "illness", "bed", "ward", "infection", "drugs", "dispensary", "physician", "surgical"
    ],
    "Water & Sanitation": [
        "water", "drinking water", "handpump", "borewell", "pipeline", "drainage", "sewage",
        "leak", "pipe", "toilet", "sanitation", "wells", "contamination", "tap", "tanker",
        "scarcity", "dirty water", "garbage dump", "drain", "waterlogging", "sewer", "chlorination"
    ],
    "Education": [
        "school", "teacher", "student", "classroom", "college", "education", "books",
        "exam", "syllabus", "university", "faculty", "study", "tuition", "literacy",
        "blackboard", "midday meal", "campus", "scholarship", "mid-day meal"
    ],
    "Infrastructure/Transport": [
        "road", "bridge", "pothole", "highway", "bus", "transport", "traffic", "street",
        "footpath", "overbridge", "flyover", "culvert", "pavement", "construction",
        "tar", "asphalt", "connectivity", "lane", "commute", "junction"
    ],
    "Energy": [
        "electricity", "power", "transformer", "load shedding", "voltage", "blackout",
        "wire", "pole", "solar", "grid", "power outage", "electric", "short circuit",
        "feeder", "substation", "generator"
    ],
    "Environment": [
        "pollution", "garbage", "trash", "waste", "dump", "forest", "mining", "dust",
        "smoke", "tree", "river", "coal slurry", "plastic", "cleanliness", "emission",
        "air quality", "deforestation", "wildlife", "smog"
    ],
    "Urban Development": [
        "encroachment", "park", "urban", "slum", "building", "metro", "smart city",
        "zoning", "street light", "colony", "town planning", "vendor", "commercial",
        "residential", "sidewalk", "beautification"
    ],
    "Rural Livelihoods": [
        "farmer", "crop", "agriculture", "fertilizer", "pesticide", "irrigation",
        "mgnrega", "ration", "kisan", "mandis", "drought", "seeds", "harvest",
        "livelihood", "farming", "dairy", "livestock", "tractor", "paddy"
    ],
    "Accessibility": [
        "wheelchair", "ramp", "disabled", "disability", "braille", "differently abled",
        "barrier", "handicapped", "accessible", "pedestrian crossing", "tactile"
    ],
    "Public Administration": [
        "corruption", "bribe", "pension", "ration card", "aadhaar", "certificate",
        "officer", "bureaucracy", "delay", "panchayat", "bdo", "tehsildar", "collectorate",
        "governance", "complaint", "portal", "grievance", "fraud"
    ]
}

def classify_heuristic(text: str) -> dict:
    """
    Deterministic rule/keyword-based domain and subdomain classifier.
    Fast, lightweight, and requires no PyTorch or Transformers.
    """
    text_lower = text.lower()
    raw_scores = {}

    for domain in DOMAINS:
        keywords = DOMAIN_KEYWORDS.get(domain, [])
        score = 0.05  # baseline floor
        for kw in keywords:
            if " " in kw:
                if kw in text_lower:
                    score += 2.0
            else:
                matches = len(re.findall(r'\b' + re.escape(kw) + r'\b', text_lower))
                score += matches * 1.0
        raw_scores[domain] = score

    total_score = sum(raw_scores.values()) or 1.0
    domain_scores = {d: round(s / total_score, 3) for d, s in raw_scores.items()}

    # Select top domain
    top_domain = max(domain_scores, key=domain_scores.get)

    # Subdomain detection
    subdomain = None
    if top_domain in SUBDOMAIN_MAP:
        candidate_subdomains = SUBDOMAIN_MAP[top_domain]
        for sub in candidate_subdomains:
            sub_words = [w.lower() for w in re.findall(r'\w+', sub)]
            if any(re.search(r'\b' + re.escape(w) + r'\b', text_lower) for w in sub_words if len(w) > 3):
                subdomain = sub
                break

    return {
        "domain": top_domain,
        "subdomain": subdomain,
        "domain_scores": domain_scores,
        "model_version": "heuristic/keyword-rules-v1"
    }

def extract_entities_gazetteer(text: str, metadata: dict = None) -> dict:
    """
    Direct gazetteer string matching for Jharkhand districts and blocks.
    Requires no spaCy or large NLP models.
    """
    gazetteer = load_gazetteer()
    metadata = metadata or {}
    text_lower = text.lower()

    detected_district = None
    detected_block = None
    confidence = 0.0
    method = None

    # 1. Look for district names
    for district, blocks in gazetteer.items():
        pattern = r'\b' + re.escape(district.lower()) + r'\b'
        if re.search(pattern, text_lower):
            detected_district = district
            confidence = 0.90
            method = "gazetteer_match"
            break

    # 2. Look for block names
    for district, blocks in gazetteer.items():
        for block in blocks:
            pattern = r'\b' + re.escape(block.lower()) + r'\b'
            if re.search(pattern, text_lower):
                detected_block = block
                if not detected_district:
                    detected_district = district
                confidence = max(confidence, 0.85)
                method = method or "gazetteer_match"
                break
        if detected_block:
            break

    lat = metadata.get("latitude")
    lng = metadata.get("longitude")

    return {
        "district": detected_district,
        "block": detected_block,
        "latitude": lat,
        "longitude": lng,
        "resolution_method": method or "none",
        "confidence": confidence
    }

def get_deterministic_embedding(text: str, dim: int = 384) -> list[float]:
    """
    Generate a deterministic 384-dimensional unit-normalized pseudo-embedding.
    Guarantees:
      - Strictly 384 floats (compatible with canonical sentence-transformers dimension)
      - Deterministic for the same text
      - Normalized (L2 norm = 1.0) so cosine similarity is well-defined
      - Zero ML dependencies (no PyTorch, no Hugging Face)
    """
    tokens = re.findall(r'\w+', text.lower())
    if not tokens:
        val = round(1.0 / math.sqrt(dim), 6)
        return [val] * dim

    vec = [0.0] * dim
    for token in tokens:
        h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
        bin_idx = h % dim
        sign = 1.0 if ((h >> 16) & 1) else -1.0
        vec[bin_idx] += sign

    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        val = round(1.0 / math.sqrt(dim), 6)
        return [val] * dim

    return [round(x / norm, 6) for x in vec]

def load_all_models():
    """Warmup entrypoint for FastAPI startup in lightweight mode."""
    print("[lightweight_orchestrator] Warming up lightweight rules and gazetteer...")
    load_gazetteer()
    print("[lightweight_orchestrator] Lightweight pipeline ready (Zero heavy ML overhead).")

def process_evidence(evidence_data: dict, db: Session) -> dict:
    """
    Process incoming evidence (citizen submission, tweet, field report)
    through the lightweight pipeline and persist results to the database.
    """
    raw_text = evidence_data.get("raw_text") or evidence_data.get("description") or ""
    title_hint = evidence_data.get("title")
    source = evidence_data.get("source", "citizen")
    submitted_lat = evidence_data.get("submitted_lat")
    submitted_lng = evidence_data.get("submitted_lng")
    loc_hint = evidence_data.get("location")

    combined_input = f"{title_hint + '. ' if title_hint else ''}{raw_text}{' at ' + loc_hint if loc_hint and loc_hint not in raw_text else ''}".strip()

    # 1. Clean Text via pure regex
    clean_txt = clean_text(combined_input)

    # 2. Heuristic Domain & Subdomain Classification
    class_res = classify_heuristic(clean_txt)
    domain = class_res["domain"]
    subdomain = class_res.get("subdomain")

    # 3. Location Extraction via Jharkhand Gazetteer
    loc_metadata = {"latitude": submitted_lat, "longitude": submitted_lng}
    loc_res = extract_entities_gazetteer(clean_txt, loc_metadata)
    district = loc_res.get("district")
    block = loc_res.get("block")
    res_lat = loc_res.get("latitude") or submitted_lat
    res_lng = loc_res.get("longitude") or submitted_lng

    resolved_location = f"{block or ''}{', ' if block and district else ''}{district or loc_hint or 'Jharkhand'}".strip()
    if not resolved_location:
        resolved_location = loc_hint or "Jharkhand"

    # 4. Deterministic 384-dimensional Embedding
    embed_text = f"[{domain}] {clean_txt}"
    embedding = get_deterministic_embedding(embed_text)

    # 5. Semantic Deduplication via Cosine Similarity (numpy + scikit-learn)
    candidate_records = db.query(Challenge).filter(Challenge.domain == domain)
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
        challenge_id = "CHL-" + datetime.utcnow().strftime("%Y") + "-" + str(uuid.uuid4().hex[:6]).upper()
        challenge = Challenge(
            id=challenge_id,
            title=title_hint or "Civic Issue Report",
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

    # Persist Evidence Row
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

    # Record Candidate Relations
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

    # Update counts
    social_sources = sum(1 for e in all_evidences if e.source in ["twitter", "social"])
    citizen_sources = sum(1 for e in all_evidences if e.source in ["citizen", "field_agent", "unknown"])
    challenge.source_counts = {
        "social": social_sources,
        "citizen": citizen_sources
    }
    challenge.complaint_count = len(all_evidences)

    # 8. Explainable Priority Scoring
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
        "classification": "heuristic/keyword-rules-v1",
        "embeddings": "deterministic/hash-384d",
        "summarization": "extractive/groq-fallback"
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
    On-demand re-analysis of an existing Challenge using lightweight components.
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        return {"status": "error", "message": f"Challenge {challenge_id} not found"}

    evidences = db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == challenge_id).all()
    if evidences:
        combined_text = "\n".join([e.clean_text or e.raw_text for e in evidences])
    else:
        combined_text = f"{challenge.title}. {challenge.official_description or challenge.ai_generated_summary or challenge.location}"
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
    class_res = classify_heuristic(clean_txt)
    domain = class_res["domain"]
    subdomain = class_res.get("subdomain")

    loc_metadata = {"latitude": challenge.lat, "longitude": challenge.lng}
    loc_res = extract_entities_gazetteer(clean_txt, loc_metadata)
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
        "classification": "heuristic/keyword-rules-v1",
        "embeddings": "deterministic/hash-384d",
        "summarization": "extractive/groq-fallback"
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
