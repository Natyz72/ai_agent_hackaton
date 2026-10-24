from fastapi import APIRouter, HTTPException

from app.schemas.incidents import (
    IncidentApprovalRequest,
    IncidentSaveResponse,
    IncidentListResponse,
    IncidentDetail,
    IncidentActivityResponse,
)

router = APIRouter()


@router.post("/incidents", response_model=IncidentSaveResponse)
async def create_incident(req: IncidentApprovalRequest):
    if not req.approved or not req.proposal_id:
        raise HTTPException(status_code=400, detail="Approval required with valid proposal")
    # Stage 7 will implement
    raise HTTPException(status_code=400, detail="Not implemented yet")


@router.get("/incidents", response_model=IncidentListResponse)
async def list_incidents(page: int = 1, page_size: int = 20):
    return IncidentListResponse(incidents=[], total=0, page=page, page_size=page_size)


@router.get("/incidents/{incident_id}", response_model=IncidentDetail)
async def get_incident(incident_id: str):
    raise HTTPException(status_code=404, detail="Not found")


@router.get("/incidents/{incident_id}/activity", response_model=IncidentActivityResponse)
async def get_incident_activity(incident_id: str):
    return IncidentActivityResponse(incident_id=incident_id, activity=[])
