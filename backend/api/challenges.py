"""
api/challenges.py — CRUD & NLP Pipeline integration routes for Challenges (SIH 2026).
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
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
    RoutingBatchOut,
    AssignmentOut,
    ChallengeEvidenceOut,
    ChallengeAnalysisOut,
    ChallengeRelationOut,
    EvidenceIngestRequest,
    PipelineProcessResponse
)
from pipeline.orchestrator import process_evidence, analyze_challenge

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
            (Challenge.official_description.ilike(search)) |
            (Challenge.ai_generated_summary.ilike(search)) |
            (Challenge.id.ilike(search))
        )

    challenges = q.order_by(Challenge.created_at.desc()).all()
    
    # Populate active_deadline for routed challenges
    for c in challenges:
        if c.status == "routed":
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
    """
    Creates/links a challenge by running input data through the full NLP Pipeline
    (Cleaning, Zero-Shot Classification, Location Extraction, Embeddings, Deduplication, Canonical Summarization, and Priority Scoring).
    """
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
        # Run on-demand analysis if none exists yet
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
    db: Session = Depends(get_db)
):
    q = db.query(RoutingInvitation)
    if org_id:
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
    import json
    
    invitation = db.query(RoutingInvitation).filter(RoutingInvitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
        
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
                {"title": "Solution Proposal Submission", "status": "in_progress"},
                {"title": "Prototype Development & Pilot", "status": "pending"},
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
def decline_invitation(invitation_id: str, db: Session = Depends(get_db)):
    invitation = db.query(RoutingInvitation).filter(RoutingInvitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
        
    invitation.status = "rejected"
    invitation.responded_at = datetime.utcnow()
    db.commit()
    return {"message": "Invitation declined", "invitation_id": invitation.id, "status": "rejected"}
