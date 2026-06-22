# MailAuthCheck Pre-Launch Checklist

This file is the short go/no-go checklist for launch. The fuller product checklist lives in `docs/16-mvp-launch-checklist.md`.

## Frontend

- [ ] `npm run typecheck` passes.
- [ ] `npm run build` passes.
- [ ] Homepage and SEO pages render:
  - `/`
  - `/bulk-email-readiness-checker`
  - `/gmail-bulk-sender-requirements`
  - `/spf-checker`
  - `/dmarc-checker`
  - `/mx-record-checker`
  - `/spf-lookup-counter`
- [ ] Main checker submits to `NEXT_PUBLIC_MAILAUTHCHECK_API_URL`.
- [ ] CTA is lightweight and does not imply a SaaS account, checkout or dashboard.
- [ ] Disclaimer is visible and does not promise inbox placement.
- [ ] Mobile layout is checked on a real phone.

## Backend

- [ ] `python -m pytest` passes.
- [ ] `/healthz` responds.
- [ ] `/api/check-domain` responds for a real domain.
- [ ] DNS timeout and partial-failure responses are understandable.
- [ ] Rate limiting and TTL cache are active.
- [ ] JSON logs are readable in the deployment platform.

## Environment

- [ ] `NEXT_PUBLIC_SITE_URL` points to the production frontend URL.
- [ ] `NEXT_PUBLIC_MAILAUTHCHECK_API_URL` points to the production API URL.
- [ ] `NEXT_PUBLIC_PLAUSIBLE_DOMAIN` is set only when Plausible is ready.
- [ ] `NEXT_PUBLIC_LEAD_CAPTURE_URL` points to the external lead form or stays empty.
- [ ] Backend `ALLOWED_ORIGINS` allows the production frontend domain.

## Free-Tier Launch Path

- [ ] Frontend deployed on Vercel free tier.
- [ ] Backend deployed on a low-cost/free platform such as Oracle Cloud Free Tier, Render free tier, Railway trial/free credits or Fly.io free allowance if available.
- [ ] No database provisioned for MVP.
- [ ] No paid monitoring stack required before validation.
- [ ] Smoke test script passes against production URLs.

## Smoke Test

```bash
NEXT_PUBLIC_SITE_URL=https://mailauthcheck.com \
NEXT_PUBLIC_MAILAUTHCHECK_API_URL=https://api.mailauthcheck.com \
./tests/smoke_tests.sh
```

## Go/No-Go

- [ ] Automated checks pass.
- [ ] Smoke tests pass.
- [ ] Lead capture path was manually tested.
- [ ] Founder review approved.
- [ ] Launch announcement channels are ready.
