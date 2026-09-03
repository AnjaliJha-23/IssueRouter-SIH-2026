# SIC Portal — Societal Innovation Collaboration Portal

**Smart India Hackathon 2026 · SIH26043 · Government of Jharkhand**  
**Team Convergence**  
**Hero Theme**: MedTech / BioTech / HealthTech

> **From Problem Discovery to Measurable Impact**: A unified societal challenge platform that turns multi-source citizen and social signals into verified, university-led, industry-backed innovation projects tracked end-to-end by the government.

---

## 1. Executive Direction

The **IssueRouter** concept is evolved, not discarded. Its core strength—discovering and semantically clustering public complaints and social signals (historically from Twitter/X) geographically and analytically—is preserved and extended. SIC Portal adds a structured intake channel for direct citizen and community submissions. 

**This is not two separate complaint systems.** It is one unified societal challenge platform:
1. **Multi-Source Intake**: Ingests both Twitter/X public social signals and direct citizen web form submissions into a single pipeline.
2. **Unified Semantic Clustering**: A shared deduplication and clustering engine ensures signals from any source merge into a single **Master Societal Challenge** rather than creating duplicative tickets.
3. **Government Verification**: Authorized officials review candidate challenges, evaluate evidence confidence and trend metrics, and verify them.
4. **Smart Router**: Our core differentiator. A multi-target, explainable, weighted deterministic scoring engine that matches challenges to Government Departments, Universities, Faculty/Research Groups, Industry/CSR Partners, and Pilot Locations.
5. **Collaborative Innovation**: Universities submit solution proposals and assemble multidisciplinary teams; Industry/CSR partners pledge mentorship, technology, funding, or pilot support.
6. **Shared Project Workspace**: Government, universities, and industry collaborate in one unified workspace with role-based views through prototype, testing, pilot deployment, and community impact measurement.

*Source of Truth Blueprint*: [IssueRouter_SIH_Final_Implementation_Blueprint.md](IssueRouter_SIH_Final_Implementation_Blueprint.md)

---

## 2. Core Principles & Architecture Decisions

| Principle | Decision |
|---|---|
| **Intake** | Twitter/X public signals + direct citizen web forms + future NGO/Panchayat/Govt intake |
| **Clustering** | One unified semantic clustering and deduplication layer across all sources |
| **Source of Truth** | **One Master Societal Challenge** per underlying problem; multiple Evidence items link to it |
| **Dashboards** | Role-based and organization-scoped portals on a shared application codebase, not separate apps |
| **University Model** | One University Portal; each institution sees its own matched challenges, faculty, and proposals |
| **Industry Model** | One Industry Portal; companies discover relevant collaboration opportunities and track pledges |
| **Collaboration** | One shared **Innovation Project Workspace** with role-based permissions |
| **AI Stance** | Assistive, explainable, human-reviewable; deterministic scoring over opaque black boxes |
| **SIH Focus** | Explainable Smart Router + multi-source discovery + HealthTech hero use cases + measurable impact |

---

## 3. System Architecture & End-to-End Flow

```
   ┌───────────────────────┐        ┌─────────────────────────────┐
   │ Twitter/X Signals     │        │ Direct Citizen Submission   │
   │ (Discovery/Scraped)   │        │ (Web Form + Geo + Media)    │
   └──────────┬────────────┘        └──────────────┬──────────────┘
              │                                    │
              └──────────────────┬─────────────────┘
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │       Unified Ingestion & Normalization         │
         │ (BART Zero-Shot Classifier + spaCy Geo Gazette) │
         └───────────────────────┬─────────────────────────┘
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │ Semantic Clustering & Deduplication (MiniLM-L6) │
         │   Maps incoming evidence to Master Challenges   │
         └───────────────────────┬─────────────────────────┘
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │           Master Societal Challenge             │
         │  (Priority Score, Evidence Confidence, Trend)   │
         └───────────────────────┬─────────────────────────┘
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │   Government Command Center: Review & Verify    │
         └───────────────────────┬─────────────────────────┘
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │         Explainable Smart Router Match          │
         │ • Dept  • University  • Faculty  • Industry/CSR │
         └───────────────────────┬─────────────────────────┘
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │   University Accept ──▶ Proposal & Team Formed  │
         │   Industry Accept   ──▶ Support Pledged (Tech)  │
         └───────────────────────┬─────────────────────────┘
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │      Shared Innovation Project Workspace        │
         │ Milestones ──▶ Prototype ──▶ Testing ──▶ Pilot  │
         └───────────────────────┬─────────────────────────┘
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │     Citizen Feedback & Verified Impact KPIs     │
         └─────────────────────────────────────────────────┘
```

