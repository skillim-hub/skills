#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from invoice_ocr_extractor import InvoiceOCRExtractor, export_csv

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("INVOICE_OCR_ENV", "sandbox"))
parser.add_argument("--input-dir", default=os.getenv("INVOICE_OCR_INPUT_DIR"))
parser.add_argument("--output", default=os.getenv("INVOICE_OCR_OUTPUT"))
args = parser.parse_args()

with tempfile.TemporaryDirectory() as tmp:
    folder = Path(args.input_dir) if args.input_dir else Path(tmp)
    if not args.input_dir:
        (folder / "a.txt").write_text("A Ltd.\nInvoice No. 1\nDate: 12/05/2026\nTotal NIS 20.00", encoding="utf-8")
        (folder / "b.txt").write_text("B Ltd.\nInvoice No. 2\nDate: 13/05/2026\nTotal NIS 30.00", encoding="utf-8")
    output = Path(args.output) if args.output else folder / "expenses.csv"
    extractor = InvoiceOCRExtractor()
    rows = extractor.batch_extract(folder)
    export_csv(rows, output)
    print(json.dumps({"env": args.env, "processed": len(rows), "output": str(output), "record_ids": [r.record_id for _, r in rows]}, ensure_ascii=False, indent=2))
