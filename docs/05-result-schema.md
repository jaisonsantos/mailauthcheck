# 05 — Result Schema

## Purpose

This document defines the standard result model for MailAuthCheck.

The goal is to make all checks render consistently in the frontend.

## Check schema

~~~json
{
  "checkName": "SPF",
  "status": "ok",
  "severity": "info",
  "summary": "SPF record found.",
  "technicalDetails": "One TXT record starting with v=spf1 was found.",
  "recommendedFix": null,
  "rawRecords": ["v=spf1 include:_spf.google.com ~all"],
  "references": [
    {
      "label": "SPF RFC 7208",
      "url": "https://datatracker.ietf.org/doc/html/rfc7208"
    }
  ],
  "confidence": "high",
  "canBeFalsePositive": false
}
~~~

## Aggregated response schema

~~~json
{
  "domain": "example.com",
  "score": 72,
  "status": "needs_attention",
  "summary": "Your domain has SPF and MX records, but DMARC is missing.",
  "checks": [],
  "nextSteps": [],
  "disclaimer": "This is a DNS/authentication check and does not guarantee inbox placement."
}
~~~

## Field rules

| Field | Rule |
|---|---|
| `checkName` | Human-readable check name. |
| `status` | One of `ok`, `warning`, `missing`, `error`. |
| `severity` | One of `info`, `low`, `medium`, `high`. |
| `summary` | Short plain-English result. |
| `technicalDetails` | Optional technical explanation. |
| `recommendedFix` | Null when no fix is needed. |
| `rawRecords` | Public DNS records used for the result. |
| `references` | Optional external references. |
| `confidence` | One of `high`, `medium`, `low`. |
| `canBeFalsePositive` | Boolean warning for uncertain checks. |

## Confidence rule

Use `high` when:

- the DNS result is direct;
- the record is clearly present or missing;
- no recursive interpretation is needed.

Use `medium` when:

- recursive SPF lookup counting is involved;
- provider-specific behavior may affect interpretation;
- the parser uses simplified MVP rules.

Use `low` when:

- selector guessing is involved;
- DNS response is partial;
- timeout or provider behavior may distort the result.

## canBeFalsePositive rule

Set `canBeFalsePositive` to `true` when:

- DKIM selector was guessed;
- SPF recursive lookup count may be incomplete;
- DNS timeout prevented full analysis;
- the result depends on provider-specific interpretation.

Set `canBeFalsePositive` to `false` when:

- checking direct presence/absence of SPF, DMARC, or MX;
- multiple SPF records are detected;
- DMARC policy is directly parsed.

## Examples

### SPF ok

~~~json
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
~~~

### SPF missing

~~~json
{
  "checkName": "SPF",
  "status": "missing",
  "severity": "high",
  "summary": "No SPF record found.",
  "technicalDetails": "No TXT record starting with v=spf1 was found at the root domain.",
  "recommendedFix": "Add a TXT record starting with v=spf1 that includes your email sending providers.",
  "rawRecords": [],
  "references": [],
  "confidence": "high",
  "canBeFalsePositive": false
}
~~~

### Multiple SPF records

~~~json
{
  "checkName": "SPF",
  "status": "error",
  "severity": "high",
  "summary": "Multiple SPF records found.",
  "technicalDetails": "A domain should publish only one SPF TXT record.",
  "recommendedFix": "Merge all SPF mechanisms into a single SPF TXT record.",
  "rawRecords": [
    "v=spf1 include:_spf.google.com ~all",
    "v=spf1 include:sendgrid.net ~all"
  ],
  "references": [],
  "confidence": "high",
  "canBeFalsePositive": false
}
~~~

### DMARC missing

~~~json
{
  "checkName": "DMARC",
  "status": "missing",
  "severity": "high",
  "summary": "No DMARC record found.",
  "technicalDetails": "No TXT record starting with v=DMARC1 was found at _dmarc.example.com.",
  "recommendedFix": "Add a TXT record at _dmarc.example.com, starting with v=DMARC1; p=none.",
  "rawRecords": [],
  "references": [],
  "confidence": "high",
  "canBeFalsePositive": false
}
~~~

### DMARC p=none

~~~json
{
  "checkName": "DMARC",
  "status": "warning",
  "severity": "medium",
  "summary": "DMARC is present, but policy is monitoring only.",
  "technicalDetails": "Policy p=none does not ask receivers to quarantine or reject failing mail.",
  "recommendedFix": "Use p=none to monitor first. Move to quarantine or reject only after confirming legitimate senders pass authentication.",
  "rawRecords": ["v=DMARC1; p=none; rua=mailto:dmarc@example.com"],
  "references": [],
  "confidence": "high",
  "canBeFalsePositive": false
}
~~~

### MX missing

~~~json
{
  "checkName": "MX",
  "status": "missing",
  "severity": "medium",
  "summary": "No MX records found.",
  "technicalDetails": "No MX records were returned for this domain.",
  "recommendedFix": "Add MX records from your email provider if this domain should receive email.",
  "rawRecords": [],
  "references": [],
  "confidence": "high",
  "canBeFalsePositive": false
}
~~~

### SPF too many DNS lookups

~~~json
{
  "checkName": "SPF Lookup Count",
  "status": "error",
  "severity": "high",
  "summary": "SPF exceeds the 10 DNS lookup limit.",
  "technicalDetails": "Estimated DNS lookups: 12. SPF may return permerror.",
  "recommendedFix": "Remove unused include mechanisms or consolidate email sending providers.",
  "rawRecords": ["v=spf1 include:a.com include:b.com include:c.com include:d.com ~all"],
  "references": [],
  "confidence": "medium",
  "canBeFalsePositive": true
}
~~~
