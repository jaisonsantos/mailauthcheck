# AGENTS.md

This document defines permanent rules for any AI agent, Codex session, automation, or contributor working in this repository.

## Project mission

MailAuthCheck is a free utility site that helps users understand whether a domain is minimally ready to send email correctly.

The product checks public DNS/email authentication signals and explains them clearly:

- SPF;
- DMARC;
- MX;
- SPF DNS lookup count;
- basic Gmail/Yahoo sender readiness.

The primary user question is:

> Is my domain ready to send email?

## Strategic rule: do not turn this into SaaS too early

The project must start as a free, fast, SEO-friendly utility site.

Do not introduce SaaS concepts unless the roadmap explicitly moves to a later phase and the decision log is updated first.

## Allowed MVP scope

Agents may work on documentation, planning, and future implementation tasks related to:

- domain input;
- SPF check;
- DMARC check;
- MX check;
- SPF DNS lookup count;
- basic Gmail/Yahoo readiness;
- simple score;
- simple result cards;
- simple next steps;
- lightweight lead capture;
- CTA for assisted setup;
- SEO pages for the initial hub;
- analytics and Search Console planning;
- simple cache and rate limit planning.

## Prohibited MVP scope

Agents must not add or propose implementation for:

- login;
- dashboard;
- Stripe;
- billing;
- paid plans;
- multi-tenant architecture;
- complex scan history;
- recurring monitoring;
- paid public API;
- complex PDF report generation;
- agency panel;
- database;
- AI in the technical DNS/authentication core;
- blacklist checks;
- BIMI;
- MTA-STS;
- TLS-RPT;
- email header analyzer;
- Kubernetes;
- microservices;
- queue systems;
- enterprise features.

## Preferred stack

The preferred initial implementation direction is:

- Next.js for frontend and SEO pages;
- FastAPI for DNS lookup and parsing endpoints;
- no database in the MVP;
- in-memory TTL cache;
- basic IP/domain rate limiting;
- JSON logs;
- simple, cheap deployment.

Spring Boot may be reconsidered later only if a documented reason appears in `docs/12-decision-log.md`.

## Documentation-first rule

Before changing product scope, architecture, scoring, SEO strategy, monetization, or roadmap:

1. Update the relevant document in `docs/`.
2. Add or update a decision in `docs/12-decision-log.md`.
3. Keep the change small and reviewable.

## No code without explicit task

Do not write code unless the user or project owner creates an explicit implementation task.

This repository may contain documentation first. Do not create:

- Next.js app files;
- FastAPI app files;
- `package.json`;
- `pyproject.toml`;
- `requirements.txt`;
- Dockerfile;
- CI/CD files;
- runtime config files.

Only create implementation files when explicitly requested.

## Keep changes small

Each change should be small, focused, and easy to review.

Prefer one clear documentation change or one implementation task at a time.

Avoid large rewrites unless the task explicitly asks for them.

## Tone and product principles

All user-facing language should be:

- clear;
- practical;
- non-alarmist;
- useful for non-technical users;
- credible for developers and agencies;
- careful not to promise inbox placement.

Never claim that MailAuthCheck guarantees deliverability, inbox placement, reputation improvement, or spam-folder avoidance.

## Pending decisions

If an agent finds uncertainty, mark it as a pending decision instead of inventing scope.

Use this format:

- **Pending decision:** description
- **Why it matters:** impact
- **Recommended owner:** product / technical / SEO
