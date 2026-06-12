# Israeli E-Invoice Compliance Skill

Generate, validate, and troubleshoot Israeli Chashbonit Yisrael tax invoice allocation requests. The package includes English and Hebrew skill instructions, API references, a typed Python client, a Typer CLI, and pytest coverage.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

## Quick start

Validate an invoice JSON file:

```bash
python scripts/israeli_e_invoice_compliance_cli.py validate invoice.json
```

Check whether an invoice requires an allocation number:

```bash
python scripts/israeli_e_invoice_compliance_cli.py threshold --invoice-date 2026-06-15 --amount 6000 --invoice-type 305
```

Send an approval request to sandbox:

```bash
python scripts/israeli_e_invoice_compliance_cli.py approve invoice.json --environment sandbox --token "$ITA_TOKEN"
```

## Python example

```python
from scripts.israeli_e_invoice_compliance_client import Environment, InvoiceApprovalRequest, InvoiceComplianceClient

payload = {...}
request = InvoiceApprovalRequest.from_payload(payload)
request.raise_for_validation_errors()
client = InvoiceComplianceClient(access_token="token", environment=Environment.SANDBOX)
result = client.request_approval(request)
print(result.confirmation_number)
```

## File index

| File | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision tree, troubleshooting, and anti-patterns. |
| `SKILL_HE.md` | Hebrew operating guide using Israeli terminology and local date/currency presentation. |
| `references/api-reference.md` | Web-validated source register, endpoint paths, fields, and error tables. |
| `references/troubleshooting.md` | Practical operational playbook for API and business-process failures. |
| `references/test-scenarios.md` | Concrete acceptance and regression scenarios. |
| `scripts/israeli_e_invoice_compliance_client.py` | Typed sync and async Python client plus validation helpers. |
| `scripts/israeli_e_invoice_compliance_cli.py` | Typer CLI for validation, threshold checks, approval calls, and lookups. |
| `scripts/test_israeli_e_invoice_compliance_client.py` | Pytest suite with mocked HTTP calls. |
| `metadata.json` | Skill metadata without author field. |
| `CHANGELOG.md` | Keep-a-Changelog release notes. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Package metadata and pytest configuration. |
| `requirements-dev.txt` | Development and test dependencies. |

## Development

Run the test suite:

```bash
python -m pytest -q
```

## Compliance notes

- Confirm live API access and service permissions through the Tax Authority portal before production use.
- Store the full allocation number and response payload in the audit trail.
- Use the invoice date and amount before VAT for threshold decisions.
- Keep professional tax review for non-standard cases such as reverse charge, zero-rate exports, nonprofit arrangements, or manual invoice books.
