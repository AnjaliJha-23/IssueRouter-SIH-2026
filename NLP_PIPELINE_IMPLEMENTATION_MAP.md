# NLP / AI Pipeline — Implementation Map

**Module owner (per CONTRIBUTING.md):** AI Intake
**Repository surface:** `backend/pipeline/`, feeding from `backend/ingestion/`, writing to `backend/db/`
**Blueprint sections grounding this map:** Blueprint §3, §4, §7, §8, §13, §14; ARCHITECTURE.md §4, §6, §8; ROADMAP.md Phase 1 & Phase 3; README.md §6

> Note on scope: the project docs describe `backend/pipeline/` as containing "AI classification, deduplication, scoring, summarization" but the actual Python modules are not present in this workspace (only the markdown docs were provided). This map therefore proposes the concrete file layout inside the *documented* repository path, using the REBUILD/EXTEND/NEW labeling convention required by Blueprint §19. Before implementation, run Phase 0 (repo audit) to confirm which of these files already exist under different names and reconcile.

---

## 1. Where the Pipeline Sits in the System

```
Twitter/X Adapter ──┐
                     ├──▶ backend/ingestion/  (normalize to raw evidence)
Citizen Web Form ────┘              │
                                     ▼
                     backend/pipeline/orchestrator.py
                                     │
        ┌────────────┬──────────────┼───────────────┬────────────────┐
        ▼            ▼              ▼               ▼                ▼
  classification  location_ner  embeddings    dedup/clustering  priority_scoring
   .py             .py           .py            .py               .py
        │            │              │               │                │
        └─────────────────┬─────────┴───────────────┴────────────────┘
                           ▼
                 summarization.py (canonical challenge text)
                           ▼
              backend/db/ writes: ChallengeEvidence,
              ChallengeAnalysis, ChallengeRelation, Challenge (create/update)
                           ▼
              backend/api/challenges.py exposes:
              POST /api/challenges/{id}/analyze, GET analysis, GET dedup candidates
```

The pipeline is called from two places:
1. **Ingestion time** — every new Evidence item (tweet, citizen form) is run through the full pipeline automatically to decide if it joins an existing Master Challenge or creates a new candidate one (Blueprint §4, §20).
2. **On-demand re-analysis** — via `POST /api/challenges/{id}/analyze`, so a government reviewer can trigger re-scoring after new evidence is linked or after weights are tuned (ARCHITECTURE.md §8).

---

## 2. Module-by-Module Design

### 2.1 `backend/pipeline/__init__.py` — **EXTEND**
Exposes a single public entrypoint, `run_pipeline(evidence: EvidenceIn) -> PipelineResult`, so `ingestion/` and `api/challenges.py` never call individual stages directly. This keeps the orchestration logic in one place and makes the pipeline independently testable via `test_pipeline.py`.

### 2.2 `backend/pipeline/classification.py` — **EXTEND**
- **Model:** `facebook/bart-large-mnli` (zero-shot classification), loaded once at process start and cached (see §4 Caching).
- **Labels:** the 10 societal domains referenced in README §6 — Healthcare, Education, Water & Sanitation, Environment, Energy, Urban Development, Accessibility, Public Administration, Rural Livelihoods, Infrastructure/Transport (confirm exact 10 against the existing IssueRouter category list during Phase 0 audit; do not silently rename categories already used in seed data).
- **Input:** normalized evidence text (title + body, cleaned of URLs/mentions for tweets).
- **Output contract:**
  ```json
  {
    "domain": "Healthcare",
    "subdomain": "Rural Access",
    "domain_scores": {"Healthcare": 0.83, "Public Administration": 0.09, "...": "..."},
    "model_version": "facebook/bart-large-mnli"
  }
  ```
- **Reused from IssueRouter:** category taxonomy and thresholding logic if present; retarget label set from generic complaint categories to the societal domain list.
- **Subdomain:** a second-pass zero-shot call scoped to a per-domain subdomain label set (e.g., Healthcare → {Rural Access, PHC Staffing, Diagnostics, Maternal Health, Waterborne Disease}), only run when top-domain confidence clears a threshold (default 0.55, configurable).

