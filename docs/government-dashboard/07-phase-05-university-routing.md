# Phase 5: University Routing — Government Dashboard (SIH 2026)

## Objective
Implement the matching and routing interface that completes the primary lifecycle of a challenge from the Government's perspective, transitioning it out of the active dashboard to the matching partners.

## Files Created
- `frontend/src/components/ui/RoutingModal.jsx`: A modal that is invoked when a user wants to route a verified challenge.
  - Automatically fetches intelligent matches from `GET /api/matches/generate/{id}`.
  - Renders match cards displaying organization names, match rationale, and percentage score.
  - Allows selection of a partner and attaching a contextual routing note.
  - Dispatches the `POST /api/challenges/{id}/route` request upon confirmation.

## Files Changed
- `backend/api/challenges.py`: Added the `POST /{challenge_id}/route` endpoint. It expects an `org_id` and optional `note`, and officially transitions the status to `routed`.
- `frontend/src/pages/GovDashboard.jsx`: 
  - Integrated `RoutingModal`.
  - Replaced the hardcoded `handleVerifyRoute` with a dynamic `handleAction(challenge)` function that understands the current workflow state (Verify vs Route) and invokes the correct API or UI flow.
  - Addressed state management for opening/closing the routing modal, and automatically closing the underlying drawer when routing succeeds.

## UI / UX Improvements
- Officers no longer just click a black box "Route" button. They see exact, AI-justified reasons why a university is recommended.
- The UI proactively auto-selects the highest-rated partner, reducing click-fatigue for straightforward cases, while still allowing manual override.
- Once routed, the challenge disappears from the main active dashboard automatically (handled by Phase 3 updates), establishing a clear "inbox zero" psychological reward loop for the officer.

## Next Phase
**Phase 6 — Progress Integration**: Create or update the Progress/Tracking view so that routed challenges can still be observed.
