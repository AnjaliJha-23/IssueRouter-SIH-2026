# NLP Pipeline — Cost & Performance Optimization Plan

**Project:** SIC Portal / IssueRouter · SIH 2026 (SIH26043) · Team Convergence
**Scope:** `backend/pipeline/`, `backend/ingestion/`, `backend/api/`, deployment (Azure App Service B1 + Vercel)
**Status:** Proposal — analysis complete, no code changed
**Model ownership (per `docs/CONTRIBUTING.md` / `AGENTS.md`):** AI Intake — code changes belong on the `nlp-pipeline` branch; deployment/config changes may also touch `backend` / `platform`.

> This document is a *plan*, not an implementation. Nothing in the repository was modified to produce it.

---

## 0. TL;DR — the three immediate levers

1. **Fix the currently broken `summarization.py`** (missing imports + undefined `get_client()`).
2. **Stop shipping CUDA torch** — swap to the CPU wheel right away, then remove torch entirely.
3. **Offload BART classification → LLM API** and **MiniLM embeddings → hosted embedding API**, then delete `torch` / `transformers` / `sentence-transformers`.

Together these cut the deploy image from ~2.5–3 GB to ~300–500 MB, resident RAM from ~1.5–1.8 GB to ~150–300 MB, and let the backend run comfortably on B1 — or on scale-to-zero Container Apps for close to $0 during a demo.

---

## 1. Diagnosis — where the compute (and therefore cost) actually goes

The ingestion path is fully **synchronous inside the request thread**:

```
POST /api/challenges/  ·  /api/challenges/ingest  ·  /api/process
        │
        └─ process_evidence()            backend/pipeline/orchestrator.py:27
             clean_text                 ingestion/normaliser.py
             → classify(BART)           pipeline/classification.py
             → spaCy NER                pipeline/location_extraction.py
             → get_embedding(MiniLM)    pipeline/embeddings.py
             → resolve(cosine)          pipeline/deduplication.py
             → generate_summary(Groq)   pipeline/summarization.py
             → calculate_priority       pipeline/priority_scoring.py
             → DB commit
```

Everything heavy runs in **one Gunicorn worker** — `startup.sh` forces `WORKER_COUNT=1` — on a **B1 = 1 vCPU / 1.75 GB RAM** box. Five concrete culprits:

| # | Culprit | Location | Why it hurts on B1 |
|---|---|---|---|
| 1 | `facebook/bart-large-mnli` (~1.6 GB fp32) loaded in-process and executed **twice** (domain pass + subdomain pass) | `backend/pipeline/classification.py` | Single biggest RAM consumer: ~1.5–1.6 GB of the 1.75 GB budget. A forward pass on 1 vCPU takes seconds, ×2 passes → multi-second blocking request. Cold start 60–120 s+. |
| 2 | `sentence-transformers/all-MiniLM-L6-v2` (~80–90 MB) plus the whole **torch** runtime | `backend/pipeline/embeddings.py` | Keeps torch resident just to produce 384-d vectors. |
| 3 | **`torch>=2.2.0` pinned to default PyPI** | `backend/requirements.txt:17` | On Linux this resolves to the **CUDA** wheel and pulls the `nvidia-*` stack (~2–3 GB) at build time — even though no GPU is used. Huge image, slow Oryx deploys, wasted disk. The CPU index hint exists only as a comment and is not applied. |
| 4 | No caching anywhere; LLM + embedding called for every evidence item | `backend/cache/` (contains only an empty `summaries.json`) | Retweets and seed replays re-invoke models and network calls on identical text. |
| 5 | Entire pipeline blocks the single vCPU | `orchestrator.py`, `backend/api/challenges.py:186,225` | One slow inference stalls the whole API — no concurrency. |

### 1.1 Currently-broken file (blocking correctness, fix regardless)

`backend/pipeline/summarization.py` has **no import statements** and calls an **undefined `get_client()`** at line 28 — *outside* the `try` block. Every code path that reaches `process_evidence()` (i.e. `POST /api/challenges/`, `/ingest`, `/api/process`, and `POST /{id}/analyze`) will raise `NameError`. This must be repaired before any optimization work.

### 1.2 Model naming — standardized on Groq Compound Mini ✅ (resolved)

The summarization model is now **`groq/compound-mini`** everywhere, with `pipeline/config.py` as the single source of truth:

- `pipeline/config.py` → `SUMMARIZATION_MODEL = "groq/compound-mini"`
- `backend/.env.example` → `GROQ_MODEL=groq/compound-mini`
- `pipeline/summarization.py` → `os.getenv("GROQ_MODEL", SUMMARIZATION_MODEL)` (no hard-coded default)
- `pipeline/orchestrator.py` and `backend/seed_mock_data.py` → already record `"groq/compound-mini"`.

