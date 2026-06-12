# Real Estate Capital-Gains Tax Assistant

Estimate Israeli Mas Shevach on property sales using a structured model for gain, CPI indexation, linear allocation, exemptions, deductions, depreciation, and professional handoff.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a local calculation case in the sandbox environment:

```bash
CREATE_RESPONSE=$(python scripts/real-estate-capital-gains-tax-cli.py create \
  --purchase-date 2008-06-01 \
  --sale-date 2025-06-01 \
  --purchase-price 1000000 \
  --sale-price 2400000 \
  --purchase-costs 50000 \
  --improvements 150000 \
  --sale-costs 60000 \
  --property-type residential_apartment \
  --qualifying-residential \
  --env sandbox)
```

Extract the case id from the create response:

```bash
CASE_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["case_id"])' <<< "$CREATE_RESPONSE")
```

Use the extracted case id in the next step:

```bash
python scripts/real-estate-capital-gains-tax-cli.py estimate-case \
  --case-id "$CASE_ID" \
  --env sandbox \
  --json
```

Run a direct one-off estimate:

```bash
python scripts/real-estate-capital-gains-tax-cli.py estimate \
  --purchase-date 2020-01-01 \
  --sale-date 2025-01-01 \
  --purchase-price 1500000 \
  --sale-price 1900000 \
  --json
```

Use the installable module:

```python
from real_estate_capital_gains_tax import TaxInputs, estimate_tax

inputs = TaxInputs.from_dict({
    "purchase_date": "2020-01-01",
    "sale_date": "2025-01-01",
    "purchase_price": 1500000,
    "sale_price": 1900000,
})
estimate = estimate_tax(inputs)
print(estimate.rounded())
```

Run tests:

```bash
pytest -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide. |
| `SKILL_HE.md` | Hebrew operating guide localized for Israeli terminology. |
| `references/api-reference.md` | Israeli regulation/data/API-equivalent reference. |
| `references/workflow-guide.md` | End-to-end workflows. |
| `references/troubleshooting.md` | Error handling and user-facing fixes. |
| `references/test-scenarios.md` | 20+ concrete scenarios. |
| `references/migration-checklist.md` | Migration and acceptance checklist. |
| `references/branding-audit.md` | Branding, attribution, visual identity, and public Markdown audit. |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance log. |
| `real_estate_capital_gains_tax/` | Installable Python module. |
| `real_estate_capital_gains_tax_client.py` | Compatibility import module. |
| `scripts/real_estate_capital_gains_tax_client.py` | Underscored script-side compatibility module. |
| `scripts/real-estate-capital-gains-tax-cli.py` | Typer CLI. |
| `scripts/test_real_estate_capital_gains_tax_client.py` | Pytest suite. |
| `scripts/examples/` | Runnable examples. |
| `metadata.json` | Skill metadata. |
| `pyproject.toml` | Python project configuration. |

## Calculation features

- Adjusted basis from purchase price, costs, improvements, and depreciation.
- Net sale proceeds after sale costs.
- CPI-based indexed basis and real gain.
- Linear taxable share for qualifying residential-apartment scenarios.
- Ownership-share allocation.
- Local case creation and case-based estimation flow.
- Warning system for business use, foreign residency, unsupported exemptions, CPI gaps, and losses.
- Deterministic JSON output.

## Important caveat

Use estimates for planning and review only. Verify current Israeli law, official CPI values, exemption eligibility, and filing positions with qualified professionals before filing.


## Web-validated v3 notes

- Use the CBS official price-index API host `api.cbs.gov.il` when automating CPI lookups.
- Treat the 25% default rate as an assumption only; verify surtax, additional capital-income tax, company tax, foreign-resident withholding, and VAT exposure.
- Use the local `create` then `estimate-case` flow for reproducible CLI estimates.
