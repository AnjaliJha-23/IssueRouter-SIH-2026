# Current State: Government Routing & University Integration

## 1. Repository Audit
The IssueRouter platform currently consists of a FastAPI backend using SQLite and SQLAlchemy ORM, and a React frontend utilizing Tailwind CSS and Lucide React icons.

## 2. CSV Audit
The target CSV file is located at `docs/Jharkhand universities list with domains.csv`.
It contains 35 entries, providing real data on universities in Jharkhand.
The columns are:
- `University Name`
- `Location`
- `Domains of Research & Specialisation`
- `Successful Research Output (Est.)`

## 3. Existing Architecture Analysis
### Backend
- **Database Models (`backend/db/models.py`)**: Currently defines `Organization`, `User`, `Challenge`, `Match`, and `Project`. The `Challenge` model tracks a simple string status.
- **Smart Router API (`backend/api/smart_router.py`)**: Employs deterministic/hardcoded mocking. If a challenge domain is "HealthTech", it specifically queries "RIMS Ranchi" and "Tata Steel CSR". It doesn't actually search or rank based on university domains from the entire database.
- **Challenges API (`backend/api/challenges.py`)**: Has a `/route` endpoint that just changes the status to `routed` and assumes a single `org_id` target, lacking a structured invitation or deadline model.

### Frontend
- **GovDashboard (`frontend/src/pages/GovDashboard.jsx`)**: Lists challenges and triggers the routing workflow via a drawer/modal. Active challenges that are 'routed' are filtered out.
- **RoutingModal (`frontend/src/components/ui/RoutingModal.jsx`)**: Submits a route request to a single partner (the first one matching) and doesn't handle multiple selection or response deadlines.
- **Progress Tracker (`frontend/src/pages/Progress.jsx`)**: Displays "routed", "in_project", or "resolved" challenges. It uses local UI state (a countdown of 7 days derived purely on the client side from `created_at`) rather than a real backend-calculated deadline.
- **Sidebar (`frontend/src/components/layout/Sidebar.jsx`)**: Currently lacks a dedicated "Universities" section. 

## 4. Current Workflow Analysis
Presently, the workflow is:
1. Challenge is verified.
2. The user opens the Routing Modal.
3. The API suggests mock matches.
4. The user clicks "Confirm Routing" for a single selected organization.
5. The challenge status becomes `routed` and it disappears from the active dashboard, moving to Progress.

**What's missing / mock:**
- No real university directory or management.
- No response deadlines.
- No routing to *multiple* universities simultaneously with a first-accept-wins race condition.
- No expiry/re-routing mechanism.

## 5. Data Model Analysis
The current `Match` and `Challenge` models are insufficient.
We need:
- `University` (an extension of `Organization` or properly defined as `Organization` with specific fields from the CSV).
- `RoutingBatch` to group invitations for a specific challenge.
- `RoutingInvitation` to track each university's status (INVITED, ACCEPTED, REJECTED, CLOSED, EXPIRED) and the deadline.

## 6. UX Analysis
The current UI is clean, using a glassmorphism style. However, the Routing Modal needs to support multi-select (checkboxes) and a deadline dropdown. A completely new page `Universities` is needed to manage the institutions. The `Progress` page needs to accurately reflect real invitation statuses (e.g. "RIMS Ranchi: Awaiting Response").

## 7. What Must Change
- Database schemas and models must support the `RoutingBatch` and `RoutingInvitation` concepts.
- A CSV parser must be written to safely seed the universities into the `Organization` table.
- A `Universities` dashboard page must be added to the frontend.
- The `smart_router.py` must use the seeded university data to match dynamically rather than hardcoding.
- `RoutingModal.jsx` must support selecting a deadline and multiple universities.
- `Progress.jsx` must consume the real routing invitations and deadlines from the backend.
