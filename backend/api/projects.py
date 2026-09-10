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
from db.models import Project, Proposal, Challenge, Organization, User
from db.schemas import ProjectOut, ProposalDetailOut, ProposalCreate, MilestonesUpdateRequest, ProjectStatusUpdate
from api.auth import require_roles

from api.proposals import PROPOSAL_STATE_OVERRIDES

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
    current_user: User = Depends(require_roles("Gov", "University", "Industry")),
    db: Session = Depends(get_db)
):
    q = db.query(Project)
    if current_user.role == "University":
        q = q.filter(Project.org_id == current_user.org_id)
    elif org_id:
        q = q.filter(Project.org_id == org_id)
    projects = q.order_by(Project.created_at.desc()).all()
    
    # Sync memory overrides if any
    for p in projects:
        prop_id = f"PROP-{p.challenge_id}"
        if prop_id in PROPOSAL_STATE_OVERRIDES and p.proposal:
            ov = PROPOSAL_STATE_OVERRIDES[prop_id]
            p.proposal.funds_committed = ov.get("funds_committed", p.proposal.funds_committed)
            p.proposal.funding_status = ov.get("funding_status", p.proposal.funding_status)
            p.proposal.partners = ov.get("partners", p.proposal.partners)
            p.proposal.collaboration_status = ov.get("collaboration_status", p.proposal.collaboration_status)

    return projects

@router.get("/industry/funded")
def get_industry_funded_projects(
    funder_name: Optional[str] = Query(None),
    current_user: User = Depends(require_roles("Industry", "Gov")),
    db: Session = Depends(get_db)
):
    """Returns active projects and proposals funded by Industry CSR."""
    org_name = funder_name or (current_user.organization.name if current_user.organization else "Tata Steel CSR")
    
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    results = []
    
    for p in projects:
        prop = p.proposal
        prop_id = f"PROP-{p.challenge_id}"
        ov = PROPOSAL_STATE_OVERRIDES.get(prop_id, {})
        
        partners = ov.get("partners") or (prop.partners if prop else []) or []
        funds_committed = ov.get("funds_committed") or (prop.funds_committed if prop else 0)
        funding_status = ov.get("funding_status") or (prop.funding_status if prop else "Open for Funding")
        
        # Include if funded/partnered or if has commitments
        if funds_committed > 0 or funding_status in ["Funded", "Partially Funded"] or any(org_name.lower() in str(pt).lower() for pt in partners):
            b_num = (prop.budget_num if prop else 850000) or 850000
            rem = max(0, b_num - funds_committed)
            pct = min(100, int((funds_committed / b_num) * 100)) if b_num else 100
            
            c = p.challenge
            uni = p.organization
            
            results.append({
                "id": p.id,
                "project_id": p.id,
                "challenge_id": p.challenge_id,
                "challenge_title": c.title if c else "Civic Infrastructure Challenge",
                "department": c.department if c else "Public Works",
                "location": c.location if c else "Jharkhand",
                "domain": c.domain if c else "HealthTech",
                "priority_score": c.priority_score if c else 85,
                "university": uni.name if uni else "RIMS Ranchi",
                "faculty_lead": (prop.faculty_lead if prop else "Dr. Sharma (Research Lead)") or "Dr. Sharma (Research Lead)",
                "contact_email": prop.contact_email if prop else "sharma.biomed@rims.ac.in",
                "proposed_solution": (prop.proposed_solution if prop else (c.official_description if c else "Automated sensor-based intervention")) or "Automated sensor-based intervention",
                "trl": prop.trl if prop else "TRL-6 (Field Pilot Ready)",
                "budget_required": prop.budget_required if prop else f"₹{b_num:,}",
                "budget_num": b_num,
                "funds_committed": funds_committed,
                "remaining_budget": rem,
                "funding_percentage": pct,
                "funding_status": funding_status,
                "partners": partners if partners else [org_name],
                "milestones": json.loads(p.milestones_json) if isinstance(p.milestones_json, str) else (p.milestones_json or []),
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else datetime.utcnow().isoformat()
            })
            
    return results

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str,
    current_user: User = Depends(require_roles("Gov", "University", "Industry")),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/{project_id}/proposal", response_model=ProposalDetailOut)
def submit_or_save_proposal(
    project_id: str,
    req: ProposalCreate,
    current_user: User = Depends(require_roles("University", "Gov")),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    challenge = db.query(Challenge).filter(Challenge.id == project.challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Associated challenge not found")

    org_id = current_user.org_id if current_user.role == "University" else project.org_id
    if not org_id:
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

@router.patch("/{project_id}/milestones", response_model=ProjectOut)
def update_project_milestones(
    project_id: str,
    req: MilestonesUpdateRequest,
    current_user: User = Depends(require_roles("University", "Gov")),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role == "University" and project.org_id and current_user.org_id != project.org_id:
        raise HTTPException(status_code=403, detail="Not authorized to update milestones for other institutions' projects.")

    milestones_data = [m.model_dump() for m in req.milestones]
    project.milestones_json = json.dumps(milestones_data)

    # Automatically synchronize project status if all milestones are completed or in progress
    all_completed = all(m.get("status") == "completed" for m in milestones_data)
    any_in_progress = any(m.get("status") == "in_progress" for m in milestones_data)
    
    if all_completed:
        project.status = "deployed"
        if project.challenge and project.challenge.status != "resolved":
            project.challenge.status = "resolved"
    elif any_in_progress and project.status in ["prototype", "pending"]:
        project.status = "in_progress"

    db.commit()
    db.refresh(project)
    return project

@router.patch("/{project_id}/status", response_model=ProjectOut)
def update_project_status(
    project_id: str,
    req: ProjectStatusUpdate,
    current_user: User = Depends(require_roles("University", "Gov")),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role == "University" and project.org_id and current_user.org_id != project.org_id:
        raise HTTPException(status_code=403, detail="Not authorized to update status for other institutions' projects.")

    valid_statuses = {"prototype", "in_progress", "proposal_submitted", "field_pilot", "deployed"}
    if req.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status '{req.status}'. Must be one of {valid_statuses}")

    project.status = req.status
    if req.status == "deployed" and project.challenge:
        project.challenge.status = "resolved"

    db.commit()
    db.refresh(project)
    return project

