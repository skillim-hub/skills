from __future__ import annotations

import os

from _common import parser, print_json
from real_estate_search import Listing, RealEstateSearchClient, SearchCriteria

args = parser("Compare manually collected listings").parse_args()
client = RealEstateSearchClient(args.env)
criteria = SearchCriteria(
    city=os.getenv("REAL_ESTATE_SEARCH_CITY", "חיפה"),
    deal_type=os.getenv("REAL_ESTATE_SEARCH_DEAL_TYPE", "rent"),
    neighborhoods=tuple(os.getenv("REAL_ESTATE_SEARCH_NEIGHBORHOODS", "בת גלים").split(",")),
    max_price=int(os.getenv("REAL_ESTATE_SEARCH_MAX_PRICE", "5200")),
    min_rooms=float(os.getenv("REAL_ESTATE_SEARCH_MIN_ROOMS", "2.5")),
)
listings = [
    Listing(title="דירה ליד הים", source="manual", city="חיפה", neighborhood="בת גלים", price=4900, rooms=3, balcony=True),
    Listing(title="דירה משופצת", source="manual", city="חיפה", neighborhood="הדר", price=5400, rooms=3, parking=True),
]
print_json([item.to_dict() for item in client.compare_listings(listings, criteria)])
