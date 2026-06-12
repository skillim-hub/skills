"""Command-line interface for the Savings Goal Planner."""

from __future__ import annotations

import json
from typing import Any, Mapping

import click

from .client import (
    GoalRepository,
    GoalRequest,
    RetirementRequest,
    SavingsGoalError,
    SavingsGoalPlannerClient,
    VEHICLES,
    format_ils,
)


def _print_json(data: Mapping[str, Any] | list[Mapping[str, Any]]) -> None:
    click.echo(json.dumps(data, ensure_ascii=False, indent=2))


def _print_goal_table(result: Any) -> None:
    click.echo(f"Goal: {result.goal_name}")
    click.echo(f"Target future value: {format_ils(result.target_future_value)}")
    click.echo(f"Months: {result.months}")
    click.echo(f"Monthly required: {format_ils(result.monthly_required)}")
    click.echo(f"Current monthly savings: {format_ils(result.current_monthly_savings)}")
    click.echo(f"Projected total: {format_ils(result.projected_total_value)}")
    click.echo(f"Shortfall at current rate: {format_ils(result.shortfall_at_current_rate)}")
    click.echo(f"Effective annual return: {result.effective_annual_return:.2%}")
    if result.vehicle:
        click.echo(f"Vehicle: {result.vehicle.english_name} / {result.vehicle.hebrew_name}")
    if result.warnings:
        click.echo("Warnings:")
        for warning in result.warnings:
            click.echo(f"- {warning}")


def _print_retirement_table(result: Any) -> None:
    click.echo("Retirement gap plan")
    click.echo(f"Accumulation months: {result.accumulation_months}")
    click.echo(f"Retirement months: {result.retirement_months}")
    click.echo(f"Monthly income gap today: {format_ils(result.monthly_income_gap_today)}")
    click.echo(f"Required nest egg today: {format_ils(result.required_nest_egg_today)}")
    click.echo(f"Monthly required today: {format_ils(result.monthly_required_today)}")
    click.echo(f"Projected current savings today: {format_ils(result.projected_current_savings_today)}")
    if result.warnings:
        click.echo("Warnings:")
        for warning in result.warnings:
            click.echo(f"- {warning}")


def _goal_request(
    name: str,
    target: float,
    months: int,
    current_savings: float,
    current_monthly: float,
    annual_return: float | None,
    annual_fee: float | None,
    tax_rate_on_gain: float | None,
    inflation_rate: float,
    future_amount: bool,
    timing: str,
    vehicle_key: str | None,
    monthly_income: float | None,
) -> GoalRequest:
    return GoalRequest(
        goal_name=name,
        target_amount=target,
        months=months,
        current_savings=current_savings,
        current_monthly_savings=current_monthly,
        annual_return=annual_return,
        annual_fee=annual_fee,
        tax_rate_on_gain=tax_rate_on_gain,
        inflation_rate=inflation_rate,
        amount_is_today_terms=not future_amount,
        contribution_timing=timing,  # type: ignore[arg-type]
        vehicle_key=vehicle_key,
        monthly_income=monthly_income,
    )


