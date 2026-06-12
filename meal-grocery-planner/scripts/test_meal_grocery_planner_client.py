import asyncio
import json
from pathlib import Path

import pytest

from meal_grocery_planner import MealGroceryPlannerClient, PlannerValidationError


def client():
    return MealGroceryPlannerClient(environment="sandbox")


def test_list_stores_contains_supported_chains():
    stores = client().list_stores()
    keys = {store["key"] for store in stores}
    assert {"shufersal", "rami_levy", "victory", "yochananof"} <= keys


def test_invalid_environment_rejected():
    with pytest.raises(PlannerValidationError):
        MealGroceryPlannerClient(environment="demo")


def test_search_products_returns_results():
    results = client().search_products("עגבניה")
    assert results
    assert results[0]["name"] == "עגבניה"


def test_search_store_filter():
    results = client().search_products("עגבניה", store="rami_levy")
    assert results
    assert {row["store"] for row in results} == {"rami_levy"}


def test_search_empty_query_rejected():
    with pytest.raises(PlannerValidationError):
        client().search_products(" ")


def test_search_max_results_rejected():
    with pytest.raises(PlannerValidationError):
        client().search_products("עגבניה", max_results=0)


def test_english_synonym_search():
    results = client().search_products("tomatoes")
    assert results
    assert results[0]["name"] == "עגבניה"


@pytest.mark.asyncio
async def test_async_search_products():
    results = await client().async_search_products("עגבניה")
    assert results[0]["name"] == "עגבניה"


def test_suggest_vegetarian_recipes():
    recipes = client().suggest_recipes(diet="vegetarian")
    assert recipes
    assert all("vegetarian" in recipe["diet_tags"] for recipe in recipes)


def test_suggest_vegan_recipes():
    recipes = client().suggest_recipes(diet="vegan")
    assert recipes
    assert all("vegan" in recipe["diet_tags"] for recipe in recipes)


def test_suggest_recipes_rejects_invalid_servings():
    with pytest.raises(PlannerValidationError):
        client().suggest_recipes(servings=0)


def test_suggest_recipes_rejects_short_time():
    with pytest.raises(PlannerValidationError):
        client().suggest_recipes(max_minutes=4)


def test_allergen_exclusion_changes_recipes():
    recipes = client().suggest_recipes(diet="vegan", exclude_allergens=["sesame"], limit=10)
    titles = {recipe["title"] for recipe in recipes}
    assert "צלחות חומוס וטחינה" not in titles


@pytest.mark.asyncio
async def test_async_suggest_recipes():
    recipes = await client().async_suggest_recipes(diet="low_budget")
    assert recipes


def test_build_meal_plan():
    plan = client().build_meal_plan(profile="family", days=3, diet="low_budget")
    assert plan["plan_id"].startswith("plan_")
    assert len(plan["recipes"]) == 3


def test_build_meal_plan_invalid_days():
    with pytest.raises(PlannerValidationError):
        client().build_meal_plan(profile="family", days=0)


def test_build_meal_plan_invalid_meals_per_day():
    with pytest.raises(PlannerValidationError):
        client().build_meal_plan(profile="family", meals_per_day=5)


@pytest.mark.asyncio
async def test_async_build_meal_plan():
    plan = await client().async_build_meal_plan(profile="family", days=2)
    assert plan["days"] == 2


def test_create_basket_from_plan():
    c = client()
    plan = c.build_meal_plan(profile="family", days=2, diet="low_budget")
    basket = c.create_basket(plan, household_size=4)
    assert basket
    assert all("estimated_cost_ils" in line for line in basket)


def test_create_basket_removes_pantry():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1, diet="low_budget", pantry=["אורז פרסי"])
    basket = c.create_basket(plan, household_size=4, pantry=["אורז פרסי"])
    names = {line["ingredient"]["name"] for line in basket}
    assert "אורז פרסי" not in names


def test_create_basket_rejects_household_zero():
    c = client()
    plan = c.build_meal_plan(profile="family")
    with pytest.raises(PlannerValidationError):
        c.create_basket(plan, household_size=0)


@pytest.mark.asyncio
async def test_async_create_basket():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = await c.async_create_basket(plan)
    assert basket


def test_compare_basket_returns_recommendation():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1, diet="low_budget")
    basket = c.create_basket(plan)
    comparison = c.compare_basket(basket)
    assert comparison["recommended_store"] in comparison["stores"]


def test_compare_basket_delivery_flag_changes_total():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1, diet="low_budget")
    basket = c.create_basket(plan)
    with_delivery = c.compare_basket(basket, preferred_stores=["rami_levy"], include_delivery=True)
    without_delivery = c.compare_basket(basket, preferred_stores=["rami_levy"], include_delivery=False)
    assert with_delivery["stores"]["rami_levy"]["total_ils"] > without_delivery["stores"]["rami_levy"]["total_ils"]


def test_compare_basket_rejects_no_stores():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    with pytest.raises(PlannerValidationError):
        c.compare_basket(basket, preferred_stores=[])


