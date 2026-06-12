"""Command-line interface for the Hebrew Translation Assistant."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from .client import (
    Direction,
    Environment,
    HebrewTranslationAssistant,
    HelperError,
    Register,
    get_reference_facts,
    localize_date,
    result_to_markdown,
)

app = typer.Typer(
    help="Hebrew-English translation helper for Israeli business, freelance, and consumer contexts.",
    no_args_is_help=True,
)


def _client() -> HebrewTranslationAssistant:
    storage = os.getenv("HEBREW_TRANSLATION_ASSISTANT_HOME")
    return HebrewTranslationAssistant(storage_dir=Path(storage) if storage else None)


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, HelperError):
        typer.echo(f"{exc.code}: {exc.message}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1) from exc


@app.command()
def translate(
    text: str = typer.Argument(..., help="Source text to translate or adapt."),
    direction: str = typer.Option(Direction.AUTO.value, "--direction", "-d"),
    register: str = typer.Option(Register.BUSINESS.value, "--register", "-r"),
    audience: Optional[str] = typer.Option(None, "--audience", "-a"),
    industry: Optional[str] = typer.Option(None, "--industry", "-i"),
    preserve: list[str] = typer.Option(None, "--preserve", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Translate text with terminology and register assistance."""

    try:
        result = _client().translate_text(
            text=text,
            direction=direction,
            register=register,
            audience=audience,
            industry=industry,
            preserve_terms=tuple(preserve or ()),
        )
    except Exception as exc:
        _handle_error(exc)
    typer.echo(result.to_json() if json_output else result_to_markdown(result))


@app.command()
def create(
    text: str = typer.Argument(..., help="Source text to translate and store."),
    direction: str = typer.Option(Direction.AUTO.value, "--direction", "-d"),
    register: str = typer.Option(Register.BUSINESS.value, "--register", "-r"),
    env: str = typer.Option(Environment.SANDBOX.value, "--env"),
    audience: Optional[str] = typer.Option(None, "--audience", "-a"),
    industry: Optional[str] = typer.Option(None, "--industry", "-i"),
    preserve: list[str] = typer.Option(None, "--preserve", "-p"),
) -> None:
    """Create a stored translation request and print JSON containing the id."""

    try:
        job = _client().create_request(
            text=text,
            direction=direction,
            register=register,
            environment=env,
            audience=audience,
            industry=industry,
            preserve_terms=tuple(preserve or ()),
        )
    except Exception as exc:
        _handle_error(exc)
    typer.echo(job.to_json())


@app.command()
def show(request_id: str = typer.Argument(..., help="Stored request id.")) -> None:
    """Show a stored translation request generated through the create command."""

    try:
        item = _client().get_request(request_id)
    except Exception as exc:
        _handle_error(exc)
    typer.echo(json.dumps(item, ensure_ascii=False, indent=2))


@app.command("list")
def list_requests() -> None:
    """List stored translation requests."""

    try:
        items = _client().list_requests()
    except Exception as exc:
        _handle_error(exc)
    typer.echo(json.dumps(items, ensure_ascii=False, indent=2))


@app.command()
def review(
    text: str = typer.Argument(...),
    register: str = typer.Option(Register.BUSINESS.value, "--register", "-r"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Review text without storing a translation request."""

    try:
        result = _client().review_text(text, register=register)
    except Exception as exc:
        _handle_error(exc)
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo(f"Direction: {result['direction']}")
    typer.echo(f"Register: {result['register']}")
    if result["detected_terms"]:
        typer.echo("Detected terms:")
        for source, target in result["detected_terms"].items():
            typer.echo(f"- {source} -> {target}")
    if result["notes"]:
        typer.echo("Notes:")
        for note in result["notes"]:
            typer.echo(f"- {note}")
    if result["warnings"]:
        typer.echo("Warnings:")
        for warning in result["warnings"]:
            typer.echo(f"- {warning}")


@app.command()
def glossary(
    term: str = typer.Argument(...),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Look up a glossary term."""

    try:
        result = _client().glossary_lookup(term)
    except Exception as exc:
        _handle_error(exc)
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for source, target in result.items():
            typer.echo(f"{source} -> {target}")


@app.command("localize-date")
def localize_date_command(value: str = typer.Argument(...)) -> None:
    """Convert a date to Israeli DD/MM/YYYY format."""

    try:
        typer.echo(localize_date(value))
    except Exception as exc:
        _handle_error(exc)



@app.command("facts")
def reference_facts_command() -> None:
    """Print source-sensitive Israeli reference facts for this release."""

    typer.echo(json.dumps(get_reference_facts(), ensure_ascii=False, indent=2))

def main() -> None:
    """Run the CLI."""

    app()


if __name__ == "__main__":
    main()
