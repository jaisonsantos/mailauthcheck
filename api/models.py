from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

GeneralStatus = Literal["ready", "needs_attention", "not_ready", "error"]
BulkStatus = Literal["ready", "needs_work", "not_ready", "incomplete"]
CheckStatus = Literal["ok", "warning", "missing", "manual_check", "unknown", "error"]
Severity = Literal["info", "low", "medium", "high"]
Confidence = Literal["high", "medium", "low"]


class ErrorResponse(BaseModel):
    error: str
    message: str


class DomainRequest(BaseModel):
    domain: str = Field(min_length=1)
    mode: str | None = None
    espProvider: str | None = None


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


class ManualCheckResult(BaseModel):
    checkName: str
    status: Literal["manual_check", "unknown"] = "manual_check"
    summary: str
    whyItMatters: str
    howToVerify: str
    references: list[dict[str, str]] = Field(default_factory=list)


class BulkComplianceItem(BaseModel):
    item: str
    provider: Literal["gmail", "yahoo"]
    required: bool
    status: CheckStatus
    automated: bool
    explanation: str
    howToVerify: str | None = None
    sourceUrl: str | None = None


class AggregateResult(BaseModel):
    domain: str
    mode: str = "bulk_sender"
    espProvider: str | None = None
    score: int = Field(ge=0, le=100)
    dnsAuthenticationScore: int = Field(ge=0, le=100)
    status: GeneralStatus
    bulkStatus: BulkStatus
    summary: str
    checks: list[CheckResult]
    automatedChecks: list[CheckResult] = Field(default_factory=list)
    manualChecks: list[ManualCheckResult] = Field(default_factory=list)
    gmailBulkChecklist: list[BulkComplianceItem] = Field(default_factory=list)
    yahooBulkChecklist: list[BulkComplianceItem] = Field(default_factory=list)
    nextSteps: list[str]
    disclaimer: str


class CheckListResponse(BaseModel):
    domain: str
    checks: list[CheckResult]
