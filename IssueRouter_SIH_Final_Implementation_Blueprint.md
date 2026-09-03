# IssueRouter -> Societal Innovation Collaboration Portal

## Final Product Architecture, Workflow & Antigravity Implementation Brief

### SIH 2026 | Unified Social Signals + Citizen Intake + Smart Routing + Collaborative Innovation

## 1. Executive Direction

The current IssueRouter concept should be evolved, not discarded. Its existing strength is the ability to discover and cluster public complaints/signals (historically from Twitter/X) and surface them geographically and analytically. The final SIH product should preserve that foundation and add a second intake channel for direct citizen/community submissions. Both sources must feed one unified challenge-intelligence pipeline and one master source of truth.

The product is not two complaint systems. It is one societal challenge platform with multiple intake sources, followed by government verification, AI analysis, explainable Smart Routing, university/industry collaboration, project execution, pilot/deployment, and impact measurement.

| Principle | Decision |
| --- | --- |
| Intake | Twitter/X public signals + direct forms + future NGO/Panchayat/Govt sources |
| Clustering | One unified semantic clustering/deduplication layer across all sources |
| Source of truth | One Master Societal Challenge per underlying problem; multiple evidence items can belong to it |
| Dashboards | Role-based portals, not separate codebases per organization |
| University model | One University Portal; each institution sees its own matched challenges/projects based on organization identity |
| Industry model | One Industry Portal; each company sees relevant opportunities and its own collaborations |
| Collaboration | One shared Project Workspace with role-based permissions |
| AI | Assistive, explainable, human-reviewable; not a black box |
| SIH focus | Smart Router + multi-source discovery + HealthTech use cases + measurable impact |
| MVP strategy | Prioritize a complete end-to-end demo over deep implementation of every requested feature |

## 2. Final End-to-End Product Flow

The complete lifecycle should be treated as a stateful pipeline. A social post is initially a signal, not automatically an official government challenge. A direct form submission is also an input item. The platform normalizes both, detects related items, creates/updates a master challenge, performs AI analysis, and then moves the challenge into verification and routing.

1. Public signal (Twitter/X) OR direct citizen/community submission
2. -> Ingestion and normalization
3. -> AI classification + location/topic extraction
4. -> Semantic similarity / duplicate detection / clustering
5. -> Master Societal Challenge created or updated
6. -> Priority + evidence confidence + trend analysis
7. -> Government/authorized verifier review
8. -> Verified challenge
9. -> Smart Router ranks government department, universities, faculty/teams, and industry/CSR partners
10. -> University accepts/rejects/requests information
11. -> University forms project team and submits proposal
12. -> Industry/CSR partner is invited or discovers the opportunity
13. -> Government/project authority approves collaboration/project
14. -> Shared Project Workspace
15. -> Milestones -> prototype -> testing -> pilot -> deployment
16. -> Citizen/community feedback
17. -> Impact metrics + analytics + outcome history

## 3. Unified Challenge Intake Model

### 3.1 Sources

- Twitter/X: discovery of public social signals where people are already discussing problems.
- Direct citizen form: structured submission for people who do not use Twitter/X or prefer an official channel.
- NGO/community organization: future/optional structured intake.
- Panchayat/ULB/government department: future/optional official challenge intake.

### 3.2 Do not maintain separate cluster systems

All sources must enter the same normalization, classification, similarity and clustering service. The UI may provide filters such as All, Social Signals, Citizen Reports, Government, HealthTech, and High Priority, but these are views of the same challenge dataset rather than separate databases or independent clusters.

### 3.3 Evidence vs challenge

Use two conceptual levels: Evidence/Signal and Master Challenge. A tweet, form report, photo, or NGO report is evidence. The Master Challenge represents the underlying societal problem. Multiple evidence items can update one Master Challenge. This prevents the same problem from becoming multiple projects merely because it was reported through different channels.

## 4. Master Societal Challenge

The Master Challenge is the central domain object. It should be the bridge between the original IssueRouter clustering concept and the SIH collaboration workflow.

