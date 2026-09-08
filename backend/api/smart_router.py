"""
api/smart_router.py — Matches challenges to universities and industries (SIH 2026).
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import Challenge, Match, Organization, Project
from db.schemas import MatchOut, MatchAccept

router = APIRouter(prefix="/api/matches", tags=["smart-router"])

@router.post("/generate/{challenge_id}", response_model=List[MatchOut])
def generate_matches(challenge_id: str, db: Session = Depends(get_db)):
    """
    Mock Smart Router logic.
    For a given challenge, it creates deterministic matches against seeded organizations.
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
        
    # Check if matches already exist
    existing = db.query(Match).filter(Match.challenge_id == challenge_id).all()
    if existing:
        return existing

    # Dynamic Semantic Matchmaking Engine
    new_matches = []
    
    # 1. Fetch active universities
    universities = db.query(Organization).filter(
        Organization.type == "University",
        Organization.status == "ACTIVE"
    ).all()
    
    # 2. Extract context from challenge
    c_text = f"{challenge.title} {challenge.description} {challenge.domain} {challenge.department}".lower()
    import re
    keywords = set(re.findall(r'\b[a-z]{4,}\b', c_text))
    
    c_domain = (challenge.domain or "").lower()
    c_location = (challenge.location or "").lower()
    
    scored_unis = []
    
    for uni in universities:
        score = 40 # Base score
        reasons = []
        
        uni_domains = (uni.research_domains or "").lower()
        uni_output = (uni.research_output or "").lower()
        uni_district = (uni.district or "").lower()
        
        # Domain Direct Match
        c_domains = [d.strip().lower() for d in (challenge.domain or "").split(",") if d.strip()]
        u_domains_list = [d.strip().lower() for d in (uni.research_domains or "").split(",") if d.strip()]
        
        domain_overlap = set(c_domains).intersection(set(u_domains_list))
        if domain_overlap:
            score += 30 + (len(domain_overlap) * 5) # Boost for multiple matches
            reasons.append(f"Strong domain match ({', '.join([d.title() for d in domain_overlap])})")
        
        # Keyword matches in domains
        domain_kw_matches = sum(1 for kw in keywords if kw in uni_domains)
        if domain_kw_matches > 0:
            added = min(20, domain_kw_matches * 5)
            score += added
            if added > 0 and not reasons:
                reasons.append("Relevant specialization areas")
                
        # Keyword matches in previous output
        output_kw_matches = sum(1 for kw in keywords if kw in uni_output)
        if output_kw_matches > 0:
            added = min(25, output_kw_matches * 5)
            score += added
            if added > 0:
                reasons.append("Prior research output in this topic")
                
        # Geographic Proximity
        if uni_district and uni_district in c_location:
            score += 15
            reasons.append(f"Geographic proximity ({uni.district})")
            
        score = min(99, score)
        
        # Recommend if score is above threshold
        if score >= 55:
            reason_str = " • ".join(reasons) if reasons else "General research capacity available"
            scored_unis.append((score, uni, reason_str))
            
    # Sort descending by score and pick top 7
    scored_unis.sort(key=lambda x: x[0], reverse=True)
    
    for score, uni, reason in scored_unis[:7]:
        new_matches.append(Match(
            id=str(uuid.uuid4()), 
            challenge_id=challenge_id, 
            org_id=uni.id,
            match_score=score, 
            match_reason=reason,
            status="suggested"
        ))
            
    if new_matches:
        db.bulk_save_objects(new_matches)
        db.commit()
        
    return db.query(Match).filter(Match.challenge_id == challenge_id).order_by(Match.match_score.desc()).all()

@router.patch("/{match_id}", response_model=MatchOut)
def update_match_status(match_id: str, req: MatchAccept, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    match.status = req.status
    
    # If accepted, create a project automatically
    if req.status == "accepted":
        challenge = match.challenge
        challenge.status = "matched"
        
        # Prevent creating multiple projects for the same challenge
        existing_project = db.query(Project).filter(Project.challenge_id == challenge.id).first()
        if not existing_project:
            import json
            new_project = Project(
                id=str(uuid.uuid4()),
                challenge_id=challenge.id,
                status="prototype",
                milestones_json=json.dumps([
                    {"title": "Requirements Gathering", "status": "pending"},
                    {"title": "Prototype Development", "status": "pending"}
                ])
            )
            db.add(new_project)
            
    db.commit()
    db.refresh(match)
    return match
