from typing import Any
from app.schemas.tools import MapAttackSequenceInput, MapAttackSequenceOutput
from app.schemas.common import Finding, AttackStep, EvidenceSpan
from app.services.evidence import is_valid_span


def map_attack_sequence(input: MapAttackSequenceInput) -> MapAttackSequenceOutput:
    message = input.message
    findings = input.findings

    steps: list[dict[str, Any]] = []
    step_num = 1

    # Map findings into logical attack phases
    # Step 1: Initial contact / Delivery
    delivery_findings = [f for f in findings if f.get("category") in ("indicators", "delivery") and f.get("status") == "detected"]
    delivery_spans = []
    delivery_ids = []
    for f in delivery_findings:
        delivery_ids.append(f.get("id", ""))
        for s in f.get("source_evidence", []):
            if is_valid_span(s, message):
                delivery_spans.append(s)

    if delivery_findings or len(message) > 0:
        steps.append({
            "step": step_num,
            "description": "Attacker initiates contact via unsolicited communication containing external indicators",
            "evidence_ids": [fid for fid in delivery_ids if fid],
            "evidence_offsets": delivery_spans,
        })
        step_num += 1

    # Step 2: Psychological manipulation (Urgency / Social Engineering)
    se_findings = [f for f in findings if f.get("category") == "social_engineering" and f.get("status") == "detected"]
    se_spans = []
    se_ids = []
    for f in se_findings:
        se_ids.append(f.get("id", ""))
        for s in f.get("source_evidence", []):
            if is_valid_span(s, message):
                se_spans.append(s)

    if se_findings:
        steps.append({
            "step": step_num,
            "description": "Attacker introduces urgency, authority, or pretext to induce impulsive recipient compliance",
            "evidence_ids": [fid for fid in se_ids if fid],
            "evidence_offsets": se_spans,
        })
        step_num += 1

    # Step 3: Deceptive Link / Malicious Infrastructure
    url_findings = [f for f in findings if f.get("category") in ("url_structure", "domain_reputation") and f.get("status") == "detected"]
    url_spans = []
    url_ids = []
    for f in url_findings:
        url_ids.append(f.get("id", ""))
        for s in f.get("source_evidence", []):
            if is_valid_span(s, message):
                url_spans.append(s)

    if url_findings:
        steps.append({
            "step": step_num,
            "description": "Attacker directs recipient toward untrusted or deceptive external URL destination",
            "evidence_ids": [fid for fid in url_ids if fid],
            "evidence_offsets": url_spans,
        })
        step_num += 1

    # Step 4: Credential Harvesting or Financial Exfiltration
    cred_findings = [f for f in findings if ("cred" in f.get("id", "").lower() or "pay" in f.get("id", "").lower() or "sensitive" in f.get("id", "").lower()) and f.get("status") == "detected"]
    cred_spans = []
    cred_ids = []
    for f in cred_findings:
        cred_ids.append(f.get("id", ""))
        for s in f.get("source_evidence", []):
            if is_valid_span(s, message):
                cred_spans.append(s)

    if cred_findings:
        steps.append({
            "step": step_num,
            "description": "Attacker attempts to harvest credentials or redirect payment/sensitive information",
            "evidence_ids": [fid for fid in cred_ids if fid],
            "evidence_offsets": cred_spans,
        })
        step_num += 1

    all_evidence_ids: list[str] = []
    for s in steps:
        for eid in s.get("evidence_ids", []):
            if eid and eid not in all_evidence_ids:
                all_evidence_ids.append(eid)

    output_findings: list[Finding] = [
        Finding(
            id="ATK-SEQUENCE",
            category="attack_sequence",
            status="detected" if steps else "not_detected",
            reason=f"Mapped {len(steps)} potential attacker tactic phases from evidence (no recipient action implied)",
            evidence_ids=all_evidence_ids,
            tool="map_attack_sequence",
        )
    ]

    return MapAttackSequenceOutput(steps=steps, findings=output_findings)
