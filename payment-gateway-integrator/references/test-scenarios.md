# Test Scenarios

Run these scenarios before production and after every gateway adapter change. Use sandbox credentials and synthetic customer data only.

## Core scenarios

| # | Scenario | Setup | Expected result |
|---:|---|---|---|
| 1 | Basic approved charge | `amount_agorot=1000`, `installments=1` | Status `approved`, transaction id stored. |
| 2 | Hosted checkout requires action | Gateway returns redirect URL | Status `requires_action`, redirect URL present. |
| 3 | Issuer decline | Provider returns decline code | Status `declined`, no automatic fallback. |
| 4 | Network timeout before transaction id | First gateway raises timeout | Next eligible gateway attempted. |
| 5 | Timeout after transaction id | Adapter receives id then unknown state | Status inquiry required, no fallback. |
| 6 | Duplicate order submit | Same order and amount sent twice | Same cached response returned. |
| 7 | Different amount same order | Same order id, changed amount | New idempotency key or policy rejection. |
| 8 | Unsupported currency | Request `USD` on `ILS` terminal | Validation error. |
| 9 | Installment count too high | `installments=36`, max 12 | Validation error before gateway call. |
| 10 | Installments supported | `installments=3`, max 12 | Gateway receives installment field. |
| 11 | Tokenization requested | `tokenize=true` | Adapter sends tokenization flag and stores token if returned. |
| 12 | Token charge | `payment_method_token` present | Charge uses token flow. |
| 13 | Authorization-only | `capture=false` and gateway supports auth | Status approved/pending with auth transaction id. |
| 14 | Capture authorization | Capture known auth id | Capture id stored and ledger updated. |
| 15 | Full refund | Refund captured amount | Refund status `approved/refunded`. |
| 16 | Partial refund | Refund smaller amount | Cumulative refund updated. |
| 17 | Refund above captured amount | Refund exceeds available balance | Validation error. |
| 18 | Webhook valid signature | Correct HMAC header | Event accepted. |
| 19 | Webhook invalid signature | Wrong HMAC header | Event rejected. |
| 20 | Webhook replay | Same event id repeated | Second event ignored. |
| 21 | Callback before return page | Webhook arrives first | Order paid; return page reads local state. |
| 22 | Return page before callback | Customer returns first | Page shows checking state; status inquiry runs. |
| 23 | Provider report local-only mismatch | Local paid record absent in settlement | Exception created. |
| 24 | Provider-only settlement | Settlement row absent locally | Incident created and investigated. |
| 25 | Duplicate provider reference | Same order appears twice | Alert and duplicate review. |
| 26 | Gateway disabled | Config `enabled=false` | Gateway excluded from routing. |
| 27 | Capability missing | Request requires tokenization but gateway lacks it | Gateway excluded. |
| 28 | Credential error | Provider returns auth error | Status `error`, alert operations. |
| 29 | Hebrew customer fields | Hebrew name/description | UTF-8 preserved. |
| 30 | Agorot rounding | `Decimal("10.015")` conversion | Validation rejects more than two decimals. |

## Gateway-specific coverage

### Cardcom

1. Low-profile page created.
2. Low-profile callback approved.
3. Duplicate `ReturnValue` handled by inquiry.
4. Token returned and stored.
5. Refund rejected due to state.

### Tranzila

1. `Response=000` maps to approved.
2. Non-`000` issuer decline maps to declined.
3. Installment fields sent correctly.
4. Token charge with existing token.
5. Terminal name mismatch maps to configuration error.

### Meshulam

1. Page URL returned.
2. `status=1` maps to pending/requires action when URL exists.
3. `status=0` maps to error/decline based on provider message.
4. Callback signature mismatch rejected.
5. Refund denied when transaction not settled.

### Pelecard

1. `StatusCode=000` maps to approved or requires action.
2. `PelecardTransactionId` persisted.
3. Authorization-only request keeps capture pending.
4. Capture after expiry fails safely.
5. Refund through wrong gateway rejected locally.

### Grow

1. Checkout URL returned.
2. `success=true` and `status=pending` maps to requires action.
3. `success=false` maps to error with provider message.
4. Long pending checkout expires locally.
5. Webhook confirms final status.

## Non-functional tests

| Area | Test |
|---|---|
| Security | Logs never include API key, secret, CVV, or full card number. |
| Privacy | Support export contains only required fields. |
| Observability | Metrics include gateway, status, and error category. |
| Reliability | Provider timeout does not block request thread indefinitely. |
| Localization | Dates display as `DD/MM/YYYY`; amounts display as `₪`. |
| Accessibility | Hosted checkout error messages are readable in Hebrew and English. |
| Accounting | Refunds link to original charge and invoice reference. |
| Disaster recovery | Gateway credentials can be rotated without code change. |


## Web-validated source scenarios

| # | Scenario | Input | Expected result |
|---:|---|---|---|
| 41 | VAT configuration | Date `02/06/2026`, amount `₪118.00` including VAT | VAT rate defaults to 18% but remains configurable. |
| 42 | Grow legacy alias | Gateway name `meshulam` | Normalizes to supported legacy alias and recommends `grow` for new contracts. |
| 43 | Unknown webhook name | Payload has provider-specific fields only | Stores raw payload and maps by verified status fields, not event name. |
| 44 | Cardcom callback | Callback received before status inquiry | Keeps order pending until `GetLpResult` or provider status confirms. |
| 45 | Pelecard sandbox preset | Refund scenario in sandbox | Uses sandbox-supported refund/status preset before production. |
