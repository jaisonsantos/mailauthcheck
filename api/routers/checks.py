from __future__ import annotations

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from api.models import CheckListResponse, ErrorResponse
from api.services.placeholder_results import build_single_check_response
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


@router.get("/spf", response_model=CheckListResponse, responses={400: {"model": ErrorResponse}})
def get_spf(domain: str = Query(..., min_length=1)) -> CheckListResponse | JSONResponse:
    normalized_domain = _normalize_or_raise(domain)
    if isinstance(normalized_domain, JSONResponse):
        return normalized_domain
    return build_single_check_response(
        normalized_domain,
        "SPF",
        "SPF placeholder result is available, but DNS lookup is not wired yet.",
    )


@router.get("/dmarc", response_model=CheckListResponse, responses={400: {"model": ErrorResponse}})
def get_dmarc(domain: str = Query(..., min_length=1)) -> CheckListResponse | JSONResponse:
    normalized_domain = _normalize_or_raise(domain)
    if isinstance(normalized_domain, JSONResponse):
        return normalized_domain
    return build_single_check_response(
        normalized_domain,
        "DMARC",
        "DMARC placeholder result is available, but DNS lookup is not wired yet.",
    )


@router.get("/mx", response_model=CheckListResponse, responses={400: {"model": ErrorResponse}})
def get_mx(domain: str = Query(..., min_length=1)) -> CheckListResponse | JSONResponse:
    normalized_domain = _normalize_or_raise(domain)
    if isinstance(normalized_domain, JSONResponse):
        return normalized_domain
    return build_single_check_response(
        normalized_domain,
        "MX",
        "MX placeholder result is available, but DNS lookup is not wired yet.",
    )
