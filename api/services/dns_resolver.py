from __future__ import annotations

from dataclasses import dataclass

import dns.exception
import dns.resolver


DNS_TIMEOUT_SECONDS = 3.0


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

    try:
        answers = resolver.resolve(name, "TXT")
    except dns.resolver.NXDOMAIN:
        return DNSQueryResult(status="nxdomain", values=[], error_category="nxdomain")
    except dns.resolver.NoAnswer:
        return DNSQueryResult(status="no_answer", values=[], error_category="no_answer")
    except dns.exception.Timeout:
        return DNSQueryResult(status="timeout", values=[], error_category="timeout")
    except dns.resolver.NoNameservers:
        return DNSQueryResult(status="error", values=[], error_category="no_nameservers")
    except dns.exception.DNSException:
        return DNSQueryResult(status="error", values=[], error_category="dns_error")

    values = []
    for answer in answers:
        if hasattr(answer, "strings"):
            parts = [part.decode("utf-8", errors="replace") for part in answer.strings]
            values.append("".join(parts))
        else:
            values.append(answer.to_text().replace('"', ""))

    return DNSQueryResult(status="ok", values=values)


def resolve_mx(name: str) -> DNSQueryResult:
    resolver = _build_resolver()

    try:
        answers = resolver.resolve(name, "MX")
    except dns.resolver.NXDOMAIN:
        return DNSQueryResult(status="nxdomain", values=[], error_category="nxdomain")
    except dns.resolver.NoAnswer:
        return DNSQueryResult(status="no_answer", values=[], error_category="no_answer")
    except dns.exception.Timeout:
        return DNSQueryResult(status="timeout", values=[], error_category="timeout")
    except dns.resolver.NoNameservers:
        return DNSQueryResult(status="error", values=[], error_category="no_nameservers")
    except dns.exception.DNSException:
        return DNSQueryResult(status="error", values=[], error_category="dns_error")

    values = []
    for answer in answers:
        values.append(f"{answer.preference} {str(answer.exchange).rstrip('.')}")

    return DNSQueryResult(status="ok", values=values)
