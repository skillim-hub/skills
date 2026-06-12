#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from invoice_ocr_extractor import InvoiceOCRExtractor, load_invoice_json

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("INVOICE_OCR_ENV", "sandbox"))
parser.add_argument("--json-file", default=os.getenv("INVOICE_OCR_JSON_FILE"))
parser.add_argument("--expected-id", default=os.getenv("INVOICE_OCR_EXPECTED_ID"))
args = parser.parse_args()

if args.json_file:
    data = load_invoice_json(Path(args.json_file))
else:
    result = InvoiceOCRExtractor().extract_from_text("Demo Ltd.\nInvoice No. 1\nDate: 12/05/2026\nTotal NIS 20.00")
    data = result.to_dict()
    args.expected_id = args.expected_id or result.record_id
errors = InvoiceOCRExtractor().validate(data, expected_id=args.expected_id)
print(json.dumps({"env": args.env, "valid": not bool(errors), "errors": errors, "record_id": data.get("record_id")}, ensure_ascii=False, indent=2))
