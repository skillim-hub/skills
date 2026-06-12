# Car Leasing Tax Benefit Calculator

Local calculator for Israeli Shovi Rechev imputed tax benefit on company cars. It supports single-car and batch calculations, Hebrew labels, traceable results, a package import path, CLI workflows, runnable examples, and tests.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

Core imports work after installation:

```python
from car_leasing_tax_benefit import CarLeasingTaxBenefitClient
```

## Quick start: create, extract id, calculate

Create a request and store it locally:

```bash
CREATE_RESPONSE="$(python scripts/car_leasing_tax_benefit_client.py --env sandbox create \
  --price 180000 \
  --category private_combustion \
  --tax-rate 0.35)"
```

Extract the id from the create response:

```bash
REQUEST_ID="$(python -c 'import json, os; print(json.loads(os.environ["CREATE_RESPONSE"])["id"])')"
```

Use that id in the next step:

```bash
python scripts/car_leasing_tax_benefit_client.py --env sandbox calculate \
  --request-id "$REQUEST_ID" \
  --json
```

Direct calculation remains available:

```bash
python scripts/car_leasing_tax_benefit_client.py calculate \
  --price 220000 \
  --category electric \
  --tax-rate 0.47 \
  --json
```

Batch output:

```bash
python scripts/car_leasing_tax_benefit_client.py batch \
  scripts/examples/06_cli_batch_payload.json \
  --output-csv shovi-rechev.csv
```

## Environment variables

Examples and CLI defaults read these variables:

| Variable | Meaning | Default |
|---|---|---|
| `CAR_LEASING_TAX_BENEFIT_ENV` | `sandbox` or `production` | `sandbox` |
| `CAR_LEASING_TAX_BENEFIT_TAX_YEAR` | Tax year | `2026` |
| `CAR_LEASING_TAX_BENEFIT_ORIGINAL_PRICE_ILS` | Coordinated original price in ₪ | `180000` |
| `CAR_LEASING_TAX_BENEFIT_MARGINAL_TAX_RATE` | Marginal tax-rate assumption | `0.35` |
| `CAR_LEASING_TAX_BENEFIT_CATEGORY` | Vehicle category | `private_combustion` |
| `CAR_LEASING_TAX_BENEFIT_MONTHS_AVAILABLE` | Months available | `12` |

## Run examples

```bash
python scripts/examples/01_single_combustion.py --env sandbox
python scripts/examples/02_electric_reduction.py --env sandbox
python scripts/examples/05_async_portfolio.py --env production
```

Each example prints `json.dumps(..., ensure_ascii=False, indent=2)` output.

## Run tests

```bash
pytest scripts
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision tree, edge cases, anti-patterns, and checklist. |
| `SKILL_HE.md` | Hebrew guide with Israeli professional terminology and ₪ localization. |
| `car_leasing_tax_benefit/` | Installable Python package. |
| `data/tax_authority_tables.json` | Local yearly rates and category reductions. |
| `references/api-reference.md` | Official-source reference, schema, commands, responses, errors. |
| `references/workflow-guide.md` | End-to-end workflows for payroll, comparison, updates, and review packs. |
| `references/troubleshooting.md` | Diagnosis and fixes for common errors. |
| `references/test-scenarios.md` | Concrete scenarios for validation and QA. |
| `references/migration-checklist.md` | Checklist for moving from spreadsheets or manual calculations. |
| `references/branding-audit.md` | Neutrality and identity audit report. |
| `references/hebrew-qa-log.md` | Hebrew review changes and style decisions. |
| `scripts/car_leasing_tax_benefit_client.py` | Script wrapper for the package client and CLI. |
| `scripts/car_leasing_tax_benefit_cli.py` | Script wrapper for the package CLI. |
| `scripts/test_car_leasing_tax_benefit_client.py` | Pytest suite. |
| `scripts/examples/` | Runnable examples and batch payload. |
| `metadata.json` | Skill metadata without creator information. |
| `CHANGELOG.md` | Version history. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Installable project metadata and tooling configuration. |
| `requirements-dev.txt` | Development and test dependencies. |

## Production caution

The included tables are editable starter data. Verify the current Israel Tax Authority table before production payroll, filing, or client advice.


## Web-validated 2026 values

The v3 package applies the 2026 coordinated-price ceiling of ₪596,860 and the 2026 monthly reductions of ₪580 for hybrid, ₪1,150 for plug-in hybrid, and ₪1,380 for electric vehicles. Re-verify official publications before payroll filing.
