"""Command line interface for HR Compliance Advisor."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import EmployeeFacts, HRComplianceClient, config_from_env, report_to_markdown, validate_facts

app = typer.Typer(help="Offline Israeli HR compliance triage CLI. Verify current legal rates before action.", no_args_is_help=True)


def _client_from_env() -> HRComplianceClient:
    return HRComplianceClient(config_from_env())


@app.command()
def analyze(
    input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="JSON file containing EmployeeFacts fields."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Optional output JSON file."),
    markdown: bool = typer.Option(False, "--markdown", help="Render markdown instead of JSON."),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Analyze a JSON facts file."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    report = _client_from_env().review_file(input)
    report["environment"] = env
    rendered = report_to_markdown(report) if markdown else json.dumps(report, ensure_ascii=False, indent=2 if pretty else None)
    if output:
        output.write_text(rendered + ("\n" if not rendered.endswith("\n") else ""), encoding="utf-8")
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(rendered)


@app.command("create-case")
def create_case(
    input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="JSON file containing EmployeeFacts fields."),
    case_dir: Path = typer.Option(Path(".hr-compliance-cases"), "--case-dir", help="Directory for stored case files."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Create a local case and print its identifier."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    data = json.loads(input.read_text(encoding="utf-8"))
    response = _client_from_env().create_case(data, case_dir=case_dir, environment=env)
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


@app.command("review-case")
def review_case(
    case_id: str = typer.Argument(..., help="Case identifier returned by create-case."),
    case_dir: Path = typer.Option(Path(".hr-compliance-cases"), "--case-dir", help="Directory for stored case files."),
    markdown: bool = typer.Option(False, "--markdown", help="Render markdown instead of JSON."),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON."),
) -> None:
    """Review a previously created local case."""
    report = _client_from_env().review_case(case_id, case_dir=case_dir)
    rendered = report_to_markdown(report) if markdown else json.dumps(report, ensure_ascii=False, indent=2 if pretty else None)
    typer.echo(rendered)


@app.command("validate-json")
def validate_json(input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="JSON facts file to validate.")) -> None:
    """Validate a JSON facts file."""
    facts = EmployeeFacts(**json.loads(input.read_text(encoding="utf-8")))
    validate_facts(facts)
    typer.echo("OK")


@app.command()
def scenario(name: str = typer.Argument("retail-minimum-wage")) -> None:
    """Print a built-in scenario JSON."""
    scenarios = {
        "retail-minimum-wage": {"worker_type": "employee", "sector": "retail", "hourly_rate_ils": 31.0, "weekly_hours": 38, "tenure_months": 10, "has_pension_arrangement": False, "contract_text": "Closing time is unpaid."},
        "global-overtime": {"worker_type": "employee", "sector": "tech", "monthly_salary_ils": 9500, "weekly_hours": 54, "daily_hours": 11, "overtime_hours_weekly": 12, "tenure_months": 8, "contract_text": "Salary includes all overtime."},
        "contractor-risk": {"worker_type": "contractor", "sector": "design", "tenure_months": 18, "contractor_controls": 5, "contract_text": "Full time contractor uses company email and needs manager approval for vacation."},
    }
    if name not in scenarios:
        raise typer.BadParameter(f"Unknown scenario. Choose one of: {', '.join(sorted(scenarios))}")
    typer.echo(json.dumps(scenarios[name], ensure_ascii=False, indent=2))


@app.command()
def version() -> None:
    """Print package version."""
    metadata_path = Path(__file__).resolve().parents[1] / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    typer.echo(metadata.get("version", "unknown"))


if __name__ == "__main__":
    app()
