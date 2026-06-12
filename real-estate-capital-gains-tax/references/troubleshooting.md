# Troubleshooting Guide

## Calculation issues

### Estimate is unexpectedly high

Possible causes:

- CPI values were omitted.
- Deductible purchase or sale costs were omitted.
- Improvements were entered as sale costs or not entered at all.
- Linear relief was not applied for a qualifying residential apartment.
- A possible exemption was not checked.
- Depreciation was entered twice.

Fix:

1. Re-enter all costs by category.
2. Add CPI values from the official source.
3. Confirm apartment eligibility.
4. Re-run with and without linear relief.
5. Compare both results and document assumptions.

### Estimate is unexpectedly low

Possible causes:

- Full exemption was assumed without eligibility proof.
- Depreciation was ignored.
- Ownership share was entered as `0.1` instead of `1.0`.
- Sale costs include buyer-paid expenses.
- Purchase price includes mortgage principal or financing amounts that are not basis.

Fix:

1. Remove unsupported exemptions.
2. Add depreciation.
3. Verify ownership share.
4. Reconcile contract values with invoices.
5. Run a conservative scenario.

### Real gain is zero after CPI

Possible causes:

- CPI sale/purchase ratio is too high due to mismatched CPI bases.
- Purchase CPI and sale CPI were reversed.
- Purchase date is wrong.
- Purchase basis includes non-deductible expenses.

Fix:

1. Confirm both CPI values use the same base series.
2. Ensure `cpi_sale > cpi_purchase` only when the official index increased.
3. Confirm date format.
4. Review cost categories.

### Linear taxable share is zero

Possible causes:

- Sale occurred before the linear relief start date.
- Purchase date is after the relief start date and the model caps taxable days incorrectly.
- Dates were reversed or entered in the wrong format.

Fix:

1. Confirm sale date is after purchase date.
2. Confirm the relief date.
3. For post-2014 acquisitions, expect most or all gain to be taxable under a simple linear model.
4. Verify whether a full exemption applies instead.

## Input validation issues

| Message | Meaning | Fix |
|---|---|---|
| `Sale date must be after purchase date` | Date order is invalid | Correct dates. |
| `Money amounts must be non-negative` | A cost or price is negative | Enter positive values in the correct field. |
| `Ownership share must be > 0 and <= 1` | Invalid fraction | Use `1`, `0.5`, `0.3333`, etc. |
| `Both CPI values must be supplied together` | Only one CPI value exists | Add the missing CPI or remove both. |
| `CPI values must be positive` | CPI is zero/negative | Use official positive values. |

## Exemption issues

### Single-apartment exemption is uncertain

Ask:

- Did the seller own any other apartment, including a share?
- Did the seller own an apartment abroad?
- How long was the apartment held?
- Is the seller an Israeli resident?
- Was any part used for business or rental?
- Was a similar exemption used recently?

### Inheritance exemption is uncertain

Ask:

- Was the seller a spouse, descendant, or spouse of descendant?
- Did the deceased own more than one apartment?
- Would the deceased have qualified for an exemption?
- Were there equalization payments between heirs?

### Gift exemption or continuity is uncertain

Ask:

- Who gave the property?
- When did the donor buy it?
- Was consideration paid?
- Has the cooling-off period passed?
- Did the recipient live in the apartment?

## CLI issues

### Typer is missing

Install runtime requirements:

```bash
pip install -e .
```

or:

```bash
pip install typer
```

### JSON output is not valid

Use:

```bash
python scripts/real-estate-capital-gains-tax-cli.py estimate ... --json
```

Do not mix shell comments inside the command.

### Import fails for the client file

The required client filename contains hyphens. Import it by path:

```python
import importlib.util
from pathlib import Path

path = Path("real_estate_capital_gains_tax")
spec = importlib.util.spec_from_file_location("mas_shevach_client", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
```

## Professional escalation triggers

Escalate to a lawyer/CPA/tax adviser when any of these apply:

- Foreign resident seller.
- Company, partnership, trust, or estate seller.
- Urban renewal or combination transaction.
- Gift or inheritance with missing history.
- Business/rental use and depreciation.
- Multiple owners with different acquisition dates.
- Betterment levy dispute.
- Non-cash consideration.
- Related-party transaction.
- Sale under insolvency, divorce, or court order.
- Assessment differs materially from the estimate.


## Default 25% rate warning

The helper may show a warning that the default 25% rate excludes high-income surtax and additional capital-income tax where applicable. This is expected. Override `--tax-rate` only after professional review or keep the warning in the output.
