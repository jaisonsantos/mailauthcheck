import type { AggregateResult } from "@/lib/checker-types";


const leadCaptureUrl = process.env.NEXT_PUBLIC_LEAD_CAPTURE_URL;
const contactEmail =
  process.env.NEXT_PUBLIC_CONTACT_EMAIL ?? "hello@mailauthcheck.com";

export function buildLeadCaptureUrl(result: AggregateResult) {
  const issueSummary = result.checks
    .filter((check) => check.status !== "ok")
    .map((check) => `${check.checkName}: ${check.summary}`)
    .slice(0, 3)
    .join(" | ");

  if (!leadCaptureUrl) {
    const subject = encodeURIComponent(
      `MailAuthCheck help request for ${result.domain}`,
    );
    const body = encodeURIComponent(
      [
        `Domain: ${result.domain}`,
        `Status: ${result.status}`,
        `Score: ${result.score}/100`,
        issueSummary ? `Main issues: ${issueSummary}` : "Main issues: none listed",
        "",
        "I would like help reviewing SPF, DMARC and MX for this domain.",
      ].join("\n"),
    );

    return `mailto:${contactEmail}?subject=${subject}&body=${body}`;
  }

  const url = new URL(leadCaptureUrl);
  url.searchParams.set("domain", result.domain);
  url.searchParams.set("status", result.status);
  url.searchParams.set("score", String(result.score));
  if (issueSummary) {
    url.searchParams.set("issues", issueSummary);
  }
  return url.toString();
}
