#!/usr/bin/env python3
"""Create a foreign-currency export invoice-receipt using USD amounts.

Expected output: a JSON document response containing type 320, currency USD, the account-applied exchange rate fields when returned, and English download links when enabled.
"""
from __future__ import annotations

import argparse
import json
import os

from green_invoice_client import GreenInvoiceClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a foreign-currency export example")
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = GreenInvoiceClient(key_id=os.environ["GREEN_INVOICE_KEY_ID"], key_secret=os.environ["GREEN_INVOICE_KEY_SECRET"], environment=args.env)
    payload = {
        "type": 320,
        "date": "2026-05-31",
        "dueDate": "2026-05-31",
        "lang": "en",
        "currency": "USD",
        "currencyRate": 3.70,
        "vatType": 1,
        "client": {"name": "Example US LLC", "emails": ["ap@example.invalid"], "country": "US", "add": True},
        "income": [{"description": "Export consulting services", "quantity": 1, "price": 2000, "currency": "USD", "vatRate": 0, "vatType": 2}],
        "payment": [{"type": 3, "date": "2026-05-31", "price": 2000, "currency": "USD", "bankName": "International bank transfer"}],
        "remarks": "VAT treatment must be confirmed before production issuance.",
    }
    try:
        print(json.dumps(client.create_document(payload), ensure_ascii=False, indent=2))
    finally:
        client.close()


if __name__ == "__main__":
    main()
