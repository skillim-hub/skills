from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import date

from domestic_bank_transfer_helper_client import TransferRequest, async_validate_transfers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate several transfers asynchronously.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DOMESTIC_TRANSFER_ENV", "sandbox"))
    return parser.parse_args()


async def run(env: str) -> None:
    requests = [
        TransferRequest(
            recipient_name=os.getenv("DBTF_RECIPIENT_NAME", "Supplier A"),
            bank_code=os.getenv("DBTF_BANK_CODE", "12"),
            branch_code=os.getenv("DBTF_BRANCH_CODE", "456"),
            account_number=os.getenv("DBTF_ACCOUNT_NUMBER", "123456789"),
            amount_ils=os.getenv("DBTF_AMOUNT_ILS", "1000"),
            value_date=os.getenv("DBTF_VALUE_DATE", "03/06/2026"),
            purpose=os.getenv("DBTF_PURPOSE", "Invoice A"),
        ),
        TransferRequest(
            recipient_name="Supplier B",
            bank_code="10",
            branch_code="800",
            account_number="987654321",
            amount_ils="1500",
            value_date="03/06/2026",
            purpose="Invoice B",
        ),
    ]
    reports = await async_validate_transfers(requests, env=env, today=date(2026, 6, 2))
    print(json.dumps({"reports": [report.to_dict() for report in reports]}, ensure_ascii=False, indent=2, default=str))


def main() -> None:
    args = parse_args()
    asyncio.run(run(args.env))


if __name__ == "__main__":
    main()
