from __future__ import annotations

from dataclasses import dataclass

from api.models import (
    AggregateResult,
    BulkComplianceItem,
    CheckListResponse,
    CheckResult,
    ManualCheckResult,
)
from api.services.dns_resolver import DNSQueryResult, resolve_mx, resolve_txt


DISCLAIMER = (
    "This tool checks public DNS records and known bulk sender readiness signals. "
    "It does not guarantee inbox placement, campaign performance, sender reputation "
    "or provider acceptance."
)

SPF_LOOKUP_MECHANISMS = ("include:", "a", "mx", "ptr", "exists:", "redirect=")
GMAIL_SENDER_GUIDELINES_URL = "https://support.google.com/mail/answer/81126?hl=en"
GMAIL_SENDER_FAQ_URL = "https://support.google.com/mail/answer/14229414?hl=en"
YAHOO_SENDER_GUIDELINES_URL = "https://senders.yahooinc.com/best-practices/"

COMMON_DKIM_SELECTORS_BY_ESP: dict[str, tuple[str, ...]] = {
    "mailchimp": ("k1", "k2", "mandrill"),
    "brevo": ("mail", "brevo", "sib1", "sib2"),
    "klaviyo": ("kl", "klaviyo", "s1", "s2"),
    "sendgrid": ("s1", "s2"),
    "mailgun": ("smtp", "mailo", "k1"),
    "resend": ("resend", "s1", "s2"),
    "amazon_ses": ("amazonses", "selector1", "selector2"),
    "hubspot": ("hs1", "hs2", "hubspot"),
}

DEFAULT_DKIM_SELECTORS = (
    "default",
    "google",
    "selector1",
    "selector2",
    "s1",
    "s2",
    "k1",
    "k2",
)


@dataclass(slots=True)
class SPFCountResult:
    count: int | None
    confidence: str
    can_be_false_positive: bool
    technical_details: str
    raw_records: list[str]
    included_records: list[tuple[str, int | None, str]]
    error: str | None = None


@dataclass(slots=True)
class AggregateComputation:
    checks: list[CheckResult]
    score: int
    status: str
    summary: str
    next_steps: list[str]


def normalize_esp_provider(esp_provider: str | None) -> str | None:
    if not esp_provider:
        return None
    normalized = esp_provider.strip().lower().replace("-", "_").replace(" ", "_")
    return normalized if normalized in COMMON_DKIM_SELECTORS_BY_ESP else None


def make_check(
    *,
    check_name: str,
    status: str,
    severity: str,
    summary: str,
    technical_details: str | None,
    recommended_fix: str | None,
    raw_records: list[str],
    confidence: str,
    can_be_false_positive: bool,
) -> CheckResult:
    return CheckResult(
        checkName=check_name,
        status=status,
        severity=severity,
        summary=summary,
        technicalDetails=technical_details,
        recommendedFix=recommended_fix,
        rawRecords=raw_records,
        references=[],
        confidence=confidence,
        canBeFalsePositive=can_be_false_positive,
    )


def _error_from_dns(
    check_name: str,
    result: DNSQueryResult,
    summary: str,
    recommended_fix: str | None = None,
) -> CheckResult:
    technical_details = {
        "timeout": "DNS lookup timed out. Try again in a moment.",
        "no_nameservers": "The domain's DNS servers did not answer this request reliably.",
        "dns_error": "A DNS error prevented this check from completing.",
        "nxdomain": "The domain does not appear to exist in DNS.",
        "no_answer": "DNS returned no answer for this record type.",
    }.get(result.error_category or "", "A DNS error prevented this check from completing.")

    return make_check(
        check_name=check_name,
        status="error",
        severity="high" if result.error_category == "timeout" else "medium",
        summary=summary,
        technical_details=technical_details,
        recommended_fix=recommended_fix,
        raw_records=[],
        confidence="low",
        can_be_false_positive=result.error_category == "timeout",
    )


