# Runnable examples

Install the package in editable mode before running examples:

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
export GREEN_INVOICE_KEY_ID="replace-with-key-id"
export GREEN_INVOICE_KEY_SECRET="replace-with-key-secret"
```

Each example accepts `--env sandbox|production` and defaults to sandbox. Every script prints JSON with `ensure_ascii=False` and indentation for review.

Examples:

```bash
python scripts/examples/01_create_tax_invoice_receipt.py --env sandbox
python scripts/examples/02_credit_note_refund.py --env sandbox --original-document-id doc_original_demo
python scripts/examples/03_foreign_currency_export.py --env sandbox
python scripts/examples/04_deposit_prepayment.py --env sandbox
python scripts/examples/05_webhook_verify.py --env sandbox
python scripts/examples/06_async_list_documents.py --env sandbox --page 0 --page-size 25
```
