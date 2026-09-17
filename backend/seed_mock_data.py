"""
seed_mock_data.py — Seeds the SQLite database with SIH 2026 mock data (Jharkhand focused), high volume.
"""
import sys
import uuid
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from db.database import engine, SessionLocal, Base
from db.models import Organization, User, Challenge, Match, Project, ChallengeEvidence, ChallengeAnalysis

AREAS = {
    "Main Road, Ranchi": (23.3441, 85.3096),
    "Kanke, Ranchi": (23.4333, 85.3211),
    "Bariatu, Ranchi": (23.3860, 85.3421),
    "Doranda, Ranchi": (23.3323, 85.3220),
    "Dhurwa, Ranchi": (23.2929, 85.2917),
    "Jharia, Dhanbad": (23.7431, 86.4137),
    "Bank More, Dhanbad": (23.7915, 86.4253),
    "Saraidhela, Dhanbad": (23.8193, 86.4526),
    "Sakchi, Jamshedpur": (22.8046, 86.2029),
    "Bistupur, Jamshedpur": (22.7937, 86.1837),
    "Mango, Jamshedpur": (22.8251, 86.2069),
    "Sector 4, Bokaro": (23.6693, 86.1511),
    "Chas, Bokaro": (23.6334, 86.1772),
    "Santhal Pargana, Dumka": (24.2687, 87.2490),
    "Deoghar City": (24.4842, 86.6961),
    "Hazaribagh Town": (23.9930, 85.3582),
}
AREA_NAMES = list(AREAS.keys())