There is no longer any `gpt-oss` reference in the project. (Note: `summarization.py` still needs the Sector G1 repair — missing `import os` / `import json` and the undefined `get_client()` — before this model is actually invoked.)

---

## 2. The two proposed ideas — validated

### 2.1 Use GPT / an LLM for the "decision" — ✅ strongly recommended

On 1 vCPU a local BART forward pass is **slower than an LLM round-trip** *and* consumes the entire RAM budget. A single structured-output LLM call can return `{domain, subdomain, tags, severity_hint}` in one shot, replacing **two** BART passes.

Design caveats:

- **Pin a small/cheap model** — e.g. Groq `llama-3.3-70b-versatile`, OpenAI `gpt-4o-mini` / `gpt-5-mini`, or the Azure OpenAI equivalent — with `response_format=json_schema`. (Summarization itself stays on `groq/compound-mini`; this is only about the future classification stage.)
- **Keep a deterministic keyword fallback** (domain → keyword map in `config.py`) so the demo never depends on the network.
- **Keep priority scoring deterministic.** Do not let the LLM produce the priority number — explainability is a documented non-negotiable (`Blueprint §7`, `ARCHITECTURE.md §6`).
- **Cost scales with volume.** The mock feed replays every ~8 s and `backend/run_large_scale_simulation.py` processes many items → cache by text hash and skip the LLM for obvious cases.
- **Latency budget.** The frontend Axios client uses a 15 s timeout (`frontend/src/api/client.js`), so the LLM stage must stay well under it — or move processing to a background task (Sector C).

### 2.2 Use NVIDIA NIM embeddings instead of sentence-transformers — ✅ feasible, with one important correction

- "NVIDIA NIM" is the *container/runtime*. **Self-hosting NIM requires a GPU**, which would **increase** cost. The cost-reducing form is the **hosted** endpoint: the NVIDIA API catalog (`build.nvidia.com`) or **NVIDIA models served via Azure AI Foundry serverless**.
- Real model IDs to target:
  - `nvidia/nv-embedqa-e5-v5` — **1024-d**
  - `nvidia/llama-3.2-nv-embedqa-1b-v2` — 2048-d
  - `nvidia/nv-embed-v1` — 4096-d
- **These are not 384-d.** Switching requires **re-embedding stored evidence** and a **versioned embedding dimension** — otherwise cosine similarity silently produces nonsense because `ChallengeEvidence.embedding_json` stores raw float lists.
- **Cheaper/simpler alternatives worth weighing:**
  - Azure OpenAI `text-embedding-3-small` (1536-d, ~$0.02/1M tokens).
  - **Local ONNX / fastembed MiniLM** (~40–90 MB, **no torch**) — stays offline, no per-call cost, still removes the torch dependency.

> **Key insight:** you only get the real win — deleting `torch`/`transformers`/`sentence-transformers` and shrinking the image — by replacing **both** BART *and* MiniLM. Replacing just the embedder while keeping BART leaves torch loaded and saves almost nothing.

---

## 3. Implementation plan by sector

Each item lists **what → where → impact → effort → risk**.

### Sector A — De-localize heavy inference (biggest RAM / CPU win)

| ID | Change | Files | Impact | Effort | Risk |
|---|---|---|---|---|---|
| **A1** | Add `LLMClassifier` behind `CLASSIFIER_BACKEND=llm\|local_bart\|keyword`. One JSON-schema call returns `{domain, subdomain, tags, severity_hint}`; keep the existing return contract so `orchestrator.py` is untouched. | `pipeline/classification.py`, `pipeline/config.py` | Removes ~1.6 GB RAM; 2 passes → 1 offloaded call | M | Med (network dependency → mitigated by fallback) |
| **A2** | Add `APIEmbedder` behind `EMBEDDING_BACKEND=api\|local_onnx\|local_minilm`, returning a fixed `EMBEDDING_DIM`. Add a **dimension-versioned embedding** and re-embed on mismatch. | `pipeline/embeddings.py`, `db/models.py` | Removes ~90 MB + torch | M | Med (dimension migration) |
| **A3** | Once A1+A2 are default, **drop `torch`, `transformers`, `sentence-transformers`, `scikit-learn`, `scipy`** from requirements; replace sklearn `cosine_similarity` with a NumPy dot of normalized vectors. | `backend/requirements.txt`, `pipeline/deduplication.py` | Image ~2.5–3 GB → ~300–500 MB; frees RAM | S | Low |
| **A4** | Replace spaCy NER with a pure-Python gazetteer matcher (dict/regex) from the existing gazetteer JSON. NER is already fully rule-based → behaviour-preserving. `NER_BACKEND=spacy\|regex`. | `pipeline/location_extraction.py`, `pipeline/data/jharkhand_gazetteer.json` | Removes ~50–100 MB + load time | S | Low |
| **A5** | If a local classifier fallback is required, use a distilled/ONNX model (`valhalla/distilbart-mnli-12-3` or an ONNX MiniLM) — **never** full `bart-large-mnli` on B1. | `pipeline/classification.py` | Keeps a local fallback viable | S | Low |

