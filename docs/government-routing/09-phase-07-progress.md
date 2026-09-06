# Phase 7: Progress Integration

## Objective
Connect the frontend tracking and accountability dashboard (`Progress.jsx`) to the real routing data structures established in Phase 6, moving away from purely UI-mocked countdowns.

## Scope
- Modify the backend `GET /api/challenges/` endpoint to append the most recent `RoutingBatch` deadline (`active_deadline`) to routed challenges.
- Update `ChallengeOut` schema to expose `active_deadline`.
- Update `Progress.jsx` to consume the actual backend deadline for its live countdown timers.

## Files Modified
- `backend/db/schemas.py`: Added `active_deadline` to the `ChallengeOut` schema.
- `backend/api/challenges.py`: Modified the `list_challenges` function. When it encounters a challenge with `status == "routed"`, it queries the database for the active `RoutingBatch` and populates the `active_deadline` attribute.
- `frontend/src/pages/Progress.jsx`: 
  - Updated the due date fallback logic. It now attempts to read `cluster.active_deadline`. 
  - Changed the visual phrasing from "Overdue" to "Expired" to better reflect the routing SLA context.
  - Adjusted the default status checks to render "Awaiting Acceptance" instead of "Unassigned" when a challenge is routed but no project has started yet.

## Design Decisions
- **Avoid N+1 Endpoints**: Instead of forcing the frontend to make separate API calls to fetch batch data for every routed challenge, I opted to enrich the existing `ChallengeOut` response. This keeps the frontend architecture simple while still delivering the dynamic data.
- **Graceful Fallbacks**: The frontend maintains null checks so that if a challenge somehow bypasses the batch system, it won't crash the UI.

## Test Cases
- **Test 1**: Route a new challenge with a Custom Date of tomorrow. Open the Progress tab and verify the timer says ~"1d 0h left" instead of the default 7 days. (Passed).
- **Test 2**: Route a challenge with a deadline in the past. Verify the UI turns red and displays "Expired". (Passed).

## Next Phase
**Phase 8 — University Acceptance API**: With challenges now fully routed with deadlines, we must implement the "First-Accept-Wins" mechanism so that universities can accept invitations and convert them into projects.
