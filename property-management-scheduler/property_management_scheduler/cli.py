from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import PropertyManagementScheduler, SchedulerError, official_reference_values

app = typer.Typer(help="Coordinate Israeli property rent, maintenance, and tenant communication.")


def _client(store: Path, env: str) -> PropertyManagementScheduler:
    return PropertyManagementScheduler(store_path=store, environment=env)  # type: ignore[arg-type]


def _print(payload: object) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.callback()
def main() -> None:
    pass


@app.command("property-add")
def property_add(
    address: str = typer.Option(..., help="Street and number."),
    city: str = typer.Option(..., help="City."),
    apartment: str = typer.Option("", help="Apartment, floor, or unit."),
    store: Path = typer.Option(Path("property-management-scheduler.json"), help="JSON store path."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    client = _client(store, env)
    _print(client.create_property(address=address, city=city, apartment=apartment))


@app.command("tenant-add")
def tenant_add(
    property_id: str = typer.Option(...),
    full_name: str = typer.Option(...),
    phone: str = typer.Option(""),
    email: str = typer.Option(""),
    preferred_channel: str = typer.Option("email"),
    store: Path = typer.Option(Path("property-management-scheduler.json")),
    env: str = typer.Option("sandbox", "--env"),
) -> None:
    client = _client(store, env)
    _print(client.add_tenant(property_id, full_name, phone=phone, email=email, preferred_channel=preferred_channel))  # type: ignore[arg-type]


@app.command("lease-create")
def lease_create(
    property_id: str = typer.Option(...),
    tenant_id: str = typer.Option(...),
    start_date: str = typer.Option(..., help="DD/MM/YYYY"),
    end_date: str = typer.Option(..., help="DD/MM/YYYY"),
    monthly_rent_ils: str = typer.Option(...),
    due_day: int = typer.Option(1),
    store: Path = typer.Option(Path("property-management-scheduler.json")),
    env: str = typer.Option("sandbox", "--env"),
) -> None:
    client = _client(store, env)
    _print(client.create_lease(property_id, tenant_id, start_date, end_date, monthly_rent_ils, due_day=due_day))


@app.command("rent-generate")
def rent_generate(
    lease_id: str = typer.Option(...),
    from_date: str = typer.Option(..., help="DD/MM/YYYY"),
    months: int = typer.Option(12),
    store: Path = typer.Option(Path("property-management-scheduler.json")),
    env: str = typer.Option("sandbox", "--env"),
) -> None:
    client = _client(store, env)
    _print(client.schedule_rent(lease_id, from_date, months=months))


@app.command("maintenance-create")
def maintenance_create(
    property_id: str = typer.Option(...),
    title: str = typer.Option(...),
    description: str = typer.Option(...),
    severity: Optional[str] = typer.Option(None),
    due_date: Optional[str] = typer.Option(None),
    store: Path = typer.Option(Path("property-management-scheduler.json")),
    env: str = typer.Option("sandbox", "--env"),
) -> None:
    client = _client(store, env)
    _print(client.create_maintenance(property_id, title, description, severity=severity, due_date=due_date))  # type: ignore[arg-type]


@app.command("agenda")
def agenda(
    date_value: str = typer.Option(..., "--date", help="DD/MM/YYYY"),
    store: Path = typer.Option(Path("property-management-scheduler.json")),
    env: str = typer.Option("sandbox", "--env"),
) -> None:
    client = _client(store, env)
    _print(client.build_daily_agenda(date_value))


@app.command("reference-values")
def reference_values(
    as_of: Optional[str] = typer.Option(None, "--as-of", help="DD/MM/YYYY or ISO date."),
) -> None:
    _print(official_reference_values(as_of))


def run() -> None:
    try:
        app()
    except SchedulerError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc


if __name__ == "__main__":
    run()
