from __future__ import annotations

import argparse
import json
import os
from typing import Any

from meal_grocery_planner import MealGroceryPlannerClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("MEAL_GROCERY_ENV", "sandbox"))
    parser.add_argument("--city", default=os.getenv("MEAL_GROCERY_CITY", "תל אביב"))
    return parser.parse_args()


def emit(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))

def main() -> None:
    args = parse_args()
    client = MealGroceryPlannerClient(environment=args.env, default_city=args.city)
    feed_path = os.getenv("MEAL_GROCERY_PRICE_FEED")
    if feed_path:
        imported = client.import_price_feed(feed_path)
    else:
        imported = []
    results = client.search_products(os.getenv("MEAL_GROCERY_QUERY", "עגבניה"), max_results=5)
    emit({"imported_count": len(imported), "results": results})


if __name__ == "__main__":
    main()
