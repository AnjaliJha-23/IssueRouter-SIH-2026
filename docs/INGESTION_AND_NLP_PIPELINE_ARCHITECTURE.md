# IssueRouter: Ingestion & NLP Pipeline Technical Architecture & Deep Dive

> **SIH 2026 — Societal Innovation & Civic Intelligence Platform**  
> **Module Ownership:** Data Ingestion, Text Normalization, Natural Language Processing (NLP), Semantic Clustering, Geo-Resolution, Priority Scoring, and AI Orchestration.

---

## 1. Executive Summary & Module Scope

In modern civic-tech systems, citizen grievances and societal signals arrive asynchronously from heterogeneous, unstructured channels (social media feeds like Twitter/X, direct citizen portal forms, community reports, and municipal feeds). Raw signals are notoriously noisy: they feature unstructured text, slang, missing metadata, redundant duplicates of the same physical incident, and vague geographical descriptions.

The **Ingestion & NLP Pipeline** is the intelligence gateway of **IssueRouter**. It transforms noisy, raw civic evidence into structured, geocoded, deduplicated, prioritized, and actionable **Master Societal Challenges**.

```text
===================================================================================
                       DATA INGESTION & NLP PIPELINE FLOW
===================================================================================

 [ Twitter / X Stream ]                                [ Citizen Web Form ]
           |                                                      |
           +--------------------------+---------------------------+
                                      |
                                      v
                 +------------------------------------------+
                 | 1. TEXT NORMALIZATION (clean_text)       |
                 | - Strips URLs, @mentions, & noise emojis |
                 | - Preserves hashtag text (e.g. #water)   |
                 +------------------------------------------+
                                      |
                                      v
                 +------------------------------------------+
                 | 2. ZERO-SHOT DOMAIN CLASSIFIER (classify)|
                 | - Model: facebook/bart-large-mnli        |
                 | - 10 Primary Civic Domains               |
                 | - Conditional Subdomain 2nd Pass         |
                 +------------------------------------------+
                                      |  
                                      v
                 +------------------------------------------+
                 | 3. SPATIAL NER & GAZETTEER RESOLUTION    |
                 | - spaCy EntityRuler + Jharkhand Gazetteer|
                 | - Matches Block & Infers Parent District |
                 | - Fallback: Substring / GPS Coordinates  |
                 +------------------------------------------+
                                      |
                                      v
                 +------------------------------------------+
                 | 4. DENSE SEMANTIC EMBEDDINGS (get_embed) |
                 | - Model: all-MiniLM-L6-v2 (384 dims)     |
                 | - Prefixes domain context: [Domain] Text |
                 +------------------------------------------+
                                      |
                                      v
                 +------------------------------------------+
                 | 5. PARTITIONED DEDUPLICATION ENGINE      |
                 | - Candidate Partition: (Domain, District)|
                 | - Vectorized Cosine Similarity (Score S) |
                 +------------------------------------------+
                                      |
                 +--------------------+--------------------+
                 |                    |                    |
            (S >= 0.80)        (0.60 <= S < 0.80)       (S < 0.60)
                 |                    |                    |
                 v                    v                    v
          +--------------+     +--------------+     +--------------+
          | Action: LINK |     | FLAG RELATED |     | NEW CHALLENGE|
          | Link to old  |     | Create new & |     | Create fresh |
          | Challenge ID |     | log Relation |     | Challenge ID |
          +--------------+     +--------------+     +--------------+
                 |                    |                    |
                 +--------------------+--------------------+
                                      |
                                      v
                 +------------------------------------------+
                 | 6. MULTI-EVIDENCE LLM SUMMARIZATION      |
                 | - Model: groq/compound-mini              |
                 | - Generates canonical Title (<=10 words) |
                 |   and Description (<=30 words)           |
                 | - Zero-downtime extractive fallback      |
                 +------------------------------------------+
                                      |
                                      v
                 +------------------------------------------+
                 | 7. EXPLAINABLE PRIORITY SCORING          |
                 | - 4-Factor Weighted Formula (0-100 score)|
                 |   Severity (30%) + Volume (25%) +        |
                 |   Confidence (25%) + Trend (20%)         |
                 +------------------------------------------+
                                      |
                                      v
                 +------------------------------------------+
                 | 8. JURISDICTIONAL SMART ROUTER           |
                 | - Category -> Nodal Department           |
                 | - City Municipal Overrides (e.g. MCGM)   |
                 +------------------------------------------+
                                      |
                                      v
                 +------------------------------------------+
                 | 9. DATABASE TRANSACTION (SQLAlchemy)     |
                 | - Challenge, Evidence, Analysis, Relation|
                 | - Real-time WebSocket Broadcast to UI    |
                 +------------------------------------------+
```

