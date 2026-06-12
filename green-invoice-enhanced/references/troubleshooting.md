# Troubleshooting Green Invoice API Integrations

This guide is organized by symptom, diagnosis, and fix. Use it for production incidents, sandbox test failures, and accountant-reported document problems.

## Fast diagnostic checklist

1. Confirm environment: production and sandbox tokens, ids, and base URLs are not interchangeable.
2. Confirm the API token is present: `Authorization: Bearer <token>`.
3. Decode JWT expiry without logging the token value.
4. Check plan and feature access for API and Webhooks.
5. Verify active business id and user role.
6. Reproduce with a minimal curl request.
7. For document failures, validate client, document type, VAT type, payment rows, and totals.
8. For B2B high-value tax invoices, verify Tax Authority authorization and allocation number presence.
9. For webhook failures, verify signature with raw body bytes.
10. Persist the response body, request id headers, timestamp, and sanitized payload for support escalation.

## Minimal auth diagnostic

```bash
export GREEN_INVOICE_BASE_URL="https://api.greeninvoice.co.il/api/v1"
export GREEN_INVOICE_KEY_ID="replace-with-key-id"
export GREEN_INVOICE_KEY_SECRET="replace-with-key-secret"

TOKEN="$(
  curl -s -X POST "$GREEN_INVOICE_BASE_URL/account/token" \
    -H "Content-Type: application/json" \
    --data-binary "{\"id\":\"$GREEN_INVOICE_KEY_ID\",\"secret\":\"$GREEN_INVOICE_KEY_SECRET\"}" |
  python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("accessToken") or d.get("token") or "")'
)"

curl -s "$GREEN_INVOICE_BASE_URL/users/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" |
  python3 -m json.tool
```

## Symptom tables

### Authentication and authorization

| Symptom | Diagnosis | Fix | Diagnostic curl |
|---|---|---|---|
| Token endpoint returns `400` | JSON malformed or credentials fields named incorrectly | Send `id`, `secret`, and `grant_type` exactly | `curl -v -X POST "$BASE/account/token" -H "Content-Type: application/json" -d '{"id":"x","secret":"y","grant_type":"client_credentials"}'` |
| Token endpoint returns `401` | Key id/secret invalid, revoked, or copied from another environment | Regenerate key and verify environment | `curl -v -X POST "$BASE/account/token" -d @auth.json` |
| `users/me` returns `401` | Bearer token missing, expired, or malformed | Refresh token and retry once | `curl -v "$BASE/users/me" -H "Authorization: Bearer $TOKEN"` |
| Most endpoints return `403` | API access not enabled for plan or user lacks role | Confirm plan, active business, and role | `curl -v "$BASE/businesses" -H "Authorization: Bearer $TOKEN"` |
| Webhooks return `403` | Webhooks gated separately | Disable webhook setup for this account or enable the feature | `curl -v "$BASE/webhooks" -H "Authorization: Bearer $TOKEN"` |

### Documents

| Symptom | Diagnosis | Fix | Diagnostic curl |
|---|---|---|---|
| `422` with client field | Missing client name/email/tax id or invalid email | Supply `client.id` or a complete client object | `curl -s -X POST "$BASE/documents" -H "Authorization: Bearer $TOKEN" -d @document.json` |
| `422` with VAT field | Invalid `vatType`, row VAT mismatch, or business type conflict | Align document and row VAT values | `jq '.vatType,.income[].vatType,.income[].vatRate' document.json` |
| `422` with payment total | Payment rows do not match receipt total | Recalculate payment rows and withholding split | `jq '.payment' document.json` |
| `409` on close | Document already closed or cancelled | Re-read the document and reconcile status | `curl -s "$BASE/documents/$DOC_ID" -H "Authorization: Bearer $TOKEN"` |
| Missing download link | File generation delayed or `attachment` not requested | Re-read document and call download links endpoint | `curl -s "$BASE/documents/$DOC_ID/download/links" -H "Authorization: Bearer $TOKEN"` |
| Email not sent | Missing recipient email or feature restriction | Provide `to`, validate email, and inspect response | `curl -s -X POST "$BASE/documents/$DOC_ID/email" -d @email.json` |

### SHAAM allocation number

| Symptom | Diagnosis | Fix |
|---|---|---|
| B2B tax invoice over threshold lacks allocation number | Tax Authority authorization absent, expired, or wrong buyer classification | Renew authorization in dashboard, verify client `taxId`, and re-check document response. |
| Accountant says buyer cannot deduct VAT | Allocation missing from issued document or invoice type not accepted | Inspect `GET /documents/{id}`; issue correction only after accountant review. |
| Allocation worked last month but stopped | Authorization validity window expired | Renew authorization and add monitoring around high-value invoices. |
| Sandbox cannot reproduce allocation behavior | Sandbox may not mirror live Tax Authority flow | Test payload logic in sandbox and run final allocation verification on a controlled production invoice. |

