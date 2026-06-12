#!/usr/bin/env python3
"""Create a sandbox tax invoice-receipt for a paid local service sale.

Expected output: a JSON document response containing an issued document id, type 320, official number, totals, and download links when the account is configured to issue signed attachments.
"""
from __future__ import annotations

import argparse
import json
import os

from green_invoice_client import GreenInvoiceClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a tax invoice-receipt example")
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = GreenInvoiceClient(
        key_id=os.environ["GREEN_INVOICE_KEY_ID"],
        key_secret=os.environ["GREEN_INVOICE_KEY_SECRET"],
        environment=args.env,
    )
    payload = {
        "type": 320,
        "date": "2026-05-31",
        "dueDate": "2026-05-31",
        "lang": "he",
        "currency": "ILS",
        "vatType": 0,
        "rounding": True,
        "signed": True,
        "attachment": True,
        "client": {"name": "Example Ltd", "emails": ["finance@example.invalid"], "taxId": "515555555", "country": "IL", "add": True},
        "income": [{"catalogNum": "CONSULT-001", "description": "Consulting services", "quantity": 1, "price": 1000, "currency": "ILS", "vatRate": 0.18, "vatType": 0}],
        "payment": [{"type": 4, "date": "2026-05-31", "price": 1180, "currency": "ILS", "bankName": "Bank Leumi", "bankBranch": "800", "bankAccount": "123456"}],
    }
    try:
        result = client.create_document(payload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        client.close()


if __name__ == "__main__":
    main()
