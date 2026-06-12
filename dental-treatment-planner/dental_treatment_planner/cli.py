from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import DentalTreatmentPlannerClient, format_currency, load_json, sample_plan, treatment_catalog

app = typer.Typer(help="Plan Israeli dental treatments and cost estimates.")
catalog_app = typer.Typer(help="Catalog utilities.")
app.add_typer(catalog_app, name="catalog")


def _client(env: str) -> DentalTreatmentPlannerClient:
    return DentalTreatmentPlannerClient(environment=env)


@app.command()
def sample(output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write sample JSON to file.")) -> None:
    """Print or write a sample treatment-plan request."""
    data = sample_plan()
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if output:
        output.write_text(text + "\n", encoding="utf-8")
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(text)


@app.command()
def create(
    output: Path = typer.Argument(..., help="Destination plan JSON file."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    provider: str = typer.Option("private", help="Provider profile."),
    region: str = typer.Option("center", help="Israeli region profile."),
) -> None:
    """Create a validated editable request and print a JSON response with plan_id."""
    data = sample_plan()
    data["context"]["provider"] = provider
    data["context"]["region"] = region
    envelope = _client(env).create_plan(data)
    plan_to_write = dict(data)
    plan_to_write["plan_id"] = envelope["plan_id"]
    output.write_text(json.dumps(plan_to_write, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    response = {"plan_id": envelope["plan_id"], "environment": env, "plan_path": str(output), "warnings": envelope["warnings"]}
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


@app.command()
def validate(
    plan: Path = typer.Argument(..., help="Plan JSON file."),
    strict: bool = typer.Option(False, help="Fail on warnings."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Validate a treatment-plan request."""
    data = load_json(plan)
    data.setdefault("context", {})["strict"] = strict
    warnings = _client(env).validate_plan(data)
    if warnings:
        for warning in warnings:
            typer.echo(f"WARNING: {warning}")
        if strict:
            raise typer.Exit(code=2)
    else:
        typer.echo("Valid plan.")


@app.command()
def estimate(
    plan: Path = typer.Argument(..., help="Plan JSON file."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write JSON estimate to file."),
    markdown: bool = typer.Option(False, "--markdown", help="Print Markdown instead of JSON."),
    plan_id: Optional[str] = typer.Option(None, "--plan-id", help="Expected plan id from the create response."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Estimate cost, coverage, warnings, and schedule."""
    data = load_json(plan)
    if plan_id and data.get("plan_id") != plan_id:
        raise typer.BadParameter("--plan-id does not match plan_id in the plan file")
    result = _client(env).estimate(data)
    text = result.to_markdown() if markdown else json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    if output:
        output.write_text(text + "\n", encoding="utf-8")
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(text)


@app.command()
def compare(
    plan: Path = typer.Argument(..., help="Plan JSON file."),
    providers: str = typer.Option("private,maccabident,clalit_smile", help="Comma-separated providers."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Compare estimated patient totals across providers."""
    selected = [part.strip() for part in providers.split(",") if part.strip()]
    estimates = _client(env).compare_providers(load_json(plan), selected)
    typer.echo("| Provider | Total | Visits | Warnings |")
    typer.echo("|---|---:|---:|---:|")
    for estimate_result in estimates:
        typer.echo(
            f"| {estimate_result.provider_display_name} | "
            f"{format_currency(estimate_result.total_patient_ils)} | "
            f"{estimate_result.visits} | {len(estimate_result.warnings)} |"
        )


@app.command()
def schedule(
    plan: Path = typer.Argument(..., help="Plan JSON file."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Print a draft visit schedule in DD/MM/YYYY format."""
    result = _client(env).estimate(load_json(plan))
    for entry in result.schedule:
        typer.echo(f"{entry['date']} | visit {entry['visit_number']} | {entry['code']} | {entry['minutes']} min")


@catalog_app.command("list")
def catalog_list() -> None:
    """Print built-in treatment codes."""
    for code, entry in treatment_catalog().items():
        typer.echo(f"{code}\t{entry['category']}\t{entry['description']}")


@catalog_app.command("export")
def catalog_export(output: Path = typer.Argument(..., help="Destination CSV file."), env: str = typer.Option("sandbox", "--env", help="sandbox or production.")) -> None:
    """Export the built-in treatment catalog to CSV."""
    _client(env).export_catalog_csv(output)
    typer.echo(f"Wrote {output}")


if __name__ == "__main__":
    app()
