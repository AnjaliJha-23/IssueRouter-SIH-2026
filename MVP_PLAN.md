# X-Based AI Grievance Triage Assistant MVP Plan

---

## 1. Problem Framing (Sharp, Non-Generic)

**The Problem:**
Government departments, city administrations, and public institutions are drowning in unstructured complaints. Citizens submit grievances via email, calls, WhatsApp, social media—each with different formats, unclear locations, vague urgency, and no automatic routing. A public works department receives "potholes near the market" but doesn't know which market, doesn't know if it's critical or minor, and has no automated way to assign it. **The pain is not solving issues; it's sorting them.**

**Who Feels It:**
- City administrators: Complaints land everywhere—no single source of truth
- Citizens: No visibility into complaint status or which department owns their issue
- Public workers: They receive poorly categorized tasks with missing context

**Why Current Systems Fail:**
- Manual data entry is slow and error-prone
- Complaints lack structured metadata (location, urgency, category)
- No intelligent routing—a road complaint goes to someone's inbox, not to PWD
- No prioritization—critical safety issues get buried next to cosmetic complaints

**Why AI/ML is Necessary (Not Optional):**
- **Text classification** extracts structured category from free-form text
- **Named Entity Recognition** pulls location and department names automatically
- **Urgency detection** identifies safety-critical complaints without manual review
- **Semantic clustering** groups duplicate/related complaints into single actionable clusters
- **Summarization** standardizes messy citizen language into actionable summaries
- This 5-step pipeline cannot be solved with rules alone—it requires ML

---

## 2. MVP Scope (Hackathon-Optimized)

**What IS Built (Scope):**
1. ✅ Real-time X post ingestion via Tweepy FilteredStream (search for `#complaints_gov`); mock replay for dev/demo
2. ✅ ML pipeline:
   - Zero-shot text classification (6 categories: Infrastructure, Water, Sanitation, Health, Safety, Other) via BART
   - NER for location extraction — spaCy + Indian locality gazetteer
   - Urgency scoring (Low/Medium/High) — hybrid keyword rules + retweet-boost
   - Semantic clustering — sentence-transformers groups similar complaints
   - LLM-based summary generation — Groq API (free tier)
3. ✅ SQLite database storing complaints with metadata
4. ✅ React admin dashboard — dark-themed, priority-ranked cluster cards with expand panels
5. ✅ Department routing suggestion (deterministic rule-based: category → department)
6. ✅ Officer actions: Assign / Resolve / Escalate / Export Brief

