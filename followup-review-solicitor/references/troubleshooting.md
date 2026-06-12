# Troubleshooting

Use this guide when generated messages, schedules, imports, or channel sends behave incorrectly.

## Message problems

### Unresolved placeholders appear

Example:

```text
היי {customer_name}, תודה שבחרת ב{business_name}
```

Cause: missing input field or template mismatch.

Fix:

1. Validate required fields before rendering.
2. Use fallback greeting when `customer_name` is empty.
3. Reject sending when `business_name`, `event_type`, or `event_date` is missing.
4. Add a test case for every custom template.

### Hebrew sounds unnatural

Cause: literal translation, gendered wording, or overly formal phrasing.

Fix:

- Prefer `אפשר`, `נא`, `תודה`, `רציתי לוודא`.
- Avoid `דרג אותנו`, `תן 5 כוכבים`, `אנא השאר ביקורת חיובית`.
- Use `חוות דעת` instead of transliterated review.
- Use `חשבונית מס/קבלה` and `דו"ח מע"מ` for accounting contexts.

### SMS is too long

Cause: WhatsApp-style text used for SMS.

Fix:

- Remove secondary sentence.
- Move details to a link.
- Keep review link on a separate line only when the provider preserves line breaks.
- Test Unicode segment counts with the SMS vendor.

### Message includes sensitive information

Cause: event data inserted directly into the template.

Fix:

- For clinics, legal, therapy, insurance, debt, minors, and tax investigations, use generic wording only.
- Do not include diagnosis, treatment type, supplier details, debt notes, or ID numbers.
- Send secure portal links for documents.

## Scheduling problems

### Message scheduled on Saturday

Cause: calendar rules disabled or timezone missing.

Fix:

1. Set timezone to `Asia/Jerusalem`.
2. Enable Saturday blackout.
3. Add Friday noon cutoff.
4. Add a holiday blackout list.

### Friday afternoon sends still occur

Cause: Friday cutoff set to end of day.

Fix:

- Set Friday cutoff to 12:30.
- Move non-urgent messages to Sunday 09:30.
- Allow override only for urgent transactional notices.

### Payment reminder sent too late

Cause: due date logic not connected to invoice status.

Fix:

- Send upcoming reminder 1 day before due date at 09:30.
- Send overdue reminder 3 business days after due date at 09:30.
- Stop reminders immediately after payment confirmation.

### Duplicate sends

Cause: retry without idempotency or multiple automations attached to the same CRM stage.

Fix:

- Use idempotency key: `{event_id}:{contact_id}:{event_type}:{event_date}`.
- Store send status before calling the provider.
- Treat HTTP 409 duplicate as success or already queued.
- Disable overlapping legacy automation.

## Consent and compliance problems

### Opted-out customer receives a message

Cause: suppression list not checked across channels.

Fix:

1. Centralize suppression by contact ID and channel.
2. Apply suppression before rendering.
3. Record inbound `הסר`, `STOP`, `remove`, and manual opt-out.
4. Audit failed suppressions.

### Review request sent after complaint

Cause: sentiment status not updated from support system.

Fix:

- Add a `complaint_open` flag.
- Stop review flow when refund, repair, warranty, anger, or legal words appear.
- Route to service recovery template.

### Promotional text sent without opt-in

Cause: marketing offer inserted into a transactional template.

Fix:

- Detect words such as `מבצע`, `הנחה`, `קופון`, `לקוחות חוזרים`.
- Require `marketing_opt_in`.
- Add opt-out line.
- Remove promotion when consent is unknown.

## Channel problems

### WhatsApp rejects message outside window

Cause: free-form message sent outside the customer-care window.

Fix:

- Use an approved template where policy requires it.
- Wait for inbound customer reply if possible.
- Track last inbound timestamp.

### SMS sender ID rejected

Cause: provider-specific sender restrictions.

Fix:

- Use a registered sender where required.
- Avoid Hebrew sender IDs unless supported.
- Keep a numeric fallback sender.

### Email lands in spam

Cause: domain authentication or suspicious links.

Fix:

- Configure SPF, DKIM, and DMARC.
- Avoid link shorteners.
- Use a recognizable domain.
- Include plain-text body and unsubscribe header for marketing messages.

## Import and migration problems

### Dates parsed incorrectly

Cause: US-style month/day parsing.

Fix:

- Require `DD/MM/YYYY`.
- Reject ambiguous dates such as `06/07/26`.
- Convert to ISO internally only after validation.

### Phone numbers fail

Cause: local Israeli formats mixed with E.164.

Fix:

- Normalize `050-123-4567` to `+972501234567`.
- Reject missing mobile prefix unless the channel supports landlines.
- Keep original value in import audit.

### Amounts display incorrectly

Cause: numeric value not localized.

Fix:

- Format as `₪1,250` or `₪1,250.50`.
- Do not use `$`, `NIS`, or `ש"ח` in machine-generated summaries unless the business explicitly prefers it.

## Debug checklist

- Check `should_send`.
- Check `fallback_action`.
- Check `consent_status`.
- Check `sentiment`.
- Check `complaint_open`.
- Check generated `recommended_send_at`.
- Check timezone offset.
- Check unresolved placeholders.
- Check channel-specific length and policy.
- Check review link.
- Check idempotency key.
- Check provider response code.
- Check opt-out persistence.

## Emergency stop

Use an emergency stop when many messages are wrong, duplicated, or non-compliant.

1. Pause all queues.
2. Disable provider credentials if needed.
3. Export send log and affected contact IDs.
4. Suppress further messages for affected contacts.
5. Send correction only when legally and operationally appropriate.
6. Fix template, segmentation, or consent source.
7. Restart with a 10-contact test batch.
