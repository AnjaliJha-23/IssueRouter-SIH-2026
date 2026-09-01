# Roadmap — SIC Portal

**Submission deadline: 20 September 2026 (sih.gov.in)**
**Today: 1 September 2026 — roughly 19 days out.**

This roadmap turns `MVP_PLAN.md §4.6`'s three-tier scoping into a day-by-day plan. Dates below are a proposal — adjust to your team's actual availability, but keep the phase order: the engine before the body, the body before the polish.

Legend: 🟢 Fully built & demoed live · 🟡 Simplified but functional · ⚪ Roadmapped, not built (mention in pitch only)

---

## Phase 0 — Foundation (Sep 1–3)

Goal: everyone can run the project locally and the schema is agreed before anyone builds against it.

- [ ] Repo scaffolded (backend + frontend skeleton, see `README.md §6`)
- [ ] Data model finalized and reviewed against `ARCHITECTURE.md §2` (Challenge, University, Faculty, IndustryPartner, Team, Proposal, Project, Notification)
- [ ] Seed data drafted: Jharkhand districts/blocks gazetteer, real universities with discipline tags, plausible industry/CSR partners
- [ ] Dev environment doc confirmed working for every team member (`README.md §7`)
- [ ] Task ownership assigned per module (see `CONTRIBUTING.md §4`)

**Exit criteria**: `git clone` → running FastAPI + Next.js dev servers takes under 10 minutes for a teammate who wasn't the one who wrote the setup.

## Phase 1 — Reused Engine, Ported and Retargeted (Sep 4–8) 🟢

Goal: get IssueRouter's proven pipeline running against this project's domains, not civic complaint categories.

- [ ] Port BART zero-shot classification, retag from 7 civic categories to the 10 thematic domains in the problem statement
- [ ] Port spaCy EntityRuler, rebuild gazetteer for Jharkhand districts/blocks (not Delhi-centric)
- [ ] Port sentence-transformers dedup (all-MiniLM-L6-v2 + cosine similarity)
- [ ] Port priority scoring formula, reweight from urgency+social-reach to volume+severity
- [ ] End-to-end test: submit a raw Challenge description → get back domain, dedup flag, priority score

**Exit criteria**: a challenge like "no clean drinking water in [Jharkhand block]" gets correctly classified as `water resources`, doesn't false-positive dedup against unrelated challenges, and gets a sane priority score.

## Phase 2 — University Matching & Collaboration Layer (Sep 9–12) 🟢

Goal: the genuinely new part that didn't exist in IssueRouter.

- [ ] Tag-overlap matcher: Challenge domain → best-fit University by discipline tag overlap
- [ ] University dashboard: view assigned challenges, form a Team, submit a Proposal
- [ ] Faculty/Team data model wired to Proposal submission
- [ ] Explainability check: for any routed challenge, can you point to the exact matching tag? (This is the pitch's answer to "why this university?" — don't skip verifying it.)

**Exit criteria**: a challenge routes to a plausible university given its seed discipline tags, and a Proposal can be created against it through the UI, not just the DB.

## Phase 3 — Industry Partnership Layer (Sep 13–15) 🟢

Goal: close the loop the problem statement is actually about — university work reaching funding and deployment.

- [ ] Industry dashboard: browse open Proposals across all universities
- [ ] Pledge mechanism (funding/mentorship/deployment — no real payment processing, see ⚪ below)
- [ ] Project status field wired: `submitted → team formed → prototype → testing → deployed`

**Exit criteria**: an industry user can find an open Proposal and pledge support, and that pledge is visible from both the university and government views.

## Phase 4 — Government Analytics + Notifications (Sep 16–17) 🟢 / 🟡

- [ ] Government dashboard: volume, domain/district distribution, university/industry engagement counts, pipeline progress
- [ ] In-app notification system: citizen (challenge picked up), university (new routed challenge), industry (new open proposal) 🟢
- [ ] 🟡 Role selector as access control (citizen/university/industry/government) — confirm this is clearly framed as MVP simplification in the pitch, not hidden
- [ ] 🟡 Basic file upload/display for challenge photos — confirm no production storage pipeline is implied anywhere in the demo

**Exit criteria**: government dashboard numbers update correctly when you run through the full flow once end to end.

## Phase 5 — Jharkhand Grounding Pass (Sep 18) 🟢

Goal: make sure nothing in the demo accidentally still looks like IssueRouter's Delhi/Mumbai data.

- [ ] Audit every seed record: real districts/blocks, real universities (BIT Mesra, IIT ISM Dhanbad, NIT Jamshedpur, Central University of Jharkhand, Vinoba Bhave University, others), plausible industry/CSR partners (Tata Steel Foundation, JSPL CSR as reference points)
- [ ] Walk through the full demo flow with Jharkhand-specific example challenges (not generic placeholders)

**Exit criteria**: nothing in the live demo would make a judge ask "wait, is this actually for Jharkhand?"

## Phase 6 — Polish, Pitch, Rehearsal (Sep 19–20)

- [ ] Full end-to-end dry run, timed
- [ ] Pitch deck finalized, explicitly stating the three-tier scope (🟢/🟡/⚪) as a strength, per `MVP_PLAN.md §4.6`
- [ ] Prepared answer for "why tag-overlap and not embedding similarity for university matching" (`ARCHITECTURE.md §4`)
- [ ] Prepared answer for "what would production auth/multilingual/payments look like" (they're ⚪, not secrets you're hiding — have a one-liner ready for each)
- [ ] Submission uploaded well before the 20 Sep deadline, not at the wire

---

## ⚪ Explicitly Not Building (say so proactively, don't get caught by a question)

- Production authentication and security
- Multilingual intake (Hindi and regional languages)
- Real funding/payment flows
- IP and legal tracking
- SMS/email notification delivery
- Video content analysis

If a judge asks about any of these, the answer is "roadmapped — here's what it would take" (`MVP_PLAN.md §4.6`), not a scramble.

---

## Demo-Day Checklist

- [ ] One rehearsed happy-path walkthrough: citizen submits → AI classifies/dedupes/scores → routes to university → team forms, proposal submitted → industry pledges → status progresses → government dashboard reflects it all → notifications fired at each step
- [ ] Backup plan if live demo breaks: recorded screen capture of the same flow
- [ ] Seed data reset script so the demo can be re-run cleanly if needed
- [ ] Every team member can explain the tag-overlap matching decision without notes
