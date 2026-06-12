# Stock Options Tax Advisor

Local planning helper for Israeli employee stock options, RSUs, ESPP shares, and related equity compensation.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a scenario in Python, keep the returned object, then use that same object in the next step.

```python
from stock_options_tax_advisor import EquityScenario, StockOptionsTaxAdvisorClient

client = StockOptionsTaxAdvisorClient(environment="sandbox")
created = client.create_scenario({
    "grant_type": "options",
    "track": "102_capital",
    "quantity": 50000,
    "exercise_price": 1,
    "sale_price": 10,
    "grant_date": "15/03/2024",
    "sale_date": "02/01/2027",
    "other_annual_income": 360000,
    "trustee_approved": True,
})
result = client.calculate(created)
print(result.to_json())
```

The same create-then-use flow works from JSON data: store `created.to_dict()` in a case file, reload it with `EquityScenario.from_dict`, and pass the result to `calculate` or `compare_tracks`.

## CLI

```bash
stock-options-tax-advisor calculate   --env sandbox   --grant-type options   --track 102_capital   --quantity 50000   --exercise-price 1   --sale-price 10   --grant-date 15/03/2024   --sale-date 02/01/2027   --other-income 360000   --trustee-approved   --json
```

## Examples

Every script accepts `--env sandbox|production`, reads optional environment variables such as `STOCK_OPTIONS_QUANTITY`, `STOCK_OPTIONS_SALE_PRICE`, and `STOCK_OPTIONS_OTHER_INCOME`, and prints JSON using `ensure_ascii=False` with two-space indentation.

```bash
python scripts/examples/01_capital_track_options.py --env sandbox
python scripts/examples/05_compare_tracks.py --env production
```

## File index

| Path | Purpose |
| --- | --- |
| `SKILL.md` | English operational guide. |
| `SKILL_HE.md` | Hebrew operational guide with Israeli terminology and date format. |
| `stock_options_tax_advisor/` | Installable Python package. |
| `scripts/stock_options_tax_advisor_client.py` | Underscored compatibility import for the client API. |
| `scripts/stock-options-tax-advisor-cli.py` | Direct script wrapper for the CLI. |
| `scripts/test_stock_options_tax_advisor_client.py` | Pytest suite. |
| `scripts/examples/` | Runnable scenario scripts. |
| `references/api-reference.md` | Regulation and helper-interface reference. |
| `references/workflow-guide.md` | End-to-end workflows. |
| `references/troubleshooting.md` | Diagnostic guide. |
| `references/test-scenarios.md` | Scenario catalog. |
| `references/migration-checklist.md` | Upgrade checklist. |
| `references/branding-audit.md` | Neutrality and branding audit. |
| `references/hebrew-qa-log.md` | Hebrew review log. |
| `references/verification-log.md` | Web validation log with pass 1 and pass 2 sources. |

## Validate

```bash
python -m compileall scripts/ -q
pytest
```

## Official-source refresh

Before using the helper for a live case, open `references/verification-log.md`, re-check the official source rows for the target tax year, and override `TaxConstants` when an updated rate, threshold, or trustee position applies.
