# Meal and Grocery Planner

Installable Python helper and skill package for Israeli meal planning, grocery basket estimation, supermarket comparison, and order-link preparation.

## Install

```bash
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Create an order response, extract the id, then use it in the next command:

```bash
create_response=$(meal-grocery-planner order --env sandbox --profile family --city "חיפה" --save)
order_id=$(python -c 'import json,sys; print(json.load(sys.stdin)["order_id"])' <<< "$create_response")
meal-grocery-planner show-order "$order_id" --env sandbox
meal-grocery-planner validate "$order_id" --env sandbox
```

## Python usage

```python
from meal_grocery_planner import MealGroceryPlannerClient

client = MealGroceryPlannerClient(environment="sandbox")
plan = client.build_meal_plan(profile="family", days=7, diet="low_budget")
basket = client.create_basket(plan, household_size=4)
order = client.create_order_plan(basket, city="תל אביב")

print(order["order_id"])
print(order["estimated_total_ils"])
```

## Async usage

```python
import asyncio
from meal_grocery_planner import MealGroceryPlannerClient

async def main():
    client = MealGroceryPlannerClient(environment="sandbox")
    result = await client.async_search_products("עגבניה")
    print(result[0]["name"])

asyncio.run(main())
```

## CLI commands

```bash
meal-grocery-planner stores --env sandbox
meal-grocery-planner recipes --env sandbox --diet vegetarian
meal-grocery-planner meal-plan --env sandbox --profile freelancer --days 3
meal-grocery-planner basket --env sandbox --profile family --household-size 5
meal-grocery-planner order --env sandbox --profile workshop --city "ירושלים" --save
meal-grocery-planner import-feed ./prices.csv --env sandbox --store rami_levy
```

## Environment variables

| Variable | Purpose |
|---|---|
| `MEAL_GROCERY_ENV` | Default example environment, either `sandbox` or `production` |
| `MEAL_GROCERY_CITY` | Default city for CLI commands |
| `MEAL_GROCERY_ORDER_DIR` | Local directory for saved order JSON |
| `MEAL_GROCERY_PRICE_FEED` | Optional CSV or JSON price feed path for examples |

Never place payment credentials in environment variables used by these examples.

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide |
| `meal_grocery_planner/client.py` | Typed sync and async client |
| `meal_grocery_planner/cli.py` | Typer CLI implementation |
| `scripts/meal_grocery_planner_client.py` | Standalone client module copy for script-oriented usage |
| `scripts/meal-grocery-planner-cli.py` | CLI launcher |
| `scripts/test_meal_grocery_planner_client.py` | Pytest suite |
| `scripts/examples/` | Runnable planning scenarios |
| `references/api-reference.md` | Data source and regulation reference |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Troubleshooting guide |
| `references/test-scenarios.md` | Scenario catalog |
| `references/migration-checklist.md` | Upgrade checklist |
| `references/branding-audit.md` | Branding and metadata audit |
| `references/hebrew-qa-log.md` | Hebrew quality log |
| `references/verification-log.md` | Two-pass web validation log |

## Development

```bash
pytest -q
python -m compileall scripts/ -q
```

## Operational limits

The package does not submit supermarket orders. It produces estimates and search links. Verify item availability, final prices, package sizes, delivery fees, minimum order, and delivery windows in the supermarket cart before payment.
