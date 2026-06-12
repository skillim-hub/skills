"""Typer command line interface for the loan amortization planner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import (
    LoanScenario,
    build_schedule,
    compare_scenarios,
    create_scenario_record,
    load_scenarios,
    resolve_scenario,
)

app = typer.Typer(help="Plan Israeli fixed, prime-linked, and CPI-linked loan schedules.")


@app.command("create-scenario")
def create_scenario(
    principal: str = typer.Option(..., "--principal", help="Principal in NIS."),
    term_months: int = typer.Option(..., "--term-months", help="Term in months."),
    start_date: str = typer.Option(..., "--start-date", help="Start date, preferably DD/MM/YYYY."),
    name: str = typer.Option("loan", "--name", help="Scenario name."),
    rate_type: str = typer.Option("fixed", "--rate-type", help="fixed, prime, or cpi."),
    annual_interest_rate: str = typer.Option("0.06", "--annual-interest-rate", help="Annual rate as decimal."),
    prime_rate: Optional[str] = typer.Option(None, "--prime-rate", help="Prime base rate as decimal."),
    prime_margin: str = typer.Option("0", "--prime-margin", help="Prime margin as decimal."),
    annual_cpi_rate: str = typer.Option("0", "--annual-cpi-rate", help="Annual CPI assumption as decimal."),
    payment_frequency: str = typer.Option("monthly", "--payment-frequency", help="monthly or quarterly."),
    grace_months: int = typer.Option(0, "--grace-months", help="Interest-only grace months."),
    balloon_percent: str = typer.Option("0", "--balloon-percent", help="Final balloon as principal percent decimal."),
    origination_fee: str = typer.Option("0", "--origination-fee", help="Origination fee in NIS."),
    early_payment_fee: str = typer.Option("0", "--early-payment-fee", help="Early repayment fee in NIS."),
    registry: Optional[Path] = typer.Option(None, "--registry", help="Scenario registry path."),
) -> None:
    """Create and store a scenario, then print its local identifier."""
    data = {
        "name": name,
        "principal": principal,
        "term_months": term_months,
        "start_date": start_date,
        "rate_type": rate_type,
        "annual_interest_rate": annual_interest_rate,
        "prime_rate": prime_rate,
        "prime_margin": prime_margin,
        "annual_cpi_rate": annual_cpi_rate,
        "payment_frequency": payment_frequency,
        "grace_months": grace_months,
        "balloon_percent": balloon_percent,
        "origination_fee": origination_fee,
        "early_payment_fee": early_payment_fee,
    }
    record = create_scenario_record(data, registry)
    typer.echo(json.dumps(record, ensure_ascii=False, indent=2))


@app.command()
def schedule(
    scenario: str = typer.Argument(..., help="JSON scenario path or registry id from create-scenario."),
    json_out: Optional[Path] = typer.Option(None, "--json-out", help="Write full schedule JSON."),
    csv_out: Optional[Path] = typer.Option(None, "--csv-out", help="Write full schedule CSV."),
    rows: int = typer.Option(6, "--rows", min=0, help="Preview rows to print."),
    registry: Optional[Path] = typer.Option(None, "--registry", help="Scenario registry path."),
) -> None:
    """Build one repayment schedule."""
    loan = resolve_scenario(scenario, registry)
    result = build_schedule(loan)
    if json_out:
        result.to_json(json_out)
    if csv_out:
        result.to_csv(csv_out)
    typer.echo(json.dumps(result.summary.as_dict(), ensure_ascii=False, indent=2))
    for row in result.rows[:rows]:
        typer.echo(json.dumps(row.as_dict(), ensure_ascii=False))


@app.command()
def compare(
    scenarios: Path = typer.Argument(..., exists=True, readable=True, help="JSON file containing a scenario list."),
) -> None:
    """Compare multiple scenarios by effective cash cost."""
    loans = load_scenarios(scenarios)
    typer.echo(json.dumps(compare_scenarios(loans), ensure_ascii=False, indent=2))


@app.command()
def validate(
    scenario: str = typer.Argument(..., help="JSON scenario path or registry id."),
    registry: Optional[Path] = typer.Option(None, "--registry", help="Scenario registry path."),
) -> None:
    """Validate a scenario without writing a schedule."""
    loan = resolve_scenario(scenario, registry)
    loan.validate()
    typer.echo(json.dumps({"valid": True, "name": loan.name}, ensure_ascii=False, indent=2))


def main() -> None:
    """Console entry point."""
    app()


if __name__ == "__main__":
    main()
