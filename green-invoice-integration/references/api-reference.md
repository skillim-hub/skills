# API and Regulation Reference

Access date for all sources: 05-06-2026.

## Source register

| Area | Source | URL | Short quote |
|---|---|---|---|
| API documentation entry point | Green Invoice API docs | https://www.greeninvoice.co.il/api-docs/ | "API documentation for developers and companies" |
| API infrastructure update | Green Invoice API updates 2026 | https://www.greeninvoice.co.il/help-center/api-updates-26/ | "add also: grant_type: client_credentials" |
| API key setup | API key generation help | https://www.greeninvoice.co.il/help-center/generating-api-key/ | "the secret key is displayed once" |
| Webhooks | Webhook setup help | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "URL ... https only" |
| Webhook payload and document types | document/created help | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "type 320" |
| Add document endpoint | Apiary add-document reference | https://greeninvoice.docs.apiary.io/reference/documents/add-document/add-document | "POST https://api.greeninvoice.co.il/api/v1/documents" |
| Payment links | Payment-link help | https://www.greeninvoice.co.il/help-center/create-payment-link/ | "create a payment link for a fixed amount" |
| Digital payments | Digital payments help | https://www.greeninvoice.co.il/help-center/digital-payments/ | "credit, bit, Google Pay and Apple Pay" |
| VAT rates | Israel Tax Authority VAT amounts and rates | https://www.gov.il/en/pages/vat-rate-amount-new | "amounts and rates set out in VAT legislation" |
| VAT increase | Knesset press release | https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx | "VAT rate from 17% to 18%" |
| Israel Invoices threshold | Israel Invoice landing page | https://www.gov.il/en/departments/topics/israel-invoice/govil-landing-page | "5,000 NIS starting June 1, 2026" |
| Allocation-number request | Allocation number service | https://www.gov.il/en/service/request-assignment-number-for-tax-invoice | "Invoice amount before VAT" |
| Supplier invoice verification | Supplier invoice verification service | https://www.gov.il/en/service/verify-vendor-invoice-information | "deducting input tax" |
| Exempt dealer registration | Exempt dealer online application | https://www.gov.il/en/service/request-open-exempt-dealer-via-internet | "open a tax-exempt dealer file" |
| Authorized dealer form | VAT form 821 | https://www.gov.il/en/service/vat-821 | "open an authorized dealer file with VAT" |
| Small business threshold | Small Business Owner topic | https://www.gov.il/en/departments/topics/income-tax-small-business-owner-24 | "around 122,833 ₪ in 2026" |

## Environments and authentication

| Environment | Base URL |
|---|---|
| Production | `https://api.greeninvoice.co.il/api/v1` |
| Sandbox | `https://sandbox.d.greeninvoice.co.il/api/v1` |

Token request:

```http
POST /account/token
Content-Type: application/json
```

```json
{
  "id": "API_KEY_ID",
  "secret": "API_KEY_SECRET",
  "grant_type": "client_credentials"
}
```

Token response can expose the bearer token as `token`, `access_token`, or an authorization header depending on rollout state. Robust clients should check each location.

## Core endpoint map

| Operation | Method | Path | Validation status |
|---|---|---|---|
| Get token | `POST` | `/account/token` | Official 2026 update confirms token-body change |
| Verify credentials | `GET` | `/users/me` | Common Green Invoice API pattern; verify in current developer portal |
| Create client | `POST` | `/clients` | Exposed by integration module docs and common API clients |
| Search clients | `POST` | `/clients/search` | Exposed by integration module docs and common workflows |
| Get client | `GET` | `/clients/{id}` | Exposed by integration module docs |
| Update client | `PUT` | `/clients/{id}` | Exposed by integration module docs |
| Create document | `POST` | `/documents` | Apiary search result confirms full production URL |
| Search/list documents | `POST` | `/documents/search` | Exposed by integration module docs; verify response shape per account |
| Get document | `GET` | `/documents/{id}` | Exposed by integration module docs |
| Cancel document | `POST` | `/documents/{id}/cancel` | Treat as account-version sensitive; fallback to credit-note flow |
| Download document | `GET` | `/documents/download?d=...` | Present in official webhook payload example |
| Payment link | Account-specific | Confirm in developer portal | Product help confirms links; public endpoint can vary |

## Document schema essentials

Minimal tax invoice-receipt payload:

```json
{
  "type": 320,
  "date": "2026-06-05",
  "lang": "he",
  "currency": "ILS",
  "vatType": 0,
  "client": {
    "name": "Demo Client Ltd",
    "emails": ["billing@example.com"],
    "country": "IL",
    "taxId": "512345678"
  },
  "income": [
    {
      "description": "Consulting service",
      "quantity": 1,
      "price": 1000,
      "currency": "ILS",
      "vatRate": 0.18
    }
  ],
  "payment": [
    {
      "type": 4,
      "date": "2026-06-05",
      "price": 1180,
      "currency": "ILS"
    }
  ],
  "signed": true,
  "attachment": true
}
```

## Document types

