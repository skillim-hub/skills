# Migration Checklist

Use this checklist when replacing an FAQ bot, contact form, WhatsApp auto-reply, helpdesk macros, or manual support flow.

## Inventory

- [ ] Export FAQ pages.
- [ ] Export helpdesk macros.
- [ ] Export WhatsApp auto-replies.
- [ ] Export contact form fields.
- [ ] List top intents from last 90 days.
- [ ] Identify owners for operations, billing, accounting, privacy, accessibility, and technical support.

## Remove unsafe content

- [ ] Delete old prices.
- [ ] Delete expired holiday hours.
- [ ] Delete discontinued services.
- [ ] Remove legal claims not reviewed by counsel.
- [ ] Remove tax guidance not reviewed by accounting owner.
- [ ] Remove old refund promises.
- [ ] Remove requests for unnecessary sensitive data.

## Localize for Israel

- [ ] Convert prices to ₪.
- [ ] Convert dates to DD/MM/YYYY.
- [ ] Confirm VAT wording: כולל מע״מ, בתוספת מע״מ, or not applicable.
- [ ] Confirm business status: עוסק פטור, עוסק מורשה, חברה, עמותה, or other.
- [ ] Replace translated wording with natural Hebrew.
- [ ] Use gender-neutral phrasing where possible.
- [ ] Confirm phone and address formats.

## Map intents

- [ ] Map top questions to intents.
- [ ] Mark each answer as direct, clarify, lookup, or handoff.
- [ ] Mark refund, cancellation, warranty, privacy, payment dispute, legal, safety, and accessibility as handoff where needed.
- [ ] Add unknown-policy fallback.

## Configure integrations

- [ ] Order status.
- [ ] Shipping/tracking.
- [ ] Payment links.
- [ ] Invoice/receipt creation.
- [ ] Ticket/handoff.
- [ ] Booking calendar.
- [ ] Chat channel adapter.
- [ ] Secret storage.
- [ ] APtimeout and retry.

## Privacy and security

- [ ] Define allowed personal data per workflow.
- [ ] Block passwords, OTPs, full card numbers, and unnecessary ID scans.
- [ ] Redact logs.
- [ ] Define attachment retention.
- [ ] Define deletion/export workflow.
- [ ] Review permissions and audit logs.

## Hebrew QA

- [ ] Test slang and short messages.
- [ ] Test angry messages.
- [ ] Test mixed Hebrew-English.
- [ ] Test RTL punctuation.
- [ ] Test mobile rendering.
- [ ] Test gender-neutral language.
- [ ] Test ₪ and DD/MM/YYYY.

## Launch

- [ ] Run pytest.
- [ ] Run 20+ scenarios.
- [ ] Pilot low-risk FAQ first.
- [ ] Monitor all handoffs for first two weeks.
- [ ] Add missing FAQ daily during pilot.
- [ ] Confirm rollback plan.

## Rollback plan

1. Disable Areplies for risky intents.
2. Keep phone/contact form visible.
3. Route conversations to human queue.
4. Preserve logs according to retention policy.
5. Restore previous approved FAQ if needed.
6. Add incident regression tests.
