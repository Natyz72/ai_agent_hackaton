# Hackathon Submission Package
## Project 8: AI Suspicious Message Investigation Agent

**Assigned Role**: IT Helpdesk Analyst  
**Application Goal**: Examine suspicious messages (emails, SMS, chat) and create referenced incident records and user guidance drafts with human-in-the-loop approval.  
**Repository Branch**: `backend-y`  
**License / Mode**: 100% Free Service Plan Compliance  

---

## 1. Five-Case Test Report

The hackathon requires testing three ordinary cases, one ambiguous/incomplete case, and one simulated model or tool failure.

| Case # | Test Case Description | Input Snippet | Expected Result | Observed Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Case 1** (Ordinary) | **Credential Phishing & Urgency**<br>IT suspension threat with deceptive subdomain link. | *"URGENT IT SECURITY NOTICE: Your corporate account password will expire in 2 hours... http://login.company.example.phishy.example/auth/reset"* | • Extracts & defangs URL<br>• Flags `SE-URGENCY` and `SE-CREDS`<br>• Flags suspicious domain reputation<br>• High risk score (≥ 60)<br>• Cites `[SEC-01]`, `[SEC-04]`<br>• Proposal returned without incident save | **PASS**: Risk High (Score 85). Highlights generated. Guidance draft cites policy `SEC-04`. No incident record saved before approval. | **PASS** |
| **Case 2** (Ordinary) | **Wire Fraud via IP-based Link**<br>Urgent invoice routing redirect with direct IPv4 address. | *"URGENT: Executive payment wire instructions have been updated... http://192.168.1.100/invoices/wire_update.php"* | • Flags raw IP host (`url_ip_host`) without network requests<br>• Flags `SE-PAYMENT`<br>• High risk score<br>• Cites `[SEC-06]` payment verification policy | **PASS**: Risk High (Score 60). URL defanged to `hxxp[://]192[.]168[.]1[.]100/...`. `SEC-06` cited in guidance draft. | **PASS** |
| **Case 3** (Ordinary) | **Host Spoof via User-Info Trick (@)**<br>Deceptive link using `@` symbol to hide real destination. | *"Security Alert: Unauthorized sign-in detected... http://trusted.example@suspicious.example/session/verify"* | • Detects user-info spoofing (`url_user_info_spoof`)<br>• Resolves destination host as `suspicious.example` (not `trusted.example`)<br>• High risk | **PASS**: Risk High (Score 75). True host parsed as `suspicious.example`. User-info spoofing penalty applied. | **PASS** |
| **Case 4** (Ambiguous) | **Incomplete / Ambiguous Request**<br>Vague text lacking links, headers, or specific requests. | *"Hey team, please review the file from yesterday whenever you have a chance."* | • Does not invent or fabricate headers<br>• Returns `status: "clarification_needed"`<br>• Requests essential missing context (headers, URLs, attachments) | **PASS**: Agent returns `status: "clarification_needed"` and requests specific message details rather than hallucinating threats. | **PASS** |
| **Case 5** (Failure) | **Simulated LLM Provider Failure**<br>Model API times out or throws provider 500 error. | Model API failure simulated or unreachable key. | • App does not crash or leak server internals<br>• Returns safe fallback assessment and error activity event<br>• Retains input message for manual analyst retry | **PASS**: Handled gracefully. Activity logs `llm_call: failed`. Retains raw message and returns safe fallback assessment without data corruption. | **PASS** |

---

## 2. Three Required Tools

Per Hackathon specification, the application implements exactly three primary operational tools:

1. **`Inspect indicators`** (`inspect_indicators` / `analyze_url_structure` / `detect_social_engineering`):
   * Extracts links without making any network requests (offline text analysis only).
   * Runs the 4 mandatory visible checks: Credential requests, Urgency indicators, IP-address links, and Trusted-domain mismatch.
   * Calculates exact character offsets (`EvidenceSpan`) into the original message for UI highlighting.
2. **`Search guidance`** (`search_guidance`):
   * Queries verified handbook passages (`SEC-01` to `SEC-06`) stored in database.
   * `validate_evidence` strictly checks that every cited reference ID exists in the repository, rejecting hallucinated IDs.
3. **`Create incident`** (`create_incident` / `persist_incident`):
   * Internal persistence service strictly excluded from LLM tool registry.
   * Persists approved evidence, risk assessment, analyst notes, and response draft.
   * Enforces explicit analyst confirmation (`approved: true`), valid unexpired proposal ID, and duplicate save prevention.

---

## 3. Free-Service Register

All services and development tools comply with the Hackathon Free Plan requirement:

| Service / Tool | Provider & Tier | Official Pricing / Plan URL | Usage Limits & Free Tier Terms |
| :--- | :--- | :--- | :--- |
| **Web Service & Backend** | Render Free Web Service | https://render.com/pricing | Free plan: 750 hours/month, automatic HTTPS on `onrender.com`. Sleeps after 15 min inactivity. |
| **Database** | Supabase Free Tier | https://supabase.com/pricing | Free tier: 500 MB Postgres storage, 2 active projects, remote database with RLS. |
| **AI Inference** | Google Gemini API (Free Tier) | https://ai.google.dev/pricing | Free plan: Gemini 2.0 Flash (`15 RPM`, `1,500 RPD`, `1,000,000 TPM`). Zero credit card required. |
| **Development & Package Manager** | `uv` / Python 3.13 / FastAPI | https://github.com/astral-sh/uv | Open-source software (MIT / Apache 2.0). |

---

## 4. Key Design & Security Boundaries

1. **Text Analysis Only**: Never visit, resolve, fetch, preview, or follow URLs. All URLs are defanged (`hxxp[://]`).
2. **Untrusted Evidence Boundary**: Submitted messages are treated strictly as passive data, never as agent instructions (prompt injection defense).
3. **Uncertainty Principle**: "Absence of detected warning signs must not be presented as proof of safety." Score is heuristic (`heuristic: true`), not a statistical certainty.
4. **Human-in-the-Loop Approval Gate**: `POST /api/investigate` strictly creates an unpersisted proposal. Only explicit analyst review and approval via `POST /api/incidents` commits to the database.

---

## 5. Live Demonstration Guide (10 Minutes)

1. **Step 1: Load Demo Message** (1 min):
   * Use `GET /api/demo-messages` or paste `DEMO-01` (Password expiry phish).
2. **Step 2: Run Investigation** (2 min):
   * Trigger `POST /api/investigate`.
   * Observe tool activities in the live activity stream (`inspect_indicators`, `analyze_url_structure`, `search_guidance`).
3. **Step 3: Review Evidence & Proposal** (3 min):
   * Review highlighted spans in message text.
   * Point out the 4 checks (Urgency, Credential Harvest, Domain mismatch, Defanged URL).
   * Note the referenced handbook citation (`[SEC-04]`).
4. **Step 4: Analyst Approval & Save** (2 min):
   * Edit analyst notes or guidance text.
   * Click **Approve & Create Incident**.
   * Verify saved incident ID. Show that submitting approval a second time is rejected (duplicate-prevention).
5. **Step 5: Reopen Incident & Clarification Demo** (2 min):
   * Navigate to Incident History (`GET /api/incidents`) and reopen saved record.
   * Paste `DEMO-04` (Ambiguous message) to demonstrate the **Clarification Workflow** (`clarification_needed`).
