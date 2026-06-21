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

## Free-tier launch path

The preferred launch path should stay cheap and operationally simple. This is a launch hypothesis, not a permanent infrastructure decision.

### Recommended first setup

| Layer | Free or low-cost option | Why it fits the MVP |
|---|---|---|
| Frontend | Vercel free tier | Simple Next.js deploy, preview URLs, custom domain support and no server management. |
| Backend | Oracle Cloud Always Free VM, Render free/low-cost service, Fly.io allowance or Railway trial/low-cost plan | FastAPI can run as a small single process. DNS checks do not need a database, queue or cluster. |
| Domain/DNS | Existing domain DNS provider | No special DNS infrastructure is required for the product itself. |
| Analytics | Plausible trial/self-host later, or a privacy-friendly alternative if cost becomes an issue | The app only needs page views and a few custom events at launch. |
| Lead capture | Tally free tier, Google Forms, Formspree free tier or similar | Keeps lead capture external and avoids a database. |
| Monitoring | Provider health checks and manual smoke tests | Enough for the first validation window. Avoid recurring monitoring features inside the product. |

### Easiest operational option

Use Vercel for the frontend and a simple managed backend provider for the first deploy.

This is easiest because:

- Vercel handles the Next.js build and HTTPS.
- The backend receives one public HTTPS URL.
- `NEXT_PUBLIC_MAILAUTHCHECK_API_URL` points to that backend URL.
- `ALLOWED_ORIGINS` only needs the Vercel production domain and any preview domains used for testing.

Tradeoff:

- Some free backend providers sleep or cold-start. That can make the first scan slower.

### Cheapest persistent option

Use Vercel for the frontend and Oracle Cloud Always Free for the backend.

This can be very cheap because:

- the backend VM can stay running without free-tier sleep;
- FastAPI + Uvicorn is lightweight enough for a small VM;
- no database, queue or Redis is required.

Tradeoffs:

- you must manage the VM, firewall, process restart and HTTPS/proxy setup;
- setup is slower than a managed platform;
- DNS/firewall mistakes can make the API unreachable.

### Minimal Oracle VM shape

For MVP validation, a small VM is enough:

- one FastAPI process;
- Uvicorn behind a simple reverse proxy such as Caddy or Nginx;
- HTTPS enabled by the proxy;
- systemd service for restart on reboot;
- no database;
- no Docker requirement unless it makes your own operations easier.

Suggested backend environment:

~~~env
ALLOWED_ORIGINS=https://mailauthcheck.com,https://www.mailauthcheck.com,https://mailauthcheck.vercel.app
~~~

Suggested frontend environment:

~~~env
NEXT_PUBLIC_SITE_URL=https://mailauthcheck.com
NEXT_PUBLIC_MAILAUTHCHECK_API_URL=https://api.mailauthcheck.com
NEXT_PUBLIC_SHOW_LOCALE_SELECTOR=false
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=mailauthcheck.com
NEXT_PUBLIC_LEAD_CAPTURE_URL=https://tally.so/r/your-form-id
NEXT_PUBLIC_CONTACT_EMAIL=hello@mailauthcheck.com
~~~

### Free-tier risks to watch

- Backend sleep or cold start can make the first scan feel broken.
- Provider request limits may affect public launch posts if traffic spikes.
- Free analytics or form tools may limit event history or submissions.
- Oracle VM operations are cheap but require manual maintenance.
- Using `http://` instead of `https://` in production can cause browser and CORS issues.
- CORS must include the exact frontend origin; do not use `*` in production.

### Recommendation for the first 30 days

Start with the simplest path that you can actually operate:

1. Deploy frontend to Vercel.
2. Deploy backend to either a simple managed service or Oracle Always Free.
3. Configure an external form.
4. Configure Search Console.
5. Run manual smoke tests after every deploy.

Do not add database, login, queue, billing or internal lead storage to solve launch operations.

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
