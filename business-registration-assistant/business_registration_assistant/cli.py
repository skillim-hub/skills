"""Command line interface for business registration preparation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import BusinessIntake, BusinessRegistrationClient, dump_json, load_intake


app = typer.Typer(help="Prepare Israeli עוסק פטור / עוסק מורשה registration checklists and plans.")


@app.command()
def classify(
    activity: str = typer.Option(..., help="Business activity description."),
    turnover: float = typer.Option(..., help="Expected annual turnover in ₪."),
    profit: Optional[float] = typer.Option(None, help="Expected monthly profit in ₪."),
    ceiling: Optional[float] = typer.Option(None, help="Current exempt dealer ceiling in ₪."),
    regulated_profession: bool = typer.Option(False, help="Flag regulated or professional activity."),
    clients_require_tax_invoice: bool = typer.Option(False, help="Flag clients requiring VAT tax invoices."),
    large_vat_bearing_expenses: bool = typer.Option(False, help="Flag significant VAT-bearing expenses."),
    foreign_clients: bool = typer.Option(False, help="Flag foreign clients."),
    online_sales: bool = typer.Option(False, help="Flag digital marketplace or platform sales."),
    import_export: bool = typer.Option(False, help="Flag import or export activity."),
    currently_employee: bool = typer.Option(False, help="Flag concurrent salaried employment."),
    receives_benefits: bool = typer.Option(False, help="Flag Bituach Leumi benefits or unemployment."),
) -> None:
    """Classify likely VAT status."""
    intake = BusinessIntake(
        activity_description=activity,
        expected_annual_turnover_nis=turnover,
        expected_monthly_profit_nis=profit,
        current_osek_patur_ceiling_nis=ceiling,
        regulated_profession=regulated_profession,
        clients_require_tax_invoice=clients_require_tax_invoice,
        large_vat_bearing_expenses=large_vat_bearing_expenses,
        foreign_clients=foreign_clients,
        online_sales=online_sales,
        import_export=import_export,
        currently_employee=currently_employee,
        receives_benefits=receives_benefits,
    )
    typer.echo(dump_json(BusinessRegistrationClient().classify_status(intake).to_dict()))


@app.command()
def checklist(
    status: str = typer.Option("needs_review", help="osek_patur, osek_murshe, or needs_review."),
    activity: str = typer.Option("General services", help="Business activity description."),
    turnover: float = typer.Option(0, help="Expected annual turnover in ₪."),
    work_location: str = typer.Option("home", help="home, rented_office, client_sites, online, etc."),
    regulated_profession: bool = typer.Option(False),
    foreign_clients: bool = typer.Option(False),
    online_sales: bool = typer.Option(False),
    import_export: bool = typer.Option(False),
    currently_employee: bool = typer.Option(False),
    receives_benefits: bool = typer.Option(False),
    prior_self_employment_file: bool = typer.Option(False),
    bank_ownership_confirmation: bool = typer.Option(True),
) -> None:
    """Build a document checklist."""
    intake = BusinessIntake(
        activity_description=activity,
        expected_annual_turnover_nis=turnover,
        work_location=work_location,
        regulated_profession=regulated_profession,
        foreign_clients=foreign_clients,
        online_sales=online_sales,
        import_export=import_export,
        currently_employee=currently_employee,
        receives_benefits=receives_benefits,
        prior_self_employment_file=prior_self_employment_file,
        bank_ownership_confirmation=bank_ownership_confirmation,
    )
    result = BusinessRegistrationClient().build_document_checklist(intake, status=status)  # type: ignore[arg-type]
    typer.echo(dump_json(result.to_dict()))


@app.command()
def plan(
    input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="JSON or YAML intake file."),
) -> None:
    """Generate a full plan from an intake file."""
    intake = load_intake(input)
    result = BusinessRegistrationClient().build_full_plan(intake)
    typer.echo(dump_json(result.to_dict()))


@app.command("case-create")
def case_create(
    input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="JSON or YAML intake file."),
    case_store: Path = typer.Option(Path(".business-registration-cases.json"), help="Local JSON case store."),
) -> None:
    """Create a local planning case and return its id."""
    intake = load_intake(input)
    result = BusinessRegistrationClient().create_case(intake, case_store)
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@app.command("case-plan")
def case_plan(
    case_id: str = typer.Option(..., help="Case id returned by case-create."),
    case_store: Path = typer.Option(Path(".business-registration-cases.json"), help="Local JSON case store."),
) -> None:
    """Generate a full plan for a stored case id."""
    result = BusinessRegistrationClient().build_plan_for_case(case_id, case_store)
    typer.echo(dump_json(result.to_dict()))


@app.command()
def migrate(
    ytd: float = typer.Option(..., help="Year-to-date turnover in ₪."),
    forecast: float = typer.Option(..., help="Forecast remaining turnover in ₪."),
    ceiling: float = typer.Option(..., help="Current exempt dealer ceiling in ₪."),
) -> None:
    """Build a migration checklist from עוסק פטור to עוסק מורשה."""
    result = BusinessRegistrationClient().migration_checklist(
        year_to_date_turnover_nis=ytd,
        forecast_remaining_turnover_nis=forecast,
        current_osek_patur_ceiling_nis=ceiling,
    )
    typer.echo(dump_json(result))


@app.command()
def handoff(
    input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="JSON or YAML intake file."),
) -> None:
    """Generate accountant handoff JSON."""
    intake = load_intake(input)
    result = BusinessRegistrationClient().accountant_handoff(intake)
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
