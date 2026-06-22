# 06 — Scoring Model

## Purpose

MailAuthCheck uses a simple score to help users understand the automated DNS authentication state of a domain for bulk sending.

The score must not pretend to be a precise deliverability score.

It is a DNS authentication score, separate from the manual bulk sender checklist.

## Score range

The score ranges from 0 to 100.

Bulk labels:

| Score | Label | Meaning |
|---:|---|---|
| 80–100 | Ready | Automated DNS authentication signals look ready for the next manual review step. |
| 50–79 | Needs review | Some important records exist, but issues need fixing or manual confirmation. |
| 0–49 | Not ready | Important email authentication records are missing, broken or inconclusive. |

## DNS Authentication Score

| Item | Weight |
|---|---:|
| SPF exists and single | 20 |
| SPF lookup count valid | 15 |
| DKIM found for selected/common selector | 25 |
| DMARC exists | 20 |
| DMARC policy quality | 10 |
| MX exists | 10 |

Total automated score: 100.

Manual checks such as one-click unsubscribe, spam rate, From alignment and message formatting must not be scored as verified automatically.

## DMARC policy quality

Suggested policy scoring:

| Policy | Points | Meaning |
|---|---:|---|
| `p=reject` | 10 | Strong enforcement. |
| `p=quarantine` | 8 | Enforcement enabled. |
| `p=none` | 5 | Minimum/monitoring mode, weak enforcement. |
| missing/invalid | 0 | Not ready. |

`p=none` must not be described as absolute non-compliance with Gmail minimum bulk sender requirements. It is acceptable as a minimum monitoring policy, but weaker than quarantine or reject.

## DKIM scoring

| Condition | Points | Meaning |
|---|---:|---|
| DKIM found for selected ESP selector | 25 | Strong selector-based signal. |
| DKIM found for common selector | 20 | Good signal, but selector source should be shown. |
| Selector not found, ESP selected | 8 | Warning; possible false negative. |
| No selector and ESP unknown | 10 | Unknown; not automatically verified. |
| DNS error | 5 | Inconclusive. |
| Malformed DKIM | 0 | Broken. |

## SPF lookup count scoring

| Lookup count | Status | Points |
|---:|---|---:|
| 0–7 | OK | 15 |
| 8–10 | Warning | 8 |
| 11+ | Error | 0 |
| Unknown | Warning | 5 |

## Bulk Readiness Checklist

The bulk readiness checklist is not a mathematical score. It should use explicit item states:

- `pass`;
- `warning`;
- `missing`;
- `manual_check`;
- `not_checked`.

Initial Gmail/Yahoo checklist items:

| Item | Source |
|---|---|
| SPF configured | automated |
| DKIM configured | automated/selector-based |
| DMARC configured | automated |
| DMARC policy visible | automated |
| From alignment | manual or future header analyzer |
| One-click unsubscribe | manual |
| Spam rate under provider threshold | manual via Postmaster/provider tools |
| Message formatting | manual/future header analyzer |
| PTR / forward-reverse DNS | future / not MVP |
| TLS | future / not MVP |

## Ready blockers

A domain must not receive the `Ready` label if any of these are true:

- DMARC is missing.
- SPF has multiple records.
- SPF lookup count is above 10.
- SPF is missing and DKIM is missing or unknown.
- DKIM is malformed.
- DNS errors prevent checking core records.

Optional blocker depending on page context:

- MX missing can block `Ready` when the page evaluates general business email readiness.

## Score disclaimer

Use this disclaimer near the score:

> This score is based on public DNS records and automated bulk sender readiness signals. Manual requirements still need review. It does not guarantee inbox placement, reputation, spam-folder avoidance, campaign performance or provider acceptance.

## Visual display

Recommended UI pattern:

~~~text
72/100 - Needs review

SPF: OK
DMARC: Missing
DKIM: Selector not found
MX: OK
SPF lookups: OK
Manual checks: Review one-click unsubscribe and spam rate

Fix first: Add a DMARC record.
~~~

## Tone rules

Do not use language like:

- “Guaranteed inbox.”
- “Spam proof.”
- “Fully deliverable.”
- “Your emails will reach inbox.”

Use language like:

- “Basic DNS readiness looks good.”
- “Needs review.”
- “This may affect authentication.”
- “This does not guarantee inbox placement.”
- “This manual requirement cannot be verified from DNS.”
