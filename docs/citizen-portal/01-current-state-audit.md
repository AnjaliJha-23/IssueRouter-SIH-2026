# IssueRouter — Citizen Portal Current State Audit

**Project**: SIC Portal · SIH26043 · Team Convergence  
**Target Module**: Citizen Experience (`frontend` & `backend`)  
**Audit Date**: September 2026  
**Status**: Completed Baseline Assessment

---

## 1. Executive Summary & Repository Overview

The **IssueRouter** repository is a societal challenge routing platform designed to bridge citizen distress signals, government oversight, university academic research, and industry CSR implementation.

### Codebase Organization
- **Backend**: FastAPI (`backend/main.py`), SQLAlchemy ORM (`backend/db/models.py`), SQLite (`backend/issueRouter.db`), and mock/NLP pipelines (`backend/pipeline/`).
- **Frontend**: React 18 / Vite SPA (`frontend/src/App.jsx`), Tailwind CSS v4 (`@tailwindcss/vite`), React Router v7 (`react-router-dom`).
- **Data Models**:
  - `User` (`backend/db/models.py:29`): Contains `id`, `name`, `email`, `password_hash`, `role` (`'Citizen'`, `'Gov'`, `'University'`, `'Industry'`), `org_id`.
  - `Challenge` (`backend/db/models.py:42`): Canonical societal issue record with `title`, `official_description`, `ai_generated_summary`, `domain`, `status`, `priority_score`, `location`, `district`, `block`, `lat`, `lng`, `source_counts`, `verified`, `created_by`.
  - `ChallengeEvidence` (`backend/db/models.py:85`): Individual complaint/signal item containing `source`, `raw_text`, `clean_text`, `embedding_json`, `submitted_lat`, `submitted_lng`.
  - `Match`, `Project`, `Proposal`, `RoutingBatch`, `RoutingInvitation`: Institutional routing and implementation tracking models.

---

## 2. Current Citizen UX Analysis

**Source File**: `frontend/src/pages/CitizenDashboard.jsx`

### Current State
1. **Layout**:
   - A basic 2-column dashboard layout:
     - Left column: "Report a New Challenge" form.
     - Right column: "Recent Community Challenges" list.
2. **Form Experience**:
   - Only 3 text inputs: `Title`, `Description`, and `Location`.
   - Hardcoded coordinates: Latitude `23.3441` and Longitude `85.3096` are blindly posted for every submission (`CitizenDashboard.jsx:42-43`).
   - No GPS geolocation support.
   - No district or block selector for administrative alignment.
   - No photo or document upload support whatsoever.
   - Rudimentary HTML5 `required` attribute; no inline validation, character count, or guidance.
   - Single static submit button with basic text change to "Submitting...".
3. **Data Leakage in UI**:
   - The dashboard calls `/api/challenges/` to populate "Recent Community Challenges" (`CitizenDashboard.jsx:20`).
   - It renders all challenges in the database without any ownership checks or citizen-specific privacy filtering.
4. **Visual Polish**:
   - Uses a generic purple/pink text gradient and plain rounded cards.
   - Lacks an inviting citizen-facing hero, reassuring process explanations, or clear next-step calls-to-action.

---

## 3. Current Authentication & RBAC Analysis

**Source Files**:
- `backend/api/auth.py`
- `backend/db/models.py`
- `frontend/src/context/AuthContext.jsx`
- `frontend/src/components/ProtectedRoute.jsx`

### Vulnerabilities & Incomplete Architecture

| Layer | Component | Current Implementation | Flaw / Vulnerability |
|---|---|---|---|
| **Backend** | `backend/api/auth.py` | `create_access_token` generates tokens with `{"sub": user.id, "role": user.role}`. | `get_current_user` dependency was not implemented. Endpoints throughout the backend do not inspect the `Authorization` header. |
| **Backend** | `backend/api/auth.py` | `GET /api/auth/me?email={email}` | Returns full user profile purely from a query parameter without verifying the Bearer token. |
| **Backend** | `backend/api/challenges.py` | `POST /api/challenges/` | Does not authenticate the caller; leaves `created_by = None` (`challenges.py:101`). |
| **Backend** | `backend/api/challenges.py` | `PATCH /api/challenges/{id}/verify` | Government verification endpoint has NO role check. A citizen or anonymous client can mark any challenge verified. |
| **Backend** | `backend/api/challenges.py` | `POST /api/challenges/{id}/route` | Government dispatch endpoint has NO role check. An unauthorized user can route batches to universities. |
| **Backend** | `backend/api/challenges.py` | `GET /api/challenges/` | Returns every challenge across the entire state. No `/api/challenges/my` endpoint exists for citizen ownership isolation. |
| **Frontend** | `frontend/src/context/AuthContext.jsx` | Line 24: `fetch('/api/auth/me?email=admin')` | Background sync hardcodes `email=admin`. When a citizen logs in, this query attempts to fetch the admin user and corrupts context. |
| **Frontend** | `frontend/src/components/ProtectedRoute.jsx` | Supports `allowedRoles`, but `App.jsx:35` declares `<Route element={<ProtectedRoute />}>` with NO `allowedRoles` set. | Any authenticated user (including a Citizen) can navigate to `/dashboard/gov`, `/dashboard/org`, `/dashboard/industry`, `/analytics`, `/maps`, `/universities`, `/project/:id`. |
| **Frontend** | `frontend/src/App.jsx` | Route `dashboard` redirects unconditionally to `/dashboard/gov` (`App.jsx:37`). | If a Citizen enters `/dashboard`, they are directed to the Government Dashboard. |

