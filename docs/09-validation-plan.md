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
- ask for help preparing SPF/DKIM/DMARC for a campaign or ESP.

## Days 1–3

### Deliverables

- Main domain scanner.
- SPF check.
- DKIM selector signal.
- DMARC check.
- MX check.
- SPF lookup count.
- Gmail/Yahoo bulk sender readiness.
- Manual checks for one-click unsubscribe and spam-rate review.
- Score and label.
- Basic result UI.
- Next steps.
- Setup assistance CTA.
- Analytics plan.
- Search Console setup plan.

### Metrics to prepare

- scans performed;
- scans with ESP selected;
- unique domains tested;
- percentage of scans with DKIM warning/unknown;
- score bucket;
- failed checks;
- CTA clicks;
- latency;
- error rate.

## Days 4–7

### Publish pages

- `/`
- `/bulk-email-readiness-checker`
- `/gmail-bulk-sender-requirements`
- `/dmarc-policy-bulk-email`
- `/guides/mailchimp-gmail-compliance`

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

- Improve DKIM selector coverage if confidence language is clear.
- Add “Copy technical report”.
- Improve error messages.
- Add provider-specific next steps.
- Draft Brevo, Klaviyo, SendGrid and Postmaster Tools guides.

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
- clicks on ESP-specific guides;
- clicks on Postmaster Tools references;
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
- 1 person asks about price for SPF/DKIM/DMARC setup.
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
