"""
db/schemas.py — Pydantic response models for IssueRouter API (SIH 2026).
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel

# ── Base Entities ────────────────────────────────────────────────────────
class OrganizationOut(BaseModel):
    id: str
    name: str
    type: str
    location: Optional[str]
    district: Optional[str] = None
    research_domains: Optional[str] = None
    research_specializations: Optional[str] = None
    research_output: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrganizationCreate(BaseModel):
    name: str
    type: str = "University"
    location: Optional[str] = None
    district: Optional[str] = None
    research_domains: Optional[str] = None
    research_specializations: Optional[str] = None
    research_output: Optional[str] = None
    status: str = "ACTIVE"

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    district: Optional[str] = None
    research_domains: Optional[str] = None
    research_specializations: Optional[str] = None
    research_output: Optional[str] = None
    status: Optional[str] = None

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    org_id: Optional[str]
    organization: Optional[OrganizationOut] = None

    class Config:
        from_attributes = True

# ── Project ────────────────────────────────────────────────────────────────
class ProjectOut(BaseModel):
    id: str
    challenge_id: str
    status: str
    milestones_json: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True

# ── Match ──────────────────────────────────────────────────────────────────
class MatchOut(BaseModel):
    id: str
    challenge_id: str
    org_id: str
    match_score: int
    match_reason: str
    status: str
    organization: Optional[OrganizationOut] = None

    class Config:
        from_attributes = True

class MatchAccept(BaseModel):
    status: str # 'accepted' or 'rejected'

# ── Challenge ──────────────────────────────────────────────────────────────
class ChallengeBase(BaseModel):
    id: str
    title: str
    description: str
    domain: Optional[str]
    status: str
    priority_score: Optional[int]
    location: str
    lat: Optional[float]
    lng: Optional[float]
    department: Optional[str]
    complaint_count: int = 1
    source_counts: Optional[Any] = None
    ai_confidence: Optional[float] = None
    duplicate_risk: Optional[float] = None
    rt_reach: int = 0
    trend: str = "stable"
    created_by: Optional[str]
    verified: bool
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChallengeOut(ChallengeBase):
    creator: Optional[UserOut] = None
    matches: List[MatchOut] = []
    project: Optional[ProjectOut] = None
    active_deadline: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChallengeCreate(BaseModel):
    title: str
    description: str
    location: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class ChallengeVerify(BaseModel):
    verified: bool

class ChallengeRouteRequest(BaseModel):
    org_ids: List[str]
    deadline: datetime
    note: Optional[str] = None

class RoutingInvitationOut(BaseModel):
    id: str
    org_id: str
    status: str
    responded_at: Optional[datetime]
    created_at: datetime
    organization: Optional[OrganizationOut] = None

    class Config:
        from_attributes = True

class RoutingBatchOut(BaseModel):
    id: str
    challenge_id: str
    deadline: datetime
    note: Optional[str]
    status: str
    created_at: datetime
    invitations: List[RoutingInvitationOut] = []

    class Config:
        from_attributes = True

# ── Stats ──────────────────────────────────────────────────────────────────
class StatsOverviewOut(BaseModel):
    total_challenges: int
    pending_verification: int
    matched: int
    in_project: int
    resolved: int
    avg_priority: float

class LocationPointOut(BaseModel):
    id: str
    title: str
    location: str
    lat: Optional[float]
    lng: Optional[float]
    priority_score: Optional[int]
    status: str

class LocationsOut(BaseModel):
    locations: List[LocationPointOut]
