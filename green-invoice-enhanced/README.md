# Green Invoice (Morning) API Skill

Neutral technical reference and tooling for integrating with the Green Invoice (Morning) API for Israeli invoices, receipts, client records, catalog items, expenses, payments, and webhooks.

## Contents

```text
SKILL.md
SKILL_HE.md
metadata.json
README.md
CHANGELOG.md
LICENSE
references/
  api-reference.md
  document-workflows.md
  migration-checklist.md
  test-scenarios.md
  troubleshooting.md
scripts/
  green_invoice_client.py
  green-invoice-cli.py
  test_green_invoice_client.py
  examples/
```

## Installation

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

Use sandbox credentials while developing:

```bash
export GREEN_INVOICE_ENV=sandbox
export GREEN_INVOICE_KEY_ID="replace-with-key-id"
export GREEN_INVOICE_KEY_SECRET="replace-with-key-secret"
```

## Quick start: verify auth

```bash
python scripts/green-invoice-cli.py --env sandbox auth verify --json
```

Python:

```python
from green_invoice_client import GreenInvoiceClient

client = GreenInvoiceClient.from_env()
try:
    client.authenticate()
    print(client.verify_auth())
finally:
    client.close()
```

## Quick start: create one invoice end-to-end

Create `invoice.json`:

```json
{
  "type": 320,
  "date": "2026-05-31",
  "dueDate": "2026-05-31",
  "lang": "he",
  "currency": "ILS",
  "vatType": 0,
  "rounding": true,
  "signed": true,
  "attachment": true,
  "client": {
    "name": "Example Ltd",
    "emails": ["finance@example.co.il"],
    "taxId": "515555555",
    "country": "IL",
    "add": true
  },
  "income": [
    {
      "catalogNum": "CONSULT-001",
      "description": "Consulting services",
      "quantity": 1,
      "price": 1000,
      "currency": "ILS",
      "vatRate": 0.18,
      "vatType": 0
    }
  ],
  "payment": [
    {
      "type": 4,
      "date": "2026-05-31",
      "price": 1180,
      "currency": "ILS",
      "bankName": "Bank Leumi",
      "bankBranch": "800",
      "bankAccount": "123456"
    }
  ]
}
```

Issue it in sandbox, save the create response, extract the issued document id, and email the same document:

```bash
python scripts/green-invoice-cli.py --env sandbox docs create invoice.json --json | tee create-response.json
DOC_ID="$(jq -r '.id' create-response.json)"
python scripts/green-invoice-cli.py --env sandbox docs email "$DOC_ID" \
  --to finance@example.co.il \
  --subject "חשבונית מס/קבלה" \
  --message "שלום, מצורפת חשבונית מס/קבלה."
```

## CLI examples

```bash
python scripts/green-invoice-cli.py clients list --name Example
python scripts/green-invoice-cli.py clients get cli_2001 --json
python scripts/green-invoice-cli.py items create item.json
python scripts/green-invoice-cli.py docs list --from-date 2026-05-01 --to-date 2026-05-31 --type 320
python scripts/green-invoice-cli.py payments record payment.json --json
python scripts/green-invoice-cli.py webhooks register webhook.json
python scripts/green-invoice-cli.py expenses list --from-date 2026-05-01 --to-date 2026-05-31
```

## Python client

The client supports synchronous and asynchronous usage:

```python
from green_invoice_client import GreenInvoiceClient

client = GreenInvoiceClient.from_env()
try:
    document = client.create_document({
        "type": 320,
        "date": "2026-05-31",
        "client": {"name": "Example Ltd", "emails": ["finance@example.co.il"], "add": True},
        "income": [{"description": "Service", "quantity": 1, "price": 1000, "currency": "ILS"}],
        "payment": [{"type": 4, "date": "2026-05-31", "price": 1180, "currency": "ILS"}]
    })
    print(document["id"])
finally:
    client.close()
```

Async:

```python
import asyncio
from green_invoice_client import GreenInvoiceClient

async def main():
    client = GreenInvoiceClient.from_env()
    try:
        result = await client.async_search_documents({"page": 0, "pageSize": 25})
        print(result)
    finally:
        await client.aclose()

asyncio.run(main())
```

## Run tests

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
python -m pytest scripts/test_green_invoice_client.py
```

The test suite uses mocked HTTP transports and does not call the live API.

## References

- `references/api-reference.md`: endpoints, payloads, errors, pagination, and webhooks.
- `references/document-workflows.md`: lifecycle guide for all 13 document types.
- `references/troubleshooting.md`: symptom-diagnosis-fix tables and diagnostic curl snippets.
- `references/test-scenarios.md`: sandbox test matrix.
- `references/migration-checklist.md`: migration from manual issuance or another provider.

## Production notes

- Separate sandbox and production credentials.
- Keep API secrets out of source control.
- Confirm plan access before enabling API and webhook flows.
- Complete Tax Authority authorization when B2B tax invoices require allocation numbers.
- Store document ids, official numbers, totals, currency, download links, and allocation numbers.
- Use application-level idempotency for create operations.
- Validate webhook signatures using raw request body bytes.
