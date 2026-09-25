# IssueRouter-SIH-2026 — Master Deployment Implementation Plan (`deploymentImplementplan.md`)

> **READ-ONLY AUDIT EXECUTION BLUEPRINT**  
> *Target Goal:* Zero-cost, high-reliability cloud deployment of the Societal Innovation Collaboration Platform (IssueRouter) for SIH 2026 evaluation.  
> *Core Stack:* React 19 + Vite (Frontend) → FastAPI (Backend) → SQLite + Auto-Seed (Database) with ML Decoupling.  
> *Repository:* `IssueRouter-SIH-2026` ([GitHub](https://github.com/PiUnknown/IssueRouter-SIH-2026))

---

## 1. Architectural Blueprint & Target Infrastructure

```mermaid
flowchart TD
    subgraph Client Tier
        User[Evaluator / Jury Device]
    end

    subgraph Frontend Tier (Vercel CDN)
        Vercel[Vercel Global Edge]
        VercelConfig[vercel.json Rewrites]
        Dist[Compiled Vite Bundle: dist/]
    end

    subgraph Backend Tier (Render Free Web Service)
        Uvicorn[Uvicorn Server : single worker]
        FastAPI[FastAPI Application : main:app]
        LightweightPipeline[Lightweight Heuristic Pipeline : pure Python]
        StaticUploads[/uploads : StaticFiles Mount]
    end

    subgraph Storage Tier (Local Container Disk)
        SQLite[(SQLite : issueRouter.db)]
        WAL[WAL Mode Journal]
        SeedHook[Auto-Seed On Boot Hook : 127 Clusters]
    end

    User -->|HTTPS : Direct Navigation| Vercel
    VercelConfig -->|SPA Rewrite: /* -> /index.html| Dist
    User -->|API Calls: /api/*| Vercel
    VercelConfig -->|Reverse Proxy /api/(.*)| FastAPI
    User -->|Direct API Calls (CORS Allowed)| FastAPI
    FastAPI --> Uvicorn
    FastAPI --> LightweightPipeline
    FastAPI -->|Read / Write| SQLite
    SQLite --> WAL
    FastAPI --> StaticUploads
    Uvicorn -.->|If DB Empty On Boot| SeedHook
    SeedHook -.->|Populate 127 Challenges + Unis| SQLite
```

### Architecture Specifications
| Component | Provider & Tier | Configuration | Cost |
|---|---|---|---|
| **Frontend** | Vercel (Hobby Tier) | Build: `npm run build`, Output: `dist/`, Root: `frontend` | $0.00 |
| **Backend** | Render (Free Web Service) | Python 3.11, Command: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1` | $0.00 |
| **Database** | Embedded SQLite | File: `backend/issueRouter.db` with WAL mode (`PRAGMA journal_mode=WAL;`) | $0.00 |
| **ML Engine** | Decoupled / Heuristic Mode | Pre-seeded 127 clusters active; live intake via fast regex + gazetteer (<60MB RAM) | $0.00 |
| **Total Monthly Cost** | | | **$0.00 / month** |

---

## 2. Master Phase-by-Phase Implementation Plan

### PHASE 0 — Pre-Deployment Audit & Baseline Snapshot
* **Objective:** Ensure current branch `data-fix` is stable, tests pass, and all 127 clusters are intact.
* **Actions:**
  1. Verify working tree status: `git status`.
  2. Run local tests: `pytest backend/tests/test_nlp_pipeline.py`.
  3. Ensure [backend/seed_mock_data.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/seed_mock_data.py) and [docs/Jharkhand universities list with domains updated.csv](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/docs/Jharkhand%20universities%20list%20with%20domains%20updated.csv) exist.
* **Risk Level:** Zero (Read-only).
* **Dependencies:** None.
* **Verification:** Test suite passes; no uncommitted conflicts.

---

### PHASE 1 — ML / Heavy Dependency Decoupling
* **Objective:** Prevent backend crash on 512MB RAM cloud hosts by separating core web dependencies from 3GB PyTorch/Transformers dependencies.
* **Target Files:**
  * [backend/requirements.txt](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/requirements.txt)
  * `backend/requirements-ml.txt` (New reference file for offline ML)
* **Required Blueprint:**
  * Keep only core dependencies in `requirements.txt`:
    ```txt
    fastapi>=0.111.0
    uvicorn[standard]>=0.29.0
    sqlalchemy>=2.0.0
    pydantic>=2.6.0
    python-dotenv>=1.0.0
    httpx>=0.27.0
    pyjwt>=2.8.0
    python-multipart>=0.0.9
    scikit-learn>=1.4.0
    numpy>=1.26.0
    scipy>=1.13.0
    ```
  * Move `torch`, `transformers`, `sentence-transformers`, `spacy`, `huggingface-hub`, `tokenizers` into `requirements-ml.txt`.
* **Technical Reason:** PyTorch and BART exceed build time limits (15 min) and slug limits, triggering instant OOM crash on Render free tier.
* **Risk Level:** High if import chain is not guarded (addressed in Phase 2).
* **Verification:** `pip install -r backend/requirements.txt` installs in <30 seconds with a ~50MB slug.

---

### PHASE 2 — Startup ML Import Guard & Lightweight Pipeline Fallback
* **Objective:** Prevent `ModuleNotFoundError` in `main.py` when heavy ML packages are excluded, while preserving real-time challenge ingestion.
* **Target Files:**
  * [backend/api/challenges.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/api/challenges.py#L40)
  * [backend/pipeline/orchestrator.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/pipeline/orchestrator.py)
* **Required Blueprint:**
  * In `api/challenges.py`, replace eager top-level orchestrator imports:
    ```python
    # Lazy/Safe import to protect cloud startup
    def get_pipeline():
        try:
            from pipeline.orchestrator import process_evidence, analyze_challenge
            return process_evidence, analyze_challenge
        except (ImportError, ModuleNotFoundError):
            from pipeline.lightweight_orchestrator import process_evidence, analyze_challenge
            return process_evidence, analyze_challenge
    ```
  * Or provide [pipeline/lightweight_orchestrator.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/pipeline/) that executes:
    1. Text cleaning via [ingestion/normaliser.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/ingestion/normaliser.py).
    2. Domain heuristic match from [pipeline/config.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/pipeline/config.py) `DOMAINS`.
    3. Location regex match from [pipeline/data/jharkhand_gazetteer.json](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/pipeline/data/jharkhand_gazetteer.json).
    4. Deterministic hash 384d embedding vector.
    5. Cosine deduplication against candidate database clusters.
    6. Canonical title/summary via [pipeline/summarization.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/pipeline/summarization.py) fallback.
    7. Priority calculation via [pipeline/priority_scoring.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/pipeline/priority_scoring.py).
* **Technical Reason:** Allows the API to intake live citizen reports and return complete contracts (`ChallengeOut`, `PipelineProcessResponse`) in <15ms with 0MB additional RAM.
* **Risk Level:** Medium.
* **Verification:** Run `python -c "import main; print('Server boot verified')"` without PyTorch installed.

---

### PHASE 3 — SQLite Concurrency Hardening & Auto-Seed Hook
* **Objective:** Guarantee that a freshly cloned cloud repository boots with all 127 pre-synthesized challenges, and prevent database locking errors.
* **Target Files:**
  * [backend/db/database.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/db/database.py)
  * [backend/main.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/main.py#L66-L95)
  * [backend/seed_universities.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/seed_universities.py#L15)
* **Required Blueprint:**
  * In `db/database.py`, support environment variable override and enable WAL mode:
    ```python
    import os
    from pathlib import Path
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import sessionmaker, declarative_base

    DB_PATH = Path(os.getenv("SQLITE_PATH", Path(__file__).resolve().parent.parent / "issueRouter.db"))
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

    engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

    if DATABASE_URL.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()
    ```
  * In `main.py` `startup_event()`, add auto-seed verification:
    ```python
    @app.on_event("startup")
    def startup_event():
        Base.metadata.create_all(bind=engine)
        # Apply table migrations (guarded for SQLite)
        ...
        # Check if database is populated; seed automatically if empty
        try:
            from db.models import Challenge
            from sqlalchemy.orm import Session
            with Session(engine) as db:
                count = db.query(Challenge).count()
                if count == 0:
                    print("[IssueRouter-SIH] Database is empty. Running seed_all.py...")
                    import seed_all
                    seed_all.seed_mock_data.seed()
                    try:
                        seed_all.seed_universities.seed()
                    except Exception as ue:
                        print("[IssueRouter-SIH] University CSV seed notice:", ue)
                    print("[IssueRouter-SIH] Database successfully auto-seeded with 127 clusters.")
        except Exception as e:
            print("[IssueRouter-SIH] Auto-seed check error:", e)
    ```
  * In `seed_universities.py`, ensure CSV fallback path resolves if `docs/` is copied inside backend:
    ```python
    CSV_PATH = Path(__file__).parent.parent / "docs" / "Jharkhand universities list with domains updated.csv"
    if not CSV_PATH.exists():
        CSV_PATH = Path(__file__).parent / "data" / "Jharkhand universities list with domains updated.csv"
    ```
* **Technical Reason:** Cloud clones do not track `.db` files. Auto-seeding guarantees instant data availability on every fresh boot.
* **Risk Level:** Low.
* **Verification:** Delete `issueRouter.db` locally, start backend, query `GET /api/challenges/`, verify 127 challenges returned.

---

### PHASE 4 — CORS & Security Hardening
* **Objective:** Enable the deployed frontend to communicate with the backend while securing authentication tokens.
* **Target Files:**
  * [backend/main.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/main.py#L41-L51)
  * [backend/api/auth.py](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/backend/api/auth.py#L21)
* **Required Blueprint:**
  * In `main.py`, parse comma-separated origins from `CORS_ORIGINS`:
    ```python
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
    )
    allow_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```
  * In `api/auth.py`:
    ```python
    SECRET_KEY = os.getenv("SECRET_KEY", "sih-2026-issuerouter-secure-jwt-secret-key-convergence")
    ```
* **Technical Reason:** Without dynamic CORS origins, modern browsers block all requests from the Vercel domain.
* **Risk Level:** Low.
* **Verification:** Preflight `OPTIONS` request with `Origin: https://issuerouter.vercel.app` returns `Access-Control-Allow-Origin`.

---

### PHASE 5 — Frontend API Client Centralization & Localhost Elimination
* **Objective:** Direct all frontend API traffic to the deployed backend URL, increase request timeouts for Render cold starts, and eliminate hardcoded `localhost:8000` URLs.
* **Target Files:**
  * [frontend/src/api/client.js](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/frontend/src/api/client.js)
  * [frontend/src/pages/Maps.jsx](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/frontend/src/pages/Maps.jsx#L297-L299)
  * [frontend/src/pages/CitizenProgress.jsx](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/frontend/src/pages/CitizenProgress.jsx)
  * [frontend/src/pages/Progress.jsx](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/frontend/src/pages/Progress.jsx)
  * [frontend/src/components/ui/ChallengeDetailDrawer.jsx](file:///c:/Users/anuj%20chahar/OneDrive/Desktop/SIH-26/IssueRouter-SIH-2026/frontend/src/components/ui/ChallengeDetailDrawer.jsx)
* **Required Blueprint:**
  * In `frontend/src/api/client.js`:
    ```javascript
    import axios from 'axios'

    export const API_BASE_URL = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace(/\/$/, '') : ''

    const client = axios.create({
      baseURL: API_BASE_URL ? `${API_BASE_URL}/api` : '/api',
      timeout: 60_000, // 60s accommodates Render cold starts
      headers: { 'Content-Type': 'application/json' },
    })

    export function resolveApiUrl(path) {
      if (!path) return ''
      if (path.startsWith('http://') || path.startsWith('https://')) return path
      const cleanPath = path.startsWith('/') ? path : `/${path}`
      return API_BASE_URL ? `${API_BASE_URL}${cleanPath}` : cleanPath
    }

    export async function authFetch(inputUrl, options = {}) {
      const token = localStorage.getItem('token')
      const isFormData = options.body instanceof FormData
      const headers = {
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...(options.headers || {}),
      }

      const finalUrl = resolveApiUrl(inputUrl)
      return fetch(finalUrl, { ...options, headers })
    }

    export function getMediaUrl(url) {
      if (!url) return ''
      if (url.startsWith('http://') || url.startsWith('https://')) return url
      const clean = url.startsWith('/') ? url : `/${url}`
      return API_BASE_URL ? `${API_BASE_URL}${clean}` : clean
    }
    ```
  * In `Maps.jsx` (L297-299):
    ```javascript
    // Before:
    const res = await fetch('/api/challenges/').catch(() => fetch('http://localhost:8000/api/challenges/'))
    // After:
    const res = await authFetch('/api/challenges/')
    ```
  * In `CitizenProgress.jsx`, `Progress.jsx`, and `ChallengeDetailDrawer.jsx`: replace `http://localhost:8000${url}` fallbacks with `getMediaUrl(url)`.
* **Technical Reason:** Prevents network failure when evaluators open the app on external laptops or mobile devices.
* **Risk Level:** Medium.
* **Verification:** Run `npm run build` in `frontend/`; grep `dist/` for `localhost:8000` (must return 0 matches).

---

### PHASE 6 — Single Page Application (SPA) Routing Configuration
* **Objective:** Prevent 404 errors when an evaluator refreshes on deep routes (`/dashboard/gov`, `/maps`, `/project/:id`).
* **Target File:** `frontend/vercel.json` (New File)
* **Required Blueprint:**
  ```json
  {
    "rewrites": [
      {
        "source": "/(.*)",
        "destination": "/index.html"
      }
    ]
  }
  ```
  *(Optional: If Vercel reverse proxying is chosen instead of direct CORS, include `{ "source": "/api/(.*)", "destination": "https://<render-url>/api/$1" }` before the wildcard).*
* **Technical Reason:** Static CDN web servers do not understand client-side browser routes without fallback rewriting.
* **Risk Level:** Low.
* **Verification:** Navigate to any nested route and trigger a hard refresh (`Ctrl + F5`).

---

### PHASE 7 — Production Server Startup Script & Procfile
* **Objective:** Ensure Render and PaaS builders execute the correct working directory and bind to the dynamic `$PORT`.
* **Target Files:**
  * `backend/Procfile` (Optional reference)
  * `render.yaml` (Optional blueprint)
* **Required Blueprint:**
  * Render Start Command:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
    ```
  * Render Build Command:
    ```bash
    pip install -r requirements.txt
    ```
* **Technical Reason:** Render assigns random ports via `$PORT`. Hardcoding port 8000 causes deployment failure.
* **Risk Level:** Low.
* **Verification:** Test start locally via `PORT=8000 uvicorn main:app --host 0.0.0.0 --port 8000`.

---

### PHASE 8 — Local Production Simulation
* **Objective:** Replicate the exact cloud environment on localhost before deploying.
* **Execution Steps:**
  1. Build frontend:
     ```bash
     cd frontend
     npm run build
     npx vite preview --port 4173
     ```
  2. Start backend with production flags:
     ```bash
     cd backend
     python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
     ```
  3. Open `http://localhost:4173` in an Incognito window.
  4. Perform complete user journey: Login → Gov Dashboard → Verify → Route → University Accept → Project Workspace → CSR Funding.
* **Verification:** All 127 challenges display, charts load, maps render points, zero console errors.

---

### PHASE 9 — Backend Cloud Deployment (Render)
* **Objective:** Deploy and verify the live API service.
* **Execution Steps:**
  1. Push validated changes to GitHub.
  2. In **Render Dashboard**, click **New + → Web Service**.
  3. Connect GitHub repository `PiUnknown/IssueRouter-SIH-2026`.
  4. Settings:
     * **Name:** `issuerouter-api`
     * **Root Directory:** `backend`
     * **Environment:** `Python 3`
     * **Build Command:** `pip install -r requirements.txt`
     * **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
     * **Plan:** Free ($0.00/mo)
  5. Environment Variables:
     * `CORS_ORIGINS` = `https://<your-vercel-app>.vercel.app,http://localhost:5173`
     * `SECRET_KEY` = `<generated-64-char-hex>`
     * `AUTO_SEED_ON_START` = `true`
  6. Click **Create Web Service**.
* **Verification:** Visit `https://issuerouter-api.onrender.com/`; returns `{"status": "active"}`. Visit `/docs`; Swagger UI renders.

---

### PHASE 10 — Frontend Cloud Deployment (Vercel)
* **Objective:** Deploy and verify the static web app on Vercel CDN.
* **Execution Steps:**
  1. In **Vercel Dashboard**, click **Add New... → Project**.
  2. Import `PiUnknown/IssueRouter-SIH-2026`.
  3. Project Settings:
     * **Framework Preset:** Vite
     * **Root Directory:** `frontend`
     * **Build Command:** `npm run build`
     * **Output Directory:** `dist`
  4. Environment Variables:
     * `VITE_API_URL` = `https://issuerouter-api.onrender.com`
  5. Click **Deploy**.
* **Verification:** Visit assigned Vercel URL (e.g. `https://issuerouter-sih-2026.vercel.app`); landing page renders cleanly with HTTPS.

---

### PHASE 11 — End-to-End Live Staging Verification
* **Objective:** Verify live communication between Vercel and Render.
* **Execution Steps:**
  1. Open browser DevTools Network tab.
  2. Navigate to `https://issuerouter-sih-2026.vercel.app/login`.
  3. Click **Quick Demo Login: Gov Admin** (`gov@jharkhand.gov.in`).
  4. Verify redirect to `/dashboard/gov`; confirm network call `POST /api/auth/login` returns HTTP 200 with JWT.
  5. Verify `GET /api/challenges/` loads all 127 items.
  6. Navigate to `/maps`; verify all Jharkhand markers render on Leaflet heatmap.

---

### PHASE 12 — Disaster Recovery & Rollback Rehearsal
* **Objective:** Establish clear recovery procedures in case of unexpected evaluator issues.
* **Execution Steps:**
  * **Frontend:** Vercel Dashboard → Deployments → Instant "Promote to Production" on prior build.
  * **Backend:** Render Dashboard → Manual Deploy → Deploy previous commit.
  * **Database Reset:** If test submissions clutter the demo, restart the Render instance; the auto-seed hook re-initializes the pristine 127-challenge dataset.

---

## 3. Comprehensive File Modification Specifications

```
================================================================================
TABLE OF FILE MODIFICATIONS
================================================================================
```

| File Path | Action | Exact Modification | Rationale | Risk |
|---|---|---|---|---|
| `backend/requirements.txt` | **MODIFY** | Remove `torch`, `transformers`, `sentence-transformers`, `spacy`. Retain FastAPI, Uvicorn, SQLAlchemy, Pydantic, Scikit-learn, Numpy. | Prevents slug explosion & 512MB RAM OOM kill. | Low |
| `backend/requirements-ml.txt` | **NEW** | Store isolated heavy ML packages for optional local runs. | Preserves offline research capability. | Zero |
| `backend/main.py` | **MODIFY** | 1. Read `CORS_ORIGINS` from env.<br>2. Add auto-seed check in `startup_event()` if `Challenge` count is 0. | Enables cross-origin Vercel requests; seeds empty cloud DB. | Low |
| `backend/api/challenges.py` | **MODIFY** | Wrap orchestrator imports with lazy/lightweight fallback. | Prevents `ModuleNotFoundError` on startup. | Medium |
| `backend/db/database.py` | **MODIFY** | Add `SQLITE_PATH` & `DATABASE_URL` env read; configure SQLite WAL PRAGMAs. | Prevents DB locking; enables custom mounts. | Low |
| `backend/api/auth.py` | **MODIFY** | Read `SECRET_KEY` from `os.getenv`. | Cryptographic token protection. | Low |
| `frontend/src/api/client.js` | **MODIFY** | Bind Axios and `authFetch` to dynamic `VITE_API_URL`; set timeout to 60s. | Connects to cloud API; handles cold starts. | Low |
| `frontend/src/pages/Maps.jsx` | **MODIFY** | Replace direct `fetch('http://localhost:8000/api/...')` with `authFetch`. | Eliminates connection refused errors. | Low |
| `frontend/src/pages/CitizenProgress.jsx` | **MODIFY** | Replace localhost strings with `authFetch` & `getMediaUrl`. | Ensures citizen tracking works globally. | Low |
| `frontend/src/pages/Progress.jsx` | **MODIFY** | Replace localhost image fallbacks with `getMediaUrl`. | Fixes image rendering in resolution drawer. | Low |
| `frontend/src/components/ui/ChallengeDetailDrawer.jsx` | **MODIFY** | Replace localhost image fallbacks with `getMediaUrl`. | Fixes image rendering in lightbox modal. | Low |
| `frontend/vercel.json` | **NEW** | Add SPA wildcard rewrite rule (`/(.*) -> /index.html`). | Prevents 404 errors on page refresh. | Low |
| `backend/.env.example` | **MODIFY** | Document `CORS_ORIGINS`, `SECRET_KEY`, `PORT`, `DATABASE_URL`. | Standardizes environment setup. | Low |

```
================================================================================
FILES THAT MUST REMAIN UNTOUCHED
================================================================================
```
* **`backend/seed_mock_data.py`** — Contains the core 127 Jharkhand clusters, organizations, users, and proposals.
* **`frontend/src/App.jsx`** — Application shell, role guards, and navigation structure are already properly configured.
* **`frontend/src/context/AuthContext.jsx`** — Correctly handles token storage and profile state.
* **`backend/db/models.py`** — Schema definitions, foreign keys, and JSON columns are structurally complete.
* **`backend/db/schemas.py`** — Pydantic response models conform with Pydantic v2.
* **All Dashboard Views** (`GovDashboard.jsx`, `OrgDashboard.jsx`, `IndustryDashboard.jsx`, `CitizenDashboard.jsx`, `ProjectWorkspace.jsx`, `Universities.jsx`) — Fully functional presentation components.

---

## 4. Exact Environment Variables Matrix

### Backend Environment Variables (Render)
```ini
# Production Port (Dynamically injected by Render, fallback for local test)
PORT=10000

# Allowed Frontend Origins (Comma-separated)
CORS_ORIGINS=https://issuerouter-sih-2026.vercel.app,http://localhost:5173

# Cryptographic Secret for JWT Signature
SECRET_KEY=sih2026_prod_jwt_secret_d98f7e6a5b4c3d2e1f0a9b8c7d6e5f4a

# Database Configuration (Defaults to embedded SQLite)
DATABASE_URL=sqlite:///backend/issueRouter.db

# Auto-seeding toggle on boot
AUTO_SEED_ON_START=true

# Groq API Configuration (Optional: live summarization fallback is active)
GROQ_API_KEY=
GROQ_MODEL=groq/compound-mini

# Lightweight Pipeline Flag
ENABLE_HEAVY_ML=false
```

### Frontend Environment Variables (Vercel)
```ini
# Backend Cloud API Gateway URL (No trailing slash)
VITE_API_URL=https://issuerouter-api.onrender.com
```

---

## 5. End-to-End Demonstration Quality Checklist

### Pre-Deployment Quality Gates (Local Testing)
- [ ] `npm run build` in `frontend/` succeeds without warnings or errors.
- [ ] Backend starts with `python -m uvicorn main:app` using only `requirements.txt`.
- [ ] Removing `issueRouter.db` triggers auto-seeding; all 127 challenges reload.
- [ ] `POST /api/auth/login` returns valid token for `gov@jharkhand.gov.in`.
- [ ] Zero instances of `localhost:8000` present in compiled frontend `dist/` bundle.

### Post-Deployment Quality Gates (Live Testing)
- [ ] **API Health:** `GET https://issuerouter-api.onrender.com/` returns HTTP 200 `{"status": "active"}`.
- [ ] **SPA Routing:** Direct navigation to `/dashboard/gov` and `/maps` renders without 404.
- [ ] **Console Cleanliness:** Browser console displays 0 CORS policy or mixed content warnings.
- [ ] **Gov Flow:** Government Officer verifies a pending challenge (`PATCH /api/challenges/{id}/verify`).
- [ ] **Smart Routing:** Dispatch routing batch to RIMS Ranchi (`POST /api/challenges/{id}/route`).
- [ ] **University Flow:** Login as `sharma@rims.ac.in`, accept invitation, inspect Project Workspace.
- [ ] **Industry Flow:** Login as `csr@tatasteel.com`, commit funding to active project.
- [ ] **GIS Visualization:** All 24 Jharkhand district clusters render on Leaflet heatmap.
- [ ] **Citizen Intake:** Submit new issue from citizen portal; receive immediate tracking ID.

---

## Next Step
This implementation plan has been written to the artifact **`deploymentImplementplan.md`**.  
Please review the plan. Once approved, we can proceed with executing the phases in strict order. No source files have been modified.
