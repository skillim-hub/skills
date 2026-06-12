# Test Scenarios

Run these scenarios in sandbox before production. Use `DD-MM-YYYY` for human review dates and ISO `YYYY-MM-DD` in API payloads.

| # | Scenario | Input | Expected result |
|---:|---|---|---|
| 1 | Token with current body | Key id, secret, `grant_type: client_credentials` | Token returned and accepted by `GET /users/me` |
| 2 | Token with wrong secret | Valid key id, wrong secret | `401` or validation error without leaking secret in logs |
| 3 | Create Israeli business customer | Name, email, Israeli tax id, country `IL` | Customer id returned; repeat run finds same customer |
| 4 | Search Hebrew customer | Hebrew name with final letters and punctuation | Search returns likely match or clear empty result |
| 5 | Tax invoice-receipt under threshold | Type `320`, net `₪1,000`, VAT `18%`, paid by bank transfer on `05-06-2026` | Total `₪1,180`; document status created; PDF link available |
| 6 | B2B tax invoice above threshold | Type `305`, net `₪6,000`, business customer | Allocation-number check is performed after creation |
| 7 | Payment not yet received | Type `300`, due date in future, no payment item | Document created as payment demand without receipt |
| 8 | Receipt after payment | Type `400`, linked original document, payment amount | Payment recorded and reconciliation reference stored |
| 9 | Cancellation or refund | Original type `320`, refund amount `₪590` | Credit-note or official cancel flow records correction |
| 10 | Foreign customer | Country not `IL`, currency `USD`, language `en` | Document created only after VAT treatment is explicitly confirmed |
| 11 | Payment-link request | Digital payments connected, amount and customer email | Link returned or clear `403/404` fallback path triggered |
| 12 | Webhook duplicate | Send the same `document/created` payload twice | Only one downstream side effect occurs |
| 13 | Webhook timeout resilience | Handler enqueues work and returns quickly | Platform does not retry because `2xx` returns within six seconds |
| 14 | Wrong VAT regression | Force stale `17%` in calculation test | Test fails and reports expected `18%` |
| 15 | Hebrew PDF filing | `document/created` payload with Hebrew download link | File stored under correct year/month/type path |

## Manual smoke test

```bash
python scripts/green_invoice_integration_cli.py auth \
  --env sandbox \
  --key-id "$GREEN_INVOICE_KEY_ID" \
  --key-secret "$GREEN_INVOICE_KEY_SECRET"

python scripts/green_invoice_integration_cli.py whoami \
  --env sandbox \
  --token "$GREEN_INVOICE_TOKEN"
```

## Production cutover checklist

- Confirm sandbox scenarios 1, 3, 5, 6, and 12 pass.
- Confirm Tax Authority authorization status for accounts that issue B2B tax invoices above `₪5,000` before VAT.
- Confirm digital-payment setup before enabling payment-link automation.
- Replace sandbox credentials with production credentials in a secret manager.
- Run one low-value production document and verify dashboard, PDF, webhook, and downstream sync.
