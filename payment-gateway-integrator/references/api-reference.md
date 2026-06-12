# API and Regulation Reference

This reference provides a provider-neutral contract and adapter notes for Cardcom, Tranzila, Pelecard, and Grow. Treat Meshulam as the legacy name or merchant-contract alias for Grow unless a current provider contract exposes a separate Meshulam API.

Validate exact field names, endpoint paths, authentication scheme, webhooks, enabled features, rates, refund windows, and settlement reports against the merchant portal and provider contract before production. Use `references/verification-log.md` for the live-source audit performed on 02/06/2026.

## Official and regulatory reference links

| Area | Reference | Validated note |
|---|---|---|
| Cardcom API v11 | `https://secure.cardcom.solutions/Api/v11/Docs` | Low Profile create and result endpoints were validated. |
| Cardcom support webhooks | `https://support.cardcom.solutions/` | Duplicate callback handling and server-side verification were validated. |
| Tranzila API docs | `https://docs.tranzila.com/` | Payment request endpoint and access-token authentication were validated. |
| Tranzila merchant resources | `https://www.tranzila.com/` | Hosted/iframe and PCI positioning were validated. |
| Grow Payments docs | `https://grow-il.readme.io/` | Current docs identify Grow Payments as formerly Meshulam. |
| Grow API developers | `https://grow.business/api-developers/` | API developer positioning was validated. |
| Pelecard API | `https://pelecard.com/api/` | Payments, credits, standing orders, and reports were validated. |
| Pelecard Gateway21 | `https://gateway21.pelecard.biz/` | Gateway 2.0, IFrame/Redirect, and sandbox links were validated. |
| SHVA and Ashrait | `https://www.shva.co.il/` | Hebrew `אשראית EMV` terminology was validated. |
| Bank of Israel payment systems | `https://www.boi.org.il/` | Payment-system participant and payment-services context was validated. |
| Israel Tax Authority VAT | `https://www.gov.il/he/pages/vat-history` | VAT at 18% from 01/01/2025 was validated. |
| Privacy Protection Authority | `https://www.gov.il/he/departments/the_privacy_protection_authority` | Data-security and serious incident terminology were validated. |
| Consumer Protection Authority | `https://www.gov.il/` | Inclusive price and cancellation-fee guidance were validated. |
| PCI Security Standards Council | `https://www.pcisecuritystandards.org/` | Storage restrictions and cardholder-data framework were validated. |

## Canonical internal API

These paths are the orchestration API exposed by the merchant application. They are not provider endpoint paths.

| Operation | Method | Internal path | Purpose |
|---|---|---|---|
| Create hosted checkout | `POST` | `/payments/checkout` | Create a provider payment page and return a redirect URL. |
| Charge token or safe method | `POST` | `/payments/charge` | Charge an existing provider token or provider-safe method. |
| Authorize | `POST` | `/payments/authorize` | Reserve amount without capture when supported. |
| Capture | `POST` | `/payments/{id}/capture` | Capture a previous authorization. |
| Refund | `POST` | `/payments/{id}/refunds` | Full or partial refund. |
| Status inquiry | `GET` | `/payments/{id}` | Query canonical status. |
| Webhook receiver | `POST` | `/webhooks/{gateway}` | Validate and ingest provider callback. |
| Reconciliation import | `POST` | `/reconciliation/{gateway}` | Import settlement and fee reports. |

## Canonical request

```json
{
  "order_id": "INV-2026-0042",
  "amount_agorot": 34990,
  "currency": "ILS",
  "description": "Consulting package",
  "customer": {
    "name": "Dana Levi",
    "email": "dana@example.co.il",
    "phone": "+972501234567",
    "national_id": "123456789"
  },
  "installments": 3,
  "capture": true,
  "return_url": "https://example.co.il/pay/return",
  "notify_url": "https://example.co.il/pay/webhook",
  "tokenize": true,
  "metadata": {
    "invoice_id": "A-10042"
  }
}
```

## Canonical response

```json
{
  "gateway": "cardcom",
  "transaction_id": "lp-884422",
  "order_id": "INV-2026-0042",
  "status": "requires_action",
  "amount_agorot": 34990,
  "currency": "ILS",
  "approval_code": null,
  "redirect_url": "https://secure.cardcom.solutions/checkout/example",
  "failure_code": null,
  "failure_message": null,
  "token": null
}
```

## Gateway adapter mappings

### Cardcom

Validated provider paths:

| Purpose | Method | Provider path |
|---|---|---|
| Create hosted page | `POST` | `https://secure.cardcom.solutions/api/v11/LowProfile/Create` |
| Verify hosted result | `POST` | `https://secure.cardcom.solutions/api/v11/LowProfile/GetLpResult` |

