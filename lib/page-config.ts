import type { AggregateResult } from "@/lib/checker-types";

export type FAQItem = {
  question: string;
  answer: string;
};

export type ToolLink = {
  href: string;
  label: string;
};

export type GuidePreview = {
  title: string;
  summary: string;
};

export type CheckerPageConfig = {
  pathname: string;
  apiPath: string;
  title: string;
  description: string;
  h1: string;
  eyebrow: string;
  buttonLabel: string;
  intro: string;
  previewSummary: string;
  resultsHeading: string;
  resultsIntro: string;
  placeholderResult: AggregateResult;
  guidePreviews: GuidePreview[];
  faqs: FAQItem[];
  relatedTools: ToolLink[];
  reportToolName: string;
  reportScope: string;
  statusLabels: {
    ready: string;
    needs_attention: string;
    not_ready: string;
    error: string;
  };
  showEspSelector: boolean;
};

const bulkStatusLabels: CheckerPageConfig["statusLabels"] = {
  ready: "Ready",
  needs_attention: "Needs review",
  not_ready: "Not ready",
  error: "Error",
};

const spfStatusLabels: CheckerPageConfig["statusLabels"] = {
  ready: "SPF OK",
  needs_attention: "SPF needs review",
  not_ready: "SPF problem",
  error: "SPF problem",
};

const dmarcStatusLabels: CheckerPageConfig["statusLabels"] = {
  ready: "DMARC OK",
  needs_attention: "DMARC needs review",
  not_ready: "DMARC problem",
  error: "DMARC problem",
};

const mxStatusLabels: CheckerPageConfig["statusLabels"] = {
  ready: "MX OK",
  needs_attention: "MX needs review",
  not_ready: "MX problem",
  error: "MX problem",
};

const spfLookupStatusLabels: CheckerPageConfig["statusLabels"] = {
  ready: "Lookup count OK",
  needs_attention: "Lookup count needs review",
  not_ready: "Lookup count problem",
  error: "Lookup count problem",
};

const homePreview: AggregateResult = {
  domain: "example.com",
  score: 78,
  status: "needs_attention",
  summary:
    "example.com has several bulk sender basics in place, but DKIM and manual requirements still need review before a campaign.",
  checks: [
    {
      checkName: "SPF",
      status: "ok",
      severity: "info",
      summary: "Your domain has one SPF record.",
      technicalDetails: "One TXT record starting with v=spf1 was found.",
      recommendedFix: null,
      rawRecords: ["v=spf1 include:_spf.google.com ~all"],
      references: [],
      confidence: "high",
      canBeFalsePositive: false,
    },
    {
      checkName: "DKIM",
      status: "warning",
      severity: "medium",
      summary: "DKIM needs selector confirmation.",
      technicalDetails:
        "Common ESP selectors should be checked, but a missing guessed selector can be a false positive.",
      recommendedFix:
        "Open your ESP domain authentication page and confirm the exact DKIM selector before changing DNS.",
      rawRecords: [],
      references: [],
      confidence: "low",
      canBeFalsePositive: true,
    },
    {
      checkName: "DMARC",
      status: "warning",
      severity: "medium",
      summary: "DMARC is present, but policy is monitoring only.",
      technicalDetails:
        "Policy p=none is minimum/monitoring mode. It does not ask receivers to quarantine or reject failing mail.",
      recommendedFix:
        "Use p=none to monitor first. Move to quarantine or reject only after confirming legitimate senders pass authentication.",
      rawRecords: ["v=DMARC1; p=none; rua=mailto:dmarc@example.com"],
      references: [],
      confidence: "high",
      canBeFalsePositive: false,
    },
    {
      checkName: "MX",
      status: "ok",
      severity: "info",
      summary: "Your domain has MX records.",
      technicalDetails: "2 MX record(s) found.",
      recommendedFix: null,
      rawRecords: ["10 alt1.aspmx.l.google.com", "20 alt2.aspmx.l.google.com"],
      references: [],
      confidence: "high",
      canBeFalsePositive: false,
    },
    {
      checkName: "SPF Lookup Count",
      status: "ok",
      severity: "info",
      summary: "SPF lookup count is within the safe range.",
      technicalDetails: "Estimated DNS lookups: 4.",
      recommendedFix: null,
      rawRecords: ["v=spf1 include:_spf.google.com ~all"],
      references: [],
      confidence: "medium",
      canBeFalsePositive: false,
    },
    {
      checkName: "Gmail/Yahoo Readiness",
      status: "warning",
      severity: "medium",
      summary:       "Bulk readiness needs review.",
      technicalDetails:
        "Automated DNS signals are only part of bulk readiness. One-click unsubscribe, spam rate and alignment still need manual review.",
      recommendedFix:
        "Confirm DKIM, review one-click unsubscribe in your ESP and check spam rate in Postmaster/provider tools.",
      rawRecords: [],
      references: [],
      confidence: "high",
      canBeFalsePositive: false,
    },
  ],
  nextSteps: [
    "Confirm DKIM in your ESP domain authentication screen before your next campaign.",
    "Keep exactly one SPF record and avoid adding duplicate SPF TXT records.",
    "Review one-click unsubscribe and spam-rate monitoring outside DNS.",
  ],
  disclaimer:
    "This tool checks public DNS records and known bulk sender readiness signals. It does not guarantee inbox placement, campaign performance, sender reputation or provider acceptance.",
};

