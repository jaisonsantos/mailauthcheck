"""DNS client with timeout and retry handling."""
from __future__ import annotations

import logging
from typing import Literal

import dns.resolver
from dns.exception import Timeout, NXDOMAIN, DNSException

from api.errors import DNSTimeoutError, DNSError

logger = logging.getLogger(__name__)

DNS_TIMEOUT_SECONDS = 3.0
DNS_RETRY_ATTEMPTS = 2


def dns_query_with_retry(
    domain: str,
    record_type: Literal["A", "AAAA", "MX", "TXT", "NS", "SOA", "CNAME"],
    timeout: float = DNS_TIMEOUT_SECONDS,
    retry_attempts: int = DNS_RETRY_ATTEMPTS,
) -> list[str]:
    """
    Query DNS with timeout and retry logic.

    Args:
        domain: Domain to query
        record_type: DNS record type (A, MX, TXT, etc)
        timeout: Query timeout in seconds
        retry_attempts: Number of retry attempts

    Returns:
        List of DNS records as strings, or empty list if not found

    Raises:
        DNSTimeoutError: If timeout after all retries
        DNSError: If other DNS errors occur
    """
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout

    for attempt in range(retry_attempts):
        try:
            logger.debug(f"DNS query: {domain} {record_type} (attempt {attempt + 1}/{retry_attempts})")
            response = resolver.resolve(domain, record_type)
            records = [str(r) for r in response]
            logger.debug(f"DNS query success: {domain} {record_type} -> {len(records)} records")
            return records

        except Timeout as e:
            logger.warning(
                f"DNS timeout: {domain} {record_type} (attempt {attempt + 1}/{retry_attempts})"
            )
            if attempt == retry_attempts - 1:
                raise DNSTimeoutError(domain)
            continue

        except NXDOMAIN:
            logger.debug(f"DNS NXDOMAIN: {domain} {record_type}")
            return []  # Domain doesn't exist

        except DNSException as e:
            logger.warning(f"DNS error: {domain} {record_type} -> {str(e)}")
            return []  # Other DNS errors

    return []