def build_spf_check(domain: str) -> tuple[CheckResult, list[str]]:
    result = resolve_txt(domain)
    if result.status in {"timeout", "error", "nxdomain"}:
        return (
            _error_from_dns(
                "SPF",
                result,
                "SPF could not be checked because DNS did not respond cleanly.",
            ),
            [],
        )

    spf_records = [record for record in result.values if record.lower().startswith("v=spf1")]

    if not spf_records:
        return (
            make_check(
                check_name="SPF",
                status="missing",
                severity="high",
                summary="No SPF record found.",
                technical_details="No TXT record starting with v=spf1 was found at the root domain.",
                recommended_fix="Add one SPF TXT record that includes your legitimate sending providers.",
                raw_records=[],
                confidence="high",
                can_be_false_positive=False,
            ),
            [],
        )

    if len(spf_records) > 1:
        return (
            make_check(
                check_name="SPF",
                status="error",
                severity="high",
                summary="Multiple SPF records found.",
                technical_details="A domain should publish only one SPF TXT record.",
                recommended_fix="Merge all SPF mechanisms into a single SPF TXT record.",
                raw_records=spf_records,
                confidence="high",
                can_be_false_positive=False,
            ),
            spf_records,
        )

    spf_record = spf_records[0]
    lower_record = spf_record.lower()
    uses_unsafe_all = "+all" in lower_record
    missing_all = all(token not in lower_record for token in ["-all", "~all", "?all", "+all"])
    redirect_target = next(
        (token.split("=", 1)[1] for token in spf_record.split() if token.startswith("redirect=")),
        None,
    )

    if uses_unsafe_all:
        return (
            make_check(
                check_name="SPF",
                status="warning",
                severity="medium",
                summary="SPF exists, but the policy looks weak.",
                technical_details="The SPF record uses +all, which is too permissive for a deliberate SPF policy.",
                recommended_fix="Review the SPF policy so it ends with a deliberate all mechanism, usually ~all or -all.",
                raw_records=[spf_record],
                confidence="high",
                can_be_false_positive=False,
            ),
            [spf_record],
        )

    if missing_all and redirect_target:
        redirected = _get_single_spf_record(redirect_target)
        if redirected.status == "ok" and redirected.value:
            redirected_lower = redirected.value.lower()
            redirected_uses_unsafe_all = "+all" in redirected_lower
            redirected_missing_all = all(
                token not in redirected_lower for token in ["-all", "~all", "?all", "+all"]
            )

            if not redirected_uses_unsafe_all and not redirected_missing_all:
                return (
                    make_check(
                        check_name="SPF",
                        status="ok",
                        severity="info",
                        summary="Your domain has one SPF record.",
                        technical_details=(
                            f"SPF uses redirect to {redirect_target}. "
                            "The redirected SPF policy ends with a clear all mechanism."
                        ),
                        recommended_fix=None,
                        raw_records=[spf_record, f"{redirect_target}: {redirected.value}"],
                        confidence="high",
                        can_be_false_positive=False,
                    ),
                    [spf_record],
                )

            return (
                make_check(
                    check_name="SPF",
                    status="warning",
                    severity="medium",
                    summary="SPF exists, but the redirected policy still needs review.",
                    technical_details=(
                        f"SPF uses redirect to {redirect_target}, but the redirected SPF policy "
                        "still uses +all or does not end with a clear all mechanism."
                    ),
                    recommended_fix=(
                        "Review the redirected SPF policy so it ends with a deliberate all "
                        "mechanism, usually ~all or -all."
                    ),
                    raw_records=[spf_record, f"{redirect_target}: {redirected.value}"],
                    confidence="high",
                    can_be_false_positive=False,
                ),
                [spf_record],
            )

        return (
            make_check(
                check_name="SPF",
                status="warning",
                severity="medium",
                summary="SPF uses redirect, but the redirected policy could not be confirmed.",
                technical_details=(
                    f"SPF uses redirect to {redirect_target}. Check the redirected SPF record "
                    "before judging policy strength."
                ),
                recommended_fix=(
                    "Open the redirected SPF record and confirm that it ends with a deliberate "
                    "all mechanism, usually ~all or -all."
                ),
                raw_records=[spf_record],
                confidence="medium",
                can_be_false_positive=True,
            ),
            [spf_record],
        )

    if missing_all:
        return (
            make_check(
                check_name="SPF",
                status="warning",
                severity="medium",
                summary="SPF exists, but the policy looks weak.",
                technical_details="The SPF record does not end with a clear all mechanism.",
                recommended_fix="Review the SPF policy so it ends with a deliberate all mechanism, usually ~all or -all.",
                raw_records=[spf_record],
                confidence="high",
                can_be_false_positive=False,
            ),
            [spf_record],
        )

    return (
        make_check(
            check_name="SPF",
            status="ok",
            severity="info",
            summary="Your domain has one SPF record.",
            technical_details="One TXT record starting with v=spf1 was found.",
            recommended_fix=None,
            raw_records=[spf_record],
            confidence="high",
            can_be_false_positive=False,
        ),
        [spf_record],
    )


