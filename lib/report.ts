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

type DeveloperReportContext = {
  toolName: string;
  scope: string;
  statusLabels: Record<AggregateResult["status"], string>;
};

function formatRawRecords(check: CheckResult): string[] {
  if (check.rawRecords.length === 0) {
    return [];
  }

  if (check.checkName === "SPF Lookup Count") {
    const [rootRecord, ...includedRecords] = check.rawRecords;
    const lines = ["  Root SPF record:", `  ${rootRecord}`];

    if (includedRecords.length > 0) {
      lines.push("", "  Included SPF records:");
      for (const record of includedRecords) {
        const separatorIndex = record.indexOf(": ");
        if (separatorIndex > 0) {
          lines.push(
            `  - ${record.slice(0, separatorIndex)}:`,
            `    ${record.slice(separatorIndex + 2)}`,
          );
        } else {
          lines.push(`  - ${record}`);
        }
      }
    } else {
      lines.push("", "  Included SPF records:", "  - No included SPF records were expanded.");
    }

    return lines;
  }

  return ["  Raw records:", ...check.rawRecords.map((record) => `  - ${record}`)];
}

function formatTechnicalDetails(details: string): string[] {
  const [firstLine, ...rest] = details.split("\n");
  return [`  Technical details: ${firstLine}`, ...rest.map((line) => `  ${line}`)];
}

export function buildDeveloperReport(
  result: AggregateResult,
  context?: DeveloperReportContext,
): string {
  const statusLabels = context?.statusLabels ?? {
    ready: statusLabel("ready"),
    needs_attention: statusLabel("needs_attention"),
    not_ready: statusLabel("not_ready"),
    error: statusLabel("error"),
  };

  const lines = [
    ...(context ? [`Tool: ${context.toolName}`, `Scope: ${context.scope}`] : []),
    `Domain: ${result.domain}`,
    `Score: ${result.score}/100`,
    `Status: ${statusLabels[result.status]}`,
    `Summary: ${result.summary}`,
    "",
    "Checks:",
  ];

  for (const check of result.checks) {
    lines.push(`- ${check.checkName}: ${check.summary}`);
    if (check.technicalDetails) {
      lines.push(...formatTechnicalDetails(check.technicalDetails));
    }
    lines.push(...formatRawRecords(check));
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
