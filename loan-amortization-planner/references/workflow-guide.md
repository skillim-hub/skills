# Workflow Guide

Use these workflows to turn loan offers into practical repayment schedules and decision-ready comparisons.

## Workflow 1: Compare three bank offers for a small business

### Goal

Select the most suitable ₪300,000 loan for a business that needs equipment financing.

### Steps

1. Create one JSON scenario for each offer.
2. Use the same `principal`, `term_months`, and `start_date` unless the offer terms differ.
3. Enter fees exactly as quoted.
4. Enter fixed, prime, and CPI assumptions separately.
5. Run the comparison command.
6. Review `effective_cash_cost`, `max_payment`, and risk type.
7. Export the winning scenario to CSV for the credit file.

### Example `offers.json`

```json
{
  "scenarios": [
    {
      "name": "Bank A fixed",
      "principal": "300000",
      "term_months": 60,
      "start_date": "01/07/2026",
      "rate_type": "fixed",
      "annual_interest_rate": "0.064",
      "origination_fee": "1500"
    },
    {
      "name": "Bank B prime",
      "principal": "300000",
      "term_months": 60,
      "start_date": "01/07/2026",
      "rate_type": "prime",
      "prime_rate": "0.0525",
      "prime_margin": "0.012",
      "origination_fee": "900"
    },
    {
      "name": "Bank C CPI",
      "principal": "300000",
      "term_months": 60,
      "start_date": "01/07/2026",
      "rate_type": "cpi",
      "annual_interest_rate": "0.039",
      "annual_cpi_rate": "0.025",
      "origination_fee": "1200"
    }
  ]
}
```

```bash
python scripts/loan_amortization_planner_cli.py compare offers.json
```

### Decision notes

- Prefer the lowest effective cash cost only if liquidity risk and index/rate risk are acceptable.
- For prime-linked offers, add stress cases rather than relying on the base case.
- For CPI-linked offers, disclose the CPI assumption beside every result.

## Workflow 2: Freelancer cash-flow check before taking a loan

### Goal

Confirm whether a freelancer can service a ₪90,000 loan while expecting a future VAT refund.

### Steps

1. Build a base fixed-rate scenario.
2. Add expected VAT-refund repayment as `extra_payments`.
3. Add any quoted early-repayment fee.
4. Compare base and extra-repayment scenarios.
5. Check `max_payment` against monthly available cash after tax advances, National Insurance, rent, payroll, software, and living draw.

### Output to keep

- Base schedule CSV.
- Extra-repayment schedule CSV.
- Memo showing whether the VAT refund is committed to loan reduction or retained as liquidity.

## Workflow 3: CPI-linked consumer loan stress test

### Goal

Show the household impact of indexation uncertainty.

### Steps

1. Create three CPI scenarios: `0`, base inflation, and high inflation.
2. Keep rate, term, and fees identical.
3. Run comparison.
4. Export the high-CPI case to CSV.
5. Review whether the highest payment and total adjustment remain acceptable.

### Suggested scenario names

- `CPI low 0%`
- `CPI base 2.5%`
- `CPI stress 5%`

## Workflow 4: Vehicle loan with balloon payment

### Goal

Check affordability of a commercial vehicle loan that has lower monthly payments and a large final payment.

### Steps

1. Enter the full principal.
2. Enter the final balloon as `balloon_percent`.
3. Generate the schedule.
4. Inspect final-period `total_payment`.
5. Document the planned exit source: resale, refinancing, retained cash, or owner injection.
6. Create a no-balloon comparison with the same rate and term.

### Red flags

- The balloon is larger than conservative resale value.
- Refinancing is assumed but not approved.
- The monthly saving is used for ongoing expenses rather than reserved for the final payment.

## Workflow 5: Grace-period bridge loan

### Goal

Evaluate a short grace period while a project waits for customer collection.

### Steps

1. Enter the full term.
2. Enter `grace_months`.
3. Confirm that grace is interest-only, not full-payment deferral.
4. Compare with a no-grace scenario.
5. Check total interest and maximum payment after grace ends.

### Interpretation

Grace improves near-term liquidity but usually increases total interest because principal amortization starts later.

## Workflow 6: Board or owner approval pack

### Goal

Prepare a concise approval pack for a material loan.

### Pack contents

1. Input JSON for every scenario.
2. CSV schedule for selected scenario.
3. Comparison table.
4. Assumption register with source of principal, rate, margin, CPI, fees, and due date.
5. Stress-case summary.
6. Accounting and tax review note if material.
7. Statement that the output is a planning calculation, not an official lender disclosure.

## Workflow 7: Monthly reconciliation after loan starts

### Goal

Find differences between planned and actual payments.

### Steps

1. Export the schedule to CSV.
2. Add actual bank debits beside planned payments.
3. Investigate differences above the tolerance threshold.
4. Check for date shifts, daily-interest treatment, CPI publication lag, fees, and rate resets.
5. Update assumptions only when there is a documented reason.


## Workflow 8: Update live assumptions before a new decision

### Goal

Avoid using stale public rates in a new loan comparison.

### Steps

1. Check the current Bank of Israel rate.
2. Derive the prime base as Bank of Israel rate plus 1.5%.
3. Enter the prime base explicitly as `prime_rate`.
4. Check whether VAT at 18% affects surrounding cash-flow timing, especially for VAT refunds and taxable interest in related transactions.
5. Confirm whether CPI assumptions are forecasts or imported historical values.
6. Record the source URL and access date in the workpaper.

### Current verified baseline on 2026-06-02

- Bank of Israel rate: 3.75%.
- Implied prime base: 5.25%.
- Standard VAT rate: 18%.