**What is EXCLUDED (Out of Scope):**
- ❌ Closed-loop feedback (citizens don't see status updates in this MVP)
- ❌ Multi-language support
- ❌ Real email routing to departments (show suggestions only)
- ❌ User authentication (public dashboard)
- ❌ Fine-tuned models (zero-shot + pre-trained only)
- ❌ Mobile app

**The "Wow Factor" Demo Moment:**
Show judges a real X post like *"Broken streetlight on Main St, happens every night, nobody fixes it!"*
→ System instantly outputs:
- **Category:** Infrastructure | **Urgency:** High | **Department:** PWD | **Location:** Main St
- Clean summary shown in dashboard
- Original X post linked
- Cluster card shows if other similar complaints were grouped together
Repeat with 2–3 more examples in 60 seconds. Judges see: "This could save hours of work per day."

---

## 3. End-to-End User Flow

### User Side (Citizen):
```
1. Citizen posts on X: "Potholes blocking traffic, Area 51, near mosque. Fix ASAP!"
2. Citizen adds hashtag: #complaints_gov
3. Post goes live (no special action needed)
```

### System Processing:
```
4. Tweepy FilteredStream: ingests #complaints_gov posts live
5. For each new post:
   a. Extract text, author, timestamp, retweet count
   b. Run through ML pipeline:
      - BART zero-shot classification → "Infrastructure"
      - spaCy + EntityRuler NER → Extract "Area 51"
      - Urgency scorer → "High" (keywords: "ASAP", "blocking", "traffic")
      - sentence-transformers → cluster with similar pothole complaints
      - Groq LLM → "Dangerous pothole on main road, Area 51 — immediate action needed"
   c. Urgency rank boosted if retweet_count > threshold
   d. Rule-based routing → "Public Works Department"
   e. Store in DB; dashboard cluster card updated
6. Dashboard auto-refreshes (polling or WebSocket)
```

### Admin Side (Government):
```
7. Dashboard loads → See priority-ranked cluster cards (not a raw tweet feed)
8. Click any cluster card → See:
   - Grouped complaints (volume × social reach = rank)
   - Extracted metadata (category, urgency, location, dept)
   - AI-generated one-line officer brief
   - Original X post links
9. Officer actions:
   - Assign / Resolve / Escalate / Export Brief
   - Filter by urgency/category
```

---

## 4. System Architecture (Practical, Not Theoretical)

```
┌─────────────────────────────────────────────────────────────┐
│                    X PUBLIC API                              │
│    Tweepy FilteredStream (#complaints_gov) / mock replay    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI + Python)                      │
│                                                              │
│  1. Ingestion Layer                                          │
│     └─ Tweepy FilteredStream → raw post → DB                │
│                                                              │
│  2. ML Pipeline (Dev 2 — pipeline/ai-migration-fixes)        │
│     ├─ Classification: BART zero-shot (bart-large-mnli)     │
│     ├─ NER: spaCy en_core_web_sm + EntityRuler gazetteer    │
│     ├─ Urgency: Hybrid keyword rules + retweet-boost        │
│     ├─ Clustering: sentence-transformers all-MiniLM-L6-v2   │
│     └─ Summarisation: Groq API (llama3-8b-8192)             │
│                                                              │
│  3. Routing Logic (Deterministic Rules)                      │
│     └─ category → department mapping                         │
│                                                              │
│  4. REST API Endpoints                                       │
│     ├─ GET /api/complaints (all, filtered)                  │
│     ├─ GET /api/complaints/:id (detail)                     │
│     ├─ POST /api/complaints/:id/status (mark processed)     │
│     └─ GET /api/stats (dashboard metrics)                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  SQLite Database     │
        │                      │
        │ Table: complaints    │
        │ - id                 │
        │ - x_post_id          │
        │ - text               │
        │ - category           │
        │ - location           │
        │ - urgency            │
        │ - retweet_count      │
        │ - cluster_id         │
        │ - department         │
        │ - summary            │
        │ - confidence_score   │
        │ - priority_rank      │
        │ - created_at         │
        └──────────────────────┘
                   ▲
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
   ┌─────────────┐   ┌──────────────────┐
   │  React SPA  │   │  WebSocket Feed  │
   │ (Dashboard) │   │  (Live updates)  │
   │ Dark theme  │   │                  │
   │ Cluster     │   │                  │
   │ Cards +     │   │                  │
   │ Expand Panel│   │                  │
   └─────────────┘   └──────────────────┘
```

**Key Flows:**
1. **Ingestion:** Tweepy FilteredStream → FastAPI → Store raw post in DB
2. **Processing:** Background pipeline runs BART → spaCy → urgency → cluster → Groq → update DB
3. **Display:** React fetches from API → Dashboard renders ranked cluster cards
4. **Live Updates:** WebSocket/polling pushes new clusters to open dashboards

---

## 5. AI/ML Design (Confirmed Stack)

### A. Text Classification (Category Assignment)

**Problem:** Classify "Potholes on Main Street" → Infrastructure

**Model Choice (confirmed):**
- **Model:** `facebook/bart-large-mnli` via Hugging Face zero-shot pipeline
- **Why:** No training data required, strong out-of-the-box accuracy for civic complaint categories, CPU-friendly for demo

**Implementation:**
```python
from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

candidate_labels = ["Infrastructure", "Water", "Sanitation", "Health", "Safety", "Other"]

result = classifier(complaint_text, candidate_labels)
category = result["labels"][0]          # top prediction
confidence = result["scores"][0]        # confidence score
```

**Confidence Threshold:** Only show category if confidence > 0.6; otherwise flag as "Unclear / Manual Review"

---

### B. Named Entity Recognition (Location Extraction)

**Problem:** Extract "Main Street" or "Sector 5" from "Potholes on Main Street near mosque" — including informal Indian locality names

**Model Choice (confirmed):**
- **Library:** spaCy `en_core_web_sm` + custom `EntityRuler` with an Indian locality gazetteer
- **Why:** Fast, zero GPU, custom gazetteer handles informal place names that generic NER misses (e.g., "Gurugram", "Sector 56", landmark names)

**Implementation:**
```python
import spacy
from spacy.pipeline import EntityRuler

nlp = spacy.load("en_core_web_sm")

# Custom gazetteer for Indian localities
ruler = nlp.add_pipe("entity_ruler", before="ner")
patterns = [
    {"label": "GPE", "pattern": "Gurugram"},
    {"label": "GPE", "pattern": "Sector 56"},
    {"label": "LOC", "pattern": "near the mosque"},
    # ... extend with local landmark patterns
]
ruler.add_patterns(patterns)

doc = nlp("Potholes near the mosque in Sector 56")
locations = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]
# Output: ["the mosque", "Sector 56"]
```

**Fallback:** Regex for numbered sectors (`Sector \d+`) and street patterns (`\d+ .*?(Street|Road|Marg)`)

---

### C. Urgency Scoring (Hybrid: Rules + Retweet Boost)

**Problem:** Classify urgency and amplify based on social reach

**Approach (confirmed): Hybrid keyword rules + retweet-count boost**

```python
HIGH_KEYWORDS = {"fatal", "death", "injury", "emergency", "asap", "danger", "critical",
                 "blocked", "flooding", "accident", "immediate", "please fix", "no water"}
MEDIUM_KEYWORDS = {"broken", "issue", "problem", "not working", "needed", "days"}

RETWEET_BOOST_THRESHOLD = 50   # retweets above this → bump urgency one level

def compute_urgency(text: str, retweet_count: int) -> str:
    text_lower = text.lower()
    if any(kw in text_lower for kw in HIGH_KEYWORDS):
        base = "High"
    elif any(kw in text_lower for kw in MEDIUM_KEYWORDS):
        base = "Medium"
    else:
        base = "Low"

    # Retweet boost: social signal amplifies priority
    if retweet_count >= RETWEET_BOOST_THRESHOLD:
        if base == "Low":
            base = "Medium"
        elif base == "Medium":
            base = "High"

    return base
```

**Priority Rank Formula:**
```python
priority_score = complaint_volume_in_cluster * (1 + log(1 + total_retweets))
```
Cluster cards sorted descending by priority_score → officers always see highest-impact issues first.

---

### D. Semantic Clustering

**Problem:** Group "Pothole on MG Road" and "Bad road near MG Road market" into one cluster rather than surfacing as separate complaints

**Model Choice (confirmed):** `sentence-transformers/all-MiniLM-L6-v2`

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def cluster_complaints(texts: list[str], threshold: float = 0.75) -> list[int]:
    embeddings = model.encode(texts)
    sim_matrix = cosine_similarity(embeddings)
    # Simple greedy clustering: assign to existing cluster if sim > threshold
    clusters = [-1] * len(texts)
    cluster_id = 0
    for i in range(len(texts)):
        if clusters[i] == -1:
            clusters[i] = cluster_id
            for j in range(i + 1, len(texts)):
                if sim_matrix[i][j] >= threshold:
                    clusters[j] = cluster_id
            cluster_id += 1
    return clusters
```

---

### E. Summarisation (LLM — Groq API)

**Model Choice (confirmed):** Groq API, `llama3-8b-8192` — free tier, no credit card required

```python
from groq import Groq

client = Groq()  # reads GROQ_API_KEY from env

def summarise_cluster(complaints: list[str]) -> str:
    combined = "\n".join(f"- {c}" for c in complaints)
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a government intake clerk. Given a cluster of citizen complaints, "
                    "write a single clear sentence for a government officer. "
                    "Include: issue type, location (if available), severity, and recommended action. "
                    "Be direct and professional. No preamble."
                )
            },
            {"role": "user", "content": combined}
        ],
        max_tokens=120
    )
    return response.choices[0].message.content.strip()