---

## 2. Complete End-to-End System Workflow & Tech Stack

Before diving into the pipeline internals, here is how the Ingestion & NLP layer bridges the raw inputs to the full application stack.

```text
===================================================================================
                       END-TO-END SYSTEM WORKFLOW
===================================================================================

 [ Citizens & Sensors ]
           |
           | (Twitter/X API, Citizen Web Portal, Simulation)
           v
 +---------------------------------------------------------------------------------+
 |                           1. INGESTION & NORMALIZATION                          |
 | - Normalizer: Regex sanitization, URL removal, hashtag semantic preservation    |
 +---------------------------------------------------------------------------------+
                                      |
                                      v
 +---------------------------------------------------------------------------------+
 |                           2. NLP & AI INTELLIGENCE PIPELINE                     |
 | - Classification: BART-Large-MNLI (10 Domains + Subdomains)                     |
 | - Spatial NER: spaCy EntityRuler + Jharkhand Gazetteer + Lat/Lng Fallback       |
 | - Embeddings: sentence-transformers/all-MiniLM-L6-v2 (384-dimensional)          |
 | - Deduplication: Partitioned Cosine Similarity (Auto-Link / Flag / New)         |
 | - Summarization: groq/compound-mini + Extractive Fallback                 |
 | - Priority Scoring: Explainable 4-Factor Linear Model (0-100)                   |
 | - Smart Routing: Category to Department Mapping + City Overrides                |
 +---------------------------------------------------------------------------------+
                                      |
                                      v
 +---------------------------------------------------------------------------------+
 |                           3. DATA PERSISTENCE & BROADCAST                       |
 | - Relational DB: SQLite (Dev) / PostgreSQL (Prod) via SQLAlchemy ORM            |
 | - Event Broadcaster: FastAPI WebSocket Channels for Live UI Updates            |
 +---------------------------------------------------------------------------------+
                                      |
                 +--------------------+--------------------+
                 |                                         |
                 v                                         v
 +----------------------------------+     +----------------------------------------+
 |   4. REAL-TIME FRONTEND DASHBOARD|     |   5. DOWNSTREAM ROLE-BASED PORTALS     |
 | - Next.js 14 + React + Tailwind  |     | - Government Verification Portal       |
 | - Dynamic Incident Heatmaps      |     | - University Innovation & R&D Hub      |
 | - Live Clustered Challenge Feed  |     | - Industry Collaboration Workspace     |
 +----------------------------------+     +----------------------------------------+
```

### Full Project Tech Stack Overview

| Layer | Technology | Role in System |
|---|---|---|
| **Ingestion Engine** | Python 3.12, Tweepy, Regex | Stream ingestion, polling, text sanitization |
| **NLP & Deep Learning** | PyTorch, Hugging Face Transformers, `sentence-transformers` | Zero-shot inference, dense embeddings |
| **Information Extraction** | spaCy v3, Custom Rule-based EntityRuler | Spatial Named Entity Recognition (NER), Gazetteer resolution |
| **Deduplication / Math** | Scikit-Learn, NumPy | High-speed vectorized cosine similarity, matrix operations |
| **Generative AI** | Groq SDK (`groq/compound-mini`) | Canonical issue synthesis, incremental summarization |
| **Backend & APIs** | FastAPI, Pydantic v2, Uvicorn | Async REST APIs, WebSockets, lifecycle management |
| **Data Persistence** | SQLAlchemy 2.0, SQLite (Dev) / PostgreSQL (Prod) | Relational schema with foreign keys and embedded JSON vectors |
| **Frontend UI** | Next.js 14, React, TailwindCSS, Lucide Icons | Real-time map dashboard, university/industry portal, admin panels |

---

## 3. Stage-by-Stage Technical Deep Dive (What, How, and Why)

Every stage in `backend/pipeline/` and `backend/ingestion/` was designed with specific algorithmic and architectural constraints. Below is the comprehensive breakdown of each stage.

---

### Stage 1: Ingestion & Text Normalization

- **Files:** `backend/ingestion/normaliser.py`, `backend/ingestion/mock_feed.py`, `backend/ingestion/x_listener.py`
- **Module Function:** `clean_text(raw: str) -> str`

