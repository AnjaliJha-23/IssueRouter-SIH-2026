# Implementation Summary: Complete Citizen Experience & Strict RBAC Enforcement

**Project**: SIC Portal (IssueRouter) · SIH 2026 · Team Convergence  
**Scope**: Complete Citizen Experience Implementation & RBAC Protection  
**Status**: Completed & Verified  

---

## 1. Executive Overview

The Citizen Portal has been transformed into a streamlined, high-trust, and reassuring societal challenge reporting and tracking platform. Citizens can now easily report local civic/societal issues, upload authentic photo evidence, and follow their challenges from initial submission through university research, industrial prototyping, and government verification.

Simultaneously, enterprise-grade Role-Based Access Control (RBAC) was implemented across both frontend navigation/routes and backend REST endpoints. Citizens are strictly prevented from viewing or accessing administrative interfaces or executing privileged mutations (verification, routing, university partner management, proposals, stats).

---

## 2. Completed Architecture & Deliverables

### Phase 1: Backend Security & RBAC Enforcement
- **JWT Verification & Role Checks (`backend/api/auth.py`)**:
  - Implemented `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")`.
  - Added `decode_token(token)`, `get_current_user`, `get_optional_current_user`, and `require_roles(*roles)` FastAPI dependency factories.
  - Secret key RFC 7518 compliance (>32 bytes) enforced.
  - User model updated with proper `id` mapping and authenticated payload.
- **Strict Endpoint Hardening**:
  - `GET /api/challenges/my`: Returns strictly challenges submitted by `current_user.id` (`created_by == current_user.id`).
  - `PATCH /api/challenges/{id}/verify`: Restricted to `Gov` role (HTTP 403 for citizens).
  - `POST /api/challenges/{id}/route`: Restricted to `Gov` role (HTTP 403 for citizens).
  - `GET /api/stats/overview` & `GET /api/stats/locations`: Restricted to `Gov`, `University`, `Industry` (HTTP 403 for citizens).
  - `GET /api/universities/`: Restricted to `Gov`, `University`, `Industry` (HTTP 403 for citizens).
  - `POST /api/projects/{id}/proposal`: Restricted to `Gov`, `University` (HTTP 403 for citizens).
  - Unauthenticated submissions to `/api/challenges/` blocked with HTTP 401.

### Phase 2: Evidence & Photo Storage Engine
- **File Upload Handler (`POST /api/challenges/upload-photos`)**:
  - Accepts up to 3 image files per challenge submission.
  - Validates MIME types (`image/jpeg`, `image/png`, `image/webp`) and enforces 5MB file size limit.
  - Generates secure unique filenames (`ev_<hex>.ext`) and stores them in `backend/uploads/evidence/`.
- **Static Asset Serving & Database Persistence**:
  - `backend/main.py` mounts `/uploads` via `StaticFiles`.
  - Added `media_urls` JSON column to `Challenge` and `ChallengeEvidence` SQLAlchemy models with automatic startup SQLite column migration.
  - Exposed `media_urls` in Pydantic schemas (`ChallengeCreate`, `ChallengeBase`, `ChallengeOut`).

### Phase 3: Frontend Route Guards & Role-Aware Navigation
- **Automatic Token Interceptor (`frontend/src/api/client.js`)**:
  - Axios request interceptor injects `Authorization: Bearer <token>` from `localStorage.getItem("token")` into every outgoing HTTP request.
- **Strict Route Protection (`frontend/src/components/ProtectedRoute.jsx` & `App.jsx`)**:
  - Implemented route-level `allowedRoles` enforcement.
  - Unauthorized role navigation triggers an immediate redirect to `/unauthorized`.
  - Root route (`/`) automatically redirects authenticated users to their specific dashboard (`/` -> `/dashboard` for Citizens, `/government/dashboard` for Gov, etc.).
- **Access Denied Page (`frontend/src/pages/Unauthorized.jsx`)**:
  - Styled with clear contextual messaging and role-appropriate return buttons.
- **Streamlined Citizen Navigation (`frontend/src/components/layout/Sidebar.jsx`)**:
  - Configured `ROLE_NAVIGATION` dictionary.
  - Citizen navigation displays **only**:
    - **MAIN**:
      - `Dashboard` (Submit Societal Challenge)
      - `My Progress` (Track Submitted Challenges)
    - **ACCOUNT**:
      - `Profile`
      - `Notifications`
      - `Settings`
  - All admin sections (Analytics, Maps, Pipeline, Routing, Universities, Projects, Verification) are completely removed from citizen sidebar and hidden from DOM.

### Phase 4: Premium Citizen Dashboard UX (`frontend/src/pages/CitizenDashboard.jsx`)
- **4-Step Intuitive Workflow**:
  1. **The Problem**: Domain selector cards with clear icons, title, and detailed description with live character counter.
  2. **Location**: District selector pre-populated with all 24 Jharkhand districts, block/tehsil input, landmark/address, and a one-click **GPS Coordinate Finder** using browser Geolocation API.
  3. **Photo Evidence**: Drag-and-drop / file browser uploading up to 3 real photos, image format & size validation, live thumbnail preview strip with remove action, and full-screen image lightbox.
  4. **Review & Submit**: Structured summary card reviewing all inputs, submit button with loading state, and post-submission modal with reference ID and direct deep-link to **My Progress**.
