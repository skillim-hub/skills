# API and Regulation Reference

This skill is a validation and workflow helper. It does not assume access to a public Israeli domestic transfer submission API. Use the structures below for internal approval queues, bank-form prefill, audit trails, or adapters to bank-provided channels.

Verify current legal, regulatory, and bank-specific requirements before production use.

## Web-validated official source register

Access date for every row: 2026-06-02. Quote snippets are short excerpts from the live source and are intentionally limited.

| Topic | Official source URL | Verified snippet | Package use |
|---|---|---|---|
| VAT rate | https://www.gov.il/BlobFolder/dynamiccollectorresultitem/represent-info-051224-2/he/vat_represent-info-051224-2.pdf | `החל מיום 01/01/2025 יחול מע״מ בשיעור של .18%` | Use 18% only in tax-payment purpose text and accounting context. |
| VAT history | https://www.gov.il/he/pages/vat-history | `1.1.25 עלה המע״מ ל-18%` | Second source for current VAT-rate wording. |
| Zahav operating days | https://www.boi.org.il/media/1x1a4n3r/zahav-holidays-2026-eng.pdf | `operating days of the RTGS system are Sunday through Friday` | Warn Friday as short-day risk, not a blanket weekend error. |
| Zahav short day | https://www.boi.org.il/media/1x1a4n3r/zahav-holidays-2026-eng.pdf | `Friday and holiday eves—the banking business day ends at 14:00` | Require cutoff/calendar confirmation for Friday and holiday eves. |
| Zahav RTGS | https://www.boi.org.il/en/economic-roles/payment-systems/payment-systems-in-israel/zahav/ | `real-time, final, efficient, and reliable settlement of shekel payments` | Recommend Zahav for urgent final settlement. |
| Zahav no minimum | https://www.boi.org.il/en/economic-roles/payment-systems/payment-systems-in-israel/zahav/ | `The use of the Zahav system is not dependent on a minimum amount` | Do not present an official Zahav minimum amount. |
| Zahav fees | https://www.boi.org.il/en/economic-roles/payment-systems/payment-systems-in-israel/zahav/ | `The fee is determined by each bank, and therefore changes from bank to bank` | Do not hard-code customer bank fees. |
| MASAV purpose | https://www.boi.org.il/en/economic-roles/supervision-and-regulation/payment-systems-oversight/masav/ | `electronic system for settling shekel transactions` | Use MASAV for routine shekel credits, debits, payroll, tax payments, and batches. |
| MASAV clearing windows | https://www.boi.org.il/roles/supervisionregulation/payment-systems-oversight/masav/ | `קיימים שני חלונות סליקה` | Document deferred/batch behavior and bank cutoff dependency. |
| Identification codes | https://www.boi.org.il/en/economic-roles/supervision-and-regulation/payment-systems-oversight/access-to-payment-systems/identification-codes/ | `Payment service providers...required to obtain a unique ID code` | Treat bank codes as Bank of Israel identification codes. |
| Code 9 | https://www.boi.org.il/en/economic-roles/supervision-and-regulation/payment-systems-oversight/access-to-payment-systems/identification-codes/ | `D.I. POSTAL FINANCE Ltd 9` | Normalize code 9 to Postal Finance. |
| Code 54 | https://www.boi.org.il/en/economic-roles/supervision-and-regulation/payment-systems-oversight/access-to-payment-systems/identification-codes/ | `Bank of Jerusalem Ltd 54` | Normalize code 54 to Bank of Jerusalem. |
| Code expansion | https://www.boi.org.il/en/communication-and-publications/press-releases/the-bank-of-israel-announces-an-expansion-of-the-identification-code-used-by-nonbank-corporations-to-connect-to-the-payment-systems-to-three-digits-as-a-further-step-in-opening-access-to-the-payment-systems/ | `currently composed of two digits. It will be expanded to three digits` | Accept 1 to 3 digit codes and warn when unknown. |
| Branch source | https://www.boi.org.il/information/bank-branch-locate/ | `רשימת הסניפים של התאגידים הבנקאיים ומערכות תשלומים שאינן בנק` | Treat local branch validation as format-only unless an official branch table is integrated. |
| Open banking payments | https://boi.org.il/media/s2pjyjfi/boi-implementation-guidelines-v17_16_11_2023.pdf | `payments/{payment-product} POST Mandatory Create a payment initiation resource` | Document ASPSP/TPP payment-initiation endpoint patterns separately from manual form help. |
| Payment products | https://www.gov.il/BlobFolder/dynamiccollectorresultitem/notice-2023-061/he/main_1.6.yaml_.txt | `masav`, `zahav`, `fp` | Mention product identifiers only when building regulated adapters. |
| Status notifications | https://boi.org.il/media/fhwbfq1k/111529.pdf | `where Xi is one of the constants SCA, PROCESS, LAST` | Do not invent helper webhook event names. |
| Consent status | https://boi.org.il/media/fhwbfq1k/111529.pdf | `revokedByPsu The consent has been revoked` | Use official status names only in open-banking adapters. |
| Payment Services Law context | https://boi.org.il/media/l1qm2pql/access-guide-to-ps-english.pdf | `Payment service providers...required to obtain a unique ID code` | Keep licensing and access controls outside the form helper. |
| Recordkeeping | https://www.gov.il/BlobFolder/generalpage/income-tax-guide-knowyourright/he/Guides_IncomeTax_da-2025.pdf | `לנהל את פנקסי חשבונותיו` | Preserve source document, purpose, approver, and audit trail. |

