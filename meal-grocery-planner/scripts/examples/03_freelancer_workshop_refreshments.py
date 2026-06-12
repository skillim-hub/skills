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
    participants = int(os.getenv("MEAL_GROCERY_PARTICIPANTS", "12"))
    client = MealGroceryPlannerClient(environment=args.env, default_city=args.city)
    recipes = client.suggest_recipes(diet="vegetarian", servings=participants, max_minutes=30, exclude_allergens=["sesame"])
    plan = client.build_meal_plan(profile="freelancer-workshop", days=1, meals_per_day=1, diet="vegetarian", servings=participants, max_minutes=30, exclude_allergens=["sesame"])
    basket = client.create_basket(plan, household_size=participants, exclude_allergens=["sesame"])
    order = client.create_order_plan(basket, city=args.city, max_stores=1)
    emit({"participants": participants, "recipes": recipes, "order": order})


if __name__ == "__main__":
    main()
