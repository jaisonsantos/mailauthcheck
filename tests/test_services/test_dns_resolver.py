from __future__ import annotations

from unittest.mock import patch

import dns.exception
import dns.resolver

from api.services import dns_resolver


class FakeTxtAnswer:
    strings = [b"v=spf1 -all"]


class FakeMxAnswer:
    preference = 10
    exchange = "mail.example.com."


def test_resolve_txt_retries_timeout_then_succeeds() -> None:
    with patch(
        "dns.resolver.Resolver.resolve",
        side_effect=[dns.exception.Timeout, [FakeTxtAnswer()]],
    ) as resolve:
        result = dns_resolver.resolve_txt("example.com")

    assert resolve.call_count == 2
    assert result.status == "ok"
    assert result.values == ["v=spf1 -all"]


def test_resolve_txt_timeout_after_retries() -> None:
    with patch(
        "dns.resolver.Resolver.resolve",
        side_effect=dns.exception.Timeout,
    ) as resolve:
        result = dns_resolver.resolve_txt("example.com")

    assert resolve.call_count == dns_resolver.DNS_RETRY_ATTEMPTS
    assert result.status == "timeout"
    assert result.error_category == "timeout"


def test_resolve_mx_retries_timeout_then_succeeds() -> None:
    with patch(
        "dns.resolver.Resolver.resolve",
        side_effect=[dns.exception.Timeout, [FakeMxAnswer()]],
    ) as resolve:
        result = dns_resolver.resolve_mx("example.com")

    assert resolve.call_count == 2
    assert result.status == "ok"
    assert result.values == ["10 mail.example.com"]


def test_resolve_mx_nxdomain() -> None:
    with patch("dns.resolver.Resolver.resolve", side_effect=dns.resolver.NXDOMAIN):
        result = dns_resolver.resolve_mx("missing.example")

    assert result.status == "nxdomain"
    assert result.error_category == "nxdomain"
