# Green Invoice Integration

A compact, testable skill package for Green Invoice API workflows in Israel. It covers document creation and retrieval, customer management, payment-link request preparation, webhook handling, document type mapping, current VAT assumptions, and allocation-number checks.

## Install for local development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

## Quick start

Authenticate in sandbox:

```bash
python scripts/green_invoice_integration_cli.py auth \
  --env sandbox \
  --key-id "$GREEN_INVOICE_KEY_ID" \
  --key-secret "$GREEN_INVOICE_KEY_SECRET"
```

Verify credentials:

```bash
python scripts/green_invoice_integration_cli.py whoami \
  --env sandbox \
  --token "$GREEN_INVOICE_TOKEN"
```

Create a sandbox tax invoice-receipt:

```bash
python scripts/green_invoice_integration_cli.py create-document \
  --env sandbox \
  --token "$GREEN_INVOICE_TOKEN" \
  --type 320 \
  --client-name "Demo Client Ltd" \
  --client-email billing@example.com \
  --description "Consulting service" \
  --amount 1000 \
  --currency ILS \
  --date 2026-06-05 \
  --payment-method wire-transfer
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision tree, troubleshooting, and anti-patterns |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology and ₪ examples |
| `references/api-reference.md` | Web-validated API, regulation, endpoint, and error reference |
| `references/troubleshooting.md` | Debugging and escalation guide |
| `references/test-scenarios.md` | Sandbox and production-cutover scenarios |
| `scripts/green_invoice_integration_client.py` | Typed sync and async Python client |
| `scripts/green_invoice_integration_cli.py` | Typer CLI for practical operations |
| `scripts/test_green_invoice_integration_client.py` | Pytest suite |
| `metadata.json` | Package metadata |
| `CHANGELOG.md` | Keep a Changelog history |
| `LICENSE` | MIT license |
| `pyproject.toml` | Python project/test configuration |
| `requirements-dev.txt` | Development dependencies |

## Run tests

```bash
pytest -q
```

## Safety defaults

- Use sandbox first.
- Keep secrets in environment variables or a secret manager.
- Search customers before creating customers.
- Fetch documents after creation and verify totals, document type, and allocation number when relevant.
- Deduplicate webhook events before side effects.
