# Test Scenarios

Use these scenarios before launch and after every change to program rules, gateway adapters, imports, or accounting exports.

| # | Scenario | Steps | Expected result |
|---:|---|---|---|
| 1 | Basic credit reward | Create program, add two customers, register, qualify, approve | Reward is approved with configured ₪ amount. |
| 2 | Self-referral by customer ID | Same referrer and referred ID | Validation error; no event. |
| 3 | Self-referral by phone | Two customers share normalized phone | Fraud review or rejection. |
| 4 | Existing customer referred | Referred customer marked existing | Manual review or rejection. |
| 5 | Duplicate referral | Same program/referrer/referred twice | Duplicate blocked. |
| 6 | Two referrers claim same customer | Register two events | First valid attribution wins unless override. |
| 7 | Qualification without payment | Qualify without evidence | Validation error. |
| 8 | Cooldown not elapsed | Approve too early | Reward stays pending. |
| 9 | Coupon expiry | Coupon reward | Expiry calculated and exported. |
| 10 | Refund after qualification | Original order refunded | Reward reversed or review. |
| 11 | Chargeback after cash payout | Chargeback flag | Referrer frozen. |
| 12 | Gateway timeout | Simulate timeout | Retry same idempotency key. |
| 13 | Gateway duplicate key | Submit same reward twice | Existing reference reused. |
| 14 | Invalid webhook signature | Wrong HMAC | Reject. |
| 15 | Valid webhook paid | Signed paid webhook | Reward becomes paid. |
| 16 | Missing tax document | Cash payout with no tax data | Payout blocked. |
| 17 | Business recipient withholding | VAT number and withholding flag | Export includes tax fields. |
| 18 | Marketing opt-out | Opt-out before campaign | Message suppressed. |
| 19 | Hebrew encoding | Hebrew customer name | UTF-8 export readable. |
| 20 | DD-MM-YYYY import | Import `31-03-2026` | Parsed as 31 March 2026. |
| 21 | Ambiguous date | Import `03-04-2026` without locale | Requires explicit format. |
| 22 | Coupon stacking disabled | Existing promo code | Referral coupon rejected unless stackable. |
| 23 | Monthly cap reached | More than cap rewards | Extra event reviewed or rejected. |
| 24 | High-value cash | Above threshold | Manager approval required. |
| 25 | Employee referral | Employee flag | Route to HR policy. |
| 26 | Minor recipient | Minor flag | Cash blocked. |
| 27 | Related-party exception | Shared family phone with reason | Approved only with documented override. |
| 28 | Payout CSV | Export approved rewards | CSV contains ID, amount, status, tax treatment. |
| 29 | Accounting mismatch | Gateway report missing reward | Exception report. |
| 30 | Migration duplicates | Import duplicate phone/email | Merge or review. |
| 31 | Terms version change | Events before/after update | Correct version attached. |
| 32 | Program pause | Disable program | New referrals rejected; existing rewards auditable. |

## Automated categories

Validation, fraud score, status transitions, gateway adapters, CSV export, JSON persistence, async client, CLI smoke, Hebrew/localization, migration.

## Manual UAT

Create ₪10 program, add three Israeli phone formats, send one valid referral, one self-referral, one duplicate, qualify valid event, export approved rewards, verify total ₪10, simulate gateway success, verify `paid`.
