from __future__ import annotations

import argparse
import json
import os

from foreign_currency_invoicing_client import ExchangeRate, calculate_invoice, parse_date

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FCI_ENV", "sandbox"))
args = parser.parse_args()

rate = ExchangeRate("JPY", os.getenv("FCI_EXCHANGE_RATE", "2.40"), unit=os.getenv("FCI_RATE_UNIT", "100"), date=parse_date(os.getenv("FCI_ISSUE_DATE", "02/06/2026")))
lines = json.loads(os.getenv("FCI_LINES_JSON", '[{"description":"Design license","quantity":"100000","unit_price":"1","vat_category":"standard"}]'))
result = calculate_invoice(lines, "JPY", os.getenv("FCI_ISSUE_DATE", "02/06/2026"), rate)
print(json.dumps({"env": args.env, "invoice": result.to_dict()}, ensure_ascii=False, indent=2))