def _estimate_spf_lookups(
    domain: str,
    spf_record: str,
    visited: set[str] | None = None,
    depth: int = 0,
) -> SPFCountResult:
    visited = visited or set()
    domain_key = f"{domain}:{spf_record}"

    if domain_key in visited or depth > 10:
        return SPFCountResult(
            count=None,
            confidence="medium",
            can_be_false_positive=True,
            technical_details="SPF lookup recursion stopped to avoid loops or excessive depth.",
            raw_records=[spf_record],
            included_records=[],
            error="recursion_limit",
        )

    visited.add(domain_key)
    count = 0
    raw_records = [spf_record]
    included_records: list[tuple[str, int | None, str]] = []
    uncertain = False
    attempted_expansion = False
    technical_notes: list[str] = []

    for token in spf_record.split():
        normalized = token.lstrip("+-~?")

        if normalized.startswith("include:"):
            count += 1
            attempted_expansion = True
            include_domain = normalized.split(":", 1)[1]
            nested = _get_single_spf_record(include_domain)
            if nested.status == "ok" and nested.value:
                nested_result = _estimate_spf_lookups(
                    include_domain,
                    nested.value,
                    visited=visited,
                    depth=depth + 1,
                )
                if nested_result.count is None:
                    uncertain = True
                else:
                    count += nested_result.count
                raw_records.extend(nested_result.raw_records)
                included_records.append((include_domain, nested_result.count, nested.value))
                included_records.extend(nested_result.included_records)
            else:
                uncertain = True
                technical_notes.append(
                    f"Include domain {include_domain} could not be resolved completely."
                )

        elif normalized.startswith("redirect="):
            count += 1
            attempted_expansion = True
            redirect_domain = normalized.split("=", 1)[1]
            nested = _get_single_spf_record(redirect_domain)
            if nested.status == "ok" and nested.value:
                nested_result = _estimate_spf_lookups(
                    redirect_domain,
                    nested.value,
                    visited=visited,
                    depth=depth + 1,
                )
                if nested_result.count is None:
                    uncertain = True
                else:
                    count += nested_result.count
                raw_records.extend(nested_result.raw_records)
                included_records.append((redirect_domain, nested_result.count, nested.value))
                included_records.extend(nested_result.included_records)
            else:
                uncertain = True
                technical_notes.append(
                    f"Redirect domain {redirect_domain} could not be resolved completely."
                )

        elif normalized == "a" or normalized.startswith("a:"):
            count += 1
        elif normalized == "mx" or normalized.startswith("mx:"):
            count += 1
        elif normalized == "ptr" or normalized.startswith("ptr:"):
            count += 1
        elif normalized.startswith("exists:"):
            count += 1

    details_lines = [f"Estimated SPF DNS lookups: {count} of 10."]
    if included_records:
        details_lines.append("Included SPF records checked:")
        for included_domain, nested_count, _record in included_records:
            nested_label = (
                "unknown nested DNS lookups"
                if nested_count is None
                else f"{nested_count} nested DNS lookups"
            )
            details_lines.append(f"- {included_domain}: {nested_label}.")
    elif attempted_expansion:
        details_lines.append("No included SPF records were expanded successfully.")
    else:
        details_lines.append("No included SPF records were expanded.")
    if uncertain:
        details_lines.append("Some nested SPF parsing was incomplete.")
    if technical_notes:
        details_lines.extend(dict.fromkeys(technical_notes))

    return SPFCountResult(
        count=count,
        confidence="medium",
        can_be_false_positive=uncertain,
        technical_details="\n".join(details_lines),
        raw_records=list(
            dict.fromkeys(
                [spf_record]
                + [f"{included_domain}: {record}" for included_domain, _count, record in included_records]
            )
        ),
        included_records=included_records,
    )


@dataclass(slots=True)
class SPFRecordFetchResult:
    status: str
    value: str | None = None


def _get_single_spf_record(domain: str) -> SPFRecordFetchResult:
    txt_result = resolve_txt(domain)
    if txt_result.status != "ok":
        return SPFRecordFetchResult(status=txt_result.status)

    spf_records = [record for record in txt_result.values if record.lower().startswith("v=spf1")]
    if len(spf_records) != 1:
        return SPFRecordFetchResult(status="missing")

    return SPFRecordFetchResult(status="ok", value=spf_records[0])