## Open banking and payment-initiation boundary

This package is not a regulated bank API client and does not submit payments. Use it for validation, normalization, local review records, and bank-form preparation.

Regulated open-banking/payment-initiation implementations can expose ASPSP-specific hosts and endpoint paths. Do not assume one national host. Common endpoint patterns in the Bank of Israel implementation guidelines include:

```text
POST /v1/payments/{payment-product}
GET  /v1/payments/{payment-product}/{paymentId}
GET  /v1/payments/{payment-product}/{paymentId}/status
POST /v1/{payment-service}/{payment-product}/{paymentId}/authorisations
```

Product identifiers verified for Israeli domestic payment initiation include `masav`, `zahav`, and `fp`. A bank or ASPSP can publish which products and endpoints it supports.

### Webhook and notification terminology

The helper defines no webhook event names. For open-banking resource-status notifications, use official constants such as `SCA`, `PROCESS`, and `LAST`. For consent lifecycle status, use official statuses such as `revokedByPsu`, `terminatedByTpp`, `suspendedByASPSP`, and `expired` when the integration scope actually includes consent status handling.

### Rates, thresholds, and fees

- VAT is 18% from 01/01/2025 in the official Tax Authority interpretation; use it only when the payment purpose or source document concerns VAT.
- Zahav customer fees are bank-specific; do not hard-code them. Participant or infrastructure fees are not end-user bank fees.
- `₪50,000` production approval and `₪1,000,000` high-value routing are internal configurable controls in this package. They are not official thresholds.

## Israeli operational and regulatory references

| Reference | Why it matters | Practical use in the helper |
|---|---|---|
| Bank of Israel payment systems publications | Describes Israeli payment infrastructure and the role of designated payment systems. | Treat Zahav and MASAV as distinct operational rails with different settlement behavior. |
| Bank of Israel banking supervision directives | Relevant to banking controls, customer authentication, risk management, and payment operations. | Require bank-specific approval, permissions, and audit controls outside the helper. |
| MASAV company operational materials | Relevant to batch clearing, salary files, credits, debits, and participant rules. | Validate each row before batch submission and respect bank-specific upload cutoffs. |
| Zahav real-time gross settlement materials | Relevant to high-value and time-sensitive final settlement. | Recommend Zahav for urgent or high-value payments and prompt for independent verification. |
| Prohibition on Money Laundering Law and related orders | Relevant to unusual transactions, source of funds, and reporting obligations. | Do not classify compliance status; capture purpose and source document identifiers. |
| Privacy Protection Law and data security regulations | Relevant to personal data in payroll, refunds, and account details. | Minimize personal data, redact account numbers in routine reports, and restrict access. |
| Income Tax and VAT recordkeeping expectations | Relevant to supplier invoices, tax payments, payroll, and audit trails. | Capture source documents, periods, and payment purpose. |
| Israeli standard banking identifiers | Bank code, branch code, and local account number vary by bank. | Normalize fields but require official recipient confirmation where ownership matters. |

