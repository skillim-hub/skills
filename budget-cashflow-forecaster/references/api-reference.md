# Israeli Regulation and Data Reference

This reference lists official Israeli sources and the non-API regulatory inputs used by the forecaster. Most obligations are not exposed through a public transactional API for third-party forecasting. Treat this file as a regulatory input map and implementation reference.

Last web validation: 2026-06-02.

---

## 1. Official source map

| Topic | Authority | Public source | Forecast use |
|---|---|---|---|
| VAT / מע״מ | Israel Tax Authority | https://www.gov.il/he/pages/vat-history | Current VAT rate and effective-date history |
| VAT reports and payments | Israel Tax Authority | https://www.gov.il/he/service/reporting-or-payment-of-vat-reports | VAT reporting cadence and online due-date planning |
| Income-tax advances / מקדמות מס הכנסה | Israel Tax Authority | https://www.gov.il/he/service/itc-payment-online-incometax | Online reporting and payment of periodic advances |
| Income-tax payments | Israel Tax Authority | https://www.gov.il/he/service/income-tax-payment | Payment categories including advances |
| Withholding tax / ניכוי מס במקור | Israel Tax Authority | https://www.gov.il/he/service/itc-gmishurim | Supplier/customer withholding-status lookup |
| Annual withholding certificate | Israel Tax Authority | https://www.gov.il/he/service/itc806 | Form 806 annual withholding certificate reference |
| Bituach Leumi self-employed rates | National Insurance Institute | https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/rates.aspx | 2026 self-employed contribution brackets and rates |
| Bituach Leumi calculation | National Insurance Institute | https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/hishov.dmey.bituach.aspx | 2026 calculation method and final-assessment reconciliation |
| Bituach Leumi payment timing | National Insurance Institute | https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/howtopay.aspx | Direct-debit payment timing for self-employed |
| Bituach Leumi payment calendar | National Insurance Institute | https://www.btl.gov.il/Pages/BenefitsPaymentDates.aspx | Monthly reporting/payment calendar |
| Bank of Israel exchange-rate API | Bank of Israel | https://www.boi.org.il/information/bank-paymnts/guide/api-guide/ | Current series API for representative exchange-rate retrieval |
| Legacy Bank of Israel exchange-rate API | Bank of Israel | https://boi.org.il/PublicApi/GetExchangeRates | Simple legacy JSON/XML endpoint where still available |

---

## 2. Validated values as of 2026-06-02

| Item | Validated value | Forecast handling |
|---|---:|---|
| Standard VAT rate | 18%, effective from 01/01/2025 and still used in 2026 references | Default examples use `vat_rate: 0.18`; keep configurable. |
| VAT statutory due date | 15th of month for periodic reports | Use as baseline date when exact filing method is unknown. |
| VAT online due date | Up to the 19th of each month for online reporting/payment | Use 19th only when online reporting/payment applies. |
| Income-tax advances online timing | Online report submitted by the 19th at 18:30 is treated as on time | Use user-specific advance percentage and online deadline assumption only when applicable. |
| Bituach Leumi self-employed reduced bracket | Up to ₪7,703 per month as of 01/01/2026 | Flat helper rate is an approximation; bracketed official calculation should be verified. |
| Bituach Leumi self-employed maximum base | Up to ₪51,910 per month for regular bracket as of 01/01/2026 | Do not use flat rate for final calculation. |
| Bituach Leumi combined self-employed rates | 7.7% reduced bracket; 18% regular bracket | Examples use 18% as a conservative flat planning approximation. |
| Bituach Leumi direct debit timing | 22nd of each month for the prior month, subject to weekends/holidays | Add dated cash-out rows when exact vouchers or payment method are known. |
| Bank of Israel current API host | `edge.boi.gov.il` | Prefer series API for new integrations. |
| Legacy exchange-rate endpoint | `boi.org.il/PublicApi/GetExchangeRates` | Keep as legacy/simple option, not preferred. |
| Withholding tax lookup | Information service, not a filing API | Enter net cash receipts and track withheld tax as non-cash credit. |
| Webhook events | None found for this local, non-API skill | No webhook event names are implemented. |

---

## 3. Configuration-first approach

Do not hard-code legal conclusions. Load official values or user-confirmed values into `tax_profile`.

```json
{
  "tax_profile": {
    "vat_rate": 0.18,
    "vat_cadence": "bimonthly",
    "vat_amounts_are_gross": true,
    "income_tax_advance_rate": 0.08,
    "bituach_leumi_rate": 0.18,
    "withholding_tax_rate": 0.0,
    "reviewed_on": "2026-06-02",
    "source_note": "VAT 18%; Bituach Leumi flat 18% is a conservative planning approximation. Verify bracketed calculation and advance amounts."
  }
}
```

### Accepted cadence values

| Value | Meaning | Typical use |
|---|---|---|
| `none` | No VAT deadline generated | Household, non-VAT planning, עוסק פטור planning |
| `monthly` | Generate monthly VAT reserve/payment reminders | Authorized dealer/company where monthly reporting applies |
| `bimonthly` | Generate every-two-month VAT reserve/payment reminders | Authorized dealer where bimonthly reporting applies |
| `manual` | User supplies dated payments | Complex, voucher-based, or accountant-managed schedules |