def build_spf_lookup_count_check(spf_records: list[str], domain: str) -> CheckResult:
    if len(spf_records) != 1:
        return make_check(
            check_name="SPF Lookup Count",
            status="warning",
            severity="medium",
            summary="SPF lookup count could not be estimated cleanly.",
            technical_details="SPF lookup count needs exactly one SPF record to analyze.",
            recommended_fix="Publish one valid SPF record before relying on lookup count checks.",
            raw_records=spf_records,
            confidence="medium",
            can_be_false_positive=True,
        )

    result = _estimate_spf_lookups(domain, spf_records[0])

    if result.count is None:
        return make_check(
            check_name="SPF Lookup Count",
            status="warning",
            severity="medium",
            summary="SPF lookup count could not be fully confirmed.",
            technical_details=result.technical_details,
            recommended_fix="Review nested include or redirect mechanisms and keep the total under 10.",
            raw_records=result.raw_records,
            confidence=result.confidence,
            can_be_false_positive=True,
        )

    if result.count <= 7:
        status = "ok"
        severity = "info"
        summary = "SPF lookup count is within the safe range."
        recommended_fix = None
    elif result.count <= 10:
        status = "warning"
        severity = "medium"
        summary = "SPF lookup count is close to the limit."
        recommended_fix = "Reduce unnecessary include, a, mx or redirect mechanisms before SPF reaches the 10-lookup limit."
    else:
        status = "error"
        severity = "high"
        summary = "SPF exceeds the 10 DNS lookup limit."
        recommended_fix = "Remove unused include mechanisms or consolidate your sending providers."

    return make_check(
        check_name="SPF Lookup Count",
        status=status,
        severity=severity,
        summary=summary,
        technical_details=result.technical_details,
        recommended_fix=recommended_fix,
        raw_records=result.raw_records,
        confidence=result.confidence,
        can_be_false_positive=result.can_be_false_positive,
    )


def build_dmarc_check(domain: str) -> CheckResult:
    result = resolve_txt(f"_dmarc.{domain}")

    if result.status in {"timeout", "error", "nxdomain"}:
        return _error_from_dns(
            "DMARC",
            result,
            "DMARC could not be checked because DNS did not respond cleanly.",
            "Retry the check, then verify the _dmarc subdomain if the problem persists.",
        )

    dmarc_records = [record for record in result.values if record.lower().startswith("v=dmarc1")]

    if not dmarc_records:
        return make_check(
            check_name="DMARC",
            status="missing",
            severity="high",
            summary="No DMARC record found.",
            technical_details=f"No TXT record starting with v=DMARC1 was found at _dmarc.{domain}.",
            recommended_fix=f"Add a TXT record at _dmarc.{domain}, starting with v=DMARC1; p=none.",
            raw_records=[],
            confidence="high",
            can_be_false_positive=False,
        )

    if len(dmarc_records) > 1:
        return make_check(
            check_name="DMARC",
            status="error",
            severity="high",
            summary="Multiple DMARC records found.",
            technical_details="A domain should publish only one DMARC TXT record at the _dmarc subdomain.",
            recommended_fix="Remove duplicate DMARC records so only one valid policy remains.",
            raw_records=dmarc_records,
            confidence="high",
            can_be_false_positive=False,
        )

    dmarc_record = dmarc_records[0]
    tags = {}
    for part in dmarc_record.split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        tags[key.strip().lower()] = value.strip().lower()

    policy = tags.get("p")
    if policy not in {"none", "quarantine", "reject"}:
        return make_check(
            check_name="DMARC",
            status="error",
            severity="high",
            summary="DMARC record is present, but the policy is invalid or missing.",
            technical_details="The DMARC record must include p=none, p=quarantine or p=reject.",
            recommended_fix="Correct the DMARC policy tag so the record has a valid p= value.",
            raw_records=[dmarc_record],
            confidence="high",
            can_be_false_positive=False,
        )

    if policy == "none":
        return make_check(
            check_name="DMARC",
            status="warning",
            severity="medium",
            summary="DMARC is present, but policy is monitoring only.",
            technical_details="Policy p=none is minimum/monitoring mode. It does not ask receivers to quarantine or reject failing mail.",
            recommended_fix="Use p=none to monitor first. Move to quarantine or reject only after confirming legitimate senders pass authentication.",
            raw_records=[dmarc_record],
            confidence="high",
            can_be_false_positive=False,
        )

    if policy == "quarantine":
        severity = "low"
        summary = "DMARC is present with a quarantine policy."
    else:
        severity = "info"
        summary = "DMARC is present with a reject policy."

    return make_check(
        check_name="DMARC",
        status="ok",
        severity=severity,
        summary=summary,
        technical_details=f"DMARC policy is p={policy}.",
        recommended_fix=None,
        raw_records=[dmarc_record],
        confidence="high",
        can_be_false_positive=False,
    )


