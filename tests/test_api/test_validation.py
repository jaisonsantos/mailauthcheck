from __future__ import annotations

import pytest

from api.validation import DomainValidationError, normalize_domain


@pytest.mark.parametrize(
    ("raw_domain", "expected"),
    [
        ("example.com", "example.com"),
        ("Example.COM", "example.com"),
        ("sub.example.com", "sub.example.com"),
        ("my-example.com", "my-example.com"),
        ("example2024.com", "example2024.com"),
        ("www.example.com", "www.example.com"),
        ("example.com.", "example.com"),
    ],
)
def test_valid_domains(raw_domain: str, expected: str) -> None:
    assert normalize_domain(raw_domain) == expected


@pytest.mark.parametrize(
    "raw_domain",
    [
        "https://example.com",
        "http://example.com",
        "example.com/path",
        "user@example.com",
        "",
        "   ",
        "192.168.1.1",
        "example..com",
        "-example.com",
        "example-.com",
        "example!.com",
        "localhost",
        f"{'a' * 64}.com",
        f"{'a' * 250}.com",
    ],
)
def test_invalid_domains(raw_domain: str) -> None:
    with pytest.raises(DomainValidationError) as exc_info:
        normalize_domain(raw_domain)

    assert "Enter a valid domain" in str(exc_info.value)


@pytest.mark.parametrize(
    ("raw_domain", "message"),
    [
        ("https://example.com", "not a URL"),
        ("user@example.com", "not an email address"),
        ("192.168.1.1", "not an IP address"),
        (f"{'a' * 250}.com", "shorter than 254 characters"),
    ],
)
def test_invalid_domain_messages_are_actionable(raw_domain: str, message: str) -> None:
    with pytest.raises(DomainValidationError) as exc_info:
        normalize_domain(raw_domain)

    assert message in str(exc_info.value)
