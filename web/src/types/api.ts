// API Contracts synchronized with FastAPI Pydantic models in backend/app/schemas/

export interface EvidenceSpan {
  start: number;
  end: number;
  text: string;
}

export interface Finding {
  id: string;
  category: string;
  status: 'detected' | 'not_detected' | 'not_assessable';
  reason: string;
  source_evidence: EvidenceSpan[];
  evidence_ids: string[];
  tool?: string | null;
}

export interface URLAnalysis {
  url: string; // Defanged / escaped representation
  normalized_host?: string | null;
  is_ip: boolean;
  has_user_info: boolean;
  user_info?: string | null;
  suspicious: boolean;
  reasons: string[];
}

export interface ReputationResult {
  hostname: string;
  status: 'known_trusted' | 'suspicious' | 'unknown';
  source: string;
  reason: string;
}

export interface GuidanceRef {
  id: string;
  title: string;
  excerpt: string;
  reason?: string | null;
}

export interface AttackStep {
  step: number;
  description: string;
  evidence_ids: string[];
  evidence_offsets: EvidenceSpan[];
}

export interface RiskBreakdownItem {
  rule: string;
  points: number;
  reason: string;
}

export interface RiskAssessment {
  level: 'low' | 'medium' | 'high';
  score: number;
  heuristic: boolean;
  breakdown: RiskBreakdownItem[];
  notes: string[];
}

export interface ActivityEvent {
  id?: string | null;
  type: string;
  status: string;
  detail?: Record<string, unknown> | null;
  timestamp?: string | null;
}

export interface HighlightRegion {
  start: number;
  end: number;
  text: string;
  finding_id: string;
  category: string;
}

export interface InvestigateRequest {
  message: string;
}

export interface InvestigateResponse {
  proposal_id: string;
  status: 'ok' | 'clarification_needed' | 'error';
  message: string;
  findings: Finding[];
  url_analysis: URLAnalysis[];
  reputation: ReputationResult[];
  guidance: GuidanceRef[];
  attack_sequence: AttackStep[];
  validated_evidence: Finding[];
  risk?: RiskAssessment | null;
  highlights: HighlightRegion[];
  guidance_draft: string;
  clarification_questions: string[];
  activity: ActivityEvent[];
  expires_at?: string | null;
}

export interface IncidentApprovalRequest {
  proposal_id: string;
  approved: boolean;
  analyst_notes?: string | null;
  edited_guidance_draft?: string | null;
  edited_findings?: Record<string, unknown>[] | null;
}

export interface IncidentSaveResponse {
  success: boolean;
  incident_id?: string | null;
  message: string;
}

export interface IncidentSummary {
  id: string;
  created_at: string;
  risk_level?: string | null;
  summary?: string | null;
  status?: string | null;
}

export interface IncidentListResponse {
  incidents: IncidentSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface IncidentDetail {
  id: string;
  created_at: string;
  proposal_id?: string | null;
  message: string;
  findings: Record<string, unknown>[];
  risk?: Record<string, unknown> | null;
  guidance_draft?: string | null;
  guidance: Record<string, unknown>[];
  url_analysis: Record<string, unknown>[];
  attack_sequence: Record<string, unknown>[];
  activity: ActivityEvent[];
  analyst_notes?: string | null;
}

export interface IncidentActivityResponse {
  incident_id: string;
  activity: ActivityEvent[];
}


export interface DemoMessage {
  id: string;
  title: string;
  category: string;
  description: string;
  expected_risk: string;
  message: string;
}

export interface DemoMessagesResponse {
  messages: DemoMessage[];
}
