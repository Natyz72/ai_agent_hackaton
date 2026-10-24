from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None


class ActivityEvent(BaseModel):
    id: str | None = None
    type: str
    status: str
    detail: dict[str, Any] | None = None
    timestamp: datetime | None = None


class EvidenceSpan(BaseModel):
    start: int
    end: int
    text: str


class Finding(BaseModel):
    id: str
    category: str
    status: str  # detected | not_detected | not_assessable
    reason: str
    source_evidence: list[EvidenceSpan] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    tool: str | None = None


class URLAnalysis(BaseModel):
    url: str  # defanged/escaped representation
    normalized_host: str | None = None
    is_ip: bool = False
    has_user_info: bool = False
    user_info: str | None = None
    suspicious: bool = False
    reasons: list[str] = Field(default_factory=list)


class ReputationResult(BaseModel):
    hostname: str
    status: str  # known_trusted | suspicious | unknown
    source: str
    reason: str


class GuidanceRef(BaseModel):
    id: str
    title: str
    excerpt: str
    reason: str | None = None


class AttackStep(BaseModel):
    step: int
    description: str
    evidence_ids: list[str] = Field(default_factory=list)
    evidence_offsets: list[EvidenceSpan] = Field(default_factory=list)


class RiskBreakdownItem(BaseModel):
    rule: str
    points: int
    reason: str


class RiskAssessment(BaseModel):
    level: str  # low | medium | high
    score: int
    heuristic: bool = True
    breakdown: list[RiskBreakdownItem] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
