# Migration Checklist

Use this checklist when replacing an older expense spreadsheet, prior skill package, or ad-hoc accountant workflow with Expense Manager.

## 1. Inventory current sources

- List every source file: bank CSV, credit-card CSV, invoice export, receipt folder, spreadsheet workbook, and manual notes.
- Identify date format, currency, and encoding for each file.
- Record which files contain income rows that must be excluded.
- Confirm whether invoice PDFs are stored separately.

## 2. Map old columns to normalized fields

| Old field | New field | Notes |
|---|---|---|
| Transaction date | `date` | Prefer `DD/MM/YYYY` |
| Supplier/payee | `vendor` | Keep original spelling |
| Charge/debit | `amount` | Use gross amount; remove currency symbols only if parser fails |
| Details/memo | `description` | Add business-purpose keywords |
| Invoice number | `receipt_number` | Required for review quality |
| Document type | `document_type` | Use `tax_invoice`, `receipt`, `credit_note`, or local wording |
| Currency | `currency` | Use `ILS`, `USD`, `EUR`, etc. |
| FX rate | `fx_rate_to_ils` | Required for non-ILS |

## 3. Remove unsafe assumptions

- Remove old formulas that deduct restaurant meals with Israeli clients.
- Remove VAT recovery for Osek Patur files.
- Remove automatic 100% treatment for vehicle and phone costs.
- Remove immediate expensing for high-value equipment.
- Remove manual edits from bank-export source files.

## 4. Configure entity defaults

- Osek Patur: `--entity-type osek_patur`.
- Osek Murshe: `--entity-type osek_murshe`.
- Company: `--entity-type company`.
- Consumer tracking: `--entity-type private_consumer`.
- Home office: add `--home-office-percent <documented percent>`.

## 5. Run parallel comparison

1. Classify the same month with the old method and this helper.
2. Compare totals by category.
3. Investigate every difference above a materiality threshold.
4. Confirm treatment with the accountant.
5. Update internal documentation.

## 6. Migrate recurring rules

- Add vendor names to descriptions when source descriptions are vague.
- Keep custom mapping notes outside the generated client unless tests are added.
- Add a test for every custom rule.
- Document why the rule exists and which regulation or accountant instruction supports it.

## 7. Validate exports

- Generate a package ZIP.
- Open `expense-classification.csv` in a spreadsheet tool with UTF-8.
- Confirm row count and totals.
- Check `accountant-summary.json`.
- Validate `sha256-manifest.txt` after delivery.
- Import to a test company/file before production posting.

## 8. Cutover controls

- Freeze the old spreadsheet after cutover.
- Keep the old file read-only for audit trail.
- Store generated ZIP packages by fiscal period.
- Retain source invoices with the package or in the linked document store.
- Review rules at least annually for indexed caps and Tax Authority updates.

## 9. Rollback plan

- Keep the normalized input CSV used for each run.
- Keep old output files until accountant acceptance.
- Regenerate packages from source rather than editing generated files.
- If a serious mapping issue is found, fix the input/rule, rerun tests, and create a new package version.
