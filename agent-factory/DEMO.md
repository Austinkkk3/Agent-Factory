# Agent Factory — Demo Walk-Path

**System:** Retail AP Invoice Exception Handling  
**Platform:** watsonx Orchestrate (ADK 2.11)  
**Recording target:** 3 key on-camera moments + end-to-end run

---

## Pre-Demo Setup (do before recording)

```bash
# 1. Navigate to project
cd /Users/austinzhang/Bala/agent-factory

# 2. Set the python alias for this session
alias py=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3

# 3. Activate the watsonx Orchestrate environment
cd /Users/austinzhang/Bala && set -a && source .env && set +a
orchestrate env activate agent-factory --api-key "$WO_API_KEY"

# 4. Clear previous audit logs (fresh run)
rm -f logs/audit/*.jsonl
```

---

## Moment 1 — Guardrail Block (2 min)

**What to show:** Input is blocked before reaching any AI agent. Audit log appears immediately.

```bash
cd /Users/austinzhang/Bala/agent-factory
py data/test/guardrail_tests.py
```

**Expected output — point at each block:**
```
[TEST 1] PII Redaction        → PII Found: True   ✅ PASS
[TEST 2] Prompt Injection     → Blocked: True      ✅ PASS
[TEST 3] Off-Scope Block      → Blocked: True      ✅ PASS
[TEST 4] Clean Invoice Passes → All guards pass    ✅ PASS
```

**Talking point:** "The injection attack never reached the LLM. It was blocked at the guardrail layer and logged. Zero tokens consumed, zero cost."

---

## Moment 2 — Governance Proof (2 min)

**What to show:** Policy ID linked to runtime enforcement evidence.

```bash
# Show the policy registry
cat governance/policies.yaml
```

**Point at policy AP-GOV-004 (Fraud Escalation):**
```yaml
- id: AP-GOV-004
  name: Fraud Escalation Policy
  enforcement_mechanism: exception_fraud_triage counts fraud indicators...
  audit_log_field: fraud_indicators_count
  evidence: triage response includes fraud_indicators list and disposition=fraud_escalate
```

Then run the fraud scenario to generate the evidence:

```bash
py -c "
import json, sys, os
sys.path.insert(0, '.')
from flows.invoice_intake_validation import run as intake
from flows.three_way_match import run as match

with open('data/samples/fraud_invoice.json') as f:
    inv = json.load(f)

i = intake(inv)
m = match(i)
print(json.dumps(m, indent=2))
"
```

**Point at the output:**
- `status: mismatch` — three-way match flagged it
- `variance_details` — shows what triggered the exception
- "This output, combined with vendor V-099's risk_flag and bank_account_changed, triggers AP-GOV-004"

**Talking point:** "Every policy in the registry is linked to the exact runtime evidence that proves it fired. This is governance proof — not a claim, not a dashboard metric. The log entry IS the evidence."

---

## Moment 3 — Full Cost Trace (2 min)

**What to show:** Every agent hop with token counts, latency, and dollar cost per step.

```bash
# Run the full instrumentation emit
py instrumentation/emit.py
```

**Expected output — walk through line by line:**
```
clean              auto_approve   tokens_in=320  tokens_out=95   cost=$0.000306
tolerance_except.  review         tokens_in=890  tokens_out=220  cost=$0.000798
duplicate          blocked        tokens_in=45   tokens_out=11   cost=$0.000040
fraud              fraud_escalate tokens_in=1240 tokens_out=310  cost=$0.001116

Avg cost/txn: $0.000565
Vol/day: 5000 → Monthly: $62.15
```

**Talking points:**
- "The duplicate invoice cost $0.000040 — the rules layer blocked it before any LLM was invoked."
- "The fraud case is the most expensive at $0.001116 — that's the full agent chain: triage + vendor lookup + policy check + escalation."
- "At 5,000 invoices per day — enterprise scale — monthly cost is $62. That's the number your CFO wants to see."

---

## End-to-End Run — All 4 Scenarios (3 min)

**Run each scenario through the evaluation suite:**

```bash
py evals/run_evals.py
```

**Expected:**
```
OVERALL ACCURACY: 44/44 checks passed (100.0%)
```

Walk through each row:
- `eval-001 clean` → auto_approve ✅
- `eval-004 tolerance_exception` → review, manager notified ✅
- `eval-006 duplicate` → blocked at intake, zero AI cost ✅
- `eval-008 fraud` → fraud_escalate, HITL triggered ✅
- `eval-011 injection attack` → blocked by guardrail ✅

---

## Portability Demo (1 min)

**What to show:** Same artifacts, different target.

```bash
# Show the environment list — same code deployed to 2 targets
orchestrate env list
```

Point at `agent-factory` (cloud) and `local` entries.

```bash
# Show the YAML files are platform-agnostic
cat agents/ap_orchestrator.yaml
```

**Talking point:** "The agent definitions are plain YAML. No cloud-specific dependencies. This same file deploys to IBM Cloud, AWS, or an air-gapped on-prem environment. That's what no vendor lock-in looks like in practice."

---

## Acceptance Criteria — Final Check

Run this to verify all 9 criteria:

```bash
cd /Users/austinzhang/Bala/agent-factory

echo "--- 1. Multi-agent end-to-end ---"
orchestrate agents list 2>/dev/null | grep -E "ap_orches|exception|approval"

echo "--- 2. Guardrail block ---"
py data/test/guardrail_tests.py 2>/dev/null | grep "PASS\|FAIL"

echo "--- 3. Eval accuracy ---"
py evals/run_evals.py 2>/dev/null | grep "OVERALL"

echo "--- 4. Cost trace output ---"
ls -la instrumentation/per_transaction.json instrumentation/scale_model.csv

echo "--- 5. Zero hardcoded credentials ---"
grep -r "WO_API_KEY\s*=\s*[a-zA-Z0-9]" agents/ tools/ flows/ guardrails/ 2>/dev/null | grep -v "#" | wc -l

echo "--- 6. Sample data ---"
ls data/samples/

echo "--- 7. Governance registry ---"
cat governance/registry.yaml | grep "name:" | head -15
```

---

## Talking Points Cheat Sheet

| Audience question | Answer |
|------------------|--------|
| "Is the data real?" | "No — synthetic mock data. The AI reasoning, guardrails, costs, and traces are real." |
| "Can this run on-prem?" | "Yes. The YAML artifacts are portable. Same files, different `orchestrate env activate`." |
| "What model is it using?" | "Granite 3.3 8B on watsonx.ai. Swappable — one line change in the YAML." |
| "How do I prove compliance?" | "governance/policies.yaml links each policy to the audit log field that proves it fired." |
| "What does it cost at scale?" | "scale_model.csv — $62/month at 5,000 invoices/day." |
| "What if someone tries to manipulate it?" | "injection_filter blocks it before any token is consumed. Live demo, test 2." |
