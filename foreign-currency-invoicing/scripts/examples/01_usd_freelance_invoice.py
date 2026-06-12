from __future__ import annotations

import argparse
import json
import os

from foreign_currency_invoicing_client import calculate_invoice

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FCI_ENV", "sandbox"))
args = parser.parse_args()

lines = json.loads(os.getenv("FCI_LINES_JSON", '[{"description":"Consulting services","quantity":"12","unit_price":"150","vat_category":"zero","note":"Service supplied to a foreign resident; retain evidence."}]'))
result = calculate_invoice(
    lines,
    os.getenv("FCI_CURRENCY", "USD"),
    os.getenv("FCI_ISSUE_DATE", "02/06/2026"),
    os.getenv("FCI_EXCHANGE_RATE", "3.70"),
)
payload = {"env": args.env, "invoice": result.to_dict()}
print(json.dumps(payload, ensure_ascii=False, indent=2))
