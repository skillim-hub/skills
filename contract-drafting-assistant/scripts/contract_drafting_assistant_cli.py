#!/usr/bin/env python3
"""Command-line interface for the contract drafting helper."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import typer

import contract_drafting_assistant_client as client_mod

app = typer.Typer(
    help="Draft and check Israeli service, freelance, consumer, NDA, sale, and supply agreements."
)


@app.command()
def new(
    input_json: Path = typer.Argument(..., exists=True, readable=True, help="Input JSON file."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output markdown path."),
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON result."),
    async_mode: bool = typer.Option(False, "--async", help="Use the async helper path."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Generate a contract draft from a JSON input file."""

    _validate_env(env)
    client = client_mod.ContractDraftingClient()
    terms = client_mod.load_terms(input_json)
    result = asyncio.run(client.async_draft(terms)) if async_mode else client.draft(terms)
    if output:
        client_mod.save_draft(result, output)
        typer.echo(json.dumps({"env": env, "output": str(output)}, ensure_ascii=False, indent=2))
        return
    payload = json.loads(result.to_json())
    payload["env"] = env
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2) if json_output else result.contract_markdown)


@app.command()
def check(
    input_json: Path = typer.Argument(..., exists=True, readable=True, help="Input JSON file."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON findings."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Scan contract inputs for common Israeli drafting risks."""

    _validate_env(env)
    terms = client_mod.load_terms(input_json)
    findings = client_mod.scan_risks(terms)
    if json_output:
        typer.echo(
            json.dumps(
                {"env": env, "findings": [asdict(f) for f in findings]},
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if not findings:
        typer.echo("No findings.")
        return
    for item in findings:
        typer.echo(f"{item.severity.upper()} {item.code}: {item.message} Fix: {item.fix}")


@app.command()
def vat(
    amount: float = typer.Argument(..., min=0, help="Net amount in NIS."),
    rate: float = typer.Option(client_mod.DEFAULT_VAT_RATE, "--rate", min=0, max=1, help="VAT rate."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Calculate VAT and total amount."""

    _validate_env(env)
    result = client_mod.calculate_vat(amount, rate)
    result["env"] = env
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@app.command("validate-id")
def validate_id(
    id_number: str = typer.Argument(..., help="Israeli ID number."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Validate an Israeli ID checksum."""

    _validate_env(env)
    try:
        normalized = client_mod.normalize_israeli_id(id_number)
        valid = client_mod.validate_israeli_id(id_number)
    except ValueError as exc:
        typer.echo(json.dumps({"env": env, "valid": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        raise typer.Exit(code=1)
    typer.echo(json.dumps({"env": env, "valid": valid, "normalized": normalized}, ensure_ascii=False, indent=2))
    if not valid:
        raise typer.Exit(code=1)


@app.command()
def scenario(
    name: str = typer.Argument("freelance-design", help="Built-in scenario name."),
    language: str = typer.Option("he", "--language", "-l", help="he or en."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output markdown path."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Generate a built-in scenario draft."""

    _validate_env(env)
    if name not in client_mod.scenario_names():
        typer.echo(f"Unknown scenario: {name}. Available: {', '.join(client_mod.scenario_names())}")
        raise typer.Exit(code=2)
    if language not in {"he", "en"}:
        typer.echo("language must be he or en")
        raise typer.Exit(code=2)
    terms = client_mod.sample_terms(name, language)
    result = client_mod.ContractDraftingClient().draft(terms)
    if output:
        client_mod.save_draft(result, output)
        typer.echo(json.dumps({"env": env, "output": str(output)}, ensure_ascii=False, indent=2))
    else:
        typer.echo(result.contract_markdown)


@app.command("list-scenarios")
def list_scenarios() -> None:
    """List built-in scenarios."""

    typer.echo(json.dumps({"scenarios": client_mod.scenario_names()}, ensure_ascii=False, indent=2))


def _validate_env(env: str) -> None:
    if env not in {"sandbox", "production"}:
        typer.echo("env must be sandbox or production")
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
