"""
Flow: Invoice Intake & Validation
Deterministic pipeline — no LLM involved.
Steps:
  1. Validate required fields
  2. Run duplicate/anomaly detection
  3. Return ValidatedInvoice or ValidationFailure
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.ap_tools import duplicate_anomaly_detector


def run(invoice: dict) -> dict:
    """
    Validate and deduplicate an incoming invoice.

    Args:
        invoice: dict with keys invoice_id, vendor_id, po_number, amount, line_items

    Returns:
        dict with status ("validated" or "failed") and details
    """
    required_fields = ["invoice_id", "vendor_id", "po_number", "amount", "line_items"]
    missing = [f for f in required_fields if f not in invoice or invoice[f] is None]
    if missing:
        return {
            "status": "failed",
            "reason": f"Missing required fields: {', '.join(missing)}",
            "invoice_id": invoice.get("invoice_id", "UNKNOWN"),
            "block_type": "validation_failure"
        }

    # Basic type checks
    if not isinstance(invoice["amount"], (int, float)) or invoice["amount"] <= 0:
        return {
            "status": "failed",
            "reason": "Invoice amount must be a positive number",
            "invoice_id": invoice["invoice_id"],
            "block_type": "validation_failure"
        }

    if not isinstance(invoice["line_items"], list) or len(invoice["line_items"]) == 0:
        return {
            "status": "failed",
            "reason": "Invoice must have at least one line item",
            "invoice_id": invoice["invoice_id"],
            "block_type": "validation_failure"
        }

    # Duplicate / anomaly check
    dup_raw = duplicate_anomaly_detector(
        invoice_id=invoice["invoice_id"],
        vendor_id=invoice["vendor_id"],
        amount=invoice["amount"]
    )
    dup = dup_raw.content if hasattr(dup_raw, "content") else dup_raw

    if dup["is_duplicate"]:
        return {
            "status": "failed",
            "reason": dup["reason"],
            "invoice_id": invoice["invoice_id"],
            "block_type": "duplicate",
            "duplicate_check": dup
        }

    return {
        "status": "validated",
        "invoice_id": invoice["invoice_id"],
        "vendor_id": invoice["vendor_id"],
        "po_number": invoice["po_number"],
        "amount": invoice["amount"],
        "line_items": invoice["line_items"],
        "anomaly_check": dup
    }


if __name__ == "__main__":
    # Quick smoke test
    test = {
        "invoice_id": "INV-2024-001",
        "vendor_id": "V-001",
        "po_number": "PO-5001",
        "amount": 4800.00,
        "line_items": [{"item": "SKU-A", "qty": 10, "unit_price": 480.00}]
    }
    result = run(test)
    print(json.dumps(result, indent=2))
