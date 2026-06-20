# 03 — Technical Architecture

## Architecture goal

Use the simplest architecture that can support a fast, SEO-friendly utility site with reliable DNS checks.

The MVP should avoid unnecessary infrastructure.

## Chosen stack

- **Frontend:** Next.js
- **Backend:** FastAPI
- **Persistence:** none for MVP
- **Cache:** in-memory TTL cache
- **Rate limit:** basic IP/domain-based rate limiting
- **Logs:** structured JSON logs
- **Analytics:** Plausible
- **SEO:** Google Search Console

## Why Next.js + FastAPI

### Next.js

Use Next.js because the product needs:

- SEO-friendly pages;
- fast static/SSR pages;
- a clean frontend structure;
- easy route-based tool pages;
- good developer experience.

### FastAPI

Use FastAPI because the backend needs:

- simple HTTP endpoints;
- DNS lookup orchestration;
- quick iteration;
- low runtime overhead;
- simple JSON responses;
- easy integration with Python DNS libraries.

### Why not Spring Boot for the MVP

Spring Boot is robust, but heavier for this utility-site MVP.

It may be reconsidered later if:

- the product grows into a larger backend;
- there are strong operational reasons;
- the decision is documented in `docs/12-decision-log.md`.

## Why no database in the MVP

A database is intentionally excluded from the MVP.

Reasons:

- no login;
- no dashboard;
- no scan history;
- no billing;
- no monitoring;
- no multi-tenant model;
- no need to persist scan results.

For validation, use:

- analytics events;
- JSON logs;
- external lead form;
- Search Console data.

## Suggested deployment

| Layer | Suggested options |
|---|---|
| Frontend | Vercel or Cloudflare Pages |
| Backend | Render, Fly.io, Railway, or small VPS |
| Analytics | Plausible |
| SEO | Google Search Console |
| Forms | external hosted form URL such as Tally, Formspree, Google Forms, or similar |

## Frontend analytics

Use a lightweight client-side analytics helper.

Current MVP implementation target:

- Plausible script loaded only when `NEXT_PUBLIC_PLAUSIBLE_DOMAIN` is configured;
- automatic page views handled by Plausible;
- custom events for scans, CTA clicks and lead clicks sent from the checker UI;
- no cookies or internal event storage required in the repo.

Suggested event names:

- `scan_started`
- `scan_completed`
- `scan_failed`
- `cta_help_clicked`
- `cta_send_to_dev_clicked`
- `lead_form_started`

## Cache

Use simple in-memory TTL cache for repeated domain scans.

Current MVP implementation target:

- 15-minute TTL for repeated scans;
- endpoint-specific cache keys such as `aggregate:example.com` and `/api/spf:example.com`;
- no long-term persistence.

Cache key examples:

- normalized domain;
- endpoint type;
- mode, such as `bulk_sender`;
- optional ESP provider;
- optional selector for DKIM checks.

If cache TTL is revisited during the bulk refactor, prefer one documented value. Current implementation uses 15 minutes; a future adjustment to 10 minutes is acceptable only if the decision log is updated.

## Rate limiting

Use basic rate limiting to avoid abuse.

Current MVP implementation target:

- 30 requests per IP per minute;
- 10 repeated checks per IP+domain per minute;
- repeated scans should usually be served from cache before they become expensive.

Rate limit response:

- HTTP 429;
- plain message: “Too many checks. Please try again later.”

## Logs

Use structured JSON logs.

Useful fields:

- timestamp;
- normalized domain hash;
- TLD;
- result status;
- score bucket;
- failed checks;
- latency in milliseconds;
- endpoint;
- error category;
- CTA clicked, if applicable.

Current MVP implementation target:

- log one structured event per API request completion or rejection;
- hash domains before logging;
- include cache-hit information and latency in milliseconds.

Avoid logging:

- full IP addresses where unnecessary;
- email addresses without explicit consent;
- full domain history indefinitely;
- sensitive user-provided content.

## Lead capture

Use an external hosted form URL for MVP setup requests.

Current MVP implementation target:

- configure `NEXT_PUBLIC_LEAD_CAPTURE_URL`;
- prefill domain, selected ESP, status and main issues in the outbound link when possible;
- open the form in a new tab;
- keep privacy/disclaimer copy near the CTA;
- do not store leads inside the application.

## Future folder structure reference

This is a reference only. Do not create executable files until there is an explicit implementation task.

## Current implementation note

The MVP implementation currently keeps executable code at the repository root to avoid premature monorepo structure complexity.

- Frontend currently lives in the root `app/` directory.
- Backend skeleton is expected to live in the root `api/` directory.
- A move to `apps/web` and `apps/api` can be reconsidered later if the codebase becomes large enough to justify it.

~~~text
mailauthcheck/
  app/
    page.tsx
    spf-checker/page.tsx
    dmarc-checker/page.tsx
    mx-record-checker/page.tsx
    spf-lookup-counter/page.tsx
  api/
    main.py
    routers/
      check_domain.py
      checks.py
    services/
      placeholder_results.py
    models.py
    validation.py
~~~

## Full scan flow

~~~text
User enters domain
→ user optionally selects ESP provider
→ frontend validates basic domain format
→ frontend calls POST /api/check-domain
→ backend normalizes domain
→ backend runs DNS checks:
   - TXT at root domain for SPF
   - TXT at selector._domainkey.domain for DKIM when selector/ESP is available
   - TXT at _dmarc.domain for DMARC
   - MX at root domain
   - SPF DNS lookup count
→ backend generates manual checklist items that cannot be verified from DNS
→ backend builds standard check results
→ backend calculates DNS Authentication Score
→ backend generates next steps
→ backend returns JSON
→ frontend renders score, automated checks, manual checks, details, next steps, CTA
~~~

## DNS error handling

| DNS condition | Expected handling |
|---|---|
| NXDOMAIN | Return missing/error depending on check context. |
| No answer | Return missing for expected record type. |
| Timeout | Return error with retry-friendly message. |
| SERVFAIL | Return error with technical details. |
| Too many nested SPF lookups | Stop safely and return warning/error. |
| Malformed TXT record | Return warning or error with raw record. |

## Domain validation

The domain input should:

- accept `example.com`;
- reject full URLs like `https://example.com`;
- reject email addresses like `user@example.com`;
- reject empty input;
- normalize casing;
- trim whitespace;
- support common subdomains if intentionally entered;
- avoid scanning internal/private hostnames.
- avoid URL fetching and any SSRF-prone behavior.
- do not call ESP APIs in the MVP.

User-facing validation message:

> Enter a valid domain, like example.com. Do not include https:// or email addresses.

## Pending decisions

- **Pending decision:** Which hosting provider should be used for the backend MVP?
- **Why it matters:** Backend DNS latency and cold starts can affect UX.
- **Recommended owner:** technical.
