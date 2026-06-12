# API and Regulation Reference

This package is a non-API calculator. Treat the importable helper, CLI commands, rate-table schema, source registry, request/response examples, and operational error tables as the operational reference.

## Source registry

Verify these sources during each annual rate update. Prefer official publications when available. See `references/verification-log.md` for the web-validated two-pass log used for this release.

| Source area | Primary source to verify | Used for |
|---|---|---|
| Average wage under National Insurance definitions | National Insurance Institute average-wage page, `btl.gov.il` | Average wage, half-average bracket, self-employed mandatory pension base |
| Mandatory pension for employees | Extension Order for Comprehensive Pension Insurance in the Economy; Ministry of Labor guidance; Kol Zchut summaries | Employee contribution, employer contribution, severance minimum, start-date rules |
| Self-employed mandatory pension | Ministry of Finance self-employed pension page; Kol Zchut self-employed pension procedure | 4.45% and 12.55% brackets, first-year exemption, age scope |
| Income Tax Ordinance and regulations | Israel Tax Authority annual booklets and current ordinance text | Pension credit, pension deduction, Keren Hishtalmut tax treatment |
| Capital Market, Insurance and Savings Authority | Uniform reporting protocol and employer reporting guidance on `gov.il` | Comprehensive pension fund deposit ceiling, product categories, reporting rules |
| Keren Hishtalmut guidance | Tax Authority publications, Kol Zchut summaries, and fund ceiling circulars | Employee salary ceiling, self-employed deduction and profit-exempt ceilings |
| Bituach Menahalim rules | Knesset publication on the 2023 restriction; Kol Zchut Bituach Menahalim page | Product comparison, new-policy eligibility, legacy-policy caution |
| Section 14 severance | Severance Pay Law, Section 14 approval, employment agreements, and Ministry of Labor severance guidance | 8.33% severance treatment and release rules |
| Uniform reporting interface | Capital Market Authority uniform protocol: `ממשק מעסיקים - דיווח שוטף`, `ממשק מעסיקים - דיווח שלילי`, `EVEMAS` | Payroll file controls and fund confirmation reconciliation |
| VAT rate | Tax Authority VAT history and Knesset order publication | Out-of-scope reference only; VAT is not used in contribution calculations |

No external production API host, endpoint path, or webhook event is used by this package. It exposes only the local Python helper and CLI.

## Versioned rate table

The local helper uses a `RateTable` dataclass. Treat it as an API contract for calculations.

```json
{
  "tax_year": 2026,
  "effective_from": "2026-01-01",
  "currency": "ILS",
  "employee_pension_rate": 0.06,
  "employer_pension_rate": 0.065,
  "employer_severance_min_rate": 0.06,
  "employer_severance_section14_rate": 0.0833,
  "hishtalmut_employee_rate": 0.025,
  "hishtalmut_employer_rate": 0.075,
  "hishtalmut_employee_salary_cap": 15712.0,
  "average_wage_monthly": 13769.0,
  "comprehensive_pension_monthly_deposit_cap": 5645.29,
  "self_pension_low_rate": 0.0445,
  "self_pension_high_rate": 0.1255,
  "self_hishtalmut_deduction_cap": 13203.0,
  "self_hishtalmut_profit_exempt_cap": 20566.0
}
```

### Rate-table validation rules

| Field | Validation |
|---|---|
| `tax_year` | Four-digit year |
| `effective_from` | ISO date, usually `YYYY-01-01` |
| Rate fields | Decimal values between `0` and `1` |
| Currency fields | Non-negative ILS amounts |
| Salary ceilings | Confirm against source publications before production |
| Unknown fields | Reject during JSON load |

## Local helper contract

### Employee request

```json
{
  "gross_salary": 20000,
  "pensionable_salary": 20000,
  "product": "pension_fund",
  "include_hishtalmut": true,
  "section14_full": false
}
```

### Employee response

```json
{
  "tax_year": 2026,
  "product": "pension_fund",
  "gross_salary": 20000.0,
  "pensionable_salary": 20000.0,
  "section14_full": false,
  "employee_pension": 1200.0,
  "employer_pension": 1300.0,
  "employer_severance": 1200.0,
  "total_retirement_deposit": 3700.0,
  "comprehensive_pension_fund_deposit": 3700.0,
  "supplemental_or_policy_deposit": 0.0,
  "employee_hishtalmut": 500.0,
  "employer_hishtalmut": 1500.0,
  "employer_hishtalmut_tax_free": 1178.4,
  "employer_hishtalmut_taxable": 321.6,
  "total_hishtalmut": 2000.0,
  "total_employee_cash_outflow": 1700.0,
  "total_employer_cash_cost": 4000.0,
  "total_monthly_deposit": 5700.0,
  "annualized_total_deposit": 68400.0,
  "notes": [
    "Employer training fund deposits above the salary ceiling are taxable income to the employee.",
    "Severance calculated at the 6% minimum contribution rate."
  ]
}
```

### Self-employed request

```json
{
  "annual_net_taxable_income": 260000,
  "age": 44,
  "first_year_business": false,
  "retirement_age": 67,
  "annual_pension_deposit": 38412,
  "annual_hishtalmut_deposit": 20566
}
```

