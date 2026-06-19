import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  CircleHelp,
  Copy,
  MailCheck,
  ShieldCheck,
  Wrench,
  XCircle,
} from "lucide-react";

const checks = [
  {
    title: "SPF record",
    status: "Ready",
    tone: "ok",
    summary: "One SPF record was found for this domain.",
    detail: "v=spf1 include:_spf.google.com ~all",
  },
  {
    title: "DMARC record",
    status: "Needs attention",
    tone: "warn",
    summary: "DMARC exists, but the current policy is monitoring only.",
    detail: "v=DMARC1; p=none; rua=mailto:dmarc@example.com",
  },
  {
    title: "MX records",
    status: "Ready",
    tone: "ok",
    summary: "Mail exchange records are present.",
    detail: "10 alt1.aspmx.l.google.com",
  },
  {
    title: "SPF lookup count",
    status: "Ready",
    tone: "ok",
    summary: "Estimated DNS lookups are below the SPF limit.",
    detail: "Estimated count: 4 of 10",
  },
  {
    title: "Gmail/Yahoo readiness",
    status: "Partial",
    tone: "warn",
    summary: "The basics are close, but DMARC policy should be reviewed.",
    detail: "Basic readiness only. This is not a deliverability guarantee.",
  },
];

const nextSteps = [
  "Review the DMARC policy and decide whether p=none is enough for your current sending setup.",
  "Keep exactly one SPF record and avoid adding duplicate SPF TXT records.",
  "Send the technical details to your developer or DNS provider before changing records.",
];

const faqs = [
  {
    question: "Does this guarantee inbox placement?",
    answer:
      "No. MailAuthCheck only checks public DNS authentication signals and basic sender-readiness indicators.",
  },
  {
    question: "Why does DMARC matter?",
    answer:
      "DMARC tells receiving mail systems how your domain handles authentication failures and is part of modern sender requirements.",
  },
  {
    question: "Can I check any domain?",
    answer:
      "The MVP is planned for domain-only checks such as example.com, not URLs or email addresses.",
  },
];

function StatusIcon({ tone }: { tone: string }) {
  if (tone === "ok") {
    return <CheckCircle2 aria-hidden="true" />;
  }

  if (tone === "error") {
    return <XCircle aria-hidden="true" />;
  }

  return <AlertTriangle aria-hidden="true" />;
}

export default function Home() {
  return (
    <main>
      <section className="hero">
        <div className="shell hero-grid">
          <div className="hero-copy">
            <a className="brand" href="/" aria-label="MailAuthCheck home">
              <MailCheck aria-hidden="true" />
              <span>MailAuthCheck</span>
            </a>
            <p className="eyebrow">Free email domain authentication checker</p>
            <h1>Check if your domain is ready to send email</h1>
            <p className="hero-text">
              Run a quick SPF, DMARC, MX and Gmail/Yahoo readiness check. Get a
              simple explanation of what is missing and what to fix next.
            </p>

            <form className="domain-form" aria-label="Static domain check preview">
              <label htmlFor="domain">Domain</label>
              <div className="input-row">
                <input id="domain" name="domain" placeholder="example.com" />
                <button type="button">
                  <span>Check domain</span>
                  <ArrowRight aria-hidden="true" />
                </button>
              </div>
              <p>This static preview uses mock data. Real DNS checks are planned next.</p>
            </form>
          </div>

          <aside className="score-panel" aria-label="Mock scan result">
            <div className="score-topline">
              <span>Example result</span>
              <strong>Needs attention</strong>
            </div>
            <div className="score-ring" aria-label="Score 78 out of 100">
              <span>78</span>
              <small>/100</small>
            </div>
            <p>
              example.com is close to ready, but DMARC should be reviewed before
              treating the domain as fully prepared.
            </p>
            <div className="score-flags">
              <span>
                <ShieldCheck aria-hidden="true" />
                SPF present
              </span>
              <span>
                <AlertTriangle aria-hidden="true" />
                DMARC p=none
              </span>
            </div>
          </aside>
        </div>
      </section>

      <section className="results-band">
        <div className="shell">
          <div className="section-heading">
            <p className="eyebrow">Mocked result cards</p>
            <h2>One scan, five basic readiness signals</h2>
          </div>

          <div className="cards-grid">
            {checks.map((check) => (
              <article className={`check-card ${check.tone}`} key={check.title}>
                <div className="card-title">
                  <StatusIcon tone={check.tone} />
                  <div>
                    <h3>{check.title}</h3>
                    <span>{check.status}</span>
                  </div>
                </div>
                <p>{check.summary}</p>
                <code>{check.detail}</code>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="next-steps">
        <div className="shell steps-grid">
          <div>
            <p className="eyebrow">Next steps</p>
            <h2>Make the result useful before adding complexity</h2>
            <p>
              The MVP should explain the most important issues first, then show
              raw records for developers and agencies who need the technical view.
            </p>
          </div>
          <ol>
            {nextSteps.map((step) => (
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
              A lightweight CTA can capture setup requests without adding login,
              checkout, dashboards or a database to the MVP.
            </p>
          </div>
          <div className="cta-actions">
            <button type="button">
              <Wrench aria-hidden="true" />
              Need help fixing this?
            </button>
            <button className="secondary" type="button">
              <Copy aria-hidden="true" />
              Send this report to your developer
            </button>
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
            {faqs.map((faq) => (
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
            Disclaimer: This check does not guarantee inbox placement. It only
            verifies public DNS and basic sender-readiness signals.
          </p>
        </div>
      </section>
    </main>
  );
}
