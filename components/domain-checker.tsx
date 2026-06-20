"use client";

import { FormEvent, useMemo, useState, type CSSProperties } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  CircleHelp,
  Copy,
  LoaderCircle,
  MailCheck,
  ShieldCheck,
  Wrench,
  XCircle,
} from "lucide-react";

import type {
  AggregateResult,
  CheckListResult,
  CheckResult,
  ErrorResult,
} from "@/lib/checker-types";
import { trackEvent } from "@/lib/analytics";
import { buildLeadCaptureUrl } from "@/lib/lead-capture";
import type { CheckerPageConfig } from "@/lib/page-config";
import { buildDeveloperReport, statusLabel, toneFromStatus } from "@/lib/report";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MAILAUTHCHECK_API_URL ?? "http://127.0.0.1:8000";

function StatusIcon({ tone }: { tone: "ok" | "warn" | "error" }) {
  if (tone === "ok") {
    return <CheckCircle2 aria-hidden="true" />;
  }

  if (tone === "error") {
    return <XCircle aria-hidden="true" />;
  }

  return <AlertTriangle aria-hidden="true" />;
}

function ScoreFlags({ result }: { result: AggregateResult }) {
  const topFlags = result.checks
    .filter((check) => check.status !== "ok")
    .slice(0, 2)
    .map((check) => `${check.checkName}: ${check.summary}`);

  if (topFlags.length === 0) {
    topFlags.push("Core DNS checks look healthy", "Ready for the next review step");
  }

  return (
    <div className="score-flags">
      {topFlags.map((flag) => (
        <span key={flag}>
          <ShieldCheck aria-hidden="true" />
          {flag}
        </span>
      ))}
    </div>
  );
}

