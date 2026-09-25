"""
seed_universities.py — Seeds the SQLite database with Universities from CSV and creates accounts for them.
"""
import os
import sys
import csv
import uuid
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from db.database import engine, SessionLocal, Base
from db.models import Organization, User


def resolve_csv_path() -> Path:
    """Resolve Jharkhand universities CSV across root, backend, and environment paths."""
    env_path = os.getenv("UNIVERSITIES_CSV_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    candidates = [
        Path(__file__).resolve().parent.parent / "docs" / "Jharkhand universities list with domains updated.csv",
        Path(__file__).resolve().parent / "docs" / "Jharkhand universities list with domains updated.csv",
        Path.cwd() / "docs" / "Jharkhand universities list with domains updated.csv",
        Path.cwd() / "backend" / "docs" / "Jharkhand universities list with domains updated.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


CSV_PATH = resolve_csv_path()


def seed():
    print("[seed_universities] Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    csv_file = resolve_csv_path()
    try:
        if not csv_file.exists():
            print(f"Error: CSV not found at {csv_file}")
            return
            
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            added = 0
            updated = 0
            users_added = 0
            
            for row in reader:
                name = row.get("University Name", "").strip()
                location = row.get("Location", "").strip()
                email = row.get("Official Email (Domain)", "").strip()
                domains = row.get("Domains of Research & Specialisation", "").strip()
                output = row.get("Successful Researches / Output (Est.)", "").strip()
                
                if not name:
                    continue
                    
                org = db.query(Organization).filter(Organization.name == name).first()
                if org:
                    org.location = location
                    org.district = location
                    org.research_domains = domains
                    org.research_output = output
                    org.type = "University"
                    org.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    org = Organization(
                        id=f"org-{uuid.uuid4().hex[:8]}",
                        name=name,
                        type="University",
                        location=location,
                        district=location,
                        research_domains=domains,
                        research_output=output,
                        status="ACTIVE",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(org)
                    added += 1
                    
                db.flush() # flush to get org.id if new
                
                # Check for user
                if email:
                    user = db.query(User).filter(User.email == email).first()
                    if not user:
                        new_user = User(
                            id=f"user-{uuid.uuid4().hex[:8]}",
                            name=f"{name} Admin",
                            email=email,
                            password_hash="dummyhash", # No password requirement for now
                            role="University",
                            org_id=org.id
                        )
                        db.add(new_user)
                        users_added += 1
                    
            db.commit()
            print(f"[seed_universities] Seed complete: {added} orgs added, {updated} orgs updated, {users_added} users added.")
            
    finally:
        db.close()

if __name__ == "__main__":
    seed()
