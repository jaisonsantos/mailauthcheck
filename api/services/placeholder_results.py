from __future__ import annotations

from api.models import AggregateResult, CheckListResponse, CheckResult


DISCLAIMER = (
    "This is a DNS/authentication check and does not guarantee inbox placement."
)

SKELETON_TECHNICAL_DETAILS = (
    "Placeholder output from the API skeleton. Real DNS checks are not implemented yet."
)


def _placeholder_check(
    check_name: str,
    summary: str,
    recommended_fix: str | None = None,
) -> CheckResult:
    return CheckResult(
        checkName=check_name,
        status="error",
        severity="low",
        summary=summary,
        technicalDetails=SKELETON_TECHNICAL_DETAILS,
        recommendedFix=recommended_fix,
        rawRecords=[],
        references=[],
        confidence="low",
        canBeFalsePositive=False,
    )


def build_aggregate_result(domain: str) -> AggregateResult:
    checks = [
        _placeholder_check("SPF", "SPF placeholder result is available, but DNS lookup is not wired yet."),
        _placeholder_check("DMARC", "DMARC placeholder result is available, but DNS lookup is not wired yet."),
        _placeholder_check("MX", "MX placeholder result is available, but DNS lookup is not wired yet."),
        _placeholder_check(
            "SPF Lookup Count",
            "SPF lookup count placeholder is available, but recursive parsing is not wired yet.",
        ),
        _placeholder_check(
            "Gmail/Yahoo Readiness",
            "Readiness placeholder is available, but the underlying checks are not wired yet.",
        ),
    ]

    return AggregateResult(
        domain=domain,
        score=0,
        status="error",
        summary="The API skeleton is running, but real DNS checks are not implemented yet.",
        checks=checks,
        nextSteps=[
            "Wire real DNS lookups into SPF, DMARC and MX checks.",
            "Replace placeholder scoring with the MVP scoring model.",
            "Connect the frontend to this endpoint after DNS checks are implemented.",
        ],
        disclaimer=DISCLAIMER,
    )


def build_single_check_response(domain: str, check_name: str, summary: str) -> CheckListResponse:
    return CheckListResponse(
        domain=domain,
        checks=[_placeholder_check(check_name, summary)],
    )
