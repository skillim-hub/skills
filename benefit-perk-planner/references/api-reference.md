# Israeli API and Regulation Reference

This reference identifies official sources, public systems, and provider integration patterns relevant to Israeli benefit and perk planning. Use it as an implementation reference, not as legal, tax, payroll, pension, insurance, or investment advice. Verify current versions, forms, rates, and endpoints before production.

## Official sources to verify

| Area | Source type | Use |
|---|---|---|
| Pension and severance | Ministry of Labor publications, extension orders, labor law materials, pension remittance rules | Mandatory pension, severance, start dates, employer obligations |
| Income tax | Israel Tax Authority circulars, employer withholding instructions, benefit valuation materials | Payroll tax treatment, taxable benefit value, annual ceilings |
| VAT | Israel Tax Authority VAT guidance | Invoices, input VAT, reimbursement documentation |
| National Insurance | National Insurance Institute guidance | Employee and self-employed contributions |
| Keren Hishtalmut | Israel Tax Authority and Capital Market, Insurance and Savings Authority publications | Contribution ceilings, deductibility, exemptions, fund rules |
| Privacy | Protection of Privacy Law and Privacy Protection Authority guidance | Employee data, wellness privacy, vendor data processing |
| Employment classification | Labor law, case law, legal review | Contractor vs employee risk |
| Consumer protection | Consumer Protection Authority guidance | Subscription comparison, cancellation, consumer rights |
| Accessibility | Equal Rights for Persons with Disabilities framework | Inclusive communication and benefit access |

## Israel Tax Authority planning reference

```json
{
  "tax_year": 2026,
  "benefit_type": "meal_benefit",
  "employee_gross_salary_ils": 18000,
  "monthly_benefit_value_ils": 770,
  "provider_invoice_available": true,
  "employee_payment_required": false
}
```

Expected planning response:

```json
{
  "requires_payroll_review": true,
  "likely_documents": ["written policy", "provider invoice", "utilization export", "payroll approval"],
  "verify_with": ["current Israel Tax Authority guidance", "accountant", "payroll provider"]
}
```

## National Insurance planning reference

```json
{
  "person_status": "self_employed",
  "monthly_income_ils": 28000,
  "has_salary_income": false,
  "planning_goal": "long_term_savings_and_business_perks"
}
```

```json
{
  "must_verify_registration_status": true,
  "cash_flow_note": "monthly advances may change after annual assessment",
  "recommended_actions": ["confirm classification", "budget monthly advances", "keep reserve for annual adjustment"]
}
```

## Pension clearing and employer interface

Use for employee pension remittance, fund details, confirmations, and reconciliation.

```json
{
  "employer_id": "example-employer",
  "payroll_month": "2026-07",
  "employee": {
    "id_number_masked": "***1234",
    "start_date": "2026-07-01",
    "fund_identifier": "example-fund",
    "gross_salary_base_ils": 16000
  },
  "contributions": {
    "employee_pension_ils": 960,
    "employer_pension_ils": 1040,
    "severance_ils": 1333.33
  }
}
```

```json
{
  "status": "accepted_with_warnings",
  "confirmation_id": "CONF-2026-07-0001",
  "warnings": [{"code": "FUND_DETAILS_REQUIRE_VERIFICATION", "message": "Confirm employee fund details before the next payroll cycle."}]
}
```

## Capital Market, Insurance and Savings Authority reference

```json
{
  "product": "keren_hishtalmut",
  "person_type": "employee",
  "tax_year": 2026,
  "questions": [
    "Which contribution ceiling applies?",
    "Which party contributes?",
    "Which fees apply?",
    "Which liquidity rules apply?",
    "Which investment track was selected?"
  ]
}
```

## Privacy Protection Authority reference

```json
{
  "vendor_category": "meal_card",
  "personal_data": ["employee name", "employee identifier", "email", "transaction date", "transaction amount", "merchant category"],
  "sensitive_data": [],
  "employee_notice_required": true,
  "retention_policy_required": true
}
```


## Web-validated official checkpoints, accessed 2026-06-04

| Topic | Confirmed value or rule | Source discipline |
|---|---|---|
| VAT | Current standard VAT rate is 18%, effective from 01/01/2025. | Confirm against Israel Tax Authority VAT history and terminology before implementation. |
| Employee pension | General minimum pension arrangement is 18.5% of salary: 6% employee, 6.5% employer pension, 6% employer severance, subject to sector and agreement exceptions. | Confirm with Ministry of Labor guidance, payroll provider, and applicable collective agreement. |
| Severance | A 6% severance component may require completion to 8.33% depending on the arrangement and entitlement. | Confirm with payroll/legal review and Section 14 context. |
| Self-employed pension | Mandatory self-employed pension uses 4.45% and 12.55% brackets up to the average wage framework. | Confirm current average wage and exemptions for the tax year. |
| National Insurance self-employed classification | 2026 classification examples include 20 weekly hours, income of at least 50% of the average wage, or 12 weekly hours plus 15% of the average wage. | Confirm status directly with National Insurance guidance. |
| National Insurance example rates | 2026 example lists self-employed National Insurance 4.47%/12.83% and health insurance 3.23%/5.17%. | Treat as an example; calculate with current National Insurance tables. |
| Keren Hishtalmut employee salary basis | 2026 deductions booklet lists ₪188,544 annually as the salary basis reference for employee study-fund deposits. | Confirm current tax-year booklet and employee category. |
| Keren Hishtalmut self-employed ceiling | 2026 reference ceiling is ₪293,397 of income; 4.5% is ₪13,203 for maximum deductible contribution. | Confirm current tax-year booklet and accountant treatment. |
| Israel Invoice allocation number | Threshold is ₪10,000 from 01/01/2026 and ₪5,000 from 01/06/2026. | Confirm invoice date, amount before VAT, and Tax Authority guidance. |
| Tax Authority API documentation | Registration of software house and developers is required; full docs may require developer portal access. | Do not invent hosts, endpoint paths, or webhook names. |
| Form 161 | New digital retirement reporting workflow applies from 01/01/2024. | Confirm current digital reporting requirements. |
| Form 135 | Individual tax refund request can generally be submitted up to six years back. | Confirm current eligibility and year availability. |
| Form 126 | Use current Tax Authority/National Insurance file structure and deadlines. | Confirm current file specification before payroll export. |