def _goal_options(function):
    function = click.option("--monthly-income", default=None, type=float)(function)
    function = click.option("--vehicle", "vehicle_key", default=None, help="Vehicle preset key. Run 'vehicles' for choices.")(function)
    function = click.option("--timing", type=click.Choice(["end", "beginning"]), default="end", show_default=True)(function)
    function = click.option("--future-amount/--today-amount", default=False, help="Mark target as already future nominal value.")(function)
    function = click.option("--inflation-rate", default=0.0, show_default=True, type=float)(function)
    function = click.option("--tax-rate-on-gain", default=None, type=float, help="Override tax drag on gains, for example 0.25.")(function)
    function = click.option("--annual-fee", default=None, type=float, help="Override annual fee, for example 0.006.")(function)
    function = click.option("--annual-return", default=None, type=float, help="Override annual return, for example 0.04.")(function)
    function = click.option("--current-monthly", default=0.0, show_default=True, type=float)(function)
    function = click.option("--current-savings", default=0.0, show_default=True, type=float)(function)
    function = click.option("--months", required=True, type=int, help="Months until money is needed.")(function)
    function = click.option("--target", required=True, type=float, help="Target amount in ILS.")(function)
    function = click.option("--name", default="Savings goal", show_default=True)(function)
    return function


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Plan Israeli savings goals, vehicle scenarios, and retirement gaps."""


@main.command()
@_goal_options
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table", show_default=True)
def goal(
    name: str,
    target: float,
    months: int,
    current_savings: float,
    current_monthly: float,
    annual_return: float | None,
    annual_fee: float | None,
    tax_rate_on_gain: float | None,
    inflation_rate: float,
    future_amount: bool,
    timing: str,
    vehicle_key: str | None,
    monthly_income: float | None,
    fmt: str,
) -> None:
    """Calculate monthly savings required for a purchase or reserve."""

    try:
        request = _goal_request(
            name,
            target,
            months,
            current_savings,
            current_monthly,
            annual_return,
            annual_fee,
            tax_rate_on_gain,
            inflation_rate,
            future_amount,
            timing,
            vehicle_key,
            monthly_income,
        )
        result = SavingsGoalPlannerClient().calculate_goal(request)
    except SavingsGoalError as exc:
        raise click.ClickException(str(exc)) from exc
    if fmt == "json":
        _print_json(result.to_dict())
    else:
        _print_goal_table(result)


@main.command("create-goal")
@_goal_options
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--store", default=None, type=click.Path(dir_okay=False, path_type=str), help="Optional JSON store path.")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="json", show_default=True)
def create_goal(
    name: str,
    target: float,
    months: int,
    current_savings: float,
    current_monthly: float,
    annual_return: float | None,
    annual_fee: float | None,
    tax_rate_on_gain: float | None,
    inflation_rate: float,
    future_amount: bool,
    timing: str,
    vehicle_key: str | None,
    monthly_income: float | None,
    environment: str,
    store: str | None,
    fmt: str,
) -> None:
    """Create a stored goal and return its identifier."""

    try:
        request = _goal_request(
            name,
            target,
            months,
            current_savings,
            current_monthly,
            annual_return,
            annual_fee,
            tax_rate_on_gain,
            inflation_rate,
            future_amount,
            timing,
            vehicle_key,
            monthly_income,
        )
        stored = SavingsGoalPlannerClient().create_goal(request, store, environment)  # type: ignore[arg-type]
    except SavingsGoalError as exc:
        raise click.ClickException(str(exc)) from exc
    if fmt == "json":
        _print_json(stored.to_dict())
    else:
        click.echo(f"Created goal {stored.id}")
        _print_goal_table(stored.result)


@main.command("show-goal")
@click.option("--id", "goal_id", required=True, help="Goal identifier from create-goal.")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--store", default=None, type=click.Path(dir_okay=False, path_type=str), help="Optional JSON store path.")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="json", show_default=True)
def show_goal(goal_id: str, environment: str, store: str | None, fmt: str) -> None:
    """Show a stored goal by identifier."""

    try:
        stored = SavingsGoalPlannerClient().get_goal(goal_id, store, environment)  # type: ignore[arg-type]
    except SavingsGoalError as exc:
        raise click.ClickException(str(exc)) from exc
    if fmt == "json":
        _print_json(stored.to_dict())
    else:
        click.echo(f"Goal id: {stored.id}")
        _print_goal_table(stored.result)


@main.command("list-goals")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--store", default=None, type=click.Path(dir_okay=False, path_type=str), help="Optional JSON store path.")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table", show_default=True)
def list_goals(environment: str, store: str | None, fmt: str) -> None:
    """List stored goal identifiers."""

    try:
        goals = SavingsGoalPlannerClient().list_goals(store, environment)  # type: ignore[arg-type]
    except SavingsGoalError as exc:
        raise click.ClickException(str(exc)) from exc
    if fmt == "json":
        _print_json([goal.to_dict() for goal in goals])
        return
    for item in goals:
        click.echo(f"{item.id} {item.environment} {item.created_at} {item.request.goal_name}")


@main.command("delete-goal")
@click.option("--id", "goal_id", required=True, help="Goal identifier from create-goal.")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--store", default=None, type=click.Path(dir_okay=False, path_type=str), help="Optional JSON store path.")
def delete_goal(goal_id: str, environment: str, store: str | None) -> None:
    """Delete a stored goal by identifier."""

    try:
        deleted = GoalRepository(store, environment).delete_goal(goal_id)  # type: ignore[arg-type]
    except SavingsGoalError as exc:
        raise click.ClickException(str(exc)) from exc
    if not deleted:
        raise click.ClickException(f"goal not found: {goal_id}")
    click.echo(f"Deleted goal {goal_id}")


@main.command()
@click.option("--current-age", required=True, type=float)
@click.option("--retirement-age", required=True, type=float)
@click.option("--life-expectancy", required=True, type=float)
@click.option("--monthly-spending", required=True, type=float, help="Desired monthly spending in today's ILS.")
@click.option("--expected-pension", "--state-pension", "expected_pension", default=0.0, show_default=True, type=float, help="Expected monthly pension or allowance income in today's ILS.")
@click.option("--current-savings", default=0.0, show_default=True, type=float)
@click.option("--accumulation-return", default=0.04, show_default=True, type=float, help="Annual real accumulation return.")
@click.option("--retirement-return", default=0.025, show_default=True, type=float, help="Annual real retirement return.")
@click.option("--timing", type=click.Choice(["end", "beginning"]), default="end", show_default=True)
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table", show_default=True)
def retirement(
    current_age: float,
    retirement_age: float,
    life_expectancy: float,
    monthly_spending: float,
    expected_pension: float,
    current_savings: float,
    accumulation_return: float,
    retirement_return: float,
    timing: str,
    fmt: str,
) -> None:
    """Calculate a retirement savings gap using real returns."""

    try:
        request = RetirementRequest(
            current_age=current_age,
            retirement_age=retirement_age,
            life_expectancy=life_expectancy,
            desired_monthly_spending_today=monthly_spending,
            expected_monthly_pension_today=expected_pension,
            current_retirement_savings=current_savings,
            annual_real_return_accumulation=accumulation_return,
            annual_real_return_retirement=retirement_return,
            contribution_timing=timing,  # type: ignore[arg-type]
        )
        result = SavingsGoalPlannerClient().calculate_retirement(request)
    except SavingsGoalError as exc:
        raise click.ClickException(str(exc)) from exc
    if fmt == "json":
        _print_json(result.to_dict())
    else:
        _print_retirement_table(result)


@main.command()
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table", show_default=True)
def vehicles(fmt: str) -> None:
    """List available Israeli savings and investment vehicle presets."""

    data = {key: VEHICLES[key].__dict__ for key in sorted(VEHICLES)}
    if fmt == "json":
        _print_json(data)
        return

    for key, vehicle in data.items():
        click.echo(f"{key}: {vehicle['english_name']} / {vehicle['hebrew_name']}")
        click.echo(f"  risk={vehicle['risk_level']} min_horizon={vehicle['min_horizon_months']} months")
        click.echo(f"  default_return={vehicle['default_annual_return']:.2%} fee={vehicle['default_annual_fee']:.2%}")
        click.echo(f"  caution={vehicle['caution']}")


@main.command("recommend-vehicles")
@click.option("--months", required=True, type=int)
@click.option("--risk", "risk_tolerance", type=click.Choice(["very_low", "low", "medium", "high"]), default="medium", show_default=True)
@click.option("--liquidity", "liquidity_need", type=click.Choice(["same_day", "few_days", "locked_ok"]), default="few_days", show_default=True)
@click.option("--tax-advantaged/--taxable-only", default=False)
@click.option("--limit", default=5, show_default=True, type=int)
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table", show_default=True)
def recommend_vehicles(
    months: int,
    risk_tolerance: str,
    liquidity_need: str,
    tax_advantaged: bool,
    limit: int,
    fmt: str,
) -> None:
    """Rank vehicle candidates for a horizon and constraint set."""

    try:
        candidates = SavingsGoalPlannerClient().recommend_vehicles(
            horizon_months=months,
            risk_tolerance=risk_tolerance,  # type: ignore[arg-type]
            liquidity_need=liquidity_need,  # type: ignore[arg-type]
            tax_advantaged_available=tax_advantaged,
        )[:limit]
    except SavingsGoalError as exc:
        raise click.ClickException(str(exc)) from exc
    if fmt == "json":
        click.echo(json.dumps(candidates, ensure_ascii=False, indent=2))
        return
    for item in candidates:
        click.echo(f"{item['key']} score={item['score']}: {item['english_name']} / {item['hebrew_name']}")
        for reason in item["reasons"]:
            click.echo(f"  - {reason}")
        click.echo(f"  caution: {item['caution']}")


if __name__ == "__main__":
    main()
