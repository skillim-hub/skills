# Troubleshooting

## Installation

### CLI command is not found

Cause: package not installed in editable mode or shell path not refreshed.

Fix:

```bash
pip install -e .
hash -r
meal-grocery-planner stores --env sandbox
```

### Tests cannot import the package

Cause: running tests from outside the package root without installation.

Fix:

```bash
cd meal-grocery-planner
pip install -e .
pytest -q
```

### Async tests fail

Cause: missing development dependency.

Fix:

```bash
pip install -r requirements-dev.txt
```

## Product matching

### Search returns no product

Cause: the query includes a brand, package size, plural form, or typo.

Fix:

- Search a generic item name such as `עגבניה`, `חלב`, or `פסטה`.
- Try the same query without store filtering.
- Import a fresh price feed when using branch-specific prices.

### Product match is technically valid but not suitable

Cause: generic matching cannot detect all cooking, kashrut, or brand preferences.

Fix:

- Review the `matched_item` field.
- Check `substitutions`.
- Replace the line manually before checkout.

### Allergy filter removes all options

Cause: all matching catalog entries contain an excluded allergen.

Fix:

- Keep the line unmatched.
- Select a safe product manually.
- Verify product labeling before purchase.

## Pricing

### Estimate differs from final cart

Cause: delivery area, branch, promotions, package size, deposit, substitutions, or stale prices.

Fix:

1. Compare package size.
2. Compare unit price.
3. Check promotion conditions.
4. Check live delivery fee and minimum order.
5. Treat cart price as authoritative for purchase approval.

### Basket total is lower than expected

Cause: missing matches or pantry items removed too broadly.

Fix:

- Inspect lines where `matched_item` is null.
- Confirm pantry list includes only items truly available.
- Rebuild the basket after removing uncertain pantry entries.

### Live delivery fee changes the best store

Cause: a cheaper item subtotal can lose after delivery fee.

Fix:

- Run `compare_basket(..., include_delivery=True)`.
- Prefer one store when split orders create duplicate delivery charges.

## CLI and JSON

### Hebrew appears escaped

Cause: JSON was printed with ASCII escaping.

Fix:

```python
json.dumps(data, ensure_ascii=False, indent=2)
```

### Saved order cannot be found

Cause: a different order directory is used.

Fix:

```bash
export MEAL_GROCERY_ORDER_DIR=.meal_grocery_planner_orders
meal-grocery-planner show-order "$order_id" --env sandbox
```

## Data import

### CSV file imports with broken Hebrew

Cause: source file encoding is not UTF-8 or UTF-8 with BOM.

Fix:

- Save the CSV as UTF-8.
- Use spreadsheet export settings that preserve Hebrew.
- Reopen and inspect the first product name.

### Negative price error

Cause: feed contains a refund row, malformed value, or separator issue.

Fix:

- Remove non-product rows.
- Convert decimal separators to period format.
- Validate `price_ils` before import.

## Production safety

Do not automate payment submission with this package. Keep a manual approval step for final cart contents, price, delivery window, allergens, kashrut, and business record requirements.
