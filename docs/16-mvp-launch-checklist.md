# 16 — MVP Launch Checklist

This checklist defines what must be true before publishing the MVP.

It should be used after specific implementation tasks exist. It does not authorize building beyond the accepted MVP scope.

## Product

- [x] The central question is clear: is this domain ready for bulk email sending to Gmail and Yahoo?
- [x] Domain input is easy to find and use.
- [x] Optional sending platform selector is available.
- [x] The result is understandable for non-technical users.
- [x] SPF, DKIM selector signal, DMARC, MX, SPF lookup count and Gmail/Yahoo readiness are visible.
- [x] Automated checks and manual checks are visually separated.
- [x] Next steps are clear and limited to the main issues.
- [x] Technical details are available without overwhelming the main result.
- [x] Disclaimers are visible near the result.
- [x] The product does not promise inbox placement.
- [x] The CTA for assisted setup is present but lightweight.
- [x] The main form makes the domain the primary input and the sending platform optional.
- [x] No SaaS language dominates the MVP.

## Technical

- [x] Domain validation accepts domains only.
- [x] URLs are rejected.
- [x] Email addresses are rejected.
- [x] Empty input is rejected.
- [x] SPF check works.
- [x] Multiple SPF records are detected.
- [x] DKIM selector-aware check works.
- [x] DMARC check works.
- [x] DMARC policy is detected.
- [x] DMARC `p=none` is treated as minimum/monitoring mode, not absolute non-compliance.
- [x] MX check works.
- [x] SPF lookup count is estimated.
- [x] DNS timeout is handled.
- [x] DNS error is handled.
- [x] Basic rate limiting exists.
- [x] In-memory TTL cache exists.
- [x] JSON logs exist.
- [x] Errors are friendly and actionable.
- [x] No database is required.
- [x] No authentication is required.
- [ ] Recent checks history is local-only, capped at 10 items, and expires after 24h.

## SEO

- [x] `/` has a unique title and meta description.
- [x] `/bulk-email-readiness-checker` has a unique title and meta description.
- [x] `/gmail-bulk-sender-requirements` has a unique title and meta description.
- [x] `/dmarc-policy-bulk-email` has a unique title and meta description.
- [x] `/guides/mailchimp-gmail-compliance` has a unique title and meta description.
- [x] `/spf-checker` has a unique title and meta description.
- [x] `/dmarc-checker` has a unique title and meta description.
- [x] `/mx-record-checker` has a unique title and meta description.
- [x] `/spf-lookup-counter` has a unique title and meta description.
- [x] Each page has one clear H1.
- [x] FAQ content exists where useful.
- [x] Internal links connect the initial pages.
- [x] Canonical URLs are set.
- [x] `sitemap.xml` exists.
- [x] `robots.txt` exists.
- [ ] Google Search Console is ready.
- [x] SEO copy avoids deliverability guarantees.

## Analytics

- [x] `page_view` is tracked.
- [x] `scan_started` is tracked.
- [x] `scan_completed` is tracked.
- [x] `scan_failed` is tracked.
- [x] ESP selection is tracked in scan events without storing unnecessary personal data.
- [x] `cta_clicked` is tracked.
- [ ] `lead_submitted` is tracked.
- [ ] Scan error rate can be reviewed.
- [x] CTA clicks can be separated by CTA type.
- [ ] Unique domains can be estimated in a privacy-conscious way.

## Lead Capture

- [x] A visible CTA exists after relevant scan results.
- [x] Lead capture uses an external form or simple non-database approach where possible.
- [ ] Form captures email.
- [x] Form captures domain.
- [x] Form captures selected ESP when available.
- [x] Form captures detected problem or issue summary.
- [ ] Optional message field exists.
- [ ] Confirmation message is shown after submission.
- [x] Privacy/disclaimer copy is visible.
- [x] No checkout exists.
- [x] No paid plan language is required.

## Launch

- [ ] Choose the first deployment path: easiest managed backend or cheapest persistent Oracle Always Free backend.
- [ ] Configure frontend env vars in the hosting provider.
- [ ] Configure backend `ALLOWED_ORIGINS` with exact production and preview frontend origins.
- [ ] Confirm frontend and backend both use HTTPS in production.
- [ ] Confirm backend `/healthz` is reachable from outside the local network.
- [x] Test with real domains that have valid SPF, DMARC and MX.
- [x] Test with an ESP-selected domain that has DKIM selector records.
- [x] Test with an ESP-selected domain where common DKIM selectors are not found.
- [x] Test with a domain without SPF.
- [x] Test with a domain without DMARC.
- [x] Test with a domain with multiple SPF records.
- [x] Test with a domain near or above SPF lookup limits.
- [x] Test DMARC `p=none` copy and scoring.
- [x] Test manual checks are not marked as passed automatically.
- [x] Test timeout or DNS error handling.
- [ ] Test mobile layout.
- [ ] Test desktop layout.
- [ ] Test recent checks can reopen a saved result without a new API request.
- [ ] Test Refresh DNS now performs a live API request.
- [ ] Test Clear history removes local saved snapshots.
- [ ] Test 429 shows a fallback path when a saved snapshot exists.
- [x] Test SEO metadata in production build.
- [ ] Test analytics events in production or preview.
- [ ] Test lead form submission.
- [ ] Confirm external lead form receives `domain`, `espProvider`, `status`, `score`, `issues`, `tool`, `page`, and `cta`.
- [ ] Publish the MVP.
- [ ] Submit sitemap in Search Console.
- [ ] Share in initial channels.
- [ ] Measure results for 30 days.

## Launch criteria

Launch when:

- [x] The scanner answers the bulk sender readiness question.
- [x] Core DNS checks, including selector-aware DKIM, work for representative domains.
- [x] The result includes next steps and disclaimers.
- [ ] Analytics and Search Console are ready.
- [ ] Lead capture works without SaaS infrastructure.
- [x] The first five pages are indexable.

Do not delay launch for:

- Login.
- Dashboard.
- Billing.
- Database-backed scan history.
- Monitoring.
- Paid API.
- Blacklist checks.
- BIMI, MTA-STS or TLS-RPT.
- DKIM selector checker.
- ESP API integrations.
- Email list verification.
- Email content scanning.
- Sending real test emails.
- Complex PDF reports.
