# Troubleshooting

Use this reference to diagnose validation, rendering, CLI, and allocation-integration failures.

## Installation

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: invoice_generator` | Package was not installed. | Run `pip install -e .` from the package root. |
| CLI command not found | Console script was not installed in the active environment. | Activate the correct virtual environment and run `pip install -e .`. |
| `pytest` not found | Development dependencies are missing. | Run `pip install -r requirements-dev.txt`. |

## Validation

| Symptom | Cause | Fix |
|---|---|---|
| Osek patur tax invoice error | Exempt dealer cannot issue a tax invoice in the modeled workflow. | Use a receipt or change status only from the official registration date. |
| Missing payment error | Receipt or tax invoice receipt has no `payments`. | Add method, amount, date, and reference. |
| Credit note error | Original document is missing. | Add `original_document_number`; add original allocation number when relevant. |
| Discount error | Discount exceeds line amount. | Reduce fixed or percentage discount. |
| Tax id error | Identifier is not 9 digits after normalization. | Enter the correct customer or issuer identifier. |

## Allocation readiness

| Symptom | Cause | Fix |
|---|---|---|
| Allocation warning appears | Document is B2B, taxable, and above threshold. | Request allocation before final issuance. |
| Allocation not required unexpectedly | Customer type is not `business`, amount is below threshold, or issuer status is not taxable. | Review customer classification, totals, and issuer status. |
| Duplicate allocation submission | Same idempotency key was reused. | Retrieve prior result or confirm retry safety. |

## Rendering

| Symptom | Cause | Fix |
|---|---|---|
| Date appears as ISO in payload | Payload uses machine date format. | Render Hebrew markdown to display `DD/MM/YYYY`. |
| Currency displays as `USD` instead of ₪ | Currency is not ILS. | Keep this behavior for foreign-currency documents and add exchange-rate note. |
| Warnings appear in the rendered draft | Validation found review items. | Resolve warnings before official issuance when they affect compliance. |

## CLI storage

| Symptom | Cause | Fix |
|---|---|---|
| Stored id not found | Wrong environment or store directory. | Pass the same `--env` and `--store-dir` used during `create`. |
| Production id resolves to sandbox document | Store directories were shared incorrectly. | Keep separate sandbox and production directories. |
| Create command fails | Validation errors exist. | Run `validate` on the JSON path and correct the errors. |

## Allocation threshold changed during 2026

| Symptom | Cause | Fix |
|---|---|---|
| A June 2026 invoice unexpectedly requires allocation | The active threshold dropped to ₪5,000.00 on 01/06/2026. | Check the document date and compare the amount before VAT to the effective-date threshold. |
| An exact-threshold invoice is flagged by an external system | The local helper uses `>` because official wording says `עולה על`. | Recheck the external system rule and keep the official source in the file. |
| A zero-rate business invoice is not flagged | The helper requires a non-zero VAT component. | Keep zero-rate evidence and do not request allocation unless current official guidance requires it. |
