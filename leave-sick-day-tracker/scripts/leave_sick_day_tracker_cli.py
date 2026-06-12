#!/usr/bin/env python3
"""Command-line helper for Israeli leave and sick-day tracking."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click

from leave_sick_day_tracker.client import (
    EmployeeProfile,
    LeaveEvent,
    LeaveTrackerClient,
    annual_accrual_between,
    annual_entitlement_days,
    sick_pay_equivalent_days,
    write_template_csvs,
)


def _echo_json(payload: object) -> None:
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Track Israeli annual leave, sick days, miluim, birth and parenthood leave, and mourning days."""


@cli.command("template")
@click.argument("directory", type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
def template(directory: Path) -> None:
    """Create starter employees.csv and events.csv files."""
    employees_path, events_path = write_template_csvs(directory)
    _echo_json({"employees_csv": str(employees_path), "events_csv": str(events_path)})


@cli.command("create-employee")
@click.option("--employee-id", required=True, help="Stable employee identifier used in events.")
@click.option("--name", required=True, help="Employee display name.")
@click.option("--hire-date", required=True, help="Hire date, DD/MM/YYYY or YYYY-MM-DD.")
@click.option("--work-week-days", default="5", type=click.Choice(["5", "6"]), help="Israeli work week: 5 or 6 days.")
@click.option("--opening-annual-balance", default=0.0, type=float, help="Opening annual leave balance.")
@click.option("--opening-sick-balance", default=0.0, type=float, help="Opening sick-day balance.")
def create_employee(employee_id: str, name: str, hire_date: str, work_week_days: str, opening_annual_balance: float, opening_sick_balance: float) -> None:
    """Validate and print one employee JSON object for scripts or CSV conversion."""
    employee = EmployeeProfile(
        employee_id=employee_id,
        name=name,
        hire_date=hire_date,
        work_week_days=int(work_week_days),
        opening_annual_balance=opening_annual_balance,
        opening_sick_balance=opening_sick_balance,
    )
    _echo_json({"employee": employee.to_dict()})


@cli.command("add-event")
@click.option("--employee-id", required=True, help="Employee identifier from create-employee or employees.csv.")
@click.option("--absence-type", required=True, type=click.Choice(["annual", "sick", "miluim", "parental", "mourning"]), help="Absence category.")
@click.option("--start-date", required=True, help="Start date, DD/MM/YYYY or YYYY-MM-DD.")
@click.option("--end-date", required=True, help="End date, DD/MM/YYYY or YYYY-MM-DD.")
@click.option("--days", default=None, type=float, help="Override day count. Omit to calculate from the work week in summary workflows.")
@click.option("--approved/--not-approved", default=True, help="Whether the event is approved for balance calculations.")
@click.option("--reference", default="", help="Approval, certificate, or payroll reference.")
def add_event(employee_id: str, absence_type: str, start_date: str, end_date: str, days: Optional[float], approved: bool, reference: str) -> None:
    """Validate and print one event JSON object for scripts or CSV conversion."""
    event = LeaveEvent(employee_id, absence_type, start_date, end_date, days=days, approved=approved, reference=reference)
    _echo_json({"event": event.to_dict()})


@cli.command("entitlement")
@click.option("--hire-date", required=True, help="Hire date, DD/MM/YYYY or YYYY-MM-DD.")
@click.option("--as-of", required=True, help="Calculation date, DD/MM/YYYY or YYYY-MM-DD.")
@click.option("--work-week-days", default="5", type=click.Choice(["5", "6"]), help="Israeli work week: 5 or 6 days.")
@click.option("--override-days", type=float, default=None, help="Contractual annual entitlement override.")
def entitlement(hire_date: str, as_of: str, work_week_days: str, override_days: Optional[float]) -> None:
    """Print annual entitlement and accrued annual leave."""
    entitlement_days = annual_entitlement_days(hire_date, as_of, int(work_week_days), override_days)
    accrued = annual_accrual_between(hire_date, as_of, int(work_week_days), override_days)
    _echo_json({"entitlement_days": entitlement_days, "accrued_days": accrued})


@cli.command("sick-pay")
@click.option("--days", required=True, type=float, help="Continuous sick absence days.")
def sick_pay(days: float) -> None:
    """Print statutory paid-day equivalent for a continuous sick event."""
    _echo_json({"sick_days": days, "paid_equivalent_days": sick_pay_equivalent_days(days)})


@cli.command("summary")
@click.argument("employees_csv", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("events_csv", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--as-of", required=True, help="Calculation date, DD/MM/YYYY or YYYY-MM-DD.")
@click.option("--output", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Optional CSV output path.")
def summary(employees_csv: Path, events_csv: Path, as_of: str, output: Optional[Path]) -> None:
    """Calculate balances for all employees from CSV files."""
    tracker = LeaveTrackerClient.from_csv(employees_csv, events_csv)
    rows = [snapshot.to_dict() for snapshot in tracker.balances(as_of)]
    if output:
        tracker.export_balances_csv(output, as_of)
    _echo_json({"rows": rows, "output_csv": str(output) if output else None})


@cli.command("validate-data")
@click.argument("employees_csv", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("events_csv", required=False, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--as-of", default=None, help="Optional balance date to validate negative balances.")
def validate_data(employees_csv: Path, events_csv: Optional[Path], as_of: Optional[str]) -> None:
    """Validate CSV shape, employee references, dates, and optional balances."""
    tracker = LeaveTrackerClient.from_csv(employees_csv, events_csv)
    result = {"employees": len(tracker.employees), "events": len(tracker.events), "errors": [], "warnings": []}
    if as_of:
        for snapshot in tracker.balances(as_of):
            result["warnings"].extend(f"{snapshot.employee_id}: {warning}" for warning in snapshot.warnings)
    _echo_json(result)
    if result["errors"]:
        raise click.ClickException("Validation failed")


@cli.command("scenario")
def scenario() -> None:
    """Run a small built-in scenario and print the resulting balance."""
    employee = EmployeeProfile(employee_id="E001", name="Dana Levi", hire_date="01/01/2024", work_week_days=5)
    tracker = LeaveTrackerClient([employee])
    tracker.record_event(LeaveEvent("E001", "annual", "18/08/2024", "22/08/2024"))
    tracker.record_event(LeaveEvent("E001", "sick", "01/09/2024", "03/09/2024"))
    snapshot = tracker.balance("E001", "31/12/2024")
    _echo_json(snapshot.to_dict())


if __name__ == "__main__":
    cli()
