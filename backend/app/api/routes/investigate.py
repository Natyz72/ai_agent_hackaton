from typing import Any
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.investigate import InvestigateRequest, InvestigateResponse
from app.config import settings
from app.api.deps import get_db_repo, get_rate_limiter, RateLimiter
from app.db.repositories import Repository
from app.agent.loop import run_investigation_loop
from app.llm.base import LLMClient
from app.llm.fake import FakeLLMClient
from app.llm.gemini import GeminiClient

router = APIRouter()


def get_llm_client() -> LLMClient:
    if settings.gemini_api_key:
        return GeminiClient()
    return FakeLLMClient()


@router.post("/investigate", response_model=InvestigateResponse)
async def investigate(
    req: InvestigateRequest,
    repo: Repository = Depends(get_db_repo),
    limiter: RateLimiter = Depends(get_rate_limiter),
):
    """
    POST /api/investigate
    Executes the bounded investigation loop, runs deterministic validation and scoring,
    and returns a durable investigation proposal.
    STRICTLY NEVER saves an incident.
    """
    if len(req.message) > settings.max_message_length:
        raise HTTPException(
            status_code=400,
            detail=f"Message exceeds maximum allowed length of {settings.max_message_length} characters",
        )
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Submitted message cannot be empty")

    llm = get_llm_client()
    result = await run_investigation_loop(req.message, llm, repo=repo)

    # Prepare snapshot for proposal storage
    snapshot = {
        "status": result["status"],
        "findings": [f.model_dump() for f in result["findings"]],
        "url_analysis": [u.model_dump() for u in result["url_analysis"]],
        "reputation": [r.model_dump() for r in result["reputation"]],
        "guidance": [g.model_dump() for g in result["guidance"]],
        "attack_sequence": [s.model_dump() for s in result["attack_sequence"]],
        "validated_evidence": [v.model_dump() for v in result["validated_evidence"]],
        "risk": result["risk"].model_dump() if result["risk"] else None,
        "highlights": result["highlights"],
        "guidance_draft": result["guidance_draft"],
        "clarification_questions": result["clarification_questions"],
        "activity": [a.model_dump() for a in result["activity"]],
    }

    # Persist proposal (proposal only, NO incident)
    proposal_record = repo.create_proposal(req.message, snapshot)

    return InvestigateResponse(
        proposal_id=proposal_record["id"],
        status=result["status"],
        message=req.message,
        findings=result["findings"],
        url_analysis=result["url_analysis"],
        reputation=result["reputation"],
        guidance=result["guidance"],
        attack_sequence=result["attack_sequence"],
        validated_evidence=result["validated_evidence"],
        risk=result["risk"],
        highlights=result["highlights"],
        guidance_draft=result["guidance_draft"],
        clarification_questions=result["clarification_questions"],
        activity=result["activity"],
        expires_at=proposal_record.get("expires_at"),
    )