| Field / concept | Purpose |
| --- | --- |
| Challenge ID | Stable identifier, e.g. HC-102 |
| Title / canonical problem statement | Human-readable consolidated problem |
| Description | AI-assisted summary plus editable official description |
| Domain / subdomain / tags | Healthcare, education, water, etc. |
| Location | District, block, village/ward, latitude/longitude |
| Evidence count | Number of linked social/direct/official reports |
| Source breakdown | Twitter/X vs citizen vs NGO vs government |
| Priority score | 0-100, with explanation |
| Evidence confidence | Confidence based on report volume, consistency, location, media, verification, etc. |
| Trend | Stable / increasing / decreasing where supported by timestamps |
| Verification status | Candidate / Under Review / Verified / Rejected |
| Routing status | Not Routed / Recommended / Invited / Accepted / Assigned |
| Project status | No Project / Proposal / Active / Pilot / Deployed / Closed |
| Impact summary | People impacted, outcome metrics, feedback, geography |

## 5. Portal & Dashboard Architecture

Do not build a unique dashboard codebase for every organization. Build a shared application with role- and organization-scoped data. The same University Portal can render RIMS Ranchi, University B, etc. based on the logged-in organization and role. The same principle applies to Industry.

| Actor | Portal | Primary capabilities |
| --- | --- | --- |
| Public/Citizen | Citizen Portal | Submit challenge, upload evidence, location, view own reports, track outcomes, feedback |
| Government | Government Dashboard | Challenge intelligence, verification, priority review, routing, approvals, heatmaps, analytics |
| University Admin | University Portal | Matched challenges, accept/reject, faculty/students, teams, proposals, projects |
| Faculty | University Portal | Assigned challenges, mentoring, project oversight, milestones, deliverables |
| Student | University Portal | Assigned projects/tasks, submissions, progress, collaboration |
| Industry Admin | Industry Portal | Recommended opportunities, accept/decline, collaborations, funding/mentoring/pilot participation |
| Industry Member/Mentor | Industry Portal | Assigned collaborations, technical input, mentorship, deliverables |
| Shared Project | Innovation Workspace | Government + university + industry collaboration with permission-based views |

## 6. Challenge Intelligence UI

The main challenge dashboard should be a unified intelligence view. Use filters instead of separate dashboards for source types.

Recommended filters: All Challenges | Social Signals | Citizen Reports | Government Reports | Healthcare | High Priority | Pending Verification | Routed | Active Projects.

### 6.1 Challenge list card

- Challenge title and canonical summary
- Domain/subdomain
- District/location
- Priority score
- Verification status
- Evidence count with source breakdown
- Last activity / trend
- Routing status
- Project status

### 6.2 Challenge detail page

- Overview and canonical problem statement
- Social evidence: clustered posts/signals and trend
- Direct evidence: citizen reports, photos, videos, documents
- AI classification and priority explanation
- Duplicate/related challenge suggestions
- Location/map and geographic context
- Government verification controls
- Smart Router recommendations with explainable scores
- University proposals and industry opportunities once routed

## 7. Smart Router - Core Differentiator

The Smart Router should be the centrepiece of the SIH solution. Its purpose is not simply to assign a department. It finds the best ecosystem participants and explains why they are a match.

| Routing target | Inputs |
| --- | --- |
| Government department | Domain, jurisdiction, severity, location, department mandate |
| University | Domain expertise, subdomain, faculty expertise, labs, research areas, location, capacity, past projects |
| Faculty / research group | Specialization, availability/capacity, research areas, relevant labs |
| Industry / startup | Technology capability, domain, CSR focus, funding, implementation capacity, location |
| Pilot location | Geographic need, infrastructure readiness, population, challenge severity |

Recommended MVP scoring approach: weighted deterministic ranking rather than an opaque ML model. Example university score = 40% domain/expertise match + 20% location relevance + 20% capacity + 20% relevant past performance. Store the score breakdown and a human-readable explanation. The weights should be configurable.

## 8. AI Layer

| AI capability | MVP behaviour | Human control |
| --- | --- | --- |
| Classification | Domain, subdomain, tags from challenge text/evidence | |
| Priority | 0-100 score with factors/explanation | |
| Deduplication | Semantic similarity; flag probable duplicate/related challenges | |
| Cluster summarization | Generate/update canonical challenge summary from evidence | |
| Routing assistance | Use AI-derived attributes as inputs; final match comes from transparent scoring | |
| Explainability | Show top factors; allow reviewer override | |

