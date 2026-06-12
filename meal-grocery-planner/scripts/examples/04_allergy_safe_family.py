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
    allergens = [value for value in os.getenv("MEAL_GROCERY_EXCLUDE_ALLERGENS", "sesame,milk").split(",") if value]
    client = MealGroceryPlannerClient(environment=args.env, default_city=args.city)
    recipes = client.suggest_recipes(diet="standard", servings=4, max_minutes=45, exclude_allergens=allergens)
    plan = client.build_meal_plan(profile="allergy-safe-family", days=3, diet="standard", exclude_allergens=allergens)
    basket = client.create_basket(plan, household_size=4, exclude_allergens=allergens)
    emit({"allergens": allergens, "recipes": recipes, "basket": basket})


if __name__ == "__main__":
    main()
