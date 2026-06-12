# API and Regulation Reference

This reference documents the rules, data contracts, and export conventions used by the Expense Manager helper. Confirm current law, indexed caps, reporting thresholds, and software import templates before final filing.

## Regulation sources to verify

| Area | Source to verify | Use in this skill | Rule impact |
|---|---|---|---|
| Ordinary expense deductibility | Income Tax Ordinance [New Version], section 17 and related case law/practice | Business-purpose test for ordinary expenses | Supports 100% treatment for ordinary business expenses when wholly and exclusively business-related |
| Disallowance authority | Income Tax Ordinance [New Version], section 31 | Power to restrict or disallow categories by regulation | Supports conservative defaults for special categories |
| Certain expense limits | Income Tax Regulations (Deduction of Certain Expenses), 1972 | Hospitality, gifts, travel, refreshments, and similar limits | Applies 0% domestic hospitality default, gift cap warning, and documentation requirements |
| Current VAT rate | Israel Tax Authority VAT history and interpretation 01/2025 | 18% from 01/01/2025 and current for 2026 validation pass | Gross-to-net VAT calculation uses 18% |
| Input VAT recovery | Value Added Tax Law, 1975, sections 38 and 41 | Input-tax eligibility and business-use requirement | Separates VAT recovery from income-tax deductibility |
| VAT invoices and input documents | VAT Regulations, 1976 | Required evidence for input VAT | Adds missing invoice flags and document requirements |
| Bookkeeping records | Income Tax Regulations (Management of Account Books), 1973 | Record retention and source-document discipline | Keeps source files and manifest, flags missing documents |
| Depreciation | Income Tax Depreciation Regulations, 1941 and current Tax Authority tables | Asset treatment and depreciation period | Treats equipment over threshold as capital asset by default |
| Electronic invoice allocation | Israel Tax Authority Invoice Israel / allocation-number guidance | High-value invoice validation where applicable | Keep allocation number fields when present; verify API rules with current Tax Authority documentation |
| Osek Patur ceiling | Israel Tax Authority annual publications | Entity status validation | Use current annual threshold externally; do not hard-code filing status from old data |

## Local helper API

### VAT calculation default

Use 18% Israeli VAT for 2026 gross-to-net calculations when `amount_includes_vat=True` and the document is an Israeli tax invoice. Foreign invoices and card charges without Israeli VAT should set recoverable VAT to zero during accountant review.


The bundled client is not a government API client. It is a deterministic classification and export helper. Import it with `from expense_manager import ...` after installation, import `scripts.expense_manager_client` inside this repository, or run the CLI through `scripts/expense-manager-cli.py`.

### `ExpenseInput`

```python
ExpenseInput(
    date=date(2026, 1, 15),
    vendor="Bezeq",
    amount=Decimal("234.00"),
    description="Internet and phone for studio",
    currency="ILS",
    amount_includes_vat=True,
    receipt_number="INV-1001",
    document_type="tax_invoice",
    fx_rate_to_ils=Decimal("1"),
)
```

### `BusinessConfig`

```python
BusinessConfig(
    entity_type=EntityType.OSEK_MURSHE,
    home_office_percent=Decimal("12.5"),
    vehicle_business_vat_rate=Decimal("0.6667"),
    equipment_immediate_expense_limit_ils=Decimal("1200"),
    gift_cap_ils=Decimal("240"),
    fiscal_year=2026,
    strict=True,
)
```

### Created record contract

Request:

```python
record = create_expense_record(expense, "created-expense.json")
expense_id = record["id"]
result = classify_expense_record(record, expected_id=expense_id, config=config)
```

Response example:

```json
{
  "id": "exp_0123456789abcdef",
  "date": "15/01/2026",
  "vendor": "Bezeq",
  "amount": "234.00",
  "currency": "ILS",
  "description": "Internet and phone for studio",
  "receipt_number": "INV-1001"
}
```

### Synchronous classification

Request:

```python
result = classify_expense(expense, config)
print(result.to_flat_dict())
```

Response example:

```json
{
  "date": "15/01/2026",
  "vendor": "Bezeq",
  "description": "Internet and phone for studio",
  "currency": "ILS",
  "amount_original": "234.00",
  "amount_ils": "234.00",
  "category": "phone_internet",
  "hebrew_category": "טלפון ואינטרנט",
  "account_code": "6510",
  "net_amount_ils": "198.31",
  "input_vat_ils": "35.69",
  "reclaimable_vat_ils": "23.79",
  "income_tax_base_ils": "210.21",
  "deductible_rate": "80.00",
  "deductible_amount_ils": "168.17",
  "non_deductible_amount_ils": "42.04",
  "confidence": "70.00",
  "suggested_export_code": "IL-6510"
}
```

