from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import LeaseAgreementDrafterClient, load_request_file

app = typer.Typer(help="Draft and audit Israeli apartment and office lease agreements.")


def _client(env: str) -> LeaseAgreementDrafterClient:
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    return LeaseAgreementDrafterClient.from_env(environment=env)  # type: ignore[arg-type]


@app.command()
def draft(
    input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="JSON request file."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Optional Markdown output path."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    response_format: str = typer.Option("json", "--format", help="json or markdown."),
) -> None:
    """Create a lease draft from a JSON request."""
    client = _client(env)
    request = load_request_file(input)
    result = client.draft(request)
    if output:
        client.export_markdown(result, output)
    if response_format == "markdown":
        typer.echo(result.markdown)
        return
    payload = result.to_dict()
    if output:
        payload["output"] = str(output)
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command()
def audit(
    input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="Markdown or text draft file."),
    draft_id: str = typer.Option(..., "--draft-id", help="Draft id returned from the draft command."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production."),
) -> None:
    """Scan an existing draft for common missing clauses."""
    client = _client(env)
    findings = client.scan_template(input.read_text(encoding="utf-8"))
    payload = {"id": draft_id, "environment": client.environment, "findings": [finding.to_dict() for finding in findings]}
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("schema")
def schema(env: str = typer.Option("sandbox", "--env", help="sandbox or production.")) -> None:
    """Print the request schema."""
    client = _client(env)
    typer.echo(json.dumps(client.request_schema(), ensure_ascii=False, indent=2))


@app.command("error-catalog")
def error_catalog(env: str = typer.Option("sandbox", "--env", help="sandbox or production.")) -> None:
    """Print validation error codes."""
    client = _client(env)
    typer.echo(json.dumps(client.error_catalog(), ensure_ascii=False, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
