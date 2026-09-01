# Glossary — SIC Portal

Alphabetical. If a term used in standup, code review, or the pitch isn't here, add it — this file exists so nobody has to ask "wait, what's a Proposal vs a Project again" twice.

---

**Challenge**
A societal problem submitted by a citizen, community organization, PRI, ULB, or government department. The atomic unit the whole platform routes around. Has a description, district, optional photo, a classified `domain`, a `priority_score`, and a `status`.

**CSR Organization**
Corporate Social Responsibility arm of an industry partner (e.g. Tata Steel Foundation, JSPL CSR — used as reference points for seed data). Functions the same as an `IndustryPartner` in the data model but flagged separately for reporting.

**Deduplication (Dedup)**
The process of detecting that a newly submitted Challenge is semantically the same underlying issue as one already in the system, so it's merged/clustered rather than treated as a fresh, separately-routed problem. Implemented via `sentence-transformers` (`all-MiniLM-L6-v2`) embeddings + cosine similarity. Ported directly from IssueRouter.

**Discipline Tag**
A label attached to a `University` describing an academic/research strength (e.g. "agriculture", "urban development", "energy"). Used as the basis for university matching. Not the same as `Domain` — a Domain describes a Challenge, a Discipline Tag describes a University's capability; matching compares the two.

**Domain**
One of the 10 thematic categories a Challenge is classified into: education, agriculture, healthcare, water resources, environment, energy, urban development, accessibility, public administration, rural livelihoods. Assigned by the AI Intake Layer via zero-shot classification.

**Faculty**
A university staff member who reviews Challenges routed to their institution and forms a `Team` around one they choose to pursue. Owns the Proposal on behalf of their institution.

**Government Analytics Layer**
The dashboard and underlying aggregation logic that gives Government users a real-time, state-wide view: challenge volume, domain/district distribution, university and industry engagement, and pipeline progress. Read-only for this stakeholder — Government doesn't act on individual Challenges, it observes the system.

**Industry Partner**
A startup, MSME, research lab, or CSR organization that browses open `Proposal`s and pledges support (funding, mentorship, or deployment help). Distinct from a `University` — industry partners don't originate Proposals, they back them.

**IssueRouter**
Team Convergence's prior project (3rd place, HNC 3.0): an AI-powered civic complaint triage system that classified, deduplicated, and prioritized citizen complaints from X (Twitter) and routed them to government departments. SIC Portal reuses its classification/dedup/prioritization engine directly. See `README.md §5` for exactly what's reused vs. new.

**Notification**
An in-app (not SMS/email — that's roadmapped, not built) alert that fires when something relevant happens to a stakeholder: a citizen's Challenge gets picked up, a university gets a new routed Challenge, an industry partner sees a new open Proposal.

**Pledge**
An Industry Partner's commitment of support (funding, mentorship, deployment help) toward a specific Proposal. The mechanism through which the Industry Partnership Layer connects to a university's work.

**Priority Score**
A numeric score assigned to a Challenge at intake, based on volume (how many similar/duplicate submissions exist) and severity signals. Determines how urgently it should be surfaced. Formula ported from IssueRouter, reweighted from "urgency + social reach" to "challenge volume + severity."

**Project**
What a `Proposal` becomes once it's accepted and moves into execution. Tracked through a single `status` field in the MVP (not full milestone management — that's a documented simplification): `submitted → team formed → prototype → testing → deployed`.

**Proposal**
A solution write-up submitted by a university `Team` in response to a routed `Challenge`. What Industry Partners browse and pledge support toward. Becomes a `Project` once accepted.

**Role Selector**
The MVP's access-control mechanism: a simple choice of citizen / university / industry / government that determines which dashboard a user sees. Explicitly **not** production authentication — see `MVP_PLAN.md §4.4` for why this is a conscious scoping decision, not an oversight.

**SIC Portal**
Short name for the Societal Innovation Collaboration Portal — this project. Full name used in formal contexts (pitch deck title, problem statement references); "SIC Portal" used everywhere else including code and casual docs.

**Tag Overlap Matching**
The algorithm that routes a classified Challenge to a University: compare the Challenge's `Domain` against each University's `Discipline Tags`, propose the best-overlap match. Chosen over embedding-similarity matching specifically because it's explainable — see `ARCHITECTURE.md §4` for the full reasoning.

**Team**
A group formed by a `Faculty` member at a university around a specific Challenge they've chosen to pursue. Produces a `Proposal`.

**University**
A Higher Education Institution in the seed data (e.g. BIT Mesra, IIT ISM Dhanbad, NIT Jamshedpur, Central University of Jharkhand, Vinoba Bhave University), tagged with `Discipline Tags`. The entity Challenges get routed to.

**Zero-shot Classification**
A classification approach that requires no labeled training data for the target categories — the model (`facebook/bart-large-mnli`) classifies text against arbitrary candidate labels at inference time. Used because the timeline doesn't allow for building a labeled training set for the 10 new Domains.
