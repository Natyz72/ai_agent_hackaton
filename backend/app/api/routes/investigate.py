from fastapi import APIRouter, Depends, HTTPException

from app.schemas.investigate import InvestigateRequest, InvestigateResponse
from app.config import settings

router = APIRouter()


@router.post("/investigate", response_model=InvestigateResponse)
async def investigate(req: InvestigateRequest):
    if len(req.message) > settings.max_message_length:
        raise HTTPException(status_code=400, detail="Message too long")
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message required")
    # Stage 6 will implement full logic; placeholder for now
    return InvestigateResponse(
        proposal_id="placeholder",
        status="ok",
        message=req.message,
        guidance_draft="",
        activity=[],
    )