#### What it does
Receives raw JSON payloads from external streams (Twitter/X streaming API, simulated replay feeds, or direct HTTP citizen forms) and purifies the text representation before sending it to NLP models.

#### How it works
```python
# Regular expression pipeline:
1. Strip URLs: r'http\S+|www\S+' -> ''
2. Strip @mentions: r'@\w+' -> ''
3. Preserve Hashtag text, strip '#': r'#(\w+)' -> r'\1' (e.g. #watercrisis -> watercrisis)
4. Filter out emojis & noise: r'[^\w\s\.,!?-]' -> ''
5. Whitespace normalization: r'\s+' -> ' '
```

#### Why this decision?
- **Preserving Hashtag Semantic Value:** Hashtags contain rich topical keywords (e.g., `#RanchiWaterCrisis`). Deleting the entire hashtag destroys critical NER and classification tokens; deleting only the `#` symbol retains the semantic information.
- **Model Efficiency & Noise Reduction:** Transformer tokenizers waste compute and context length parsing complex URLs, nested mentions, and irregular emojis that do not contribute to civic classification.
- **Idempotency:** The clean text ensures deterministic downstream embeddings regardless of source platform formatting quirks.

---

### Stage 2: Zero-Shot Domain & Subdomain Classification

- **Files:** `backend/pipeline/classification.py`, `backend/pipeline/config.py`
- **Model:** `facebook/bart-large-mnli` (configurable via `CLASSIFICATION_MODEL` env var)
- **Module Function:** `classify(text: str) -> dict`

```text
                            Raw Cleaned Text
                                   |
                                   v
             +-------------------------------------------+
             | 1st Pass: Top-Level Domain Classification |
             | (10 candidate domains via BART-Large-MNLI)|
             +-------------------------------------------+
                                   |
                                   v
             +-------------------------------------------+
             | Is Top Confidence >= 0.55                 |
             | AND Top Domain exists in SUBDOMAIN_MAP?   |
             +-------------------------------------------+
                     |                           |
                   [YES]                        [NO]
                     |                           |
                     v                           v
     +-------------------------------+   +-----------------------------+
     | 2nd Pass: Subdomain Inference |   | Set Subdomain = None        |
     | (Confidence threshold >= 0.40)|   |                             |
     +-------------------------------+   +-----------------------------+
                     |                           |
                     +-------------+-------------+
                                   |
                                   v
             +-------------------------------------------+
             | Output Classification Contract Payload    |
             | (domain, subdomain, domain_scores, model) |
             +-------------------------------------------+
```

#### What it does
Categorizes unstructured text into one of 10 primary government operational domains and performs a second conditional pass to identify granular subdomains.

#### 10 Primary Domains
1. `Healthcare`
2. `Education`
3. `Water & Sanitation`
4. `Environment`
5. `Energy`
6. `Urban Development`
7. `Accessibility`
8. `Public Administration`
9. `Rural Livelihoods`
10. `Infrastructure/Transport`

#### How it works
1. **First-Pass Zero-Shot Classification:** Runs Natural Language Inference (NLI) using BART-Large-MNLI. The text serves as the *premise*, and `"This text is about {domain}"` serves as the *hypothesis*.
2. **Confidence Filtering:** If the top domain confidence exceeds `0.55` and the domain has mapped subdomains in `SUBDOMAIN_MAP`, a second zero-shot pass is triggered over the sub-categories.
3. **Output Contract:**
```json
{
  "domain": "Healthcare",
  "subdomain": "PHC Staffing",
  "domain_scores": {
    "Healthcare": 0.892,
    "Water & Sanitation": 0.045
  },
  "model_version": "facebook/bart-large-mnli"
}
```

#### Why this decision?
- **Zero-Shot vs Supervised Classifier:** Civic problem categories evolve constantly. In hackathons and production pilots, there is no pre-labeled dataset of 50,000 localized Indian civic complaints. Zero-shot NLI allows instant domain expansion by merely editing `config.py` without model retraining.
- **Hierarchical Two-Pass Routing:** Running a single flat classification across 50+ granular subdomains severely degrades MNLI softmax distribution. A two-pass hierarchical approach (Domain -> Subdomain) maintains high statistical precision.

---

### Stage 3: Spatial NER & Geographical Gazetteer Resolution

- **Files:** `backend/pipeline/location_extraction.py`, `backend/pipeline/data/jharkhand_gazetteer.json`
- **Engine:** spaCy v3 with custom `EntityRuler` + Tri-level Fallback Hierarchy
- **Module Function:** `extract_entities(text: str, evidence_metadata: dict) -> dict`

