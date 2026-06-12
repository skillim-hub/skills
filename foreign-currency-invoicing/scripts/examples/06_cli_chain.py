from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FCI_ENV", "sandbox"))
args = parser.parse_args()

create_cmd = [
    sys.executable,
    "-m",
    "foreign_currency_invoicing_cli",
    "create",
    "--env",
    args.env,
    "--currency",
    os.getenv("FCI_CURRENCY", "USD"),
    "--issue-date",
    os.getenv("FCI_ISSUE_DATE", "02/06/2026"),
    "--exchange-rate",
    os.getenv("FCI_EXCHANGE_RATE", "3.70"),
    "--lines-json",
    os.getenv("FCI_LINES_JSON", '[{"description":"Advisory","quantity":"1","unit_price":"750","vat_category":"standard"}]'),
]
create = subprocess.check_output(create_cmd, text=True)
invoice_id = json.loads(create)["id"]
show_cmd = [sys.executable, "-m", "foreign_currency_invoicing_cli", "show", "--env", args.env, invoice_id]
shown = subprocess.check_output(show_cmd, text=True)
print(json.dumps({"env": args.env, "created_id": invoice_id, "shown": json.loads(shown)}, ensure_ascii=False, indent=2))
