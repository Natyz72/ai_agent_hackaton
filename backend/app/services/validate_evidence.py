from typing import Any
from app.schemas.common import Finding, EvidenceSpan, GuidanceRef
from app.services.evidence import is_valid_span
from app.db.repositories import Repository


VALID_STATUSES = {"detected", "not_detected", "not_assessable"}


def validate_evidence(
    message: str,
    findings: list[Finding | dict[str, Any]],
    guidance_refs: list[GuidanceRef | dict[str, Any]] | None = None,
    repo: Repository | None = None,
) -> tuple[list[Finding], list[str]]:
    """
    App-controlled validation:
    1. Validates that every evidence offset falls strictly within message bounds and matches text.
    2. Verifies that every cited guidance ID exists in the database (rejects invented IDs).
    3. Verifies finding status consistency.
    """
    validated_findings: list[Finding] = []
    warnings: list[str] = []

    for item in findings:
        f = item if isinstance(item, Finding) else Finding(**item)

        # 1. Validate status
        if f.status not in VALID_STATUSES:
            warnings.append(f"Finding {f.id} had invalid status '{f.status}'; default to not_assessable")
            f.status = "not_assessable"

        # 2. Validate evidence spans
        valid_spans: list[EvidenceSpan] = []
        for span in f.source_evidence:
            if is_valid_span(span, message):
                valid_spans.append(span if isinstance(span, EvidenceSpan) else EvidenceSpan(**span))
            else:
                warnings.append(
                    f"Finding {f.id} contained invalid span [{getattr(span, 'start', None)}:{getattr(span, 'end', None)}] "
                    f"exceeding text length ({len(message)}) or mismatching text"
                )

        f.source_evidence = valid_spans

        # 3. Validate guidance IDs if this is a guidance finding
        if f.category == "guidance" and f.evidence_ids and repo:
            verified_ids: list[str] = []
            for gid in f.evidence_ids:
                if isinstance(gid, str):
                    passage = repo.get_guidance_by_id(gid)
                    if passage:
                        verified_ids.append(gid)
                    else:
                        warnings.append(f"Rejected invented or non-existent guidance ID '{gid}'")
            f.evidence_ids = verified_ids

        validated_findings.append(f)

    # 4. Validate guidance_refs if supplied
    if guidance_refs and repo:
        for g in guidance_refs:
            gid = g.id if isinstance(g, GuidanceRef) else g.get("id")
            if gid and not repo.get_guidance_by_id(gid):
                warnings.append(f"Guidance reference '{gid}' does not exist in repository")

    return validated_findings, warnings
