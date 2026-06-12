#!/usr/bin/env python3
from __future__ import annotations
import argparse
import asyncio
import json
import os
from whatsapp_invoice_processor import InvoiceProcessor, ProcessingConfig

SAMPLE = 'א.ב. שירותים בע"מ\nח.פ. 516123456\nחשבונית מס/קבלה מס\' 8841\nתאריך 14/02/2026\nסה"כ לתשלום 117.00 ₪'
parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("WHATSAPP_INVOICE_ENV", "sandbox"))
args = parser.parse_args()

async def main() -> None:
    text = os.getenv("WHATSAPP_INVOICE_OCR_TEXT", SAMPLE)
    processor = InvoiceProcessor(ProcessingConfig.from_env(env=args.env))
    results = await asyncio.gather(processor.parse_text_async(text), processor.parse_text_async(text))
    print(json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2))

asyncio.run(main())
