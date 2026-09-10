# Plan: Citizen Dashboard Hero Banner Removal & Layout Polish

**Target**: `frontend/src/pages/CitizenDashboard.jsx`  
**Purpose**: Eliminate visual noise by safely removing the oversized dark hero banner ("Jharkhand Civic Innovation Portal", "Make your community better..."), elevating the "Report a Community Challenge" form as the primary visual focus, and fine-tuning spacing and responsive balance across desktop, tablet, and mobile.

---

## 1. Scope & Impact Analysis

- **Element to Remove**:
  - The static dark gradient banner block (`lines 292–309` in `frontend/src/pages/CitizenDashboard.jsx`).
  - Unused imports (`Sparkles`, `ShieldCheck`).
- **Dependencies**:
  - None. No other components or state logic reference this banner.
- **Preserved Functionality**:
  - All 4 steps of the challenge submission form (Title, Description, District, Block, GPS coordinates, Photos drag-and-drop/upload, Preview Lightbox, Validation).
  - Post-submission modal and navigation deep-links to `/progress`.
  - Right-side informational panel: *"What happens after submitting?"* (4-phase explanation).
  - *"Recent Community Activity"* feed with live query from `/api/challenges/?priority=high`.
- **Layout & Spacing Polish**:
  - Introduce a lightweight, contextual dashboard header (matching `CitizenProgress.jsx` design language) that provides immediate orientation and an action link to view submitted challenges.
  - Adjust top and vertical spacing (`space-y-6`, `gap-6`) to position the form naturally at the top of the viewport without feeling cramped or empty.
  - Ensure mobile and tablet displays (`sm:`, `lg:`) maintain balanced margins and padding.
