# Test scenarios

Use these scenarios for manual QA, automated tests, and acceptance reviews.

| ID | Scenario | Input | Expected result |
|---|---|---|---|
| 1 | Basic product search | `עגבניה` | Returns products from supported stores |
| 2 | Store-specific search | `עגבניה`, `rami_levy` | Returns only Rami Levy rows |
| 3 | Empty query validation | empty query | Raises validation error |
| 4 | English synonym | `tomatoes` | Normalizes to tomato results |
| 5 | Vegetarian recipes | `diet=vegetarian` | Returns vegetarian-compatible recipes |
| 6 | Vegan recipes | `diet=vegan` | Returns vegan recipes only |
| 7 | Low-budget recipes | `diet=low_budget` | Prioritizes lower-cost recipes |
| 8 | Max time filter | `max_minutes=10` | Returns only quick recipes |
| 9 | Allergen exclusion | `sesame` | Removes tahini-based options |
| 10 | Family meal plan | 7 days, 4 servings | Creates deterministic plan id |
| 11 | Invalid days | 0 days | Raises validation error |
| 12 | Pantry removal | pantry contains rice | Basket excludes rice |
| 13 | Package rounding | 1.5 kg potatoes | Rounds package count upward |
| 14 | Basket comparison | all stores | Returns recommended store |
| 15 | Delivery included | include delivery | Total includes sandbox delivery-fee estimate |
| 16 | Delivery excluded | no delivery | Total excludes sandbox delivery-fee estimate |
| 17 | Order creation | city and basket | Returns order id and links |
| 18 | Empty basket order | empty list | Raises validation error |
| 19 | Split order | max two stores | Produces store buckets |
| 20 | Hebrew shopping list | `locale=he-IL` | Includes ₪ and Hebrew labels |
| 21 | English shopping list | `locale=en-IL` | Includes English package text |
| 22 | JSON price feed | valid feed | Imports products |
| 23 | CSV price feed | valid feed | Imports products |
| 24 | Missing feed | nonexistent path | Raises validation error |
| 25 | Negative feed price | `-1` price | Raises validation error |
| 26 | Async search | await search | Returns same shape as sync search |
| 27 | Async order plan | await order flow | Returns valid order plan |
| 28 | Invalid environment | `demo` | Raises validation error |
| 29 | Budget overrun | low weekly limit | Marks over budget |
| 30 | Store links | basket and stores | Produces URLs for selected chains |
| 31 | CLI stores | `stores --env sandbox` | Prints JSON array |
| 32 | CLI order save | `order --save` | Stores order file by id |
