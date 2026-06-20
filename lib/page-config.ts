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
      summary: "Bulk readiness needs work.",
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
    buttonLabel: "Check bulk readiness",
    intro:
      "Check if your domain meets the basic Gmail and Yahoo bulk sender requirements before your next campaign. Review SPF, DKIM, DMARC, MX, SPF lookups and manual checks like one-click unsubscribe and spam-rate monitoring.",
    previewSummary:
      "Run the checker to see automated DNS signals and manual bulk sender checks in one place.",
    resultsHeading: "Automated DNS signals plus manual bulk checks",
    resultsIntro: "Review the combined check first, then inspect individual cards, confidence and raw DNS records.",
    placeholderResult: homePreview,
    guidePreviews: [
      {
        title: "Mailchimp Gmail compliance guide",
        summary:
          "Planned next: a campaign-focused SPF, DKIM and DMARC checklist for Mailchimp senders.",
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
      { href: "/spf-checker", label: "SPF checker" },
      { href: "/dmarc-checker", label: "DMARC checker" },
      { href: "/mx-record-checker", label: "MX checker" },
      { href: "/spf-lookup-counter", label: "SPF lookup counter" },
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
