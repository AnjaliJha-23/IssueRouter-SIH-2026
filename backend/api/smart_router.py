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

    # Mock Matchmaking Engine
    new_matches = []
    if challenge.domain == "HealthTech":
        rims = db.query(Organization).filter(Organization.name == "RIMS Ranchi").first()
        tata = db.query(Organization).filter(Organization.name == "Tata Steel CSR").first()
        
        if rims:
            new_matches.append(Match(
                id=str(uuid.uuid4()), challenge_id=challenge_id, org_id=rims.id,
                match_score=94, match_reason="High domain expertise in HealthTech and proximity to location.",
                status="suggested"
            ))
        if tata:
            new_matches.append(Match(
                id=str(uuid.uuid4()), challenge_id=challenge_id, org_id=tata.id,
                match_score=82, match_reason="Available CSR funding for healthcare pilots.",
                status="suggested"
            ))
            
    if new_matches:
        db.bulk_save_objects(new_matches)
        db.commit()
        
    return db.query(Match).filter(Match.challenge_id == challenge_id).all()

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
