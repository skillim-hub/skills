# Troubleshooting

## Triage Order

1. Check appointment status.
2. Check phone normalization.
3. Check template vs. free-form eligibility.
4. Check provider API response.
5. Check delivery status webhook.
6. Check duplicate suppression.
7. Check calendar conflicts.
8. Check opt-out and consent.
9. Escalate when customer impact is likely.

## Message Not Sent

Possible causes: missing token, wrong phone number ID, invalid phone, template not approved, outside service window, rate limit, appointment cancelled.

Commands:

```bash
python scripts/whatsapp-scheduling-bot-cli.py validate-phone "054-123-4567"
python scripts/whatsapp-scheduling-bot-cli.py confirm --to "054-123-4567" --customer "דנה" --service "ייעוץ" --start "2026-06-18T10:30:00+03:00" --dry-run
```

Fix: validate phone, use approved template, check token and phone ID, requeue only after checking idempotency.

## Duplicate Reminder

Possible causes: worker ran twice without locking, webhook retry processed as new, appointment imported twice, idempotency key changed, staff also sent manual reminder.

Fix: deduplicate by `(appointment_id, offset_minutes, template_name)`, persist provider message ID, lock reminder rows, keep stable appointment ID, warn staff.

## Wrong Time

Possible causes: naive datetime, server timezone, daylight-saving conversion, calendar update without reminder update, `MM-DD-YYYY` parsing.

Fix: store timezone-aware ISO datetimes, display `DD/MM/YYYY`, recalculate reminders after reschedule, test DST cases.

## Template Rejected

Possible causes: wrong category, promotional wording in utility reminder, unclear placeholders, missing examples.

Fix: remove coupons and upsells, use realistic Hebrew examples, split reminder and marketing templates, keep placeholders short.

## Webhook Verification Fails

Possible causes: wrong verification token, JSON response instead of raw challenge, HTTPS issue, firewall, wrong route.

Fix: return exact `hub.challenge`, 200 only when token matches, 403 otherwise, confirm public HTTPS URL.

## Incoming Message Not Parsed

Possible causes: audio/image/button/interactive payload, status payload, emoji-only message, unsupported slang, wrong phone number ID.

Fix: store metadata, route media to staff, add interactive parsing, add real examples to tests.

## Reminders Sent After Cancellation

Possible causes: queue not cancelled, worker selected before cancellation, calendar did not sync, stale status.

Fix: re-check status immediately before send, cancel pending reminders transactionally, use locks, reconcile calendar changes.

## Hebrew Looks Broken

Possible causes: mixed RTL/LTR, hidden line breaks, long variables, odd punctuation around phone numbers.

Fix: preview on a device, put address on its own line, keep dates/prices compact, keep variables short.

## Customer Calls It Spam

Possible causes: marketing in reminder, no service relationship, old CRM import, too many reminders, no human path.

Fix: stop messages, mark opt-out, review consent source, remove promotions, reduce cadence, escalate.

## Error Decision Table

| Error | Check first | Safe next action |
|---|---|---|
| 400 invalid recipient | Phone normalization | Correct CRM phone |
| 400 template parameters | Placeholder count | Fix builder |
| 401 token | Secret and expiry | Rotate token |
| 403 permission | WABA and phone ID access | Reconnect asset |
| 404 object not found | API version and ID | Verify IDs |
| 429 rate limit | Volume and quality | Back off |
| 5xx provider | Provider status | Retry with jitter |
| No webhook | URL and subscriptions | Reconfigure |
| Duplicate webhook | Message ID | Ignore duplicate |
| Calendar conflict | Slot lock | Offer alternatives |

## Log Fields

```json
{
  "event": "whatsapp_send",
  "appointment_id": "apt_123",
  "to_masked": "97254***567",
  "template_name": "appointment_reminder_he",
  "idempotency_key": "apt_123:1440:appointment_reminder_he",
  "provider_message_id": "wamid...",
  "status": "sent",
  "timestamp": "2026-06-17T10:30:00+03:00"
}
```

Avoid full tokens, routine full webhook payloads, sensitive notes, payment data, and full message bodies for regulated services.

## Recovery Playbooks

### Provider Outage

1. Pause reminder worker.
2. Queue due messages.
3. Monitor provider status.
4. Resume with rate limiting.
5. Skip reminders for appointments already started.
6. Notify staff.

### Bad Template

1. Pause sends using the template.
2. Create corrected template.
3. Submit for approval.
4. Use staff handling for urgent same-day cases.
5. Re-enable after approval.
6. Add a regression test.

### Token Leaked

1. Revoke token.
2. Rotate to least-privilege token.
3. Search logs and repositories.
4. Review unusual sends.
5. Update secrets manager.
6. Document the incident.

### Calendar Corruption

1. Stop appointment writes.
2. Export appointment store.
3. Compare against calendar.
4. Reconcile by appointment ID.
5. Recompute reminders.
6. Run scenario tests before reopening.
