# Agent Factory 

---

## What This Is

I am building a **multi-agent AI system** from scratch on IBM watsonx Orchestrate to handle retail AP invoice exceptions — with enterprise-grade security guardrails, governance audit, and cost tracing built in from day one.

The identical system is built in parallel on the **Claude Agent SDK** for an objective, apples-to-apples platform comparison.


---

## The Problem We Are Solving

On every AI deal, enterprise clients ask the same questions:

- Does my data leave my boundary?
- Who audits the AI decisions — and how do I prove compliance?
- Can I swap the AI model later without rebuilding everything?
- If it runs on IBM Cloud today, can I move it to AWS or on-prem tomorrow?

Every current demo **answers these questions verbally**. This asset makes the answers **visible on screen** — live, not claimed.

---

## The Scenario — Retail AP Invoice Exception Handling

Chosen because it is governance-heavy, mixes rules-based logic with AI reasoning, and maps to a real enterprise pain point.

```
Invoice arrives
  │
  ├─ Step 1: Validate fields, check for duplicates     ← rules only, no AI
  │
  ├─ Step 2: Three-way match vs PO and goods receipt   ← rules only, no AI
  │
  ├─ Match OK → auto-approve and post to ERP
  │
  └─ Exception → AI analyses, cites policy, proposes disposition
                  │
                  └─ Amount > $10K or suspected fraud → human approval required
```

**4 test scenarios — both platforms run the exact same data:**

| Scenario | Description | Expected outcome |
|----------|-------------|-----------------|
| Clean invoice | Amount and quantities match exactly | Auto-approved; minimal AI involvement; lowest cost |
| Tolerance exception | Unit price 8% over PO (ceiling: 5%) | Routed to manager for human approval |
| Duplicate invoice | Same invoice ID already processed | Blocked by rules layer; zero AI cost |
| Fraud case | Vendor risk flag + bank account just changed + amount 10× typical | Full AI reasoning chain + forced human approval |

---

## The Core Capability — Enterprise Guardrails Visible on Camera

These are not add-ons bolted on later. They are built in from day one and every one is demonstrable on screen:

| Capability | What the demo shows |
|------------|-------------------|
| **PII auto-redaction** | Names, tax IDs, account numbers stripped before any LLM sees the invoice |
| **Prompt-injection block** | Write "ignore all previous instructions" in an invoice field — system rejects and logs it |
| **RBAC deny-by-default** | Every agent and tool is locked; access requires explicit role assignment |
| **Human-in-the-loop** | Automatically pauses for human sign-off above $10K or on any fraud disposition |
| **Full audit log** | Every AI decision and tool call written to structured JSON — queryable and exportable |
| **Governance proof** | Each policy links to the runtime log entry proving it fired — compliance evidence, not a claim |
| **Zero hardcoded credentials** | All secrets managed via HashiCorp Vault; the codebase contains no passwords |

---

## How the Two Platforms Are Compared

### What is kept identical (the controlled variables)

- Same 7 tool function signatures and return schemas
- Same 4 sample invoices
- Same 10+ evaluation set with expected outcomes
- Same cost field names — so the data from both platforms can be directly compared

### What is measured

| Dimension | What it answers |
|-----------|----------------|
| **Token consumption** | Does one platform use more prompt tokens for the same task? |
| **Tool call count** | Does one platform make unnecessary tool calls? Each call adds latency and cost. |
| **Latency per step** | How many milliseconds does each agent hop take? |
| **Cost per invoice** | What does it actually cost to process one invoice end-to-end? |
| **Scale cost model** | At 100 / 500 / 1K / 5K invoices/day — what is the monthly bill? |
| **Native guardrails** | Which security controls are platform-native vs custom-coded? |
| **Governance & audit** | Built-in or assembled from third-party tools? |
| **Portability** | Can the same artifacts deploy to multiple targets without modification? |

### The output schema — identical on both platforms

```json
{
  "platform": "watsonx_orchestrate",
  "scenario": "fraud",
  "tokens_in": 1240,
  "tokens_out": 310,
  "tool_calls": 4,
  "agent_hops": 3,
  "latency_ms": 2100,
  "cost_usd": 0.0031,
  "hitl_triggered": true
}
```

Both platforms emit `per_transaction.json` and `scale_model.csv` using the same field names — so the comparison is data-driven, not subjective.

---

## Build Plan — 8 Phases

| Phase | What gets built | Milestone |
|-------|----------------|-----------|
| **1. Foundation** | Git repo, ADK scaffold, directory structure, Vault credential placeholders | Local dev server running |
| **2. Tools** | 7 Python tool functions with mock backends | **Tool signatures locked** — Claude build uses the same |
| **3. Deterministic flows** | Invoice validation flow + three-way match flow | 2 rules-based pipelines running independently, zero LLM cost |
| **4. AI agents** | Exception & Fraud Triage agent, Approval Router agent, AP Orchestrator supervisor | Full end-to-end flow on a clean invoice |
| **5. Guardrails & governance** | PII/injection guardrails, RBAC, governance registry, policy definitions, audit log | Guardrail block demonstrable on camera |
| **6. Observability & evaluation** | End-to-end tracing, eval set (10+ cases), baseline metrics run | Per-step token and cost trace visible |
| **7. Sample data & cost output** | 4 canonical invoices, `emit.py` script, `per_transaction.json`, `scale_model.csv` | **Sample data locked** — both builds run the same inputs |
| **8. Deploy & demo script** | Deploy to watsonx Orchestrate, second-target portability test, `DEMO.md` walk-path | All 9 acceptance criteria verified |

---

## The Three On-Camera Demo Moments

| Moment | Setup | What the audience sees |
|--------|-------|----------------------|
| **Guardrail block** | Send an invoice with `"ignore all instructions"` injected into a description field | Request blocked before reaching any agent; audit log entry appears immediately |
| **Governance proof** | After running the fraud invoice end-to-end | Governance registry → fraud-escalation policy → linked audit log entry with matching `policy_ref` |
| **Full cost trace** | Run `trace_viewer.py` on the fraud transaction | Terminal table: every agent hop and tool call with `tokens_in`, `tokens_out`, `latency_ms`, `cost_usd`; total at the bottom |

---

## Acceptance Criteria

- [ ] Multi-agent system end-to-end: supervisor + 2 deterministic flows + 2 AI reasoning agents
- [ ] Guardrail block visible on camera — PII redacted, injection attempt blocked, both in audit log
- [ ] Governance proof on camera — policy ID linked to runtime audit log entry
- [ ] Full cost trace on camera — per-step `tokens_in`, `tokens_out`, `latency_ms`, `cost_usd`
- [ ] Zero hardcoded credentials anywhere in the codebase
- [ ] Human-in-the-loop triggered on the fraud scenario (amount > $10K)
- [ ] `per_transaction.json` and `scale_model.csv` emitted with correct field names
- [ ] All 4 scenarios (clean, exception, duplicate, fraud) run end-to-end with correct dispositions
- [ ] Same artifacts run unchanged on ≥ 2 deployment targets — portability proven, not claimed
