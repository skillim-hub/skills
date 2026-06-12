# Migration Checklist

Use this checklist when replacing a gateway, adding a second gateway, or moving from direct integration to orchestration.

## Phase 1: Inventory

- List active gateways, terminals, currencies, and settlement accounts.
- Export current transaction states for the last 18 months or the required accounting period.
- List enabled features: hosted checkout, tokenization, installments, refunds, authorization, capture, wallets, invoices.
- Identify all code paths that create, update, refund, or query payments.
- Identify all webhooks, return URLs, cron jobs, and manual back-office actions.
- Document current provider fields used by support and finance.
- Record current decline/error mapping.
- Record current reconciliation report format.

## Phase 2: Canonical model

- Define `order_id`, `payment_id`, `gateway`, `transaction_id`, `status`, amount, currency, and approval code.
- Store amount in agorot.
- Store gateway raw status in a redacted audit field.
- Create immutable ledger events for charge, authorization, capture, refund, void, dispute, and adjustment.
- Add idempotency keys for charge, checkout, refund, and capture.
- Add webhook event table with provider event id and signature result.

## Phase 3: Adapter parity

For the existing gateway:

- Implement adapter using current production behavior.
- Match current request fields.
- Match current webhook handling.
- Match current refund flow.
- Match current reports.
- Run approval, decline, refund, timeout, and duplicate tests.
- Release with routing pinned to existing gateway only.

## Phase 4: Data migration

- Backfill existing transaction ids.
- Backfill gateway name for each payment.
- Backfill approval code where available.
- Backfill refund records and link them to original charges.
- Mark unknown legacy records explicitly.
- Do not invent approval states when source data is missing.
- Preserve original timestamps and add migration timestamp separately.

## Phase 5: Second gateway onboarding

- Confirm contract terms and supported features.
- Create sandbox credentials.
- Configure return URL and webhook URL.
- Configure allowed domains and IP restrictions when required.
- Map request and response fields.
- Run gateway-specific scenarios from `test-scenarios.md`.
- Run Hebrew text and ₪ amount tests.
- Run daily reconciliation import against sample reports.
- Enable internal canary transactions.
- Enable limited real customer traffic only after reconciliation passes.

## Phase 6: Cutover

### Before cutover

- Freeze risky payment changes.
- Confirm rollback plan.
- Confirm operations owner and provider support contacts.
- Lower alert thresholds for errors and timeouts.
- Confirm customer support scripts.
- Confirm finance report import.

### During cutover

- Enable new routing policy.
- Keep in-flight transactions pinned to original gateway.
- Monitor approval rate, error rate, pending payments, duplicate attempts, and webhook failures.
- Compare provider dashboard against local state every hour for the first day.
- Disable fallback after issuer declines.

### After cutover

- Reconcile first settlement cycle manually.
- Review all payment exceptions.
- Compare fees and net settlement.
- Verify refund path on real low-value transaction.
- Verify chargeback/dispute visibility.
- Remove unused credentials only after refund and dispute windows are handled.

## Phase 7: Token migration

Token portability is rarely automatic. Treat tokens as provider-specific unless a written provider process confirms otherwise.

- Identify active tokens and customer consent records.
- Check whether token export/import is supported.
- If unsupported, request customers to update payment method.
- Do not move tokens through internal systems unless PCI scope and contract allow it.
- Record migration consent and new token creation date.
- Deactivate old tokens after successful replacement and required grace period.

## Rollback plan

- Keep original gateway credentials active.
- Keep original webhook endpoint able to process old events.
- Keep payment attempts pinned by transaction id.
- Revert routing policy without changing historical records.
- Query statuses for all attempts created during incident window.
- Communicate with support using order ids and customer-safe language.

## Sign-off checklist

| Role | Sign-off item |
|---|---|
| Product | Customer flow, messages, cancellation terms. |
| Engineering | Tests, idempotency, webhooks, status inquiry, rollback. |
| Security | Secrets, PCI scope, logs, access control. |
| Finance | Invoices, refunds, settlement reports, fees. |
| Support | Search tools, customer scripts, escalation paths. |
| Management | Provider contracts and risk acceptance. |


## v3 source-validated migration note

Treat new Grow integrations as `grow`. Keep `meshulam` only as a legacy adapter name for existing merchant contracts. During migration, map old Meshulam page or process identifiers to Grow transaction records and reconcile both names for at least one settlement cycle.
