"""
api/universities.py — CRUD routes for Universities (SIH 2026).
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from db.models import Organization, User
from db.schemas import OrganizationOut, OrganizationCreate, OrganizationUpdate
from api.auth import require_roles

router = APIRouter(prefix="/api/universities", tags=["universities"])

@router.get("/", response_model=List[OrganizationOut])
def list_universities(
    status: Optional[str] = Query(None, description="Filter by status"),
    domain: Optional[str] = Query(None, description="Filter by domain keyword"),
    district: Optional[str] = Query(None, description="Filter by district"),
    search: Optional[str] = Query(None, description="Search query by name"),
    current_user: User = Depends(require_roles("Gov", "University", "Industry")),
    db: Session = Depends(get_db)
):
    q = db.query(Organization).filter(Organization.type == "University")
    
    if status and status != 'all':
        q = q.filter(Organization.status == status)
    if domain:
        q = q.filter(Organization.research_domains.ilike(f"%{domain}%"))
    if district:
        q = q.filter(Organization.district.ilike(f"%{district}%"))
    if search:
        q = q.filter(Organization.name.ilike(f"%{search}%"))

    return q.order_by(Organization.name.asc()).all()

@router.get("/{org_id}", response_model=OrganizationOut)
def get_university(
    org_id: str,
    current_user: User = Depends(require_roles("Gov", "University", "Industry")),
    db: Session = Depends(get_db)
):
    org = db.query(Organization).filter(Organization.id == org_id, Organization.type == "University").first()
    if not org:
        raise HTTPException(status_code=404, detail="University not found")
    return org

@router.post("/", response_model=OrganizationOut)
def create_university(
    req: OrganizationCreate,
    current_user: User = Depends(require_roles("Gov")),
    db: Session = Depends(get_db)
):
    existing = db.query(Organization).filter(Organization.name == req.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization with this name already exists")
        
    new_org = Organization(
        id=f"org-{uuid.uuid4().hex[:8]}",
        name=req.name,
        type="University",
        location=req.location,
        district=req.district,
        research_domains=req.research_domains,
        research_specializations=req.research_specializations,
        research_output=req.research_output,
        status=req.status
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org

@router.put("/{org_id}", response_model=OrganizationOut)
def update_university(
    org_id: str,
    req: OrganizationUpdate,
    current_user: User = Depends(require_roles("Gov")),
    db: Session = Depends(get_db)
):
    org = db.query(Organization).filter(Organization.id == org_id, Organization.type == "University").first()
    if not org:
        raise HTTPException(status_code=404, detail="University not found")
        
    update_data = req.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)
        
    db.commit()
    db.refresh(org)
    return org

@router.patch("/{org_id}/status", response_model=OrganizationOut)
def update_university_status(
    org_id: str,
    status: str,
    current_user: User = Depends(require_roles("Gov")),
    db: Session = Depends(get_db)
):
    org = db.query(Organization).filter(Organization.id == org_id, Organization.type == "University").first()
    if not org:
        raise HTTPException(status_code=404, detail="University not found")
        
    org.status = status
    db.commit()
    db.refresh(org)
    return org