## Internal request schema

Use this JSON structure when feeding a request into a queue or automation layer.

```json
{
  "recipient_name": "Example Supplier Ltd",
  "payer_name": "Acme Israel Ltd",
  "bank_code": "12",
  "branch_code": "456",
  "account_number": "123456789",
  "amount_ils": "2450.80",
  "value_date": "03/06/2026",
  "method": "auto",
  "purpose": "Invoice 1007",
  "reference": "INV-1007",
  "urgent": false,
  "same_day": false,
  "recurring": false,
  "bulk_count": 1,
  "approved_by": "",
  "source_document_id": "INV-1007"
}
```

### Field rules

| Field | Type | Rule | Error or warning |
|---|---|---|---|
| `recipient_name` | string | Required, non-empty | Error when missing |
| `bank_code` | string | 1 to 3 digits after digit normalization | Error when invalid; warning when unknown |
| `branch_code` | string | 1 to 3 digits, normalized to three digits | Error when invalid; warning when padded |
| `account_number` | string | 4 to 12 digits after normalization | Error when invalid |
| `amount_ils` | string or number | Positive decimal in ₪ | Error when missing, nonnumeric, zero, or negative |
| `value_date` | string | `YYYY-MM-DD`, `DD-MM-YYYY`, or `DD/MM/YYYY`; not past | Error for invalid or past; warning for Friday short day or Saturday closure risk |
| `method` | string | `auto`, `masav`, or `zahav` | Warning for method mismatch |
| `purpose` | string | Recommended operational description | Warning when missing |
| `reference` | string | Default maximum 35 characters | Warning when longer |
| `approved_by` | string | Recommended for production and high-value flows | Warning in production over ₪50,000 when missing |

## Internal validation response

```json
{
  "valid": true,
  "normalized": {
    "payer_name": "Acme Israel Ltd",
    "recipient_name": "Example Supplier Ltd",
    "bank_code": "12",
    "bank_name": "Bank Hapoalim",
    "branch_code": "456",
    "account_number": "123456789",
    "redacted_account_number": "*****6789",
    "amount_ils": "2450.80",
    "amount_display": "₪2,450.80",
    "method": "masav",
    "requested_method": "auto",
    "value_date": "2026-06-03",
    "value_date_display": "03/06/2026",
    "purpose": "Invoice 1007",
    "reference": "INV-1007",
    "urgent": false,
    "same_day": false,
    "recurring": false,
    "bulk_count": 1,
    "approved_by": "",
    "source_document_id": "INV-1007",
    "environment": "sandbox"
  },
  "decision": {
    "method": "masav",
    "reasons": ["Non-urgent single transfer."],
    "cutoff_note": "Allow normal bank processing time and avoid last-minute payroll or supplier deadlines."
  },
  "issues": []
}
```

## Local create response

The CLI `create` command stages a local review record. It does not send money.

```json
{
  "id": "dtf_9cc8e32d51f2a2a0",
  "environment": "sandbox",
  "created_at": "2026-06-02T10:30:00+00:00",
  "status": "ready_for_review",
  "report": {
    "valid": true,
    "normalized": {
      "recipient_name": "Example Supplier Ltd",
      "bank_code": "12",
      "branch_code": "456",
      "account_number": "123456789",
      "amount_display": "₪2,450.80",
      "method": "masav"
    },
    "decision": {
      "method": "masav",
      "reasons": ["Non-urgent single transfer."],
      "cutoff_note": "Allow normal bank processing time and avoid last-minute payroll or supplier deadlines."
    },
    "issues": []
  }
}
```

