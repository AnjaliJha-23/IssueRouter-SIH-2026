# NLP Pipeline Architectural Decisions & Changelog (`nlp_decisions.md`)

This file documents all architectural decisions, design contracts, threshold tunings, fixes, and modifications applied to the **IssueRouter NLP / AI Pipeline module** (`backend/pipeline/`, `backend/tests/`, and related touchpoints).

---

## 📋 Changelog & Decision History

### [2026-09-09] — Comprehensive Pipeline Verification, Bug Fixes & Test Suite Implementation

#### 1. Test Suite Creation & Multi-Source Verification
- **Decision:** Implemented a dual-layer test framework:
  1. **PyTest Suite (`backend/tests/test_nlp_pipeline.py`)**: 20 automated unit and end-to-end integration tests covering all 9 pipeline stages.
  2. **Standalone Smoke & Integration Runner (`backend/test_pipeline.py`)**: Standalone CLI runner with model warmup, individual component verification, in-memory SQLite DB persistence, and multi-source signal convergence checks.
- **Verification Result:** 20/20 tests passing (100% pass rate).

#### 2. Lazy-Loading in Pipeline Package Initialization (`backend/pipeline/__init__.py`)
- **Motivation:** Importing submodules (e.g. `pipeline.config`, `pipeline.router`) triggered `pipeline/__init__.py`, which eagerly imported `orchestrator.py` and forced immediate startup of heavy ML libraries (`torch`, `transformers`, `sentence_transformers`).
- **Change:** Refactored `process_evidence` and `load_all_models` in `backend/pipeline/__init__.py` to lazy load the orchestrator functions upon invocation.
- **Impact:** Lightweight utilities and tests execute instantly without unneeded library initialization overhead.

#### 3. Parent District Gazetteer Inference Fix (`backend/pipeline/location_extraction.py`)
- **Motivation:** Test failure in `TestLocationExtraction.test_block_match_infers_district` identified that when spaCy's `EntityRuler` matched a block (e.g., `Namkum`), the parent district (`Ranchi`) remained `None`.
- **Change:** Added post-match gazetteer lookup in `extract_entities` to automatically resolve and populate the parent district whenever a block entity is matched.
- **Impact:** Guarantees proper `domain + district` candidate filtering in deduplication even if evidence only specifies a block name.

#### 4. Resilient spaCy Model Loading (`backend/pipeline/location_extraction.py`)
- **Motivation:** `spacy.load("en_core_web_sm")` failed when the pre-trained model package was not downloaded in the environment.
- **Change:** Added fallback to `spacy.blank("en")` with custom `EntityRuler` seeded from `backend/pipeline/data/jharkhand_gazetteer.json`.
- **Impact:** Eliminates hard dependencies on external downloads while preserving 100% accuracy for Jharkhand district/block gazetteer matching.

#### 5. Configurable Model Versions & Extractive Fallback (`backend/pipeline/classification.py` & `backend/pipeline/summarization.py`)
- **Motivation:** Environment flexibility and zero downtime during network or API rate limits.
- **Change:** 
  - `classification.py`: Made classification model configurable via `CLASSIFICATION_MODEL` (defaults to `facebook/bart-large-mnli`).
  - `summarization.py`: Added `GROQ_MODEL` environment variable support (defaulting to `groq/compound-mini`), with robust extractive fallback if external LLM APIs return 404/rate limit or if `GROQ_API_KEY` is not present.
- **Impact:** Ensures the pipeline always succeeds deterministically without crashing on third-party service outages.

#### 6. JEV Decision Model for Domain Classification (`backend/pipeline/classification.py`, `backend/pipeline/jev_client.py`)
- **Motivation:** The local `facebook/bart-large-mnli` zero-shot pipeline held ~1.6 GB of weights on a 1.75 GB B1 instance and ran two forward passes per complaint.
- **Change:**
  - `classification.py`: introduced `CLASSIFIER_BACKEND` (`jev` | `transformers` | `keyword`, default `jev`). The `jev` backend asks TypeSafe System One for domain (`Choice`), severity (`Score`) and urgency (`Noul`) in one call, plus a gated second call for subdomain. `keyword` (`pipeline/keyword_classifier.py`) is the deterministic Hinglish-aware offline fallback. `transformers` keeps the legacy local BART and is imported only when explicitly selected.
  - Added `pipeline/jev_client.py` (httpx client, retry on 429/529) and the JEV rubrics `DOMAIN_CRITERIA` / `SEVERITY_LEVELS` in `config.py`.
- **Impact:** Frees ~1.6 GB of RAM and removes torch/transformers from the default import path. Return contract unchanged, so `orchestrator.py` is untouched. Any API failure or missing key falls back to the lexicon, so the pipeline never hard-fails on the decision model.

