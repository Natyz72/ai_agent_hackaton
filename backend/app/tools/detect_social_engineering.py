import re
from app.schemas.tools import DetectSocialEngineeringInput, DetectSocialEngineeringOutput
from app.schemas.common import Finding, EvidenceSpan


URGENT = re.compile(r"\b(urgent|immediately|act now|expires (today|soon)|suspended|locked|final warning)\b", re.IGNORECASE)
THREAT = re.compile(r"\b(arrest|police|lawsuit|penalty|fine|tax|irs)\b", re.IGNORECASE)
CRED = re.compile(r"\b(password|pin|otp|mfa code|login|credentials|bank details|card number)\b", re.IGNORECASE)
PAYMENT = re.compile(r"\b(wire transfer|gift card|bitcoin|crypto|payment method|change.*payment)\b", re.IGNORECASE)
AUTHORITY = re.compile(r"\b(ceo|hr|it support|manager|administrator)\b", re.IGNORECASE)


def _span(text: str, start: int, end: int) -> EvidenceSpan:
    return EvidenceSpan(start=start, end=end, text=text[start:end])


def detect_social_engineering(input: DetectSocialEngineeringInput) -> DetectSocialEngineeringOutput:
    message = input.message
    findings: list[Finding] = []
    tactics: list[dict] = []

    def check(pattern, name, reason):
        spans = []
        for m in pattern.finditer(message):
            spans.append(_span(message, m.start(), m.end()))
            tactics.append({"tactic": name, "match": m.group(), "start": m.start(), "end": m.end()})
        if spans:
            findings.append(
                Finding(
                    id=f"SE-{name.upper().replace(' ', '_')}",
                    category="social_engineering",
                    status="detected",
                    reason=reason,
                    source_evidence=spans,
                    tool="detect_social_engineering",
                )
            )
        else:
            findings.append(
                Finding(
                    id=f"SE-{name.upper().replace(' ', '_')}",
                    category="social_engineering",
                    status="not_detected",
                    reason=f"No {name} indicators",
                    tool="detect_social_engineering",
                )
            )

    check(URGENT, "urgency", "Urgency/pressure tactic detected")
    check(THREAT, "threat", "Threat/authority fear tactic detected")
    check(CRED, "credential_request", "Credential/request for sensitive info detected")
    check(PAYMENT, "payment_redirect", "Unusual payment method request detected")
    check(AUTHORITY, "impersonation", "Authority/impersonation indicators detected")

    return DetectSocialEngineeringOutput(findings=findings, tactics=tactics)
