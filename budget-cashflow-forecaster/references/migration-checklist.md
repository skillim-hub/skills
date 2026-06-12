# Migration Checklist

Use this checklist when migrating from an older package version, spreadsheet, notebook, or manual forecast.

---

## Package migration

- Remove promotional wording and distribution callouts.
- Remove visual marks, status marks, visual headers, and image references.
- Remove creator metadata from `metadata.json`.
- Use the included MIT license text exactly in `LICENSE`.
- Confirm neutral, imperative wording.
- Confirm the current file structure:
  - `SKILL.md`
  - `SKILL_HE.md`
  - `metadata.json`
  - `references/api-reference.md`
  - `references/workflow-guide.md`
  - `references/troubleshooting.md`
  - `references/test-scenarios.md`
  - `references/migration-checklist.md`
  - `scripts/budget-cashflow-forecaster-client.py`
  - `scripts/budget-cashflow-forecaster-cli.py`
  - `scripts/test_budget_cashflow_forecaster_client.py`
  - `scripts/examples/`
- Run tests.
- Build the zip.

---

## Data migration from spreadsheet

- Export as CSV.
- Normalize dates to `YYYY-MM-DD`.
- Ensure amounts are positive.
- Add `direction` with `in` or `out`.
- Split tax payments from operating costs where possible.
- Split owner draw from supplier expenses.
- Add categories.
- Add taxability flags.
- Validate using CLI.

---

## Data migration from older JSON

- Rename `income` to `cash_in`.
- Rename `expenses` to `cash_out`.
- Ensure `start_month` uses `YYYY-MM`.
- Move tax settings into `tax_profile`.
- Add `buffer`.
- Add `reviewed_on` after verification.
- Replace hard-coded rates with configurable values.

---

## Israeli assumption migration

- Confirm VAT registration status.
- Confirm VAT cadence.
- Confirm whether receipts are gross or net.
- Confirm current VAT rate.
- Confirm income-tax advance percentage.
- Confirm Bituach Leumi advance amount or planning rate.
- Document source and review date.
- Mark uncertain assumptions as provisional.
- Request professional review before operational use.

---

## Hebrew localization

- Display currency as `₪`.
- Display Hebrew-facing dates as `DD/MM/YYYY`.
- Use standard terminology: תזרים מזומנים, יתרת פתיחה, יתרת סגירה, רזרבת מס, מע״מ עסקאות, מע״מ תשומות, מקדמות מס הכנסה, דמי ביטוח לאומי, ניכוי מס במקור, משיכת בעלים.
- Avoid unnecessary transliteration when a Hebrew term exists.

---

## Validation after migration

```bash
budget-cashflow-forecaster validate path/to/forecast.json
budget-cashflow-forecaster forecast path/to/forecast.json --output migrated-output.csv
python -m pytest scripts
```

Check that first-month closing balance matches the old model within expected rounding, tax reserves are not double-counted, owner draw is included, annual payments are preserved, and sensitive data is removed from shared examples.
