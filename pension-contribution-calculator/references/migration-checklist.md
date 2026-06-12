# Migration Checklist

Use this checklist when moving from a manual spreadsheet, old calculator, payroll macro, or previous package version.

## 1. Inventory current calculations

- List every current spreadsheet tab, payroll formula, macro, and manual adjustment.
- Identify rate sources used today.
- Identify tax-year ceilings hard-coded in payroll.
- Identify product routing assumptions.
- Identify where Keren Hishtalmut taxable excess is calculated.
- Identify where Section 14 is stored.
- Identify how self-employed year-end deposits are currently estimated.

## 2. Map fields

| Existing field | New input |
|---|---|
| Monthly gross salary | `gross_salary` |
| Pension salary / insured salary | `pensionable_salary` |
| Product name | `product` |
| Training fund flag | `include_hishtalmut` |
| Section 14 flag | `section14_full` |
| Annual profit | `annual_net_taxable_income` |
| Business first year | `first_year_business` |
| Age at year end | `age` |
| Actual pension deposit | `annual_pension_deposit` |
| Actual training fund deposit | `annual_hishtalmut_deposit` |

## 3. Validate rates

- Confirm tax year.
- Confirm average wage.
- Confirm comprehensive pension fund monthly deposit ceiling.
- Confirm employee and employer contribution rates.
- Confirm self-employed brackets.
- Confirm Keren Hishtalmut salary and annual ceilings.
- Confirm pension tax credit and deduction caps.
- Store source links and check date.

## 4. Run parallel payroll

1. Select at least ten employees:
   - Low salary.
   - Salary above Keren Hishtalmut ceiling.
   - Salary above comprehensive pension fund deposit ceiling.
   - Section 14.
   - No Section 14.
   - Pensionable salary below gross.
   - Bituach Menahalim.
2. Run old and new calculations side by side.
3. Investigate differences.
4. Classify differences:
   - Corrected bug.
   - Rate update.
   - Input mapping issue.
   - Product routing issue.
   - Taxable benefit issue.
5. Approve final mapping.

## 5. Run freelancer validation

- Test low income.
- Test high income above full average wage.
- Test first-year exemption.
- Test age exemption.
- Test full Keren Hishtalmut deposit.
- Test pension top-up to maximum benefit room.
- Compare with accountant's expected report.

## 6. Update operations

- Replace hard-coded spreadsheet rates with versioned `RateTable`.
- Store rate-table JSON with tax-year evidence.
- Add pytest execution to release checklist.
- Add CLI JSON output to audit archive where useful.
- Train payroll staff on notes in the result object.
- Add exception review for high salary and taxable benefits.

## 7. Cutover

- Freeze old spreadsheet.
- Export final reference outputs.
- Tag package version.
- Run full test suite.
- Run first live payroll in parallel.
- Reconcile fund confirmations.
- Sign off after all rejections are resolved.

## 8. Rollback

Maintain the old method for one payroll cycle only as a fallback. Do not maintain two active calculation sources long term. Dual systems cause rate drift and inconsistent audit trails.

## 9. Annual update migration

At each tax-year update:

1. Copy current rate table.
2. Enter new ceilings.
3. Update docs and examples.
4. Update tests that assert exact ceiling values.
5. Run all tests.
6. Add changelog entry.
7. Archive evidence and outputs.
