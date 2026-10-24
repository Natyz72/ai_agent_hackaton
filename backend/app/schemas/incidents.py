from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ActivityEvent


class IncidentApprovalRequest(BaseModel):
    proposal_id: str
    approved: bool = True
    analyst_notes: str | None = None
    edited_guidance_draft: str | None = None
    edited_findings: list[dict[str, Any]] | None = None


class IncidentSaveResponse(BaseModel):
    success: bool
    incident_id: str | None = None
    message: str


class IncidentSummary(BaseModel):
    id: str
    created_at: str
    risk_level: str | None = None
    summary: str | None = None
    status: str | None = None


class IncidentListResponse(BaseModel):
    incidents: list[IncidentSummary]
    total: int
    page: int
    page_size: int


class IncidentDetail(BaseModel):
    id: str
    created_at: str
    proposal_id: str | None = None
    message: str
    findings: list[dict[str, Any]] = Field(default_factory=list)
    risk: dict[str, Any] | None = None
    guidance_draft: str | None = None
    guidance: list[dict[str, Any]] = Field(default_factory=list)
    url_analysis: list[dict[str, Any]] = Field(default_factory=list)
    attack_sequence: list[dict[str, Any]] = Field(default_factory=list)
    activity: list[ActivityEvent] = Field(default_factory=list)
    analyst_notes: str | None = None


class IncidentActivityResponse(BaseModel):
    incident_id: str
    activity: list[ActivityEvent]
