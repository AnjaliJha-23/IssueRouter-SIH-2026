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
    challenges = relationship("Challenge", back_populates="creator")

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    domain = Column(String, nullable=True) # e.g., 'HealthTech', 'EdTech'
    status = Column(String, default="pending_verification") # pending_verification | verified | matches_suggested | ready_for_routing | routed | in_project | resolved
    priority_score = Column(Integer, nullable=True)
    location = Column(String, nullable=False)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    department = Column(String, nullable=True)
    complaint_count = Column(Integer, default=1) # total evidence count
    source_counts = Column(JSON, nullable=True) # {"twitter": 47, "citizen": 8, "ngo": 2}
    ai_confidence = Column(Float, nullable=True)
    duplicate_risk = Column(Float, nullable=True)
    rt_reach = Column(Integer, default=0)
    trend = Column(String, default="stable") # up | down | stable
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="challenges")
    matches = relationship("Match", back_populates="challenge")
    project = relationship("Project", back_populates="challenge", uselist=False)

class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, index=True)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    match_score = Column(Integer, nullable=False)
    match_reason = Column(Text, nullable=False)
    status = Column(String, default="suggested") # suggested | accepted | rejected

    challenge = relationship("Challenge", back_populates="matches")
    organization = relationship("Organization", back_populates="matches")

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False, unique=True)
    status = Column(String, default="prototype") # prototype | testing | pilot | deployed
    milestones_json = Column(JSON, nullable=True) # Stores list of milestones
    created_at = Column(DateTime, default=datetime.utcnow)

    challenge = relationship("Challenge", back_populates="project")
