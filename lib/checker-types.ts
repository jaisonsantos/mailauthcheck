export type AggregateStatus = "ready" | "needs_attention" | "not_ready" | "error";
export type CheckStatus = "ok" | "warning" | "missing" | "error";

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
  score: number;
  status: AggregateStatus;
  summary: string;
  checks: CheckResult[];
  nextSteps: string[];
  disclaimer: string;
};

export type CheckListResult = {
  domain: string;
  checks: CheckResult[];
};

export type ErrorResult = {
  error: string;
  message: string;
};
