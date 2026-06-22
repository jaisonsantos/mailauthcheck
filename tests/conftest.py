from __future__ import annotations

from typing import Callable

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.models import AggregateResult
from api.services import runtime


@pytest.fixture(autouse=True)
def clear_runtime_state() -> None:
    with runtime._cache_lock:
        runtime._cache.clear()
    with runtime._rate_limit_lock:
        runtime._rate_limits.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def ready_aggregate() -> AggregateResult:
    return AggregateResult(
        domain="example.com",
        mode="bulk_sender",
        espProvider=None,
        score=100,
        dnsAuthenticationScore=100,
        status="ready",
        bulkStatus="ready",
        summary="example.com has the basic DNS signals expected for this MVP check.",
        checks=[],
        automatedChecks=[],
        manualChecks=[],
        gmailBulkChecklist=[],
        yahooBulkChecklist=[],
        nextSteps=["Keep monitoring your DNS records when you change providers or sending setup."],
        disclaimer="This tool checks public DNS records and does not guarantee inbox placement.",
    )


@pytest.fixture
def forwarded_headers() -> Callable[[str], dict[str, str]]:
    def build(ip: str) -> dict[str, str]:
        return {"x-forwarded-for": ip}

    return build