#### 7. Hosted embeddings and summarization on NVIDIA NIM (`backend/pipeline/nvidia_embed.py`, `backend/pipeline/nvidia_llm.py`)
- **Motivation:** `sentence-transformers` pulled `torch` + `transformers` into every process just to produce dedup vectors — hundreds of MB of dependencies and resident RAM on a 1.75 GB instance. Summarization was also tied to a single provider.
- **Change:**
  - `embeddings.py`: introduced `EMBEDDING_BACKEND` (`api` | `local_minilm`, default `api`). The `api` backend calls NVIDIA NIM `POST /v1/embeddings` with `nvidia/nemotron-3-embed-1b` (2048-d, `input_type=passage`); `local_minilm` keeps the offline 384-d model as an optional dev extra. `EMBEDDING_DIM` is derived from the model rather than read from env, and `get_embedding()` returns `None` instead of raising when no backend can serve a vector, so dedup degrades to `new_challenge` instead of failing a submission.
  - **Dimension versioning:** vectors are tagged `<model>:<dimension>` in the new `challenge_evidence.embedding_model` column (added by the startup migration). A stored vector from a different model is never compared; `orchestrator.py` re-embeds it once and persists the result (capped at 25 per request) so pre-existing rows rejoin dedup. The `api` backend deliberately does **not** fall back to the local model — mixing 2048-d and 384-d vectors in one comparison set would silently corrupt every score.
  - `deduplication.py`: cosine similarity is a NumPy dot product of L2-normalised unit vectors; `scikit-learn` is gone. Thresholds are unchanged.
  - `summarization.py` + `nvidia_llm.py`: introduced `SUMMARIZATION_BACKEND` (`nvidia` | `groq` | `extractive`, default `nvidia`), calling NIM `POST /chat/completions` with `nvidia/nemotron-3.5-lightning-30b-a3b` (`config.SUMMARIZATION_MODEL`, overridable via `NVIDIA_MODEL`). The deterministic extractive fallback still guards every failure path, and `generate_summary()` now reports which backend served the summary.
  - **The NIM chat model must be verified against the live catalog.** The model originally chosen for this path, `qwen/qwen2.5-7b-instruct`, was retired by NVIDIA: `POST /v1/chat/completions` answers a bare `404 page not found`, which the pipeline silently absorbs as an extractive fallback. `GET https://integrate.api.nvidia.com/v1/models` is public and is now the check of record — an unknown ID returns `404`, a retired one returns `410 Gone`. The embedding model (`nvidia/nemotron-3-embed-1b`) is unaffected and still returns 200.
  - **A catalog listing is not proof the account can call the model.** `google/gemma-3-12b-it` and `mistralai/mistral-7b-instruct-v0.3` both appear in the public catalog and answer `GET /v1/models/<id>` with 200, yet `POST /v1/chat/completions` answers `404 ... Not found for account '<id>'`. Only a real chat completion proves a model is usable, and a 404 there degrades silently to extractive.
  - **Reasoning models need the thinking budget pinned to 0.** `nvidia/nemotron-3.5-lightning-30b-a3b` reasons before answering, and the trace is returned in `message.reasoning_content` while `message.content` stays empty; it also counts against `max_tokens`, so the 150-token summary budget was spent on reasoning and production fell back to extractive. NVIDIA's own request examples suggest `chat_template_kwargs.enable_thinking=false`, but **that field hangs the request when `stream=false`** — measured >120s with no response, versus ~5s for the identical call without it (with `stream=true` it returns in ~62s). The reliable switch is the top-level `reasoning_budget`, now defaulted to `0` via `NVIDIA_REASONING_BUDGET` (`omit` drops the field). Measured: budget 0 → 200, `finish_reason=stop`, real JSON, 4–9s warm; thinking left on → 200 but empty `content` with a 535-char trace.
  - `requirements.txt`: dropped `torch`, `transformers`, `sentence-transformers`, `scikit-learn`, `scipy`, `huggingface-hub`, `tokenizers` and `groq`; all are now documented optional local-dev extras.
- **Impact:** the default deployment ships no model weights and no torch runtime, and `analysis.model_versions` records the backend that actually served each stage (including `"extractive"`, and `null` embeddings when no vector was produced).

### [2026-10-18] — Deferred summarization for instant submissions

#### 8. Citizen submissions answer instantly; the hosted summary lands afterwards
- **Motivation:** a hosted summary costs ~5-15s and can take far longer, and it sat on the request path of `POST /api/challenges/`, so every citizen waited on an external model before getting a response.
- **Change:**
  - `summarization.generate_summary(..., allow_hosted=False)` returns the deterministic extractive summary without touching the network — the "first half" of a deferred submission.
  - `orchestrator.process_evidence(..., defer_summary=...)` uses it and hands the caller a job dict describing what the hosted call needs. Callers that omit the argument (seeders, simulations, `POST /api/challenges/ingest`) keep the fully synchronous behaviour, so nothing else changed speed.
  - `orchestrator.refresh_summary(job, db)` performs the hosted call and persists the resulting title, description and `analysis.model_versions["summarization"]`. It re-reads the evidence rather than replaying the job's copy, so if a second submission lands while the first job is queued, the newer evidence still wins regardless of the order the jobs run in.
  - `api.challenges.schedule_summary` / `_summary_worker` run those jobs on **one** worker thread, started lazily on first use.
