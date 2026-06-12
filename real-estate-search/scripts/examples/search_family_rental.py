from __future__ import annotations

import os

from _common import parser, print_json
from real_estate_search import RealEstateSearchClient, SearchCriteria

args = parser("Create a family rental search plan").parse_args()
client = RealEstateSearchClient(args.env)
criteria = SearchCriteria(
    city=os.getenv("REAL_ESTATE_SEARCH_CITY", "רמת גן"),
    deal_type="rent",
    neighborhoods=tuple(os.getenv("REAL_ESTATE_SEARCH_NEIGHBORHOODS", "מרום נווה,הראשונים").split(",")),
    max_price=int(os.getenv("REAL_ESTATE_SEARCH_MAX_PRICE", "8500")),
    min_rooms=float(os.getenv("REAL_ESTATE_SEARCH_MIN_ROOMS", "3.5")),
    parking=True,
    balcony=True,
)
print_json(client.build_search_plan(criteria).to_dict())
