# Migration Checklist

Use this checklist when replacing an older tax-return skill package or integrating this enhanced package into an existing assistant setup.

## Package-level migration

- [ ] Replace the old package folder with `tax-return-filing-assistant`.
- [ ] Remove any branding, visual marks, credit lines, organization references, or distribution callouts from downstream copies.
- [ ] Confirm `metadata.json` has no `author` field.
- [ ] Confirm the license file uses the required neutral MIT copyright notice.
- [ ] Confirm README, SKILL.md, and SKILL_HE.md use neutral imperative language.
- [ ] Confirm no image references exist in markdown.
- [ ] Confirm the package version is `2.1.0` or later.
- [ ] Run `pytest scripts/test_tax_return_filing_assistant_client.py`.

## Workflow migration

- [ ] Map old “annual individual return” instructions to the Form 1301 workflow.
- [ ] Map old “salary refund” instructions to the Form 135 workflow.
- [ ] Map old “employer annual report” instructions to Form 126.
- [ ] Map old “supplier report” instructions to Form 856.
- [ ] Map old “financial statement” instructions to Form 6111.
- [ ] Remove corporate-only workflows unless needed by local users.
- [ ] Replace hard-coded thresholds with filing-year-aware configuration.
- [ ] Add official-verification notes to every deadline and threshold.
- [ ] Add privacy minimization before document collection.
- [ ] Add reconciliation steps before final summary.

## Data migration

- [ ] Convert old profile fields to the new JSON shape:
  - `tax_year`
  - `taxpayer_type`
  - `salary_only`
  - `wants_refund`
  - `business_income`
  - `annual_turnover_ils`
  - `has_employees`
  - `paid_suppliers`
  - `foreign_income`
  - `capital_gains`
  - `rental_income`
  - `is_online`
  - `represented_by_cpa`
- [ ] Keep amounts as numbers, not formatted strings.
- [ ] Keep identity numbers out of sample profiles.
- [ ] Store notes without full bank or payroll details.
- [ ] Re-run validation after migration.

## CLI migration

- [ ] Use `tax-return-filing-assistant recommend --profile profile.json` for form selection.
- [ ] Use `deadline` command instead of static deadline text.
- [ ] Use `fields FORM` to expose field help.
- [ ] Use `validate --profile` before generating a final report.
- [ ] Capture the default JSON output for automated workflows.

## Hebrew content migration

- [ ] Use “רשות המסים”, not transliteration.
- [ ] Use “דוח שנתי”, “ניכוי במקור”, “נקודות זיכוי”, “מאזן בוחן”, “כרטסת”, and “מייצג”.
- [ ] Use `₪` for shekels.
- [ ] Use `DD/MM/YYYY` dates.
- [ ] Avoid English terms when a professional Hebrew term exists.
