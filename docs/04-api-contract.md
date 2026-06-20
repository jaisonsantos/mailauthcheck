# 04 — API Contract

## Purpose

This document defines the initial API contract for the MVP.

No implementation should be created from this document until an explicit implementation task exists.

## Main endpoint

`POST /api/check-domain` is the primary aggregate endpoint of the MVP.

The frontend should use this endpoint for the homepage and initial tool pages.

The bulk sender refactor keeps this endpoint to reduce risk. A future `/api/v1/bulk-readiness` endpoint can be considered after the response shape stabilizes.

## Status values

General scan status:

- `ready`
- `needs_work`
- `needs_attention`
- `not_ready`
- `incomplete`
- `error`

Check status:

- `ok`
- `warning`
- `missing`
- `manual_check`
- `unknown`
- `error`

Severity:

- `info`
- `low`
- `medium`
- `high`

Confidence:

- `high`
- `medium`
- `low`

## Endpoint: POST /api/check-domain

### Input

~~~json
{
  "domain": "example.com",
  "mode": "bulk_sender",
  "espProvider": "mailchimp"
}
~~~

`mode` and `espProvider` are optional during the transition. When omitted, the backend should default to the aggregate scanner behavior currently used by the frontend.

### Success response

HTTP 200

~~~json
{
  "domain": "example.com",
  "mode": "bulk_sender",
  "espProvider": "mailchimp",
  "score": 72,
  "dnsAuthenticationScore": 72,
  "status": "needs_work",
  "bulkStatus": "needs_work",
  "summary": "Your domain has SPF and MX records, but DMARC or DKIM still needs attention before bulk sending.",
  "checks": [
    {
      "checkName": "SPF",
      "status": "ok",
      "severity": "info",
      "summary": "Your domain has one SPF record.",
      "technicalDetails": "One TXT record starting with v=spf1 was found.",
      "recommendedFix": null,
      "rawRecords": ["v=spf1 include:_spf.google.com ~all"],
      "references": [],
      "confidence": "high",
      "canBeFalsePositive": false
    }
  ],
  "automatedChecks": [],
  "manualChecks": [
    {
      "checkName": "One-click unsubscribe",
      "status": "manual_check",
      "summary": "This cannot be verified from DNS.",
      "manualVerificationInstructions": "Check your ESP campaign settings and message headers for List-Unsubscribe and one-click unsubscribe support."
    }
  ],
  "gmailBulkChecklist": [],
  "yahooBulkChecklist": [],
  "nextSteps": [
    "Confirm DKIM in your ESP domain authentication screen.",
    "Keep SPF DNS lookups below 10.",
    "Review one-click unsubscribe and spam rate in Postmaster/provider tools."
  ],
  "disclaimer": "This tool checks public DNS records and known bulk sender readiness signals. It does not guarantee inbox placement, campaign performance, sender reputation or provider acceptance."
}
~~~

During migration, `score`, `status` and `checks` may remain for frontend compatibility. New UI should prefer `dnsAuthenticationScore`, `bulkStatus`, `automatedChecks` and `manualChecks` when present.

### Possible HTTP statuses

| Status | Meaning |
|---:|---|
| 200 | Scan completed. |
| 400 | Invalid domain input. |
| 408 | DNS lookup timeout. |
| 429 | Too many requests. |
| 500 | Unexpected server error. |

### Error response example

~~~json
{
  "error": "invalid_domain",
  "message": "Enter a valid domain, like example.com. Do not include https:// or email addresses."
}
~~~

## Endpoint: GET /api/spf

### Purpose

Returns SPF status and SPF lookup count for one domain.

This endpoint can support `/spf-checker` and `/spf-lookup-counter`.

### Input

Query parameter:

~~~text
domain=example.com
~~~

### Success response

HTTP 200

~~~json
{
  "domain": "example.com",
  "checks": [
    {
      "checkName": "SPF",
      "status": "ok",
      "severity": "info",
      "summary": "Your domain has one SPF record.",
      "rawRecords": ["v=spf1 include:_spf.google.com ~all"],
      "confidence": "high",
      "canBeFalsePositive": false
    },
    {
      "checkName": "SPF Lookup Count",
      "status": "ok",
      "severity": "info",
      "summary": "SPF lookup count is within the safe range.",
      "technicalDetails": "Estimated DNS lookups: 3.",
      "confidence": "medium",
      "canBeFalsePositive": true
    }
  ]
}
~~~

## Endpoint: GET /api/dmarc

### Purpose

Returns DMARC status and policy for one domain.

### Input

Query parameter:

~~~text
domain=example.com
~~~

### Success response

HTTP 200

~~~json
{
  "domain": "example.com",
  "checks": [
    {
      "checkName": "DMARC",
      "status": "warning",
      "severity": "medium",
      "summary": "DMARC is present, but policy is monitoring only.",
      "technicalDetails": "Policy p=none is minimum/monitoring mode. It does not ask receivers to quarantine or reject failing mail.",
      "recommendedFix": "Use p=none to monitor first. Move to quarantine or reject only after confirming legitimate senders pass authentication.",
      "rawRecords": ["v=DMARC1; p=none; rua=mailto:dmarc@example.com"],
      "confidence": "high",
      "canBeFalsePositive": false
    }
  ]
}
~~~

## Endpoint: GET /api/mx

### Purpose

Returns MX status and records for one domain.

### Input

Query parameter:

~~~text
domain=example.com
~~~

### Success response

HTTP 200

~~~json
{
  "domain": "example.com",
  "checks": [
    {
      "checkName": "MX",
      "status": "ok",
      "severity": "info",
      "summary": "Your domain has MX records.",
      "technicalDetails": "2 MX records found.",
      "recommendedFix": null,
      "rawRecords": [
        "10 alt1.aspmx.l.google.com",
        "20 alt2.aspmx.l.google.com"
      ],
      "confidence": "high",
      "canBeFalsePositive": false
    }
  ]
}
~~~

## Notes

- The frontend should render cards from the `checks` array.
- The API must not claim inbox placement or deliverability guarantees.
- Manual requirements must not be marked as passed unless the API verifies them.
- DKIM selector misses must use low confidence or `canBeFalsePositive=true` when selectors are guessed.
- DMARC `p=none` must be described as minimum/monitoring mode, not absolute Gmail non-compliance.
- Endpoint responses should be stable enough for multiple SEO pages to reuse.
- More endpoints should not be added unless they support the MVP pages or a documented roadmap phase.
