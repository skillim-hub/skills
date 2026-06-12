from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from .client import MealGroceryPlannerClient, PlannerValidationError

app = typer.Typer(help="Plan Israeli grocery baskets, recipe lists, and supermarket order links.")


def _client(env: str) -> MealGroceryPlannerClient:
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    default_city = os.getenv("MEAL_GROCERY_CITY", "תל אביב")
    return MealGroceryPlannerClient(environment=env, default_city=default_city)  # type: ignore[arg-type]


def _print(data: object) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


def _store_dir() -> Path:
    path = Path(os.getenv("MEAL_GROCERY_ORDER_DIR", ".meal_grocery_planner_orders"))
    path.mkdir(parents=True, exist_ok=True)
    return path


@app.command()
def stores(env: str = typer.Option("sandbox", "--env", help="sandbox or production")) -> None:
    client = _client(env)
    _print(client.list_stores())


@app.command()
def recipes(
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    diet: str = typer.Option("standard", "--diet", help="standard, vegetarian, vegan, kosher_meat, kosher_dairy, low_budget"),
    servings: int = typer.Option(4, "--servings"),
    max_minutes: int = typer.Option(45, "--max-minutes"),
) -> None:
    client = _client(env)
    _print(client.suggest_recipes(diet=diet, servings=servings, max_minutes=max_minutes))  # type: ignore[arg-type]


@app.command()
def meal_plan(
    profile: str = typer.Option("family", "--profile"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    days: int = typer.Option(7, "--days"),
    meals_per_day: int = typer.Option(1, "--meals-per-day"),
    diet: str = typer.Option("standard", "--diet"),
    servings: int = typer.Option(4, "--servings"),
) -> None:
    client = _client(env)
    _print(client.build_meal_plan(profile=profile, days=days, meals_per_day=meals_per_day, diet=diet, servings=servings))  # type: ignore[arg-type]


@app.command()
def basket(
    profile: str = typer.Option("family", "--profile"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    days: int = typer.Option(7, "--days"),
    household_size: int = typer.Option(4, "--household-size"),
    diet: str = typer.Option("standard", "--diet"),
) -> None:
    client = _client(env)
    plan = client.build_meal_plan(profile=profile, days=days, diet=diet)  # type: ignore[arg-type]
    _print(client.create_basket(plan, household_size=household_size))


@app.command()
def order(
    profile: str = typer.Option("family", "--profile"),
    city: Optional[str] = typer.Option(None, "--city"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    days: int = typer.Option(7, "--days"),
    household_size: int = typer.Option(4, "--household-size"),
    diet: str = typer.Option("standard", "--diet"),
    max_stores: int = typer.Option(2, "--max-stores"),
    save: bool = typer.Option(False, "--save", help="Store the order JSON locally so the id can be used by show-order."),
) -> None:
    client = _client(env)
    plan = client.build_meal_plan(profile=profile, days=days, diet=diet)  # type: ignore[arg-type]
    basket_lines = client.create_basket(plan, household_size=household_size)
    order_plan = client.create_order_plan(basket_lines, city=city, max_stores=max_stores)
    if save:
        (_store_dir() / f"{order_plan['order_id']}.json").write_text(json.dumps(order_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    _print(order_plan)


@app.command("show-order")
def show_order(
    order_id: str = typer.Argument(...),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
) -> None:
    _client(env)
    path = _store_dir() / f"{order_id}.json"
    if not path.exists():
        raise typer.BadParameter(f"order id not found: {order_id}")
    _print(json.loads(path.read_text(encoding="utf-8")))


@app.command("import-feed")
def import_feed(
    path: Path = typer.Argument(..., exists=True, readable=True),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    store: Optional[str] = typer.Option(None, "--store", help="Default store for rows without a store column."),
) -> None:
    client = _client(env)
    _print(client.import_price_feed(path, store=store))  # type: ignore[arg-type]


@app.command()
def validate(
    order_id: str = typer.Argument(...),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
) -> None:
    _client(env)
    path = _store_dir() / f"{order_id}.json"
    if not path.exists():
        raise typer.BadParameter(f"order id not found: {order_id}")
    client = _client(env)
    order_plan = json.loads(path.read_text(encoding="utf-8"))
    _print(client.validate_order_plan(order_plan))


def main() -> None:
    try:
        app()
    except PlannerValidationError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


if __name__ == "__main__":
    main()
