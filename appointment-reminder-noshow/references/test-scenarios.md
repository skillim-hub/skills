# Test Scenarios

Use these scenarios for manual QA, automated tests, and acceptance checks.

## 1. Hebrew WhatsApp reminder for a confirmed physiotherapy appointment

Input:

- Customer: יעל כהן
- Phone: `050-123-4567`
- Consent: WhatsApp true, SMS true
- Appointment: 18-06-2026 15:30
- Business: קליניקת אביב
- Location: רוטשילד 10, תל אביב

Expected:

- Phone normalizes to `+972501234567`.
- Channel is `whatsapp`.
- Body uses Hebrew, `DD-MM-YYYY`, and clear confirm/reschedule/cancel options.

## 2. SMS fallback when WhatsApp consent is missing

Input:

- WhatsApp consent false
- SMS consent true

Expected:

- Channel is `sms`.
- Body is shorter than the WhatsApp version.
- No WhatsApp payload is created.

## 3. Consent missing

Input:

- WhatsApp consent false
- SMS consent false

Expected:

- Planner raises `CONSENT_MISSING`.
- No reminder is sent.

## 4. Invalid Israeli mobile number

Input:

- Phone: `03-555-5555`

Expected:

- Validation fails with `PHONE_INVALID` because reminders require a mobile number.

## 5. Quiet-hour adjustment

Input:

- Appointment: 18-06-2026 07:00
- Reminder offset: 3 hours before

Expected:

- Calculated 04:00 send time moves to an allowed quiet-hour boundary.
- Metadata marks `quiet_hours_adjusted=true`.

## 6. Past reminder skipped

Input:

- `now`: 18-06-2026 14:00
- Appointment: 18-06-2026 15:30
- Offsets: 48, 24, and 3 hours before

Expected:

- 48-hour, 24-hour, and 3-hour reminders are skipped because their send times are past.
- No automated late reminder is created unless a same-day policy is added.

## 7. Customer confirms attendance

Input:

- Incoming reply: `1`

Expected:

- Appointment status changes to `confirmed`.
- Later reminders suppress confirmation wording or stop according to policy.

## 8. Customer requests reschedule

Input:

- Incoming reply: `2`

Expected:

- Appointment status changes to `rescheduled_requested` or equivalent workflow state.
- Re-booking slots are generated.

## 9. Customer cancels before cutoff

Input:

- Incoming reply: `3`
- Reply arrives before cancellation cutoff

Expected:

- Appointment status changes to `cancelled`.
- No no-show is recorded.
- Optional re-booking message stays transactional.

## 10. No-show after missed appointment

Input:

- Appointment start passed.
- No arrival, cancellation, or reschedule exists.

Expected:

- Appointment status changes to `no_show` after grace period.
- No-show count increments.
- Re-booking suggestion is generated without shame or marketing.

## 11. Hebrew SMS segmentation risk

Input:

- Hebrew SMS body longer than 70 characters

Expected:

- QA flags possible multiple SMS segments.
- Recommendation suggests shortening or switching to WhatsApp.

## 12. Provider failure with fallback

Input:

- WhatsApp send returns `429`.
- SMS consent true.

Expected:

- System backs off WhatsApp retries.
- Manual or SMS fallback is considered only if policy allows.
- Duplicate messages are prevented.

## 13. Marketing content blocked without consent

Input:

- Re-booking message includes a discount or package upsell.
- Marketing consent false.

Expected:

- Validation blocks the message with `MARKETING_WITHOUT_CONSENT`.

## 14. Price display with ₪ and Israeli date

Input:

- Appointment price: 250
- Language: Hebrew

Expected:

- Body or metadata can show `₪250`.
- Date is `18-06-2026`, not `2026-06-18`.

## 15. Data minimization check

Input:

- Appointment notes include sensitive diagnosis.

Expected:

- Message body excludes diagnosis.
- Stored provider payload uses a generic service label.
