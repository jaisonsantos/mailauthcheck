from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from api.models import AggregateResult, DomainRequest, ErrorResponse
from api.services.checks import build_aggregate_result, normalize_esp_provider
from api.services.runtime import (
    domain_hash,
    domain_tld,
    enforce_rate_limit,
    extract_client_ip,
    get_cached_response,
    log_api_event,
    score_bucket,
    store_cached_response,
    RateLimitExceeded,
)
from api.validation import DomainValidationError, normalize_domain


router = APIRouter()


@router.post(
    "/check-domain",
    response_model=AggregateResult,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
def check_domain(payload: DomainRequest, request: Request) -> AggregateResult | JSONResponse:
    started_at = perf_counter()
    client_ip = extract_client_ip(request)

    try:
        domain = normalize_domain(payload.domain)
    except DomainValidationError as exc:
        log_api_event(
            "scan_rejected",
            endpoint="/api/check-domain",
            client_ip=client_ip,
            reason="invalid_domain",
            latency_ms=round((perf_counter() - started_at) * 1000, 2),
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_domain",
                "message": str(exc),
            },
        )

    esp_provider = normalize_esp_provider(payload.espProvider)
    cache_key = f"aggregate:{domain}:bulk_sender:{esp_provider or 'unknown'}"
    cached_result = get_cached_response(cache_key, AggregateResult)
    if cached_result is not None:
        log_api_event(
            "scan_completed",
            endpoint="/api/check-domain",
            client_ip=client_ip,
            domain_hash=domain_hash(domain),
            tld=domain_tld(domain),
            status=cached_result.status,
            score_bucket=score_bucket(cached_result.score),
            esp_provider=esp_provider,
            failed_checks=[
                check.checkName
                for check in cached_result.checks
                if check.status in {"warning", "missing", "error"}
            ],
            cache_hit=True,
            latency_ms=round((perf_counter() - started_at) * 1000, 2),
        )
        return cached_result

    try:
        enforce_rate_limit(client_ip, domain)
    except RateLimitExceeded as exc:
        log_api_event(
            "scan_rejected",
            endpoint="/api/check-domain",
            client_ip=client_ip,
            domain_hash=domain_hash(domain),
            tld=domain_tld(domain),
            reason="rate_limited",
            latency_ms=round((perf_counter() - started_at) * 1000, 2),
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={"Retry-After": "60"},
            content={
                "error": "rate_limited",
                "message": str(exc),
            },
        )

    result = build_aggregate_result(domain, esp_provider)
    store_cached_response(cache_key, result)
    log_api_event(
        "scan_completed",
        endpoint="/api/check-domain",
        client_ip=client_ip,
        domain_hash=domain_hash(domain),
        tld=domain_tld(domain),
        status=result.status,
        score_bucket=score_bucket(result.score),
        esp_provider=esp_provider,
        failed_checks=[
            check.checkName for check in result.checks if check.status in {"warning", "missing", "error"}
        ],
        cache_hit=False,
        latency_ms=round((perf_counter() - started_at) * 1000, 2),
    )
    return result