| Canonical field | Cardcom field or concept |
|---|---|
| `order_id` | `ReturnValue` or configured merchant reference |
| `amount_agorot / 100` | `Amount`, up to two decimal places |
| `currency=ILS` | Terminal currency or `CoinID` according to contract |
| `installments` | Terminal installment field according to enabled feature |
| `return_url` | Success or error redirect URL |
| `notify_url` | `WebHookUrl` or configured callback |
| `tokenize` | Operation such as token creation when enabled |

Request example:

```json
{
  "TerminalNumber": "1000",
  "ApiName": "api-name",
  "Amount": "349.90",
  "ReturnValue": "INV-2026-0042",
  "ProductName": "Consulting package",
  "SuccessRedirectUrl": "https://example.co.il/pay/return",
  "WebHookUrl": "https://example.co.il/pay/webhook",
  "Operation": "ChargeAndCreateToken"
}
```

Response example:

```json
{
  "ResponseCode": 0,
  "Description": "OK",
  "LowProfileId": "6f02b9",
  "Url": "https://secure.cardcom.solutions/LP/6f02b9"
}
```

Common errors:

| Code pattern | Meaning | Action |
|---|---|---|
| nonzero `ResponseCode` | Validation, terminal, or provider failure | Preserve provider code; show safe customer message. |
| missing `Url` | Hosted page creation did not complete | Check terminal settings and redirect/callback URLs. |
| duplicate callback | Provider retried notification | Process idempotently by transaction id or merchant order id. |
| callback without status verification | Browser or webhook event is not authoritative | Query `GetLpResult` before marking paid. |

### Tranzila

Validated provider path:

| Purpose | Method | Provider path |
|---|---|---|
| Create payment request | `POST` | `https://api.tranzila.com/v1/pr/create` |

Authentication note: current docs describe a secure access-token. Do not send terminal secrets to the browser.

| Canonical field | Tranzila field or concept |
|---|---|
| `order_id` | `order_id` or merchant reference |
| `amount_agorot / 100` | Amount field according to terminal API |
| `currency=ILS` | Terminal currency value according to contract |
| `installments` | Installment fields when enabled |
| `return_url` | Hosted page return URL |
| `notify_url` | Notification URL |
| `payment_method_token` | Token field when enabled |

Request example:

```json
{
  "terminal_name": "merchant-terminal",
  "order_id": "INV-2026-0042",
  "amount": "349.90",
  "currency": "ILS",
  "contact": "Dana Levi",
  "email": "dana@example.co.il",
  "phone": "+972501234567",
  "notify_url": "https://example.co.il/pay/webhook"
}
```

Response example:

```json
{
  "Response": "000",
  "transaction_id": "tx-8811",
  "redirect_url": "https://direct.tranzila.com/example",
  "authnr": "123456"
}
```

Common errors:

| Code pattern | Meaning | Action |
|---|---|---|
| non-approval response | Decline or validation failure | Map to `declined` or `error` using provider code. |
| access-token failure | Authentication, replay, or request-signing issue | Regenerate token and verify clock skew. |
| missing transaction reference | Response cannot be reconciled | Query provider status before retry. |
| installment rejected | Terminal does not support requested split | Disable installments or update merchant contract. |

### Grow, formerly Meshulam

Current live documentation identifies Grow Payments as formerly Meshulam. Use `grow` as the primary adapter name and keep `meshulam` as a legacy alias only for merchants with existing Meshulam contracts.

| Canonical field | Grow field or concept |
|---|---|
| `order_id` | `transactionId` or merchant metadata |
| `amount_agorot / 100` | Amount or sum field according to product API |
| `description` | Description or payment-link text |
| `customer` | Customer details sent according to plan and consent |
| `installments` | Payment count where enabled |
| `return_url` | Customer redirect URL |
| `notify_url` | Webhook URL enabled by Grow support |

Request example:

```json
{
  "transactionId": "INV-2026-0042",
  "amount": "349.90",
  "description": "Consulting package",
  "customer": {
    "name": "Dana Levi",
    "email": "dana@example.co.il",
    "phone": "+972501234567"
  },
  "successUrl": "https://example.co.il/pay/return",
  "webhookUrl": "https://example.co.il/pay/webhook"
}
```

Webhook payload example based on documented field names:

```json
{
  "transactionId": "INV-2026-0042",
  "status": "success",
  "statusCode": "1",
  "paymentLinkProcessId": "plp-7001"
}
```

Common errors:

