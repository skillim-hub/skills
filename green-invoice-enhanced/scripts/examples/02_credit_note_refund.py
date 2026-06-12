#!/usr/bin/env python3
"""Create a credit note for a partial refund of a previously issued tax invoice.

Expected output: a JSON document response containing type 330, negative or credit totals as represented by the account, and links or relation fields to the original document when the API accepts the linkage.
"""
from __future__ import annotations

import argparse
import json
import os

from green_invoice_client import GreenInvoiceClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a credit note refund example")
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    parser.add_argument("--original-document-id", default="doc_original_demo")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = GreenInvoiceClient(key_id=os.environ["GREEN_INVOICE_KEY_ID"], key_secret=os.environ["GREEN_INVOICE_KEY_SECRET"], environment=args.env)
    payload = {
        "type": 330,
        "date": "2026-05-31",
        "lang": "he",
        "currency": "ILS",
        "vatType": 0,
        "client": {"name": "Example Ltd", "emails": ["finance@example.invalid"], "taxId": "515555555", "country": "IL"},
        "income": [{"description": "Partial service refund", "quantity": 1, "price": 250, "currency": "ILS", "vatRate": 0.18, "vatType": 0}],
        "linkedDocumentIds": [args.original_document_id],
        "remarks": "Partial refund against original tax invoice.",
    }
    try:
        print(json.dumps(client.create_document(payload), ensure_ascii=False, indent=2))
    finally:
        client.close()


if __name__ == "__main__":
    main()
