"""Command-line interface for the Benefit & Perk Planner."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer

from benefit_perk_planner_client import (
    AsyncBenefitPlannerClient,
    BenefitPlannerClient,
    BenefitRequest,
    Environment,
    PlannerError,
    load_request,
    save_plan,
)

app = typer.Typer(help="Plan Israeli benefit and perk packages for employers, freelancers, consumers, and employees.")


def _client(env: str) -> BenefitPlannerClient:
    return BenefitPlannerClient(environment=env)  # type: ignore[arg-type]


@app.command()
def plan(
    entity_type: str = typer.Option(..., "--entity", "-e", help="employer, freelancer, consumer, or employee"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    budget: Optional[float] = typer.Option(None, "--budget", "-b", help="Monthly budget in ILS"),
    employees: Optional[int] = typer.Option(None, "--employees", help="Employee count"),
    gross_salary: Optional[float] = typer.Option(None, "--gross-salary", help="Gross salary in ILS"),
    monthly_income: Optional[float] = typer.Option(None, "--income", help="Monthly income in ILS"),
    goal: list[str] = typer.Option([], "--goal", help="retention, equity, cost_control, tax_efficiency, wellbeing, simplicity"),
    work_model: str = typer.Option("unspecified", "--work-model", help="onsite, hybrid, remote, shifts, or custom text"),
    location: str = typer.Option("Israel", "--location", help="Location"),
    existing_benefit: list[str] = typer.Option([], "--existing-benefit", help="Existing benefit label"),
    cash_buffer_months: Optional[float] = typer.Option(None, "--cash-buffer-months", help="Freelancer reserve in months"),
    includes_contractors: bool = typer.Option(False, "--includes-contractors", help="Flag contractor inclusion risk"),
    wants_keren_hishtalmut: bool = typer.Option(False, "--keren-hishtalmut", help="Include study fund review"),
    no_meals: bool = typer.Option(False, "--no-meals", help="Exclude meal benefit"),
    no_wellness: bool = typer.Option(False, "--no-wellness", help="Exclude wellness benefit"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    fmt: str = typer.Option("md", "--format", help="md or json"),
) -> None:
    """Create a benefit plan from CLI options."""
    try:
        request = BenefitRequest(
            entity_type=entity_type,  # type: ignore[arg-type]
            monthly_budget_ils=budget,
            employee_count=employees,
            gross_salary_ils=gross_salary,
            monthly_income_ils=monthly_income,
            goals=goal,  # type: ignore[arg-type]
            work_model=work_model,
            location=location,
            existing_benefits=existing_benefit,
            cash_buffer_months=cash_buffer_months,
            includes_contractors=includes_contractors,
            wants_keren_hishtalmut=wants_keren_hishtalmut,
            wants_meal_benefit=not no_meals,
            wants_wellness=not no_wellness,
        )
        benefit_plan = _client(env).plan(request)
    except PlannerError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(2) from exc

    if output:
        save_plan(benefit_plan, output, fmt="json" if fmt == "json" else "md")
        typer.echo(str(output))
    elif fmt == "json":
        typer.echo(json.dumps(benefit_plan.to_dict(), ensure_ascii=False, indent=2))
    else:
        typer.echo(benefit_plan.to_markdown())


@app.command()
def create(
    entity_type: str = typer.Option(..., "--entity", "-e", help="employer, freelancer, consumer, or employee"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    budget: Optional[float] = typer.Option(None, "--budget", "-b", help="Monthly budget in ILS"),
    employees: Optional[int] = typer.Option(None, "--employees", help="Employee count"),
    store_dir: Path = typer.Option(Path(".benefit-perk-planner"), "--store-dir", help="Directory for saved plans"),
) -> None:
    """Create and persist a plan, returning a JSON object with plan_id."""
    try:
        response = _client(env).create_plan(
            BenefitRequest(entity_type=entity_type, monthly_budget_ils=budget, employee_count=employees),  # type: ignore[arg-type]
            store_dir=store_dir,
        )
    except PlannerError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


@app.command()
def show(
    plan_id: str = typer.Option(..., "--plan-id", help="Plan identifier returned by create"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    store_dir: Path = typer.Option(Path(".benefit-perk-planner"), "--store-dir", help="Directory for saved plans"),
) -> None:
    """Show a stored plan by plan_id."""
    try:
        data = _client(env).get_plan(plan_id, store_dir=store_dir)
    except PlannerError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


@app.command("from-file")
def from_file(
    input_path: Path = typer.Argument(..., help="JSON request file"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    fmt: str = typer.Option("md", "--format", help="md or json"),
) -> None:
    """Create a benefit plan from a JSON request file."""
    try:
        request = load_request(input_path)
        benefit_plan = _client(env).plan(request)
    except (PlannerError, OSError, ValueError, TypeError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(2) from exc

    if output:
        save_plan(benefit_plan, output, fmt="json" if fmt == "json" else "md")
        typer.echo(str(output))
    elif fmt == "json":
        typer.echo(json.dumps(benefit_plan.to_dict(), ensure_ascii=False, indent=2))
    else:
        typer.echo(benefit_plan.to_markdown())


@app.command("compare-salary-benefit")
def compare_salary_benefit(
    gross_salary_offer: float = typer.Option(..., "--salary", help="Gross salary alternative in ILS"),
    benefit_value: float = typer.Option(..., "--benefit", help="Headline benefit value in ILS"),
    utilization: float = typer.Option(0.75, "--utilization", min=0.0, max=1.0, help="Expected utilization ratio"),
) -> None:
    """Compare a gross salary alternative with expected usable benefit value."""
    usable = benefit_value * utilization
    typer.echo(
        json.dumps(
            {
                "gross_salary_offer_ils": gross_salary_offer,
                "benefit_headline_value_ils": benefit_value,
                "expected_utilization": utilization,
                "expected_usable_benefit_ils": round(usable, 2),
                "decision_note": "Compare expected usable benefit to net salary after payroll withholding.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@app.command("async-plan")
def async_plan(
    entity_type: str = typer.Option(..., "--entity", "-e"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    budget: Optional[float] = typer.Option(None, "--budget", "-b"),
    employees: Optional[int] = typer.Option(None, "--employees"),
) -> None:
    """Run the async planner wrapper."""

    async def _run() -> None:
        request = BenefitRequest(entity_type=entity_type, monthly_budget_ils=budget, employee_count=employees)  # type: ignore[arg-type]
        benefit_plan = await AsyncBenefitPlannerClient(_client(env)).plan(request)
        typer.echo(benefit_plan.to_markdown())

    asyncio.run(_run())


if __name__ == "__main__":
    app()
