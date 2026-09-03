# Architecture - SIC Portal

This document is the technical companion to `IssueRouter_SIH_Final_Implementation_Blueprint.md`. The blueprint defines the product contract; this document maps that contract to the repository's implementation boundaries.

## 1. Architectural Principle

IssueRouter evolves into one societal challenge platform. Twitter/X signals, direct citizen submissions, and future NGO, Panchayat, ULB, or government inputs enter the same normalization, AI analysis, semantic grouping, and evidence pipeline. A **Master Societal Challenge** is the source of truth; each tweet, form, photo, video, document, or official report is linked evidence.

The application uses shared role- and organization-scoped portals. It does not create a separate dashboard or database for every university or company, and it does not create isolated copies of a project for each stakeholder.

## 2. Layered View

```text
CITIZEN
                     │
         Twitter/X / Direct Form
                     │
                     ▼
            ┌────────────────┐
            │ ISSUE ROUTER   │
            │ AI ENGINE      │
            └───────┬────────┘
                    │
            ┌─────────┴──────┐
            │ Classification │
            │ Deduplication  │
            │ Priority       │
            │ Clustering     │
            └─────────┬──────┘
                    │
                    ▼
          MASTER CHALLENGE
                    │
                    ▼
            GOV VERIFICATION
                    │
                    ▼
             SMART ROUTER
              /    |    \
             /     |     \
            ▼      ▼      ▼
      University Industry  Govt
            │       │
            │       │
            └───┬───┘
                │
                ▼
          COLLABORATION
                │
                ▼
          PROJECT CREATED
                │
          ┌─────┴──────┐
          ▼            ▼
      University     Industry
        Team         Partner
          │            │
          └─────┬──────┘
                ▼
           DEVELOPMENT
                │
          Milestones
                │
                ▼
            PROTOTYPE
                │
                ▼
             TESTING
                │
                ▼
              PILOT
                │
                ▼
            DEPLOYMENT
                │
                ▼
         CITIZEN FEEDBACK
                │
                ▼
          IMPACT ANALYTICS
                │
                ▼
            GOVERNMENT
```

## 3. Repository Ownership Map

| Boundary | Repository surface | Blueprint responsibility |
| --- | --- | --- |
| API entrypoint | `backend/main.py` | FastAPI application and middleware |
| API modules | `backend/api/` | Auth, challenges, Smart Router, projects, actions, stats |
| Persistence | `backend/db/` | SQLAlchemy models, schemas, and database session |
| Intake | `backend/ingestion/` | Twitter/X adapter, replay data, and normalized evidence intake |
| AI pipeline | `backend/pipeline/` | Classification, NER, clustering, summarization, urgency/priority |
| Frontend shell | `frontend/src/App.jsx`, `frontend/src/components/layout/` | Shared role-based application layout and navigation |
| Frontend views | `frontend/src/pages/` | Government, citizen, organization, project, analytics, maps, progress |
| Frontend data/API | `frontend/src/api/`, `frontend/src/data/`, `frontend/src/context/` | API access, seeded demo data, and shared state |

## 4. Conceptual Data Model

The model should preserve current SQLAlchemy concepts where practical and add only the entities needed for the demonstrable lifecycle.

| Entity | Key relationships / role |
| --- | --- |
| User | Belongs to an organization; has a role; owns or submits records |
| Organization | Government, University, Industry, CSR, or Research/NGO |
| UniversityProfile | Institution expertise, departments, capabilities, and capacity |
| FacultyProfile | Specializations, research areas, and availability |
| IndustryProfile | Technology, domain, CSR focus, funding, and implementation capability |
| Challenge | Master societal problem and lifecycle state |
| ChallengeEvidence | Tweet, form, media, or official report linked to a challenge |
| ChallengeAnalysis | Domain, tags, priority, confidence, trend, and model/version |
| ChallengeRelation | Duplicate, related, or merged relationships |
| Match | Challenge/project to organization/person, with score, explanation, and status |
| Proposal | University solution proposal |
| Project | Approved execution unit derived from a challenge and proposal |
| ProjectMember | Users participating with a project role |
| Milestone | Tracked project delivery stage |
| Deliverable | Files, links, or evidence associated with a milestone |
| Collaboration | Industry/CSR involvement and support type |
| Funding | Optional MVP record of pledged or approved support |
| Pilot | Deployment location and period |
| ImpactMetric | Measured social or operational outcome |
| CitizenFeedback | Post-pilot community validation |
| Notification | Workflow communication |
| AuditLog | Immutable record of sensitive actions |

