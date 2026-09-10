# IssueRouter — Citizen Portal Final Implementation Plan

**Project**: SIC Portal · SIH26043 · Team Convergence  
**Target Scope**: Complete Citizen Experience & Hardened RBAC Security  
**Target Branches**: `backend` & `frontend`  
**Date**: September 2026  
**Status**: Approved for Phased Execution  

---

## 1. Architectural Blueprint & Target Model

### 1.1 Core Flow
```
Citizen User (Authenticated)
  │
  ├─► [Citizen Dashboard]
  │     ├── Hero CTA & Information
  │     ├── Geolocation / District & Locality Selection
  │     ├── Photo Upload & Previews (Max 3, validated, uploaded to /uploads/evidence)
  │     └── POST /api/challenges (Authenticated via Bearer Token)
  │
  ├─► [Backend API]
  │     ├── JWT Validation & Ownership Tagging (created_by = current_user.id)
  │     ├── Challenge Record Created (CHL-2026-XXXX)
  │     ├── ChallengeEvidence Record Created (media_urls = [saved_photo_urls])
  │     └── AI Categorization (Domain, Priority, Location Extraction)
  │
  ├─► [Citizen Progress]
  │     ├── GET /api/challenges/my (Strict ownership: only citizen's submissions)
  │     ├── Stage-Based Lifecycle Tracker (Submitted → AI Analysis → Verified → Routed → University Research → Solution → Industry Collab → Implementation → Impact)
  │     ├── Non-technical, reassuring status descriptions
  │     └── Original Evidence Photos Gallery with Lightbox
  │
  └─► [Government Challenge Detail & Dossier]
        └── Canonical Challenge views load the citizen's actual photos from ChallengeEvidence.media_urls
```

---

## 2. Actual Repository Files & Planned Changes

| Component / Layer | File Path | Nature of Changes |
|---|---|---|
| **Backend Core** | `backend/main.py` | Mount `StaticFiles` for `/uploads`, register upload directory, ensure DB column migrations. |
| **Backend Database** | `backend/db/models.py` | Add `media_urls` (JSON) to `ChallengeEvidence` and `Challenge` models. |
| **Backend Schemas** | `backend/db/schemas.py` | Add `evidence_photos: List[str]` to `ChallengeOut` and `ChallengeBase`; add `district`, `block`, `media_urls` to `ChallengeCreate`. |
| **Backend Security** | `backend/api/auth.py` | Add `get_current_user`, `get_current_active_user`, and `require_roles(*roles)` dependencies. Ensure token expiration & PyJWT decoding. |
| **Backend API** | `backend/api/challenges.py` | 1. Implement `GET /api/challenges/my` (requires authenticated Citizen/Gov).<br>2. Secure `POST /api/challenges/` to set `created_by` and create linked `ChallengeEvidence` with photos.<br>3. Secure `PATCH /{id}/verify` and `POST /{id}/route` with `require_roles('Gov')`.<br>4. Add photo upload endpoint `POST /api/challenges/upload-evidence`. |
| **Backend API** | `backend/api/stats.py` | Protect `/api/stats/overview` and `/api/stats/locations` with `require_roles('Gov')`. |
| **Backend API** | `backend/api/projects.py` | Protect proposal submissions with `require_roles('University', 'Gov')`. |
| **Backend API** | `backend/api/universities.py` | Protect university mutations with `require_roles('Gov')`. |
| **Frontend Auth Context** | `frontend/src/context/AuthContext.jsx` | Fix hardcoded `?email=admin` in background sync; ensure Bearer token is passed in all API calls; retain clean user state. |
| **Frontend Route Guards** | `frontend/src/components/ProtectedRoute.jsx` | Ensure proper redirection when `allowedRoles` does not match, returning to role dashboard or `/unauthorized`. |
| **Frontend Routing** | `frontend/src/App.jsx` | Segregate routes by role: Citizen, Gov, University, Industry. Prevent unauthorized cross-role access. |
| **Frontend Navigation** | `frontend/src/components/layout/Sidebar.jsx` | Implement clean role-based navigation dictionary (`CITIZEN_NAV`, `GOV_NAV`, `UNIVERSITY_NAV`, `INDUSTRY_NAV`). Citizen sees ONLY Dashboard, Progress, Profile, Notifications, Settings. |
| **Frontend Topbar** | `frontend/src/components/layout/Topbar.jsx` | Adjust page labels, breadcrumbs, search visibility for Citizen vs Government. |
| **Frontend Citizen Dashboard** | `frontend/src/pages/CitizenDashboard.jsx` | Complete redesign into premium, welcoming Citizen experience with step form, GPS helper, district dropdown, and photo upload with previews. |
| **Frontend Citizen Progress** | `frontend/src/pages/Progress.jsx` or `frontend/src/pages/CitizenProgress.jsx` | Implement dedicated Citizen Progress view with stage tracker, clean cards, status translation, and original evidence gallery. |
| **Frontend Gov Dossier** | `frontend/src/components/ui/ChallengeDetailDrawer.jsx` | Display actual citizen-submitted photos from `challenge.media_urls` or `evidence` when available. |