### Asynchronous classification

Request:

```python
results = await async_classify_many(expenses, config)
```

Response: list of `ExpenseResult` objects.

### CSV classification

Command:

```bash
python scripts/expense-manager-cli.py classify input.csv output.csv --entity-type osek_murshe --home-office-percent 12.5 --env sandbox
```

Input CSV example:

```csv
date,vendor,amount,description,receipt_number
15/01/2026,Bezeq,234,Internet and phone,INV-1
16/01/2026,Aroma,58,Coffee with Israeli client,RCPT-2
```

Output fields:

| Field | Type | Meaning |
|---|---|---|
| `date` | `DD/MM/YYYY` | Expense date |
| `vendor` | string | Supplier/payee exactly as supplied |
| `amount_original` | decimal string | Original amount before FX conversion |
| `amount_ils` | decimal string | Amount in ₪ |
| `category` | enum-like string | Deterministic category |
| `hebrew_category` | string | Hebrew category label |
| `account_code` | string | Suggested chart-of-accounts card |
| `net_amount_ils` | decimal string | Net amount derived from gross when VAT included |
| `input_vat_ils` | decimal string | Input VAT embedded in gross amount |
| `reclaimable_vat_ils` | decimal string | VAT amount estimated as recoverable |
| `income_tax_base_ils` | decimal string | Gross less recoverable VAT |
| `deductible_rate` | percent string | Income-tax deductibility rate |
| `deductible_amount_ils` | decimal string | Deductible estimate |
| `non_deductible_amount_ils` | decimal string | Non-deductible estimate |
| `review_flags` | string | Semicolon-separated warnings/blockers |

## Accountant package contract

Command:

```bash
python scripts/expense-manager-cli.py package input.csv ./out --package-name 2026-01-expenses
```

Response:

```json
{
  "env": "sandbox",
  "package_zip": "out/2026-01-expenses.zip",
  "summary": {
    "total_rows": 2,
    "total_amount_ils": "292.00"
  }
}
```

ZIP contents:

```text
2026-01-expenses/
  README-accountant.md
  exports/expense-classification.csv
  exports/import-mapping.json
  reports/accountant-summary.json
  reports/sha256-manifest.txt
  source/input.csv
```

### `accountant-summary.json` example

```json
{
  "total_rows": 2,
  "total_amount_ils": "292.00",
  "total_reclaimable_vat_ils": "23.79",
  "total_deductible_ils": "168.17",
  "total_non_deductible_ils": "100.04",
  "by_category": {
    "domestic_hospitality": {
      "rows": 1,
      "account_code": "6620",
      "amount_ils": "58.00",
      "deductible_ils": "0.00",
      "reclaimable_vat_ils": "0.00"
    }
  },
  "review_flag_count": 1
}
```

## Error and flag table

| Code | Severity | Trigger | Corrective action |
|---|---|---|---|
| `missing_receipt` | warning | `receipt_number` is empty | Attach tax invoice/receipt or mark as unavailable |
| `uncategorized` | blocker | No rule matched vendor/description | Add description, split row, or map manually |
| `missing_home_office_percent` | blocker | Home-office row without configured percentage | Supply documented dedicated-area percentage |
| `small_equipment` | info | Asset keyword but amount below threshold | Confirm whether immediate expense is allowed |
| `travel_docs_required` | warning | Business travel abroad category | Attach itinerary, business purpose, receipts |
| `foreign_guest_details_required` | warning | Foreign guest hospitality category | Attach guest identity, country, role, and business purpose |
| `strict_mode` | blocker | Strict mode enabled and warnings remain | Resolve warnings before export |

## Official external services and request/response references

The helper does not call government systems. Use this section as an implementation reference only after registering through the Tax Authority development process and confirming the current developer-portal documentation.

### Invoice Israel allocation-number services

Source: Israel Tax Authority API description for the Invoice Israel model, version 2.0, accessed 2026-06-02. The official document lists OAuth2 user-restricted authorization and JSON request bodies.

