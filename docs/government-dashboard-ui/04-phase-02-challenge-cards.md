# Phase 2 Documentation — Challenge Cards Redesign
**Date:** September 2026  
**Objective:** Eliminate colored priority side stripes, implement a compact GovTech intelligence card architecture adhering to the 5-second comprehension rule, surface real status-driven "Next Actions", incorporate university match summaries, and add subtle desktop hover elevation.

---

## 1. Scope of Changes

- **Files Modified**:
  - [`frontend/src/components/ui/ChallengeCard.jsx`](file:///F:/issueRouter/SIH/IssueRouter/frontend/src/components/ui/ChallengeCard.jsx): Completely redesigned into a compact, neutral-bordered intelligence card.
- **Files Created**:
  - `docs/government-dashboard-ui/04-phase-02-challenge-cards.md`
- **Files Removed**: None.

---

## 2. Key Design & Structural Transformations

1. **Elimination of Priority Stripe**:
   - Removed `border-l-4 border-l-red-500` / `border-l-orange-400` / `border-l-blue-400` entirely.
   - Replaced with semantic priority badges at top right: `CRITICAL · 100`, `HIGH · 86`, `MEDIUM · 60`, `LOW · 35`.
   - Card border remains visually neutral (`border-neutral-200/90 dark:border-neutral-800/90`), transitioning smoothly to `border-blue-500/50` on hover.

2. **5-Second Decision Architecture**:
   - **What is it?** Prominent 2-line clamped title with domain & district chips.
   - **How serious?** Top-right semantic priority badge with numerical score.
   - **Where is it?** Location chip (`MapPin`) and department chip (`Building2`).
   - **What evidence exists?** Social signals count (`Share2`), citizen complaints count (`Users`), and AI Confidence percentage (`Sparkles`).
   - **What stage?** State pill (`Pending Verification`, `Verified`, `Matches Suggested`, `Ready for Routing`, `Routed`, `Active Project`).
   - **What to do next?** Explicit bottom "Next Action" callout + CTA:
     - `pending_verification`: "Review Evidence → Verify" (`ShieldCheck` green button)
     - `verified` / `matches_suggested`: "Select Universities → Route" (`ArrowRight` blue button)
     - `routed`: "Track Progress" / "View Project Workspace"

3. **University Match & Routing Visibility on Card**:
   - If AI matches exist: Displays a compact row showing top university match name (e.g. `RIMS Ranchi`), match percentage (`94%`), and count of additional matches (`+2 more`).
   - If routed: Displays active deadline with countdown preview.

4. **Desktop Hover Micro-Interactions**:
   - Subtle vertical lift (`-translate-y-0.5`).
   - Gentle shadow bloom (`shadow-lg shadow-blue-500/5`).
   - Refined 200ms cubic-bezier transition without aggressive scaling.

---

## 3. Verification & Regression Tests

- **Build Test**: Vite build completed successfully in 3.15s with 0 errors.
- **Action Flow**: Clicking anywhere on the card triggers `onToggle` (opening the intelligence drawer), while clicking "Proceed" directly triggers the stage-appropriate action (`onVerify` or routing).
- **Dark Mode Support**: Validated across light and dark modes with proper contrast ratios and no harsh border artifacts.

---

## 4. Next Phase

Proceeding to **Phase 3 — Challenge Detail Drawer Redesign**:
- Transform the drawer into a comprehensive GovTech intelligence dossier.
- Add evidence media gallery with thumbnail zoom and full preview modal.
- Visualize AI intelligence breakdown (population impact, severity, frequency, vulnerability bars).
- Display ranked university recommendations with match explanations.
- Add smooth slide/backdrop entrance transitions and sticky action footer.
