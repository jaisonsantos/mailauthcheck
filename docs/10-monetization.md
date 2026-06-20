# 10 — Monetization

## Principle

Do not monetize heavily before validating usage.

MailAuthCheck should first prove that users search, scan, understand, and ask for help.

## Monetization stages

| Option | When to consider | Difficulty | First version | Risk |
|---|---|---:|---|---|
| Assisted setup | From day 1 | Low | SPF/DKIM/DMARC setup CTA/form | Manual support burden |
| Email capture | From day 1 | Low | Waitlist/checklist form | Low conversion |
| Affiliates | After traffic appears | Medium | Links in provider guides | May look spammy |
| Ads | After meaningful traffic | Low/medium | Minimal ad placement | Can hurt UX |
| Paid PDF | After users ask for reports | Medium | Human-readable export | Users may not pay |
| Monitoring | After recurring demand | Medium/high | One-domain alerting | Turns into SaaS too early |
| Agency/API | After agency demand | High | Manual pilot | Multi-tenant complexity |

## Assisted setup

### When to consider

Immediately, but lightweight only.

### First version

A CTA after the result:

> Need help fixing this?

Form fields:

- email;
- domain;
- issue summary;
- selected ESP;
- optional message.

### Risk

Can become manual consulting with no clear price.

### Guardrail

Do not build a marketplace, booking system, or payment flow in the MVP.

## Email capture

### When to consider

Immediately.

### First version

Options:

- “Send me the checklist.”
- “Notify me when monitoring is available.”
- “Send this report to my developer.”
- “Prepare my domain for Gmail bulk sender requirements.”
- “Configure SPF/DKIM/DMARC for Mailchimp.”

### Risk

Users may not want to give email for a one-time utility.

## Affiliates

### When to consider

After pages receive traffic.

### Possible areas

- email hosting;
- domain hosting;
- Google Workspace/Microsoft 365 partners if appropriate;
- email sending providers;
- DNS providers.

### Risk

Affiliate links can reduce trust if introduced too early or too aggressively.

## Ads

### When to consider

Only after meaningful traffic.

Suggested threshold:

- 5k–10k visits/month minimum.

### Risk

Ads can make a trust-sensitive technical tool look low quality.

## Paid PDF

### When to consider

Only if users ask for shareable reports.

### First version

Simple “human-readable report” export or email summary.

### Risk

This can distract from the core utility and may not convert.

## Monitoring

### When to consider

Only if users explicitly ask:

> Can you monitor this domain and tell me if something breaks?

### First version

Manual or simple one-domain monitoring pilot.

### Risk

This introduces database, jobs, email alerts, account state, and billing pressure.

## Agency/API

### When to consider

Only after agencies use the tool repeatedly or request bulk checks.

### First version

Manual pilot with a small agency.

### Risk

This is the path to SaaS complexity. Do not start here.

## CTA examples

- Need help fixing this?
- Prepare my domain for Gmail bulk sender requirements.
- Configure SPF/DKIM/DMARC for my ESP.
- Want us to monitor this domain?
- Get a human-readable report.
- Send this report to your developer.
- Join the waitlist for monitoring.

## First signal of money

The first real money signal is:

> A user submits a domain and asks for help fixing SPF, DKIM, DMARC, MX, or bulk sender readiness before a campaign.

Not a scan. Not a page view. Not a compliment.

A help request is the first commercial signal.