### API and webhook caveat

The sample API paths below are integration patterns, not confirmed public endpoints. Replace every path, host, payload field, webhook name, and error code with the current vendor or official developer-portal documentation before production use. If a vendor or authority does not provide public webhook event names, write `not publicly confirmed` rather than inventing names.

## Illustrative provider API patterns

Most providers expose REST endpoints, CSV exports, or both. Request sandbox access and written data terms.

### Employee provisioning

```http
POST /employees
Content-Type: application/json
Authorization: Bearer <token>
Idempotency-Key: <uuid>
```

```json
{
  "external_employee_id": "E-1007",
  "name": "Dana Cohen",
  "email": "dana@example.co.il",
  "monthly_limit_ils": 770,
  "daily_limit_ils": 35,
  "allowed_categories": ["restaurants", "grocery"],
  "active_from": "2026-07-01"
}
```

```json
{
  "provider_employee_id": "mp_7b21",
  "status": "active",
  "limits": {"monthly_limit_ils": 770, "daily_limit_ils": 35}
}
```

### Error table

| HTTP | Code | Meaning | Fix |
|---:|---|---|---|
| 400 | INVALID_LIMIT | Daily or monthly cap is missing or invalid | Validate caps before upload |
| 400 | INVALID_DATE | Date format is invalid | Send YYYY-MM-DD |
| 401 | UNAUTHORIZED | Token missing or expired | Refresh token |
| 403 | FORBIDDEN | Account lacks permission | Update provider role |
| 409 | EMPLOYEE_EXISTS | Employee already exists | Update instead of create |
| 422 | EMAIL_INVALID | Employee email invalid | Correct HR data |
| 429 | RATE_LIMITED | Too many requests | Back off and retry |
| 500 | PROVIDER_ERROR | Provider failure | Retry with idempotency key |

## Utilization export

```http
GET /reports/utilization?month=2026-07
Authorization: Bearer <token>
```

```json
{
  "month": "2026-07",
  "currency": "ILS",
  "rows": [{
    "external_employee_id": "E-1007",
    "employee_name": "Dana Cohen",
    "transactions": 18,
    "gross_amount_ils": 612,
    "employer_amount_ils": 612,
    "employee_amount_ils": 0
  }],
  "invoice_total_ils": 7344
}
```

## Payroll import CSV

```csv
employee_id,month,component_code,amount_ils,notes
E-1007,2026-07,MEAL_BENEFIT,612,Meal provider utilization
E-1007,2026-07,WELLNESS_REIMB,120,Receipt approved
```

| Validation | Error | Fix |
|---|---|---|
| Employee not in payroll | UNKNOWN_EMPLOYEE | Reconcile HR master data |
| Negative amount | NEGATIVE_AMOUNT | Use adjustment component |
| Duplicate component | DUPLICATE_COMPONENT | Merge or mark correction |
| Missing approval | MISSING_APPROVAL | Attach approval record |

## Accounting export pattern

```json
{
  "date": "2026-07-31",
  "currency": "ILS",
  "entries": [
    {"account": "employee_meals_expense", "debit_ils": 7344, "credit_ils": 0},
    {"account": "accounts_payable", "debit_ils": 0, "credit_ils": 7344}
  ],
  "attachments": ["provider_invoice.pdf", "utilization_report.csv", "policy_version_2026-07.pdf"]
}
```

## Planner error table

| Code | Severity | Trigger | Action |
|---|---|---|---|
| MISSING_ENTITY_TYPE | Medium | Entity not clear | State assumption or ask once |
| MISSING_BUDGET | Medium | No budget | Provide tiered package |
| COMPLIANCE_FIRST | High | Optional perks before mandatory checks | Fix payroll/pension first |
| TAX_TREATMENT_UNKNOWN | High | Tax-free claim without verification | Require accountant/payroll review |
| CONTRACTOR_RISK | High | Contractors receive employee-style perks | Separate terms and seek legal review |
| PRIVACY_RISK | High | Health details requested | Minimize data |
| PROVIDER_COVERAGE_GAP | Medium | Weak meal provider coverage | Add reimbursement fallback |
| OVER_BUDGET | Medium | Package exceeds cap | Reduce caps |
| LOW_UTILIZATION | Low | Perk likely unused | Use flexible wallet |
| EDGE_CASE_UNHANDLED | Medium | Leave, part-time, reserve duty, termination missing | Add rules |

## Currentness discipline

Where statutory amounts, ceilings, tax treatment, or rates matter, state: verify the current statutory rate, annual ceiling, and payroll treatment for the exact tax year before implementation. Do not invent current caps or rates when not supplied.
