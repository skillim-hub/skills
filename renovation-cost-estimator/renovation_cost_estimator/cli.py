"""Command-line interface for the renovation cost estimator."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from .client import EstimatorError, ProjectInput, RenovationCostEstimatorClient

app = typer.Typer(help="Estimate Israeli renovation costs using local planning benchmarks.")


def _client(vat_rate: float = 0.18) -> RenovationCostEstimatorClient:
    return RenovationCostEstimatorClient(default_vat_rate=vat_rate)


@app.command()
def create(
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    project_name: str = typer.Option("Renovation project"),
    city: str = typer.Option("", envvar="RENOVATION_CITY"),
    property_type: str = typer.Option("apartment", envvar="RENOVATION_PROPERTY_TYPE"),
    area_sqm: float = typer.Option(0.0, envvar="RENOVATION_AREA_SQM"),
    scope_level: str = typer.Option("partial", envvar="RENOVATION_SCOPE_LEVEL"),
    finish_level: str = typer.Option("standard", envvar="RENOVATION_FINISH_LEVEL"),
    bathrooms: int = typer.Option(0, envvar="RENOVATION_BATHROOMS"),
    kitchens: int = typer.Option(0, envvar="RENOVATION_KITCHENS"),
    include_vat: bool = typer.Option(True, envvar="RENOVATION_INCLUDE_VAT"),
    vat_rate: float = typer.Option(0.18, envvar="RENOVATION_VAT_RATE"),
) -> None:
    """Create a stored project and print its id."""
    try:
        project = ProjectInput(
            project_name=project_name,
            city=city,
            property_type=property_type,
            area_sqm=area_sqm,
            scope_level=scope_level,
            finish_level=finish_level,
            bathrooms=bathrooms,
            kitchens=kitchens,
            include_vat=include_vat,
            vat_rate=vat_rate,
        )
        record = _client(vat_rate).create_project(project, environment=env)
        typer.echo(json.dumps({"id": record.id, "environment": record.environment, "path": record.path}, ensure_ascii=False, indent=2))
    except EstimatorError as exc:
        typer.echo(f"{exc.code}: {exc.message}", err=True)
        raise typer.Exit(2)


@app.command()
def estimate(
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    project_id: Optional[str] = typer.Option(None, "--project-id", help="Stored project id from create."),
    input_file: Optional[Path] = typer.Option(None, "--input", "-i", help="JSON project input file."),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Optional JSON output path."),
    city: str = typer.Option("", envvar="RENOVATION_CITY"),
    property_type: str = typer.Option("apartment", envvar="RENOVATION_PROPERTY_TYPE"),
    area_sqm: float = typer.Option(0.0, envvar="RENOVATION_AREA_SQM"),
    scope_level: str = typer.Option("partial", envvar="RENOVATION_SCOPE_LEVEL"),
    finish_level: str = typer.Option("standard", envvar="RENOVATION_FINISH_LEVEL"),
    bathrooms: int = typer.Option(0, envvar="RENOVATION_BATHROOMS"),
    kitchens: int = typer.Option(0, envvar="RENOVATION_KITCHENS"),
    include_vat: bool = typer.Option(True, envvar="RENOVATION_INCLUDE_VAT"),
    vat_rate: float = typer.Option(0.18, envvar="RENOVATION_VAT_RATE"),
    language: str = typer.Option("en", envvar="RENOVATION_LANGUAGE"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Estimate a stored project, JSON file, or command-line project."""
    try:
        client = _client(vat_rate)
        if project_id:
            result = client.estimate_by_id(project_id, environment=env)
        elif input_file:
            project = ProjectInput.from_mapping(json.loads(input_file.read_text(encoding="utf-8")))
            result = client.estimate(project)
        else:
            project = ProjectInput(
                city=city,
                property_type=property_type,
                area_sqm=area_sqm,
                scope_level=scope_level,
                finish_level=finish_level,
                bathrooms=bathrooms,
                kitchens=kitchens,
                include_vat=include_vat,
                vat_rate=vat_rate,
                language=language,
            )
            result = client.estimate(project)

        if output_file:
            output_file.write_text(result.to_json(), encoding="utf-8")
        typer.echo(result.to_json() if json_output else result.to_text(language=language))
    except EstimatorError as exc:
        typer.echo(f"{exc.code}: {exc.message}", err=True)
        raise typer.Exit(2)


@app.command()
def benchmarks(json_output: bool = typer.Option(True, "--json/--text")) -> None:
    """Print benchmark registry."""
    data = RenovationCostEstimatorClient().benchmarks()
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2) if json_output else str(data))


@app.command()
def validate(input_file: Path = typer.Argument(...)) -> None:
    """Validate a project input file."""
    try:
        RenovationCostEstimatorClient().validate(ProjectInput.from_mapping(json.loads(input_file.read_text(encoding="utf-8"))))
        typer.echo("valid")
    except EstimatorError as exc:
        typer.echo(f"{exc.code}: {exc.message}", err=True)
        raise typer.Exit(2)


@app.command()
def scenario(name: str = typer.Argument("clinic"), env: str = typer.Option("sandbox", "--env")) -> None:
    """Run a built-in scenario."""
    scenarios = {
        "apartment": {"project_name": "72 m² apartment", "city": "Ramat Gan", "area_sqm": 72, "scope_level": "partial", "finish_level": "standard", "bathrooms": 1, "kitchens": 1},
        "clinic": {"project_name": "Clinic fit-out", "city": "Tel Aviv", "property_type": "clinic", "area_sqm": 38, "scope_level": "commercial_fitout", "finish_level": "standard", "requires_business_license": True, "commercial_public_access": True, "include_vat": False},
        "shop": {"project_name": "Retail shop", "city": "Jerusalem", "property_type": "shop", "area_sqm": 42, "scope_level": "retail_fitout", "finish_level": "premium", "requires_business_license": True, "signage": True, "include_vat": False},
        "office": {"project_name": "Small office", "city": "Bnei Brak", "property_type": "office", "area_sqm": 60, "scope_level": "office_fitout", "finish_level": "standard", "include_vat": False},
    }
    if name not in scenarios:
        typer.echo(f"UNKNOWN_SCENARIO: choose one of {', '.join(sorted(scenarios))}", err=True)
        raise typer.Exit(2)
    result = RenovationCostEstimatorClient().estimate(scenarios[name])
    typer.echo(result.to_text())


def main() -> None:
    app()


if __name__ == "__main__":
    main()
