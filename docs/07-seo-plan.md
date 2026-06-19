# 07 — SEO Plan

## SEO goal

The initial SEO goal is to validate whether users search for and use a simple domain email authentication checker.

MailAuthCheck should start with a small number of useful pages, not a large programmatic SEO site.

## Initial language

Start in English.

Reasons:

- larger global search market;
- stronger technical keyword volume;
- better fit for SPF, DMARC, MX and sender requirement queries;
- higher potential for future B2B leads and affiliates.

Do not start multilingual.

Future language expansion:

1. English first.
2. Spanish after validation.
3. Portuguese later only if there is clear demand.

## Priority keywords

| Priority | Keyword |
|---:|---|
| P0 | SPF checker |
| P0 | DMARC checker |
| P0 | MX record checker |
| P0 | SPF lookup counter |
| P0 | email domain health check |
| P1 | Gmail sender requirements checker |
| P1 | Yahoo sender requirements checker |
| P1 | Google Workspace SPF DKIM DMARC |
| P1 | Microsoft 365 DMARC setup |
| P2 | why are my emails going to spam |
| P2 | domain email authentication check |
| P2 | business emails going to spam |
| P2 | check domain email setup |
| P2 | SPF DMARC DKIM checker |

## First 5 pages

Launch these first:

1. `/`
2. `/spf-checker`
3. `/dmarc-checker`
4. `/mx-record-checker`
5. `/spf-lookup-counter`

Each page must include a real tool or tool-specific output above the fold.

## Future cluster

Future pages after MVP:

- `/dkim-selector-checker`
- `/gmail-yahoo-sender-requirements-checker`
- `/guides/google-workspace-spf-dkim-dmarc`
- `/guides/microsoft-365-dmarc-setup`
- `/guides/mailchimp-dkim-setup`
- `/guides/brevo-spf-dkim-dmarc`
- `/guides/sendgrid-domain-authentication`

Do not launch provider guides until the core tool works.

## URL structure

Use short, descriptive, English URLs:

- `/spf-checker`
- `/dmarc-checker`
- `/mx-record-checker`
- `/spf-lookup-counter`
- `/guides/google-workspace-spf-dkim-dmarc`

Avoid unnecessary nesting for tools.

## Schema markup

Suggested schema types:

- `SoftwareApplication` for the main tool;
- `FAQPage` for page FAQs;
- `HowTo` for provider setup guides;
- `BreadcrumbList` for guides and hub pages.

## Interlinking

Internal linking rules:

- Home links to all initial tools.
- SPF checker links to SPF lookup counter.
- SPF lookup counter links back to SPF checker.
- DMARC checker links to Gmail/Yahoo readiness checker when available.
- Provider guides link back to the domain checker.
- Every tool page includes related tools near the bottom.

## FAQ strategy

Each page should have 3–5 specific FAQ items.

FAQ content should answer real questions, not generic filler.

Examples:

- What is SPF?
- Why can multiple SPF records break email authentication?
- What is DMARC `p=none`?
- Does this guarantee inbox placement?
- Why does SPF have a 10 DNS lookup limit?

## Avoid bad programmatic SEO

Do not create many thin pages such as:

- `/check-spf-for-gmail`
- `/check-spf-for-yahoo`
- `/check-spf-for-outlook`
- `/spf-checker-for-ecommerce`

Only create a page when it has:

- distinct search intent;
- useful content;
- real tool output or a practical guide;
- internal links;
- specific FAQ.

## Content quality rule

Every SEO page should:

- put the tool above the fold;
- answer the main query quickly;
- explain the result in plain English;
- include technical details when useful;
- include next steps;
- avoid generic AI-written filler;
- avoid deliverability guarantees.
