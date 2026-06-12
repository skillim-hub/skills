# Migration Checklist

Use this checklist when moving from an older wedding-only package, an ad hoc spreadsheet, a WhatsApp list, or a folder of vendor PDFs into the enhanced event scheduler.

## Migration goals

- Preserve useful planning data.
- Remove branding, unused visual assets, unused templates, and outdated assumptions.
- Expand from wedding-only planning to lifecycle and small-business events.
- Normalize dates to `DD/MM/YYYY` for Israeli-facing documents.
- Normalize money to `₪` and store numeric values separately from display values.
- Replace free-text RSVP values with controlled statuses.
- Reduce privacy exposure.

## Source inventory

| Source | Examples | Action |
|---|---|---|
| Old skill docs | wedding guide, rabbinate checklist | Keep useful operational content; remove branding/identity metadata |
| Spreadsheet | guest list, budget, seating | Normalize columns and statuses |
| WhatsApp messages | RSVP replies, logistics | Extract final answers only; avoid storing full chat history |
| Vendor PDFs | quote, contract, invoice | Store final signed/accepted version |
| Calendar | meetings, payment dates | Convert to event milestones |
| Email | supplier confirmations | Store key terms and contact details |
| Forms | RSVP forms | Check consent, privacy, and opt-out language |

## Field mapping

| Old field | New field | Notes |
|---|---|---|
| Name | `contact_name` or `household_name` | Separate household and contact person |
| Phone | `phone` | Normalize to `+972...` where possible |
| Coming? | `status` | Map to `confirmed`, `declined`, `tentative`, `no_response` |
| Number | `party_size_confirmed` | Keep invited count separately |
| Invited | `party_size_invited` | Do not overwrite confirmed count |
| Side | `group` | Use for seating and reports |
| Notes | `notes` | Remove sensitive or irrelevant details |
| Food | `dietary` | Store specific operational needs only |
| Bus | `needs_transport` | Build transport manifest |
| Table | `table_number` | Recalculate after deduplication |

## RSVP status mapping

| Legacy text | New status |
|---|---|
| כן | `confirmed` |
| מגיעים | `confirmed` |
| אישר | `confirmed` |
| לא | `declined` |
| לא מגיעים | `declined` |
| אולי | `tentative` |
| נראה | `tentative` |
| אין תשובה | `no_response` |
| לא ענו | `no_response` |

## Cleanup steps

1. Create a backup of the original source files.
2. Remove unused visual assets and unrelated distribution text.
3. Remove metadata fields that identify people or organizations.
4. Convert date columns to `DD/MM/YYYY`.
5. Convert currency display to `₪` while keeping numeric fields as numbers.
6. Normalize phone numbers.
7. Deduplicate by normalized phone and household name.
8. Split household count into invited and confirmed.
9. Move sensitive family notes to restricted planner notes or delete them.
10. Add language, dietary, accessibility, and transport fields.
11. Add event type and lifecycle-specific timeline.
12. Add compliance checkpoints for privacy, messaging, accessibility, licensing, and tax documentation.
13. Run the test scenarios in `references/test-scenarios.md`.
14. Run `pytest scripts`.
15. Archive the migrated package.

## Validation checklist

- [ ] No identity field exists in `metadata.json`.
- [ ] No visual assets or image references exist.
- [ ] Hebrew copy uses natural terminology and `₪`.
- [ ] Dates in Hebrew-facing examples use `DD/MM/YYYY`.
- [ ] Guest records have stable IDs.
- [ ] RSVP statuses are controlled values.
- [ ] Duplicate phones are resolved.
- [ ] Dietary/accessibility notes are minimized.
- [ ] Venue capacity and minimum guest count are both stored.
- [ ] Supplier quotes include VAT status and invoice allocation-number follow-up where relevant.
- [ ] Tests pass.


## 2026 web-validated migration additions

- Add invoice date and amount-before-VAT columns to supplier-payment sheets.
- Add an `allocation_number` column for supplier/customer invoices that cross current Tax Authority thresholds.
- Replace old 2026 threshold assumptions with ₪10,000 before VAT through 31/05/2026 and ₪5,000 before VAT from 01/06/2026.
- Add an ACUM license checkpoint with separate family-event and business-event paths.
- Add a venue due-diligence field for noise monitor, closing hour, accessibility proof, kashrut certificate scope and business-license status.