## 5. Challenge and Project States

| Entity | Recommended states |
| --- | --- |
| Evidence/Signal | Received -> Normalized -> Linked/Clustered -> Archived |
| Challenge | Candidate -> Under Review -> Verified -> Rejected -> Closed |
| Routing | Not Routed -> Recommendations Ready -> Invited -> Accepted / Rejected |
| Proposal | Draft -> Submitted -> Under Review -> Approved / Rework / Rejected |
| Project | Planned -> Active -> Prototype -> Testing -> Pilot -> Deployed -> Impact Validation -> Closed |
| Milestone | Pending -> In Progress -> Submitted -> Approved / Rework -> Completed |

Every transition is permission controlled and recorded in `AuditLog`.

## 6. AI and Smart Router

The AI layer is assistive and human-reviewable:

- Classification produces domain, subdomain, and tags.
- Priority produces a 0-100 score with factors and an explanation.
- Semantic similarity flags probable duplicates and related challenges.
- Summarization maintains the canonical challenge summary.
- AI-derived attributes assist routing, but final matches use transparent deterministic scoring.
- Reviewers can override AI-derived classifications, priorities, deduplication decisions, and recommendations.

The Smart Router ranks government departments, universities, faculty/research groups, industry/startups/CSR partners, and pilot locations. Its weights are configurable. The example university score is 40% domain/expertise match, 20% location relevance, 20% capacity, and 20% relevant past performance. Every result stores its score breakdown and a human-readable reason.

## 7. Reuse Plan

| Area | Change label | Direction |
| --- | --- | --- |
| Existing ingestion and replay | EXTEND | Support social signals and direct citizen evidence through one normalized path |
| Classification | EXTEND | Retarget categories to societal domains |
| Location extraction | EXTEND | Use the Jharkhand district/block gazetteer |
| Clustering and deduplication | EXTEND | Link all source types to one Master Challenge |
| Priority and trend | MODIFY | Include severity, evidence confidence, volume, and timestamps |
| Existing frontend/layout | MODIFY | Preserve useful IssueRouter surfaces and make them role-scoped |
| Challenge/evidence model | REBUILD | Separate evidence items from the Master Societal Challenge |
| Smart Router | REBUILD | Add multi-target, weighted, explainable matching |
| University/industry collaboration | NEW | Profiles, matches, proposals, teams, and support |
| Shared project workspace | NEW | Role-based project, milestone, deliverable, pilot, and impact views |
| Governance | NEW | Verification, approvals, privacy/moderation, and audit trail |

## 8. Target MVP API Surface

| Area | Endpoints / purpose |
| --- | --- |
| Auth | `POST /api/auth/register`, `POST /api/auth/login`, current-user/profile |
| Challenges | Create, list, detail, update, verify, and close |
| Evidence | Add/list challenge evidence and moderation controls |
| AI | Analyze a challenge and retrieve analysis |
| Dedup/relations | Candidate relations, link, merge, or mark separate |
| Routing | Generate recommendations and list challenge matches |
| Matches | Accept, reject, or request information |
| Universities | Profiles, expertise, capacity, and matched challenges |
| Industry | Profiles, opportunities, and collaboration responses |
| Projects | Create from approved proposal and manage project |
| Milestones | Create, update, and approve |
| Analytics | Challenge, routing, project, and impact summaries |
| Notifications | List, read, and create workflow notifications |

## 9. Trust and Deployment Constraints

- Use JWT authentication and RBAC in the target architecture; government verification must remain separate from citizen submission permissions.
- Scope data by organization unless a public or authorized shared object permits access.
- Protect personal information, precise locations, and sensitive healthcare evidence.
- Moderate user-generated evidence and uploads.
- The demo must remain functional with seeded or replayed data if Twitter/X is unavailable.
- Prefer a stable reproducible local/staging environment over production infrastructure that does not improve the SIH demonstration.
