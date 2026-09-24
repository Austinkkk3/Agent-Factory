"""
Trace viewer for AP Invoice Exception Handling system.
Reads trace JSONL files and prints a per-transaction summary table.

Usage:
  python3 observability/trace_viewer.py                     # show today's traces
  python3 observability/trace_viewer.py <trace_id>          # show one transaction
  python3 observability/trace_viewer.py --all               # show all traces
"""
import json
import os
import sys
import glob
import datetime

TRACE_DIR = os.path.join(os.path.dirname(__file__), "../logs/audit")


def load_traces(trace_id=None, date_str=None):
    entries = []
    pattern = os.path.join(TRACE_DIR, "*.jsonl")
    files = sorted(glob.glob(pattern))
    if not files:
        return []
    for filepath in files:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if trace_id and entry.get("invoice_id") != trace_id:
                        continue
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
    return entries


def print_transaction_table(entries):
    if not entries:
        print("\n  No trace entries found.\n")
        return

    # Group by invoice_id
    by_invoice = {}
    for e in entries:
        inv = e.get("invoice_id", "UNKNOWN")
        by_invoice.setdefault(inv, []).append(e)

    for invoice_id, events in by_invoice.items():
        print("\n" + "="*72)
        print(f"  TRACE — Invoice: {invoice_id}")
        print("="*72)
        print(f"  {'#':<3} {'Event Type':<32} {'Agent':<25} {'Tool':<25}")
        print(f"  {'-'*3} {'-'*32} {'-'*25} {'-'*25}")

        total_tokens_in = 0
        total_tokens_out = 0
        total_cost = 0.0
        total_tool_calls = 0

        for i, e in enumerate(events, 1):
            event_type = e.get("event_type", "")[:32]
            agent = e.get("agent", "")[:25]
            tool = e.get("tool") or ""
            tool = tool[:25]
            data = e.get("data", {})

            tokens_in  = data.get("tokens_in", 0)
            tokens_out = data.get("tokens_out", 0)
            cost       = data.get("cost_usd", 0.0)
            latency    = data.get("latency_ms", 0)

            total_tokens_in  += tokens_in
            total_tokens_out += tokens_out
            total_cost       += cost
            if tool:
                total_tool_calls += 1

            row = f"  {i:<3} {event_type:<32} {agent:<25} {tool:<25}"
            if tokens_in or tokens_out:
                row += f"  tok_in={tokens_in} tok_out={tokens_out} {latency}ms ${cost:.5f}"
            print(row)

        print(f"  {'-'*72}")
        print(f"  TOTAL  tokens_in={total_tokens_in}  tokens_out={total_tokens_out}  "
              f"tool_calls={total_tool_calls}  cost=${total_cost:.5f}")
        print("="*72)


def main():
    args = sys.argv[1:]
    trace_id = None

    if args and args[0] != "--all":
        trace_id = args[0]

    entries = load_traces(trace_id=trace_id)
    print_transaction_table(entries)


if __name__ == "__main__":
    main()
