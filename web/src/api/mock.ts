import { InvestigateRequest, InvestigateResponse, Assessment, IncidentSummary, IncidentDetail, CreateIncidentRequest } from '../types/api';

// In-memory incidents list for mock
let mockIncidents: IncidentDetail[] = [];
let incidentCounter = 0;

// Helper to generate incident ID
function generateIncidentId(): string {
  incidentCounter++;
  return `INC-${incidentCounter.toString().padStart(4, '0')}`;
}

// Sample High Risk assessment for password request
const createHighRiskAssessment = (message: string, investigationId: string): Assessment => {
  return {
    type: "assessment",
    investigation_id: investigationId,
    message: message,
    urls: [
      {
        raw: "https://northwind-login.example/verify",
        defanged: "hxxps://northwind-login[.]example/verify",
        host: "northwind-login.example"
      }
    ],
    indicators: [
      {
        id: "credential_request",
        label: "Credential request",
        status: "detected",
        evidence: [
          { start: message.indexOf("Verify your password"), end: message.indexOf("Verify your password") + "Verify your password".length, text: "Verify your password", source: "pattern" }
        ],
        tool: "pattern_matcher"
      },
      {
        id: "urgency",
        label: "Urgency",
        status: "detected",
        evidence: [
          { start: message.indexOf("detected unusual activity"), end: message.indexOf("detected unusual activity") + "detected unusual activity".length, text: "detected unusual activity", source: "pattern" }
        ],
        tool: "pattern_matcher"
      },
      {
        id: "ip_address_link",
        label: "IP-address link",
        status: "not_detected",
        evidence: [],
        tool: "url_analyzer"
      },
      {
        id: "trusted_domain_mismatch",
        label: "Trusted-domain mismatch",
        status: "not_detected",
        evidence: [],
        tool: "domain_analyzer"
      }
    ],
    social_engineering: [
      {
        id: "authority",
        label: "Authority impersonation",
        status: "detected",
        evidence: [
          { start: message.indexOf("Northwind IT"), end: message.indexOf("Northwind IT") + "Northwind IT".length, text: "Northwind IT", source: "nlp" }
        ],
        tool: "nlp_classifier"
      },
      {
        id: "fear",
        label: "Fear tactics",
        status: "detected",
        evidence: [
          { start: message.indexOf("detected unusual activity"), end: message.indexOf("detected unusual activity") + "detected unusual activity".length, text: "detected unusual activity", source: "nlp" }
        ],
        tool: "nlp_classifier"
      }
    ],
    domain_reputation: [
      {
        host: "northwind-login.example",
        status: "unknown",
        source: "reputation_db",
        note: "Domain not in known safe list"
      }
    ],
    attack_sequence: [
      {
        step: "Initial contact impersonating IT department",
        evidence: [{ start: message.indexOf("Northwind IT"), end: message.indexOf("Northwind IT") + "Northwind IT".length, text: "Northwind IT", source: "pattern" }]
      },
      {
        step: "Create sense of urgency/fear",
        evidence: [{ start: message.indexOf("detected unusual activity"), end: message.indexOf("detected unusual activity") + "detected unusual activity".length, text: "detected unusual activity", source: "pattern" }]
      },
      {
        step: "Request credential verification",
        evidence: [{ start: message.indexOf("Verify your password"), end: message.indexOf("Verify your password") + "Verify your password".length, text: "Verify your password", source: "pattern" }]
      }
    ],
    guidance: [
      {
        id: "G-001",
        title: "Verify requests through official channels",
        excerpt: "Always contact the organization directly through official phone numbers or websites, not through links provided in suspicious messages."
      },
      {
        id: "G-002",
        title: "Never share passwords via email",
        excerpt: "Legitimate organizations will never ask you to verify or share passwords via email or text messages."
      }
    ],
    risk: {
      score: 85,
      band: "High",
      breakdown: [
        { rule: "Credential request", points: 30 },
        { rule: "Authority impersonation", points: 25 },
        { rule: "Urgency/fear tactics", points: 20 },
        { rule: "Suspicious domain", points: 10 }
      ]
    },
    assessment: "This message exhibits multiple characteristics of a phishing attempt. It impersonates IT support, creates urgency, and requests password verification through a suspicious domain. This is consistent with credential harvesting attacks.",
    next_steps: [
      "Do not click the link or provide any credentials",
      "Report this message to your IT security team",
      "Delete the message and scan your device if credentials were entered",
      "Block the sender if possible"
    ],
    draft: "Subject: Report of suspicious message\n\nHi IT Security Team,\n\nI received a suspicious message claiming to be from Northwind IT asking me to verify my password. The message contained a link to northwind-login.example. Please investigate.\n\nThank you.",
    validation: {
      passed: true,
      issues: []
    },
    activity: [
      { at: new Date().toISOString(), kind: "tool_call", tool_name: "pattern_matcher", summary: "Scanning for phishing patterns" },
      { at: new Date().toISOString(), kind: "tool_result", tool_name: "pattern_matcher", summary: "Found credential request and urgency indicators" },
      { at: new Date().toISOString(), kind: "tool_call", tool_name: "url_analyzer", summary: "Analyzing extracted URLs" },
      { at: new Date().toISOString(), kind: "tool_result", tool_name: "url_analyzer", summary: "URL extracted, domain reputation unknown" },
      { at: new Date().toISOString(), kind: "tool_call", tool_name: "nlp_classifier", summary: "Classifying social engineering tactics" },
      { at: new Date().toISOString(), kind: "tool_result", tool_name: "nlp_classifier", summary: "Identified authority and fear tactics" }
    ]
  };
};

