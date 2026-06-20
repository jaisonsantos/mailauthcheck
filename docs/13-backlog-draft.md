# 13 — Backlog Draft

This backlog is a planning document only.

Do not write code from this backlog until specific implementation tasks are created.

## P0 MVP

### 0. Reposition MVP to Bulk Sender Readiness

**Description:** Update product, SEO, schema and implementation tasks so the first vertical answers Gmail/Yahoo bulk sender readiness instead of generic email domain health.

**Reason:** Bulk sender readiness has clearer urgency, stronger commercial intent and better differentiation than a generic SPF/DMARC/MX checker.

**Acceptance criteria:**

- Home copy uses Bulk Email Readiness positioning.
- Optional ESP selector is planned and implemented.
- DKIM selector-aware checks are planned with confidence warnings.
- Automated DNS checks and manual checks are separated.
- DMARC `p=none` is described as minimum/monitoring mode, not absolute Gmail non-compliance.
- No SaaS scope is introduced.

**Priority:** P0

**Dependencies:** Decision log

---

### 1. Define domain scan result contract

**Description:** Finalize the aggregate response and check result schemas for the MVP.

**Reason:** Frontend cards and backend checks need a stable contract.

**Acceptance criteria:**

- Schema includes domain, mode, optional ESP provider, DNS Authentication Score, bulk status, automated checks, manual checks, checklist items, nextSteps and disclaimer.
- Check schema includes status, severity, summary, technicalDetails, recommendedFix, rawRecords, confidence and canBeFalsePositive.
- Examples exist for SPF, DKIM selector signal, DMARC, MX, SPF lookup count and manual checks.

**Priority:** P0

**Dependencies:** None

---

### 2. Define domain validation rules

**Description:** Document accepted and rejected domain input formats.

**Reason:** Prevent confusing scans and reduce invalid requests.

**Acceptance criteria:**

- Accepts `example.com`.
- Rejects URLs.
- Rejects email addresses.
- Rejects empty input.
- Normalizes whitespace and casing.
- User-facing error copy is defined.

**Priority:** P0

**Dependencies:** API contract

---

### 3. Specify SPF check behavior

**Description:** Define how SPF records are detected and classified.

**Reason:** SPF is one of the core MVP checks.

**Acceptance criteria:**

- Missing SPF behavior is defined.
- Single SPF OK behavior is defined.
- Multiple SPF error behavior is defined.
- Weak SPF warning behavior is defined.
- Raw TXT output is included.

**Priority:** P0

**Dependencies:** Result schema

---

### 4. Specify SPF lookup count behavior

**Description:** Define how the MVP estimates SPF DNS lookup count.

**Reason:** SPF exceeding 10 DNS lookups is a high-value issue.

**Acceptance criteria:**

- Count ranges are defined: 0–7 OK, 8–10 warning, 11+ error.
- Mechanisms to count are listed.
- Confidence is set to medium when recursive parsing is simplified.
- canBeFalsePositive is true where appropriate.

**Priority:** P0

**Dependencies:** SPF check behavior

---

### 5. Specify DMARC check behavior

**Description:** Define how DMARC records and policies are detected.

**Reason:** DMARC is central to sender readiness.

**Acceptance criteria:**

- `_dmarc.domain` lookup behavior is defined.
- Missing DMARC behavior is defined.
- `p=none`, `p=quarantine`, and `p=reject` behavior is defined.
- Invalid DMARC behavior is defined.
- Recommended fixes are documented.

**Priority:** P0

**Dependencies:** Result schema

---

### 6. Specify MX check behavior

**Description:** Define how MX records are detected and displayed.

**Reason:** MX is a simple, useful signal for domain email setup.

**Acceptance criteria:**

- MX OK behavior is defined.
- MX missing behavior is defined.
- DNS error behavior is defined.
- Output includes hostnames and priorities when present.

**Priority:** P0

**Dependencies:** Result schema

---

### 7. Define Gmail/Yahoo readiness logic

**Description:** Define basic readiness logic without promising deliverability.

**Reason:** This creates a clearer business-facing result.

**Acceptance criteria:**

- Ready, needs work, not ready and incomplete states are defined.
- DMARC missing blocks readiness for bulk sender requirements.
- DKIM missing/unknown is confidence-aware and cannot be overclaimed.
- One-click unsubscribe and spam rate are manual checks.
- Disclaimer is included.
- No inbox placement guarantee is made.

**Priority:** P0

**Dependencies:** SPF, DMARC and SPF lookup checks

---

### 8. Define homepage content and layout

**Description:** Document homepage sections and microcopy.

**Reason:** The first page must convert search intent into scans.

**Acceptance criteria:**

- Hero copy is defined.
- Domain input copy is defined.
- Result card structure is defined.
- Next steps section is defined.
- Setup CTA is defined.
- FAQ topics are defined.

