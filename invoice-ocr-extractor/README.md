# Invoice OCR Extractor

Neutral package for extracting expense-entry data from Hebrew and English invoice OCR text, with Israeli localization for ₪ amounts and `DD/MM/YYYY` dates.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create `invoice.txt`:

```text
א.ב. שירותי מחשוב בע"מ
ח.פ. 512345678
חשבונית מס קבלה מס' 2026-104
תאריך: 21/05/2026
סה"כ לפני מע"מ: ₪1,000.00
מע"מ 18%: ₪180.00
סה"כ לתשלום: ₪1,180.00
```

Create the extraction response:

```bash
python -m invoice_ocr_extractor.cli parse --text-file invoice.txt --pretty > create-response.json
```

Extract the `record_id` from the create response and use it in the validation step:

```bash
EXTRACTION_ID=$(python -c 'import json; print(json.load(open("create-response.json", encoding="utf-8"))["record_id"])')
python -m invoice_ocr_extractor.cli validate --json-file create-response.json --expected-id "$EXTRACTION_ID"
```

Import from Python:

```python
from invoice_ocr_extractor import InvoiceOCRExtractor

extractor = InvoiceOCRExtractor()
result = extractor.extract_from_text("חשבונית מס קבלה מס' 100\nסה\"כ לתשלום ₪118\nמע\"מ 18% ₪18")
print(result.to_json())
```

## Batch processing

```bash
python -m invoice_ocr_extractor.cli batch ./ocr-texts --output expenses.csv --pretty-summary
```

## Validate JSON

```bash
python -m invoice_ocr_extractor.cli validate --json-file create-response.json --expected-id "$EXTRACTION_ID"
```

## Run tests

```bash
pytest -q
python -m compileall scripts/ -q
```

## File index

```text
SKILL.md
SKILL_HE.md
README.md
CHANGELOG.md
LICENSE
metadata.json
pyproject.toml
requirements-dev.txt
src/invoice_ocr_extractor/__init__.py
src/invoice_ocr_extractor/client.py
src/invoice_ocr_extractor/cli.py
references/api-reference.md
references/workflow-guide.md
references/troubleshooting.md
references/test-scenarios.md
references/migration-checklist.md
references/branding-audit.md
references/hebrew-qa-log.md
references/verification-log.md
scripts/invoice_ocr_extractor_client.py
scripts/invoice_ocr_extractor_cli.py
scripts/test_invoice_ocr_extractor_client.py
scripts/examples/parse_hebrew_invoice.py
scripts/examples/batch_folder_to_csv.py
scripts/examples/validate_extraction.py
scripts/examples/async_batch_extract.py
scripts/examples/export_review_queue.py
```

## Verified regulatory notes

The package includes `references/verification-log.md`, a two-pass web validation record for the current VAT rate, Israel Invoices allocation thresholds, Tax Authority endpoint paths, official terminology, privacy, and recordkeeping references.

## Notes

Image OCR requires an OCR engine outside this package. The included code parses OCR text and provides a stable integration point for image and PDF OCR. Require manual review for low-confidence or flagged records.
