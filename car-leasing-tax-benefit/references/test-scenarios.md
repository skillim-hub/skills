# Test Scenarios

Use these scenarios for manual QA, regression testing, accountant review, and payroll reconciliation. Amounts depend on the included starter table; update expected values after official table changes.

| # | Scenario | Input highlights | Expected behavior |
|---:|---|---|---|
| 1 | Regular petrol car, full year | ₪100,000, `private_combustion`, 12 months | Monthly value ₪2,480.00. |
| 2 | Regular petrol car, high price | ₪450,000, `private_combustion` | Monthly value equals price × 2.48%. |
| 3 | Electric car reduction | ₪200,000, `electric` | Monthly value equals ₪4,960.00 minus electric reduction. |
| 4 | Hybrid reduction | ₪200,000, `hybrid` | Monthly value lower than regular vehicle by hybrid reduction. |
| 5 | Plug-in hybrid reduction | ₪200,000, `plugin_hybrid` | Monthly value lower than regular vehicle by plug-in reduction. |
| 6 | Reduction floor | ₪1,000, `electric` | Monthly value floored at ₪0.00. |
| 7 | Partial year, 3 months | ₪100,000, 3 months | Annual period value equals monthly × 3. |
| 8 | Employee joined 01/08/2026 | 5 months available | Period value equals monthly × 5. |
| 9 | Vehicle switched in April | Two records: 4 + 8 months | Keep rows separate; total months 12. |
| 10 | Marginal tax 35% | Monthly ₪2,480.00, tax rate 0.35 | Estimated monthly tax cost ₪868.00. |
| 11 | Marginal tax 47% | Electric vehicle, tax rate 0.47 | Estimated tax cost uses 47%. |
| 12 | Tax rate 0% | Valid vehicle, tax rate 0 | Imputed value remains; estimated tax cost ₪0.00. |
| 13 | Tax rate 100% | Valid vehicle, tax rate 1 | Estimated tax cost equals imputed value. |
| 14 | Negative price | `-1` | Reject with validation error. |
| 15 | Zero price | `0` | Reject with validation error. |
| 16 | Agorot entered as shekels | ₪18,000,000 | Warning for unusually high price. |
| 17 | Unknown category | `spaceship` | Reject with unsupported category error. |
| 18 | Motorcycle L3 | `motorcycle_l3` | Reject; dedicated rule required. |
| 19 | Missing year | `2035` | Reject with missing rules error. |
| 20 | Private-use ratio 0.5 | Ratio below 1 | Calculate adjusted amount and issue planning warning. |
| 21 | Private-use ratio 1.1 | Ratio above 1 | Reject. |
| 22 | Months 0 | `months_available=0` | Reject. |
| 23 | Months 13 | `months_available=13` | Reject. |
| 24 | Batch JSON two cars | Regular + electric | Return two result objects. |
| 25 | CSV export | Batch output | CSV contains Hebrew labels and numeric result columns. |
| 26 | Hebrew employee names | `employee_name="נועה"` | Preserve UTF-8 text. |
| 27 | License plate with dashes | `123-45-678` | Preserve as text. |
| 28 | JSON trace review | `--json` | Output contains formula, rate, reduction, and warnings. |
| 29 | Stale table detection | Wrong effective year in review | Reviewer catches mismatch before payroll. |
| 30 | Payroll reconciliation | Same inputs in payroll system | Difference isolated to source price, rounding, or table values. |

## Detailed scenario examples

### Scenario 1: regular petrol car

```bash
python scripts/car_leasing_tax_benefit_client.py calculate --price 100000 --category private_combustion --json
```

Expected key fields:

```json
{
  "monthly_imputed_value_ils": "2480.00",
  "annual_imputed_value_ils": "29760.00"
}
```

### Scenario 6: electric reduction floor

```bash
python scripts/car_leasing_tax_benefit_client.py calculate --price 1000 --category electric --json
```

Expected key field:

```json
{
  "monthly_imputed_value_ils": "0.00"
}
```

### Scenario 20: private-use planning warning

```bash
python scripts/car_leasing_tax_benefit_client.py calculate \
  --price 100000 \
  --private-use-ratio 0.5 \
  --json
```

Expected: a warning stating that partial private use is a planning assumption.

## Acceptance criteria

- All valid scenarios return deterministic numeric values.
- All invalid scenarios fail with clear errors.
- JSON outputs are parseable.
- CSV exports open in Excel with Hebrew intact.
- Every calculation includes a trace.
- Updated tax tables are accompanied by updated tests and changelog entry.
