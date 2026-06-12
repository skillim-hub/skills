# Reference: Israeli labor-law sources and local helper interface

This skill is not a remote API integration. It uses official Israeli legal sources, public databases, and a local Python/CLI helper. Treat every legal rate as date-sensitive and verify against an official source before payroll action.

## Source hierarchy

1. Primary legislation and official publications.
2. Ministry of Labor pages, calculators, permits, collective agreement databases, and extension orders.
3. National Insurance Institute guidance for birth, injury, unemployment, insolvency, and benefit eligibility.
4. Tax Authority guidance for Form 161, pension tax treatment, and reporting.
5. Collective agreements and extension orders.
6. Kol Zchut as a practical secondary explainer.
7. Histadrut or worker-committee publications as useful context, then verify the actual agreement or order.

## Core laws and regulations

| Topic | Hebrew source name | English name | Typical use |
|---|---|---|---|
| Minimum wage | חוק שכר מינימום, תשמ"ז-1987 | Minimum Wage Law | Monthly/hourly minimum wage and enforcement |
| Hours and rest | חוק שעות עבודה ומנוחה, תשי"א-1951 | Hours of Work and Rest Law | Overtime, night work, weekly rest, permits |
| Severance | חוק פיצויי פיטורים, תשכ"ג-1963 | Severance Pay Law | Dismissal, resignation treated as dismissal, payment deadline |
| Women and parenthood | חוק עבודת נשים, תשי"ד-1954 | Employment of Women Law | Pregnancy, fertility, birth and parenting period, dismissal permits |
| Annual leave | חוק חופשה שנתית, תשי"א-1951 | Annual Leave Law | Vacation accrual, vacation pay, redemption |
| Sick pay | חוק דמי מחלה, תשל"ו-1976 | Sick Pay Law | Sick day accrual and graduated pay |
| Notice | חוק הודעה מוקדמת לפיטורים ולהתפטרות, תשס"א-2001 | Prior Notice Law | Notice periods and pay in lieu |
| Written terms | חוק הודעה לעובד ולמועמד לעבודה, תשס"ב-2002 | Notice to Employee/Candidate Law | Employment terms notice and candidate notifications |
| Payslip and deductions | חוק הגנת השכר, תשי"ח-1958 | Wage Protection Law | Payslips, deductions, wage delays, records |
| Pension | צו הרחבה לפנסיה חובה | Mandatory Pension Extension Order | Pension and severance contributions |
| Collective agreements | חוק הסכמים קיבוציים, תשי"ז-1957 | Collective Agreements Law | Workplace and sector collective agreements |
| Labor disputes | חוק יישוב סכסוכי עבודה, תשי"ז-1957 | Settlement of Labor Disputes Law | Collective dispute process |
| Equal opportunities | חוק שוויון ההזדמנויות בעבודה, תשמ"ח-1988 | Equal Employment Opportunities Law | Discrimination and retaliation |
| Sexual harassment | חוק למניעת הטרדה מינית, תשנ"ח-1998 | Prevention of Sexual Harassment Law | Employer procedures and complaint handling |
| Disability | חוק שוויון זכויות לאנשים עם מוגבלות, תשנ"ח-1998 | Equal Rights for People with Disabilities Law | Reasonable accommodation |

## Public websites and identifiers

| Source | URL pattern | Data obtained | Notes |
|---|---|---|---|
| Ministry of Labor | `https://www.gov.il/he/departments/labor` | rates, permits, enforcement, forms | Verify minimum wage, protected dismissal permits, youth employment |
| Ministry collective agreements database | `https://workagreements.labor.gov.il/` and `https://workagreements.labor.gov.il/api/GetSelect/DownLoadFile?FileExtension=<pdf|docx>&FileName=<agreement_number>&Type=Agreements` | collective agreements and extension orders | Search by employer, sector, agreement number, and date; do not assume every endpoint is public or stable |
| National Insurance Institute | `https://www.btl.gov.il` | birth allowance, maternity/partner benefits, employer insolvency | Benefit eligibility is separate from job protection |
| Tax Authority | `https://www.gov.il/he/departments/israel_tax_authority` | Form 161, tax reporting, pension tax | Required at termination |
| Official legislation databases | official legal publications | full legislation text | Use for exact legal wording |
| Kol Zchut | `https://www.kolzchut.org.il` | practical summaries | Secondary reference; verify rates |
| Histadrut | `https://www.histadrut.org.il` | union guidance, campaigns, sector info | Use to find possible agreement, then verify agreement text |


