from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import (
    ActivityEvent,
    AttackStep,
    Finding,
    GuidanceRef,
    ReputationResult,
    RiskAssessment,
    URLAnalysis,
)


class InvestigateRequest(BaseModel):
    message: str = Field(min_length=1)


class InvestigateResponse(BaseModel):
    proposal_id: str
    status: str  # ok | clarification_needed | error
    message: str
    findings: list[Finding] = Field(default_factory=list)
    url_analysis: list[URLAnalysis] = Field(default_factory=list)
    reputation: list[ReputationResult] = Field(default_factory=list)
    guidance: list[GuidanceRef] = Field(default_factory=list)
    attack_sequence: list[AttackStep] = Field(default_factory=list)
    validated_evidence: list[Finding] = Field(default_factory=list)
    risk: RiskAssessment | None = None
    highlights: list[dict[str, Any]] = Field(default_factory=list)
    guidance_draft: str
    clarification_questions: list[str] = Field(default_factory=list)
    activity: list[ActivityEvent] = Field(default_factory=list)
    expires_at: str | None = None
