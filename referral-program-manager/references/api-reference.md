# API and Regulation Reference

## Scope

Use this reference to connect a referral reward ledger to Israeli payment gateways and operational compliance checkpoints. Provider APIs change by merchant contract, terminal permission, endpoint version, and enabled modules. Treat endpoint paths below as adapter examples and confirm the current production endpoint, authentication method, and signing rule in the provider dashboard or official documentation before launch.


## Live verification snapshot

Access date: 2026-06-03

| Topic | Verified public source | Operational implication |
|---|---|---|
| Israeli VAT rate | Israel Tax Authority public terminology/history pages cite 18% from 01/01/2025. | Use 18% as the current standard rate in examples, but keep accountant approval for actual VAT treatment. |
| PayPlus refund endpoint | Public docs list `https://restapi.payplus.co.il/api/v1.0/Transactions/Refund`. | Do not treat `/internal/referral-rewards/refunds` as a PayPlus endpoint. |
| PayPlus refund by transaction UID | Public docs list `https://restapi.payplus.co.il/api/v1.0/Transactions/RefundByTransactionUID`, `transaction_uid`, `amount`, `api-key`, and `secret-key`. | Store original transaction UID and secret material separately. |
| PayPlus callback | Public docs state callbacks can send details successfully charged or refunded. | Reconcile callback payloads with reward ID and transaction UID. |
| Cardcom token refund | Public docs state POST, URL-encoded values, and Name-to-Value response format. | Implement Cardcom as a dedicated adapter, not as generic JSON-only REST. |
| Tranzila authentication | Public docs mention secure access-token and HMAC-SHA256 four-header authentication for V2 APIs. | Validate the enabled version and required headers per terminal. |
| Grow Payments | Public docs identify Grow Payments as formerly Meshulam and require support enablement for webhooks. | Use `grow` as the preferred adapter name; keep `meshulam` as a legacy alias only. |
| YabandPay / YaadPay | Public docs expose API reference, portal manual, and refund sections. | Treat refund/API support as account-specific and keep portal/manual fallback. |
| Privacy Amendment 13 | Public Gov.il pages describe registration and notification duties for certain databases. | Review database duties when referral data grows or includes sensitive payout information. |
| Communications Law §30A | Public Gov.il/Knesset pages describe advertising-message obligations and consent. | Store consent and opt-out evidence before referral marketing messages. |

### Verified PayPlus refund by transaction UID

```http
POST https://restapi.payplus.co.il/api/v1.0/Transactions/RefundByTransactionUID
api-key: $PAYPLUS_API_KEY
secret-key: $PAYPLUS_SECRET_KEY
Content-Type: application/json

{
  "transaction_uid": "TX_UID_FROM_ORIGINAL_J5",
  "amount": 50,
  "initial_invoice": false
}
```

### Verified PayPlus callback URL pattern

```http
GET https://restapi.payplus.co.il/api/v1.0/YOURDOMAIN/YOURENDPOINT
```

The PayPlus public page describes this as a callback URL configured in the account that sends transaction details that were successfully charged or refunded.

### Verified Cardcom Name-to-Value token refund pattern

Cardcom's public Name-to-Value guide states that the request is POST, values are URL encoded, and the response is in Name-to-Value format such as `ResponseCode=4&Description=NoPemition&LowProfileCode=601`.

### Verified Grow Payments webhook limitation

Grow's public webhook guide lists webhook categories and says to contact support to enable webhooks. Do not hard-code unverified event-name constants for Grow unless the merchant account documentation or support response confirms them.

### Verified YabandPay / YaadPay limitation

YabandPay public documentation exposes an API reference and merchant-portal refunds area. Confirm actual refund and callback capability for the merchant's account before production use.

## Israeli providers and public documentation references

| Provider or body | Typical relevance | Public reference |
|---|---|---|
| Cardcom | Clearing, refunds, token operations, invoice modules | https://www.cardcom.solutions/ |
| Tranzila | Hosted payment pages, clearing, tokens, refunds | https://www.tranzila.com/ |
| Grow Payments (formerly Meshulam) | Payment pages, card and Bit-style checkout flows depending on contract | https://grow-il.readme.io/ |
| PayPlus | Ecommerce payments, invoice integrations, refunds, tokens | https://www.payplus.co.il/ |
| YabandPay / YaadPay | Hosted payment, portal, API reference, and manual refund workflows | https://yabandpay.com/documentation/ |
| SHVA | Israeli payment-card infrastructure and EMV context | https://www.shva.co.il/ |
| Bank of Israel | Payment systems and banking supervision context | https://www.boi.org.il/ |
| Israel Tax Authority | VAT, income tax, withholding, bookkeeping rules | https://www.gov.il/he/departments/israel_tax_authority |
| Privacy Protection Authority | Privacy Protection Law and database/security guidance | https://www.gov.il/he/departments/the_privacy_protection_authority |
| Consumer Protection and Fair Trade Authority | Consumer Protection Law and promotional practices | https://www.gov.il/he/departments/consumer_protection_and_fair_trade_authority |
| Ministry of Communications | Communications Law and spam rules context | https://www.gov.il/he/departments/ministry_of_communications |

