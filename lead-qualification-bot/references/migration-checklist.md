# Migration Checklist

Use this checklist when moving from manual WhatsApp replies, spreadsheets, website forms, legacy bots, or CRM-only workflows.

## Inventory

- [ ] List inbound channels.
- [ ] Review recent lead conversations where permitted.
- [ ] Identify top intents, cities, service areas, and disqualifiers.
- [ ] Identify current response times and owners.
- [ ] Identify current CRM/spreadsheet fields.
- [ ] Identify current privacy, service, and marketing consent text.
- [ ] Identify retention and deletion practices.

## Data mapping

| Current field | New field | Notes |
|---|---|---|
| phone | customer.phone_e164 | Normalize to +972 |
| name | customer.full_name | Optional until intent is real |
| city | customer.city | Add aliases |
| inquiry | description | Keep concise |
| service | service_category | Controlled vocabulary |
| source | channel/source | WhatsApp, form, referral, ad |
| budget | budget_ils | Numeric min/max |
| status | qualification.tier | Map carefully |
| owner | routing.owner | Define fallback |
| consent | consent.* | Split service and marketing |

## Copy migration

- [ ] Replace long forms with one-question messages.
- [ ] Add short privacy notice.
- [ ] Add separate marketing opt-in.
- [ ] Add opt-out text.
- [ ] Add sensitive handoff text.
- [ ] Add after-hours text.
- [ ] Add out-of-area text.
- [ ] Remove brand references, images, and promotional distribution text.

## Technical migration

- [ ] Create webhook endpoint.
- [ ] Validate source signatures.
- [ ] Normalize inbound messages.
- [ ] Store session state.
- [ ] Add idempotency by message ID.
- [ ] Add retry queue.
- [ ] Add CRM/CSV export.
- [ ] Add monitoring and alerts.
- [ ] Run pytest suite.

## Pilot

- [ ] Start with one service category.
- [ ] Run during business hours first.
- [ ] Human-review all hot leads.
- [ ] Review transcripts daily.
- [ ] Track drop-off, callbacks, conversions, opt-outs, and complaints.
- [ ] Tune scoring before expansion.

## Cutover

- [ ] Freeze old flow.
- [ ] Import suppression list.
- [ ] Confirm owners are active.
- [ ] Confirm fallback phone.
- [ ] Confirm approved templates.
- [ ] Confirm CRM mapping.
- [ ] Activate bot and monitor first 24 hours.

## Rollback

Disable outbound automation, keep safe inbound capture, route all leads to humans, export queued leads, fix issue in staging, rerun test scenarios, and reactivate gradually.
