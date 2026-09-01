# Societal Innovation Collaboration Portal (SIC Portal)
### MVP Plan — SIH26043, Government of Jharkhand
**Team Convergence**

---

## 1. Problem Statement

Communities across Jharkhand face recurring local challenges in education, healthcare, agriculture, water management, sanitation, environment, rural livelihoods, accessibility, urban infrastructure, and public service delivery. Citizens are usually the first to notice these problems, but there is no structured channel through which they can submit them for systematic evaluation and innovation-driven resolution.

At the same time, Higher Education Institutions across the state hold significant academic expertise, research capacity, and a large pool of students capable of building practical solutions, while industries, startups, and CSR organizations bring technical execution capability and funding. Today, collaboration between citizens, universities, and industry on these problems is fragmented, ad hoc, and project-specific, with no shared platform connecting the three.

The state needs a digital platform that lets citizens report societal challenges, uses AI to categorize and route those challenges to the right university based on academic strength, lets universities form teams and propose solutions, brings in industry and CSR partners for funding and deployment, and gives the government a real-time view of the entire pipeline from problem to outcome.

The bottleneck this platform solves is not the availability of expertise. It is the absence of a structured connection between the people who face problems and the institutions equipped to solve them.

---

## 2. Our Approach

We are not building this from a blank page. Our team previously built IssueRouter, an AI-powered civic complaint triage system that ingested citizen complaints from X (Twitter), classified them using zero-shot NLP, deduplicated similar complaints through semantic clustering, scored them for urgency, and routed them to the right government department on a live dashboard. It placed 3rd at HNC 3.0.

That system solved one third of this problem well: turning unstructured citizen input into structured, prioritized, routed information. It did not solve the other two thirds, which is everything this problem statement is actually about: connecting that structured problem to a university with the right expertise, letting that university form a team and propose a solution, and bringing in industry to fund and deploy it.

Our approach is to treat this as an engine-and-body build, not a full rewrite and not a light patch. We keep the parts of IssueRouter that already work and are hard to get right from scratch: the zero-shot classification pipeline, the semantic deduplication logic, the priority scoring formula, and the FastAPI plus SQLAlchemy backend pattern. We rebuild everything else, because the core of what this problem statement asks for, university and industry collaboration, simply did not exist in the old system.

Given an aggressive build timeline, we are scoping this as a genuine MVP: one complete, working, end-to-end flow across all four stakeholder types, built to demo depth rather than production depth. We are deliberately not building full authentication, multilingual support, real payment or funding flows, or production-grade file storage. Every simplification is a conscious choice we can defend, not a corner cut by accident.

---

## 3. What the Solution Is

The SIC Portal is a four-sided platform connecting citizens, universities, industry and CSR partners, and government officials around a shared pipeline: a challenge is submitted, AI classifies and routes it, a university takes ownership and proposes a solution, industry supports it, and government tracks the outcome across the state.

### 3.1 Citizen Layer
A citizen, community organization, Panchayati Raj Institution, or Urban Local Body submits a challenge through a simple web form: a description, a district, an optional photo, and no requirement to know which category or department it belongs to. The system figures that out.

### 3.2 AI Intake Layer
Every submitted challenge is automatically classified into a thematic domain (education, agriculture, healthcare, water resources, environment, energy, urban development, accessibility, public administration, rural livelihoods), checked against existing submissions to avoid duplicate entries piling up separately, and scored for priority based on volume and severity signals. This is the direct evolution of IssueRouter's pipeline, retargeted from civic complaints to societal challenges.

### 3.3 University Matching and Collaboration Layer
Each classified challenge is matched against a database of Jharkhand universities and research institutions tagged by discipline and research strength, and routed to the best-fit institution. A university-side dashboard shows that institution its assigned challenges, lets a faculty member form a project team, and lets the team submit a solution proposal.

### 3.4 Industry Partnership Layer
An industry-side dashboard shows open proposals across all universities. A startup, MSME, research lab, or CSR organization can view a proposal and pledge to support it, representing the mentorship, funding, and deployment collaboration the problem statement calls for.

### 3.5 Government Analytics Layer
A government-facing dashboard aggregates everything happening across the platform: how many challenges have come in, their distribution across domains and districts, how many universities and industry partners are actively engaged, and how far projects have progressed through the pipeline.

### 3.6 Notification Layer
A lightweight in-app notification system keeps each stakeholder aware of movement relevant to them, a citizen knowing their challenge was picked up, a university knowing a new challenge was routed to them, an industry partner knowing a new proposal is open.

---

## 4. How We Are Going to Solve It

### 4.1 Reused Engine, Redesigned Body

The AI pipeline is the one part of this system with real precedent and real engineering risk already retired. We reuse it directly:

