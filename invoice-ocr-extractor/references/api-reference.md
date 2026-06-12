# Israeli API and Regulation Reference

This reference lists official source categories and practical schemas for local invoice extraction. Verify current requirements against official Israeli sources before production use.

## Official sources to verify

| Area | Official source category | Relevance |
|---|---|---|
| VAT invoices and VAT rates | Israel Tax Authority, `taxes.gov.il` and `gov.il` service pages | VAT rate, invoice wording, dealer status, reporting processes |
| Bookkeeping and record retention | Israel Tax Authority bookkeeping instructions and Income Tax regulations | Source document retention, audit trail, required books |
| Digital invoice allocation numbers | Israel Tax Authority online services | Allocation/approval numbers where applicable |
| Company identifiers | Corporations Authority / Registrar databases | Company number and legal entity validation |
| Government API access | Israel government API portal / service documentation | Authentication, endpoint details, developer registration |
| Privacy | Protection of Privacy Law and Privacy Protection Authority guidance | Invoice images can contain personal data |


## Web-validated current values as of 01/06/2026

Use these values as reviewed defaults, not as permanent legal constants. Official Tax Authority publications override this package.

| Item | Current package setting | Validation note |
|---|---:|---|
| Standard VAT rate | 18% | Effective from 01/01/2025 and still used by current 2026 tax summaries. Always prefer the rate printed on the invoice. |
| Allocation threshold, 2025 | Above ₪20,000 before VAT | Relevant to tax invoices for input VAT deduction. |
| Allocation threshold, 01/01/2026-31/05/2026 | Above ₪10,000 before VAT | Corrects the stale 07/2024 API table that listed ₪15,000 for 2026. |
| Allocation threshold from 01/06/2026 | Above ₪5,000 before VAT | Current Tax Authority service page and 2026 announcement confirm this threshold. |
| Allocation request service fee | ₪0 | The Tax Authority service page states that the service is free of charge. |

The parser adds a review flag when an ILS `tax_invoice` or `tax_invoice_receipt` is above the verified threshold for the document date and no allocation number is visible. This is a review aid only.

## Tax Authority endpoint references

The local CLI does not call Tax Authority services. Use the following only when building a separate registered integration.

| Purpose | Sandbox host/path | Production host/path | Notes |
|---|---|---|---|
| Invoice approval / allocation number | `https://ita-api.taxes.gov.il/shaam/tsandbox/Invoices/v2/Approval` | `https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval` | OAuth2, user restricted; software-house registration required. |
| Retrieve invoice information | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/details` | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/details` | Reference endpoint in Tax Authority API documentation. |
| Retrieve confirmation number | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/confirmationNumber` | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/confirmationNumber` | Keep separate from local `document_number`. |
| Received invoices for a period | `https://ita-api.taxes.gov.il/shaam/tsandbox/MultiInvoiceInformationApi/v1/Details` | `https://openapi.taxes.gov.il/shaam/production/MultiInvoiceInformationApi/v1/Details` | Requires customer VAT file and date range fields. |
| Minimum amount for allocation | `https://ita-api.taxes.gov.il/shaam/tsandbox/general-information/v2/MinimumAmount` | `https://openapi.taxes.gov.il/shaam/production/general-information/v2/MinimumAmount` | Returns the minimum amount according to invoice date. |

No webhook event names are referenced by this package. The official materials reviewed describe request/response API services and OAuth2 authorization, not webhook subscriptions.

## Regulation-aware extraction behavior

- `עוסק מורשה`: supplier may issue VAT-bearing tax invoices.
- `עוסק פטור`: do not infer VAT unless VAT appears explicitly.
- `חשבונית מס`: VAT may be present and must be validated.
- `קבלה`: payment evidence; not always a tax invoice.
- `חשבונית מס קבלה`: combined tax invoice and receipt.
- `חשבונית זיכוי`: preserve signs and validate import behavior.

## Israeli business identifiers

### VAT dealer number

Request snippet:

```json
{"text":"עוסק מורשה: 123456789"}
```

Response:

```json
{"business_id":"123456789","business_id_type":"vat_dealer"}
```

### Company number

```json
{"text":"ח.פ. 512345678"}
```

```json
{"business_id":"512345678","business_id_type":"company_number"}
```

### Association number

```json
{"text":"ע.ר. 580123456"}
```

```json
{"business_id":"580123456","business_id_type":"association_number"}
```

## Digital invoice allocation numbers

Treat `מספר הקצאה` or `Allocation Number` as `allocation_number`, not `document_number`.

```json
{"document_number":"700114","allocation_number":"987654321"}
```

## Suggested internal extraction API

### POST /extract

Request:

```json
{"source_type":"ocr_text","locale":"he-IL","default_vat_rate":18.0,"text":"חשבונית מס קבלה מס' 100\nסה\"כ לתשלום ₪118\nמע\"מ 18% ₪18"}
```

Response:

```json
{"schema_version":"2.2.0","data":{"document_type":"tax_invoice_receipt","document_number":"100","currency":"ILS","total_gross":118.0,"vat_amount":18.0,"total_net":100.0,"vat_rate":18.0}}
```

### POST /validate

Request:

```json
{"total_gross":118.0,"total_net":100.0,"vat_amount":19.0,"vat_rate":18.0}
```

Response:

```json
{"valid":false,"errors":[{"code":"VAT_MATH_MISMATCH","field":"vat_amount"}]}
```

## Error table

| Code | Status | Meaning | Action |
|---|---:|---|---|
| `NO_TEXT_FOUND` | 422 | OCR produced no usable text | Rescan or enter manually |
| `UNSUPPORTED_FILE_TYPE` | 415 | Unsupported input | Upload image, PDF, or text |
| `OCR_ENGINE_UNAVAILABLE` | 503 | OCR engine missing | Provide OCR text or install OCR |
| `AMBIGUOUS_TOTAL` | 200 | Multiple totals conflict | Review original document |
| `VAT_MATH_MISMATCH` | 200 | Net, VAT, gross do not reconcile | Preserve visible values and flag |
| `DOCUMENT_NUMBER_MISSING` | 200 | Number not detected | Review manually |
| `VENDOR_MISSING` | 200 | Supplier not detected | Review supplier block |
| `DATE_INVALID` | 200 | Invalid date | Correct manually |
| `FOREIGN_CURRENCY` | 200 | Non-ILS currency | Add exchange-rate workflow |
| `POSSIBLE_DUPLICATE` | 409 | Duplicate key found | Open existing record |
| `PRIVACY_REDACTION_FAILED` | 500 | Sensitive log redaction failed | Stop raw logging |

## CSV export columns

`source_file,date,vendor,document_type,document_number,total_net,vat_amount,total_gross,currency,payment_method,business_id,confidence,review_flags`

## Validation formulas

```text
abs((total_net + vat_amount) - total_gross) <= 0.05
abs((vat_amount / total_net * 100) - vat_rate) <= 0.25
```

## Privacy checklist

Process locally when possible, redact card fragments and phone numbers in logs, encrypt raw images, restrict exports, delete temporary OCR files, and document any external OCR provider before use.
## Record id chaining

A local create-style extraction response includes `record_id`. Use it in the next validation or review step.

Request:

```json
{
  "text": "חשבונית מס קבלה מס' 100\nתאריך 21/05/2026\nסה"כ לתשלום ₪118"
}
```

Create response:

```json
{
  "record_id": "inv_example123",
  "date": "21/05/2026",
  "total_gross": 118.0
}
```

Validation request:

```json
{
  "expected_id": "inv_example123",
  "record_id": "inv_example123"
}
```
