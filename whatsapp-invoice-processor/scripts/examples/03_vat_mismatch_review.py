#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
from whatsapp_invoice_processor import InvoiceProcessor, ProcessingConfig

SAMPLE = 'כהן ייעוץ\nע.מ. 012345678\nחשבונית מס 1007\nתאריך 05/02/2026\nלפני מע"מ 100.00 ₪\nמע"מ 12.00 ₪\nסה"כ 112.00 ₪'
parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("WHATSAPP_INVOICE_ENV", "sandbox"))
args = parser.parse_args()
text = os.getenv("WHATSAPP_INVOICE_OCR_TEXT", SAMPLE)
result = InvoiceProcessor(ProcessingConfig.from_env(env=args.env)).parse_text(text)
print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
