# AGENTS.md — GitHub Workflow for AI Coding Agents

This file is the operating manual for any AI agent (Claude Code, Cursor, Copilot Workspace, or similar) acting on behalf of a team member in this repo. If you are an AI agent and a human just asked you to "push my changes" or "open a PR," read this file in full before running any git command. Every team member's agent reads the same file, so behavior is consistent no matter who triggers it.

Project: SIC Portal · SIH26043 · Team Convergence
Team size: 6 members across 4 module branches

---

## 1. Non-Negotiable Rules

An agent operating in this repo must never do the following, regardless of what the human asks in the moment:

- Never push directly to `main`. Every change reaches `main` through a pull request.
- Never push directly to another member's module branch unless the human explicitly says they're working in that module today.
- Never merge a pull request. Merging is a human decision, made by someone other than the PR author.
- Never approve your own operator's pull request, and never attempt to work around required-review settings.
- Never force-push (`git push --force`) to any shared branch (`main`, `frontend`, `backend`, `ingestion`, `nlp-pipeline`). Force-push is only ever acceptable on a branch only one person uses, and only after confirming with the human.
- Never rewrite another person's commits (no `git commit --amend` on commits you didn't just make, no interactive rebase across others' work).
- Never skip the pre-push checklist in Section 4 to save time.

If a human instruction conflicts with any of these, follow this file and tell the human why.

## 2. Branch Structure

```
main
├── frontend       (long-lived, all frontend work lands here first)
├── backend         (long-lived, all backend/API work lands here first)
├── ingestion       (long-lived, citizen submission intake, file handling, gazetteer)
└── nlp-pipeline    (long-lived, classification, dedup, priority scoring, matching)
```

Every member is assigned to exactly one of these four branches for their current task. Fill in the actual mapping below and keep it current — the agent uses this table to decide where to push.

| Branch | Members assigned | Covers |
|---|---|---|
| `frontend` | _fill in_ | React/Vite portals (citizen, university, industry, government), shared UI components |
| `backend` | _fill in_ | FastAPI API modules, data model, RBAC, notifications, deployment |
| `ingestion` | _fill in_ | Citizen submission form/API, photo/file handling, Jharkhand district and block gazetteer |
| `nlp-pipeline` | _fill in_ | BART zero-shot classification, sentence-transformers dedup, priority scoring, discipline-tag matching |

Two or more people can share a module branch. When they do, they push sequentially (pull before you push, every time — see Section 4) rather than in parallel to avoid stepping on each other.

`main` only ever receives merges via reviewed PRs from the four module branches. Nobody commits to `main` directly, including agents acting for the team lead.

## 3. How the Agent Determines Which Branch to Use

When a human says "push my changes" or "open a PR," the agent must resolve the target branch in this order:

1. If the human names the branch explicitly ("push to backend"), use that.
2. If the human doesn't name it, infer from the files changed in `git status` / `git diff --name-only`:
   - Changes under `frontend/` → `frontend`
  - Changes under `backend/api/`, `backend/db/`, or `backend/main.py` → `backend`
  - Changes under `backend/ingestion/` or gazetteer/seed data for districts → `ingestion`
  - Changes under `backend/pipeline/` → `nlp-pipeline`
