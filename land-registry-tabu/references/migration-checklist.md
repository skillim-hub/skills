# Migration Checklist

Use this checklist when replacing manual Tabu checks, spreadsheets, email threads, or one-off scripts with the structured package.

## 1. Inventory current process

- List every source used today: official portal, PDFs, spreadsheets, email attachments, lawyer notes, municipality documents, Israel Land Authority records, and housing company letters.
- Identify who retrieves extracts.
- Identify who pays fees.
- Identify where files are stored.
- Identify who can view personal data.
- Identify how often extracts are refreshed.
- Identify how risk flags are currently communicated.

## 2. Define target workflow

Choose one or more workflows:

- Consumer purchase check.
- Business premises lease check.
- Collateral review.
- Inheritance or family transfer.
- Address-to-parcel triage.
- Mortgage release monitoring.
- Professional review pack generation.
- Order and payment chain.

For each workflow define:

- Required inputs.
- Allowed data sources.
- Output template.
- Legal-review trigger list.
- Retention period.
- Approval owner.

## 3. Configure data access

- Select an approved gateway.
- Confirm authentication method.
- Confirm payment and order flow.
- Confirm rate limits.
- Confirm allowed use.
- Configure `base_url`.
- Store API credentials in environment variables or a secrets manager.
- Keep endpoint and fee mappings configurable.

## 4. Migrate identifiers

Normalize historical identifiers:

| Legacy input | Target field |
|---|---|
| `גוש` | `block` |
| `חלקה` | `parcel` |
| `תת חלקה` or `תת-חלקה` | `subparcel` |
| `כתובת` | address fields |
| `מספר שטר` | deed reference |
| `בעלים` | right holder |

Reject records that cannot be matched to a reliable property identifier.

## 5. Migrate documents

For each legacy extract:

- Store raw file securely.
- Record retrieval date.
- Record property identifier.
- Record source.
- Extract owners, shares, and encumbrances.
- Mask IDs in summaries.
- Mark stale extracts.
- Link supporting documents.

## 6. Replace spreadsheets

Replace free-text columns with structured fields:

- `block`
- `parcel`
- `subparcel`
- `address`
- `retrieved_at`
- `right_holder`
- `right_type`
- `share`
- `encumbrance_type`
- `beneficiary`
- `amount_ils`
- `registered_date`
- `risk_flag`
- `next_action`

## 7. Add validation gates

Before allowing a report to be marked complete, require:

- Valid property identifier.
- Raw response retained.
- Rights parsed or explicit no-record status.
- Encumbrances parsed or explicitly unavailable.
- ID masking confirmed.
- Freshness check.
- Legal-review flags checked.

## 8. Build test coverage

Add anonymized test fixtures for:

- No encumbrance.
- Mortgage.
- Caveat.
- Attachment.
- Easement.
- Hebrew keys.
- Address ambiguity.
- No record.
- Company owner.
- Missing subparcel.
- Old extract.
- Async lookup.
- CLI mock mode.
- Create-order chain.
- Installable import.

## 9. Train users

Train operators to avoid:

- Treating address lookup as definitive.
- Treating old extracts as current.
- Ignoring subparcel mismatches.
- Sending full IDs in reports.
- Making legal conclusions.
- Blindly retrying paid orders.

## 10. Cutover plan

1. Run the structured workflow in parallel with the current process.
2. Compare outputs on at least 20 anonymized cases.
3. Fix field mappings and report language.
4. Confirm privacy and retention controls.
5. Freeze the old spreadsheet template.
6. Move new checks into the CLI/client workflow.
7. Keep a manual escalation path.
8. Review changes after the first month.

## 11. Rollback plan

Rollback is required if:

- Official access fails.
- Payment flow cannot be reconciled.
- Parsing drops encumbrances.
- Reports expose full IDs.
- Operators cannot identify ambiguous address results.
- Legal-review triggers are missed.

Rollback steps:

1. Stop automated retrieval.
2. Continue manual official extract retrieval.
3. Preserve all raw outputs created during the incident.
4. Identify affected cases.
5. Re-issue summaries after correction.
