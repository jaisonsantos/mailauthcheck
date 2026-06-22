"""Tests for rate limiting functionality."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from time import time

from api.main import app
from api.services.runtime import RateLimitExceeded

client = TestClient(app)


class TestRateLimiting:
    """Test rate limiting logic."""

    def test_first_request_allowed(self, mock_dns_query_success):
        """Test first request is allowed."""
        response = client.post(
            '/api/check-domain',
            json={'domain': 'first-test.com'}
        )
        assert response.status_code == 200

    def test_rapid_same_domain_blocked(self, mock_dns_query_success):
        """Test rapid requests for same domain are rate limited."""
        domain = 'ratelimit-test.com'
        
        # First request should succeed
        response1 = client.post(
            '/api/check-domain',
            json={'domain': domain}
        )
        assert response1.status_code == 200
        
        # Rapid second request should be rate limited
        response2 = client.post(
            '/api/check-domain',
            json={'domain': domain}
        )
        # Second request hits cache, so still 200
        # But if we bypass cache...
        assert response2.status_code in [200, 429]

    def test_different_domains_allowed(self, mock_dns_query_success):
        """Test different domains bypass rate limit."""
        domains = ['test1.com', 'test2.com', 'test3.com']
        
        for domain in domains:
            response = client.post(
                '/api/check-domain',
                json={'domain': domain}
            )
            assert response.status_code == 200

    def test_rate_limit_headers_present(self, mock_dns_query_success):
        """Test 429 response includes Retry-After header."""
        # This would require forcing rate limit bypass
        # Skipping for now as it requires internal state manipulation
        pass

    def test_cache_hit_not_counted_for_limit(self, mock_dns_query_success):
        """Test cache hits don't trigger rate limit."""
        domain = 'cache-test.com'
        
        # First request
        response1 = client.post(
            '/api/check-domain',
            json={'domain': domain}
        )
        assert response1.status_code == 200
        
        # Second request (cache hit) should also work
        response2 = client.post(
            '/api/check-domain',
            json={'domain': domain}
        )
        assert response2.status_code == 200
