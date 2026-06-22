from __future__ import annotations

from api.services import checks


def make_status_check(name: str, status: str, confidence: str = "high"):
    return checks.make_check(
        check_name=name,
        status=status,
        severity="info" if status == "ok" else "high",
        summary=f"{name} {status}",
        technical_details=None,
        recommended_fix=None,
        raw_records=[],
        confidence=confidence,
        can_be_false_positive=confidence == "low",
    )


def test_perfect_domain_score_100() -> None:
    score = checks._score_from_checks(
        make_status_check("MX", "ok"),
        make_status_check("SPF", "ok"),
        make_status_check("DKIM", "ok", "medium"),
        make_status_check("SPF Lookup Count", "ok", "medium"),
        checks.make_check(
            check_name="DMARC",
            status="ok",
            severity="info",
            summary="DMARC reject",
            technical_details=None,
            recommended_fix=None,
            raw_records=["v=DMARC1; p=reject"],
            confidence="high",
            can_be_false_positive=False,
        ),
    )

    assert score == 100


def test_missing_dmarc_score_low_and_not_ready() -> None:
    check_list = [
        make_status_check("SPF", "ok"),
        make_status_check("DKIM", "ok", "medium"),
        make_status_check("DMARC", "missing"),
        make_status_check("MX", "ok"),
        make_status_check("SPF Lookup Count", "ok", "medium"),
        make_status_check("Gmail/Yahoo Readiness", "error"),
    ]

    assert checks._aggregate_status(70, check_list) == "needs_attention"


def test_multiple_spf_blocks_ready() -> None:
    check_list = [
        make_status_check("SPF", "error"),
        make_status_check("DKIM", "ok", "medium"),
        make_status_check("DMARC", "ok"),
        make_status_check("MX", "ok"),
        make_status_check("SPF Lookup Count", "ok", "medium"),
        make_status_check("Gmail/Yahoo Readiness", "error"),
    ]

    assert checks._aggregate_status(90, check_list) == "needs_attention"


def test_spf_lookup_count_warning_points() -> None:
    spf_lookup_check = checks.make_check(
        check_name="SPF Lookup Count",
        status="warning",
        severity="medium",
        summary="SPF lookup count is close to the limit.",
        technical_details=None,
        recommended_fix=None,
        raw_records=[],
        confidence="medium",
        can_be_false_positive=False,
    )

    score = checks._score_from_checks(
        make_status_check("MX", "ok"),
        make_status_check("SPF", "ok"),
        make_status_check("DKIM", "ok", "medium"),
        spf_lookup_check,
        make_status_check("DMARC", "ok"),
    )

    assert score == 83


def test_spf_lookup_count_error_blocks_ready() -> None:
    check_list = [
        make_status_check("SPF", "ok"),
        make_status_check("DKIM", "ok", "medium"),
        make_status_check("DMARC", "ok"),
        make_status_check("MX", "ok"),
        make_status_check("SPF Lookup Count", "error"),
        make_status_check("Gmail/Yahoo Readiness", "error"),
    ]

    assert checks._aggregate_status(85, check_list) == "needs_attention"


def test_dkim_selector_mismatch_confidence_low() -> None:
    dkim_check = make_status_check("DKIM", "warning", "low")

    assert dkim_check.confidence == "low"
    assert dkim_check.canBeFalsePositive is True
