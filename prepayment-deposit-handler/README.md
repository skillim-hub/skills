# Prepayment & Deposit Handler

Neutral bilingual skill package for handling Israeli deposits, advances, refundable security deposits, booking fees, retentions, credit balances, and final invoice settlement.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained deposit ID

Create a deposit record, extract the deposit ID from the JSON response, and use that ID in the final settlement step.

```bash
CREATE_RESPONSE="$(prepayment-deposit-handler record \
  --deposit-id DEP-2026-0007 \
  --contract-id ORD-4431 \
  --received-date 15/03/2026 \
  --amount 3000 \
  --payer-name "Example Customer Ltd." \
  --payee-name "Example Studio" \
  --nature advance_for_taxable_supply \
  --payment-method bank_transfer)"

DEPOSIT_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["deposit_id"])' <<< "$CREATE_RESPONSE")"

prepayment-deposit-handler settle \
  --line "Consulting:1:12000:0.18" \
  --deposit 3000 \
  --business-type osek_murshe \
  --deposit-reference "$DEPOSIT_ID"
```

Expected settlement values:

- Total including VAT: `14160.00`
- Deposit applied: `3000.00`
- Balance due: `11160.00`
- Deposit reference: `DEP-2026-0007`

## Python import

After `pip install -e .`, import the module without path changes:

```python
from prepayment_deposit_handler_client import LineItem, PrepaymentDepositClient

client = PrepaymentDepositClient()
result = client.settle(
    [LineItem("Consulting", 1, "12000", "0.18")],
    deposit="3000",
    business_type="osek_murshe",
    deposit_reference="DEP-2026-0007",
)
print(result.as_dict())
```

## Development checks

```bash
pytest scripts
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision trees, edge cases, anti-patterns, and production checklist |
| `SKILL_HE.md` | Hebrew operating guide using Israeli terminology, ₪, and DD/MM/YYYY examples |
| `references/api-reference.md` | Local helper API and Israeli regulatory reference map |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Common failures and resolutions |
| `references/test-scenarios.md` | Concrete test and training scenarios |
| `references/migration-checklist.md` | Migration checklist for legacy processes |
| `references/branding-audit.md` | Neutrality and visual-reference audit |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization QA log |
| `references/verification-log.md` | Web-validated two-pass source log |
| `references/deposit-record.schema.json` | JSON schema for deposit records |
| `scripts/prepayment_deposit_handler_client.py` | Typed sync and async Python helper plus argparse CLI |
| `scripts/prepayment_deposit_handler_cli.py` | Typer CLI implementation |
| `scripts/prepayment-deposit-handler-cli.py` | CLI compatibility wrapper |
| `scripts/test_prepayment_deposit_handler_client.py` | Pytest suite with more than 20 tests |
| `scripts/examples/` | Runnable examples that read environment variables and accept `--env sandbox|production` |
| `metadata.json` | Skill metadata |
| `CHANGELOG.md` | Keep-a-Changelog format |
| `LICENSE` | MIT license |
| `pyproject.toml` | Editable-install project metadata and pytest configuration |
| `requirements-dev.txt` | Development dependencies |

## Core workflow

1. Classify the money.
2. Issue a receipt for money received.
3. Determine whether a tax invoice is required.
4. Track unapplied amounts as deposit liability, customer advance, retention receivable, or credit balance.
5. Apply deposits to the final invoice.
6. Refund or document overpayments.
7. Reconcile the customer ledger and VAT documents.

## Accounting caution

This package is a workflow and calculation aid. It does not submit invoices, allocate official invoice numbers, or replace licensed Israeli accounting advice. Verify the current VAT rate, invoice allocation thresholds, cash restrictions, and bookkeeping rules before production use.
