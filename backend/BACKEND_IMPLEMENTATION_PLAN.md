# Backend Implementation Plan - AI Suspicious Message Investigation Agent

**Repo**: `C:\Users\Student38\Desktop\ai_agent_hackaton`  
**Branch**: `backend-y`  
**Reference**: `backend/AGENTS.md`  
**Goal**: Build the FastAPI backend in small, testable stages following all security/correctness rules.

## Current State Assessment

Based on initial inspection:
- Backend skeleton already exists with all modules from repository map (agent/, llm/, tools/, services/, db/, schemas/, api/routes/, tests/)
- Many files appear to be scaffolded/implemented (e.g., all 6 tools exist, agent components exist, services exist, tests exist)
- `main.py`, `config.py`, `schema.sql` all appear empty (0 lines) per earlier reads - need to verify
- Frontend is React + Vite (`web/`) - must serve from FastAPI in production on Render
- Supabase schema/seed files exist in `supabase/`

We need to audit what's actually implemented vs scaffolded before proceeding. Stage 0 is a repo audit (no changes).

## Stage-by-Stage Plan

### Stage 0: Repository Audit & Plan (No Code Changes) 
**Goal**: Understand current implementation state, identify gaps vs requirements.

**Tasks:**
1. Read all backend files to see what's actually implemented (main.py, config.py, schemas, routes, agent, llm, tools, services, db)
2. Read `supabase/schema.sql`, `supabase/seed.sql`
3. Read `web/src/types/api.ts` if exists
4. Read `.env.example`
5. Check git status/diff
6. List test files and run `pytest --collect-only` from backend to see what tests exist
7. Verify frontend is Vite (check `web/vite.config.ts`, `web/package.json`)
8. Document current state vs required state from AGENTS.md

**Deliverable**: Audit report with:
- What's implemented vs missing
- Contradictions found
- Test commands available
- Vite confirmation
- Proposed implementation order for remaining gaps

**Acceptance**: No files modified, full picture of current state.

---

### Stage 1: Settings, Schemas, DB Design, Health Endpoint
**Goal**: Foundations - config, schemas, DB client/repo, schema/seed, health, minimal main.py

**Files to implement/update:**
- `backend/app/config.py` - Pydantic settings with env vars, limits (message length, tool call cap, timeouts, rate limits)
- `backend/app/schemas/common.py`, `investigate.py`, `incidents.py`, `tools.py` - all request/response/tool schemas
- `backend/app/db/client.py` - Supabase client (server-side only)
- `backend/app/db/repositories.py` - repo interfaces/impl
- `backend/app/api/deps.py` - dependencies (db, rate limiter)
- `backend/app/api/routes/health.py` - GET /api/health
- `backend/app/main.py` - app setup, middleware/CORS, routers, health, static serving, SPA fallback
- `supabase/schema.sql` - tables: trusted_domains, domain_reputation, guidance_passages, incidents, activity_log, **investigation_proposals/drafts** (needed for approval flow per AGENTS.md line 75)
- `supabase/seed.sql` - 3 trusted domains, ~6 reputation entries, 3-6 guidance passages with stable IDs (SEC-01, etc.)

**Requirements:**
- Secrets only server-side, .env.example has placeholders only
- RLS enabled on tables, no anonymous write policies
- investigation_proposals table with opaque ID, status, output snapshot, expiry, creation time
- Health endpoint minimal, no env/creds leaked
- Tests for config/schema validation

**Acceptance**: Foundations in place, health works, schema/seed complete, tests pass.

---

### Stage 2: Deterministic Analysis Tools (One by One)
**Goal**: Implement 3 core tools with unit tests first

**Tools (in order):**
1. `backend/app/tools/inspect_indicators.py` - extract indicators, detect patterns
2. `backend/app/tools/analyze_url_structure.py` - URL parsing, handle user-info tricks (trusted.example@attacker.example), host boundaries, subdomains, IP URLs. NO network calls.
3. `backend/app/tools/detect_social_engineering.py` - detect SE tactics with evidence spans

**For each tool:**
- Define edge cases and test cases first
- Return structured output with evidence offsets into exact original message
- No fetch/resolve/preview/follow URLs
- Add focused pytest tests (normal, misleading, empty, malformed/edge cases)
- Run tests and report results

**Acceptance**: All 3 tools correct on adversarial cases (especially URL parsing).

---

### Stage 3: Supabase-Backed Retrieval Tools
**Goal**: DB-backed lookup tools

**Tools:**
- `backend/app/tools/check_domain_reputation.py` - normalized hostname lookup from reputation table; known/suspicious/unknown with explanation
- `backend/app/tools/search_guidance.py` - retrieve actual IDs, titles, content/excerpts from DB. Never invent IDs. Must return real DB record IDs.

**Requirements:**
- Use repository abstraction
- Unit tests with fake repos
- Unknown = unknown (not safe/malicious)
- Guidance IDs come from DB rows

**Acceptance**: Correct handling of unknown domains, real IDs only.

---

### Stage 4: Attack Sequence, Activity, Risk, Validation
**Goal**: Orchestration services (app-controlled, not Gemini tools)

