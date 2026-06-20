from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers.check_domain import router as check_domain_router
from api.routers.checks import router as checks_router


app = FastAPI(
    title="MailAuthCheck API",
    version="0.1.0",
    description="MVP API skeleton for MailAuthCheck.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
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
