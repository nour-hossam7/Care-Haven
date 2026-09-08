# CareHaven AI

**Intelligent Humanitarian Aid & Donation Platform** — one-day MVP build.

CareHaven AI turns the traditional `Donate → Deliver` flow into an AI-assisted
decision-support cycle: **Understand → Verify → Prioritize → Match → Support → Track**.
AI assists humans with understanding, prioritizing, and matching cases —
it never automatically rejects a case or accuses anyone of fraud. Suspicious
or unusual cases are always flagged for **human review**.

> **Scope note:** this repo is the one-day sprint version of a larger planned
> architecture. See [Deferred / Future Work](#deferred--future-work) for what's
> intentionally left out for now.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | Streamlit (single UI — no React/Next.js in this build) |
| Backend | FastAPI (Python) |
| Database | SQLite (`carehaven.db`) — models are PostgreSQL-ready |
| AI — NLP | One LLM API call (OpenAI / Anthropic / Ollama) for case understanding |
| AI — Priority | Rule-based weighted scoring (explainable, no training needed) |
| AI — Duplicate check | Text similarity (difflib / TF-IDF cosine) on case descriptions |
| Recommendation | Content-based scoring (category + budget + location + priority) |
| File storage | Local `/uploads` folder |

---

## Repo Structure

```
carehaven-ai/
├── backend/
│   ├── main.py                  # FastAPI app entrypoint
│   ├── database.py              # DB connection/session
│   ├── models.py                # SQLAlchemy models
│   ├── routers/
│   │   ├── cases.py             # Case management endpoints
│   │   ├── donations.py         # Donation management endpoints
│   │   └── ai.py                # AI endpoints
│   └── ai/
│       ├── nlp_extraction.py    # LLM case understanding
│       ├── priority_engine.py   # Rule-based priority scoring
│       ├── duplicate_check.py   # Text-similarity duplicate flagging
│       └── recommender.py       # Donor-case matching
├── frontend/
│   ├── streamlit_app.py         # App entrypoint / navigation
│   ├── pages/                   # Submit Case, Browse Cases, Case Details,
│   │                             # Donate, Recommendations, NGO Review Queue, Dashboard
│   └── api_client.py            # Thin requests wrapper around the backend API
├── seed.py                      # Populates demo cases, donors, donations
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup

### 1. Clone & install

```bash
git clone <repo-url>
cd carehaven-ai
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

Copy `.env.example` to `.env` and fill in:

```
DATABASE_URL=sqlite:///./carehaven.db
LLM_API_KEY=your_key_here
LLM_PROVIDER=openai            # openai | anthropic | ollama
BACKEND_URL=http://localhost:8000
```

### 3. Seed demo data

```bash
python seed.py
```

Populates ~10 demo cases, ~5 demo donors, and a few donations so the app is
never demoed empty.

### 4. Run the backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Swagger docs available at `http://localhost:8000/docs`.

### 5. Run the frontend

In a second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Opens at `http://localhost:8501`.

---

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /cases` | Create a new humanitarian case |
| `GET /cases` | List cases (filter by `status`, `category`) |
| `GET /cases/{id}` | Case details |
| `PATCH /cases/{id}/status` | NGO/Admin approves, flags, or completes a case |
| `POST /donations` | Record a donation; auto-recalculates funding progress & gap |
| `GET /donations` | List donations (by donor or case) |
| `POST /ai/analyze-case` | Runs NLP extraction + priority scoring + duplicate check |
| `GET /recommendations/{donor_id}` | Ranked cases matching a donor's preferences |
| `GET /analytics/summary` | Dashboard totals (active/critical cases, funding gap, people supported) |

---

## Core AI Logic

**Priority Score** = Severity + People Affected + Emergency Indicator + Funding Gap + Time Since Submission
→ mapped to **Critical / High / Medium / Low**, with the top contributing
factors returned as human-readable `reasons`.

**Duplicate check**: new case descriptions are compared against existing ones;
similarity above ~80% sets `duplicate_flag = "Needs Human Review"`. Nothing is
ever auto-rejected.

**Recommendation**: donor preferences (category, budget, location) are matched
against open case characteristics to produce a ranked list with a one-line
match reason.

---

## Team

| Member | Role | Owns |
|---|---|---|
| Member 1 | Backend & Data Lead | FastAPI, DB models, Case & Donation endpoints, seed data |
| Member 2 | AI/ML Lead | NLP extraction, priority engine, duplicate check, recommender |
| Member 3 | Streamlit & Integration Lead | All UI pages, API wiring, dashboard, demo flow |

---

## Deferred / Future Work

Not built in this one-day MVP, planned for later phases:

- Next.js/React frontend
- Computer Vision / YOLO damage detection & image-similarity fraud checks
- RAG chatbot + ChromaDB + Ollama knowledge-base assistant
- Predictive analytics / demand forecasting
- Real authentication (JWT) — currently a role selector in the sidebar
- Interactive filterable humanitarian map & Emergency Response Mode automation

---

*CareHaven AI — Turning Every Contribution Into Smarter Impact.*
