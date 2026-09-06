"""
db/models.py — SQLAlchemy ORM models for IssueRouter (SIH 2026).
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False) # e.g., 'Gov', 'University', 'Industry'
    location = Column(String, nullable=True)
    
    # New fields for University Directory
    district = Column(String, nullable=True)
    research_domains = Column(String, nullable=True)
    research_specializations = Column(String, nullable=True)
    research_output = Column(Text, nullable=True)
    status = Column(String, default="ACTIVE") # ACTIVE, INACTIVE, PENDING_REVIEW
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = relationship("User", back_populates="organization")
    matches = relationship("Match", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) # 'Citizen', 'Gov', 'University', 'Industry'
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True)

    organization = relationship("Organization", back_populates="users")
    challenges = relationship("Challenge", foreign_keys="[Challenge.created_by]", back_populates="creator")

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    official_description = Column(Text, nullable=True) # Edited by human
    ai_generated_summary = Column(Text, nullable=True) # Maintained by pipeline
    domain = Column(String, nullable=True) 
    status = Column(String, default="pending_verification") 
    priority_score = Column(Integer, nullable=True)
    
    location = Column(String, nullable=False)
    district = Column(String, nullable=True)
    block = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    
    department = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    verified_by = Column(String, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", foreign_keys=[created_by], back_populates="challenges")
    matches = relationship("Match", back_populates="challenge")
    project = relationship("Project", back_populates="challenge", uselist=False)
    
    evidence = relationship("ChallengeEvidence", back_populates="challenge")
    analysis = relationship("ChallengeAnalysis", back_populates="challenge", uselist=False)

class ChallengeEvidence(Base):
    __tablename__ = "challenge_evidence"
    
    id = Column(String, primary_key=True, index=True)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=True) # Can be null if flagged related but not linked
    source = Column(String, nullable=False) # "twitter", "citizen", etc.
    raw_text = Column(Text, nullable=False)
    clean_text = Column(Text, nullable=False)
    embedding_json = Column(JSON, nullable=True) # JSON list of floats
    submitted_lat = Column(Float, nullable=True)
    submitted_lng = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    challenge = relationship("Challenge", back_populates="evidence")

class ChallengeAnalysis(Base):
    __tablename__ = "challenge_analysis"
    
    id = Column(String, primary_key=True, index=True)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False, unique=True)
    domain = Column(String, nullable=True)
    subdomain = Column(String, nullable=True)
    domain_scores = Column(JSON, nullable=True)
    priority_score = Column(Integer, nullable=True)
    priority_factors = Column(JSON, nullable=True)
    evidence_confidence = Column(Float, nullable=True)
    trend = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)
    model_versions = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    challenge = relationship("Challenge", back_populates="analysis")

class ChallengeRelation(Base):
    __tablename__ = "challenge_relations"
    
    id = Column(String, primary_key=True, index=True)
    source_challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    target_challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    status = Column(String, default="pending") # pending | merged | rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    source_challenge = relationship("Challenge", foreign_keys=[source_challenge_id])
    target_challenge = relationship("Challenge", foreign_keys=[target_challenge_id])

class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, index=True)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    match_score = Column(Integer, nullable=False)
    match_reason = Column(Text, nullable=False)
    status = Column(String, default="suggested")

    challenge = relationship("Challenge", back_populates="matches")
    organization = relationship("Organization", back_populates="matches")

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False, unique=True)
    status = Column(String, default="prototype")
    milestones_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    challenge = relationship("Challenge", back_populates="project")

class RoutingBatch(Base):
    __tablename__ = "routing_batches"
    
    id = Column(String, primary_key=True, index=True)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    deadline = Column(DateTime, nullable=False)
    note = Column(Text, nullable=True)
    status = Column(String, default="active") # active | completed | expired
    created_at = Column(DateTime, default=datetime.utcnow)
    
    challenge = relationship("Challenge")
    invitations = relationship("RoutingInvitation", back_populates="batch")

class RoutingInvitation(Base):
    __tablename__ = "routing_invitations"
    
    id = Column(String, primary_key=True, index=True)
    batch_id = Column(String, ForeignKey("routing_batches.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    status = Column(String, default="pending") # pending | accepted | rejected | expired | closed
    responded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    batch = relationship("RoutingBatch", back_populates="invitations")
    organization = relationship("Organization")
