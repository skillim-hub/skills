# Migration Checklist

Use this checklist when moving from spreadsheets, POS exports, accounting item lists, e-commerce products, or supplier files into the structured catalog.

## Phase 1: Discovery

- [ ] Collect all catalog files.
- [ ] Identify source of truth.
- [ ] Identify duplicate spreadsheets.
- [ ] Identify POS/accounting/e-commerce exports.
- [ ] Identify supplier files.
- [ ] Identify internal-only fields.
- [ ] Identify public price-list fields.
- [ ] Separate services and physical products.
- [ ] Separate stock and non-stock items.
- [ ] Confirm business VAT status.
- [ ] Confirm whether source prices include VAT.

## Phase 2: Data profiling

- [ ] Count rows.
- [ ] Count active rows.
- [ ] Count inactive rows.
- [ ] Count missing SKUs.
- [ ] Count duplicate SKUs.
- [ ] Count duplicate barcodes.
- [ ] Count missing prices.
- [ ] Count missing VAT rates.
- [ ] Count negative prices.
- [ ] Count negative stock.
- [ ] Count corrupted Hebrew rows.
- [ ] Count formula cells.
- [ ] Count merged-cell artifacts.
- [ ] Count mixed decimal separators.
- [ ] Count categories and units.

## Phase 3: Field mapping

| Source | Target | Rule |
|---|---|---|
| Item Code | `sku` | Normalize uppercase; reject unsafe characters. |
| Hebrew Name | `name_he` | Trim spaces; preserve punctuation. |
| English Name | `name_en` | Optional. |
| Department | `category` | Map to approved list. |
| Unit | `unit` | Normalize to approved units. |
| Price | `price_before_vat` or `price_with_vat` | Decide meaning before import. |
| VAT | `vat_rate` | Convert `18%` or `18` to `0.18`. |
| Quantity | `stock_quantity` | Preserve decimals only when allowed. |
| Min Stock | `reorder_point` | Default zero only for non-stock items. |
| Barcode | `barcode` | Store as text. |
| Supplier Code | `supplier_sku` | Keep separate from internal SKU. |
| Status | `active` | Map discontinued to `false`. |

## Phase 4: Cleanup

- [ ] Back up originals.
- [ ] Save working files as UTF-8.
- [ ] Remove blank rows and columns.
- [ ] Remove visual headers inside data.
- [ ] Unmerge cells.
- [ ] Replace formulas with values.
- [ ] Trim spaces.
- [ ] Normalize SKUs.
- [ ] Generate draft SKUs for missing values.
- [ ] Split combined name/size/color.
- [ ] Normalize categories.
- [ ] Normalize units.
- [ ] Normalize VAT rates.
- [ ] Normalize money values.
- [ ] Review zero prices.
- [ ] Review negative stock.
- [ ] Review duplicate barcodes.
- [ ] Mark discontinued items inactive.

## Phase 5: Test import

- [ ] Import 5 representative products.
- [ ] Import 5 service items.
- [ ] Import one Hebrew-only item.
- [ ] Import one item with barcode.
- [ ] Import one item with supplier SKU.
- [ ] Import one zero-VAT item if relevant.
- [ ] Import one fractional quantity item if relevant.
- [ ] Export back to CSV.
- [ ] Compare input and output values.
- [ ] Open output in target spreadsheet app.
- [ ] Run automated tests.

## Phase 6: Validation

- [ ] All active SKUs unique.
- [ ] No required field missing.
- [ ] All prices are valid decimals.
- [ ] All VAT rates are valid decimals.
- [ ] Price including VAT matches expectation.
- [ ] No unintended inactive items exported.
- [ ] No supplier cost in public export.
- [ ] Stock quantities match opening count.
- [ ] Low-stock report works.
- [ ] Accounting import sample totals match.
- [ ] Hebrew readable.
- [ ] Backups exist.
- [ ] Migration log updated.

## Phase 7: Go-live

- [ ] Freeze legacy edits.
- [ ] Export final legacy backup.
- [ ] Import final cleaned catalog.
- [ ] Run validation suite.
- [ ] Publish public price list if needed.
- [ ] Connect POS/accounting/e-commerce systems.
- [ ] Confirm sample sale.
- [ ] Confirm sample stock purchase.
- [ ] Confirm sample invoice export.
- [ ] Train staff on SKU and stock rules.
- [ ] Record go-live date.

## Phase 8: Monitoring

Review daily for the first week:

- [ ] Duplicate SKUs.
- [ ] Negative stock.
- [ ] Failed imports.
- [ ] VAT mismatches.
- [ ] Corrupted Hebrew.
- [ ] Public export leaks.
- [ ] Wrong SKU sales.
- [ ] Missing supplier orders.
- [ ] Unexpected price changes.

Review monthly:

- [ ] Inactive items.
- [ ] Slow-moving stock.
- [ ] Reorder points.
- [ ] Supplier price changes.
- [ ] VAT settings.
- [ ] Backup restore test.
- [ ] User permissions.

## Rollback plan

1. Stop imports.
2. Export broken state for investigation.
3. Restore latest clean backup.
4. Reapply verified changes only.
5. Re-run validation.
6. Notify affected users.
7. Document root cause.
8. Add validation rule.

## Cutover message

```text
Catalog migration completed on 02/06/2026.
Use the new catalog file as the source of truth from this point forward.
Do not edit legacy spreadsheets.
Report missing SKUs, wrong prices, VAT issues, or stock differences before creating manual workarounds.
```

## Migration risks

| Risk | Impact | Mitigation |
|---|---|---|
| Duplicate SKUs | Wrong item sold or invoiced. | Validate uniqueness. |
| VAT mismatch | Wrong invoice amounts. | Test sample invoices. |
| Hebrew corruption | Unusable names. | Use UTF-8. |
| Supplier cost leak | Commercial exposure. | Use public export allowlist. |
| Stock mismatch | Bad reorder decisions. | Perform opening count. |
| Legacy edits continue | Data divergence. | Freeze old files. |