### Sector B — Hosting / platform (biggest $ win)

| ID | Change | Detail | Impact |
|---|---|---|---|
| **B1** | **Evaluate Azure Container Apps (Consumption) with scale-to-zero** vs staying on App Service B1. | B1 is always-on (≈$13/mo, indicative). Container Apps has a monthly free grant (~180k vCPU-s + 360k GiB-s + 2M requests) and `minReplicas: 0`. Trade-off: cold start on scale-from-zero → use `minReplicas=1` only during the demo or add a scheduled warm-up ping. | Largest recurring saving |
| **B2** | If staying on App Service, immediately switch to the **CPU torch wheel** until A3 is done. | `torch --extra-index-url https://download.pytorch.org/whl/cpu`. Also confirm **persistent `/home` storage** for SQLite + HF cache, or the DB resets on every deploy/restart. | Stops multi-GB CUDA builds |
| **B3** | Decide the durable data store now. | Keep **SQLite on App Service `/home`** (fine for 1 worker) **or** move to **Azure Postgres Flexible Server Burstable B1ms** (needed if you go multi-replica / scale-to-zero, since scale-to-zero requires external state). Embeddings are JSON in `ChallengeEvidence.embedding_json`; **pgvector** is the future vector-search path but is not required to cut cost. | Enables B1 safely |

### Sector C — Async + caching (removes the 1-vCPU stall)

| ID | Change | Files | Impact |
|---|---|---|---|
| **C1** | Move `process_evidence` off the request thread (FastAPI `BackgroundTasks` or a small queue) for `/api/challenges/` and `/api/challenges/ingest`; return the created/linked record immediately. Keep `/{id}/analyze` synchronous for the reviewer flow. | `backend/api/challenges.py`, `pipeline/orchestrator.py` | No more multi-second blocking requests |
| **C2** | Build a real cache in `backend/cache/`: (a) embedding cache keyed by `sha256(text)`, (b) classification cache for identical/near-identical text, (c) canonical-embedding cache per challenge, (d) summary cache. | `backend/cache/`, `pipeline/*` | Directly cuts LLM + embedding spend on replays |
| **C3** | Batch embeddings where a caller submits multiple evidence items. | `pipeline/embeddings.py` | Fewer round-trips |
| **C4** | Only warm models eagerly if local models remain; otherwise keep lazy. | `main.py`, `orchestrator.py:16` | Faster startup when API-backed |

### Sector D — Pipeline correctness & efficiency

| ID | Change | Location | Notes |
|---|---|---|---|
| **D1** | Collapse domain+subdomain into one LLM call (see A1). | `classification.py` | Removes a second inference round |
| **D2** | **Fix the canonical-embedding bug** — the code uses the *first* evidence embedding as the challenge centroid (un-ordered `.first()`), not the canonical summary embedding as documented. Recompute/store the centroid on update. | `orchestrator.py:88` | Improves dedup accuracy |
| **D3** | Make **trend** time-window based (trailing timestamp buckets) instead of `"increasing" if ev_count > 2`. | `orchestrator.py:187,322` | Matches docs (`NLP_PIPELINE_IMPLEMENTATION_MAP.md §2.7`) |
| **D4** | Fix the confidence/name mismatch — `challenge.ai_confidence` stores **evidence confidence**, not model confidence. | `orchestrator.py:191,326` | Correctness / clarity |
| **D5** | Vectorize `deduplication.py` — normalize the candidate matrix once and do a single `np.dot` instead of a per-candidate `cosine_similarity` loop. | `deduplication.py:51-64` | Speed |
| **D6** | Fix the district-only candidate query edge case: when `district is None` the query filters by domain only, then `resolve()` re-filters on `district is None`. | `orchestrator.py:80-83` | Correctness |

### Sector E — Frontend / Vercel (minor)

- **E1.** The frontend is a static Vite SPA on Vercel → already effectively free. Keep all compute server-side. Ensure `VITE_API_URL` points at the (possibly new) backend and update `ALLOWED_ORIGINS` / `CORS_ORIGINS` in `backend/.env`.
- **E2.** Reduce backend chatter — cache list/stats responses (SWR / React Query stale-while-revalidate) so the 1-vCPU backend isn't hit repeatedly; this lowers the required SKU.