---

## 4. Stakeholder Portals

Rather than fragmented codebases, the system delivers tailored, organization-scoped experiences:

| Actor / Portal | Primary Capabilities |
|---|---|
| **Citizen**<br>*(Citizen Portal)* | Submit societal challenges with district/block, description, and photos; view submitted reports; track project progress and provide community validation feedback. |
| **Government**<br>*(Command Center)* | Triage incoming challenges with real-time KPIs; review evidence breakdown and AI rationale; verify challenges; execute Smart Routing; track statewide project progress and impact. |
| **University**<br>*(University Portal)* | View incoming matched challenges with transparent match reasons; accept/decline; form multidisciplinary faculty/student teams; submit solution proposals. |
| **Industry / CSR**<br>*(Industry Portal)* | Discover high-relevance collaboration opportunities; pledge mentorship, technology, funding/CSR, equipment, pilot support, or co-development. |
| **Shared Collaboration**<br>*(Innovation Workspace)* | Multi-stakeholder project workspace covering Overview, Team, Milestones, Deliverables, Prototype, Testing, Pilot, Communication, Impact, and Governance. |

---

## 5. Smart Router — Core Differentiator

The Smart Router does not merely assign a category; it finds the optimal ecosystem participants and explains **why** they are a match.

It evaluates 5 targets using transparent, weighted deterministic scoring:
- **Government Department**: Domain, jurisdiction, severity, location, department mandate.
- **University**: Domain expertise (40%), location relevance (20%), capacity (20%), relevant past performance (20%).
- **Faculty / Research Group**: Academic specialization, availability/capacity, research areas, and relevant labs.
- **Industry / Startup / CSR**: Technology capability, domain alignment, CSR focus, funding capacity, and implementation presence.
- **Pilot Location**: Geographic need, infrastructure readiness, population density, and challenge severity.

---

## 6. Tech Stack

### Frontend
- **Framework**: React 19 SPA built with Vite
- **Routing**: React Router v7
- **Styling**: Tailwind CSS v4
- **State Management**: React Context (`IssueContext`, `AuthContext`, `ThemeContext`)
- **Visualizations & Maps**: Recharts, Leaflet with custom GIS layers
- **Key Views**: `GovDashboard` (Command Center), `CitizenDashboard`, `OrgDashboard`, `ProjectWorkspace`, `Maps`, `Progress`

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: SQLite / PostgreSQL via SQLAlchemy ORM
- **Validation**: Pydantic v2 schemas
- **Architecture**: Modular routers (`challenges`, `smart_router`, `stats`, `auth`)

### AI & NLP Pipeline
- **Zero-Shot Classification**: `facebook/bart-large-mnli` tuned across 10 societal domains
- **Location Extraction**: spaCy with custom EntityRuler and Jharkhand gazetteer (districts and blocks)
- **Semantic Deduplication**: `sentence-transformers` (`all-MiniLM-L6-v2`) cosine similarity clustering
- **Summarization & Insights**: Fast LLM inference (Groq / Hugging Face) for canonical challenge synthesis
- **Scoring**: Weighted multi-factor deterministic algorithms for priority and routing

---

## 7. Repository Structure

