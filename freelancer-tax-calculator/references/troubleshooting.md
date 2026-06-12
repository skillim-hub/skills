# Troubleshooting

## VAT payable is much higher than expected

Likely causes:

- Revenue was entered including VAT instead of before VAT.
- Input VAT was entered as total expense instead of VAT component only.
- VAT rate in configuration does not match the tax year.

Fix:

1. Split VAT-inclusive receipts using the gross-to-net helper.
2. Re-enter supplier VAT as the VAT component only.
3. Update `vat_rate` from an official current-year source.
4. Rerun the scenario and compare output VAT to the invoice export.

## Osek patur shows no input VAT credit

This is expected. Osek patur does not charge VAT and does not offset input VAT in the calculator. Treat VAT paid on expenses according to professional bookkeeping guidance.

## Osek patur threshold warning appears too early

Likely causes:

- The warning ratio is set to `0.90` by default.
- Revenue includes amounts that should not be in business turnover.
- The annual threshold in configuration is outdated.

Fix:

1. Reconcile revenue to receipts.
2. Update `osek_patur_threshold_annual`.
3. Adjust `osek_patur_warning_ratio` if an internal monitoring policy uses a different trigger.

## Income-tax advances differ from the portal

Likely causes:

- Wrong official percentage.
- Wrong base selection.
- Portal notice changed during the year.
- Calculation uses annual planning while the portal displays period payment.

Fix:

1. Confirm the current percentage in the business file.
2. Use `income_tax_advance_base = revenue` unless instructed otherwise.
3. Recalculate after updating the percentage.
4. Compare annual amount to period schedule.

## National Insurance differs from an official notice

Likely causes:

- Configuration thresholds or rates are outdated.
- Personal status, other income, credits, or minimum contributions are not modeled.
- Official assessment uses actual annual income after adjustments.

Fix:

1. Update National Insurance configuration.
2. Add notes about employment income or other income.
3. Treat the result as a reserve estimate.
4. Compare against the latest official notice before payment.

## Scenario ID not found

Likely causes:

- Scenario was created under a different store directory.
- `FTC_STORE_DIR` changed between `create` and `run`.
- The scenario file was deleted.

Fix:

1. Pass the same `--store-dir` used during creation.
2. Set `FTC_STORE_DIR` consistently.
3. Create a new scenario if the input file is missing.

## Python import fails

Likely causes:

- Package was not installed in editable mode.
- Commands run from a different virtual environment.
- An old hyphenated client path is still referenced.

Fix:

```bash
pip install -e .
python -c "from freelancer_tax_calculator import FreelancerTaxCalculator; print(FreelancerTaxCalculator)"
```

Replace path-based imports with:

```python
from freelancer_tax_calculator import FreelancerTaxCalculator, FreelancerTaxInput
```

## JSON consumer expects numbers, not strings

Amounts are serialized as strings to preserve exact Decimal values. Parse them as Decimal in the receiving system. Do not convert money through binary floating-point unless rounding differences are acceptable.
