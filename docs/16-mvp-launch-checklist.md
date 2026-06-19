# 16 — MVP Launch Checklist

This checklist defines what must be true before publishing the MVP.

It should be used after specific implementation tasks exist. It does not authorize building beyond the accepted MVP scope.

## Product

- [ ] The central question is clear: is this domain ready to send email?
- [ ] Domain input is easy to find and use.
- [ ] The result is understandable for non-technical users.
- [ ] SPF, DMARC, MX, SPF lookup count and Gmail/Yahoo readiness are visible.
- [ ] Next steps are clear and limited to the main issues.
- [ ] Technical details are available without overwhelming the main result.
- [ ] Disclaimers are visible near the result.
- [ ] The product does not promise inbox placement.
- [ ] The CTA for assisted setup is present but lightweight.
- [ ] No SaaS language dominates the MVP.

## Technical

- [ ] Domain validation accepts domains only.
- [ ] URLs are rejected.
- [ ] Email addresses are rejected.
- [ ] Empty input is rejected.
- [ ] SPF check works.
- [ ] Multiple SPF records are detected.
- [ ] DMARC check works.
- [ ] DMARC policy is detected.
- [ ] MX check works.
- [ ] SPF lookup count is estimated.
- [ ] DNS timeout is handled.
- [ ] DNS error is handled.
- [ ] Basic rate limiting exists.
- [ ] In-memory TTL cache exists.
- [ ] JSON logs exist.
- [ ] Errors are friendly and actionable.
- [ ] No database is required.
- [ ] No authentication is required.

## SEO

- [ ] `/` has a unique title and meta description.
- [ ] `/spf-checker` has a unique title and meta description.
- [ ] `/dmarc-checker` has a unique title and meta description.
- [ ] `/mx-record-checker` has a unique title and meta description.
- [ ] `/spf-lookup-counter` has a unique title and meta description.
- [ ] Each page has one clear H1.
- [ ] FAQ content exists where useful.
- [ ] Internal links connect the initial pages.
- [ ] Canonical URLs are set.
- [ ] `sitemap.xml` exists.
- [ ] `robots.txt` exists.
- [ ] Google Search Console is ready.
- [ ] SEO copy avoids deliverability guarantees.

## Analytics

- [ ] `page_view` is tracked.
- [ ] `scan_started` is tracked.
- [ ] `scan_completed` is tracked.
- [ ] `scan_failed` is tracked.
- [ ] `cta_clicked` is tracked.
- [ ] `lead_submitted` is tracked.
- [ ] Scan error rate can be reviewed.
- [ ] CTA clicks can be separated by CTA type.
- [ ] Unique domains can be estimated in a privacy-conscious way.

## Lead Capture

- [ ] A visible CTA exists after relevant scan results.
- [ ] Lead capture uses an external form or simple non-database approach where possible.
- [ ] Form captures email.
- [ ] Form captures domain.
- [ ] Form captures detected problem or issue summary.
- [ ] Optional message field exists.
- [ ] Confirmation message is shown after submission.
- [ ] Privacy/disclaimer copy is visible.
- [ ] No checkout exists.
- [ ] No paid plan language is required.

## Launch

- [ ] Test with real domains that have valid SPF, DMARC and MX.
- [ ] Test with a domain without SPF.
- [ ] Test with a domain without DMARC.
- [ ] Test with a domain with multiple SPF records.
- [ ] Test with a domain near or above SPF lookup limits.
- [ ] Test timeout or DNS error handling.
- [ ] Test mobile layout.
- [ ] Test desktop layout.
- [ ] Test SEO metadata in production build.
- [ ] Test analytics events in production or preview.
- [ ] Test lead form submission.
- [ ] Publish the MVP.
- [ ] Submit sitemap in Search Console.
- [ ] Share in initial channels.
- [ ] Measure results for 30 days.

## Launch criteria

Launch when:

- [ ] The scanner answers the central user question.
- [ ] Core DNS checks work for representative domains.
- [ ] The result includes next steps and disclaimers.
- [ ] Analytics and Search Console are ready.
- [ ] Lead capture works without SaaS infrastructure.
- [ ] The first five pages are indexable.

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
- Complex PDF reports.
