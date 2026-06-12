# Workflow Guide

This guide shows concrete end-to-end flows for Israeli payment orchestration. Use the canonical client and adapt the payload mapping per gateway contract.

## Workflow 1: One-time hosted checkout for a freelancer

Use when a freelancer sends a payment link for a service invoice.

### Preconditions

- Merchant account active.
- Hosted checkout enabled.
- Return URL and webhook URL use HTTPS.
- Invoice issuance flow prepared after approval.

### Steps

1. Create internal invoice draft with amount, customer, and due date.
2. Create a canonical `PaymentRequest` with `capture=true`, `installments=1`, and `tokenize=false`.
3. Route to a gateway supporting hosted checkout.
4. Store `gateway`, `transaction_id`, `order_id`, and `redirect_url`.
5. Send payment link to customer.
6. Receive signed webhook.
7. Query status when webhook is missing or delayed.
8. Mark invoice paid only after approval.
9. Issue tax invoice/receipt according to accounting rules.
10. Send customer confirmation.

### Failure handling

- If page creation fails without transaction id, try another enabled gateway.
- If transaction id exists but status is unknown, query status before retry.
- If customer abandons page, expire the link after the configured time.

## Workflow 2: Small shop checkout with installments

### Preconditions

- Installments enabled in terminal contract.
- Customer-facing checkout displays total amount and installment count.
- Merchant understands settlement and fee impact.

### Steps

1. Let customer choose a valid installment count.
2. Validate count against route capabilities.
3. Reject count above `max_installments`.
4. Create hosted checkout request.
5. Display redirect and preserve cart lock.
6. Handle webhook.
7. Confirm order after approval.
8. Release inventory after reliable success state.
9. Reconcile daily against provider report.

| Condition | Action |
|---|---|
| `installments=1` | Route to any regular card-capable gateway. |
| `installments>1` and provider supports count | Continue. |
| `installments>max_installments` | Block checkout and show valid options. |
| Provider rejects installments | Disable option until terminal contract is corrected. |

## Workflow 3: Subscription or recurring charge

### Preconditions

- Tokenization enabled.
- Terms explicitly cover future charges and cancellation.
- Customer consent stored.
- Card token storage isolated and access-controlled.

### Steps

1. Use hosted checkout with `tokenize=true`.
2. Receive token in signed callback or status inquiry.
3. Store provider token, gateway, masked card details if provided, and consent reference.
4. Schedule renewal charge.
5. Before each charge, check subscription state and cancellation requests.
6. Charge token through the same gateway unless a migration process permits otherwise.
7. Send customer receipt/notification after approval.
8. Retry failed renewal according to a written dunning policy.

### Edge cases

- Token becomes invalid: ask customer to update payment method.
- Provider migration: collect new token unless token portability is contractually supported.
- Customer cancels: stop future charges immediately according to terms.

## Workflow 4: Authorization and later capture

Use for hotels, equipment rental, deposits, or services where final amount can change.

### Preconditions

- Authorization-only supported by gateway and acquirer.
- Capture window known.
- Business process can release unused authorization.

### Steps

1. Create authorization with `capture=false`.
2. Store authorization transaction id and expiry.
3. Provide service or reserve inventory.
4. Capture final amount before expiry.
5. Void/reverse unused amount when applicable.
6. Reconcile captured amount, not authorized amount.

### Risk controls

- Do not show authorization as final charge.
- Notify customer about authorization hold.
- Monitor expiring authorizations daily.

## Workflow 5: Refund flow

### Preconditions

- Original transaction captured.
- Refund API enabled.
- Refund amount is less than or equal to captured minus prior refunds.
- Accounting reversal process prepared.

### Steps

1. Locate original payment by `order_id`.
2. Calculate refundable amount.
3. Create `RefundRequest`.
4. Send refund through original gateway.
5. Store refund id and raw status.
6. Update ledger with refund amount.
7. Issue accounting document if required.
8. Notify customer with expected timing.

