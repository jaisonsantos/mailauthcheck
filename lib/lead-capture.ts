import type { AggregateResult } from "@/lib/checker-types";

const leadCaptureUrl = process.env.NEXT_PUBLIC_LEAD_CAPTURE_URL;
const contactEmail =
  process.env.NEXT_PUBLIC_CONTACT_EMAIL ?? "hello@mailauthcheck.com";

type LeadCaptureContext = {
  buttonLabel: string;
  toolName: string;
  toolPath: string;
};

export function buildLeadCaptureUrl(
  result: AggregateResult,
  espProvider: string | undefined,
  context: LeadCaptureContext,
) {
  const issueSummary = result.checks
    .filter((check) => check.status !== "ok")
    .map((check) => `${check.checkName}: ${check.summary}`)
    .slice(0, 3)
    .join(" | ");

  if (!leadCaptureUrl) {
    return buildMailtoUrl(result, espProvider, context, issueSummary);
  }

  try {
    const url = new URL(leadCaptureUrl);
    url.searchParams.set("domain", result.domain);
    url.searchParams.set("tool", context.toolName);
    url.searchParams.set("page", context.toolPath);
    if (espProvider) {
      url.searchParams.set("espProvider", espProvider);
    }
    url.searchParams.set("status", result.status);
    url.searchParams.set("score", String(result.score));
    url.searchParams.set("cta", context.buttonLabel);
    if (issueSummary) {
      url.searchParams.set("issues", issueSummary);
    }
    return url.toString();
  } catch {
    return buildMailtoUrl(result, espProvider, context, issueSummary);
  }
}

function buildMailtoUrl(
  result: AggregateResult,
  espProvider: string | undefined,
  context: LeadCaptureContext,
  issueSummary: string,
) {
    const subject = encodeURIComponent(
      `MailAuthCheck help request for ${result.domain}`,
    );
    const body = encodeURIComponent(
      [
        `Domain: ${result.domain}`,
        espProvider ? `ESP: ${espProvider}` : "ESP: not specified",
        `Status: ${result.status}`,
        `Score: ${result.score}/100`,
        `Tool: ${context.toolName}`,
        `Page: ${context.toolPath}`,
        issueSummary ? `Main issues: ${issueSummary}` : "Main issues: none listed",
        "",
        "I would like help reviewing SPF, DKIM, DMARC and MX for this domain before bulk sending.",
      ].join("\n"),
    );

    return `mailto:${contactEmail}?subject=${subject}&body=${body}`;
}
