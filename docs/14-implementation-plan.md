# 14 — Implementation Plan

This plan turns the current backlog into an incremental implementation sequence.

It is a planning document only. Do not write code from this file until a specific implementation task is created.

## Decision status

- **accepted:** MailAuthCheck starts as a free, fast, SEO-friendly utility site.
- **accepted:** The first product vertical is Bulk Sender Readiness for Gmail/Yahoo bulk sender requirements.
- **accepted:** MVP checks are SPF, DKIM selector signals, DMARC, MX, SPF DNS lookup count and manual bulk sender checklist items.
- **accepted:** DMARC `p=none` is minimum/monitoring mode for bulk sender requirements, not absolute Gmail non-compliance.
- **accepted:** The MVP has no login, dashboard, billing, database, recurring monitoring or paid API.
- **accepted:** Preferred stack is Next.js for frontend/SEO and FastAPI for DNS/API checks.
- **hypothesis:** Lightweight lead capture can create assisted setup requests without turning the MVP into SaaS.

## Milestone 0 — Repository preparation

### Objective

Prepare the repository for implementation without adding unnecessary executable files.

### Small tasks

- Verify the current documentation map.
- Confirm that the MVP scope in `docs/02-mvp-scope.md` is still closed.
- Review pending decisions before implementation starts.
- Confirm that API, schema, scoring and SEO documents are aligned.
- Define the first implementation task in a narrow issue or prompt.
- Keep the project documentation-first until an explicit code task exists.

### Expected files

- Existing docs only.
- No new runtime files.
- Optional future documentation updates if a real decision changes.

### Acceptance criteria

- Contributors can identify what is in and out of MVP scope.
- The first code task is small and reviewable.
- No executable project structure exists before it is explicitly requested.
- `docs/12-decision-log.md` is unchanged unless a real decision changes.

### Risks

- Starting frontend/backend scaffolding before the first implementation task is approved.
- Treating backlog items as permission to build everything at once.
- Adding SaaS-oriented assumptions too early.

### What not to do

- Do not create a Next.js app.
- Do not create a FastAPI app.
- Do not create `package.json`, `pyproject.toml`, `requirements.txt`, Dockerfile or CI/CD files.
- Do not add a database.
- Do not add authentication, billing, dashboards or scan history.

## Milestone 1 — Frontend static shell

### Objective

Plan the first static interface before real DNS logic is connected.

### Small tasks

- Define the static homepage structure.
- Plan a mobile-first layout with the domain input visible above the fold.
- Include bulk sender hero copy from the product brief.
- Plan a domain input state and optional ESP selector without real scanning behavior.
- Design mocked result cards for SPF, DKIM selector signal, DMARC, MX, SPF lookup count and Gmail/Yahoo readiness.
- Include a manual checks panel for one-click unsubscribe and spam-rate review.
- Add a simple score preview using realistic placeholder states.
- Plan a next steps section with 1-3 practical recommendations.
- Include CTA copy: `Need help fixing this?`
- Draft the initial FAQ section.
- Plan reusable layout pieces for the initial SEO pages.

### Expected files

- Future frontend files only when an implementation task is created.
- Documentation references: `docs/01-product-brief.md`, `docs/05-result-schema.md`, `docs/06-scoring-model.md`, `docs/08-pages-and-content.md`.

### Acceptance criteria

- The static shell answers the central question clearly.
- Mocked cards match the planned bulk result schema.
- Manual requirements are shown as manual checks, not passed checks.
- The UI includes a visible disclaimer that no inbox placement is guaranteed.
- The CTA exists but does not imply automatic paid checkout.
- The page is useful on mobile and desktop.

### Risks

- Making the page look like a SaaS dashboard.
- Overexplaining DNS before giving the user a result.
- Adding too many CTAs before validation.

### What not to do

- Do not add accounts, dashboard navigation or pricing pages.
- Do not add fake monitoring history.
- Do not imply that MailAuthCheck guarantees deliverability.
- Do not build complex report exports.

## Milestone 2 — Backend API skeleton

### Objective

Plan the minimum backend API shape without complex DNS logic.

### Small tasks

