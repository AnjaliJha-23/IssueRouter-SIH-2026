"""
main.py — IssueRouter FastAPI application (SIH 2026).
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── DB setup ───────────────────────────────────────────────────────────────
from db.database import engine, Base

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
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
        with engine.connect() as conn:
            # 1. Projects org_id migration
            proj_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(projects)").fetchall()]
            if "org_id" not in proj_cols:
                conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN org_id VARCHAR REFERENCES organizations(id)")
                conn.commit()
                print("[IssueRouter-SIH] Migrated projects table: added org_id column.")

            # 2. Challenges media_urls migration
            ch_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(challenges)").fetchall()]
            if "media_urls" not in ch_cols:
                conn.exec_driver_sql("ALTER TABLE challenges ADD COLUMN media_urls JSON")
                conn.commit()
                print("[IssueRouter-SIH] Migrated challenges table: added media_urls column.")

            # 3. ChallengeEvidence media_urls migration
            ev_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(challenge_evidence)").fetchall()]
            if "media_urls" not in ev_cols:
                conn.exec_driver_sql("ALTER TABLE challenge_evidence ADD COLUMN media_urls JSON")
                conn.commit()
                print("[IssueRouter-SIH] Migrated challenge_evidence table: added media_urls column.")
    except Exception as e:
        print("[IssueRouter-SIH] Startup column check notice:", e)
    print("[IssueRouter-SIH] DB ready.")

# ── Health check ───────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def home():
    return {
        "message": "Societal Innovation Collaboration Portal API is running",
        "status": "active"
    }

# ── Legacy ML endpoint stub ────────────────────────────────────────────────
class ComplaintRequest(BaseModel):
    text: str

@app.post("/api/process", tags=["pipeline"])
def process_complaint(req: ComplaintRequest):
    return {"error": "Legacy ML pipeline is disabled for this MVP phase. Use /api/challenges endpoint."}