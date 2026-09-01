# Contributing — Team Convergence Internal Guide

This is for the team, not external contributors. It exists so a 19-day sprint doesn't lose time to merge conflicts, unclear ownership, or "wait, who's working on this."

---

## 1. Branching

- `main` — always demo-able. Nothing broken gets merged here.
- `dev` — integration branch, where feature branches land first.
- `feature/<module>-<short-desc>` — e.g. `feature/matching-tag-overlap`, `feature/university-dashboard`.

Merge order: `feature/*` → `dev` (PR + at least one review) → `main` (only at phase checkpoints, per `ROADMAP.md`).

## 2. Commits

Keep them scoped and readable — future-you (or a judge skimming git history, which happens) should understand the log without opening every diff.

```
<module>: <what changed, imperative mood>

feat(matching): implement tag-overlap scoring for university routing
fix(intake): correct dedup threshold causing false-positive merges
docs(architecture): document tag-overlap decision rationale
```

## 3. Code Review

- Every PR into `dev` needs one reviewer from a different module than the author, where feasible — the point is a second pair of eyes, not gatekeeping.
- Review for correctness against `ARCHITECTURE.md`'s data model first, style second.
- If a PR changes the data model, flag it in the team channel before merging — other modules depend on shared entities.

## 4. Module Ownership

Assign one primary owner per module at Phase 0 (`ROADMAP.md`). Suggested split, adjust to actual team size/skills:

| Module | Covers |
|---|---|
| AI Intake | Classification, location extraction, dedup, priority scoring (porting from IssueRouter) |
| Matching & University | Tag-overlap matcher, university dashboard, team/proposal flow |
| Industry & Government | Industry dashboard, pledge flow, government analytics |
| Platform | Data model, auth/role-selector, notifications, seed data, deployment |
| Frontend | Shared UI components, four dashboards' visual layer |

One person can own more than one module in a small team — the table is about clarity of "who do I ask," not headcount.

## 5. Definition of Done (per feature)

A feature is done when:
- [ ] It works against the shared data model in `ARCHITECTURE.md §2` (not a local mock)
- [ ] It's reachable from the actual UI, not just testable via API client
- [ ] It's been walked through once against a real Jharkhand seed example, not a placeholder
- [ ] The relevant doc (`ARCHITECTURE.md`, `GLOSSARY.md`) is updated if it changes a decision or adds a term

## 6. Communication

- Daily check-in against `ROADMAP.md` phase checklist — even 5 minutes async is enough. The goal is catching drift early, not ceremony.
- Anything that changes scope (adds/cuts a feature) gets flagged against `MVP_PLAN.md §4.6`'s tier list before it happens, not after — the three-tier scope is a team commitment, not just pitch framing.

## 7. Before Demo Day

- No new feature branches after the Phase 6 cutoff in `ROADMAP.md` — polish and rehearsal only.
- Everyone should be able to explain any module's basic logic, not just their own — a judge can ask anyone.
