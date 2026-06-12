# Migration Checklist

Use when moving from manual WhatsApp, WhatsApp Web, spreadsheets, paper diaries, generic booking tools, or another WhatsApp provider.

## Phase 1: Inventory

- [ ] List services, durations, prices, deposits, cancellation rules, and preparation time.
- [ ] List staff, branches, rooms, equipment, and resources.
- [ ] Export current appointments.
- [ ] Export customer phone numbers only where a service relationship exists.
- [ ] Identify recurring appointments.
- [ ] Identify opt-outs.
- [ ] Identify sensitive services requiring neutral wording.
- [ ] Identify workflows that remain manual.

## Phase 2: Data Cleanup

- [ ] Normalize phones to E.164.
- [ ] Remove duplicate customers.
- [ ] Remove past appointments unless needed for history.
- [ ] Convert dates to timezone-aware ISO datetimes.
- [ ] Display dates as `DD/MM/YYYY`.
- [ ] Convert prices to `₪`.
- [ ] Remove unnecessary notes from reminders.
- [ ] Tag records requiring staff review.

## Phase 3: Templates

- [ ] Create appointment confirmation template in Hebrew.
- [ ] Create 24-hour reminder template in Hebrew.
- [ ] Create same-day reminder template in Hebrew.
- [ ] Create reschedule template in Hebrew.
- [ ] Create cancellation acknowledgement template in Hebrew.
- [ ] Create opt-out acknowledgement template in Hebrew.
- [ ] Submit templates with realistic examples.
- [ ] Confirm approval before production.

## Phase 4: Technical Migration

- [ ] Configure test sender.
- [ ] Configure production sender.
- [ ] Store access token in secrets manager.
- [ ] Configure HTTPS webhook.
- [ ] Implement webhook verification.
- [ ] Implement retries with backoff.
- [ ] Implement idempotency for incoming and outgoing messages.
- [ ] Connect calendar or database.
- [ ] Add staff escalation inbox.
- [ ] Add monitoring.

## Phase 5: Import Dry Run

- [ ] Import into staging.
- [ ] Validate counts.
- [ ] Validate Hebrew names.
- [ ] Validate price rendering.
- [ ] Validate Friday and Saturday rules.
- [ ] Validate reminder times.
- [ ] Validate recurring exceptions.
- [ ] Validate opt-outs.
- [ ] Run automated tests.
- [ ] Run test scenarios.

## Phase 6: Pilot

- [ ] Select a small customer group.
- [ ] Send confirmations after staff approval.
- [ ] Review replies and parsing.
- [ ] Check delivery status webhooks.
- [ ] Confirm escalations are visible.
- [ ] Measure no-shows and support load.
- [ ] Fix wording.
- [ ] Re-run regression tests.

## Phase 7: Cutover

- [ ] Freeze manual changes during migration.
- [ ] Export final appointment state.
- [ ] Import final state.
- [ ] Reconcile counts.
- [ ] Enable reminder worker.
- [ ] Monitor logs.
- [ ] Keep manual fallback.
- [ ] Review first full business day.

## Phase 8: Rollback

Rollback when reminders use wrong times, duplicate messages appear, calendar writes fail, staff cannot see escalations, provider account is restricted, or consent/privacy issues appear.

Steps:

1. Disable reminder worker.
2. Disable automatic webhook replies.
3. Keep inbound messages visible to staff.
4. Export current state.
5. Revert calendar ownership to previous process.
6. Notify staff of manual handling.
7. Repair data before re-enable.

## Source-Specific Notes

### From Manual WhatsApp

- [ ] Stop personal WhatsApp for new business reminders.
- [ ] Keep a human phone line.
- [ ] Avoid importing old chat history unless necessary.
- [ ] Train staff to use structured statuses.
- [ ] Add daily review until confidence is high.

### From Spreadsheet

- [ ] Lock columns and date formats.
- [ ] Reject rows without timezone.
- [ ] Reject invalid phones.
- [ ] Map each row to appointment ID.
- [ ] Keep original sheet read-only.
- [ ] Replace manual reminder columns with reminder records.

### From Generic Booking Tool

- [ ] Map service and staff IDs.
- [ ] Confirm webhook or polling support.
- [ ] Check cancellation representation.
- [ ] Check recurring exports.
- [ ] Disable duplicate native reminders where needed.
- [ ] Keep unstable booking URLs out of templates.

### From Another WhatsApp Provider

- [ ] Export template list where possible.
- [ ] Confirm template names may differ.
- [ ] Recreate provider-specific templates.
- [ ] Verify sender phone ownership.
- [ ] Compare webhook payloads.
- [ ] Test delivery status mappings.
- [ ] Rebuild opt-out list.
- [ ] Prevent both providers from sending during cutover.
