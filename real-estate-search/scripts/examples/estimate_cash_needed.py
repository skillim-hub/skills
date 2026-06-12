from __future__ import annotations

import os

from _common import parser, print_json
from real_estate_search import RealEstateSearchClient

args = parser("Estimate initial cash needed for a rental listing").parse_args()
client = RealEstateSearchClient(args.env)
listing = {
    "title": os.getenv("REAL_ESTATE_SEARCH_LISTING_TITLE", "דירה לדוגמה"),
    "city": os.getenv("REAL_ESTATE_SEARCH_CITY", "גבעתיים"),
    "price": int(os.getenv("REAL_ESTATE_SEARCH_MAX_PRICE", "7200")),
}
estimate = client.estimate_monthly_cash_needed(
    listing,
    monthly_arnona=int(os.getenv("REAL_ESTATE_SEARCH_ARNONA", "550")),
    monthly_vaad_bayit=int(os.getenv("REAL_ESTATE_SEARCH_VAAD_BAYIT", "300")),
    broker_fee_months=float(os.getenv("REAL_ESTATE_SEARCH_BROKER_FEE_MONTHS", "1")),
    deposit_months=float(os.getenv("REAL_ESTATE_SEARCH_DEPOSIT_MONTHS", "2")),
)
print_json(estimate.to_dict())