```

---

## 6. Data Strategy

### Data Requirements:

**For Inference (Real X Posts):**
- Raw X post data: `{"id", "text", "author", "created_at", "retweet_count", "url"}`

**No training data required** — BART zero-shot classification eliminates the need to collect and label training samples for classification.

### Mock Data (For Dev / Demo Replay):

```json
[
  {
    "text": "Pothole on MG Road near mosque, traffic accident risk! #complaints_gov",
    "retweet_count": 87,
    "category": "Infrastructure",
    "location": "MG Road",
    "urgency": "High",
    "department": "Public Works Department"
  },
  {
    "text": "Water tap not working in Sector 56 for 3 days #complaints_gov",
    "retweet_count": 12,
    "category": "Water",
    "location": "Sector 56",
    "urgency": "Medium",
    "department": "Water Works"
  },
  {
    "text": "Streetlight broken outside Govt School, Gurugram #complaints_gov",
    "retweet_count": 62,
    "category": "Infrastructure",
    "location": "Gurugram",
    "urgency": "High",
    "department": "Public Works Department"
  }
]
```

---

## 7. Tech Stack (Confirmed)

| Component | Choice | Why |
|-----------|--------|-----|
| **Backend Framework** | FastAPI (Python) | Fast, async, built-in API docs, ideal for ML pipelines |
| **Classification** | `facebook/bart-large-mnli` (zero-shot) | No training data needed; strong civic domain performance |
| **NER** | spaCy `en_core_web_sm` + custom EntityRuler | Fast, Indian-locale aware via custom gazetteer |
| **Urgency Scoring** | Hybrid keyword rules + retweet-count boost | Interpretable, fast, socially amplified |
| **Clustering** | `sentence-transformers/all-MiniLM-L6-v2` | Lightweight, CPU-friendly, strong semantic similarity |
| **LLM Summarisation** | Groq API — `llama3-8b-8192` | Free tier, no card, ~0.5s latency |
| **Database** | SQLite (MVP) → PostgreSQL (production) | Zero setup for hackathon |
| **Frontend** | React 18, Tailwind CSS, shadcn/ui, Recharts | Dark-themed, cluster card layout |
| **X Ingestion** | Tweepy FilteredStream / mock replay | Standard; swap one flag for live vs. mock |
| **Job Scheduling** | APScheduler (Python) | Lightweight background ingestion |
| **Real-Time Updates** | WebSocket / polling | Live dashboard updates |
| **Hosting (Optional)** | Vercel (frontend) + Railway/Render (backend) | Free tier, simple deploy |

**Why NOT:**
- ❌ OpenAI / Claude for summarisation — paid, card required; Groq free tier is sufficient
- ❌ scikit-learn classifier — needs labelled training data; BART zero-shot eliminates this
- ❌ Django: Too heavy for MVP
- ❌ MongoDB: SQL better for structured complaints data

---

## 8. Step-by-Step Build Plan

### Phase 1: Foundation (Hours 1–4) — **Parallel**

**Task 1a (Backend — Om/Dev 2):** FastAPI project, SQLite schema, X ingestion
- Create FastAPI project structure
- Define SQLite schema (add `retweet_count`, `cluster_id`, `priority_rank` fields)
- Write Tweepy FilteredStream client + mock replay mode
- `GET /api/complaints` endpoint

**Task 1b (Frontend Dev):** React dashboard skeleton
- Dark-themed layout: Header + cluster card list + expand panel
- Mock data cards showing priority rank, category, urgency badge, location
- Routing: list view → detail view

**Deliverable:** Backend returns mock complaints; frontend displays ranked cluster cards.

---

### Phase 2: ML Pipeline (Hours 5–8) — **Dev 2 owned (branch: pipeline/ai-migration-fixes)**

**Status: ✅ Smoke-tested — all models load and process correctly**

- BART zero-shot classification ✅
- spaCy + EntityRuler NER ✅
- Hybrid urgency scorer ✅
- sentence-transformers clustering ✅
- Groq summarisation ✅
- `/api/process` endpoint: raw text + retweet_count → structured JSON

**Deliverable:** Hit `/api/process` with raw X post → get back `{category, location, urgency, cluster_id, summary, priority_rank}`

---

### Phase 3: Integration (Hours 9–12) — **Parallel**

**Task 3a (Backend):** Wire pipeline to ingestion
- Ingestion job calls `/api/process` per post, stores results in DB
- Filtering endpoints: `/api/complaints?category=Infrastructure&urgency=High`
- Cluster aggregation endpoint: `/api/clusters` (ranked by priority score)

**Task 3b (Frontend):** Interactive dashboard
- Real-time cluster cards ranked by priority_score
- Expand panel: grouped complaint tweets + officer brief + action buttons
- Filters (category, urgency, department)
- Assign / Resolve / Escalate / Export Brief actions

**Deliverable:** Full end-to-end: X post → pipeline → ranked cluster card in dashboard

---

### Phase 4: Polish & Demo (Hours 13–24) — **Buffer**

- Test with real X posts (mock replay if quota tight)
- Tune EntityRuler gazetteer for Gurugram/local landmarks
- Add metrics panel: total clusters, urgency distribution, avg processing time
- Write demo script; prepare 3–4 example posts
- Deploy (Vercel + Railway)
- Merge `pipeline/ai-migration-fixes` → integration branch after stash resolution

---

### Parallelization:
- **Om (Dev 2):** Pipeline code (done ✅) → Phase 3a integration → stash resolution → merge
- **Frontend Dev:** Phase 1b → Phase 3b → polish
- **Others:** Mock data prep, NER gazetteer expansion, demo script, testing

---

## 9. Demo Script (CRITICAL)

### Setup:
- Mock replay loaded with 10–15 pre-processed complaints
- Dashboard open (dark theme, cluster cards visible)
- Terminal showing live API calls on second screen

### Demo Flow (5 minutes):

**Intro (30 sec):**
> "Governments get thousands of complaints on X every day — potholes, water cuts, broken lights. The problem: no one systematically reads them. We built a system that ingests complaints automatically, runs them through an AI pipeline, and surfaces ranked action briefs to officers. Let me show you."

**Demo Part 1: Ingestion (1 min):**
> "I'll post a complaint on X right now with #complaints_gov..."
- Post: "Broken streetlight on MG Road. Kids can't walk to school safely. PLEASE FIX!"
- Wait ~10 seconds → cluster card appears or updates in dashboard

**Demo Part 2: AI Pipeline Output (2 min):**
> "Watch what the system extracted automatically..."
- Click cluster card → expand panel
- Show:
  - **Category:** Infrastructure (BART zero-shot)
  - **Location:** MG Road (spaCy + EntityRuler)
  - **Urgency:** High (keyword: "PLEASE FIX" + retweet boost)
  - **Department:** Public Works Department
  - **Officer Brief:** "Streetlight outage on MG Road near school — immediate safety risk, assign to PWD"
  - **Cluster:** 2 similar complaints grouped → "12 retweets combined"

**Demo Part 3: Prioritization (1.5 min):**
> "Officers don't see a raw tweet feed — they see ranked priorities."
- Show cluster #1 (high retweet + high urgency)
- Show cluster #2 (lower reach, Medium urgency)
- Filter by "High Urgency" → 3 clusters
- Click Assign on cluster #1 → status updates

**Demo Part 4: Value (30 sec):**
> "Instead of a clerk manually reading 200 tweets and guessing which department, the system ranks the top issues in under 2 seconds. Government can now focus on fixing problems, not finding them."

### Key Points:
- ✅ Show **ranked cluster cards**, not raw tweets — this is the differentiator
- ✅ Show **retweet-boost effect** (explain why #1 card is #1)
- ✅ Show **all 5 pipeline steps** working
- ✅ Show **speed** (<2 sec end-to-end)
- ✅ Have a "low confidence" example ready — show "Manual Review" flag honestly

---

## 10. Evaluation & Metrics

### During Development:

| Metric | Target | How to Measure |
|--------|--------|-----------------|
| **Classification Accuracy** | >85% on 30 test complaints | Manual spot-check vs. BART output |
| **Location Extraction** | >75% on Indian locality test set | Spot-check 10 extractions with EntityRuler |
| **Urgency Detection** | >80% on test set | Compare rule output vs. manual label |
| **Clustering Quality** | Similar complaints grouped | Visual inspection of 3–4 cluster groups |
| **Summarization Quality** | Clear, actionable, <2 sentences | Read 5 briefs: "Would an officer act on this?" |
| **End-to-End Latency** | <5 sec from post to dashboard | Time from ingestion to DB write |

### For Demo Judges:

**They'll care about:**
1. **Accuracy:** Correct category + location? (Spot-check 3 examples live)
2. **Speed:** <5 sec end-to-end
3. **Prioritization:** Does the ranking make sense?
4. **Clarity:** Officer briefs readable and actionable?
5. **Real Problem:** Manual triage is slow — does this solve it?

### Metrics Panel (Dashboard):
```
Total Clusters: 12      Total Complaints: 47
├─ By Urgency:    High (5 clusters), Medium (4), Low (3)
├─ By Category:   Infrastructure (6), Water (3), Health (2), Other (1)
├─ By Department: PWD (6), Water Works (3), Health Dept (2), Unknown (1)
└─ Avg Processing Time: 1.8 sec
```

---

## 11. Stretch Features (If Time Permits)

### Stretch 1: Department Email Routing
- SMTP auto-email to department inboxes on "Assign" click
- Template: `[URGENT] Pothole cluster (5 complaints) on MG Road — #complaints_gov`
- **Time:** +2 hours

