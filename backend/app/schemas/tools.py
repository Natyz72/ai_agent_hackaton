from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import EvidenceSpan, Finding


class InspectIndicatorsInput(BaseModel):
    message: str


class InspectIndicatorsOutput(BaseModel):
    findings: list[Finding]
    indicators: list[dict[str, Any]] = Field(default_factory=list)


class AnalyzeURLStructureInput(BaseModel):
    message: str


class AnalyzeURLStructureOutput(BaseModel):
    urls: list[str] = Field(default_factory=list)
    analysis: list[dict[str, Any]] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)


class DetectSocialEngineeringInput(BaseModel):
    message: str


class DetectSocialEngineeringOutput(BaseModel):
    findings: list[Finding]
    tactics: list[dict[str, Any]] = Field(default_factory=list)


class CheckDomainReputationInput(BaseModel):
    hostnames: list[str]


class CheckDomainReputationOutput(BaseModel):
    results: list[dict[str, Any]] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)


class SearchGuidanceInput(BaseModel):
    query: str
    findings_context: list[dict[str, Any]] | None = None


class SearchGuidanceOutput(BaseModel):
    guidance: list[dict[str, Any]] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)


class MapAttackSequenceInput(BaseModel):
    message: str
    findings: list[dict[str, Any]]


class MapAttackSequenceOutput(BaseModel):
    steps: list[dict[str, Any]] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
