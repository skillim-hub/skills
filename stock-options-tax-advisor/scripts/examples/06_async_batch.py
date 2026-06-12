import asyncio
import json

from _example_loader import env_float, parser
from stock_options_tax_advisor import AsyncStockOptionsTaxAdvisorClient

args = parser("Run two scenarios through the async wrapper.").parse_args()

async def main() -> None:
    client = AsyncStockOptionsTaxAdvisorClient(environment=args.env)
    results = await client.calculate_many([
        {
            "grant_type": "options",
            "track": "102_capital",
            "quantity": env_float("STOCK_OPTIONS_QUANTITY", 10000),
            "exercise_price": 1,
            "sale_price": 11,
            "grant_date": "01/01/2024",
            "sale_date": "02/01/2027",
            "trustee_approved": True,
        },
        {
            "grant_type": "rsu",
            "track": "102_capital",
            "quantity": 500,
            "exercise_price": 0,
            "sale_price": 100,
            "grant_date": "01/01/2024",
            "sale_date": "02/01/2027",
            "trustee_approved": True,
        },
    ])
    print(json.dumps({"environment": args.env, "results": [r.to_dict() for r in results]}, ensure_ascii=False, indent=2))

asyncio.run(main())