For SIH, prefer pre-trained models/embeddings and deterministic scoring over time-consuming custom model training. AI should accelerate workflow, not become the highest-risk part of the project.

## 9. University Flow

1. Government verifies a challenge.
2. Smart Router generates ranked universities and match reasons.
3. Authorized coordinator invites/routes the challenge to selected universities.
4. University admin sees it in Recommended/Incoming Challenges.
5. University opens the Challenge Detail page and reviews evidence, AI analysis, and match rationale.
6. University chooses Accept / Reject / Request More Information.
7. If accepted, university creates a solution proposal and forms a multidisciplinary team.
8. Faculty mentor is assigned; students are added.
9. Proposal is sent for project approval.
10. Once approved, a Project Workspace is created.

University does not need a separate dashboard implementation. Organization-scoped data and RBAC determine what the institution and its users can see or edit.

## 10. Industry / Startup / CSR Flow

1. The system identifies project needs/capabilities that cannot be met by the university alone.
2. Smart Router ranks relevant industry/startup/CSR partners.
3. Industry Portal shows Recommended Collaboration Opportunities rather than every challenge.
4. Industry reviews the challenge, university team, required support, expected impact, and proposed timeline.
5. Industry can Accept / Decline / Ask Questions / Offer Support.
6. Support type can be Mentor, Technology, Funding/CSR, Equipment, Pilot Support, Deployment, or Co-development.
7. Accepted collaboration attaches the organization to the shared project workspace.
8. Industry participants then see their scoped tasks, milestones, documents, funding/commitments, and pilot status.

## 11. Shared Innovation Project Workspace

Do not create isolated copies of a project for government, university, and industry. Create one project object with role-based permissions and different views.

| Section | Purpose |
| --- | --- |
| Overview | Problem, solution, participants, status, timeline, expected impact |
| Team | Faculty, students, industry mentors, government coordinator |
| Milestones | Plan, due dates, owners, status, approvals |
| Deliverables | Documents, prototypes, test reports, media |
| Prototype | Version/status tracking and evidence |
| Testing | Test cases, results, approval |
| Pilot | Location, dates, population, deployment status |
| Communication | Project comments/messages/notifications |
| Impact | Outcome metrics and citizen/community feedback |
| Governance | Approvals, audit trail, decisions |

## 12. Recommended State Model

| Entity | Recommended states |
| --- | --- |
| Evidence/Signal | Received -> Normalized -> Linked/Clustered -> Archived |
| Challenge | Candidate -> Under Review -> Verified -> Rejected -> Closed |
| Routing | Not Routed -> Recommendations Ready -> Invited -> Accepted / Rejected |
| Proposal | Draft -> Submitted -> Under Review -> Approved / Rework / Rejected |
| Project | Planned -> Active -> Prototype -> Testing -> Pilot -> Deployed -> Impact Validation -> Closed |
| Milestone | Pending -> In Progress -> Submitted -> Approved / Rework -> Completed |

Every state transition should be permission controlled and recorded in an audit log.

## 13. Recommended Data Model

Antigravity must first inspect the current SQLAlchemy models and preserve/reuse them where practical. The target conceptual model is below; it is not a mandate to create every table if the existing architecture can model the relationship more simply.

| Entity | Key relationships / role |
| --- | --- |
| User | Belongs to organization; has role; owns/submits records |
| Organization | Type: Government, University, Industry, CSR, Research/NGO |
| UniversityProfile | Institution expertise, departments, capabilities, capacity |
| FacultyProfile | Specializations, research areas, availability |
| IndustryProfile | Technology, domain, CSR focus, funding/implementation capability |
| Challenge | Master societal problem |
| ChallengeEvidence | Tweet/form/media/official report linked to Challenge |
| ChallengeAnalysis | Domain, tags, priority, confidence, trend, model/version |
| ChallengeRelation | Duplicate/related/merged relationships |
| Match | Challenge/Project to organization/person, score, explanation, status |
| Proposal | University solution proposal |
| Project | Approved execution unit derived from Challenge + Proposal |
| ProjectMember | Users participating with project role |
| Milestone | Tracked project delivery stage |
| Deliverable | Files/links/evidence associated with milestone |
| Collaboration | Industry/CSR involvement and support type |
| Funding | Optional MVP record of pledged/approved support |
| Pilot | Deployment location and period |
| ImpactMetric | Measured social/operational outcome |
| CitizenFeedback | Post-pilot community validation |
| Notification | Workflow communication |
| AuditLog | Immutable record of sensitive actions |

