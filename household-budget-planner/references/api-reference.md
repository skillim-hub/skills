# Israeli API and Regulation Reference

Use this file as the verification and integration reference for Israeli household, consumer, freelancer, and small-business budgeting. Some sources expose APIs, some expose official files or calculators, and some require manual entry from an official bill or statement. Treat all rates, thresholds, fees, forms, tariff tables and endpoint examples as time-sensitive.

## Verification hierarchy

1. Official Israeli government, regulator, municipality, or public authority source.
2. Official open-data endpoint or machine-readable publication.
3. Official notice, PDF, calculator, or bill.
4. User-owned bank/card/account export.
5. Manual input with a dated verification note.

Avoid scraping private accounts. Prefer exported CSV files or explicit user-provided values.

## Current verified source highlights

The live web validation pass on 04-06-2026 confirmed these practical values and source patterns:

| Topic | Verified planning treatment |
|---|---|
| VAT rate | Use 18% for Israeli VAT examples from 01-01-2025 onward, while keeping `vat_rate` configurable. |
| Osek patur threshold | For 2026, the Tax Authority source states 122,833 ₪. Verify annually before registration or pricing decisions. |
| National Insurance self-employed rates | For a self-employed person aged 18 to retirement age, the National Insurance source lists 7.7% and 18% bands from 01-01-2026. Do not compute final liability without status-specific rules. |
| Bank of Israel interest endpoint | `https://www.boi.org.il/PublicApi/GetInterest` is an official API path documented by the Bank of Israel. |
| Bank of Israel exchange-rate endpoint | `https://boi.org.il/PublicApi/GetExchangeRates` is an official API path documented by the Bank of Israel. |
| CBS CPI endpoints | CBS exposes CPI data through `https://api.cbs.gov.il/index/data/price_all?...` and SDMX CPI data through `https://apis.cbs.gov.il/SDMX/DATA/IMF/ECOFIN_CPI/1`. |
| Electricity tariffs | Electricity tariffs are regulator-set and updated for 2026; use the latest Electricity Authority tariff book or the current electricity bill. |
| Water tariffs | Water and sewage tariffs are updated by the Water Authority; use the latest Water Authority tariff table or local water corporation bill. |
| Arnona | Arnona is municipal and depends on area, property type, use, zone, discounts and billing cycle. Use the municipal bill whenever possible. |
| Public transport | Rav-Kav and app fares are managed through public-transport authority information; use the latest fare page or actual user spending. |
| Health spending | Use Kupat Cholim and SHABAN bills for household tracking; do not infer entitlement or medical coverage. |
| Banking fees | Bank fees should be checked through the bank fee schedule and Bank of Israel fee guidance. |
| Pension/provident funds | Use Capital Market Authority and user statements for context only; do not provide investment or pension advice. |
| Minimum wage | Minimum wage and labor thresholds change over time; verify before payroll, employment, or pricing decisions. |

## Israeli sources and use

| Topic | Source to cite or verify | Use in planner | Sensitivity |
|---|---|---|---|
| VAT / Ma'am | Israel Tax Authority | VAT extraction and VAT reserve | High |
| Osek patur / small business owner | Israel Tax Authority | Registration and threshold context | High |
| Income tax | Israel Tax Authority | Freelancer reserve planning | High |
| Bituach Leumi | National Insurance Institute | Social-insurance reserve planning | High |
| Interest and monetary rates | Bank of Israel | Mortgage, overdraft, and interest context | High |
| Prime references | Bank/banking disclosures and Bank of Israel context | Loan and mortgage context | High |
| Consumer Price Index | Central Bureau of Statistics | Indexed rent and real spending analysis | Medium |
| Wages and labor | Ministry of Labor and official notices | Salary and minimum wage checks | High |
| Arnona | Municipality bill or municipal tariff | Local property-tax planning | High |
| Electricity | Electricity Authority / electricity bill | Utility planning | High |
| Water | Water Authority / local water corporation bill | Utility planning | High |
| Public transport | Ministry of Transport / Rav-Kav data | Commute budget | Medium |
| Health | Ministry of Health / Kupat Cholim bill | Health spending | Medium |
| Banking fees | Bank fee schedule and user statement | Fee leakage and overdraft cost | Medium |
| Pension/provident funds | Capital Market Authority and user statements | Context only; not investment advice | Medium |

## Normalized data contract

### Transaction request

