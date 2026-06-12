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
business_type = os.getenv("PREPAYMENT_DEPOSIT_BUSINESS_TYPE", "osek_murshe")
result = client.classify(
    nature="advance_for_taxable_supply",
    business_type=business_type,
    refundable=False,
)
print_payload({"environment": args.env, "scenario": "classify_advance", "result": result.as_dict()})
