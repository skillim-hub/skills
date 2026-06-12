"""Command-line interface for the Tax-Law Explainer helper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.table import Table

from tax_law_explainer import TaxLawExplainerClient, load_facts_json, scenario_payload

app = typer.Typer(help="Explain Israeli tax-law workflows with structured safeguards.")


def _client(language: str) -> TaxLawExplainerClient:
    return TaxLawExplainerClient(default_language=language)


def _validate_env(env: str) -> str:
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    return env


@app.command()
def list_topics() -> None:
    """Print supported explanation topics."""
    table = Table(title="Supported topics")
    table.add_column("Topic")
    for topic in TaxLawExplainerClient.topics():
        table.add_row(topic)
    rprint(table)


@app.command()
def list_workflows() -> None:
    """Print supported workflow checklists."""
    table = Table(title="Supported workflows")
    table.add_column("Workflow")
    for workflow in TaxLawExplainerClient.workflows():
        table.add_row(workflow)
    rprint(table)


@app.command()
def explain(
    topic: str = typer.Option(..., help="Supported topic slug."),
    business_type: str = typer.Option("unspecified", help="User or business type."),
    annual_turnover: Optional[float] = typer.Option(None, help="Expected annual turnover in NIS."),
    profession: Optional[str] = typer.Option(None, help="Profession or activity description."),
    facts_json: Optional[str] = typer.Option(None, help="JSON object or path to JSON file with additional facts."),
    language: str = typer.Option("en", help="en or he."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production. Production still requires official verification."),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON."),
) -> None:
    """Explain a supported tax topic."""
    _validate_env(env)
    facts = load_facts_json(facts_json)
    facts["environment"] = env
    if annual_turnover is not None:
        facts["annual_turnover"] = annual_turnover
    if profession is not None:
        facts["profession"] = profession
    result = _client(language).explain(topic, user_type=business_type, facts=facts, language=language)
    payload = result.to_dict()
    payload["environment"] = env
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    rprint(f"[bold]{result.summary}[/bold]")
    rprint(f"Environment: {env}")
    rprint("\nDecision points:")
    for point in result.decision_points:
        rprint(f"- {point}")
    if result.missing_facts:
        rprint("\nMissing facts:")
        for fact in result.missing_facts:
            rprint(f"- {fact}")
    rprint("\nWarnings:")
    for warning in result.warnings:
        rprint(f"- {warning}")


@app.command()
def validate(
    topic: str = typer.Option(..., help="Supported topic slug."),
    facts_json: str = typer.Option("{}", help="JSON object or path to JSON file."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON."),
) -> None:
    """Validate whether facts are sufficient for a topic."""
    _validate_env(env)
    facts = load_facts_json(facts_json)
    facts["environment"] = env
    result = TaxLawExplainerClient().validate_facts(topic, facts)
    payload = result.to_dict()
    payload["environment"] = env
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    rprint(f"Valid: {result.valid}")
    rprint(f"Environment: {env}")
    if result.missing:
        rprint("Missing:")
        for item in result.missing:
            rprint(f"- {item}")
    if result.warnings:
        rprint("Warnings:")
        for item in result.warnings:
            rprint(f"- {item}")


@app.command()
def checklist(
    workflow: str = typer.Option(..., help="Supported workflow slug."),
    language: str = typer.Option("en", help="en or he."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON."),
) -> None:
    """Print a workflow checklist."""
    _validate_env(env)
    result = _client(language).checklist(workflow, language=language)
    result["environment"] = env
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    rprint(f"[bold]{workflow}[/bold]")
    rprint(f"Environment: {env}")
    for index, step in enumerate(result["steps"], start=1):
        rprint(f"{index}. {step}")


@app.command()
def export_scenario(
    scenario: str = typer.Option(..., help="Scenario name."),
    output: Path = typer.Option(..., help="Output JSON path."),
    language: str = typer.Option("en", help="en or he."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Write a runnable scenario JSON file."""
    _validate_env(env)
    payload = scenario_payload(scenario, language=language)
    payload["environment"] = env
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    rprint(f"Wrote {output}")


@app.command()
def run_scenario(
    scenario: str = typer.Option(..., help="Scenario name."),
    language: str = typer.Option("en", help="en or he."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON."),
) -> None:
    """Run one built-in scenario."""
    _validate_env(env)
    payload = scenario_payload(scenario, language=language)
    payload["facts"]["environment"] = env
    result = _client(language).explain(payload["topic"], facts=payload["facts"], language=language)
    output = result.to_dict()
    output["environment"] = env
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return
    rprint(f"[bold]{result.summary}[/bold]")
    rprint(f"Environment: {env}")
    for point in result.decision_points:
        rprint(f"- {point}")


if __name__ == "__main__":
    app()
