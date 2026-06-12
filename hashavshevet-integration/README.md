# Hashavshevet Integration

Practical integration helpers for Hashavshevet export/import workflows, customer and supplier sync, journal entry pulls, BTKN transfer generation, OPENFORMAT/BKMV staging checks, Israel Invoices allocation-number validation, Hebrew encoding conversion, and multi-company operation.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

For minimal runtime use:

```bash
pip install -r requirements-dev.txt
```

## Quick start

Calculate VAT and allocation-number status:

```bash
python scripts/hashavshevet_integration_cli.py vat 12000 --date 2026-01-15 --customer-vat 514087337
```

Convert a Hebrew CSV export to JSON:

```bash
python scripts/hashavshevet_integration_cli.py csv-to-json customers.csv customers.json
```

Generate a BTKN transfer file from JSON rows:

```bash
python scripts/hashavshevet_integration_cli.py generate-btkn entries.json BTKN.TXT
```

Run tests:

```bash
pytest
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision tree, troubleshooting, and anti-patterns. |
| `SKILL_HE.md` | Hebrew operating guide with Israeli terminology and DD-MM-YYYY examples. |
| `references/api-reference.md` | Web-validated API and regulation reference with source URLs and error tables. |
| `references/troubleshooting.md` | Operational troubleshooting checklist. |
| `references/test-scenarios.md` | Concrete test and acceptance scenarios. |
| `scripts/hashavshevet_integration_client.py` | Typed sync and async client plus validation, encoding, CSV, BTKN, and staging helpers. |
| `scripts/hashavshevet_integration_cli.py` | Typer CLI for VAT checks, conversion, BTKN generation, and payload validation. |
| `scripts/test_hashavshevet_integration_client.py` | Pytest suite covering validation, calculations, file generation, and HTTP clients. |
| `metadata.json` | Skill metadata without author fields. |
| `CHANGELOG.md` | Keep-a-Changelog release notes. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Python project metadata and dependencies. |
| `requirements-dev.txt` | Lightweight development/test dependencies. |

## Production notes

Keep raw source files immutable. Use company-specific folders, tokens, account mappings, and logs. Run dry-run validation before import. Treat BTKN output as a deterministic staging bundle unless the production target explicitly accepts that structure. Use official Hashavshevet exports or vendor APIs for regulated handoff.
