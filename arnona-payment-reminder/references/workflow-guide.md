# End-to-End Workflow Guide

## Workflow 1: Household Bill Reminder

### Goal

Create safe reminders for a residential Arnona bill and avoid late payment.

### Steps

1. Receive the bill by mail, email, municipal app, or upload.
2. Extract municipality, payer/account number, bill number, address, period, amount, issue date, and due date.
3. Confirm that the address and billing period match the household.
4. Check whether a standing order exists.
5. Check whether a discount or exemption request is pending.
6. Generate reminders at 30, 14, 7, 3, 1, and 0 days before the due date.
7. Pay through the official payment page or the link printed on the bill.
8. Save the receipt and confirmation number.
9. Mark the bill as paid and cancel remaining reminders.

### Output Example

```text
Status: upcoming
Next reminder: 14-02-2026
Payment amount: ₪782.40
Required fields: מספר משלם/חשבון, מספר שובר, מספר זהות, סכום לתשלום
Receipt required: yes
```

## Workflow 2: Small Business Approval Flow

### Goal

Route a business Arnona bill through owner approval and bookkeeping.

### Steps

1. Create a bill record per branch or property.
2. Add branch label, internal cost center, and accounting folder path.
3. Validate the property address against the branch list.
4. Add a 14-day reminder to approve the payment.
5. Add a 7-day reminder to the bookkeeper.
6. Add a 3-day urgent reminder to the business owner.
7. Pay after approval.
8. Store the receipt in the accounting folder.
9. Attach the receipt to the expense record.
10. Reconcile the bank/card transaction.

### Suggested Message

```text
Arnona approval needed: Branch Bialik 40, period 03-04/2026, amount ₪1,288.90.
Verify property, period, discount status, and payment method before approving.
```

## Workflow 3: Freelancer Working From Home

### Goal

Remind payment while preserving evidence for accountant review.

### Steps

1. Treat the municipal bill as a household payment unless the municipality classifies the asset otherwise.
2. Create reminders normally.
3. Add a receipt tag: `accountant_review`.
4. After payment, save the receipt with the tax year and address.
5. Ask the accountant whether any part is deductible.
6. Avoid stating deductibility in the reminder.

### Evidence Pack

- Arnona bill.
- Receipt.
- Payment confirmation.
- Business-use note.
- Accountant decision, when provided.

## Workflow 4: Landlord-Tenant Handoff

### Goal

Make sure the correct party pays and the other party receives proof.

### Steps

1. Read the lease allocation for Arnona responsibility.
2. Verify the current holder in municipal records when available.
3. Generate payment instructions for the paying party.
4. Generate a separate receipt-request reminder for the non-paying party.
5. After payment, send the receipt and period summary.
6. Store communication in the property folder.

### Risk Controls

- Do not send full payer ID unless required.
- Do not accept a screenshot without visible municipality, amount, date, and confirmation number.
- Do not reimburse without matching property and period.

## Workflow 5: Overdue Bill

### Goal

Avoid paying a stale balance after the due date.

### Steps

1. Mark the bill as `overdue`.
2. Do not rely solely on the old amount.
3. Request current balance from the municipality or official payment page.
4. Check interest, linkage, collection expenses, and payment arrangement options.
5. Confirm whether enforcement has started.
6. Pay the updated balance or approved arrangement.
7. Save receipt and updated balance proof.
8. Close reminders only after receipt is available.

### Overdue Message

```text
This Arnona bill is overdue. Check the current balance with the municipality before payment. The original amount may exclude interest, linkage, or collection costs.
```

## Workflow 6: Corrected or Replaced Voucher

### Goal

Prevent duplicate payment when the municipality issues a correction.

### Steps

1. Compare municipality, account number, asset, period, and amount.
2. Keep both bill records.
3. Mark the older bill as `candidate_replaced`.
4. Confirm replacement from the payment site, personal area, or municipal service.
5. Cancel reminders for the obsolete bill.
6. Generate reminders only for the current bill.
7. Save a note explaining the replacement.

## Workflow 7: Standing Order Monitoring

### Goal

Track automatic payments without causing a duplicate manual payment.

### Steps

1. Identify הוראת קבע or direct debit status.
2. Replace payment reminders with debit-verification reminders.
3. Schedule a check after the expected debit date.
4. Confirm bank/card charge.
5. Download or request receipt.
6. Mark the bill paid only after confirmation.

## Workflow 8: Discount or Exemption Pending

### Goal

Avoid missing payment deadlines while preserving discount rights.

### Steps

1. Mark discount or exemption request as pending.
2. Generate a status-check reminder 14 days before due date.
3. Ask the municipality whether payment is required pending a decision.
4. If payment is required, pay by due date and preserve refund/credit evidence.
5. If a stay or arrangement exists, document it and adjust reminders.
6. After approval or denial, update bill balance and status.

## Workflow 9: Multi-Municipality Property Manager

### Goal

Track many properties across different authorities.

### Steps

1. Store one profile per municipality.
2. Store one bill record per property and period.
3. Deduplicate by municipality, account reference, property label, period, and bill number.
4. Group reminders by due date and responsible person.
5. Generate daily task lists for due-soon and overdue bills.
6. Archive receipts by property and year.
7. Run monthly reconciliation.

## Workflow 10: Accounting Close

### Goal

Prepare month-end documentation.

### Steps

1. Export paid bills for the month.
2. Verify each paid bill has a receipt.
3. Verify the paid amount matches the bank/card transaction.
4. Attach receipt and bill to the accounting entry.
5. Mark partial or disputed bills for review.
6. Store a reconciliation report.


## Workflow 11: VAT and Accounting Context Check

### Goal

Prevent a business workflow from adding VAT to an Arnona bill or treating an Arnona payment as a supplier invoice.

### Steps

1. Use the official municipal bill amount or current balance as the amount to pay.
2. Do not add VAT to the Arnona amount.
3. Save the bill, receipt, payment confirmation, property label, period, and payment date.
4. Hand the record to the accountant for bookkeeping treatment when the payer is a business or freelancer.
5. Keep deductibility decisions outside the reminder workflow.
