from __future__ import annotations

import argparse
import json
import os

from foreign_currency_invoicing_client import calculate_invoice

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FCI_ENV", "sandbox"))
args = parser.parse_args()

lines = json.loads(os.getenv("FCI_LINES_JSON", '[{"description":"Software implementation","quantity":"1","unit_price":"2500","vat_category":"standard"}]'))
result = calculate_invoice(lines, os.getenv("FCI_CURRENCY", "EUR"), os.getenv("FCI_ISSUE_DATE", "02/06/2026"), os.getenv("FCI_EXCHANGE_RATE", "4.02"))
print(json.dumps({"env": args.env, "invoice": result.to_dict()}, ensure_ascii=False, indent=2))
