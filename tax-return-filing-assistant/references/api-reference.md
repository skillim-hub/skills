# API and Regulatory Reference

This skill is primarily a structured filing-assistance workflow, not a direct filing API client. Most Israeli Tax Authority filing systems are portal-based, representative-based, certified-software-based, or require authentication. Do not screen-scrape official portals. Use official online forms, certified accounting/payroll software exports, or an authorized representative.

## Covered forms

| Form | Hebrew name | Purpose | Typical system path |
|---:|---|---|---|
| 1301 | טופס 1301 - דוח ליחיד | Annual individual return | Tax Authority online annual return services |
| 135 | דין וחשבון מקוצר ליחיד המבקש החזר מס | Short return/refund claim for individuals not required to file a full annual return | Tax Authority refund/annual return service |
| 126 | דיווח שנתי על ניכויים ממשכורת ומשכר עבודה | Employer annual salary and withholding report | Payroll reporting/transmission channel |
| 856 | דיווח שנתי על ניכויים מתשלומים שאינם משכורת או שכר עבודה | Supplier and non-employee payment report | Withholding/supplier annual report channel |
| 6111 | נספח לדוח השנתי המפרט נתוני דוחות כספיים | Standardized financial statement appendix | Accounting software export and online annual return attachment |


## Web-validated 2026 operating facts

These values were checked during the final validation pass on 01/06/2026 and remain planning defaults rather than legal advice.

| Item | Validated operating fact | Package effect |
|---|---|---|
| VAT rate | Standard VAT is 18% after the 01/01/2025 increase. VAT filing remains outside this skill except for reconciliation examples. | Keep VAT references as reconciliation context only. |
| Form 1301, tax year 2025 | Non-online individual filing deadline: 29/05/2026. Online individual filing deadline: 30/06/2026. | Year-specific deadline override added for 2025. |
| Form 135 | Refund claims for individuals not required to file a full annual report may generally be submitted up to six years back. | Limitation reminder remains 31/12 six years after the tax year, with official-confirmation flag. |
| Forms 126 and 856, tax year 2025 | Annual withholding reports were extended to 31/05/2026, with online transmission and approval requirements to verify. | Year-specific deadline override added for 2025. |
| Form 6111 | Business owners with annual turnover over ₪300,000 including VAT are generally required to submit the appendix unless an exemption applies. | Default planning threshold remains ₪300,000 and always emits a verification warning. |
| API and webhooks | No public unauthenticated submission API or webhook event model was confirmed for Forms 1301, 135, 126, 856, or 6111. Official workflows use service pages, authenticated systems, file structures, and approval flows. | Keep the package offline; do not add webhook event names or automated submission endpoints. |

## Official source categories to verify before filing

Use current official materials for the specific tax year. Names and service locations can change.

| Category | What to verify | Why it matters |
|---|---|---|
| Israel Tax Authority annual return instructions | Current Form 1301/135 fields, appendices, electronic filing rules, due dates | Annual form layouts and deadlines can change |
| Israel Tax Authority employer reporting instructions | Current Form 126 broadcast format, corrections, deadlines | Payroll reports are format-sensitive |
| Israel Tax Authority supplier reporting instructions | Current Form 856 file format, payment types, withholding reconciliation | Supplier records often fail on classification or certificate validity |
| Form 6111 instructions | Required filer criteria, standardized account codes, validation rules | Code mapping errors can produce material inconsistencies |
| Gov.il service pages | Authentication, portal URLs, attachments, appointment/service changes | Portal workflows change without changing tax law |
| Income Tax Ordinance [New Version] | Filing obligation, deductions, credits, refund limitation, withholding framework | Legal basis for reporting and claims |
| Income Tax Regulations and bookkeeping instructions | Accounting records, recognized documents, withholding certificates, record retention | Audit trail and document sufficiency |
| National Insurance Institute rules | Payroll, benefits, maternity/unemployment/reserve-duty certificates | Relevant to Form 126 and refund evidence |
| Protection of Privacy Law and data-security regulations | Handling identity, payroll, bank, and health-related records | Personal data must be minimized and protected |

## Regulations and legal anchors commonly cited

The following legal references appear in workflows. Verify exact wording and current amendments before relying on them.

| Reference | Practical use in this skill |
|---|---|
| Income Tax Ordinance [New Version] | General income-tax filing, income classification, deductions, credits, withholding, refunds |
| Section 160 of the Income Tax Ordinance | Refund limitation period for prior tax years |
| Section 46 of the Income Tax Ordinance | Recognized donations credit support |
| Sections 45A and 47 of the Income Tax Ordinance | Pension, provident fund, and insurance-related tax benefits |
| Section 121B of the Income Tax Ordinance | Surtax/מס יסף framework where relevant |
| Income Tax Regulations on withholding from payments and services | Supplier withholding certificate and Form 856 logic |
| Income Tax bookkeeping instructions | Bookkeeping documents, ledgers, receipt/invoice audit trail |
| National Insurance Law | Salary-related National Insurance and health tax support for Form 126 |
| Protection of Privacy Law | Handling sensitive personal and payroll data |
| VAT Law and VAT reporting instructions | Boundary and reconciliation only; VAT filing is outside this skill |

