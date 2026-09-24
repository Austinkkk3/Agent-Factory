import json
import os
from ibm_watsonx_orchestrate.agent_builder.tools import tool

MOCK_DIR = os.path.join(os.path.dirname(__file__), "../data/mock")

def _load(filename):
    with open(os.path.join(MOCK_DIR, filename)) as f:
        return json.load(f)


@tool
def po_lookup(po_number: str) -> dict:
    """Look up a Purchase Order by PO number. Returns PO header and line items including vendor, quantities, and unit prices."""
    data = _load("purchase_orders.json")
    if po_number not in data:
        return {"error": f"PO {po_number} not found", "po_number": po_number}
    return data[po_number]


@tool
def goods_receipt_lookup(po_number: str) -> dict:
    """Look up goods receipt records for a given PO number. Returns received quantities and receipt dates."""
    data = _load("goods_receipts.json")
    if po_number not in data:
        return {"error": f"No goods receipt found for PO {po_number}", "po_number": po_number}
    return data[po_number]


@tool
def vendor_master_lookup(vendor_id: str) -> dict:
    """Look up vendor master data by vendor ID. Returns vendor name, payment terms, risk flag, and whether bank account was recently changed."""
    data = _load("vendors.json")
    if vendor_id not in data:
        return {"error": f"Vendor {vendor_id} not found", "vendor_id": vendor_id}
    return data[vendor_id]


_seen_invoices: dict = {}

@tool
def duplicate_anomaly_detector(invoice_id: str, vendor_id: str, amount: float) -> dict:
    """Check whether an invoice is a duplicate or statistical anomaly. Returns is_duplicate, is_anomaly, reason, and confidence score."""
    key = f"{invoice_id}:{vendor_id}"

    if key in _seen_invoices:
        prev = _seen_invoices[key]
        if prev["amount"] == amount:
            return {
                "is_duplicate": True,
                "is_anomaly": False,
                "reason": f"Invoice {invoice_id} already processed for vendor {vendor_id} with amount ${amount}",
                "confidence": 1.0
            }

    _seen_invoices[key] = {"amount": amount}

    vendors = _load("vendors.json")
    vendor = vendors.get(vendor_id, {})
    avg = vendor.get("avg_invoice_amount", amount)

    if avg > 0 and amount > avg * 5:
        return {
            "is_duplicate": False,
            "is_anomaly": True,
            "reason": f"Invoice amount ${amount} is {round(amount/avg, 1)}x the vendor average of ${avg}",
            "confidence": 0.92
        }

    return {
        "is_duplicate": False,
        "is_anomaly": False,
        "reason": "No duplicate or anomaly detected",
        "confidence": 0.98
    }


@tool
def policy_tolerance_check(variance_pct: float, amount: float) -> dict:
    """Check whether a price variance falls within AP policy tolerance. Returns disposition (auto_approve, review, or escalate), policy reference, and threshold applied."""
    if variance_pct <= 3.0:
        return {
            "disposition": "auto_approve",
            "policy_ref": "AP-POL-001",
            "threshold_applied": 3.0,
            "reason": f"Variance {variance_pct}% is within auto-approval threshold of 3%"
        }
    elif variance_pct <= 5.0:
        return {
            "disposition": "auto_approve",
            "policy_ref": "AP-POL-001",
            "threshold_applied": 5.0,
            "reason": f"Variance {variance_pct}% is within tolerance ceiling of 5%"
        }
    elif variance_pct <= 10.0 or amount <= 10000:
        return {
            "disposition": "review",
            "policy_ref": "AP-POL-002",
            "threshold_applied": 10.0,
            "reason": f"Variance {variance_pct}% exceeds tolerance — manager review required"
        }
    else:
        return {
            "disposition": "escalate",
            "policy_ref": "AP-POL-003",
            "threshold_applied": 10.0,
            "reason": f"Variance {variance_pct}% on amount ${amount} exceeds escalation threshold"
        }


@tool
def erp_post(invoice_id: str, disposition: str) -> dict:
    """Post an invoice to the ERP system with a given disposition. Returns confirmation number, post timestamp, and status."""
    import uuid, datetime
    if disposition not in ("auto_approve", "approved"):
        return {
            "confirmation_number": None,
            "posted_at": None,
            "status": "held",
            "reason": f"Invoice {invoice_id} held — disposition '{disposition}' requires further action"
        }
    return {
        "confirmation_number": f"ERP-{str(uuid.uuid4())[:8].upper()}",
        "posted_at": datetime.datetime.utcnow().isoformat() + "Z",
        "status": "posted",
        "invoice_id": invoice_id
    }


@tool
def notify_escalate(case_id: str, reason: str, assignee: str) -> dict:
    """Send a notification or escalation for a case to the specified assignee. Returns notification status, channel, and timestamp."""
    import datetime
    print(f"[NOTIFY] → {assignee} | Case: {case_id} | Reason: {reason}")
    return {
        "notified": True,
        "channel": "email",
        "assignee": assignee,
        "case_id": case_id,
        "reason": reason,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
