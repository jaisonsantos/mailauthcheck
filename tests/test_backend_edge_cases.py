from __future__ import annotations

import unittest
from unittest.mock import patch

from api import main as api_main
from api.services import checks
from api.services.checks import SPFRecordFetchResult
from api.services.dns_resolver import DNSQueryResult


class BackendEdgeCaseTests(unittest.TestCase):
    def test_allowed_origins_from_env_uses_local_defaults(self) -> None:
        with patch.dict("os.environ", {}, clear=False):
            self.assertEqual(api_main.allowed_origins_from_env(), api_main.DEFAULT_LOCAL_ORIGINS)

    def test_allowed_origins_from_env_parses_csv(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "ALLOWED_ORIGINS": (
                    "https://mailauthcheck.com, https://www.mailauthcheck.com, "
                    "https://mailauthcheck.vercel.app"
                )
            },
            clear=False,
        ):
            self.assertEqual(
                api_main.allowed_origins_from_env(),
                [
                    "https://mailauthcheck.com",
                    "https://www.mailauthcheck.com",
                    "https://mailauthcheck.vercel.app",
                ],
            )

    def test_spf_timeout_returns_error_with_retry_message(self) -> None:
        with patch.object(
            checks,
            "resolve_txt",
            return_value=DNSQueryResult(
                status="timeout",
                values=[],
                error_category="timeout",
            ),
        ):
            spf_check, spf_records = checks.build_spf_check("example.com")

        self.assertEqual(spf_check.status, "error")
        self.assertEqual(spf_check.severity, "high")
        self.assertEqual(
            spf_check.technicalDetails,
            "DNS lookup timed out. Try again in a moment.",
        )
        self.assertTrue(spf_check.canBeFalsePositive)
        self.assertEqual(spf_records, [])

    def test_dmarc_dns_error_returns_error_message(self) -> None:
        with patch.object(
            checks,
            "resolve_txt",
            return_value=DNSQueryResult(
                status="error",
                values=[],
                error_category="dns_error",
            ),
        ):
            dmarc_check = checks.build_dmarc_check("example.com")

        self.assertEqual(dmarc_check.status, "error")
        self.assertEqual(
            dmarc_check.technicalDetails,
            "A DNS error prevented this check from completing.",
        )
        self.assertEqual(
            dmarc_check.recommendedFix,
            "Retry the check, then verify the _dmarc subdomain if the problem persists.",
        )

    def test_multiple_spf_records_are_detected(self) -> None:
        with patch.object(
            checks,
            "resolve_txt",
            return_value=DNSQueryResult(
                status="ok",
                values=[
                    "v=spf1 include:_spf.google.com ~all",
                    "v=spf1 include:spf.protection.outlook.com -all",
                ],
            ),
        ):
            spf_check, spf_records = checks.build_spf_check("example.com")

        self.assertEqual(spf_check.status, "error")
        self.assertEqual(spf_check.summary, "Multiple SPF records found.")
        self.assertEqual(len(spf_records), 2)

    def test_dkim_found_for_common_esp_selector(self) -> None:
        def fake_resolve_txt(host: str) -> DNSQueryResult:
            if host == "k1._domainkey.example.com":
                return DNSQueryResult(
                    status="ok",
                    values=["v=DKIM1; k=rsa; p=abc123"],
                )
            return DNSQueryResult(status="no_answer", values=[])

        with patch.object(checks, "resolve_txt", side_effect=fake_resolve_txt):
            dkim_check = checks.build_dkim_check("example.com", "mailchimp")

        self.assertEqual(dkim_check.status, "ok")
        self.assertEqual(dkim_check.confidence, "medium")
        self.assertEqual(dkim_check.rawRecords, ["v=DKIM1; k=rsa; p=abc123"])

    def test_dkim_empty_public_key_is_warning(self) -> None:
        def fake_resolve_txt(host: str) -> DNSQueryResult:
            if host == "k1._domainkey.example.com":
                return DNSQueryResult(
                    status="ok",
                    values=["v=DKIM1; p="],
                )
            return DNSQueryResult(status="no_answer", values=[])

        with patch.object(checks, "resolve_txt", side_effect=fake_resolve_txt):
            dkim_check = checks.build_dkim_check("example.com", "mailchimp")

        self.assertEqual(dkim_check.status, "warning")
        self.assertEqual(
            dkim_check.summary,
            "DKIM selector found, but the public key is empty.",
        )
        self.assertIn("p= value is empty", dkim_check.technicalDetails or "")
        self.assertEqual(dkim_check.rawRecords, ["v=DKIM1; p="])

    def test_dkim_not_found_for_common_selectors_is_warning_not_error(self) -> None:
        with patch.object(
            checks,
            "resolve_txt",
            return_value=DNSQueryResult(status="no_answer", values=[]),
        ):
            dkim_check = checks.build_dkim_check("example.com", "mailchimp")

        self.assertEqual(dkim_check.status, "warning")
        self.assertEqual(dkim_check.confidence, "low")
        self.assertTrue(dkim_check.canBeFalsePositive)
        self.assertIn(
            "We did not find DKIM using common selectors for this ESP.",
            dkim_check.technicalDetails or "",
        )

    def test_spf_redirect_with_clear_all_is_not_marked_weak(self) -> None:
        def fake_resolve_txt(host: str) -> DNSQueryResult:
            if host == "gmail.com":
                return DNSQueryResult(status="ok", values=["v=spf1 redirect=_spf.google.com"])
            return DNSQueryResult(
                status="ok",
                values=["v=spf1 include:_netblocks.google.com ~all"],
            )

        with patch.object(checks, "resolve_txt", side_effect=fake_resolve_txt):
            spf_check, spf_records = checks.build_spf_check("gmail.com")

        self.assertEqual(spf_check.status, "ok")
        self.assertEqual(spf_records, ["v=spf1 redirect=_spf.google.com"])
        self.assertIn("SPF uses redirect to _spf.google.com.", spf_check.technicalDetails or "")
        self.assertEqual(
            spf_check.rawRecords,
            [
                "v=spf1 redirect=_spf.google.com",
                "_spf.google.com: v=spf1 include:_netblocks.google.com ~all",
            ],
        )

    def test_spf_lookup_limit_above_ten_returns_error(self) -> None:
        spf_record = "v=spf1 " + " ".join(
            f"include:sender{i}.example.net" for i in range(1, 12)
        ) + " -all"

        with patch.object(
            checks,
            "_get_single_spf_record",
            return_value=SPFRecordFetchResult(status="missing"),
        ):
            lookup_check = checks.build_spf_lookup_count_check(
                [spf_record],
                "example.com",
            )

        self.assertEqual(lookup_check.status, "error")
        self.assertEqual(
            lookup_check.summary,
            "SPF exceeds the 10 DNS lookup limit.",
        )
        self.assertIn("Estimated SPF DNS lookups: 11 of 10.", lookup_check.technicalDetails or "")
        self.assertIn(
            "No included SPF records were expanded successfully.",
            lookup_check.technicalDetails or "",
        )

    def test_aggregate_status_is_error_when_dns_requests_fail(self) -> None:
        with patch.object(
            checks,
            "resolve_txt",
            return_value=DNSQueryResult(
                status="timeout",
                values=[],
                error_category="timeout",
            ),
        ), patch.object(
            checks,
            "resolve_mx",
            return_value=DNSQueryResult(
                status="ok",
                values=["10 mail.example.com"],
            ),
        ):
            aggregate = checks.build_aggregate_result("example.com")

        self.assertEqual(aggregate.status, "error")
        self.assertIn("could not be fully checked", aggregate.summary)

    def test_aggregate_result_includes_manual_bulk_checks(self) -> None:
        with patch.object(
            checks,
            "resolve_txt",
            return_value=DNSQueryResult(status="no_answer", values=[]),
        ), patch.object(
            checks,
            "resolve_mx",
            return_value=DNSQueryResult(
                status="ok",
                values=["10 mail.example.com"],
            ),
        ):
            aggregate = checks.build_aggregate_result("example.com", "mailchimp")

        self.assertEqual(aggregate.mode, "bulk_sender")
        self.assertEqual(aggregate.espProvider, "mailchimp")
        self.assertTrue(aggregate.manualChecks)
        self.assertTrue(aggregate.gmailBulkChecklist)
        self.assertTrue(
            any(item.status == "manual_check" for item in aggregate.gmailBulkChecklist)
        )

    def test_aggregate_status_needs_attention_when_readiness_is_warning(self) -> None:
        check_results = [
            checks.make_check(
                check_name="SPF",
                status="ok",
                severity="info",
                summary="SPF is present.",
                technical_details=None,
                recommended_fix=None,
                raw_records=["v=spf1 -all"],
                confidence="high",
                can_be_false_positive=False,
            ),
            checks.make_check(
                check_name="DKIM",
                status="warning",
                severity="medium",
                summary="DKIM selector needs confirmation.",
                technical_details=None,
                recommended_fix=None,
                raw_records=[],
                confidence="low",
                can_be_false_positive=True,
            ),
            checks.make_check(
                check_name="DMARC",
                status="ok",
                severity="info",
                summary="DMARC is present.",
                technical_details=None,
                recommended_fix=None,
                raw_records=["v=DMARC1; p=reject"],
                confidence="high",
                can_be_false_positive=False,
            ),
            checks.make_check(
                check_name="MX",
                status="ok",
                severity="info",
                summary="MX records found.",
                technical_details=None,
                recommended_fix=None,
                raw_records=["10 mail.example.com"],
                confidence="high",
                can_be_false_positive=False,
            ),
            checks.make_check(
                check_name="SPF Lookup Count",
                status="ok",
                severity="info",
                summary="SPF lookup count is within the safe range.",
                technical_details=None,
                recommended_fix=None,
                raw_records=[],
                confidence="high",
                can_be_false_positive=False,
            ),
            checks.make_check(
                check_name="Gmail/Yahoo Readiness",
                status="warning",
                severity="medium",
                summary="Bulk readiness needs DKIM confirmation.",
                technical_details=None,
                recommended_fix=None,
                raw_records=[],
                confidence="low",
                can_be_false_positive=True,
            ),
        ]

        self.assertEqual(checks._aggregate_status(83, check_results), "needs_attention")

    def test_readiness_check_does_not_look_good_when_mx_fails(self) -> None:
        spf_check = checks.make_check(
            check_name="SPF",
            status="ok",
            severity="info",
            summary="SPF is present.",
            technical_details=None,
            recommended_fix=None,
            raw_records=["v=spf1 -all"],
            confidence="high",
            can_be_false_positive=False,
        )
        dkim_check = checks.make_check(
            check_name="DKIM",
            status="ok",
            severity="info",
            summary="DKIM is present.",
            technical_details=None,
            recommended_fix=None,
            raw_records=["v=DKIM1; p=abc"],
            confidence="high",
            can_be_false_positive=False,
        )
        dmarc_check = checks.make_check(
            check_name="DMARC",
            status="ok",
            severity="info",
            summary="DMARC is present.",
            technical_details=None,
            recommended_fix=None,
            raw_records=["v=DMARC1; p=reject"],
            confidence="high",
            can_be_false_positive=False,
        )
        spf_lookup_check = checks.make_check(
            check_name="SPF Lookup Count",
            status="ok",
            severity="info",
            summary="SPF lookup count is within the safe range.",
            technical_details=None,
            recommended_fix=None,
            raw_records=[],
            confidence="high",
            can_be_false_positive=False,
        )
        mx_check = checks.make_check(
            check_name="MX",
            status="error",
            severity="high",
            summary="MX could not be checked because DNS did not respond cleanly.",
            technical_details="DNS lookup timed out. Try again in a moment.",
            recommended_fix="Retry the check, then verify your DNS provider if the problem persists.",
            raw_records=[],
            confidence="low",
            can_be_false_positive=True,
        )

        readiness = checks.build_readiness_check(
            spf_check,
            dkim_check,
            dmarc_check,
            spf_lookup_check,
            mx_check,
        )

        self.assertEqual(readiness.status, "error")
        self.assertIn("incomplete because MX could not be checked", readiness.summary)


if __name__ == "__main__":
    unittest.main()
