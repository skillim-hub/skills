from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence
from urllib.parse import quote_plus


Environment = Literal["sandbox", "production"]
StoreName = Literal["shufersal", "rami_levy", "victory", "yochananof"]
Diet = Literal["standard", "vegetarian", "vegan", "kosher_meat", "kosher_dairy", "low_budget"]


@dataclass(frozen=True)
class StoreConfig:
    key: StoreName
    display_name: str
    search_url_template: str
    order_url: str
    price_feed_notes: str
    default_delivery_fee_ils: float
    minimum_order_ils: float


@dataclass(frozen=True)
class PriceItem:
    sku: str
    store: StoreName
    name: str
    category: str
    unit: str
    package_size: float
    price_ils: float
    brand: str = ""
    kosher: bool = True
    allergens: tuple[str, ...] = ()
    promotion: str | None = None
    last_updated: str | None = None

    @property
    def unit_price_ils(self) -> float:
        if self.package_size <= 0:
            return self.price_ils
        return round(self.price_ils / self.package_size, 2)


@dataclass(frozen=True)
class Ingredient:
    name: str
    quantity: float
    unit: str
    category: str = "general"


@dataclass(frozen=True)
class Recipe:
    key: str
    title: str
    servings: int
    minutes: int
    diet_tags: tuple[Diet, ...]
    ingredients: tuple[Ingredient, ...]
    steps: tuple[str, ...]
    notes: str = ""


@dataclass(frozen=True)
class BasketLine:
    ingredient: Ingredient
    matched_item: PriceItem | None
    requested_quantity: float
    estimated_packages: int
    estimated_cost_ils: float
    substitutions: tuple[PriceItem, ...] = ()


@dataclass(frozen=True)
class MealPlan:
    plan_id: str
    profile: str
    days: int
    recipes: tuple[Recipe, ...]
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class OrderPlan:
    order_id: str
    city: str
    environment: Environment
    lines: tuple[BasketLine, ...]
    selected_stores: tuple[StoreName, ...]
    store_totals_ils: dict[str, float]
    delivery_fee_ils: float
    estimated_total_ils: float
    warnings: tuple[str, ...]
    store_links: dict[str, str]
    created_date: str = field(default_factory=lambda: date.today().isoformat())


class PlannerValidationError(ValueError):
    """Raised when a basket, price feed, or order request is invalid."""


