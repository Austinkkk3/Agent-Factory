# AP Policy Manual — Retail Accounts Payable

## 1. Invoice Acceptance Policy (AP-POL-001)

All invoices must be submitted with the following required fields:
- Invoice ID (unique per vendor)
- Vendor ID (registered in vendor master)
- Purchase Order (PO) number
- Invoice amount (positive numeric value)
- Line items with item code, quantity, and unit price
- Invoice date

Invoices missing any required field will be automatically rejected and returned to the vendor.

## 2. Price Variance Tolerance (AP-POL-002)

Price variances between invoiced unit price and PO unit price are evaluated as follows:

| Variance | Action |
|----------|--------|
| 0% – 3% | Auto-approve — within standard tolerance |
| 3.01% – 5% | Auto-approve — within ceiling tolerance |
| 5.01% – 10% | Manager review required before approval |
| > 10% | Escalation required — VP Finance approval |

For invoices with amount ≤ $10,000, the review threshold is relaxed to 10%.
For invoices with amount > $10,000, the standard thresholds apply regardless of variance.

## 3. Duplicate Invoice Control (AP-POL-003)

An invoice is considered a duplicate if:
- The same Invoice ID has already been processed for the same vendor, OR
- The same amount has been invoiced by the same vendor within 30 days for the same PO

Duplicate invoices must be blocked and logged. No payment shall be issued. The vendor must be notified to resubmit with a corrected invoice ID.

## 4. Fraud Indicators and Escalation (AP-POL-004)

Any invoice exhibiting two or more of the following indicators must be escalated to the Fraud Review team and require VP Finance sign-off before any payment:

- Vendor has an active risk flag in the vendor master
- Vendor bank account has changed within the last 30 days
- Invoice amount is 5× or more above the vendor's historical average
- Invoice references a PO not found in the approved PO register
- Line items contain SKUs not on the original PO

Suspected fraud cases must be assigned to the AP Fraud Analyst role and must not be auto-approved or auto-posted under any circumstances.

## 5. Approval Authority Matrix (AP-POL-005)

| Amount | Approval Authority |
|--------|--------------------|
| ≤ $5,000 | AP Processor (auto-approve if within tolerance) |
| $5,001 – $10,000 | AP Manager |
| $10,001 – $50,000 | VP Finance |
| > $50,000 | CFO + VP Finance |

Human-in-the-loop approval is mandatory for all invoices above $10,000.

## 6. Goods Receipt Matching (AP-POL-006)

Payment shall not be issued for quantities exceeding goods received. If invoiced quantity exceeds received quantity, the invoice must be held for goods receipt reconciliation before payment.

## 7. Audit and Compliance (AP-POL-007)

All invoice decisions — approve, review, escalate, or reject — must be logged with:
- Decision timestamp
- Decision rationale
- Agent or user who made the decision
- Policy reference cited

Audit logs must be retained for a minimum of 7 years.
