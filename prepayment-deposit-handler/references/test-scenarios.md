# Test Scenarios

Use these scenarios for manual QA, automated tests, bookkeeping-system acceptance testing, and staff training.

## Scenario 1: Simple service advance

- Business: עוסק מורשה
- Customer pays: ₪3,000 on 15/03/2026
- Contract: ₪12,000 + 18% מע״מ
- Expected: receipt now, final tax invoice later, deposit applied, balance ₪11,160.

## Scenario 2: VAT-exempt freelancer advance

- Business: עוסק פטור
- Customer pays: ₪500
- Contract: ₪2,500 no VAT
- Expected: receipt only, no tax invoice, balance ₪2,000.

## Scenario 3: Refundable equipment deposit

- Business: עוסק מורשה
- Deposit: ₪1,500
- Equipment returned undamaged
- Expected: receipt on receipt date, refund proof, no revenue merely from deposit.

## Scenario 4: Partial security deposit retained

- Deposit: ₪1,500
- Damage charge: ₪300
- Refund: ₪1,200
- Expected: determine tax treatment for retained ₪300, issue refund proof for ₪1,200.

## Scenario 5: Non-refundable booking fee credited to final invoice

- Booking fee: ₪750
- Final package: ₪5,000 + VAT
- Expected: receipt and tax documentation according to timing, final balance after ₪750 credit is ₪5,150.

## Scenario 6: Booking cancelled by customer

- Fee: ₪750 non-refundable
- Cancellation: 3 days before event
- Expected: verify written terms and consumer rules; if retained, keep tax documentation; if refunded, document refund and correction.

## Scenario 7: Supplier cancels booking

- Fee: ₪750
- Supplier cannot perform
- Expected: refund unless contract/law says otherwise; issue correction if tax invoice exists.

## Scenario 8: Deposit exceeds final invoice

- Deposit: ₪2,000
- Final invoice: ₪1,500 + 18% VAT = ₪1,770
- Expected: apply ₪1,770, refund or credit ₪230.

## Scenario 9: Partial delivery

- Deposit: ₪4,000
- Total contract: ₪10,000 + VAT
- Delivered portion: 40%
- Expected: apply only against delivered/taxable portion where appropriate; keep remaining deposit tracked.

## Scenario 10: Mixed VAT rates

- Line A: ₪1,000 at 18%
- Line B: ₪500 at 0%
- Deposit: ₪300
- Expected: VAT calculated by line; no blended rate without support.

## Scenario 11: Foreign currency deposit

- Deposit: USD 1,000
- Invoice issued in ILS
- Expected: store exchange-rate source, NIS value, currency gain/loss policy.

## Scenario 12: Customer retention

- Contract: ₪80,000 + VAT
- Customer withholds 5%
- Expected: no receipt for withheld money until paid; track retention receivable.

## Scenario 13: Retention released

- Retention: ₪4,000
- Release date: 30/06/2026
- Expected: issue receipt on actual receipt date and reconcile open receivable.

## Scenario 14: VAT-exempt to VAT-registered transition

- Deposit received while עוסק פטור
- Work completed after becoming עוסק מורשה
- Expected: split treatment by dates and obtain accountant review.

## Scenario 15: Customer demands tax invoice from עוסק פטור

- Expected: provide receipt and explanation; do not issue tax invoice.

## Scenario 16: Tax invoice issued by mistake for refundable deposit

- Expected: review validity, issue credit/correction if needed, reclassify deposit liability.

## Scenario 17: Deposit applied twice

- Same deposit ID applied to two invoices
- Expected: block duplicate, reverse incorrect application, reconcile customer card.

## Scenario 18: Bank import duplicated receipt

- Same bank transfer imported twice
- Expected: reverse duplicate receipt and preserve audit trail.

## Scenario 19: Cash deposit

- Amount: ₪8,000
- Expected: verify current cash-law limits, collect payer identity, prefer traceable method if needed.

## Scenario 20: Israel Invoice allocation needed

- Final tax invoice meets current allocation threshold
- Expected: obtain official allocation number through approved channel; store response.

## Scenario 21: Allocation number failure

- Customer tax ID invalid
- Expected: correct data, retry, keep error evidence, do not invent number.

## Scenario 22: Gift card sold

- Customer pays ₪300 for future purchase
- Expected: issue receipt, track liability/credit, issue tax invoice at redemption according to applicable rule.

## Scenario 23: Gift card partially redeemed

- Credit: ₪300
- Purchase: ₪180
- Expected: apply ₪180, leave ₪120 credit balance, document expiry/refund terms.

## Scenario 24: Price reduction after deposit

- Deposit: ₪1,000
- Original quote: ₪5,000 + VAT
- Final price: ₪4,000 + VAT
- Expected: final balance ₪3,720; verify whether prior tax invoice needs correction.

## Scenario 25: Non-profit/Malkar context

- Entity receives deposit for activity
- Expected: validate document type and tax status before applying ordinary VAT-registered workflow.

## Scenario 26: Refund by bank transfer to different account

- Customer requests refund to another person
- Expected: obtain written authorization and anti-fraud approval before refund.

## Scenario 27: Deposit without written terms

- Customer asks for refund after cancellation
- Expected: review consumer law and communications; avoid assuming non-refundable status.

## Scenario 28: Old unclaimed deposit

- Deposit open for 18 months
- Expected: contact customer, document decision, get professional review before clearing.

## Scenario 29: Overpayment kept as credit

- Customer agrees to keep ₪230 for future work
- Expected: written approval, credit balance record, future application reference.

## Scenario 30: Final invoice lower due to partial cancellation after tax invoice

- Prior tax invoice exists
- Expected: issue credit invoice if required, update VAT report according to system rules.
