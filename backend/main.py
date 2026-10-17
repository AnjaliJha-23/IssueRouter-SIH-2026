"""
main.py — IssueRouter FastAPI application (SIH 2026).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend and root
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from typing import Optional
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

# ── DB setup ───────────────────────────────────────────────────────────────
from db.database import engine, Base, get_db

# ── Routers ─────────────────────────────────────────────────────────────
from api.auth import router as auth_router
from api.challenges import router as challenges_router
from api.smart_router import router as smart_router
from api.projects import router as projects_router
from api.stats import router as stats_router
from api.proposals import router as proposals_router
from api.universities import router as universities_router

# ── Uploads setup ──────────────────────────────────────────────────────────
UPLOADS_DIR = Path(__file__).resolve().parent / "uploads"
EVIDENCE_UPLOADS_DIR = UPLOADS_DIR / "evidence"
EVIDENCE_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Societal Innovation Collaboration Portal API",
    description="SIH 2026 Backend - DB routes with mock AI pipeline and citizen portal",
    version="2.1.0",
)

# ── CORS configuration ─────────────────────────────────────────────────────
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

env_origins = os.getenv("ALLOWED_ORIGINS") or os.getenv("CORS_ORIGINS")
if env_origins:
    configured_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
else:
    configured_origins = DEFAULT_ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount static uploads ───────────────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# ── Register routers ───────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(challenges_router)
app.include_router(smart_router)
app.include_router(projects_router)
app.include_router(stats_router)
app.include_router(proposals_router)
app.include_router(universities_router)

# ── Startup: create DB tables and migrations ───────────────────────────────
@app.on_event("startup")
def startup_event():
    print("[IssueRouter-SIH] Creating DB tables if not exist…")
    Base.metadata.create_all(bind=engine)
    try:
        from sqlalchemy import inspect
        with engine.connect() as conn:
            inspector = inspect(conn)
            table_names = inspector.get_table_names()

            # 1. Projects org_id migration
            if "projects" in table_names:
                proj_cols = [c["name"] for c in inspector.get_columns("projects")]
                if "org_id" not in proj_cols:
                    conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN org_id VARCHAR REFERENCES organizations(id)")
                    conn.commit()
                    print("[IssueRouter-SIH] Migrated projects table: added org_id column.")

            # 2. Challenges media_urls migration
            if "challenges" in table_names:
                ch_cols = [c["name"] for c in inspector.get_columns("challenges")]
                if "media_urls" not in ch_cols:
                    conn.exec_driver_sql("ALTER TABLE challenges ADD COLUMN media_urls JSON")
                    conn.commit()
                    print("[IssueRouter-SIH] Migrated challenges table: added media_urls column.")

            # 3. ChallengeEvidence media_urls migration
            if "challenge_evidence" in table_names:
                ev_cols = [c["name"] for c in inspector.get_columns("challenge_evidence")]
                if "media_urls" not in ev_cols:
                    conn.exec_driver_sql("ALTER TABLE challenge_evidence ADD COLUMN media_urls JSON")
                    conn.commit()
                    print("[IssueRouter-SIH] Migrated challenge_evidence table: added media_urls column.")

            # 4. ChallengeEvidence embedding_model migration (dimension-versioned vectors)
            if "challenge_evidence" in table_names:
                ev_cols = [c["name"] for c in inspector.get_columns("challenge_evidence")]
                if "embedding_model" not in ev_cols:
                    conn.exec_driver_sql("ALTER TABLE challenge_evidence ADD COLUMN embedding_model VARCHAR")
                    conn.commit()
                    print("[IssueRouter-SIH] Migrated challenge_evidence table: added embedding_model column.")
    except Exception as e:
        print("[IssueRouter-SIH] Startup column check notice:", e)
    print("[IssueRouter-SIH] DB ready.")

    # 5. Optional pre-warming of full ML pipeline models during startup
    if os.getenv("WARM_MODELS_ON_STARTUP", "false").lower() in ("1", "true", "yes"):
        try:
            print("[IssueRouter-SIH] Pre-warming full ML models into memory...")
            from pipeline.orchestrator import load_all_models
            load_all_models()
            print("[IssueRouter-SIH] Full ML pipeline models pre-warmed successfully.")
        except Exception as e:
            print("[IssueRouter-SIH] Model warm-up notice:", e)

# ── Health check ───────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def home():
    return {
        "message": "Societal Innovation Collaboration Portal API is running",
        "status": "active"
    }

# ── ML complaint processing endpoint ───────────────────────────────────────
class ComplaintRequest(BaseModel):
    text: str
    location: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

@app.post("/api/process", tags=["pipeline"])
def process_complaint(req: ComplaintRequest, db: Session = Depends(get_db)):
    """
    Direct endpoint executing the complete IssueRouter NLP pipeline on input complaint text.
    Invokes normaliser, the JEV domain classifier, spaCy gazetteer entity extraction,
    dense vector embedding, semantic deduplication, canonical summarization, and priority scoring.
    """
    from pipeline.orchestrator import process_evidence
    payload = {
        "source": "api_direct",
        "raw_text": req.text,
        "location": req.location,
        "submitted_lat": req.lat,
        "submitted_lng": req.lng
    }
    return process_evidence(payload, db)