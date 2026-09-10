import os
from dotenv import load_dotenv

# Load .env from backend and root
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Societal Innovation Collaboration Portal API",
    description="SIH 2026 Backend - DB routes with mock AI pipeline",
    version="2.0.0",
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

# ── Register routers ───────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(challenges_router)
app.include_router(smart_router)
app.include_router(projects_router)
app.include_router(stats_router)
app.include_router(proposals_router)
app.include_router(universities_router)

# ── Startup: create DB tables ──────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    print("[IssueRouter-SIH] Creating DB tables if not exist…")
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(projects)").fetchall()]
            if "org_id" not in cols:
                conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN org_id VARCHAR REFERENCES organizations(id)")
                conn.commit()
                print("[IssueRouter-SIH] Migrated projects table: added org_id column.")
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