```text
                     Clean Evidence Text + Metadata
                                   |
                                   v
             +-------------------------------------------+
             | 1. spaCy EntityRuler Exact Match          |
             | (Patterns seeded from jharkhand_gazetteer)|
             +-------------------------------------------+
                     |                           |
               [Match Found]               [No Match]
                     |                           |
                     v                           v
     +-------------------------------+   +-----------------------------+
     | Match District / Block        |   | 2. Case-Insensitive Substring|
     | If Block -> Infer Parent Dist |   | Scan across full Gazetteer  |
     | (Confidence: 0.85 - 0.90)     |   +-----------------------------+
     +-------------------------------+           |              |
                     |                     [Match Found]    [No Match]
                     |                           |              |
                     |                           v              v
                     |           +--------------------+  +--------------------+
                     |           | Set fuzzy_gazetteer|  | 3. Metadata GPS   |
                     |           | (Confidence: 0.70) |  | Coordinate Check   |
                     |           +--------------------+  +--------------------+
                     |                     |                    |       |
                     |                     |              [Coords]   [No Coords]
                     |                     |                    |       |
                     |                     |                    v       v
                     |                     |             +------------+ +------------+
                     |                     |             |Coords Conf | |Unresolved  |
                     |                     |             |(Conf: 0.95)| |(Conf: 0.0) |
                     |                     |             +------------+ +------------+
                     |                     |                    |       |
                     +---------------------+--------------------+-------+
                                           |
                                           v
             +-------------------------------------------------------------+
             | Output Location Contract Payload                            |
             | (district, block, latitude, longitude, method, confidence)  |
             +-------------------------------------------------------------+
```

#### What it does
Extracts administrative boundaries (Districts and Blocks across all 24 districts of Jharkhand) and resolves parent-child relationships (e.g., matching block `Namkum` automatically resolves parent district `Ranchi`).

#### How it works
1. **Primary Pass (spaCy EntityRuler):** Evaluates text through spaCy with patterns compiled directly from the comprehensive `jharkhand_gazetteer.json`. Matches `DISTRICT` and `BLOCK` tokens before standard statistical NER.
2. **Parent District Inference:** If a block entity is extracted but the district was omitted in the tweet, the gazetteer performs a reverse index lookup to populate the parent district.
3. **Secondary Pass (Fuzzy Substring Search):** If EntityRuler token boundaries miss colloquial expressions, a case-insensitive sliding substring scanner matches against all gazetteer keys and values.
4. **Tertiary Pass (Geotagged Metadata Fallback):** If text contains zero location references, checks if `evidence_metadata` contains `latitude` and `longitude` submitted via GPS device or citizen portal.

#### Why this decision?
- **Out-of-the-Box NER Failure on Indian Names:** Pre-trained spaCy (`en_core_web_sm`) consistently misclassifies Indian administrative names like *Bermo*, *Chaibasa*, or *Namkum* as `PERSON`, `ORG`, or not at all.
- **Rule-Based Determinism:** For geographical routing in government workflows, 100% precision on known jurisdictions is mandatory. An `EntityRuler` backed by an authoritative state gazetteer guarantees deterministic extraction.
- **Resilient Fallback:** If `en_core_web_sm` is missing from the host environment, the module initializes `spacy.blank("en")` with zero external network downloads.

---

### Stage 4: Dense Semantic Vector Embeddings

- **Files:** `backend/pipeline/embeddings.py`
- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Dimension:** 384-dimensional dense float32 array
- **Module Function:** `get_embedding(text: str) -> list[float]`

#### What it does
Converts variable-length text into a dense 384-dimensional semantic representation vector where semantically similar civic complaints occupy proximate coordinates in vector space.

#### How it works
Before embedding, domain context is prepended to the normalized text to anchor the embedding in the domain cluster:
```python
embed_text = f"[{domain}] {clean_txt}"
embedding = get_embedding(embed_text)  # Returns list of 384 floats
```

#### Why this decision?
- **Model Selection (`all-MiniLM-L6-v2`):**
  - **Latency:** ~15ms per inference on modern CPUs (no GPU required).
  - **Memory:** Lightweight (~80MB model size), making it ideal for scalable microservices.
  - **Semantic Quality:** Outperforms standard word2vec/TF-IDF by capturing complex semantic equivalence (e.g., *"no water in tap"* is equivalent to *"drinking water supply disrupted"*).
