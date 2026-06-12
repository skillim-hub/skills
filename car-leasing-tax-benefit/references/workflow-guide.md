# Workflow Guide

Use these workflows to move from raw vehicle data to a documented Shovi Rechev result.

## Workflow 1: Single employee company car

### Goal

Calculate the taxable monthly benefit for one employee using a standard company car.

### Inputs to collect

1. Employee name or payroll identifier.
2. License plate.
3. Tax year.
4. Vehicle category.
5. Official coordinated original price.
6. Start and end dates during the year.
7. Employee marginal tax rate for planning.

### Steps

```bash
python scripts/car_leasing_tax_benefit_client.py calculate \
  --price 180000 \
  --category private_combustion \
  --year 2026 \
  --tax-rate 0.35 \
  --months 12 \
  --employee-name "Dana Cohen" \
  --license-plate "123-45-678" \
  --json
```

### Review

- Check that `gross_monthly_value_ils` equals price × 2.48%.
- Confirm that `category_reduction_ils` is ₪0 for regular petrol/diesel.
- Attach JSON output to payroll support.

## Workflow 2: Electric-car benefit comparison

### Goal

Compare a regular vehicle and an electric vehicle for the same employee.

### Command set

```bash
python scripts/car_leasing_tax_benefit_client.py calculate --price 180000 --category private_combustion --tax-rate 0.35 --json
python scripts/car_leasing_tax_benefit_client.py calculate --price 220000 --category electric --tax-rate 0.35 --json
```

### Decision notes

- Compare estimated tax cost, not only monthly lease payment.
- Include charging, insurance, maintenance, and employer policy.
- Confirm the annual electric reduction before relying on the result.

## Workflow 3: Employee changes vehicle mid-year

### Goal

Calculate two separate periods and combine the results.

### Input JSON

```json
[
  {
    "employee_name": "Noa",
    "license_plate": "111-22-333",
    "original_price_ils": "160000",
    "category": "private_combustion",
    "months_available": 4,
    "employee_marginal_tax_rate": "0.31"
  },
  {
    "employee_name": "Noa",
    "license_plate": "444-55-666",
    "original_price_ils": "225000",
    "category": "electric",
    "months_available": 8,
    "employee_marginal_tax_rate": "0.31"
  }
]
```

### Command

```bash
python scripts/car_leasing_tax_benefit_client.py batch vehicles.json --output-csv noa-vehicle-change.csv
```

### Review

- Confirm the two periods do not overlap.
- Confirm total months do not exceed 12 unless multiple employees are involved.
- Keep each row separate for audit clarity.

## Workflow 4: Small company monthly payroll handoff

### Goal

Prepare a CSV for a payroll provider.

### Steps

1. Export all company cars from fleet software.
2. Normalize category keys to supported values.
3. Add tax year, months available, and employee marginal tax rate.
4. Save as JSON list.
5. Run batch calculation.
6. Send CSV and source JSON to payroll provider.

### Command

```bash
python scripts/car_leasing_tax_benefit_client.py batch fleet.json --output-csv payroll-shovi-rechev.csv
```

### Controls

- Verify row count equals active company-car assignments.
- Sort by employee identifier before sending.
- Store the output file using `YYYY-MM` in the filename.
- Ask payroll provider to confirm values imported into payslips.

## Workflow 5: Freelancer or owner-manager decision support

### Goal

Estimate the effect of taking a company car versus paying privately.

### Steps

1. Calculate Shovi Rechev for the proposed vehicle.
2. Estimate incremental personal tax cost.
3. Add employee social contributions when relevant.
4. Compare against private lease/loan, insurance, maintenance, fuel/charging, parking, and depreciation.
5. Review VAT and deductibility limitations with an accountant.

### Important limitation

This skill does not calculate deductibility, VAT recovery, or company tax savings. Use it as one component in a broader decision model.

## Workflow 6: Annual table update

### Goal

Update tax-year tables safely after a new official publication.

### Steps

1. Download or copy the current official Israel Tax Authority Shovi Rechev table.
2. Open `data/tax_authority_tables.json`.
3. Duplicate the prior year object.
4. Update:
   - `effective_from`
   - `effective_to`
   - `base_linear_rate`
   - each `monthly_reduction_ils`
   - category notes
5. Change top-level `last_reviewed` to `DD/MM/YYYY`.
6. Add a `CHANGELOG.md` entry.
7. Run:

```bash
pytest scripts
```

8. Run several scenarios from `references/test-scenarios.md`.
9. Keep the official source PDF/page with payroll documentation.

## Workflow 7: Accountant review pack

### Pack contents

- Input JSON.
- Output JSON or CSV.
- `data/tax_authority_tables.json`.
- Official source table used.
- Vehicle price source.
- Availability dates.
- Notes for any warning in the trace.

### Review questions

- Is the tax year correct?
- Is the vehicle category correct?
- Is the official coordinated original price documented?
- Is the availability period correct?
- Does payroll use the same category reduction?
