# API and Regulation Reference

Access date: 2026-06-04.

## Source register

| Topic | Source URL | Short quote |
|---|---|---|
| Invoice allocation API v2 | https://www.gov.il/BlobFolder/generalpage/hor-software-other/he/vat_software-houses-180724.pdf | "OAuth2: User Restricted" |
| English mirror of API v2 | https://assets.kpmg.com/content/dam/kpmg/il/pdf/vat_software-houses-ENG.pdf | "Sandbox url" |
| Public guide for businesses | https://govextra.gov.il/taxes/innovation/home/israel-invoices/ | "מספר הקצאה" |
| API services listing | https://govextra.gov.il/taxes/innovation/home/api/ | "שירותי ה-API של רשות המסים" |
| Manual allocation request | https://www.gov.il/he/service/request-assignment-number-for-tax-invoice | "השירות ניתן ללא עלות" |
| Supplier invoice verification | https://www.gov.il/he/service/verify-vendor-invoice-information | "אימות פרטי חשבונית הספק" |
| Digital authorization | https://www.gov.il/he/service/authorize-certification-perform-digital-operations | "פעולות דיגיטליות" |
| 2026 threshold notice | https://www.gov.il/he/pages/pa240525-1 | "תחול מ-5,000 ₪" |
| 2025 VAT increase approval | https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx | "effective January 1, 2025" |
| VAT rates page | https://www.gov.il/en/pages/vat-rate-amount-new | "VAT legislation and regulations" |

Use the official Tax Authority portal as the governing source for live integration. The English mirror is useful when the gov.il PDF blocks automated fetching, but production implementations should confirm the official Hebrew PDF and OpenAPI portal.

## Current VAT rate

The standard VAT rate is 18% from 01-01-2025 onward. For invoices with older dates, select the rate in force on the invoice date and keep evidence for any zero-rate or exempt treatment.

## Allocation thresholds

| Effective period | Allocation threshold before VAT | Practical rule |
|---|---:|---|
| 01-05-2024 to 31-12-2024 | Above ₪25,000 | Pilot year; technical denials still possible. |
| 01-01-2025 to 31-12-2025 | Above ₪20,000 | Allocation becomes material for input VAT deduction. |
| 01-01-2026 to 31-05-2026 | Above ₪10,000 | Validate customer VAT number for B2B requests. |
| 01-06-2026 onward | Above ₪5,000 | Treat threshold as operationally active for Israeli B2B tax invoices. |

The threshold is tested against `payment_amount` before VAT, not the amount including VAT.

## Endpoint catalogue

### Allocation approval

| Environment | Method | URL |
|---|---|---|
| Sandbox | POST | `https://ita-api.taxes.gov.il/shaam/tsandbox/Invoices/v2/Approval` |
| Production | POST | `https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval` |

### Batch allocation approval

| Environment | Method | URL |
|---|---|---|
| Sandbox | POST | `https://ita-api.taxes.gov.il/shaam/tsandbox/Multi-invoices/v2/MultiApproval` |
| Production | POST | `https://ita-api.taxes.gov.il/shaam/production/Multi-invoices/v2/MultiApproval` |

### Recipient-side invoice details by allocation number

| Environment | Method | URL |
|---|---|---|
| Sandbox | POST | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/details` |
| Production | POST | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/details` |

### Recipient-side allocation number by invoice details

| Environment | Method | URL |
|---|---|---|
| Sandbox | POST | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/confirmationNumber` |
| Production | POST | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/confirmationNumber` |

### Decision update for held invoice

| Decision | Sandbox URL | Production URL |
|---|---|---|
| Cancel | `https://ita-api.taxes.gov.il/shaam/tsandbox/InvoiceDecisionApi/v1/Cancel` | `https://ita-api.taxes.gov.il/shaam/production/InvoiceDecisionApi/v1/Cancel` |
| Continue without allocation | `https://ita-api.taxes.gov.il/shaam/tsandbox/InvoiceDecisionApi/v1/Continue` | `https://ita-api.taxes.gov.il/shaam/production/InvoiceDecisionApi/v1/Continue` |
| Further objection/hearing | `https://ita-api.taxes.gov.il/shaam/tsandbox/InvoiceDecisionApi/v1/FurtherObjection` | `https://ita-api.taxes.gov.il/shaam/production/InvoiceDecisionApi/v1/FurtherObjection` |

