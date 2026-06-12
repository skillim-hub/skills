# Troubleshooting Guide

## Validation failures

| Message | Meaning | Fix |
|---|---|---|
| `business_tax_id must contain 9 digits` | Missing or malformed Israeli business identifier | Enter a 9-digit Osek/Company ID; preserve leading zeroes |
| `transaction_id is required` | Gateway event cannot identify the transaction | Export the full webhook/result payload from the provider |
| `amount must be positive` | Missing or invalid amount | Use the gross amount actually charged |
| `raw card number detected` | Payload contains PAN-like data that passes Luhn validation | Replace with `****1234` or last4 before generating output |
| `gateway success could not be confirmed` | Payload lacks a success code or recognized success field | Read the provider response and map the success code manually |

## Gateway-specific checks

### Cardcom

- Check top-level `ResponseCode` first.
- Inspect nested `DocumentInfo.ResponseCode` when document creation was requested.
- Save `LowProfileId` and call `LowProfile/GetLpResult` after redirects or webhooks.
- Do not treat `UrlToBit` or `UrlToPayPal` as payment success. They are payment options, not results.

### Tranzila

- Keep API app key and secret in server-side storage only.
- Verify `transaction/credit_card/create` or payment request result fields before output.
- For iframe flows, check handshake creation and final transaction response separately.
- Keep 3DS completion status separate from authorization and settlement.

### Grow/Meshulam

- Use `notifyUrl` for server-to-server confirmation.
- Verify `transactionUniqueIdentifier` behavior to avoid duplicate token charges.
- Treat payment-link creation as pending until the paid notification or status lookup confirms success.
- Use `invoiceNotifyUrl` only as a document notification, not a payment success signal.

### Pelecard

- Require `StatusCode` `000` and a successful Shva result before marking as paid.
- Distinguish pending transactions from debit transactions.
- Check `VoucherId` and `PelecardTransactionId` in reconciliation exports.
- Use the current Gateway21 collection or merchant support docs when endpoint behavior differs from legacy Gateway20 references.

## VAT and document issues

| Situation | Recommended handling |
|---|---|
| Osek Patur receipt | Show total paid and statement that no VAT was charged |
| Osek Murshe / company receipt | Split gross amount into net and 18% VAT unless the transaction is exempt/zero-rated |
| B2B tax invoice above threshold | Add Tax Authority allocation number before final tax invoice handoff |
| Rounding mismatch | Recalculate with Decimal from the gross paid amount and round to 0.01 |
| Refund or partial refund | Generate a negative/credit document through accounting software or provider document API |

## Security and privacy

- Redact PAN, CVV, track data, identity documents, and unnecessary personal notes before storage.
- Log the gateway transaction ID and source hash instead of full payloads when possible.
- Store generated customer PDFs or HTML in access-controlled storage.
- Avoid sending accounting documents over unsecured links.
- Rotate keys if gateway credentials appear in a receipt export or debug log.
