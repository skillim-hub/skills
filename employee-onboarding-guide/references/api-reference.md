# Israeli Regulation and Workflow Reference

This file is a reference for onboarding workflows in Israel. It lists authorities, legal areas, local data models, CLI request and response shapes, and error tables. It is not a live API manual. Verify current official instructions before production use.

## Authority and regulation map

| Topic | Authority or framework | Onboarding use | Artifact |
|---|---|---|---|
| Employee tax card and withholding | Israel Tax Authority | Form 101, tax coordination, employee tax facts | Form 101 and tax coordination approval |
| National Insurance and health insurance contributions | National Insurance Institute | Multiple income coordination and payroll status facts | Coordination approval or payroll note |
| Pension and provident arrangements | Capital Market, Insurance and Savings Authority, pension providers | Existing pension status, fund details, first deposit timing | Pension intake form |
| Employment terms and working hours | Ministry of Labor and employment legislation | Terms notice, hours, rest, overtime, youth work | Employment terms notice |
| Privacy and employee records | Privacy Protection Authority and privacy law | Secure storage of ID, bank, pension, tax, and medical documents | Privacy and access-control checklist |
| Prevention of sexual harassment | Workplace prevention framework | Policy route, contact person, complaint handling | Employee acknowledgment |
| Occupational safety | Safety legislation and sector rules | Safety briefing and role-specific training | Safety checklist |
| Foreign workers | Population and Immigration Authority and sector rules | Permit, visa, employer authorization, health insurance | Permit review checklist |

## Local data model

```json
{
  "employee": {
    "full_name": "Dana Levi",
    "start_date": "01-09-2026",
    "employment_type": "employee",
    "role": "Sales Coordinator",
    "salary_type": "monthly",
    "has_other_employer": true,
    "has_active_pension": true,
    "remote": false,
    "foreign_worker": false,
    "youth": false
  },
  "payroll": {
    "monthly_salary_nis": 12000,
    "hourly_rate_nis": null,
    "payment_day": 9
  },
  "documents": {
    "form_101": "pending",
    "bank_details": "received",
    "tax_coordination": "missing",
    "national_insurance_coordination": "missing",
    "employment_notice": "drafted"
  }
}
```

## Local CLI reference

The local helper does not transmit employee data. It reads and writes JSON files under a local storage directory.

### Create record

Request:

```bash
employee-onboarding-guide create --name "Dana Levi" --start-date 01-09-2026 --role "Sales Coordinator" --other-employer --active-pension
```

Response:

```json
{
  "id": "rec_8f3a2b91",
  "environment": "sandbox",
  "record_file": ".onboarding-records/rec_8f3a2b91.json",
  "ok": true
}
```

### Generate checklist from the created record

Request:

```bash
employee-onboarding-guide checklist --id rec_8f3a2b91
```

Response excerpt:

```markdown
# Onboarding Checklist: Dana Levi

Start date: 01-09-2026
...
```

### Validate record

Request:

```bash
employee-onboarding-guide validate --id rec_8f3a2b91
```

Response:

```json
{
  "ok": true,
  "errors": [],
  "warnings": [
    "Employee has another employer: request tax coordination before payroll close."
  ],
  "next_actions": [
    "Request completed Form 101 before payroll close."
  ]
}
```

## Error table

| Code | Meaning | Fix |
|---|---|---|
| DATE_FORMAT_INVALID | Date is not DD-MM-YYYY or DD/MM/YYYY | Use 01-09-2026 for English or 01/09/2026 for Hebrew. |
| FORM_101_MISSING | Employee workflow lacks Form 101 status | Request Form 101 before payroll close. |
| CONTRACTOR_FORM_101 | Supplier workflow includes Form 101 | Remove Form 101 and use supplier onboarding. |
| OTHER_EMPLOYER_NO_TAX_COORDINATION | Another employer exists but no tax coordination approval | Request approval and ask payroll how to process until received. |
| OTHER_EMPLOYER_NO_NI_COORDINATION | Another employer exists but National Insurance coordination was not checked | Ask payroll whether coordination is required. |
| ACTIVE_PENSION_NO_DETAILS | Active pension exists but fund details are missing | Request fund name, account or policy number, and provider contact. |
| FOREIGN_WORKER_REVIEW_REQUIRED | Foreign-worker facts require review | Verify permit, visa, employer authorization, insurance, and payroll route. |
| YOUTH_REVIEW_REQUIRED | Youth employee facts require review | Verify age, permitted hours, role restrictions, and safety training. |
| BANK_DETAILS_MISSING | Salary payment details are missing | Request bank, branch, account number, and confirmation if needed. |
| EMPLOYMENT_NOTICE_MISSING | Written terms are not drafted or delivered | Prepare terms notice or employment agreement. |
| INSECURE_CHANNEL | Sensitive documents were sent through an unapproved channel | Move records to restricted storage and remove unnecessary copies. |

## Official-source verification checklist

- Verify the current Form 101 version and submission process with the Israel Tax Authority.
- Verify National Insurance coordination requirements with the National Insurance Institute or payroll provider.
- Verify pension timing and default arrangement rules with payroll or a licensed pension professional.
- Verify youth, foreign-worker, safety, and working-hours rules with the relevant authority.
- Verify employee-record retention and access rules with privacy counsel when needed.


## Web-validated 2026 reference notes

These figures were verified on the access date listed in `references/verification-log.md`. Do not hard-code them into payroll calculations without rechecking the official source.

| Topic | 2026 verified value or status | Operational use |
|---|---|---|
| VAT | Standard VAT remains 18% from 01-01-2025 onward in official Tax Authority and Knesset/government sources. | Relevant only when closing prior supplier invoices during freelancer-to-employee conversion. |
| Form 101 | Employee must submit Form 101 to the employer within 7 days of starting work and again at the beginning of each tax year. | Add to employee document request and annual renewal reminder. |
| National Insurance reduced bracket | ₪7,703 from 01-01-2026 for salaried employee contribution tables. | Use only as reference for payroll provider review. |
| National Insurance maximum income | ₪51,910 from 01-01-2026 for salaried employee contribution tables. | Use only as reference for payroll provider review. |
| Health insurance deduction | 3.23% up to the reduced bracket and 5.17% above it for salaried employees, with 2025 effective dates and 2026 bracket. | Do not calculate manually outside payroll. |
| Pension waiting period | 6 months without prior active coverage; day-one entitlement with prior coverage, with first payment after 3 months or at tax-year end, whichever is earlier, retroactive to start. | Add pension continuity question. |
| Live APIs and webhooks | No external API endpoint or webhook event is required or referenced by this package. | Keep the helper local-only. |
