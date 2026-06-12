#!/usr/bin/env python3
"""Verify a webhook signature using the raw request body bytes and a shared secret.

Expected output: a JSON object with valid=true when the supplied signature matches the body and secret.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os

from green_invoice_client import GreenInvoiceClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a webhook signature example")
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox", help="Accepted for consistency with other examples; not used by signature verification")
    parser.add_argument("--secret", default=os.getenv("GREEN_INVOICE_WEBHOOK_SECRET", "shared-secret"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    body = b'{"event":"document.created","id":"evt_demo"}'
    signature = "sha256=" + hmac.new(args.secret.encode(), body, hashlib.sha256).hexdigest()
    result = {"environment": args.env, "valid": GreenInvoiceClient.verify_webhook_signature(body, signature, args.secret)}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
