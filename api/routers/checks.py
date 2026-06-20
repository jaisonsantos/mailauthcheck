from __future__ import annotations

from time import perf_counter
from typing import Callable

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse

from api.models import CheckListResponse, ErrorResponse
from api.services.checks import (
    build_dmarc_response,
    build_mx_response,
    build_spf_response,
)
from api.services.runtime import (
    RateLimitExceeded,
    domain_hash,
    domain_tld,
    enforce_rate_limit,
    extract_client_ip,
    get_cached_response,
    log_api_event,
    store_cached_response,
)
from api.validation import DomainValidationError, normalize_domain


router = APIRouter()


def _normalize_or_raise(domain: str) -> str | JSONResponse:
    try:
        return normalize_domain(domain)
    except DomainValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_domain",
                "message": str(exc),
            },
        )


def _handle_check_request(
    *,
    request: Request,
    endpoint: str,
    domain: str,
    builder: Callable[[str], CheckListResponse],
) -> CheckListResponse | JSONResponse:
    started_at = perf_counter()
    client_ip = extract_client_ip(request)
    normalized_domain = _normalize_or_raise(domain)
    if isinstance(normalized_domain, JSONResponse):
        log_api_event(
            "scan_rejected",
            endpoint=endpoint,
            client_ip=client_ip,
            reason="invalid_domain",
            latency_ms=round((perf_counter() - started_at) * 1000, 2),
        )
        return normalized_domain

    cache_key = f"{endpoint}:{normalized_domain}"
    cached_result = get_cached_response(cache_key, CheckListResponse)
    if cached_result is not None:
        log_api_event(
            "scan_completed",
            endpoint=endpoint,
            client_ip=client_ip,
            domain_hash=domain_hash(normalized_domain),
            tld=domain_tld(normalized_domain),
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
        enforce_rate_limit(client_ip, normalized_domain)
    except RateLimitExceeded as exc:
        log_api_event(
            "scan_rejected",
            endpoint=endpoint,
            client_ip=client_ip,
            domain_hash=domain_hash(normalized_domain),
            tld=domain_tld(normalized_domain),
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

    result = builder(normalized_domain)
    store_cached_response(cache_key, result)
    log_api_event(
        "scan_completed",
        endpoint=endpoint,
        client_ip=client_ip,
        domain_hash=domain_hash(normalized_domain),
        tld=domain_tld(normalized_domain),
        failed_checks=[
            check.checkName for check in result.checks if check.status in {"warning", "missing", "error"}
        ],
        cache_hit=False,
        latency_ms=round((perf_counter() - started_at) * 1000, 2),
    )
    return result


@router.get(
    "/spf",
    response_model=CheckListResponse,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
def get_spf(
    request: Request,
    domain: str = Query(..., min_length=1),
) -> CheckListResponse | JSONResponse:
    return _handle_check_request(
        request=request,
        endpoint="/api/spf",
        domain=domain,
        builder=build_spf_response,
    )


@router.get(
    "/dmarc",
    response_model=CheckListResponse,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
def get_dmarc(
    request: Request,
    domain: str = Query(..., min_length=1),
) -> CheckListResponse | JSONResponse:
    return _handle_check_request(
        request=request,
        endpoint="/api/dmarc",
        domain=domain,
        builder=build_dmarc_response,
    )


@router.get(
    "/mx",
    response_model=CheckListResponse,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
def get_mx(
    request: Request,
    domain: str = Query(..., min_length=1),
) -> CheckListResponse | JSONResponse:
    return _handle_check_request(
        request=request,
        endpoint="/api/mx",
        domain=domain,
        builder=build_mx_response,
    )
