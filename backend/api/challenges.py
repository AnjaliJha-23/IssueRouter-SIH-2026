"""
api/challenges.py — CRUD routes for Challenges & Evidence (SIH 2026).
"""
import uuid
import json
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from db.database import get_db
from db.models import Challenge, User, Organization, RoutingBatch, RoutingInvitation, Project, ChallengeEvidence
from db.schemas import ChallengeOut, ChallengeCreate, ChallengeVerify, ChallengeRouteRequest, RoutingBatchOut, AssignmentOut
from api.auth import get_current_user, get_optional_current_user, require_roles

router = APIRouter(prefix="/api/challenges", tags=["challenges"])

@router.get("/", response_model=List[ChallengeOut])
def list_challenges(
    status: Optional[str] = Query(None, description="Filter by status"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    district: Optional[str] = Query(None, description="Filter by district"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    search: Optional[str] = Query(None, description="Search query"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Challenge)
    
    if status and status != 'all':
        q = q.filter(Challenge.status == status)
    if domain:
        q = q.filter(Challenge.domain == domain)
    if district:
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
        search_pattern = f"%{search}%"
        q = q.filter(
            (Challenge.title.ilike(search_pattern)) |
            (Challenge.official_description.ilike(search_pattern)) |
            (Challenge.ai_generated_summary.ilike(search_pattern)) |
            (Challenge.id.ilike(search_pattern))
        )

    challenges = q.order_by(Challenge.created_at.desc()).all()
    
    # Populate active_deadline for routed challenges
    for c in challenges:
        if c.status == "routed":
            batch = db.query(RoutingBatch).filter(
                RoutingBatch.challenge_id == c.id,
                RoutingBatch.status == "active"
            ).order_by(desc(RoutingBatch.created_at)).first()
            if batch:
                c.active_deadline = batch.deadline
                
    return challenges

@router.get("/my", response_model=List[ChallengeOut])
def get_my_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve ONLY the challenges submitted by the authenticated citizen/user."""
    challenges = db.query(Challenge).filter(
        Challenge.created_by == current_user.id
    ).order_by(Challenge.created_at.desc()).all()

    for c in challenges:
        if c.status == "routed":
            batch = db.query(RoutingBatch).filter(
                RoutingBatch.challenge_id == c.id,
                RoutingBatch.status == "active"
            ).order_by(desc(RoutingBatch.created_at)).first()
            if batch:
                c.active_deadline = batch.deadline

    return challenges

@router.post("/upload-photos", response_model=List[str])
async def upload_challenge_photos(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Validates and stores up to 3 evidence photographs for citizen submissions.
    Saves to /uploads/evidence and returns accessible relative URLs.
    """
    if len(files) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 photographs allowed per challenge submission.")
    
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    max_bytes = 5 * 1024 * 1024  # 5MB
    
    uploads_dir = Path(__file__).resolve().parent.parent / "uploads" / "evidence"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    saved_urls = []

    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format '{file.content_type}'. Please upload PNG, JPEG, or WebP images."
            )
        
        content = await file.read()
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' exceeds the maximum allowed size of 5 MB."
            )
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is empty or unreadable."
            )
        
        ext = Path(file.filename or "photo.jpg").suffix.lower()
        if not ext or ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"

        safe_filename = f"ev_{uuid.uuid4().hex[:12]}{ext}"
        target_path = uploads_dir / safe_filename
        target_path.write_bytes(content)

        saved_urls.append(f"/uploads/evidence/{safe_filename}")

    return saved_urls

