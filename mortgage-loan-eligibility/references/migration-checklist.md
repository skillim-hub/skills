# Migration Checklist

Use this checklist when replacing an older mortgage calculator, spreadsheet, intake form, or manually maintained worksheet.

## 1. Map fields

| Old concept | New field | Notes |
|---|---|---|
| Purchase price | `property_value` | Use lower of contract and accepted valuation when known |
| Loan requested | `requested_loan_amount` | Include only mortgage principal |
| Asset type | `property_status` | Normalize to three supported values |
| Household income | `net_monthly_income` | Use net monthly income |
| Monthly commitments | `existing_monthly_debt` | Include recurring obligations |
| Available equity | `cash_equity` | Use verified funds only |
| Interest assumption | `annual_rate` | Accepts percent or decimal |
| Loan term | `term_years` | 1-30 in the helper; set stricter production limits if needed |
| Product mix | `tracks` | Optional; sum must match requested loan |

## 2. Remove unsupported assumptions

Delete or replace:

- Promotional text.
- Decorative media references.
- Person or organization attribution fields.
- Hard-coded lender names unless a lender-specific policy module exists.
- Gross-income fields used as repayment capacity.
- Hidden formulas that cannot be audited.
- Manual overrides without reason codes.
- Output that resembles final lender approval.

## 3. Normalize statuses

Use only:

```text
single_home
replacement_home
investment_property
```

Add manual review for:

- Unclear property status.
- Replacement-home sale deadline issues.
- Mixed residential and commercial collateral.
- Family transfers.
- Construction or self-build transactions.

## 4. Validate policy values

Before launch:

1. Confirm current Bank of Israel LTV caps, PTI/DSR thresholds, and 30-year term cap.
2. Confirm current lender repayment-ratio handling.
3. Confirm maximum term by borrower age.
4. Confirm track-composition limits.
5. Confirm treatment of foreign income and guarantors.
6. Confirm treatment of business debt and owner guarantees.

## 5. Rebuild test cases

Create test cases for:

- LTV pass and fail for every property status.
- DSR pass, review, and fail.
- Cash-equity shortfall.
- Freelancer income normalization.
- Track sum mismatch.
- Zero interest.
- High-interest stress.
- Existing-debt sensitivity.
- Lower appraisal value.
- Replacement-home fallback.

## 6. Data protection

- Remove identity numbers from fixtures.
- Remove real bank account numbers from examples.
- Store borrower files outside the repository.
- Encrypt production storage.
- Limit logs to values needed for audit.
- Add retention rules for abandoned applications.

## 7. Deployment checklist

1. Run `python -m pytest scripts`.
2. Run a sample CLI command.
3. Create a sample JSON request.
4. Compare output with the legacy worksheet for at least 20 scenarios.
5. Investigate any difference above tolerance.
6. Record active policy thresholds.
7. Train users to interpret `needs_review`.
8. Publish a limitation statement with each result.

## 8. Cutover plan

1. Freeze the old worksheet.
2. Export representative historical scenarios.
3. Convert inputs to the new JSON schema.
4. Run batch calculations.
5. Review differences with a mortgage specialist.
6. Update templates and borrower-facing explanations.
7. Archive the old tool.
8. Monitor first production cases for false passes or false failures.


## 2.1.0 migration from v2.0.0

- Replace file-loader imports with `from mortgage_loan_eligibility_client import MortgageEligibilityClient`.
- Remove references to the deleted hyphenated client file.
- Run `pip install -e .` before using examples or the console command.
- Use `mortgage-loan-eligibility create` to create a stored scenario and `mortgage-loan-eligibility evaluate` with the returned `scenario_id` to evaluate it.
- Set environment defaults with `MLE_SANDBOX_*` or `MLE_PRODUCTION_*` variables.
