"""Command-line interface for land registry Tabu workflows."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import click

from .client import (
    FileJsonTransport,
    LandRegistryTabuClient,
    ParcelId,
    TabuClientConfig,
    extract_risk_flags,
    normalize_share,
    validate_israeli_id,
)

DEFAULT_ENV_URLS = {
    "sandbox": "https://sandbox.example.internal.gov-adapter.local",
    "production": "https://production.example.internal.gov-adapter.local",
}


def _base_url_for(env_name: str, explicit_base_url: str | None) -> str:
    if explicit_base_url:
        return explicit_base_url
    env_var = "TABU_SANDBOX_BASE_URL" if env_name == "sandbox" else "TABU_PRODUCTION_BASE_URL"
    return os.getenv(env_var, DEFAULT_ENV_URLS[env_name])


def _make_client(ctx: click.Context) -> LandRegistryTabuClient:
    obj = ctx.obj or {}
    mock_file = obj.get("mock_file")
    order_mock_file = obj.get("order_mock_file")
    transport = FileJsonTransport(mock_file, order_mock_file) if mock_file else None
    return LandRegistryTabuClient(
        config=TabuClientConfig(
            base_url=_base_url_for(obj["env_name"], obj.get("base_url")),
            api_key=obj.get("api_key"),
            timeout_seconds=obj["timeout"],
        ),
        transport=transport,
    )


def _echo_json(value: Any) -> None:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    click.echo(json.dumps(value, ensure_ascii=False, indent=2))


def _echo_extract_table(extract: Any) -> None:
    data = extract.to_dict()
    click.echo(f"Property: {data.get('property_id')}")
    click.echo(f"Address: {data.get('address') or '-'}")
    click.echo(f"Retrieved at: {data.get('retrieved_at')}")
    click.echo("")
    click.echo("Rights:")
    for right in data.get("rights", []):
        click.echo(
            f"- {right.get('owner_name')} | {right.get('right_type')} | "
            f"share={right.get('share') or '-'} | id={right.get('id_masked') or '-'}"
        )
        for enc in right.get("encumbrances", []):
            amount = enc.get("amount_ils")
            amount_text = f"₪{amount:,.0f}" if isinstance(amount, (int, float)) else "-"
            click.echo(
                f"  * {enc.get('type')} | beneficiary={enc.get('beneficiary') or '-'} | "
                f"amount={amount_text} | date={enc.get('registered_date') or '-'}"
            )
    warnings = extract_risk_flags(extract)
    if warnings:
        click.echo("")
        click.echo("Warnings:")
        for warning in warnings:
            click.echo(f"- {warning}")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--env", "env_name", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--base-url", default=None, help="Override adapter base URL. Otherwise read TABU_SANDBOX_BASE_URL or TABU_PRODUCTION_BASE_URL.")
@click.option("--api-key", default=lambda: os.getenv("TABU_API_KEY"), help="Bearer token. Defaults to TABU_API_KEY.")
@click.option("--timeout", default=20.0, show_default=True, type=float)
@click.option("--mock-file", type=click.Path(exists=True, dir_okay=False, path_type=str), help="Use local JSON extract fixture.")
@click.option("--order-mock-file", type=click.Path(exists=True, dir_okay=False, path_type=str), help="Use local JSON order fixture.")
@click.pass_context
def cli(
    ctx: click.Context,
    env_name: str,
    base_url: str | None,
    api_key: str | None,
    timeout: float,
    mock_file: str | None,
    order_mock_file: str | None,
) -> None:
    """Retrieve and inspect Israeli Tabu land-registry adapter data."""
    ctx.obj = {
        "env_name": env_name,
        "base_url": base_url,
        "api_key": api_key,
        "timeout": timeout,
        "mock_file": mock_file,
        "order_mock_file": order_mock_file,
    }


@cli.command()
@click.option("--block", required=True, type=int, help="Gush / block.")
@click.option("--parcel", required=True, type=int, help="Helka / parcel.")
@click.option("--subparcel", type=int, default=None, help="Tat-helka / subparcel.")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="json", show_default=True)
@click.pass_context
def parcel(ctx: click.Context, block: int, parcel: int, subparcel: int | None, output_format: str) -> None:
    """Fetch by block, parcel, and optional subparcel."""
    client = _make_client(ctx)
    extract = client.get_by_parcel(ParcelId(block=block, parcel=parcel, subparcel=subparcel))
    if output_format == "json":
        _echo_json(extract)
    else:
        _echo_extract_table(extract)


@cli.command("address")
@click.option("--city", required=True)
@click.option("--street", required=True)
@click.option("--house", required=True)
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="json", show_default=True)
@click.pass_context
def address_lookup(ctx: click.Context, city: str, street: str, house: str, output_format: str) -> None:
    """Fetch by address through the configured adapter."""
    client = _make_client(ctx)
    extract = client.search_by_address(city=city, street=street, house=house)
    if output_format == "json":
        _echo_json(extract)
    else:
        _echo_extract_table(extract)


@cli.command("create-order")
@click.option("--block", required=True, type=int)
@click.option("--parcel", required=True, type=int)
@click.option("--subparcel", type=int, default=None)
@click.option("--purpose", default="purchase_due_diligence", show_default=True)
@click.option("--language", default="he", show_default=True)
@click.option("--payment-reference", default=None)
@click.option("--idempotency-key", default=None)
@click.pass_context
def create_order(
    ctx: click.Context,
    block: int,
    parcel: int,
    subparcel: int | None,
    purpose: str,
    language: str,
    payment_reference: str | None,
    idempotency_key: str | None,
) -> None:
    """Create an extract order for adapters that use an order/payment flow."""
    client = _make_client(ctx)
    order = client.create_extract_order(
        ParcelId(block=block, parcel=parcel, subparcel=subparcel),
        purpose=purpose,
        language=language,
        payment_reference=payment_reference,
        idempotency_key=idempotency_key,
    )
    _echo_json(order)


@cli.command("order-status")
@click.option("--order-id", required=True)
@click.pass_context
def order_status(ctx: click.Context, order_id: str) -> None:
    """Read extract order status."""
    client = _make_client(ctx)
    order = client.get_order_status(order_id)
    _echo_json(order)


@cli.command("validate-id")
@click.argument("identifier")
def validate_id(identifier: str) -> None:
    """Validate a 9-digit Israeli personal ID checksum."""
    click.echo("valid" if validate_israeli_id(identifier) else "invalid")


@cli.command("normalize-share")
@click.argument("share")
def normalize_share_command(share: str) -> None:
    """Normalize a share such as 50%, 0.5, or 1/2."""
    click.echo(normalize_share(share))


@cli.command("sample-template")
def sample_template() -> None:
    """Print a minimal JSON fixture template."""
    payload = {
        "property": {"block": 30001, "parcel": 12, "subparcel": 4, "address": "Example Street 10, Tel Aviv-Yafo"},
        "retrieved_at": "2026-06-04T12:00:00Z",
        "rights": [
            {
                "owner_name": "Dana Cohen",
                "id": "123456782",
                "right_type": "ownership",
                "share": "1/2",
                "deed_date": "2022-02-15",
                "encumbrances": [],
            }
        ],
        "warnings": [],
    }
    _echo_json(payload)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
