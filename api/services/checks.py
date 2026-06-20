from __future__ import annotations

from dataclasses import dataclass

from api.models import AggregateResult, CheckListResponse, CheckResult
from api.services.dns_resolver import DNSQueryResult, resolve_mx, resolve_txt


DISCLAIMER = (
    "This is a DNS/authentication check and does not guarantee inbox placement."
)

SPF_LOOKUP_MECHANISMS = ("include:", "a", "mx", "ptr", "exists:", "redirect=")


@dataclass(slots=True)
class SPFCountResult:
    count: int | None
    confidence: str
    can_be_false_positive: bool
    technical_details: str
    raw_records: list[str]
    error: str | None = None


@dataclass(slots=True)
class AggregateComputation:
    checks: list[CheckResult]
    score: int
    status: str
    summary: str
    next_steps: list[str]


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

    if uses_unsafe_all or missing_all:
        return (
            make_check(
                check_name="SPF",
                status="warning",
                severity="medium",
                summary="SPF exists, but the policy looks weak.",
                technical_details="The SPF record uses +all or does not end with a clear all mechanism.",
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
            error="recursion_limit",
        )

    visited.add(domain_key)
    count = 0
    raw_records = [spf_record]
    uncertain = False
    technical_notes: list[str] = []

    for token in spf_record.split():
        normalized = token.lstrip("+-~?")

        if normalized.startswith("include:"):
            count += 1
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
                technical_notes.append(nested_result.technical_details)
            else:
                uncertain = True
                technical_notes.append(
                    f"Include domain {include_domain} could not be resolved completely."
                )

        elif normalized.startswith("redirect="):
            count += 1
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
                technical_notes.append(nested_result.technical_details)
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

    details = f"Estimated DNS lookups: {count}."
    if uncertain:
        details = f"{details} Some nested SPF parsing was incomplete."
    if technical_notes:
        details = f"{details} {' '.join(dict.fromkeys(technical_notes))}"

    return SPFCountResult(
        count=count,
        confidence="medium",
        can_be_false_positive=uncertain,
        technical_details=details,
        raw_records=list(dict.fromkeys(raw_records)),
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
            technical_details="Policy p=none does not ask receivers to quarantine or reject failing mail.",
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


def build_readiness_check(
    spf_check: CheckResult,
    dmarc_check: CheckResult,
    spf_lookup_check: CheckResult,
) -> CheckResult:
    if dmarc_check.status == "missing":
        return make_check(
            check_name="Gmail/Yahoo Readiness",
            status="error",
            severity="high",
            summary="Basic readiness is not met because DMARC is missing.",
            technical_details="DMARC is required for basic Gmail/Yahoo bulk sender readiness checks.",
            recommended_fix="Add a DMARC record before treating the domain as ready to send email at scale.",
            raw_records=[],
            confidence="high",
            can_be_false_positive=False,
        )

    if spf_check.status in {"missing", "error"}:
        return make_check(
            check_name="Gmail/Yahoo Readiness",
            status="error",
            severity="high",
            summary="Basic readiness is not met because SPF is missing or broken.",
            technical_details="SPF must be valid before this domain can be treated as basically ready.",
            recommended_fix="Publish one valid SPF record for your legitimate sending providers.",
            raw_records=[],
            confidence="high",
            can_be_false_positive=False,
        )

    if spf_lookup_check.status == "error":
        return make_check(
            check_name="Gmail/Yahoo Readiness",
            status="error",
            severity="high",
            summary="Basic readiness is blocked by SPF lookup count issues.",
            technical_details="SPF above the 10-lookup limit can cause authentication failures.",
            recommended_fix="Reduce SPF lookup count to 10 or fewer.",
            raw_records=[],
            confidence="medium",
            can_be_false_positive=spf_lookup_check.canBeFalsePositive,
        )

    if dmarc_check.status == "warning" or spf_lookup_check.status == "warning":
        return make_check(
            check_name="Gmail/Yahoo Readiness",
            status="warning",
            severity="medium",
            summary="Basic readiness is partial.",
            technical_details="The core records exist, but DMARC policy or SPF lookup count still needs attention.",
            recommended_fix="Strengthen DMARC policy or reduce SPF lookup count before calling the domain fully ready.",
            raw_records=[],
            confidence="high",
            can_be_false_positive=spf_lookup_check.canBeFalsePositive,
        )

    return make_check(
        check_name="Gmail/Yahoo Readiness",
        status="ok",
        severity="info",
        summary="Basic readiness looks good.",
        technical_details="SPF and DMARC are present, and SPF lookup count is within the expected range.",
        recommended_fix=None,
        raw_records=[],
        confidence="high",
        can_be_false_positive=False,
    )


def _score_from_checks(
    mx_check: CheckResult,
    spf_check: CheckResult,
    spf_lookup_check: CheckResult,
    dmarc_check: CheckResult,
    readiness_check: CheckResult,
) -> int:
    score = 0

    if mx_check.status == "ok":
        score += 15

    if spf_check.status == "ok":
        score += 20
    elif spf_check.status == "warning":
        score += 10

    if spf_lookup_check.status == "ok":
        score += 15
    elif spf_lookup_check.status == "warning":
        score += 8 if not spf_lookup_check.canBeFalsePositive else 5

    if dmarc_check.status in {"ok", "warning"}:
        score += 25
        raw_record = dmarc_check.rawRecords[0] if dmarc_check.rawRecords else ""
        if "p=reject" in raw_record.lower():
            score += 10
        elif "p=quarantine" in raw_record.lower():
            score += 8
        elif "p=none" in raw_record.lower():
            score += 5

    if readiness_check.status == "ok":
        score += 15
    elif readiness_check.status == "warning":
        score += 8

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
        and check.checkName in {"SPF", "DMARC", "SPF Lookup Count", "MX"}
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


def build_aggregate_result(domain: str) -> AggregateResult:
    spf_check, spf_records = build_spf_check(domain)
    spf_lookup_check = build_spf_lookup_count_check(spf_records, domain)
    dmarc_check = build_dmarc_check(domain)
    mx_check = build_mx_check(domain)
    readiness_check = build_readiness_check(spf_check, dmarc_check, spf_lookup_check)

    checks = [spf_check, dmarc_check, mx_check, spf_lookup_check, readiness_check]
    score = _score_from_checks(mx_check, spf_check, spf_lookup_check, dmarc_check, readiness_check)
    status = _aggregate_status(score, checks)

    return AggregateResult(
        domain=domain,
        score=score,
        status=status,
        summary=_summary_from_checks(domain, checks, status),
        checks=checks,
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