**Priority:** P0

**Dependencies:** Product brief

---

### 9. Define first 5 SEO pages

**Description:** Finalize URL, H1, title, meta description, FAQ and CTA for the first pages.

**Reason:** SEO validation depends on shipping useful pages quickly.

**Acceptance criteria:**

- `/` is defined.
- `/bulk-email-readiness-checker` is defined.
- `/gmail-bulk-sender-requirements` is defined.
- `/dmarc-policy-bulk-email` is defined.
- `/guides/mailchimp-gmail-compliance` is defined.
- Secondary SPF, DMARC, MX and SPF lookup pages remain available.
- Internal links are defined.

**Priority:** P0

**Dependencies:** SEO plan, page map

---

### 10. Define validation metrics

**Description:** Decide what metrics must be captured in the first 30 days.

**Reason:** The project needs clear continue/pause criteria.

**Acceptance criteria:**

- Scan count is tracked.
- Unique domains are tracked or estimated.
- CTA clicks are tracked.
- Email captures are tracked.
- Search Console metrics are reviewed.
- Success/pause criteria are documented.

**Priority:** P0

**Dependencies:** Validation plan

## P1 post-launch

### 11. DKIM selector checker planning

**Description:** Plan `/dkim-selector-checker` using domain + selector input.

**Reason:** DKIM is valuable but risky if selector is guessed.

**Acceptance criteria:**

- Domain + selector input is required.
- Selector guessing is not the primary path.
- False positive warning is documented.
- Page SEO metadata is defined.

**Priority:** P1

**Dependencies:** MVP launch

---

### 12. Gmail/Yahoo bulk sender requirements page

**Description:** Create a dedicated page for Gmail/Yahoo bulk sender readiness.

**Reason:** This can capture search demand from sender requirement changes.

**Acceptance criteria:**

- Page avoids deliverability guarantees.
- Readiness checklist is clear.
- SPF/DMARC/DKIM limitations are explained.
- Internal links point to SPF and DMARC tools.

**Priority:** P1

**Dependencies:** Core scanner stable

---

### 13. Copy technical report

**Description:** Define a copyable result summary for users to send to developers.

**Reason:** Non-technical users need help communicating DNS issues.

**Acceptance criteria:**

- Summary includes domain, score, failed checks and next steps.
- Raw records are included only in technical section.
- Disclaimer is included.

**Priority:** P1

**Dependencies:** Result schema

---

### 14. Provider guide drafts

**Description:** Draft Google Workspace and Microsoft 365 setup guides.

**Reason:** Provider guides can capture long-tail SEO and setup intent.

**Acceptance criteria:**

- Guides link back to relevant tools.
- Guides include practical checklist.
- Guides avoid outdated provider-specific claims unless verified.

**Priority:** P1

**Dependencies:** SEO plan

## P2 growth

### 15. Assisted setup landing section

**Description:** Improve the setup assistance CTA if users click it.

**Reason:** Setup requests are the first monetization signal.

**Acceptance criteria:**

- CTA explains what help is offered.
- Form captures email, domain and issue summary.
- No payment flow is added.

**Priority:** P2

**Dependencies:** CTA click data

---

### 16. Lightweight report export planning

**Description:** Plan a simple human-readable report only if users ask for it.

**Reason:** Reports may be useful, but should not distract from validation.

**Acceptance criteria:**

- Report scope is limited.
- No complex PDF engine is required in the planning phase.
- Decision log is updated before implementation.

**Priority:** P2

**Dependencies:** User requests

---

### 17. Monitoring pilot planning

**Description:** Plan a simple monitoring pilot only if users request recurring checks.

**Reason:** Monitoring is the likely path to SaaS, but should not start early.

**Acceptance criteria:**

- Clear signal threshold is defined.
- Minimal persistence need is documented.
- No full dashboard is included.

**Priority:** P2

**Dependencies:** Repeated monitoring requests

## Out of scope for now

### Login/dashboard

**Reason:** Premature SaaS complexity.

**Allowed later:** V4 only after commercial demand.

---

### Stripe/billing

**Reason:** No paid product exists yet.

**Allowed later:** Only after setup or monitoring demand is validated.

---

### Database

**Reason:** MVP has no persistence need.

**Allowed later:** Monitoring, history or accounts may require it.

---

### Blacklist checks

**Reason:** Adds third-party data quality issues and false positives.

**Allowed later:** Only if users explicitly request it and data source is reliable.

---

### BIMI, MTA-STS, TLS-RPT

**Reason:** Useful but not part of smallest email readiness MVP.

**Allowed later:** SEO hub expansion after core validation.

---

### Email header analyzer

**Reason:** Higher complexity and different input model.

**Allowed later:** Future utility page after initial hub traction.
