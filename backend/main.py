"""
main.py — IssueRouter FastAPI application (SIH 2026).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend and root
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── DB setup ───────────────────────────────────────────────────────────────
from db.database import engine, Base, SessionLocal
from db.models import Challenge

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

# ── CORS setup ─────────────────────────────────────────────────────────────
DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:5173",
]


def get_cors_origins() -> list[str]:
    """
    Parse and validate allowed CORS origins from CORS_ORIGINS environment variable.
    - If CORS_ORIGINS is unset in environment: defaults to local development origins.
    - If CORS_ORIGINS is set: splits by comma, trims, and filters empty items.
    - If CORS_ORIGINS is explicitly present but empty/whitespace-only: raises ValueError
      to prevent silently falling back or broadening access.
    """
    if "CORS_ORIGINS" not in os.environ:
        return list(DEFAULT_CORS_ORIGINS)

    raw_origins = os.environ["CORS_ORIGINS"]
    if not raw_origins or not raw_origins.strip():
        raise ValueError(
            "CORS_ORIGINS environment variable is set but empty. "
            "Provide at least one valid origin or unset CORS_ORIGINS to use default development origins."
        )

    parsed = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    if not parsed:
        raise ValueError(
            "CORS_ORIGINS environment variable contains no valid origins after parsing. "
            "Provide at least one valid origin or unset CORS_ORIGINS to use default development origins."
        )

    return parsed


cors_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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

    # ── Security & environment configuration logging ────────────────────────
    try:
        active_origins = get_cors_origins()
        print(f"[CONFIG] CORS origins configured: {len(active_origins)}")
    except Exception as cors_err:
        print(f"[CONFIG] CORS configuration error: {cors_err}")
    
    has_jwt_secret = bool((os.getenv("JWT_SECRET") or "").strip() or (os.getenv("SECRET_KEY") or "").strip())
    print(f"[CONFIG] JWT secret configured: {'yes' if has_jwt_secret else 'no'}")

    # ── Auto-seeding on start (if configured) ──────────────────────────────
    auto_seed = os.getenv("AUTO_SEED_ON_START", "false").strip().lower() in ("true", "1", "yes")
    if auto_seed:
        db = SessionLocal()
        try:
            challenge_count = db.query(Challenge).count()
            if challenge_count == 0:
                print("[IssueRouter-SIH] AUTO_SEED_ON_START is true and database is empty (0 challenges). Running seed...")
                try:
                    import seed_mock_data
                    seed_mock_data.seed()
                    try:
                        import seed_universities
                        seed_universities.seed()
                    except Exception as u_err:
                        print(f"[IssueRouter-SIH] Warning: University seed failed: {u_err}")
                    print("[IssueRouter-SIH] Auto-seed complete.")
                except Exception as seed_err:
                    print(f"[IssueRouter-SIH] CRITICAL: Auto-seed failed: {seed_err}")
                    raise seed_err
            else:
                print(f"[IssueRouter-SIH] Database already contains {challenge_count} challenges. Auto-seed skipped.")
        finally:
            db.close()

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