- **Contextual Guidance**: Helpful side panel explaining the 4-step impact journey to establish citizen trust.

### Phase 5: Citizen Progress & Timeline Tracker (`frontend/src/pages/CitizenProgress.jsx`)
- **Isolated Citizen Data**:
  - Fetches strictly the user's submitted challenges via `GET /api/challenges/my`.
- **Reassuring 8-Stage Lifecycle Tracker**:
  - Citizen-facing translated stage titles and descriptions:
    1. *Submission Received* — Challenge logged in state registry.
    2. *Field Verification* — District officer reviewing authenticity.
    3. *Academic Routing* — Matched to specialized university departments.
    4. *Research in Progress* — Academic labs engineering solutions.
    5. *Proposed Solution* — Technical blueprint under evaluation.
    6. *Industry Collaboration* — Corporate/manufacturing partner engaged.
    7. *Field Implementation* — Deployment on the ground.
    8. *Impact Verified* — Civic issue successfully resolved.
- **Evidence Inspection**:
  - Attached photo evidence thumbnail gallery with click-to-enlarge lightbox.
- **Search & Empty States**:
  - Real-time search filter across challenge titles and districts.
  - Helpful empty state when no challenges exist with a direct action to submit a challenge.

### Phase 6: Cross-Stakeholder Evidence Continuity (`frontend/src/components/ui/ChallengeDetailDrawer.jsx`)
- Seamless transition between citizen submission and government administration.
- Real photos uploaded by citizens appear directly in the canonical **Challenge Evidence** tab and government dossier drawer.
- Lightbox zoom support preserves forensic inspection capability for government reviewers.

---

## 3. Verification & Test Results

The end-to-end integration test script (`backend/test_citizen_e2e.py`) was executed against the live application context:

| Test ID | Test Scenario | Expected Outcome | Result |
|---|---|---|---|
| **TEST 1** | Citizen Authentication (`/api/auth/login`, `/api/auth/me`) | Returns valid JWT token; role is `Citizen`; name is Rahul Kumar | **PASS** |
| **TEST 2** | Evidence Photo Upload (`/api/challenges/upload-photos`) | Uploads PNG evidence; serves static image via `/uploads/evidence/*` with HTTP 200 | **PASS** |
| **TEST 3** | Challenge Creation (`POST /api/challenges/`) | Challenge stored with `created_by=user-cit-1`, `district=Ranchi`, and `media_urls` | **PASS** |
| **TEST 4** | Progress Isolation (`GET /api/challenges/my`) | Citizen sees only their own challenges; uploaded photos included | **PASS** |
| **TEST 5.1** | Verification Route Protection (`PATCH /api/challenges/{id}/verify`) | Citizen attempt blocked with HTTP 403 Forbidden | **PASS** |
| **TEST 5.2** | Routing Route Protection (`POST /api/challenges/{id}/route`) | Citizen attempt blocked with HTTP 403 Forbidden | **PASS** |
| **TEST 5.3** | Stats Route Protection (`GET /api/stats/overview`) | Citizen attempt blocked with HTTP 403 Forbidden | **PASS** |
| **TEST 5.4** | University API Protection (`GET /api/universities/`) | Citizen attempt blocked with HTTP 403 Forbidden | **PASS** |
| **TEST 5.5** | Project Proposal Protection (`POST /api/projects/{id}/proposal`) | Citizen attempt blocked with HTTP 403 Forbidden | **PASS** |
| **TEST 5.6** | Unauthenticated Submission (`POST /api/challenges/` without token) | Request blocked with HTTP 401 Unauthorized | **PASS** |
| **TEST 6** | Government View & Evidence Continuity | Gov officer views challenge with citizen photos; verifies challenge; accesses stats | **PASS** |

### Frontend Build Verification
- Vite production build executed with `npm run build`:
  - 1825 modules transformed.
  - Output generated to `dist/` with **0 errors**.

---

## 4. Key Security & Design Decisions

1. **Defense-in-Depth RBAC**: Route guarding occurs at three levels:
   - UI Level: `Sidebar.jsx` only renders navigation items permitted for the user's role.
   - Client Route Guard: `ProtectedRoute.jsx` intercepts URL bar tampering and routes to `/unauthorized`.
   - Backend API Level: `require_roles(...)` validates JWT claims on every single API request, guaranteeing zero data leaks even if client-side code is bypassed.
2. **Data Isolation by Design**: `GET /api/challenges/my` filters at the SQL level (`created_by == current_user.id`), ensuring citizens never have visibility into others' private submissions unless published to the public registry.
3. **Forensic Evidence Integrity**: Citizen photos are saved immutably with SHA/hex-randomized filenames, stored locally under `backend/uploads/evidence/`, and linked directly in the database record for uninterrupted cross-role inspection.
