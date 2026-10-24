import re
from urllib.parse import urlparse
from typing import Any

from app.schemas.tools import AnalyzeURLStructureInput, AnalyzeURLStructureOutput
from app.schemas.common import Finding, EvidenceSpan, URLAnalysis


# Match http/https URLs
URL_RE = re.compile(r"https?://[^\s<>\"]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s<>\"]*)?", re.IGNORECASE)


def _defang(url: str) -> str:
    return url.replace("http://", "hxxp://").replace("https://", "hxxps://").replace(".", "[.]")


def _span(text: str, start: int, end: int) -> EvidenceSpan:
    return EvidenceSpan(start=start, end=end, text=text[start:end])


def _parse_host(host: str) -> tuple[str | None, bool, bool, str | None]:
    if not host:
        return None, False, False, None
    has_user = "@" in host
    user_info = None
    if has_user:
        # user:pass@host or user@host
        user_info = host.split("@")[0]
        host = host.split("@")[-1]
    # remove port if present
    if ":" in host and not host.startswith("["):
        # simple case
        try:
            host = host.split(":")[0]
        except Exception:
            pass
    is_ip = re.match(r"^\d+\.\d+\.\d+\.\d+$", host) is not None
    return host.lower(), has_user, is_ip, user_info


def analyze_url_structure(input: AnalyzeURLStructureInput) -> AnalyzeURLStructureOutput:
    message = input.message
    findings: list[Finding] = []
    urls_found: list[str] = []
    analysis_list: list[dict[str, Any]] = []

    for m in URL_RE.finditer(message):
        raw = m.group()
        urls_found.append(raw)
        try:
            parsed = urlparse(raw if raw.startswith("http") else "http://" + raw)
        except Exception:
            parsed = urlparse("http://" + raw)

        host, has_user_info, is_ip, user_info = _parse_host(parsed.netloc)
        reasons = []
        suspicious = False
        if is_ip:
            suspicious = True
            reasons.append("URL uses IP address instead of domain")
        if has_user_info:
            suspicious = True
            reasons.append("URL contains user-info (possible trick like user@attacker)")
        if host and host.count(".") >= 3:
            # check for misleading subdomains - simple heuristic
            parts = host.split(".")
            if len(parts) > 3:
                reasons.append("Unusually deep subdomain structure")
        if host and "trusted.example" in host and host != "trusted.example":
            # could be misleading like trusted.example.attacker.example
            if not host.endswith(".trusted.example"):
                suspicious = True
                reasons.append("Misleading subdomain vs trusted domain")

        analysis_list.append(
            {
                "raw": raw,
                "defanged": _defang(raw),
                "normalized_host": host,
                "scheme": parsed.scheme,
                "path": parsed.path,
                "has_user_info": has_user_info,
                "user_info": user_info,
                "is_ip": is_ip,
                "suspicious": suspicious,
                "reasons": reasons,
            }
        )

    if urls_found:
        findings.append(
            Finding(
                id="URL-ANALYSIS",
                category="urls",
                status="detected",
                reason=f"Found {len(urls_found)} URL(s)",
                source_evidence=[_span(message, m.start(), m.end()) for m in URL_RE.finditer(message)],
                tool="analyze_url_structure",
            )
        )
    else:
        findings.append(
            Finding(
                id="URL-ANALYSIS",
                category="urls",
                status="not_detected",
                reason="No URLs found",
                tool="analyze_url_structure",
            )
        )

    url_analysis = [
        URLAnalysis(
            url=a["defanged"],
            normalized_host=a["normalized_host"],
            is_ip=a["is_ip"],
            has_user_info=a["has_user_info"],
            user_info=a["user_info"],
            suspicious=a["suspicious"],
            reasons=a["reasons"],
        )
        for a in analysis_list
    ]

    return AnalyzeURLStructureOutput(urls=urls_found, analysis=analysis_list, findings=findings)
