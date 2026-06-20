# 15 — Customer Acquisition

This document explains how MailAuthCheck can create possible customer conversations without becoming SaaS in the MVP.

## Decision status

- **accepted:** The MVP is a free utility site with lightweight lead capture and assisted setup CTA.
- **accepted:** There is no Stripe, checkout, billing system, dashboard, account model or database in the MVP.
- **accepted:** Plausible is the preferred MVP analytics tool.
- **accepted:** Lead capture should use an external hosted form URL instead of an internal database-backed form.
- **hypothesis:** Some users with SPF, DMARC, MX or sender-readiness issues will ask for paid setup help.
- **hypothesis:** Assisted setup can be validated manually before any productized paid workflow exists.

## 1. Who are the possible customers?

### Small businesses

- **Main pain:** They rely on business email but do not understand DNS.
- **Why they would use the tool:** To learn why email setup may be incomplete.
- **Probability of paying:** Medium if the result shows a clear issue.
- **What they could buy first:** Assisted Email DNS Setup.

### Freelancers

- **Main pain:** They need to validate client domains quickly.
- **Why they would use the tool:** To check SPF, DMARC, MX and lookup count in one place.
- **Probability of paying:** Low to medium for one-off help; higher if the tool saves client work.
- **What they could buy first:** A review for a difficult client setup.

### Agencies

- **Main pain:** They manage many client domains and need a clear client-friendly report.
- **Why they would use the tool:** To explain DNS issues without sending clients to technical tools.
- **Probability of paying:** Medium if repeated client use appears.
- **What they could buy first:** Manual assisted setup or a later agency pilot, not an MVP dashboard.

### Small e-commerce stores

- **Main pain:** Order, support or marketing emails may not be trusted.
- **Why they would use the tool:** To check whether the domain has basic sender-readiness signals.
- **Probability of paying:** Medium when email affects revenue.
- **What they could buy first:** Basic SPF, DMARC and MX setup help.

### WordPress site owners

- **Main pain:** Contact form, plugin or transactional emails fail or land in spam.
- **Why they would use the tool:** To understand whether the domain DNS setup is missing basics.
- **Probability of paying:** Medium if they do not have a developer.
- **What they could buy first:** Simple review or setup guidance.

### Shopify stores

- **Main pain:** Store notifications and marketing sender setup can be confusing.
- **Why they would use the tool:** To check the sending domain before campaigns or store launch.
- **Probability of paying:** Medium if setup blocks campaigns.
- **What they could buy first:** Basic setup with their DNS and email provider.

### Small SaaS

- **Main pain:** Product, transactional and marketing emails depend on correct domain authentication.
- **Why they would use the tool:** To quickly audit a sending domain during setup.
- **Probability of paying:** Medium, especially for multi-provider setups.
- **What they could buy first:** Multi-provider setup review.

### Marketing teams

- **Main pain:** Campaign tools ask for DNS records and the team needs confidence before sending.
- **Why they would use the tool:** To validate readiness before involving a developer.
- **Probability of paying:** Medium if a campaign is blocked.
- **What they could buy first:** Human review and recommended DNS changes.

### Developers configuring email for clients

- **Main pain:** They need a fast sanity check and shareable explanation.
- **Why they would use the tool:** To confirm records and communicate status to non-technical clients.
- **Probability of paying:** Low for basic help, medium for edge cases or volume later.
- **What they could buy first:** Nothing initially; they may refer non-technical clients.

## 2. Initial funnel

Google, community post, LinkedIn post or referral
-> user enters MailAuthCheck
-> user scans a domain
-> user sees a clear issue or readiness result
-> user receives practical next steps
-> user clicks a CTA
-> user leaves email and domain
-> manual follow-up is sent
-> possible paid assisted setup happens outside the product

The funnel should validate intent, not automate sales.

## 3. MVP CTAs

### Need help fixing this?

- **When to show:** After a result with missing or risky SPF, DMARC, MX or lookup count.
- **User intent:** The user wants someone to fix the issue.
- **Risk:** Can create manual support burden.
- **Analytics event:** `cta_help_clicked`.

