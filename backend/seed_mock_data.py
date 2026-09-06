
"""
seed_mock_data.py — Seeds the SQLite database with SIH 2026 mock data (Jharkhand focused).
"""
import sys
import uuid
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from db.database import engine, SessionLocal, Base
from db.models import Organization, User, Challenge, Match, Project

def seed():
    print("[seed] Creating tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("[seed] Wiping existing data...")
        db.query(Project).delete()
        db.query(Match).delete()
        db.query(Challenge).delete()
        db.query(User).delete()
        db.query(Organization).delete()
        db.commit()

        # --- SEED ORGANIZATIONS ---
        orgs = [
            Organization(id="org-gov-1", name="Jharkhand Health Department", type="Gov", location="Ranchi"),
            Organization(id="org-univ-1", name="RIMS Ranchi", type="University", location="Ranchi"),
            Organization(id="org-univ-2", name="IIT ISM Dhanbad", type="University", location="Dhanbad"),
            Organization(id="org-univ-3", name="NIT Jamshedpur", type="University", location="Jamshedpur"),
            Organization(id="org-ind-1", name="Tata Steel CSR", type="Industry", location="Jamshedpur"),
        ]
        db.bulk_save_objects(orgs)
        db.commit()

        # --- SEED USERS ---
        users = [
            User(id="user-gov-1", name="Admin", email="gov@jharkhand.gov.in", password_hash="dummyhash", role="Gov", org_id="org-gov-1"),
            User(id="user-cit-1", name="Rahul Kumar", email="rahul@citizen.in", password_hash="dummyhash", role="Citizen", org_id=None),
            User(id="user-univ-1", name="Dr. Sharma", email="sharma@rims.ac.in", password_hash="dummyhash", role="University", org_id="org-univ-1"),
            User(id="user-ind-1", name="CSR Head", email="csr@tatasteel.com", password_hash="dummyhash", role="Industry", org_id="org-ind-1"),
        ]
        db.bulk_save_objects(users)
        db.commit()

        # --- SEED CHALLENGES (Jharkhand HealthTech focused) ---
        c1_id = str(uuid.uuid4())
        c2_id = str(uuid.uuid4())
        c3_id = str(uuid.uuid4())

        challenges = [
            Challenge(
                id=c1_id,
                title="Lack of Telemedicine in Dumka Villages",
                description="Villages around Dumka block have no direct access to specialists. Need a solar-powered telemedicine kiosk.",
                domain="HealthTech",
                status="verified",
                priority_score=92,
                location="Dumka, Jharkhand",
                lat=24.26, lng=87.25,
                department="Rural Health",
                created_by="user-cit-1",
                verified=True
            ),
            Challenge(
                id=c2_id,
                title="Waterborne Illness Outbreak in Jharia",
                description="Frequent reports of cholera and dysentery in Jharia mining areas due to contaminated water.",
                domain="HealthTech",
                status="pending",
                priority_score=85,
                location="Jharia, Dhanbad",
                lat=23.74, lng=86.41,
                department="Public Health",
                created_by="user-cit-1",
                verified=False
            ),
            Challenge(
                id=c3_id,
                title="Ambulance Routing Inefficiency in Ranchi",
                description="Heavy traffic on Main Road Ranchi delays emergency ambulances. Need an AI routing solution.",
                domain="HealthTech",
                status="matched",
                priority_score=78,
                location="Main Road, Ranchi",
                lat=23.34, lng=85.30,
                department="Traffic & Emergency",
                created_by="user-cit-1",
                verified=True
            ),
        ]
        db.bulk_save_objects(challenges)
        db.commit()

        # --- SEED MATCHES ---
        matches = [
            Match(
                id=str(uuid.uuid4()),
                challenge_id=c1_id,
                org_id="org-univ-1", # RIMS
                match_score=95,
                match_reason="RIMS Ranchi has strong rural health expertise and proximity to Santhal Pargana.",
                status="suggested"
            ),
            Match(
                id=str(uuid.uuid4()),
                challenge_id=c1_id,
                org_id="org-ind-1", # Tata Steel
                match_score=88,
                match_reason="Tata CSR has funds allocated for rural healthcare infrastructure.",
                status="suggested"
            ),
            Match(
                id=str(uuid.uuid4()),
                challenge_id=c3_id,
                org_id="org-univ-1",
                match_score=91,
                match_reason="Already engaged in HealthTech innovations in Ranchi.",
                status="accepted"
            )
        ]
        db.bulk_save_objects(matches)
        db.commit()

        # --- SEED PROJECT ---
        p1 = Project(
            id=str(uuid.uuid4()),
            challenge_id=c3_id,
            status="prototype",
            milestones_json=json.dumps([
                {"title": "Initial Research", "status": "completed"},
                {"title": "Prototype AI Algorithm", "status": "in_progress"},
                {"title": "Pilot with 5 Ambulances", "status": "pending"}
            ])
        )
        db.add(p1)
        db.commit()

        print("[seed] Successfully seeded Jharkhand mock data.")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
