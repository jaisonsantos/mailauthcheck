export type AggregateStatus = "ready" | "needs_attention" | "not_ready" | "error";
export type BulkStatus = "ready" | "needs_work" | "not_ready" | "incomplete";
export type CheckStatus = "ok" | "warning" | "missing" | "manual_check" | "unknown" | "error";

export type CheckResult = {
  checkName: string;
  status: CheckStatus;
  severity: "info" | "low" | "medium" | "high";
  summary: string;
  technicalDetails: string | null;
  recommendedFix: string | null;
  rawRecords: string[];
  references: Array<{ label: string; url: string }>;
  confidence: "high" | "medium" | "low";
  canBeFalsePositive: boolean;
};

export type AggregateResult = {
  domain: string;
  mode?: "bulk_sender" | string;
  espProvider?: string | null;
  score: number;
  dnsAuthenticationScore?: number;
  status: AggregateStatus;
  bulkStatus?: BulkStatus;
  summary: string;
  checks: CheckResult[];
  automatedChecks?: CheckResult[];
  manualChecks?: ManualCheckResult[];
  gmailBulkChecklist?: BulkComplianceItem[];
  yahooBulkChecklist?: BulkComplianceItem[];
  nextSteps: string[];
  disclaimer: string;
};

export type ManualCheckResult = {
  checkName: string;
  status: "manual_check" | "unknown";
  summary: string;
  whyItMatters: string;
  howToVerify: string;
  references: Array<{ label: string; url: string }>;
};

export type BulkComplianceItem = {
  item: string;
  provider: "gmail" | "yahoo";
  required: boolean;
  status: CheckStatus;
  automated: boolean;
  explanation: string;
  howToVerify?: string | null;
  sourceUrl?: string | null;
};

export type CheckListResult = {
  domain: string;
  checks: CheckResult[];
};

export type ErrorResult = {
  error: string;
  message: string;
};
