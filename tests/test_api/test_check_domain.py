"""End-to-end integration tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from dns.exception import Timeout

from api.main import app

client = TestClient(app)


class TestCheckDomainE2E:
    """End-to-end tests for check-domain endpoint."""

    @patch('api.services.checks.check_spf')
    @patch('api.services.checks.check_dkim')
    @patch('api.services.checks.check_dmarc')
    @patch('api.services.checks.check_mx')
    @patch('api.services.checks.check_spf_lookup_count')
    def test_e2e_ready_domain(self, mock_lookup, mock_mx, mock_dmarc, mock_dkim, mock_spf):
        """Test E2E with domain ready for bulk sending."""
        from api.models import CheckResult

        mock_spf.return_value = CheckResult(
            checkName='SPF', status='ok', severity='info',
            summary='SPF record found', confidence='high', canBeFalsePositive=False
        )
        mock_dkim.return_value = CheckResult(
            checkName='DKIM', status='ok', severity='info',
            summary='DKIM found', confidence='high', canBeFalsePositive=False
        )
        mock_dmarc.return_value = CheckResult(
            checkName='DMARC', status='ok', severity='info',
            summary='DMARC p=reject', confidence='high', canBeFalsePositive=False
        )
        mock_mx.return_value = CheckResult(
            checkName='MX', status='ok', severity='info',
            summary='MX records found', confidence='high', canBeFalsePositive=False
        )
        mock_lookup.return_value = CheckResult(
            checkName='SPF Lookup Count', status='ok', severity='info',
            summary='5 lookups', confidence='high', canBeFalsePositive=False
        )

        response = client.post(
            '/api/check-domain',
            json={'domain': 'ready-example.com', 'mode': 'bulk_sender'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['score'] >= 80
        assert data['status'] == 'ready'
        assert 'checks' in data
        assert len(data['checks']) > 0

    @patch('api.services.checks.check_spf')
    @patch('api.services.checks.check_dkim')
    @patch('api.services.checks.check_dmarc')
    @patch('api.services.checks.check_mx')
    @patch('api.services.checks.check_spf_lookup_count')
    def test_e2e_needs_work_domain(self, mock_lookup, mock_mx, mock_dmarc, mock_dkim, mock_spf):
        """Test E2E with domain that needs attention."""
        from api.models import CheckResult

        mock_spf.return_value = CheckResult(
            checkName='SPF', status='ok', severity='info',
            summary='SPF record found', confidence='high', canBeFalsePositive=False
        )
        mock_dkim.return_value = CheckResult(
            checkName='DKIM', status='warning', severity='medium',
            summary='DKIM selector not found', confidence='low', canBeFalsePositive=True
        )
        mock_dmarc.return_value = CheckResult(
            checkName='DMARC', status='warning', severity='medium',
            summary='DMARC p=none', confidence='high', canBeFalsePositive=False
        )
        mock_mx.return_value = CheckResult(
            checkName='MX', status='ok', severity='info',
            summary='MX records found', confidence='high', canBeFalsePositive=False
        )
        mock_lookup.return_value = CheckResult(
            checkName='SPF Lookup Count', status='ok', severity='info',
            summary='5 lookups', confidence='high', canBeFalsePositive=False
        )

        response = client.post(
            '/api/check-domain',
            json={'domain': 'needswork-example.com'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 50 <= data['score'] < 80
        assert data['status'] == 'needs_work'

    def test_e2e_invalid_domain_rejected(self):
        """Test E2E rejects invalid domain format."""
        response = client.post(
            '/api/check-domain',
            json={'domain': 'https://example.com'}
        )
        assert response.status_code == 400
        assert response.json()['error'] == 'invalid_domain'

    def test_e2e_healthz_endpoint(self):
        """Test healthz endpoint is working."""
        response = client.get('/healthz')
        assert response.status_code == 200
        assert response.json()['status'] == 'ok'
