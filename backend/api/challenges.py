"""
api/challenges.py — CRUD & NLP Pipeline integration routes for Challenges & Evidence (SIH 2026).
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
from db.models import (
    Challenge,
    ChallengeEvidence,
    ChallengeAnalysis,
    ChallengeRelation,
    User,
    Organization,
    RoutingBatch,
    RoutingInvitation,
    Project
)
from db.schemas import (
    ChallengeOut,
    ChallengeCreate,
    ChallengeVerify,
    ChallengeRouteRequest,
    ChallengeResolveRequest,
    RoutingBatchOut,
    AssignmentOut,
    ChallengeEvidenceOut,
    ChallengeAnalysisOut,
    ChallengeRelationOut,
    EvidenceIngestRequest,
    PipelineProcessResponse
)
from api.auth import get_current_user, get_optional_current_user, require_roles
from pipeline.orchestrator import process_evidence, analyze_challenge

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
    
    # Populate active_deadline for routed and in_project challenges
    for c in challenges:
        if c.status in ["routed", "in_project"]:
            batch = db.query(RoutingBatch).filter(
                RoutingBatch.challenge_id == c.id
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
        if c.status in ["routed", "in_project"]:
            batch = db.query(RoutingBatch).filter(
                RoutingBatch.challenge_id == c.id
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
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates/links a challenge by running input data through the full NLP Pipeline
    (Cleaning, Zero-Shot Classification, Location Extraction, Embeddings, Deduplication, Canonical Summarization, and Priority Scoring).
    """
    if not req.description or len(req.description.strip()) < 5:
        raise HTTPException(status_code=400, detail="Please provide a description of the issue.")

    evidence_payload = {
        "source": req.source or "citizen",
        "title": req.title,
        "raw_text": req.description,
        "location": req.location,
        "submitted_lat": req.lat,
        "submitted_lng": req.lng
    }
    
    # Execute NLP pipeline orchestrator
    pipeline_res = process_evidence(evidence_payload, db)
    challenge_id = pipeline_res.get("challenge_id")
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=500, detail="Failed to retrieve processed challenge from NLP pipeline")
    
    # Attach user ownership and media URLs if available
    if current_user and not challenge.created_by:
        challenge.created_by = current_user.id
    if req.media_urls:
        existing_urls = challenge.media_urls or []
        for url in req.media_urls:
            if url not in existing_urls:
                existing_urls.append(url)
        challenge.media_urls = existing_urls
        db.commit()
        db.refresh(challenge)
        
    return challenge

@router.post("/ingest", response_model=PipelineProcessResponse)
def ingest_signal(req: EvidenceIngestRequest, db: Session = Depends(get_db)):
    """
    Ingest a raw civic distress alert (Twitter post, citizen report, field log)
    into the NLP pipeline and return real-time categorization, deduplication action, and priority score.
    """
    evidence_payload = {
        "source": req.source,
        "raw_text": req.raw_text,
        "submitted_lat": req.submitted_lat,
        "submitted_lng": req.submitted_lng
    }
    
    res = process_evidence(evidence_payload, db)
    return res

@router.post("/{challenge_id}/analyze")
def run_ai_analysis(challenge_id: str, db: Session = Depends(get_db)):
    """
    On-demand trigger to re-run the NLP pipeline analysis for a given challenge.
    """
    res = analyze_challenge(challenge_id, db)
    if res.get("status") == "error":
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res

@router.get("/{challenge_id}/analysis", response_model=ChallengeAnalysisOut)
def get_challenge_analysis(challenge_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full explainable AI rationale and scoring factors for a challenge.
    """
    analysis = db.query(ChallengeAnalysis).filter(ChallengeAnalysis.challenge_id == challenge_id).first()
    if not analysis:
        analyze_challenge(challenge_id, db)
        analysis = db.query(ChallengeAnalysis).filter(ChallengeAnalysis.challenge_id == challenge_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis record not found")
    return analysis

@router.get("/{challenge_id}/evidence", response_model=List[ChallengeEvidenceOut])
def list_challenge_evidence(challenge_id: str, db: Session = Depends(get_db)):
    """
    Retrieve all linked civic and social evidence records for a challenge.
    """
    evidences = db.query(ChallengeEvidence).filter(
        ChallengeEvidence.challenge_id == challenge_id
    ).order_by(ChallengeEvidence.created_at.desc()).all()
    return evidences

@router.get("/{challenge_id}/relations", response_model=List[ChallengeRelationOut])
def list_challenge_relations(challenge_id: str, db: Session = Depends(get_db)):
    """
    Retrieve candidate duplicate or related challenge relations flagged by semantic deduplication.
    """
    relations = db.query(ChallengeRelation).filter(
        (ChallengeRelation.source_challenge_id == challenge_id) |
        (ChallengeRelation.target_challenge_id == challenge_id)
    ).all()
    return relations

@router.get("/assignments", response_model=List[AssignmentOut])
def list_assignments(
    org_id: Optional[str] = Query(None, description="Filter assignments by University organization ID"),
    status: Optional[str] = Query(None, description="Filter assignments by status: pending, accepted, rejected, all"),
    current_user: User = Depends(require_roles("Gov", "University")),
    db: Session = Depends(get_db)
):
    q = db.query(RoutingInvitation)
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
    
    if not challenge.verified and challenge.status == "pending_verification":
        if current_user and (current_user.role == "Gov" or current_user.id == challenge.created_by):
            pass
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

@router.patch("/{challenge_id}/resolve", response_model=ChallengeOut)
def resolve_challenge(
    challenge_id: str,
    req: ChallengeResolveRequest,
    current_user: User = Depends(require_roles("Gov")),
    db: Session = Depends(get_db)
):
    """
    Formally resolves a challenge. Accessible by Government nodal officers.
    Marks challenge status as resolved, advances linked project to deployed,
    and completes all project milestones.
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    challenge.status = "resolved"
    challenge.verified = True

    project = db.query(Project).filter(Project.challenge_id == challenge.id).first()
    if project:
        project.status = "deployed"
        try:
            m_list = json.loads(project.milestones_json) if isinstance(project.milestones_json, str) else (project.milestones_json or [])
            for m in m_list:
                m["status"] = "completed"
            project.milestones_json = json.dumps(m_list)
        except Exception:
            pass

    db.commit()
    db.refresh(challenge)
    return challenge
