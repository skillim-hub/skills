#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
from decimal import Decimal
from whatsapp_invoice_processor import InvoiceProcessor, ProcessingConfig, allocation_threshold_for_date

SAMPLE = 'ספק ציוד משרדי בע"מ\nח.פ. 515555555\nחשבונית מס 3001\nתאריך 20/02/2026\nסה"כ לפני מע"מ 30000.00 ₪\nמע"מ 5400.00 ₪\nסה"כ לתשלום 35400.00 ₪'
parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("WHATSAPP_INVOICE_ENV", "sandbox"))
args = parser.parse_args()
text = os.getenv("WHATSAPP_INVOICE_OCR_TEXT", SAMPLE)
threshold = Decimal(os.getenv("WHATSAPP_INVOICE_ALLOCATION_THRESHOLD", str(allocation_threshold_for_date("2026-06-03") or Decimal("5000"))))
config = ProcessingConfig.from_env(env=args.env)
config = ProcessingConfig(allocation_policy_enabled=True, allocation_threshold_before_vat=threshold, default_ocr_confidence=config.default_ocr_confidence)
result = InvoiceProcessor(config).parse_text(text)
print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
