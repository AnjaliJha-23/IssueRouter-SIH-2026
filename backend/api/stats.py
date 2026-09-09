"""
api/stats.py — Aggregated analytics endpoints for the SIH Dashboard.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from db.database import get_db
from db.models import Challenge, User
from db.schemas import StatsOverviewOut, LocationsOut, LocationPointOut
from api.auth import require_roles

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("/overview", response_model=StatsOverviewOut)
def overview(
    current_user: User = Depends(require_roles("Gov", "University", "Industry")),
    db: Session = Depends(get_db)
):
    """Overall platform statistics for authorized stakeholder dashboards."""
    total = db.query(func.count(Challenge.id)).scalar() or 0
    pending = db.query(func.count(Challenge.id)).filter(Challenge.status == "pending_verification").scalar() or 0
    matched = db.query(func.count(Challenge.id)).filter(Challenge.status == "matched").scalar() or 0
    in_project = db.query(func.count(Challenge.id)).filter(Challenge.status == "in_project").scalar() or 0
    resolved = db.query(func.count(Challenge.id)).filter(Challenge.status == "resolved").scalar() or 0

    avg_priority = db.query(func.avg(Challenge.priority_score)).scalar() or 0.0

    return StatsOverviewOut(
        total_challenges=total,
        pending_verification=pending,
        matched=matched,
        in_project=in_project,
        resolved=resolved,
        avg_priority=round(float(avg_priority), 1)
    )

@router.get("/locations", response_model=LocationsOut)
def locations(
    top: int = Query(15, ge=5, le=50, description="How many top locations to return"),
    current_user: User = Depends(require_roles("Gov", "University", "Industry")),
    db: Session = Depends(get_db),
):
    """Top locations by challenge priority for the heatmap."""
    rows = (
        db.query(
            Challenge.id,
            Challenge.title,
            Challenge.location,
            Challenge.lat,
            Challenge.lng,
            Challenge.priority_score,
            Challenge.status,
        )
        .filter(Challenge.lat != None)
        .order_by(Challenge.priority_score.desc())
        .limit(top)
        .all()
    )
    
    return LocationsOut(
        locations=[
            LocationPointOut(
                id=r.id,
                title=r.title,
                location=r.location,
                lat=r.lat,
                lng=r.lng,
                priority_score=r.priority_score,
                status=r.status,
            )
            for r in rows
        ]
    )
