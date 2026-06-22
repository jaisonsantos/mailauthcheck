from __future__ import annotations

from dataclasses import dataclass
import logging

import dns.exception
import dns.resolver


DNS_TIMEOUT_SECONDS = 3.0
DNS_RETRY_ATTEMPTS = 2
logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DNSQueryResult:
    status: str
    values: list[str]
    error_category: str | None = None


def _build_resolver() -> dns.resolver.Resolver:
    resolver = dns.resolver.Resolver()
    resolver.timeout = DNS_TIMEOUT_SECONDS
    resolver.lifetime = DNS_TIMEOUT_SECONDS
    return resolver


def resolve_txt(name: str) -> DNSQueryResult:
    resolver = _build_resolver()

    answers_result = _resolve_with_retry(resolver, name, "TXT")
    if answers_result.status != "ok" or answers_result.answers is None:
        return DNSQueryResult(
            status=answers_result.status,
            values=[],
            error_category=answers_result.error_category,
        )

    values = []
    for answer in answers_result.answers:
        if hasattr(answer, "strings"):
            parts = [part.decode("utf-8", errors="replace") for part in answer.strings]
            values.append("".join(parts))
        else:
            values.append(answer.to_text().replace('"', ""))

    return DNSQueryResult(status="ok", values=values)


def resolve_mx(name: str) -> DNSQueryResult:
    resolver = _build_resolver()

    answers_result = _resolve_with_retry(resolver, name, "MX")
    if answers_result.status != "ok" or answers_result.answers is None:
        return DNSQueryResult(
            status=answers_result.status,
            values=[],
            error_category=answers_result.error_category,
        )

    values = []
    for answer in answers_result.answers:
        values.append(f"{answer.preference} {str(answer.exchange).rstrip('.')}")

    return DNSQueryResult(status="ok", values=values)


@dataclass(slots=True)
class DNSAnswersResult:
    status: str
    answers: object | None
    error_category: str | None = None


def _resolve_with_retry(
    resolver: dns.resolver.Resolver,
    name: str,
    record_type: str,
) -> DNSAnswersResult:
    for attempt in range(1, DNS_RETRY_ATTEMPTS + 1):
        try:
            return DNSAnswersResult(
                status="ok",
                answers=resolver.resolve(name, record_type),
            )
        except dns.exception.Timeout:
            logger.warning(
                "DNS timeout: %s %s attempt %s/%s",
                name,
                record_type,
                attempt,
                DNS_RETRY_ATTEMPTS,
            )
            if attempt == DNS_RETRY_ATTEMPTS:
                return DNSAnswersResult(
                    status="timeout",
                    answers=None,
                    error_category="timeout",
                )
        except dns.resolver.NXDOMAIN:
            return DNSAnswersResult(status="nxdomain", answers=None, error_category="nxdomain")
        except dns.resolver.NoAnswer:
            return DNSAnswersResult(status="no_answer", answers=None, error_category="no_answer")
        except dns.resolver.NoNameservers:
            return DNSAnswersResult(
                status="error",
                answers=None,
                error_category="no_nameservers",
            )
        except dns.exception.DNSException:
            return DNSAnswersResult(status="error", answers=None, error_category="dns_error")

    return DNSAnswersResult(status="timeout", answers=None, error_category="timeout")
