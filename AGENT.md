# AGENT.md — "Agent Factory" Build Brief for IBM Bob

**How to use this file:** This is the build intent for IBM Bob. Read it end‑to‑end, then
scaffold and build the solution described below in **watsonx Orchestrate** using the
**ADK (Agent Development Kit)**. Keep everything in a Git repo. Where exact ADK syntax has
moved, follow current ADK conventions — but do not drop any requirement in §3, §4, §5 or §7;
those are the point of the asset. Ask before inventing external system credentials — use
placeholders (see §3, identity).

---

## 0. Mission — the one story

Build a reusable pursuit asset called **Agent Factory** that proves a single narrative:

> **AI‑assisted agent development with enterprise guardrails — that runs sovereign and hybrid, with no vendor lock‑in.**

We prove it by building **one** real, multi‑agent business process in watsonx Orchestrate with
**production‑grade governance, custom security policy, and observability built in from the
start** — not bolted on. The build is then instrumented so a screen‑recorded demo speaks for
itself. There are **no decks and no slides**: the final packaging is a video + one interactive
HTML talking page (built separately). This file builds the **watsonx Orchestrate half**.

The same scenario is built in parallel with the Claude Agent SDK for a head‑to‑head on
enterprise features and cost — so **keep tool contracts and sample data stable** (see §8).

---

## 1. What to build — scenario  ⟨SWAPPABLE: change only this section to re‑target the asset⟩

**Retail Accounts Payable — Invoice Exception Handling.**

An invoice arrives. Most process straight through; the value (and the risk) is in the
exceptions. The flow:

1. **Intake & validation** of the invoice (deterministic).
2. **Three‑way match** against PO and goods‑receipt (deterministic).
3. On a mismatch, duplicate, or anomaly → **exception & fraud triage** (agentic reasoning).
4. **Approval routing & posting** — auto‑approve within tolerance, human‑in‑the‑loop above a
   threshold, escalate suspected fraud (agentic + policy).

This scenario is chosen deliberately: it is governance‑heavy, mixes deterministic and agentic
work, and maps to a real retail AP pain point. *(To re‑target — e.g. vendor onboarding/KYC or
claims fraud — replace this section and keep the rest.)*

---

## 2. Agent & tool roster

**Explicitly mix deterministic flows with agentic reasoning agents.**

**Agents**
- **AP Orchestrator** — *supervisor / agentic.* Entry point; routes work to collaborators,
  owns the end‑to‑end decision. Uses `collaborators` for multi‑agent orchestration.
- **Invoice Intake & Validation** — *deterministic flow.* Parse, normalize, validate required
  fields, dedupe check.
- **Three‑Way Match** — *deterministic flow.* Invoice ↔ PO ↔ goods receipt; compute variances
  against tolerance rules.
- **Exception & Fraud Triage** — *agentic.* Reasons over mismatches/anomalies, cites the AP
  policy, proposes a disposition with rationale.
- **Approval & Posting Router** — *agentic + policy.* Applies approval matrix, triggers
  human‑in‑the‑loop above threshold, posts or escalates.

**Tools** (build as Python `@tool`, OpenAPI import, or MCP — with mock/sample backends):
PO lookup · Goods‑receipt lookup · Vendor master lookup · Duplicate/anomaly detector ·
Policy & tolerance check · ERP post (mock) · Notify/escalate.

**Knowledge base:** AP policy manual, tolerance/approval matrix, vendor contract terms — so the
triage agent grounds its reasoning and citations.

---

## 3. Non‑negotiables — enterprise guardrails  ⟨THE EMPHASIS⟩

Build these as first‑class, on‑camera capabilities. This is what the asset is *about*.

**Custom security policy**
- Input/output guardrails: PII detection & redaction, prompt‑injection / jailbreak filter,
  off‑scope topic blocking, output validation.
- RBAC on every agent and tool; **deny‑by‑default** tool access.
- Data residency honored; no data egress beyond declared boundaries.
- **Human‑in‑the‑loop** required on approvals above a configurable value threshold and on any
  suspected‑fraud disposition.

**Governance (control plane)**
- Register every agent, model, and tool in the governance/agent directory.
- Define risk and policy, and produce **enforcement tracking / governance proof** — link each
  policy to the evidence that it was enforced at runtime.
- Full **audit log** of every agent decision and tool call.
- **Pre‑deployment evaluation**: accuracy, tool‑call reliability, task completion, cost, and
  safety metrics, with a saved eval set.

