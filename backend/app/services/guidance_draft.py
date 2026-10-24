from typing import Any
from app.schemas.common import Finding, RiskAssessment, GuidanceRef


def generate_guidance_draft(
    risk: RiskAssessment,
    findings: list[Finding | dict[str, Any]],
    guidance_refs: list[GuidanceRef | dict[str, Any]] | None = None,
) -> str:
    """
    Drafts clear, actionable user and analyst guidance citing verified handbook passage IDs.
    """
    lines = [
        f"### Investigation Guidance Summary (Risk: {risk.level.upper()})",
        "",
    ]

    finding_objs = [f if isinstance(f, Finding) else Finding(**f) for f in findings]
    detected_ids = {f.id for f in finding_objs if f.status == "detected"}

    # Core user warnings based on detected tactics
    lines.append("**Immediate Recommendations:**")
    if "SE-CREDS" in detected_ids or "IND-SENSITIVE" in detected_ids:
        lines.append("- Do NOT click any links, open attachments, or input passwords/MFA codes.")
    if "SE-PAYMENT" in detected_ids:
        lines.append("- Do NOT initiate or approve any financial wire transfers or payment detail changes.")
    if "SE-URGENCY" in detected_ids:
        lines.append("- Beware of artificial urgency; verify the legitimacy of this communication via independent out-of-band contact.")

    if not any(f.status == "detected" for f in finding_objs):
        lines.append("- No obvious malicious indicators were detected. However, remain vigilant and report any unexpected requests.")

    # Cite verified guidance passages
    if guidance_refs:
        lines.append("")
        lines.append("**Applicable Security Handbook Policies:**")
        for g in guidance_refs:
            gid = g.id if isinstance(g, GuidanceRef) else g.get("id", "")
            title = g.title if isinstance(g, GuidanceRef) else g.get("title", "")
            excerpt = g.excerpt if isinstance(g, GuidanceRef) else g.get("excerpt", "")
            lines.append(f"- **[{gid}] {title}**: {excerpt}")

    lines.append("")
    lines.append("**Next Steps:** Preserve the original message headers and escalate to the security operations team if further analysis is required.")

    return "\n".join(lines)