```json
{
  "source": "bank_csv",
  "currency": "ILS",
  "month": "05-2026",
  "transactions": [
    {
      "date": "03-05-2026",
      "amount": 245.90,
      "kind": "expense",
      "category": "food",
      "description": "Supermarket",
      "vendor": "Example Market",
      "payment_method": "credit_card",
      "vat_included": true,
      "is_business": false,
      "business_use_percent": 0,
      "normalize_months": 1
    }
  ]
}
```

### Budget response

```json
{
  "month": "05-2026",
  "currency": "ILS",
  "income_total": 18200,
  "expense_total": 11420,
  "net_cash_flow": 6780,
  "savings_rate": 0.3725,
  "category_totals": {
    "housing": 6200,
    "arnona": 460,
    "food": 3900,
    "transport": 860
  },
  "warnings": [
    "Food and delivery exceeded the planned category limit."
  ],
  "recommendations": [
    "Set a food cap before the next card cycle.",
    "Create an automatic savings transfer after salary receipt."
  ],
  "assumptions": [
    "Arnona was normalized from a bi-monthly payment."
  ]
}
```

## Bank of Israel reference pattern

Use official Bank of Israel data for reference rates. Do not hard-code rates into decision logic.

### Official interest API

```http
GET https://www.boi.org.il/PublicApi/GetInterest
Accept: application/json
```

Documented response shape:

```json
{
  "currentInterest": 3.25,
  "nextInterestDate": "2023-01-02T00:00:00Z"
}
```

Normalize any returned rate before using it in a budget record:

```json
{
  "source": "Bank of Israel",
  "field": "interest_rate",
  "value": 3.25,
  "unit": "percent",
  "verified_at": "04-06-2026",
  "note": "Use for context only. Verify current publication before decisions."
}
```

### Official exchange-rate API

```http
GET https://boi.org.il/PublicApi/GetExchangeRates
Accept: application/json
```

For a single currency:

```http
GET https://boi.org.il/PublicApi/GetExchangeRate?key=USD
Accept: application/json
```

Use card-settlement amounts in ₪ for household spending whenever available. Use Bank of Israel rates only when the user asks for reference context and not as a substitute for the card issuer settlement amount.

## Israel Tax Authority VAT pattern

Keep VAT rate configurable. The web validation pass confirmed 18% as the current Israeli VAT rate for examples from 01-01-2025 onward. Do not rely on an unofficial VAT endpoint.

### Manual verified-rate record

```json
{
  "jurisdiction": "IL",
  "tax": "VAT",
  "rate": 0.18,
  "valid_from": "01-01-2025",
  "verified_at": "04-06-2026",
  "source": "Israel Tax Authority",
  "source_url": "https://www.gov.il/en/pages/taxes-glossary",
  "note": "Verify again before filing or issuing production tax calculations."
}
```

### VAT extraction response

```json
{
  "gross_amount": 1180,
  "vat_rate": 0.18,
  "net_before_vat": 1000,
  "vat_component": 180
}
```

### Osek patur threshold record

```json
{
  "topic": "osek_patur_threshold",
  "year": 2026,
  "amount_ils": 122833,
  "source": "Israel Tax Authority",
  "verified_at": "04-06-2026",
  "note": "Threshold changes annually. Do not infer eligibility without checking profession-specific restrictions and current rules."
}
```

## Income tax and small-business reserve pattern

Do not calculate final income-tax liability without current brackets, deductions, credits, business classification, and user-specific facts. Use reserve planning unless the user provides accountant-approved percentages.

```json
{
  "month": "05-2026",
  "status": "self_employed",
  "profit_estimate": 22000,
  "reserve_rate_source": "accountant_provided",
  "reserve_rate": 0.25,
  "response": {
    "reserve_type": "income_tax_placeholder",
    "message": "Treat as planning reserve only. Verify final liability with the Israel Tax Authority or a qualified professional."
  }
}
```

## National Insurance pattern

Do not compute final liability without current brackets and user-specific status. Use reserve planning only unless an accountant-provided rate is supplied.

```json
{
  "month": "05-2026",
  "status": "self_employed",
  "profit_estimate": 22000,
  "known_prepaid_amount": 2500,
  "source_check": {
    "authority": "National Insurance Institute",
    "verified_at": "04-06-2026",
    "self_employed_bands_from_01_01_2026": [
      {"band": "reduced", "total_rate": 0.077},
      {"band": "regular", "total_rate": 0.18}
    ]
  },
  "response": {
    "reserve_type": "bituach_leumi_placeholder",
    "message": "Enter accountant-provided reserve rate or verify current brackets with National Insurance Institute."
  }
}
```