```
sic-portal/
├── backend/
│   ├── api/                 # FastAPI router endpoints (challenges, smart_router, stats)
│   ├── cache/               # Caching layer for fast response times
│   ├── db/                  # SQLAlchemy models, schemas, and database session
│   ├── ingestion/           # Twitter/X scraper adapter + citizen intake handlers
│   ├── pipeline/            # AI classification, deduplication, scoring, summarization
│   ├── issueRouter.db       # SQLite local database instance
│   ├── main.py              # Application entrypoint & CORS middleware
│   ├── requirements.txt     # Python dependencies
│   ├── seed_mock_data.py    # Seed generator for Jharkhand institutions & challenges
│   └── test_pipeline.py     # End-to-end pipeline test suite
├── frontend/
│   ├── public/              # Static assets and icons
│   ├── src/
│   │   ├── api/             # API client and endpoints integration
│   │   ├── components/      # UI components (ChallengeCard, FilterBar, RoutingModal, Drawer)
│   │   ├── context/         # Auth, Issue, and Theme context providers
│   │   ├── data/            # Static Jharkhand geography, mock organizations, seed definitions
│   │   ├── pages/           # GovDashboard, CitizenDashboard, OrgDashboard, Maps, Progress
│   │   ├── App.jsx          # Route declarations
│   │   └── main.jsx         # React root
│   ├── package.json         # Node.js dependencies (React 19, Vite, Tailwind CSS v4)
│   └── vite.config.js       # Vite build configuration
├── docs/
│   ├── ARCHITECTURE.md      # Detailed system architecture, data models, and Smart Router
│   ├── MVP_PLAN.md          # Master product plan, scoping, and stakeholder flows
│   ├── GLOSSARY.md          # Definitions of all entities, fields, and terms
│   ├── ROADMAP.md           # 9-stage build plan, milestones, and Definition of Done
│   ├── CONTRIBUTING.md      # Team git workflow, module branches, and review rules
│   └── (shared project documentation is listed below)
├── AGENTS.md                # GitHub workflow and agent operating manual
└── README.md                # Project overview and entry point
```

---

## 8. Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python seed_mock_data.py
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 9. Hero Demonstration Strategy (HealthTech Focus)

To highlight the SIH MedTech/BioTech/HealthTech theme, SIC Portal features three end-to-end Jharkhand scenarios:
1. **Rural Telemedicine Access**: Discovery of access barriers in remote blocks -> AI clustering -> Verification -> Smart Routing to RIMS Ranchi + HealthTech industry partner -> Project formation -> Pilot deployment -> Community feedback.
2. **Primary Health Center (PHC) Diagnostic Gaps**: Multi-source social + direct complaints clustered into an urgent regional challenge -> Smart Routing to biomedical engineering university + CSR diagnostic lab.
3. **Waterborne Disease Early Signal**: Social signals and citizen water quality reports clustered into an emerging outbreak alert -> Accelerated routing to Public Health Dept + BIT Mesra Environmental Lab.

---

## 10. Document Map

| Document | Purpose | Read When |
|---|---|---|
| [IssueRouter_SIH_Final_Implementation_Blueprint.md](IssueRouter_SIH_Final_Implementation_Blueprint.md) | **Single Source of Truth** for architecture, workflow, and specs | Grounding high-level design decisions |
| [docs/MVP_PLAN.md](docs/MVP_PLAN.md) | MVP workflow, scope, state model, and Definition of Done | Understanding requirements and MVP boundaries |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture, data model, Smart Router, and APIs | Implementing backend and frontend modules |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Authoritative terms, entities, and statuses | Aligning code, PRs, and product language |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Workflow implementation phases and demo milestones | Checking progress and exit criteria |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Git workflow, module branches, and review rules | Preparing commits and pull requests |
| [AGENTS.md](AGENTS.md) | GitHub workflow operating manual | Running git operations, branching, and reviews |

---

*Team Convergence · SIH 2026 · Problem Statement SIH26043*
