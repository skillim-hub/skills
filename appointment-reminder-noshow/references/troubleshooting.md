# Troubleshooting Guide

Use this guide when reminders are not scheduled, not delivered, misclassified, or producing inaccurate no-show results.

## Fast diagnosis

| Check | Command or action | Expected result |
|---|---|---|
| Validate phone | `python scripts/appointment_reminder_noshow_cli.py validate-phone 050-123-4567` | `+972501234567` |
| Generate one message | `python scripts/appointment_reminder_noshow_cli.py message ...` | JSON reminder body with `DD-MM-YYYY` in Hebrew mode |
| Run tests | `pytest -q` | All tests pass |
| Check consent | Inspect customer record | At least one of `consent_whatsapp` or `consent_sms` is true |
| Check quiet hours | Inspect `metadata.quiet_hours_adjusted` | True only when send time was moved |

## Scheduling problems

### No reminders are generated

Likely causes:

- Appointment time is already in the past.
- All configured reminder offsets produce past send times.
- Customer phone is invalid.
- Customer has no channel consent.

Fix:

1. Normalize the phone number.
2. Check consent fields.
3. Pass an explicit `now` value in tests.
4. Reduce reminder offsets for same-day appointments.

### Reminder moved to an unexpected time

Likely cause: the calculated send time falls inside quiet hours.

Fix:

- Keep quiet hours in `ReminderPolicy(quiet_start_hour=21, quiet_end_hour=8)`.
- Document the adjustment in the outgoing message metadata.
- For urgent operational changes, use manual contact rather than disabling quiet hours globally.

### Duplicate reminders are created

Likely causes:

- The same appointment ID appears twice in the input file.
- A retry job reruns without idempotency checks.
- Provider callback was interpreted as a send request.

Fix:

- Deduplicate by `appointment_id`, `channel`, and `send_at`.
- Store a provider message ID after successful send.
- Treat callbacks as status updates only.

## WhatsApp problems

| Symptom | Cause | Fix |
|---|---|---|
| `400` response | Template variable mismatch or invalid payload | Compare approved template variables with payload. |
| `401` response | Expired token | Rotate the token and reload environment variables. |
| `403` response | Phone number or template unavailable | Verify WABA, phone number ID, and template approval. |
| Customer does not receive business-initiated message | No approved template or missing opt-in | Use a utility template and documented consent. |
| Message content rejected | Marketing language in utility template | Remove discounts, offers, and unrelated upsells. |

## SMS problems

| Symptom | Cause | Fix |
|---|---|---|
| Message is split into several segments | Hebrew uses UCS-2 encoding | Keep SMS short or use WhatsApp for longer content. |
| `undelivered` status | Carrier filter, blocked sender, unreachable phone | Try another permitted channel or manual call. |
| Sender name not displayed | Sender ID restrictions or provider configuration | Configure approved sender ID where available. |
| Link not clickable | Device or carrier behavior | Place the full HTTPS link at the end of the message. |

## Consent and opt-out problems

### Customer asks to stop messages

Action:

1. Mark marketing consent false immediately.
2. Stop nonessential reminders if the customer clearly asks to stop all messages.
3. Keep a minimal suppression record to avoid future sends.
4. Confirm the stop request only when permitted and necessary.

### Reminder is accused of being spam

Action:

1. Review whether the message included promotion, discount, upsell, or unrelated service text.
2. Confirm that the appointment existed and that the customer gave contact details for that appointment.
3. Remove marketing text from reminder templates.
4. Keep future re-booking messages limited to the missed appointment.

## No-show tracking problems

| Symptom | Cause | Fix |
|---|---|---|
| No-show rate too high | Cancelled or rescheduled records counted as no-shows | Count only `no_show` among completed or missed appointments. |
| Confirmed customers marked no-show too early | Attendance job ran before appointment ended | Add a grace period after start time. |
| Re-booking suggestions are outside business hours | Slot generator was configured incorrectly | Set business start/end hours and timezone. |
| Customer disputes no-show | Manual arrival record missing | Keep staff override and audit notes. |

## Data protection problems

### Sensitive details appear in provider logs

Fix:

- Replace service-specific text with generic labels such as “appointment”.
- Remove notes, diagnosis, case numbers, and private details from message bodies.
- Store provider message IDs and statuses instead of full payloads when possible.

### Too many staff members can see attendance history

Fix:

- Restrict access by role.
- Export only aggregate no-show rates when possible.
- Remove historical data that is no longer operationally necessary.

## CLI problems

| Error | Cause | Fix |
|---|---|---|
| `No such option` | Typo in command flag | Run `--help` on the command. |
| `Invalid value for --starts-at` | Date is not ISO 8601 | Use `2026-06-18T15:30:00+03:00`. |
| `CONSENT_MISSING` | Both consent flags are false | Pass `--consent-whatsapp` or `--consent-sms`. |
| Import error | Running from another directory without module path | Run from the package root or set `PYTHONPATH=scripts`. |

## Escalation checklist

Escalate to a human operator when:

- A customer disputes a fee or no-show mark.
- A sensitive appointment type may expose private information.
- Provider delivery fails after one fallback.
- A customer asks for deletion or access to personal data.
- The message content might be marketing without clear consent.