@pytest.mark.asyncio
async def test_async_compare_basket():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    comparison = await c.async_compare_basket(basket)
    assert "recommended_store" in comparison


def test_create_order_plan():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1, diet="low_budget")
    basket = c.create_basket(plan)
    order = c.create_order_plan(basket, city="חיפה")
    assert order["order_id"].startswith("order_")
    assert order["store_links"]


def test_create_order_plan_rejects_empty_city():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    with pytest.raises(PlannerValidationError):
        c.create_order_plan(basket, city=" ")


def test_create_order_plan_rejects_empty_basket():
    with pytest.raises(PlannerValidationError):
        client().create_order_plan([], city="חיפה")


def test_create_order_plan_rejects_bad_max_stores():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    with pytest.raises(PlannerValidationError):
        c.create_order_plan(basket, city="חיפה", max_stores=0)


@pytest.mark.asyncio
async def test_async_create_order_plan():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    order = await c.async_create_order_plan(basket, city="חיפה")
    assert order["city"] == "חיפה"


def test_split_order():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    order = c.create_order_plan(basket, city="חיפה", max_stores=2)
    split = c.split_order(order, max_stores=2)
    assert split["split_count"] >= 1


def test_export_shopping_list_hebrew():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    text = c.export_shopping_list(basket, locale="he-IL")
    assert "₪" in text
    assert "יחידות" in text


def test_export_shopping_list_english():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    text = c.export_shopping_list(basket, locale="en-IL")
    assert "packages" in text


def test_export_shopping_list_bad_locale():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    with pytest.raises(PlannerValidationError):
        c.export_shopping_list(basket, locale="fr-FR")


def test_calculate_budget_overrun():
    c = client()
    plan = c.build_meal_plan(profile="family", days=2)
    basket = c.create_basket(plan)
    budget = c.calculate_budget(basket, weekly_limit_ils=1)
    assert budget["over_budget"] is True


def test_calculate_budget_rejects_invalid_limit():
    with pytest.raises(PlannerValidationError):
        client().calculate_budget([], weekly_limit_ils=0)


def test_generate_store_links():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    links = c.generate_store_links(basket, stores=["shufersal", "rami_levy"])
    assert set(links) == {"shufersal", "rami_levy"}
    assert links["rami_levy"].startswith("https://www.rami-levy.co.il/he/online/search?q=")


def test_generate_store_links_uses_verified_host_fallbacks():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    links = c.generate_store_links(basket, stores=["victory", "yochananof"])
    assert links["victory"] == "https://www.victoryonline.co.il/"
    assert links["yochananof"] == "https://yochananof.co.il/search"
    assert "ybitan" not in links["yochananof"]


def test_validate_order_plan():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    order = c.create_order_plan(basket, city="חיפה")
    validation = c.validate_order_plan(order)
    assert validation["order_id"] == order["order_id"]
    assert validation["valid"] in {True, False}


def test_import_csv_price_feed(tmp_path):
    feed = tmp_path / "prices.csv"
    feed.write_text("store,sku,name,category,unit,package_size,price_ils,kosher,allergens,last_updated\nrami_levy,x1,אבוקדו,produce,kg,1,12.5,true,,04/06/2026\n", encoding="utf-8")
    rows = client().import_price_feed(feed)
    assert rows[0]["name"] == "אבוקדו"


def test_import_json_price_feed(tmp_path):
    feed = tmp_path / "prices.json"
    feed.write_text(json.dumps({"items": [{"store": "victory", "sku": "j1", "name": "אגס", "category": "produce", "unit": "kg", "package_size": 1, "price_ils": 10.9}]}, ensure_ascii=False), encoding="utf-8")
    rows = client().import_price_feed(feed)
    assert rows[0]["store"] == "victory"


def test_import_price_feed_missing_file(tmp_path):
    with pytest.raises(PlannerValidationError):
        client().import_price_feed(tmp_path / "missing.csv")


def test_import_price_feed_bad_extension(tmp_path):
    feed = tmp_path / "prices.txt"
    feed.write_text("bad", encoding="utf-8")
    with pytest.raises(PlannerValidationError):
        client().import_price_feed(feed)


def test_import_price_feed_negative_price(tmp_path):
    feed = tmp_path / "prices.csv"
    feed.write_text("store,sku,name,category,unit,package_size,price_ils\nrami_levy,x1,אבוקדו,produce,kg,1,-1\n", encoding="utf-8")
    with pytest.raises(PlannerValidationError):
        client().import_price_feed(feed)


def test_import_price_feed_missing_name(tmp_path):
    feed = tmp_path / "prices.csv"
    feed.write_text("store,sku,category,unit,package_size,price_ils\nrami_levy,x1,produce,kg,1,8\n", encoding="utf-8")
    with pytest.raises(PlannerValidationError):
        client().import_price_feed(feed)


def test_order_plan_is_json_serializable():
    c = client()
    plan = c.build_meal_plan(profile="family", days=1)
    basket = c.create_basket(plan)
    order = c.create_order_plan(basket, city="חיפה")
    encoded = json.dumps(order, ensure_ascii=False)
    assert "חיפה" in encoded