const spfPreview: AggregateResult = {
  domain: "example.com",
  score: 68,
  status: "needs_attention",
  summary:
    "example.com has SPF in place, but the policy still needs review before you treat it as clean.",
  checks: homePreview.checks.filter(
    (check) => check.checkName === "SPF" || check.checkName === "SPF Lookup Count",
  ),
  nextSteps: [
    "Keep exactly one SPF record for the domain.",
    "Review includes and other mechanisms if the SPF lookup count gets close to the limit.",
    "Send the raw SPF policy to your developer before making DNS changes.",
  ],
  disclaimer: homePreview.disclaimer,
};

const dmarcPreview: AggregateResult = {
  domain: "example.com",
  score: 68,
  status: "needs_attention",
  summary:
    "example.com publishes DMARC, but the policy is still in monitoring mode.",
  checks: homePreview.checks.filter((check) => check.checkName === "DMARC"),
  nextSteps: [
    "Confirm legitimate senders pass authentication before tightening DMARC enforcement.",
    "Use monitoring first, then move to quarantine or reject when safe.",
  ],
  disclaimer: homePreview.disclaimer,
};

const mxPreview: AggregateResult = {
  domain: "example.com",
  score: 100,
  status: "ready",
  summary:
    "example.com shows MX coverage in this preview, so incoming mail routing looks available.",
  checks: homePreview.checks.filter((check) => check.checkName === "MX"),
  nextSteps: [
    "Confirm the MX hosts match your current email provider.",
    "Review priorities before changing mail providers or DNS zones.",
  ],
  disclaimer: homePreview.disclaimer,
};

const spfLookupPreview: AggregateResult = {
  domain: "example.com",
  score: 68,
  status: "needs_attention",
  summary:
    "example.com is still within the SPF lookup limit, but the policy should stay deliberately small.",
  checks: homePreview.checks.filter(
    (check) => check.checkName === "SPF" || check.checkName === "SPF Lookup Count",
  ),
  nextSteps: [
    "Remove unused senders before adding more SPF includes.",
    "Review lookup-heavy SPF policies before they cross the 10-lookup limit.",
  ],
  disclaimer: homePreview.disclaimer,
};