## CBS CPI pattern

Use CPI for indexed rent or real-spending trend analysis only. Replace the previous illustrative `/cbs/cpi` path with actual CBS public endpoints.

### CBS index endpoint pattern

```http
GET https://api.cbs.gov.il/index/data/price_all?download=false&format=xml&oldformat=true
Accept: application/xml
```

### CBS SDMX endpoint pattern

```http
GET https://apis.cbs.gov.il/SDMX/DATA/IMF/ECOFIN_CPI/1
Accept: application/xml
```

Normalize responses to the planner's internal format:

```json
{
  "series": "consumer_price_index",
  "observations": [
    {"month": "03-2026", "index": 120010}
  ],
  "source": "Central Bureau of Statistics",
  "verified_at": "04-06-2026"
}
```

## Municipality arnona pattern

Arnona depends on city, property type, square meters, zone, discounts, and billing period. Use the bill when possible.

```json
{
  "municipality": "Tel Aviv-Yafo",
  "property_type": "residential",
  "area_sqm": 85,
  "billing_period": "bi_monthly",
  "gross_bill": 920,
  "bill_date": "05-05-2026",
  "response": {
    "monthly_budget_amount": 460,
    "assumptions": [
      "Bi-monthly bill divided by 2.",
      "No discount eligibility inferred."
    ]
  }
}
```

## Bank and card CSV import

### Expected columns

| Column | Required | Format | Notes |
|---|---:|---|---|
| date | Yes | DD-MM-YYYY, DD/MM/YYYY, or YYYY-MM-DD | Output can be localized by language |
| amount | Yes | Decimal | Positive amount; kind determines income or expense |
| kind | Yes | income / expense / transfer | Refund may be a negative expense in source data but is normalized |
| category | No | Text | Infer only when confidence is high |
| description | No | Text | Merchant or memo |
| vendor | No | Text | Useful for recurring-charge detection |
| payment_method | No | Text | bank, credit_card, cash, transfer |
| vat_included | No | true / false | Use only when known |
| is_business | No | true / false | Separates business and household totals |

### CSV example

```csv
date,amount,kind,category,description,vendor,payment_method,vat_included,is_business
03-05-2026,245.90,expense,food,Supermarket,Example Market,credit_card,true,false
10-05-2026,15000,income,salary,Net salary,Employer,bank,false,false
```

## Error table

| Code | Meaning | Suggested fix |
|---|---|---|
| INVALID_DATE | Date is missing or not parseable | Use DD-MM-YYYY, DD/MM/YYYY, or YYYY-MM-DD |
| INVALID_MONTH | Month is missing or not parseable | Use MM-YYYY or MM/YYYY |
| INVALID_AMOUNT | Amount is empty, zero where not allowed, or not numeric | Enter a positive number and set kind correctly |
| UNKNOWN_KIND | Transaction kind is not income, expense, or transfer | Use `income`, `expense`, or `transfer` |
| DUPLICATE_TRANSACTION | Same date, amount, vendor, and description imported twice | Remove duplicate or add a unique transaction ID |
| UNSUPPORTED_CURRENCY | Currency is not ILS | Convert using actual card settlement in ₪ |
| STALE_RATE | Rate was not verified recently | Verify against official source before production use |
| MIXED_EXPENSE_UNTAGGED | Expense appears both household and business | Add business-use percentage or mark as unclear |
| VAT_RATE_MISSING | VAT calculation requested without a positive rate | Provide current VAT rate |
| GOAL_DATE_PAST | Savings goal due date already passed | Update due date or close goal |
| RECONCILIATION_MISMATCH | Imported totals do not match account totals | Check refunds, duplicates, pending card charges, and cash withdrawals |
| BUDGET_ID_MISMATCH | CLI budget identifier does not match the file | Use the identifier returned by `create` or omit the check |

## Security and privacy

- Store only data needed for budgeting.
- Avoid full identity numbers, full card numbers, account passwords, API tokens, and bank credentials.
- Keep raw statements in encrypted storage when retained.
- Redact sensitive health, legal, family, or employer notes before sharing.
- Use read-only exports where possible.
