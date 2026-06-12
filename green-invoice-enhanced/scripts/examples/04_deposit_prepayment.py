#!/usr/bin/env python3
"""Record a deposit or prepayment as a receipt-style document.

Expected output: a JSON document response containing type 400 with one payment row and remarks that identify the future service or order covered by the prepayment.
"""
from __future__ import annotations

import argparse
import json
import os

from green_invoice_client import GreenInvoiceClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a deposit/prepayment receipt example")
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = GreenInvoiceClient(key_id=os.environ["GREEN_INVOICE_KEY_ID"], key_secret=os.environ["GREEN_INVOICE_KEY_SECRET"], environment=args.env)
    try:
        result = client.record_payment(
            client={"name": "Workshop Client", "emails": ["client@example.invalid"], "country": "IL"},
            payment=[{"type": 2, "date": "2026-05-31", "price": 500, "currency": "ILS", "chequeNum": "10001", "bankName": "Bank Hapoalim", "bankBranch": "001", "bankAccount": "987654"}],
            date="2026-05-31",
            remarks="Deposit received for future workshop delivery.",
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        client.close()


if __name__ == "__main__":
    main()
