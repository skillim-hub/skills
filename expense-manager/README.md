# Expense Manager

Expense Manager classifies Israeli expenses, estimates income-tax and VAT treatment, flags documentation gaps, and exports accountant-ready CSV/JSON packages for small businesses, freelancers, companies, and consumer tracking.

## Install

Use Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

For normal usage, the client library uses the Python standard library. The CLI requires Typer, installed by `pip install -e .`.

## Quick start

Create one normalized expense record, capture the returned id, then use that id in the next command:

```bash
python scripts/expense-manager-cli.py create \
  --vendor Bezeq \
  --amount 234 \
  --date 15/01/2026 \
  --description "Internet and phone for studio" \
  --receipt-number INV-1001 \
  --output created-expense.json \
  > create-response.json

EXPENSE_ID=$(python -c 'import json; print(json.load(open("create-response.json", encoding="utf-8"))["id"])')

python scripts/expense-manager-cli.py classify-created created-expense.json \
  --id "$EXPENSE_ID" \
  --env sandbox \
  > classification.json
```

Create `input.csv` for batch classification:

```csv
date,vendor,amount,description,receipt_number
15/01/2026,Bezeq,234,Internet and phone,INV-1001
16/01/2026,Aroma,58,Coffee with Israeli client,RCPT-1002
```

Classify the CSV:

```bash
python scripts/expense-manager-cli.py classify input.csv classified.csv --entity-type osek_murshe --env sandbox
```

Create an accountant package:

```bash
python scripts/expense-manager-cli.py package input.csv ./out --package-name 2026-01-expenses --entity-type osek_murshe --env production
```

Use the importable package from Python:

```python
from datetime import date
from expense_manager import BusinessConfig, EntityType, ExpenseInput, classify_expense, parse_decimal

expense = ExpenseInput(
    date=date(2026, 1, 15),
    vendor="Bezeq",
    amount=parse_decimal("234"),
    description="Internet and phone for studio",
)
result = classify_expense(expense, BusinessConfig(entity_type=EntityType.OSEK_MURSHE))
print(result.to_flat_dict())
```

Run tests:

```bash
pytest scripts/test_expense_manager_client.py
python -m compileall scripts/ -q
```

## Environment variables

Examples and CLI defaults read these optional variables:

| Variable | Purpose |
|---|---|
| `EXPENSE_MANAGER_ENV` | `sandbox` or `production` for examples |
| `EXPENSE_MANAGER_ENTITY_TYPE` | `osek_patur`, `osek_murshe`, `company`, or `private_consumer` |
| `EXPENSE_MANAGER_HOME_OFFICE_PERCENT` | Dedicated home-office percentage, such as `12.5` |
| `EXPENSE_MANAGER_OUTPUT_DIR` | Output directory used by example scripts |
| `EXPENSE_MANAGER_PACKAGE_NAME` | Default package name for CLI package export |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `references/api-reference.md` | Regulation/API-style reference, data contracts, examples, and error tables |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Diagnostics and fixes |
| `references/test-scenarios.md` | Manual and automated QA scenarios |
| `references/migration-checklist.md` | Migration steps from older spreadsheets and ad-hoc workflows |
| `references/branding-audit.md` | Neutrality and public-Markdown audit |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology QA log |
| `scripts/expense_manager_client.py` | Typed sync/async Python client and record helpers |
| `scripts/expense_manager_cli.py` | Typer CLI implementation |
| `scripts/expense-manager-cli.py` | CLI compatibility launcher |
| `scripts/test_expense_manager_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario examples |
| `expense_manager/` | Installable package facade |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep a Changelog record |
| `LICENSE` | MIT license |
| `pyproject.toml` | Project metadata, install settings, and test configuration |
| `requirements-dev.txt` | Development dependencies |

## Professional review

Use generated outputs for preparation and review. Final classification, VAT reporting, depreciation, and tax filing require qualified professional approval.
