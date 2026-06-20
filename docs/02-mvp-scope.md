# 02 — MVP Scope

## MVP goal

Launch the smallest useful bulk sender readiness checker that can validate real demand.

The MVP should answer:

> Is this domain ready for bulk email sending to Gmail and Yahoo?

## What enters the MVP

The MVP includes:

- domain input;
- optional ESP selector;
- SPF check;
- DKIM selector-aware check for selected/common ESP selectors;
- DMARC check;
- MX check;
- SPF DNS lookup count;
- Gmail/Yahoo bulk sender readiness status;
- automated/manual check separation;
- manual one-click unsubscribe verification instructions;
- manual spam-rate monitoring guidance through Google Postmaster Tools or provider dashboards;
- provider-specific next steps where the ESP is known;
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
- ESP API integrations;
- email list verification;
- email content scanning;
- sending real test emails.

## P0 checks

| Check | MVP status | Priority | Notes |
|---|---|---:|---|
| MX | Included | P0 | Confirms whether the domain has mail exchange records. |
| SPF record | Included | P0 | Detects TXT records starting with `v=spf1`. |
| Multiple SPF records | Included | P0 | More than one SPF record is a common failure. |
| SPF DNS lookup count | Included | P0 | Warns when close to or above the 10-lookup limit. |
| DKIM selector signal | Included | P0/P1 | Checks selected/common ESP selectors with explicit false-positive warnings. |
| DMARC record | Included | P0 | Checks `_dmarc.domain`. |
| DMARC policy | Included | P0 | Detects `p=none`, `p=quarantine`, or `p=reject`; `p=none` is minimum/monitoring mode, not absolute Gmail non-compliance. |
| Gmail/Yahoo readiness | Included | P0 | Bulk sender readiness only, not a deliverability or inbox-placement guarantee. |
| One-click unsubscribe | Manual check | P0 | Required for many marketing/subscribed bulk messages, but not verifiable from DNS. |
| Spam rate | Manual check | P0 | Must be reviewed in Postmaster Tools or provider dashboards; never estimated from DNS. |

## DKIM decision

DKIM becomes part of the bulk sender MVP, but it must be selector-aware and confidence-aware.

Reason:

- DKIM usually requires a selector.
- Guessing selectors can generate false negatives.
- Gmail/Yahoo bulk sender requirements make DKIM important enough to expose early.
- Not finding a common selector is a warning, not proof that DKIM is absent.

Planned timing:

- Bulk MVP: use selected/common ESP selectors with `canBeFalsePositive=true` when selectors are guessed.
- V1: add a dedicated `/dkim-selector-checker` with explicit `domain + selector` input.

## Smallest useful launch

The smallest useful launch is one page with:

- domain input;
- SPF card;
- DKIM signal card;
- DMARC card;
- MX card;
- SPF lookup count card;
- Gmail/Yahoo bulk readiness;
- manual checks panel;
- score;
- top 1–3 next steps;
- CTA: “Need help fixing this?”

## MVP checklist

- [ ] Domain input accepts only domains, not URLs or email addresses.
- [ ] SPF check returns ok, warning, missing, or error.
- [ ] DKIM selector signal returns ok, warning, missing, unknown, or error.
- [ ] DMARC check returns ok, warning, missing, or error.
- [ ] MX check returns ok, missing, or error.
- [ ] SPF lookup count returns ok, warning, or error.
- [ ] Gmail/Yahoo readiness returns ready, needs work, not ready, or incomplete.
- [ ] Manual checks are never marked passed unless verified.
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
