#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
from whatsapp_invoice_processor import InvoiceProcessor, ProcessingConfig

SAMPLE = "דנה עיצוב פנים\nעוסק פטור 123456789\nקבלה מס' 51\nתאריך 03/01/2026\nסך הכול שולם 750.00 ₪"
parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("WHATSAPP_INVOICE_ENV", "sandbox"))
args = parser.parse_args()
text = os.getenv("WHATSAPP_INVOICE_OCR_TEXT", SAMPLE)
result = InvoiceProcessor(ProcessingConfig.from_env(env=args.env)).parse_text(text)
print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