def build_mx_check(domain: str) -> CheckResult:
    result = resolve_mx(domain)
    has_null_mx = any(
        record.split(maxsplit=1)[0] == "0"
        and (len(record.split(maxsplit=1)) == 1 or not record.split(maxsplit=1)[1].strip())
        for record in result.values
    )

    if result.status == "ok" and result.values and not has_null_mx:
        return make_check(
            check_name="MX",
            status="ok",
            severity="info",
            summary="Your domain has MX records.",
            technical_details=f"{len(result.values)} MX record(s) found.",
            recommended_fix=None,
            raw_records=result.values,
            confidence="high",
            can_be_false_positive=False,
        )

    if result.status == "ok" and has_null_mx:
        return make_check(
            check_name="MX",
            status="missing",
            severity="medium",
            summary="This domain publishes Null MX and does not accept incoming email.",
            technical_details="A Null MX record (0 .) tells receivers that this domain is not configured to receive mail.",
            recommended_fix="Add standard MX records from your email provider if this domain should receive email.",
            raw_records=result.values,
            confidence="high",
            can_be_false_positive=False,
        )

    if result.status in {"no_answer", "nxdomain"}:
        return make_check(
            check_name="MX",
            status="missing",
            severity="medium",
            summary="No MX records found.",
            technical_details="No MX records were returned for this domain.",
            recommended_fix="Add MX records from your email provider if this domain should receive email.",
            raw_records=[],
            confidence="high",
            can_be_false_positive=False,
        )

    return _error_from_dns(
        "MX",
        result,
        "MX could not be checked because DNS did not respond cleanly.",
        "Retry the check, then verify your DNS provider if the problem persists.",
    )


def build_dkim_check(domain: str, esp_provider: str | None = None) -> CheckResult:
    normalized_esp = normalize_esp_provider(esp_provider)
    selectors = COMMON_DKIM_SELECTORS_BY_ESP.get(normalized_esp or "", DEFAULT_DKIM_SELECTORS)
    raw_records: list[str] = []
    checked_hosts: list[str] = []
    had_dns_error = False
    had_timeout = False

    for selector in selectors:
        host = f"{selector}._domainkey.{domain}"
        checked_hosts.append(host)
        result = resolve_txt(host)

        if result.status == "ok":
            dkim_records = [
                record for record in result.values if record.lower().startswith("v=dkim1")
            ]
            if dkim_records:
                raw_records.extend(dkim_records)
                confidence = "medium" if normalized_esp else "low"
                return make_check(
                    check_name="DKIM",
                    status="ok",
                    severity="info",
                    summary="DKIM record found for a common selector.",
                    technical_details=f"Found DKIM at {host}.",
                    recommended_fix=None,
                    raw_records=dkim_records,
                    confidence=confidence,
                    can_be_false_positive=not bool(normalized_esp),
                )

        if result.status == "timeout":
            had_timeout = True
        elif result.status == "error":
            had_dns_error = True

    checked_summary = ", ".join(checked_hosts[:5])
    if len(checked_hosts) > 5:
        checked_summary = f"{checked_summary}, ..."

    if had_timeout or had_dns_error:
        return make_check(
            check_name="DKIM",
            status="unknown",
            severity="medium",
            summary="DKIM could not be fully checked.",
            technical_details="DNS did not respond cleanly for one or more DKIM selector checks.",
            recommended_fix="Check your ESP's domain authentication page for the exact DKIM selector.",
            raw_records=raw_records,
            confidence="low",
            can_be_false_positive=True,
        )

    return make_check(
        check_name="DKIM",
        status="warning",
        severity="medium",
        summary="DKIM was not found using common selectors for this ESP.",
        technical_details=(
            "We did not find DKIM using common selectors for this ESP. "
            "This does not always mean DKIM is missing. "
            f"Checked: {checked_summary}."
        ),
        recommended_fix="Check your ESP domain authentication page for the exact selector.",
        raw_records=[],
        confidence="low",
        can_be_false_positive=True,
    )


