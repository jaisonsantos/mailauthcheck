from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import dns.exception

from api.services import dns_resolver


class DNSResolverTests(unittest.TestCase):
    @patch("api.services.dns_resolver.dns.resolver.Resolver")
    def test_resolve_mx_uses_fallback_after_timeout(self, mock_resolver_class: Mock) -> None:
        system_resolver = Mock()
        fallback_resolver = Mock()

        system_resolver.resolve.side_effect = dns.exception.Timeout()
        fallback_resolver.resolve.return_value = [
            SimpleNamespace(preference=10, exchange="aspmx.l.google.com.")
        ]
        mock_resolver_class.side_effect = [system_resolver, fallback_resolver]

        result = dns_resolver.resolve_mx("google.com")

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.values, ["10 aspmx.l.google.com"])
        self.assertIsNone(result.error_category)
        self.assertEqual(mock_resolver_class.call_count, 2)

    @patch("api.services.dns_resolver.dns.resolver.Resolver")
    def test_resolve_mx_returns_timeout_when_both_resolvers_timeout(
        self, mock_resolver_class: Mock
    ) -> None:
        system_resolver = Mock()
        fallback_resolver = Mock()

        system_resolver.resolve.side_effect = dns.exception.Timeout()
        fallback_resolver.resolve.side_effect = dns.exception.Timeout()
        mock_resolver_class.side_effect = [system_resolver, fallback_resolver]

        result = dns_resolver.resolve_mx("example.com")

        self.assertEqual(result.status, "timeout")
        self.assertEqual(result.error_category, "timeout")
        self.assertEqual(result.values, [])

    @patch("api.services.dns_resolver.dns.resolver.Resolver")
    def test_resolve_txt_timeout_behavior_unchanged(self, mock_resolver_class: Mock) -> None:
        resolver = Mock()
        resolver.resolve.side_effect = dns.exception.Timeout()
        mock_resolver_class.return_value = resolver

        result = dns_resolver.resolve_txt("example.com")

        self.assertEqual(result.status, "timeout")
        self.assertEqual(result.error_category, "timeout")
        self.assertEqual(result.values, [])
        self.assertEqual(mock_resolver_class.call_count, 1)


if __name__ == "__main__":
    unittest.main()