TEMPLATES = [
    ("Lack of Telemedicine", "Villages have no direct access to specialists. Need a solar-powered telemedicine kiosk.", "HealthTech", "Rural Health", (80, 100), (50, 300)),
    ("Waterborne Illness Outbreak", "Frequent reports of cholera and dysentery due to contaminated water supply.", "HealthTech", "Public Health", (85, 100), (100, 500)),
    ("Ambulance Routing Inefficiency", "Heavy traffic delays emergency ambulances. Need an AI routing solution.", "HealthTech", "Traffic & Emergency", (70, 95), (80, 400)),
    ("Non-functional Primary Health Centre", "PHC is locked for 3 weeks, no doctor available. People travelling 40km for basics.", "HealthTech", "Rural Health", (85, 100), (60, 200)),
    ("Broken Medical Equipment", "X-Ray and MRI machines at district hospital out of order for months.", "HealthTech", "Medical Infrastructure", (60, 90), (40, 150)),
    ("Malnutrition in Tribal Belts", "Severe cases of malnutrition observed among children in remote hamlets.", "BioTech", "Child Welfare", (90, 100), (120, 600)),
    ("Fake Medicine Distribution", "Counterfeit drugs being sold in local pharmacies. Needs blockchain/tracking solution.", "BioTech", "Drug Control", (80, 95), (30, 120)),
    ("Stray Dog Menace", "Aggressive packs of dogs near hospital premises biting patients.", "Public Health", "Municipal Corp", (50, 75), (20, 100)),
    ("Open Medical Waste", "Hospital bio-waste dumped in open grounds near residential area.", "HealthTech", "Sanitation", (85, 100), (70, 250)),
    ("High Maternal Mortality", "No safe delivery centers nearby, leading to risky home births.", "HealthTech", "Maternal Health", (90, 100), (80, 350)),
    ("School Dropout Rate", "Children dropping out due to lack of digital access and infrastructure.", "EdTech", "Education", (60, 80), (30, 150)),
    ("Contaminated Groundwater", "Arsenic/Fluoride poisoning detected in local handpumps.", "Public Health", "Water Dept", (85, 95), (60, 200)),
    ("Inadequate Crop Yield", "Farmers facing losses due to unknown soil disease.", "AgriTech", "Agriculture", (50, 80), (40, 180)),
    ("Frequent Power Cuts in Hospital", "Daily 6-hour power cuts affecting ICU ventilators.", "HealthTech", "Energy", (95, 100), (150, 500)),
    ("Lack of Blood Bank", "Nearest blood bank is 60km away. Emergency patients suffering.", "HealthTech", "Medical Infrastructure", (85, 95), (90, 300)),
]

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

        # --- SEED HIGH VOLUME CHALLENGES ---
        now = datetime.utcnow()
        challenges = []
        for i in range(100): # 100 challenges
            tmpl = random.choice(TEMPLATES)
            title, desc, domain, dept, prio_range, count_range = tmpl
            area = random.choice(AREA_NAMES)
            lat, lng = AREAS[area]
            
            # small jitter
            lat += random.uniform(-0.015, 0.015)
            lng += random.uniform(-0.015, 0.015)

            prio = random.randint(*prio_range)
            comp_count = random.randint(*count_range)
            
            reach = int(comp_count * random.uniform(2.0, 8.0))
            trend = random.choices(["up", "stable", "down"], weights=[40, 40, 20])[0]
            status = random.choices(["pending_verification", "verified", "matches_suggested", "ready_for_routing", "routed", "in_project", "resolved"], weights=[20, 20, 10, 10, 15, 15, 10])[0]
            
            # Create a realistic breakdown of evidence sources based on comp_count
            social_count = int(comp_count * random.uniform(0.6, 0.9))
            citizen_count = comp_count - social_count
            ngo_count = random.randint(0, min(5, citizen_count)) if citizen_count > 0 else 0
            citizen_count -= ngo_count
            
            source_counts = {
                "social": social_count,
                "citizen": citizen_count,
                "ngo": ngo_count,
                "government": random.randint(0, 1) if status != "pending_verification" else 0
            }
            
            ai_confidence = round(random.uniform(0.75, 0.98), 2)
            duplicate_risk = round(random.uniform(0.01, 0.15), 2)

            days_ago = random.randint(0, 14)
            c_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            challenges.append(Challenge(
                id=f"CHL-2026-{str(i+1).zfill(4)}",
                title=f"{title} - {area.split(',')[0]}",
                official_description=desc,
                domain=domain,
                department=dept,
                status=status,
                priority_score=prio,
                location=area,
                lat=round(lat, 6),
                lng=round(lng, 6),
                created_by="user-cit-1",
                verified=(status != "pending_verification"),
                created_at=c_at
            ))

        db.bulk_save_objects(challenges)
        db.commit()
        
        # --- SEED EVIDENCE AND AI ANALYSIS FOR CHALLENGES ---
        evidences = []
        analyses = []
        matches = []
        projects = []

        for c in challenges:
            # 1. Evidence item
            ev_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
            evidences.append(ChallengeEvidence(
                id=ev_id,
                challenge_id=c.id,
                source="citizen" if random.random() > 0.4 else "twitter",
                raw_text=f"{c.title}. {c.official_description} Located at {c.location}.",
                clean_text=f"{c.title}. {c.official_description} Located at {c.location}.",
                submitted_lat=c.lat,
                submitted_lng=c.lng,
                created_at=c.created_at
            ))

            # 2. Challenge Analysis
            domain_scores = {
                c.domain: round(random.uniform(0.78, 0.96), 2),
                "Public Administration": round(random.uniform(0.04, 0.12), 2),
                "Infrastructure/Transport": round(random.uniform(0.02, 0.09), 2),
            }
            analyses.append(ChallengeAnalysis(
                id=f"CA-{uuid.uuid4().hex[:8].upper()}",
                challenge_id=c.id,
                domain=c.domain,
                subdomain=c.department,
                domain_scores=domain_scores,
                priority_score=c.priority_score,
                priority_factors={
                    "severity": round(c.priority_score * 0.30 / 100, 2),
                    "evidence_volume": round(random.uniform(0.15, 0.25), 2),
                    "confidence": round(random.uniform(0.18, 0.25), 2),
                    "trend": round(random.uniform(0.10, 0.20), 2)
                },
                evidence_confidence=round(random.uniform(0.80, 0.98), 2),
                trend=c.trend,
                explanation=f"Zero-shot classification identified {c.domain} ({c.department}) with high confidence. Priority computed from {c.complaint_count} cross-verified civic signals.",
                model_versions={
                    "classification": "facebook/bart-large-mnli",
                    "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
                    "summarization": "groq/compound-mini"
                },
                updated_at=c.created_at
            ))

            # 3. Matches and Projects
            if c.status in ["matches_suggested", "ready_for_routing", "routed", "in_project", "resolved"]:
                num_matches = random.randint(1, 3)
                chosen_orgs = random.sample(["org-univ-1", "org-univ-2", "org-univ-3", "org-ind-1"], num_matches)
                for i, org_id in enumerate(chosen_orgs):
                    m_status = "suggested"
                    if c.status in ["routed", "in_project", "resolved"] and i == 0:
                        m_status = "accepted"
                    matches.append(Match(
                        id=str(uuid.uuid4()),
                        challenge_id=c.id,
                        org_id=org_id,
                        match_score=random.randint(75, 98),
                        match_reason=f"Strong research alignment and domain expertise in {c.department}.",
                        status=m_status
                    ))

            if c.status in ["in_project", "resolved"]:
                projects.append(Project(
                    id=str(uuid.uuid4()),
                    challenge_id=c.id,
                    status="prototype" if c.status == "in_project" else "deployed",
                    milestones_json=json.dumps([
                        {"title": "Initial Research", "status": "completed"},
                        {"title": "Prototype Phase", "status": "in_progress" if c.status == "in_project" else "completed"},
                        {"title": "Deployment", "status": "pending" if c.status == "in_project" else "completed"}
                    ])
                ))

        db.bulk_save_objects(evidences)
        db.bulk_save_objects(analyses)
        db.bulk_save_objects(matches)
        db.bulk_save_objects(projects)
        db.commit()

        print(f"[seed] Successfully seeded 100 Jharkhand challenges with {len(evidences)} evidence records, {len(analyses)} AI analyses, {len(matches)} matches, and {len(projects)} projects for SIH demo.")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
