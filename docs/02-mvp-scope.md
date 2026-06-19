# 02 — MVP Scope

## MVP goal

Launch the smallest useful version of MailAuthCheck that can validate real demand.

The MVP should answer:

> Is this domain minimally ready to send email?

## What enters the MVP

The MVP includes:

- domain-only input;
- SPF check;
- DMARC check;
- MX check;
- SPF DNS lookup count;
- basic Gmail/Yahoo readiness status;
- simple score;
- result cards;
- simple explanations;
- optional technical details;
- next steps;
- lightweight lead capture;
- CTA for assisted setup;
- first 5 SEO pages.

## What does not enter the MVP

The MVP excludes:

- login;
- dashboard;
- Stripe;
- billing;
- paid plans;
- multi-tenant features;
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

## P0 checks

| Check | MVP status | Priority | Notes |
|---|---|---:|---|
| MX | Included | P0 | Confirms whether the domain has mail exchange records. |
| SPF record | Included | P0 | Detects TXT records starting with `v=spf1`. |
| Multiple SPF records | Included | P0 | More than one SPF record is a common failure. |
| SPF DNS lookup count | Included | P0 | Warns when close to or above the 10-lookup limit. |
| DMARC record | Included | P0 | Checks `_dmarc.domain`. |
| DMARC policy | Included | P0 | Detects `p=none`, `p=quarantine`, or `p=reject`. |
| Gmail/Yahoo readiness | Included | P0 | Basic readiness only, not deliverability guarantee. |

## DKIM decision

DKIM should not be a required MVP check.

Reason:

- DKIM usually requires a selector.
- Guessing selectors can generate false negatives.
- A selector-based DKIM checker is valuable, but should be added after the first launch.

Planned timing:

- MVP: mention DKIM as not checked unless selector is provided.
- Week 2 / V1: add `/dkim-selector-checker` with `domain + selector` input.

## Smallest useful launch

The smallest useful launch is one page with:

- domain input;
- SPF card;
- DMARC card;
- MX card;
- SPF lookup count card;
- basic Gmail/Yahoo readiness;
- score;
- top 1–3 next steps;
- CTA: “Need help fixing this?”

## MVP checklist

- [ ] Domain input accepts only domains, not URLs or email addresses.
- [ ] SPF check returns ok, warning, missing, or error.
- [ ] DMARC check returns ok, warning, missing, or error.
- [ ] MX check returns ok, missing, or error.
- [ ] SPF lookup count returns ok, warning, or error.
- [ ] Gmail/Yahoo readiness returns ready, partial, or not ready.
- [ ] Score returns 0–100 and label.
- [ ] Result includes plain-English summary.
- [ ] Result includes optional technical details.
- [ ] Result includes next steps.
- [ ] CTA for setup assistance exists.
- [ ] No login exists.
- [ ] No database exists.
- [ ] No billing exists.

## Scope creep guardrails

A feature must be rejected or deferred if it:

- requires user accounts;
- requires persistent scan history;
- requires payment infrastructure;
- requires multi-tenant modeling;
- requires a background job system;
- requires complex provider integrations;
- does not directly improve the first scan experience;
- does not support the first 5 SEO pages;
- creates support burden before validation.

## Pending decisions

- **Pending decision:** Should the MVP include a manual email form or a third-party form tool for lead capture?
- **Why it matters:** A third-party form avoids backend persistence and keeps the MVP simpler.
- **Recommended owner:** product/technical.
