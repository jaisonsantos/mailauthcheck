from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from time import monotonic
from typing import TypeVar

from fastapi import Request
from pydantic import BaseModel


CACHE_TTL_SECONDS = 900
IP_RATE_LIMIT_WINDOW_SECONDS = 60
IP_RATE_LIMIT_MAX_REQUESTS = 30
DOMAIN_RATE_LIMIT_WINDOW_SECONDS = 60
DOMAIN_RATE_LIMIT_MAX_REQUESTS = 10

ModelT = TypeVar("ModelT", bound=BaseModel)


@dataclass(slots=True)
class CacheEntry:
    expires_at: float
    value: BaseModel


@dataclass(slots=True)
class RateLimitEntry:
    window_started_at: float
    count: int


class RateLimitExceeded(Exception):
    pass


_cache_lock = Lock()
_cache: dict[str, CacheEntry] = {}

_rate_limit_lock = Lock()
_rate_limits: dict[str, RateLimitEntry] = {}


def extract_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        first_ip = forwarded_for.split(",", 1)[0].strip()
        if first_ip:
            return first_ip

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def get_cached_response(cache_key: str, response_model: type[ModelT]) -> ModelT | None:
    now = monotonic()
    with _cache_lock:
        entry = _cache.get(cache_key)
        if entry is None:
            return None
        if entry.expires_at <= now:
            _cache.pop(cache_key, None)
            return None
        return response_model.model_validate(entry.value.model_dump())


def store_cached_response(cache_key: str, value: BaseModel) -> None:
    with _cache_lock:
        _cache[cache_key] = CacheEntry(
            expires_at=monotonic() + CACHE_TTL_SECONDS,
            value=value,
        )


def enforce_rate_limit(client_ip: str, domain: str) -> None:
    _increment_rate_limit(
        f"ip:{client_ip}",
        limit=IP_RATE_LIMIT_MAX_REQUESTS,
        window_seconds=IP_RATE_LIMIT_WINDOW_SECONDS,
        message="Too many checks from this IP. Please try again in a minute.",
    )
    _increment_rate_limit(
        f"ip-domain:{client_ip}:{domain}",
        limit=DOMAIN_RATE_LIMIT_MAX_REQUESTS,
        window_seconds=DOMAIN_RATE_LIMIT_WINDOW_SECONDS,
        message="Too many repeated checks for this domain. Please try again in a minute.",
    )


def log_api_event(event: str, **fields: object) -> None:
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event,
        **fields,
    }
    print(json.dumps(payload, sort_keys=True))


def domain_hash(domain: str) -> str:
    return hashlib.sha256(domain.encode("utf-8")).hexdigest()[:12]


def domain_tld(domain: str) -> str:
    parts = [part for part in domain.split(".") if part]
    if len(parts) < 2:
        return domain
    return parts[-1]


def score_bucket(score: int | None) -> str | None:
    if score is None:
        return None
    if score >= 90:
        return "90-100"
    if score >= 70:
        return "70-89"
    if score >= 40:
        return "40-69"
    return "0-39"


def _increment_rate_limit(
    key: str,
    *,
    limit: int,
    window_seconds: int,
    message: str,
) -> None:
    now = monotonic()
    with _rate_limit_lock:
        entry = _rate_limits.get(key)
        if entry is None or now - entry.window_started_at >= window_seconds:
            _rate_limits[key] = RateLimitEntry(window_started_at=now, count=1)
            return

        if entry.count >= limit:
            raise RateLimitExceeded(message)

        entry.count += 1
