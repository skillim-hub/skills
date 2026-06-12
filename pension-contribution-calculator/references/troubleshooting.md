# Troubleshooting

## Input problems

### Gross salary is negative

Cause: payroll export contains refund, reversal, or malformed value.

Fix:

1. Remove reversal rows from the contribution calculation.
2. Recalculate the corrected month separately.
3. Keep a payroll correction memo.

### Pensionable salary exceeds gross salary

Cause: mapping error between gross salary, pensionable salary, overtime, bonus, or retroactive pay.

Fix:

1. Reconcile salary components.
2. Confirm whether retroactive pensionable pay belongs to the current month.
3. Correct the pensionable salary input.

### Product value is rejected

Cause: product code is not `pension_fund` or `bituach_menahalim`.

Fix:

1. Use `pension_fund` for קרן פנסיה.
2. Use `bituach_menahalim` for ביטוח מנהלים.
3. Treat provident fund routing as supplemental output, not as the main product flag.

## Employee payroll problems

### Employee total is lower than expected

Possible causes:

- Pensionable salary lower than gross.
- Keren Hishtalmut not included.
- Section 14 flag not enabled.
- Waiting period applied outside the calculator.

Fix:

1. Check pensionable salary.
2. Add `--hishtalmut` when the benefit exists.
3. Add `--section14` only when 8.33% severance applies.
4. Compare the start-date rule outside the numerical calculator.

### Employer cost is higher than payroll budget

Possible causes:

- Keren Hishtalmut added.
- Full Section 14 used.
- Salary ceiling not considered for taxable benefit.
- Gross salary used where only a pensionable component should be used.

Fix:

1. Separate cash cost from taxable benefit.
2. Review employment agreement.
3. Confirm whether budget included employer pension, severance, and Keren Hishtalmut.

### Comprehensive pension fund receives too much

Cause: high salary or full Section 14 pushes the monthly deposit above the comprehensive fund deposit ceiling.

Fix:

1. Use `supplemental_or_policy_deposit` from the result.
2. Route excess to a supplemental pension fund, provident fund, or other allowed product.
3. Confirm fund routing with the operating fund.

### Keren Hishtalmut tax treatment is wrong

Cause: employer deposit above salary ceiling treated as fully exempt.

Fix:

1. Check `employer_hishtalmut_taxable`.
2. Add the taxable amount to payroll.
3. Document the ceiling used for the tax year.

## Self-employed problems

### Mandatory pension is zero

Possible causes:

- Annual net taxable income is zero.
- First-year-business flag is set.
- Age is below 21.
- Age is at or above retirement age input.

Fix:

1. Check annual income.
2. Confirm business opening year.
3. Confirm age at tax-year end.
4. Override retirement age only with a reason.

### Mandatory pension is higher than expected

Possible causes:

- Revenue entered instead of net taxable income.
- Annual figure entered as monthly income.
- Duplicate top-up amount added to mandatory amount.

Fix:

1. Use net taxable income after expenses.
2. Confirm annual versus monthly units.
3. Compare fund deposits already made.

### Keren Hishtalmut deduction is lower than deposit

Cause: the deduction ceiling is lower than the profit-exempt ceiling.

Fix:

1. Accept that part of the deposit can be non-deductible.
2. Preserve the profit-exempt ceiling where appropriate.
3. Confirm with the annual tax return preparer.

### Pension tax credit is lower than expected

Cause: credit applies only up to the contribution base and depends on qualifying income.

Fix:

1. Check `pension_credit_base`.
2. Check `pension_deduction_base`.
3. Avoid treating tax credit and tax deduction as the same benefit.

## Product comparison problems

### Pension fund and Bituach Menahalim totals are the same

This is expected. The mandatory split can be identical before fees. The product decision depends on fees, insurance cost, medical underwriting, policy guarantees, survivors/disability coverage, and tax.

### Old Bituach Menahalim appears expensive

Do not evaluate old policies by fees alone. Pre-2013 policies may include a guaranteed annuity factor. Replacement can be irreversible.

### Survivors or disability cover changes after product change

Product switches can alter insurance definitions and coverage. Obtain licensed review before replacement.

## Testing problems

### `pytest` cannot import the client

Run tests from the package root:

```bash
pytest scripts/test_pension-contribution-calculator_client.py
```

The tests load the hyphenated script path through `importlib`.

### CLI command not found

Run the script directly:

```bash
python scripts/pension-contribution-calculator-cli.py --help
```

Install development requirements when `typer` or `click` is missing:

```bash
python -m pip install -r requirements-dev.txt
```

### JSON rate table fails to load

Cause: unknown field or malformed JSON.

Fix:

1. Compare keys to `RateTable`.
2. Remove unsupported keys.
3. Keep rates as decimals, not percentages. Use `0.06`, not `6`.

## Escalation triggers

Send the case to a licensed or specialist reviewer when any condition appears:

- Product replacement.
- Pre-2013 Bituach Menahalim.
- Severance withdrawal or settlement.
- Retirement pension drawdown.
- Cross-border tax residency.
- Divorce, death, disability claim, or beneficiary dispute.
- Employer arrears across multiple tax years.
- Large one-time bonus or retroactive salary payment.


## Bituach Menahalim eligibility warning appears

Cause: calculation uses `bituach_menahalim`. For policies opened from 01/09/2023, current rules generally restrict deposits to eligible excess after comprehensive pension funding.

Fix:

1. Identify whether the policy is legacy or new.
2. For a new policy, confirm salary above twice the average wage and funding of the comprehensive pension fund deposit ceiling before routing excess to the policy.
3. For a legacy policy, review policy terms, guaranteed annuity factor, insurance cost, and management fees before changing deposits.
4. Document the professional review in the payroll file.