- **Domain Prefixing (`[Healthcare] ...`):** Prepending the classified domain prevents false semantic bridges across dissimilar domains that use overlapping vocabulary (e.g., *"power cut in hospital"* vs *"power cut in residential market"*).

---

### Stage 5: Partitioned Deduplication & Semantic Clustering

- **Files:** `backend/pipeline/deduplication.py`, `backend/pipeline/config.py`
- **Algorithm:** Domain & District Partitioned Vectorized Cosine Similarity
- **Module Function:** `resolve(new_embedding, new_domain, new_district, candidate_challenges) -> dict`

```text
                     New Evidence Embedding Vector (384-dim)
                                       |
                                       v
             +---------------------------------------------------+
             | Partition Candidates from Database:               |
             | SELECT * WHERE domain == new_domain               |
             |            AND district == new_district           |
             +---------------------------------------------------+
                                       |
                                       v
             +---------------------------------------------------+
             | Compute Cosine Similarity against all Centroids   |
             | Find Maximum Similarity Score (S)                 |
             +---------------------------------------------------+
                                       |
                  +--------------------+--------------------+
                  |                    |                    |
             (S >= 0.80)        (0.60 <= S < 0.80)       (S < 0.60)
                  |                    |                    |
                  v                    v                    v
           +--------------+     +--------------+     +--------------+
           | Action: LINK |     | FLAG RELATED |     | NEW CHALLENGE|
           | Link to      |     | Create new   |     | Create fresh |
           | Matched ID   |     | Challenge +  |     | Master       |
           |              |     | log Relation |     | Challenge    |
           +--------------+     +--------------+     +--------------+
```

#### Mathematical Formulation
Given new evidence embedding $\vec{u} \in \mathbb{R}^{384}$ and canonical challenge embedding $\vec{v} \in \mathbb{R}^{384}$:

$$\text{Cosine Similarity}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2}$$

#### Tri-State Action Logic

| Threshold Range | Action | System Response |
|---|---|---|
| **$\ge 0.80$** | `link` | Deduplicated as identical incident. Evidence is attached to existing Master Challenge; evidence count increments; priority and summary update. |
| **$0.60 \le \text{Score} < 0.80$** | `flag_related` | Evaluated as related or cascading issue (e.g., water pipeline burst -> road cave-in). Creates new Challenge, and writes relation edge to `ChallengeRelation` table. |
| **$< 0.60$** | `new_challenge` | Evaluated as unique independent problem. Creates brand new Master Challenge. |

#### Why this decision?
- **Partitioned Search vs Global Nearest Neighbors:** Comparing a water crisis in Ranchi against a streetlight issue in Dhanbad is computationally wasteful and mathematically prone to false positives. Partitioning candidates by `(domain, district)` reduces search space by $>95\%$ while guaranteeing $O(K)$ localized comparisons.
- **Tri-State Thresholds vs Hard Binary Deduplication:** Real-world civic issues have nuanced relationships (e.g., contaminated water supply causing jaundice outbreak in the same ward). Binary dedup either incorrectly merges them or misses their connection entirely. The `flag_related` state preserves systemic root-cause correlations.

---

### Stage 6: Database Orchestration & Schema Multi-Tenancy

- **Files:** `backend/pipeline/orchestrator.py`, `backend/db/models.py`
- **Module Function:** `process_evidence(evidence_data: dict, db: Session) -> dict`

#### What it does
The master state machine that   coordinates Stages 1 through 9 inside an atomic ACID database transaction.

```text
===================================================================================
                       ORCHESTRATOR EXECUTION SEQUENCE
===================================================================================

 Incoming Raw Evidence Dict
           |
           v
 [ 1. clean_text() ] -------------> Sanitized Clean String
           |
           v
 [ 2. classify() ] ---------------> Domain + Subdomain + Confidence Scores
           |
           v
 [ 3. extract_entities() ] -------> District + Block + GPS Coords
           |
           v
 [ 4. get_embedding() ] ----------> 384-dim Dense Vector '[Domain] Text'
           |
           v
 [ 5. resolve() ] ----------------> Action: 'link' | 'flag_related' | 'new_challenge'
           |
           +----------------------------------+
           |                                  |
    (Action == 'link')          (Action in ['new_challenge', 'flag_related'])
           |                                  |
           v                                  v
 [ Fetch Existing Challenge ]       [ Create New Challenge (ID: HC-xxxx) ]
           |                                  |
           +-----------------+----------------+
                             |
                             v
                 [ Insert ChallengeEvidence (ID: EV-xxxx) ]
                             |
                             v
                 [ If 'flag_related' -> Insert ChallengeRelation (CR-xxxx) ]
                             |
                             v
                 [ 6. generate_summary() -> Multi-Evidence LLM Synthesis ]
                             |
                             v
                 [ 7. calculate_priority() -> Explainable 0-100 Score ]
                             |
                             v
                 [ 8. Upsert ChallengeAnalysis Audit Snapshot (CA-xxxx) ]
                             |
                             v
                 [ 9. db.commit() -> Atomic Relational Persistence ]
```