- **Classification**: BART zero-shot classification (facebook/bart-large-mnli), retagged from IssueRouter's 7 civic categories to the 10 thematic domains this problem statement specifies. Zero-shot means no training data is needed, which matters given the timeline.
- **Location extraction**: spaCy with a custom EntityRuler, gazetteer rebuilt from IssueRouter's Delhi-centric locality list to Jharkhand's districts and blocks.
- **Deduplication**: sentence-transformers (all-MiniLM-L6-v2) embeddings compared by cosine similarity, exactly as in IssueRouter, to catch multiple citizens reporting the same underlying issue.
- **Prioritization**: the same weighted scoring formula from IssueRouter, adapted from urgency-plus-social-reach to challenge volume plus severity signals appropriate to this domain.

What does not carry over from IssueRouter, because it does not exist there at all, is university matching, industry collaboration, project lifecycle tracking, and multi-role access. These are new builds.

### 4.2 University Matching Logic

Rather than the flat category-to-department dictionary IssueRouter used for government routing, we match challenges to universities using discipline tag overlap. Each university in our seed data is tagged with the domains it has real strength in (for example, an agricultural research institute tagged for agriculture and rural livelihoods, a technical institute tagged for urban development and energy). A challenge's classified domain is compared against each university's tags, and the best-overlap match is proposed as the routing recommendation.

We chose tag overlap over a more sophisticated embedding-similarity match deliberately. It is fast to build, and just as important, it is explainable: if a judge or an official asks why a challenge was routed to a specific university, we can point to the exact matching tag rather than a similarity score nobody can intuitively verify. Depth we can defend matters more than a fancier system we can't explain under questioning.

### 4.3 New Data Model

The old system's schema (RawTweet, Complaint, Cluster, Action) was built around a single officer consuming a single stream. This system needs a schema built around four independent stakeholder types interacting with a shared pipeline: Challenge, University, Faculty, IndustryPartner, Team, Proposal, Project, and Notification. Each stakeholder type gets its own view into this shared data, filtered to what's relevant to them.

### 4.4 Role Access Without Production Auth

Given the timeline, full authentication is out of scope. Access is handled through a simple role selector, citizen, university, industry, or government, that determines which dashboard a user sees. This is a conscious MVP simplification, not an oversight, and it lets us demonstrate the full multi-stakeholder flow without spending days on login infrastructure that adds no value to a hackathon evaluation.

### 4.5 Real Jharkhand Grounding

A platform built for Jharkhand has to actually reflect Jharkhand. We are seeding the system with real institutions (BIT Mesra, IIT ISM Dhanbad, NIT Jamshedpur, Central University of Jharkhand, Vinoba Bhave University, and others), real districts and blocks in the location gazetteer, and plausible regional industry and CSR partners (drawing on organizations like Tata Steel Foundation and JSPL CSR as reference points), rather than reusing IssueRouter's Delhi and Mumbai centric data.

### 4.6 Honest Scoping

We are explicitly building this in three tiers, and we say so in our pitch rather than hiding it:

- **Fully built and demoed live**: citizen submission, AI classification, deduplication, prioritization, university matching, university team formation and proposals, industry pledges, government analytics dashboard, in-app notifications.
- **Simplified but functional for the demo**: role access (no real auth), project status tracking (a single status field rather than full milestone management), file handling (basic upload and display, no production storage pipeline).
- **Roadmapped, not built**: production authentication and security, multilingual intake (Hindi and regional languages), real funding and payment flows, IP and legal tracking, SMS and email notification delivery, video content analysis.

This scoping is a strength in the pitch, not a weakness. It shows we understand the full scope of the problem statement and made deliberate engineering tradeoffs under a real deadline, rather than either overpromising or narrowly solving one slice of the problem and calling it done.

---

## 5. The Project End to End

**Flow**: A citizen in a Jharkhand district submits a challenge with a description, district, and optional photo. The AI pipeline classifies it into a thematic domain, checks it against existing submissions for duplicates, and assigns it a priority score. The system matches it to the best-fit university based on discipline overlap and routes it there. A faculty member at that university reviews the challenge, forms a team, and submits a solution proposal. An industry or CSR partner browsing open proposals pledges support to one. The project's status moves from submitted through team formed, prototype, testing, to deployed. Throughout this, a government dashboard shows the full picture: how many challenges have come in, their spread across domains and districts, how many universities and industry partners are actively engaged, and how projects are progressing. Each stakeholder gets an in-app notification when something relevant to them happens.

**What this demonstrates against the problem statement**: a citizen engagement module with multimedia and location support, an AI-enabled classification and deduplication and routing module, a university collaboration module with team formation and proposals, an industry partnership module with mentorship and funding pledges, a lightweight project lifecycle tracker, a government analytics dashboard, and a notification system connecting all stakeholders, which together cover every core component the problem statement describes, built to a working prototype standard within the available timeline.

---

*Team Convergence · SIH26043 · MVP Plan*