- Keep `POST /api/check-domain` as the main aggregate endpoint for now.
- Plan request support for `mode=bulk_sender` and optional `espProvider`.
- Confirm whether any auxiliary health endpoint is needed.
- Apply domain validation rules before DNS work.
- Return the aggregate response structure from the API contract.
- Define initial error responses for invalid input, timeout and DNS failure.
- Keep responses compatible with frontend result cards.
- Keep the service stateless.

### Expected files

- Future FastAPI files only when an implementation task is created.
- Documentation references: `docs/04-api-contract.md`, `docs/05-result-schema.md`.

### Acceptance criteria

- `POST /api/check-domain` accepts a domain-only payload.
- URLs, email addresses and empty input are rejected.
- API responses include domain, mode, ESP provider, DNS authentication score, bulk status, automated checks, manual checks, checklist items, next steps and disclaimer.
- Errors are understandable for non-technical users.
- No persistence is required.

### Risks

- Adding persistence for convenience.
- Expanding the API into a public developer product.
- Returning backend-centric errors that are hard to render.

### What not to do

- Do not add a database.
- Do not add authentication.
- Do not add paid API concepts.
- Do not add user accounts or scan history.

## Milestone 3 — DNS checks

### Objective

Plan implementation of the technical checks required for the MVP.

### Small tasks

- Implement MX lookup behavior.
- Implement SPF TXT lookup behavior.
- Detect multiple SPF records.
- Estimate SPF DNS lookup count.
- Implement DKIM TXT lookup behavior for selected/common ESP selectors.
- Implement DMARC lookup at `_dmarc.domain`.
- Parse DMARC policy values: `p=none`, `p=quarantine`, `p=reject`.
- Define DNS timeout behavior.
- Define DNS error behavior.
- Set `confidence` for each check.
- Set `canBeFalsePositive` where simplified parsing or DNS behavior may mislead.
- Generate manual checks for one-click unsubscribe and spam rate without marking them as verified.

### Expected files

- Future backend DNS modules only when implementation starts.
- Documentation references: `docs/02-mvp-scope.md`, `docs/04-api-contract.md`, `docs/05-result-schema.md`, `docs/06-scoring-model.md`.

### Acceptance criteria

- MX results include hostnames and priorities when available.
- SPF results distinguish missing, single record, multiple records and lookup-count risk.
- DKIM results distinguish found, not found, unknown selector, malformed record and DNS errors.
- DKIM selector misses are confidence-aware and can be false positives.
- DMARC results distinguish missing record and policy state.
- DMARC `p=none` is represented as minimum/monitoring mode.
- Timeout and DNS errors do not crash the whole scan.
- Each check can expose raw records for technical users.

### Risks

- False negatives from DNS resolver timeouts.
- Overclaiming Gmail/Yahoo readiness from basic records alone.
- Recursive SPF lookup count becoming too complex for MVP.

### What not to do

- Do not present guessed DKIM selector misses as proof that DKIM is absent.
- Do not add blacklist checks.
- Do not add BIMI, MTA-STS or TLS-RPT.
- Do not add AI diagnosis in the DNS core.

## Milestone 4 — Scoring and result rendering

### Objective

Plan score, labels, result cards and explanations in a way users can act on.

### Small tasks

- Apply a DNS Authentication Score from 0-100.
- Map score and blockers to `Ready`, `Needs work`, `Not ready` or `DNS checks incomplete`.
- Render manual checks separately from the score.
- Define blockers that prevent `Ready`.
- Render result cards for each check.
- Show concise explanations first.
- Show technical details and raw records behind an optional section.
- Include next steps based on the most important issues.
- Include disclaimers near the result.

### Expected files

- Future frontend result components only when implementation starts.
- Documentation references: `docs/05-result-schema.md`, `docs/06-scoring-model.md`.

### Acceptance criteria

- Users can understand whether the domain is minimally ready.
- A missing DMARC, broken SPF or missing/unknown DKIM cannot be presented as fully ready for bulk sending.
- One-click unsubscribe and spam rate cannot be marked as passed unless verified.
- Next steps are practical and limited.
- Technical users can inspect raw records.
- Every result avoids inbox placement guarantees.

### Risks

- A score that feels precise beyond the available checks.
- Too much technical language in the main result.
- Hiding critical warnings in technical details.

### What not to do

