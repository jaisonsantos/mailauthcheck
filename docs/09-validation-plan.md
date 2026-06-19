# 09 — Validation Plan

## Goal

Validate in 30 days whether MailAuthCheck deserves continued investment.

The goal is not to build a complete SaaS.

The goal is to learn whether users:

- search for this;
- run scans;
- understand the result;
- click CTAs;
- leave email;
- ask for help fixing their domain.

## Days 1–3

### Deliverables

- Main domain scanner.
- SPF check.
- DMARC check.
- MX check.
- SPF lookup count.
- Basic Gmail/Yahoo readiness.
- Score and label.
- Basic result UI.
- Next steps.
- Setup assistance CTA.
- Analytics plan.
- Search Console setup plan.

### Metrics to prepare

- scans performed;
- unique domains tested;
- score bucket;
- failed checks;
- CTA clicks;
- latency;
- error rate.

## Days 4–7

### Publish pages

- `/`
- `/spf-checker`
- `/dmarc-checker`
- `/mx-record-checker`
- `/spf-lookup-counter`

### Additional deliverables

- sitemap;
- robots.txt;
- FAQ content;
- internal links;
- privacy/disclaimer page;
- basic analytics;
- Search Console submission.

## Days 8–14

### Improvements

- Add `/gmail-yahoo-sender-requirements-checker` if core checks are stable.
- Add `/dkim-selector-checker` if selector-based scope is clear.
- Add “Copy technical report”.
- Improve error messages.
- Add provider-specific hints.
- Draft Google Workspace and Microsoft 365 guides.

### Validation activity

- Share with developers and freelancers.
- Ask for feedback on clarity.
- Observe where users misunderstand the result.
- Track whether people click setup CTA.

## Days 15–30

### Distribution

- LinkedIn post.
- Indie Hackers post.
- Reddit feedback posts where allowed.
- WordPress/Shopify/freelancer groups.
- Spanish/LatAm communities.
- Direct feedback requests to freelancers/agencies.

### Measure

Track:

- scans;
- unique domains;
- Search Console impressions;
- organic clicks;
- indexed pages;
- emails captured;
- CTA clicks;
- setup requests;
- time on page;
- returning users.

## Realistic 30-day numbers

| Metric | Realistic range |
|---|---:|
| Indexed pages | 5–8 |
| Search Console impressions | 50–500 |
| Organic clicks | 5–50 |
| Total scans | 50–300 |
| Unique domains | 30–150 |
| Emails captured | 1–10 |
| CTA clicks | 3–30 |
| Setup/help requests | 0–5 |
| Returning users | 0–10 |
| Time on tool pages | >45 seconds is positive |

## Success criteria

Continue if at least two of these happen in the first 30 days:

- 100+ real scans.
- 5+ email captures.
- 1+ assisted setup request.
- Search Console impressions are growing.
- Someone shares or recommends the tool without being asked.
- Users say the result is clearer than existing tools.

## Pause or pivot criteria

Pause or pivot if:

- almost nobody scans after manual distribution;
- users scan but do not click any CTA;
- users do not understand the result;
- SEO pages are not indexed or show no impressions;
- only advanced developers use it and show no commercial intent;
- support burden appears before any monetization signal.

## Decision at day 30

At the end of 30 days, choose one:

1. Continue with V1 hub SEO.
2. Improve positioning and UX, then retest.
3. Pivot to setup-assisted service.
4. Pause the project.

The decision must be added to `docs/12-decision-log.md`.