---

## 3. Phased Implementation Plan

### Phase 1: Backend Security, RBAC & Authentication Hardening
- **Objective**: Prevent unauthorized API access and enforce data ownership at the server level.
- **Tasks**:
  1. Add dependencies in `backend/api/auth.py`:
     - `get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User`
     - `require_roles(*roles: str)` returning a dependency that checks `current_user.role in roles`.
     - Update `/api/auth/me` to read from the authenticated user token instead of open `?email=...`.
  2. Protect endpoints in `backend/api/challenges.py`:
     - `GET /api/challenges/my`: Authenticated, filters `Challenge.created_by == current_user.id`.
     - `POST /api/challenges/`: Authenticated, sets `Challenge.created_by = current_user.id`.
     - `PATCH /api/challenges/{id}/verify`: Restricted to `role == 'Gov'`.
     - `POST /api/challenges/{id}/route`: Restricted to `role == 'Gov'`.
  3. Protect endpoints in `backend/api/stats.py`, `backend/api/projects.py`, `backend/api/universities.py`:
     - Disallow Citizen access to government verification, administrative routing, and university roster mutations.
- **Verification**: Run curl/python requests with Citizen token to verify endpoints return `403 Forbidden` for government actions and `200 OK` for own challenge operations.

### Phase 2: Evidence & Photo Storage Engine
- **Objective**: Enable real photo uploads that persist into canonical `ChallengeEvidence`.
- **Tasks**:
  1. Update `backend/db/models.py`:
     - Add `media_urls = Column(JSON, nullable=True)` to `ChallengeEvidence`.
     - Add `media_urls = Column(JSON, nullable=True)` to `Challenge`.
  2. In `backend/main.py`:
     - Create `backend/uploads/evidence` directory.
     - Mount `app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")`.
     - Add migration check to ensure SQLite adds columns if missing.
  3. In `backend/api/challenges.py`:
     - Create `POST /api/challenges/upload-evidence` accepting `files: List[UploadFile]`.
     - Validate: Max 3 files, allowed formats (`image/jpeg`, `image/png`, `image/webp`), max size 5MB each.
     - Save files with unique names (`ev_{uuid}_{filename}`) to `backend/uploads/evidence/`.
     - Return array of accessible URLs (e.g., `/uploads/evidence/ev_...`).
  4. In `POST /api/challenges/`:
     - Accept optional `media_urls: List[str]` in `ChallengeCreate`.
     - Create `Challenge` and `ChallengeEvidence(source="citizen", media_urls=media_urls, ...)`.
     - Expose `media_urls` in `ChallengeOut`.
- **Verification**: Upload sample image through API, confirm file exists on disk, confirm URL loads image.

### Phase 3: Frontend Route Protection & Role-Aware Navigation
- **Objective**: Prevent citizens from manually visiting Government, University, or Industry URLs.
- **Tasks**:
  1. In `frontend/src/components/ProtectedRoute.jsx`:
     - Verify token and user role.
     - If role is not permitted, redirect to the user's appropriate home (`/dashboard/citizen` for Citizen) or `/unauthorized`.
  2. In `frontend/src/App.jsx`:
     - Wrap routes with specific role arrays:
       - Citizen: `/dashboard/citizen`, `/progress`, `/profile`
       - Gov: `/dashboard/gov`, `/analytics`, `/maps`, `/universities`
       - University: `/dashboard/org`, `/project/:id`
       - Industry: `/dashboard/industry`
     - Update `/dashboard` to redirect dynamically based on `user.role`.
  3. In `frontend/src/components/layout/Sidebar.jsx`:
     - Replace hardcoded `mainNav` with a role-based dictionary:
       - `CITIZEN`: `[ { label: 'Dashboard', path: '/dashboard/citizen', icon: LayoutDashboard }, { label: 'Progress', path: '/progress', icon: TrendingUp } ]`
       - `GOV`: Retains Gov Dashboard, Analytics, Maps, Progress, Universities.
       - `UNIVERSITY`: Org Dashboard, Workspace, Progress.
       - `INDUSTRY`: Industry Dashboard, Projects.
     - Restrict Account menu for Citizens to Profile, Notifications, Settings.
  4. In `frontend/src/context/AuthContext.jsx`:
     - Remove `fetch('/api/auth/me?email=admin')`.
     - Add helper to get `authHeaders()` with `Authorization: Bearer <token>`.