3. If the changed files span more than one module, or the mapping is ambiguous, stop and ask the human which branch this belongs on. Do not guess and push — a misfiled PR wastes a reviewer's time.
4. If the human is not currently on the branch resolved in steps 1 to 3, check out that branch (creating it from `main` with `git fetch origin && git checkout -b <branch> origin/<branch>` if it doesn't exist locally) before making or staging any changes.

## 4. Standard Push-and-PR Workflow

Run every step below, in order, every time. Do not skip steps because "it's a small change."

### Step 1 — Confirm the target branch and sync

```bash
git status
git branch --show-current
git fetch origin
git pull origin <target-branch>
```

If `git pull` reports conflicts, stop and resolve them with the human before proceeding. Do not auto-resolve conflicts in files you don't understand — surface them and ask.

### Step 2 — Review what's about to be committed

```bash
git diff
git status
```

Confirm with the human (or from context) that everything staged is actually meant to be pushed. Never include `.env`, credentials, model weight files, or anything matching `.gitignore` — if `git status` shows an untracked file that looks like a secret or a large binary, flag it and ask before adding it.

### Step 3 — Stage and commit

```bash
git add <specific files, not blanket `git add .` unless the human confirms everything changed is intentional>
git commit -m "<type>(<module>): <what changed, imperative mood>"
```

Commit message format (matches `docs/CONTRIBUTING.md`):

```
feat(nlp-pipeline): retag BART classifier to 10 thematic domains
fix(ingestion): correct district gazetteer entry for Ranchi block
docs(backend): document notification dispatch flow
refactor(frontend): extract university dashboard card component
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`. Module: one of `frontend`, `backend`, `ingestion`, `nlp-pipeline`, or `platform` for cross-cutting changes.

One commit per logical change. If the diff covers two unrelated things, split into two commits.

### Step 4 — Push to the module branch

```bash
git push -u origin <target-branch>
```

If this is the first push of a new module branch, this also creates it on the remote.

### Step 5 — Open the pull request

```bash
gh pr create \
  --base main \
  --head <target-branch> \
  --title "<module>: <one-line summary>" \
  --body "$(cat <<'EOF'
## What changed
<2-4 bullet points, plain language>

## Module
<frontend | backend | ingestion | nlp-pipeline>

## How to verify
<one or two concrete steps a reviewer can run or check>

## Related
<link an issue/task if one exists, otherwise omit this section>
EOF
)"
```

### Step 6 — Assign a reviewer who is not the author

```bash
gh pr edit <pr-number> --add-reviewer <a-teammate-who-is-not-the-current-operator>
```

The agent must never add the current operator (the human it's acting for) as the reviewer. If the agent doesn't know who else is available, list the other 5 team members and ask the human to pick one, or assign round-robin from the module's member list in Section 2 if the human says "just pick someone."

### Step 7 — Confirm and report back

Print the PR URL to the human. Do not attempt to merge it, approve it, or ping anyone outside the repo's own review request. The agent's job ends when the PR is open and correctly reviewer-assigned.

## 5. Enforcing "Author Cannot Merge Their Own PR"

GitHub already blocks a PR author from approving their own pull request — this is platform-level, not something either the repo owner or the agent needs to build. Combined with the branch protection settings below, this gives you the exact rule you asked for: authored-by-them PRs cannot be merged by them, only by a teammate who reviews and approves.

One team member (repo admin) needs to configure this once, in GitHub, not something an agent should attempt via API without explicit human instruction:

Settings → Branches → Add branch protection rule, applied to `main` and to each of the four module branches:

- Require a pull request before merging: on
- Require approvals: 1 (minimum)
- Require review from someone other than the last pusher: on (this is the setting that most directly enforces your rule)
- Dismiss stale pull request approvals when new commits are pushed: on
- Do not allow bypassing the above settings: on (applies the rule to admins too, including any human who might otherwise self-merge)
- Restrict who can push to matching branches: on, limited to the repo's collaborators (blocks any direct push that skips the PR flow entirely)

Once this is set, even if an agent or a human tries to merge their own PR, GitHub will refuse it at the platform level. This is the actual enforcement mechanism — the agent's job is to always go through `gh pr create` rather than ever touching `main` directly, not to police the review itself.

## 6. Conflict and Merge Etiquette

- Module branches merge into `main` only after review approval. Merging is done by the approving reviewer, or by whoever the team has designated to press the merge button, never by the PR author.
- Before opening a PR, sync your module branch against `main` if `main` has moved since you branched, to catch conflicts early:

```bash
git fetch origin
git merge origin/main
```

Resolve any conflicts locally, commit the resolution, then push and open the PR. Don't let GitHub's web UI surface a conflict a reviewer then has to untangle.

- If two members on the same module branch both have pending work, whoever pushes second should `git pull --rebase` before pushing, not force-push over the other's commits.

## 7. One-Time Setup (each member does this once)

```bash
gh auth login
git config user.name "<your name>"
git config user.email "<your email>"
git clone <repo-url>
cd sic-portal
git fetch origin
git checkout <your-assigned-module-branch>
```

If your module branch doesn't exist on the remote yet, the first person on that module creates it from `main`:

```bash
git checkout main
git pull origin main
git checkout -b <module-branch>
git push -u origin <module-branch>
```

## 8. Quick Reference

| Human says | Agent does |
|---|---|
| "push my changes" | Resolve branch (Section 3) → run full workflow (Section 4) |
| "open a PR" | Same as above, or Steps 5-7 alone if already pushed |
| "merge this PR" | Refuse. Explain that only a non-author teammate can merge, via GitHub, after review. |
| "just push straight to main, it's urgent" | Refuse. Explain Section 1 rule 1, offer to fast-track a PR and flag the reviewer for immediate attention instead. |
| "force push" | Ask for explicit confirmation and check the branch is not shared before doing it. Refuse outright on `main` or any module branch with more than one active contributor. |

---

*Keep this file at the repo root as `AGENTS.md`. Most AI coding agents (Claude Code, Cursor, and others adopting the emerging AGENTS.md convention) auto-read a root-level file with this name — if your team's tool instead looks for `CLAUDE.md` or `.cursorrules`, symlink or copy this content there rather than maintaining two versions.*