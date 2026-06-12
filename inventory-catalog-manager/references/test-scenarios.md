# Test Scenarios

Run these scenarios before production use, migration, or integration.

## Scenario 1: Add standard VAT product
Setup: empty catalog. Action: add `COF-BNS-001`, price before VAT `42.37`, VAT `0.18`, stock `18`. Expected: price with VAT is `50.00`.

## Scenario 2: Add zero-rate item
Setup: empty catalog. Action: add `BOOK-EXP-001`, VAT `0`, price `100`. Expected: price with VAT is `100.00` and tax note exists.

## Scenario 3: Reject duplicate SKU
Setup: catalog contains `MUG-WHT-001`. Action: add same SKU again. Expected: operation fails.

## Scenario 4: Normalize lowercase SKU
Setup: empty catalog. Action: add `mug-wht-001`. Expected: stored as `MUG-WHT-001`.

## Scenario 5: Reject unsupported SKU characters
Setup: empty catalog. Action: add `ספל לבן/XL`. Expected: invalid SKU error.

## Scenario 6: Preserve supplier SKU
Setup: empty catalog. Action: add internal SKU and `SUP-9981`. Expected: both identifiers separate.

## Scenario 7: Export Hebrew CSV
Setup: Hebrew item names. Action: export CSV. Expected: Hebrew stays readable in UTF-8.

## Scenario 8: Import valid CSV
Setup: CSV contains required fields. Action: import. Expected: all rows imported.

## Scenario 9: Reject missing price
Setup: CSV row lacks `price_before_vat`. Action: import. Expected: validation error.

## Scenario 10: Convert final price to before-VAT
Setup: final price ₪100 including 18%. Action: calculate before-VAT. Expected: ₪84.75.

## Scenario 11: Purchase movement
Setup: item stock `5`. Action: movement `+10`. Expected: stock `15`.

## Scenario 12: Sale movement
Setup: item stock `15`. Action: movement `-3`. Expected: stock `12`.

## Scenario 13: Prevent silent stock edit
Setup: item stock `12`. Action: change to `9` without reason. Expected: process rejects or flags.

## Scenario 14: Count adjustment
Setup: system `12`, count `10`. Action: movement `-2` with reason `count_adjustment`. Expected: stock `10`.

## Scenario 15: Low-stock report
Setup: stock `3`, reorder point `5`. Action: run report. Expected: item appears.

## Scenario 16: Exclude inactive low stock
Setup: inactive item stock `0`, reorder point `5`. Action: run report. Expected: excluded by default.

## Scenario 17: Fractional stock for weight
Setup: unit `kg`. Action: stock `2.5`. Expected: accepted.

## Scenario 18: Strict review for fractional units
Setup: unit `unit`. Action: stock `2.5`. Expected: flagged under strict policy.

## Scenario 19: Retire item
Setup: active item with history. Action: set `active=false`. Expected: not in public exports; remains in catalog.

## Scenario 20: Do not reuse retired SKU
Setup: inactive `ACC-OLD-001`. Action: add different item with same SKU. Expected: rejected.

## Scenario 21: Barcode conflict
Setup: active item barcode `7290000000000`. Action: add another active item with same barcode. Expected: validation warning/error.

## Scenario 22: Consumer export excludes supplier cost
Setup: catalog includes supplier cost. Action: consumer export. Expected: no supplier cost or margin.

## Scenario 23: B2B export includes VAT rate
Setup: service item. Action: B2B export. Expected: before-VAT price, VAT rate, and final price.

## Scenario 24: VAT rate change
Setup: before-VAT price `100`; old VAT `0.17`, new `0.18`. Action: recalculate. Expected: `117.00` and `118.00`.

## Scenario 25: Preserve final consumer price
Setup: final price ₪100, VAT `0.18`. Action: calculate base price. Expected: ₪84.75.

## Scenario 26: Supplier new item
Setup: supplier row has no SKU/barcode match. Action: staging import. Expected: draft item, not active auto-create.

## Scenario 27: Service zero stock
Setup: `SRV-CONS-001`. Action: stock report. Expected: excluded from reorder.

## Scenario 28: CLI init and add
Setup: temp folder. Action: run `init`, then `add`. Expected: JSON catalog contains item.

## Scenario 29: Async save/load
Setup: catalog with one item. Action: async save and load. Expected: data preserved.

## Scenario 30: Backup before bulk import
Setup: existing catalog. Action: import workflow. Expected: backup exists before changes.

## Scenario 31: UTF-8 BOM export option
Setup: legacy Excel recipient. Action: export CSV with BOM. Expected: Hebrew opens correctly.

## Scenario 32: Zero stock product at reorder point
Setup: active product stock `0`, reorder `0`. Action: low-stock report. Expected: appears only if policy treats zero threshold as reorder signal.

## Scenario 33: Bundle component validation
Setup: bundle contains two components. Action: build bundle. Expected: component stock decreases according to bundle policy.

## Scenario 34: Invalid decimal separator
Setup: CSV contains `42,37`. Action: import. Expected: validation error or normalization decision.

## Scenario 35: Public export date format
Setup: approved catalog. Action: public export. Expected: date appears as `02/06/2026`.
