# Migration Checklist

Use this checklist when moving from manual invoices, spreadsheets, quote-only tools, or an older draft package into the installable invoice-generator package.

## Preparation

- Freeze the latest official document numbers for each series.
- Export customer names, identifiers, addresses, and customer type classifications.
- Export product or service descriptions, units, default prices, and VAT treatment.
- Identify which customers are businesses that may need allocation-number workflows.
- Identify open credit-note cases and original document references.
- Document the official accounting system that will issue final documents.

## Package migration

- Replace hyphenated script imports with `from invoice_generator import ...`.
- Install with `pip install -e .`.
- Install test dependencies with `pip install -r requirements-dev.txt`.
- Use `invoice-generator` as the CLI entry point.
- Use `scripts/invoice_generator_client.py` and `scripts/invoice_generator_cli.py` only as compatibility wrappers.
- Remove local path-import workarounds from downstream projects.

## Data migration

- Convert a recent tax invoice into `examples/tax-invoice.json` format.
- Convert a recent receipt into `examples/receipt-patur.json` or another receipt fixture.
- Convert a recent credit note into `examples/credit-note.json` format.
- Validate identifiers as 9-digit values where applicable.
- Convert Hebrew display dates to `DD/MM/YYYY` or ISO dates.
- Keep original document numbers unchanged.

## Allocation integration

- Rebuild allocation threshold fixtures with the 2026 effective-date schedule: ₪10,000.00 from 01/01/2026 and ₪5,000.00 from 01/06/2026.
- Treat the allocation trigger as greater than the active threshold, not equal to it.
- Add tests for zero-rate and exempt documents above the threshold because they should not trigger allocation in this helper.
- Map `to_shaam_payload()` to the current official allocation request schema.
- Keep separate sandbox and production credentials.
- Use idempotency keys for safe retries.
- Store request payloads, response payloads, allocation numbers, and final documents.
- Reconcile sandbox behavior before production use.

## Acceptance checks

- Run `pytest`.
- Run `python -m compileall scripts/ -q`.
- Compare generated totals against historical documents.
- Confirm Hebrew output uses professional terminology, ₪ amounts, and `DD/MM/YYYY` dates.
- Confirm no obsolete branding, visual promotional assets, handles, or ownership metadata remain.
- Confirm the license uses the neutral MIT placeholder.