## 14. API Surface - Target MVP

| Area | Endpoints / purpose |
| --- | --- |
| Auth | POST /api/auth/register, POST /api/auth/login, current-user/profile |
| Challenges | POST /api/challenges, GET /api/challenges, GET /api/challenges/{id}, update/verify/close |
| Evidence | POST /api/challenges/{id}/evidence, list evidence, moderation controls |
| AI | POST /api/challenges/{id}/analyze, GET analysis |
| Dedup/relations | GET candidates, link/merge/mark-separate |
| Routing | POST /api/challenges/{id}/route, GET /api/challenges/{id}/matches |
| Matches | accept/reject/request-info |
| Universities | profiles, expertise, capacity, matched challenges |
| Industry | profiles, opportunities, collaboration responses |
| Projects | create from approved proposal, project CRUD |
| Milestones | create/update/approve |
| Analytics | challenge, routing, project, impact summaries |
| Notifications | list/read/create workflow notifications |

## 15. Security, Governance & Trust

- JWT authentication and role-based access control.
- Organization-level tenancy/scoping: a university sees only its organization data unless a public/authorized shared object permits access.
- Government verification and approval permissions separated from citizen submission permissions.
- Human approval before an AI-derived candidate challenge becomes officially verified.
- AI explanation and override for classification, priority, deduplication decisions, and routing recommendations.
- Audit trail for verification, routing, approvals, project status, funding/support commitments, and closure.
- Validation/moderation for user-generated evidence and uploads.
- Privacy controls for location, personal information, and sensitive healthcare-related evidence.

## 16. HealthTech Demonstration Strategy

Because the stated theme is MedTech / BioTech / HealthTech, the final demo should make Healthcare the hero example while preserving a multi-domain architecture.

| Demo use case | What it demonstrates |
| --- | --- |
| Rural telemedicine access | End-to-end discovery -> verification -> university + HealthTech partner -> project -> pilot -> impact |
| PHC staffing/access problem | Multi-source evidence, clustering, priority, geographic aggregation, Smart Routing |
| Waterborne disease signal | Multiple social reports + direct reports -> outbreak-like cluster -> health department + research routing |

## 17. MVP Priorities for SIH

| Priority | Features |
| --- | --- |
| MUST HAVE | Unified intake; Twitter/X ingestion or seeded social dataset; direct citizen submission; one master cluster/challenge; AI classification; priority; duplicate/related flag; government verification; Smart Router; University Portal; shared Project Workspace; core project milestones; strong HealthTech demo |
| SHOULD HAVE | Semantic embeddings; heatmaps; industry matching; proposal workflow; notifications; impact dashboard; faculty/student views; pilot tracking |
| NICE TO HAVE | Mobile-native app; advanced funding ledger; blockchain; sophisticated custom ML training; large-scale external integrations; fully featured chat |

## 18. Recommended Build Order

1. Repository audit + architecture lock - Inspect actual repo, map reusable modules, identify migration risk, confirm current APIs/models/UI.
2. Authentication + organization/RBAC foundation - Users, roles, organization tenancy, protected routes.
3. Unified intake + Master Challenge - Twitter/X adapter + direct form -> common ingestion -> evidence -> challenge clustering.
4. AI intelligence - Classification, priority, semantic similarity, challenge summary, confidence.
5. Government Challenge Intelligence dashboard - Verification, evidence view, filters, maps, challenge lifecycle.
6. Smart Router - University + industry profiles, ranking, explanations, accept/reject flow.
7. University + Industry portals - Organization-scoped dashboards, challenge acceptance, proposal, collaboration.
8. Shared Project Workspace - Project, team, milestones, deliverables, testing/pilot/impact skeleton.
9. Analytics + polish + demo hardening - Impact KPIs, seeded data, failure fallbacks, responsive UI, final demo script.

## 19. Exact Instructions to Antigravity

Use this section as the implementation-analysis contract. Do not start by blindly coding. First inspect the repository and produce a final plan grounded in the actual codebase.

