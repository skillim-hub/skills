# API and Israeli data reference

This skill is designed as a planning layer. It does not rely on a single universal supermarket ordering API. Use it to normalize inputs, prepare basket estimates, and link users to supermarket carts or search pages for manual verification.

## Data source categories

| Source category | Use | Verification requirement |
|---|---|---|
| Supermarket public site search | Generate a search path for products | Confirm final item, price, package size, and availability in the cart |
| Published price transparency files | Import price rows for comparison | Check timestamp, branch relevance, and product identifier |
| Internal business pantry records | Remove existing inventory from planned purchases | Confirm actual stock level before ordering |
| Receipts and invoices | Reconcile estimates after purchase | Keep source documents for accounting and warranty needs |

## Israeli supermarket targets

| Store key | Chain | Planning behavior |
|---|---|---|
| `shufersal` | Shufersal | Use the generated search URL, then verify online cart data |
| `rami_levy` | Rami Levy | Use for budget-sensitive comparison and staple pricing |
| `victory` | Victory | Use as an alternative chain for availability and price comparison |
| `yochananof` | Yochananof | Use for family-basket comparison and store coverage checks |

## Price transparency and consumer-law context

Relevant Israeli compliance areas can affect grocery planning:

| Area | Practical impact |
|---|---|
| Food retail price publication duties | Prices may be available through published files, but file format, freshness, and branch coverage must be validated |
| Consumer protection rules | Final checkout price, delivery terms, cancellation terms, and disclosed fees must be checked at the seller |
| Product marking and unit-price display | Package size and unit price must be verified when comparing alternatives |
| Allergen and food labeling duties | Do not treat a planner match as an allergen-safe confirmation |
| Kashrut marking | Confirm kashrut status on the product package or seller page |
| VAT and business records | Preserve receipts and invoices; classify expenses according to the actual transaction and business use |

This package is not a legal or tax opinion. Use a professional adviser for accounting, tax, or compliance decisions.


## Web-validated official context, accessed 04/06/2026

Use these facts as planning guardrails, not as automated checkout authority. Verify final values in the live cart and original source before payment or reporting.

| Topic | Validated result | Operational handling |
|---|---|---|
| Standard Israeli VAT | 18% from 01/01/2025 and still listed as current in 2026 secondary tax references | Record receipts and invoices; do not calculate deductible VAT unless the business use is known |
| Price transparency | Large retailers must publish store lists, food product prices, and promotions online | Prefer official transparency files when importing branch-specific price data |
| Search links | Public search pages exist for supported supermarket sites, but URL parameters can change without notice | Treat generated links as convenience links and fall back to the retailer search page |
| Delivery fees and minimum orders | Current values could not be double-confirmed from stable official pages for all four chains | Keep built-in fee and minimum-order values as sandbox estimates only |
| Allergen and kashrut marking | Official guidance requires label-level review for allergens and kashrut | Never mark a basket as allergen-safe or kosher without checking the product label or seller page |

## Local client interface

### Create a client

```python
from meal_grocery_planner import MealGroceryPlannerClient

client = MealGroceryPlannerClient(environment="sandbox", default_city="תל אביב")
```

### Search products

Request:

```python
client.search_products(
    query="עגבניה",
    store="rami_levy",
    max_results=3,
    require_kosher=True,
    exclude_allergens=[],
)
```

Response:

```json
[
  {
    "sku": "sku_9c52b8c8e13a",
    "store": "rami_levy",
    "name": "עגבניה",
    "category": "produce",
    "unit": "kg",
    "package_size": 1.0,
    "price_ils": 6.9,
    "brand": "",
    "kosher": true,
    "allergens": [],
    "promotion": null,
    "last_updated": "01/06/2026",
    "unit_price_ils": 6.9
  }
]
```

### Suggest recipes

Request:

```python
client.suggest_recipes(
    diet="vegetarian",
    servings=4,
    max_minutes=30,
    pantry=["אורז פרסי"],
    exclude_allergens=["sesame"],
)
```

Response:

