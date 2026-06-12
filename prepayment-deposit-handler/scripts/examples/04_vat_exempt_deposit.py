from __future__ import annotations

import argparse
import json
import os

from prepayment_deposit_handler_client import LineItem, PrepaymentDepositClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PREPAYMENT_DEPOSIT_ENV", "sandbox"))
    return parser.parse_args()


def print_payload(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))

args = parse_args()
client = PrepaymentDepositClient()
result = client.settle(
    [LineItem(os.getenv("PREPAYMENT_DEPOSIT_LINE_DESC", "Private lesson package"), 1, os.getenv("PREPAYMENT_DEPOSIT_NET", "2500"), "0.18")],
    deposit=os.getenv("PREPAYMENT_DEPOSIT_AMOUNT", "500"),
    business_type="osek_patur",
    deposit_reference=os.getenv("PREPAYMENT_DEPOSIT_ID", "DEP-PATUR-SANDBOX-1"),
)
print_payload({"environment": args.env, "scenario": "vat_exempt_deposit", "result": result.as_dict()})
