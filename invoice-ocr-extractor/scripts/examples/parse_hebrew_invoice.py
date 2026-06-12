#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from invoice_ocr_extractor import ExtractorConfig, InvoiceOCRExtractor

DEFAULT_TEXT = """א.ב. שירותי מחשוב בע"מ
ח.פ. 512345678
חשבונית מס קבלה מס' 2026-104
תאריך: 21/05/2026
סה"כ לפני מע"מ: ₪1,000.00
מע"מ 18%: ₪180.00
סה"כ לתשלום: ₪1,180.00
"""

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("INVOICE_OCR_ENV", "sandbox"))
args = parser.parse_args()
text = os.getenv("INVOICE_OCR_TEXT", DEFAULT_TEXT)
vat_rate = float(os.getenv("INVOICE_OCR_DEFAULT_VAT_RATE", "18"))
extractor = InvoiceOCRExtractor(ExtractorConfig(default_vat_rate=vat_rate))
result = extractor.extract_from_text(text)
print(json.dumps({"env": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))
