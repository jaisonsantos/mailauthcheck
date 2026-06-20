import type { AggregateResult, CheckResult } from "./checker-types";

export function toneFromStatus(status: CheckResult["status"]): "ok" | "warn" | "error" {
  if (status === "ok") {
    return "ok";
  }

  if (status === "warning" || status === "manual_check" || status === "unknown") {
    return "warn";
  }

  return "error";
}

export function statusLabel(status: AggregateResult["status"]): string {
  switch (status) {
    case "ready":
      return "Ready";
    case "needs_attention":
      return "Needs work";
    case "not_ready":
      return "Not ready";
    default:
      return "Error";
  }
}

export function buildDeveloperReport(result: AggregateResult): string {
  const lines = [
    `Domain: ${result.domain}`,
    `Score: ${result.score}/100`,
    `Status: ${statusLabel(result.status)}`,
    `Summary: ${result.summary}`,
    "",
    "Checks:",
  ];

  for (const check of result.checks) {
    lines.push(`- ${check.checkName}: ${check.summary}`);
    if (check.technicalDetails) {
      lines.push(`  Technical details: ${check.technicalDetails}`);
    }
    if (check.rawRecords.length > 0) {
      lines.push(`  Raw records: ${check.rawRecords.join(" | ")}`);
    }
  }

  if (result.nextSteps.length > 0) {
    lines.push("", "Next steps:");
    for (const step of result.nextSteps) {
      lines.push(`- ${step}`);
    }
  }

  lines.push("", `Disclaimer: ${result.disclaimer}`);

  return lines.join("\n");
}
