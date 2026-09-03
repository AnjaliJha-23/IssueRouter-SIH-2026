# MVP Plan - SIC Portal

This plan follows `IssueRouter_SIH_Final_Implementation_Blueprint.md` and the canonical workflow:

```text
Citizen
  Twitter/X / Direct Form
        |
        v
IssueRouter AI Engine
  Classification | Deduplication | Priority | Clustering
        |
        v
Master Challenge
        |
        v
Government Verification
        |
        v
Smart Router
  University | Industry | Government
        |
        v
Collaboration -> Project Created
        |
        v
University Team + Industry Partner
        |
        v
Development -> Milestones -> Prototype -> Testing -> Pilot -> Deployment
        |
        v
Citizen Feedback -> Impact Analytics -> Government
```

## Product Definition

SIC Portal is one societal challenge platform, not separate complaint systems. Twitter/X signals and direct citizen/community submissions enter one normalized evidence pipeline. The pipeline classifies, extracts location/topic information, detects duplicates and related items, assigns priority and confidence, and groups evidence into one Master Societal Challenge. A social post or form submission is evidence; it is not automatically an official government challenge.

## Core Workflow

1. A citizen submits a direct form or a public Twitter/X signal is ingested or replayed from seeded data.
2. The IssueRouter AI Engine performs classification, deduplication, priority scoring, and clustering.
3. Related evidence creates or updates a Master Challenge.
4. Government or an authorized verifier reviews the evidence and verifies the challenge.
5. Smart Router ranks government departments, universities, faculty/research groups, industry/CSR partners, and pilot locations.
6. A university accepts, forms a multidisciplinary team, and submits a solution proposal.
7. An industry/CSR partner accepts a collaboration role such as technology, mentorship, funding/CSR, equipment, pilot support, deployment, or co-development.
8. Government/project authority approves the collaboration and creates one shared Project Workspace.
9. The project moves through development, milestones, prototype, testing, pilot, and deployment.
10. Citizens provide feedback and the government reviews impact analytics and outcome history.

## MVP Priorities

### MUST HAVE

- Twitter/X ingestion or seeded replay plus direct citizen submission.
- One shared normalization, classification, deduplication, and clustering pipeline.
- Master Challenge with linked evidence, source breakdown, location, domain, priority, confidence, trend, and lifecycle status.
- Government verification and approval controls.
- Explainable Smart Router with configurable weighted scoring and match reasons.
- Organization-scoped University and Industry Portals.
- University proposal and multidisciplinary team flow.
- Industry/CSR collaboration response and support type.
- One shared Project Workspace with team, milestones, deliverables, prototype, testing, pilot, impact, and governance sections.
- Government challenge, project, and impact analytics.
- A reliable HealthTech demonstration using controlled or seeded data when external services are unavailable.

### SHOULD HAVE

Semantic embeddings, heatmaps, notifications, faculty/student views, pilot tracking, richer proposal workflow, and industry matching improvements.

### NICE TO HAVE

Mobile-native app, advanced funding ledger, blockchain, sophisticated custom ML training, large-scale external integrations, and fully featured chat.

## AI and Smart Router Policy

Use pretrained models/embeddings and deterministic scoring rather than custom model training. AI assists classification, priority, deduplication, summarization, and routing attributes; humans review and can override AI results. Every routing result stores its score breakdown and a human-readable explanation. Example university weighting: 40% domain/expertise match, 20% location relevance, 20% capacity, and 20% relevant past performance.

## State Model

| Entity | States |
| --- | --- |
| Evidence/Signal | Received -> Normalized -> Linked/Clustered -> Archived |
| Challenge | Candidate -> Under Review -> Verified -> Rejected -> Closed |
| Routing | Not Routed -> Recommendations Ready -> Invited -> Accepted / Rejected |
| Proposal | Draft -> Submitted -> Under Review -> Approved / Rework / Rejected |
| Project | Planned -> Active -> Prototype -> Testing -> Pilot -> Deployed -> Impact Validation -> Closed |
| Milestone | Pending -> In Progress -> Submitted -> Approved / Rework -> Completed |

Every transition is permission controlled and recorded in an audit log.

## Explicit Boundary

Do not make unstable external services a demo dependency. Seeded replay data is required. Multilingual intake, real payment processing, advanced funding ledgers, blockchain, custom model training, large external integrations, and fully featured chat remain outside the SIH MVP.

## Definition of Done

- Social and direct-form evidence can converge on the same Master Challenge.
- Challenge Detail shows evidence breakdown, AI analysis, verification state, and Smart Router explanations.
- Government can verify and route a challenge.
- University can accept, form a team, and submit a proposal.
- Industry can accept a collaboration opportunity.
- A shared Project Workspace can progress from development through impact.
- Citizen feedback and government impact analytics are visible.
- Organization and role permissions prevent unauthorized access.
- The complete demo runs in 5-10 minutes without relying on a live Twitter/X API.
