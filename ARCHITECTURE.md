# Architecture — SIC Portal

This doc covers the data model, the reused-vs-new component split, and the reasoning behind the one design decision worth defending under questioning: how challenges get matched to universities. Read `MVP_PLAN.md` first — this doc goes one level deeper into implementation, it doesn't re-argue the scoping.

---

## 1. Layered View

```
┌─────────────────────────────────────────────────────────────┐
│  Citizen Layer          — submission web form                │
├─────────────────────────────────────────────────────────────┤
│  AI Intake Layer        — classify · dedup · prioritize      │  ← reused from IssueRouter
├─────────────────────────────────────────────────────────────┤
│  University Matching &  — tag-overlap match · team formation │  ← new
│  Collaboration Layer      · proposal submission               │
├─────────────────────────────────────────────────────────────┤
│  Industry Partnership   — browse proposals · pledge support  │  ← new
│  Layer                                                        │
├─────────────────────────────────────────────────────────────┤
│  Government Analytics   — aggregate dashboard, read-only     │  ← new
│  Layer                                                        │
├─────────────────────────────────────────────────────────────┤
│  Notification Layer     — in-app alerts across all roles     │  ← new
└─────────────────────────────────────────────────────────────┘
```

Each layer maps roughly to a router module in `backend/app/routers/` and a route group in `frontend/src/app/`.

## 2. Data Model

Core entities and their relationships. See `GLOSSARY.md` for what each one means conceptually.

```
Challenge
├── id, description, district, block, photo_url (optional)
├── domain            (assigned by AI Intake Layer, one of 10 thematic domains)
├── priority_score     (assigned by AI Intake Layer)
├── duplicate_of        (nullable FK → Challenge, set by dedup step)
├── status             (submitted → routed → team_formed → in_progress → resolved)
└── routed_university_id (FK → University, nullable until matched)

University
├── id, name, location
└── discipline_tags[]   (e.g. ["agriculture", "rural_livelihoods"])

Faculty
├── id, name, university_id (FK → University)

Team
├── id, challenge_id (FK → Challenge), lead_faculty_id (FK → Faculty)
└── members[]            (Faculty and/or student records — keep loose in MVP)

Proposal
├── id, team_id (FK → Team), challenge_id (FK → Challenge)
├── summary, submitted_at
└── status               (open → pledged → accepted)

IndustryPartner
├── id, name, type        (startup / MSME / research_lab / CSR)

Pledge
├── id, proposal_id (FK → Proposal), industry_partner_id (FK → IndustryPartner)
└── support_type          (funding / mentorship / deployment)

Project
├── id, proposal_id (FK → Proposal, 1:1 once accepted)
└── status                (submitted → team_formed → prototype → testing → deployed)

Notification
├── id, recipient_role, recipient_id, message, read_at (nullable)
```

This replaces IssueRouter's old schema (`RawTweet`, `Complaint`, `Cluster`, `Action`), which was built for a single officer consuming a single stream. This schema is built for four independent stakeholder types sharing one pipeline — each gets a filtered view into the same underlying data, not a separate database.

## 3. Reused vs. New — Component Map

| Component | Status | Source |
|---|---|---|
| Zero-shot classification (BART) | Reused, retagged | IssueRouter — 7 categories → 10 domains |
| Location extraction (spaCy EntityRuler) | Reused, regazetteered | IssueRouter — Delhi locality list → Jharkhand districts/blocks |
| Deduplication (sentence-transformers + cosine sim) | Reused as-is | IssueRouter |
| Priority scoring | Reused, reweighted | IssueRouter — urgency+social-reach → volume+severity |
| Backend pattern (FastAPI + SQLAlchemy) | Reused | IssueRouter |
| University matching | **New** | Discipline tag overlap (see §4) |
| Team formation / Proposal flow | **New** | — |
| Industry partnership / Pledge flow | **New** | — |
| Project lifecycle status | **New**, simplified | Single status field, not full milestone tracking |
| Government analytics dashboard | **New** | Aggregation queries over shared schema |
| Notification system | **New**, simplified | In-app only, no SMS/email |
| Role-based access | **New**, simplified | Role selector, not production auth |

The point of this table: don't spend engineering time re-risking the row that's already reused. Spend it on the "New" rows — that's where the problem statement actually lives and where judges will probe.

## 4. Why Tag Overlap, Not Embedding Similarity, for University Matching

This is the one architectural decision worth being able to defend in one breath:

**Embedding similarity** (e.g. embed challenge description + embed university research abstracts, compare vectors) is more sophisticated, but produces a similarity score nobody in the room — including the team — can intuitively verify. If a judge asks "why was this challenge routed to BIT Mesra and not NIT Jamshedpur," the honest answer with embeddings is "the vectors were closer," which isn't an answer.

**Tag overlap** (challenge's classified domain vs. each university's discipline tags, best-overlap wins) is:
- **Fast to build** — no embedding infrastructure needed for this step, just a set-intersection query
- **Explainable** — the answer to "why this university" is always "it's tagged for `[domain]`, here's the tag," which a judge can verify by eye
- **Consistent with the rest of the intake pipeline** — the domain classification step already produces a clean categorical label; tag overlap uses it directly instead of throwing it away and re-embedding

The tradeoff, stated honestly: tag overlap can't capture nuance a good embedding match might (a university strong in "water resources" research that also happens to be relevant to a "sanitation" challenge, for instance). That's a fair critique to expect and a fair one to concede — the mitigation is that discipline tags can be multi-valued and reasonably granular in the seed data, which covers most of the gap without the explainability cost.

## 5. API Surface (proposed — fill in as routers are built)

| Route group | Stakeholder | Core endpoints |
|---|---|---|
| `/challenges` | Citizen, AI Intake | `POST /challenges` (submit), `GET /challenges/{id}` |
| `/university` | University | `GET /university/{id}/challenges`, `POST /teams`, `POST /proposals` |
| `/industry` | Industry | `GET /proposals?status=open`, `POST /pledges` |
| `/government` | Government | `GET /analytics/summary`, `GET /analytics/by-domain`, `GET /analytics/by-district` |
| `/notifications` | All | `GET /notifications?recipient=`, `POST /notifications/{id}/read` |

Keep this table updated as the actual FastAPI routers land — it should never drift more than a day behind the code.

## 6. Deployment Shape for the Demo

No production infra needed. A single deployed instance (backend + Postgres + frontend) is enough — this is a hackathon MVP being demoed live, not a service under real load. Prioritize a stable, reproducible local/staging environment over any cloud polish that doesn't change what a judge sees.
