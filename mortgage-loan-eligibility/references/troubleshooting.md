# Troubleshooting

## Not eligible due to LTV

### Common causes

- Requested loan is above the cap for the property status.
- Property is marked as investment property.
- Accepted valuation is lower than contract price.
- Replacement-home status is not confirmed.
- Cash equity is too low.

### Fixes

1. Compare `requested_loan_amount` with `max_loan_by_ltv`.
2. Reduce loan to the cap.
3. Increase verified equity.
4. Confirm property status with legal and tax documents.
5. Recalculate using the lower valuation when appraisal is lower than price.

## Not eligible due to DSR

### Common causes

- Net income is too low.
- Existing debt is high.
- Interest rate or term creates high payment.
- Short term was used.
- Business income was normalized conservatively.

### Fixes

1. Compare `estimated_monthly_payment` with `max_monthly_payment_by_dsr`.
2. Test a lower loan amount.
3. Extend the term only when realistic under lender policy and borrower age.
4. Reduce existing debt before application.
5. Add verified co-borrower income when appropriate.
6. Prepare exception handling only when documents are strong.

## Needs review

### Common causes

- PTI/DSR is above 40%.
- LTV is near the cap.
- Income history is short.
- Borrower is self-employed, newly employed, or has foreign income.
- Equity comes from a gift or recent transfer.

### Fixes

1. Prepare complete source documents.
2. Stress-test rates and CPI-linked tracks.
3. Add a valuation buffer.
4. Add source-of-funds evidence.
5. Run a conservative scenario with lower income and higher rate.

## Payment differs from a bank quote

### Possible reasons

- Quote includes insurance, fees, CPI linkage, or different rounding.
- Quote uses a mixed track structure.
- Quote includes an initial interest-only period.
- Quote applies future rate reset or stress testing.

### Fixes

- Enter each track separately.
- Compare base amortizing payment before fees and insurance.
- Add stress testing outside the base formula.
- Request a payment schedule by track.

## Freelancer income looks too low

### Possible reasons

- Only verified net income was used.
- One-off high months were trimmed.
- Gross revenue was excluded.
- Tax, National Insurance, VAT, pension, and business expenses reduced available income. VAT collected from customers is not borrower income.

### Fixes

- Provide 12-24 months when available.
- Add accountant confirmation.
- Separate one-time projects from recurring work.
- Use documented weighting when seasonality is real.

## Cash equity fails despite family support

### Possible reasons

- Gift funds were not entered.
- Gift funds are undocumented.
- Funds are pledged or not yet transferred.
- Purchase costs outside the price were ignored.

### Fixes

- Enter documented cash equity only.
- Obtain gift confirmation and source-of-funds evidence.
- Keep extra cash for tax and transaction costs.
- Re-run after funds are available.

## CLI cannot run

### Symptom

```text
ModuleNotFoundError: No module named 'typer'
```

Install dependencies:

```bash
python -m pip install -e .
```

or:

```bash
python -m pip install typer
```

### Symptom

```text
sum of tracks.principal must equal requested_loan_amount within ₪1
```

Fix the track totals:

```json
{
  "requested_loan_amount": 1500000,
  "tracks": [
    {"name": "fixed", "principal": 500000},
    {"name": "prime", "principal": 500000},
    {"name": "variable", "principal": 500000}
  ]
}
```

## Validation reference

| Message | Meaning | Resolution |
|---|---|---|
| `provide net_monthly_income or income_records` | No repayment-capacity data | Add net income or verified records |
| `requested_loan_amount must not exceed property_value` | Loan above asset value | Correct value or lower loan |
| `annual_rate appears too high after normalization` | Rate entered as 525 instead of 5.25 | Enter percentage correctly |
| `term_years must be between 1 and 30` | Term outside supported range | Use a realistic term |
| `at least one verified income record is required` | All records are unverified | Verify at least one record |
| `cash_equity must not be negative` | Invalid equity input | Correct input |