## Authentication and headers

| Element | Requirement |
|---|---|
| Authorization | `Bearer <access_token>` from the Tax Authority authorization flow. |
| Authorization model | OAuth2 user-restricted authorization. |
| `Accept` | `application/json`. |
| `Content-Type` | `application/json`. |
| Permissions | The operator must hold permission for the relevant dealer, service, and environment. |

## Allocation approval request fields

| API field | Meaning | Requirement |
|---|---|---|
| `invoice_id` | Internal bookkeeping ID | Mandatory |
| `invoice_type` | Document type code | Mandatory |
| `vat_number` | Seller VAT dealer number | Mandatory |
| `union_vat_number` | VAT union number | Conditional |
| `authorized_company` | Authorized corporation/entity | Conditional |
| `user_id` | Service operator ID | Conditional |
| `user_name` | Service operator username | Conditional |
| `accounting_software_number` | Software registration or producer company number | Mandatory |
| `customer_vat_number` | Buyer VAT dealer number | Mandatory for Israeli B2B allocation |
| `customer_name` | Buyer name | Mandatory when available |
| `invoice_date` | Printed date, `YYYY-MM-DD` | Mandatory |
| `invoice_issuance_date` | System issue date, `YYYY-MM-DD` | Mandatory |
| `amount_before_discount` | Amount before discount and VAT | Mandatory |
| `discount` | Absolute discount amount | Mandatory |
| `payment_amount` | Total before VAT | Mandatory |
| `vat_amount` | VAT amount | Mandatory |
| `payment_amount_including_vat` | Total including VAT | Mandatory |
| `invoice_note` | Notes | Optional |
| `action` | Special action such as reverse charge | Conditional |
| `items` | Invoice line list | Required where line-level detail is sent |

## Response handling

Store these response fields:

- `status` or `Status`
- `message` or `Message`
- `confirmation_number` or `Confirmation_Number`
- `approved` where present
- `transaction_id` for batch requests
- full error list with `code`, `message`, `param`, `location`

When the full allocation number is received, store it. For PCN874 reporting, use the right-most 9 characters where required.

## HTTP error table

| HTTP code | Meaning | Action |
|---:|---|---|
| 400 | Logical bad request | Inspect the API error list and fix the payload. |
| 401 | Unauthorized | Refresh token and confirm OAuth2 configuration. |
| 403 | Forbidden | Recheck permissions for the dealer and service. |
| 404 | Not found | Correct host, environment, service version, or path. |
| 406 | Not acceptable | Confirm permission for the VAT number or customer VAT number. |
| 422 | Schema mismatch | Validate JSON object shapes and field formats. |
| 500 | Server error | Check permissions and retry according to incident policy before contacting support. |

## Business error table

| Code | Message pattern | Typical fix |
|---:|---|---|
| 431 | VAT Number is incorrect | Validate 9-digit VAT number and check digit. |
| 434 | Invoice date is too old for approval | Check retroactive rules and avoid stale invoice dates. |
| 435 | Invoice date is more than a month ahead | Use the actual printed invoice date. |
| 438 | Invoices amount is not the same as actual invoices amount | Recalculate batch summary totals. |
| 446 | Required one of user ID or user name | Send one service-operator identifier. |
| 460 | Invoice not approved | Treat as substantive refusal and present held-invoice alternatives. |
| 462 | Unapproved invoice exists and decision was sent | Avoid duplicate decision or changed retry sequence. |
| 463 | No matching unapproved invoice found | Verify `invoice_id`, `vat_number`, and original attempted allocation. |

## Held-invoice alternatives

When allocation is not provided for a substantive reason, present the business user with these choices:

1. Cancel or abandon the invoice.
2. Continue issuing without an allocation number and print a prominent input-tax non-deduction notice.
3. Apply reverse charge where legally and commercially suitable.
4. Request a hearing or further objection through the Tax Authority service channel.

Reverse charge uses the approval service with the required action value and a zero-rate invoice structure. Cancellation, continuation, and further objection use the decision-update service.
