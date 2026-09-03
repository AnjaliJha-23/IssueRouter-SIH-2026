# Phase 4: Challenge Detail Experience — Government Dashboard (SIH 2026)

## Objective
Provide government officers with a detailed, professional workspace to review challenge evidence, AI rationale, and lifecycle history before taking action. Replace the basic expandable card with a premium Drawer UI.

## Files Created
- `frontend/src/components/ui/ChallengeDetailDrawer.jsx`: A full-height side drawer that displays:
  - **Hero Section**: Priority, Status, Description, Location, Domain, and submission timestamp.
  - **Evidence Gallery**: A grid showing mock photo evidence alongside a clear breakdown of social signals (extracted from the new `source_counts` JSON).
  - **AI Analysis Panel**: Displays the interpretable priority rationale (why a score is high) and the deduplication risk score.
  - **Lifecycle Timeline**: Visually tracks the challenge from detection to verification.
  - **Footer Actions**: Context-aware action buttons (Verify or Route) matching the SIH workflow state.

## Files Changed
- `frontend/src/components/ui/ChallengeCard.jsx`: Removed the inline expandable details section entirely, as clicking "View Action Details" now triggers the Drawer instead. This keeps the feed list dense and clean.
- `frontend/src/pages/GovDashboard.jsx`: 
  - Integrated `ChallengeDetailDrawer`.
  - Replaced the `expandedId` state with `selectedChallenge` (storing the full challenge object to pass to the drawer).

## UX Improvements
- Officers no longer lose their place in the list when viewing a long challenge description, as the drawer overlays the content.
- The AI context is presented not just as a raw number, but with interpretable supporting factors (e.g., "+25 Population Impact").

## Next Phase
**Phase 5 — University Matching & Routing**: We will build the Routing Modal that allows officers to see actual matched universities, select one, and officially persist the routing state, moving the challenge out of the active dashboard.