class MealGroceryPlannerClient:
    """Typed local client for Israeli grocery planning workflows.

    The client is deterministic in sandbox mode and avoids placing real orders.
    Production mode validates inputs the same way but still returns plans and links
    rather than submitting purchases to supermarket sites.
    """

    def __init__(
        self,
        environment: Environment = "sandbox",
        catalog: Sequence[PriceItem] | None = None,
        store_configs: Sequence[StoreConfig] | None = None,
        default_city: str = "תל אביב",
    ) -> None:
        if environment not in {"sandbox", "production"}:
            raise PlannerValidationError("environment must be 'sandbox' or 'production'")
        self.environment = environment
        self.default_city = default_city
        self._stores = {store.key: store for store in (store_configs or default_store_configs())}
        self._catalog = list(catalog or default_catalog())
        self._recipes = list(default_recipes())

    def list_stores(self) -> list[dict[str, Any]]:
        return [asdict(store) for store in self._stores.values()]

    def list_recipes(self, diet: Diet | None = None) -> list[dict[str, Any]]:
        recipes = self._recipes
        if diet:
            recipes = [recipe for recipe in recipes if diet in recipe.diet_tags or diet == "standard"]
        return [recipe_to_dict(recipe) for recipe in recipes]

    def normalize_query(self, query: str) -> str:
        text = re.sub(r"\s+", " ", query.strip().lower())
        synonyms = {
            "עגבניות שרי": "עגבניה",
            "עגבניות": "עגבניה",
            "מלפפונים": "מלפפון",
            "גבינה צהובה": "גבינה",
            "חזה עוף": "עוף",
            "פסטות": "פסטה",
            "rice": "אורז",
            "tomatoes": "עגבניה",
            "cucumber": "מלפפון",
            "chicken": "עוף",
            "pasta": "פסטה",
            "milk": "חלב",
        }
        return synonyms.get(text, text)

    def search_products(
        self,
        query: str,
        store: StoreName | None = None,
        max_results: int = 10,
        require_kosher: bool = True,
        exclude_allergens: Sequence[str] = (),
    ) -> list[dict[str, Any]]:
        if not query.strip():
            raise PlannerValidationError("query must not be empty")
        if max_results < 1:
            raise PlannerValidationError("max_results must be positive")
        normalized = self.normalize_query(query)
        allergen_set = {a.strip().lower() for a in exclude_allergens}
        items = []
        for item in self._catalog:
            if store and item.store != store:
                continue
            if require_kosher and not item.kosher:
                continue
            if allergen_set.intersection({a.lower() for a in item.allergens}):
                continue
            haystack = f"{item.name} {item.category} {item.brand}".lower()
            score = self._score_match(normalized, haystack)
            if score > 0:
                items.append((score, item.unit_price_ils, item))
        items.sort(key=lambda row: (-row[0], row[1], row[2].price_ils))
        return [price_item_to_dict(row[2]) for row in items[:max_results]]

    async def async_search_products(
        self,
        query: str,
        store: StoreName | None = None,
        max_results: int = 10,
        require_kosher: bool = True,
        exclude_allergens: Sequence[str] = (),
    ) -> list[dict[str, Any]]:
        await asyncio.sleep(0)
        return self.search_products(query, store, max_results, require_kosher, exclude_allergens)

    def suggest_recipes(
        self,
        diet: Diet = "standard",
        servings: int = 4,
        max_minutes: int = 45,
        pantry: Sequence[str] = (),
        exclude_allergens: Sequence[str] = (),
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        if servings < 1:
            raise PlannerValidationError("servings must be positive")
        if max_minutes < 5:
            raise PlannerValidationError("max_minutes must be at least 5")
        pantry_terms = {self.normalize_query(item) for item in pantry}
        excluded = {term.lower() for term in exclude_allergens}
        allergen_aliases = {
            "sesame": ("טחינה", "שומשום"),
            "milk": ("חלב", "גבינה", "יוגורט"),
            "egg": ("ביצים",),
            "eggs": ("ביצים",),
        }
        excluded_terms = set(excluded)
        for value in excluded:
            excluded_terms.update(allergen_aliases.get(value, ()))
        scored: list[tuple[float, Recipe]] = []
        for recipe in self._recipes:
            if diet != "standard" and diet not in recipe.diet_tags:
                continue
            if recipe.minutes > max_minutes:
                continue
            ingredient_text = " ".join(i.name for i in recipe.ingredients).lower()
            if any(term in ingredient_text for term in excluded_terms):
                continue
            pantry_hits = sum(1 for ingredient in recipe.ingredients if self.normalize_query(ingredient.name) in pantry_terms)
            budget_bonus = 1 if "low_budget" in recipe.diet_tags else 0
            score = pantry_hits * 2 + budget_bonus + max(0, 60 - recipe.minutes) / 60
            scored.append((score, recipe))
        scored.sort(key=lambda row: (-row[0], row[1].minutes, row[1].title))
        return [recipe_to_dict(recipe) for _, recipe in scored[:limit]]

    async def async_suggest_recipes(
        self,
        diet: Diet = "standard",
        servings: int = 4,
        max_minutes: int = 45,
        pantry: Sequence[str] = (),
        exclude_allergens: Sequence[str] = (),
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        await asyncio.sleep(0)
        return self.suggest_recipes(diet, servings, max_minutes, pantry, exclude_allergens, limit)

    def build_meal_plan(
        self,
        profile: str,
        days: int = 7,
        meals_per_day: int = 1,
        diet: Diet = "standard",
        servings: int = 4,
        max_minutes: int = 45,
        pantry: Sequence[str] = (),
        exclude_allergens: Sequence[str] = (),
    ) -> dict[str, Any]:
        if days < 1 or days > 31:
            raise PlannerValidationError("days must be between 1 and 31")
        if meals_per_day < 1 or meals_per_day > 4:
            raise PlannerValidationError("meals_per_day must be between 1 and 4")
        needed = min(days * meals_per_day, 14)
        candidates = self.suggest_recipes(diet, servings, max_minutes, pantry, exclude_allergens, limit=max(needed, 3))
        if not candidates:
            raise PlannerValidationError("no recipes match the requested constraints")
        recipes = [dict_to_recipe(item) for item in candidates]
        chosen = [recipes[i % len(recipes)] for i in range(needed)]
        assumptions = (
            f"{servings} servings per cooked meal",
            "Prices are estimates until verified in the selected supermarket cart",
            "Pantry quantities are treated as already available",
        )
        plan_id = stable_id("plan", profile, str(days), diet, ",".join(r.key for r in chosen))
        plan = MealPlan(plan_id, profile, days, tuple(chosen), assumptions)
        return meal_plan_to_dict(plan)

    async def async_build_meal_plan(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        await asyncio.sleep(0)
        return self.build_meal_plan(*args, **kwargs)

    def create_basket(
        self,
        meal_plan: dict[str, Any] | MealPlan,
        household_size: int = 4,
        pantry: Sequence[str] = (),
        preferred_store: StoreName | None = None,
        exclude_allergens: Sequence[str] = (),
    ) -> list[dict[str, Any]]:
        if household_size < 1:
            raise PlannerValidationError("household_size must be positive")
        plan = meal_plan if isinstance(meal_plan, MealPlan) else dict_to_meal_plan(meal_plan)
        pantry_terms = {self.normalize_query(item) for item in pantry}
        totals: dict[tuple[str, str], Ingredient] = {}
        scale = household_size / 4
        for recipe in plan.recipes:
            for ingredient in recipe.ingredients:
                key = (self.normalize_query(ingredient.name), ingredient.unit)
                if key[0] in pantry_terms:
                    continue
                existing = totals.get(key)
                quantity = round(ingredient.quantity * scale, 2)
                if existing:
                    totals[key] = Ingredient(existing.name, round(existing.quantity + quantity, 2), existing.unit, existing.category)
                else:
                    totals[key] = Ingredient(ingredient.name, quantity, ingredient.unit, ingredient.category)
        lines = []
        for ingredient in totals.values():
            match = self._best_match(ingredient.name, preferred_store, exclude_allergens)
            substitutions = self._substitutions(ingredient.name, match, exclude_allergens)
            if match:
                package_count = max(1, math.ceil(ingredient.quantity / max(match.package_size, 0.01)))
                cost = round(package_count * match.price_ils, 2)
            else:
                package_count = 0
                cost = 0.0
            lines.append(BasketLine(ingredient, match, ingredient.quantity, package_count, cost, tuple(substitutions)))
        lines.sort(key=lambda line: (line.ingredient.category, line.ingredient.name))
        return [basket_line_to_dict(line) for line in lines]

    async def async_create_basket(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        await asyncio.sleep(0)
        return self.create_basket(*args, **kwargs)

    def compare_basket(
        self,
        basket: Sequence[dict[str, Any] | BasketLine],
        preferred_stores: Sequence[StoreName] | None = None,
        include_delivery: bool = True,
    ) -> dict[str, Any]:
        lines = [line if isinstance(line, BasketLine) else dict_to_basket_line(line) for line in basket]
        stores = list(self._stores.keys()) if preferred_stores is None else list(preferred_stores)
        if not stores:
            raise PlannerValidationError("at least one store is required")
        comparison: dict[str, dict[str, Any]] = {}
        for store in stores:
            subtotal = 0.0
            missing: list[str] = []
            replacements: list[dict[str, Any]] = []
            for line in lines:
                match = self._best_match(line.ingredient.name, store)
                if not match:
                    missing.append(line.ingredient.name)
                    continue
                packages = max(1, math.ceil(line.requested_quantity / max(match.package_size, 0.01)))
                subtotal += packages * match.price_ils
                replacements.append(
                    {
                        "ingredient": line.ingredient.name,
                        "sku": match.sku,
                        "name": match.name,
                        "packages": packages,
                        "cost_ils": round(packages * match.price_ils, 2),
                    }
                )
            delivery = self._stores[store].default_delivery_fee_ils if include_delivery else 0.0
            comparison[store] = {
                "subtotal_ils": round(subtotal, 2),
                "delivery_fee_ils": round(delivery, 2),
                "total_ils": round(subtotal + delivery, 2),
                "missing": missing,
                "lines": replacements,
                "minimum_order_ils": self._stores[store].minimum_order_ils,
            }
        winner = min(comparison.items(), key=lambda pair: (pair[1]["total_ils"], len(pair[1]["missing"])))[0]
        return {"stores": comparison, "recommended_store": winner}

    async def async_compare_basket(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        await asyncio.sleep(0)
        return self.compare_basket(*args, **kwargs)

    def create_order_plan(
        self,
        basket: Sequence[dict[str, Any] | BasketLine],
        city: str | None = None,
        preferred_stores: Sequence[StoreName] | None = None,
        max_stores: int = 2,
        include_delivery: bool = True,
    ) -> dict[str, Any]:
        city_value = city or self.default_city
        if not city_value.strip():
            raise PlannerValidationError("city must not be empty")
        if max_stores < 1 or max_stores > 4:
            raise PlannerValidationError("max_stores must be between 1 and 4")
        lines = [line if isinstance(line, BasketLine) else dict_to_basket_line(line) for line in basket]
        if not lines:
            raise PlannerValidationError("basket must not be empty")
        comparison = self.compare_basket(lines, preferred_stores, include_delivery)
        ranked = sorted(comparison["stores"].items(), key=lambda pair: (pair[1]["total_ils"], len(pair[1]["missing"])))
        selected = [store for store, _ in ranked[:max_stores]]
        first = selected[0]
        selected_lines = []
        subtotal = 0.0
        warnings: list[str] = []
        for line in lines:
            match = self._best_match(line.ingredient.name, first)
            if match:
                packages = max(1, math.ceil(line.requested_quantity / max(match.package_size, 0.01)))
                subtotal += packages * match.price_ils
                selected_lines.append(BasketLine(line.ingredient, match, line.requested_quantity, packages, round(packages * match.price_ils, 2), line.substitutions))
            else:
                warnings.append(f"No match found for {line.ingredient.name} at {self._stores[first].display_name}")
                selected_lines.append(line)
        delivery = self._stores[first].default_delivery_fee_ils if include_delivery else 0.0
        if subtotal < self._stores[first].minimum_order_ils:
            warnings.append(
                f"Estimated subtotal ₪{subtotal:.2f} is below the minimum order of ₪{self._stores[first].minimum_order_ils:.2f}"
            )
        store_totals = {first: round(subtotal, 2)}
        order_id = stable_id("order", city_value, first, json.dumps([basket_line_to_dict(line) for line in selected_lines], ensure_ascii=False, sort_keys=True))
        links = self.generate_store_links(selected_lines, selected)
        plan = OrderPlan(
            order_id=order_id,
            city=city_value,
            environment=self.environment,
            lines=tuple(selected_lines),
            selected_stores=tuple(selected),
            store_totals_ils=store_totals,
            delivery_fee_ils=round(delivery, 2),
            estimated_total_ils=round(subtotal + delivery, 2),
            warnings=tuple(warnings),
            store_links=links,
        )
        return order_plan_to_dict(plan)

    async def async_create_order_plan(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        await asyncio.sleep(0)
        return self.create_order_plan(*args, **kwargs)

    def split_order(self, order_plan: dict[str, Any] | OrderPlan, max_stores: int = 2) -> dict[str, Any]:
        plan = order_plan if isinstance(order_plan, OrderPlan) else dict_to_order_plan(order_plan)
        if max_stores < 1:
            raise PlannerValidationError("max_stores must be positive")
        stores = plan.selected_stores[:max_stores]
        if not stores:
            raise PlannerValidationError("order plan must include selected stores")
        buckets = {store: [] for store in stores}
        for index, line in enumerate(plan.lines):
            store = stores[index % len(stores)]
            buckets[store].append(basket_line_to_dict(line))
        return {
            "order_id": plan.order_id,
            "split_count": len(stores),
            "stores": {store: {"lines": buckets[store], "link": plan.store_links.get(store, "")} for store in stores},
        }

    def export_shopping_list(self, basket: Sequence[dict[str, Any] | BasketLine], locale: Literal["he-IL", "en-IL"] = "he-IL") -> str:
        lines = [line if isinstance(line, BasketLine) else dict_to_basket_line(line) for line in basket]
        if locale not in {"he-IL", "en-IL"}:
            raise PlannerValidationError("locale must be he-IL or en-IL")
        output = []
        for line in lines:
            item_name = line.matched_item.name if line.matched_item else line.ingredient.name
            cost = format_ils(line.estimated_cost_ils)
            if locale == "he-IL":
                output.append(f"{item_name}: {line.estimated_packages} יחידות, {cost}")
            else:
                output.append(f"{item_name}: {line.estimated_packages} packages, {cost}")
        return "\n".join(output)

    def import_price_feed(self, path: str | Path, store: StoreName | None = None) -> list[dict[str, Any]]:
        file_path = Path(path)
        if not file_path.exists():
            raise PlannerValidationError(f"price feed not found: {file_path}")
        if file_path.suffix.lower() == ".json":
            raw = json.loads(file_path.read_text(encoding="utf-8"))
            rows = raw if isinstance(raw, list) else raw.get("items", [])
        elif file_path.suffix.lower() == ".csv":
            with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
        else:
            raise PlannerValidationError("price feed must be CSV or JSON")
        parsed = []
        for idx, row in enumerate(rows, start=1):
            try:
                store_value = row.get("store") or store
                if store_value not in self._stores:
                    raise PlannerValidationError("unknown store")
                item = PriceItem(
                    sku=str(row.get("sku") or stable_id("sku", str(idx))),
                    store=store_value,  # type: ignore[arg-type]
                    name=str(row["name"]),
                    category=str(row.get("category") or "general"),
                    unit=str(row.get("unit") or "unit"),
                    package_size=float(row.get("package_size") or 1),
                    price_ils=float(row.get("price_ils") or row.get("price") or 0),
                    brand=str(row.get("brand") or ""),
                    kosher=str(row.get("kosher", "true")).lower() not in {"false", "0", "no"},
                    allergens=tuple(split_terms(str(row.get("allergens") or ""))),
                    promotion=str(row.get("promotion") or "") or None,
                    last_updated=str(row.get("last_updated") or "") or None,
                )
            except KeyError as exc:
                raise PlannerValidationError(f"missing required field {exc.args[0]} on row {idx}") from exc
            except ValueError as exc:
                raise PlannerValidationError(f"invalid numeric field on row {idx}") from exc
            if item.price_ils < 0:
                raise PlannerValidationError(f"negative price on row {idx}")
            self._catalog.append(item)
            parsed.append(price_item_to_dict(item))
        return parsed

    def validate_order_plan(self, order_plan: dict[str, Any] | OrderPlan) -> dict[str, Any]:
        plan = order_plan if isinstance(order_plan, OrderPlan) else dict_to_order_plan(order_plan)
        issues = list(plan.warnings)
        if not plan.lines:
            issues.append("Order has no lines")
        if plan.estimated_total_ils <= 0:
            issues.append("Estimated total must be positive")
        for store in plan.selected_stores:
            if store not in self._stores:
                issues.append(f"Unknown store {store}")
        for line in plan.lines:
            if line.estimated_packages < 0:
                issues.append(f"Negative package count for {line.ingredient.name}")
        return {"order_id": plan.order_id, "valid": not issues, "issues": issues}

    def calculate_budget(
        self,
        basket: Sequence[dict[str, Any] | BasketLine],
        weekly_limit_ils: float,
        include_delivery: bool = True,
    ) -> dict[str, Any]:
        if weekly_limit_ils <= 0:
            raise PlannerValidationError("weekly_limit_ils must be positive")
        subtotal = round(sum((line if isinstance(line, BasketLine) else dict_to_basket_line(line)).estimated_cost_ils for line in basket), 2)
        delivery = 29.90 if include_delivery else 0.0
        total = round(subtotal + delivery, 2)
        return {
            "subtotal_ils": subtotal,
            "delivery_fee_ils": delivery,
            "total_ils": total,
            "weekly_limit_ils": weekly_limit_ils,
            "remaining_ils": round(weekly_limit_ils - total, 2),
            "over_budget": total > weekly_limit_ils,
        }

    def generate_store_links(
        self,
        basket: Sequence[dict[str, Any] | BasketLine],
        stores: Sequence[StoreName] | None = None,
    ) -> dict[str, str]:
        lines = [line if isinstance(line, BasketLine) else dict_to_basket_line(line) for line in basket]
        selected = list(stores or self._stores.keys())
        query = " ".join(line.ingredient.name for line in lines[:8])
        return {store: self._stores[store].search_url_template.format(query=quote_plus(query)) for store in selected if store in self._stores}

    @staticmethod
    def _score_match(query: str, haystack: str) -> int:
        if query in haystack:
            return 10
        tokens = [token for token in re.split(r"\W+", query) if token]
        return sum(2 for token in tokens if token in haystack)

    def _best_match(
        self,
        ingredient_name: str,
        store: StoreName | None = None,
        exclude_allergens: Sequence[str] = (),
    ) -> PriceItem | None:
        results = self.search_products(ingredient_name, store=store, max_results=1, exclude_allergens=exclude_allergens)
        if not results:
            return None
        return dict_to_price_item(results[0])

    def _substitutions(
        self,
        ingredient_name: str,
        selected: PriceItem | None,
        exclude_allergens: Sequence[str] = (),
    ) -> list[PriceItem]:
        results = self.search_products(ingredient_name, max_results=4, exclude_allergens=exclude_allergens)
        substitutions = [dict_to_price_item(item) for item in results]
        if selected:
            substitutions = [item for item in substitutions if item.sku != selected.sku]
        return substitutions[:3]


def default_store_configs() -> list[StoreConfig]:
    return [
        StoreConfig("shufersal", "Shufersal", "https://www.shufersal.co.il/online/he/search?text={query}", "https://www.shufersal.co.il/online/he", "Use published price files, official online search, or verified cart prices; sandbox fees are estimates.", 29.90, 180.0),
        StoreConfig("rami_levy", "Rami Levy", "https://www.rami-levy.co.il/he/online/search?q={query}", "https://www.rami-levy.co.il", "Use published price files, official online search, or verified cart prices; sandbox fees are estimates.", 28.90, 150.0),
        StoreConfig("victory", "Victory", "https://www.victoryonline.co.il/", "https://www.victoryonline.co.il", "Use published price files, official online search, or verified cart prices; sandbox fees are estimates.", 29.90, 160.0),
        StoreConfig("yochananof", "Yochananof", "https://yochananof.co.il/search", "https://www.yochananof.co.il", "Use published price files, official online search, or verified cart prices; sandbox fees are estimates.", 29.90, 150.0),
    ]


def default_catalog() -> list[PriceItem]:
    base_items = [
        ("עגבניה", "produce", "kg", 1.0, {"shufersal": 7.90, "rami_levy": 6.90, "victory": 7.50, "yochananof": 6.80}),
        ("מלפפון", "produce", "kg", 1.0, {"shufersal": 6.90, "rami_levy": 5.90, "victory": 6.40, "yochananof": 5.80}),
        ("בצל יבש", "produce", "kg", 1.0, {"shufersal": 4.90, "rami_levy": 3.90, "victory": 4.50, "yochananof": 3.80}),
        ("תפוח אדמה", "produce", "kg", 1.0, {"shufersal": 5.90, "rami_levy": 4.90, "victory": 5.40, "yochananof": 4.80}),
        ("פסטה", "dry", "g", 500.0, {"shufersal": 5.90, "rami_levy": 4.90, "victory": 5.50, "yochananof": 4.70}),
        ("אורז פרסי", "dry", "kg", 1.0, {"shufersal": 9.90, "rami_levy": 8.90, "victory": 9.50, "yochananof": 8.70}),
        ("עדשים ירוקות", "dry", "g", 500.0, {"shufersal": 7.90, "rami_levy": 6.90, "victory": 7.20, "yochananof": 6.80}),
        ("חומוס גרגרים", "dry", "g", 500.0, {"shufersal": 8.90, "rami_levy": 7.90, "victory": 8.40, "yochananof": 7.70}),
        ("חלב 3 אחוז", "dairy", "l", 1.0, {"shufersal": 6.23, "rami_levy": 6.23, "victory": 6.23, "yochananof": 6.23}),
        ("גבינה לבנה", "dairy", "g", 250.0, {"shufersal": 6.50, "rami_levy": 5.90, "victory": 6.20, "yochananof": 5.80}),
        ("יוגורט טבעי", "dairy", "g", 150.0, {"shufersal": 3.20, "rami_levy": 2.90, "victory": 3.10, "yochananof": 2.80}),
        ("ביצים גודל L", "eggs", "unit", 12.0, {"shufersal": 14.90, "rami_levy": 13.90, "victory": 14.40, "yochananof": 13.80}),
        ("חזה עוף טרי", "meat", "kg", 1.0, {"shufersal": 34.90, "rami_levy": 29.90, "victory": 32.90, "yochananof": 28.90}),
        ("טונה במים", "canned", "g", 160.0, {"shufersal": 6.90, "rami_levy": 5.90, "victory": 6.40, "yochananof": 5.80}),
        ("שמן זית", "oil", "ml", 750.0, {"shufersal": 32.90, "rami_levy": 29.90, "victory": 31.50, "yochananof": 28.90}),
        ("טחינה גולמית", "spread", "g", 500.0, {"shufersal": 13.90, "rami_levy": 11.90, "victory": 12.90, "yochananof": 11.50}),
        ("לחם אחיד פרוס", "bakery", "unit", 1.0, {"shufersal": 7.11, "rami_levy": 7.11, "victory": 7.11, "yochananof": 7.11}),
        ("קוואקר", "dry", "g", 500.0, {"shufersal": 8.90, "rami_levy": 7.90, "victory": 8.40, "yochananof": 7.70}),
        ("בננה", "produce", "kg", 1.0, {"shufersal": 8.90, "rami_levy": 7.90, "victory": 8.20, "yochananof": 7.80}),
        ("תפוח עץ", "produce", "kg", 1.0, {"shufersal": 11.90, "rami_levy": 9.90, "victory": 10.90, "yochananof": 9.80}),
    ]
    catalog: list[PriceItem] = []
    for name, category, unit, package_size, prices in base_items:
        for store, price in prices.items():
            allergens: tuple[str, ...] = ()
            if category == "dairy":
                allergens = ("milk",)
            if name == "טחינה גולמית":
                allergens = ("sesame",)
            catalog.append(
                PriceItem(
                    sku=stable_id("sku", store, name),
                    store=store,  # type: ignore[arg-type]
                    name=name,
                    category=category,
                    unit=unit,
                    package_size=package_size,
                    price_ils=price,
                    brand="",
                    allergens=allergens,
                    last_updated="01/06/2026",
                )
            )
    return catalog


def default_recipes() -> list[Recipe]:
    return [
        Recipe(
            key="lentil-rice-bowl",
            title="תבשיל עדשים ואורז",
            servings=4,
            minutes=35,
            diet_tags=("vegetarian", "vegan", "low_budget"),
            ingredients=(
                Ingredient("עדשים ירוקות", 500, "g", "dry"),
                Ingredient("אורז פרסי", 1, "kg", "dry"),
                Ingredient("בצל יבש", 0.5, "kg", "produce"),
                Ingredient("עגבניה", 0.5, "kg", "produce"),
                Ingredient("שמן זית", 60, "ml", "oil"),
            ),
            steps=("לשטוף אורז ועדשים.", "לטגן בצל, להוסיף עגבניה, אורז ועדשים.", "לבשל עד ריכוך ולתקן תיבול."),
            notes="מתאים להכנה מראש ולחימום בעסק קטן.",
        ),
        Recipe(
            key="chicken-potato-tray",
            title="תבנית עוף ותפוחי אדמה",
            servings=4,
            minutes=50,
            diet_tags=("standard", "kosher_meat"),
            ingredients=(
                Ingredient("חזה עוף טרי", 1, "kg", "meat"),
                Ingredient("תפוח אדמה", 1.5, "kg", "produce"),
                Ingredient("בצל יבש", 0.4, "kg", "produce"),
                Ingredient("שמן זית", 50, "ml", "oil"),
            ),
            steps=("לחתוך ירקות.", "לתבל עוף וירקות.", "לאפות עד שהעוף מוכן."),
            notes="בדוק הפרדה בין בשר וחלב בעגלת הקניות.",
        ),
        Recipe(
            key="israeli-breakfast",
            title="ארוחת בוקר ישראלית",
            servings=4,
            minutes=20,
            diet_tags=("standard", "vegetarian", "kosher_dairy"),
            ingredients=(
                Ingredient("ביצים גודל L", 8, "unit", "eggs"),
                Ingredient("גבינה לבנה", 500, "g", "dairy"),
                Ingredient("מלפפון", 0.5, "kg", "produce"),
                Ingredient("עגבניה", 0.5, "kg", "produce"),
                Ingredient("לחם אחיד פרוס", 1, "unit", "bakery"),
            ),
            steps=("להכין ביצים לפי העדפה.", "לחתוך ירקות.", "להגיש עם גבינה ולחם."),
            notes="מתאים לאירוח קטן במשרד.",
        ),
        Recipe(
            key="pasta-tuna-salad",
            title="סלט פסטה וטונה",
            servings=4,
            minutes=25,
            diet_tags=("standard", "low_budget"),
            ingredients=(
                Ingredient("פסטה", 500, "g", "dry"),
                Ingredient("טונה במים", 320, "g", "canned"),
                Ingredient("מלפפון", 0.4, "kg", "produce"),
                Ingredient("עגבניה", 0.4, "kg", "produce"),
                Ingredient("שמן זית", 40, "ml", "oil"),
            ),
            steps=("לבשל פסטה ולקרר.", "לסנן טונה.", "לערבב עם ירקות ותיבול."),
            notes="שמור בקירור עד ההגשה.",
        ),
        Recipe(
            key="hummus-tahini-plates",
            title="צלחות חומוס וטחינה",
            servings=4,
            minutes=30,
            diet_tags=("vegetarian", "vegan", "low_budget"),
            ingredients=(
                Ingredient("חומוס גרגרים", 500, "g", "dry"),
                Ingredient("טחינה גולמית", 500, "g", "spread"),
                Ingredient("מלפפון", 0.5, "kg", "produce"),
                Ingredient("עגבניה", 0.5, "kg", "produce"),
                Ingredient("לחם אחיד פרוס", 1, "unit", "bakery"),
            ),
            steps=("לבשל או להשתמש בחומוס מוכן.", "לערבב טחינה עם מים ולימון.", "להגיש עם ירקות ולחם."),
            notes="בדוק רגישות לשומשום.",
        ),
        Recipe(
            key="oat-fruit-yogurt",
            title="קוואקר עם יוגורט ופירות",
            servings=4,
            minutes=10,
            diet_tags=("vegetarian", "kosher_dairy", "low_budget"),
            ingredients=(
                Ingredient("קוואקר", 300, "g", "dry"),
                Ingredient("יוגורט טבעי", 600, "g", "dairy"),
                Ingredient("בננה", 0.5, "kg", "produce"),
                Ingredient("תפוח עץ", 0.5, "kg", "produce"),
            ),
            steps=("לחלק קוואקר לקערות.", "להוסיף יוגורט ופירות חתוכים.", "להגיש קר."),
            notes="מתאים לארוחת בוקר מהירה.",
        ),
    ]


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def format_ils(value: float) -> str:
    return f"₪{value:,.2f}"


def split_terms(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,;|]", text) if part.strip()]


def price_item_to_dict(item: PriceItem) -> dict[str, Any]:
    data = asdict(item)
    data["unit_price_ils"] = item.unit_price_ils
    return data


def dict_to_price_item(data: dict[str, Any]) -> PriceItem:
    clean = dict(data)
    clean.pop("unit_price_ils", None)
    if isinstance(clean.get("allergens"), list):
        clean["allergens"] = tuple(clean["allergens"])
    return PriceItem(**clean)


def ingredient_to_dict(item: Ingredient) -> dict[str, Any]:
    return asdict(item)


def dict_to_ingredient(data: dict[str, Any]) -> Ingredient:
    return Ingredient(**data)


def recipe_to_dict(recipe: Recipe) -> dict[str, Any]:
    data = asdict(recipe)
    data["ingredients"] = [ingredient_to_dict(item) for item in recipe.ingredients]
    data["diet_tags"] = list(recipe.diet_tags)
    data["steps"] = list(recipe.steps)
    return data


def dict_to_recipe(data: dict[str, Any]) -> Recipe:
    return Recipe(
        key=data["key"],
        title=data["title"],
        servings=int(data["servings"]),
        minutes=int(data["minutes"]),
        diet_tags=tuple(data.get("diet_tags", [])),
        ingredients=tuple(dict_to_ingredient(item) for item in data.get("ingredients", [])),
        steps=tuple(data.get("steps", [])),
        notes=data.get("notes", ""),
    )


def basket_line_to_dict(line: BasketLine) -> dict[str, Any]:
    return {
        "ingredient": ingredient_to_dict(line.ingredient),
        "matched_item": price_item_to_dict(line.matched_item) if line.matched_item else None,
        "requested_quantity": line.requested_quantity,
        "estimated_packages": line.estimated_packages,
        "estimated_cost_ils": line.estimated_cost_ils,
        "substitutions": [price_item_to_dict(item) for item in line.substitutions],
    }


def dict_to_basket_line(data: dict[str, Any]) -> BasketLine:
    return BasketLine(
        ingredient=dict_to_ingredient(data["ingredient"]),
        matched_item=dict_to_price_item(data["matched_item"]) if data.get("matched_item") else None,
        requested_quantity=float(data.get("requested_quantity", data["ingredient"].get("quantity", 0))),
        estimated_packages=int(data.get("estimated_packages", 0)),
        estimated_cost_ils=float(data.get("estimated_cost_ils", 0)),
        substitutions=tuple(dict_to_price_item(item) for item in data.get("substitutions", [])),
    )


def meal_plan_to_dict(plan: MealPlan) -> dict[str, Any]:
    return {
        "plan_id": plan.plan_id,
        "profile": plan.profile,
        "days": plan.days,
        "recipes": [recipe_to_dict(recipe) for recipe in plan.recipes],
        "assumptions": list(plan.assumptions),
    }


def dict_to_meal_plan(data: dict[str, Any]) -> MealPlan:
    return MealPlan(
        plan_id=data["plan_id"],
        profile=data["profile"],
        days=int(data["days"]),
        recipes=tuple(dict_to_recipe(item) for item in data.get("recipes", [])),
        assumptions=tuple(data.get("assumptions", [])),
    )


def order_plan_to_dict(plan: OrderPlan) -> dict[str, Any]:
    return {
        "order_id": plan.order_id,
        "city": plan.city,
        "environment": plan.environment,
        "lines": [basket_line_to_dict(line) for line in plan.lines],
        "selected_stores": list(plan.selected_stores),
        "store_totals_ils": plan.store_totals_ils,
        "delivery_fee_ils": plan.delivery_fee_ils,
        "estimated_total_ils": plan.estimated_total_ils,
        "warnings": list(plan.warnings),
        "store_links": plan.store_links,
        "created_date": plan.created_date,
    }


def dict_to_order_plan(data: dict[str, Any]) -> OrderPlan:
    return OrderPlan(
        order_id=data["order_id"],
        city=data["city"],
        environment=data.get("environment", "sandbox"),
        lines=tuple(dict_to_basket_line(item) for item in data.get("lines", [])),
        selected_stores=tuple(data.get("selected_stores", [])),
        store_totals_ils=dict(data.get("store_totals_ils", {})),
        delivery_fee_ils=float(data.get("delivery_fee_ils", 0)),
        estimated_total_ils=float(data.get("estimated_total_ils", 0)),
        warnings=tuple(data.get("warnings", [])),
        store_links=dict(data.get("store_links", {})),
        created_date=data.get("created_date", date.today().isoformat()),
    )
