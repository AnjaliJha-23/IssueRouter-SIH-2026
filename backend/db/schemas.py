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

# ── Proposal ───────────────────────────────────────────────────────────────
class ProposalDetailOut(BaseModel):
    id: str
    project_id: str
    challenge_id: str
    org_id: str
    title: str
    problem_understanding: Optional[str] = None
    proposed_solution: str
    approach_methodology: Optional[str] = None
    trl: str = "TRL-6 (Field Pilot Ready)"
    budget_required: str
    budget_num: int
    impact_metrics: Optional[str] = None
    timeline: Optional[str] = None
    resources_needed: Optional[str] = None
    faculty_lead: Optional[str] = None
    contact_email: Optional[str] = None
    team_members: Optional[str] = None
    evidence_research: Optional[str] = None
    status: str = "submitted"
    funding_status: str = "Open for Funding"
    collaboration_status: str = "Seeking Industry Partner"
    funds_committed: int = 0
    partners: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProposalCreate(BaseModel):
    solution_title: str
    problem_understanding: Optional[str] = None
    proposed_solution: str
    approach_methodology: Optional[str] = None
    trl: Optional[str] = "TRL-6 (Field Pilot Ready)"
    budget_required: str
    budget_num: Optional[int] = None
    impact_metrics: Optional[str] = None
    timeline: Optional[str] = None
    resources_needed: Optional[str] = None
    faculty_lead: Optional[str] = None
    contact_email: Optional[str] = None
    team_members: Optional[str] = None
    evidence_research: Optional[str] = None
    is_draft: Optional[bool] = False

# ── Project ────────────────────────────────────────────────────────────────
class ProjectOut(BaseModel):
    id: str
    challenge_id: str
    org_id: Optional[str] = None
    status: str
    milestones_json: Optional[Any] = None
    created_at: datetime
    organization: Optional[OrganizationOut] = None
    challenge: Optional[ChallengeBase] = None
    proposal: Optional[ProposalDetailOut] = None

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

# ── Evidence & NLP Pipeline Schemas ─────────────────────────────────────────
class ChallengeEvidenceOut(BaseModel):
    id: str
    challenge_id: Optional[str] = None
    source: str
    raw_text: str
    clean_text: str
    media_urls: Optional[List[str]] = None
    submitted_lat: Optional[float] = None
    submitted_lng: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChallengeAnalysisOut(BaseModel):
    id: str
    challenge_id: str
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    domain_scores: Optional[Any] = None
    priority_score: Optional[int] = None
    priority_factors: Optional[Any] = None
    evidence_confidence: Optional[float] = None
    trend: Optional[str] = None
    explanation: Optional[str] = None
    model_versions: Optional[Any] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        protected_namespaces = ()

class ChallengeRelationOut(BaseModel):
    id: str
    source_challenge_id: str
    target_challenge_id: str
    similarity_score: float
    status: str = "pending"
    created_at: datetime

    class Config:
        from_attributes = True

# ── Challenge ──────────────────────────────────────────────────────────────
class ChallengeBase(BaseModel):
    id: str
    title: str
    description: str
    official_description: Optional[str] = None
    ai_generated_summary: Optional[str] = None
    domain: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    status: str
    priority_score: Optional[int] = None
    location: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    department: Optional[str] = None
    complaint_count: int = 1
    source_counts: Optional[Any] = None
    ai_confidence: Optional[float] = None
    duplicate_risk: Optional[float] = None
    rt_reach: int = 0
    trend: str = "stable"
    created_by: Optional[str] = None
    verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    media_urls: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChallengeOut(ChallengeBase):
    creator: Optional[UserOut] = None
    matches: List[MatchOut] = []
    project: Optional[ProjectOut] = None
    active_deadline: Optional[datetime] = None
    analysis: Optional[ChallengeAnalysisOut] = None
    evidence: List[ChallengeEvidenceOut] = []

    class Config:
        from_attributes = True

class ChallengeCreate(BaseModel):
    title: Optional[str] = None
    description: str
    location: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    media_urls: Optional[List[str]] = None
    source: Optional[str] = "citizen"

class EvidenceIngestRequest(BaseModel):
    source: str = "citizen"  # "citizen" | "twitter" | "field_agent"
    raw_text: str
    submitted_lat: Optional[float] = None
    submitted_lng: Optional[float] = None

class PipelineProcessResponse(BaseModel):
    status: str
    action: str  # "link" | "flag_related" | "new_challenge"
    challenge_id: str
    priority_score: Optional[int] = None
    domain: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    summary_title: Optional[str] = None
    summary_description: Optional[str] = None
    confidence: Optional[float] = None
    similarity_score: Optional[float] = None
    candidate_relations: List[Any] = []
    analysis: Optional[ChallengeAnalysisOut] = None

class ChallengeVerify(BaseModel):
    verified: bool

class ChallengeRouteRequest(BaseModel):
    org_ids: List[str]
    deadline: datetime
    note: Optional[str] = None

class ChallengeResolveRequest(BaseModel):
    resolution_summary: Optional[str] = "Solution field-tested and deployed successfully in community."
    impact_verified: Optional[bool] = True

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

class AssignmentOut(BaseModel):
    assignment_id: str
    batch_id: str
    org_id: str
    status: str
    created_at: datetime
    responded_at: Optional[datetime] = None
    deadline: datetime
    government_note: Optional[str] = None
    total_assigned_universities: int = 1
    challenge: ChallengeBase

    class Config:
        from_attributes = True

ProjectOut.model_rebuild()
ChallengeOut.model_rebuild()
AssignmentOut.model_rebuild()

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
