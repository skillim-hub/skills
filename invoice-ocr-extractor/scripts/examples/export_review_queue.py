#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from invoice_ocr_extractor import InvoiceOCRExtractor

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("INVOICE_OCR_ENV", "sandbox"))
args = parser.parse_args()
samples = os.getenv("INVOICE_OCR_REVIEW_TEXTS")
texts = samples.split("\n---\n") if samples else [
    "Clean Ltd.\nInvoice No. 1\nDate: 12/05/2026\nSubtotal NIS 100\nVAT 18% NIS 18\nGrand Total NIS 118",
    "₪120",
    "Bit\nהעברה בוצעה בהצלחה\n₪120\nמספר אישור 998877",
]
extractor = InvoiceOCRExtractor()
queue = []
for index, text in enumerate(texts, start=1):
    invoice = extractor.extract_from_text(text)
    item = extractor.to_review_queue_item(f"sample-{index}", invoice)
    if item["review_required"]:
        queue.append(item)
print(json.dumps({"env": args.env, "review_queue": queue}, ensure_ascii=False, indent=2))
