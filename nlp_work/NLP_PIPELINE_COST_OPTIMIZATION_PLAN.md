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
3. **Offload BART classification → the TypeSafe JEV decision model** (✅ shipped) and **MiniLM embeddings → hosted embedding API**, then delete `torch` / `transformers` / `sentence-transformers`.

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

### 1.2 Model naming — standardized on NVIDIA NIM ✅ (resolved; provider changed)

Summarization now runs on **NVIDIA NIM** (`qwen/qwen2.5-7b-instruct`), still with `pipeline/config.py` as the single source of truth:

- `pipeline/config.py` → `SUMMARIZATION_MODEL = "qwen/qwen2.5-7b-instruct"`
- `backend/.env.example` → `NVIDIA_MODEL=qwen/qwen2.5-7b-instruct`
- `pipeline/summarization.py` → `os.getenv("NVIDIA_MODEL", SUMMARIZATION_MODEL)` (no hard-coded default)
- `pipeline/orchestrator.py` and `backend/seed_mock_data.py` → record the effective model via `summarization.active_model()`.

`SUMMARIZATION_BACKEND` (`nvidia` | `groq` | `extractive`, default `nvidia`) selects the provider, and the deterministic extractive fallback is unchanged. There is no `gpt-oss` reference in the project.

---

## 2. The two proposed ideas — validated

### 2.1 Offload the "decision" to a hosted model — ✅ shipped as TypeSafe JEV

On 1 vCPU a local BART forward pass is **slower than a hosted round-trip** *and* consumes the entire RAM budget. A single call returns domain, subdomain, severity and urgency in one shot, replacing **two** BART passes.

**Decision: TypeSafe JEV (System One), not a general-purpose LLM.** JEV is a hosted *classifier*, not a text generator: one `POST /v1/systemone` carries a map of typed questions (`Choice` for domain/subdomain, `Score` for severity, `Noul` for urgency) and returns calibrated probabilities the code branches on directly. It is defined entirely by the `criteria` we send, so new domains are added by editing `config.py` — no fine-tuning, no prompt drift, and nothing to parse. Pricing: **$0.042/MTok input, output free** (≈$0.000027 per complaint, measured).

Design caveats, all honoured in the implementation:
- **Keep a deterministic keyword fallback** (domain → keyword map in `config.py`) so the demo never depends on the network.
- **Keep priority scoring deterministic.** Do not let the LLM produce the priority number — explainability is a documented non-negotiable (`Blueprint §7`, `ARCHITECTURE.md §6`).
- **Cost scales with volume.** The mock feed replays every ~8 s and `backend/run_large_scale_simulation.py` processes many items → cache by text hash and skip the LLM for obvious cases.
- **Latency budget.** The frontend Axios client uses a 15 s timeout (`frontend/src/api/client.js`), so the LLM stage must stay well under it — or move processing to a background task (Sector C).

### 2.2 Use NVIDIA NIM embeddings instead of sentence-transformers — ✅ shipped

- "NVIDIA NIM" is the *container/runtime*. **Self-hosting NIM requires a GPU**, which would **increase** cost. The cost-reducing form is the **hosted** endpoint, and that is what shipped: `POST https://integrate.api.nvidia.com/v1/embeddings`.
- **Model chosen:** `nvidia/nemotron-3-embed-1b` — **2048-d**, 4096-token window, and it requires an explicit `input_type` (`passage` for stored evidence). `nvidia/nv-embedqa-e5-v5` (1024-d) and `nvidia/llama-3.2-nv-embedqa-1b-v2` (2048-d) remain drop-in alternatives via `NVIDIA_EMBED_MODEL`.
- **These are not 384-d,** so switching required **re-embedding stored evidence** and a **versioned embedding dimension** — both shipped: `challenge_evidence.embedding_model` stores `<model>:<dimension>`, mismatched rows are re-embedded lazily (capped at 25 per request), and shape-mismatched vectors are never compared.
- **Cheaper/simpler alternative kept available:** `EMBEDDING_BACKEND=local_minilm` restores the offline `all-MiniLM-L6-v2` (384-d). It is no longer installed by `requirements.txt`, so it is an opt-in dev extra.

> **Key insight:** you only get the real win — deleting `torch`/`transformers`/`sentence-transformers` and shrinking the image — by replacing **both** BART *and* MiniLM. That is now done: A1 + A2 shipped, and A3 removed the packages.

---

## 3. Implementation plan by sector

Each item lists **what → where → impact → effort → risk**.

### Sector A — De-localize heavy inference (biggest RAM / CPU win)

