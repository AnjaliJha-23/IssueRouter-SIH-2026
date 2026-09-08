# Phase 3 Documentation — Challenge Detail Drawer Redesign
**Date:** September 2026  
**Objective:** Redesign the Challenge Detail Drawer into an authoritative, multi-tabbed GovTech intelligence dossier with smooth slide transitions, structured metadata overview, interactive civic evidence gallery with lightbox preview, AI scoring composition breakdown, dynamic university recommendations, lifecycle audit trail, and a sticky action footer.

---

## 1. Scope of Changes

- **Files Modified**:
  - [`frontend/src/components/ui/ChallengeDetailDrawer.jsx`](file:///F:/issueRouter/SIH/IssueRouter/frontend/src/components/ui/ChallengeDetailDrawer.jsx): Transformed into a high-density intelligence dossier.
- **Files Created**:
  - `docs/government-dashboard-ui/05-phase-03-detail-drawer.md`
- **Files Removed**: None.

---

## 2. Dossier Architecture & Features

1. **Header & Shell Motion**:
   - Drawer entrance powered by hardware-accelerated `.animate-slide-in-right` with `cubic-bezier(0.16, 1, 0.3, 1)`.
   - Backdrop uses neutral dark blur (`bg-neutral-950/60 backdrop-blur-xs`).
   - Sticky header presents Challenge ID in monospace badge, priority pill with score, status badge, and close button.

2. **Dossier Tabs**:
   - **Dossier Overview**: Full title, official description, 4-panel metadata grid (Location, Responsible Department, AI Confidence %, Administrative Verification status), top university match card with quick link, and a vertical lifecycle audit trail.
   - **Evidence**: Metric breakdown between Social Distress Signals and Verified Citizen Reports, alongside ground inspection photo cards with category chips, zoom icons, and interactive preview modal.
   - **AI Rationale**: Detailed score composition bars (Population Impact & Density, Severity Factor, Distress Signal Frequency, Ward Vulnerability, Verified Citizen Corroboration), plus duplicate probability percentage with semantic deduplication engine assessment.
   - **University Matches**: Ranked list of partner institutions with institutional district, match score pill (`94%`), and detailed AI matching rationale (domain overlap, publication output, geographic proximity).

3. **Sticky Action Footer**:
   - Left side shows live challenge stage status.
   - Right side houses "Close Dossier" button and primary stage-dependent action:
     - `pending_verification`: "Verify Challenge" (Green, with `CheckCircle2`)
     - `verified` / `matches_suggested` / `ready_for_routing`: "Select Universities & Route" (Blue, with `ArrowRight`)

---

## 3. Verification & Regression Tests

- **Build Test**: Built successfully with Vite in 1.55s. 0 errors, 0 warnings.
- **Data Flow**: Drawer calls `POST /api/matches/generate/{id}` automatically upon opening to fetch ranked universities, seamlessly integrating with the backend matching engine.
- **State Integrity**: Clicking "Verify Challenge" or "Select Universities & Route" properly invokes `onRoute(challenge)` and advances workflow without visual glitches.

---

## 4. Next Phase

Proceeding to **Phase 4 — Loading / Skeleton / Error System**:
- Implement realistic dashboard skeleton states (KPI tiles, Filter bar, Card grid matching the new card shape).
- Enhance RoutingModal with university card selection micro-interactions and realistic loading skeletons.
- Add error recovery states and contextual empty states.
