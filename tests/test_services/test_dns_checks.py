from __future__ import annotations

from unittest.mock import patch

from api.services import checks
from api.services.dns_resolver import DNSQueryResult


def test_spf_single_record_found() -> None:
    with patch(
        "api.services.checks.resolve_txt",
        return_value=DNSQueryResult(status="ok", values=["v=spf1 include:_spf.example.com ~all"]),
    ):
        spf_check, spf_records = checks.build_spf_check("example.com")

    assert spf_check.status == "ok"
    assert spf_records == ["v=spf1 include:_spf.example.com ~all"]


def test_spf_multiple_records_error() -> None:
    with patch(
        "api.services.checks.resolve_txt",
        return_value=DNSQueryResult(
            status="ok",
            values=["v=spf1 include:a.example.com ~all", "v=spf1 include:b.example.com ~all"],
        ),
    ):
        spf_check, _spf_records = checks.build_spf_check("example.com")

    assert spf_check.status == "error"
    assert spf_check.summary == "Multiple SPF records found."


def test_dkim_selector_found() -> None:
    def fake_txt(name: str) -> DNSQueryResult:
        if name == "s1._domainkey.example.com":
            return DNSQueryResult(status="ok", values=["v=DKIM1; p=abc123"])
        return DNSQueryResult(status="no_answer", values=[])

    with patch("api.services.checks.resolve_txt", side_effect=fake_txt):
        dkim_check = checks.build_dkim_check("example.com", "sendgrid")

    assert dkim_check.status == "ok"
    assert dkim_check.confidence == "medium"


def test_dkim_selector_not_found_is_low_confidence_warning() -> None:
    with patch(
        "api.services.checks.resolve_txt",
        return_value=DNSQueryResult(status="no_answer", values=[]),
    ):
        dkim_check = checks.build_dkim_check("example.com", "mailchimp")

    assert dkim_check.status == "warning"
    assert dkim_check.confidence == "low"
    assert dkim_check.canBeFalsePositive is True


def test_dmarc_policy_none_warning() -> None:
    with patch(
        "api.services.checks.resolve_txt",
        return_value=DNSQueryResult(status="ok", values=["v=DMARC1; p=none"]),
    ):
        dmarc_check = checks.build_dmarc_check("example.com")

    assert dmarc_check.status == "warning"
    assert "monitoring" in dmarc_check.summary


def test_dmarc_policy_reject_ok() -> None:
    with patch(
        "api.services.checks.resolve_txt",
        return_value=DNSQueryResult(status="ok", values=["v=DMARC1; p=reject"]),
    ):
        dmarc_check = checks.build_dmarc_check("example.com")

    assert dmarc_check.status == "ok"
    assert "reject" in (dmarc_check.technicalDetails or "")


def test_mx_present_ok() -> None:
    with patch(
        "api.services.checks.resolve_mx",
        return_value=DNSQueryResult(status="ok", values=["10 mail.example.com"]),
    ):
        mx_check = checks.build_mx_check("example.com")

    assert mx_check.status == "ok"
    assert mx_check.rawRecords == ["10 mail.example.com"]


def test_mx_absent_missing() -> None:
    with patch(
        "api.services.checks.resolve_mx",
        return_value=DNSQueryResult(status="no_answer", values=[], error_category="no_answer"),
    ):
        mx_check = checks.build_mx_check("example.com")

    assert mx_check.status == "missing"


def test_dns_timeout_handling_for_mx() -> None:
    with patch(
        "api.services.checks.resolve_mx",
        return_value=DNSQueryResult(status="timeout", values=[], error_category="timeout"),
    ):
        mx_check = checks.build_mx_check("example.com")

    assert mx_check.status == "error"
    assert mx_check.canBeFalsePositive is True