export const checkerPages: Record<string, CheckerPageConfig> = {
  home: {
    pathname: "/",
    apiPath: "/api/check-domain",
    title: "Bulk Email Readiness Checker",
    description:
      "Check SPF, DKIM, DMARC, MX, SPF lookups and manual Gmail/Yahoo bulk sender requirements.",
    h1: "Bulk Email Readiness Checker",
    eyebrow: "Gmail/Yahoo bulk sender readiness",
    buttonLabel: "Check readiness",
    intro:
      "Check if your domain meets the basic Gmail and Yahoo bulk sender requirements before your next campaign. Review SPF, DKIM, DMARC, MX, SPF lookups and manual checks like one-click unsubscribe and spam-rate monitoring.",
    previewSummary:
      "Run the checker to see automated DNS signals and manual bulk sender checks in one place.",
    resultsHeading: "Automated DNS signals plus manual bulk checks",
    resultsIntro: "Review the combined check first, then inspect individual cards, confidence and raw DNS records.",
    placeholderResult: homePreview,
    reportToolName: "Bulk Email Readiness Checker",
    reportScope: "Bulk sender readiness check based on public DNS plus manual checklist items.",
    statusLabels: bulkStatusLabels,
    showEspSelector: true,
    guidePreviews: [
      {
        title: "Mailchimp Gmail compliance guide",
        summary:
          "A campaign-focused SPF, DKIM and DMARC checklist for Mailchimp senders.",
      },
      {
        title: "Google Postmaster Tools guide",
        summary:
          "Planned next: a practical guide to reviewing spam rate and compliance status outside DNS.",
      },
      {
        title: "One-click unsubscribe explainer",
        summary:
          "Planned next: a plain-English guide to what can and cannot be checked from DNS.",
      },
    ],
    faqs: [
      {
        question: "What is a bulk sender?",
        answer:
          "For Gmail, a bulk sender is a sender that sends about 5,000 or more messages to personal Gmail accounts in a 24-hour period.",
      },
      {
        question: "Is DMARC p=none enough?",
        answer:
          "p=none is minimum/monitoring mode for bulk sender requirements, but it does not enforce quarantine or rejection.",
      },
      {
        question: "Does this guarantee inbox placement?",
        answer:
          "No. MailAuthCheck checks public DNS and known readiness signals, but it cannot guarantee inbox placement or campaign performance.",
      },
      {
        question: "What cannot be checked from DNS?",
        answer:
          "One-click unsubscribe, spam rate, From alignment and message formatting usually need ESP settings, message headers or Postmaster/provider tools.",
      },
    ],
    relatedTools: [
      { href: "/bulk-email-readiness-checker", label: "Bulk readiness" },
      { href: "/gmail-bulk-sender-requirements", label: "Gmail requirements" },
      { href: "/dmarc-policy-bulk-email", label: "DMARC policy" },
      { href: "/guides/mailchimp-gmail-compliance", label: "Mailchimp guide" },
      { href: "/spf-checker", label: "SPF checker" },
    ],
  },
  bulkReadiness: {
    pathname: "/bulk-email-readiness-checker",
    apiPath: "/api/check-domain",
    title: "Free Bulk Email Readiness Checker",
    description:
      "Check whether your domain has the basic DNS signals expected before bulk sending to Gmail and Yahoo.",
    h1: "Bulk Email Readiness Checker",
    eyebrow: "Bulk sender DNS readiness",
    buttonLabel: "Check readiness",
    intro:
      "Run a focused bulk sender readiness check before a newsletter, campaign or automation. Review SPF, DKIM selector signals, DMARC, MX, SPF lookups and manual requirements that DNS cannot confirm.",
    previewSummary:
      "Run the checker to separate automated DNS checks from manual bulk sender requirements.",
    resultsHeading: "Bulk sender readiness signals",
    resultsIntro:
      "Use the DNS Authentication Score first, then review manual checks before sending campaigns.",
    placeholderResult: homePreview,
    reportToolName: "Bulk Email Readiness Checker",
    reportScope: "Bulk sender readiness check based on public DNS plus manual checklist items.",
    statusLabels: bulkStatusLabels,
    showEspSelector: true,
    guidePreviews: [
      {
        title: "Mailchimp Gmail compliance guide",
        summary:
          "Practical setup guidance for Mailchimp domains sending to Gmail recipients.",
      },
      {
        title: "One-click unsubscribe",
        summary:
          "Planned next: how to verify unsubscribe support in campaign tools and message headers.",
      },
    ],
    faqs: [
      {
        question: "What does this checker verify automatically?",
        answer:
          "It checks public DNS signals such as SPF, DKIM selectors, DMARC, MX and SPF lookup count.",
      },
      {
        question: "What still needs manual review?",
        answer:
          "One-click unsubscribe, spam rate, From alignment and message formatting usually require ESP dashboards or message headers.",
      },
      {
        question: "Does this guarantee Gmail delivery?",
        answer:
          "No. It checks readiness signals, not inbox placement, reputation or campaign performance.",
      },
    ],
    relatedTools: [
      { href: "/gmail-bulk-sender-requirements", label: "Gmail requirements" },
      { href: "/dmarc-policy-bulk-email", label: "DMARC policy" },
      { href: "/guides/mailchimp-gmail-compliance", label: "Mailchimp guide" },
      { href: "/dmarc-checker", label: "DMARC checker" },
      { href: "/spf-checker", label: "SPF checker" },
    ],
  },
  gmailBulkSenderRequirements: {
    pathname: "/gmail-bulk-sender-requirements",
    apiPath: "/api/check-domain",
    title: "Gmail Bulk Sender Requirements Checker",
    description:
      "Review SPF, DKIM, DMARC, unsubscribe and spam-rate readiness for Gmail bulk sender requirements.",
    h1: "Gmail Bulk Sender Requirements Checker",
    eyebrow: "Gmail bulk sender checklist",
    buttonLabel: "Check Gmail readiness",
    intro:
      "Check the DNS signals Gmail expects from bulk senders, then review manual requirements like one-click unsubscribe and spam rate outside DNS.",
    previewSummary:
      "Run the checker to see which Gmail bulk sender requirements are automated DNS checks and which need manual confirmation.",
    resultsHeading: "Gmail readiness checklist",
    resultsIntro:
      "SPF, DKIM and DMARC can be checked from DNS. Spam rate and unsubscribe support need provider or message-level review.",
    placeholderResult: homePreview,
    reportToolName: "Gmail Bulk Sender Requirements Checker",
    reportScope: "Gmail bulk sender readiness check based on public DNS plus manual checklist items.",
    statusLabels: bulkStatusLabels,
    showEspSelector: true,
    guidePreviews: [
      {
        title: "Google Postmaster Tools guide",
        summary:
          "Planned next: how to review spam rate and compliance status in Google's own dashboard.",
      },
      {
        title: "DMARC policy for bulk email",
        summary:
          "When p=none is enough for minimum readiness and when to move toward enforcement.",
      },
    ],
    faqs: [
      {
        question: "Who is a Gmail bulk sender?",
        answer:
          "Gmail describes bulk senders as senders that send about 5,000 or more messages to personal Gmail accounts in a 24-hour period.",
      },
      {
        question: "Does Gmail require DKIM?",
        answer:
          "For bulk senders, Gmail expects SPF, DKIM and DMARC. DKIM selector checks can be uncertain unless the exact selector is known.",
      },
      {
        question: "Is p=none enough for Gmail?",
        answer:
          "A valid DMARC policy can use p=none as minimum/monitoring mode, but it is weaker than quarantine or reject.",
      },
    ],
    relatedTools: [
      { href: "/bulk-email-readiness-checker", label: "Bulk readiness" },
      { href: "/dmarc-policy-bulk-email", label: "DMARC policy" },
      { href: "/guides/mailchimp-gmail-compliance", label: "Mailchimp guide" },
      { href: "/dmarc-checker", label: "DMARC checker" },
      { href: "/spf-checker", label: "SPF checker" },
    ],
  },
  dmarcPolicyBulkEmail: {
    pathname: "/dmarc-policy-bulk-email",
    apiPath: "/api/dmarc",
    title: "DMARC Policy for Bulk Email",
    description:
      "Understand p=none, quarantine and reject for Gmail and Yahoo bulk sender readiness.",
    h1: "DMARC Policy for Bulk Email",
    eyebrow: "DMARC policy guidance",
    buttonLabel: "Check DMARC policy",
    intro:
      "Review your domain's DMARC policy and understand what p=none, quarantine and reject mean before bulk campaigns to Gmail and Yahoo recipients.",
    previewSummary:
      "Run the checker to see the current DMARC policy, then use the explanation below to decide whether monitoring or stronger enforcement is the right next step.",
    resultsHeading: "DMARC policy status and next step",
    resultsIntro:
      "This page stays focused on DMARC policy interpretation for bulk sending. SPF and DKIM still matter, but the main question here is whether your DMARC policy is present and how strong it is.",
    placeholderResult: dmarcPreview,
    reportToolName: "DMARC Policy for Bulk Email",
    reportScope: "DMARC policy check only. This is not a full bulk sender readiness report.",
    statusLabels: dmarcStatusLabels,
    showEspSelector: false,
    guidePreviews: [
      {
        title: "Google Postmaster Tools guide",
        summary:
          "Planned next: review spam rate and reputation signals after DMARC is stable.",
      },
      {
        title: "Mailchimp Gmail compliance guide",
        summary:
          "Use the Mailchimp guide when your campaigns depend on provider-specific DKIM selectors and unsubscribe settings.",
      },
    ],
    faqs: [
      {
        question: "Is p=none enough?",
        answer:
          "For minimum/monitoring mode, yes. It satisfies the basic DMARC requirement for many bulk-sender checks, but it does not tell receivers to quarantine or reject failing mail.",
      },
      {
        question: "When should I move to quarantine or reject?",
        answer:
          "Move only after confirming legitimate senders pass SPF or DKIM alignment. Tightening policy too early can break valid traffic.",
      },
      {
        question: "What is DMARC alignment?",
        answer:
          "Alignment means the authenticated SPF or DKIM domain matches the domain used in the visible From address closely enough for DMARC to pass.",
      },
    ],
    relatedTools: [
      { href: "/gmail-bulk-sender-requirements", label: "Gmail requirements" },
      { href: "/bulk-email-readiness-checker", label: "Bulk readiness" },
      { href: "/dmarc-checker", label: "DMARC checker" },
      { href: "/guides/mailchimp-gmail-compliance", label: "Mailchimp guide" },
    ],
  },
  mailchimpGmailCompliance: {
    pathname: "/guides/mailchimp-gmail-compliance",
    apiPath: "/api/check-domain",
    title: "Mailchimp Gmail Compliance Guide",
    description:
      "Check SPF, DKIM, DMARC and manual Gmail bulk sender requirements for Mailchimp campaigns.",
    h1: "Mailchimp Gmail Compliance Guide",
    eyebrow: "Mailchimp setup guide",
    buttonLabel: "Check Mailchimp setup",
    intro:
      "Use this guide when you send campaigns from Mailchimp and want to confirm the domain has the right DNS basics plus the manual Gmail bulk sender checks that Mailchimp alone does not prove.",
    previewSummary:
      "Run the checker with Mailchimp selected to review common DKIM selectors, DMARC policy, SPF, MX and the manual checks that still need confirmation.",
    resultsHeading: "Mailchimp domain readiness",
    resultsIntro:
      "This page reuses the main checker, but frames the result around Mailchimp setup and the Gmail requirements most likely to matter before a campaign.",
    placeholderResult: {
      ...homePreview,
      espProvider: "mailchimp",
      summary:
        "example.com has several Mailchimp-related DNS basics in place, but DKIM selector confirmation and manual Gmail requirements still need review.",
      nextSteps: [
        "Confirm the exact DKIM selector in Mailchimp's domain authentication page before changing DNS.",
        "Keep exactly one SPF record for the domain and avoid duplicate SPF TXT records.",
        "Review one-click unsubscribe behavior and spam-rate monitoring outside DNS before your next campaign.",
      ],
    },
    reportToolName: "Mailchimp Gmail Compliance Guide",
    reportScope: "Mailchimp-oriented bulk sender readiness check based on public DNS plus manual checklist items.",
    statusLabels: bulkStatusLabels,
    showEspSelector: true,
    guidePreviews: [
      {
        title: "DMARC policy for bulk email",
        summary:
          "Use the DMARC policy page when Mailchimp is authenticated but your enforcement mode is still unclear.",
      },
      {
        title: "Google Postmaster Tools guide",
        summary:
          "Planned next: review spam rate and compliance signals after Mailchimp authentication is stable.",
      },
    ],
    faqs: [
      {
        question: "Which DKIM selectors does Mailchimp use?",
        answer:
          "Mailchimp can use provider-specific selectors that vary by account or setup. Common selectors are a useful hint, but the exact selector should be confirmed in Mailchimp's authentication page.",
      },
      {
        question: "Does Mailchimp handle one-click unsubscribe?",
        answer:
          "Mailchimp can help with unsubscribe behavior, but this checker does not verify live message headers or campaign settings automatically. Review the message-level setup before sending.",
      },
      {
        question: "What should I verify in Postmaster Tools?",
        answer:
          "Review spam rate, domain reputation and any compliance warnings after authentication is in place. Those checks sit outside public DNS.",
      },
    ],
    relatedTools: [
      { href: "/bulk-email-readiness-checker", label: "Bulk readiness" },
      { href: "/gmail-bulk-sender-requirements", label: "Gmail requirements" },
      { href: "/dmarc-policy-bulk-email", label: "DMARC policy" },
      { href: "/spf-checker", label: "SPF checker" },
    ],
  },
  spf: {
    pathname: "/spf-checker",
    apiPath: "/api/spf",
    title: "Free SPF Record Checker",
    description:
      "Find SPF records and common SPF issues for your domain.",
    h1: "SPF Record Checker",
    eyebrow: "SPF tool",
    buttonLabel: "Check SPF",
    intro:
      "Check whether your domain publishes one valid SPF record, inspect the raw TXT value and spot common SPF mistakes quickly.",
    previewSummary:
      "Run the SPF checker to inspect the SPF record and the estimated SPF DNS lookup count.",
    resultsHeading: "Focused SPF result",
    resultsIntro: "This page stays focused on SPF policy quality and SPF DNS lookup pressure.",
    placeholderResult: spfPreview,
    reportToolName: "SPF Record Checker",
    reportScope: "SPF-only check. This is not a full bulk sender readiness report.",
    statusLabels: spfStatusLabels,
    showEspSelector: false,
    guidePreviews: [],
    faqs: [
      {
        question: "Can I have multiple SPF records?",
        answer:
          "No. A domain should publish one SPF TXT record. Multiple SPF records can cause authentication failures.",
      },
      {
        question: "What does ~all mean?",
        answer:
          "~all is a soft fail. It is commonly used while a sender is still validating the final SPF policy.",
      },
      {
        question: "What does -all mean?",
        answer:
          "-all is a hard fail. It tells receivers that mail from servers outside the SPF policy should fail SPF.",
      },
    ],
    relatedTools: [
      { href: "/dmarc-checker", label: "DMARC checker" },
      { href: "/spf-lookup-counter", label: "SPF lookup counter" },
    ],
  },
  dmarc: {
    pathname: "/dmarc-checker",
    apiPath: "/api/dmarc",
    title: "Free DMARC Record Checker",
    description: "Check if your domain has a valid DMARC policy.",
    h1: "DMARC Record Checker",
    eyebrow: "DMARC tool",
    buttonLabel: "Check DMARC",
    intro:
      "Validate whether your domain publishes DMARC, see the active policy and understand what to fix next.",
    previewSummary:
      "Run the DMARC checker to inspect the published DMARC policy and the current enforcement mode.",
    resultsHeading: "Focused DMARC result",
    resultsIntro: "This page stays focused on DMARC presence, policy mode and the next enforcement step.",
    placeholderResult: dmarcPreview,
    reportToolName: "DMARC Record Checker",
    reportScope: "DMARC-only check. This is not a full bulk sender readiness report.",
    statusLabels: dmarcStatusLabels,
    showEspSelector: false,
    guidePreviews: [],
    faqs: [
      {
        question: "What is p=none?",
        answer:
          "p=none means monitoring only. It lets you collect reports before moving to stricter DMARC enforcement.",
      },
      {
        question: "Should I use quarantine or reject?",
        answer:
          "Start with p=none, confirm legitimate senders pass authentication, then move to quarantine or reject when safe.",
      },
      {
        question: "Does DMARC require SPF or DKIM?",
        answer:
          "Yes. DMARC depends on underlying authentication such as SPF or DKIM, plus alignment with your domain.",
      },
    ],
    relatedTools: [
      { href: "/spf-checker", label: "SPF checker" },
      { href: "/spf-lookup-counter", label: "SPF lookup counter" },
    ],
  },
  mx: {
    pathname: "/mx-record-checker",
    apiPath: "/api/mx",
    title: "Free MX Record Checker",
    description: "Check mail exchange records for your domain.",
    h1: "MX Record Checker",
    eyebrow: "MX tool",
    buttonLabel: "Check MX",
    intro:
      "Inspect whether your domain receives mail correctly, including MX hosts, priorities and Null MX cases.",
    previewSummary:
      "Run the MX checker to inspect MX records, priorities and Null MX behavior for the domain.",
    resultsHeading: "Focused MX result",
    resultsIntro: "This page stays focused on mail routing, MX hosts and domains that do not accept incoming mail.",
    placeholderResult: mxPreview,
    reportToolName: "MX Record Checker",
    reportScope: "MX-only check. This is not a full bulk sender readiness report.",
    statusLabels: mxStatusLabels,
    showEspSelector: false,
    guidePreviews: [],
    faqs: [
      {
        question: "What is an MX record?",
        answer:
          "An MX record tells other mail systems where to deliver incoming email for your domain.",
      },
      {
        question: "Do I need MX to send email?",
        answer:
          "Not always for sending, but most business domains still need MX when they also receive email.",
      },
      {
        question: "Why are MX records missing?",
        answer:
          "The domain may not be configured to receive mail, or the provider setup may be incomplete.",
      },
    ],
    relatedTools: [
      { href: "/spf-checker", label: "SPF checker" },
      { href: "/dmarc-checker", label: "DMARC checker" },
    ],
  },
  spfLookup: {
    pathname: "/spf-lookup-counter",
    apiPath: "/api/spf",
    title: "SPF DNS Lookup Counter",
    description:
      "Count SPF DNS lookups and detect the 10-lookup limit.",
    h1: "SPF Lookup Counter",
    eyebrow: "SPF lookup tool",
    buttonLabel: "Count SPF lookups",
    intro:
      "Estimate how many DNS lookups your SPF policy triggers and spot records that are close to or above the SPF limit.",
    previewSummary:
      "Run the SPF lookup counter to estimate SPF DNS lookups before the policy reaches the SPF limit.",
    resultsHeading: "Focused SPF lookup result",
    resultsIntro: "This page stays focused on lookup-heavy SPF policies and the 10-lookup limit.",
    placeholderResult: spfLookupPreview,
    reportToolName: "SPF Lookup Counter",
    reportScope: "SPF lookup-count check only. This is not a full bulk sender readiness report.",
    statusLabels: spfLookupStatusLabels,
    showEspSelector: false,
    guidePreviews: [],
    faqs: [
      {
        question: "Why is there a 10 lookup limit?",
        answer:
          "SPF evaluation has a hard limit of 10 DNS lookups to avoid excessive recursion and abuse.",
      },
      {
        question: "What counts as an SPF DNS lookup?",
        answer:
          "Mechanisms like include, a, mx, ptr, exists and redirect can trigger DNS lookups during SPF evaluation.",
      },
      {
        question: "How do I reduce SPF lookups?",
        answer:
          "Remove unused providers, flatten unnecessary includes where appropriate and keep one deliberate SPF policy.",
      },
    ],
    relatedTools: [
      { href: "/spf-checker", label: "SPF checker" },
      { href: "/dmarc-checker", label: "DMARC checker" },
    ],
  },
};
