# Workflow Guide

Use these workflows to apply the calculator in a store, service business, or consumer support operation.

## Web-validated 2026 pre-check

1. Confirm whether the displayed amount is consumer-facing or business-facing.
2. Use 18% as the current VAT baseline only after confirming no later update applies.
3. For consumer-facing display, keep the cash price total and VAT-inclusive.
4. For cancellation work, calculate the lower of 5% or ₪100, then verify that the case qualifies and no exception applies.
5. For B2B invoice workflows after 01/06/2026, check whether the pre-VAT amount exceeds ₪5,000 and needs an Israel Invoice allocation number.

## Workflow 1: Online checkout

1. Load cart total as the cash price.
2. Confirm whether the displayed price is VAT-inclusive.
3. Offer a short list of permitted installment counts.
4. Calculate each plan with the approved interest and fee policy.
5. Sort by total paid and show the cash price beside every installment offer.
6. Require explicit customer acceptance of total paid, first due date, and cancellation terms.
7. Store the serialized plan with the order.
8. Pass only the approved payment amount and schedule to the payment provider.
9. Reconcile settlement against the stored schedule.

Acceptance criteria:

- Cash price remains visible.
- The selected plan stores every input and every calculated output.
- A customer can see total cost above cash price before approval.

## Workflow 2: Freelancer quote

1. Create the service quote with a fixed cash price.
2. Add a down payment if work starts before all payments are collected.
3. Calculate the financed balance and monthly schedule.
4. Mark `consumer_context=False` only when the customer is clearly a business customer.
5. Attach the schedule to the quote.
6. Convert the accepted quote into an invoice or receipt workflow according to bookkeeping guidance.
7. Recalculate if scope, price, date, or payment count changes.

Example:

```python
InstallmentRequest(
    cash_price="9800",
    down_payment="2800",
    installments=4,
    first_due_date="10/08/2026",
    consumer_context=False,
)
```

## Workflow 3: Consumer disclosure review

1. Calculate the plan.
2. Read `plan.disclosure_checks`.
3. Resolve every `review` item before publication.
4. Confirm that marketing language does not imply free credit when fees exist.
5. Keep a copy of the final displayed wording.

Minimum display:

```text
Cash price: ₪3,600.00
Plan: 12 monthly payments from 05/07/2026
Nominal annual interest: 7.5%
Fees: ₪49.00 upfront and ₪1.90 per installment
Total paid: calculated value
Cost above cash price: calculated value
```

## Workflow 4: Cancellation and refund

1. Retrieve the stored plan accepted by the customer.
2. Count installments already paid.
3. Run `estimate_refund`.
4. Compare the estimate with contract terms, cancellation rules, product return status, and acquirer rules.
5. Issue a refund, credit invoice, or settlement demand only after approval.
6. Store the decision and supporting evidence.

## Workflow 5: Spreadsheet replacement

1. Export representative historical rows.
2. Convert columns to `InstallmentRequest` fields.
3. Run the test scenario file against the old calculations.
4. Investigate differences caused by rounding, fee timing, and date clipping.
5. Use the package as the single calculation source.
6. Lock old spreadsheet formulas to read-only or remove them from production.

## Workflow 6: Support-call explanation

1. Ask for the order identifier.
2. Retrieve the stored cash price and selected plan.
3. Explain the cash price, financed amount, payment count, fees, and current balance.
4. Avoid legal conclusions on the call.
5. Escalate cancellation disputes with the serialized plan and payment evidence.

## Workflow 7: Month-end reconciliation

1. Export expected payments from stored schedules.
2. Export actual card-settlement data.
3. Match by order, date, and amount.
4. Investigate failed payments, chargebacks, early payments, and refunds.
5. Post accounting corrections according to bookkeeping guidance.
