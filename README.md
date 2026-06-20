# MailAuthCheck

MailAuthCheck is a free, fast, SEO-friendly utility site that checks whether a domain is ready for bulk email sending to Gmail and Yahoo.

The user enters a domain, such as `example.com`, optionally selects an email service provider, and receives a practical report covering SPF, DKIM selector signals, DMARC, MX records, SPF DNS lookup count, and manual bulk-sender requirements that cannot be verified from DNS alone.

## Product vision

MailAuthCheck should work like a practical utility site, not like a SaaS product at launch.

The goal is to give users an immediate answer to one question:

> Is my domain ready for bulk email sending to Gmail and Yahoo?

The MVP must be useful without login, dashboard, billing, or complex onboarding.

## MVP strategy

The first version should be:

- free;
- fast;
- simple;
- indexable by Google;
- clear for non-technical users;
- useful for developers and agencies;
- prepared for SEO pages and future lead capture;
- focused on public DNS checks and explicit manual checklist items.

## Target MVP scope

- Domain input at the top of the page.
- Optional ESP selector.
- SPF check.
- DKIM selector-aware check for selected/common ESP selectors.
- DMARC check.
- MX check.
- SPF DNS lookup count.
- Gmail/Yahoo bulk sender readiness checklist.
- Manual checks for one-click unsubscribe and spam-rate monitoring.
- Simple score: Ready / Needs attention / Not ready.
- Plain-English explanation.
- Optional technical details.
- Clear next steps.
- Lightweight lead capture.
- CTA for assisted setup.
- Initial SEO pages:
  - `/`
  - `/bulk-email-readiness-checker`
  - `/gmail-bulk-sender-requirements`
  - `/spf-checker`
  - `/dmarc-checker`
  - `/mx-record-checker`
  - `/spf-lookup-counter`

## Current implementation status

The current implementation includes the Next.js frontend, FastAPI backend, SPF, DKIM selector-aware signals, DMARC, MX, SPF lookup count, bulk readiness checklist fields, manual check fields, cache, rate limiting, JSON logs, Plausible integration and external lead capture URL support.

Manual checks such as one-click unsubscribe, spam rate and From alignment are shown as manual checks only. They are not marked as passed automatically.

## What the MVP does not include

The MVP must not include:

- login;
- dashboard;
- Stripe;
- billing;
- paid plans;
- multi-tenant architecture;
- complex scan history;
- recurring monitoring;
- paid public API;
- complex PDF reports;
- agency panel;
- database;
- AI in the technical core;
- blacklist checks;
- BIMI;
- MTA-STS;
- TLS-RPT;
- email header analyzer.
- ESP API integrations;
- email list verification;
- email content scanning;
- sending real test emails.

## Initial positioning

**Name:** MailAuthCheck

**Headline:** Bulk Email Readiness Checker

**Subheadline:** Check if your domain meets the basic Gmail and Yahoo bulk sender requirements before your next campaign. Review SPF, DKIM, DMARC, MX, SPF lookups and manual checks like one-click unsubscribe and spam-rate monitoring.

**Disclaimer:** This tool checks public DNS records and known bulk sender readiness signals. It does not guarantee inbox placement, campaign performance, sender reputation or provider acceptance.

## Preferred technical direction

The preferred initial stack is:

- Next.js for frontend and SEO pages;
- FastAPI for DNS/authentication checks;
- no database in the MVP;
- simple in-memory TTL cache;
- basic rate limiting;
- JSON logs;
- Google Search Console;
- Plausible or Google Analytics.

## Run locally

Install frontend dependencies:

~~~bash
npm install
~~~

Start the FastAPI backend:

~~~bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
~~~

Start the Next.js frontend in another terminal:

~~~bash
NEXT_PUBLIC_MAILAUTHCHECK_API_URL=http://127.0.0.1:8000 npm run dev
~~~

Then open:

~~~text
http://localhost:3000
~~~

## Documentation map

- `AGENTS.md` — permanent rules for AI agents and contributors.
- `docs/00-master-plan-summary.md` — executive summary.
- `docs/01-product-brief.md` — product brief and positioning.
- `docs/02-mvp-scope.md` — closed MVP scope.
- `docs/03-technical-architecture.md` — pragmatic architecture.
- `docs/04-api-contract.md` — initial API contract.
- `docs/05-result-schema.md` — standard result model.
- `docs/06-scoring-model.md` — score model.
- `docs/07-seo-plan.md` — initial SEO plan.
- `docs/08-pages-and-content.md` — page map and content plan.
- `docs/09-validation-plan.md` — 30-day validation plan.
- `docs/10-monetization.md` — lightweight monetization plan.
- `docs/11-roadmap.md` — post-MVP roadmap.
- `docs/12-decision-log.md` — product and architecture decision log.
- `docs/13-backlog-draft.md` — initial backlog draft.