// IP link assessment
const createIpLinkAssessment = (message: string, investigationId: string): Assessment => {
  return {
    type: "assessment",
    investigation_id: investigationId,
    message: message,
    urls: [
      {
        raw: "http://192.0.2.15/login",
        defanged: "hxxp://192[.]0[.]2[.]15/login",
        host: "192.0.2.15"
      }
    ],
    indicators: [
      {
        id: "credential_request",
        label: "Credential request",
        status: "not_detected",
        evidence: [],
        tool: "pattern_matcher"
      },
      {
        id: "urgency",
        label: "Urgency",
        status: "detected",
        evidence: [
          { start: message.indexOf("suspended within 24 hours"), end: message.indexOf("suspended within 24 hours") + "suspended within 24 hours".length, text: "suspended within 24 hours", source: "pattern" }
        ],
        tool: "pattern_matcher"
      },
      {
        id: "ip_address_link",
        label: "IP-address link",
        status: "detected",
        evidence: [
          { start: message.indexOf("http://192.0.2.15/login"), end: message.indexOf("http://192.0.2.15/login") + "http://192.0.2.15/login".length, text: "http://192.0.2.15/login", source: "url" }
        ],
        tool: "url_analyzer"
      },
      {
        id: "trusted_domain_mismatch",
        label: "Trusted-domain mismatch",
        status: "not_assessable",
        reason: "Host is an IP address; cannot evaluate domain trust",
        evidence: [
          { start: message.indexOf("http://192.0.2.15/login"), end: message.indexOf("http://192.0.2.15/login") + "http://192.0.2.15/login".length, text: "http://192.0.2.15/login", source: "url" }
        ],
        tool: "domain_analyzer"
      }
    ],
    social_engineering: [
      {
        id: "fear",
        label: "Fear tactics",
        status: "detected",
        evidence: [
          { start: message.indexOf("suspended"), end: message.indexOf("suspended") + "suspended".length, text: "suspended", source: "nlp" }
        ],
        tool: "nlp_classifier"
      }
    ],
    domain_reputation: [
      {
        host: "192.0.2.15",
        status: "unknown",
        source: "reputation_db",
        note: "IP address, not a domain"
      }
    ],
    attack_sequence: [
      {
        step: "Create fear of service suspension",
        evidence: [{ start: message.indexOf("Your mailbox will be suspended"), end: message.indexOf("Your mailbox will be suspended") + "Your mailbox will be suspended".length, text: "Your mailbox will be suspended", source: "pattern" }]
      },
      {
        step: "Pressure for immediate action",
        evidence: [{ start: message.indexOf("within 24 hours"), end: message.indexOf("within 24 hours") + "within 24 hours".length, text: "within 24 hours", source: "pattern" }]
      },
      {
        step: "Direct to IP-based login page",
        evidence: [{ start: message.indexOf("http://192.0.2.15/login"), end: message.indexOf("http://192.0.2.15/login") + "http://192.0.2.15/login".length, text: "http://192.0.2.15/login", source: "url" }]
      }
    ],
    guidance: [
      {
        id: "G-003",
        title: "Legitimate services use domain names",
        excerpt: "Most legitimate email providers do not send login links to IP addresses. Be suspicious of such messages."
      }
    ],
    risk: {
      score: 65,
      band: "Suspicious",
      breakdown: [
        { rule: "IP-address link", points: 35 },
        { rule: "Urgency/fear tactics", points: 20 },
        { rule: "Domain trust unassessable", points: 10 }
      ]
    },
    assessment: "This message uses urgency tactics and directs users to an IP address rather than a proper domain. This is a common tactic in phishing attacks to bypass domain reputation checks.",
    next_steps: [
      "Do not click the link",
      "Contact your email provider directly through official channels",
      "Report the message as phishing"
    ],
    draft: "Subject: Suspicious message with IP link\n\nI received a message claiming my mailbox will be suspended and directing me to http://192.0.2.15/login. This appears suspicious as it uses an IP address. Please investigate.",
    validation: {
      passed: false,
      issues: ["No clear credential request detected but high-risk indicators present"]
    },
    activity: [
      { at: new Date().toISOString(), kind: "tool_call", tool_name: "url_analyzer", summary: "Analyzing URL format" },
      { at: new Date().toISOString(), kind: "tool_result", tool_name: "url_analyzer", summary: "IP address detected in URL" },
      { at: new Date().toISOString(), kind: "tool_call", tool_name: "domain_analyzer", summary: "Checking domain trust" },
      { at: new Date().toISOString(), kind: "tool_result", tool_name: "domain_analyzer", summary: "Cannot assess - IP address" }
    ]
  };
};

