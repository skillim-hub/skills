# Workflow Guide

Use these workflows as end-to-end operating procedures for real planning cases.

---

## Workflow 1: Freelancer monthly forecast

Goal: identify whether the next three months have enough free cash after VAT, income-tax advances, Bituach Leumi, and owner withdrawals.

Steps:

1. Create `freelancer.json`.
2. Enter opening balance, start month, and forecast length.
3. Add customer payments by expected bank date.
4. Add recurring expenses.
5. Add owner draw as cash-out.
6. Set VAT cadence.
7. Enter verified advance rates or conservative planning rates.
8. Run `budget-cashflow-forecaster forecast freelancer.json --output freelancer.csv`.
9. Review `free_cash` before `closing_balance`.
10. Create a collection or cost action for every month below buffer.

Decision points:

- If free cash is negative, reduce discretionary spending or collect earlier.
- If closing balance is positive but free cash is low, protect tax reserves.
- If a large VAT payment lands before receivables, negotiate earlier customer terms.

---

## Workflow 2: עוסק מורשה with bimonthly VAT

1. Mark revenue as taxable and gross when receipts include VAT.
2. Set `vat_cadence` to `bimonthly`.
3. Add supplier payments and notes for input VAT when known.
4. Review two-month periods together.
5. Keep protected reserve separate from working cash.
6. Use exact authority payment dates when known.

Expected output:

- `tax_reserved` rises during activity months.
- `tax_paid` appears in payment months.
- `protected_reserve` falls after payment.

---

## Workflow 3: עוסק פטור planning

1. Set `vat_cadence` to `none`.
2. Keep income-tax and Bituach Leumi assumptions if relevant.
3. Add professional costs: accountant, software, insurance, and equipment.
4. Add owner draw.
5. Add a note to review annual turnover threshold.

Do not treat VAT-disabled planning as status confirmation.

---

## Workflow 4: Retail inventory cycle

1. Enter supplier payments by bank debit date.
2. Enter card settlements by bank credit date.
3. Add rent, wages, municipal taxes, utilities, delivery, and payment processing fees.
4. Use weekly detail if monthly totals hide risk.
5. Set buffer to at least one month of fixed costs.
6. Run conservative scenario with lower sales and higher supplier costs.

Action triggers:

- Split inventory order if supplier timing creates negative cash.
- Prepare financing before the gap.
- Avoid using VAT reserve for stock replenishment without a repayment plan.

---

## Workflow 5: Consumer budget

1. Disable business tax settings.
2. Add salary by payment date.
3. Add rent, mortgage, card debit, loans, savings, childcare, and groceries.
4. Add irregular costs such as car insurance and school payments.
5. Review low-balance months and card billing clusters.

---

## Workflow 6: Spreadsheet migration

1. Export the sheet as CSV.
2. Rename columns to `date`, `amount`, `direction`, `description`, `category`.
3. Use `direction` values `in` and `out`.
4. Keep all amounts positive.
5. Validate JSON after conversion.
6. Compare first-month closing balance to the original sheet.

---

## Workflow 7: Monthly close

1. Copy the previous forecast file.
2. Replace completed-month estimates with actual bank activity.
3. Move unpaid invoices to updated expected payment dates.
4. Update tax reserves with actual taxable receipts.
5. Add new known expenses.
6. Run baseline and conservative scenarios.
7. Save dated outputs.

---

## Workflow 8: Late-payment stress test

1. Copy baseline to `late-payment.json`.
2. Move the largest receipt 30–60 days later.
3. Run the forecast.
4. Compare minimum free cash to baseline.
5. Prepare actions if the stress scenario breaks the buffer.

---

## Workflow 9: Accountant review pack

Include:

- Forecast JSON.
- CSV output.
- Tax assumptions.
- VAT cadence assumption.
- Income-tax advance source.
- Bituach Leumi assumption.
- Uncertain receivables.
- Large irregular expenses.
- Open questions.

Ask:

- Are rates current?
- Is cadence correct?
- Are receipts gross or net?
- Are advance payments modeled correctly?
- Should any receipt be excluded from taxable base?

---

## Workflow 10: Recovery plan for negative cash

1. Identify first negative month.
2. Separate causes: delayed receipts, supplier payment, authority deadline, owner draw, seasonality.
3. Quantify the gap.
4. Choose actions: collect earlier, request deposit, split payment, reduce draw, defer purchase, use approved credit.
5. Rerun forecast with chosen actions.
6. Confirm negative month disappears or becomes manageable.
