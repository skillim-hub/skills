from __future__ import annotations

import argparse
import asyncio
import json
import os

from lead_router import LeadRouterClient

async def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LEAD_ROUTER_ENV", "sandbox"))
    parser.add_argument("--config", default=os.getenv("LEAD_ROUTER_CONFIG"))
    args = parser.parse_args()

    client = LeadRouterClient.from_json_file(args.config) if args.config else LeadRouterClient()
    leads = [
        {"phone": os.getenv("LEAD_ROUTER_PHONE", "0521234567"), "message": os.getenv("LEAD_ROUTER_MESSAGE", "צריך מחיר בחיפה")},
        {"email": os.getenv("LEAD_ROUTER_EMAIL", "client@example.co.il"), "message": "أحتاج فاتورة للدفع"},
    ]
    results = await client.aroute_many(leads)
    print(json.dumps([{"env": args.env, **result.to_dict()} for result in results], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(run())
