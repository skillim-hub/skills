# Migration Checklist

Use this checklist when moving from spreadsheets, ad hoc scripts, or earlier package versions.

## Inventory current calculation assets

- Locate all spreadsheets, formulas, and manual notes.
- Record the tax year covered by each file.
- Identify whether revenue values are before VAT or including VAT.
- Identify whether income-tax advances were calculated from revenue or profit.
- Identify the National Insurance thresholds and rates used.
- Archive the old calculation before changing it.

## Replace old imports

Old path-based or hyphenated client loading should be removed. Use:

```python
from freelancer_tax_calculator import FreelancerTaxCalculator, FreelancerTaxInput
```

Run:

```bash
pip install -e .
python -c "from freelancer_tax_calculator import FreelancerTaxCalculator; print('ok')"
```

## Migrate CLI usage

Use the installed command:

```bash
freelancer-tax-calculator calculate --business-type osek-murshe --revenue 100000 --json
```

For reproducible workflows, create a scenario first:

```bash
freelancer-tax-calculator create --business-type osek-murshe --revenue 100000 --json
```

Extract `scenario_id` and run it later with:

```bash
freelancer-tax-calculator run SCENARIO_ID --json
```

## Migrate configuration

1. Create a JSON configuration file from `freelancer-tax-calculator example-config`.
2. Replace default rates and thresholds with current verified values.
3. Store the configuration file with the report output.
4. Prefer environment variables only for repeatable local workflows.

## Validate migrated results

- Compare VAT output against the old spreadsheet for one osek murshe scenario.
- Compare osek patur threshold utilization for one near-threshold scenario.
- Compare income-tax advances using both revenue and profit bases when the old basis is unclear.
- Compare National Insurance estimates only after matching thresholds and rates.
- Investigate differences greater than a rounding tolerance.

## Decommission old files

- Mark old spreadsheets as read-only.
- Keep an archive for audit trail.
- Remove instructions that mention the hyphenated client path.
- Update README snippets and team notes.
- Run the full test suite after migration.
