# Test Scenarios

Use these scenarios to validate calculations, payroll workflows, and year-end processes. Amounts use 2026 defaults.

| # | Scenario | Input | Expected focus |
|---:|---|---|---|
| 1 | Basic employee pension | Gross ₪10,000 | Employee ₪600, employer ₪650, severance ₪600 |
| 2 | Employee with Keren Hishtalmut | Gross ₪10,000, Hishtalmut yes | Employee fund ₪250, employer fund ₪750 |
| 3 | Full Section 14 | Gross ₪10,000, Section 14 yes | Severance ₪833 |
| 4 | Partial pensionable salary | Gross ₪15,000, pensionable ₪12,000 | Notes flag lower pensionable salary |
| 5 | Bituach Menahalim | Gross ₪20,000, product policy | Full retirement deposit routed to policy bucket |
| 6 | Pension fund ceiling | Gross ₪40,000, Section 14 yes | Comprehensive cap reached, excess routed |
| 7 | Keren Hishtalmut above cap | Gross ₪20,000, Hishtalmut yes | Taxable employer excess ₪321.60 |
| 8 | No Keren Hishtalmut | Gross ₪20,000 | Training fund values zero |
| 9 | High salary, no Section 14 | Gross ₪32,000 | Check comprehensive ceiling and notes |
| 10 | New employee with existing arrangement | Start date plus existing coverage | Start from day one, retro payment outside calculation |
| 11 | New employee without existing arrangement | No prior coverage | Start after six months, no retro coverage |
| 12 | Freelancer low income | Annual net ₪60,000, age 30 | Mandatory pension ₪2,670 |
| 13 | Freelancer at half average wage | Annual net ₪82,614, age 30 | Entire income in low bracket |
| 14 | Freelancer at full average wage | Annual net ₪165,228, age 30 | Low plus high bracket |
| 15 | Freelancer high income | Annual net ₪300,000, age 40 | Mandatory pension capped near ₪14,044.38 |
| 16 | Freelancer first year | Annual net ₪180,000, first-year yes | Mandatory pension zero |
| 17 | Freelancer under age 21 | Age 20 | Mandatory pension zero |
| 18 | Freelancer at retirement age | Age 67, retirement age 67 | Mandatory pension zero |
| 19 | Keren Hishtalmut self-employed deduction cap | Annual net ₪400,000, deposit ₪20,566 | Deductible ₪13,203 |
| 20 | Keren Hishtalmut above profit ceiling | Deposit ₪25,000 | Profit-exempt amount capped at ₪20,566 |
| 21 | Maximum pension benefit room | Income ₪232,800, pension deposit ₪38,412 | Credit base ₪12,804, deduction base ₪25,608 |
| 22 | Pension deposit below mandatory | Income ₪180,000, pension deposit ₪1 | Warning note |
| 23 | Zero freelancer income | Annual net ₪0 | Mandatory pension zero |
| 24 | Invalid negative salary | Gross -₪1 | Validation error |
| 25 | Invalid product code | Product `other` | Validation error |
| 26 | Rate table override | JSON with tax year 2027 | Defaults retained for omitted fields |
| 27 | Unknown rate key | JSON with unsupported field | Validation error |
| 28 | CLI employee JSON | Employee command with `--json` | JSON contains expected keys |
| 29 | CLI rates | `rates --json` | Rate table serializes |
| 30 | Batch payroll export | Three employees in CSV example | Output rows contain six payroll columns |

## Manual acceptance tests

### A. Payroll reconciliation

1. Run scenario 1.
2. Enter employee pension as payroll deduction.
3. Enter employer pension and severance as employer costs.
4. Confirm total monthly transfer equals ₪1,850.
5. Save output with payslip.

### B. High-salary routing

1. Run scenario 6.
2. Confirm `comprehensive_pension_fund_deposit` equals the monthly cap.
3. Confirm `supplemental_or_policy_deposit` is positive.
4. Verify transfer file contains two routing lines when required by the fund.

### C. Freelancer year-end

1. Run scenario 15.
2. Compare mandatory pension to actual deposits.
3. Run scenario 21 to test voluntary room.
4. Confirm accountant accepts deduction and credit bases.

### D. Hebrew localization

1. Use `SKILL_HE.md`.
2. Confirm values are formatted with ₪.
3. Confirm dates in operational checklists use DD-MM-YYYY style where a date is entered.
4. Confirm terminology uses קרן פנסיה, ביטוח מנהלים, קרן השתלמות, תגמולים, פיצויים, הכנסה חייבת, and שכר מבוטח.