const createLowInconclusiveAssessment = (message: string, investigationId: string): Assessment => {
  return {
    type: "assessment",
    investigation_id: investigationId,
    message: message,
    urls: [
      {
        raw: "https://hr.northwind-corp.test/events",
        defanged: "hxxps://hr[.]northwind-corp[.]test/events",
        host: "hr.northwind-corp.test"
      }
    ],
    indicators: [
      { id: "credential_request", label: "Credential request", status: "not_detected", evidence: [], tool: "pattern_matcher" },
      { id: "urgency", label: "Urgency", status: "not_detected", evidence: [], tool: "pattern_matcher" },
      { id: "ip_address_link", label: "IP-address link", status: "not_detected", evidence: [], tool: "url_analyzer" },
      { id: "trusted_domain_mismatch", label: "Trusted-domain mismatch", status: "not_detected", evidence: [], tool: "domain_analyzer" }
    ],
    social_engineering: [],
    domain_reputation: [
      {
        host: "hr.northwind-corp.test",
        status: "unknown",
        source: "reputation_db",
        note: "Not in known safe list"
      }
    ],
    attack_sequence: [],
    guidance: [
      {
        id: "G-004",
        title: "Verify unexpected requests",
        excerpt: "Even legitimate-looking messages can be spoofed. When in doubt, verify through another channel."
      }
    ],
    risk: {
      score: 10,
      band: "Low / Inconclusive",
      breakdown: [
        { rule: "No strong phishing indicators", points: 0 }
      ]
    },
    assessment: "No clear phishing indicators were detected in this message. However, the domain is not in our known-safe list, so caution is advised. This analysis is inconclusive.",
    next_steps: [
      "Verify the sender through an official channel if unexpected",
      "Proceed with normal caution"
    ],
    draft: "Subject: Inquiry about message\n\nI received a message regarding the all-hands meeting. Can you confirm if this is legitimate?",
    validation: {
      passed: true,
      issues: []
    },
    activity: [
      { at: new Date().toISOString(), kind: "tool_call", tool_name: "pattern_matcher", summary: "Scanning message" },
      { at: new Date().toISOString(), kind: "tool_result", tool_name: "pattern_matcher", summary: "No phishing patterns detected" }
    ]
  };
};

export async function mockInvestigate(request: InvestigateRequest): Promise<InvestigateResponse> {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 600 + Math.random() * 600));
  
  // Forced error when message contains "[force-error]"
  if (request.message.includes('[force-error]')) {
    throw new Error('Simulated API error: Analysis failed due to service interruption');
  }
  
  // Clarification when message is under 20 characters
  if (request.message.trim().length < 20) {
    return {
      type: "clarification",
      question: "The message is very short. Could you provide more context - who sent it, or include the full message with any links or headers?"
    };
  }
  
  const investigationId = `INV-${Date.now().toString().slice(-6)}`;
  
  // Sample password request (High Risk)
  if (request.message.includes("password") && request.message.includes("verify")) {
    return createHighRiskAssessment(request.message, investigationId);
  }
  
  // IP link
  if (request.message.includes("192.0.2")) {
    return createIpLinkAssessment(request.message, investigationId);
  }
  
  // Default to low/inconclusive
  return createLowInconclusiveAssessment(request.message, investigationId);
}

export async function mockCreateIncident(request: CreateIncidentRequest): Promise<{ id: string; status: string }> {
  await new Promise(resolve => setTimeout(resolve, 400));
  
  const id = generateIncidentId();
  const now = new Date().toISOString();
  
  const incident: IncidentDetail = {
    id: id,
    created_at: now,
    risk_band: request.assessment.risk.band,
    status: "Pending review",
    reviewed_by: request.reviewed_by,
    approved_at: now,
    draft_edited: request.draft_edited,
    assessment: request.assessment,
    final_draft: request.draft
  };
  
  mockIncidents.unshift(incident);
  return { id, status: "Pending review" };
}

export async function mockGetIncidents(): Promise<IncidentSummary[]> {
  await new Promise(resolve => setTimeout(resolve, 300));
  return mockIncidents.map(inc => ({
    id: inc.id,
    created_at: inc.created_at,
    risk_band: inc.risk_band,
    status: inc.status,
    reviewed_by: inc.reviewed_by
  }));
}

export async function mockGetIncident(id: string): Promise<IncidentDetail> {
  await new Promise(resolve => setTimeout(resolve, 300));
  const incident = mockIncidents.find(inc => inc.id === id);
  if (!incident) {
    throw new Error('Incident not found');
  }
  return incident;
}
