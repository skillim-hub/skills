# Migration Checklist

Use this checklist when migrating from a simple prompt, spreadsheet, manual travel process, or older skill package to this enhanced Travel-Booking Assistant.

## 1. Content migration

- Remove promotional references, visual marks, image references, personal attribution, and distribution callouts.
- Keep neutral imperative wording.
- Replace vague travel advice with concrete workflows.
- Add Israeli domestic use cases: Eilat, Ramon Airport, Israel Rail, hotels, VAT invoices.
- Add outbound international use cases with currency conversion and passport prompts.
- Add Hebrew localization with ₪ and DD/MM/YYYY.
- Add troubleshooting and test scenarios.

## 2. Data migration

| Old field | New field |
|---|---|
| destination | trip.destination |
| from | trip.origin |
| date_start | trip.start_date |
| date_end | trip.end_date |
| pax | travelers |
| business_trip | business.is_business |
| invoice_needed | business.needs_vat_invoice |
| currency | money.supplier_currency |
| exchange_rate | money.fx_rate |
| booking_status | status |

## 3. Integration migration

- Replace hard-coded API keys with environment variables.
- Add idempotency keys for booking and cancellation actions.
- Add timeout and retry policy.
- Add structured error mapping.
- Add exchange-rate source and timestamp.
- Add audit record for quote, approval, booking, cancellation, and refund events.
- Add supplier request/response IDs.
- Add redaction for sensitive fields.

## 4. Hebrew migration

- Use תאריך, יעד, נוסעים, חשבונית מס, קבלה, חשבונית מס/קבלה, עוסק מורשה, עוסק פטור, ניכוי מס תשומות.
- Use ש״ח or ₪ consistently in user-facing output.
- Use DD/MM/YYYY for dates.
- Avoid unnecessary transliteration when standard Hebrew terms exist.
- Use formal but practical Israeli business language.

## 5. Testing migration

Before production, confirm:

- At least 20 automated tests pass.
- Hebrew examples render correctly.
- CLI validates invalid dates.
- FX conversion preserves original currency.
- Business invoice checklist appears.
- International passport prompts appear.
- Separate-ticket warnings appear.
- Shabbat/holiday warnings appear.
- No promotional references, visual marks, image references, or personal attribution remain.

## 6. Operational migration

- Define approval owner.
- Define payment owner.
- Define refund owner.
- Define invoice follow-up owner.
- Define retention period for travel documents.
- Define escalation path for urgent travel issues.
- Define fallback when live supplier data is unavailable.

## 7. Rollback plan

- Preserve the previous workflow for read-only reference.
- Keep old booking references and receipts unchanged.
- Use the new assistant only for new quotes until validated.
- Compare totals from old and new process for ten sample cases.
- Enable production booking only after approval and audit checks pass.

## 8. Cutover checklist

- [ ] README updated.
- [ ] Metadata version bumped.
- [ ] Personal attribution field removed from metadata.
- [ ] LICENSE keeps the permitted MIT holder text.
- [ ] SKILL.md complete.
- [ ] SKILL_HE.md complete.
- [ ] API reference complete.
- [ ] Workflow guide complete.
- [ ] Troubleshooting guide complete.
- [ ] Test scenarios complete.
- [ ] Client and CLI installed.
- [ ] Pytest suite passing.
- [ ] Example scripts run.
- [ ] No visual marks or image references remain.
