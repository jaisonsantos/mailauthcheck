from __future__ import annotations

import re


DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)

INVALID_DOMAIN_MESSAGE = (
    "Enter a valid domain, like example.com. Do not include https:// or email addresses."
)


class DomainValidationError(ValueError):
    pass


def normalize_domain(raw_domain: str) -> str:
    domain = raw_domain.strip().lower().rstrip(".")

    if not domain:
        raise DomainValidationError(INVALID_DOMAIN_MESSAGE)

    if "://" in domain or "/" in domain or "@" in domain:
        raise DomainValidationError(INVALID_DOMAIN_MESSAGE)

    try:
        domain = domain.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise DomainValidationError(INVALID_DOMAIN_MESSAGE) from exc

    if not DOMAIN_PATTERN.match(domain):
        raise DomainValidationError(INVALID_DOMAIN_MESSAGE)

    return domain
