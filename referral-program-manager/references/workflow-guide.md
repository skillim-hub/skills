# Workflow Guide

## Workflow 1: Launch a local service referral program

Goal: launch a compliant, trackable referral program for a local Israeli service business.

1. Choose reward: use credit or coupon for most consumer businesses; use cash only when identity and tax checks are ready.
2. Define qualifying action: paid invoice, completed appointment, paid order, or activated subscription.
3. Set waiting period: 3–30 days for services; at least the return/cancellation window for goods.
4. Publish terms: include exclusions, expiry, caps, and reversal.
5. Configure program:

```bash
python scripts/referral-program-manager-cli.py init-state --state data.json
python scripts/referral-program-manager-cli.py create-program \
  --state data.json \
  --program-id salon-50-2026 \
  --name "Salon ₪50 Referral" \
  --reward-type credit \
  --reward-amount 50 \
  --qualifying-action paid_completed_appointment \
  --cooldown-days 3 \
  --max-rewards 10
```

6. Add referrer and referred customer.
7. Generate link.
8. Train staff to request referral code during booking.
9. Run test scenarios.
10. Launch a limited pilot.

Acceptance criteria: link resolves, signup stores code, paid appointment creates evidence, reward appears only after waiting period, export contains reward ID, customer ID, amount in ₪, and tax treatment.

## Workflow 2: Ecommerce coupon reward

Rules: referred customer receives 10% first-order coupon; referrer receives ₪40 coupon after 14 days; minimum order ₪199; gift cards, wholesale, canceled, returned, and existing-customer orders are excluded.

Steps:

1. Create `coupon` program with `paid_order_not_returned` action.
2. Capture referral code at checkout.
3. Store order ID as evidence.
4. Wait for delivery plus return window.
5. Qualify event.
6. Generate one-time coupon in commerce platform.
7. Mark reward paid after coupon creation.
8. Reconcile unused and expired coupons monthly.

Edge handling: partial returns require explicit terms; chargebacks move reward to review; typos can be corrected only before first paid order; stacking depends on published policy.

## Workflow 3: B2B cash or credit payout

Goal: pay or credit ₪250 to a business that referred a signed client.

1. Register referrer with business name, VAT number, contact, and payout preference.
2. Register referred lead.
3. Attach signed agreement and paid invoice evidence.
4. Run duplicate and related-party checks.
5. Request invoice/receipt or approved tax document.
6. Approve reward.
7. Export bank transfer CSV when cash is selected.
8. Upload to banking portal.
9. Store bank reference.
10. Mark reward paid.

Required ledger fields: reward ID, recipient customer ID, amount, tax treatment, invoice number, withholding status, bank transfer reference, approver, payment date in DD-MM-YYYY.

## Workflow 4: Gateway refund reward

Use this only when gateway and acquirer permit partial refund connected to the original transaction.

1. Store original gateway transaction ID.
2. Approve reward with method `refund`.
3. Build refund request through gateway adapter.
4. Submit with idempotency key.
5. Store provider response.
6. Mark reward `submitted`.
7. Wait for webhook or settlement report.
8. Mark reward `paid` only after approval.
9. Create credit note or accounting record when required.
10. Reconcile with provider report.

Failure handling:

| Failure | Response |
|---|---|
| Refund not allowed | Convert to store credit after customer notice, if terms allow. |
| Amount exceeds refundable balance | Reduce amount or create credit. |
| Gateway timeout | Retry with same idempotency key. |
| Duplicate request | Fetch existing result and attach to reward. |

## Workflow 5: Manual fraud review

Triggers: same phone/email, same card token, three referrals from same IP in 30 days, order value barely above minimum, chargeback history, employee or related-party signal.

Steps:

1. Move event to `fraud_review`.
2. Freeze reward creation.
3. Check customer IDs, phones, emails, card token, device/IP, order status, cancellations.
4. Decide: approve, reject, request more information, or suspend referrer.
5. Record reason and reviewer.
6. Notify customer support.

Reason codes: `SELF_REFERRAL`, `DUPLICATE_CUSTOMER`, `RELATED_PARTY`, `PAYMENT_RISK`, `VOLUME_ABUSE`, `MANUAL_OVERRIDE_APPROVED`.

## Workflow 6: Spreadsheet migration

1. Export as CSV.
2. Normalize dates to DD-MM-YYYY.
3. Normalize phones to `+9725XXXXXXXX`.
4. Deduplicate by phone, email, VAT number, customer ID, and payment token.
5. Create programs first.
6. Import customers.
7. Import events.
8. Import rewards with original status.
9. Attach document numbers.
10. Reconcile totals and run tests.

## Workflow 7: Customer support

For "Where is my reward?":

1. Verify identity.
2. Find event by code, phone, or referred customer.
3. Explain status without exposing another customer's private data.
4. For `registered`, explain missing qualifying action.
5. For `qualified`, explain waiting period.
6. For `reward_pending`, explain approval queue.
7. For `reward_approved`, explain payment/credit timeline.
8. For `reward_paid`, provide credit/coupon/payment reference.
9. For `rejected`, provide terms-based reason, not internal fraud details.
10. Record support note.

## Workflow 8: Month-end reconciliation

1. Export rewards with `approved`, `paid`, `reversed`, and `expired`.
2. Compare approved rewards to accounting entries.
3. Compare paid rewards to gateway or bank report.
4. Check open credit liability.
5. Check expired coupons.
6. Review fraud queue.
7. Review support complaints.
8. Produce summary with approved ₪, paid ₪, open liability, reversals, expired credit, open fraud cases, and complaints.

## Workflow 9: Pause or rollback

Pause when gateway webhook fails repeatedly, fraud rate spikes, terms contain an error, accounting classification is disputed, or complaints exceed threshold.

Steps: disable new referral-code creation, freeze qualified rewards, publish support notice when needed, preserve logs, fix root cause, reprocess pending events in order, reopen with versioned terms.
