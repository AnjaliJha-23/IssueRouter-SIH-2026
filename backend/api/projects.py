"""
api/projects.py — CRUD routes for Projects & University Proposals (SIH 2026).
"""
import uuid
import json
import re
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from db.models import Project, Proposal, Challenge, Organization
from db.schemas import ProjectOut, ProposalDetailOut, ProposalCreate

router = APIRouter(prefix="/api/projects", tags=["projects"])

def _parse_budget_num(val: Optional[str], default_num: Optional[int] = None) -> int:
    if default_num is not None and default_num > 0:
        return default_num
    if not val:
        return 750000
    digits = re.sub(r'[^\d]', '', str(val))
    return int(digits) if digits else 750000

@router.get("/", response_model=List[ProjectOut])
def list_projects(
    org_id: Optional[str] = Query(None, description="Filter projects by University organization ID"),
    db: Session = Depends(get_db)
):
    q = db.query(Project)
    if org_id:
        q = q.filter(Project.org_id == org_id)
    return q.order_by(Project.created_at.desc()).all()

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/{project_id}/proposal", response_model=ProposalDetailOut)
def submit_or_save_proposal(project_id: str, req: ProposalCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    challenge = db.query(Challenge).filter(Challenge.id == project.challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Associated challenge not found")

    org_id = project.org_id
    if not org_id:
        # Fallback to university org if not set
        first_uni = db.query(Organization).filter(Organization.type == "University").first()
        org_id = first_uni.id if first_uni else "org-univ-1"
        project.org_id = org_id

    budget_num = _parse_budget_num(req.budget_required, req.budget_num)
    budget_req_str = req.budget_required
    if not budget_req_str.startswith("₹") and not budget_req_str.lower().startswith("inr"):
        budget_req_str = f"₹{budget_num:,}"

    status_str = "draft" if req.is_draft else "submitted"

    # Check if a proposal already exists for this project
    existing_proposal = db.query(Proposal).filter(Proposal.project_id == project.id).first()

    if existing_proposal:
        existing_proposal.title = req.solution_title
        existing_proposal.problem_understanding = req.problem_understanding
        existing_proposal.proposed_solution = req.proposed_solution
        existing_proposal.approach_methodology = req.approach_methodology
        existing_proposal.trl = req.trl or existing_proposal.trl or "TRL-6 (Field Pilot Ready)"
        existing_proposal.budget_required = budget_req_str
        existing_proposal.budget_num = budget_num
        existing_proposal.impact_metrics = req.impact_metrics
        existing_proposal.timeline = req.timeline
        existing_proposal.resources_needed = req.resources_needed
        existing_proposal.faculty_lead = req.faculty_lead
        existing_proposal.contact_email = req.contact_email
        existing_proposal.team_members = req.team_members
        existing_proposal.evidence_research = req.evidence_research
        existing_proposal.status = status_str
        existing_proposal.updated_at = datetime.utcnow()
        prop = existing_proposal
    else:
        prop_id = f"PROP-{challenge.id}"
        prop = Proposal(
            id=prop_id,
            project_id=project.id,
            challenge_id=challenge.id,
            org_id=org_id,
            title=req.solution_title,
            problem_understanding=req.problem_understanding,
            proposed_solution=req.proposed_solution,
            approach_methodology=req.approach_methodology,
            trl=req.trl or "TRL-6 (Field Pilot Ready)",
            budget_required=budget_req_str,
            budget_num=budget_num,
            impact_metrics=req.impact_metrics,
            timeline=req.timeline,
            resources_needed=req.resources_needed,
            faculty_lead=req.faculty_lead,
            contact_email=req.contact_email,
            team_members=req.team_members,
            evidence_research=req.evidence_research,
            status=status_str,
            funding_status="Open for Funding",
            collaboration_status="Seeking Industry Partner",
            funds_committed=0,
            partners=[],
            created_at=datetime.utcnow()
        )
        db.add(prop)

    # Update project status and milestones
    if not req.is_draft:
        project.status = "proposal_submitted"
        try:
            m_list = json.loads(project.milestones_json) if isinstance(project.milestones_json, str) else (project.milestones_json or [])
            for m in m_list:
                if "proposal" in m.get("title", "").lower():
                    m["status"] = "completed"
            project.milestones_json = json.dumps(m_list)
        except Exception:
            pass

    db.commit()
    db.refresh(prop)
    return prop
