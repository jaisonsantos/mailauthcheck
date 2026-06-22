"""Tests for DNS checking services."""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from dns.exception import Timeout, NXDOMAIN

from api.services.checks import check_spf, check_dmarc, check_mx, check_dkim


class TestSPFCheck:
    """Test SPF record checking."""

    @patch('api.services.checks.dns_query_with_retry')
    def test_spf_single_record_found(self, mock_query):
        """Test SPF found with single record."""
        mock_query.return_value = ['v=spf1 include:_spf.google.com ~all']
        result = check_spf('example.com')
        assert result.status == 'ok'
        assert result.checkName == 'SPF'
        assert result.confidence == 'high'
        assert not result.canBeFalsePositive

    @patch('api.services.checks.dns_query_with_retry')
    def test_spf_multiple_records_error(self, mock_query):
        """Test SPF with multiple records is error."""
        mock_query.return_value = [
            'v=spf1 include:_spf.google.com ~all',
            'v=spf1 include:sendgrid.net ~all'
        ]
        result = check_spf('example.com')
        assert result.status == 'error'
        assert 'multiple' in result.summary.lower()

    @patch('api.services.checks.dns_query_with_retry')
    def test_spf_missing(self, mock_query):
        """Test SPF missing."""
        mock_query.return_value = []
        result = check_spf('example.com')
        assert result.status == 'missing'

    @patch('api.services.checks.dns_query_with_retry')
    def test_spf_timeout_handling(self, mock_query):
        """Test SPF timeout handled gracefully."""
        mock_query.side_effect = Timeout("DNS timeout")
        result = check_spf('example.com')
        assert result.status == 'error'
        assert result.severity == 'high'


class TestDMARCCheck:
    """Test DMARC record checking."""

    @patch('api.services.checks.dns_query_with_retry')
    def test_dmarc_reject_policy(self, mock_query):
        """Test DMARC with p=reject policy."""
        mock_query.return_value = ['v=DMARC1; p=reject; rua=mailto:dmarc@example.com']
        result = check_dmarc('example.com')
        assert result.status == 'ok'
        assert 'p=reject' in result.technicalDetails or 'reject' in result.summary

    @patch('api.services.checks.dns_query_with_retry')
    def test_dmarc_quarantine_policy(self, mock_query):
        """Test DMARC with p=quarantine policy."""
        mock_query.return_value = ['v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com']
        result = check_dmarc('example.com')
        assert result.status == 'ok'
        assert result.severity == 'info'

    @patch('api.services.checks.dns_query_with_retry')
    def test_dmarc_none_policy(self, mock_query):
        """Test DMARC with p=none policy (monitoring mode)."""
        mock_query.return_value = ['v=DMARC1; p=none; rua=mailto:dmarc@example.com']
        result = check_dmarc('example.com')
        assert result.status == 'warning'
        assert 'monitoring' in result.summary.lower() or 'none' in result.summary.lower()

    @patch('api.services.checks.dns_query_with_retry')
    def test_dmarc_missing(self, mock_query):
        """Test DMARC missing."""
        mock_query.return_value = []
        result = check_dmarc('example.com')
        assert result.status == 'missing'


class TestMXCheck:
    """Test MX record checking."""

    @patch('api.services.checks.dns_query_with_retry')
    def test_mx_records_found(self, mock_query):
        """Test MX records found."""
        mock_query.return_value = [
            '10 aspmx.l.google.com',
            '20 alt1.aspmx.l.google.com'
        ]
        result = check_mx('example.com')
        assert result.status == 'ok'
        assert len(result.rawRecords) == 2

    @patch('api.services.checks.dns_query_with_retry')
    def test_mx_missing(self, mock_query):
        """Test MX records missing."""
        mock_query.return_value = []
        result = check_mx('example.com')
        assert result.status == 'missing'

    @patch('api.services.checks.dns_query_with_retry')
    def test_mx_single_record(self, mock_query):
        """Test single MX record is ok."""
        mock_query.return_value = ['10 mail.example.com']
        result = check_mx('example.com')
        assert result.status == 'ok'


class TestDKIMCheck:
    """Test DKIM selector checking."""

    @patch('api.services.checks.dns_query_with_retry')
    def test_dkim_selector_found_google(self, mock_query):
        """Test DKIM found for Google selector."""
        # Mock successful query for selector1._domainkey.example.com
        mock_query.return_value = ['v=DKIM1; k=rsa; p=MIGfMA0B...']
        result = check_dkim('example.com', 'google')
        assert result.status == 'ok'
        assert result.confidence == 'high'
        assert not result.canBeFalsePositive

    @patch('api.services.checks.dns_query_with_retry')
    def test_dkim_selector_not_found_with_esp(self, mock_query):
        """Test DKIM not found but ESP selected = warning with low confidence."""
        mock_query.return_value = []
        result = check_dkim('example.com', 'mailchimp')
        assert result.status == 'warning'
        assert result.confidence == 'low'
        assert result.canBeFalsePositive
        assert 'false negative' in result.summary.lower() or 'selector' in result.summary.lower()

    @patch('api.services.checks.dns_query_with_retry')
    def test_dkim_no_esp_unknown(self, mock_query):
        """Test DKIM unknown when no ESP selected."""
        mock_query.return_value = []
        result = check_dkim('example.com', None)
        assert result.status == 'unknown'
        assert result.confidence == 'low'
        assert result.canBeFalsePositive
