"""
api/challenges.py — CRUD routes for Challenges (SIH 2026).
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from db.models import Challenge, User, Organization, RoutingBatch, RoutingInvitation
from db.schemas import ChallengeOut, ChallengeCreate, ChallengeVerify, ChallengeRouteRequest, RoutingBatchOut

router = APIRouter(prefix="/api/challenges", tags=["challenges"])

@router.get("/", response_model=List[ChallengeOut])
def list_challenges(
    status: Optional[str] = Query(None, description="Filter by status"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    district: Optional[str] = Query(None, description="Filter by district"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    search: Optional[str] = Query(None, description="Search query"),
    db: Session = Depends(get_db)
):
    q = db.query(Challenge)
    
    if status and status != 'all':
        q = q.filter(Challenge.status == status)
    if domain:
        q = q.filter(Challenge.domain == domain)
    if district:
        # Assuming location contains the district string e.g. "Ranchi"
        q = q.filter(Challenge.location.ilike(f"%{district}%"))
    if priority:
        if priority == "critical":
            q = q.filter(Challenge.priority_score >= 85)
        elif priority == "high":
            q = q.filter(Challenge.priority_score >= 70, Challenge.priority_score < 85)
        elif priority == "medium":
            q = q.filter(Challenge.priority_score >= 50, Challenge.priority_score < 70)
        elif priority == "low":
            q = q.filter(Challenge.priority_score < 50)
    if search:
        search = f"%{search}%"
        q = q.filter(
            (Challenge.title.ilike(search)) |
            (Challenge.description.ilike(search)) |
            (Challenge.id.ilike(search))
        )

    challenges = q.order_by(Challenge.created_at.desc()).all()
    
    # Populate active_deadline for routed challenges
    for c in challenges:
        if c.status == "routed":
            # Find the most recent active batch
            from sqlalchemy import desc
            batch = db.query(RoutingBatch).filter(
                RoutingBatch.challenge_id == c.id,
                RoutingBatch.status == "active"
            ).order_by(desc(RoutingBatch.created_at)).first()
            if batch:
                c.active_deadline = batch.deadline
                
    return challenges


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
        status="pending_verification",
        source_counts={"social": 1, "citizen": 1},
        ai_confidence=0.92,
        duplicate_risk=0.05,
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
    if req.verified and challenge.status == "pending_verification":
        from datetime import datetime
        challenge.status = "verified"
        challenge.verified_at = datetime.utcnow()
        challenge.verified_by = "user-gov-1" # Mock current user ID
        
    db.commit()
    db.refresh(challenge)
    return challenge

@router.post("/{challenge_id}/route", response_model=RoutingBatchOut)
def route_challenge(challenge_id: str, req: ChallengeRouteRequest, db: Session = Depends(get_db)):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
        
    if not req.org_ids:
        raise HTTPException(status_code=400, detail="Must provide at least one organization ID")
    
    # Create the batch
    batch_id = f"batch-{uuid.uuid4().hex[:8]}"
    new_batch = RoutingBatch(
        id=batch_id,
        challenge_id=challenge.id,
        deadline=req.deadline,
        note=req.note,
        status="active"
    )
    db.add(new_batch)
    
    # Create invitations
    invitations = []
    for org_id in req.org_ids:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            continue
            
        inv = RoutingInvitation(
            id=f"inv-{uuid.uuid4().hex[:8]}",
            batch_id=batch_id,
            org_id=org.id,
            status="pending"
        )
        invitations.append(inv)
        
    if invitations:
        db.bulk_save_objects(invitations)
    
    challenge.status = "routed"
    db.commit()
    db.refresh(new_batch)
    return new_batch

@router.post("/invitations/{invitation_id}/accept")
def accept_invitation(invitation_id: str, db: Session = Depends(get_db)):
    from datetime import datetime
    
    invitation = db.query(RoutingInvitation).filter(RoutingInvitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
        
    if invitation.status != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot accept invitation in state: {invitation.status}")
        
    batch = invitation.batch
    if batch.status != "active":
        raise HTTPException(status_code=400, detail="The routing batch is no longer active.")
        
    if batch.deadline < datetime.utcnow():
        # Clean up state since it's expired
        batch.status = "expired"
        invitation.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="The routing deadline has expired.")
        
    # Atomic first-accept-wins logic
    now = datetime.utcnow()
    
    # 1. Accept this invitation
    invitation.status = "accepted"
    invitation.responded_at = now
    
    # 2. Close all other pending invitations in this batch
    other_invitations = db.query(RoutingInvitation).filter(
        RoutingInvitation.batch_id == batch.id,
        RoutingInvitation.id != invitation.id,
        RoutingInvitation.status == "pending"
    ).all()
    
    for other in other_invitations:
        other.status = "closed"
        
    # 3. Mark batch as completed
    batch.status = "completed"
    
    # 4. Advance challenge state
    challenge = batch.challenge
    challenge.status = "in_project"
    
    # In a full system, we would create the Project record here as well.
    # We leave Project creation for the future scope.
    
    db.commit()
    return {"message": "Invitation accepted successfully", "challenge_id": challenge.id}