### Send this report to your developer

- **When to show:** On every completed scan, especially for non-technical copy.
- **User intent:** The user needs to pass the issue to someone else.
- **Risk:** May imply a report feature if not scoped simply.
- **Analytics event:** `cta_send_to_dev_clicked`.

### Want a human to review your DNS setup?

- **When to show:** When results are mixed, uncertain or marked with `canBeFalsePositive`.
- **User intent:** The user wants confidence from a person.
- **Risk:** Could turn into open-ended consulting.
- **Analytics event:** `cta_help_clicked`.

### Get help setting up SPF, DMARC and MX

- **When to show:** When core records are missing or broken.
- **User intent:** The user wants implementation help, not just explanation.
- **Risk:** Could be interpreted as guaranteed deliverability help.
- **Analytics event:** `setup_request_received` after form submission.

### Join the monitoring waitlist

- **When to show:** Lightly, after a completed scan or in a secondary area.
- **User intent:** The user wants to know if records break later.
- **Risk:** Monitoring pulls the product toward SaaS too early.
- **Analytics event:** `lead_form_submitted` with source `monitoring_waitlist`.

## 4. Initial assisted setup offer

### Offer name

Assisted Email DNS Setup

### What is included

- Review of SPF, DMARC, MX and SPF lookup count for one domain.
- Plain-English issue summary.
- Recommended DNS changes.
- Help coordinating records for common providers when the user supplies access or exact DNS screens.
- One confirmation scan after changes are made.

### What is not included

- Inbox placement guarantee.
- Email reputation repair.
- Blacklist removal.
- Cold email strategy.
- Ongoing monitoring.
- Unlimited revisions.
- Full DNS hosting management.
- Provider migration.
- Custom development.

### Experimental pricing hypotheses

- **hypothesis:** EUR 49 for a simple review.
- **hypothesis:** EUR 99 for basic setup.
- **hypothesis:** EUR 149-EUR 249 for setup involving multiple providers.

These are not final prices. They should only be used to test willingness to pay through manual conversations.

### When to charge

Charge only after the issue is understood, scope is clear and the user agrees manually.

Do not add checkout to the MVP.

### How to avoid infinite support

- Define one domain per request.
- Define one review plus one confirmation scan.
- Ask for provider names before quoting.
- State that extra providers, migrations or unrelated DNS issues are separate.
- Keep all communication tied to SPF, DMARC, MX and sender-readiness basics.

### Inbox disclaimer

Use language like:

> This setup can help fix visible DNS authentication issues, but it cannot guarantee inbox placement, reputation improvement or spam-folder avoidance.

## 5. Lead follow-up messages

### English

Hi,

Thanks for using MailAuthCheck for `example.com`. The scan showed an issue with `[detected issue]`.

I can help review the SPF, DMARC and MX setup and suggest the exact DNS changes to make. This would only cover visible DNS authentication issues and would not guarantee inbox placement.

If you want, send me the DNS provider and email service you use, and I will confirm the next step.

### Spanish

Hola,

Gracias por usar MailAuthCheck para `example.com`. El análisis mostró un problema con `[problema detectado]`.

Puedo ayudarte a revisar la configuración de SPF, DMARC y MX y sugerir los cambios DNS concretos. Esto solo cubre problemas visibles de autenticación DNS y no garantiza llegar a la bandeja de entrada.

Si te interesa, dime qué proveedor DNS y qué servicio de email usas, y confirmo el siguiente paso.

### Portuguese

Olá,

Obrigado por usar o MailAuthCheck para `example.com`. A verificação encontrou um problema com `[problema detectado]`.

Posso ajudar a revisar a configuração de SPF, DMARC e MX e sugerir as alterações exatas de DNS. Isso cobre apenas problemas visíveis de autenticação DNS e não garante chegada na caixa de entrada.

Se fizer sentido, envie o provedor de DNS e o serviço de email que você usa, e eu confirmo o próximo passo.

## 6. Initial distribution

### LinkedIn

