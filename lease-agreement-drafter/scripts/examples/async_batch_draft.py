from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from lease_agreement_drafter import LeaseAgreementDrafterClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LEASE_DRAFTER_ENV", "sandbox"))
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def requests() -> list[dict]:
    return [
        {
            "landlord": {"name": "רונית שמש"},
            "tenant": {"name": "אלון הדר"},
            "property": {"property_type": "apartment", "address": "אחד העם 2", "city": "ראשון לציון"},
            "terms": {"start_date": "01/08/2026", "end_date": "31/07/2027", "monthly_rent_ils": 4500, "security_deposit_ils": 9000},
            "language": "he",
        },
        {
            "landlord": {"name": "נכסי השרון"},
            "tenant": {"name": "קליניקת שקד"},
            "property": {"property_type": "office", "address": "ויצמן 50", "city": "כפר סבא", "permitted_use": "קליניקה משרדית"},
            "terms": {"start_date": "15/08/2026", "end_date": "14/08/2028", "monthly_rent_ils": 6900, "security_deposit_ils": 20700, "vat_applies": True},
            "language": "he",
        },
    ]


async def main_async() -> None:
    args = parse_args()
    api_key = os.getenv("LEASE_DRAFTER_API_KEY", "")
    client = LeaseAgreementDrafterClient(api_key=api_key, environment=args.env)
    results = await asyncio.gather(*(client.draft_async(item) for item in requests()))
    payload = {"environment": args.env, "drafts": [result.to_dict() for result in results]}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    asyncio.run(main_async())