- **One worker is not incidental.** Measured against the free NIM tier, concurrent chat completions do not share: with three submissions in flight, all three failed every retry (~91s each) and stayed extractive, while the same calls issued one at a time all succeeded. A single worker also keeps a burst of submissions from occupying the request threadpool, which a locking background task would do.
- **Measured end to end over HTTP** against a throwaway SQLite database and the live endpoint: submission answered in ~2.2-2.8s (previously ~13s) carrying the extractive title; a canary upgraded after 17.3s; three submissions fired back to back upgraded at +32.7s / +48.2s / +85.9s, all four served by `nvidia/nemotron-3.5-lightning-30b-a3b` with no fallbacks in the log.
- **Impact:** the submission path no longer depends on the hosted model at all. The response is always the deterministic summary, and it is replaced in place once the model answers. Any failure in the background path leaves the extractive summary standing, so the fallback contract is unchanged. `analysis.model_versions["summarization"]` reads `extractive` until the hosted summary lands.
- **Caveat:** free-tier NIM latency is highly variable (observed 4-56s for a single call). If the queue cannot keep up with a burst, later submissions keep their extractive summary; raising `NVIDIA_TIMEOUT` trades a longer per-job wait for fewer fallbacks.

---

## 🏛️ Pipeline Module Architectural Reference

| Submodule | Core Responsibility | Underlying Model / Logic | Config Key / Contract |
|---|---|---|---|
| `classification.py` | Top-level domain & subdomain classification | TypeSafe **JEV** (System One) via `CLASSIFIER_BACKEND=jev`, with a deterministic keyword-lexicon fallback (`transformers` keeps local BART) | `DOMAINS` (10 categories), `SUBDOMAIN_MAP`, `DOMAIN_CRITERIA` |
| `location_extraction.py` | 24 Jharkhand districts & block resolution | spaCy `EntityRuler` + `jharkhand_gazetteer.json` | Exact, Substring, Coords fallback |
| `embeddings.py` | Dense semantic vectors | `EMBEDDING_BACKEND=api` → NVIDIA NIM `nvidia/nemotron-3-embed-1b` (2048-d); `local_minilm` → offline `all-MiniLM-L6-v2` (384-d) | `[Domain] Cleaned_Text`, tag stored as `<model>:<dim>` |
| `deduplication.py` | Filter by `(domain, district)` + cosine similarity clustering | NumPy dot product of L2-normalised vectors | `auto_link` (≥0.80), `flag_related` (0.60–0.79), `new_challenge` (<0.60) |
| `priority_scoring.py` | Explainable 0–100 priority calculation | Weighted Severity (30%), Volume (25%), Conf (25%), Trend (20%) | `DOMAIN_SEVERITY`, `TREND_MULTIPLIERS` |
| `summarization.py` | Canonical title & problem statement generation | `SUMMARIZATION_BACKEND=nvidia` → NIM `nvidia/nemotron-3.5-lightning-30b-a3b`; `groq` legacy; `extractive` offline. `allow_hosted=False` answers extractively without a network call | `{"title": str, "description": str, "model": str}` |
| `router.py` | Department routing with municipality overrides | Rule-based mapping with city overrides | `CATEGORY_TO_DEPARTMENT`, `CITY_OVERRIDES` |
| `orchestrator.py` | End-to-end multi-stage pipeline executor | SQLAlchemy DB persistence to `Challenge`, `ChallengeEvidence`, `ChallengeAnalysis`, `ChallengeRelation`. Summarization can be deferred: `process_evidence(..., defer_summary=...)` stores the extractive summary and `refresh_summary(job, db)` applies the hosted one later | `process_evidence(data, db, defer_summary=None)` → `dict`, `refresh_summary(job, db)` → `dict \| None` |
| `api/challenges.py` | Citizen submission endpoint | `schedule_summary` queues hosted summaries on one lazily-started worker thread (`_summary_worker`) | `POST /api/challenges/` returns the extractive summary immediately |

---

## 🧪 Verification & Test Commands

To execute tests for the NLP pipeline:

```bash
# Option 1: Run the full PyTest test suite (20 tests)
cd backend
py -3.12 -m pytest tests/test_nlp_pipeline.py -v

# Option 2: Run the standalone smoke and E2E convergence runner
cd backend
py -3.12 test_pipeline.py
```
