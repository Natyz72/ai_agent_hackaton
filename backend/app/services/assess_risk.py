from typing import Any
from app.schemas.common import Finding, RiskAssessment, RiskBreakdownItem


def assess_risk(
    findings: list[Finding | dict[str, Any]],
    urls_analysis: list[dict[str, Any]] | None = None,
    reputation_results: list[dict[str, Any]] | None = None,
) -> RiskAssessment:
    """
    Deterministic, explainable risk scoring heuristic based purely on verified findings.
    Missing data or absence of signals does NOT lower the score.
    """
    score = 0
    breakdown: list[RiskBreakdownItem] = []
    notes: list[str] = [
        "Score is calculated using a deterministic rule-based heuristic, not a statistical probability."
    ]

    # Convert findings to Finding instances if needed
    finding_objs = [f if isinstance(f, Finding) else Finding(**f) for f in findings]
    detected_ids = {f.id for f in finding_objs if f.status == "detected"}

    # 1. URL Analysis Rules
    if urls_analysis:
        for u in urls_analysis:
            if u.get("is_ip"):
                breakdown.append(
                    RiskBreakdownItem(
                        rule="url_ip_host",
                        points=25,
                        reason="URL contains direct IP address host",
                    )
                )
                score += 25
            if u.get("has_user_info"):
                breakdown.append(
                    RiskBreakdownItem(
                        rule="url_user_info_spoof",
                        points=30,
                        reason="URL uses '@' user-info trick to disguise true destination host",
                    )
                )
                score += 30
            if any("subdomain" in r.lower() for r in u.get("reasons", [])):
                breakdown.append(
                    RiskBreakdownItem(
                        rule="url_misleading_subdomain",
                        points=20,
                        reason="URL features misleading subdomain structure",
                    )
                )
                score += 20
            elif u.get("suspicious") and not u.get("is_ip") and not u.get("has_user_info"):
                breakdown.append(
                    RiskBreakdownItem(
                        rule="url_suspicious_features",
                        points=20,
                        reason="URL displays suspicious attributes",
                    )
                )
                score += 20

    # 2. Domain Reputation Rules
    if reputation_results:
        has_unknown = False
        for r in reputation_results:
            status = r.get("status")
            host = r.get("hostname", "")
            if status == "suspicious":
                breakdown.append(
                    RiskBreakdownItem(
                        rule="domain_reputation_suspicious",
                        points=35,
                        reason=f"Hostname '{host}' is flagged as suspicious in reputation database",
                    )
                )
                score += 35
            elif status == "unknown":
                has_unknown = True
        if has_unknown:
            notes.append("One or more domains have unknown reputation; score was not decreased.")

    # 3. Social Engineering Rules
    if "SE-CREDS" in detected_ids:
        breakdown.append(
            RiskBreakdownItem(
                rule="social_eng_credentials",
                points=30,
                reason="Message explicitly requests credentials, authentication codes, or login action",
            )
        )
        score += 30

    if "SE-URGENCY" in detected_ids:
        breakdown.append(
            RiskBreakdownItem(
                rule="social_eng_urgency",
                points=20,
                reason="Message creates artificial urgency or coercive deadlines to pressure recipient",
            )
        )
        score += 20

    if "SE-PAYMENT" in detected_ids:
        breakdown.append(
            RiskBreakdownItem(
                rule="social_eng_payment",
                points=25,
                reason="Message requests urgent or unverified financial payment or account routing changes",
            )
        )
        score += 25

    # 4. Sensitive Indicators Rule
    if "IND-SENSITIVE" in detected_ids:
        breakdown.append(
            RiskBreakdownItem(
                rule="indicators_sensitive",
                points=15,
                reason="Message contains sensitive keywords and indicators",
            )
        )
        score += 15

    # Deduplicate rules if multiple triggers fired identical rules
    seen_rules = set()
    deduped_breakdown = []
    total_score = 0
    for item in breakdown:
        key = (item.rule, item.reason)
        if key not in seen_rules:
            seen_rules.add(key)
            deduped_breakdown.append(item)
            total_score += item.points

    total_score = max(0, min(100, total_score))

    if total_score >= 60:
        level = "high"
    elif total_score >= 30:
        level = "medium"
    else:
        level = "low"

    return RiskAssessment(
        level=level,
        score=total_score,
        heuristic=True,
        breakdown=deduped_breakdown,
        notes=notes,
    )