### Sector F — Observability, guardrails, feature flags

- **F1.** Per-stage **feature flags** so the same build runs local-only or API-backed — preserves the "demo must not depend on unstable external services" requirement (`MVP_PLAN.md`, `ROADMAP Phase 6`).
- **F2.** Log **tokens / latency / cost per stage**; add a `/ready` endpoint reporting model/client readiness separately from `/`.
- **F3.** **Dedupe/throttle identical submissions** before they reach the LLM to cap runaway cost.
- **F4.** Respect the 15 s client timeout — keep the LLM stage well under it or move it to a background task (C1).

### Sector G — Immediate blocking fixes (do first)

- **G1.** Repair `pipeline/summarization.py`: add `import os`, `import json`, and a cached `get_client()` (Groq / OpenAI / Azure client). Currently raises `NameError`.
- **G2.** Unify the summarization model name across `config.py`, `.env.example`, and the code default.
- **G3.** Decide `WARM_MODELS_ON_STARTUP` and document the cold-start behaviour for the demo.

---

## 4. Proposed config / env contract (stages become swappable)

```dotenv
# Classifier
CLASSIFIER_BACKEND=llm                 # llm | local_bart | keyword
CLASSIFICATION_MODEL=llama-3.3-70b-versatile   # or gpt-4o-mini / gpt-5-mini

# Embeddings
EMBEDDING_BACKEND=api                  # api | local_onnx | local_minilm
EMBEDDING_MODEL=nvidia/nv-embedqa-e5-v5        # or text-embedding-3-small
EMBEDDING_DIM=1024

# NER
NER_BACKEND=regex                      # regex | spacy

# Provider credentials
LLM_API_BASE=
LLM_API_KEY=
EMBEDDING_API_BASE=
EMBEDDING_API_KEY=

# Behaviour
ENABLE_EMBEDDING_CACHE=true
PIPELINE_ASYNC=true
```

---

## 5. Recommended sequence (quick wins first)

1. **G1–G3** — fix the broken summarizer + model-name drift (unblocks the app).
2. **B2 / A3 (partial)** — swap to the CPU torch wheel immediately (stops multi-GB CUDA builds on the next deploy).
3. **A1 + A2** — LLM classifier + hosted embedder behind flags; validate against `backend/tests/test_nlp_pipeline.py`.
4. **A3 + A4** — remove torch/transformers/sentence-transformers/sklearn/spaCy; replace with NumPy + regex.
5. **C1 + C2** — async + caching.
6. **B1** — evaluate Container Apps scale-to-zero vs keeping B1.
7. **D1–D6 / E / F** — efficiency, correctness, guardrails.

---

## 6. Indicative cost model

> Figures are **approximate (2026) and indicative** — verify on the Azure pricing calculator before committing to a plan.

| Metric | Today (B1) | Lean target |
|---|---|---|
| Hosting | App Service B1 Linux, always-on ≈ **$13/mo** | Container Apps Consumption, scale-to-zero ≈ **$0–5/mo** |
| Deploy image | ~2.5–3 GB (CUDA torch) | ~300–500 MB |
| Resident RAM | ~1.5–1.8 GB (BART) — at/over the B1 limit | ~150–300 MB |
| Cold start | 60–120 s+ | 2–10 s |
| Classification / request | 2 local BART passes (seconds, blocks 1 vCPU) | 1 offloaded LLM call (~0.3–1 s) |
| Net effect | Pinned to B1+ because of RAM | Fits B1 comfortably; can scale to zero |

---

## 7. Open decisions

- **Embedding provider:** NVIDIA NIM (Azure AI Foundry serverless / `build.nvidia.com`) vs Azure OpenAI `text-embedding-3-small` vs local ONNX/fastembed (no per-call cost, offline).
- **LLM provider for classification/summary:** Groq (fast, cheap/free) vs Azure OpenAI vs OpenAI direct — this also decides whether you consolidate to a single provider/key.
- **Hosting target:** stay on App Service B1 vs move to Container Apps (scale-to-zero). This drives the state/DB decision (SQLite on `/home` vs Postgres).

---

## 8. Constraints & process notes

- Per `docs/AGENTS.md`: changes under `backend/pipeline/` belong on the **`nlp-pipeline`** branch; deployment/config changes may also touch **`backend`** / **`platform`**. Everything reaches `main` through a reviewed PR — no direct pushes, no self-merges.
- Keep the explainability guarantee intact: every AI-derived field must retain its factors, and reviewers can override AI results (`Blueprint §15`, `ARCHITECTURE.md §9`).
- The demo must remain runnable **without** live external services. Every API-backed stage needs a deterministic fallback and a cache.

---

*Team Convergence · SIH 2026 · Problem Statement SIH26043*
