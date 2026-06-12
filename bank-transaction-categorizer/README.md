# Bank Transaction Categorizer

Neutral, offline-first categorization of Israeli bank transactions from CSV-style exports.

## What it does

- Parse Israeli bank statement exports.
- Handle Hebrew and English column names.
- Convert `חובה` and `זכות` into signed amounts.
- Categorize common Israeli business and household transactions.
- Flag low-confidence, duplicate, wallet, card-settlement, and review-needed rows.
- Export CSV or JSON.
- Provide English and Hebrew documentation, troubleshooting, workflows, tests, and runnable examples.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with registered input id

Create a sample statement and capture the returned id:

```bash
python scripts/bank-transaction-categorizer-cli.py create-sample --env sandbox --output sample.csv > create-response.json
INPUT_ID=$(python -c "import json; print(json.load(open('create-response.json', encoding='utf-8'))['id'])")
```

Use the id in the next step:

```bash
python scripts/bank-transaction-categorizer-cli.py categorize --env sandbox --input-id "$INPUT_ID" --output categorized.csv
python scripts/bank-transaction-categorizer-cli.py summary --env sandbox categorized.csv
```

Direct file use is also supported:

```bash
python scripts/bank-transaction-categorizer-cli.py categorize statement.csv --output categorized.csv
```

## Programmatic use

```python
from bank_transaction_categorizer import BankTransactionCategorizer

categorizer = BankTransactionCategorizer()
result = categorizer.categorize_file("statement.csv", output_path="categorized.csv")
print(result["summary"])
```

## Run tests

```bash
python -m pytest -q
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English skill guide |
| `SKILL_HE.md` | Hebrew skill guide |
| `README.md` | Installation and quick start |
| `CHANGELOG.md` | Keep-a-Changelog release notes |
| `LICENSE` | MIT license |
| `metadata.json` | Skill metadata |
| `pyproject.toml` | Python project and pytest configuration |
| `requirements-dev.txt` | Development dependencies |
| `bank_transaction_categorizer/` | Installable Python package |
| `references/api-reference.md` | Israeli banking, API, privacy, and regulatory context |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Troubleshooting guide |
| `references/test-scenarios.md` | Concrete validation scenarios |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Branding and attribution audit |
| `references/hebrew-qa-log.md` | Hebrew quality-assurance log |
| `references/verification-log.md` | Two-pass web validation log |
| `scripts/bank_transaction_categorizer_client.py` | Compatibility re-export for the installable client |
| `scripts/bank-transaction-categorizer-cli.py` | CLI wrapper |
| `scripts/test_bank_transaction_categorizer_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |

## Verified regulatory scope

The v3 package includes `references/verification-log.md` with two-pass web validation performed on 2026-06-02. The package remains offline-first: it does not claim endorsement by any bank, does not provide official Bank of Israel API hosts, and does not implement live account access.

## Data safety

Process statement files locally whenever possible. Bank statements contain sensitive financial and personal data. Avoid sharing raw statements through unsecured channels, remove full account numbers when sharing, and keep custom rules private when they contain client or supplier names.
