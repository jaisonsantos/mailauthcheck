from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers.check_domain import router as check_domain_router
from api.routers.checks import router as checks_router

DEFAULT_LOCAL_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
]


def allowed_origins_from_env() -> list[str]:
    raw_origins = os.getenv("ALLOWED_ORIGINS")
    if not raw_origins:
        return DEFAULT_LOCAL_ORIGINS

    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or DEFAULT_LOCAL_ORIGINS


app = FastAPI(
    title="MailAuthCheck API",
    version="0.1.0",
    description="MVP API skeleton for MailAuthCheck.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_from_env(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    del request, exc
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_domain",
            "message": "Enter a valid domain, like example.com. Do not include https:// or email addresses.",
        },
    )


app.include_router(check_domain_router, prefix="/api")
app.include_router(checks_router, prefix="/api")
