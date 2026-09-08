# Phase 6: Routing Backend

## Objective
Update the backend data model and API to support the 1-to-Many routing architecture, moving away from simple single-org assignment to formal batches and invitations.

## Scope
- Define `RoutingBatch` and `RoutingInvitation` models in SQLAlchemy.
- Create Pydantic schemas for the routing request and response.
- Update `POST /api/challenges/{challenge_id}/route` to accept an array of `org_ids` and a `deadline`, generating the batch and invitation records.

## Files Modified
- `backend/db/models.py`: Added `RoutingBatch` (tracks `deadline` and `note`) and `RoutingInvitation` (tracks per-university state: `pending`, `accepted`, `rejected`, `expired`).
- `backend/db/schemas.py`: Defined `RoutingBatchOut`, `RoutingInvitationOut`, and `ChallengeRouteRequest`.
- `backend/api/challenges.py`: Rewrote the `route_challenge` endpoint to create one `RoutingBatch` and N `RoutingInvitation`s instead of just modifying the challenge state. It still transitions the `Challenge` to `routed`.

## Database Changes
- Used SQLAlchemy `create_all` to automatically create the new `routing_batches` and `routing_invitations` tables in the SQLite database.

## Design Decisions
- **1-to-Many Architecture**: By wrapping the routing action in a `RoutingBatch`, we can easily track a single routing event (with a single deadline) that was broadcast to multiple universities.
- **Invitation Statuses**: Individual `RoutingInvitation`s have their own state (`pending`, `accepted`, `rejected`), which will allow us in a later phase to implement the "first-accept-wins" concurrency rule, where accepting one invitation automatically closes the others in the batch.
- **Graceful Error Handling**: If an invalid `org_id` is passed, the backend silently ignores it rather than failing the whole batch, ensuring the other valid universities still receive the invitation.

## Test Cases
- **Test 1**: Verify the routing modal now successfully posts to the backend and the challenge is removed from the GovDashboard active list. (Passed - The API returns the `RoutingBatchOut` and the dashboard refreshes).
- **Test 2**: Verify the new tables exist in SQLite. (Passed).

## Next Phase
**Phase 7 — Progress Integration**: We need to hook the frontend `Progress.jsx` up to this real routing state, replacing its mocked countdown timers with real deadline calculations based on the `RoutingBatch`.
