"""Tests for scoring model."""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from api.models import CheckResult, AggregateResult
from api.services.checks import build_aggregate_result


class TestScoringModel:
    """Test scoring logic against docs/06-scoring-model.md."""

    @patch('api.services.checks.check_spf')
    @patch('api.services.checks.check_dkim')
    @patch('api.services.checks.check_dmarc')
    @patch('api.services.checks.check_mx')
    @patch('api.services.checks.check_spf_lookup_count')
    def test_perfect_domain_score_100(self, mock_lookup, mock_mx, mock_dmarc, mock_dkim, mock_spf):
        """Test perfect domain gets score 100."""
        # All checks pass
        mock_spf.return_value = CheckResult(
            checkName='SPF', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_dkim.return_value = CheckResult(
            checkName='DKIM', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_dmarc.return_value = CheckResult(
            checkName='DMARC', status='ok', severity='info',
            summary='v=DMARC1; p=reject', confidence='high', canBeFalsePositive=False
        )
        mock_mx.return_value = CheckResult(
            checkName='MX', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_lookup.return_value = CheckResult(
            checkName='SPF Lookup Count', status='ok', severity='info',
            summary='OK (5 lookups)', confidence='high', canBeFalsePositive=False
        )

        result = build_aggregate_result('example.com', None)
        assert result.score == 100
        assert result.status == 'ready'

    @patch('api.services.checks.check_spf')
    @patch('api.services.checks.check_dkim')
    @patch('api.services.checks.check_dmarc')
    @patch('api.services.checks.check_mx')
    @patch('api.services.checks.check_spf_lookup_count')
    def test_missing_dmarc_score_penalized(self, mock_lookup, mock_mx, mock_dmarc, mock_dkim, mock_spf):
        """Test missing DMARC is penalized and status not ready."""
        # SPF, DKIM, MX ok, but DMARC missing
        mock_spf.return_value = CheckResult(
            checkName='SPF', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_dkim.return_value = CheckResult(
            checkName='DKIM', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_dmarc.return_value = CheckResult(
            checkName='DMARC', status='missing', severity='high',
            summary='Missing', confidence='high', canBeFalsePositive=False
        )
        mock_mx.return_value = CheckResult(
            checkName='MX', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_lookup.return_value = CheckResult(
            checkName='SPF Lookup Count', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )

        result = build_aggregate_result('example.com', None)
        assert result.score < 80
        assert result.status != 'ready'  # Blocker: DMARC missing

    @patch('api.services.checks.check_spf')
    @patch('api.services.checks.check_dkim')
    @patch('api.services.checks.check_dmarc')
    @patch('api.services.checks.check_mx')
    @patch('api.services.checks.check_spf_lookup_count')
    def test_multiple_spf_blocks_ready(self, mock_lookup, mock_mx, mock_dmarc, mock_dkim, mock_spf):
        """Test multiple SPF records block 'Ready' status."""
        # SPF has error (multiple records)
        mock_spf.return_value = CheckResult(
            checkName='SPF', status='error', severity='high',
            summary='Multiple SPF records', confidence='high', canBeFalsePositive=False
        )
        mock_dkim.return_value = CheckResult(
            checkName='DKIM', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_dmarc.return_value = CheckResult(
            checkName='DMARC', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_mx.return_value = CheckResult(
            checkName='MX', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_lookup.return_value = CheckResult(
            checkName='SPF Lookup Count', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )

        result = build_aggregate_result('example.com', None)
        assert result.status != 'ready'  # Blocker: Multiple SPF

    @patch('api.services.checks.check_spf')
    @patch('api.services.checks.check_dkim')
    @patch('api.services.checks.check_dmarc')
    @patch('api.services.checks.check_mx')
    @patch('api.services.checks.check_spf_lookup_count')
    def test_spf_lookup_warning_at_8_10(self, mock_lookup, mock_mx, mock_dmarc, mock_dkim, mock_spf):
        """Test SPF lookup count 8-10 is warning."""
        mock_spf.return_value = CheckResult(
            checkName='SPF', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_dkim.return_value = CheckResult(
            checkName='DKIM', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_dmarc.return_value = CheckResult(
            checkName='DMARC', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_mx.return_value = CheckResult(
            checkName='MX', status='ok', severity='info',
            summary='OK', confidence='high', canBeFalsePositive=False
        )
        mock_lookup.return_value = CheckResult(
            checkName='SPF Lookup Count', status='warning', severity='medium',
            summary='8 lookups (limit is 10)', confidence='high', canBeFalsePositive=False
        )

        result = build_aggregate_result('example.com', None)
        # Should be lower than 100 due to warning
        assert result.score < 100
        assert result.score >= 50  # Still needs_work, not not_ready