## Internal adapter contract

### Reward payout request

```json
{
  "reward_id": "rwd_20260331_0001",
  "program_id": "salon-50-2026",
  "recipient_customer_id": "cust_1001",
  "amount_ils": 50.0,
  "currency": "ILS",
  "method": "credit",
  "gateway": "payplus",
  "original_transaction_id": "TX-7788",
  "idempotency_key": "reward-rwd_20260331_0001",
  "reason": "referral_reward",
  "metadata": {
    "invoice_number": "INV-2026-0042",
    "qualifying_action": "paid_completed_appointment"
  }
}
```

### Reward payout response

```json
{
  "reward_id": "rwd_20260331_0001",
  "status": "submitted",
  "gateway": "payplus",
  "gateway_reference": "RF-998877",
  "idempotency_key": "reward-rwd_20260331_0001",
  "created_at": "2026-03-31T10:00:00+03:00",
  "raw_status": "approved"
}
```

### Error response

```json
{
  "status": "failed",
  "gateway": "cardcom",
  "error_code": "REFUND_NOT_ALLOWED",
  "message": "Refund permission is not enabled for this terminal.",
  "retryable": false,
  "operator_action": "Enable refund permission or export manual credit workflow."
}
```

## Authentication patterns

| Pattern | Usage | Control |
|---|---|---|
| API key header | Common for modern REST APIs | Store in secret manager; rotate quarterly. |
| Terminal ID + password | Common for clearing terminals | Restrict dashboard access; never commit credentials. |
| HMAC signature | Common for webhooks | Validate body bytes, timestamp, and replay window. |
| IP allowlist | Sometimes required for backoffice APIs | Use static outbound IP; document exceptions. |
| Merchant portal export | Common fallback | Export CSV and reconcile manually. |

## Gateway request examples

### Internal generic refund request, not a provider endpoint

```http
POST /internal/referral-rewards/refunds
Authorization: Bearer ${INTERNAL_SERVICE_TOKEN}
Idempotency-Key: reward-rwd_20260331_0001
Content-Type: application/json

{
  "transaction_id": "TX-7788",
  "amount": 50.00,
  "currency": "ILS",
  "reason": "referral_reward",
  "metadata": {
    "reward_id": "rwd_20260331_0001",
    "program_id": "salon-50-2026"
  }
}
```

Expected response:

```json
{
  "refund_id": "RF-998877",
  "transaction_id": "TX-7788",
  "amount": 50.00,
  "currency": "ILS",
  "status": "approved"
}
```

### Generic credit creation

```http
POST /api/v1/credits
Authorization: Bearer ${INTERNAL_SERVICE_TOKEN}
Content-Type: application/json

{
  "customer_reference": "cust_1001",
  "amount": 50.00,
  "currency": "ILS",
  "expires_at": "2026-09-27",
  "source": "referral_program",
  "metadata": {
    "reward_id": "rwd_20260331_0001"
  }
}
```

Expected response:

```json
{
  "credit_id": "CR-5512",
  "customer_reference": "cust_1001",
  "status": "active",
  "balance": 50.00
}
```

### Generic webhook

```http
POST /webhooks/payments
X-Gateway-Signature: sha256=...
X-Gateway-Timestamp: 1774940400
Content-Type: application/json

{
  "event_type": "payment.refunded",
  "transaction_id": "TX-7788",
  "refund_id": "RF-998877",
  "amount": 50.00,
  "currency": "ILS",
  "status": "approved",
  "metadata": {
    "reward_id": "rwd_20260331_0001"
  }
}
```

Expected internal event:

```json
{
  "type": "reward_gateway_update",
  "reward_id": "rwd_20260331_0001",
  "gateway_reference": "RF-998877",
  "status": "paid",
  "raw_gateway_status": "approved"
}
```

## Provider adapter notes

### Cardcom

| Internal field | Cardcom-style concept |
|---|---|
| `terminal_number` | merchant terminal or low-profile terminal |
| `transaction_id` | original deal/transaction identifier |
| `amount_ils` | refund or credit amount |
| `document_number` | invoice or receipt module identifier when enabled |
| `response_code` | gateway/acquirer result code |

Confirm refund API availability, invoice module behavior, partial refund rules, callback format, and transaction/invoice identifier separation.

### Tranzila

| Internal field | Tranzila-style concept |
|---|---|
| `supplier` | terminal/supplier identifier |
| `transaction_id` | indexed transaction identifier |
| `token` | payment token where tokenization is enabled |
| `sum` | amount in ILS |
| `Response` | clearing result code |

