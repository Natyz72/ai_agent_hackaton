import { CreateIncidentRequest, IncidentSummary, IncidentDetail } from '../types/api';
import { fetchApi } from './client';
import { mockCreateIncident, mockGetIncidents, mockGetIncident } from './mock';

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';

export async function createIncident(request: CreateIncidentRequest): Promise<{ id: string; status: string }> {
  if (USE_MOCKS) {
    return mockCreateIncident(request);
  }
  const proposalId = request.assessment?.investigation_id || (request.assessment as any)?.proposal_id;
  const res = await fetchApi<any>('/api/incidents', {
    method: 'POST',
    body: JSON.stringify({
      proposal_id: proposalId,
      approved: request.approved,
      analyst_notes: request.reviewed_by || 'Analyst',
      edited_guidance_draft: request.draft,
      edited_findings: request.assessment?.indicators as any,
    }),
  });
  return { id: res.incident_id || res.id, status: res.status || 'approved' };
}

export async function getIncidents(): Promise<IncidentSummary[]> {
  if (USE_MOCKS) {
    return mockGetIncidents();
  }
  const res = await fetchApi<any>('/api/incidents');
  const items = Array.isArray(res) ? res : res.incidents || [];
  return items.map((i: any) => ({
    id: i.id,
    created_at: i.created_at,
    risk_band:
      i.risk_level === 'high' ? 'High' : i.risk_level === 'medium' ? 'Suspicious' : 'Low / Inconclusive',
    status: i.status || 'approved',
    reviewed_by: i.reviewed_by || (i.analyst_notes ? i.analyst_notes.slice(0, 30) : 'Analyst'),
  }));
}

export async function getIncident(id: string): Promise<IncidentDetail> {
  if (USE_MOCKS) {
    return mockGetIncident(id);
  }
  const res = await fetchApi<any>(`/api/incidents/${id}`);
  const riskBand =
    res.risk?.level === 'high' ? 'High' : res.risk?.level === 'medium' ? 'Suspicious' : 'Low / Inconclusive';
  return {
    id: res.id,
    created_at: res.created_at,
    approved_at: res.created_at,
    risk_band: riskBand,
    status: res.status || 'approved',
    reviewed_by: res.analyst_notes || 'Analyst',
    draft_edited: false,
    final_draft: res.guidance_draft || '',
    assessment: {
      type: 'assessment',
      investigation_id: res.proposal_id || res.id,
      message: res.message || '',
      urls: (res.url_analysis || []).map((u: any) => ({
        raw: u.url,
        defanged: u.url,
        host: u.normalized_host || '',
      })),
      indicators: res.findings || [],
      social_engineering: (res.findings || []).filter((f: any) => f.category === 'social_engineering'),
      domain_reputation: [],
      attack_sequence: (res.attack_sequence || []).map((s: any) => ({
        step: s.description || `Step ${s.step}`,
        evidence: s.evidence_offsets || [],
      })),
      guidance: res.guidance || [],
      risk: {
        score: res.risk?.score || 0,
        band: riskBand,
        breakdown: res.risk?.breakdown || [],
      },
      assessment: `Saved Incident Record: ${res.id}`,
      next_steps: ['Incident closed with analyst approval.'],
      draft: res.guidance_draft || '',
      validation: { passed: true, issues: [] },
      activity: (res.activity || []).map((a: any) => ({
        at: a.timestamp || res.created_at,
        kind: 'save',
        summary: `${a.type || 'event'}: ${a.status || 'approved'}`,
      })),
    },
  };
}