## No-public-API assumption

Do not assume that a public unauthenticated API exists for submitting Forms 1301, 135, 126, 856, or 6111. Treat this package as an offline preparation helper.

Allowed integration approaches:

1. Manual entry into official online Tax Authority services.
2. Upload of files generated by certified accounting or payroll software.
3. Submission by an authorized representative through official channels.
4. Internal validation of user-provided JSON/CSV exports before portal entry.

Disallowed approaches:

1. Screen-scraping login-protected Tax Authority portals.
2. Storing passwords, one-time codes, or smart-card credentials.
3. Circumventing certificate, representative, or authentication requirements.
4. Sending live taxpayer data to unofficial services.

## Local structured request examples

### Form recommendation request

```json
{
  "tax_year": 2025,
  "taxpayer_type": "sole_proprietor",
  "salary_only": false,
  "wants_refund": false,
  "business_income": true,
  "annual_turnover_ils": 420000,
  "has_employees": false,
  "paid_suppliers": true,
  "foreign_income": false,
  "capital_gains": false,
  "rental_income": false,
  "is_online": true,
  "represented_by_cpa": false
}
```

### Form recommendation response

```json
{
  "forms": ["1301", "856", "6111"],
  "explanations": {
    "1301": "Individual annual return is needed because business income is present.",
    "856": "Supplier report may be needed because the business paid non-employee suppliers.",
    "6111": "Standardized financial statement may be needed because annual turnover is at or above the planning threshold."
  },
  "warnings": [
    "Verify Form 6111 requirement and current threshold with official instructions for the tax year."
  ]
}
```

### Deadline request

```json
{
  "form": "1301",
  "tax_year": 2025,
  "is_online": true,
  "represented_by_cpa": false
}
```

### Deadline response

```json
{
  "form": "1301",
  "due_date": "30/06/2026",
  "basis": "Official 2025 online Form 1301 planning deadline.",
  "requires_official_confirmation": true,
  "reminders": ["01/05/2026", "31/05/2026", "16/06/2026", "23/06/2026", "30/06/2026"]
}
```

### Field-help request

```json
{
  "form": "856",
  "field_id": "withholding_rate"
}
```

### Field-help response

```json
{
  "form": "856",
  "field_id": "withholding_rate",
  "label_he": "שיעור ניכוי במקור",
  "label_en": "Withholding rate",
  "description": "Use the supplier's valid Tax Authority withholding certificate for the payment date. Split payments when certificate validity changed during the year.",
  "source_documents": ["Supplier withholding certificate", "Supplier ledger", "Payment register"],
  "common_errors": ["Using an expired certificate", "Applying a rate to VAT when instructions require a different base", "Using a certificate that belongs to a different legal entity"]
}
```

## CLI request examples

### Recommend forms

```bash
tax-return-filing-assistant recommend --profile profile.json
```

### Show deadlines

```bash
tax-return-filing-assistant deadline 1301 --tax-year 2025 --online
```

### Print field help

```bash
tax-return-filing-assistant fields 856 withholding_rate
```

### Validate a profile

```bash
tax-return-filing-assistant validate --profile profile.json
```

## Error table

| Code | Severity | Meaning | Fix |
|---|---|---|---|
| TAX_YEAR_MISSING | error | No tax year was supplied | Add a four-digit tax year |
| TAX_YEAR_RANGE | error | Tax year is outside the supported planning range | Use a realistic year and verify historical forms |
| FORM_UNKNOWN | error | Form is not one of 1301, 135, 126, 856, 6111 | Choose a covered form |
| PROFILE_INCONSISTENT | warning | Facts point to a different form than requested | Re-run recommendation and review assumptions |
| FIELD_UNKNOWN | error | Requested field is not in the local field-help repository | Use `fields FORM` to list available field IDs |
| DEADLINE_NEEDS_CONFIRMATION | warning | Deadline is a planning default, not official confirmation | Verify on official Tax Authority instructions |
| PERSONAL_DATA_RISK | warning | Input appears to include unnecessary sensitive details | Redact ID, bank, payroll, and medical data |
| RECONCILIATION_MISMATCH | error | Totals do not reconcile across documents | Reconcile ledgers, payroll, VAT, bank, or supplier cards |
| CERTIFICATE_EXPIRED | error | Supplier withholding certificate does not cover payment date | Split periods or request a valid certificate |
| FORM_6111_MAPPING | warning | Account-code mapping is missing or uncertain | Use accounting software mapping or adviser review |

## Response normalization

All local helper responses use:

- Dates: `DD/MM/YYYY`.
- Currency: integer or decimal ILS amounts, displayed as `₪`.
- Forms: strings `"1301"`, `"135"`, `"126"`, `"856"`, `"6111"`.
- Severity: `"info"`, `"warning"`, `"error"`.
- No live submission status unless received from an official, authenticated source.

## Security requirements

- Store local profiles only at user-chosen paths.
- Do not persist portal credentials.
- Redact identity numbers in logs and examples.
- Avoid uploading tax data to third-party services.
- Keep generated files under the user's local working directory.
- Treat payroll and supplier files as confidential business records.
