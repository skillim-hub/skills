# Workflow Guide

This guide gives end-to-end workflows for Israeli catalog, price, VAT, and stock operations.

## Workflow 1: Create a new catalog

Inputs: item list, service list, current prices, VAT treatment, opening stock count, suppliers, category list, unit list.

Steps:

1. Define SKU rules.
2. Define required fields.
3. Create a blank JSON or CSV catalog.
4. Add service items first; set stock to zero.
5. Add physical products with opening stock.
6. Add reorder points.
7. Calculate VAT-inclusive prices.
8. Review consumer and B2B displays separately.
9. Export a backup.
10. Run test scenarios.

CLI:

```bash
python scripts/inventory-catalog-manager-cli.py init catalog.json
CREATE_RESPONSE=$(python scripts/inventory-catalog-manager-cli.py create-item catalog.json --sku COF-BNS-001 --name "פולי קפה 1 ק״ג" --category coffee --unit kg --price-before-vat 42.37 --vat-rate 0.18 --stock 18 --reorder-point 5)
ITEM_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")
python scripts/inventory-catalog-manager-cli.py create-item catalog.json --sku SRV-CONS-001 --name "פגישת ייעוץ" --category services --unit hour --price-before-vat 350 --vat-rate 0.18 --stock 0 --reorder-point 0
```

Acceptance criteria:

- All SKUs unique.
- All active items have unit, price, and VAT rate.
- Stock items have reorder points.
- Consumer export uses final ₪ price.
- Hebrew opens correctly in target tools.

## Workflow 2: Import a supplier price list

Inputs: supplier CSV, master catalog, mapping between supplier SKU and internal SKU, cost policy.

Steps:

1. Save supplier file as UTF-8.
2. Rename source columns to staging names.
3. Validate supplier SKU and barcode.
4. Match rows to existing SKUs.
5. Flag unknown rows for review.
6. Update supplier cost fields only after approval.
7. Do not automatically update selling prices.
8. Create new internal SKUs for new items.
9. Export a change report.
10. Back up catalog.

Staging example:

```csv
supplier_sku,barcode,name_he,cost_ils,suggested_price_with_vat
SUP-9981,7290000000000,ספל לבן,11.50,25.00
SUP-4412,7290000000001,כוס אספרסו,7.20,18.00
```

Matching rules:

| Condition | Action |
|---|---|
| Barcode and supplier SKU match one item | Update approved supplier fields. |
| Barcode matches but supplier SKU changed | Flag for review. |
| Supplier SKU matches but name changed | Flag for review. |
| No match | Create draft SKU; require approval. |

## Workflow 3: Publish a consumer price list

Inputs: approved catalog, effective date, consumer template.

Steps:

1. Filter `active=true`.
2. Exclude internal supplier and cost fields.
3. Use `price_with_vat`.
4. Show currency as `₪` or `ILS`.
5. Add update date as `DD/MM/YYYY`.
6. Include unit and relevant limitations.
7. Review Hebrew names.
8. Store a dated copy.

Example:

```csv
sku,name_he,unit,price_with_vat,currency,updated_at,notes
COF-BNS-001,פולי קפה 1 ק״ג,kg,50.00,ILS,02/06/2026,מחיר כולל מע״מ
MUG-WHT-001,ספל לבן,unit,25.00,ILS,02/06/2026,מחיר כולל מע״מ
```

Checks:

- No supplier cost.
- No margin columns.
- No inactive items.
- Date and currency visible.
- Final price clear.

## Workflow 4: Publish a B2B price list

Inputs: approved catalog, business audience, VAT treatment, commercial terms.

Steps:

1. Filter active items.
2. Include `price_before_vat`.
3. Include `vat_rate`.
4. Include `price_with_vat` for convenience.
5. Add payment terms outside item rows.
6. Add effective date.
7. Keep customer-specific discounts separate unless approved.

Example:

```csv
sku,name_he,unit,price_before_vat,vat_rate,price_with_vat,currency,updated_at
SRV-CONS-001,פגישת ייעוץ,hour,350.00,0.18,413.00,ILS,02/06/2026
```

## Workflow 5: Run a low-stock report

Inputs: current catalog, reorder points, pending orders.

Steps:

1. Load catalog.
2. Filter stock items.
3. Select `stock_quantity <= reorder_point`.
4. Exclude inactive items.
5. Sort by supplier and category.
6. Confirm pending orders.
7. Place supplier orders.
8. Record purchases when received.

