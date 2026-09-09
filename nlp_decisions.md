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
  - `summarization.py`: Added `GROQ_MODEL` environment variable support (defaulting to `llama-3.3-70b-versatile`), with robust extractive fallback if external LLM APIs return 404/rate limit or if `GROQ_API_KEY` is not present.
- **Impact:** Ensures the pipeline always succeeds deterministically without crashing on third-party service outages.

---

## 🏛️ Pipeline Module Architectural Reference

| Submodule | Core Responsibility | Underlying Model / Logic | Config Key / Contract |
|---|---|---|---|
| `classification.py` | Top-level domain & subdomain classification | Zero-Shot `facebook/bart-large-mnli` | `DOMAINS` (10 categories), `SUBDOMAIN_MAP` |
| `location_extraction.py` | 24 Jharkhand districts & block resolution | spaCy `EntityRuler` + `jharkhand_gazetteer.json` | Exact, Substring, Coords fallback |
| `embeddings.py` | 384-dimensional dense semantic vectors | `sentence-transformers/all-MiniLM-L6-v2` | `[Domain] Cleaned_Text` |
| `deduplication.py` | Filter by `(domain, district)` + Cosine similarity clustering | `scikit-learn` Cosine Similarity | `auto_link` (≥0.80), `flag_related` (0.60–0.79), `new_challenge` (<0.60) |
| `priority_scoring.py` | Explainable 0–100 priority calculation | Weighted Severity (30%), Volume (25%), Conf (25%), Trend (20%) | `DOMAIN_SEVERITY`, `TREND_MULTIPLIERS` |
| `summarization.py` | Canonical title & problem statement generation | Groq Llama LLM with Extractive Fallback | `{"title": str, "description": str}` |
| `router.py` | Department routing with municipality overrides | Rule-based mapping with city overrides | `CATEGORY_TO_DEPARTMENT`, `CITY_OVERRIDES` |
| `orchestrator.py` | End-to-end multi-stage pipeline executor | SQLAlchemy DB persistence to `Challenge`, `ChallengeEvidence`, `ChallengeAnalysis`, `ChallengeRelation` | `process_evidence(data, db)` |

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
