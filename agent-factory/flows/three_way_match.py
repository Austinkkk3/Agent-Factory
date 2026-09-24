"""
Flow: Three-Way Match
Deterministic pipeline — no LLM involved.
Steps:
  1. Look up PO
  2. Look up Goods Receipt
  3. Compute line-item variance %
  4. Apply tolerance policy per line
  5. Return MatchResult
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.ap_tools import po_lookup, goods_receipt_lookup, policy_tolerance_check


def run(validated_invoice: dict) -> dict:
    """
    Perform three-way match: Invoice vs PO vs Goods Receipt.

    Args:
        validated_invoice: output from invoice_intake_validation flow

    Returns:
        MatchResult dict with overall status and per-line variance details
    """
    invoice_id = validated_invoice["invoice_id"]
    po_number = validated_invoice["po_number"]
    invoice_lines = validated_invoice["line_items"]
    invoice_amount = validated_invoice["amount"]

    # Step 1 — PO lookup
    _po_raw = po_lookup(po_number)
    po = _po_raw.content if hasattr(_po_raw, "content") else _po_raw
    if "error" in po:
        return {
            "status": "mismatch",
            "invoice_id": invoice_id,
            "reason": f"PO not found: {po['error']}",
            "block_type": "po_not_found",
            "variance_details": []
        }

    # Step 2 — Goods receipt lookup
    _gr_raw = goods_receipt_lookup(po_number)
    gr = _gr_raw.content if hasattr(_gr_raw, "content") else _gr_raw
    if "error" in gr:
        return {
            "status": "mismatch",
            "invoice_id": invoice_id,
            "reason": f"Goods receipt not found: {gr['error']}",
            "block_type": "gr_not_found",
            "variance_details": []
        }

    # Step 3 — Line-item variance computation
    po_lines = {line["item"]: line for line in po["lines"]}
    gr_lines = {line["item"]: line for line in gr["received_lines"]}

    variance_details = []
    overall_disposition = "auto_approve"

    for inv_line in invoice_lines:
        item = inv_line["item"]
        inv_price = inv_line["unit_price"]
        inv_qty = inv_line["qty"]

        po_line = po_lines.get(item)
        gr_line = gr_lines.get(item)

        if not po_line:
            variance_details.append({
                "item": item,
                "issue": "item_not_on_po",
                "disposition": "escalate",
                "policy_ref": "AP-POL-004"
            })
            overall_disposition = "escalate"
            continue

        if not gr_line:
            variance_details.append({
                "item": item,
                "issue": "no_goods_receipt",
                "disposition": "review",
                "policy_ref": "AP-POL-002"
            })
            if overall_disposition == "auto_approve":
                overall_disposition = "review"
            continue

        # Quantity check
        if inv_qty > gr_line["qty_received"]:
            variance_details.append({
                "item": item,
                "issue": "qty_over_received",
                "invoiced_qty": inv_qty,
                "received_qty": gr_line["qty_received"],
                "disposition": "review",
                "policy_ref": "AP-POL-002"
            })
            if overall_disposition == "auto_approve":
                overall_disposition = "review"
            continue

        # Price variance
        po_price = po_line["unit_price"]
        variance_pct = abs(inv_price - po_price) / po_price * 100 if po_price > 0 else 0

        _tol_raw = policy_tolerance_check(
            variance_pct=round(variance_pct, 2),
            amount=invoice_amount
        )
        tolerance = _tol_raw.content if hasattr(_tol_raw, "content") else _tol_raw

        variance_details.append({
            "item": item,
            "invoiced_price": inv_price,
            "po_price": po_price,
            "variance_pct": round(variance_pct, 2),
            "disposition": tolerance["disposition"],
            "policy_ref": tolerance["policy_ref"],
            "reason": tolerance["reason"]
        })

        # Escalate overall if any line escalates; review if any reviews
        if tolerance["disposition"] == "escalate":
            overall_disposition = "escalate"
        elif tolerance["disposition"] == "review" and overall_disposition == "auto_approve":
            overall_disposition = "review"

    # Step 5 — Determine overall match status
    if overall_disposition == "auto_approve":
        match_status = "matched"
    elif overall_disposition == "review":
        match_status = "tolerance_exception"
    else:
        match_status = "mismatch"

    return {
        "status": match_status,
        "invoice_id": invoice_id,
        "po_number": po_number,
        "invoice_amount": invoice_amount,
        "po_total": po["total"],
        "overall_disposition": overall_disposition,
        "variance_details": variance_details,
        "po": po,
        "goods_receipt": gr
    }


if __name__ == "__main__":
    # Quick smoke test — tolerance exception case
    validated = {
        "invoice_id": "INV-2024-002",
        "vendor_id": "V-002",
        "po_number": "PO-5002",
        "amount": 5400.00,
        "line_items": [{"item": "SKU-B", "qty": 20, "unit_price": 270.00}]
    }
    result = run(validated)
    print(json.dumps(result, indent=2))
