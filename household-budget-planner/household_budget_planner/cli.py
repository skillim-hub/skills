"""Command-line interface for household budget planning."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, Optional

import typer

from .client import (
    BudgetValidationError,
    HouseholdBudgetPlannerClient,
    create_budget,
    create_sample_plan,
    ensure_budget_id,
    format_shekel,
)

Environment = Literal["sandbox", "production"]

app = typer.Typer(help="Track Israeli household budgets, savings goals, VAT-aware expenses, and monthly summaries.")


@app.command()
def create(
    month: str = typer.Option(..., "--month", "-m", help="Budget month, such as 05-2026."),
    output: Path = typer.Option(Path("budget.json"), "--output", "-o", help="Path for the new budget JSON file."),
    env: Environment = typer.Option("sandbox", "--env", help="Execution environment label."),
    json_output: bool = typer.Option(True, "--json/--text", help="Print JSON response by default."),
) -> None:
    """Create an empty budget file and return a budget identifier."""
    response = create_budget(month, output, environment=env)
    if json_output:
        typer.echo(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Created budget {response['budget_id']} at {response['path']}")


@app.command()
def sample(
    output: Path = typer.Option(Path("sample-budget.json"), "--output", "-o", help="Path for generated sample JSON."),
    env: Environment = typer.Option("sandbox", "--env", help="Execution environment label."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable response."),
) -> None:
    """Create a sample Israeli household budget JSON file."""
    client = create_sample_plan(environment=env)
    client.to_json(output)
    response = {"budget_id": client.plan.budget_id, "path": str(output), "environment": env}
    if json_output:
        typer.echo(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Created sample budget {client.plan.budget_id} at {output}")


@app.command()
def summary(
    budget_file: Path = typer.Argument(..., help="Budget JSON file."),
    month: Optional[str] = typer.Option(None, "--month", "-m", help="Month in MM-YYYY."),
    budget_id: Optional[str] = typer.Option(None, "--budget-id", help="Expected budget identifier."),
    vat_rate: float = typer.Option(0.18, "--vat-rate", help="VAT rate for VAT-inclusive expenses."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    """Print a monthly budget summary."""
    client = HouseholdBudgetPlannerClient.from_json(budget_file)
    ensure_budget_id(client, budget_id)
    client.vat_rate = vat_rate
    result = client.summary(month=month)
    if json_output:
        typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        typer.echo(client.render_text_summary(month=month))


@app.command()
def add(
    budget_file: Path = typer.Argument(..., help="Budget JSON file to update."),
    budget_id: Optional[str] = typer.Option(None, "--budget-id", help="Expected budget identifier."),
    date: str = typer.Option(..., "--date", help="Transaction date DD-MM-YYYY or DD/MM/YYYY."),
    amount: float = typer.Option(..., "--amount", help="Amount in ₪."),
    kind: str = typer.Option(..., "--kind", help="income, expense, or transfer."),
    category: str = typer.Option(..., "--category", help="Budget category."),
    description: str = typer.Option("", "--description", help="Description or memo."),
    vendor: str = typer.Option("", "--vendor", help="Merchant or payer."),
    business: bool = typer.Option(False, "--business", help="Mark as business-related."),
    vat_included: bool = typer.Option(False, "--vat-included", help="Mark amount as VAT-inclusive."),
) -> None:
    """Add one transaction to a budget file."""
    client = HouseholdBudgetPlannerClient.from_json(budget_file)
    ensure_budget_id(client, budget_id)
    client.add_transaction(
        date=date,
        amount=amount,
        kind=kind,  # type: ignore[arg-type]
        category=category,
        description=description,
        vendor=vendor,
        is_business=business,
        vat_included=vat_included,
    )
    client.to_json(budget_file)
    typer.echo(f"Added {kind} {format_shekel(amount)} to {budget_file}")


@app.command()
def goal(
    budget_file: Path = typer.Argument(..., help="Budget JSON file to update."),
    budget_id: Optional[str] = typer.Option(None, "--budget-id", help="Expected budget identifier."),
    name: str = typer.Option(..., "--name", help="Goal name."),
    target: float = typer.Option(..., "--target", help="Target amount in ₪."),
    current: float = typer.Option(0.0, "--current", help="Current saved amount in ₪."),
    due: str = typer.Option(..., "--due", help="Due date DD-MM-YYYY or DD/MM/YYYY."),
) -> None:
    """Add a savings goal to a budget file."""
    client = HouseholdBudgetPlannerClient.from_json(budget_file)
    ensure_budget_id(client, budget_id)
    client.add_savings_goal(name=name, target_amount=target, current_amount=current, due_date=due)
    client.to_json(budget_file)
    typer.echo(f"Added goal {name}")


@app.command("import-csv")
def import_csv(
    budget_file: Path = typer.Argument(..., help="Budget JSON file to update."),
    csv_file: Path = typer.Argument(..., help="CSV file with normalized transaction columns."),
    budget_id: Optional[str] = typer.Option(None, "--budget-id", help="Expected budget identifier."),
) -> None:
    """Import transactions from CSV into a budget JSON file."""
    client = HouseholdBudgetPlannerClient.from_json(budget_file)
    ensure_budget_id(client, budget_id)
    count = client.load_csv(csv_file)
    client.to_json(budget_file)
    typer.echo(f"Imported {count} transactions")


@app.command()
def validate(
    budget_file: Path = typer.Argument(..., help="Budget JSON file."),
    budget_id: Optional[str] = typer.Option(None, "--budget-id", help="Expected budget identifier."),
) -> None:
    """Validate a budget file and print warnings."""
    client = HouseholdBudgetPlannerClient.from_json(budget_file)
    ensure_budget_id(client, budget_id)
    warnings = client.validate()
    if not warnings:
        typer.echo("No validation warnings.")
        return
    for warning in warnings:
        typer.echo(f"- {warning}")


@app.command("export-csv")
def export_csv(
    budget_file: Path = typer.Argument(..., help="Budget JSON file."),
    output: Path = typer.Option(Path("transactions.csv"), "--output", "-o", help="Output CSV path."),
    budget_id: Optional[str] = typer.Option(None, "--budget-id", help="Expected budget identifier."),
) -> None:
    """Export transactions to normalized CSV."""
    client = HouseholdBudgetPlannerClient.from_json(budget_file)
    ensure_budget_id(client, budget_id)
    client.export_csv(output)
    typer.echo(f"Exported {output}")


def main() -> None:
    try:
        app()
    except BudgetValidationError as exc:
        raise typer.BadParameter(str(exc)) from exc


if __name__ == "__main__":
    main()
