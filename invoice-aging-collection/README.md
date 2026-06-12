# Invoice Aging & Collection Reminders

Neutral skill package for tracking unpaid invoices in Israel, generating Hebrew WhatsApp and email collection reminders, and managing escalation logic for small businesses, freelancers, and consumers.

## What is included

- English and Hebrew operating guides.
- Israeli regulation and integration reference.
- End-to-end workflow guide.
- Troubleshooting guide.
- Test scenarios.
- Migration checklist.
- Branding audit and Hebrew quality log.
- Typed Python client with sync and async helpers.
- Typer-based CLI.
- Pytest suite with more than 20 tests.
- Runnable scenario examples.

## Install for local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create sample data, append a new invoice, extract the created invoice ID from the create response, then use that ID in the next command.

```bash
python scripts/invoice-aging-collection-cli.py sample-data --out sample-ledger.json

CREATE_RESPONSE=$(python scripts/invoice-aging-collection-cli.py create-invoice sample-ledger.json \
  --client-id c-100 \
  --issue-date 01/04/2026 \
  --due-date 30/04/2026 \
  --amount 1800.00 \
  --json)

INVOICE_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["invoice_id"])' <<< "$CREATE_RESPONSE")

python scripts/invoice-aging-collection-cli.py validate sample-ledger.json
python scripts/invoice-aging-collection-cli.py age sample-ledger.json --as-of 01/06/2026
python scripts/invoice-aging-collection-cli.py reminders sample-ledger.json --as-of 01/06/2026 --channel whatsapp --json
python scripts/invoice-aging-collection-cli.py render sample-ledger.json --invoice-id "$INVOICE_ID" --stage friendly_whatsapp --as-of 01/06/2026 --json
```

After installation, the same CLI is available as:

```bash
invoice-aging-collection age sample-ledger.json --as-of 01/06/2026
```

## Python quick start

```python
from invoice_aging_collection_client import InvoiceAgingClient, sample_ledger

client = InvoiceAgingClient(sample_ledger())
report = client.aging_report("01/06/2026")
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English guide with rules, examples, decision trees, anti-patterns, and checklist. |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, ₪ formatting, and DD/MM/YYYY localization. |
| `metadata.json` | Neutral metadata. |
| `references/api-reference.md` | Israeli regulations, services, and integration examples. |
| `references/workflow-guide.md` | End-to-end operational workflows. |
| `references/troubleshooting.md` | Diagnosis and recovery procedures. |
| `references/test-scenarios.md` | Concrete QA scenarios. |
| `references/migration-checklist.md` | Migration path from spreadsheets or older workflows. |
| `references/branding-audit.md` | Neutrality, branding, visual identity asset, visual marker, and public Markdown checks. |
| `references/hebrew-qa-log.md` | Hebrew terminology, date, currency, and style QA log. |
| `references/verification-log.md` | Web validation log with two-pass source checks and corrections. |
| `scripts/invoice_aging_collection_client.py` | Typed sync and async client/helper library. |
| `scripts/invoice_aging_collection_cli.py` | Importable Typer CLI module. |
| `scripts/invoice-aging-collection-cli.py` | CLI compatibility entry point. |
| `scripts/test_invoice_aging_collection_client.py` | Pytest suite. |
| `scripts/examples/` | Runnable examples. |
| `pyproject.toml` | Installable project and pytest configuration. |
| `requirements-dev.txt` | Development dependencies. |
| `CHANGELOG.md` | Keep-a-Changelog release notes. |
| `LICENSE` | MIT license. |

## Ledger format

```json
{
  "business": {
    "name": "סטודיו דוגמה",
    "payment_instructions": "בנק 12, סניף 345, חשבון 67890"
  },
  "clients": [
    {
      "client_id": "c-100",
      "name": "לקוח לדוגמה בע\"מ",
      "email": "client@example.co.il",
      "whatsapp": "+972501234567",
      "mailing_address": "רחוב הדוגמה 1, תל אביב"
    }
  ],
  "invoices": [
    {
      "invoice_id": "INV-100",
      "client_id": "c-100",
      "issue_date": "01/01/2026",
      "due_date": "31/01/2026",
      "amount": "2500.00",
      "currency": "ILS",
      "status": "open",
      "partial_payments": []
    }
  ],
  "blocked_dates": []
}
```

## Example scripts

Each example reads environment variables and accepts `--env sandbox|production`.

```bash
INVOICE_AGING_AS_OF=01/06/2026 python scripts/examples/01_aging_report.py --env sandbox
python scripts/examples/02_whatsapp_reminder.py --env sandbox --invoice-id INV-100
```

## Run tests

```bash
pytest -q
python -m compileall scripts/ -q
```

## Legal and accounting caution

The package helps organize operational collection workflows. It does not provide legal representation, tax filing, accounting approval, or court filing. Verify current law, rates, thresholds, and government forms before legal escalation.
