# Final Implementation Plan — Government Dashboard (SIH 2026)

This document outlines the step-by-step repository-specific implementation plan for transforming the IssueRouter Government Dashboard into the SIH 2026 Jharkhand Societal Challenge Command Center.

## Phase 1: Foundation (Data & Workflow)
- **Feature**: Challenge Evidence Source & Expanded Statuses
- **Purpose**: Reflect multiple evidence sources (Twitter, Citizen, etc.) without duplicating challenges, and establish the proper SIH routing lifecycle.
- **Current implementation**: `complaint_count` (int) serves as a proxy for evidence volume. Statuses are `pending`, `verified`, `matched`, `in_project`, `resolved`.
- **Required change**: Add a `source_counts` JSON column to represent unified intake. Expand statuses to align with the new workflow (`PENDING_VERIFICATION`, `VERIFIED`, `READY_FOR_ROUTING`, `ROUTED`, etc.). Update the DB seeder to populate these.
- **Frontend files**: `src/context/IssueContext.jsx`
- **Backend files**: `db/models.py`, `db/schemas.py`, `api/challenges.py`, `seed_mock_data.py`
- **Database changes**: Add `source_counts` (JSON) to `challenges` table.
- **API changes**: Update `ChallengeOut` schema to return `source_counts`.
- **Dependencies**: None.
- **Risk**: Low. Existing API consumers missing `source_counts` will ignore it.
- **Testing method**: Check `/api/challenges` response structure.
- **Rollback strategy**: Remove column from model and schema.
- **Category**: **MODIFY**

## Phase 2: Government Dashboard UX
- **Feature**: Command Center Layout, KPIs, Dense Challenge Card, Priority Sorting
- **Purpose**: Redesign the interface to feel like premium GovTech rather than a basic CRUD app.
- **Current implementation**: Basic grid in `GovDashboard.jsx` with generic cards and client-side sorting.
- **Required change**: Build the KPI layer (Total Active, Pending Verification, High Priority, Ready for Routing). Redesign `ChallengeCard.jsx` to be information-dense (showing priority, evidence breakdown, AI confidence, and top matches directly). Ensure default sorting is strictly by priority score.
- **Frontend files**: `src/pages/GovDashboard.jsx`, `src/components/ui/ChallengeCard.jsx`
- **Backend files**: None.
- **Category**: **MODIFY**

## Phase 3: Functional Search, Filters, and Map Sync
- **Feature**: Backend-driven filtering and unified geography.
- **Purpose**: Support complex combinations (e.g. District=Dumka + Domain=Healthcare + Status=Verified) across both the challenge list and the map.
- **Current implementation**: Partial client-side filtering via `useMemo` in `GovDashboard.jsx`.
- **Required change**: Centralize Jharkhand district data in a new config file. Move search and filtering logic completely to the backend API so pagination and filtering work together predictably.
- **Frontend files**: `src/components/ui/FilterBar.jsx`, `src/pages/GovDashboard.jsx`, `src/pages/Maps.jsx`, `src/data/geography.js`
- **Backend files**: `api/challenges.py`
- **API changes**: Enhance `GET /api/challenges/` to properly accept and filter by `search`, `district`, `priority`, `domain`, `status`.
- **Category**: **CREATE / MODIFY**

## Phase 4: Challenge Detail Experience
- **Feature**: Dedicated Intelligence Drawer
- **Purpose**: Allow officers to deep-dive into a challenge's evidence, AI rationale, and university matches before routing.
- **Current implementation**: Expanding the `ChallengeCard` component reveals basic info.
- **Required change**: Create `ChallengeDetailDrawer.jsx`. Include an Evidence Gallery (mock images), Social Signals breakdown, AI Analysis Panel (interpretable priority explanation), and University Recommendations.
- **Frontend files**: `src/pages/GovDashboard.jsx`, `src/components/ui/ChallengeDetailDrawer.jsx`
- **Backend files**: None.
- **Category**: **CREATE**

## Phase 5: University Matching & Routing
- **Feature**: Routing Modal and State Persistence
- **Purpose**: Enable the government officer to officially route a challenge to a selected university.
- **Current implementation**: Mock deterministic matches exist, but routing is a hidden side effect of a match being "accepted".
- **Required change**: Add a premium Routing Modal. On submit, record the routing action (who, when, which university), transition the challenge status to `ROUTED`, and remove it from the active dashboard feed.
- **Frontend files**: `src/components/ui/RoutingModal.jsx`, `src/pages/GovDashboard.jsx`
- **Backend files**: `api/challenges.py`, `api/smart_router.py`
- **API changes**: Create `POST /api/challenges/{id}/route` taking `org_id` and optional notes.
- **Category**: **CREATE / EXTEND**

## Phase 6: Progress Integration
- **Feature**: Handoff to Progress tracking
- **Purpose**: Ensure that once routed, challenges are trackable but no longer clutter the active dashboard.
- **Current implementation**: `Progress.jsx` handles generic tracking.
- **Required change**: Filter out `ROUTED` (and subsequent states) from `GovDashboard.jsx`. Ensure `Progress.jsx` accurately reads `ROUTED` challenges, rendering their timeline and university assignment.
- **Frontend files**: `src/pages/Progress.jsx`, `src/pages/GovDashboard.jsx`
- **Backend files**: None.
- **Category**: **MODIFY**

## Phase 7: Polish & QA
- **Feature**: Final UX review and error handling
- **Purpose**: Ensure professional states (Loading, Empty, Error) and responsive behavior.
- **Required change**: Add skeleton loaders tailored to the new cards. Design empty states for "No matches found" or "No active challenges". Verify map synchronization and backward compatibility with Citizen/Org flows.
- **Category**: **EXTEND**