Validate signatures, normalize Hebrew encoding, and treat refund permission as a terminal-level setting.

### Grow Payments (formerly Meshulam)

| Internal field | Grow-style concept |
|---|---|
| `payment_id` | provider payment identifier |
| `page_code` | hosted page code |
| `transaction_id` | clearing transaction reference |
| `status` | payment/refund state |
| `api_key` | merchant credential |

Confirm product-tier operations, Bit-related settlement fields, callback signing, and personal-data minimization.

### PayPlus

| Internal field | PayPlus-style concept |
|---|---|
| `api_key` | API credential |
| `secret_key` | signing or authentication secret |
| `transaction_uid` | transaction identifier |
| `invoice_uid` | invoice module identifier |
| `refund_uid` | refund identifier |

Confirm API version, webhook secret, invoice module behavior, and idempotency options.

### YabandPay / YaadPay

| Internal field | Yaad-style concept |
|---|---|
| `Masof` | terminal number |
| `PassP` | terminal password or credential |
| `Id` | transaction identifier |
| `Amount` | amount |
| `CCode` | response code |

Normalize Windows-1255/UTF-8 issues, confirm callback verification, and use merchant-portal export when API refunds are unavailable.

## Error table

| Error code | Meaning | Retryable | Operator action |
|---|---|---:|---|
| `AUTH_FAILED` | API key, terminal password, or signature invalid | No | Rotate credentials and update secret store. |
| `REFUND_NOT_ALLOWED` | Terminal lacks refund permission | No | Enable refund or switch to credit/coupon flow. |
| `TRANSACTION_NOT_FOUND` | Original payment reference wrong or unsettled | Sometimes | Verify transaction ID and settlement state. |
| `AMOUNT_EXCEEDS_ORIGINAL` | Refund amount greater than allowed balance | No | Reduce amount or use store credit. |
| `DUPLICATE_IDEMPOTENCY_KEY` | Request already processed | No | Fetch existing result and attach to reward. |
| `CURRENCY_UNSUPPORTED` | Non-ILS or unsupported currency sent | No | Normalize to ILS or supported currency. |
| `VALIDATION_ERROR` | Provider field missing | No | Fix adapter mapping. |
| `RATE_LIMITED` | Provider throttled requests | Yes | Retry with exponential backoff and jitter. |
| `TEMPORARY_GATEWAY_ERROR` | Provider outage or timeout | Yes | Retry with same idempotency key. |
| `WEBHOOK_SIGNATURE_INVALID` | Incoming event cannot be trusted | No | Reject event and investigate secret mismatch. |
| `PAYOUT_DOCUMENT_MISSING` | Cash payout lacks tax document or identity data | No | Request missing documents. |
| `CHARGEBACK_OPEN` | Original qualifying payment disputed | No | Freeze or reverse reward. |

## Webhook validation checklist

1. Read the raw request body before parsing JSON.
2. Validate HMAC or provider-specific signature.
3. Reject timestamps outside a replay window, such as 5 minutes.
4. Check provider account or terminal ID.
5. Confirm referenced transaction belongs to the merchant.
6. Enforce idempotency on provider event ID.
7. Map external status to internal status.
8. Store only necessary fields; avoid card data.
9. Emit an audit entry.

## Regulation reference

### VAT Law and bookkeeping

Ask whether the reward is a discount, price reduction, credit balance, marketing expense, or consideration for a service. Store `tax_treatment`, accounting document number, reward ID, and month-end reconciliation entry.

### Income Tax Ordinance and withholding tax

Identify recipient type: private individual, licensed dealer, company, nonprofit, employee, or supplier. Require identity fields, vendor status, invoice/receipt, withholding confirmation when applicable, and payment proof before cash payout.

### Consumer Protection Law

Make terms clear and accessible before participation. Publish eligibility, exclusions, expiry, reversal, support contact, and terms version. Attach terms version to every event.

### Privacy Protection Law

Keep a data inventory, collect only necessary data, restrict access to payout/fraud details, log exports, apply retention, and separate marketing consent from service-contact permission.

### Communications Law §30A

Store consent timestamp, source, text version, and channel. Suppress opt-outs across SMS, email, WhatsApp, and phone. Include opt-out instructions in every promotional message.

## Reconciliation reference

| Field | Source |
|---|---|
| `reward_id` | referral ledger |
| `gateway_reference` | provider response |
| `amount_ils` | ledger and provider report |
| `status` | provider report |
| `document_number` | accounting system |
| `settlement_date` | provider or bank report |
| `operator` | approval audit log |

Monthly checks: approved rewards equal accounting entries, paid rewards equal settlement/export, expired credits are recognized under accounting policy, reversals link to reason, and open liabilities are aged.
