from __future__ import annotations

from unittest.mock import patch

import pytest

from api.services import runtime


def test_first_request_allowed() -> None:
    runtime.enforce_rate_limit("203.0.113.10", "example.com")


def test_rapid_same_domain_blocked() -> None:
    for _ in range(runtime.DOMAIN_RATE_LIMIT_MAX_REQUESTS):
        runtime.enforce_rate_limit("203.0.113.10", "example.com")

    with pytest.raises(runtime.RateLimitExceeded):
        runtime.enforce_rate_limit("203.0.113.10", "example.com")


def test_different_domains_allowed() -> None:
    for index in range(runtime.DOMAIN_RATE_LIMIT_MAX_REQUESTS + 2):
        runtime.enforce_rate_limit("203.0.113.10", f"example{index}.com")


def test_different_ips_allowed() -> None:
    for index in range(runtime.DOMAIN_RATE_LIMIT_MAX_REQUESTS + 2):
        runtime.enforce_rate_limit(f"203.0.113.{index}", "example.com")


def test_rate_limit_headers(client, ready_aggregate, forwarded_headers) -> None:
    with patch("api.routers.check_domain.get_cached_response", return_value=None), patch(
        "api.routers.check_domain.store_cached_response",
    ), patch("api.routers.check_domain.build_aggregate_result", return_value=ready_aggregate):
        for _ in range(runtime.DOMAIN_RATE_LIMIT_MAX_REQUESTS):
            response = client.post(
                "/api/check-domain",
                json={"domain": "example.com"},
                headers=forwarded_headers("203.0.113.10"),
            )
            assert response.status_code == 200

        response = client.post(
            "/api/check-domain",
            json={"domain": "example.com"},
            headers=forwarded_headers("203.0.113.10"),
        )

    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"
    assert response.json()["error"] == "rate_limited"


def test_cache_hit_not_counted(client, ready_aggregate, forwarded_headers) -> None:
    with patch("api.routers.check_domain.build_aggregate_result", return_value=ready_aggregate):
        for _ in range(runtime.DOMAIN_RATE_LIMIT_MAX_REQUESTS + 3):
            response = client.post(
                "/api/check-domain",
                json={"domain": "example.com"},
                headers=forwarded_headers("203.0.113.10"),
            )
            assert response.status_code == 200

    assert response.json()["status"] == "ready"
