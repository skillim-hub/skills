# Migration Checklist

Use this checklist when moving from an older Hebrew chatbot, spreadsheet-based sales script, manual WhatsApp replies, or generic bot platform into this skill.

## Inventory

- [ ] Export all products and services.
- [ ] Assign a stable SKU to every item.
- [ ] Map Hebrew product names.
- [ ] Map categories and tags.
- [ ] Add current price in ILS.
- [ ] Add VAT policy.
- [ ] Add stock source.
- [ ] Add allowed installment count.
- [ ] Add warranty months where relevant.
- [ ] Add approved cross-sell SKUs.
- [ ] Add approved upsell SKU.
- [ ] Remove discontinued items.
- [ ] Mark products requiring age or eligibility checks.

## Conversation migration

- [ ] Collect top 50 real customer questions.
- [ ] Group by intent: price, fit, shipping, warranty, cancellation, payment, invoice, complaint.
- [ ] Replace old generic replies with local Hebrew templates.
- [ ] Remove pressure tactics.
- [ ] Remove claims that cannot be substantiated.
- [ ] Add opt-out response.
- [ ] Add sensitive data warning.
- [ ] Add handoff response.
- [ ] Add quote validity date.
- [ ] Add secure payment link wording.

## Consent and compliance

- [ ] Import existing consent only when source and wording are documented.
- [ ] Treat unknown consent as not granted.
- [ ] Map opt-out list.
- [ ] Block promotional sends to revoked contacts.
- [ ] Add privacy notice link or text.
- [ ] Add retention policy for chat logs.
- [ ] Confirm support path for accessibility needs.
- [ ] Confirm cancellation and return wording.
- [ ] Confirm invoice workflow with bookkeeping.

## Technical migration

- [ ] Place catalog JSON under source control or controlled storage.
- [ ] Validate catalog using CLI.
- [ ] Add tests for top 20 customer messages.
- [ ] Configure webhook adapter.
- [ ] Configure payment link provider.
- [ ] Configure accounting adapter.
- [ ] Configure shipping adapter.
- [ ] Configure CRM handoff queue.
- [ ] Add monitoring for provider errors.
- [ ] Add rollback to previous catalog version.
- [ ] Add audit log with `quote_id`.

## Acceptance criteria

- [ ] 20+ test scenarios pass.
- [ ] Hebrew review completed by native speaker familiar with Israeli sales/service phrasing.
- [ ] Consumer price includes ₪ and VAT wording.
- [ ] Installment wording includes total.
- [ ] No card data is collected in chat.
- [ ] Complaint and cancellation routes do not sell.
- [ ] Opt-out works immediately.
- [ ] Human support receives useful context.
- [ ] Accounting flow can issue correct documents.
- [ ] Deployment owner can roll back within minutes.

## Migration risk table

| Risk | Impact | Mitigation |
|---|---|---|
| Old consent data is incomplete | Illegal or unwanted marketing | Treat as no consent until refreshed |
| Prices copied without VAT context | Misleading price display | Add explicit VAT field and review |
| Too many products mapped to same tag | Wrong recommendation | Add specific Hebrew tags |
| Manual discounts not encoded | Bot promises unavailable discount | Keep discounts in controlled policy |
| Payment provider allows fewer installments | Failed checkout | Cap by provider and product |
| Old chatbot kept selling during complaints | Customer escalation | Force handoff for complaint terms |
| Staff ignores quote ID | Harder support | Include quote ID in CRM task |


## Web-validated production migration

- Review `references/verification-log.md` before deployment.
- Replace hardcoded invoice-allocation thresholds with the Tax Authority `MinimumAmount` service.
- Confirm VAT configuration remains `18%` before each tax-year release.
- Re-test Bank of Israel SDMX requests after changing currency conversions.
- Re-approve WhatsApp templates after changing promotional text or opt-in wording.
