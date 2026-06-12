from __future__ import annotations

import os

from _common import parser, print_json
from real_estate_search import RealEstateSearchClient, SearchCriteria

args = parser("Create a street-front shop search plan").parse_args()
client = RealEstateSearchClient(args.env)
criteria = SearchCriteria(
    city=os.getenv("REAL_ESTATE_SEARCH_CITY", "חיפה"),
    deal_type="commercial_rent",
    neighborhoods=tuple(os.getenv("REAL_ESTATE_SEARCH_NEIGHBORHOODS", "הדר,עיר תחתית").split(",")),
    max_price=int(os.getenv("REAL_ESTATE_SEARCH_MAX_PRICE", "9000")),
    property_types=("חנות", "נכס מסחרי"),
)
print_json(client.build_search_plan(criteria).to_dict())