@router.post("/", response_model=ChallengeOut)
def create_challenge(
    req: ChallengeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new canonical challenge, tags ownership to authenticated user,
    creates linked ChallengeEvidence, and runs initial domain categorization.
    """
    if not req.title or len(req.title.strip()) < 5:
        raise HTTPException(status_code=400, detail="Challenge title must be at least 5 characters.")
    if not req.description or len(req.description.strip()) < 15:
        raise HTTPException(status_code=400, detail="Please provide a meaningful description of the issue (at least 15 characters).")
    if not req.location or len(req.location.strip()) < 2:
        raise HTTPException(status_code=400, detail="Location is required.")

    # Domain categorization heuristic
    desc_lower = (req.title + " " + req.description).lower()
    assigned_domain = "Civic Infrastructure"
    assigned_priority = 65
    
    if any(k in desc_lower for k in ["health", "doctor", "disease", "hospital", "medicine", "clinic", "phc", "ambulance", "patient", "medical"]):
        assigned_domain = "HealthTech"
        assigned_priority = 85
    elif any(k in desc_lower for k in ["school", "education", "student", "teacher", "classroom", "college", "dropout", "literacy"]):
        assigned_domain = "EdTech"
        assigned_priority = 70
    elif any(k in desc_lower for k in ["water", "drain", "sewage", "drinking", "pipeline", "handpump", "contamination", "arsenic", "fluoride"]):
        assigned_domain = "Water Management"
        assigned_priority = 80
    elif any(k in desc_lower for k in ["farmer", "crop", "agriculture", "fertilizer", "soil", "irrigation", "paddy"]):
        assigned_domain = "AgriTech"
        assigned_priority = 75
    elif any(k in desc_lower for k in ["electricity", "power", "blackout", "solar", "transformer", "grid"]):
        assigned_domain = "Clean Energy"
        assigned_priority = 75
    elif any(k in desc_lower for k in ["road", "pothole", "bridge", "traffic", "street light", "transport"]):
        assigned_domain = "Urban Infrastructure"
        assigned_priority = 70

    challenge_id = f"CHL-2026-{uuid.uuid4().hex[:6].upper()}"

    new_challenge = Challenge(
        id=challenge_id,
        title=req.title.strip(),
        official_description=req.description.strip(),
        location=req.location.strip(),
        district=req.district,
        block=req.block,
        lat=req.lat or 23.3441,
        lng=req.lng or 85.3096,
        domain=assigned_domain,
        priority_score=assigned_priority,
        status="pending_verification",
        source_counts={"social": 0, "citizen": 1},
        ai_confidence=0.94,
        duplicate_risk=0.03,
        verified=False,
        media_urls=req.media_urls or [],
        created_by=current_user.id
    )
    db.add(new_challenge)

    # Persist as canonical ChallengeEvidence
    evidence_id = f"ev-{uuid.uuid4().hex[:8]}"
    evidence = ChallengeEvidence(
        id=evidence_id,
        challenge_id=new_challenge.id,
        source="citizen",
        raw_text=f"{req.title}: {req.description}",
        clean_text=f"{req.title}. {req.description}",
        media_urls=req.media_urls or [],
        submitted_lat=req.lat,
        submitted_lng=req.lng
    )
    db.add(evidence)

    db.commit()
    db.refresh(new_challenge)
    return new_challenge

@router.get("/assignments", response_model=List[AssignmentOut])
def list_assignments(
    org_id: Optional[str] = Query(None, description="Filter assignments by University organization ID"),
    status: Optional[str] = Query(None, description="Filter assignments by status: pending, accepted, rejected, all"),
    current_user: User = Depends(require_roles("Gov", "University")),
    db: Session = Depends(get_db)
):
    q = db.query(RoutingInvitation)
    # If university user, enforce seeing only own organization invitations
    if current_user.role == "University":
        q = q.filter(RoutingInvitation.org_id == current_user.org_id)
    elif org_id:
        q = q.filter(RoutingInvitation.org_id == org_id)

    if status and status != "all":
        q = q.filter(RoutingInvitation.status == status)

    invitations = q.order_by(RoutingInvitation.created_at.desc()).all()
    results = []
    for inv in invitations:
        batch = inv.batch
        if not batch or not batch.challenge:
            continue
        
        total_unis = len(batch.invitations) if batch.invitations else 1

        results.append(AssignmentOut(
            assignment_id=inv.id,
            batch_id=batch.id,
            org_id=inv.org_id,
            status=inv.status,
            created_at=inv.created_at,
            responded_at=inv.responded_at,
            deadline=batch.deadline,
            government_note=batch.note,
            total_assigned_universities=total_unis,
            challenge=batch.challenge
        ))
    return results

@router.get("/{challenge_id}", response_model=ChallengeOut)
def get_challenge(
    challenge_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Ownership privacy check:
    # If challenge is still pending verification and not verified, only creator or Gov can view
    if not challenge.verified and challenge.status == "pending_verification":
        if current_user and (current_user.role == "Gov" or current_user.id == challenge.created_by):
            pass # allowed
        else:
            raise HTTPException(status_code=404, detail="Challenge not found or pending verification.")
            
    return challenge

@router.patch("/{challenge_id}/verify", response_model=ChallengeOut)
def verify_challenge(
    challenge_id: str,
    req: ChallengeVerify,
    current_user: User = Depends(require_roles("Gov")),
    db: Session = Depends(get_db)
):
    """Only Government nodal officers can verify challenges."""
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    challenge.verified = req.verified
    if req.verified and challenge.status in ["pending_verification", "pending"]:
        challenge.status = "verified"
        challenge.verified_at = datetime.utcnow()
        challenge.verified_by = current_user.id
        
    db.commit()
    db.refresh(challenge)
    return challenge

@router.post("/{challenge_id}/route", response_model=RoutingBatchOut)
def route_challenge(
    challenge_id: str,
    req: ChallengeRouteRequest,
    current_user: User = Depends(require_roles("Gov")),
    db: Session = Depends(get_db)
):
    """Only Government nodal officers can route challenges to institutions."""
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
        
    if not req.org_ids:
        raise HTTPException(status_code=400, detail="Must provide at least one organization ID")
    
    batch_id = f"batch-{uuid.uuid4().hex[:8]}"
    new_batch = RoutingBatch(
        id=batch_id,
        challenge_id=challenge.id,
        deadline=req.deadline,
        note=req.note,
        status="active"
    )
    db.add(new_batch)
    
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
def accept_invitation(
    invitation_id: str,
    current_user: User = Depends(require_roles("University", "Gov")),
    db: Session = Depends(get_db)
):
    invitation = db.query(RoutingInvitation).filter(RoutingInvitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    if current_user.role == "University" and invitation.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized to accept invitations for other institutions.")
        
    if invitation.status != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot accept invitation in state: {invitation.status}")
        
    batch = invitation.batch
    if batch.status != "active":
        raise HTTPException(status_code=400, detail="The routing batch is no longer active.")
        
    if batch.deadline < datetime.utcnow():
        batch.status = "expired"
        invitation.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="The routing deadline has expired.")
        
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
    
    # 5. Create or associate Project record with this organization
    project = db.query(Project).filter(Project.challenge_id == challenge.id).first()
    if not project:
        project = Project(
            id=f"proj-{uuid.uuid4().hex[:8]}",
            challenge_id=challenge.id,
            org_id=invitation.org_id,
            status="prototype",
            milestones_json=json.dumps([
                {"title": "Initial Problem Analysis & Architecture", "status": "completed"},
                {"title": "Research and Prototype Submission", "status": "in_progress"},
                {"title": "Solution Submission", "status": "pending"},
                {"title": "Industry Deployment", "status": "pending"}
            ])
        )
        db.add(project)
    else:
        if not project.org_id:
            project.org_id = invitation.org_id
        if project.status == "prototype":
            project.status = "in_progress"
            
    db.commit()
    db.refresh(project)
    return {
        "message": "Invitation accepted successfully",
        "challenge_id": challenge.id,
        "project_id": project.id,
        "status": "accepted"
    }

@router.post("/invitations/{invitation_id}/decline")
def decline_invitation(
    invitation_id: str,
    current_user: User = Depends(require_roles("University", "Gov")),
    db: Session = Depends(get_db)
):
    invitation = db.query(RoutingInvitation).filter(RoutingInvitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    if current_user.role == "University" and invitation.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized to decline invitations for other institutions.")
        
    invitation.status = "rejected"
    invitation.responded_at = datetime.utcnow()
    db.commit()
    return {"message": "Invitation declined", "invitation_id": invitation.id, "status": "rejected"}
