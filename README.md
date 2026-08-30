# MailAuthCheck

MailAuthCheck is a fast, public-domain readiness checker for teams preparing to send bulk email to Gmail and Yahoo.

Enter a domain and get a practical report covering SPF, DKIM signals, DMARC, MX records, SPF DNS lookup count, and the bulk-sender requirements that still need manual verification.

## Why this project

Bulk-email requirements are spread across DNS records, provider-specific guidance, and operational checks. MailAuthCheck turns those signals into one simple readiness result without requiring an account, dashboard, or paid plan.

## Engineering highlights

- **Next.js frontend** designed for fast, indexable utility pages.
- **FastAPI backend** for DNS and email-authentication checks.
- SPF, DKIM selector-aware signals, DMARC, MX, and SPF lookup-count analysis.
- Bulk-sender readiness scoring with explicit manual checks instead of pretending every requirement is machine-verifiable.
- In-memory TTL caching and basic rate limiting.
- Structured JSON logging.
- Configurable CORS for local and production environments.
- Plausible analytics integration and external lead-capture support.
- No database or authentication required for the MVP, keeping the runtime deliberately small.

## Architecture

```text
Browser
  │
  ▼
Next.js UI / SEO pages
  │
  ▼
FastAPI
  ├── SPF analysis
  ├── DKIM selector checks
  ├── DMARC analysis
  ├── MX lookup
  ├── SPF DNS lookup counter
  ├── readiness scoring
  ├── TTL cache
  └── rate limiting + JSON logs
  │
  ▼
Public DNS
```

The product intentionally distinguishes between checks that can be derived from public DNS and requirements such as one-click unsubscribe, spam-rate monitoring, and From alignment that may require manual verification.

## Main capabilities

- Domain readiness check.
- Optional ESP selection.
- SPF validation.
- DKIM selector-aware signals.
- DMARC validation.
- MX validation.
- SPF DNS lookup count.
- Gmail/Yahoo bulk-sender checklist.
- Ready / Needs attention / Not ready result.
- Plain-English explanations plus technical details.
- Dedicated SEO utility pages for individual checks.

## Tech stack

- **Frontend:** Next.js
- **Backend:** FastAPI / Python
- **Runtime:** Node.js 18.18+ and Python
- **Observability:** structured JSON logs, Plausible integration
- **State:** in-memory TTL cache; no database in the MVP

## Run locally

### Backend

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```bash
nvm install 20
nvm use 20
npm install
NEXT_PUBLIC_MAILAUTHCHECK_API_URL=http://127.0.0.1:8000 npm run dev
```

Open `http://localhost:3000`.

## Configuration

Frontend example:

```env
NEXT_PUBLIC_SITE_URL=https://mailauthcheck.com
NEXT_PUBLIC_MAILAUTHCHECK_API_URL=https://api.mailauthcheck.com
NEXT_PUBLIC_SHOW_LOCALE_SELECTOR=false
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=mailauthcheck.com
NEXT_PUBLIC_LEAD_CAPTURE_URL=https://example.com/your-form
NEXT_PUBLIC_CONTACT_EMAIL=hello@example.com
```

Backend example:

```env
ALLOWED_ORIGINS=https://mailauthcheck.com,https://www.mailauthcheck.com
```

Keep production CORS explicit; do not use `*`.

## Production smoke test

```bash
curl https://api.mailauthcheck.com/healthz
curl -s -X POST https://api.mailauthcheck.com/api/check-domain \
  -H "content-type: application/json" \
  -d '{"domain":"example.com","mode":"bulk_sender","espProvider":"mailchimp"}'
```

## Design choices

This repository deliberately avoids SaaS complexity in the first version. There is no login, billing, dashboard, recurring monitoring, database, or paid API. The goal is to prove the usefulness of the core DNS-analysis workflow before introducing heavier product infrastructure.

## Documentation

More detailed product and engineering decisions live under `docs/`, including:

- `docs/03-technical-architecture.md`
- `docs/04-api-contract.md`
- `docs/05-result-schema.md`
- `docs/06-scoring-model.md`
- `docs/07-seo-plan.md`
- `docs/09-validation-plan.md`
- `docs/12-decision-log.md`

`AGENTS.md` contains repository-level instructions for automated development agents and contributors.

## Disclaimer

MailAuthCheck evaluates public DNS records and known bulk-sender readiness signals. It does not guarantee inbox placement, sender reputation, campaign performance, or acceptance by an email provider.
