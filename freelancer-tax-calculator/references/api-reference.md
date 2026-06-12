# Reference: Israeli Tax Sources and Local Calculation Interface

This package is a local calculation helper. It does not call an external API. Use the references below to verify current rules, portal values, and official notices before filing or payment.

## Official source map

| Topic | Source to verify | How it affects the calculator |
|---|---|---|
| VAT registration, output VAT, input VAT, and VAT returns | Israel Tax Authority, VAT information pages: `https://www.gov.il/he/departments/topics/vat/govil-landing-page`; Value Added Tax Law, 5736-1975 | Set `vat_rate`, identify `osek-patur` or `osek-murshe`, and verify input VAT eligibility. |
| Osek patur annual ceiling | Israel Tax Authority small-business and VAT guidance: `https://www.gov.il/he/departments/israel_tax_authority/govil-landing-page` | Set `osek_patur_threshold_annual` and warning ratio. |
| Income-tax advances | Israel Tax Authority income-tax guidance and personal business file notices: `https://www.gov.il/he/departments/topics/income_tax/govil-landing-page`; Income Tax Ordinance [New Version] | Set `income_tax_advance_rate` and confirm whether the applicable base is revenue or another professional basis. |
| National Insurance and health-insurance contributions | National Insurance Institute information pages: `https://www.btl.gov.il`; National Insurance Law [Consolidated Version], 5755-1995 | Set reduced rate, regular rate, reduced threshold, and annual ceiling. |
| Micro-business or small-business expense simplification | Israel Tax Authority current small-business guidance and eligibility notices | Use `apply_micro_business_normative_expense` only after verifying eligibility; 2026 Tax Authority guidance permits the 30 percent normative expense route for eligible osek patur or osek murshe businesses whose turnover is not above the osek patur ceiling. |
| Recordkeeping and source documents | Tax Authority bookkeeping instructions and professional accounting guidance | Reconcile revenue, expenses, invoices, receipts, and VAT components before relying on a report. |

## Web-validated 2026 default corrections

- VAT remains configured at `0.18` from 01/01/2025 onward.
- Osek patur ceiling is configured as ₪122,833 for 2026.
- National Insurance and health-insurance planning defaults were corrected to combined rates of 7.70 percent and 18.00 percent, annual reduced threshold ₪92,436, and annual ceiling ₪622,920.
- The local calculation remains a planning estimate and does not replace official BTL notices, personal status review, or the full official deduction adjustment.

## Local input schema

```json
{
  "business_type": "osek-murshe",
  "annual_revenue_ils": "300000",
  "deductible_expenses_ils": "80000",
  "input_vat_ils": "7200",
  "income_tax_advance_rate": "0.10",
  "income_tax_advance_base": "revenue",
  "apply_micro_business_normative_expense": false,
  "calculation_date": "2026-06-01"
}
```

## Field reference

| Field | Type | Required | Accepted values | Notes |
|---|---|---:|---|---|
| `business_type` | string | Yes | `osek-patur`, `osek-murshe` | Controls VAT handling. |
| `annual_revenue_ils` | decimal string | Yes | `0` or greater | Enter before VAT for osek murshe. |
| `deductible_expenses_ils` | decimal string | No | `0` or greater | Enter before VAT when input VAT is separated. |
| `input_vat_ils` | decimal string | No | `0` or greater | Applies to osek murshe only. |
| `income_tax_advance_rate` | decimal string | No | `0` through `1` | Use `0.07` for 7 percent. |
| `income_tax_advance_base` | string | No | `revenue`, `profit` | Use `revenue` for turnover-style advance planning. |
| `apply_micro_business_normative_expense` | boolean | No | `true`, `false` | Valid only for eligible osek patur planning. |
| `calculation_date` | string | No | ISO date | Display layers can show `DD/MM/YYYY`. |

## Local configuration schema

