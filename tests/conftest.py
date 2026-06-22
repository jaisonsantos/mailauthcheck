"""Pytest configuration and shared fixtures."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import dns.resolver
from dns.exception import NXDOMAIN, Timeout

from api.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_dns_resolver():
    """Mock DNS resolver for testing."""
    with patch('dns.resolver.Resolver') as mock:
        yield mock


@pytest.fixture
def mock_dns_query_success():
    """Mock successful DNS query."""
    with patch('api.services.checks.dns_query_with_retry') as mock:
        def side_effect(domain: str, record_type: str, *args, **kwargs):
            if record_type == 'TXT' and '_dmarc' in domain:
                return ['v=DMARC1; p=reject; rua=mailto:dmarc@example.com']
            elif record_type == 'TXT':
                return ['v=spf1 include:_spf.google.com ~all']
            elif record_type == 'MX':
                return ['10 aspmx.l.google.com', '20 alt1.aspmx.l.google.com']
            elif record_type == 'A':
                return ['192.0.2.1']
            return []
        mock.side_effect = side_effect
        yield mock


@pytest.fixture
def mock_dns_query_timeout():
    """Mock DNS query timeout."""
    with patch('api.services.checks.dns_query_with_retry') as mock:
        mock.side_effect = Timeout("DNS query timeout")
        yield mock


@pytest.fixture
def mock_dns_query_nxdomain():
    """Mock DNS NXDOMAIN response."""
    with patch('api.services.checks.dns_query_with_retry') as mock:
        mock.return_value = []
        yield mock


@pytest.fixture
def valid_domains():
    """Collection of valid test domains."""
    return [
        'example.com',
        'sub.example.com',
        'my-example.com',
        'example2024.com',
        'a.co',
    ]


@pytest.fixture
def invalid_domains():
    """Collection of invalid test domains."""
    return [
        'https://example.com',
        'www.example.com',
        'user@example.com',
        '',
        '192.168.1.1',
        'example..com',
        'a' * 254 + '.com',
        'example.com!',
        '-example.com',
        'example-.com',
    ]


@pytest.fixture
def esp_providers():
    """Collection of ESP providers for testing."""
    return ['google', 'mailchimp', 'brevo', 'sendgrid', 'klaviyo', 'resend']
