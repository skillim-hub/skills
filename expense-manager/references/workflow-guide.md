# Workflow Guide

Use these workflows to process expenses from raw files to accountant-ready ZIP packages.

## Workflow 1: Monthly Osek Murshe VAT review

Goal: classify monthly expenses, estimate input VAT, and deliver a review file before VAT reporting.

1. Export bank and credit-card expenses to CSV.
2. Create one normalized file with columns: `date`, `vendor`, `amount`, `description`, `receipt_number`, `document_type`.
3. Add `fx_rate_to_ils` for non-ILS transactions.
4. Run:

```bash
python scripts/expense-manager-cli.py package january.csv ./out --package-name 2026-01-osek-murshe --entity-type osek_murshe
```

5. Open `exports/expense-classification.csv`.
6. Filter `review_flags` for blockers.
7. Attach missing invoices.
8. Confirm VAT treatment for foreign SaaS and vehicle rows.
9. Send the ZIP and source invoices to the accountant.

Acceptance criteria:

- No `uncategorized` blockers remain.
- Total gross amount reconciles to statements.
- Every VAT claim has a valid tax invoice.

## Workflow 2: Osek Patur annual expense cleanup

Goal: prepare deductible expense totals without input VAT recovery.

1. Export all annual expenses.
2. Remove income rows, owner draws, transfers, and loans.
3. Run:

```bash
python scripts/expense-manager-cli.py classify annual.csv annual-classified.csv --entity-type osek_patur
```

4. Confirm that `reclaimable_vat_ils` is always `0.00`.
5. Filter categories `personal`, `fines_penalties`, and `domestic_hospitality`.
6. Split mixed purchases.
7. Package the final version:

```bash
python scripts/expense-manager-cli.py package annual-clean.csv ./out --package-name 2026-annual-osek-patur --entity-type osek_patur
```

Acceptance criteria:

- VAT recovery total equals ₪0.00.
- Personal expenses remain excluded from deductible totals.
- Missing invoices are listed for accountant review.

## Workflow 3: Home-office allocation

Goal: apply a documented home-office percentage to rent, arnona, electricity, internet, and maintenance.

1. Calculate dedicated office area divided by total home area.
2. Save the calculation as a PDF or note for the accountant.
3. Mark relevant rows with descriptions containing `home office` or `משרד ביתי`.
4. Run:

```bash
python scripts/expense-manager-cli.py package home-office.csv ./out --package-name 2026-home-office --entity-type osek_murshe --home-office-percent 12.5
```

5. Review every row in category `home_office`.
6. Remove any household costs that are not connected to the dedicated workspace.

Acceptance criteria:

- `deductible_rate` equals the documented percentage.
- No home-office row has `missing_home_office_percent`.
- The area calculation is retained with source documents.

## Workflow 4: Vehicle expense review

Goal: isolate vehicle expenses and make the VAT/income-tax assumptions visible.

1. Tag fuel, garage, insurance, parking, tolls, and vehicle licensing rows.
2. Run classification using the default vehicle VAT rate or a documented alternative:

```bash
python scripts/expense-manager-cli.py classify vehicle.csv vehicle-classified.csv --entity-type osek_murshe
```

3. Filter category `vehicle`.
4. Verify whether the vehicle is private, commercial, or special-purpose.
5. Attach invoices and mileage/use evidence when the amount is material.
6. Let the accountant adjust VAT rate if the actual usage pattern differs.

Acceptance criteria:

- All material vehicle rows are visible in one category.
- No purchase of a vehicle is treated as a normal running expense without review.
- VAT recovery is confirmed before filing.

## Workflow 5: Software and foreign supplier charges

Goal: distinguish Israeli VAT invoices from foreign service charges.

1. Export credit-card rows for SaaS vendors.
2. Add descriptions such as `software`, `hosting`, `cloud`, or `SaaS`.
3. Add invoice numbers when available.
4. Run classification.
5. For each foreign vendor, confirm whether an Israeli tax invoice exists.
6. If no Israeli VAT invoice exists, set VAT recovery to zero in the accountant review notes.

Acceptance criteria:

- Software category is complete.
- Foreign VAT treatment is not assumed from card charge alone.
- Business-only use is documented.

## Workflow 6: Accountant import mapping

Goal: produce a stable file for import into bookkeeping software.

1. Confirm the target import template with the accountant.
2. Generate the package.
3. Open `exports/import-mapping.json`.
4. Map `account_code`, `date`, `vendor`, `amount_ils`, `reclaimable_vat_ils`, and `receipt_number` to the target fields.
5. Import into a test company or staging file first when available.
6. Compare totals after import.

Acceptance criteria:

- Imported row count equals CSV row count minus intentionally excluded rows.
- Gross, VAT, and deductible totals match the summary.
- Review-flagged rows are not posted without confirmation.

## Workflow 7: Consumer budgeting mode

Goal: classify personal spending without tax treatment.

1. Export spending CSV.
2. Run:

```bash
python scripts/expense-manager-cli.py classify household.csv household-classified.csv --entity-type private_consumer
```

3. Use `category` and `hebrew_category` for budgeting.
4. Ignore tax and VAT totals because they are forced to zero.

Acceptance criteria:

- `deductible_amount_ils` equals ₪0.00 for every row.
- `reclaimable_vat_ils` equals ₪0.00 for every row.
- Categories are useful for household review.
