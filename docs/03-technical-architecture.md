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
- **Analytics:** Plausible or Google Analytics
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
- optional external lead form;
- Search Console data.

## Suggested deployment

| Layer | Suggested options |
|---|---|
| Frontend | Vercel or Cloudflare Pages |
| Backend | Render, Fly.io, Railway, or small VPS |
| Analytics | Plausible or Google Analytics |
| SEO | Google Search Console |
| Forms | Tally, Formspree, Google Forms, or similar |

## Cache

Use simple in-memory TTL cache for repeated domain scans.

Suggested TTL:

- 10 to 60 minutes for full domain scan results;
- shorter TTL during development;
- no long-term persistence.

Cache key examples:

- normalized domain;
- endpoint type;
- optional selector for future DKIM checks.

## Rate limiting

Use basic rate limiting to avoid abuse.

Possible limits:

- requests per IP per minute;
- requests per IP per hour;
- repeated scans for same domain served from cache.

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

Avoid logging:

- full IP addresses where unnecessary;
- email addresses without explicit consent;
- full domain history indefinitely;
- sensitive user-provided content.

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
→ frontend validates basic domain format
→ frontend calls POST /api/check-domain
→ backend normalizes domain
→ backend runs DNS checks:
   - TXT at root domain for SPF
   - TXT at _dmarc.domain for DMARC
   - MX at root domain
   - SPF DNS lookup count
→ backend builds standard check results
→ backend calculates score
→ backend generates next steps
→ backend returns JSON
→ frontend renders score, cards, details, next steps, CTA
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

User-facing validation message:

> Enter a valid domain, like example.com. Do not include https:// or email addresses.

## Pending decisions

- **Pending decision:** Which hosting provider should be used for the backend MVP?
- **Why it matters:** Backend DNS latency and cold starts can affect UX.
- **Recommended owner:** technical.
