# Phase 8: University Acceptance API

## Objective
Implement the backend endpoint that allows a university to accept a routing invitation, enforcing the atomic "First-Accept-Wins" business logic.

## Scope
- Create `POST /api/challenges/invitations/{invitation_id}/accept` endpoint.
- Implement transactional state updates across `RoutingInvitation`, `RoutingBatch`, and `Challenge`.

## Files Modified
- `backend/api/challenges.py`: Added `accept_invitation` endpoint.

## Implementation Details
1. **Validation**: The endpoint verifies the invitation exists, is currently `pending`, the batch is `active`, and the deadline has not expired (raising 400s if any check fails).
2. **First-Accept-Wins Transaction**:
   - The accepted `RoutingInvitation` has its status set to `accepted` and `responded_at` populated.
   - All *other* pending invitations in the exact same `RoutingBatch` are automatically marked as `closed`. This instantly locks out the other universities that received the broadcast.
   - The parent `RoutingBatch` status transitions to `completed`.
   - The parent `Challenge` status transitions from `routed` to `in_project`.
3. **Database Concurrency**: Because all state changes are wrapped in a single `db.commit()` block via SQLAlchemy, the operation is atomic.

## Next Phase
**Phase 9 — End-to-End QA + UI Polish**: We will now test the full workflow (Government Verification → Multi-University Routing → Progress Tracking → University Acceptance) to ensure data flows correctly across the entire loop, and polish the UI components if any edge cases emerge.