Use `id` from the response with `payload`, `show`, or an internal approval step.

## Bank-form payload response

```json
{
  "id": "dtf_9cc8e32d51f2a2a0",
  "environment": "sandbox",
  "transfer": {
    "recipient_name": "Example Supplier Ltd",
    "bank_code": "12",
    "branch_code": "456",
    "account_number": "123456789",
    "amount_ils": "2450.80",
    "amount_display": "₪2,450.80",
    "method": "masav",
    "value_date_display": "03/06/2026",
    "purpose": "Invoice 1007",
    "reference": "INV-1007"
  },
  "decision": {
    "method": "masav",
    "reasons": ["Non-urgent single transfer."],
    "cutoff_note": "Allow normal bank processing time and avoid last-minute payroll or supplier deadlines."
  },
  "warnings": [],
  "infos": []
}
```

## Error table

| Code | Severity | Field | Meaning | Recommended correction |
|---|---|---|---|---|
| `required` | error | varies | Required value missing | Request the missing value from the payment owner. |
| `invalid_bank_code` | error | `bank_code` | Bank code is not 1 to 3 digits after normalization | Copy bank code from official recipient confirmation. |
| `unknown_bank_code` | warning | `bank_code` | Code is not in the local reference table | Verify with bank or recipient; update reference data when confirmed. |
| `invalid_branch_code` | error | `branch_code` | Branch code is not 1 to 3 digits | Enter a valid branch code, preserving leading zeroes. |
| `branch_padded` | warning | `branch_code` | Branch was normalized to three digits | Confirm the bank form expects the padded value. |
| `invalid_account_number` | error | `account_number` | Account number is not 4 to 12 digits | Use the recipient account number without branch prefix. |
| `invalid_amount` | error | `amount_ils` | Amount is missing, nonnumeric, zero, or negative | Enter a positive ₪ amount. |
| `high_value_masav` | warning | `method` | MASAV selected for a high-value transfer | Consider Zahav and extra approval. |
| `value_date_invalid` | error | `value_date` | Date format not supported | Use `YYYY-MM-DD`, `DD-MM-YYYY`, or `DD/MM/YYYY`. |
| `value_date_past` | error | `value_date` | Date is before today | Select today or a future banking business day. |
| `value_date_calendar_check` | warning | `value_date` | Friday, Saturday, holiday eve, or closure-day risk | Check the Bank of Israel operating calendar and bank cutoff before submission. |
| `purpose_missing` | warning | `purpose` | Missing payment purpose | Add invoice, salary month, rent, refund, or tax period. |
| `reference_too_long` | warning | `reference` | Reference can be truncated by bank fields | Shorten the bank reference and keep full internal reference elsewhere. |
| `method_mismatch` | warning | `method` | Manual method conflicts with urgency or amount signals | Recheck MASAV versus Zahav suitability. |
| `confirmation_recommended` | info | `recipient` | Independent recipient-detail confirmation is recommended | Confirm details by a trusted channel before submission. |
| `production_requires_approval` | warning | `approved_by` | Production high-value transfer lacks approver | Record approver before portal entry. |

## Adapter guidance

When connecting this helper to an internal approval queue or bank-provided channel:

1. Keep the helper as a pre-submission validator.
2. Store raw request, normalized fields, warnings, and final approval decision.
3. Require separate bank authentication and authorization.
4. Never convert a warning into an automatic approval.
5. Make the bank adapter reject any payload with `valid=false`.
6. Reconcile submission result and bank reference after the bank confirms processing.
7. Keep local record identifiers separate from bank confirmation identifiers.
8. Redact account numbers in logs by default.

## Non-API equivalence

When no API exists, treat the CLI and Python functions as a structured form assistant:

- `validate_transfer` equals field-level validation.
- `recommend_transfer_method` equals routing guidance.
- `create_transfer_record` equals local staging for review.
- `record_payload` equals a copy-ready normalized form view.
- `format_report` equals an operator-facing checklist.