**Observability**
- End‑to‑end **trace** of every agent hop and tool call, with **token counts, latency, and
  cost per step**.
- Live metrics view; drift / inefficiency detection.

**Agent identity**
- Each agent gets a first‑class machine identity. **No hardcoded credentials.**
- Secrets and credentials resolved via **HashiCorp Vault** — leave clearly marked
  configuration placeholders (`# VAULT: <path>`); Vault wiring is done by the platform team
  (Kabilan), not invented here.

---

## 4. Instrumentation the demo MUST expose

The demo and the cost story depend on this — emit it as structured data, not just logs.

- **Build cost:** report the tokens / compute Bob itself spent to build this (surface your own
  build token usage).
- **Per‑transaction:** tokens in/out, tool‑call count, latency, and **$ cost per invoice**.
- **Scale model:** parameterize **X transactions/day** → cost per day / month, and at
  **2× / 5× / 10×** volume. Emit as JSON + CSV so the interactive comparison page and cost
  calculator can consume it. **Align field names to the `bob-cost-comparison` tool.**
- Everything above must be **visible on screen / screen‑recordable** — that is the demo.

---

## 5. Sovereign, hybrid, no lock‑in  ⟨must be demonstrable, not just claimed⟩

- Same artifacts deployable to **IBM Cloud, AWS, and on‑prem / sovereign** (air‑gap‑capable).
- **Open standards:** MCP tools, OpenAPI, containerized, **Git‑driven** — portable by design.
- **Model choice is swappable** (watsonx.ai / Granite plus bring‑your‑own model) — show there
  is no lock to a single LLM.

---

## 6. Build sequence for Bob

1. Scaffold the ADK project in a Git repo; start the local dev server.
2. Build the **tools** (Python `@tool` / OpenAPI / MCP) with mock/sample backends.
3. Build the two **deterministic flows** (intake+validation, three‑way match).
4. Define the **agentic agents** and the **AP Orchestrator** supervisor with `collaborators`.
5. Wire **guardrails/controls**, **governance registration**, and **identity/Vault** references.
6. Enable **observability/tracing** and **evaluations**; add the sample eval set.
7. Seed **sample transactions**: clean, tolerance‑exception, duplicate, and suspected‑fraud.
8. Emit the **instrumentation data** (build cost + per‑transaction + scale model) from §4.
9. **Deploy to watsonx Orchestrate** and produce a short demo walk‑path (the click‑order that
   shows a guardrail block, an audit/governance‑proof view, and a full token‑level trace).

Use the current `orchestrate` CLI (agents/tools/knowledge‑bases import, server start, chat,
evaluations, controls). Commit at each step.

---

## 7. Acceptance criteria  ⟨so we don't get it wrong⟩

- [ ] Multi‑agent: a supervisor + **≥ 2 deterministic flows** + agentic collaborators.
- [ ] An input/output that is **blocked by a guardrail**, shown on camera.
- [ ] A **governance‑proof / enforcement‑tracking** view linking a policy to enforcement evidence.
- [ ] A **full trace** of one transaction with per‑step token counts and cost.
- [ ] Agent **identity via Vault** — no hardcoded secrets anywhere in the repo.
- [ ] **Human‑in‑the‑loop** triggered on a high‑value approval.
- [ ] Instrumentation **JSON/CSV emitted** (build cost + per‑txn + scaled cost).
- [ ] Sample data includes a **fraud** case and a **duplicate** case.
- [ ] Demonstrated running on **≥ 2 targets** (proves portability / no lock‑in).

---

## 8. Parallel Claude build — keep it apples‑to‑apples

The same scenario is built with the **Claude Agent SDK** for the head‑to‑head comparison. To
keep the governance / observability / cost comparison fair:
- **Identical tool signatures** and **identical sample transactions** on both sides.
- Same guardrail intents and same per‑transaction cost fields.

*(This half is built separately — this file just keeps Bob's contracts matching it.)*

---

## 9. To slot in later (not Bob's job)

- **Vault** agent‑identity configuration — platform team (Kabilan).
- **Apptio** FinOps — consume the §4 runtime cost data for the enterprise FinOps view.

---

## 10. Out of scope / packaging

No decks, no slides. Final asset = **screen‑recorded demo + one interactive HTML talking page**
(built separately). **This file builds the watsonx Orchestrate half of the Agent Factory.**