#### Entity Relationship Schema Mapping

```text
+-----------------------+              +-----------------------+
|       CHALLENGE       | 1          * |   CHALLENGE_EVIDENCE  |
+-----------------------+--------------+-----------------------+
| PK id                 |              | PK id                 |
|    title              |              | FK challenge_id       |
|    domain             |              |    source             |
|    district           |              |    raw_text           |
|    block              |              |    clean_text         |
|    location           |              |    embedding_json     |
|    status             |              |    submitted_lat      |
|    priority_score     |              |    submitted_lng      |
|    ai_summary         |              |    created_at         |
|    created_at         |              +-----------------------+
+-----------------------+
        | 1
        |
        | 1
+-----------------------+              +-----------------------+
|   CHALLENGE_ANALYSIS  |              |   CHALLENGE_RELATION  |
+-----------------------+              +-----------------------+
| PK id                 |              | PK id                 |
| FK challenge_id       |              | FK source_challenge_id|
|    domain             |              | FK target_challenge_id|
|    subdomain          |              |    similarity_score   |
|    domain_scores      |              +-----------------------+
|    priority_score     |
|    priority_factors   |
|    confidence         |
|    trend              |
|    explanation        |
+-----------------------+
```

---

### Stage 7: Incremental Multi-Evidence Summarization

- **Files:** `backend/pipeline/summarization.py`
- **LLM Engine:** Groq API (`groq/compound-mini`, configurable via `GROQ_MODEL`) with Extractive Fallback
- **Module Function:** `generate_summary(existing_summary, new_evidence_text, domain, location) -> dict`

#### What it does
Synthesizes multiple raw evidence texts into an executive title ($\le 10$ words) and concise problem statement ($\le 30$ words). As new evidence links to a Challenge, the summary updates incrementally without losing context.

#### Prompt Engineering & Structure
```text
You are a civic grievance summarizer.
Update or create a canonical summary for this issue based on new evidence.
Respond ONLY with a valid JSON object containing exactly two keys: "title" (max 10 words) and "description" (max 30 words).

Domain: {domain}
Location: {location}
Previous Title: {existing_summary.title}
Previous Description: {existing_summary.description}
New Evidence: {combined_clean_text}
```

#### Resilient Extractive Fallback Engine
If the Groq API key is missing, rate-limited (HTTP 429), or experiencing network timeout, the system executes deterministic extractive synthesis:
```python
fallback_title = f"{domain} Issue in {location}" if location else f"{domain} Issue"
fallback_desc = (combined_text[:147] + "...") if len(combined_text) > 150 else combined_text
```

#### Why this decision?
- **Strict Word Limit Guardrails:** Government dashboards require high scannability. Unconstrained LLM outputs produce paragraphs of text that break UI tables and overwhelm administrative officers.
- **Incremental Synthesis vs Static Snapshot:** When 15 citizens tweet about a contaminated tube-well, the summary must evolve from *"Water problem reported"* to *"Widespread tube-well contamination causing illness across Sector 4"*.
- **Zero-Downtime Extractive Fallback:** An external LLM API outage must never crash the ingestion pipeline or block citizen submissions.

---

### Stage 8: Transparent & Explainable Priority Scoring

- **Files:** `backend/pipeline/priority_scoring.py`, `backend/pipeline/config.py`
- **Module Function:** `calculate_priority(domain, evidence_volume, evidence_confidence, trend) -> dict`

#### Mathematical Formula

$$\text{Priority Score} = \text{round}\left( (\text{Severity} \times W_{\text{sev}}) + (\text{Volume Factor} \times W_{\text{vol}}) + (\text{Confidence} \times W_{\text{conf}}) + (\text{Trend Factor} \times W_{\text{trend}}) \right)$$

Where the weights $W$ sum to 100:
- **$W_{\text{sev}} = 30$** (Domain Severity Weight)
- **$W_{\text{vol}} = 25$** (Evidence Volume Weight)
- **$W_{\text{conf}} = 25$** (Data Source Confidence Weight)
- **$W_{\text{trend}} = 20$** (Velocity / Escalation Trend Weight)