### 2.3 `backend/pipeline/location_extraction.py` — **EXTEND**
- **Model:** spaCy pipeline (`en_core_web_sm` or similar base model) + a custom `EntityRuler` seeded with a **Jharkhand gazetteer** (24 districts + block-level names).
- **Reused from IssueRouter:** existing spaCy NER integration; the gazetteer itself is new/expanded.
- **Resolution order:** (1) EntityRuler exact/fuzzy match against gazetteer → (2) spaCy `GPE`/`LOC` entities → (3) fallback to evidence's submitted lat/long (citizen form) or profile location (Twitter geotag/user location, when available) → (4) unresolved, flagged for manual tagging.
- **Output contract:**
  ```json
  {
    "district": "Ranchi",
    "block": "Namkum",
    "village_ward": null,
    "latitude": 23.34,
    "longitude": 85.42,
    "resolution_method": "gazetteer_match",
    "confidence": 0.9
  }
  ```
- **Gazetteer file:** `backend/pipeline/data/jharkhand_gazetteer.json` — **NEW**, structured as `{district: [block, block, ...]}`, sourced once and version-controlled; frontend's `frontend/src/data/` geography file should be generated from (or kept in sync with) this same source to avoid two diverging copies of Jharkhand geography (Blueprint §3.2 "do not maintain separate systems" applies here too).

### 2.4 `backend/pipeline/embeddings.py` — **NEW**
- **Model:** `sentence-transformers/all-MiniLM-L6-v2`.
- **Responsibility:** produce a fixed-length embedding vector per evidence item's canonical text (title + cleaned body, domain-prefixed to aid separation, e.g. `"[Healthcare] <text>"`).
- **Storage:** store embeddings alongside `ChallengeEvidence` rows (a `vector`/`ARRAY(Float)` column, or a lightweight `EvidenceEmbedding` side table if the SQLAlchemy/Postgres setup doesn't support pgvector — confirm DB choice against `backend/db/` during Phase 0; SQLite fallback stores as a JSON-encoded float array).
- **Caching layer:** `backend/cache/` (already in repo structure per README §7) should cache embeddings for identical/near-identical text to avoid recomputation on ingestion retries.

### 2.5 `backend/pipeline/deduplication.py` — **REBUILD**
This is the module most affected by the shift from "single-source clustering" to "unified multi-source clustering" (Blueprint §3.2, §19).

- **Input:** new evidence's embedding + domain + location.
- **Candidate retrieval:** narrow the search space before computing full cosine similarity — filter existing open/active Master Challenges by same `domain` and same `district` (and `block` if resolved) first, then compute cosine similarity against that candidate set only. This avoids an O(n) full-corpus scan on every ingestion event.
- **Similarity scoring:** cosine similarity between new evidence embedding and each candidate challenge's canonical embedding (canonical embedding = embedding of the challenge's current summary, recomputed by `summarization.py` on each update — see §2.6).
- **Decision thresholds (configurable, store in `backend/pipeline/config.py`):**
  | Similarity | Action |
  |---|---|
  | ≥ 0.80 | Auto-link evidence to existing Master Challenge |
  | 0.60 – 0.79 | Create `ChallengeRelation` as "probable duplicate/related", surface to government reviewer for confirm/reject (never auto-merge in this band) |
  | < 0.60 | Treat as new candidate Master Challenge |
- **Cross-source requirement:** the same threshold logic applies whether the new evidence is a tweet or a citizen form — there must be no source-specific branch that creates a separate clustering path (this is the literal Blueprint §19 instruction: "Do not create separate Twitter and citizen clustering systems").
- **Output contract:**
  ```json
  {
    "action": "link" | "flag_related" | "new_challenge",
    "matched_challenge_id": "HC-102",
    "similarity_score": 0.84,
    "candidate_relations": [{"challenge_id": "HC-098", "score": 0.71}]
  }
  ```