| Service | Sandbox URL | Production URL | Notes |
|---|---|---|---|
| Approval | `https://ita-api.taxes.gov.il/shaam/tsandbox/Invoices/v2/Approval` | `https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval` | Request an allocation number for one invoice. |
| Multi Approval | `https://ita-api.taxes.gov.il/shaam/tsandbox/Multi-invoices/v2/MultiApproval` | `https://ita-api.taxes.gov.il/shaam/production/Multi-invoices/v2/MultiApproval` | Request allocation numbers for a batch of invoices. |
| Invoice information details | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/details` | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/details` | Retrieve invoice details by customer VAT number, allocation number, and supplier VAT number. |
| Invoice information confirmation number | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/confirmationNumber` | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/confirmationNumber` | Retrieve allocation number by invoice details. |
| Invoice decision | `https://ita-api.taxes.gov.il/shaam/tsandbox/Invoice-decision/v1/Cancel` and related actions | `https://ita-api.taxes.gov.il/shaam/production/Invoice-decision/v1/Cancel` and related actions | Official documents use endpoint casing inconsistently in secondary references. Confirm in the developer portal before implementation. |

### Allocation threshold reference for 2026

For 2026, an allocation number is required as a condition for input VAT deduction above the legal transaction threshold: more than ₪10,000 before VAT from 01/01/2026, and more than ₪5,000 before VAT from 01/06/2026. The package keeps allocation fields for accountant review but does not validate allocation numbers online.

### Example: validation request shape for a future integration

```http
POST /shaam/production/invoice-information/v1/details HTTP/1.1
Accept: application/json
Content-Type: application/json
Authorization: Bearer <token>

{
  "Number_VAT_Customer": 512345678,
  "Number_Confirmation": "123456789",
  "Number_Vat": 515151515
}
```

Successful response shape based on the official API examples:

```json
{
  "Status": 200,
  "Message": {
    "Invoice_Type": 305,
    "Vat_Number": 515151515,
    "Invoice_Reference_Number": "INV-1001",
    "Customer_VAT_Number": 512345678,
    "Invoice_Date": "2026-01-15",
    "Amount_Payment": 198.31,
    "VAT_Amount": 35.69,
    "Payment_Amount_Including_VAT": 234.00
  }
}
```

Confirmation-number lookup response shape:

```json
{
  "Status": 200,
  "Message": "Invoice confirmation number for the received data is: 20240704061109183186068226",
  "Confirmation_Number": "20240704061109183186068226"
}
```

Decision-service response examples from the official document:

```json
{
  "status": 200,
  "message": "Decision accepted"
}
```

```json
{
  "status": 400,
  "message": {
    "errors": [
      {
        "code": 463,
        "message": "No matching unapproved invoice found",
        "param": "invoice_id",
        "location": "request"
      }
    ]
  }
}
```

### External API error table

| HTTP code | Meaning in official API material | Handling in an Expense Manager integration |
|---:|---|---|
| 200 | Request processed; response can still contain unapproved invoice details or confirmation number `0` | Inspect response fields, not only HTTP status. |
| 400 | Request includes logical or JSON data errors | Block validation and correct payload before retrying. |
| 401 | Security checks failed or token is invalid | Refresh OAuth2 credentials and verify client registration. |
| 403 | Permission denied for the service | Confirm API permissions in the developer portal. |
| 404 | Requested URI not found | Recheck endpoint path and environment host. |
| 406 | Request not acceptable for the operation | Confirm VAT-number permissions and requested operation. |
| 422 | Schema validation failure | Validate all objects against the current schema. |
| 500 | Internal server error | Retry later and keep validation pending. |

### Local placeholder error table

When an implementation wraps the official services behind an internal adapter, normalize errors to the following local codes before feeding them into Expense Manager review flags.

| Error | Meaning | Handling |
|---|---|---|
| `allocation_not_found` | Allocation number not confirmed | Flag row before input VAT claim. |
| `supplier_mismatch` | Supplier VAT ID differs | Block import until corrected. |
| `amount_mismatch` | Gross or VAT amount differs | Reconcile invoice data. |
| `date_out_of_range` | Invoice date outside supported period | Confirm current API rules. |
| `unauthorized` | Token or permissions invalid | Refresh credentials through official channel. |
| `service_unavailable` | Government service unavailable | Retry later; do not assume validity. |

### Uniform-file and accounting-software compatibility

Common Israeli bookkeeping systems often import CSV/Excel-style accountant files and may also generate or validate official uniform-structure files. This package exports accountant-ready CSV, JSON, mapping metadata, source copies, and a SHA-256 manifest. It is not registered bookkeeping software and does not generate an official uniform-structure file. Use registered software or the Tax Authority simulator when an official uniform file is required.

## Change control

Update this reference whenever:

- The Israel Tax Authority changes an indexed cap or reporting threshold.
- A bookkeeping system changes import-field names.
- A new official API integration is added.
- A rule moves from conservative default to verified workflow.
