"""
Tracing wrapper for AP Invoice flows.
Instruments flow runs and writes structured trace entries to logs/audit/.
"""
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from governance.audit_logger import log_event

# Approximate cost per token (Granite 3.3 8B on watsonx)
COST_PER_TOKEN_IN  = 0.0000006   # $0.60 / 1M input tokens
COST_PER_TOKEN_OUT = 0.0000012   # $1.20 / 1M output tokens


def trace_flow(flow_name: str, invoice_id: str, fn, *args, **kwargs):
    """Run a flow function and emit a trace entry."""
    start = time.time()
    result = fn(*args, **kwargs)
    latency_ms = int((time.time() - start) * 1000)

    log_event(
        event_type=f"FLOW_{flow_name.upper()}",
        invoice_id=invoice_id,
        agent=flow_name,
        data={
            "latency_ms": latency_ms,
            "tokens_in": 0,   # deterministic flows use 0 LLM tokens
            "tokens_out": 0,
            "cost_usd": 0.0,
            "result_status": result.get("status") if isinstance(result, dict) else "ok"
        }
    )
    return result


def trace_agent_call(agent_name: str, invoice_id: str, tokens_in: int,
                     tokens_out: int, tool: str = None, event_type: str = None,
                     policy_refs: list = None, extra: dict = None):
    """Emit a trace entry for an agent LLM call or tool call."""
    cost = (tokens_in * COST_PER_TOKEN_IN) + (tokens_out * COST_PER_TOKEN_OUT)
    data = {
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": round(cost, 6),
        **(extra or {})
    }
    log_event(
        event_type=event_type or f"AGENT_{agent_name.upper()}",
        invoice_id=invoice_id,
        agent=agent_name,
        tool=tool,
        policy_refs=policy_refs or [],
        data=data
    )
    return data
