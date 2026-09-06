# Phase 4: Government Verification

## Objective
Formalize the challenge verification workflow to ensure an auditable trail of when and by whom a challenge was verified before it is routed to a university.

## Scope
- Update the `Challenge` database model and schemas to track verification details.
- Modify the existing verification API endpoint to persist the timestamp and user ID during the state transition from `pending_verification` to `verified`.

## Files Modified
- `backend/db/models.py`: Added `verified_by` and `verified_at` columns to the `Challenge` model.
- `backend/db/schemas.py`: Added `verified_by` and `verified_at` to the `ChallengeBase` Pydantic model.
- `backend/api/challenges.py`: Updated the `PATCH /api/challenges/{challenge_id}/verify` endpoint. When `verified` is set to `true`, the backend now automatically populates the `verified_at` timestamp and assigns the `verified_by` field to the mocked Government Officer user ID (`user-gov-1`).

## Database Changes
- Altered the `challenges` table in `issueRouter.db` to add columns: `verified_by` (VARCHAR), `verified_at` (DATETIME).

## API Changes
- `PATCH /api/challenges/{challenge_id}/verify`: The payload remains the same (`{"verified": true}`), but the response now includes the populated `verified_at` and `verified_by` fields if the state transition was successful.

## Design Decisions
- For this MVP phase, authentication is handled via a context mock (`user-gov-1` represents the admin). In a production environment, this would be derived dynamically from the FastAPI `Depends(get_current_user)` context.
- We deliberately only set the verification timestamp when transitioning *from* `pending_verification` to avoid overwriting the original audit trail if a challenge is modified later.

## Test Cases
- **Test 1**: Send a PATCH request to verify a challenge and verify the `verified_at` and `verified_by` fields are populated in the database. (Passed).

## Regression Checks
- The frontend `GovDashboard.jsx` handles the new response seamlessly because it expects the standard `ChallengeOut` schema. The verification UI remains fully functional.

## Next Phase
**Phase 5 — Routing UI**: With verification auditable, we will now rebuild the `RoutingModal.jsx` to allow the Government officer to select multiple universities and define a specific response deadline.
