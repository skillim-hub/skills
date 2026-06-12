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
    plan = client.build_meal_plan(profile="family", days=7, diet="low_budget", servings=4)
    basket = client.create_basket(plan, household_size=4, pantry=os.getenv("MEAL_GROCERY_PANTRY", "").split(",") if os.getenv("MEAL_GROCERY_PANTRY") else [])
    order = client.create_order_plan(basket, city=args.city, preferred_stores=["rami_levy", "yochananof"])
    emit({"plan": plan, "basket": basket, "order": order})


if __name__ == "__main__":
    main()