| Code pattern | Meaning | Action |
|---|---|---|
| webhook not received | Webhooks not enabled or URL blocked | Ask support to enable webhooks and test HTTPS reachability. |
| missing `transactionId` | Merchant reference was not echoed | Use provider process id and reconcile manually. |
| `statusCode` rejected | Provider-specific business failure | Preserve raw status and query dashboard. |
| legacy Meshulam mismatch | Old contract uses older field names | Keep a separate adapter profile and migration checklist. |

### Pelecard

Validated provider hosts and resources:

| Purpose | Provider location |
|---|---|
| Gateway 2.0 API | `https://gateway21.pelecard.biz/` |
| IFrame/Redirect | `https://gateway21.pelecard.biz/` |
| Sandbox service presets | `https://gateway21.pelecard.biz/services/SandboxServices` |

| Canonical field | Pelecard field or concept |
|---|---|
| `order_id` | Merchant order or custom parameter field |
| `amount_agorot` | Amount in the unit required by the selected endpoint |
| `currency=ILS` | Terminal currency setting |
| `installments` | Installment field when enabled |
| `return_url` | Hosted page success/error URL |
| `notify_url` | Callback URL where supported |
| `payment_method_token` | Token returned by tokenization flow |

Request example:

```json
{
  "terminalNumber": "YOUR TERMINAL NUMBER",
  "user": "YOUR USERNAME",
  "password": "YOUR PASSWORD",
  "orderId": "INV-2026-0042",
  "amountAgorot": 34990,
  "currency": "ILS",
  "returnUrl": "https://example.co.il/pay/return",
  "callbackUrl": "https://example.co.il/pay/webhook"
}
```

Response example:

```json
{
  "status": "approved",
  "transactionId": "pc-9911",
  "approvalCode": "123456",
  "redirectUrl": "https://gateway21.pelecard.biz/example"
}
```

Common errors:

| Code pattern | Meaning | Action |
|---|---|---|
| credential failure | Terminal, username, or password rejected | Rotate credentials and verify environment. |
| unsupported operation | Sandbox or terminal lacks selected service | Use listed sandbox presets and merchant contract. |
| amount unit mismatch | Agorot versus shekel string mismatch | Normalize internally and map per endpoint. |
| token conversion failed | Token flow not enabled or bad source transaction | Verify tokenization contract and source status. |

## Regulation and compliance notes

### VAT

The Israeli VAT rate was verified as 18% from 01/01/2025. Use this rate for 2026 examples unless the Tax Authority publishes a later change. Keep VAT as configuration, not as a constant embedded in business logic.

### Consumer price display

Display the total consumer price in ₪ before payment. Include mandatory charges and VAT in the displayed total. For refunds and cancellations, keep provider refund evidence and evaluate consumer-cancellation rules by transaction type.

### Privacy and data security

Treat personal data, national ID, phone, email, IP address, and order metadata as personal information when they identify a person. Store only what is required for the transaction, support, fraud prevention, accounting, and legal retention.

### PCI DSS

Do not store CVV, full track data, magnetic-stripe data, chip-equivalent data, or raw card numbers unless a qualified PCI assessment confirms scope and controls. Prefer hosted payment pages and tokenization.

### Payment-services regulation

A merchant integration usually consumes gateway services. Do not infer that the merchant becomes a licensed payment-services provider. Escalate to legal review when the product holds client balances, operates a wallet, initiates payments, performs marketplace split-payments, or settles funds for third parties.

## Canonical error table

| Canonical code | Category | Safe customer message | Operator action |
|---|---|---|---|
| `amount_invalid` | validation | The payment amount is invalid. | Fix agorot conversion and min/max rules. |
| `currency_unsupported` | validation | This currency is not supported. | Confirm terminal currency support. |
| `installments_unsupported` | validation | The selected number of payments is unavailable. | Restrict installment choices by terminal. |
| `authentication_failed` | integration | Payment service authentication failed. | Rotate keys and verify environment. |
| `duplicate_order` | idempotency | This payment was already submitted. | Query status and avoid duplicate charge. |
| `issuer_declined` | issuer | The card issuer declined the payment. | Let customer use another method. |
| `gateway_unavailable` | network | Payment service is temporarily unavailable. | Retry safely or route fallback before card authorization. |
| `unknown_provider_status` | reconciliation | Payment status is being checked. | Query provider and wait for reconciliation. |
| `signature_invalid` | webhook | Payment confirmation could not be verified. | Reject callback, alert support, and preserve raw data. |
| `refund_window_closed` | business | Refund cannot be completed automatically. | Handle manually with provider and accounting. |
