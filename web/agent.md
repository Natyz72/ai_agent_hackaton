# Project 8: Frontend Prompt for the AI Coding Agent

Paste the block below into your coding agent. It builds the `/web` frontend against the API contract, with a mock mode so every screen works without the backend.

```
You are building the FRONTEND of a hackathon app: "AI Suspicious Message
Investigation Agent" (IT helpdesk analyst role). The backend (FastAPI + Supabase)
is built by other teammates in parallel, so you must work against the API contract
below and ship a MOCK MODE that lets every screen work with no backend.

STACK
- React 18 + TypeScript (strict) + Vite + Tailwind CSS
- React Router v6, TanStack Query v5
- Fonts: Inter (UI), JetBrains Mono (message text, URLs, IDs) via Google Fonts
- No UI kit required. Use plain Tailwind components. Icons: lucide-react.
- Folder: /web (the repo root also contains /backend, which you must not touch).
- Production build goes to /web/dist and is served by FastAPI, so use relative
  API paths (/api/...) and no CORS assumptions. In dev, proxy /api to
  http://localhost:8000 in vite.config.ts.

HARD RULES (add them as comments where relevant and in /web/README.md)
1. Text-only analysis. The UI never fetches, opens, or links to any URL from a
   message. URLs are shown DEFANGED (http -> hxxp, "." -> "[.]" in hosts) as
   plain, non-clickable text.
2. Render ALL message text and model output as plain text. Never use
   dangerouslySetInnerHTML. Evidence highlighting must be done by splitting the
   string by character offsets and wrapping segments in <mark>.
3. Never label a message "safe". The lowest risk band is "Low / Inconclusive"
   with neutral slate styling (never green). The uncertainty banner is always
   visible on Results, Review, and Incident detail pages:
   "No warning signs detected does not mean this message is safe."
4. Indicator status has exactly three states and each must look different:
   detected | not_detected | not_assessable (with a reason shown).
5. Nothing is saved before explicit approval. The Approve & Save button is
   disabled until the confirmation checkbox is checked. The incident ID and
   "Pending review" status are shown ONLY after the API confirms success.
   Never show an optimistic success.
6. On any error: show a clear ErrorBanner with a Retry button and KEEP all
   user input (message text, edited draft, checkbox state, reviewer name).
7. No secrets, API keys, or Supabase code in the frontend. Browser storage is
   never used as the database. (sessionStorage may hold the in-progress
   investigation so a refresh does not lose it.)
8. Demo data only: show a small "Demo, fictitious data only" tag in the header.

ROUTES
/                 InvestigatePage        (step 1)
/results          ResultsPage            (step 2)
/review           ReviewPage             (step 3, includes post-save success state)
/incidents        IncidentsPage          (saved history)
/incidents/:id    IncidentDetailPage     (reopen a saved record, read-only)
Guard /results and /review: if there is no investigation in state, redirect to /.

APP SHELL
- Top bar: logo square + "Message Investigator", nav links (New, Saved Incidents),
  right side text: "Text-only analysis · Links are never opened · Demo,
  fictitious data only".
- Stepper under the bar: 1 Investigate, 2 Results, 3 Review, 4 Saved.
  Active step is filled indigo; others slate. Shown on steps 1-3 and the
  post-save state.
- Content max-width about 1100-1200px, centered. Fully usable at 390px wide
  (stack columns below the lg breakpoint).

DESIGN TOKENS (Tailwind)
- Background slate-50; cards white, border slate-200, rounded-xl, subtle shadow
- Primary action indigo-600 (hover indigo-700), text slate-900, muted slate-600
- High risk: red-700 text on red-50 with red-200 border
- Suspicious: amber-700 on amber-50
- Low / Inconclusive: slate-700 on slate-100
- Detected indicator: red or amber accent; Not detected: neutral slate;
  Not assessable: dashed slate border, muted text, reason line
- Evidence highlight: bg-yellow-200
- Info notice: blue-50 bg, blue-200 border, blue-900 text
- Status is NEVER color alone: always include a text label (and icon).
- Touch targets at least 44px tall. Text contrast at least 4.5:1. Visible focus rings.

TYPES (src/types/api.ts) - mirror these exactly
type IndicatorStatus = "detected" | "not_detected" | "not_assessable";
type RiskBand = "Low / Inconclusive" | "Suspicious" | "High";
interface Evidence { start: number; end: number; text: string; source: string }
interface Indicator {
  id: string;                 // e.g. "credential_request"
  label: string;              // e.g. "Credential request"
  status: IndicatorStatus;
  reason?: string;            // required when not_assessable
  evidence: Evidence[];       // offsets into the ORIGINAL message
  tool: string;               // which tool produced it
}
interface UrlItem { raw: string; defanged: string; host: string }
interface GuidanceRef { id: string; title: string; excerpt: string }
interface AttackStep { step: string; evidence: Evidence[] }
interface RiskResult { score: number; band: RiskBand;
  breakdown: { rule: string; points: number }[] }
interface ValidationResult { passed: boolean; issues: string[] }
interface ActivityEntry { at: string; kind: "tool_call" | "tool_result" |
  "error" | "approval" | "save"; tool_name?: string; summary: string;
  payload?: unknown }
interface Assessment {
  type: "assessment";
  investigation_id: string;
  message: string;
  urls: UrlItem[];
  indicators: Indicator[];         // the 4 required plus extras
  social_engineering: Indicator[]; // tactics found, same shape
  domain_reputation: { host: string; status: "known_safe" |
    "known_suspicious" | "unknown"; source: string; note?: string }[];
  attack_sequence: AttackStep[];
  guidance: GuidanceRef[];
  risk: RiskResult;
  assessment: string;
  next_steps: string[];
  draft: string;
  validation: ValidationResult;
  activity: ActivityEntry[];
}
interface Clarification { type: "clarification"; question: string }
type InvestigateResponse = Assessment | Clarification;
interface InvestigateRequest { message: string; sender?: string;
  display_name?: string; headers?: string; clarification_answer?: string }
interface CreateIncidentRequest { approved: true; reviewed_by?: string;
  draft: string; draft_edited: boolean; assessment: Assessment }
interface IncidentSummary { id: string; created_at: string;
  risk_band: RiskBand; status: string; reviewed_by?: string }
interface IncidentDetail extends IncidentSummary {
  approved_at: string; draft_edited: boolean;
  assessment: Assessment; final_draft: string }
interface ApiError { error: { code: string; message: string } }

API CLIENT (src/api/)
- client.ts: fetch wrapper that parses ApiError and throws a typed error.
- investigate.ts: POST /api/investigate
- incidents.ts: POST /api/incidents (returns {id, status}),
  GET /api/incidents, GET /api/incidents/:id
- Use TanStack Query: useMutation for investigate and create incident,
  useQuery for lists and detail.
- MOCK MODE: if import.meta.env.VITE_USE_MOCKS === "true", route all calls to
  src/api/mock.ts, which returns realistic data after a 600-1200 ms delay.
  The mock must support: (a) a full High Risk assessment for the sample
  password-request message, (b) a clarification response when the message is
  under 20 characters, (c) a forced error when the message contains the token
  "[force-error]", (d) an in-memory incidents list with ID generation
  (INC-0001...) so the Saved Incidents page works after a mock save,
  (e) one not_assessable indicator (trusted-domain mismatch when the link host
  is an IP address). Mock data must use only fictitious domains (.test,
  .example) and 192.0.2.x addresses.
- Provide .env.example with VITE_USE_MOCKS=true.

STATE (src/state/InvestigationContext.tsx)
Keeps: message and optional fields, latest InvestigateResponse, edited draft,
reviewer name, checkbox state, save result. Persist the in-progress
investigation to sessionStorage. Provide reset().

PAGES

1) InvestigatePage ( / )
- Heading "New investigation" with one line of purpose text.
- Sample chips (5, from src/data/sampleMessages.ts, all fictitious):
  "Password request", "IP link + urgency", "Lookalike domain",
  "Legitimate message", "Too short". Clicking a chip fills the textarea.
- Large monospace textarea, label "Suspicious message", live counter
  "n / 3000", client-side validation: not empty, 3000 max. Show inline errors.
- Collapsible "Optional details": sender address, display name, headers
  (textarea). Collapsed by default.
- Blue notice: "Links are extracted as text and are never opened. Analysis
  is text-only."
- "Analyze Message" primary button, disabled while invalid or loading.
- Loading state: replace the button area with a progress checklist
  (Inspecting indicators -> Checking URLs and language -> Searching
  guidance -> Drafting assessment). It is a visual-only progress indicator
  cycling on a timer until the response returns; do not claim steps finished
  that did not.
- If response.type === "clarification": show an agent bubble with the
  question, an answer input, and a "Continue" button that re-submits with
  clarification_answer. Keep the original message visible.
- On success (assessment) navigate to /results.
- On error: ErrorBanner with message + Retry; input preserved.

2) ResultsPage ( /results )
- Top: assessment banner with RiskBadge and the risk band, one-line summary,
  and the always-visible UncertaintyBanner.
- Two-column layout (stack on mobile):
  Left: (a) "Original message" in monospace with EvidenceHighlight applying
  all evidence offsets from indicators and social_engineering; (b) "Extracted
  URLs" via UrlList (defanged, non-clickable, "Copy indicators" button that
  copies the defanged list); (c) "Attack sequence" via AttackSequence: ordered
  steps, each listing its supporting snippet, with the note "Inferred from
  message text; does not prove what the recipient did."; (d) "Retrieved
  guidance" GuidanceCards showing real ID (monospace), title, excerpt.
  Right: "Indicator checks" with one IndicatorCard per indicator (the four
  required first: Credential request, Urgency, IP-address link, Trusted-domain
  mismatch), then social-engineering tactics, then domain reputation rows
  (known_safe / known_suspicious / unknown). Add helper text: "Unknown is not
  the same as safe or malicious." Then a risk breakdown (rule + points) with
  the note "Heuristic score, not a probability."
- Show validation: if validation.passed is false, show an amber panel listing
  issues and keep the Continue button available but labeled with a warning.
- Collapsible ActivityLog (tool name, summary, expandable JSON payload).
- Buttons: "Edit message" (back to /), "Continue to Review" (primary).

3) ReviewPage ( /review )
- Two columns. Left (read-only): original message with highlights, evidence
  summary list, guidance excerpts with IDs, assessment text, risk band,
  next steps (ordered list), uncertainty statement.
  Right: editable "User guidance draft" textarea (nothing is sent
  automatically; say so), optional "Your name or initials" input, a
  confirmation checkbox "I have reviewed the evidence and approve saving this
  incident.", primary "Approve & Save Incident" (disabled until checked,
  disabled and spinner while saving), secondary "Discard" (confirm dialog,
  then reset and go to /).
- Track draft_edited = (edited draft !== original draft).
- Submit CreateIncidentRequest. On success ONLY: replace the page content
  with a success card showing incident ID, status "Pending review", reviewer,
  and links "View in Saved Incidents" and "Investigate another message". Do
  not show the ID or status before the API confirms.
- On error: ErrorBanner with Retry; keep the draft, checkbox, and name.
- Prevent double submit.
- Note under the button: "The incident ID and status appear only after the
  database confirms the save."

4) IncidentsPage ( /incidents )
- Table: ID, date, risk badge, status, reviewer. Row click or "Open" goes to
  detail. Empty state: "No incidents saved yet." Loading skeleton and error
  with Retry. Optional (only if the API provides it): a "Similar to INC-xxxx"
  tag. Do not invent this field.

5) IncidentDetailPage ( /incidents/:id )
- Read-only version of the Results layout using saved data, plus approval
  info (approved_at, reviewed_by, draft_edited, final_draft) and status.
  Always show the UncertaintyBanner. Include the ActivityLog if present.
  404/error state with a back link.

COMPONENTS (src/components/)
layout/AppShell, layout/Stepper, layout/NoticeBanner, RiskBadge,
UncertaintyBanner, IndicatorCard, EvidenceHighlight (offset-based, merges
overlapping ranges, plain text only), UrlList, GuidanceCard, AttackSequence,
GuidanceDraftEditor, ApprovalPanel, ClarificationPrompt, ErrorBanner,
ActivityLog, EmptyState, Spinner/Skeleton.

ACCESSIBILITY AND QUALITY
- Real <button>, <a>, <label> + <input>; aria-label on icon-only buttons;
  aria-live="polite" on loading and error regions; visible focus rings.
- Use semantic headings in order; tables use <th scope>.
- No emoji in the UI. Use lucide-react icons with text labels.
- Add a Vitest unit test for EvidenceHighlight (overlap and bounds cases) and
  for the defang helper. Add a test that ApprovalPanel's save button is
  disabled until the checkbox is checked.

FILE STRUCTURE (create exactly)
web/
  package.json, vite.config.ts, tsconfig.json, tailwind.config.ts,
  postcss.config.js, index.html, .env.example, README.md
  src/
    main.tsx, App.tsx
    api/ client.ts, investigate.ts, incidents.ts, mock.ts
    types/ api.ts
    state/ InvestigationContext.tsx
    data/ sampleMessages.ts
    lib/ defang.ts, highlight.ts, format.ts
    pages/ InvestigatePage.tsx, ResultsPage.tsx, ReviewPage.tsx,
           IncidentsPage.tsx, IncidentDetailPage.tsx
    components/ (as listed above)
    styles/ index.css

SAMPLE MESSAGES (fictitious; put in sampleMessages.ts)
1 Password request: "Northwind IT: We detected unusual activity. Verify your
  password at https://northwind-login.example/verify to keep your account."
2 IP link + urgency: "Your mailbox will be suspended within 24 hours. Confirm
  now: http://192.0.2.15/login"
3 Lookalike domain: "HR update: review your benefits at
  https://hr.northwind-corp.example.test-secure.example/portal"
4 Legitimate: "Reminder: the all-hands meeting moves to 3 PM. Details are on
  https://hr.northwind-corp.test/events"
5 Too short: "Please check this."

DELIVERABLES
1. Working app: `npm install && npm run dev` runs with VITE_USE_MOCKS=true and
   every page and state (clarification, error, saving, saved) reachable.
2. `npm run build` succeeds with zero TypeScript errors.
3. README.md: install, run, mock mode, switching to the real API
   (VITE_USE_MOCKS=false), and how the build is served by FastAPI.
4. Finish by printing the file tree and listing anything you stubbed or assumed.
```

## Before you run it

Check that the `Assessment` type matches what your backend teammate returns. If either side changes a field name, the frontend will break silently, so agree on the shape first.
