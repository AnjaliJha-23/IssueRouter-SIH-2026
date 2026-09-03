# Roadmap - SIC Portal

This roadmap follows the canonical workflow in `IssueRouter_SIH_Final_Implementation_Blueprint.md` and `docs/MVP_PLAN.md`.

## Phase 0 - Repository Audit and Foundation

- [ ] Inspect the actual frontend, backend, database, ingestion, AI pipeline, routes, components, and state management.
- [ ] Lock the Master Challenge plus linked Evidence model.
- [ ] Confirm reusable IssueRouter modules and migration risks.
- [ ] Agree organization roles, permissions, and state transitions.
- [ ] Prepare Jharkhand districts, blocks, institutions, and controlled demo data.

**Exit:** every teammate can run the current FastAPI and React/Vite applications locally and the implementation plan uses real repository paths.

## Phase 1 - Unified Intake and AI Engine

- [ ] Extend Twitter/X ingestion and seeded replay support.
- [ ] Add direct citizen/community submission.
- [ ] Normalize every source into common Evidence/Signal records.
- [ ] Implement classification, location/topic extraction, semantic similarity, deduplication, clustering, priority, confidence, trend, and canonical summary.
- [ ] Link related evidence to one Master Challenge.

**Exit:** a social signal and direct report about the same issue converge on one Master Challenge without making separate clusters.

## Phase 2 - Government Challenge Intelligence

- [ ] Show unified challenge filters by source, domain, priority, verification, routing, and project state.
- [ ] Build Challenge Detail with evidence source breakdown, AI analysis, location, relations, and trend.
- [ ] Add human verification, rejection, closure, and override controls.
- [ ] Record sensitive actions and transitions in AuditLog.

**Exit:** an authorized government user can review evidence and verify a candidate challenge.

## Phase 3 - Explainable Smart Router

- [ ] Rank government departments, universities, faculty/research groups, industry/CSR partners, and pilot locations.
- [ ] Use configurable weighted deterministic scoring.
- [ ] Store factor breakdowns and human-readable match reasons.
- [ ] Add invitation and accept/reject/request-information responses.

**Exit:** a verified challenge returns ranked matches that a reviewer can explain and override.

## Phase 4 - University and Industry Collaboration

- [ ] Build one organization-scoped University Portal.
- [ ] Add university acceptance, multidisciplinary team formation, and proposal submission.
- [ ] Build one organization-scoped Industry Portal.
- [ ] Add collaboration responses and support types: Mentor, Technology, Funding/CSR, Equipment, Pilot Support, Deployment, and Co-development.

**Exit:** a university can create a proposal and an industry/CSR partner can attach support to the resulting collaboration.

## Phase 5 - Shared Project Lifecycle

- [ ] Create one shared Project Workspace from an approved proposal.
- [ ] Add team, milestones, deliverables, prototype, testing, pilot, communication, impact, and governance views.
- [ ] Implement project progression: Planned -> Active -> Prototype -> Testing -> Pilot -> Deployed -> Impact Validation -> Closed.
- [ ] Add citizen feedback and impact metrics.

**Exit:** government, university, and industry see permission-appropriate views of the same project and its progress.

## Phase 6 - Analytics, Demo Hardening, and Rehearsal

- [ ] Add challenge, routing, project, and impact KPIs.
- [ ] Verify organization and role permissions.
- [ ] Add seeded/replay fallback for unstable external services.
- [ ] Rehearse the HealthTech story from discovery to impact in 5-10 minutes.
- [ ] Test responsive UI and failure fallbacks.

**Exit:** the full flow runs without relying on a live Twitter/X API.

## Explicitly Outside the SIH MVP

- Multilingual intake.
- Real payment processing or advanced funding ledger.
- Blockchain.
- Sophisticated custom model training.
- Large-scale external integrations.
- Fully featured chat.

## Demo Story

Rural healthcare social signals are clustered, a citizen report joins the same Master Challenge, government verifies it, Smart Router recommends a university and HealthTech partner, the university forms a team and submits a proposal, industry accepts a support role, the shared project progresses through pilot and deployment, and citizen feedback appears in government impact analytics.