def build_readiness_check(
    spf_check: CheckResult,
    dkim_check: CheckResult,
    dmarc_check: CheckResult,
    spf_lookup_check: CheckResult,
    mx_check: CheckResult,
) -> CheckResult:
    if dmarc_check.status == "missing":
        return make_check(
            check_name="Gmail/Yahoo Readiness",
            status="error",
            severity="high",
            summary="Bulk readiness is not met because DMARC is missing.",
            technical_details="DMARC is required for Gmail/Yahoo bulk sender readiness checks.",
            recommended_fix="Add a DMARC record before treating the domain as ready for bulk sending.",
            raw_records=[],
            confidence="high",
            can_be_false_positive=False,
        )

    if spf_check.status in {"missing", "error"}:
        return make_check(
            check_name="Gmail/Yahoo Readiness",
            status="error",
            severity="high",
            summary="Bulk readiness is not met because SPF is missing or broken.",
            technical_details="SPF must be valid before this domain can be treated as ready for bulk sending.",
            recommended_fix="Publish one valid SPF record for your legitimate sending providers.",
            raw_records=[],
            confidence="high",
            can_be_false_positive=False,
        )

    if mx_check.status != "ok":
        if mx_check.status == "missing":
            return make_check(
                check_name="Gmail/Yahoo Readiness",
                status="warning",
                severity="medium",
                summary="Bulk readiness needs MX records or an MX retry.",
                technical_details=(
                    "MX records are missing or could not be confirmed. "
                    "Retry the scan or verify that the domain can receive mail if it should."
                ),
                recommended_fix="Retry the check, then verify your MX records if the problem persists.",
                raw_records=[],
                confidence="medium" if mx_check.confidence == "high" else "low",
                can_be_false_positive=mx_check.canBeFalsePositive,
            )

        return make_check(
            check_name="Gmail/Yahoo Readiness",
            status="error",
            severity="high",
            summary="Bulk readiness is incomplete because MX could not be checked.",
            technical_details="MX did not respond cleanly, so the readiness check is incomplete.",
            recommended_fix="Retry the check, then verify your DNS provider if the problem persists.",
            raw_records=[],
            confidence="low",
            can_be_false_positive=True,
        )

    if spf_lookup_check.status == "error":
        return make_check(
            check_name="Gmail/Yahoo Readiness",
            status="error",
            severity="high",
            summary="Bulk readiness is blocked by SPF lookup count issues.",
            technical_details="SPF above the 10-lookup limit can cause authentication failures.",
            recommended_fix="Reduce SPF lookup count to 10 or fewer.",
            raw_records=[],
            confidence="medium",
            can_be_false_positive=spf_lookup_check.canBeFalsePositive,
        )

    if dkim_check.status in {"warning", "unknown"}:
        return make_check(
            check_name="Gmail/Yahoo Readiness",
            status="warning",
            severity="medium",
            summary="Bulk readiness needs DKIM confirmation.",
            technical_details="Gmail/Yahoo bulk sender checks require DKIM, but selector-based checks can produce false negatives.",
            recommended_fix="Confirm DKIM in your ESP domain authentication page before bulk sending.",
            raw_records=[],
            confidence="low",
            can_be_false_positive=True,
        )

    if dmarc_check.status == "warning" or spf_lookup_check.status == "warning":
        return make_check(
            check_name="Gmail/Yahoo Readiness",
            status="warning",
            severity="medium",
            summary="Bulk readiness needs work.",
            technical_details="The core records exist, but DMARC policy or SPF lookup count still needs attention.",
            recommended_fix="Review DMARC policy and SPF lookup count before treating the domain as ready for bulk sending.",
            raw_records=[],
            confidence="high",
            can_be_false_positive=spf_lookup_check.canBeFalsePositive,
        )

    return make_check(
        check_name="Gmail/Yahoo Readiness",
        status="ok",
        severity="info",
        summary="Automated bulk readiness signals look good.",
        technical_details="SPF, DKIM and DMARC are present, and SPF lookup count is within the expected range.",
        recommended_fix=None,
        raw_records=[],
        confidence="high",
        can_be_false_positive=False,
    )


