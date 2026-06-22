from __future__ import annotations

from unittest.mock import patch

from api.services.dns_resolver import DNSQueryResult


def test_check_domain_ready_domain(client) -> None:
    def fake_txt(name: str) -> DNSQueryResult:
        if name == "example.com":
            return DNSQueryResult(status="ok", values=["v=spf1 -all"])
        if name == "_dmarc.example.com":
            return DNSQueryResult(status="ok", values=["v=DMARC1; p=reject"])
        if name == "default._domainkey.example.com":
            return DNSQueryResult(status="ok", values=["v=DKIM1; p=abc123"])
        return DNSQueryResult(status="no_answer", values=[])

    with patch("api.services.checks.resolve_txt", side_effect=fake_txt), patch(
        "api.services.checks.resolve_mx",
        return_value=DNSQueryResult(status="ok", values=["10 mail.example.com"]),
    ):
        response = client.post("/api/check-domain", json={"domain": "example.com"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["score"] >= 80
    assert payload["status"] == "ready"


def test_check_domain_needs_attention(client) -> None:
    def fake_txt(name: str) -> DNSQueryResult:
        if name == "example.com":
            return DNSQueryResult(status="ok", values=["v=spf1 ~all"])
        if name == "_dmarc.example.com":
            return DNSQueryResult(status="ok", values=["v=DMARC1; p=none"])
        return DNSQueryResult(status="no_answer", values=[])

    with patch("api.services.checks.resolve_txt", side_effect=fake_txt), patch(
        "api.services.checks.resolve_mx",
        return_value=DNSQueryResult(status="ok", values=["10 mail.example.com"]),
    ):
        response = client.post("/api/check-domain", json={"domain": "example.com"})

    assert response.status_code == 200
    payload = response.json()
    assert 50 <= payload["score"] < 80
    assert payload["status"] == "needs_attention"


def test_invalid_domain_rejected(client) -> None:
    response = client.post("/api/check-domain", json={"domain": "https://example.com"})

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_domain"


def test_dns_timeout_returns_incomplete_result(client) -> None:
    with patch(
        "api.services.checks.resolve_txt",
        return_value=DNSQueryResult(status="timeout", values=[], error_category="timeout"),
    ), patch(
        "api.services.checks.resolve_mx",
        return_value=DNSQueryResult(status="timeout", values=[], error_category="timeout"),
    ):
        response = client.post("/api/check-domain", json={"domain": "timeout.com"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["bulkStatus"] == "incomplete"
