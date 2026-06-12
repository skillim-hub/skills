"""Typer command line interface for lead qualification."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer

from .client import LeadQualificationClient, flatten_lead

app = typer.Typer(help="Qualify Hebrew WhatsApp leads for Israeli small businesses.")


@app.command()
def create(
    message: str = typer.Option(..., "--message", "-m", help="Inbound WhatsApp message in Hebrew."),
    phone: Optional[str] = typer.Option(None, "--phone", "-p", help="Israeli phone number."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Customer name."),
    city: Optional[str] = typer.Option(None, "--city", "-c", help="City override."),
    env: str = typer.Option("sandbox", "--env", help="Runtime environment: sandbox or production."),
    marketing_consent: bool = typer.Option(False, "--marketing-consent", help="Whether marketing consent is already captured."),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON."),
) -> None:
    """Create and qualify a single lead, then print JSON."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("--env must be sandbox or production")
    client = LeadQualificationClient(environment=env)  # type: ignore[arg-type]
    lead = client.create_lead(
        message=message,
        phone=phone,
        name=name,
        city=city,
        marketing_consent=marketing_consent,
    )
    typer.echo(json.dumps(client.to_dict(lead), ensure_ascii=False, indent=2 if pretty else None))


@app.command()
def qualify(
    message: str = typer.Option(..., "--message", "-m", help="Inbound WhatsApp message in Hebrew."),
    phone: Optional[str] = typer.Option(None, "--phone", "-p", help="Israeli phone number."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Customer name."),
    city: Optional[str] = typer.Option(None, "--city", "-c", help="City override."),
    env: str = typer.Option("sandbox", "--env", help="Runtime environment: sandbox or production."),
    marketing_consent: bool = typer.Option(False, "--marketing-consent", help="Whether marketing consent is already captured."),
    async_mode: bool = typer.Option(False, "--async", help="Run through async client path."),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON."),
) -> None:
    """Qualify a single message and print JSON."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("--env must be sandbox or production")
    client = LeadQualificationClient(environment=env)  # type: ignore[arg-type]

    async def run_async():
        return await client.acreate_lead(
            message=message,
            phone=phone,
            name=name,
            city=city,
            marketing_consent=marketing_consent,
        )

    lead = asyncio.run(run_async()) if async_mode else client.create_lead(
        message=message,
        phone=phone,
        name=name,
        city=city,
        marketing_consent=marketing_consent,
    )
    typer.echo(json.dumps(client.to_dict(lead), ensure_ascii=False, indent=2 if pretty else None))


@app.command()
def get(
    lead_json: Path = typer.Option(..., "--lead-json", exists=True, readable=True, help="Path to JSON produced by the create command."),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON."),
) -> None:
    """Read a lead JSON file and print its normalized dictionary."""
    data = json.loads(lead_json.read_text(encoding="utf-8"))
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2 if pretty else None))


@app.command()
def batch(
    input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="Input CSV with message, phone, name columns."),
    output: Path = typer.Option(..., "--output", "-o", help="Output CSV path."),
    env: str = typer.Option("sandbox", "--env", help="Runtime environment: sandbox or production."),
) -> None:
    """Qualify all rows in a CSV file."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("--env must be sandbox or production")
    client = LeadQualificationClient(environment=env)  # type: ignore[arg-type]
    leads = client.batch_csv(input, output)
    typer.echo(f"Wrote {len(leads)} qualified leads to {output}")


@app.command()
def ask_next(
    message: str = typer.Option(..., "--message", "-m", help="Inbound message."),
    phone: Optional[str] = typer.Option(None, "--phone", "-p", help="Phone number."),
    env: str = typer.Option("sandbox", "--env", help="Runtime environment: sandbox or production."),
) -> None:
    """Print only the next recommended Hebrew bot message."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("--env must be sandbox or production")
    client = LeadQualificationClient(environment=env)  # type: ignore[arg-type]
    lead = client.create_lead(message=message, phone=phone)
    typer.echo(lead.qualification.next_question)


@app.command()
def flatten(
    message: str = typer.Option(..., "--message", "-m", help="Inbound message."),
    phone: Optional[str] = typer.Option(None, "--phone", "-p", help="Phone number."),
    env: str = typer.Option("sandbox", "--env", help="Runtime environment: sandbox or production."),
) -> None:
    """Print flattened CSV-style JSON for integrations."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("--env must be sandbox or production")
    client = LeadQualificationClient(environment=env)  # type: ignore[arg-type]
    lead = client.create_lead(message=message, phone=phone)
    typer.echo(json.dumps(flatten_lead(lead), ensure_ascii=False, indent=2))


def main() -> None:
    """Run the Typer application."""
    app()


if __name__ == "__main__":
    main()