### 2.6 `backend/pipeline/summarization.py` — **EXTEND**
- **Model:** fast LLM inference via Groq or Hugging Face inference endpoint (README §6), used to (a) synthesize/update the canonical challenge title + description whenever new evidence is linked, and (b) regenerate the canonical embedding text fed back into `embeddings.py`.
- **Prompt contract:** deterministic, template-based prompt (not free-form) so output stays auditable — inputs are the existing canonical summary (if any) + the new evidence text + domain/location tags; output is a JSON object `{title, description}` validated against a Pydantic schema before being written to `Challenge`.
- **Human-review requirement:** AI-generated summary is always editable by the government verifier (ARCHITECTURE.md §9); store `ai_generated_summary` and `official_description` as separate fields so an edited official description never gets silently overwritten by the next summarization pass.
- **Failure fallback:** if the LLM call fails or times out, fall back to a simple extractive summary (first N characters of highest-confidence evidence text) rather than blocking the pipeline — this satisfies the "demo must not depend on unstable external services" constraint (MVP_PLAN.md, ROADMAP Phase 6).

### 2.7 `backend/pipeline/priority_scoring.py` — **MODIFY**
Per Blueprint §7 and ARCHITECTURE.md §6, this produces the 0–100 priority score plus evidence confidence and trend, all with stored explanations.