### Stretch 2: Citizen Feedback Loop
- QR code on dashboard → citizens rate if issue resolved
- Feedback stored → future prioritization weight
- **Time:** +3 hours

### Stretch 3: Multi-Language Support
- `langdetect` → Google Translate API → process in English → return in original
- **Time:** +2 hours

### Stretch 4: Geospatial Mapping
- Folium/Mapbox: plot all cluster centroids
- Heatmap by urgency
- **Time:** +3 hours

### Stretch 5: Hindi/Regional Complaint Support
- Extend EntityRuler gazetteer with Hindi transliterations of localities
- **Time:** +2 hours

---

## 12. Risks & Smart Shortcuts

### Risk 1: X API Rate Limits
- **Problem:** X API free tier burns quota fast
- **Smart Shortcut:** Use mock replay for demo; 1–2 real posts if quota allows
- **Solution:** Pre-fetch 20 posts before demo; use replay mode (one flag in ingestion)

### Risk 2: BART is Slow on CPU
- **Problem:** `bart-large-mnli` can take 3–5 sec per post on CPU
- **Smart Shortcut:** Pre-compute classifications on all mock data before demo
- **Solution:** Cache predictions in DB; pipeline runs async in background

### Risk 3: NER Misses Informal Indian Locations
- **Problem:** spaCy misses "near the mosque", "Sector 56 chowk"
- **Smart Shortcut:** EntityRuler gazetteer covers known locals; accept ~70% extraction rate
- **Solution:** "Location: unclear" shown honestly; manual review flag triggered

