from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

GeneralStatus = Literal["ready", "needs_attention", "not_ready", "error"]
CheckStatus = Literal["ok", "warning", "missing", "error"]
Severity = Literal["info", "low", "medium", "high"]
Confidence = Literal["high", "medium", "low"]


class ErrorResponse(BaseModel):
    error: str
    message: str


class DomainRequest(BaseModel):
    domain: str = Field(min_length=1)


class CheckResult(BaseModel):
    checkName: str
    status: CheckStatus
    severity: Severity
    summary: str
    technicalDetails: str | None = None
    recommendedFix: str | None = None
    rawRecords: list[str] = Field(default_factory=list)
    references: list[dict[str, str]] = Field(default_factory=list)
    confidence: Confidence
    canBeFalsePositive: bool


class AggregateResult(BaseModel):
    domain: str
    score: int = Field(ge=0, le=100)
    status: GeneralStatus
    summary: str
    checks: list[CheckResult]
    nextSteps: list[str]
    disclaimer: str


class CheckListResponse(BaseModel):
    domain: str
    checks: list[CheckResult]