```json
{
  "vat_rate": "0.18",
  "osek_patur_threshold_annual": "122833",
  "osek_patur_warning_ratio": "0.90",
  "national_insurance_reduced_rate": "0.077",
  "national_insurance_regular_rate": "0.18",
  "national_insurance_reduced_threshold_annual": "92436",
  "national_insurance_annual_ceiling": "622920",
  "micro_business_normative_expense_rate": "0.30",
  "currency": "ILS"
}
```

All rate fields are decimals from `0` to `1`. All threshold fields are annual ₪ amounts. The 2026 defaults use combined National Insurance and health-insurance rates of 7.70 percent and 18.00 percent, a reduced monthly base of ₪7,703, and a monthly ceiling of ₪51,910. Update this file from official current-year sources before production use.

## Request and response examples

### CLI create request

```bash
freelancer-tax-calculator create \
  --business-type osek-murshe \
  --revenue 300000 \
  --expenses 80000 \
  --input-vat 7200 \
  --advance-rate 0.10 \
  --advance-base revenue \
  --env sandbox \
  --json
```

Response shape:

```json
{
  "scenario_id": "e1d2c3b4a596",
  "input_path": ".freelancer-tax-calculator/scenarios/e1d2c3b4a596.json",
  "environment": "sandbox",
  "created_at": "2026-06-01T08:00:00+00:00",
  "payload": {
    "business_type": "osek-murshe",
    "annual_revenue_ils": "300000.00",
    "deductible_expenses_ils": "80000.00",
    "input_vat_ils": "7200.00",
    "income_tax_advance_rate": "0.10",
    "income_tax_advance_base": "revenue",
    "apply_micro_business_normative_expense": false,
    "calculation_date": "2026-06-01"
  }
}
```

### CLI run request

```bash
freelancer-tax-calculator run e1d2c3b4a596 --env sandbox --json
```

Response sections:

```json
{
  "business_type": "osek-murshe",
  "currency": "ILS",
  "calculation_date": "2026-06-01",
  "vat": {
    "vat_rate": "0.18",
    "output_vat": "54000.00",
    "input_vat_credit": "7200.00",
    "vat_payable": "46800.00",
    "vat_refund_position": "0.00",
    "threshold": "122833.00",
    "threshold_utilization": "244.23"
  },
  "income_tax_advances": {
    "advance_rate": "0.10",
    "advance_base": "300000.00",
    "annual_advance": "30000.00",
    "monthly_reserve": "2500.00",
    "effective_expenses": "80000.00",
    "expense_method": "actual_expenses",
    "base_method": "revenue"
  },
  "national_insurance": {},
  "summary": {},
  "warnings": [],
  "assumptions": []
}
```

The shortened response above shows shape, not official rates or final assessed liability.

## Error table

| Code | Trigger | Recovery |
|---|---|---|
| `invalid_decimal` | Non-numeric, infinite, or invalid numeric input. | Re-enter amounts as plain decimal strings. |
| `negative_amount` | Negative revenue, expense, input VAT, or threshold. | Use zero or a positive amount. |
| `invalid_rate` | Rate below `0` or above `1`. | Enter decimal rates such as `0.18` or `0.07`. |
| `invalid_threshold` | National Insurance ceiling below reduced threshold. | Correct configuration order. |
| `invalid_business_type` | Unsupported business type. | Use `osek-patur` or `osek-murshe`. |
| `invalid_advance_base` | Unsupported advance base. | Use `revenue` or `profit`. |
| `micro_business_ineligible` | Normative expense scenario applied outside eligibility. | Disable the flag or verify eligibility. |
| `invalid_environment` | Unsupported environment label. | Use `sandbox` or `production`. |
| `invalid_scenario_id` | Scenario ID contains an unsafe path character. | Use the ID returned from `create`. |
| `scenario_not_found` | Saved scenario is absent from the selected store. | Pass the correct `--store-dir` or set `FTC_STORE_DIR`. |

## Audit-ready output expectations

- Amounts are strings in JSON to preserve Decimal precision.
- Warnings are part of the response and should remain visible.
- Assumptions should be stored with the report.
- Configuration values should be archived with each production calculation.
- Official source values should be rechecked whenever a tax year changes.
