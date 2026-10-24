from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas.incidents import (
    IncidentApprovalRequest,
    IncidentSaveResponse,
    IncidentListResponse,
    IncidentSummary,
    IncidentDetail,
    IncidentActivityResponse,
)
from app.api.deps import get_db_repo
from app.db.repositories import Repository
from app.tools.create_incident import persist_incident

router = APIRouter()


@router.post("/incidents", response_model=IncidentSaveResponse)
async def create_incident(
    req: IncidentApprovalRequest,
    repo: Repository = Depends(get_db_repo),
):
    """
    POST /api/incidents
    Approval-gated save action. Strictly requires explicit human approval
    and a valid, unexpired proposal ID. Idempotent against duplicate saves.
    """
    try:
        incident_id = persist_incident(
            proposal_id=req.proposal_id,
            approved=req.approved,
            analyst_notes=req.analyst_notes,
            edited_guidance_draft=req.edited_guidance_draft,
            edited_findings=req.edited_findings,
            repo=repo,
        )
        return IncidentSaveResponse(
            success=True,
            incident_id=incident_id,
            message="Incident successfully approved and saved.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="Failed to save incident record.")


@router.get("/incidents", response_model=IncidentListResponse)
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    repo: Repository = Depends(get_db_repo),
):
    """
    GET /api/incidents
    Returns stored incidents with pagination.
    """
    records, total = repo.list_incidents(page=page, page_size=page_size)
    summaries = []
    for r in records:
        risk_level = None
        risk = r.get("risk")
        if isinstance(risk, dict):
            risk_level = risk.get("level")

        summaries.append(
            IncidentSummary(
                id=r.get("id", ""),
                created_at=r.get("created_at", ""),
                risk_level=risk_level,
                summary=r.get("guidance_draft", "")[:120] if r.get("guidance_draft") else None,
                status=r.get("status", "approved"),
            )
        )
    return IncidentListResponse(
        incidents=summaries,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/incidents/{incident_id}", response_model=IncidentDetail)
async def get_incident(
    incident_id: str,
    repo: Repository = Depends(get_db_repo),
):
    """
    GET /api/incidents/{incident_id}
    Retrieves stored incident details.
    """
    record = repo.get_incident(incident_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    return IncidentDetail(**record)


@router.get("/incidents/{incident_id}/activity", response_model=IncidentActivityResponse)
async def get_incident_activity(
    incident_id: str,
    repo: Repository = Depends(get_db_repo),
):
    """
    GET /api/incidents/{incident_id}/activity
    Returns verified activity events for the incident.
    """
    record = repo.get_incident(incident_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")

    events = repo.get_activity_for_incident(incident_id)
    return IncidentActivityResponse(
        incident_id=incident_id,
        activity=events,
    )
