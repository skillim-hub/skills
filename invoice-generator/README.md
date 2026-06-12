# Invoice Generator

Draft and validate Israeli accounting-document payloads for small businesses, freelancers, and consumer-facing service providers. Use the package to choose the correct document type, calculate VAT, detect allocation-number requirements, render a Hebrew review draft, and prepare a semantic allocation request payload.

Use the output as a drafting and validation aid. Issue official documents only through registered accounting software, an approved bookkeeping workflow, or the Israel Tax Authority systems that apply to the business.

## Install

```bash
cd invoice-generator
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with a stored document id

Create a sample JSON file, store it, extract the returned id, and use the id in the next step.

```bash
invoice-generator example --kind tax-invoice > sample.json
CREATE_RESPONSE=$(invoice-generator create sample.json --env sandbox)
echo "$CREATE_RESPONSE"
DOCUMENT_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")
invoice-generator validate "$DOCUMENT_ID" --env sandbox
invoice-generator render "$DOCUMENT_ID" --env sandbox --output sample.md
invoice-generator shaam-payload "$DOCUMENT_ID" --env sandbox --output allocation-payload.json
```

## Python quick start

```python
from invoice_generator import DocumentSpec, render_hebrew_markdown, sample_tax_invoice

document = DocumentSpec.from_dict(sample_tax_invoice())
result = document.validate()
result.raise_for_errors()
print(document.requires_allocation())
print(render_hebrew_markdown(document))
```


## Web-validated rule snapshot

As of 01/06/2026, the helper defaults to 18% standard VAT from 01/01/2025 and an allocation threshold of ₪5,000.00 before VAT for taxable B2B documents dated 01/06/2026 or later. For documents dated 01/01/2026 through 31/05/2026, the threshold is ₪10,000.00. Treat the trigger as greater than the active threshold.

## CLI commands

```bash
invoice-generator example --kind receipt
invoice-generator create examples/tax-invoice.json --env sandbox
invoice-generator validate examples/receipt-patur.json --env sandbox
invoice-generator allocation-required examples/tax-invoice.json --env sandbox
invoice-generator shaam-payload examples/tax-invoice.json --env sandbox
invoice-generator render examples/tax-invoice.json --env sandbox --output invoice.md
invoice-generator totals examples/tax-invoice.json --env sandbox
```

Every command that reads or stores a document accepts `--env sandbox|production`. Store documents separately per environment to prevent accidental reuse of a sandbox draft in a production workflow.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide for Israeli invoices, receipts, credit notes, allocation checks, examples, decision trees, anti-patterns, and production checklist. |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, ₪ amounts, and DD/MM/YYYY dates. |
| `references/api-reference.md` | API and regulation reference with payload examples, response examples, and error tables. |
| `references/workflow-guide.md` | End-to-end workflows for common Israeli business scenarios. |
| `references/troubleshooting.md` | Failure diagnosis and corrective action reference. |
| `references/test-scenarios.md` | More than twenty concrete QA scenarios. |
| `references/migration-checklist.md` | Migration checklist from manual, spreadsheet, or quote-only workflows. |
| `references/branding-audit.md` | Neutrality and branding audit report. |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization QA log. |
| `references/verification-log.md` | Web validation log with two-pass source checks and correction status. |
| `src/invoice_generator/client.py` | Typed sync and async client, validators, renderer, samples, and local store. |
| `src/invoice_generator/cli.py` | Typer CLI implementation. |
| `scripts/invoice_generator_client.py` | Import-safe client helper entry point. |
| `scripts/invoice_generator_cli.py` | Import-safe CLI entry point. |
| `scripts/test_invoice_generator_client.py` | Pytest suite. |
| `scripts/examples/` | Runnable scenario scripts using environment variables and `--env`. |
| `examples/` | JSON document examples. |
| `metadata.json` | Skill metadata without author fields. |
| `pyproject.toml` | Installable Python project configuration. |
| `requirements-dev.txt` | Development and test dependencies. |

## Environment variables used by examples

| Variable | Purpose |
|---|---|
| `INVOICE_GENERATOR_ENV` | Default environment for example scripts when `--env` is not supplied. |
| `SHAAM_SANDBOX_BASE_URL` | Sandbox allocation API base URL for integration tests or live sandbox calls. |
| `SHAAM_PRODUCTION_BASE_URL` | Production allocation API base URL for live calls. |
| `SHAAM_ACCESS_TOKEN` | Bearer token used by allocation-request examples when explicit network submission is requested. |

## Operational cautions

Verify VAT rates, exempt dealer ceilings, allocation thresholds, and official API endpoints before production use. Preserve the original document number sequence. Do not delete issued documents; issue a credit note or another permitted corrective document. Store allocation numbers with the issued tax invoice and display them clearly for VAT-registered business customers.
