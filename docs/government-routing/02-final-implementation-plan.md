# Final Implementation Plan: Government Routing & University Integration

## Objective
To implement a robust Government-side Challenge Verification, Smart Routing, Response Deadline, and University Acceptance workflow based on the actual university dataset.

## Phase 1 — University Database
- **Objective:** Build the foundation for tracking universities.
- **Tasks:**
  - Create database migrations / SQLAlchemy model updates to support specific university fields (domains, output, status) within or alongside the `Organization` model.
  - Develop a Python CSV importer (`backend/seed_universities.py`) to parse `docs/Jharkhand universities list with domains.csv`.
  - Ensure idempotency so the script can be rerun without duplicating records.
  - Implement basic CRUD APIs (`/api/universities`).

## Phase 2 — University Directory UI
- **Objective:** Give the Government a UI to manage universities.
- **Tasks:**
  - Add "Universities" link to `frontend/src/components/layout/Sidebar.jsx`.
  - Create `frontend/src/pages/Universities.jsx` containing a list/table of institutions.
  - Implement search and filtering (by district, domain, status).
  - Include an add/edit modal to manage universities directly from the UI.

## Phase 3 — University Matching Engine
- **Objective:** Replace deterministic routing with a dynamic matcher.
- **Tasks:**
  - Update `backend/api/smart_router.py` to compare a challenge's domain/description against all seeded university domains and specializations.
  - Assign matching scores and generate explainable match reasons dynamically based on DB contents.
  - Remove hardcoded university names from the backend completely.

## Phase 4 — Government Verification
- **Objective:** Formalize the verification process.
- **Tasks:**
  - Update `Challenge` model to clearly track `pending_verification` -> `verified` -> `routed` -> `university_accepted`.
  - Record the user who verified the challenge and the timestamp in the audit trail.

## Phase 5 — Routing UI
- **Objective:** Enable multi-university routing and deadlines.
- **Tasks:**
  - Redesign `RoutingModal.jsx` to show recommended universities with checkboxes to select multiple.
  - Provide a search component to manually add universities not recommended by the AI.
  - Add a dropdown for Response Deadline (e.g., 3 days, 7 days, 14 days, custom date).
  - Update payload sent to `/api/challenges/{id}/route` to include an array of `university_ids` and the `deadline`.

## Phase 6 — Routing Backend
- **Objective:** Handle multiple invitations and response deadlines.
- **Tasks:**
  - Create `RoutingBatch` and `RoutingInvitation` models.
  - Implement `/api/challenges/{id}/route` to accept the new payload, create the batch, and individual invitations.
  - Persist the deadline.
  - Log audit trails.

## Phase 7 — Progress Integration
- **Objective:** Reflect accurate routing state in the Progress dashboard.
- **Tasks:**
  - Update `Progress.jsx` to fetch and display the `RoutingBatch` status.
  - Show individual university statuses ("Awaiting Response").
  - Dynamically compute time remaining based on the real `deadline` from the backend.
  - Show "Response Deadline Expired" if the deadline has passed without acceptance.

## Phase 8 — University Acceptance API
- **Objective:** Implement the atomic first-accept-wins logic.
- **Tasks:**
  - Create `/api/routing-invitations/{id}/accept` and `/api/routing-invitations/{id}/reject`.
  - Implement a transaction-safe acceptance method. If one university accepts, they become assigned, and all other invitations in the batch are marked `CLOSED`.
  - Update the `Challenge` status to `university_accepted` upon successful acceptance.

## Phase 9 — End-to-End QA + UI Polish
- **Objective:** Verify everything works seamlessly.
- **Tasks:**
  - Test happy path: Verify -> Route to 3 -> RIMS Ranchi accepts -> Assignment completed.
  - Test expiry path: Route -> Wait -> Expiry -> Needs Rerouting.
  - Test race conditions.
  - Refine UI interactions, typography, and colors.
