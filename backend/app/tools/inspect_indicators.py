import re
from typing import Any

from app.schemas.tools import InspectIndicatorsInput, InspectIndicatorsOutput
from app.schemas.common import Finding, EvidenceSpan


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b\+?\d[\d\s().-]{7,}\d\b")
CRED_WORDS = ["password", "passwd", "pin", "otp", "mfa code", "login", "credentials", "ssn", "social security"]
URGENT_WORDS = ["urgent", "immediately", "act now", "expires", "suspended", "locked", "verify now"]


def _span(text: str, start: int, end: int) -> EvidenceSpan:
    return EvidenceSpan(start=start, end=end, text=text[start:end])


def inspect_indicators(input: InspectIndicatorsInput) -> InspectIndicatorsOutput:
    message = input.message
    findings: list[Finding] = []
    indicators: list[dict[str, Any]] = []

    # Emails
    for m in EMAIL_RE.finditer(message):
        indicators.append({"type": "email", "value": m.group(), "start": m.start(), "end": m.end()})
    if indicators:
        findings.append(
            Finding(
                id="IND-EMAIL",
                category="indicators",
                status="detected",
                reason="Email addresses present in message",
                source_evidence=[_span(message, i["start"], i["end"]) for i in indicators if i["type"] == "email"],
                tool="inspect_indicators",
            )
        )
    else:
        findings.append(
            Finding(
                id="IND-EMAIL",
                category="indicators",
                status="not_detected",
                reason="No email addresses found",
                tool="inspect_indicators",
            )
        )

    # Credentials/urgent
    lower = message.lower()
    cred_hits = [w for w in CRED_WORDS if w in lower]
    urgent_hits = [w for w in URGENT_WORDS if w in lower]
    if cred_hits or urgent_hits:
        findings.append(
            Finding(
                id="IND-SENSITIVE",
                category="indicators",
                status="detected",
                reason=f"Sensitive/urgent terms: creds={cred_hits}, urgent={urgent_hits}",
                tool="inspect_indicators",
            )
        )
    else:
        findings.append(
            Finding(
                id="IND-SENSITIVE",
                category="indicators",
                status="not_detected",
                reason="No obvious credential/urgent terms",
                tool="inspect_indicators",
            )
        )

    return InspectIndicatorsOutput(findings=findings, indicators=indicators)