- Inspect the entire repository: frontend, backend, database, AI pipeline, maps, state management, routes, components, and current data ingestion.
- Identify which existing Twitter/X ingestion and clustering code can be retained and how it should feed the new unified evidence/challenge model.
- Do not create separate Twitter and citizen clustering systems. Design one common ingestion -> normalization -> semantic grouping pipeline with source metadata.
- Preserve the existing IssueRouter dashboard/layout components wherever they are useful, but redesign them into the new role-based experience.
- Use actual repository paths in the final file-level plan. Do not invent filenames or modules before inspecting the repository.
- Propose database migrations that reuse Cluster/Tweet concepts where sensible, but introduce the minimum additional entities needed for SIH.
- For each planned change, label it KEEP, EXTEND, MODIFY, REBUILD, or NEW.
- Design organization-scoped University and Industry portals. Do not generate one separately coded dashboard per institution/company.
- Design one shared Project Workspace with role-based permissions rather than duplicate project dashboards.
- Keep the Smart Router explainable and configurable. Show match score breakdowns and reasons.
- Keep AI implementation MVP-realistic; prefer pretrained models/embeddings and deterministic scoring over custom training.
- Use a HealthTech demo journey that runs from discovery all the way to project/impact, even if later lifecycle stages use controlled demo data.
- Provide a strict MVP boundary and explicitly identify anything that should not be built before the SIH demo.
- After repository analysis, produce the final implementation plan first. Only then begin implementation in small validated increments.

## 20. Definition of Done for the SIH MVP

- A Twitter/X social signal can be ingested OR replayed from a seeded dataset into the platform.
- A citizen can submit a direct challenge with evidence and location.
- Both inputs can converge on the same Master Challenge when semantically related.
- The Challenge Detail page clearly shows evidence source breakdown and AI analysis.
- A government user can verify and route a challenge.
- The Smart Router returns ranked university and industry matches with reasons.
- A university user can accept a challenge and create a proposal/team.
- An industry user can accept a collaboration opportunity.
- A shared Project Workspace can be created and shows team, milestones, deliverables, pilot and impact sections.
- The Government dashboard can show challenge/project/impact KPIs.
- Roles prevent users from seeing or modifying unauthorized data.
- The 5-10 minute demo can be executed without reliance on unstable external services.

## 21. Target SIH Demo Story

The demo should prove the entire thesis in one coherent story rather than showing disconnected pages.

1. Show several public social posts about a rural healthcare problem.
2. Show IssueRouter clustering them into one emerging challenge.
3. Submit a direct citizen report about the same problem.
4. Show semantic match: the report is linked to the existing Master Challenge rather than creating a new duplicate.
5. Show AI classification, priority score, confidence, and evidence breakdown.
6. Government verifies the challenge.
7. Smart Router recommends a university and HealthTech partner with score explanations.
8. University accepts, forms a multidisciplinary team, and submits a solution proposal.
9. Industry accepts a collaboration role such as technology + pilot support.
10. Create the shared project workspace and update milestones.
11. Move the project through prototype/testing/pilot using demo data.
12. Show citizen feedback and impact metrics on the government dashboard.

## 22. Risks to Watch

| Risk | Mitigation |
| --- | --- |
| Twitter/X API instability | Provide an adapter + seeded replay/demo dataset. Never make the live API a single point of failure. |
| Scope explosion | Freeze MUST HAVE items before UI polishing. Do not build deep features that do not improve the demo. |
| AI unpredictability | Use explainable thresholds, model versions, confidence, and human override. |
| Too many roles | Start with Citizen, Government, University Admin, Faculty, Student, Industry Admin, and optional Project Member. |
| Dashboard duplication | Build shared portal layouts with organization/role scoping. |
| Data-model sprawl | Introduce only entities needed for the demonstrable lifecycle. |
| Weak SIH narrative | Always show the transition from citizen problem -> innovation project -> impact. |

## 23. Final Architectural Principle

IssueRouter should remain recognizable as the original product, but its meaning changes. The old system answered: “What problems are people talking about?” The final SIH system answers: “What societal problems are emerging, how credible and urgent are they, who is best equipped to solve them, and did the resulting solution create measurable impact?”

That is the product definition Antigravity should use when analysing the codebase and preparing the final implementation plan.