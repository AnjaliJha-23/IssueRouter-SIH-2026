# Changelog

## [UI Clean-up] - 2026-09-12

### UI Elements Removed
1. **AI Confidence Badge on Challenge Cards**: Removed the `AI Conf. XX%` badge and Sparkles icon container from challenge cards (`ChallengeCard.jsx`) across the Government Dashboard.
2. **AI Confidence Field in Dossier Overview**: Removed the `AI Confidence — XX% Verified` indicator from the Dossier Overview metadata grid (`ChallengeDetailDrawer.jsx`).
3. **AI Rationale Tab & View in Dossier**: Removed the entire `AI Rationale` navigation tab and its underlying panel (`ChallengeDetailDrawer.jsx`), including:
   - AI Triage & Scoring Model indicator and confidence percentage
   - BART-large-MNLI model description and text
   - Score Composition Breakdown and scoring progress bars
   - Semantic Deduplication Engine section, duplicate probability score, and unique challenge tag

### Active Tabs in Challenge Dossier
After removal, the challenge detail drawer presents exactly three navigation tabs:
- **Dossier Overview**
- **Evidence**
- **University Matches**

### Files Modified
- `frontend/src/components/ui/ChallengeCard.jsx`
- `frontend/src/components/ui/ChallengeDetailDrawer.jsx`

### Files Added
- `CHANGELOG.md`

### Intentionally Left Unchanged
- **Sidebar & Topbar Navigation**: Preserved all branding, navigation links, and layout structures.
- **Government Dashboard Layout & Features**: Preserved summary KPI cards, Innovation Pipeline banner, FilterBar, status filter pills, search, and pagination.
- **Challenge Cards**: Preserved challenge ID, rank, title, description, domain tag, location tag, status badge, evidence signal indicators (social and citizen report counts, photo counts), compact university matchmaking previews, and action buttons.
- **Dossier Overview & Other Tabs**: Preserved Dossier Header, Evidence tab (with real/mock image galleries, citizen reports, and social signals), University Matches tab, and Lifecycle Innovation Pipeline trail.
- **Backend, Database & Business Logic**:
  - No changes to API routes or endpoints (`backend/api/*`)
  - No changes to database schemas, seeders, or models
  - No changes to NLP pipeline or AI scoring business logic on the backend
  - No changes to authentication or client fetch utilities

