"""Tests for domain validation."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.validation import normalize_domain, DomainValidationError
from api.main import app

client = TestClient(app)


class TestDomainValidation:
    """Test domain validation logic."""

    # Valid domains
    def test_valid_domain_simple(self):
        """Test simple valid domain."""
        result = normalize_domain('example.com')
        assert result == 'example.com'

    def test_valid_domain_subdomain(self):
        """Test subdomain is valid."""
        result = normalize_domain('sub.example.com')
        assert result == 'sub.example.com'

    def test_valid_domain_hyphenated(self):
        """Test hyphenated domain."""
        result = normalize_domain('my-example.com')
        assert result == 'my-example.com'

    def test_valid_domain_numbers(self):
        """Test domain with numbers."""
        result = normalize_domain('example2024.com')
        assert result == 'example2024.com'

    def test_valid_domain_case_insensitive(self):
        """Test domain is lowercased."""
        result = normalize_domain('Example.COM')
        assert result == 'example.com'

    def test_valid_domain_whitespace_trimmed(self):
        """Test leading/trailing whitespace removed."""
        result = normalize_domain('  example.com  ')
        assert result == 'example.com'

    # Invalid domains - URLs
    def test_reject_url_with_https(self):
        """Test HTTPS URL rejected."""
        with pytest.raises(DomainValidationError) as exc_info:
            normalize_domain('https://example.com')
        assert 'https://' in str(exc_info.value).lower()

    def test_reject_url_with_http(self):
        """Test HTTP URL rejected."""
        with pytest.raises(DomainValidationError):
            normalize_domain('http://example.com')

    def test_reject_www_prefix(self):
        """Test www prefix rejected."""
        with pytest.raises(DomainValidationError) as exc_info:
            normalize_domain('www.example.com')
        assert 'www' in str(exc_info.value).lower()

    # Invalid domains - emails
    def test_reject_email_address(self):
        """Test email address rejected."""
        with pytest.raises(DomainValidationError) as exc_info:
            normalize_domain('user@example.com')
        assert 'email' in str(exc_info.value).lower() or '@' in str(exc_info.value)

    # Invalid domains - empty
    def test_reject_empty_string(self):
        """Test empty string rejected."""
        with pytest.raises(DomainValidationError):
            normalize_domain('')

    # Invalid domains - IPs
    def test_reject_ipv4_address(self):
        """Test IPv4 address rejected."""
        with pytest.raises(DomainValidationError) as exc_info:
            normalize_domain('192.168.1.1')
        assert 'ip' in str(exc_info.value).lower()

    def test_reject_ipv6_address(self):
        """Test IPv6 address rejected."""
        with pytest.raises(DomainValidationError):
            normalize_domain('2001:db8::1')

    # Invalid domains - format
    def test_reject_double_dots(self):
        """Test double dots rejected."""
        with pytest.raises(DomainValidationError):
            normalize_domain('example..com')

    def test_reject_too_long_domain(self):
        """Test domain > 253 chars rejected."""
        long_domain = 'a' * 254 + '.com'
        with pytest.raises(DomainValidationError) as exc_info:
            normalize_domain(long_domain)
        assert 'long' in str(exc_info.value).lower()

    def test_reject_special_chars(self):
        """Test special characters rejected."""
        with pytest.raises(DomainValidationError):
            normalize_domain('example!.com')

    def test_reject_leading_hyphen(self):
        """Test leading hyphen rejected."""
        with pytest.raises(DomainValidationError):
            normalize_domain('-example.com')

    def test_reject_trailing_hyphen(self):
        """Test trailing hyphen in label rejected."""
        with pytest.raises(DomainValidationError):
            normalize_domain('example-.com')

    def test_reject_single_label(self):
        """Test single label (no dot) rejected."""
        with pytest.raises(DomainValidationError) as exc_info:
            normalize_domain('localhost')
        assert 'dot' in str(exc_info.value).lower()

    # Endpoint tests
    def test_endpoint_rejects_invalid_domain(self):
        """Test API endpoint rejects invalid domain."""
        response = client.post(
            '/api/check-domain',
            json={'domain': 'https://example.com'}
        )
        assert response.status_code == 400
        assert response.json()['error'] == 'invalid_domain'

    def test_endpoint_accepts_valid_domain(self, mock_dns_query_success):
        """Test API endpoint accepts valid domain."""
        response = client.post(
            '/api/check-domain',
            json={'domain': 'example.com'}
        )
        # Should not be 400 (invalid domain error)
        assert response.status_code in [200, 429]  # 200 OK or 429 rate limited
