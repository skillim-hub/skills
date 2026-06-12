#!/usr/bin/env python3
"""List recent documents with the asynchronous client.

Expected output: a JSON search response containing items, page, pageSize, and total-style pagination fields when returned by the account.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os

from green_invoice_client import GreenInvoiceClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Async document search example")
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    parser.add_argument("--page", type=int, default=0)
    parser.add_argument("--page-size", type=int, default=25)
    return parser.parse_args()


async def run() -> None:
    args = parse_args()
    client = GreenInvoiceClient(key_id=os.environ["GREEN_INVOICE_KEY_ID"], key_secret=os.environ["GREEN_INVOICE_KEY_SECRET"], environment=args.env)
    try:
        result = await client.async_search_documents({"page": args.page, "pageSize": args.page_size})
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(run())
