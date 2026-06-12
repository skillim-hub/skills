# Recurring Invoicing Automation

A practical package for Israeli recurring billing workflows: subscriptions, VAT calculation, invoice scheduling, date-effective allocation-threshold checks, SHAAM allocation adapter payloads, credit notes, command-line operations, examples, and tests.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

For Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create a subscription JSON file:

```bash
recurring-invoicing create-subscription \
  --subscription-id SUB-001 \
  --customer-name "Acme Israel Ltd" \
  --customer-tax-id 514324995 \
  --description "Monthly service" \
  --unit-price 1200 \
  --start 2026-01-31 > subscription.json
```

Extract the subscription ID from the create response and use it in the next step:

```bash
SUBSCRIPTION_ID=$(python - <<'PY'
import json
payload = json.load(open("subscription.json", encoding="utf-8"))
print(payload["subscription_id"])
PY
)
echo "$SUBSCRIPTION_ID"
```

Generate an invoice candidate from the saved subscription:

```bash
recurring-invoicing invoice subscription.json --issue-date 2026-01-31 --sequence 1 > invoice.json
```

Check whether the invoice requires an allocation number:

```bash
recurring-invoicing allocation-required invoice.json --business-tax-id 000000018
```

Run a Python example:

```bash
python scripts/examples/02_generate_shaam_payload.py --env sandbox
```

## Environment variables for examples

The examples read environment variables and accept `--env sandbox|production`.

| Variable | Purpose |
|---|---|
| `BUSINESS_TAX_ID` | Business tax ID for payload generation |
| `SHAAM_CLIENT_ID` | Client credential for a real gateway integration |
| `SHAAM_CLIENT_SECRET` | Client secret for a real gateway integration |
| `SHAAM_BASE_URL_SANDBOX` | Sandbox gateway base URL |
| `SHAAM_BASE_URL_PRODUCTION` | Production gateway base URL |
| `SHAAM_SOFTWARE_ID` | Registered software identifier when required |

The included examples avoid live network calls unless a user supplies a transport in application code.

## Use as a library

```python
from datetime import date
from recurring_invoicing import Customer, Interval, LineItem, Subscription, build_invoice

subscription = Subscription(
    subscription_id="SUB-001",
    customer=Customer(name="Acme Israel Ltd", tax_id="514324995"),
    line_items=[LineItem(description="Monthly service", quantity="1", unit_price="1200.00")],
    start_date=date(2026, 1, 31),
    interval=Interval.MONTHLY,
)

invoice = build_invoice(subscription, date(2026, 1, 31), 1)
print(invoice.to_dict())
```

## 2026 threshold note

The package uses date-effective allocation thresholds. For 2026, the default threshold is ₪10,000 from 01/01/2026 and ₪5,000 from 01/06/2026. The older full-year ₪15,000 value was found in an older public API document and corrected against live Tax Authority service pages.

## Development checks

```bash
pytest
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operator guide |
| `SKILL_HE.md` | Hebrew operator guide |
| `recurring_invoicing/client.py` | Typed sync and async client |
| `recurring_invoicing/cli.py` | Typer CLI implementation |
| `scripts/recurring_invoicing_client.py` | Compatibility wrapper for package client imports |
| `scripts/recurring_invoicing_cli.py` | Script entry point for the CLI |
| `scripts/test_recurring_invoicing_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenarios |
| `references/api-reference.md` | API and regulatory reference |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Recovery guide |
| `references/test-scenarios.md` | Concrete scenario matrix |
| `references/migration-checklist.md` | Migration checklist |
| `references/branding-audit.md` | Branding and authorship audit report |
| `references/hebrew-qa-log.md` | Hebrew QA change log |
| `references/verification-log.md` | Two-pass web validation log |
| `pyproject.toml` | Installable package configuration |
| `requirements-dev.txt` | Development dependencies |
| `CHANGELOG.md` | Version history |
| `LICENSE` | MIT license |

## Compliance notes

Confirm all tax, VAT, and allocation rules against official publications before production. Store thresholds as effective-date configuration, not a single annual value. Store request and response bodies for audit, subject to privacy and data-retention policy.