---

## 4. Current Challenge Submission Architecture Analysis

**Source Files**:
- `backend/api/challenges.py:68-108`
- `backend/db/schemas.py:171-177`
- `backend/pipeline/orchestrator.py`

### Observations
1. **Schema**: `ChallengeCreate` defines:
   ```python
   class ChallengeCreate(BaseModel):
       title: str
       description: str
       location: str
       lat: Optional[float] = None
       lng: Optional[float] = None
   ```
2. **Persistence**:
   - `create_challenge` creates a `Challenge` record directly.
   - It performs basic keyword checks for domain assignment (`"health" -> HealthTech`, `"school" -> EdTech`, `"water" -> Water Management`).
   - It does **not** create a `ChallengeEvidence` entry.
   - It does **not** link the record to the authenticated citizen (`created_by` remains null).
3. **Pipeline Disconnect**:
   - `backend/pipeline/orchestrator.py` has `process_evidence()`, which creates `ChallengeEvidence` and canonical challenges.
   - However, `POST /api/challenges/` does not invoke `process_evidence()` or link evidence models.

---

## 5. Current Evidence & Image Handling Analysis

**Source Files**:
- `backend/db/models.py:85-99` (`ChallengeEvidence`)
- `frontend/src/components/ui/ChallengeDetailDrawer.jsx:25-50`
- `frontend/src/pages/Progress.jsx:123-156`

### Observations
1. **Backend Storage**:
   - `ChallengeEvidence` only contains text and numerical coordinate fields (`raw_text`, `clean_text`, `embedding_json`, `submitted_lat`, `submitted_lng`).
   - There is no column for photo/image attachments (e.g., `media_urls` or `image_urls`).
   - There is no file upload router, no multipart parsing dependency configured, and no static file serving mounted in `backend/main.py`.
2. **Frontend Mock Galleries**:
   - `ChallengeDetailDrawer.jsx` defines a static array `EVIDENCE_IMAGES` with emojis and CSS gradients.
   - `Progress.jsx` reads mock fields `cluster.officer_photos` and `cluster.resolved_photos`.
   - Real citizen photo uploads cannot currently be ingested, stored, or displayed in either the citizen or government views.

---

## 6. Current Progress Architecture Analysis

**Source File**: `frontend/src/pages/Progress.jsx`

### Observations
1. **Design Persona**:
   - Current `Progress.jsx` is built as an internal administrative oversight panel, displaying SLA deadlines, "Assigned Officer" names, "Complainants" counters, and a "Mark Resolved" button.
2. **Data Scope**:
   - Fetches `/api/challenges/` and filters for `status in ['routed', 'in_project', 'resolved']` across all issues in Jharkhand.
   - Does not query or isolate challenges submitted by the logged-in citizen.
3. **Lifecycle Misalignment**:
   - Uses steps tailored to internal field maintenance (`Complaint Registered`, `Assigned to Department`, `Field Team Dispatched`, `Work In Progress`, `Verification Pending`, `Resolved & Closed`).
   - Does not reflect the core SIC Portal lifecycle:
     - `Citizen Submission` → `AI Analysis & Dedup` → `Government Verification` → `University Routing` → `Research & Solution Development` → `Industry Collaboration` → `Field Implementation` → `Impact Verification`.
4. **Jargon**:
   - Displays raw internal states without citizen-friendly explanations.

---

## 7. Current Navigation & Sidebar Analysis

**Source File**: `frontend/src/components/layout/Sidebar.jsx`

### Observations
1. **Hardcoded Menus**:
   - `mainNav` contains:
     - Dashboard (`/dashboard/gov` dynamically mapped to `/dashboard/citizen` for Citizen)
     - Analytics (`/analytics`)
     - Maps (`/maps`)
     - Progress (`/progress`)
     - Universities (`/universities`)
2. **Exposure**:
   - A logged-in Citizen sees all 5 items in the sidebar.
   - Clicking `Analytics`, `Maps`, or `Universities` gives the Citizen full view of government analytics, geospatial heatmaps, and university directory management.
3. **Account Section**:
   - Contains `Profile` (`/profile` - route does not exist in `App.jsx`, renders fallback 404), `Notifications` (`/notifications` - does not exist), `Settings` (`/settings`).

---

## 8. Summary of Deficiencies to Address

1. **Backend Authorization & Ownership**: No JWT verification on endpoints; anyone can access/mutate any challenge.
2. **Citizen-Specific APIs**: Missing `GET /api/challenges/my` and authenticated challenge creation setting `created_by`.
3. **Evidence & Photo Upload System**: Missing media columns in `ChallengeEvidence`, missing static file hosting `/uploads`, missing upload API, missing image validation.
4. **Role-Based Routing (Frontend)**: Missing role guards on all routes in `App.jsx`; Citizen can access Gov, University, and Industry portals.
5. **Role-Aware Sidebar**: Citizen navigation must be restricted to Dashboard and Progress (plus Profile/Notifications).
6. **Citizen Dashboard Redesign**: Needs a welcoming, modern, trustworthy UI with step-guided form, GPS coordinates helper, district/block hierarchy, and photo upload with previews and removal.
7. **Citizen Progress Redesign**: Dedicated view showing only the citizen's own challenges, with clear stage-based timeline and citizen-friendly language.
8. **Evidence Gallery Continuity**: Submitted photos must be persisted and viewable in both Citizen Progress and Government Challenge Detail views.
