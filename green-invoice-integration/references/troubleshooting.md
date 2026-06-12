# Troubleshooting Guide

Use this guide to debug Green Invoice integrations without leaking secrets or creating duplicate financial records.

## First checks

1. Confirm the environment: production uses `https://api.greeninvoice.co.il/api/v1`; sandbox uses `https://sandbox.d.greeninvoice.co.il/api/v1`.
2. Confirm the token request body includes `grant_type: client_credentials`.
3. Confirm `Authorization: Bearer <token>` is sent on every authenticated request.
4. Confirm the account has the required dashboard feature: API keys, webhooks, digital payments, or payment links.
5. Confirm all date fields are ISO `YYYY-MM-DD`, while Hebrew-facing documents can display `DD-MM-YYYY`.
6. Confirm amounts are in shekels, not agorot, unless the current endpoint explicitly states otherwise.

## Authentication failures

### `401 Unauthorized`

Run a fresh token request and then call `GET /users/me`. If authentication works but another endpoint fails, inspect scope and plan access.

Common causes:

- Old token request body without `grant_type`.
- Token copied with hidden whitespace.
- `Bearer` prefix missing.
- Production token used against sandbox or sandbox token used against production.
- Secret regenerated after the integration was configured.

### `403 Forbidden`

Common causes:

- API access not included in the account plan.
- Webhooks or digital payments not enabled.
- API key lacks required permission.
- Endpoint belongs to partner or account-specific API coverage.

Action: open Developer Tools in the dashboard, confirm feature visibility, and regenerate the key only after checking stored integrations that rely on the old key.

## Document failures

### Wrong document type

Use this quick mapping:

- Payment received now: `320` for taxable Israeli sale.
- Payment not received: `300` for payment demand, or `305` when a tax invoice is specifically required.
- Payment confirmation only: `400`.
- Refund or cancellation: `330` or official cancel flow.

### VAT mismatch

Use `18%` for ordinary taxable domestic transactions in 2026. Decide whether each line item is net or gross before building the payload. Store the decision in logs without storing secrets.

### Missing allocation number

Check these conditions:

- Document is type `305` or `320`.
- Customer is a business customer.
- Net amount exceeds `₪5,000` from `01-06-2026` onward.
- Tax Authority authorization is active in the dashboard.
- Created document was fetched after issuance and inspected.

If the number is missing, pause delivery to the customer and resolve authorization or reissue workflow with an accountant.

## Customer-management failures

### Duplicate customers

Search by tax id, email, and normalized Hebrew/English name before creation. If duplicates already exist, choose one canonical customer id and store it in the external system.

### Wrong customer country

Set `country` explicitly. Use `IL` for Israeli customers. International documents can require different VAT and language behavior; do not infer zero-rate treatment from country alone.

## Payment-link failures

Payment links require digital-payment setup. The UI supports payment links, but API endpoint availability can differ by account. When a payment-link endpoint returns `403` or `404`, check payment service connection and current developer documentation before retrying.

Safe fallback: issue a document with payment buttons enabled when the product supports it, or let a human create the payment link in the dashboard.

## Webhook failures

### Timeout or retry storm

The platform expects a quick response. Store the event id and payload, enqueue work, and return `2xx` before downloading PDFs or updating CRM records.

### Duplicate side effects

Deduplicate by event id when present, otherwise by document id and event topic. Make every side effect idempotent.

### Secret verification confusion

The dashboard allows setting a secret. Confirm the exact delivery format in the current webhook payload and headers. If the platform sends a raw shared secret, compare it with `hmac.compare_digest`. If it sends a signature, compute HMAC-SHA256 over the raw body.

## Logging rules

Log these fields:

- Environment.
- Request method and normalized path.
- Response status code.
- Document id, customer id, event id.
- Payload validation errors.

Never log these fields:

- API key secret.
- Bearer token.
- Full payment credentials.
- Full customer identity numbers unless required by secured audit logging.
- Webhook secret.

## Retry rules

Retry safe reads and idempotency-protected writes. Do not blindly retry document creation after a network error. First search or fetch by external reference to avoid duplicate invoices.

Recommended retry policy:

| Operation | Retry? | Notes |
|---|---|---|
| Token request | Yes | Retry transient `5xx` only |
| Customer search | Yes | Safe read-style operation |
| Customer create | Only with external idempotency guard | Search before retry |
| Document create | Only after duplicate check | Consequential financial action |
| Document fetch | Yes | Safe |
| Cancel or credit | Only after status check | Consequential financial action |
| Webhook processing | Yes internally | Deduplicate first |

## Escalation checklist

Prepare this information before contacting support or an accountant:

- Environment and base URL.
- Endpoint path and method.
- Sanitized request JSON.
- Full response status and sanitized response body.
- Document type and amount before VAT.
- Customer classification: consumer, business, nonprofit, foreign customer.
- Whether Tax Authority authorization is active.
- Timestamp in Asia/Jerusalem.
