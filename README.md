# AI Suspicious Message Investigation Agent

An autonomous, text-only investigation assistant for IT Helpdesk and Security Operations analysts. The analyst submits suspicious messages (emails, SMS, chat messages); the agent safely extracts indicators offline, verifies domain reputations, maps attack sequences, checks internal security handbook guidelines, scores risk deterministically, and prepares an evidence-referenced guidance draft.

**Strict Human-in-the-Loop Approval:** No incident records are persisted until an analyst explicitly reviews and approves the investigation proposal.

---

## Key Security & Architectural Principles

1. **Text-Only Offline Analysis**: Never visits, fetches, previews, or resolves URLs. All links are sanitized and defanged (`hxxp[://]`).
2. **Untrusted Evidence Boundary**: Input messages are treated strictly as passive data inside isolated markdown blocks, defending against prompt injection.
3. **Approval-Gated Persistence**: `POST /api/investigate` strictly creates an unpersisted proposal snapshot. Only explicit analyst review via `POST /api/incidents` (`approved: true`) saves to the database. `create_incident` is an internal service excluded from the LLM tool registry.
4. **Deterministic Validation & Scoring**: Model outputs are checked by Python validation guards (`validate_evidence`, `assess_risk`). Scoring and handbook references (`SEC-01` to `SEC-06`) are strictly validated against repository records to eliminate hallucinations.
5. **Uncertainty Principle**: "Absence of detected warning signs must not be presented as proof of safety." The lowest rating is `Low / Inconclusive`, and the score is marked as heuristic.
6. **Zero Secrets in Frontend / Single Origin**: The React SPA is built into `web/dist` and served directly by FastAPI. Zero credentials or keys exist on the client side.

---

## Free-Service Register

This project runs 100% within the free tiers of supported platforms:

| Service / Tool | Provider & Tier | Limits & Free Tier Terms |
| :--- | :--- | :--- |
| **Web Service & API** | Render Free Web Service | 750 free hours/month, automatic HTTPS on `onrender.com`. Idle sleep after 15 minutes. |
| **Database** | Supabase Free Tier | 500 MB Postgres database, Row Level Security (RLS) enabled, service-role isolation. |
| **AI Inference** | Google Gemini API (Free Tier) | Gemini 2.0 Flash (`15 RPM`, `1,500 RPD`, `1,000,000 TPM`). No credit card required. |
| **Package & Build Tools** | `uv`, Python 3.11+, Node 18+, Vite | Open source (MIT / Apache 2.0). |

---

## Project Structure

```
/
├── render.yaml                      # Render Blueprint deployment definition
├── .env.example                     # Environment template (no secrets)
├── HACKATHON_SUBMISSION_PACKAGE.md  # 5-case test report & verification pack
├── supabase/
│   ├── schema.sql                   # Database schema with RLS policies
│   └── seed.sql                     # Seed data: trusted domains, reputation, handbook passages
├── backend/
│   ├── requirements.txt             # Backend dependencies (FastAPI, Pydantic, Supabase, etc.)
│   ├── pytest.ini                   # Pytest configuration with pythonpath = .
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint, CORS, static SPA serving
│   │   ├── config.py                # Pydantic Settings & environment variables
│   │   ├── agent/                   # Investigation loop, tool registry, prompts
│   │   ├── api/                     # Routes: /health, /investigate, /incidents, /demo-messages
│   │   ├── db/                      # Supabase client & repository abstraction (with in-memory fallback)
│   │   ├── llm/                     # Gemini 2.0 REST client & offline FakeLLMClient adapter
│   │   ├── services/                # Evidence validation, risk assessment, draft generator
│   │   ├── tools/                   # URL analysis, indicator inspection, SE detection, guidance search
│   │   └── schemas/                 # Pydantic v2 data models & API contracts
│   └── tests/                       # Complete pytest test suite (46 unit & integration tests)
└── web/
    ├── package.json                 # Frontend dependencies (React, Vite, Lucide, Tailwind)
    ├── vite.config.ts               # Vite build config & dev API proxy
    ├── vitest.config.ts             # Vitest unit test configuration
    └── src/
        ├── api/                     # Backend API client with unified error handling
        ├── components/              # Evidence highlighting, Approval panel, Attack sequence, etc.
        ├── pages/                   # InvestigatePage, ReviewPage, IncidentsPage, DetailPage
        └── state/                   # React context state management
```