---

## 4. Request and response examples

### Forecast request

```json
{
  "opening_balance": 50000,
  "start_month": "2026-01",
  "months": 4,
  "cash_in": [
    {
      "date": "2026-01-10",
      "amount": 23600,
      "description": "Consulting payment including VAT",
      "category": "revenue",
      "taxable": true,
      "gross": true
    }
  ],
  "cash_out": [
    {
      "date": "2026-01-03",
      "amount": 3500,
      "description": "Software subscriptions",
      "category": "software",
      "taxable": true
    }
  ],
  "tax_profile": {
    "vat_rate": 0.18,
    "vat_cadence": "bimonthly",
    "income_tax_advance_rate": 0.08,
    "bituach_leumi_rate": 0.18,
    "reviewed_on": "2026-06-02"
  },
  "buffer": 15000
}
```

### Forecast response

```json
{
  "id": "example-id",
  "environment": "sandbox",
  "summary": {
    "start_month": "2026-01",
    "months": 4,
    "minimum_closing_balance": 41380.0,
    "minimum_free_cash": 31680.0,
    "first_negative_month": null
  },
  "rows": [
    {
      "month": "2026-01",
      "opening_balance": 50000.0,
      "cash_in": 23600.0,
      "cash_out": 3500.0,
      "tax_reserved": 10700.0,
      "tax_paid": 0.0,
      "closing_balance": 70100.0,
      "protected_reserve": 10700.0,
      "free_cash": 59400.0,
      "status": "ok"
    }
  ],
  "warnings": []
}
```

---

## 5. Error table

| Code | Meaning | Recommended response |
|---|---|---|
| `INVALID_DATE` | Date is not ISO `YYYY-MM-DD` | Correct the date. Use `DD/MM/YYYY` only in Hebrew display output. |
| `INVALID_MONTH` | Start month is not `YYYY-MM` | Use a valid start month. |
| `NEGATIVE_MONTHS` | Forecast length is below 1 | Set months to at least 1. |
| `TOO_LONG` | Forecast length exceeds supported range | Use 60 months or less for the helper. |
| `NEGATIVE_AMOUNT` | Transaction amount is below zero | Use positive amounts and choose `cash_in` or `cash_out`. |
| `UNKNOWN_CADENCE` | VAT cadence is unsupported | Use `none`, `monthly`, `bimonthly`, or `manual`. |
| `MISSING_FILE` | Input file does not exist | Check the path. |
| `JSON_PARSE_ERROR` | JSON input cannot be parsed | Validate syntax. |
| `CSV_SCHEMA_ERROR` | Required CSV columns are missing | Include `date`, `amount`, `direction`, and `description`. |
| `UNVERIFIED_TAX_RATE` | Tax profile has no review marker | Add a review date and source note. |

---

## 6. Non-API workflow equivalents

### VAT

There is no generic public API for all small-business VAT reporting. Use the official portal and treat the forecaster as a planning tool.

Equivalent workflow:

1. Enter taxable receipts and payments.
2. Estimate output VAT from gross or net receipts.
3. Estimate input VAT when supplier invoice data exists.
4. Reserve cash monthly.
5. Reconcile against bookkeeping software or accountant output.
6. Pay through the official channel.

### Income-tax advances

Equivalent workflow:

1. Enter the advance percentage from the official notice or accountant.
2. Reserve cash from receipts.
3. Generate monthly or bimonthly planning rows if relevant.
4. Reconcile paid advances against yearly tax position.

### Bituach Leumi

Equivalent workflow:

1. Enter official voucher amount when available, or use the 2026 bracketed rates for planning.
2. Use exact dated outflows for direct debit or payment vouchers.
3. Use flat 18% only as a conservative planning approximation for self-employed income above the reduced bracket.
4. Reconcile against annual assessment.

---

## 7. Bank of Israel exchange-rate reference

Prefer the current series API for new integrations:

```http
GET https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/?c%5BBASE_CURRENCY%5D=USD,EUR&c%5BCOUNTER_CURRENCY%5D=ILS&format=csv
Accept: text/csv
```

Legacy/simple endpoint, where available:

```http
GET https://boi.org.il/PublicApi/GetExchangeRates
Accept: application/json
```

Example normalized internal response:

```json
{
  "base": "ILS",
  "rates": [
    {"currency": "USD", "rate": 3.72, "date": "2026-01-15"},
    {"currency": "EUR", "rate": 4.04, "date": "2026-01-15"}
  ],
  "source": "Bank of Israel",
  "verified_at": "2026-01-15"
}
```

Error handling:

| Situation | Action |
|---|---|
| Rate unavailable for a holiday/weekend | Use most recent official business day and mark assumption |
| Currency not supported | Enter manual conversion rate |
| Forecast is sensitive to FX | Run high/low exchange-rate scenarios |

---

## 8. Data protection

Financial files may include customer names, bank balances, ID numbers, and invoices. Store input and output files securely. Avoid committing real forecasts to public repositories. Mask personal data in examples and tests.
