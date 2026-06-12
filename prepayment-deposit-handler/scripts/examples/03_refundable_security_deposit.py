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
record = client.create_record(
    deposit_id=os.getenv("PREPAYMENT_DEPOSIT_ID", "SEC-SANDBOX-1001"),
    contract_id=os.getenv("PREPAYMENT_DEPOSIT_CONTRACT_ID", "RENT-44"),
    received_date=os.getenv("PREPAYMENT_DEPOSIT_RECEIVED_DATE", "15/03/2026"),
    amount=os.getenv("PREPAYMENT_DEPOSIT_AMOUNT", "1500"),
    payer_name=os.getenv("PREPAYMENT_DEPOSIT_PAYER_NAME", "Customer"),
    payee_name=os.getenv("PREPAYMENT_DEPOSIT_PAYEE_NAME", "Equipment Rental"),
    nature="security_deposit_held_in_trust",
    payment_method=os.getenv("PREPAYMENT_DEPOSIT_PAYMENT_METHOD", "bank_transfer"),
    refundable=True,
    reference=os.getenv("PREPAYMENT_DEPOSIT_PAYMENT_REFERENCE", "Sandbox bank transfer 9912"),
)
print_payload({"environment": args.env, "scenario": "refundable_security_deposit", "result": record.as_dict()})
