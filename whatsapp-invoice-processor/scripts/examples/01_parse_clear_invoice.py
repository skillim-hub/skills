#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
from whatsapp_invoice_processor import InvoiceProcessor, ProcessingConfig

SAMPLE = 'א.ב. שירותים בע"מ\nח.פ. 516123456\nחשבונית מס/קבלה מס\' 8841\nתאריך 14/02/2026\nסה"כ לפני מע"מ 99.00 ₪\nמע"מ 18% 18.00 ₪\nסה"כ לתשלום 117.00 ₪\nמספר הקצאה 987654321'
parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("WHATSAPP_INVOICE_ENV", "sandbox"))
args = parser.parse_args()
text = os.getenv("WHATSAPP_INVOICE_OCR_TEXT", SAMPLE)
result = InvoiceProcessor(ProcessingConfig.from_env(env=args.env)).parse_text(text)
print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
