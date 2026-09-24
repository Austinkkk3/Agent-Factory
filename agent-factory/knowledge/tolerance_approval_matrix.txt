# Tolerance & Approval Matrix

## Price Variance Thresholds

| Variance % | Invoice Amount | Disposition | Approver |
|------------|---------------|-------------|---------|
| 0 – 3% | Any | auto_approve | System |
| 3.01 – 5% | Any | auto_approve | System |
| 5.01 – 10% | ≤ $10,000 | review | AP Manager |
| 5.01 – 10% | > $10,000 | escalate | VP Finance |
| > 10% | Any | escalate | VP Finance |

## Approval Authority by Amount

| Amount Range | Role Required | HITL Required |
|-------------|---------------|---------------|
| $0 – $5,000 | ap_processor | No |
| $5,001 – $10,000 | ap_manager | No (auto if tolerance met) |
| $10,001 – $50,000 | vp_finance | Yes — mandatory |
| > $50,000 | cfo | Yes — mandatory |

## Fraud Escalation Thresholds

Any invoice with 2+ fraud indicators → mandatory HITL → ap_fraud_analyst + vp_finance

Fraud indicators:
- vendor risk_flag = true
- bank_account_changed = true (within 30 days)
- amount > 5× vendor average
- PO not found
- SKU not on PO
