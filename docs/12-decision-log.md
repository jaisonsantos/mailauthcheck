# 12 — Decision Log

This document records product and architecture decisions.

Every scope or architecture change should be added here.

| Date | Decision | Reason | Impact | Status |
|---|---|---|---|---|
| 2026-06-19 | Start as a utility site, not SaaS. | The fastest validation path is a free, indexable tool with immediate value. | Avoids login, billing, dashboard and premature complexity. | Accepted |
| 2026-06-19 | Use MailAuthCheck as the initial name. | It is clear, SEO-friendly and credible enough for a technical utility. | Product starts with a practical name; InboxReady may remain a future brand option. | Accepted |
| 2026-06-19 | Use Next.js + FastAPI as preferred stack. | Next.js supports SEO pages; FastAPI supports simple DNS-check APIs with low overhead. | Keeps MVP fast to build and cheap to deploy. | Accepted |
| 2026-06-19 | Do not use a database in the MVP. | MVP has no login, dashboard, history, billing or monitoring. | Reduces infrastructure, privacy and maintenance burden. | Accepted |
| 2026-06-19 | Leave DKIM for week 2 / V1. | DKIM usually requires a selector; guessing selectors creates false negatives. | MVP focuses on SPF, DMARC, MX, SPF lookup count and readiness. | Accepted |
| 2026-06-19 | Launch first 5 SEO pages. | These pages match clear search intent and can reuse the core scanner logic. | Initial hub includes `/`, `/spf-checker`, `/dmarc-checker`, `/mx-record-checker`, `/spf-lookup-counter`. | Accepted |
| 2026-06-19 | Use CTA for assisted setup. | Setup requests are the first likely commercial signal. | Adds lightweight monetization without building SaaS. | Accepted |
| 2026-06-19 | Do not implement login, dashboard or Stripe in MVP. | These features create SaaS complexity before validation. | Protects scope and keeps launch small. | Accepted |

## Pending decisions

| Date | Pending decision | Why it matters | Owner | Status |
|---|---|---|---|---|
| 2026-06-19 | Choose backend hosting provider. | DNS latency and cold starts affect UX. | Technical | Pending |
| 2026-06-19 | Choose analytics tool: Plausible or Google Analytics. | Analytics must track validation without adding complexity. | Product/technical | Pending |
| 2026-06-19 | Choose lead capture method. | External form avoids database; custom form may improve UX. | Product/technical | Pending |
| 2026-06-19 | Decide if Spanish content should start after validation or after first traction. | User lives in Spain, but initial SEO should be English. | SEO/product | Pending |
