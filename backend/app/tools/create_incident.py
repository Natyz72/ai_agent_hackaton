from datetime import datetime, timezone
from typing import Any
import uuid

from app.db.repositories import Repository


def persist_incident(
    proposal_id: str,
    approved: bool,
    analyst_notes: str | None = None,
    edited_guidance_draft: str | None = None,
    edited_findings: list[dict[str, Any]] | None = None,
    repo: Repository | None = None,
) -> str:
    """
    Internal persistence service for approval-gated incident creation.
    Strictly NOT callable by Gemini or as a side-effect of model output.
    Enforces explicit human approval, unexpired proposal state, and duplicate prevention.
    """
    if repo is None:
        repo = Repository()

    if not approved:
        raise ValueError("Explicit approval is required to save an incident.")

    proposal = repo.get_proposal(proposal_id)
    if not proposal:
        raise ValueError(f"Proposal '{proposal_id}' not found.")

    if proposal.get("status") != "pending":
        raise ValueError(f"Proposal cannot be saved with status '{proposal.get('status')}'. Duplicate save rejected.")

    # Check expiration
    expires_at_str = proposal.get("expires_at")
    if expires_at_str:
        try:
            expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > expires_at:
                raise ValueError("Proposal has expired. Re-investigation required.")
        except (ValueError, TypeError):
            pass

    output_snapshot = proposal.get("output_snapshot", {})
    now_str = datetime.now(timezone.utc).isoformat()

    findings = (
        edited_findings
        if edited_findings is not None
        else output_snapshot.get("findings", [])
    )
    guidance_draft = (
        edited_guidance_draft
        if edited_guidance_draft is not None
        else output_snapshot.get("guidance_draft", "")
    )

    incident_id = str(uuid.uuid4())
    record = {
        "id": incident_id,
        "proposal_id": proposal_id,
        "message": proposal.get("message", ""),
        "findings": findings,
        "risk": output_snapshot.get("risk"),
        "guidance_draft": guidance_draft,
        "guidance": output_snapshot.get("guidance", []),
        "url_analysis": output_snapshot.get("url_analysis", []),
        "attack_sequence": output_snapshot.get("attack_sequence", []),
        "activity": output_snapshot.get("activity", []),
        "analyst_notes": analyst_notes,
        "created_at": now_str,
        "status": "approved",
    }

    saved_id = repo.create_incident(record)
    if not saved_id:
        raise RuntimeError("Failed to persist incident record into database.")

    # Mark proposal as saved to prevent replay/duplicate saves
    repo.update_proposal_status(proposal_id, "saved")

    # Record persistent activity
    repo.log_activity({
        "id": str(uuid.uuid4()),
        "incident_id": saved_id,
        "type": "incident_saved",
        "status": "approved",
        "detail": {"analyst_notes": analyst_notes},
        "timestamp": now_str,
    })

    return saved_id
