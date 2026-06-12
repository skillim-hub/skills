#!/usr/bin/env python3
from _example_loader import common_parser, emit, validate_catalog_data

parser = common_parser("Catalog validation scenario")
args = parser.parse_args()
bad_catalog = [{"sku": "A", "name_he": "מוצר בדיקה", "category": "בדיקה", "price_ils": "10", "cross_sell": ["MISSING-SKU"]}]
emit({"environment": args.env, "errors": validate_catalog_data(bad_catalog)})
