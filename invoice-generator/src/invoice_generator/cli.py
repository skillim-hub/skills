"""Typer CLI for the invoice-generator package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import (
    SAMPLES,
    DocumentSpec,
    DocumentStore,
    Environment,
    load_spec,
    money,
    render_hebrew_markdown,
    shaam_threshold_for_date,
)

app = typer.Typer(help="Generate and validate Israeli invoice, receipt, and credit-note drafts.")


def _store(store_dir: Path) -> DocumentStore:
    return DocumentStore(store_dir)


def _resolve(source: str, env: Environment, store_dir: Path) -> DocumentSpec:
    return _store(store_dir).resolve(source, env)


@app.command()
def example(
    kind: str = typer.Option("tax-invoice", help="tax-invoice, tax-invoice-receipt, receipt, credit-note, or export-zero-rate"),
) -> None:
    """Print a runnable JSON example."""
    if kind not in SAMPLES:
        choices = ", ".join(sorted(SAMPLES))
        raise typer.BadParameter(f"Unsupported kind: {kind}. Choose one of: {choices}")
    typer.echo(json.dumps(SAMPLES[kind](), ensure_ascii=False, indent=2))


@app.command()
def create(
    path: Path,
    env: Environment = typer.Option("sandbox", "--env", help="sandbox or production"),
    store_dir: Path = typer.Option(Path(".invoice-generator-store"), "--store-dir"),
) -> None:
    """Validate a document spec, store it locally, and print the generated id."""
    spec = load_spec(path)
    created = _store(store_dir).create(spec, env)
    typer.echo(json.dumps(created.to_response(), ensure_ascii=False, indent=2))


@app.command()
def validate(
    source: str,
    env: Environment = typer.Option("sandbox", "--env", help="sandbox or production"),
    store_dir: Path = typer.Option(Path(".invoice-generator-store"), "--store-dir"),
) -> None:
    """Validate a JSON document spec or a stored document id."""
    spec = _resolve(source, env, store_dir)
    result = spec.validate()
    typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    if not result.ok:
        raise typer.Exit(code=1)


@app.command("allocation-required")
def allocation_required(
    source: str,
    env: Environment = typer.Option("sandbox", "--env", help="sandbox or production"),
    store_dir: Path = typer.Option(Path(".invoice-generator-store"), "--store-dir"),
) -> None:
    """Print whether the document requires an allocation number."""
    spec = _resolve(source, env, store_dir)
    payload = {
        "required": spec.requires_allocation(),
        "threshold": money(shaam_threshold_for_date(spec.issue_date, spec.thresholds)),
        "amount_before_vat": money(spec.amount_before_vat_abs()),
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("shaam-payload")
def shaam_payload(
    source: str,
    env: Environment = typer.Option("sandbox", "--env", help="sandbox or production"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    store_dir: Path = typer.Option(Path(".invoice-generator-store"), "--store-dir"),
) -> None:
    """Create a semantic allocation-number payload."""
    spec = _resolve(source, env, store_dir)
    text = json.dumps(spec.to_shaam_payload(), ensure_ascii=False, indent=2) + "\n"
    if output:
        output.write_text(text, encoding="utf-8")
        typer.echo(str(output))
    else:
        typer.echo(text)


@app.command()
def render(
    source: str,
    env: Environment = typer.Option("sandbox", "--env", help="sandbox or production"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    store_dir: Path = typer.Option(Path(".invoice-generator-store"), "--store-dir"),
) -> None:
    """Render a Hebrew markdown draft from a path or stored id."""
    spec = _resolve(source, env, store_dir)
    text = render_hebrew_markdown(spec)
    if output:
        output.write_text(text, encoding="utf-8")
        typer.echo(str(output))
    else:
        typer.echo(text)


@app.command()
def totals(
    source: str,
    env: Environment = typer.Option("sandbox", "--env", help="sandbox or production"),
    store_dir: Path = typer.Option(Path(".invoice-generator-store"), "--store-dir"),
) -> None:
    """Print calculated totals."""
    spec = _resolve(source, env, store_dir)
    typer.echo(json.dumps(spec.calculate_totals().to_dict(), ensure_ascii=False, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