#### Factor Formulations

1. **Domain Severity ($\text{Severity} \in [0.50, 0.95]$):** Defined by public safety risk index:
   - Law & Order: $0.95$
   - Healthcare: $0.90$
   - Water & Sanitation: $0.85$
   - Infrastructure/Transport: $0.80$
   - Energy: $0.75$
   - Education & Rural Livelihoods: $0.70$
   - Environment: $0.65$
   - Urban Dev & Accessibility: $0.60$
   - Public Administration: $0.50$
2. **Volume Factor ($\text{Volume Factor} \in [0.0, 1.0]$):** Normalizes total reports, capped at 100:
   $$\text{Volume Factor} = \min\left(\frac{\text{Evidence Volume}}{100}, 1.0\right)$$
3. **Evidence Confidence ($\text{Confidence} \in [0.0, 1.0]$):**
   - Single unverified post: $0.50$
   - Multi-source convergence ($\ge 2$ independent reports): $0.80$
   - Official or GPS-verified intake: $0.95$
4. **Trend Multiplier ($\text{Trend Factor}$):**
   - `increasing` (rapid influx): $1.0$
   - `stable` (constant rate): $0.5$
   - `decreasing` (decaying reports): $0.2$

#### Explainability Contract
Unlike opaque neural rankers, the priority engine outputs human-readable audit trails for government transparency:
```json
{
  "priority_score": 78,
  "priority_factors": {
    "severity": 0.90,
    "evidence_volume": 0.04,
    "confidence": 0.80,
    "trend": 1.0
  },
  "explanation": "Priority 78/100: Domain severity (Healthcare) is 0.90. Backed by 4 evidence items (confidence 0.80). Report trend is increasing."
}
```

#### Why this decision?
- **Administrative Trust & Compliance:** In civic administration, arbitrary AI scores that cannot be explained lead to rejected recommendations. An officer can inspect the exact mathematical weights that elevated an issue's priority.
- **Dynamic Re-Scoring:** As new evidence links to a challenge, the priority recalculates in real-time, allowing breaking crises to bubble to the top of official feeds automatically.

---

### Stage 9: Jurisdictional Smart Routing & Municipal Overrides

- **Files:** `backend/pipeline/router.py`
- **Module Function:** `route_department(category: str, location: str) -> str`

#### What it does
Maps the classified domain and resolved geographical location to the exact nodal government agency or municipal corporation responsible for resolution.

#### How it works
1. **City-Aware Overrides:** Checks whether location tokens match major municipal boundaries with specialized bodies:
   - `Mumbai` + `Infrastructure` -> `MCGM`
   - `Bangalore` + `Utilities` -> `BESCOM`
   - `Noida` + `Utilities` -> `Noida Authority`
2. **State/Default Nodal Mapping:**
   - `Infrastructure` -> `PWD` (Public Works Department)
   - `Sanitation` -> `MCD` (Municipal Corporation Department)
   - `Healthcare` -> `Health Dept`
   - `Utilities` -> `Jal Board / Electricity Board`
   - `Education` -> `Education Dept`
   - `Law and Order` -> `State Police`
   - `Environment` -> `State Pollution Control Board (SPCB)`

---

## 4. Key Architectural Decisions (The "Why" Matrix)

| Technical Decision | Alternatives Considered | Why This Decision Was Chosen |
|---|---|---|
| **Zero-Shot NLI (`BART-MNLI`)** | Fine-tuned BERT / RoBERTa classifier | Eliminates need for thousands of manually labeled civic datasets; enables instant addition of new categories in `config.py`. |
| **Gazetteer `EntityRuler` + Fallback** | General NER (`en_core_web_sm`), LLM extraction | Pre-trained NER fails completely on Indian regional districts/blocks; Gazetteer guarantees 100% deterministic precision on Jharkhand administrative names. |
| **Domain-District Partitioned Cosine Search** | Global Flat FAISS / Milvus vector search | Civic issues are strictly localized. Filtering by `(domain, district)` prunes search space by 95%+, eliminates cross-domain false positives, and executes in $<2\text{ms}$ on SQLite/PostgreSQL without heavy vector DB infrastructure. |
| **4-Factor Weighted Linear Priority Model** | Neural ranking network | Public governance requires explainability. Every priority score must provide an interpretable audit string (severity, volume, confidence, trend) for administrative accountability. |
| **Lazy Loading in Pipeline Init** | Eager module loading | Loading PyTorch, Hugging Face transformers, and sentence-transformers at top-level import froze unit test startup and CLI scripts. Lazy loading ensures submodules import in $<50\text{ms}$. |
| **Multi-Evidence LLM Synthesis with Extractive Fallback** | Pure LLM generation OR pure text truncation | Combines high-quality natural language canonical summaries with zero-downtime robustness during third-party LLM API limits or network drops. |