- **Approach:** Share the tool as a free utility and ask for feedback from people who configure business email.
- **Short message:** I built a small free checker for SPF, DMARC, MX and basic Gmail/Yahoo sender readiness. If you configure business email, I would appreciate feedback on whether the result is clear.
- **Spam risk:** Low if posted from a personal profile with context.
- **Feedback ask:** Ask whether the result explains the next step clearly.

### Indie Hackers

- **Approach:** Post as a validation story, not a sales launch.
- **Short message:** I am validating a free email authentication checker for small businesses and freelancers. It checks SPF, DMARC, MX and SPF lookup count. I am looking for feedback on clarity and usefulness.
- **Spam risk:** Medium if it sounds promotional.
- **Feedback ask:** Ask what result information would make users trust the tool.

### Reddit

- **Approach:** Use only communities that allow feedback posts.
- **Short message:** I made a free SPF/DMARC/MX checker and would like feedback from people who troubleshoot domain email setup. No signup required.
- **Spam risk:** High in many subreddits.
- **Feedback ask:** Ask moderators first where required and request technical feedback.

### WordPress groups

- **Approach:** Frame around contact form and domain email setup issues.
- **Short message:** I built a free domain email authentication check that can help identify missing SPF, DMARC or MX records. It may help when WordPress emails are not trusted.
- **Spam risk:** Medium.
- **Feedback ask:** Ask whether the explanations are clear for non-technical site owners.

### Shopify groups

- **Approach:** Focus on sender setup before campaigns and store notifications.
- **Short message:** I am testing a free checker for SPF, DMARC, MX and basic sender readiness. It may help Shopify store owners verify their sending domain setup before campaigns.
- **Spam risk:** Medium.
- **Feedback ask:** Ask what provider-specific guidance would be useful later.

### Freelancer communities

- **Approach:** Position as a client communication helper.
- **Short message:** I built a quick email DNS checker that gives a client-friendly SPF, DMARC and MX result. Would this help when explaining setup issues to clients?
- **Spam risk:** Low to medium.
- **Feedback ask:** Ask whether freelancers would send the result to clients.

### Spanish communities

- **Approach:** Ask for feedback in Spanish and mention no signup.
- **Short message:** Estoy probando una herramienta gratuita para revisar SPF, DMARC, MX y preparación básica para enviar emails desde un dominio. Busco feedback sobre claridad y utilidad.
- **Spam risk:** Medium.
- **Feedback ask:** Ask whether the Spanish explanation should be added later.

### Brazilian/LatAm communities

- **Approach:** Use Portuguese or Spanish and focus on practical DNS setup.
- **Short message:** Criei uma ferramenta gratuita para checar SPF, DMARC, MX e preparação básica de envio de email do domínio. Queria feedback sobre clareza para pessoas não técnicas.
- **Spam risk:** Medium.
- **Feedback ask:** Ask what terms are confusing.

### Direct contacts with small agencies

- **Approach:** Send a short personal note to agencies that configure websites or email.
- **Short message:** I am testing a free SPF/DMARC/MX checker for small business domains. Since you work with client sites, would you be open to trying one domain and telling me if the result would help your clients?
- **Spam risk:** Medium if sent cold at scale.
- **Feedback ask:** Ask for one concrete improvement, not a general opinion.

## 7. Commercial metrics

### Events

- `scan_completed`
- `issue_detected`
- `cta_help_clicked`
- `cta_send_to_dev_clicked`
- `lead_form_started`
- `lead_form_submitted`
- `setup_request_received`
- `outbound_reply_sent`
- `setup_paid`

### Validation signals

- 100+ scans.
- 5+ leads.
- 1+ request for help.
- 1 person asking for price.
- 1 paid setup.

These are validation signals, not promises that the product is ready to become SaaS.

## 8. When not to sell

Do not force monetization when:

- The user only wants a technical check.
- The domain has no visible problem.
- The user is an advanced developer and does not need help.
- The assisted setup offer is still unclear.
- The request would become heavy consulting.
- The user asks for deliverability guarantees.
- The request requires blacklist removal, reputation repair, cold email strategy or ongoing monitoring.