### Risk 4: Groq API Down / Rate Limited
- **Problem:** Groq free tier has per-minute limits
- **Smart Shortcut:** Cache summaries in DB; regenerate only on new clusters
- **Solution:** Fallback to extractive summary (first + last sentence) if Groq unavailable

### Risk 5: Git / Branch Merge Conflicts
- **Problem:** pipeline/ai-migration-fixes not merged; stash issue on main
- **Smart Shortcut:** Resolve stash first (see git stash resolution guide); create PR to integration branch
- **Solution:** Each dev works on named branches; merge sequentially via PRs to avoid conflicts

### Risk 6: Judges Test Edge Cases
- **Problem:** Sarcastic or unrelated tweet with hashtag
- **Smart Shortcut:** Show confidence score; anything <0.6 flagged "Manual Review"
- **Solution:** Don't promise 100% accuracy — "captures 85%+ of real-world complaints"

### Risk 7: Frontend Not Ready
- **Problem:** ML pipeline done but frontend still building
- **Smart Shortcut:** Demo with `/api/clusters` JSON directly if needed; frontend is visual polish
- **Solution:** API-first development; frontend swaps mock → real data with one URL change

### Smart Shortcut: Deterministic Department Routing
```python
category_to_dept = {
    "Infrastructure": "Public Works Department",
    "Water": "Water Works",
    "Health": "Health Ministry",
    "Sanitation": "Municipal Corporation",
    "Safety": "Police / Disaster Management",
    "Other": "District Collector Office"
}
```

