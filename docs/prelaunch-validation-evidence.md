# Prelaunch Validation Evidence

## 1. Validation date and commit

- **Validation date/time:** 2026-06-22 16:42:28 CEST (+0200)
- **Branch:** `main`
- **Commit hash validated:** `6c9c81dc921da8c35af8660e95ad89edeb6a2f02`
- **Commit link:** https://github.com/jaisonsantos/mailauthcheck/commit/6c9c81dc921da8c35af8660e95ad89edeb6a2f02

## 2. Technical validation commands

| Command | Status | Output summary | Relevant notes |
| ------- | ------ | -------------- | -------------- |
| `npm run typecheck` | PASS | TypeScript completed with `tsc --noEmit` and no reported type errors. | npm printed `Unknown env config "min-release-age"` warning; this did not fail the command. |
| `npm run build` | PASS | Next.js 15.5.19 production build compiled successfully, generated 15 static pages, and completed page optimization/build traces. | npm printed the same env config warning before build; build passed. |
| `.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v` | PASS | Python unittest discovery ran 17 tests successfully. | Regression tests for MX fallback, DKIM empty public key, aggregate status gating, SPF, DMARC, and readiness behavior passed. |

## 3. Automated regression coverage

### MX resolver fallback

`tests/test_dns_resolver.py` confirms:

- system resolver timeout + fallback public resolver success => `resolve_mx` returns `ok`;
- system resolver timeout + fallback timeout => `resolve_mx` returns `timeout`;
- `resolve_txt` remains without fallback and TXT/SPF behavior remains unchanged.

The fallback behavior is limited to MX resolution and is triggered only for timeout/no-nameserver style resolver failures. DNS failures such as `NXDOMAIN` and `NoAnswer` remain explicit categories and are not converted into successful results.

### DKIM empty public key

`tests/test_backend_edge_cases.py` confirms:

- `v=DKIM1; p=` returns `warning`;
- expected summary is `DKIM selector found, but the public key is empty.`;
- DKIM with a valid public key remains `ok`;
- missing DKIM selector remains warning and false-positive aware.

### Aggregate status gating

`tests/test_backend_edge_cases.py` confirms:

- an aggregate score high enough for `ready` is still downgraded to `needs_attention` when `Gmail/Yahoo Readiness` is `warning`;
- `Status: Ready` is reserved for domains where automated Gmail/Yahoo readiness is `ok`.

## 4. Manual smoke test: 10 real domains

Smoke tests were rerun through the backend service logic after the DNS resolver and DKIM fixes.

| Domain | Score | Aggregate status | MX status | DKIM status | SPF lookup count | Important notes |
| ------ | ----: | ---------------- | --------- | ----------- | ---------------: | --------------- |
| example.com | 73 | needs_attention | missing | warning | 0 | Null MX detected; not a timeout. DKIM empty `p=` returns warning. |
| google.com | 83 | needs_attention | ok | warning | 1 | MX resolved. Aggregate is not `ready` because Gmail/Yahoo readiness needs DKIM confirmation. |
| github.com | 88 | needs_attention | ok | ok | 10 | MX resolved. Aggregate is not `ready` because Gmail/Yahoo readiness warns on SPF lookup count at the 10-lookup limit. |
| shopify.com | 95 | ready | ok | ok | 4 | MX resolved. |
| mailchimp.com | 95 | ready | ok | ok | 7 | MX resolved. |
| sendgrid.com | 83 | needs_attention | ok | warning | 3 | MX resolved. Aggregate is not `ready` because Gmail/Yahoo readiness needs DKIM confirmation. |
| brevo.com | 83 | needs_attention | ok | warning | 2 | MX resolved. DKIM empty `p=` returns warning; aggregate is not `ready`. |
| klaviyo.com | 95 | ready | ok | ok | 7 | MX resolved. |
| hubspot.com | 95 | ready | ok | ok | 4 | MX resolved. |
| zara.com | 83 | needs_attention | ok | warning | 1 | MX resolved. Aggregate is not `ready` because Gmail/Yahoo readiness needs DKIM confirmation. |

Findings:

- MX no longer fails in bulk across the real-domain sample.
- `example.com` is now reported as Null MX instead of timeout.
- `example.com` and `brevo.com` report DKIM empty `p=` as `warning`, not `ok`.
- Aggregate status now reflects domain-specific findings instead of blanket DNS timeout errors.
- `Status: Ready` is no longer shown when `Gmail/Yahoo Readiness` is `warning`.
- No MX timeout remained in this 10-domain smoke run.

## 5. Baseline comparison

Before:

- MX timeout appeared in bulk across all 10 tested domains.
- DKIM `v=DKIM1; p=` empty was treated as OK for some domains.

After:

- MX is OK for the real domains that publish MX records.
- `example.com` is treated as Null MX when applicable, not as a DNS timeout.
- DKIM `p=` empty is treated as warning.
- Aggregate `ready` is reserved for domains with `Gmail/Yahoo Readiness` equal to `ok`; readiness warnings now produce `needs_attention`.

## 6. Launch decision

- **READY_FOR_DEPLOY_CANDIDATE:** yes
- **Remaining blockers:** none identified in this validation pass.

Recommended next steps:

1. Repeat local test via iPhone.
2. Deploy backend.
3. Deploy frontend.
4. Configure production envs.
5. Test a real domain in production.
6. Configure Search Console/Plausible.

## 7. Commands to reproduce

Backend:

```bash
export ALLOWED_ORIGINS="http://192.168.3.141:3000,http://localhost:3000,http://127.0.0.1:3000"
.venv/bin/uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
nvm use 20
NEXT_PUBLIC_MAILAUTHCHECK_API_URL=http://192.168.3.141:8000 npm run dev -- --hostname 0.0.0.0 --port 3000
```

Technical validation:

```bash
npm run typecheck
npm run build
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```