- **Priority score factors (weights configurable, defaults below — mirror the Smart Router's "store weights + explanation" pattern):**
  | Factor | Default weight | Signal |
  |---|---|---|
  | Severity (domain-derived, e.g. health/safety domains weighted higher) | 30% | From `classification.py` domain + keyword severity list |
  | Evidence volume | 25% | Count of linked evidence items |
  | Evidence confidence | 25% | See below |
  | Trend (rate of new evidence over time) | 20% | See below |
- **Evidence confidence:** a separate 0–1 score based on report volume, source diversity (Twitter + citizen form present = higher confidence than single-source), consistency of location/domain across evidence, presence of media (photos/docs), and any government verification signal already present.
- **Trend:** classify as `increasing` / `stable` / `decreasing` by comparing evidence arrival rate over the trailing window (e.g., 7-day bucket counts) — only computed once a challenge has enough timestamped evidence (≥3 items) to be statistically meaningful; otherwise trend = `insufficient_data`.
- **Output contract:**
  ```json
  {
    "priority_score": 78,
    "priority_factors": {"severity": 0.9, "evidence_volume": 0.6, "confidence": 0.8, "trend": 0.7},
    "evidence_confidence": 0.82,
    "trend": "increasing",
    "explanation": "High severity healthcare domain, 6 evidence items across 2 sources, consistent location, rising report rate over 7 days."
  }
  ```
- **Human-readable explanation string** is mandatory on every score, matching the Smart Router's explainability contract (Blueprint §7) — reviewers must never see a bare number.

### 2.8 `backend/pipeline/orchestrator.py` — **NEW**
Sequences the stages, handles partial failure, and writes results:
1. `classification.classify(text)`
2. `location_extraction.extract(text, evidence_metadata)`
3. `embeddings.embed(text, domain)`
4. `deduplication.resolve(embedding, domain, location)` → decide link/flag/new
5. If linked or new: `summarization.update_canonical(challenge, evidence)`
6. `priority_scoring.score(challenge)`
7. Persist `ChallengeAnalysis` row (domain, tags, priority, confidence, trend, model versions used) and, if action was `flag_related`, persist `ChallengeRelation` rows for reviewer triage.
8. Write an `AuditLog` entry for any Master Challenge creation/update caused by the pipeline (ARCHITECTURE.md §9).

Each stage is wrapped so a single stage failure (e.g., LLM timeout) degrades gracefully rather than aborting the whole pipeline — logged and retried on next re-analysis rather than blocking evidence ingestion.

### 2.9 `backend/pipeline/config.py` — **NEW**
Single place for all tunables: domain label list, similarity thresholds, priority factor weights, confidence thresholds for subdomain classification, cache TTLs. This is what makes weights "configurable" as required by Blueprint §7/§17 without redeploying code — expose a subset of this (Smart Router + priority weights) through an admin-only config endpoint if time allows (SHOULD HAVE, not MUST HAVE).

---

## 3. Data Model Touchpoints (`backend/db/`)

| Table | Pipeline's read/write role |
|---|---|
| `ChallengeEvidence` | Read text/metadata in; write resolved location fields back |
| `ChallengeAnalysis` | Written by orchestrator after every pipeline run — domain, tags, priority, confidence, trend, `model_version` per stage (so results are reproducible/auditable) |
| `ChallengeRelation` | Written when similarity falls in the "flag_related" band; reviewer resolves via dedup API |
| `Challenge` | Created on `new_challenge`, updated (title/description/location/priority) on `link` |
| `AuditLog` | Written on every Master Challenge create/update triggered by the pipeline |

Confirm during Phase 0 whether an existing `Cluster`/`Tweet` table from the original IssueRouter can be repurposed as `ChallengeEvidence` (Blueprint §19 explicitly asks to reuse Cluster/Tweet concepts rather than inventing parallel tables).

---

## 4. Model Loading & Caching Strategy

- Load `bart-large-mnli`, spaCy pipeline, and `all-MiniLM-L6-v2` **once per process** at startup (not per-request) — expose as module-level singletons in each pipeline file, imported by `orchestrator.py`.
- Use `backend/cache/` for: (a) embedding cache keyed by text hash, (b) classification cache for identical/near-identical evidence text (common with retweet-style duplicate signals), (c) short-TTL cache of a challenge's canonical embedding so dedup doesn't recompute it on every incoming evidence item.
- All models must run CPU-only and fit comfortably for a live demo — confirm `bart-large-mnli` load time and consider a distilled zero-shot alternative (e.g., `valhalla/distilbart-mnli-12-3`) if startup/inference latency threatens the 5–10 minute demo constraint (MVP_PLAN.md Definition of Done).

---

## 5. API Surface Tied to This Module

| Endpoint | Pipeline responsibility |
|---|---|
| `POST /api/challenges/{id}/analyze` | Re-run orchestrator on demand |
| `GET /api/challenges/{id}/analysis` | Return latest `ChallengeAnalysis` with factor breakdowns |
| `GET /api/challenges/{id}/relations` (dedup candidates) | Return `ChallengeRelation` rows in the "flag_related" band for reviewer confirm/reject |
| `POST /api/challenges/{id}/relations/{relation_id}` (link/merge/mark-separate) | Reviewer override — writes to `AuditLog`, does not touch pipeline code itself but consumes its output |

---

## 6. Explainability & Human-Override Requirements (non-negotiable per Blueprint §15, §8)

- Every AI-derived field (domain, priority, confidence, trend, similarity match) must be stored with its contributing factors, not just a final number.
- Every AI-derived field must be reviewer-editable, and an edit must not be silently reverted by the next pipeline run (e.g., `official_description` vs `ai_generated_summary` split in §2.6).
- Model name + version is stored per `ChallengeAnalysis` row so a judge or auditor can see exactly which model produced which result.

---

## 7. Testing Plan (`backend/test_pipeline.py`)

- Unit tests per stage: classification label correctness on a small labeled Jharkhand-domain fixture set; location extraction against known district/block strings including ambiguous/misspelled inputs; embedding similarity sanity checks (near-duplicate text scores high, unrelated text scores low).
- Integration test: feed a seeded Twitter-style signal and a seeded citizen-form submission describing the *same* rural healthcare issue → assert they converge on one `Challenge` id (this is the literal Definition of Done in MVP_PLAN.md and the core Demo Story beat in ROADMAP.md §"Demo Story").
- Fallback test: force the summarization LLM call to fail → assert pipeline still completes via extractive fallback and evidence still gets linked/created.
- Regression fixture: lock a small "golden set" of Jharkhand HealthTech seed evidence (rural telemedicine, PHC diagnostics, waterborne disease — README §9) so demo behavior doesn't silently drift as thresholds are tuned.

---

## 8. Build Sequencing (maps to ROADMAP Phase 1 → Phase 3)

1. `location_extraction.py` gazetteer + `embeddings.py` (low risk, no external dependency beyond local models).
2. `classification.py` domain retargeting.
3. `deduplication.py` rebuild with candidate-filtering + threshold bands.
4. `orchestrator.py` wiring + `ChallengeAnalysis`/`ChallengeRelation` persistence.
5. `priority_scoring.py` factor weights + explanation strings.
6. `summarization.py` LLM integration + extractive fallback.
7. `config.py` externalized tunables, then wire into Smart Router's own weighting UI if time allows (Phase 3 dependency).

**Exit criterion for this module (ties to ROADMAP Phase 1 exit):** a seeded tweet and a seeded citizen report about the same rural healthcare issue converge on one Master Challenge, with a stored, human-readable explanation for the domain, priority, confidence, and match decision.