---

## Build Checklist

- [x] Dev 2 pipeline code complete (branch: pipeline/ai-migration-fixes)
- [x] Smoke test: all models load and process correctly
- [ ] Resolve git stash issue on main branch
- [ ] Merge pipeline branch → integration branch (PR)
- [ ] Backend: FastAPI project + SQLite schema (add retweet_count, cluster_id, priority_rank)
- [ ] X API: Tweepy FilteredStream + mock replay mode
- [ ] Backend: `/api/complaints`, `/api/process`, `/api/clusters` endpoints
- [ ] Frontend: Dark-themed dashboard skeleton + cluster card component
- [ ] Integration: Wire ML pipeline to ingestion job
- [ ] Frontend: Ranked cluster cards, expand panel, action buttons, filters
- [ ] Testing: End-to-end with 10–15 test complaints
- [ ] Polish: Metrics panel, confidence badges, "Manual Review" flag
- [ ] Demo: Prepare 3–4 example X posts, write script, test mock replay
- [ ] Deployment: Vercel (frontend) + Railway (backend)
- [ ] Documentation: README updated ✅

---

## Success Criteria

✅ **System works end-to-end:** X post → pipeline → ranked cluster card in dashboard (<5 sec)
✅ **ML accuracy:** >80% on category classification (BART zero-shot)
✅ **Clustering works:** Similar complaints grouped; priority rank visible and logical
✅ **Dashboard is usable:** Ranked cards, expand panel, officer actions functional
✅ **Demo is smooth:** 3 examples without errors, judges understand the value
✅ **Code is clean:** Each module (ingest, classify, NER, cluster, summarise) independently testable

**Good luck! Ship fast, demo fearlessly. 🚀**
