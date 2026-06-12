# Migration Checklist

Use this checklist when replacing manual follow-ups, spreadsheet reminders, WhatsApp copy-paste flows, or legacy CRM automations.

## 1. Inventory current workflows

- List every current message type: service check-in, review request, payment reminder, missing documents, appointment reminder, delivery check-in.
- Export existing templates.
- Identify who sends each message today.
- Identify send channels: WhatsApp, SMS, email, CRM, phone.
- Mark workflows that include promotions, coupons, or referral offers.
- Mark workflows that include sensitive information.

## 2. Clean customer data

- Normalize phone numbers to E.164, for example `+972501234567`.
- Normalize dates to `DD/MM/YYYY`.
- Store customer first names separately.
- Remove duplicate contacts.
- Remove stale contacts with no recent transaction.
- Mark opted-out contacts before importing.
- Mark contacts with open complaints, refund requests, warranty cases, or legal disputes.

## 3. Map consent and suppression

- Import opt-in source, timestamp, and scope.
- Import opt-out records from SMS, WhatsApp, email, and manual notes.
- Create a single suppression list.
- Define which messages are transactional and which are promotional.
- Add opt-out text to promotional messages.
- Block promotional sends when consent is unknown.

## 4. Rebuild templates

- Convert every template to neutral Hebrew.
- Remove requests for a specific rating.
- Remove incentives tied to reviews.
- Remove sensitive details from SMS and WhatsApp.
- Use `₪` for amounts.
- Use `DD/MM/YYYY` for dates.
- Add business-specific fields only when safe.

## 5. Configure Israeli timing

- Set timezone to `Asia/Jerusalem`.
- Block Saturday.
- Set Friday cutoff to 12:30.
- Block 21:00-08:00.
- Add yearly holiday blackout dates.
- Set separate windows for B2B, retail, home services, and appointments.

## 6. Build idempotency

- Define key format: `{event_id}:{contact_id}:{event_type}:{event_date}`.
- Store queued, sent, failed, suppressed, and skipped states.
- Prevent duplicate sends from retries.
- Disable overlapping legacy automations before production.

## 7. Integrate channels

### WhatsApp

- Verify Business account.
- Confirm template approval when required.
- Track last inbound customer message.
- Test Hebrew line breaks and link previews.

### SMS

- Register sender if the provider requires it.
- Test Unicode length and segment cost.
- Support inbound opt-out words such as `הסר`, `STOP`, `remove`.
- Confirm provider retry behavior.

### Email

- Configure SPF, DKIM, and DMARC.
- Use plain-text body.
- Add unsubscribe header for marketing.
- Avoid link shorteners.

### CRM

- Confirm webhook authentication.
- Store generated message and approval status.
- Log provider message IDs.

## 8. Test before launch

- Run the 30 scenarios in `references/test-scenarios.md`.
- Run the pytest suite in `scripts/`.
- Send 10 internal test messages.
- Send 10 real messages with manual approval.
- Review replies and complaints.
- Fix templates before batch rollout.

## 9. Launch gradually

- Start with one message type.
- Limit to recent completed transactions.
- Cap daily sends.
- Review failure logs twice daily during the first week.
- Keep manual override for sensitive cases.

## 10. Decommission old automation

- Disable old scheduled jobs.
- Archive old templates.
- Keep read-only history.
- Confirm suppression list sync.
- Remove stale CSV files from shared drives.
- Rotate old API keys.

## 11. Ongoing maintenance

- Update holiday blackout list yearly.
- Review legal and platform rules periodically.
- Sample message quality monthly.
- Audit opt-outs.
- Update templates after customer feedback.
- Re-run test scenarios after every template change.