def _score_from_checks(
    mx_check: CheckResult,
    spf_check: CheckResult,
    dkim_check: CheckResult,
    spf_lookup_check: CheckResult,
    dmarc_check: CheckResult,
) -> int:
    score = 0

    if mx_check.status == "ok":
        score += 10

    if spf_check.status == "ok":
        score += 20
    elif spf_check.status == "warning":
        score += 10

    if spf_lookup_check.status == "ok":
        score += 15
    elif spf_lookup_check.status == "warning":
        score += 8 if not spf_lookup_check.canBeFalsePositive else 5

    if dkim_check.status == "ok":
        score += 25 if dkim_check.confidence in {"high", "medium"} else 20
    elif dkim_check.status == "warning":
        score += 8
    elif dkim_check.status == "unknown":
        score += 5

    if dmarc_check.status in {"ok", "warning"}:
        score += 20
        raw_record = dmarc_check.rawRecords[0] if dmarc_check.rawRecords else ""
        if "p=reject" in raw_record.lower():
            score += 10
        elif "p=quarantine" in raw_record.lower():
            score += 8
        elif "p=none" in raw_record.lower():
            score += 5

    return min(score, 100)


def _aggregate_status(score: int, checks: list[CheckResult]) -> str:
    has_dns_error = any(
        check.status == "error" and check.checkName in {"SPF", "DMARC", "MX"} and check.confidence == "low"
        for check in checks
    )
    if has_dns_error:
        return "error"

    blockers = any(
        check.checkName == "DMARC" and check.status == "missing"
        or check.checkName == "SPF" and check.status == "error"
        or check.checkName == "DKIM" and check.status in {"missing", "error", "unknown"}
        or check.checkName == "SPF Lookup Count" and check.status == "error"
        or check.checkName == "Gmail/Yahoo Readiness" and check.status == "error"
        or check.checkName == "MX" and check.status != "ok"
        for check in checks
    )

    if score >= 80 and not blockers:
        return "ready"
    if score >= 50:
        return "needs_attention"
    return "not_ready"


def _summary_from_checks(domain: str, checks: list[CheckResult], status: str) -> str:
    if status == "error":
        return f"{domain} could not be fully checked because one or more DNS requests failed."

    high_priority = [
        check.summary
        for check in checks
        if check.status in {"missing", "error", "warning"}
        and check.checkName in {"SPF", "DKIM", "DMARC", "SPF Lookup Count", "MX"}
    ]

    if high_priority:
        return f"{domain}: {high_priority[0]}"

    return f"{domain} has the basic DNS signals expected for this MVP check."


def _next_steps_from_checks(checks: list[CheckResult]) -> list[str]:
    next_steps: list[str] = []
    for check in checks:
        if check.recommendedFix:
            next_steps.append(check.recommendedFix)

    if not next_steps:
        next_steps.append("Keep monitoring your DNS records when you change providers or sending setup.")

    return list(dict.fromkeys(next_steps))[:3]


def build_manual_checks() -> list[ManualCheckResult]:
    return [
        ManualCheckResult(
            checkName="One-click unsubscribe",
            status="manual_check",
            summary="This cannot be verified from DNS.",
            whyItMatters="Gmail and Yahoo expect easy unsubscribe support for marketing and subscribed bulk messages.",
            howToVerify="Check your ESP campaign settings and message headers for List-Unsubscribe and one-click unsubscribe support.",
            references=[
                {"label": "Gmail sender guidelines FAQ", "url": GMAIL_SENDER_FAQ_URL},
                {"label": "Yahoo sender best practices", "url": YAHOO_SENDER_GUIDELINES_URL},
            ],
        ),
        ManualCheckResult(
            checkName="Spam rate",
            status="manual_check",
            summary="Spam rate cannot be estimated from DNS.",
            whyItMatters="High complaint rates can affect bulk sender compliance and campaign performance.",
            howToVerify="Review user-reported spam rate in Google Postmaster Tools and your ESP/provider dashboards.",
            references=[
                {"label": "Gmail sender guidelines FAQ", "url": GMAIL_SENDER_FAQ_URL},
                {"label": "Yahoo sender best practices", "url": YAHOO_SENDER_GUIDELINES_URL},
            ],
        ),
        ManualCheckResult(
            checkName="From alignment",
            status="manual_check",
            summary="From alignment needs message-level verification.",
            whyItMatters="DMARC requires alignment between the From domain and SPF or DKIM authentication domains.",
            howToVerify="Send a real campaign/test message and inspect authentication results or your ESP domain authentication page.",
            references=[
                {"label": "Gmail sender guidelines", "url": GMAIL_SENDER_GUIDELINES_URL},
                {"label": "Yahoo sender best practices", "url": YAHOO_SENDER_GUIDELINES_URL},
            ],
        ),
    ]


def _bulk_status_from_general(status: str) -> str:
    if status == "ready":
        return "ready"
    if status == "needs_attention":
        return "needs_work"
    if status == "error":
        return "incomplete"
    return "not_ready"


