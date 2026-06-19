# 06 — Scoring Model

## Purpose

MailAuthCheck uses a simple score to help users understand the overall state of a domain.

The score must not pretend to be a precise deliverability score.

It is a basic DNS/authentication health score.

## Score range

The score ranges from 0 to 100.

Labels:

| Score | Label | Meaning |
|---:|---|---|
| 80–100 | Ready | Basic DNS/authentication setup looks ready. |
| 50–79 | Needs attention | Some important records exist, but issues need fixing. |
| 0–49 | Not ready | Important email authentication records are missing or broken. |

## Initial MVP weights

| Item | Weight |
|---|---:|
| MX exists | 15 |
| SPF exists and single | 20 |
| SPF lookup count valid | 15 |
| DMARC exists | 25 |
| DMARC policy quality | 10 |
| Gmail/Yahoo basic readiness | 15 |
| DKIM | 0 in MVP |

Total MVP score: 100

## DMARC policy quality

Suggested policy scoring:

| Policy | Points |
|---|---:|
| `p=reject` | 10 |
| `p=quarantine` | 8 |
| `p=none` | 5 |
| missing/invalid | 0 |

## SPF lookup count scoring

| Lookup count | Status | Points |
|---:|---|---:|
| 0–7 | OK | 15 |
| 8–10 | Warning | 8 |
| 11+ | Error | 0 |
| Unknown | Warning | 5 |

## Gmail/Yahoo readiness scoring

| Condition | Status | Points |
|---|---|---:|
| SPF present, DMARC present, SPF lookup count <= 10 | Ready/basic | 15 |
| SPF present, DMARC present, but weak DMARC or lookup warning | Partial | 8 |
| DMARC missing | Not ready for bulk sender requirements | 0 |
| SPF missing and DKIM not checked | Not ready | 0 |

## Ready blockers

A domain must not receive the `Ready` label if any of these are true:

- DMARC is missing.
- SPF has multiple records.
- SPF lookup count is above 10.
- SPF is missing and DKIM is not checked.
- DNS errors prevent checking core records.

Optional blocker depending on page context:

- MX missing can block `Ready` when the page evaluates general business email readiness.

## Score disclaimer

Use this disclaimer near the score:

> This score is based on public DNS records and basic sender-readiness checks. It does not guarantee inbox placement, reputation, spam-folder avoidance or provider-specific acceptance.

## Visual display

Recommended UI pattern:

~~~text
72/100 — Needs attention

SPF: OK
DMARC: Missing
MX: OK
SPF lookups: OK
Gmail/Yahoo readiness: Partial

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
- “Needs attention.”
- “This may affect authentication.”
- “This does not guarantee inbox placement.”
