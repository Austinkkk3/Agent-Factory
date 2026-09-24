"""
Audit logger for AP Invoice Exception Handling system.
Every agent decision and tool call is written to logs/audit/ as structured JSON.
"""
import json
import os
import datetime
import uuid


AUDIT_DIR = os.path.join(os.path.dirname(__file__), "../logs/audit")
os.makedirs(AUDIT_DIR, exist_ok=True)


def log_event(event_type: str, invoice_id: str, agent: str, tool: str = None,
              data: dict = None, policy_refs: list = None):
    """Write a structured audit log entry."""
    entry = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "invoice_id": invoice_id,
        "agent": agent,
        "tool": tool,
        "policy_refs": policy_refs or [],
        "data": data or {}
    }
    filename = f"{datetime.date.today().isoformat()}-audit.jsonl"
    filepath = os.path.join(AUDIT_DIR, filename)
    with open(filepath, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


# Event type constants
GUARDRAIL_PII_REDACTED      = "GUARDRAIL_PII_REDACTED"
GUARDRAIL_INJECTION_BLOCK   = "GUARDRAIL_INJECTION_BLOCK"
GUARDRAIL_SCOPE_BLOCK        = "GUARDRAIL_SCOPE_BLOCK"
GUARDRAIL_OUTPUT_SCHEMA_FAIL = "GUARDRAIL_OUTPUT_SCHEMA_FAIL"
INVOICE_VALIDATED            = "INVOICE_VALIDATED"
INVOICE_BLOCKED_DUPLICATE    = "INVOICE_BLOCKED_DUPLICATE"
THREE_WAY_MATCH_RESULT       = "THREE_WAY_MATCH_RESULT"
TRIAGE_DISPOSITION           = "TRIAGE_DISPOSITION"
FRAUD_ESCALATION             = "FRAUD_ESCALATION"
HITL_TRIGGERED               = "HITL_TRIGGERED"
ERP_POSTED                   = "ERP_POSTED"
INVOICE_HELD                 = "INVOICE_HELD"
