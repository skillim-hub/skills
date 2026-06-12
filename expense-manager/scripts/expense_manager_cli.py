#!/usr/bin/env python3
"""Typer CLI for Israeli expense classification and accountant package export."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

try:  # Works when installed as the scripts package.
    from . import expense_manager_client as client
except ImportError:  # Works when executed directly from the scripts directory.
    import expense_manager_client as client  # type: ignore[no-redef]

app = typer.Typer(help="Classify Israeli expenses and build accountant-ready export packages.")


def _env_default(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def _config(entity_type: str, home_office_percent: str, strict: bool) -> client.BusinessConfig:
    return client.BusinessConfig(
        entity_type=client.EntityType(entity_type),
        home_office_percent=client.parse_decimal(home_office_percent),
        strict=strict,
    )


@app.command()
def classify(
    input_csv: Path = typer.Argument(..., exists=True, dir_okay=False, help="CSV with date, vendor, amount, and description columns."),
    output_csv: Path = typer.Argument(..., help="Destination CSV for classified rows."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production; production only changes validation posture."),
    entity_type: str = typer.Option(_env_default("EXPENSE_MANAGER_ENTITY_TYPE", "osek_murshe"), help="osek_patur, osek_murshe, company, or private_consumer."),
    home_office_percent: str = typer.Option(_env_default("EXPENSE_MANAGER_HOME_OFFICE_PERCENT", "0"), help="Dedicated home-office percentage, for example 12.5."),
    strict: bool = typer.Option(False, help="Add strict blocker flags when warnings remain."),
) -> None:
    """Classify a CSV and write a result CSV."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    config = _config(entity_type, home_office_percent, strict or env == "production")
    results = client.classify_csv_file(input_csv, output_csv, config)
    payload = {"env": env, "output_csv": str(output_csv), "summary": client.summarize_results(results)}
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command()
def package(
    input_csv: Path = typer.Argument(..., exists=True, dir_okay=False, help="CSV with source expenses."),
    output_dir: Path = typer.Argument(..., help="Directory for package files and ZIP."),
    package_name: str = typer.Option(_env_default("EXPENSE_MANAGER_PACKAGE_NAME", "accountant-expense-package"), help="ZIP/package folder base name."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production; production enables strict review flags."),
    entity_type: str = typer.Option(_env_default("EXPENSE_MANAGER_ENTITY_TYPE", "osek_murshe"), help="osek_patur, osek_murshe, company, or private_consumer."),
    home_office_percent: str = typer.Option(_env_default("EXPENSE_MANAGER_HOME_OFFICE_PERCENT", "0"), help="Dedicated home-office percentage."),
    strict: bool = typer.Option(False, help="Add strict blocker flags when warnings remain."),
) -> None:
    """Classify a CSV and create an accountant package ZIP."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    config = _config(entity_type, home_office_percent, strict or env == "production")
    expenses = client.read_expenses_csv(input_csv)
    results = client.classify_many(expenses, config)
    zip_path = client.export_accountant_package(results, output_dir, package_name, source_files=[input_csv])
    payload = {"env": env, "package_zip": str(zip_path), "summary": client.summarize_results(results)}
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("single")
def single_expense(
    vendor: str = typer.Option(..., help="Vendor name."),
    amount: str = typer.Option(..., help="Gross amount, for example 117.00."),
    expense_date: str = typer.Option(..., "--date", help="DD/MM/YYYY, DD-MM-YYYY, or ISO date."),
    description: str = typer.Option("", help="Optional details."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    entity_type: str = typer.Option(_env_default("EXPENSE_MANAGER_ENTITY_TYPE", "osek_murshe"), help="Entity type."),
) -> None:
    """Classify one expense and print JSON."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    expense = client.ExpenseInput(
        date=client.parse_date(expense_date),
        vendor=vendor,
        amount=client.parse_decimal(amount),
        description=description,
    )
    result = client.classify_expense(expense, client.BusinessConfig(entity_type=client.EntityType(entity_type), strict=env == "production"))
    payload = {"env": env, "expense_id": client.make_expense_id(expense), "classification": result.to_flat_dict()}
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("create")
def create_expense(
    vendor: str = typer.Option(..., help="Vendor name."),
    amount: str = typer.Option(..., help="Gross amount."),
    expense_date: str = typer.Option(..., "--date", help="DD/MM/YYYY, DD-MM-YYYY, or ISO date."),
    description: str = typer.Option("", help="Optional details."),
    receipt_number: Optional[str] = typer.Option(None, help="Receipt or tax invoice number."),
    document_type: Optional[str] = typer.Option(None, help="Document type, for example tax invoice."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    output: Optional[Path] = typer.Option(None, "--output", help="Optional path for the created JSON record."),
) -> None:
    """Create a normalized expense JSON record and return its id."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    expense = client.ExpenseInput(
        date=client.parse_date(expense_date),
        vendor=vendor,
        amount=client.parse_decimal(amount),
        description=description,
        receipt_number=receipt_number,
        document_type=document_type,
    )
    record = client.create_expense_record(expense, output)
    response = {"env": env, "id": record["id"], "record": record, "record_path": str(output) if output else ""}
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


@app.command("classify-created")
def classify_created(
    record_json: Path = typer.Argument(..., exists=True, dir_okay=False, help="JSON produced by the create command."),
    expense_id: str = typer.Option(..., "--id", help="Expense id returned by create."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    entity_type: str = typer.Option(_env_default("EXPENSE_MANAGER_ENTITY_TYPE", "osek_murshe"), help="Entity type."),
    home_office_percent: str = typer.Option(_env_default("EXPENSE_MANAGER_HOME_OFFICE_PERCENT", "0"), help="Dedicated home-office percentage."),
) -> None:
    """Classify a previously created expense record by id."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    data = json.loads(record_json.read_text(encoding="utf-8"))
    config = _config(entity_type, home_office_percent, env == "production")
    result = client.classify_expense_record(data, expected_id=expense_id, config=config)
    payload = {"env": env, "expense_id": expense_id, "classification": result.to_flat_dict()}
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
