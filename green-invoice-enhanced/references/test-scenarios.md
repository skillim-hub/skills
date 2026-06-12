# Sandbox Test Scenarios

Run these scenarios before production go-live and after any change to document payload generation, token handling, retry policy, webhook processing, or VAT logic. Keep sandbox data separate from production and mark all created objects with a recognizable test label or remarks value.

## Scenarios

### 1. Auth success

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create sandbox API key; set key id and secret.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Token response contains `token`; `GET /users/me` returns user profile.

**Common failure modes**

Wrong base URL, copied production key into sandbox, expired/revoked key.
### 2. Auth failure

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Use an intentionally incorrect secret in sandbox.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

`POST /account/token` returns 401 or equivalent auth error.

**Common failure modes**

Secret still valid due using wrong env var; shell expanded JSON incorrectly.
### 3. Client create B2B

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create client with name, email, Israeli tax id, country IL.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Response contains client id and active true.

**Common failure modes**

Invalid tax id, duplicate client policy, invalid email.
### 4. Client update payment terms

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create client, then update `paymentTerms` to 30.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Subsequent get returns paymentTerms 30.

**Common failure modes**

PUT payload omitted required retained fields.
### 5. Item create and search

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create catalog item with catalogNum and price.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Search by description returns item.

**Common failure modes**

Inactive item filtered out, currency missing.
### 6. Price quote

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create document type 10 with client and income line.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Document has type 10, number, download links.

**Common failure modes**

Missing income line or client email.
### 7. Order linked to quote

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 100 with `linkedDocumentIds` containing quote id.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Order created and link retained.

**Common failure modes**

Quote id from production used in sandbox.
### 8. Delivery note

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 200 for goods shipment.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Delivery note issued with goods lines.

**Common failure modes**

Using service-only payload that account rules reject.
### 9. Return note

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 210 linked to delivery note.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Return note issued and linked.

**Common failure modes**

Return quantity exceeds original quantity.
### 10. Transaction invoice

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 300 without payment rows.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Open payment demand created.

**Common failure modes**

Incorrectly expecting VAT invoice status.
### 11. Tax invoice

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 305 with taxable income and no payment.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Open tax invoice created; total includes VAT.

**Common failure modes**

Osek patur account or VAT mismatch.
### 12. Tax invoice high B2B allocation

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Use type 305 above active threshold with Israeli B2B tax id after authorization.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Response includes allocation number field used by the account.

**Common failure modes**

Authorization expired; sandbox does not mirror allocation.
### 13. Tax invoice-receipt

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 320 with income and bank-transfer payment.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Closed paid document created.

**Common failure modes**

Payment total differs from document total.
### 14. Credit note full

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 330 linked to original tax document with `linkType: cancel`.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Credit note created and original marked canceled/linked.

**Common failure modes**

Original id wrong or already canceled.
### 15. Receipt against invoice

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 400 with payment and link to open invoice.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Receipt created and invoice closed.

**Common failure modes**

Payment amount short; withholding row missing.
### 16. Donation receipt

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 405 in eligible nonprofit account.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Donation receipt issued.

**Common failure modes**

Business type not eligible for donation receipt.
### 17. Purchase order

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 500 for supplier purchase.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Purchase order issued.

**Common failure modes**

Supplier modeled as customer without required fields.
### 18. Deposit receipt

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 600 with payment row.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Deposit receipt created and deposit liability tracked.

**Common failure modes**

Revenue recognized too early.
### 19. Deposit withdrawal

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create type 610 linked to deposit receipt.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Deposit balance reduced/applied.

**Common failure modes**

Deposit id missing or already consumed.
### 20. Foreign currency export

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create USD type 320 with `vatType: 1` and line `vatType: 2`.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Total in USD; VAT zero; English document link exists.

**Common failure modes**

Currency rate missing where accounting requires fixed rate.
### 21. Withholding tax split

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create receipt with bank transfer row and type 0 withholding row.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Payment rows sum to invoice total.

**Common failure modes**

Recording only net bank transfer leaves invoice partially open.
### 22. Discount rounding

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create multi-line invoice with percentage discount and `rounding: true`.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

API response totals become source of truth.

**Common failure modes**

Downstream recalculates different agorot.
### 23. Pagination

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create or mock more than pageSize documents and search page 0 then 1.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

No duplicate ids; loop stops when final page shorter than pageSize.

**Common failure modes**

One-based page index assumption.
### 24. Webhook signature valid

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Register webhook secret; replay raw body and header into verifier.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Verifier returns true.

**Common failure modes**

Verifier used parsed JSON instead of raw bytes.
### 25. Webhook signature invalid

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Change one byte in body and verify with same signature.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Verifier returns false.

**Common failure modes**

Signature comparison not constant-time.
### 26. Rate limit retry

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Mock 429 with `Retry-After: 1` followed by success.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Client waits/retries and returns success.

**Common failure modes**

Retry loop retries non-idempotent creates without reconciliation.
### 27. 5xx search retry

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Mock 502 then success for documents search.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Client retries with backoff.

**Common failure modes**

Max retry too low or no jitter.
### 28. Environment isolation

**Setup steps**

1. Use sandbox credentials unless the scenario explicitly requires production behavior.
2. Create sandbox document then try production get with same id.
3. Record request body, response body, status code, and document/client/item id when created.

**Expected output**

Production returns 404/not found.

**Common failure modes**

Shared database stores ids without env prefix.


## Recommended test data

```json
{
  "b2bClient": {
    "name": "Sandbox Example Ltd",
    "emails": ["sandbox-billing@example.co.il"],
    "taxId": "515555555",
    "country": "IL"
  },
  "b2cClient": {
    "name": "Sandbox Private Customer",
    "emails": ["sandbox-customer@example.co.il"],
    "country": "IL"
  },
  "foreignClient": {
    "name": "Sandbox Global Inc",
    "emails": ["sandbox-global@example.com"],
    "taxId": "US-12-3456789",
    "country": "US"
  },
  "incomeLine": {
    "description": "Sandbox consulting service",
    "quantity": 1,
    "price": 1000,
    "currency": "ILS",
    "vatRate": 0.18,
    "vatType": 0
  }
}
```

## Pass criteria

- Every document type that the integration can issue has at least one successful sandbox test.
- Validation failures are intentional and asserted in tests.
- Rate-limit and 5xx retries are covered by automated tests.
- Webhook signature validation uses raw bytes.
- Production credentials are never used in sandbox test code.
- Accountant-approved examples exist for B2B VAT, withholding tax, foreign currency, credit note, and deposit handling.
