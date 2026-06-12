# Workflow Guide

## Workflow 1: onboard a new employee

### Inputs

- Start date.
- Gross salary.
- Pensionable salary definition.
- Existing pension arrangement status at hiring.
- Product selected by employee.
- Section 14 status.
- Keren Hishtalmut entitlement.
- Fund identifiers and employee identity details.

### Steps

1. Collect signed employment agreement and onboarding forms.
2. Determine whether the employee had active pension coverage on the start date.
3. Set the pension start rule:
   - Existing arrangement: first day, paid retroactively after three months or tax-year end if earlier.
   - No existing arrangement: after six months, prospectively.
4. Run the employee calculation.
5. Review the notes for:
   - Pensionable salary lower than gross salary.
   - Comprehensive pension fund ceiling breach.
   - Keren Hishtalmut taxable employer excess.
   - Section 14 treatment.
6. Enter payroll deductions and employer costs.
7. Generate the fund transfer file.
8. Reconcile fund confirmation against payroll.
9. Store input, output, transfer file, confirmation, and approval.

### Example

```bash
python scripts/pension-contribution-calculator-cli.py employee \
  --gross-salary 18500 \
  --hishtalmut \
  --json
```

## Workflow 2: monthly payroll close for a small business

1. Export active employees with gross salary, pensionable salary, product type, Keren Hishtalmut entitlement, and Section 14 status.
2. Run batch calculations through the client helper or payroll export example.
3. Compare employee deductions to payroll.
4. Compare employer pension, severance, and Keren Hishtalmut costs to accounting entries.
5. Review exception report:
   - Negative or missing salary.
   - Pensionable salary below gross.
   - High salary exceeding comprehensive fund ceiling.
   - Keren Hishtalmut taxable excess.
   - New employee waiting period.
6. Create payment files.
7. Upload to the clearing system or fund interface.
8. Verify accepted deposits.
9. Resolve rejections before payroll lock.

## Workflow 3: freelancer annual pension check

### Inputs

- Annual net taxable income after deductible expenses.
- Age at 31-12.
- Business opening year.
- Deposits already made to pension and Keren Hishtalmut.
- Accountant's estimated taxable income.

### Steps

1. Use annual net taxable income, not invoices or bank deposits.
2. Mark first-year exemption only when applicable.
3. Run:

```bash
python scripts/pension-contribution-calculator-cli.py self-employed \
  --annual-income 180000 \
  --age 36 \
  --pension-deposit 14044 \
  --hishtalmut-deposit 20566 \
  --json
```

4. Compare existing pension deposits to mandatory annual pension.
5. Review remaining pension tax-benefit room.
6. Review Keren Hishtalmut deductible and profit-exempt amounts.
7. Deposit before 31-12 where relevant.
8. Save fund confirmations for the annual tax return.

## Workflow 4: year-end top-up planning for a freelancer

1. Request profit estimate from bookkeeping.
2. Calculate mandatory pension.
3. Enter actual deposits already made.
4. Add proposed top-up amount.
5. Re-run until remaining pension room and Keren Hishtalmut limits are acceptable.
6. Confirm cash-flow constraints.
7. Submit deposits through fund portal.
8. Save confirmations and accountant memo.

### Decision rule

- If mandatory pension deposit is missing, fund the mandatory amount first.
- If pension tax-benefit room remains and cash flow allows, consider pension top-up.
- If Keren Hishtalmut profit-exempt ceiling remains, consider using it before ordinary taxable savings.
- If the person is near retirement or has foreign tax exposure, obtain professional review.

## Workflow 5: compare pension fund and Bituach Menahalim

### Inputs

- Salary and pensionable salary.
- Existing product statements.
- Management fees on deposits and balance.
- Insurance premiums.
- Disability cover definitions.
- Survivors cover.
- Guaranteed annuity factor if any.
- Underwriting status and exclusions.

### Steps

1. Run the comparison command.
2. Confirm total contribution split is the same before fees.
3. Compare product routing:
   - Pension fund may split excess above comprehensive fund ceiling.
   - Bituach Menahalim routes deposits into policy terms.
4. Review non-calculator factors:
   - Fees.
   - Insurance cost.
   - Guaranteed annuity factor.
   - Policy age.
   - Surrender or transfer consequences.
   - Tax treatment.
5. Do not replace an old policy solely due to monthly deposit calculations.
6. Record recommendation source and license status when advice is provided.

## Workflow 6: handle Keren Hishtalmut above the salary ceiling

1. Run employee calculation with `--hishtalmut`.
2. Check `employer_hishtalmut_taxable`.
3. Add taxable excess to payroll as an employer benefit.
4. Keep the full deposit in the fund if the employer policy grants it.
5. Reconcile tax gross-up if the employer chooses to absorb tax.
6. Show the taxable benefit on the payslip.

## Workflow 7: correct a rejected pension transfer

1. Read rejection reason from fund or clearing interface.
2. Classify:
   - Identity mismatch.
   - Missing fund member number.
   - Deposit above comprehensive ceiling.
   - Wrong product type.
   - Negative or impossible amount.
   - Missing split between תגמולים and פיצויים.
3. Correct the input or split excess into supplemental routing.
4. Re-run the calculator.
5. Regenerate transfer file.
6. Upload correction.
7. Store rejection and correction trail.

## Workflow 8: annual rate update

1. Duplicate current rate table.
2. Verify each ceiling against official sources.
3. Update `RateTable` defaults.
4. Update `metadata.json` version and date.
5. Update `references/api-reference.md`.
6. Update English and Hebrew examples.
7. Run tests.
8. Add a changelog entry.
9. Archive old rate table and evidence.
