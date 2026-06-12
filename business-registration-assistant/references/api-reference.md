# Israeli API and Regulatory Reference

This package is not an official government integration. Many Israeli registration steps use authenticated portals, interactive forms, representatives, or branch processing rather than open public APIs. Use this reference to structure information and verify official sources before filing.

## Official sources to check

| Topic | Authority/source | Check before filing |
|---|---|---|
| VAT registration and status | Israel Tax Authority / מע״מ | Current עוסק פטור ceiling, excluded occupations, VAT rate, registration route, reporting period. |
| Income tax file | Israel Tax Authority / מס הכנסה | File opening, advances, annual return, withholding certificate, bookkeeping certificate. |
| Online access | Tax Authority personal area | File status, certificates, notices, available online forms. |
| National Insurance | Bituach Leumi / ביטוח לאומי | Self-employed classification, contribution advances, benefit interactions, hour/income thresholds. |
| Bookkeeping | Income Tax bookkeeping instructions | Required records, receipts, invoices, retention, approved software. |
| Cash payments | Reduction of Use of Cash Law | Cash limits and documentation duties. |
| Business license | Local municipality / relevant ministry | Activities requiring municipal/professional licensing. |
| Regulated professions | Professional regulator | License, title use, and whether the occupation can be עוסק פטור. |
| Foreign services | VAT Law and Tax Authority guidance | Zero-rate VAT conditions, exceptions, and documentation. |

## Values that must not be hard-coded

- Annual exempt dealer ceiling.
- VAT rate.
- Bituach Leumi hour and income thresholds.
- Income tax advance rate.
- Withholding tax rate.
- Cash-use limits.
- Filing deadlines and form IDs.
- Occupation restriction interpretations.

## Structured intake request

```json
{
  "business": {
    "activity_description": "Private English tutoring",
    "planned_start_date": "01/09/2026",
    "expected_annual_turnover_nis": 72000,
    "expected_monthly_profit_nis": 5000,
    "weekly_hours": 12,
    "current_osek_patur_ceiling_nis": 122833,
    "regulated_profession": false,
    "clients_require_tax_invoice": false,
    "foreign_clients": false,
    "currently_employee": true,
    "receives_benefits": false,
    "bank_ownership_confirmation": true
  }
}
```

## Structured response

```json
{
  "recommended_status": "osek_patur",
  "confidence": "medium",
  "reasons": [
    "Expected turnover is within the supplied exempt dealer ceiling.",
    "No supplied fact requires authorized dealer status."
  ],
  "issues": [
    {
      "code": "CURRENT_THRESHOLD_REQUIRED",
      "severity": "warning",
      "message": "Verify current-year ceiling before filing."
    }
  ],
  "next_actions": [
    "Prepare VAT, income tax, and Bituach Leumi steps separately.",
    "Configure receipt software and turnover tracking."
  ]
}
```

## Pseudo-endpoints implemented by the local client

### `classify_status(intake)`

Returns likely `osek_patur`, `osek_murshe`, or `needs_review`.

Errors/warnings include missing activity, invalid amounts, threshold unknown, turnover above ceiling, regulated profession, foreign-client VAT complexity, benefit interaction, and late registration.

### `build_document_checklist(intake)`

Returns required documents, conditional documents, missing items, and status-specific notes.

### `build_authority_plan(intake)`

Returns action lists for VAT, income tax, Bituach Leumi, bookkeeping, and professional review.

### `migration_checklist(ytd, forecast, ceiling)`

Returns whether migration from עוסק פטור to עוסק מורשה is likely needed based on gross turnover forecast.

## Error and warning table

| Code | Severity | Meaning | Corrective action |
|---|---|---|---|
| `MISSING_ACTIVITY` | error | Activity description is empty or too vague. | Ask for exact services/products and client types. |
| `MISSING_TURNOVER` | error | Annual turnover estimate is missing. | Request a non-negative ₪ amount. |
| `INVALID_AMOUNT` | error | Amount is negative or not numeric. | Correct the number. |
| `BANK_DOCUMENT_MISSING` | error | Bank ownership proof is missing. | Obtain bank letter, cancelled check, or confirmation. |
| `CURRENT_THRESHOLD_REQUIRED` | warning | Current annual ceiling is not verified. | Check official Tax Authority information. |
| `TURNOVER_EXCEEDS_CEILING` | warning | Supplied forecast exceeds supplied ceiling. | Prepare עוסק מורשה registration. |
| `REGULATED_PROFESSION` | warning | Occupation may be excluded from עוסק פטור. | Verify official list and prepare fallback. |
| `CLIENT_REQUIRES_TAX_INVOICE` | warning | Client expects VAT invoice. | Consider עוסק מורשה or clarify onboarding. |
| `FOREIGN_CLIENT_VAT_COMPLEXITY` | warning | Cross-border VAT treatment is complex. | Collect contracts and get review. |
| `BENEFIT_INTERACTION` | warning | Income may affect benefits. | Confirm with Bituach Leumi before activity/payment. |
| `LATE_REGISTRATION` | warning | Activity started before registration. | Use real dates and obtain professional guidance. |
| `VAT_STATUS_NOT_TAX_EXEMPT` | info | עוסק פטור is not general tax exemption. | Explain income tax and Bituach Leumi still apply. |

## Communication templates

### VAT eligibility question

```text
Activity: שיעורים פרטיים באנגלית לתלמידי תיכון
Expected annual turnover: ₪72,000
Planned start date: 01/09/2026
Question: Please confirm whether this activity is eligible for עוסק פטור status under current-year ceiling and occupation rules.
```

### Bituach Leumi status question

```text
Expected monthly profit: ₪5,000
Expected weekly hours: 12
Also salaried employee: Yes
Benefits: No
Question: Please confirm self-employed classification and contribution estimate.
```

## Local case workflow

The local helper includes a case workflow for deterministic chained operations. This is not a government API.

### `POST /cases`

Creates a local planning case in a JSON store.

#### Request

```json
{
  "business": {
    "activity_description": "Private English tutoring",
    "expected_annual_turnover_nis": 72000,
    "expected_monthly_profit_nis": 5000,
    "current_osek_patur_ceiling_nis": 122833,
    "planned_start_date": "01/09/2026"
  }
}
```

#### Response

```json
{
  "id": "case_123456789abc",
  "status": "created",
  "store_path": "/tmp/business-registration-cases.json"
}
```

### `GET /cases/{id}/plan`

Uses the `id` returned by case creation to produce a full plan.

#### Response

```json
{
  "classification": {
    "recommended_status": "osek_patur",
    "confidence": "medium"
  },
  "checklist": {
    "required": ["ID card and appendix or equivalent identity document"]
  }
}
```


## Self-employed contribution rates verified for 2026

For adults from age 18 until retirement age, Bituach Leumi lists a reduced monthly base up to ₪7,703 and a regular band above ₪7,703 up to ₪51,910. The listed components are 4.47% and 12.83% for National Insurance plus 3.23% and 5.17% for health insurance, totaling 7.7% and 18%. Use these only as reference values and verify before calculation or filing.
