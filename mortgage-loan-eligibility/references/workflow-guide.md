# Workflow Guide

Use these workflows to move from raw borrower data to a defensible preliminary eligibility result.

## Workflow 1: salaried first-home borrower

### Inputs

- Purchase price and accepted valuation.
- Requested mortgage amount.
- Latest 3-6 payslips.
- Bank statements.
- Existing loan repayments.
- Verified equity.
- Property status evidence.

### Steps

1. Set `property_status` to `single_home`.
2. Use the lower of purchase price and accepted valuation as `property_value`.
3. Enter requested mortgage as `requested_loan_amount`.
4. Use net salary for `net_monthly_income`.
5. Add fixed credit obligations to `existing_monthly_debt`.
6. Add verified available funds to `cash_equity`.
7. Run the calculator.
8. Review LTV, PTI/DSR, and binding constraint.
9. Route to manual review when LTV is near 75% or PTI/DSR exceeds 40%.
10. Prepare the lender document pack.

### Command

```bash
mortgage-loan-eligibility calculate \
  --property-value 2400000 \
  --loan-amount 1500000 \
  --status single_home \
  --net-income 30000 \
  --existing-debt 1000 \
  --cash-equity 900000 \
  --annual-rate 5.0 \
  --term-years 25
```

## Workflow 2: freelancer or sole proprietor

### Inputs

- Annual tax assessment.
- Accountant confirmation.
- Profit-and-loss report.
- VAT reports where relevant; exclude VAT collected from available income because the verified 2026 standard VAT rate is 18% from 01/01/2025.
- Bank statements.
- Current-year trend.
- Personal debt and relevant business debt.
- Property and equity data.

### Steps

1. Build `income_records` from verified months.
2. Use net profit available to the household, not gross revenue.
3. Remove one-time receipts unless recurring and documented.
4. Add recurring personal debt to `existing_monthly_debt`.
5. Add business debt only when lender policy treats it as a personal obligation.
6. Run the calculator.
7. Treat PTI/DSR above 40% as manual review.
8. Prepare explanations for seasonality, large clients, reserve duty, maternity leave, or recent business changes.

### JSON

```json
{
  "property_value": 1800000,
  "requested_loan_amount": 1100000,
  "property_status": "single_home",
  "income_records": [
    {"period": "2025-01", "net_income": 18500, "verified": true},
    {"period": "2025-02", "net_income": 21000, "verified": true},
    {"period": "2025-03", "net_income": 16500, "verified": true},
    {"period": "2025-04", "net_income": 23000, "verified": true},
    {"period": "2025-05", "net_income": 19000, "verified": true},
    {"period": "2025-06", "net_income": 19500, "verified": true}
  ],
  "existing_monthly_debt": 2200,
  "annual_rate": 5.4,
  "term_years": 25
}
```

## Workflow 3: replacement home

### Inputs

- Purchase contract or target purchase price.
- Existing home sale status.
- Expected sale proceeds.
- Bridge-loan needs.
- Legal and tax classification.
- Requested mortgage amount.

### Steps

1. Confirm whether replacement-home classification is supported.
2. Set `property_status` to `replacement_home` only when supported.
3. Apply the 70% LTV cap by default.
4. Include bridge-loan or temporary financing obligations when they affect monthly repayment.
5. Run the base scenario.
6. Run fallback as `investment_property` when sale timing is uncertain.
7. Compare outcomes.
8. Keep legal and tax documents in the file.

## Workflow 4: investment property

### Steps

1. Set `property_status` to `investment_property`.
2. Apply the 50% LTV cap by default.
3. Do not include expected rent unless lender policy accepts it.
4. Include existing mortgage payments and consumer debt.
5. Run the calculator.
6. If LTV fails, calculate additional equity.
7. If DSR fails, test lower loan, longer realistic term, or debt repayment.

## Workflow 5: mixed mortgage tracks

### Steps

1. Create one `tracks` item per route.
2. Ensure track principals sum to `requested_loan_amount`.
3. Run the calculator.
4. Review track-level payments and total payment.
5. Stress-test variable-rate and CPI-linked tracks outside the base output.
6. Store assumptions with the result.

### JSON

```json
{
  "property_value": 2500000,
  "requested_loan_amount": 1500000,
  "property_status": "single_home",
  "net_monthly_income": 33000,
  "existing_monthly_debt": 1500,
  "tracks": [
    {"name": "fixed_unlinked", "principal": 500000, "annual_rate": 4.9, "term_years": 25},
    {"name": "prime", "principal": 500000, "annual_rate": 5.4, "term_years": 25},
    {"name": "variable_cpi", "principal": 500000, "annual_rate": 4.7, "term_years": 25}
  ]
}
```

## Workflow 6: batch screening

### Steps

1. Prepare a JSON array of scenarios.
2. Run the batch command.
3. Filter by `status`.
4. Prioritize cases with `binding_constraint` equal to `ltv` or `dsr`.
5. Send only complete and plausible cases to lenders.
6. Store borrower data securely and delete unnecessary copies.

```bash
mortgage-loan-eligibility batch scenarios.json --output results.json
```

## Outcome action map

| Result | Main action | Next check |
|---|---|---|
| `eligible` | Continue to lender comparison and document pack | Rates, insurance, legal status, term, age |
| `needs_review` | Strengthen file before submission | DSR, income stability, LTV buffer, source of funds |
| `not_eligible` | Change the transaction | Lower loan, add equity, repay debt, lower price, or change collateral |
