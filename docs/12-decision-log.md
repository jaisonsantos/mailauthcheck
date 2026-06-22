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
| 2026-06-20 | Keep MVP executable code at repository root for now. | The current codebase is still small, and a monorepo `apps/` split would add structure before it reduces complexity. | Frontend lives in root `app/`; backend skeleton lives in root `api/` until growth justifies a move. | Accepted |
| 2026-06-20 | Use in-memory fixed-window protections for MVP runtime. | The utility needs basic abuse protection and repeat-scan efficiency without adding Redis, a database or queueing infrastructure. | MVP uses 15-minute TTL cache, basic IP/domain rate limits and JSON API logs in-process. | Accepted |
| 2026-06-20 | Use Plausible for MVP analytics. | It adds lightweight event tracking without cookies, heavy setup or internal persistence. | Frontend can track page views and key validation events through one script and a small client helper. | Accepted |
| 2026-06-20 | Use an external lead form URL for MVP setup requests. | Lead capture must work without a database, account model or internal submission backend. | CTAs open an external form with domain and issue context prefilled when configured. | Accepted |
| 2026-06-20 | Reposition the first public product vertical to Bulk Sender Readiness. | The Gmail/Yahoo bulk sender angle has stronger commercial intent, clearer urgency and better differentiation than a generic SPF/DMARC/MX checker. | Home and roadmap shift toward bulk sender readiness, optional ESP selection, DKIM selector-aware checks, manual checklist items and ESP-specific next steps. No login, dashboard, database, ESP API integration, list verification or inbox-placement promise is introduced. | Accepted |
| 2026-06-20 | Treat DMARC `p=none` as minimum/monitoring mode for bulk sender requirements. | Gmail and Yahoo guidance allow a valid DMARC policy with at least `p=none` for bulk sender minimums, while stronger enforcement remains recommended after review. | Product copy and scoring must not describe `p=none` as absolute non-compliance; it should be a warning/weak enforcement signal. | Accepted |
| 2026-06-20 | Add lightweight EN/ES/PT UI language controls and light/dark theme controls. | The MVP needs to feel credible and usable for English, Spanish and Portuguese-speaking users without adding heavy i18n routing or SaaS complexity. | Frontend may provide client-side language and theme preferences stored locally. SEO locale routing and backend-translated result text remain out of this decision. | Accepted |
| 2026-06-20 | Launch first public UI in English only while keeping ES/PT code dormant. | Spanish and Portuguese copy needs native review before public launch, and awkward translation would reduce credibility. | The language selector is hidden for launch; ES/PT client-side copy can be re-enabled after review. | Accepted |
| 2026-06-20 | Re-enable the EN/ES/PT toggle after a short UX copy review. | The current visible copy is now good enough for users to navigate the product without obvious mixed-language friction. | The language selector is visible again in the UI, while SEO locale routing and deeper content translation remain pending. | Accepted |
| 2026-06-21 | Default the launch build back to English-only with an environment-controlled locale toggle. | The first public deploy needs one consistent language, but the multilingual UI should stay available for later staged rollout. | `NEXT_PUBLIC_SHOW_LOCALE_SELECTOR` now controls whether EN/ES/PT is visible. The default launch behavior is English-only, and old locale values in localStorage are ignored when the toggle is hidden. | Accepted |
| 2026-06-22 | Accept local-only recent checks history for the MVP. | Users need a lightweight way to reopen recent scans without creating SaaS-style scan history or backend persistence. | `Recent checks` is stored only in browser `localStorage`, capped at 10 items, retained for 24h, and can be cleared locally. Opening a saved result does not call the API; refresh still does. | Accepted |
| 2026-06-22 | Make the domain input the primary action and the sending platform optional. | The product should feel like a simple domain checker first, not an ESP-first setup flow. | Form copy, button labels and help text now emphasize the domain as the main input while keeping provider selection optional and secondary. | Accepted |

## Pending decisions

| Date | Pending decision | Why it matters | Owner | Status |
|---|---|---|---|---|
| 2026-06-19 | Choose backend hosting provider. | DNS latency and cold starts affect UX. | Technical | Pending |
| 2026-06-20 | Choose the initial ESP selector set and confidence language for DKIM. | Selector guessing can create false negatives, especially across ESPs and custom configurations. | Technical/product | Pending |
| 2026-06-20 | Decide whether the aggregate endpoint remains `/api/check-domain` or later moves to `/api/v1/bulk-readiness`. | Keeping the current endpoint reduces refactor risk, but a versioned bulk endpoint may become clearer once response shape changes. | Technical | Pending |
| 2026-06-20 | Decide whether to add SEO locale routing for `/es` and `/pt`. | Client-side language controls improve UX but do not create indexable localized SEO pages. | SEO/product | Pending |