CLI:

```bash
python scripts/inventory-catalog-manager-cli.py low-stock catalog.json
```

Suggested reorder output:

```csv
sku,name_he,supplier_name,stock_quantity,reorder_point,suggested_order_quantity
MUG-WHT-001,ספל לבן,Ceramics Supplier,6,8,12
```

## Workflow 6: Reconcile a physical stock count

Inputs: count sheet, current catalog, movement history, damage/expiry notes.

Steps:

1. Freeze imports temporarily.
2. Count physical stock by SKU.
3. Compare counted quantity to system quantity.
4. Investigate large differences.
5. Create movements for known causes.
6. Use `count_adjustment` for unexplained differences.
7. Resume imports.
8. Run low-stock report.
9. Archive count sheet.

CLI:

```bash
python scripts/inventory-catalog-manager-cli.py stock-adjust catalog.json COF-BNS-001 -2 --reason count_adjustment --reference COUNT-02/06/2026 --note "Physical count found 16 instead of 18"
```

## Workflow 7: Add a service item

Steps:

1. Use `SRV-` prefix.
2. Set unit to `hour`, `session`, `project`, or `month`.
3. Set stock to `0`.
4. Set reorder point to `0`.
5. Confirm VAT treatment.
6. Add clear Hebrew invoice description.
7. Add optional English description.
8. Add scope notes.

Example:

```bash
python scripts/inventory-catalog-manager-cli.py add catalog.json SRV-TRAIN-001 "הדרכה לצוות" --category services --unit session --price-before-vat 950 --vat-rate 0.18 --stock 0 --reorder-point 0 --note "עד 12 משתתפים, עד שעתיים"
```

## Workflow 8: Prepare for VAT rate change

Steps:

1. Confirm official effective date.
2. Export backup.
3. Identify active taxable items.
4. Choose policy:
   - Preserve final consumer price.
   - Preserve before-VAT price.
5. Recalculate affected prices.
6. Preserve historical quotes and invoices.
7. Update default VAT configuration.
8. Run old-rate and new-rate tests.
9. Publish revised price lists with effective date.
10. Communicate internally.

## Workflow 9: Export to accounting software

Steps:

1. Confirm target import fields.
2. Map internal fields to target columns.
3. Use `invoice_description` when item names are too long.
4. Export price before VAT and VAT rate when target calculates VAT.
5. Export final price only when target expects final price.
6. Run a test import.
7. Compare sample invoice totals.
8. Save the mapping.

Mapping:

| Catalog | Accounting |
|---|---|
| `sku` | `item_code` |
| `name_he` | `description` |
| `unit` | `unit` |
| `price_before_vat` | `unit_price` |
| `vat_rate` | `vat_percent` |
| `active` | `is_active` |

## Workflow 10: Retire an item

Steps:

1. Confirm no open order depends on the item.
2. Set `active=false`.
3. Keep SKU unchanged.
4. Keep historical price and VAT fields.
5. Remove from public price lists.
6. Keep available for document history.
7. Add retirement note and date.

Do not delete, reuse SKU, or change historical invoices.

## Workflow 11: Build a bundle or kit

Steps:

1. Create bundle SKU.
2. List component SKUs and quantities.
3. Decide when component stock is reduced: assembly or sale.
4. Set bundle price and VAT rate.
5. Validate VAT treatment.
6. Test stock movements.

Bundle table:

```csv
bundle_sku,component_sku,component_quantity
KIT-GFT-001,COF-BNS-001,1
KIT-GFT-001,MUG-WHT-001,2
```

## Workflow 12: Clean a messy spreadsheet

Steps:

1. Back up original.
2. Remove empty rows and columns.
3. Split combined fields.
4. Normalize VAT values.
5. Normalize money values.
6. Generate draft SKUs where missing.
7. Detect duplicates.
8. Resolve manually.
9. Import structured catalog.
10. Run tests.

## Completion checklist

- [ ] Source data backed up.
- [ ] Required fields validated.
- [ ] SKU uniqueness checked.
- [ ] VAT treatment reviewed.
- [ ] Price rounding checked.
- [ ] Hebrew encoding checked.
- [ ] Stock movements recorded.
- [ ] Public exports sanitized.
- [ ] Low-stock report generated.
- [ ] Migration notes archived.
