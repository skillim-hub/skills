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
    plan = client.build_meal_plan(profile="student", days=5, diet="low_budget", servings=1, pantry=["אורז פרסי"])
    basket = client.create_basket(plan, household_size=1, pantry=["אורז פרסי"])
    budget = client.calculate_budget(basket, weekly_limit_ils=float(os.getenv("MEAL_GROCERY_WEEKLY_LIMIT", "180")))
    emit({"plan_id": plan["plan_id"], "basket": basket, "budget": budget})


if __name__ == "__main__":
    main()