---

## Local Development Setup

### Prerequisites
- Python 3.11+ (or `uv`)
- Node.js 18+ & npm

### 1. Environment Configuration

Copy the example environment configuration:

```bash
cp .env.example .env
```

Set the following variables in `.env` (optional for local mock testing; required for live Gemini/Supabase):
```ini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

*Note: If `GEMINI_API_KEY` is omitted, the backend automatically uses `FakeLLMClient` with deterministic offline analysis.*

### 2. Backend Setup & Run

```bash
cd backend
pip install -r requirements.txt
# Or using uv:
# uv run uvicorn app.main:app --reload --port 8000

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Health Check: <http://127.0.0.1:8000/api/health>
- Interactive OpenAPI Docs: <http://127.0.0.1:8000/docs>

### 3. Frontend Setup & Run

In a separate terminal:

```bash
cd web
npm install
npm run dev
```

Visit <http://localhost:5173>. Requests to `/api/*` are proxied to the backend at `http://localhost:8000`.

---

## Running Tests

### Backend Tests (46 passing tests)

```bash
cd backend
pytest
```
*Tests cover the agent loop, tool execution cap, social engineering detection, URL parsing, user-info spoofing tricks, risk assessment, guidance lookup, and the approval gate.*

### Frontend Tests (7 passing tests)

```bash
cd web
npm test -- --run
```
*Tests cover URL defanging, character offset evidence highlighting, and approval panel interaction.*

---

## Database Setup (Supabase)

1. Create a free project on [Supabase](https://supabase.com).
2. In the Supabase dashboard, open the **SQL Editor**.
3. Run `supabase/schema.sql` to create tables and enable Row Level Security (RLS).
4. Run `supabase/seed.sql` to populate trusted domains, reputation entries, and security guidance passages (`SEC-01` through `SEC-06`).
5. Copy the Project URL and `service_role` secret key into your `.env` or Render environment settings.

---

## Deployment to Render

The repository includes a ready-to-use [`render.yaml`](render.yaml) blueprint:

1. Push this repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com), click **New +** > **Blueprint**.
3. Select your repository. Render will automatically detect the `render.yaml` specification.
4. Set the secret environment variables in the Render dashboard:
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `SUPABASE_URL`: Your Supabase project URL.
   - `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role secret key.
5. Deploy. Render will:
   - Install Python dependencies (`pip install -r backend/requirements.txt`).
   - Build the frontend bundle (`cd web && npm ci && npm run build`).
   - Start the unified server (`cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`).

> **Free Tier Tip:** Render free web services spin down after 15 minutes of inactivity and take 30–50 seconds to wake on the first request. Supabase free instances pause after 7 days of inactivity. Verify `/api/health` reports `database_configured: true` before live evaluations.

---

## API Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health, model configuration, and database connection status. |
| `GET` | `/api/demo-messages` | Curated sample messages for demonstration and testing. |
| `POST` | `/api/investigate` | Evaluates message indicators, produces risk assessment and guidance draft. **Does not save an incident.** |
| `POST` | `/api/incidents` | **Approval Gate:** Persists approved incident with analyst notes. Rejects duplicate or unapproved requests. |
| `GET` | `/api/incidents` | Paginated incident list. |
| `GET` | `/api/incidents/{id}` | Detailed incident record and assessment data. |
| `GET` | `/api/incidents/{id}/activity` | Immutable audit log of investigation and save events. |