```json
[
  {
    "key": "israeli-breakfast",
    "title": "ארוחת בוקר ישראלית",
    "servings": 4,
    "minutes": 20,
    "diet_tags": ["standard", "vegetarian", "kosher_dairy"],
    "ingredients": [
      {"name": "ביצים גודל L", "quantity": 8, "unit": "unit", "category": "eggs"}
    ],
    "steps": ["להכין ביצים לפי העדפה"],
    "notes": "מתאים לאירוח קטן במשרד."
  }
]
```

### Build a meal plan

Request:

```python
plan = client.build_meal_plan(
    profile="family",
    days=7,
    meals_per_day=1,
    diet="low_budget",
    servings=4,
)
```

Response shape:

```json
{
  "plan_id": "plan_...",
  "profile": "family",
  "days": 7,
  "recipes": [],
  "assumptions": [
    "4 servings per cooked meal",
    "Prices are estimates until verified in the selected supermarket cart"
  ]
}
```

### Create a basket

Request:

```python
basket = client.create_basket(plan, household_size=4, pantry=["שמן זית"])
```

Response shape:

```json
[
  {
    "ingredient": {"name": "עגבניה", "quantity": 2.0, "unit": "kg", "category": "produce"},
    "matched_item": {"name": "עגבניה", "store": "yochananof", "price_ils": 6.8},
    "requested_quantity": 2.0,
    "estimated_packages": 2,
    "estimated_cost_ils": 13.6,
    "substitutions": []
  }
]
```

### Compare a basket

Request:

```python
client.compare_basket(basket, preferred_stores=["shufersal", "rami_levy"])
```

Response shape:

```json
{
  "stores": {
    "rami_levy": {
      "subtotal_ils": 142.3,
      "delivery_fee_ils": 28.9,
      "total_ils": 171.2,
      "missing": [],
      "lines": []
    }
  },
  "recommended_store": "rami_levy"
}
```

### Create an order plan

Request:

```python
order = client.create_order_plan(
    basket,
    city="תל אביב",
    preferred_stores=["rami_levy", "yochananof"],
    max_stores=2,
)
```

Response shape:

```json
{
  "order_id": "order_...",
  "city": "תל אביב",
  "environment": "sandbox",
  "selected_stores": ["rami_levy", "yochananof"],
  "estimated_total_ils": 199.8,
  "warnings": [],
  "store_links": {
    "rami_levy": "https://www.rami-levy.co.il/he/online/search?q=..."
  }
}
```

### Import price feed

CSV columns:

```csv
store,sku,name,category,unit,package_size,price_ils,kosher,allergens,last_updated
rami_levy,123,עגבניה,produce,kg,1,6.90,true,,01/06/2026
```

Request:

```python
client.import_price_feed("prices.csv", store="rami_levy")
```

## Error table

| Error | Trigger | Fix |
|---|---|---|
| `environment must be 'sandbox' or 'production'` | Invalid environment value | Use `sandbox` for local testing or `production` for live planning |
| `query must not be empty` | Empty product query | Send a generic product name |
| `max_results must be positive` | Zero or negative result limit | Use an integer above zero |
| `days must be between 1 and 31` | Meal plan duration outside supported range | Split long periods into monthly runs |
| `meals_per_day must be between 1 and 4` | Invalid meal frequency | Use 1 to 4 |
| `no recipes match the requested constraints` | Diet, time, or allergen filters exclude all recipes | Relax constraints or add recipes |
| `basket must not be empty` | Order plan requested without lines | Build or import a basket first |
| `price feed must be CSV or JSON` | Unsupported feed extension | Convert to CSV or JSON |
| `missing required field` | Feed row lacks product name | Add required columns |
| `negative price on row` | Feed contains invalid price | Correct feed data before import |

## Request validation checklist

1. Require non-empty city values.
2. Validate store keys against supported chains.
3. Preserve Hebrew text with UTF-8.
4. Print JSON using `ensure_ascii=False`.
5. Treat imported prices as estimates until cart verification.
6. Keep order submission outside automated code unless a separate, approved integration exists.
