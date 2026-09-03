# Phase 3: Functional Search + Filters + Map — Government Dashboard (SIH 2026)

## Objective
Replace client-side UI filtering with robust backend filtering to support combinations (e.g., District = Dumka + Domain = Healthcare + Status = Verified). Centralize geographic configuration so the frontend is unified.

## Files Changed
- `backend/api/challenges.py`: Updated `GET /api/challenges/` to natively parse `district`, `priority`, `search`, and `domain` parameters and filter the database query via SQLAlchemy.
- `frontend/src/components/ui/FilterBar.jsx`: Updated to use deterministic Dropdowns mapped to our actual predefined SIH schema constants instead of dynamically deriving them from whatever happens to be on the client.
- `frontend/src/pages/GovDashboard.jsx`: 
  - `DEFAULT_FILTERS` changed to `{ search, domain, district, priority }`.
  - Added dependency array to `useEffect` to trigger a refetch whenever filters or tabs change.
  - Simplified the local `useMemo` filter since the backend now returns exactly what matches the active filters (it only needs to locally remove 'routed' items).

## Files Created
- `frontend/src/data/geography.js`: Created to centralize `JHARKHAND_DISTRICTS`, `DOMAINS`, and `PRIORITIES` across the app.

## API Changes
- `GET /api/challenges/` now handles:
  - `status` (exact match)
  - `domain` (exact match)
  - `district` (partial match on location string)
  - `priority` (translates 'critical', 'high', 'medium', 'low' into score ranges)
  - `search` (case-insensitive ILIKE match across title, description, and ID)

## Testing Performed
- Selecting filters modifies the API query string and returns filtered results correctly without throwing React rendering errors.
- The default priority sort is preserved because `GovDashboard` still applies `.sort((a,b) => b.priority_score - a.priority_score)` on the fetched results.

## Next Phase
**Phase 4 — Challenge Detail Experience**: Build a deep-dive drawer for challenges featuring the evidence gallery and detailed AI analysis.
