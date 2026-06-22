#!/usr/bin/env bash
set -euo pipefail

FRONTEND_URL="${NEXT_PUBLIC_SITE_URL:-https://mailauthcheck.com}"
BACKEND_URL="${NEXT_PUBLIC_MAILAUTHCHECK_API_URL:-https://api.mailauthcheck.com}"

echo "Running MailAuthCheck smoke tests"
echo "Frontend: ${FRONTEND_URL}"
echo "Backend: ${BACKEND_URL}"

echo "Checking backend health..."
curl -fsS "${BACKEND_URL}/healthz" | grep -q '"status":"ok"'

echo "Checking backend domain scan..."
curl -fsS -X POST "${BACKEND_URL}/api/check-domain" \
  -H "content-type: application/json" \
  -d '{"domain":"example.com","mode":"bulk_sender"}' | grep -q '"domain":"example.com"'

echo "Checking frontend homepage..."
curl -fsS "${FRONTEND_URL}" | grep -q "MailAuthCheck"

echo "Smoke tests passed"