def _compliance_status(check: CheckResult) -> str:
    if check.status == "ok":
        return "ok"
    if check.status in {"warning", "unknown"}:
        return "warning"
    return check.status


def build_bulk_checklist(
    spf_check: CheckResult,
    dkim_check: CheckResult,
    dmarc_check: CheckResult,
    spf_lookup_check: CheckResult,
    provider: str,
) -> list[BulkComplianceItem]:
    source_url = GMAIL_SENDER_GUIDELINES_URL if provider == "gmail" else YAHOO_SENDER_GUIDELINES_URL
    return [
        BulkComplianceItem(
            item="SPF configured",
            provider=provider,
            required=True,
            status=_compliance_status(spf_check),
            automated=True,
            explanation=spf_check.summary,
            sourceUrl=source_url,
        ),
        BulkComplianceItem(
            item="DKIM configured",
            provider=provider,
            required=True,
            status=_compliance_status(dkim_check),
            automated=True,
            explanation=dkim_check.summary,
            howToVerify="Confirm the exact DKIM selector in your ESP domain authentication page.",
            sourceUrl=source_url,
        ),
        BulkComplianceItem(
            item="DMARC configured",
            provider=provider,
            required=True,
            status=_compliance_status(dmarc_check),
            automated=True,
            explanation=dmarc_check.summary,
            sourceUrl=source_url,
        ),
        BulkComplianceItem(
            item="SPF lookup count below 10",
            provider=provider,
            required=True,
            status=_compliance_status(spf_lookup_check),
            automated=True,
            explanation=spf_lookup_check.summary,
            sourceUrl=source_url,
        ),
        BulkComplianceItem(
            item="One-click unsubscribe",
            provider=provider,
            required=True,
            status="manual_check",
            automated=False,
            explanation="This cannot be verified from DNS.",
            howToVerify="Check your ESP campaign settings and message headers.",
            sourceUrl=source_url,
        ),
        BulkComplianceItem(
            item="Spam rate",
            provider=provider,
            required=True,
            status="manual_check",
            automated=False,
            explanation="This cannot be estimated from DNS.",
            howToVerify="Review spam rate in Google Postmaster Tools or provider dashboards.",
            sourceUrl=source_url,
        ),
    ]


def build_aggregate_result(domain: str, esp_provider: str | None = None) -> AggregateResult:
    spf_check, spf_records = build_spf_check(domain)
    spf_lookup_check = build_spf_lookup_count_check(spf_records, domain)
    dkim_check = build_dkim_check(domain, esp_provider)
    dmarc_check = build_dmarc_check(domain)
    mx_check = build_mx_check(domain)
    readiness_check = build_readiness_check(spf_check, dkim_check, dmarc_check, spf_lookup_check, mx_check)

    checks = [spf_check, dkim_check, dmarc_check, mx_check, spf_lookup_check, readiness_check]
    score = _score_from_checks(mx_check, spf_check, dkim_check, spf_lookup_check, dmarc_check)
    status = _aggregate_status(score, checks)
    normalized_esp = normalize_esp_provider(esp_provider)

    return AggregateResult(
        domain=domain,
        mode="bulk_sender",
        espProvider=normalized_esp,
        score=score,
        dnsAuthenticationScore=score,
        status=status,
        bulkStatus=_bulk_status_from_general(status),
        summary=_summary_from_checks(domain, checks, status),
        checks=checks,
        automatedChecks=checks,
        manualChecks=build_manual_checks(),
        gmailBulkChecklist=build_bulk_checklist(
            spf_check,
            dkim_check,
            dmarc_check,
            spf_lookup_check,
            "gmail",
        ),
        yahooBulkChecklist=build_bulk_checklist(
            spf_check,
            dkim_check,
            dmarc_check,
            spf_lookup_check,
            "yahoo",
        ),
        nextSteps=_next_steps_from_checks(checks),
        disclaimer=DISCLAIMER,
    )


def build_spf_response(domain: str) -> CheckListResponse:
    spf_check, spf_records = build_spf_check(domain)
    spf_lookup_check = build_spf_lookup_count_check(spf_records, domain)
    return CheckListResponse(domain=domain, checks=[spf_check, spf_lookup_check])


def build_dmarc_response(domain: str) -> CheckListResponse:
    return CheckListResponse(domain=domain, checks=[build_dmarc_check(domain)])


def build_mx_response(domain: str) -> CheckListResponse:
    return CheckListResponse(domain=domain, checks=[build_mx_check(domain)])
