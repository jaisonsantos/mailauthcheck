# 08 — Pages and Content

## Priority order

Launch priority:

1. `/`
2. `/spf-checker`
3. `/dmarc-checker`
4. `/mx-record-checker`
5. `/spf-lookup-counter`

These pages should launch in the first 7 days.

## Page map

| URL | Objective | Search intent | H1 | SEO title | Meta description | Tool input | Expected output | Reuses home logic? | Suggested FAQ | Internal links | CTA |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `/` | General domain email readiness scan | Is my domain ready to send email? | Check if your domain is ready to send email | Free Email Domain Health Check | Check SPF, DMARC, MX and basic sender readiness for your domain. | Domain | Score + SPF/DMARC/MX/SPF lookup/Gmail-Yahoo cards | Yes | What is SPF? What is DMARC? Does this guarantee inbox placement? What does Gmail/Yahoo readiness mean? | All initial tools | Check my domain |
| `/spf-checker` | Validate SPF record | Check my SPF record | SPF Record Checker | Free SPF Record Checker | Find SPF records and common SPF issues for your domain. | Domain | SPF status, raw TXT record, multiple SPF warning | Yes | What is SPF? Can I have multiple SPF records? What does `~all` mean? What does `-all` mean? | DMARC checker, SPF lookup counter | Check SPF |
| `/dmarc-checker` | Validate DMARC record and policy | Check DMARC record | DMARC Record Checker | Free DMARC Record Checker | Check if your domain has a valid DMARC policy. | Domain | DMARC status, policy, raw record, recommended fix | Yes | What is DMARC? What is `p=none`? Should I use quarantine or reject? Does DMARC require SPF or DKIM? | SPF checker, Gmail/Yahoo checker later | Check DMARC |
| `/mx-record-checker` | Validate MX records | MX record checker | MX Record Checker | Free MX Record Checker | Check mail exchange records for your domain. | Domain | MX status, hostnames, priorities | Yes | What is an MX record? Do I need MX records to send email? Why are MX records missing? What are Google Workspace MX records? | SPF checker, DMARC checker | Check MX |
| `/spf-lookup-counter` | Count SPF DNS lookups | SPF too many DNS lookups | SPF Lookup Counter | SPF DNS Lookup Counter | Count SPF DNS lookups and detect the 10-lookup limit. | Domain | Lookup count, status, included mechanisms, warning/error | Yes | Why is there a 10 lookup limit? What counts as an SPF DNS lookup? How do I reduce SPF lookups? What happens if SPF exceeds 10? | SPF checker | Count SPF lookups |
| `/dkim-selector-checker` | Check DKIM by selector | DKIM checker | DKIM Selector Checker | Free DKIM Selector Checker | Check DKIM TXT records by domain and selector. | Domain + selector | DKIM status and raw TXT record | Partially | What is a DKIM selector? Where do I find my selector? What are common Google/Microsoft selectors? | Provider guides | Check DKIM |
| `/gmail-yahoo-sender-requirements-checker` | Check basic readiness for Gmail/Yahoo sender requirements | Gmail Yahoo sender requirements checker | Gmail & Yahoo Sender Requirements Checker | Gmail/Yahoo Sender Requirements Checker | Check basic DNS readiness for Gmail and Yahoo sender requirements. | Domain | Readiness checklist | Yes | What is a bulk sender? Is DMARC required? Is p=none enough? Does this guarantee Gmail delivery? | SPF, DMARC, DKIM pages | Check readiness |
| `/guides/google-workspace-spf-dkim-dmarc` | Setup guide for Google Workspace | Google Workspace SPF DKIM DMARC | Google Workspace SPF, DKIM and DMARC Setup | Google Workspace SPF DKIM DMARC Setup Guide | Simple setup guide for Google Workspace email authentication. | Optional domain | Checklist and links to tools | Partially | What SPF does Google use? How do I enable DKIM? What DMARC policy should I start with? | SPF, DMARC, DKIM tools | Check domain |
| `/guides/microsoft-365-dmarc-setup` | Setup guide for Microsoft 365 | Microsoft 365 DMARC setup | Microsoft 365 DMARC Setup Guide | Microsoft 365 SPF DKIM DMARC Setup Guide | Configure domain authentication for Microsoft 365. | Optional domain | Checklist and links to tools | Partially | What SPF include does Microsoft use? How does DKIM work in Microsoft 365? What DMARC should I use? | SPF, DMARC, DKIM tools | Check domain |
| `/guides/mailchimp-dkim-setup` | Setup guide for Mailchimp | Mailchimp DKIM setup | Mailchimp DKIM and SPF Setup Guide | Mailchimp Domain Authentication Guide | Check Mailchimp SPF, DKIM and DMARC setup. | Optional domain | Checklist and links to tools | Partially | Does Mailchimp need DKIM? Does Mailchimp need SPF? Should I add DMARC? | SPF, DMARC, DKIM tools | Check domain |
| `/guides/brevo-spf-dkim-dmarc` | Setup guide for Brevo | Brevo SPF DKIM DMARC | Brevo SPF, DKIM and DMARC Setup | Brevo Email Authentication Guide | Validate Brevo sender domain authentication. | Optional domain | Checklist and links to tools | Partially | What DNS records does Brevo need? Does Brevo need DMARC? How do I validate setup? | SPF, DMARC, DKIM tools | Check domain |
| `/guides/sendgrid-domain-authentication` | Setup guide for SendGrid | SendGrid domain authentication | SendGrid Domain Authentication Guide | SendGrid SPF DKIM DMARC Setup Guide | Validate SendGrid domain authentication records. | Optional domain | Checklist and links to tools | Partially | What CNAME records does SendGrid use? Does SendGrid need DMARC? How do I test SendGrid authentication? | SPF, DMARC, DKIM tools | Check domain |

## Home layout blocks

1. Hero.
2. Domain input.
3. Result cards.
4. Explanation of checks.
5. Next steps.
6. Assisted setup CTA.
7. Related tools.
8. Guides.
9. FAQ.
10. Footer.

## Microcopy

| Situation | Copy |
|---|---|
| Button | Check my domain |
| Loading | Checking public DNS records... |
| Invalid domain | Enter a valid domain, like example.com. Do not include https:// or email addresses. |
| DNS timeout | DNS lookup took too long. Try again in a moment. |
| No DNS | We could not find DNS records for this domain. |
| Help CTA | Need help fixing this? |
| Developer CTA | Copy technical report |
| Lead CTA | Send this to my developer |
| Disclaimer | This is a DNS/authentication check, not a deliverability guarantee. |

## Content rules

- Put the tool above the fold.
- Keep explanations below the result.
- Use simple language first.
- Hide or collapse technical details.
- Include raw records for technical users.
- Avoid long intros before the tool.
- Avoid claims of guaranteed inbox placement.
