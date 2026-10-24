from typing import Any

from app.schemas.tools import SearchGuidanceInput, SearchGuidanceOutput
from app.schemas.common import Finding
from app.db.repositories import Repository


def search_guidance(
    input: SearchGuidanceInput,
    repo: Repository | None = None,
) -> SearchGuidanceOutput:
    if repo is None:
        repo = Repository()

    query = input.query.strip()
    passages: list[dict[str, Any]] = []

    if query:
        passages = repo.search_guidance(query)

    # If no passages found or additional context available, search for relevant terms
    if not passages and input.findings_context:
        for finding in input.findings_context:
            cat = finding.get("category", "")
            reason = finding.get("reason", "")
            for term in [cat, reason]:
                if term:
                    # Look up individual keywords if needed
                    for word in term.split():
                        clean_word = word.strip(".,;:\"'()[]{}")
                        if len(clean_word) > 3:
                            hits = repo.search_guidance(clean_word)
                            for h in hits:
                                if not any(p.get("id") == h.get("id") for p in passages):
                                    passages.append(h)

    formatted_guidance: list[dict[str, Any]] = []
    for p in passages:
        # Guarantee real DB passage ID is preserved and never fabricated
        pid = p.get("id")
        if not pid:
            continue
        formatted_guidance.append({
            "id": str(pid),
            "title": p.get("title", ""),
            "content": p.get("content") or p.get("text", ""),
            "excerpt": p.get("excerpt") or ((p.get("content") or "")[:120] + "..."),
            "reason": f"Matches guidance query '{query}'" if query else "Matched from findings context",
        })

    findings: list[Finding] = []
    if formatted_guidance:
        found_ids = [g["id"] for g in formatted_guidance]
        findings.append(
            Finding(
                id="GUID-RETRIEVAL",
                category="guidance",
                status="detected",
                reason=f"Retrieved {len(formatted_guidance)} guidance passage(s): {', '.join(found_ids)}",
                evidence_ids=found_ids,
                tool="search_guidance",
            )
        )
    else:
        findings.append(
            Finding(
                id="GUID-RETRIEVAL",
                category="guidance",
                status="not_detected",
                reason=f"No matching guidance passages found for query '{query}'",
                tool="search_guidance",
            )
        )

    return SearchGuidanceOutput(guidance=formatted_guidance, findings=findings)
