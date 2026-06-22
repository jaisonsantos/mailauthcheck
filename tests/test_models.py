from __future__ import annotations

from api.models import AggregateResult, CheckResult


def test_check_result_model_accepts_expected_fields() -> None:
    result = CheckResult(
        checkName="SPF",
        status="ok",
        severity="info",
        summary="SPF found.",
        technicalDetails=None,
        recommendedFix=None,
        rawRecords=["v=spf1 -all"],
        references=[],
        confidence="high",
        canBeFalsePositive=False,
    )

    assert result.checkName == "SPF"
    assert result.status == "ok"


def test_aggregate_result_model_accepts_bulk_fields() -> None:
    result = AggregateResult(
        domain="example.com",
        score=85,
        dnsAuthenticationScore=85,
        status="needs_attention",
        bulkStatus="needs_work",
        summary="Needs review.",
        checks=[],
        nextSteps=["Review DKIM."],
        disclaimer="No inbox guarantee.",
    )

    assert result.mode == "bulk_sender"
    assert result.automatedChecks == []
