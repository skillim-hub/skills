# Israeli HR Compliance Reference

This is an offline source map and structured reference. Verify current rates, official forms, legal updates, and sector coverage before final action.


## Web-validated source map, accessed 04-06-2026

This is a non-network skill. It does not call a government API, expose webhook events, or depend on an external endpoint at runtime. Treat the following as a source and rate reference for local review.

| Check | Confirmed value or rule | Production handling |
|---|---|---|
| VAT | Standard Israeli VAT is 18% from 01-01-2025 and was still current in 2026 sources checked. | Use for freelancer invoice context only; do not use VAT registration to decide worker status. |
| Minimum wage | Adult general minimum from 01-04-2026: ₪6,443.85 monthly, ₪35.40 hourly on a 182-hour basis, ₪34.64 hourly on a 186-hour basis. | Configure by pay period; youth and sector rates differ. |
| Weekly work benchmark | 42 hours per week and 182 monthly hours where the 2018 shortening order applies. | Check role, sector, public-sector rules, night work, and exceptions. |
| Overtime premiums | General premium sequence is 125% for the first two overtime hours and 150% after that. | Calculate daily first and weekly after that. |
| Overtime cap | General cap: up to 12 hours per day and up to 16 overtime hours per week, subject to permits and exceptions. | Flag any schedule above the cap as critical until verified. |
| Pension | General mandatory-pension default: 6% employee, 6.5% employer pension, 6% employer severance. | Sector orders can improve rates; prior active pension affects timing. |
| Full severance funding | 8.33% monthly severance funding is the full severance-deposit benchmark for Section 14-style arrangements. | Verify written Section 14 arrangement and release terms. |
| Severance eligibility | Dismissed employee generally qualifies after one year of continuous work with one employer or workplace. | Check qualifying resignation and continuity exceptions. |
| Pregnancy and parenthood | Dismissal of a pregnant employee with at least six months of tenure requires a permit; post-parental-leave protection includes 60 days. | Pause adverse action until permit requirements and discrimination risks are reviewed. |
| Travel reimbursement | General daily cap is ₪22.60. | Pay according to commute facts and public-transport arrangement; sector rules may improve. |
| Convalescence pay | Private-sector daily value remains ₪418 in checked 2026 references; public-sector value and sector rules may differ. | Verify current freeze or update rule before annual payment. |
| Sick pay | First sickness day is unpaid, second and third are 50%, fourth onward is full daily wage, within accrued balance. | Check part-time, child illness, special leave, and sector rules. |
| Advance notice | Monthly employees: one day per month during the first 6 months, then 2.5 days per month through month 12, then 30 days. | Count calendar days and check hourly/daily formulas separately. |
| Wage deductions | Deduct only amounts expressly allowed by law, expansion order, collective agreement, or valid written authorization where allowed. | Treat fines, shortages, tools, uniforms, and damage deductions as high risk. |
| Contractor status | Formal contractor labels and invoices do not control; apply substantive employee-status tests. | Review control, integration, substitution, exclusivity, economic dependence, tools, and core activity. |

## Source categories

| Category | Source | Use |
|---|---|---|
| Primary legislation | Laws of the State of Israel | Mandatory rights, prohibited clauses, protected status |
| Regulations and permits | Ministry publications, permits, and regulations | Overtime limits, rest-day work, protected-status procedures |
| Extension orders | General and sector expansion orders | Pension, travel, convalescence, sector rights |
| Court guidance | Labor Court decisions | Employee-status tests, hearing duties, interpretation |
| Government portals | Ministry of Labor, Kol Zchut, National Insurance Institute, Tax Authority | Explanations, rates, forms, reporting |
| Business records | Payslips, attendance, pension statements, contracts | Evidence and calculations |

## Israeli regulation and lookup table

| Topic | Regulation or source | Lookup target | Notes |
|---|---|---|---|
| Minimum wage | Minimum Wage Law, 5747-1987 | Current monthly and hourly minimum wage | Verify rate for the exact pay period. Youth rates differ. |
| Working hours and overtime | Hours of Work and Rest Law, 5711-1951 | Regular week, daily limits, overtime premium, weekly rest | Sector and permit exceptions may apply. |
| Annual leave | Annual Leave Law, 5711-1951 | Vacation accrual, use, redemption | Depends on tenure, work pattern, and recordkeeping. |
| Sick leave | Sick Pay Law, 5736-1976 | Accrual and payment structure | Special arrangements may apply by sector or contract. |
| Severance | Severance Pay Law, 5723-1963 | Eligibility, qualifying resignation, calculation | Section 14 and pension deposits must be checked. |
| Advance notice | Advance Notice for Dismissal and Resignation Law, 5761-2001 | Required notice days | Different formulas for monthly and hourly/daily workers. |
| Wage protection | Protection of Wages Law, 5718-1958 | Payslip duties, wage timing, deductions | Unauthorized deductions are high risk. |
| Pregnancy and parenthood | Women's Employment Law, 5714-1954 | Protected periods, permit requirements, parental rights | Treat related adverse action as critical. |
| Equality | Equal Employment Opportunities Law, 5748-1988 | Discrimination in hiring and employment | Includes pregnancy, parenthood, sex, age, religion, nationality, reserve duty, and other protected traits. |
| Pension | Mandatory Pension Expansion Order | Start date and contribution rates | Prior active pension changes timing. |
| Travel expenses | Travel-expense expansion order | Daily/monthly reimbursement cap | Check current maximum and commute facts. |
| Convalescence pay | General collective arrangement and extension orders | Eligibility and daily rate | Check current rate and sector variations. |
| Sector orders | Guarding, cleaning, construction, hospitality, transport, caregiving, public-contractor orders | Enhanced wages, benefits, training, seniority | Sector classification can determine the answer. |
| National Insurance | National Insurance Institute rules | Maternity, reserve duty, work injury, reporting | Benefits eligibility is separate from employer obligations. |
| Tax and VAT | Israel Tax Authority guidance | Freelancer invoicing and payroll classification | Tax registration does not decide labor-law status. |

