from __future__ import annotations

import asyncio
import os

from _common import parser, print_json
from real_estate_search import RealEstateSearchClient, SearchCriteria


async def main() -> None:
    args = parser("Create links asynchronously and return link status placeholders").parse_args()
    client = RealEstateSearchClient(args.env)
    criteria = SearchCriteria(
        city=os.getenv("REAL_ESTATE_SEARCH_CITY", "ירושלים"),
        deal_type=os.getenv("REAL_ESTATE_SEARCH_DEAL_TYPE", "sale"),
        neighborhoods=tuple(os.getenv("REAL_ESTATE_SEARCH_NEIGHBORHOODS", "בקעה,רחביה").split(",")),
        max_price=int(os.getenv("REAL_ESTATE_SEARCH_MAX_PRICE", "3200000")),
        sources=("yad2", "madlan", "komo"),
    )
    plan = await client.abuild_search_plan(criteria)
    status = await client.async_check_links(plan.links, fetch=False)
    print_json({"plan": plan.to_dict(), "status": status})


asyncio.run(main())
