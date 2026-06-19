# 04 — API Contract

## Purpose

This document defines the initial API contract for the MVP.

No implementation should be created from this document until an explicit implementation task exists.

## Main endpoint

`POST /api/check-domain` is the primary endpoint of the MVP.

The frontend should use this endpoint for the homepage and initial tool pages.

## Status values

General scan status:

- `ready`
- `needs_attention`
- `not_ready`
- `error`

Check status:

- `ok`
- `warning`
- `missing`
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
  "domain": "example.com"
}
~~~

### Success response

HTTP 200

~~~json
{
  "domain": "example.com",
  "score": 72,
  "status": "needs_attention",
  "summary": "Your domain has SPF and MX records, but DMARC is missing.",
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
  "nextSteps": [
    "Add a DMARC record at _dmarc.example.com.",
    "Keep SPF DNS lookups below 10."
  ],
  "disclaimer": "This is a DNS/authentication check and does not guarantee inbox placement."
}
~~~

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
      "technicalDetails": "Policy p=none does not ask receivers to quarantine or reject failing mail.",
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
- Endpoint responses should be stable enough for multiple SEO pages to reuse.
- More endpoints should not be added unless they support the MVP pages or a documented roadmap phase.