### Rate limits and transient failures

| Symptom | Diagnosis | Fix |
|---|---|---|
| `429 Too Many Requests` | Burst above account or endpoint limit | Respect `Retry-After`; apply exponential backoff with jitter. |
| Random `500` on search | Temporary service issue | Retry idempotent reads/searches. |
| Timeout after document create | Unknown creation result | Search by client/date/amount/source reference before retrying create. |
| Duplicate documents | Create operation retried without idempotency check | Use source order id in `remarks` or external mapping and search before replay. |

## Common Hebrew error strings

| Hebrew string or fragment | Meaning | Likely source field | Fix |
|---|---|---|---|
| `אין הרשאה` | No permission | token, business, plan | Check role, active business, plan gate. |
| `פג תוקף` | Expired | JWT or Tax Authority grant | Refresh token or renew authorization. |
| `מספר עוסק לא תקין` | Invalid business/tax id | `client.taxId` | Validate Israeli tax id or foreign id format. |
| `לקוח חובה` | Client required | `client` | Provide existing client id or complete new client object. |
| `מייל לא תקין` | Invalid email | `client.emails`, email endpoint `to` | Normalize and validate email addresses. |
| `סכום לא תקין` | Invalid amount | `income.price`, `payment.price`, `discount` | Check totals, signs, rounding, and currency. |
| `סוג מסמך לא נתמך` | Unsupported document type | `type` | Choose a document type allowed for the business type. |
| `לא ניתן לסגור מסמך` | Cannot close document | close endpoint | Re-read status and linked payments. |
| `מספר הקצאה` | Allocation number issue | tax invoice response | Renew authorization and verify B2B threshold. |
| `ניכוי במקור` | Withholding tax issue | payment row type 0 | Split actual payment and withheld tax correctly. |

## Diagnostic curl snippets

### Search for a document after timeout

```bash
curl -s -X POST "$GREEN_INVOICE_BASE_URL/documents/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary '{
    "page": 0,
    "pageSize": 25,
    "fromDate": "2026-05-31",
    "toDate": "2026-05-31",
    "clientName": "Example Ltd",
    "type": [320]
  }' | python3 -m json.tool
```

### Validate a high-value B2B invoice after issuance

```bash
curl -s "$GREEN_INVOICE_BASE_URL/documents/doc_1002" \
  -H "Authorization: Bearer $TOKEN" |
  python3 - <<'PY'
import json, sys
doc = json.load(sys.stdin)
print("id:", doc.get("id"))
print("number:", doc.get("number"))
print("type:", doc.get("type"))
print("total:", doc.get("total"))
print("taxAuthorityAllocationNumber:", doc.get("taxAuthorityAllocationNumber"))
PY
```

### Retry a rate-limited request manually

```bash
response_headers="$(mktemp)"
curl -s -D "$response_headers" -o response.json \
  -X POST "$GREEN_INVOICE_BASE_URL/documents/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary '{"page":0,"pageSize":25}'

cat "$response_headers"
cat response.json | python3 -m json.tool
```

### Verify webhook signature in Python

```python
from pathlib import Path
from green_invoice_client import GreenInvoiceClient

raw_body = Path("webhook-body.json").read_bytes()
signature = "sha256=0d4d9d2e7c1e0a5f6e5c2b0d1a9c8b7a6f5e4d3c2b1a00998877665544332211"
secret = "shared-signing-secret"

print(GreenInvoiceClient.verify_webhook_signature(raw_body, signature, secret))
```

## Incident classification

| Severity | Example | Response |
|---|---|---|
| Low | Single validation error in sandbox | Fix payload and add test. |
| Medium | Production webhook delivery failing but documents issue correctly | Queue replays, verify signature, and reprocess missed events. |
| High | Production document creation failing for all users | Stop automated issuance, alert operators, and switch to manual fallback. |
| Critical | B2B high-value invoices issued without allocation number | Pause affected flow, identify documents, consult accounting owner, and issue corrections only after professional approval. |

## Data to capture for support

- Timestamp and timezone.
- Environment and base URL.
- Endpoint, method, sanitized request body.
- HTTP status, response headers, response body.
- Token issue time and expiry, without token value.
- Business id and user id if returned by `users/me`.
- Document id, official number, client id, and total when relevant.
- Whether the same request succeeds in sandbox or production.
