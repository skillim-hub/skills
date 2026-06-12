# Migration Checklist

## 1. Discovery

- [ ] List all sources: spreadsheet, CRM, ecommerce, booking, gateway, accounting.
- [ ] Identify every active offer and terms version.
- [ ] Identify unpaid historical rewards.
- [ ] Identify coupons, credits, refunds, cash payouts, and manual promises.
- [ ] Identify support exceptions.
- [ ] Identify personal data: phone, email, ID, VAT, bank, IP, device.

## 2. Data mapping

| Old field | New field |
|---|---|
| customer name | `Customer.name` |
| phone | normalized `Customer.phone` |
| email | lowercase `Customer.email` |
| referral code | `ReferralEvent.referral_code` |
| friend name | `referred_customer_id` after creation |
| reward | `Reward.amount_ils` |
| status | event and reward status |
| invoice | evidence or document number |
| payment reference | `gateway_reference` |
| notes | audit/support note |

## 3. Data cleaning

- [ ] Convert dates to `DD-MM-YYYY`.
- [ ] Normalize phones to `+9725XXXXXXXX`.
- [ ] Lowercase and trim emails.
- [ ] Remove empty rows and tests.
- [ ] Deduplicate by customer ID, phone, email, VAT, payment token.
- [ ] Split combined cells.
- [ ] Mark uncertain records for review.
- [ ] Preserve original row number.
- [ ] Keep read-only original export.

## 4. Status mapping

| Legacy | New |
|---|---|
| new / lead | `registered` |
| paid / done | `qualified` |
| waiting | `reward_pending` |
| approved | `reward_approved` |
| paid / credited | `reward_paid` |
| suspicious | `fraud_review` |
| canceled / refunded | `reversed` |
| invalid | `rejected` |

## 5. Accounting reconciliation

- [ ] Sum approved rewards by month.
- [ ] Sum paid rewards by gateway/bank report.
- [ ] Sum unused credits.
- [ ] Sum expired credits.
- [ ] Match rewards to invoice, receipt, credit note, or ledger entry.
- [ ] Review cash payouts for tax documents.
- [ ] Confirm withholding requirements.
- [ ] Store approved `tax_treatment`.

## 6. Privacy and consent

- [ ] Import only necessary data.
- [ ] Separate marketing consent from service contact.
- [ ] Store consent source and date.
- [ ] Mark unknown consent as not opted in.
- [ ] Suppress opt-outs.
- [ ] Restrict ID and bank details.
- [ ] Define retention before import.

## 7. Gateway migration

- [ ] Export transaction IDs.
- [ ] Separate invoice numbers from gateway IDs.
- [ ] Verify refund eligibility.
- [ ] Store terminal/provider per transaction.
- [ ] Map provider codes.
- [ ] Test webhook replay in staging.
- [ ] Reconcile a full month.

## 8. Cutover

Freeze edits, export final CSV, import in staging, compare customer/event/reward counts and ₪ totals, run tests, approve reconciliation, import production, disable old forms, monitor 7 days.

## 9. Rollback

Keep old spreadsheet read-only, retain import logs and mapping file, backup before import, define rollback criteria, prevent duplicate payouts, and brief support.

## 10. Post-migration

Review fraud queue after 7 days, complaints after 14 days, accounting export after first month, unused credit liability, sensitive data retention, and documentation.
