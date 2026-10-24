// HARD RULES: Mirror types exactly as specified
export type IndicatorStatus = "detected" | "not_detected" | "not_assessable";
export type RiskBand = "Low / Inconclusive" | "Suspicious" | "High";

export interface Evidence { start: number; end: number; text: string; source: string }
export interface Indicator {
  id: string;                 // e.g. "credential_request"
  label: string;              // e.g. "Credential request"
  status: IndicatorStatus;
  reason?: string;            // required when not_assessable
  evidence: Evidence[];       // offsets into the ORIGINAL message
  tool: string;               // which tool produced it
}
export interface UrlItem { raw: string; defanged: string; host: string }
export interface GuidanceRef { id: string; title: string; excerpt: string }
export interface AttackStep { step: string; evidence: Evidence[] }
export interface RiskResult { 
  score: number; 
  band: RiskBand;
  breakdown: { rule: string; points: number }[] 
}
export interface ValidationResult { passed: boolean; issues: string[] }
export interface ActivityEntry { 
  at: string; 
  kind: "tool_call" | "tool_result" | "error" | "approval" | "save"; 
  tool_name?: string; 
  summary: string;
  payload?: unknown 
}
export interface Assessment {
  type: "assessment";
  investigation_id: string;
  message: string;
  urls: UrlItem[];
  indicators: Indicator[];         // the 4 required plus extras
  social_engineering: Indicator[]; // tactics found, same shape
  domain_reputation: { 
    host: string; 
    status: "known_safe" | "known_suspicious" | "unknown"; 
    source: string; 
    note?: string 
  }[];
  attack_sequence: AttackStep[];
  guidance: GuidanceRef[];
  risk: RiskResult;
  assessment: string;
  next_steps: string[];
  draft: string;
  validation: ValidationResult;
  activity: ActivityEntry[];
}

export interface Clarification { type: "clarification"; question: string }
export type InvestigateResponse = Assessment | Clarification;

export interface InvestigateRequest { 
  message: string; 
  sender?: string;
  display_name?: string; 
  headers?: string; 
  clarification_answer?: string 
}

export interface CreateIncidentRequest { 
  approved: true; 
  reviewed_by?: string;
  draft: string; 
  draft_edited: boolean; 
  assessment: Assessment 
}

export interface IncidentSummary { 
  id: string; 
  created_at: string;
  risk_band: RiskBand; 
  status: string; 
  reviewed_by?: string 
}

export interface IncidentDetail extends IncidentSummary {
  approved_at: string; 
  draft_edited: boolean;
  assessment: Assessment; 
  final_draft: string 
}

export interface ApiError { error: { code: string; message: string } }