- Do not create a deliverability score.
- Do not promise spam-folder avoidance.
- Do not add complex PDF report generation.
- Do not create agency-facing reporting workflows.

## Milestone 5 — SEO pages

### Objective

Plan the five initial indexable pages.

### Small tasks

- Plan `/` as the main Bulk Email Readiness Checker page.
- Plan `/bulk-email-readiness-checker`.
- Plan `/gmail-bulk-sender-requirements`.
- Plan `/dmarc-policy-bulk-email`.
- Plan `/guides/mailchimp-gmail-compliance`.
- Plan `/spf-checker`.
- Plan `/dmarc-checker`.
- Plan `/mx-record-checker`.
- Plan `/spf-lookup-counter`.
- Define title, meta description and H1 per page.
- Include FAQ content per page.
- Add internal links between related tools.
- Reuse the home scanning logic across pages.

### Expected files

- Future frontend route/page files only when implementation starts.
- Documentation references: `docs/07-seo-plan.md`, `docs/08-pages-and-content.md`.

### Acceptance criteria

- Each page has a distinct search intent.
- Each page includes the domain checker or a clear path to run it.
- Metadata is specific and not duplicated blindly.
- Internal links connect SPF, DMARC, MX and lookup count pages.
- FAQ content is useful and non-alarmist.

### Risks

- Creating thin SEO pages with no practical tool value.
- Duplicating the same copy across every page.
- Adding pages outside the MVP before the initial five are live.

### What not to do

- Do not add BIMI, blacklist or header analyzer pages in the MVP.
- Do not add ESP API integrations.
- Do not add provider-specific guides before core pages are stable.
- Do not use claims that guarantee deliverability.

## Milestone 6 — Analytics, Search Console and lead capture

### Objective

Plan real validation without adding SaaS infrastructure.

### Small tasks

- Configure analytics event names before launch.
- Prepare Google Search Console verification and sitemap submission.
- Track scans performed.
- Track unique domains, using privacy-conscious handling.
- Track CTA clicks.
- Track email captures.
- Track setup requests.
- Prefer external form tooling for lead capture if it avoids a database.
- Document basic privacy and disclaimer copy.

### Expected files

- Future analytics configuration only when implementation starts.
- Future privacy/disclaimer page or section if needed.
- Documentation references: `docs/09-validation-plan.md`, `docs/10-monetization.md`.

### Acceptance criteria

- Core events are measurable from day one.
- Lead capture works without a database.
- Users know what information they are submitting.
- Setup requests can be followed up manually.
- Analytics supports the 30-day validation decision.

### Risks

- Collecting more personal data than needed.
- Building custom CRM or persistence too early.
- Confusing a waitlist with a paid product.

### What not to do

- Do not add Stripe or checkout.
- Do not add accounts.
- Do not store scan history.
- Do not create recurring monitoring.

## Milestone 7 — MVP launch checklist

### Objective

Define what must be ready before publishing.

### Small tasks

- Complete technical checklist.
- Complete SEO checklist.
- Complete UX checklist.
- Complete analytics checklist.
- Complete lead capture checklist.
- Complete disclaimer checklist.
- Test with representative domains.
- Define launch/no-launch criteria.

### Expected files

- `docs/16-mvp-launch-checklist.md`.
- Future implementation files only after explicit implementation tasks.

### Acceptance criteria

- The domain checker works for real domains.
- Core DNS errors and timeouts are handled.
- Search Console and analytics are ready.
- Lead capture is available without SaaS infrastructure.
- Disclaimers are visible.
- Launch criteria are met.

### Risks

- Publishing without analytics and losing validation data.
- Publishing without disclaimers.
- Delaying launch for non-MVP features.

### What not to do

- Do not wait for SaaS features.
- Do not add billing to make launch feel complete.
- Do not add monitoring before users ask for it.
- Do not expand beyond the first five SEO pages before launch.

## Recommended first implementation task

Recommended first real implementation task:

> Create the static Next.js homepage shell for `/` only, with mobile-first layout, domain input, mocked result cards, next steps, FAQ, setup CTA and disclaimer. Do not connect real DNS checks yet.

Reason:

- It validates the first user experience before backend complexity.
- It uses already accepted product copy and scope.
- It keeps the first code change small and reviewable.
