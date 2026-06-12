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
    plan = client.build_meal_plan(profile="split-order", days=2, diet="low_budget")
    basket = client.create_basket(plan)
    order = client.create_order_plan(basket, city=args.city, preferred_stores=["shufersal", "rami_levy", "victory"], max_stores=2)
    split = client.split_order(order, max_stores=2)
    emit({"order_id": order["order_id"], "split": split, "links": order["store_links"]})


if __name__ == "__main__":
    main()
