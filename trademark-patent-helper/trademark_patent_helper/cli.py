"""Command-line interface for the Israeli trademark and patent filing helper."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import click

from .client import Assessment, FilingHelperClient, load_json


def _emit(result: Assessment | dict | list, output_format: str) -> None:
    if isinstance(result, Assessment):
        click.echo(result.to_json() if output_format == "json" else result.to_markdown())
        return
    click.echo(json.dumps(result, ensure_ascii=False, indent=2))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Prepare structured trademark and patent filing guidance for Israel."""


@cli.command()
@click.argument("input_json", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--format", "output_format", type=click.Choice(["json", "markdown"]), default="markdown", show_default=True)
@click.option("--async-mode", is_flag=True, help="Use the async assessment path.")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
def assess(input_json: Path, output_format: str, async_mode: bool, environment: str) -> None:
    """Assess a trademark or patent request from a JSON file."""
    payload = load_json(input_json)
    helper = FilingHelperClient(environment=environment)
    if async_mode:
        result = asyncio.run(helper.assess_async(payload))
    else:
        result = helper.assess(payload)
    _emit(result, output_format)


@cli.command()
@click.argument("input_json", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--format", "output_format", type=click.Choice(["json", "markdown"]), default="json", show_default=True)
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--state", "state_path", type=click.Path(dir_okay=False, path_type=Path), default=None)
def create(input_json: Path, output_format: str, environment: str, state_path: Path | None) -> None:
    """Create a local assessment record and return its request ID."""
    payload = load_json(input_json)
    result = FilingHelperClient(environment=environment).create(payload, state_path=state_path)
    _emit(result, output_format)


@cli.command()
@click.argument("request_id")
@click.option("--format", "output_format", type=click.Choice(["json", "markdown"]), default="markdown", show_default=True)
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--state", "state_path", type=click.Path(dir_okay=False, path_type=Path), default=None)
def show(request_id: str, output_format: str, environment: str, state_path: Path | None) -> None:
    """Show a local assessment record by request ID."""
    result = FilingHelperClient(environment=environment).get(request_id, state_path=state_path)
    _emit(result, output_format)


@cli.command()
@click.argument("description", nargs=-1)
@click.option("--format", "output_format", type=click.Choice(["json", "markdown"]), default="markdown", show_default=True)
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
def intake(description: tuple[str, ...], output_format: str, environment: str) -> None:
    """Classify a plain-language asset description."""
    text = " ".join(description).strip()
    payload = {"description": text}
    helper = FilingHelperClient(environment=environment)
    kind = helper.classify_asset(payload)
    result = helper.assess({**payload, "kind": kind} if kind != "unknown" else payload)
    _emit(result, output_format)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--format", "output_format", type=click.Choice(["json", "markdown"]), default="json", show_default=True)
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
def batch(input_dir: Path, output_format: str, environment: str) -> None:
    """Assess every JSON file in a directory."""
    helper = FilingHelperClient(environment=environment)
    results = []
    for path in sorted(input_dir.glob("*.json")):
        result = helper.assess(load_json(path))
        results.append({"file": path.name, "assessment": result.to_dict()})
    if output_format == "json":
        click.echo(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for item in results:
            click.echo(f"## {item['file']}")
            click.echo(Assessment(**item["assessment"]).to_markdown())


@cli.command("template")
@click.argument("kind", type=click.Choice(["trademark", "patent"]))
def template(kind: str) -> None:
    """Print a starter JSON template."""
    if kind == "trademark":
        payload = {
            "kind": "trademark",
            "applicant_name": "",
            "mark_text": "",
            "mark_type": "word",
            "meaning": "",
            "classes": [{"class_no": 0, "items": []}],
            "first_use": "",
            "known_similar_marks": [],
        }
    else:
        payload = {
            "kind": "patent",
            "title": "",
            "applicant_name": "",
            "inventors": [],
            "technical_field": "",
            "problem": "",
            "solution": "",
            "novel_features": [],
            "public_disclosures": [],
            "known_prior_art": [],
        }
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    cli()
