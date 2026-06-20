from __future__ import annotations

import unittest
from unittest.mock import patch

from api.services import checks
from api.services.checks import SPFRecordFetchResult
from api.services.dns_resolver import DNSQueryResult


class BackendEdgeCaseTests(unittest.TestCase):
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
        self.assertIn("Estimated DNS lookups: 11.", lookup_check.technicalDetails or "")

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


if __name__ == "__main__":
    unittest.main()