## Structured local request

```json
{
  "worker_type": "employee",
  "sector": "retail",
  "monthly_salary_ils": null,
  "hourly_rate_ils": 31.0,
  "weekly_hours": 46.0,
  "daily_hours": 9.5,
  "overtime_hours_weekly": 4.0,
  "tenure_months": 10,
  "part_time_ratio": 0.75,
  "had_active_pension_before_start": false,
  "has_pension_arrangement": false,
  "pension_start_month": null,
  "has_section_14": false,
  "employer_contribution_pension_pct": null,
  "employer_contribution_severance_pct": null,
  "is_parent_or_pregnant": false,
  "termination_reason": null,
  "notice_days_given": null,
  "contractor_controls": 0,
  "contract_text": "Hourly cashier. Closing time unpaid."
}
```

## Structured local response

```json
{
  "overall_risk": "critical",
  "finding_count": 3,
  "findings": [
    {
      "code": "MIN_WAGE_HOURLY",
      "risk": "critical",
      "title": "Hourly rate may be below Israeli minimum wage",
      "recommendation": "Verify the official hourly minimum for the pay period, raise the rate, and calculate arrears.",
      "law_refs": ["Minimum Wage Law, 5747-1987"]
    }
  ],
  "missing_facts": ["Current official rate confirmation"],
  "disclaimer": "Compliance triage only. Verify current law and obtain professional advice for high-risk action."
}
```

## Error table

| Error code | Meaning | Likely cause | Fix |
|---|---|---|---|
| `INVALID_WORKER_TYPE` | Worker category is not recognized | Typo or unsupported value | Use `employee`, `contractor`, `candidate`, or `unknown` |
| `NEGATIVE_AMOUNT` | Money field is below zero | Bad import or refund entered as wage | Correct input and rerun |
| `HOURS_OUT_OF_RANGE` | Hours exceed a plausible limit | Weekly/daily fields swapped or duplicate totals | Validate attendance records |
| `MISSING_WAGE_BASIS` | No wage field exists | Salary omitted | Add monthly, hourly, daily, or piecework amount |
| `MISSING_TENURE` | Tenure needed for notice, pension, severance, or convalescence | Start date omitted | Add start date or tenure months |
| `UNKNOWN_SECTOR_ORDER` | Sector may have special expansion order | Broad or unclear sector description | Select exact sector and verify order |
| `PROTECTED_STATUS_AMBIGUOUS` | Protected-status facts incomplete | Pregnancy, fertility treatment, parental leave, reserve duty, disability, or union facts unclear | Ask targeted follow-up and avoid adverse action |
| `RATE_STALE` | Configured rate may not match pay period | Rate not verified after update | Refresh from official source |
| `DOCUMENT_TOO_SHORT` | Text review has too little substance | Empty or summary-only document | Request contract, policy, payslip, or full clause |
| `CLI_INPUT_ERROR` | JSON cannot be parsed | Invalid file or malformed JSON | Validate JSON and rerun CLI |

## Example: minimum wage review

Request:

```json
{
  "worker_type": "employee",
  "hourly_rate_ils": 31.0,
  "weekly_hours": 38.0,
  "tenure_months": 2,
  "contract_text": "Training shifts are unpaid."
}
```

Expected response excerpt:

```json
{
  "overall_risk": "critical",
  "findings": [
    {"code": "MIN_WAGE_HOURLY", "risk": "critical"},
    {"code": "UNPAID_TRAINING_TIME", "risk": "high"}
  ]
}
```

## Example: contractor-status review

Request:

```json
{
  "worker_type": "contractor",
  "sector": "tech",
  "contractor_controls": 5,
  "tenure_months": 18,
  "contract_text": "Contractor works full time from company office and requires manager approval for vacation."
}
```

Expected response excerpt:

```json
{
  "overall_risk": "high",
  "findings": [
    {"code": "CONTRACTOR_MISCLASSIFICATION", "risk": "high"}
  ]
}
```

## Rate configuration

The helper stores configurable defaults in `ComplianceConfig`. These values are examples for local validation and tests. Before production use, confirm the current minimum wage, travel reimbursement cap, convalescence rate, pension rates, severance component, and sector-specific rates. Record source, effective date, and retrieval date.

## Citation practice

A compliance memo should name the source category and exact source to verify:

- Rule: Minimum Wage Law, 5747-1987; official minimum wage publication for the relevant pay period.
- Evidence: payslip, attendance export, agreement clause.
- Caveat: rate and sector coverage require current verification.

## Data retention

Redact ID numbers, bank details, pension account identifiers, medical details, child names, immigration documents, and home addresses unless strictly needed.