## Web-validated current facts as of 02/06/2026

Treat this table as a dated verification snapshot. Re-check before live use.

| Item | Validated value | Official or primary source to re-check | Notes |
|---|---:|---|---|
| Standard VAT rate | 18% from 01/01/2025 | Tax Authority VAT history and government VAT decision | Included because invoice-worker workflows mention VAT; not used as a payroll rate. |
| Adult minimum wage, monthly | ₪6,443.85 from 01/04/2026 | National Insurance minimum wage table; Ministry of Labor updates | Applies to adult full-time wage-floor checks. |
| Adult minimum wage, hourly, 182-hour basis | ₪35.40 from 01/04/2026 | National Insurance minimum wage table | Default used by `DEFAULT_MINIMUM_WAGE`. |
| Adult minimum wage, hourly, 186-hour basis | ₪34.64 from 01/04/2026 | National Insurance minimum wage table | Keep if comparing older payroll configurations. |
| Private-sector weekly baseline | 42 hours | Extension order and Ministry/Kol Zchut summaries | Daily thresholds still require schedule-specific review. |
| Weekday overtime premiums | 125% for first two overtime hours, then 150% | Ministry of Labor and Hours of Work and Rest Law summaries | Rest-day and holiday work can require higher combined rates. |
| Severance baseline | One monthly wage per year for monthly workers, subject to exceptions | Severance Pay Law and official summaries | Variable pay, changed scope, Section 14, and fund balances can change the result. |
| Section 14 / severance fund check | 6% mandatory partial deposit; 8.33% full monthly severance deposit may cover full liability if valid | Pension extension order summaries and official insolvency guidance | Always inspect pension reports and written arrangements. |
| Form 161 | Tax Authority retirement/termination reporting form | Tax Authority service page | Required termination-tax workflow check before releasing severance funds. |
| Maternity allowance period | 15 weeks/105 days full; 8 weeks/56 days partial | National Insurance maternity allowance page | Benefit eligibility is separate from dismissal protection. |
| Parenting hour | 1 hour per day for 4 months, generally at least 174 monthly hours | Ministry/Kol Zchut parental-rights pages | Use professional term `שעת הורות`; legacy term `שעת הנקה` may appear in sources. |

## Local helper interface

### Python client

File: `scripts/labor_law_advisor_client.py`

Import via the alias module in normal Python:

```python
from labor_law_advisor_client import LaborLawAdvisor

advisor = LaborLawAdvisor()
result = advisor.minimum_wage(monthly_salary=3000, position_fraction=0.5)
print(result.to_dict())
```

### Async usage

```python
import asyncio
from labor_law_advisor_client import LaborLawAdvisor

async def main():
    advisor = LaborLawAdvisor()
    result = await advisor.aminimum_wage(hourly_wage=34, regular_hours=120)
    print(result.shortfall)

asyncio.run(main())
```

### CLI

```bash
labor-law-advisor min-wage --monthly-salary 3000 --position-fraction 0.5
labor-law-advisor overtime --hourly-rate 40 --daily-hours 11 --daily-threshold 8.6
labor-law-advisor severance --monthly-salary 12000 --years 3 --months 4
labor-law-advisor vacation --years 6 --workweek-days 5
labor-law-advisor sick-pay --daily-wage 500 --sick-days 5
```

## Request and response examples

### Minimum wage request

```json
{
  "operation": "minimum_wage",
  "monthly_salary": 3000,
  "position_fraction": 0.5,
  "effective_date": "2026-04-01"
}
```

Response:

```json
{
  "operation": "minimum_wage",
  "required": 3221.93,
  "actual": 3000.0,
  "shortfall": 221.93,
  "compliant": false,
  "currency": "ILS",
  "effective_date": "2026-04-01",
  "notes": [
    "Rate is date-sensitive; verify against the Ministry of Labor before payroll action."
  ]
}
```

### Overtime request

