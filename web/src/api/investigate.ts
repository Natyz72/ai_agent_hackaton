import { InvestigateRequest, InvestigateResponse } from '../types/api';
import { fetchApi } from './client';
import { mockInvestigate } from './mock';

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';

function transformBackendToAssessment(backendData: any): InvestigateResponse {
  if (backendData.status === 'clarification_needed') {
    return {
      type: 'clarification',
      question:
        (backendData.clarification_questions && backendData.clarification_questions[0]) ||
        'Please provide more details or headers for this message to proceed with the investigation.',
    };
  }

  const message = backendData.message || '';
  const findings: any[] = backendData.findings || [];
  const urlAnalysis: any[] = backendData.url_analysis || [];
  const reputation: any[] = backendData.reputation || [];
  const guidance: any[] = backendData.guidance || [];
  const attackSeq: any[] = backendData.attack_sequence || [];
  const risk = backendData.risk || { score: 10, level: 'low', breakdown: [] };

  const urls = urlAnalysis.map((u: any) => ({
    raw: u.url || '',
    defanged: u.url || '',
    host: u.normalized_host || '',
  }));

  const mapSpans = (spans: any[] = []): any[] =>
    spans.map((s: any) => ({
      start: typeof s.start === 'number' ? s.start : 0,
      end: typeof s.end === 'number' ? s.end : 0,
      text: s.text || '',
      source: 'analysis',
    }));

  const credFinding = findings.find((f: any) => f.id === 'SE-CREDS' || f.id === 'IND-SENSITIVE');
  const credStatus = credFinding ? credFinding.status : 'not_detected';
  const credEvidence = credFinding ? mapSpans(credFinding.source_evidence) : [];

  const urgencyFinding = findings.find((f: any) => f.id === 'SE-URGENCY');
  const urgencyStatus = urgencyFinding ? urgencyFinding.status : 'not_detected';
  const urgencyEvidence = urgencyFinding ? mapSpans(urgencyFinding.source_evidence) : [];

  const ipUrl = urlAnalysis.find((u: any) => u.is_ip);
  const ipStatus = ipUrl ? 'detected' : 'not_detected';
  const ipEvidence: any[] = [];
  if (ipUrl && ipUrl.url) {
    const rawIp = ipUrl.normalized_host || '';
    const idx = message.indexOf(rawIp);
    if (idx !== -1) {
      ipEvidence.push({ start: idx, end: idx + rawIp.length, text: rawIp, source: 'url_analysis' });
    }
  }

  const suspiciousRep = reputation.find((r: any) => r.status === 'suspicious');
  const unknownRep = reputation.find((r: any) => r.status === 'unknown');
  let domainStatus: 'detected' | 'not_detected' | 'not_assessable' = 'not_detected';
  let domainReason = 'Domains match trusted list';
  if (suspiciousRep) {
    domainStatus = 'detected';
    domainReason = `Domain ${suspiciousRep.hostname} is suspicious`;
  } else if (unknownRep) {
    domainStatus = 'not_assessable';
    domainReason = `Domain ${unknownRep.hostname} has unknown reputation`;
  } else if (urlAnalysis.length === 0) {
    domainStatus = 'not_detected';
    domainReason = 'No external links present';
  }

  const indicators = [
    {
      id: 'credential_request',
      label: 'Credential request',
      status: credStatus,
      reason: credFinding?.reason,
      evidence: credEvidence,
      tool: 'detect_social_engineering',
    },
    {
      id: 'urgency',
      label: 'Urgency',
      status: urgencyStatus,
      reason: urgencyFinding?.reason,
      evidence: urgencyEvidence,
      tool: 'detect_social_engineering',
    },
    {
      id: 'ip_address_link',
      label: 'IP-address link',
      status: ipStatus,
      reason: ipUrl ? 'Direct IP link detected' : undefined,
      evidence: ipEvidence,
      tool: 'analyze_url_structure',
    },
    {
      id: 'trusted_domain_mismatch',
      label: 'Trusted-domain mismatch',
      status: domainStatus,
      reason: domainReason,
      evidence: [],
      tool: 'check_domain_reputation',
    },
  ];

  const socialEngineering = findings
    .filter((f: any) => f.category === 'social_engineering')
    .map((f: any) => ({
      id: f.id,
      label: f.id.replace('SE-', '').replace('_', ' '),
      status: f.status,
      reason: f.reason,
      evidence: mapSpans(f.source_evidence),
      tool: 'detect_social_engineering',
    }));

  const domainReputation = reputation.map((r: any) => ({
    host: r.hostname,
    status:
      r.status === 'known_trusted'
        ? ('known_safe' as const)
        : r.status === 'suspicious'
        ? ('known_suspicious' as const)
        : ('unknown' as const),
    source: r.source,
    note: r.reason,
  }));

  const attackSequence = attackSeq.map((s: any) => ({
    step: s.description || `Step ${s.step}`,
    evidence: mapSpans(s.evidence_offsets || []),
  }));

  const guidanceList = guidance.map((g: any) => ({
    id: g.id,
    title: g.title,
    excerpt: g.excerpt,
  }));

  const riskBand: 'High' | 'Suspicious' | 'Low / Inconclusive' =
    risk.level === 'high' ? 'High' : risk.level === 'medium' ? 'Suspicious' : 'Low / Inconclusive';

  const riskResult = {
    score: risk.score || 0,
    band: riskBand,
    breakdown: (risk.breakdown || []).map((b: any) => ({
      rule: b.rule || '',
      points: b.points || 0,
    })),
  };

  const activity = (backendData.activity || []).map((a: any) => ({
    at: a.timestamp || new Date().toISOString(),
    kind: (a.type?.includes('call') ? 'tool_call' : a.status?.includes('fail') ? 'error' : 'tool_result') as any,
    tool_name: a.detail?.tool || undefined,
    summary: `${a.type || 'event'}: ${a.status || 'ok'}`,
    payload: a.detail,
  }));

  return {
    type: 'assessment',
    investigation_id: backendData.proposal_id || 'prop-unknown',
    message: message,
    urls: urls,
    indicators: indicators,
    social_engineering: socialEngineering,
    domain_reputation: domainReputation,
    attack_sequence: attackSequence,
    guidance: guidanceList,
    risk: riskResult,
    assessment: `Risk assessed as ${riskBand.toUpperCase()} (score ${risk.score}/100) via deterministic checks.`,
    next_steps: [
      'Do not click unverified links or enter credentials.',
      'Verify urgent requests via an independent out-of-band channel.',
      'Report confirmed phishing to the IT security operations team.',
    ],
    draft: backendData.guidance_draft || '',
    validation: { passed: true, issues: [] },
    activity: activity,
  };
}

export async function investigateMessage(request: InvestigateRequest): Promise<InvestigateResponse> {
  if (USE_MOCKS) {
    return mockInvestigate(request);
  }
  const data = await fetchApi<any>('/api/investigate', {
    method: 'POST',
    body: JSON.stringify({ message: request.message }),
  });
  return transformBackendToAssessment(data);
}