### Self-employed response

```json
{
  "tax_year": 2026,
  "annual_net_taxable_income": 260000.0,
  "monthly_net_taxable_income": 21666.67,
  "age": 44,
  "first_year_business": false,
  "retirement_age_used": 67,
  "mandatory_pension_annual": 14044.38,
  "mandatory_pension_monthly_average": 1170.28,
  "low_bracket_annual_income": 82614.0,
  "high_bracket_annual_income": 82614.0,
  "annual_pension_deposit_entered": 38412.0,
  "pension_credit_base": 12804.0,
  "estimated_pension_tax_credit": 4481.4,
  "pension_deduction_base": 25608.0,
  "remaining_pension_room_for_benefit": 0.0,
  "annual_hishtalmut_deposit_entered": 20566.0,
  "hishtalmut_deductible_amount": 11700.0,
  "hishtalmut_profit_exempt_deposit": 20566.0,
  "hishtalmut_non_deductible_but_profit_exempt": 8866.0,
  "notes": [
    "Mandatory self-employed pension deposits do not increase above the annual average-wage ceiling."
  ]
}
```

### Product comparison request

```json
{
  "gross_salary": 24000,
  "include_hishtalmut": true,
  "section14_full": false
}
```

### Product comparison response

```json
{
  "headline": "Total required split is identical before product fees; routing, insurance cost, and policy terms differ.",
  "pension_fund": {
    "product": "pension_fund",
    "total_retirement_deposit": 4440.0
  },
  "bituach_menahalim": {
    "product": "bituach_menahalim",
    "total_retirement_deposit": 4440.0
  },
  "cautions": [
    "Compare management fees, disability cover, survivors cover, underwriting exclusions, and pre-2013 guaranteed annuity factors before replacing an existing policy."
  ]
}
```

## CLI reference

### Employee command

```bash
python scripts/pension-contribution-calculator-cli.py employee \
  --gross-salary 20000 \
  --pensionable-salary 18000 \
  --hishtalmut \
  --section14 \
  --json
```

Options:

| Option | Required | Meaning |
|---|---:|---|
| `--gross-salary` | Yes | Gross monthly salary in ₪ |
| `--pensionable-salary` | No | Pensionable monthly salary in ₪; defaults to gross salary |
| `--product` | No | `pension_fund` or `bituach_menahalim` |
| `--hishtalmut` | No | Include Keren Hishtalmut |
| `--section14` | No | Use 8.33% severance |
| `--json` | No | Print JSON output |

### Self-employed command

```bash
python scripts/pension-contribution-calculator-cli.py self-employed \
  --annual-income 180000 \
  --age 36 \
  --pension-deposit 20000 \
  --hishtalmut-deposit 20566 \
  --json
```

Options:

| Option | Required | Meaning |
|---|---:|---|
| `--annual-income` | Yes | Annual net taxable income in ₪ |
| `--age` | Yes | Age at tax-year end |
| `--first-year` | No | Mark first business year exemption |
| `--retirement-age` | No | Override retirement age |
| `--pension-deposit` | No | Actual annual pension deposit |
| `--hishtalmut-deposit` | No | Actual annual Keren Hishtalmut deposit |
| `--json` | No | Print JSON output |

## Error table

| Error | Trigger | Corrective action |
|---|---|---|
| `gross_salary must be non-negative` | Negative salary | Enter zero or positive amount |
| `pensionable_salary cannot exceed gross_salary` | Pensionable salary above gross | Correct salary basis |
| `product must be 'pension_fund' or 'bituach_menahalim'` | Unsupported product value | Use allowed product code |
| `age must be realistic` | Age below 0 or above 130 | Correct input |
| `Unknown rate fields` | JSON rate table contains unsupported field | Remove typo or update client contract |
| Fund rejects transfer | Deposit above product ceiling or invalid employee details | Split deposit or correct fund identifiers |
| Payroll taxable benefit mismatch | Keren Hishtalmut excess not taxed | Add taxable employer excess to payroll |
| Accountant rejects self-employed figure | Revenue used instead of net taxable income | Recalculate from annual profit after expenses |

## Regulation citation practice

When producing a payroll memo, include:

1. Tax year and rate table version.
2. Date the rates were checked.
3. Source name and URL or publication reference.
4. Employee or freelancer input assumptions.
5. Output with taxable exceptions.
6. Reviewer and approval date.

For legal or product-specific advice, attach the applicable legal source, product terms, fund confirmation, and professional opinion.


## Calculation record example

Generate a local record for audit trails and support handoffs:

```bash
python scripts/pension-contribution-calculator-cli.py employee --gross-salary 12000 --hishtalmut --json --record > /tmp/pcc-create-response.json
calc_id=$(python -c 'import json; print(json.load(open("/tmp/pcc-create-response.json", encoding="utf-8"))["id"])')
python scripts/pension-contribution-calculator-cli.py explain --from-json /tmp/pcc-create-response.json --id "$calc_id"
```

Response shape:

```json
{
  "environment": "sandbox",
  "id": "pcc-sandbox-2026-example",
  "kind": "employee",
  "result": {
    "gross_salary": 12000.0,
    "tax_year": 2026
  },
  "source": "cli"
}
```
