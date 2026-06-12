# Workflow Guide

## Workflow 1: Advance for a service project

Use for a designer, developer, consultant, marketer, repair provider, or freelancer receiving part of the price before completion.

### Inputs

- Quote or order number.
- Supplier VAT status.
- Total price before VAT.
- Deposit amount and date.
- Payment method and reference.
- Refund and cancellation terms.
- Delivery or milestone dates.

### Steps

1. Confirm supplier status: VAT-registered, VAT-exempt, non-profit/Malkar, or other.
2. Classify the payment as `advance_for_taxable_supply`.
3. Issue a receipt on the date money is received.
4. Decide whether a tax invoice is required at receipt or later.
5. Create a deposit record with deposit ID, order ID, receipt number, customer, amount, and applied amount `₪0.00`.
6. Track the balance in a deposit liability or customer advance account.
7. On delivery, prepare final settlement:
   - Total price.
   - VAT.
   - Deposit applied.
   - Balance due.
8. Issue receipt for final balance when paid.
9. Reconcile customer card and deposit account.

### Customer-facing settlement note

```text
התקבלה מקדמה בסך ₪3,000 ביום 15/03/2026 עבור הזמנה ORD-4431.
המקדמה קוזזה מהחשבונית הסופית. יתרה לתשלום לאחר קיזוז: ₪11,160.
```

## Workflow 2: Refundable security deposit

Use for equipment rental, short-term property use, workshops with refundable seat deposits, or damage deposits.

### Steps

1. Confirm the deposit is refundable and not part of the sale price unless a defined event occurs.
2. Issue receipt.
3. Do not issue tax invoice only because the deposit was received.
4. Record as security deposit liability.
5. At the end of the obligation, choose one path:
   - Full refund.
   - Partial refund and partial retention.
   - Full retention.
6. If retained as consideration, damages, or cancellation fee, determine the correct tax document at that time.
7. Store refund or retention evidence.
8. Close the deposit record.

### Control

Require second review before retaining security deposits, because tax and consumer-law consequences may differ from the original receipt treatment.

## Workflow 3: Non-refundable booking fee

Use for photographers, event suppliers, clinics, instructors, venues, and consultants who reserve time or capacity.

### Steps

1. Put cancellation and refund terms in writing before collection.
2. Classify the money as `non_refundable_booking_fee`.
3. Issue receipt.
4. For VAT-registered supplier, evaluate whether tax invoice/receipt is required immediately.
5. If the event occurs, apply the fee on the final invoice.
6. If the customer cancels:
   - Keep fee only if contract and consumer rules allow it.
   - Issue correction documents if a tax invoice was already issued and taxable amount changes.
7. If supplier cancels, refund and document the reason.

### Settlement display

```text
סה״כ עסקה כולל מע״מ: ₪5,900
דמי שריון ששולמו: ₪750
יתרה לתשלום: ₪5,150
```

## Workflow 4: VAT-exempt freelancer deposit

### Steps

1. Confirm current עוסק פטור status.
2. Issue receipt only.
3. Do not add VAT.
4. Do not issue tax invoice.
5. Track deposit until service completion.
6. At completion, issue receipt or final customer statement according to bookkeeping system practice.
7. If status changes to VAT-registered, split pre-change and post-change activity.

### Customer explanation

```text
העסק מסווג כעוסק פטור ולכן מופקת קבלה בלבד. לא נגבה מע״מ ולא ניתן להפיק חשבונית מס לקיזוז מע״מ תשומות.
```

## Workflow 5: Deposit exceeds final invoice

### Steps

1. Calculate final gross total.
2. Apply deposit only up to the final total.
3. Calculate overpayment.
4. Decide:
   - Refund immediately.
   - Keep as documented credit balance with customer approval.
5. If a tax invoice was issued for a higher amount, evaluate credit invoice.
6. Store refund proof or credit-balance approval.
7. Reconcile customer card.

### Example

- Deposit paid: ₪2,000
- Final invoice: ₪1,770
- Deposit applied: ₪1,770
- Overpayment: ₪230
- Action: refund ₪230 or keep customer-approved credit.

## Workflow 6: Customer retention

### Steps

1. Classify as `retention_held_by_customer`, not deposit received.
2. Do not issue receipt for withheld money.
3. Track retained amount as receivable if invoice has been issued.
4. Follow VAT timing and invoice rules for the supply itself.
5. When released, issue receipt for cash received.
6. If reduced, issue correction or credit documents where required.
7. Keep acceptance certificate, defect list, and release approval.

## Workflow 7: Cancellation after tax invoice issued

### Steps

1. Locate original tax invoice.
2. Determine cancellation amount.
3. Determine whether goods/services were partly supplied.
4. Issue credit invoice only against original tax invoice when required.
5. Refund cash or apply credit balance.
6. Keep cancellation request and customer approval.
7. Adjust VAT report according to document date and accounting-system rules.

## Workflow 8: Israel Invoice allocation number needed

### Steps

1. Check current threshold and invoice type.
2. Validate customer tax ID.
3. Submit through approved invoicing software, portal, or authorized API integration.
4. Store allocation number on the invoice.
5. If allocation fails, follow official fallback process and document attempts.
6. Do not invent allocation numbers.

## Workflow 9: Month-end deposit reconciliation

### Steps

1. Export all open deposit records.
2. Match each to receipt number and bank movement.
3. Match applied deposits to final invoices.
4. Investigate negative or stale balances.
5. Confirm refundable security deposits are not in revenue.
6. Confirm VAT report agrees with tax invoices, not raw deposits.
7. Produce exception report:
   - Deposits older than 90 days.
   - Deposits without contract.
   - Deposits without receipt.
   - Deposits partially applied.
   - Overpayments.



## Verified threshold control

When issuing a qualifying tax invoice on or after 01/06/2026, check whether the amount before VAT exceeds ₪5,000 and whether an allocation number is required. For 01/01/2026 through 31/05/2026, use the ₪10,000 before-VAT threshold. Keep the threshold configurable by date.
