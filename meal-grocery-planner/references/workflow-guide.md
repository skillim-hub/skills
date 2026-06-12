# Workflow guide

## Workflow 1: weekly family basket

Goal: create a weekly family basket under a fixed ₪ budget.

1. Collect household size, city, dietary constraints, pantry items, and budget.
2. Generate a low-budget meal plan.
3. Convert the plan to a basket.
4. Compare all supported stores.
5. Create an order plan for the cheapest acceptable store.
6. Verify the final cart manually.

Example:

```python
from meal_grocery_planner import MealGroceryPlannerClient

client = MealGroceryPlannerClient(environment="sandbox")
plan = client.build_meal_plan(profile="family", days=7, diet="low_budget", servings=4)
basket = client.create_basket(plan, household_size=4, pantry=["אורז פרסי"])
budget = client.calculate_budget(basket, weekly_limit_ils=450)
order = client.create_order_plan(basket, city="אשדוד")

print(budget)
print(order["store_links"])
```

Acceptance criteria:

- Budget status is visible.
- Missing products are visible.
- Final supermarket cart is checked before payment.

## Workflow 2: freelancer workshop refreshments

Goal: buy food for a client workshop and keep the plan easy to reconcile.

1. Count participants and add a small buffer.
2. Use quick recipes and ready-to-serve items.
3. Exclude known allergens.
4. Save the order plan id.
5. Keep the final receipt or invoice for bookkeeping.

Command flow:

```bash
create_response=$(meal-grocery-planner order --env sandbox --profile workshop --city "תל אביב" --days 1 --household-size 12 --diet vegetarian --save)
order_id=$(python -c 'import json,sys; print(json.load(sys.stdin)["order_id"])' <<< "$create_response")
meal-grocery-planner validate "$order_id" --env sandbox
```

## Workflow 3: office kitchenette restock

Goal: restock recurring office basics.

1. Maintain a pantry list outside the tool.
2. Include products below minimum stock only.
3. Use a single preferred delivery store when office receiving time is constrained.
4. Export a Hebrew shopping list for staff review.
5. Update the pantry list after the delivery arrives.

## Workflow 4: allergy-safe family planning

Goal: avoid unsafe substitutions.

1. Enter excluded allergens as normalized English labels, such as `milk`, `sesame`, or `nuts`.
2. Generate recipes with exclusions.
3. Create a basket with the same exclusions.
4. Inspect any line without a matched product.
5. Verify product label and seller page before checkout.

## Workflow 5: imported price feed comparison

Goal: compare current local feed rows with the built-in sandbox catalog.

1. Export or receive a CSV or JSON price feed.
2. Validate required columns.
3. Import the feed.
4. Search products and compare basket again.
5. Keep feed date and branch context in the planning record.

CSV example:

```csv
store,sku,name,category,unit,package_size,price_ils,kosher,allergens,last_updated
victory,feed-001,עגבניה,produce,kg,1,7.20,true,,04/06/2026
```

## Workflow 6: single-store manual checkout

Goal: reduce operational complexity.

1. Compare all stores.
2. Select the best store after live delivery fee and minimum order checks.
3. Open the generated search link.
4. Add items manually to the cart.
5. Reconcile final cart differences with the warning list.

## Decision checkpoints

| Checkpoint | Continue when | Stop when |
|---|---|---|
| Recipe selection | Diet and preparation time fit the need | No recipe fits allergies or kashrut |
| Basket creation | Every critical item has a match or warning | Core meal component is missing |
| Store comparison | Total includes delivery and minimum order status | Store availability is unknown |
| Manual cart verification | Cart price is close to estimate | Package size or price changed materially |
| Purchase approval | Human reviewer accepts substitutions | Allergy, kashrut, or budget risk remains |
