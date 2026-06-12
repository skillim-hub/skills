"""Command line interface for the privacy compliance checker."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import click

from .client import PrivacyComplianceCheckerClient, get_scenario, list_scenarios, load_json


def _parse_payload(json_text: str | None, file_path: str | None, scenario: str | None) -> dict[str, Any]:
    provided = [value is not None for value in (json_text, file_path, scenario)].count(True)
    if provided != 1:
        raise click.ClickException("Provide exactly one of --json, --file, or --scenario.")
    if json_text is not None:
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as exc:
            raise click.ClickException(f"Invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise click.ClickException("JSON input must be an object.")
        return data
    if file_path is not None:
        try:
            return load_json(file_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise click.ClickException(str(exc)) from exc
    try:
        return get_scenario(str(scenario))
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


def _client_from_context(ctx: click.Context) -> PrivacyComplianceCheckerClient:
    obj = ctx.ensure_object(dict)
    return PrivacyComplianceCheckerClient(environment=obj["environment"], state_dir=obj["state_dir"])


def _emit(data: Any, fmt: str) -> None:
    if fmt == "json":
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    elif fmt == "markdown" and isinstance(data, str):
        click.echo(data, nl=False)
    else:
        click.echo(str(data))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default=lambda: os.getenv("PCC_ENV", "sandbox"), show_default="PCC_ENV or sandbox", help="Execution environment.")
@click.option("--state-dir", type=click.Path(file_okay=False), default=lambda: os.getenv("PCC_STATE_DIR", ".pcc-state"), show_default="PCC_STATE_DIR or .pcc-state", help="Directory for saved assessment records.")
@click.pass_context
def cli(ctx: click.Context, environment: str, state_dir: str) -> None:
    """Assess Israeli privacy, GDPR, and operational privacy controls."""

    ctx.ensure_object(dict)
    ctx.obj["environment"] = environment
    ctx.obj["state_dir"] = state_dir


@cli.command()
@click.option("--json", "json_text", help="Assessment JSON object.")
@click.option("--file", "file_path", type=click.Path(exists=True, dir_okay=False), help="Path to assessment JSON.")
@click.option("--scenario", type=click.Choice(list_scenarios()), help="Built-in scenario name.")
@click.option("--format", "fmt", type=click.Choice(["json", "markdown"]), default="markdown", show_default=True)
@click.option("--output", type=click.Path(dir_okay=False), help="Write the report to this path.")
@click.pass_context
def assess(ctx: click.Context, json_text: str | None, file_path: str | None, scenario: str | None, fmt: str, output: str | None) -> None:
    """Generate a compliance assessment without saving state."""

    payload = _parse_payload(json_text, file_path, scenario)
    result = _client_from_context(ctx).assess(payload)
    rendered = result.to_json() if fmt == "json" else result.to_markdown()
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
        click.echo(f"Wrote {output}")
    else:
        click.echo(rendered, nl=False)


@cli.command()
@click.option("--json", "json_text", help="Assessment JSON object.")
@click.option("--file", "file_path", type=click.Path(exists=True, dir_okay=False), help="Path to assessment JSON.")
@click.option("--scenario", type=click.Choice(list_scenarios()), help="Built-in scenario name.")
@click.option("--format", "fmt", type=click.Choice(["json"]), default="json", show_default=True)
@click.pass_context
def create(ctx: click.Context, json_text: str | None, file_path: str | None, scenario: str | None, fmt: str) -> None:
    """Assess and save a record, then return its ID."""

    payload = _parse_payload(json_text, file_path, scenario)
    response = _client_from_context(ctx).create(payload)
    _emit(response, fmt)


@cli.command(name="get")
@click.argument("assessment_id")
@click.option("--format", "fmt", type=click.Choice(["json", "markdown"]), default="markdown", show_default=True)
@click.pass_context
def get_record(ctx: click.Context, assessment_id: str, fmt: str) -> None:
    """Read a saved assessment by ID."""

    client = _client_from_context(ctx)
    try:
        if fmt == "json":
            click.echo(json.dumps(client.get(assessment_id), ensure_ascii=False, indent=2))
        else:
            click.echo(client.export_report(assessment_id, "markdown"), nl=False)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("assessment_id")
@click.option("--json", "json_text", required=True, help="Patch JSON object.")
@click.pass_context
def update(ctx: click.Context, assessment_id: str, json_text: str) -> None:
    """Patch an assessment input and re-run the saved assessment."""

    try:
        patch = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid JSON: {exc}") from exc
    if not isinstance(patch, dict):
        raise click.ClickException("Patch must be a JSON object.")
    try:
        response = _client_from_context(ctx).update(assessment_id, patch)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(response, ensure_ascii=False, indent=2))


@cli.command(name="list")
@click.pass_context
def list_records(ctx: click.Context) -> None:
    """List saved assessments."""

    click.echo(json.dumps(_client_from_context(ctx).list_records(), ensure_ascii=False, indent=2))


@cli.command()
@click.argument("assessment_id")
@click.pass_context
def delete(ctx: click.Context, assessment_id: str) -> None:
    """Delete a saved assessment."""

    try:
        response = _client_from_context(ctx).delete(assessment_id)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(response, ensure_ascii=False, indent=2))


@cli.command()
@click.option("--scenario", type=click.Choice(list_scenarios()), default="customer-club", show_default=True)
def template(scenario: str) -> None:
    """Print a built-in scenario JSON template."""

    click.echo(json.dumps(get_scenario(scenario), ensure_ascii=False, indent=2))


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False))
@click.pass_context
def validate(ctx: click.Context, file_path: str) -> None:
    """Validate an assessment JSON file."""

    try:
        response = _client_from_context(ctx).validate(load_json(file_path))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(response, ensure_ascii=False, indent=2))


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--format", "fmt", type=click.Choice(["json", "markdown"]), default="markdown", show_default=True)
@click.pass_context
def checklist(ctx: click.Context, file_path: str, fmt: str) -> None:
    """Generate only the checklist for an assessment file."""

    try:
        result = _client_from_context(ctx).assess(load_json(file_path))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        raise click.ClickException(str(exc)) from exc
    if fmt == "json":
        click.echo(json.dumps([item.to_dict() for item in result.checklist], ensure_ascii=False, indent=2))
    else:
        click.echo(result.checklist_markdown(), nl=False)


@cli.command()
def scenarios() -> None:
    """List built-in scenario names."""

    click.echo(json.dumps(list_scenarios(), ensure_ascii=False, indent=2))


def main() -> None:
    """Console-script entry point."""

    cli()


if __name__ == "__main__":
    main()
