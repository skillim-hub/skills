# Workflow Guide

Use these workflows for common Israeli freelancer planning tasks. Each workflow starts with source data, creates a reproducible scenario, runs the calculation, and records follow-up checks.

## Workflow 1: Osek patur threshold watch

1. Collect current-year receipt totals from invoices, receipts, payment processors, and bank deposits.
2. Exclude non-business transfers and loans.
3. Confirm that the business is still registered as osek patur.
4. Run:

```bash
freelancer-tax-calculator calculate \
  --business-type osek-patur \
  --revenue 116000 \
  --expenses 22000 \
  --advance-rate 0.06 \
  --advance-base revenue \
  --env sandbox \
  --json
```

5. Review the `threshold_utilization` value.
6. If status is near the threshold, repeat monthly.
7. If revenue exceeds the configured ceiling, prepare an immediate VAT registration review with a professional.
8. Save the JSON report and the configuration used.

## Workflow 2: Osek murshe VAT period review

1. Export invoices issued during the VAT period.
2. Sum revenue before VAT.
3. Export supplier invoices and classify eligible input VAT.
4. Run:

```bash
freelancer-tax-calculator vat \
  --business-type osek-murshe \
  --revenue 50000 \
  --input-vat 2400 \
  --env sandbox \
  --json
```

5. Compare output VAT and input VAT credit to the bookkeeping system.
6. Investigate any refund position before relying on it.
7. Attach invoice lists, supplier invoices, and the JSON estimate to the period folder.

## Workflow 3: Annual reserve planning

1. Estimate annual revenue before VAT.
2. Estimate deductible expenses before VAT.
3. Enter the official income-tax advance percentage.
4. Use `--advance-base revenue` unless professional guidance says otherwise.
5. Run a base scenario and a conservative scenario with higher revenue or lower expenses.
6. Compare recommended monthly reserve values.
7. Transfer the selected reserve amount to a separate tax account each month.
8. Recalculate after material revenue changes.

## Workflow 4: Micro-business normative expense scenario

1. Confirm that the business is eligible for the small-business route, whether osek patur or low-turnover osek murshe.
2. Confirm that revenue does not exceed the configured osek patur ceiling.
3. Verify eligibility for a 30 percent normative expense treatment with current Tax Authority guidance.
4. Run:

```bash
freelancer-tax-calculator calculate \
  --business-type osek-patur \
  --revenue 100000 \
  --advance-rate 0.06 \
  --micro-business \
  --env sandbox \
  --json
```

5. Compare the result with actual-expense reporting.
6. Keep both scenarios for accountant review.

## Workflow 5: Saved scenario chain

1. Create a scenario:

```bash
freelancer-tax-calculator create \
  --business-type osek-murshe \
  --revenue 300000 \
  --expenses 80000 \
  --input-vat 7200 \
  --advance-rate 0.10 \
  --advance-base revenue \
  --env sandbox \
  --json
```

2. Extract `scenario_id` from the JSON response.
3. Run the scenario:

```bash
freelancer-tax-calculator run SCENARIO_ID --env sandbox --json
```

4. Save the input file, output file, and configuration together.
5. Rerun the same ID after rate configuration changes.

## Workflow 6: Accountant handoff

Prepare a folder containing:

- Scenario input JSON.
- Calculation report JSON.
- Current configuration JSON.
- Revenue export.
- Expense export.
- VAT invoice list.
- Bank reconciliation summary.
- Notes about unusual transactions.
- Question list for the accountant or tax adviser.

Use this handoff to avoid hidden assumptions and to make review faster.
