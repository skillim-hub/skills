# Migration Checklist

Use this checklist when moving from spreadsheet, manual calculation, or an earlier package version to this enhanced skill.

## 1. Inventory the existing process

- List every spreadsheet, payroll-system table, and manual worksheet used for Shovi Rechev.
- Identify the owner of each file.
- Record the last update date.
- Locate the official source table used for the current year.
- Export a sample of at least 10 historical calculations for comparison.

## 2. Normalize input data

Required fields:

```text
employee_name
license_plate
tax_year
original_price_ils
category
employee_marginal_tax_rate
months_available
```

Normalization rules:

- Convert all prices to whole shekels or decimal shekels, not agorot.
- Map local categories to calculator keys:
  - petrol/diesel/private → `private_combustion`
  - hybrid/היברידי → `hybrid`
  - plug-in/פלאג אין → `plugin_hybrid`
  - electric/חשמלי → `electric`
- Convert dates to months available before import.
- Preserve original employee identifiers in a separate payroll system if needed.

## 3. Update rule tables

- Open `data/tax_authority_tables.json`.
- Verify `last_reviewed` in `DD/MM/YYYY`.
- Add the current tax year if missing.
- Update `base_linear_rate`.
- Update all `monthly_reduction_ils` values.
- Keep rejected categories blocked unless a dedicated formula is implemented.

## 4. Run a parallel calculation

1. Select 10–20 real vehicles.
2. Run the old spreadsheet.
3. Run the client:

```bash
python scripts/car_leasing_tax_benefit_client.py batch sample.json --output-csv sample-new.csv
```

4. Compare monthly values.
5. Classify differences:
   - official price mismatch
   - stale green-vehicle reduction
   - rounding
   - wrong availability period
   - category mapping error
   - spreadsheet formula error

## 5. Update operating procedures

- Replace manual formulas with CLI or client usage.
- Require JSON input retention.
- Require JSON trace retention for exceptions.
- Require annual table review every January.
- Require accountant approval for any non-standard private-use ratio.

## 6. Rollout controls

- Use read-only review for first payroll month.
- Keep old calculation as backup for one cycle.
- Reconcile every vehicle row.
- Obtain payroll-provider signoff.
- Archive the old spreadsheet as locked reference.

## 7. Post-migration audit

Within 30 days:

- Confirm no unsupported vehicle categories were forced into the private-car formula.
- Confirm CSV encoding works for Hebrew names.
- Confirm tests pass in the deployment environment.
- Confirm changelog records the migration.
- Confirm source documents are attached to workpapers.

## 8. Rollback plan

- Restore the previous spreadsheet or payroll table.
- Keep input JSON files generated during trial.
- Preserve discrepancy notes.
- Fix rule table or mapping issues.
- Re-run tests and scenario set before re-enabling.

## Migration done criteria

Migration is complete only when:

- Current-year rule table is verified.
- At least 20 test scenarios pass.
- Payroll provider accepts the output format.
- Accountant or finance owner signs off.
- Old spreadsheet is locked against further editing.
