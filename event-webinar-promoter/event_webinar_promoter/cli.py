"""Command line interface for event-webinar-promoter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from .client import (
    EventValidationError,
    EventWebinarPromoterClient,
    build_utm_url,
    load_event,
    sample_event,
)


def json_echo(payload: Any) -> None:
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def read_payload(path: str) -> dict[str, Any]:
    try:
        return load_event(path)
    except Exception as exc:
        raise click.ClickException(f"Could not read event JSON: {exc}") from exc


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Plan and promote events/webinars for Israeli audiences."""


@cli.command()
def sample() -> None:
    """Print a sample event JSON payload."""
    json_echo(sample_event())


@cli.command()
@click.argument("event_json", type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option("--store", default=".event-webinar-promoter", show_default=True, help="Directory for stored event profiles.")
def create(event_json: str, store: str) -> None:
    """Store an event profile and return an event_id."""
    client = EventWebinarPromoterClient()
    payload = read_payload(event_json)
    try:
        response = client.create(payload, store_dir=store)
    except EventValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    json_echo(response.to_dict())


@cli.command()
@click.argument("event_json", required=False, type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option("--event-id", default=None, help="Stored event_id returned by create.")
@click.option("--store", default=".event-webinar-promoter", show_default=True, help="Directory for stored event profiles.")
def validate(event_json: str | None, event_id: str | None, store: str) -> None:
    """Validate an event JSON file or stored event_id and print warnings."""
    client = EventWebinarPromoterClient()
    try:
        payload = client.load_created(event_id, store_dir=store) if event_id else read_payload(event_json or "")
        warnings = client.validate(payload)
    except EventValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    json_echo({"valid": True, "warnings": warnings})


@cli.command()
@click.argument("event_json", required=False, type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option("--event-id", default=None, help="Stored event_id returned by create.")
@click.option("--store", default=".event-webinar-promoter", show_default=True, help="Directory for stored event profiles.")
@click.option("--output", "-o", type=click.Path(dir_okay=False, path_type=str), help="Write plan JSON to this path.")
def plan(event_json: str | None, event_id: str | None, store: str, output: str | None) -> None:
    """Generate a complete campaign plan."""
    client = EventWebinarPromoterClient()
    try:
        payload = client.load_created(event_id, store_dir=store) if event_id else read_payload(event_json or "")
        campaign = client.plan(payload)
    except EventValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    text = campaign.to_json(indent=2)
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
        click.echo(f"Wrote {output}")
    else:
        click.echo(text)


@cli.command(name="copy")
@click.argument("event_json", required=False, type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option("--event-id", default=None, help="Stored event_id returned by create.")
@click.option("--store", default=".event-webinar-promoter", show_default=True, help="Directory for stored event profiles.")
def copy_cmd(event_json: str | None, event_id: str | None, store: str) -> None:
    """Generate Hebrew-first campaign copy."""
    client = EventWebinarPromoterClient()
    try:
        payload = client.load_created(event_id, store_dir=store) if event_id else read_payload(event_json or "")
        copy = client.copy(payload)
    except EventValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    json_echo(copy)


@cli.command()
@click.argument("event_json", required=False, type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option("--event-id", default=None, help="Stored event_id returned by create.")
@click.option("--store", default=".event-webinar-promoter", show_default=True, help="Directory for stored event profiles.")
def checklist(event_json: str | None, event_id: str | None, store: str) -> None:
    """Print a production checklist."""
    client = EventWebinarPromoterClient()
    try:
        payload = client.load_created(event_id, store_dir=store) if event_id else read_payload(event_json or "")
        items = client.checklist(payload)
    except EventValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    for index, item in enumerate(items, start=1):
        click.echo(f"{index}. {item}")


@cli.command()
@click.argument("base_url")
@click.option("--source", required=True, help="UTM source, for example facebook.")
@click.option("--medium", required=True, help="UTM medium, for example social.")
@click.option("--campaign", required=True, help="UTM campaign name.")
@click.option("--content", default=None, help="Optional UTM content.")
def utm(base_url: str, source: str, medium: str, campaign: str, content: str | None) -> None:
    """Build a UTM-tagged registration URL."""
    try:
        url = build_utm_url(base_url, source=source, medium=medium, campaign=campaign, content=content)
    except EventValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(url)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
