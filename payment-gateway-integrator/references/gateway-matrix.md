# Gateway Matrix

Use this matrix as an implementation planning aid. Provider capabilities depend on merchant plan, terminal, acquirer, enabled features, and current provider contract.

| Gateway | Strong fit | Validate before production | Common integration shape |
|---|---|---|---|
| Cardcom | Hosted Low Profile checkout, invoices, tokenization, recurring-style flows, Israeli SMBs | Terminal number, API name, Low Profile operation, callbacks, refunds, installments | Create hosted page, redirect customer, receive callback, query `GetLpResult`. |
| Tranzila | Hosted and terminal-centric integrations, iframe/direct payment request, established merchant terminals | Access-token flow, terminal fields, token support, installment fields, refunds, response codes | Create payment request, route customer or iframe, normalize response, process callback/report. |
| Grow, formerly Meshulam | Payment links, hosted checkout, small-business payment flows, webhook updates | API plan, support-enabled webhooks, documented payload fields, reports, legacy Meshulam contract differences | Create checkout or payment link, receive status updates, reconcile by transaction id and process id. |
| Pelecard | Gateway-style API, IFrame/Redirect, authorization/capture use cases, refunds, reports | Credentials, terminal features, sandbox preset, auth/capture, refunds, tokenization, status endpoint | Server-side request or hosted page, status by provider transaction id. |

## Capability flags used by the client

| Flag | Meaning |
|---|---|
| `hosted_checkout` | Gateway can create a customer-facing payment page. |
| `tokenization` | Gateway can return a reusable provider token. |
| `token_charge` | Gateway can charge an existing provider token. |
| `refund` | Gateway supports API refund. |
| `partial_refund` | Gateway supports refund below full captured amount. |
| `installments` | Gateway supports installment payments for the configured terminal. |
| `authorize` | Gateway supports authorization-only. |
| `capture` | Gateway supports capture after authorization. |
| `void` | Gateway supports void or reversal before settlement. |

## Recommendation by merchant type

| Merchant | Recommended starting pattern |
|---|---|
| Freelancer | Hosted checkout, single gateway, invoice issued after approval. |
| Small retail shop | Hosted checkout, installments only after terminal validation, daily reconciliation. |
| Subscription service | Hosted checkout with tokenization, customer consent record, retry policy. |
| Marketplace or multi-branch business | Orchestration layer, gateway routing by branch/capability, ledger per merchant account. |
| High-ticket service provider | Authorization/capture or deposit workflow, strong customer communication, dispute evidence. |

## Validated terminology

| Term | Use |
|---|---|
| `Grow, formerly Meshulam` | Current public documentation and Bank of Israel participant context support this wording. |
| `אשראית EMV` | Use for the SHVA terminal-to-acquirer protocol context. |
| `מעמ 18%` | Use for 2026 examples, with configuration for future rate changes. |