**Files:**
- `backend/app/tools/map_attack_sequence.py` - propose sequence, cite evidence offsets/IDs, don't claim recipient did steps
- `backend/app/services/evidence.py` - evidence handling/offsets
- `backend/app/services/validate_evidence.py` - validate spans against text, findings match tool outputs, guidance IDs exist. **App-controlled**
- `backend/app/services/assess_risk.py` - deterministic scoring with rule-by-rule breakdown, heuristic (not probability), missing data doesn't auto-lower risk. **App-controlled**
- `backend/app/services/guidance_draft.py` - draft from validated findings + retrieved passages
- `backend/app/services/activity_log.py` - log actual events/outcomes only

**Tests:** invalid offsets, invented guidance IDs, unsupported findings, contradictory outputs, deterministic risk breakdown, attack steps missing evidence.

**Acceptance**: All validation/scoring under Python control.

---

### Stage 5: Gemini Client & Bounded Agent Loop
**Goal**: LLM integration with strict boundaries

**Files:**
- `backend/app/llm/base.py` - LLMClient interface
- `backend/app/llm/gemini.py` - Gemini implementation
- `backend/app/llm/fake.py` - fake for tests
- `backend/app/agent/prompts.py`
- `backend/app/agent/registry.py` - **ONLY** 6 tools: inspect_indicators, analyze_url_structure, detect_social_engineering, check_domain_reputation, search_guidance, map_attack_sequence. **NEVER** create_incident
- `backend/app/agent/loop.py` - bounded loop, tool call cap, reject unknown/invalid, validate args, detect repeats, run validation+scoring after, clarification variant if missing info, graceful errors

**Tests:** normal sequence, clarification, malformed call, repeated/cap reached, forced failures. No real API keys needed.

**Acceptance**: create_incident absent from registry, bounds enforced.

---

### Stage 6: Investigation Endpoint (No Incident Persistence)
**Goal**: POST /api/investigate

**Files:**
- `backend/app/api/routes/investigate.py`
- May need updates to repos for investigation_proposals

**Requirements:**
- Validate input length
- Run agent loop
- Validate evidence + score under backend control
- Create server-side pending proposal (opaque ID, status, snapshot, expiry)
- Return proposal with findings, URLs, reputation, guidance refs, attack sequence, validated evidence, risk breakdown, highlights, guidance draft, clarification state, activity
- **NO incident write**
- Tests prove incidents table not written

**Acceptance**: Proposal created durably (DB), no incident persistence.

---

### Stage 7: Approval-Gated Incident Creation & History
**Goal**: Approval flow with strict protections

**Files:**
- `backend/app/api/routes/incidents.py` - POST (approval), GET list, GET by id, GET activity
- `backend/app/tools/create_incident.py` - **internal persistence service only, NOT in Gemini registry**
- Repo methods for incidents, activity, proposal state transitions

**Requirements:**
- POST /api/incidents requires explicit approval tied to valid pending proposal ID
- Reload proposal from DB, re-validate, atomic state transition to prevent duplicates
- Reject: missing/false approval, fake/expired/modified/already-saved proposals, invalid guidance refs
- Return incident ID only after DB confirms insert
- History returns only actual saved records
- Activity reflects actual events
- Document: no auth = demo analyst action, not identity verification

**Tests:** all rejection cases, successful save, history/detail/activity.

**Acceptance**: Strict approval gate, idempotent/duplicate-protected.

---

### Stage 8: Integration, Security Review, Deployment Readiness
**Goal**: Final checks

**Tasks:**
- Run full backend test suite
- Check app locally
- Build Vite frontend
- Verify FastAPI serves web/dist and SPA fallback
- Security review: no URL fetching, create_incident not in registry, approval enforced, RLS/schema, secrets, caps, error paths
- Update .env.example, README if needed
- Fix only concrete defects, add regression tests
- Report exact results

**Acceptance**: All tests pass (or blockers reported), security boundaries confirmed.

## Critical Security Checklist (Must Verify Always)
- [ ] No URL fetch/resolve/preview/follow
- [ ] URLs escaped/defanged, non-clickable
- [ ] Message content not treated as instructions
- [ ] Hostname boundary parsing correct (user-info tricks)
- [ ] create_incident NOT in Gemini registry
- [ ] All validation/scoring in Python (not Gemini tools)
- [ ] No secrets in logs/tests/browser
- [ ] Incident only saved on explicit approval after proposal validation
- [ ] Guidance IDs from DB only
- [ ] Activity logs truthful
- [ ] Bounds enforced (length, tool calls, time, results)

## Testing Commands
From `backend/`:
- `pytest` - full suite
- `pytest -v` - verbose
- `pytest tests/test_<name>.py` - specific test

## Implementation Notes
- Work in small stages, get approval between stages
- Read diffs carefully
- Commit after tests pass per stage
- Coordinate API schema changes with frontend (web/src/types/api.ts)
- investigation_proposals table is critical - needs to be added to schema even if not shown in initial structure
- Use fake LLM by default in tests

## File Tracking
Create this plan file and update it as we progress through stages, marking completion status.
