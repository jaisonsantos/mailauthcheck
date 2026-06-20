from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from api.models import AggregateResult, DomainRequest, ErrorResponse
from api.services.checks import build_aggregate_result
from api.validation import DomainValidationError, normalize_domain


router = APIRouter()


@router.post(
    "/check-domain",
    response_model=AggregateResult,
    responses={400: {"model": ErrorResponse}},
)
def check_domain(payload: DomainRequest) -> AggregateResult | JSONResponse:
    try:
        domain = normalize_domain(payload.domain)
    except DomainValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_domain",
                "message": str(exc),
            },
        )

    return build_aggregate_result(domain)
