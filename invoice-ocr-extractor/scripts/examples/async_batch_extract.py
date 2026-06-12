#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os

from invoice_ocr_extractor import InvoiceOCRExtractor

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("INVOICE_OCR_ENV", "sandbox"))
args = parser.parse_args()
texts = os.getenv("INVOICE_OCR_TEXTS")
items = texts.split("\n---\n") if texts else [
    "Async A Ltd.\nInvoice No. A1\nDate: 12/05/2026\nTotal NIS 20.00",
    "Async B Ltd.\nInvoice No. B2\nDate: 13/05/2026\nTotal NIS 30.00",
]

async def main() -> None:
    extractor = InvoiceOCRExtractor()
    results = await asyncio.gather(*(extractor.extract_from_text_async(text) for text in items))
    print(json.dumps({"env": args.env, "results": [result.to_dict() for result in results]}, ensure_ascii=False, indent=2))

asyncio.run(main())
