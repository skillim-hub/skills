from __future__ import annotations

import argparse
import asyncio
import json
import os

from prepayment_deposit_handler_client import AsyncPrepaymentDepositClient, LineItem


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PREPAYMENT_DEPOSIT_ENV", "sandbox"))
    return parser.parse_args()


async def run() -> dict:
    client = AsyncPrepaymentDepositClient()
    result = await client.settle(
        [LineItem(os.getenv("PREPAYMENT_DEPOSIT_LINE_DESC", "Async consulting"), 1, os.getenv("PREPAYMENT_DEPOSIT_NET", "1000"))],
        os.getenv("PREPAYMENT_DEPOSIT_AMOUNT", "200"),
        deposit_reference=os.getenv("PREPAYMENT_DEPOSIT_ID", "DEP-ASYNC-SANDBOX-1"),
    )
    return result.as_dict()


args = parse_args()
print(json.dumps({"environment": args.env, "scenario": "async_client_demo", "result": asyncio.run(run())}, ensure_ascii=False, indent=2))