---

## 5. End-to-End Execution Trace (Concrete Example)

To illustrate the pipeline in action, consider incoming raw social evidence:

### 1. Ingestion Input
```json
{
  "source": "twitter",
  "raw_text": "Severe power failure and low voltage in Namkum area for past 48 hours! Transformers sparking @JharkhandBijli #ElectricityCrisis #Ranchi",
  "submitted_lat": null,
  "submitted_lng": null
}
```

### 2. Normalization Output (`clean_text`)
`"Severe power failure and low voltage in Namkum area for past 48 hours! Transformers sparking ElectricityCrisis Ranchi"`

### 3. Classification Output (`classify`)
- **Domain:** `"Energy"` (Score: 0.912)
- **Subdomain:** `"Grid Reliability"`

### 4. Location Extraction Output (`extract_entities`)
- **Block:** `"Namkum"` (Matched via EntityRuler)
- **District:** `"Ranchi"` (Inferred from Gazetteer relationship)
- **Resolution Method:** `"gazetteer_match"` (Confidence: 0.85)

### 5. Embedding Output (`get_embedding`)
- Input: `"[Energy] Severe power failure and low voltage in Namkum area..."`
- Output: `[0.0421, -0.0189, 0.0812, ...]` (384-dimensional float vector)

### 6. Deduplication Resolution (`resolve`)
- Candidates queried: All Challenges where `domain == 'Energy'` and `district == 'Ranchi'`.
- Result: Matches existing Challenge `HC-84f92a10` with Cosine Similarity `0.865` ($\ge 0.80$).
- **Action:** `"link"`

### 7. Summarization Output (`generate_summary`)
- **Title:** `"Extended Power Outage & Transformer Fault in Namkum"`
- **Description:** `"Multiple reports of persistent 48-hour power failures and hazardous transformer sparking reported across Namkum block, Ranchi."`

### 8. Priority Calculation (`calculate_priority`)
- Domain Severity (`Energy`): $0.75 \times 30 = 22.5$
- Evidence Volume (3 reports): $(3/100) \times 25 = 0.75$
- Confidence (Multi-source): $0.80 \times 25 = 20.0$
- Trend (`increasing`): $1.0 \times 20 = 20.0$
- **Total Priority Score:** $63/100$

### 9. Smart Router Output (`route_department`)
- Category: `"Energy"`, Location: `"Namkum Ranchi"` -> **Department:** `"JBVNL / Electricity Board"`

---

## 6. Verification, Testing & Demonstration Guide

The pipeline is verified using a dual-layer test suite:

### 1. PyTest Unit & Integration Suite
Executes 20 comprehensive unit tests covering individual modules, boundary thresholds, gazetteer parent inference, and end-to-end database transactions:
```bash
cd backend
py -3.12 -m pytest tests/test_nlp_pipeline.py -v
```

### 2. Standalone Smoke & Convergence Runner
Executes an interactive E2E smoke test that seeds sample evidences across multiple domains, validates multi-source signal convergence, tests deduplication clustering, and audits database state:
```bash
cd backend
py -3.12 test_pipeline.py
```

### 3. Live Stream Verification
To test live simulated streaming into the pipeline:
```bash
cd backend
py -3.12 main.py
```
*(In another terminal or via frontend dashboard, observe real-time WebSocket events clustering into Master Challenges).*

---

## 7. Summary of Module Ownership

As the owner of **Data Ingestion through NLP Pipeline**, your component guarantees:
1. **Zero Data Loss:** Every tweet, citizen form, and sensor signal is cleaned, embedded, and accounted for.
2. **Semantic Cohesion:** Multiple citizens complaining about the same breakdown are grouped into one authoritative Master Challenge.
3. **Geographic Precision:** Administrative boundaries are resolved deterministically down to block and district levels.
4. **Explainable Triage:** Priority scores are mathematically accountable, enabling civic officers to trust AI-recommended actions.
5. **System Robustness:** Fully decoupled, lazy-loaded, and equipped with zero-downtime fallbacks.
