# Phase 1: Foundation — Government Dashboard (SIH 2026)

## Objective
Establish the minimum required data foundation for source aggregation and expanded lifecycle states required by the SIH 2026 workflow, without breaking existing logic.

## Files Changed
- `backend/db/models.py`: Added `source_counts` (JSON), `ai_confidence` (Float), and `duplicate_risk` (Float) to `Challenge` model. Expanded default status to `pending_verification`.
- `backend/db/schemas.py`: Updated `ChallengeBase` with the new fields to ensure they are returned via the API.
- `backend/api/challenges.py`: Updated challenge creation to use the new `pending_verification` status and provide mock AI/source count values. Updated verification logic to check for the new status string.
- `backend/seed_mock_data.py`: Updated mock data generator to realistically populate `source_counts`, `ai_confidence`, and the new comprehensive SIH statuses (`pending_verification`, `verified`, `matches_suggested`, `ready_for_routing`, `routed`, `in_project`, `resolved`).

## Files Created
- `docs/government-dashboard/03-phase-01-foundation.md` (this file)

## Database Changes
- Re-seeded `issueRouter.db`. The `challenges` table now contains a JSON column for `source_counts` and float columns for AI context.
- Challenge statuses now follow the extended SIH lifecycle rather than the original simplified workflow.

## API Changes
- Endpoint `GET /api/challenges/` now returns the new fields: `source_counts`, `ai_confidence`, and `duplicate_risk`.
- Endpoint `PATCH /api/challenges/{id}/verify` transitions from `pending_verification` to `verified`.

## Decisions Made
- `source_counts` is implemented as a JSON blob (`{"social": 47, "citizen": 8, "ngo": 2}`) rather than a separate table for now to minimize complex relational joins while still satisfying the UI requirement of showing a breakdown.
- Retained the `complaint_count` field for backward compatibility with older sorting/filtering logic if present in other dashboards, but it is now semantically "total evidence count".

## Backward Compatibility Verified
- The Citizen and Org dashboards that hit `/api/challenges/` will simply receive extra fields they don't consume, which is safe.
- `seed_mock_data.py` successfully executes.

## Next Phase
**Phase 2 — Government Dashboard UX**: Redesign the UI to display these new fields, implement professional Command Center layout, and refine the `ChallengeCard`.
