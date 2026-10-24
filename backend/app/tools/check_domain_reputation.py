import re
from typing import Any

from app.schemas.tools import CheckDomainReputationInput, CheckDomainReputationOutput
from app.schemas.common import Finding
from app.db.repositories import Repository


def _normalize_hostname(hostname: str) -> str:
    h = hostname.strip().lower()
    if "://" in h:
        h = h.split("://", 1)[1]
    h = h.split("/", 1)[0]
    if "@" in h:
        h = h.split("@")[-1]
    if ":" in h and not h.startswith("["):
        h = h.split(":", 1)[0]
    return h.rstrip(".")


def check_domain_reputation(
    input: CheckDomainReputationInput,
    repo: Repository | None = None,
) -> CheckDomainReputationOutput:
    if repo is None:
        repo = Repository()

    results: list[dict[str, Any]] = []
    findings: list[Finding] = []

    for raw_host in input.hostnames:
        norm_host = _normalize_hostname(raw_host)
        if not norm_host:
            continue

        entry = repo.get_domain_reputation(norm_host)
        if entry:
            status = entry.get("status", "unknown")
            source = entry.get("source", "database")
            reason = entry.get("reason", f"Reputation entry found for {norm_host}")
        else:
            trusted = False
            for td in repo.get_trusted_domains():
                t_dom = td.get("domain", "").lower()
                if norm_host == t_dom or norm_host.endswith("." + t_dom):
                    trusted = True
                    break
            if trusted:
                status = "known_trusted"
                source = "trusted_domains"
                reason = f"Domain {norm_host} matches trusted domains list"
            else:
                status = "unknown"
                source = "local_lookup"
                reason = f"No reputation data found for {norm_host} (unknown status)"

        res_dict = {
            "hostname": norm_host,
            "status": status,
            "source": source,
            "reason": reason,
        }
        results.append(res_dict)

        if status == "suspicious":
            f_status = "detected"
            f_reason = f"Domain {norm_host} flagged as suspicious: {reason}"
        elif status == "known_trusted":
            f_status = "not_detected"
            f_reason = f"Domain {norm_host} is known trusted: {reason}"
        else:
            # Per AGENTS.md: unknown means unknown, not safe or malicious
            f_status = "not_assessable"
            f_reason = f"Domain {norm_host} reputation is unknown: {reason}"

        findings.append(
            Finding(
                id=f"REP-{norm_host}",
                category="domain_reputation",
                status=f_status,
                reason=f_reason,
                tool="check_domain_reputation",
            )
        )

    return CheckDomainReputationOutput(results=results, findings=findings)