```json
{
  "operation": "overtime",
  "hourly_rate": 40,
  "daily_hours": 11,
  "daily_threshold": 8.6
}
```

Response:

```json
{
  "operation": "overtime",
  "regular_hours": 8.6,
  "first_overtime_hours": 2.0,
  "additional_overtime_hours": 0.4,
  "total_pay": 468.0,
  "currency": "ILS"
}
```

### Severance request

```json
{
  "operation": "severance",
  "monthly_salary": 12000,
  "years": 3,
  "months": 4,
  "section14_balance": 35000
}
```

Response:

```json
{
  "operation": "severance",
  "estimated_statutory": 40000.0,
  "covered_by_section14_balance": 35000.0,
  "possible_top_up": 5000.0,
  "eligible_by_tenure": true,
  "currency": "ILS"
}
```

### Collective coverage request

```json
{
  "operation": "collective_check",
  "sector": "cleaning",
  "histadrut_dues_on_payslip": true,
  "workplace_committee": false
}
```

Response:

```json
{
  "operation": "collective_check",
  "risk_level": "high",
  "recommended_sources": [
    "Ministry of Labor collective agreements database",
    "Sector extension orders",
    "Employment agreement and payslips"
  ],
  "next_steps": [
    "Identify employer legal name, sector, site, and job title",
    "Search agreement and extension order coverage clauses",
    "Compare with statutory minimum and employment contract"
  ]
}
```

### Parental protected-status request

```json
{
  "operation": "parental_rights_triage",
  "pregnant": true,
  "employer_action": "dismissal",
  "months_employed": 7
}
```

Response:

```json
{
  "operation": "parental_rights_triage",
  "risk_level": "critical",
  "permit_check_required": true,
  "protected_statuses": ["pregnancy"],
  "next_steps": [
    "Confirm exact dates, tenure, employer knowledge, and proposed action",
    "Check whether a Ministry of Labor permit is required before action",
    "Escalate before dismissal, non-renewal, pay cut, or hours reduction"
  ]
}
```

## Error table

| Code | Meaning | Fix |
|---|---|---|
| `missing_salary` | Required salary field omitted | Provide monthly salary or hourly wage |
| `invalid_fraction` | Position fraction not between 0 and 1 | Use `0.5` for 50% or `1.0` for full time |
| `invalid_hours` | Hours are negative or impossible | Check attendance log |
| `missing_tenure` | Severance tenure omitted | Provide years/months or start/end dates |
| `date_sensitive_rate` | Rate may have changed | Verify official rate for the relevant date |
| `collective_unknown` | Sector or employer coverage unclear | Search collective agreements and extension orders |
| `protected_status` | Pregnancy/parenting/fertility protection may apply | Escalate before termination or reduction |
| `classification_uncertain` | Freelancer may be employee | Apply employee-status checklist and seek legal review |
| `section14_unknown` | Pension/severance arrangement missing | Get pension reports and employment agreement |
| `insufficient_documents` | Calculation cannot be validated | Request payslips, attendance records, fund reports |

## Regulatory checks by topic

### Minimum wage

- Effective date of rate.
- Full-time monthly baseline and hourly baseline.
- Youth, apprenticeship, adjusted wage, foreign worker, or household worker rules.
- Deductions and reimbursements.
- Overtime separated from base wage.

### Overtime

- Daily threshold by workweek and sector.
- Weekly threshold and daily double-counting.
- Night work, pre-holiday days, holidays, and weekly rest.
- Global overtime validity.
- Permits and collective arrangements.

### Severance

- One-year threshold and continuity.
- Dismissal or resignation treated as dismissal.
- Last salary, fixed additions, commissions, and reductions.
- Section 14 scope, fund balance, release forms, and Form 161.
- Payment date and wage-delay penalties.

### Parental rights

- Pregnancy, fertility treatment, adoption, surrogacy, birth, partner leave, unpaid extension, return-to-work period.
- Tenure and permit route.
- National Insurance benefit eligibility.
- Prohibited reduction in scope or income.

### Histadrut and collective arrangements

- Dues or committee indications.
- Employer association membership.
- Sector extension orders.
- Coverage, exclusions, and effective dates.
- More favorable terms: pension, study fund, vacation, convalescence, shift premiums, travel, clothing, seniority increments.