- **Verification**: Log in as Citizen (`rahul@citizen.in`), verify sidebar only shows Dashboard & Progress. Type `/dashboard/gov` in browser address bar, verify redirect/denial.

### Phase 4: Premium Citizen Dashboard & Submission Form
- **Objective**: Create an inviting, trustworthy, high-polish citizen interface.
- **Tasks**:
  1. Redesign `CitizenDashboard.jsx`:
     - **Hero Section**: Welcoming message, clear explanation of how reporting works.
     - **Structured Step Form**:
       - Step 1: *What is the problem?* (Title input with clear placeholder, description textarea with helper tips and character counter).
       - Step 2: *Where is it happening?* (Jharkhand district select with all 24 districts, locality/block input, "Use my current location" GPS button).
       - Step 3: *Add Evidence* (Drag & drop / click upload zone, thumbnail preview grid, hover delete, click to view full size modal, upload progress indicator).
       - Step 4: *Submit* (Duplicate click prevention, submitting state, success modal with Challenge ID, date, and "Track Progress" action).
     - **Recent Community Activity**: Anonymized, public challenge cards showing recent community impacts without exposing citizen contact details.
- **Verification**: Submit challenge with photos, check database for new record with citizen ownership and photo URLs.

### Phase 5: Citizen Progress & Timeline Experience
- **Objective**: Provide a dedicated tracking view of the citizen's own challenges.
- **Tasks**:
  1. Build a dedicated Citizen Progress view (within `Progress.jsx` or role-delegated component):
     - Fetches only the user's challenges via `GET /api/challenges/my`.
     - Status Card List:
       - Challenge title & reference ID (e.g. `CHL-2026-0042`).
       - Location & date.
       - Stage badge and visual stage progression indicator.
       - Last activity update (e.g. "Verified by nodal officer", "RIMS Ranchi accepted research challenge").
     - Empty State: Encouraging illustration and copy ("You haven't reported any challenges yet") with CTA button to report.
     - Detailed Timeline Modal:
       - 8-stage lifecycle tracker with clean icons.
       - Non-technical, reassuring status labels.
       - Original submitted evidence gallery with lightbox preview.
       - Reassurance note ("AI analysis and government verification in progress").
- **Verification**: View progress list as Citizen; verify only own challenges appear; click challenge to open full tracking view.

### Phase 6: Cross-Stakeholder Evidence Continuity
- **Objective**: Ensure photos uploaded by the citizen are visible in the Government Challenge Dossier.
- **Tasks**:
  1. In `frontend/src/components/ui/ChallengeDetailDrawer.jsx`:
     - Update the Evidence tab to display real photos from `challenge.media_urls` or `challenge.evidence` if present, falling back gracefully to mock inspection images only when no citizen photos were attached.
- **Verification**: Log in as Gov, open the challenge submitted in Phase 4, verify citizen's actual photos appear in the dossier.

### Phase 7: Verification, Regression Checks & Documentation
- **Objective**: Verify end-to-end functionality, run regression checks, and clean up.
- **Tasks**:
  1. Run comprehensive automated test script covering:
     - Citizen login and token receipt.
     - Citizen challenge submission with photo upload.
     - Citizen retrieval of own challenges (`/api/challenges/my`).
     - Rejection of citizen attempting government endpoints (403 Forbidden).
     - Rejection of unauthenticated users (401 Unauthorized).
     - Frontend build verification (`npm run build`).
  2. Document completed state in `docs/citizen-portal/03-implementation-summary.md`.

---

## 4. Backward Compatibility & Security Assurance

1. **Existing Government & University Workflows**:
   - `GovDashboard`, `OrgDashboard`, `IndustryDashboard`, `Universities`, and `ProjectWorkspace` continue to function without disruption.
   - Government users retain full visibility into all challenges and will now additionally see real citizen-uploaded photos.
2. **Database Backward Compatibility**:
   - Newly added columns (`media_urls` in `Challenge` and `ChallengeEvidence`) are nullable, ensuring all existing seeded data continues to work without corruption.
3. **No Secret Leaks**:
   - Personal citizen information (email, password hash, phone) is never exposed in public challenge summaries.
