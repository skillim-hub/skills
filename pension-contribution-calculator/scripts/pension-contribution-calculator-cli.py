#!/usr/bin/env python3
"""Command-line interface for the pension contribution calculator."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import typer

import pension_contribution_calculator_client as pcc

app = typer.Typer(add_completion=False, help="Calculate Israeli pension, training fund, and manager's insurance deposits.")


def _validate_env(environment: str) -> str:
    if environment not in {"sandbox", "production"}:
        raise typer.BadParameter("environment must be sandbox or production")
    return environment


def _print_result(result, json_output: bool, *, record: bool = False, kind: str = "employee", environment: str = "sandbox") -> None:
    environment = _validate_env(environment)
    payload = pcc.create_calculation_record(kind, result, environment=environment, source="cli") if record else result
    if json_output:
        typer.echo(json.dumps(pcc.to_plain_dict(payload), ensure_ascii=False, indent=2, sort_keys=True))
        return
    data = pcc.to_plain_dict(payload)
    for key, value in data.items():
        if isinstance(value, float):
            typer.echo(f"{key}: {pcc.format_ils(value)}")
        elif isinstance(value, dict):
            typer.echo(f"{key}:")
            for inner_key, inner_value in value.items():
                if isinstance(inner_value, float):
                    typer.echo(f"  {inner_key}: {pcc.format_ils(inner_value)}")
                else:
                    typer.echo(f"  {inner_key}: {inner_value}")
        else:
            typer.echo(f"{key}: {value}")


@app.command("employee")
def employee(
    gross_salary: float = typer.Option(..., min=0, help="Gross monthly salary in ILS."),
    pensionable_salary: Optional[float] = typer.Option(None, min=0, help="Pensionable monthly salary in ILS."),
    product: str = typer.Option("pension_fund", help="pension_fund or bituach_menahalim."),
    hishtalmut: bool = typer.Option(False, "--hishtalmut", help="Include Keren Hishtalmut split."),
    section14: bool = typer.Option(False, "--section14", help="Use 8.33% severance deposit."),
    environment: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    record: bool = typer.Option(False, "--record", help="Wrap JSON output as a calculation record with an id."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON."),
) -> None:
    """Calculate employee payroll deposits."""
    result = pcc.employee_contributions(
        gross_salary,
        pensionable_salary=pensionable_salary,
        product=product,
        include_hishtalmut=hishtalmut,
        section14_full=section14,
    )
    _print_result(result, json_output, record=record, kind="employee", environment=environment)


@app.command("self-employed")
def self_employed(
    annual_income: float = typer.Option(..., min=0, help="Annual net taxable income after expenses."),
    age: int = typer.Option(..., min=0, max=130, help="Age at tax year end."),
    first_year: bool = typer.Option(False, "--first-year", help="Mark first business year as exempt."),
    pension_deposit: Optional[float] = typer.Option(None, min=0, help="Actual annual pension deposit."),
    hishtalmut_deposit: Optional[float] = typer.Option(None, min=0, help="Actual annual training fund deposit."),
    retirement_age: Optional[int] = typer.Option(None, min=0, max=130, help="Retirement age used for exemption check."),
    environment: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    record: bool = typer.Option(False, "--record", help="Wrap JSON output as a calculation record with an id."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON."),
) -> None:
    """Calculate self-employed pension obligation and tax-benefit ceilings."""
    result = pcc.self_employed_contributions(
        annual_income,
        age=age,
        first_year_business=first_year,
        retirement_age=retirement_age,
        annual_pension_deposit=pension_deposit,
        annual_hishtalmut_deposit=hishtalmut_deposit,
    )
    _print_result(result, json_output, record=record, kind="self_employed", environment=environment)


@app.command("compare")
def compare(
    gross_salary: float = typer.Option(..., min=0, help="Gross monthly salary in ILS."),
    pensionable_salary: Optional[float] = typer.Option(None, min=0, help="Pensionable monthly salary in ILS."),
    hishtalmut: bool = typer.Option(False, "--hishtalmut", help="Include Keren Hishtalmut split."),
    section14: bool = typer.Option(False, "--section14", help="Use 8.33% severance deposit."),
    environment: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    record: bool = typer.Option(False, "--record", help="Wrap JSON output as a calculation record with an id."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON."),
) -> None:
    """Compare pension fund routing against manager's insurance routing."""
    result = pcc.compare_products(
        gross_salary,
        pensionable_salary=pensionable_salary,
        include_hishtalmut=hishtalmut,
        section14_full=section14,
    )
    _print_result(result, json_output, record=record, kind="compare", environment=environment)


@app.command("rates")
def rates(
    environment: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    record: bool = typer.Option(False, "--record", help="Wrap JSON output as a calculation record with an id."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON."),
) -> None:
    """Print active rate table."""
    _print_result(pcc.DEFAULT_RATES, json_output, record=record, kind="rates", environment=environment)


@app.command("explain")
def explain(
    from_json: Path = typer.Option(..., "--from-json", exists=True, readable=True, help="JSON record produced by --record."),
    calculation_id: str = typer.Option(..., "--id", help="Record id to verify before printing."),
) -> None:
    """Verify a saved calculation record id and print a compact summary."""
    record = json.loads(from_json.read_text(encoding="utf-8"))
    if record.get("id") != calculation_id:
        raise typer.BadParameter("record id does not match the supplied --id value")
    kind = record.get("kind", "unknown")
    result = record.get("result", {})
    tax_year = result.get("tax_year", "unknown")
    typer.echo(json.dumps({"id": calculation_id, "kind": kind, "tax_year": tax_year, "status": "verified"}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    app()
