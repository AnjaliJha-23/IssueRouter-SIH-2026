# SIC Portal — Societal Innovation Collaboration Portal

**Smart India Hackathon 2026 · SIH26043 · Government of Jharkhand**
**Team Convergence**

> A platform that turns a citizen's local problem into a university-led, industry-backed project the government can track end to end.

---

## 1. The Problem, in One Paragraph

Jharkhand's citizens are the first to spot local problems in education, healthcare, agriculture, water, sanitation, environment, rural livelihoods, accessibility, and urban infrastructure — but there's no structured way for them to report a problem and have it reach the university or research group best equipped to solve it. Universities have the expertise. Industry and CSR bodies have the funding and deployment muscle. Nothing connects the three. SIC Portal is that connective layer.

Full problem statement: `docs/PROBLEM_STATEMENT.pdf` (SIH26043, Theme: MedTech/BioTech/HealthTech, Deadline: 20 September 2026).

## 2. Our Approach in One Paragraph

We are not starting from zero. Our team previously built **IssueRouter** (3rd place, HNC 3.0) — an AI pipeline that classified, deduplicated, and prioritized citizen complaints scraped from X and routed them to government departments. It solved the "structure the input" third of this problem. SIC Portal keeps IssueRouter's classification, deduplication, and prioritization engine, and builds the two-thirds that never existed: university matching and team formation, and industry/CSR partnership. Think of it as **reused engine, new body** — not a rewrite, not a light patch.

Full reasoning and scope: [`docs/MVP_PLAN.md`](docs/MVP_PLAN.md) (source of truth for this build — read it before `docs/ARCHITECTURE.md` or `docs/ROADMAP.md`).

## 3. The Four Stakeholders

| Stakeholder | What they do on the platform |
|---|---|
| **Citizen** | Submits a challenge (description, district, optional photo). No need to know the right category or department. |
| **University** | Sees challenges routed to them, forms a project team, submits a solution proposal. |
| **Industry / CSR** | Browses open proposals across all universities, pledges funding/mentorship/deployment support. |
| **Government** | Views a real-time dashboard of the whole pipeline — volume, domain/district spread, engagement, project progress. |

See [`docs/GLOSSARY.md`](docs/GLOSSARY.md) for precise definitions of every entity and term used across the codebase and this doc set.

## 4. System at a Glance

```
Citizen submits ──▶ AI Intake Layer ──▶ University Matching ──▶ University forms team,
  (web form)         (classify,           (discipline tag         submits proposal
                       dedup, score)        overlap)                   │
                                                                        ▼
                                                          Industry pledges support
                                                                        │
                                                                        ▼
                                              Project status: submitted → team formed →
                                                  prototype → testing → deployed
                                                                        │
                                                                        ▼
                                          Government dashboard aggregates everything
                                          Notifications fire to relevant stakeholders throughout
```

Full data model and component breakdown: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## 5. Tech Stack

Reused directly from IssueRouter (proven, don't re-risk it):

- **Classification**: `facebook/bart-large-mnli` zero-shot classification, retagged to 10 thematic domains
- **Location extraction**: spaCy + custom EntityRuler, gazetteer rebuilt for Jharkhand districts/blocks
- **Deduplication**: `sentence-transformers` (`all-MiniLM-L6-v2`) + cosine similarity
- **Prioritization**: IssueRouter's weighted scoring formula, reweighted for challenge volume + severity
- **Backend pattern**: FastAPI + SQLAlchemy

New for this build:

- **Frontend**: Next.js (four role-scoped dashboards: citizen, university, industry, government)
- **University matching**: discipline tag overlap (not embedding similarity — see [`docs/ARCHITECTURE.md §4`](docs/ARCHITECTURE.md) for why)
- **Data model**: `Challenge`, `University`, `Faculty`, `IndustryPartner`, `Team`, `Proposal`, `Project`, `Notification`
- **Notifications**: lightweight in-app only (no SMS/email — roadmapped, not built)

## 6. Repo Structure (proposed)

```
sic-portal/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models (Challenge, University, Team, Proposal, Project, ...)
│   │   ├── routers/         # FastAPI routers, one per stakeholder-facing API surface
│   │   ├── pipeline/        # classification, dedup, priority scoring (ported from IssueRouter)
│   │   ├── matching/        # university tag-overlap matcher
│   │   └── core/            # config, db session, notification dispatch
│   ├── seed/                # Jharkhand universities, districts/blocks gazetteer, industry partners
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/citizen/
│       ├── app/university/
│       ├── app/industry/
│       └── app/government/
├── docs/
│   ├── PROBLEM_STATEMENT.pdf
│   ├── GLOSSARY.md
│   ├── ROADMAP.md
│   ├── ARCHITECTURE.md
│   ├── CONTRIBUTING.md
│   └── MVP_PLAN.md
├── AGENTS.md
└── README.md
```

Adjust to match whatever the team actually scaffolds — this is a proposal, not a contract.

## 7. Getting Started

> Fill in exact versions/commands once the repo is scaffolded. Placeholder shape below.

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Environment variables needed (create `backend/.env`):

```
DATABASE_URL=
HF_MODEL_CACHE_DIR=        # for bart-large-mnli, all-MiniLM-L6-v2
```

## 8. What's Actually Built vs. What's Scoped Out

This is a genuine MVP, not a demo of everything the problem statement mentions. See [`docs/MVP_PLAN.md §4.6`](docs/MVP_PLAN.md) and [`docs/ROADMAP.md`](docs/ROADMAP.md) for the full three-tier breakdown (fully built / simplified for demo / roadmapped-not-built). The short version: no production auth, no multilingual support, no real payments, no production file storage — all deliberate, all defensible under questioning.

## 9. Document Map

| Doc | What's in it | Read it when |
|---|---|---|
| [`docs/MVP_PLAN.md`](docs/MVP_PLAN.md) | Source-of-truth plan, reasoning, scoping decisions | Before touching anything else |
| [`docs/GLOSSARY.md`](docs/GLOSSARY.md) | Every entity, term, and acronym used in this project | You're unsure what a term means in code review or standup |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Data model, component design, matching algorithm detail | You're building or reviewing a new module |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Day-by-day build plan, milestones, demo-day checklist | You're planning your week or checking if we're on schedule |
| [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) | Branching, commits, code review, task ownership | You're about to open a PR |

## 10. Team Convergence

- **Hackathon**: Smart India Hackathon 2026
- **Problem statement**: SIH26043, Government of Jharkhand
- **Prize**: ₹1,00,000
- **Submission deadline**: 20 September 2026, via sih.gov.in