export function DomainChecker({ config }: { config: CheckerPageConfig }) {
  const [domain, setDomain] = useState("");
  const [result, setResult] = useState<AggregateResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copyLabel, setCopyLabel] = useState("Send this report to your developer");

  const scoreTone = useMemo(() => {
    if (!result) {
      return config.placeholderResult.score;
    }
    return Math.max(0, Math.min(100, result.score));
  }, [config.placeholderResult.score, result]);

  const displayResult = result ?? config.placeholderResult;
  const leadCaptureUrl = result ? buildLeadCaptureUrl(result) : null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedDomain = domain.trim().toLowerCase();
    trackEvent("scan_started", {
      tool: config.pathname,
      domain_entered: normalizedDomain.length > 0,
    });
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const requestUrl =
        config.apiPath === "/api/check-domain"
          ? `${API_BASE_URL}${config.apiPath}`
          : `${API_BASE_URL}${config.apiPath}?domain=${encodeURIComponent(domain)}`;

      const response = await fetch(
        requestUrl,
        config.apiPath === "/api/check-domain"
          ? {
              method: "POST",
              headers: {
                "content-type": "application/json",
              },
              body: JSON.stringify({ domain }),
            }
          : undefined,
      );

      const payload = (await response.json()) as
        | AggregateResult
        | CheckListResult
        | ErrorResult;

      if (!response.ok) {
        setResult(null);
        setErrorMessage(
          "message" in payload
            ? payload.message
            : "The DNS check could not be completed right now.",
        );
        trackEvent("scan_failed", {
          tool: config.pathname,
          domain: normalizedDomain || null,
          error:
            "error" in payload && typeof payload.error === "string"
              ? payload.error
              : "request_failed",
          status_code: response.status,
        });
        return;
      }

      if ("score" in payload) {
        const aggregateResult = payload as AggregateResult;
        setResult(aggregateResult);
        trackEvent("scan_completed", {
          tool: config.pathname,
          domain: aggregateResult.domain,
          status: aggregateResult.status,
          score: aggregateResult.score,
        });
      } else {
        const normalizedResult = normalizeCheckListResult(payload as CheckListResult);
        setResult(normalizedResult);
        trackEvent("scan_completed", {
          tool: config.pathname,
          domain: normalizedResult.domain,
          status: normalizedResult.status,
          score: normalizedResult.score,
        });
      }
    } catch {
      setResult(null);
      setErrorMessage(
        "The checker could not reach the API. Make sure the FastAPI service is running.",
      );
      trackEvent("scan_failed", {
        tool: config.pathname,
        domain: normalizedDomain || null,
        error: "network_error",
      });
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCopyReport() {
    if (!result) {
      return;
    }

    await navigator.clipboard.writeText(buildDeveloperReport(result));
    setCopyLabel("Report copied");
    window.setTimeout(() => setCopyLabel("Send this report to your developer"), 1800);
    trackEvent("cta_clicked", {
      tool: config.pathname,
      cta: "send_to_dev",
      domain: result.domain,
      status: result.status,
    });
    trackEvent("cta_send_to_dev_clicked", {
      tool: config.pathname,
      domain: result.domain,
      status: result.status,
    });
  }

  function handleHelpClick() {
    if (!result) {
      return;
    }

    trackEvent("cta_clicked", {
      tool: config.pathname,
      cta: "help",
      domain: result.domain,
      status: result.status,
    });
    trackEvent("cta_help_clicked", {
      tool: config.pathname,
      domain: result.domain,
      status: result.status,
    });
    trackEvent("lead_form_started", {
      tool: config.pathname,
      domain: result.domain,
      status: result.status,
    });
  }

  return (
    <main>
      <section className="hero">
        <div className="shell hero-grid">
          <div className="hero-copy">
            <Link className="brand" href="/" aria-label="MailAuthCheck home">
              <MailCheck aria-hidden="true" />
              <span>MailAuthCheck</span>
            </Link>
            <p className="eyebrow">{config.eyebrow}</p>
            <h1>{config.h1}</h1>
            <p className="hero-text">{config.intro}</p>

            <form className="domain-form" aria-label="Domain checker" onSubmit={handleSubmit}>
              <label htmlFor="domain">Domain</label>
              <div className="input-row">
                <input
                  id="domain"
                  name="domain"
                  placeholder="example.com"
                  value={domain}
                  onChange={(event) => setDomain(event.target.value)}
                />
                <button type="submit" disabled={isLoading}>
                  {isLoading ? <LoaderCircle aria-hidden="true" className="spin" /> : null}
                  <span>{isLoading ? "Checking public DNS records..." : config.buttonLabel}</span>
                  {!isLoading ? <ArrowRight aria-hidden="true" /> : null}
                </button>
              </div>
              <p>
                {errorMessage ??
                  "Enter a domain like example.com. Do not include https:// or email addresses."}
              </p>
            </form>
          </div>

          <aside className="score-panel" aria-label="Scan result">
            <div className="score-topline">
              <span>{result ? result.domain : "Live checker"}</span>
              <strong>{result ? statusLabel(result.status) : "Run a check"}</strong>
            </div>
            <div
              className="score-ring"
              aria-label={`Score ${result ? `${result.score} out of 100` : "not available yet"}`}
              style={
                {
                  "--score-progress": `${scoreTone}%`,
                } as CSSProperties
              }
            >
              <span>{result ? result.score : "?"}</span>
              <small>{result ? "/100" : "score"}</small>
            </div>
            <p>
              {result
                ? result.summary
                : config.previewSummary}
            </p>
            <ScoreFlags result={displayResult} />
          </aside>
        </div>
      </section>

      <section className="results-band">
        <div className="shell">
          <div className="section-heading">
            <p className="eyebrow">Result cards</p>
            <h2>{config.resultsHeading}</h2>
            <p>{config.resultsIntro}</p>
          </div>

          <div className="cards-grid">
            {displayResult.checks.map((check) => {
              const tone = toneFromStatus(check.status);
              return (
                <article className={`check-card ${tone}`} key={check.checkName}>
                  <div className="card-title">
                    <StatusIcon tone={tone} />
                    <div>
                      <h3>{check.checkName}</h3>
                      <span>{check.summary}</span>
                    </div>
                  </div>
                  <p>{check.technicalDetails ?? check.summary}</p>
                  {check.rawRecords.length > 0 ? (
                    <code>{check.rawRecords.join("\n")}</code>
                  ) : (
                    <code>No raw record to show for this check.</code>
                  )}
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="next-steps">
        <div className="shell steps-grid">
          <div>
            <p className="eyebrow">Next steps</p>
            <h2>Fix the most important issues first</h2>
            <p>
              The result starts with plain language, then keeps technical details and raw
              DNS records visible for developers and agencies who need them.
            </p>
          </div>
          <ol>
            {displayResult.nextSteps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      </section>

      <section className="help-band">
        <div className="shell help-grid">
          <div>
            <p className="eyebrow">Assisted setup CTA</p>
            <h2>Need help fixing this?</h2>
            <p>
              The MVP keeps this lightweight. It points users toward manual setup help
              without adding accounts, checkout or a dashboard.
            </p>
          </div>
          <div className="cta-actions">
            {result && leadCaptureUrl ? (
              <a
                href={leadCaptureUrl}
                target="_blank"
                rel="noreferrer"
                onClick={handleHelpClick}
              >
                <Wrench aria-hidden="true" />
                Need help fixing this?
              </a>
            ) : (
              <button type="button" disabled>
                <Wrench aria-hidden="true" />
                Need help fixing this?
              </button>
            )}
            <button className="secondary" type="button" onClick={handleCopyReport}>
              <Copy aria-hidden="true" />
              {copyLabel}
            </button>
          </div>
          <p className="cta-note">
            {result
              ? "This opens a simple external contact form and pre-fills the domain and main issues."
              : "Run a scan first to pre-fill the domain and main issues in the help request."}
          </p>
          <p className="cta-note">
            It can help with visible DNS authentication issues, but it does not guarantee inbox placement.
          </p>
        </div>
      </section>

      <section className="tools-band">
        <div className="shell">
          <div className="section-heading">
            <p className="eyebrow">Related tools</p>
            <h2>Use the focused pages when you need one check at a time</h2>
          </div>
          <div className="link-grid">
            {config.relatedTools.map((tool) => (
              <Link className="tool-link" href={tool.href} key={tool.href}>
                <span>{tool.label}</span>
                <ArrowRight aria-hidden="true" />
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="faq-band">
        <div className="shell">
          <div className="section-heading">
            <p className="eyebrow">FAQ</p>
            <h2>Clear answers for non-technical users</h2>
          </div>
          <div className="faq-list">
            {config.faqs.map((faq) => (
              <article key={faq.question}>
                <CircleHelp aria-hidden="true" />
                <div>
                  <h3>{faq.question}</h3>
                  <p>{faq.answer}</p>
                </div>
              </article>
            ))}
          </div>
          <p className="disclaimer">
            Disclaimer: {displayResult.disclaimer}
          </p>
        </div>
      </section>
    </main>
  );
}

function normalizeCheckListResult(payload: CheckListResult): AggregateResult {
  const derivedStatus = deriveAggregateStatus(payload.checks);
  const score =
    derivedStatus === "ready"
      ? 100
      : derivedStatus === "needs_attention"
        ? 68
        : 20;

  const nextSteps = payload.checks
    .map((check) => check.recommendedFix)
    .filter((value): value is string => Boolean(value));

  return {
    domain: payload.domain,
    score,
    status: derivedStatus,
    summary:
      payload.checks[0]?.summary ??
      "The domain returned a focused result for this checker.",
    checks: payload.checks,
    nextSteps:
      nextSteps.length > 0
        ? Array.from(new Set(nextSteps)).slice(0, 3)
        : ["Review the returned technical details before making DNS changes."],
    disclaimer:
      "This is a DNS/authentication check and does not guarantee inbox placement.",
  };
}

function deriveAggregateStatus(checks: CheckResult[]): AggregateResult["status"] {
  if (checks.some((check) => check.status === "error" || check.status === "missing")) {
    return "not_ready";
  }

  if (checks.some((check) => check.status === "warning")) {
    return "needs_attention";
  }

  return "ready";
}
