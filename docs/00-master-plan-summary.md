# 00 — Master Plan Summary

## Executive decision

MailAuthCheck should start as a free utility site, not as a SaaS product.

The first goal is to publish a useful, indexable tool that lets users check whether a domain is minimally ready to send email correctly.

The product should validate demand through:

- organic search impressions;
- scans performed;
- unique domains checked;
- CTA clicks;
- email captures;
- assisted setup requests.

Recurring revenue should not be the initial objective.

## Chosen name

**MailAuthCheck**

Reason:

- clear enough for technical users;
- understandable for non-technical users;
- includes strong terms: Mail, Auth, Check;
- works as a single tool now and can expand into a small hub later;
- more SEO-friendly than InboxReady.

## Value proposition

MailAuthCheck gives users a simple answer to:

> Is my domain ready to send email?

It checks public DNS records and explains what is missing, broken, or risky.

## Target audience

Primary audiences:

- small business owners;
- freelancers;
- agencies;
- e-commerce operators;
- small SaaS founders;
- developers configuring email domains;
- marketing teams using providers like Google Workspace, Microsoft 365, Mailchimp, Brevo, or SendGrid.

## Real MVP

The real MVP is:

- one homepage with a domain scanner;
- four initial SEO/tool pages;
- SPF, DMARC, MX and SPF lookup count checks;
- basic Gmail/Yahoo readiness indication;
- simple score;
- clear next steps;
- lightweight lead capture;
- CTA for setup assistance.

Initial pages:

1. `/`
2. `/spf-checker`
3. `/dmarc-checker`
4. `/mx-record-checker`
5. `/spf-lookup-counter`

## Chosen stack

Preferred initial stack:

- Next.js for frontend and SEO;
- FastAPI for DNS checks and API responses;
- no database in the MVP;
- in-memory TTL cache;
- basic rate limiting;
- JSON logs;
- cheap deployment.

## Initial monetization

The first monetization path is not subscription.

Initial monetization should be lightweight:

- lead capture;
- assisted setup CTA;
- waitlist for monitoring;
- later affiliate links or ads only after traffic exists.

First money signal:

> A user asks for help fixing SPF/DMARC/MX after running a scan.

## Main cuts

Do not build in the MVP:

- login;
- dashboard;
- Stripe;
- billing;
- SaaS plans;
- database;
- monitoring;
- paid API;
- PDF reports;
- agency panel;
- blacklist checks;
- BIMI;
- MTA-STS;
- TLS-RPT;
- email header analyzer;
- AI-based diagnosis in the technical core.