```json
{
  "transaction_id": "cc-884422",
  "amount_agorot": 10000,
  "reason": "Returned one item from order INV-2026-0042"
}
```

## Workflow 6: Webhook processing

### Requirements

- Process raw body, not parsed/re-serialized JSON, for signature verification.
- Verify signature before reading event details as trusted data.
- Use replay protection when timestamp or event id exists.
- Make processing idempotent by event id and transaction id.

### Steps

1. Receive callback at `/webhooks/{gateway}`.
2. Read raw body bytes.
3. Verify signature with gateway secret.
4. Parse event.
5. Normalize status.
6. Lock local payment row.
7. Apply state transition if valid.
8. Store raw redacted event.
9. Acknowledge success.
10. Queue reconciliation if status conflicts with local state.

| Current state | Incoming state | Action |
|---|---|---|
| `pending` | `approved` | Mark paid and trigger fulfillment. |
| `pending` | `declined` | Mark failed and release cart. |
| `approved` | `approved` | Ignore duplicate event. |
| `approved` | `refunded` | Add refund event, do not erase charge record. |
| `declined` | `approved` | Investigate; query status before changing. |
| any | unknown | Store event and query provider. |

## Workflow 7: Daily reconciliation

### Inputs

- Local payment ledger.
- Gateway settlement report.
- Refund report.
- Accounting system export.

### Steps

1. Normalize all reports to agorot.
2. Convert dates to `Asia/Jerusalem`.
3. Match by provider transaction id.
4. Fallback match by order id, amount, date, and approval code.
5. Flag local approved payments missing from settlement.
6. Flag provider transactions missing locally.
7. Flag amount mismatches and duplicate order ids.
8. Resolve flags before monthly close.
9. Export exceptions for finance review.

| Exception | Meaning | Resolution |
|---|---|---|
| `local_only` | Local order paid, provider report missing | Query gateway and inspect date boundary. |
| `provider_only` | Provider charged but local order absent | Search webhook failures and support tickets. |
| `amount_mismatch` | Amounts differ | Inspect refunds, currency, and installments. |
| `duplicate_reference` | Same `order_id` appears multiple times | Inspect retry and idempotency logic. |
| `fee_missing` | Fee not imported | Update report parser or finance mapping. |

## Workflow 8: Gateway outage and fallback

### Preconditions

- At least two gateways enabled.
- Each gateway supports required payment capabilities.
- Routing policy defines safe fallback reasons.
- Monitoring detects error rate and timeout spikes.

### Steps

1. Health check marks provider degraded.
2. New eligible payments route to next provider.
3. In-flight transactions remain pinned to original provider.
4. Unknown states trigger status inquiry, not fallback.
5. Operations dashboard shows affected order ids.
6. Restore provider only after successful canary payments.

## Workflow 9: Migrating a single gateway to orchestration

1. Freeze current payment contract as baseline.
2. Add canonical payment model while keeping existing gateway behavior.
3. Write adapter for current gateway first.
4. Backfill local transaction identifiers.
5. Add second gateway in sandbox.
6. Run test scenarios from `references/test-scenarios.md`.
7. Release orchestration with only current gateway enabled.
8. Enable canary routing for second gateway.
9. Monitor approval, error, refund, and reconciliation metrics.
10. Expand routing gradually.

## Workflow 10: Consumer support process

1. Search by order id, email, phone, amount, and last four digits when available.
2. Confirm local status and provider status.
3. Check settlement/refund state.
4. Provide customer-safe explanation.
5. Never share issuer raw codes, internal risk notes, or full card data.
6. Escalate unknown duplicate or chargeback cases.

| Case | Hebrew message |
|---|---|
| Approved | `התשלום אושר. מספר אסמכתא: 123456.` |
| Pending | `התשלום עדיין בבדיקה. נעדכן לאחר אישור סופי.` |
| Declined | `העסקה לא אושרה. ניתן לנסות כרטיס אחר או לפנות לחברת האשראי.` |
| Refund started | `ההחזר נקלט. הזיכוי יופיע לפי זמני חברת האשראי.` |
