# Migration Checklist

Use this checklist when moving conversation history from spreadsheets, shared inboxes, exports, or an older CRM.

## Before migration

- Define the business purpose for each source: sales, support, appointment, admin, or service.
- Identify the controller or business owner for each dataset.
- List source systems and export formats.
- Confirm retention requirements for messages and attachments.
- Decide which fields must not enter CRM notes.
- Create a sandbox destination.
- Create custom fields for source channel, source thread id, consent status, consent evidence, and external id.

## Source inventory

| Source | Required export fields | Risk check |
|---|---|---|
| WhatsApp Business | phone, message id, timestamp, direction, body | Images and attachments may contain sensitive data. |
| Email | message id, thread id, from, to, subject, timestamp, body | Long signatures may contain unnecessary personal data. |
| SMS | phone, provider message id, timestamp, body | Opt-out words must be preserved. |
| Spreadsheet | name, phone, email, note, date | Old sheets often contain duplicate names and stale consent. |
| Legacy CRM | object id, phone, email, notes, consent fields | Field semantics may differ from the new CRM. |

## Field mapping

- Map phone to normalized E.164.
- Map email to lowercase.
- Map original row id to `external_id` where available.
- Map source thread id to a dedicated CRM field.
- Map consent evidence to a dedicated field, not to a free-text service note.
- Map attachments to metadata and storage links.

## Dry-run gates

Continue only when all gates pass:

- At least 95 percent of rows have phone, email, or external id.
- No unredacted payment-card numbers remain in notes.
- Opt-out phrases are detected and preserved.
- Duplicate candidate rate is below the manual-review threshold.
- Hebrew text remains readable in exported JSON.
- Audit JSONL is written for sample batches.

## Production migration

1. Freeze source exports.
2. Store a hash of each export file.
3. Run batches of 50 to 500 records depending on provider limits.
4. Save create responses.
5. Extract each created CRM id and write it to the migration ledger.
6. Use audit events for retry and rollback.
7. Review warning counts after every batch.
8. Stop on unexpected duplicate spikes or provider errors.

## Rollback

- Use the migration ledger to identify objects from the run.
- Remove or archive only objects from the faulty batch.
- Preserve audit logs and source hashes.
- Rotate credentials if the incident involved token exposure.
- Document root cause and repeat sandbox validation before retry.

## After migration

- Reconcile record counts by source and destination.
- Review a random sample of Hebrew records for correct names, dates, and ₪ amounts.
- Verify service notes do not contain unnecessary identity numbers or payment-card data.
- Confirm opt-out and marketing consent fields are correct.
- Transfer ownership of unresolved matches to a named operator.


## API version migration checks

- For HubSpot, migrate new contact-create calls to `/crm/objects/2026-03/contacts`; keep older numeric paths only during a tested cutover window.
- For Salesforce, test `/services/data/v67.0/sobjects/Lead` in sandbox before production and pin a lower version only when an org-specific package requires it.
- For Monday, keep GraphQL requests on `https://api.monday.com/v2` and preserve idempotency keys around retries.
