from __future__ import annotations

import os

from _common import parser, print_json
from real_estate_search import RealEstateSearchClient, SearchCriteria

args = parser("Create a small studio or clinic search plan").parse_args()
client = RealEstateSearchClient(args.env)
criteria = SearchCriteria(
    city=os.getenv("REAL_ESTATE_SEARCH_CITY", "תל אביב-יפו"),
    deal_type="commercial_rent",
    neighborhoods=tuple(os.getenv("REAL_ESTATE_SEARCH_NEIGHBORHOODS", "לב העיר,הצפון הישן").split(",")),
    max_price=int(os.getenv("REAL_ESTATE_SEARCH_MAX_PRICE", "6500")),
    property_types=("משרד", "קליניקה"),
    accessible=True,
)
print_json(client.build_search_plan(criteria).to_dict())
