# Foreign-Currency Invoicing

Prepare Israeli foreign-currency invoice calculations with Bank of Israel representative-rate support, date-specific SDMX rate URLs, NIS VAT totals, audit-ready notes, a typed Python client, a Click CLI, examples, and tests.

## Install

```bash
unzip foreign-currency-invoicing-enhanced-v3.zip
cd foreign-currency-invoicing
pip install -e .
pip install -r requirements-dev.txt
```

After installation, import directly:

```python
from foreign_currency_invoicing_client import calculate_invoice
```

## Quick start with chained create and show

```bash
CREATE_RESPONSE=$(foreign-currency-invoicing create \
  --env sandbox \
  --currency USD \
  --issue-date 02/06/2026 \
  --exchange-rate 3.70 \
  --lines-json '[{"description":"Consulting","quantity":"1","unit_price":"500","vat_category":"standard"}]')

INVOICE_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$CREATE_RESPONSE")
foreign-currency-invoicing show --env sandbox "$INVOICE_ID"
```

## Python quick start

```python
from foreign_currency_invoicing_client import calculate_invoice

result = calculate_invoice(
    lines=[{"description": "Consulting", "quantity": "1", "unit_price": "500", "vat_category": "standard"}],
    currency="USD",
    issue_date="02/06/2026",
    exchange_rate="3.70",
)
print(result.to_json())
```


## Bank of Israel rate URLs

Date-specific invoice support uses the Bank of Israel SDMX series endpoint, for example `RER_USD_ILS` with `startPeriod`, `endPeriod`, and `format=csv`. The current public API remains supported for current-rate JSON or XML fixtures.

```bash
foreign-currency-invoicing rate-url --env sandbox --currency USD --as-of-date 02/06/2026
```

## Environment variables

Examples and the CLI read these variables when present:

| Variable | Purpose |
|---|---|
| `FCI_ENV` | `sandbox` or `production` |
| `FCI_CURRENCY` | ISO currency code, for example `USD` |
| `FCI_ISSUE_DATE` | DD/MM/YYYY or YYYY-MM-DD |
| `FCI_EXCHANGE_RATE` | ILS per one currency unit unless a rate unit is supplied in code |
| `FCI_VAT_RATE` | Decimal VAT rate, for example `0.18` |
| `FCI_LINES_JSON` | JSON array of invoice lines |
| `FCI_INVOICE_DIR` | Local store directory for CLI `create` and `show` |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operational guide |
| `SKILL_HE.md` | Hebrew operational guide with Israeli terminology |
| `references/api-reference.md` | Bank of Israel, VAT, bookkeeping, and API details |
| `references/workflow-guide.md` | End-to-end business workflows |
| `references/troubleshooting.md` | Diagnosis and fixes |
| `references/test-scenarios.md` | Concrete validation cases |
| `references/migration-checklist.md` | Migration from manual or older processes |
| `references/branding-audit.md` | Neutrality and attribution audit |
| `references/hebrew-qa-log.md` | Hebrew quality review log |
| `references/verification-log.md` | Web validation log with two-pass source review |
| `scripts/foreign_currency_invoicing_client.py` | Typed sync and async Python client |
| `scripts/foreign_currency_invoicing_cli.py` | Click CLI implementation |
| `scripts/foreign-currency-invoicing-cli.py` | CLI wrapper for direct script execution |
| `scripts/test_foreign_currency_invoicing_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario scripts |

## Validate

```bash
pytest
python -m compileall scripts/ -q
```

## VAT reminder

Foreign currency does not determine VAT treatment. Check the customer, place of supply, service use, statutory exceptions, and retained evidence before using zero-rate, exemption, reverse-charge, or outside-scope treatment.