| ID | Change | Files | Impact | Effort | Risk |
|---|---|---|---|---|---|
| **A1** | ✅ **Shipped.** `CLASSIFIER_BACKEND=jev\|transformers\|keyword` (default `jev`). The `jev` backend asks TypeSafe System One for domain (`Choice`) + severity (`Score`) + urgency (`Noul`) with a gated second call for subdomain; `keyword` is the deterministic offline fallback; `transformers` is the opt-in legacy BART. Return contract unchanged, `orchestrator.py` untouched. New: `pipeline/jev_client.py`, `pipeline/keyword_classifier.py`. | `pipeline/classification.py`, `pipeline/config.py` | Removes ~1.6 GB RAM; 2 local passes → 1–2 hosted calls | M | Low (auto-fallback to keyword) |
| **A2** | ✅ **Shipped.** `EMBEDDING_BACKEND=api\|local_minilm` (default `api`), with `EMBEDDING_DIM` derived from the model. The `api` backend calls NVIDIA NIM `nvidia/nemotron-3-embed-1b` (2048-d); `local_minilm` keeps the offline 384-d model as an optional extra. **Dimension-versioned embeddings** shipped: `challenge_evidence.embedding_model` stores `<model>:<dim>`, mismatches are re-embedded lazily, and cross-dimension comparisons are skipped. New: `pipeline/nvidia_embed.py`. | `pipeline/embeddings.py`, `pipeline/deduplication.py`, `db/models.py`, `pipeline/orchestrator.py` | Removes ~90 MB + torch from the process | M | Med (dimension migration — handled) |
| **A3** | ✅ **Shipped.** `torch`, `transformers`, `sentence-transformers`, `scikit-learn`, `scipy` (plus `huggingface-hub`, `tokenizers`, `groq`) dropped from requirements; sklearn `cosine_similarity` replaced by a NumPy dot of normalised vectors. | `backend/requirements.txt`, `pipeline/deduplication.py` | Image ~2.5–3 GB → ~300–500 MB; frees RAM | S | Low |
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
# Classifier  (✅ shipped; see backend/.env.example)
CLASSIFIER_BACKEND=jev                 # jev | transformers | keyword
JEV_MODEL=jev-latest                   # TypeSafe System One model id
TYPESAFE_API_KEY=                      # https://console.typesafe.ai/keys
CLASSIFICATION_MODEL=facebook/bart-large-mnli   # only used when CLASSIFIER_BACKEND=transformers

# Embeddings + summarization  (✅ shipped; see backend/.env.example)
NVIDIA_API_KEY=                        # https://build.nvidia.com/ (nvapi-…)
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

EMBEDDING_BACKEND=api                  # api | local_minilm
NVIDIA_EMBED_MODEL=nvidia/nemotron-3-embed-1b   # 2048-d

SUMMARIZATION_BACKEND=nvidia           # nvidia | groq | extractive
NVIDIA_MODEL=qwen/qwen2.5-7b-instruct

# NER  (A4 — not yet shipped; spaCy is the last in-process model)
NER_BACKEND=spacy                      # spacy | regex

# Behaviour  (C1/C2 — not yet shipped)
ENABLE_EMBEDDING_CACHE=false
PIPELINE_ASYNC=false
```

---

## 5. Recommended sequence (quick wins first)

1. **G1–G3** — fix the broken summarizer + model-name drift (unblocks the app). ✅
2. **B2 / A3 (partial)** — CPU torch wheel, to stop multi-GB CUDA builds. ✅ superseded: A3 removed torch entirely.
3. **A1 ✅ + A2 ✅** — JEV classifier shipped and validated on 10 Hinglish samples (10/10 correct); hosted embeddings shipped with dimension versioning.
4. **A3 ✅** — `torch`/`transformers`/`sentence-transformers`/`scikit-learn`/`scipy` removed from requirements; dedup is a NumPy dot.
5. **A4** — replace spaCy NER with a pure-Python gazetteer matcher (outstanding; spaCy is the last in-process model).
6. **C1 + C2** — async + caching.
7. **B1** — evaluate Container Apps scale-to-zero vs keeping B1.
8. **D1–D6 / E / F** — efficiency, correctness, guardrails.

---

## 6. Indicative cost model

> Figures are **approximate (2026) and indicative** — verify on the Azure pricing calculator before committing to a plan.

| Metric | Today (B1) | Lean target |
|---|---|---|
| Hosting | App Service B1 Linux, always-on ≈ **$13/mo** | Container Apps Consumption, scale-to-zero ≈ **$0–5/mo** |
| Deploy image | ~2.5–3 GB (CUDA torch) | ~300–500 MB |
| Resident RAM | ~1.5–1.8 GB (BART) — at/over the B1 limit | ~150–300 MB |
| Cold start | 60–120 s+ | 2–10 s |
| Classification / request | 2 local BART passes (seconds, blocks 1 vCPU) | 1–2 JEV calls (≈1–4 s observed; falls back to the offline lexicon) |
| Net effect | Pinned to B1+ because of RAM | Fits B1 comfortably; can scale to zero |

> **Update:** with A1–A3 shipped, the *Deploy image*, *Resident RAM* and *Classification / request* rows already sit at the lean target. The remaining gap is hosting (B1) and cold start.

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
