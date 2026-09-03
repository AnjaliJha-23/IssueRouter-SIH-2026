# Repository Analysis — Government Dashboard (SIH 2026)

## 1. Current Architecture

### Frontend
- **Framework**: React 19 as a Single Page Application (SPA) built with Vite (Note: `README.md` incorrectly states Next.js, but `package.json` and `vite.config.js` confirm it is a Vite React SPA).
- **Routing**: `react-router-dom` v7.
- **Styling**: Tailwind CSS v4.
- **State Management**: React Context (`IssueContext.jsx`, `AuthContext.jsx`, `ThemeContext.jsx`).
- **Components**: Recharts for analytics, Leaflet for maps.
- **Key Files**: 
  - `src/App.jsx` (routing)
  - `src/pages/GovDashboard.jsx` (current government dashboard)
  - `src/pages/Dashboard.jsx` (legacy priority complaints view)
  - `src/components/ui/ChallengeCard.jsx`, `FilterBar.jsx`

### Backend
- **Framework**: FastAPI with Python 3.x.
- **Database**: SQLite (`issueRouter.db`) via SQLAlchemy ORM.
- **Key Files**: 
  - `db/models.py`, `db/schemas.py`
  - `api/challenges.py`, `api/smart_router.py`, `api/stats.py`
  - `seed_mock_data.py` (provides Jharkhand-specific data)

## 2. Existing Data Model

The current domain models in `backend/db/models.py` are a solid starting point but treat challenges as somewhat flattened objects:
- **`Challenge`**: Contains `id`, `title`, `description`, `domain`, `status`, `priority_score`, `location`, `lat`, `lng`, `department`, `complaint_count` (which implies evidence aggregation), `rt_reach`, `trend`, `verified`, `created_at`.
- **`Match`**: Tracks university routing suggestions with `challenge_id`, `org_id`, `match_score`, `match_reason`, `status`.
- **`Project`**: Created automatically when a match is accepted, tracking milestones.
- **`Organization` & `User`**: Standard RBAC and entity tables.

## 3. Existing APIs
- `GET /api/challenges/`: Fetches challenges with basic filtering (status, domain, verified).
- `POST /api/challenges/`: Creates a challenge with mock NLP logic for domain and priority assignment.
- `PATCH /api/challenges/{id}/verify`: Toggles verification status.
- `POST /api/matches/generate/{id}`: Generates deterministic mock matches (e.g., RIMS Ranchi, Tata Steel) for a challenge based on domain.
- `PATCH /api/matches/{id}`: Accepts/rejects a match and auto-creates a `Project` if accepted.

## 4. Existing Dashboard Flow
1. **Load**: `GovDashboard.jsx` fetches challenges from `/api/challenges/` and stats from `/api/stats/overview`.
2. **Filter**: Mostly client-side filtering via search string, location, department, and status tabs.
3. **View**: Renders a grid of `ChallengeCard` components.
4. **Action**: Officer can click "Verify" on a card which calls the PATCH endpoint. 

## 5. Existing Problems & Architectural Gaps
- **Flattened Evidence**: `complaint_count` exists, but there is no explicit JSON or relational model to show the breakdown of evidence (e.g., 47 Twitter, 8 Citizen, 2 NGO). It currently treats it as a single aggregated number.
- **Client-Side Filtering**: Search and location filtering in `GovDashboard.jsx` is done entirely on the client side (`useMemo`), which will not scale and breaks deterministic priority sorting if not handled carefully.
- **Routing UX**: Verification happens, but the "Routing" step is not a dedicated premium drawer/modal. The transition from "Verified" to "Matched" to "Project" is somewhat hidden in backend triggers rather than explicit government action.
- **Visual Design**: The UI uses generic card expansions rather than a professional "Intelligence Drawer" suitable for a Command Center.

## 6. Risks
- **Breaking Maps & Progress**: Modifying the `Challenge` state machine (status values) could break `Maps.jsx` and `Progress.jsx` if they rely on hardcoded statuses like 'pending', 'inprogress', 'resolved'.
- **Context Conflicts**: The frontend uses `IssueContext.jsx` heavily. We must ensure our updates to `Challenge` objects via the Gov Dashboard sync properly with this global context so other pages (like Maps) stay updated.

## 7. Proposed Changes & Backward Compatibility Strategy
- **Data Model**: Extend `Challenge` slightly to include `source_counts` (JSON) to cleanly represent Twitter vs Citizen vs NGO evidence without breaking existing `complaint_count` logic. 
- **States**: Expand `Challenge.status` carefully. Existing statuses: `pending`, `verified`, `matched`, `in_project`, `resolved`. We will map the requested SIH lifecycle states to these or expand the enum, ensuring `Progress.jsx` is updated to handle them.
- **UI Components**: 
  - Create a new `ChallengeDetailDrawer.jsx` instead of modifying `ChallengeCard.jsx`'s expansion, keeping the card dense.
  - Centralize Jharkhand geographic data (districts/blocks) in a `data/geography.js` file for consistent filtering.

## 8. Files to Change vs. Protect
- **Likely to Change**:
  - `frontend/src/pages/GovDashboard.jsx`
  - `frontend/src/components/ui/ChallengeCard.jsx`
  - `frontend/src/components/ui/FilterBar.jsx`
  - `backend/db/models.py` & `schemas.py` (minor extensions)
  - `backend/api/challenges.py` (enhanced filtering)
- **Do NOT Touch (unless explicitly needed)**:
  - `frontend/src/pages/CitizenDashboard.jsx`
  - `frontend/src/pages/OrgDashboard.jsx`
  - `backend/pipeline/`
  - NLP logic in `api/challenges.py` (preserve existing mock logic)

## 9. Recommended Implementation Sequence
1. **Phase 1**: Database/API extension (Source aggregation, expanded statuses).
2. **Phase 2**: GovDashboard redesign (KPIs, Layout, dense ChallengeCard).
3. **Phase 3**: Robust Filtering + Backend integration.
4. **Phase 4**: Challenge Detail Drawer (AI analysis, evidence gallery).
5. **Phase 5**: Smart Routing UI (University selection modal).
6. **Phase 6**: Progress integration (handoff from dashboard to tracking).
7. **Phase 7**: Polish & QA.
