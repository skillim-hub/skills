# Migration Checklist

Use this checklist when replacing spreadsheets, manual calculations, or an older helper.

## Inventory current process

- List all currencies used in the last year.
- Identify how exchange rates are sourced today.
- Identify whether rates are stored with issued invoices.
- Identify all VAT categories used in invoices.
- Identify accounting-system import formats.
- Identify who approves zero-rate and exemption decisions.

## Clean data before migration

- Normalize dates to DD/MM/YYYY for Israeli-facing records.
- Normalize JSON and CSV decimal values to dot decimals.
- Replace free-text VAT labels with `standard`, `zero`, `exempt`, `reverse_charge`, or `out_of_scope`.
- Add evidence notes for non-standard VAT categories.
- Preserve original document numbers and source files.

## Replace old scripts

- Delete any hyphenated client import path.
- Import from `foreign_currency_invoicing_client` after `pip install -e .`.
- Use the CLI command `foreign-currency-invoicing` for operational runs.
- Keep direct wrapper script execution only for local convenience.
- Update batch jobs to pass `--env sandbox` during testing and `--env production` after approval.

## Validate migrated results

- Recalculate a sample of historical invoices in each currency.
- Compare NIS net, VAT, and total amounts against accounting records.
- Check JPY or other unit-based rates manually.
- Reconcile rounding policy.
- Confirm zero-rate evidence files exist.

## Cutover plan

1. Install the package in a sandbox environment.
2. Run the test suite.
3. Process one day of sample invoices.
4. Review differences with accounting.
5. Freeze spreadsheet formulas or old helper scripts.
6. Enable production CLI jobs.
7. Monitor first production invoices for rate, VAT, and rounding issues.

## Rollback plan

- Keep old exports read-only for audit.
- Retain all v2 JSON outputs for comparison.
- If a production defect appears, stop issuing new documents, identify affected invoice ids, and use the accounting system correction workflow.
