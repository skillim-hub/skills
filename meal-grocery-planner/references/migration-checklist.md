# Migration checklist

Use this checklist when upgrading from an older local copy.

## File layout

- Delete any hyphenated client module under `scripts`.
- Import the client from `meal_grocery_planner`.
- Keep `scripts/meal_grocery_planner_client.py` only for script-oriented standalone use.
- Use `meal-grocery-planner` as the console command.
- Keep examples under `scripts/examples`.

## Installation

Before:

```bash
python scripts/meal-grocery-planner-client.py
```

After:

```bash
pip install -e .
pip install -r requirements-dev.txt
python -c "from meal_grocery_planner import MealGroceryPlannerClient; print(MealGroceryPlannerClient().list_stores()[0]['key'])"
```

## Imports

Before:

```python
import sys
sys.path.append("scripts")
```

After:

```python
from meal_grocery_planner import MealGroceryPlannerClient
```

## CLI order flow

Before:

```bash
meal-grocery-planner order --profile family
```

After:

```bash
create_response=$(meal-grocery-planner order --env sandbox --profile family --city "חיפה" --save)
order_id=$(python -c 'import json,sys; print(json.load(sys.stdin)["order_id"])' <<< "$create_response")
meal-grocery-planner show-order "$order_id" --env sandbox
```

## Examples

- Read environment values from `MEAL_GROCERY_ENV`, `MEAL_GROCERY_CITY`, and `MEAL_GROCERY_PRICE_FEED`.
- Accept `--env sandbox|production`.
- Print JSON using `ensure_ascii=False`.
- Avoid path mutation hacks.

## Validation

Run:

```bash
pytest -q
python -m compileall scripts/ -q
```

Accept the migration only when both commands succeed.
