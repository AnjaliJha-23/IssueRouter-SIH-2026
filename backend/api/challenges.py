"""
api/challenges.py — CRUD routes for Challenges (SIH 2026).
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from db.models import Challenge
from db.schemas import ChallengeOut, ChallengeCreate, ChallengeVerify

router = APIRouter(prefix="/api/challenges", tags=["challenges"])

@router.get("/", response_model=List[ChallengeOut])
def list_challenges(
    status: Optional[str] = Query(None, description="Filter by status"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    verified: Optional[bool] = Query(None, description="Filter by verification status"),
    db: Session = Depends(get_db)
):
    q = db.query(Challenge)
    
    if status:
        q = q.filter(Challenge.status == status)
    if domain:
        q = q.filter(Challenge.domain == domain)
    if verified is not None:
        q = q.filter(Challenge.verified == verified)

    return q.order_by(Challenge.created_at.desc()).all()


@router.post("/", response_model=ChallengeOut)
def create_challenge(req: ChallengeCreate, db: Session = Depends(get_db)):
    # --- MOCK ML PIPELINE ---
    # In the future, this is where we call HuggingFace NLP for domain/priority
    desc_lower = req.description.lower()
    
    assigned_domain = "General"
    assigned_priority = 50
    
    if "health" in desc_lower or "doctor" in desc_lower or "disease" in desc_lower or "hospital" in desc_lower:
        assigned_domain = "HealthTech"
        assigned_priority = 85
    elif "school" in desc_lower or "education" in desc_lower:
        assigned_domain = "EdTech"
        assigned_priority = 70
    elif "water" in desc_lower or "drain" in desc_lower:
        assigned_domain = "Water Management"
        assigned_priority = 80

    new_challenge = Challenge(
        id=str(uuid.uuid4()),
        title=req.title,
        description=req.description,
        location=req.location,
        lat=req.lat,
        lng=req.lng,
        domain=assigned_domain,
        priority_score=assigned_priority,
        status="pending",
        verified=False,
        # created_by would be set via current_user in real auth
    )
    
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)
    return new_challenge


@router.get("/{challenge_id}", response_model=ChallengeOut)
def get_challenge(challenge_id: str, db: Session = Depends(get_db)):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge


@router.patch("/{challenge_id}/verify", response_model=ChallengeOut)
def verify_challenge(challenge_id: str, req: ChallengeVerify, db: Session = Depends(get_db)):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    challenge.verified = req.verified
    if req.verified and challenge.status == "pending":
        challenge.status = "verified"
        
    db.commit()
    db.refresh(challenge)
    return challenge
