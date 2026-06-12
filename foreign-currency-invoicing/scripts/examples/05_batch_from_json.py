from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from foreign_currency_invoicing_client import calculate_invoice

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FCI_ENV", "sandbox"))
parser.add_argument("--file", default=os.getenv("FCI_BATCH_FILE", ""))
args = parser.parse_args()

if args.file:
    batch = json.loads(Path(args.file).read_text(encoding="utf-8"))
else:
    batch = json.loads(os.getenv("FCI_BATCH_JSON", '[{"currency":"USD","issue_date":"02/06/2026","exchange_rate":"3.70","lines":[{"description":"Retainer","quantity":"1","unit_price":"500","vat_category":"zero","note":"Foreign-resident customer evidence retained."}]}]'))

results = [calculate_invoice(item["lines"], item["currency"], item["issue_date"], item.get("exchange_rate")).to_dict() for item in batch]
print(json.dumps({"env": args.env, "results": results}, ensure_ascii=False, indent=2))