| Code | Hebrew | English | Notes |
|---:|---|---|---|
| 10 | הצעת מחיר | Price quote | No payment record required |
| 100 | הזמנה | Order | Sales order |
| 200 | תעודת משלוח | Delivery note | Goods delivery |
| 210 | תעודת החזרה | Return note | Returned goods |
| 300 | חשבון עסקה | Transaction invoice | Use before payment where no receipt exists |
| 305 | חשבונית מס | Tax invoice | VAT invoice; check allocation number for B2B threshold |
| 320 | חשבונית מס / קבלה | Tax invoice-receipt | Use when payment is recorded immediately |
| 330 | חשבונית זיכוי | Credit note | Use for cancellation/correction/refund |
| 400 | קבלה | Receipt | Payment receipt |
| 405 | קבלה על תרומה | Donation receipt | Nonprofit context |
| 500 | הזמנת רכש | Purchase order | Procurement |
| 600 | קבלת פיקדון | Deposit receipt | Deposit received |
| 610 | משיכת פיקדון | Deposit withdrawal | Deposit returned |

## Payment method mapping

| Client value | API value | Notes |
|---|---:|---|
| `cash` | 1 | Cash receipt |
| `check` | 2 | Include bank, branch, account, and check number when available |
| `credit-card` | 3 | Do not store raw card details outside approved payment flow |
| `wire-transfer` | 4 | Common for freelancers and B2B payments |
| `paypal` | 5 | Use only when actually paid through PayPal |
| `app` | 10 | Payment apps; inspect account-specific subtype if needed |
| `other` | 11 | Use sparingly; add a clear remark |

## VAT and Israeli thresholds

| Item | Current value | Operational effect |
|---|---:|---|
| Standard VAT | `18%` | Use `0.18` in calculations unless a specific exemption or zero-rate rule applies |
| Israel Invoices threshold from `01-06-2026` | `₪5,000` before VAT | B2B tax invoices above this amount require allocation-number handling for input-tax deduction |
| Exempt dealer annual turnover indicator for 2026 | About `₪122,833` | Confirm status with official guidance and accountant before issuing VAT-bearing documents |

## Official forms and services

| Need | Official service |
|---|---|
| Open an exempt dealer file | `request-open-exempt-dealer-via-internet` |
| Open an authorized dealer VAT file | `vat-821` |
| Request allocation number for a tax invoice | `request-assignment-number-for-tax-invoice` |
| Verify a supplier invoice by allocation number | `verify-vendor-invoice-information` |
| Book a Tax Authority appointment | `scheduling-appointment-taxes` |

## Webhook topics

Official help lists these topics for webhook configuration:

| Topic | Meaning | Suggested handler action |
|---|---|---|
| `document/created` | Document issued | Fetch document, store PDF link, route by type |
| `client/created` | Customer created | Sync CRM record |
| `supplier/created` | Supplier created | Sync vendor master data |
| `payment/received` | Digital payment received | Reconcile payment and receipt |
| `sale-pages/page-contacted` | Sales page lead | Create lead record |
| `sale-pages/order-paid` | Sales page order paid | Reconcile order and issue follow-up |
| `expense-draft/parsed` | Expense draft parsed | Route for review |
| `expense/file-updated` | Expense file updated | Refresh local attachment |
| `file/infected` | File vulnerability issue | Block processing and alert operator |
| `expense-draft/declined` | Expense draft rejected | Mark failed import |

## Error tables

### HTTP errors

| Status | Meaning | Most likely cause | Next action |
|---:|---|---|---|
| 400 | Bad request | Missing field, bad enum, wrong gross/net handling | Validate payload against examples and current developer portal |
| 401 | Unauthorized | Token expired, wrong bearer header, legacy token body | Request a new token with `grant_type` |
| 403 | Forbidden | Plan, scope, payment, or webhook feature unavailable | Check plan and feature access in dashboard |
| 404 | Not found | Wrong id, retired host, disabled endpoint | Use current base URL and fetch the object from dashboard |
| 409 | Conflict | Duplicate or invalid state transition | Fetch current document status before retry |
| 422 | Validation failed | Date, VAT, customer, or payment data invalid | Print response JSON and correct fields |
| 429 | Rate limited | Burst automation | Back off with jitter and reduce concurrency |
| 500/502/503 | Server issue | Temporary platform issue | Retry safely only for idempotent reads or idempotency-protected writes |

### Business-rule errors

| Symptom | Likely cause | Action |
|---|---|---|
| Buyer rejects invoice | Allocation number missing | Renew Tax Authority authorization and reissue or correct document |
| Duplicate customer | Search skipped or matched by display name only | Search by tax id and email before creation |
| Wrong VAT amount | Used 17% or mixed net/gross amounts | Recalculate at 18% and mark gross treatment explicitly |
| Payment not linked | Receipt created without original document id | Link receipt or reconcile manually in dashboard |
| Webhook repeats | Six-second timeout or non-2xx response | Store event id before slow processing and return quickly |
| Payment link unavailable | Digital payments not connected | Connect payment service or use payment-enabled document |

## Compliance notes

This package does not replace accounting judgment. It provides operational controls and API handling. Confirm tax classification, deductible VAT, exempt dealer status, cross-border VAT, nonprofit donation receipts, and allocation-number obligations with official guidance or a qualified adviser.
