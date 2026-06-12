#!/usr/bin/env python3
"""Command-line interface for Israeli card-payment receipt generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click

from credit_card_receipt_generator_client import (
    CreditCardReceiptClient,
    Gateway,
    ReceiptFormat,
    ReceiptValidationError,
    provider_endpoint,
    read_json,
    sample_payload,
    write_text,
)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Generate receipt drafts from Israeli credit-card gateway data."""


@main.command("from-json")
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--gateway", type=click.Choice([g.value for g in Gateway]), required=True)
@click.option("--business-name", required=True)
@click.option("--business-tax-id", required=True)
@click.option("--customer-name", default="Customer", show_default=True)
@click.option("--receipt-number", default="")
@click.option("--date", "payment_date", default="", help="Payment date as DD-MM-YYYY. Defaults to current UTC date.")
@click.option("--format", "output_format", type=click.Choice([f.value for f in ReceiptFormat]), default="markdown", show_default=True)
@click.option("--output", "output_path", type=click.Path(dir_okay=False, path_type=Path))
@click.option("--exempt-dealer", is_flag=True, help="Generate Osek Patur receipt without VAT charge.")
@click.option("--allocation-number", default="")
@click.option("--description", default="Card payment", show_default=True)
def from_json(
    input_path: Path,
    gateway: str,
    business_name: str,
    business_tax_id: str,
    customer_name: str,
    receipt_number: str,
    payment_date: str,
    output_format: str,
    output_path: Path | None,
    exempt_dealer: bool,
    allocation_number: str,
    description: str,
) -> None:
    """Create a receipt from a gateway JSON export."""
    client = CreditCardReceiptClient()
    payload = read_json(input_path)
    parsed_date = _parse_date(payment_date)
    try:
        text = client.create_receipt_from_gateway(
            gateway,
            payload,
            business_name=business_name,
            business_tax_id=business_tax_id,
            customer_name=customer_name,
            receipt_number=receipt_number,
            payment_date=parsed_date,
            exempt_dealer=exempt_dealer,
            allocation_number=allocation_number,
            description=description,
            output_format=output_format,
        )
    except ReceiptValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    if output_path:
        write_text(output_path, text)
        click.echo(str(output_path))
    else:
        click.echo(text, nl=False)


@main.command("validate")
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--gateway", type=click.Choice([g.value for g in Gateway]), required=True)
def validate(input_path: Path, gateway: str) -> None:
    """Validate and summarize a gateway JSON export."""
    client = CreditCardReceiptClient()
    payload = read_json(input_path)
    try:
        result = client.normalize(gateway, payload)
    except ReceiptValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"gateway={result.gateway.value}")
    click.echo(f"success={str(result.success).lower()}")
    click.echo(f"transaction_id={result.transaction_id}")
    click.echo(f"amount={result.amount or ''}")
    for warning in result.warnings:
        click.echo(f"warning={warning}")


@main.command("endpoint")
@click.argument("gateway", type=click.Choice([g.value for g in Gateway]))
@click.argument("action")
def endpoint(gateway: str, action: str) -> None:
    """Show a provider endpoint reference."""
    try:
        spec = provider_endpoint(gateway, action)
    except ReceiptValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"{spec['method']} {spec['url']}")
    click.echo(spec["purpose"])


@main.command("sample")
@click.option("--gateway", type=click.Choice([g.value for g in Gateway]), default="cardcom", show_default=True)
@click.option("--format", "output_format", type=click.Choice([f.value for f in ReceiptFormat]), default="markdown", show_default=True)
@click.option("--exempt-dealer", is_flag=True)
def sample(gateway: str, output_format: str, exempt_dealer: bool) -> None:
    """Print a sample generated receipt."""
    client = CreditCardReceiptClient()
    payload = sample_payload(gateway)
    text = client.create_receipt_from_gateway(
        gateway,
        payload,
        business_name="Sample Business",
        business_tax_id="515123453",
        customer_name="Sample Customer",
        receipt_number="RCPT-SAMPLE-1",
        payment_date=datetime.now(timezone.utc).date(),
        exempt_dealer=exempt_dealer,
        output_format=output_format,
    )
    click.echo(text, nl=False)


def _parse_date(value: str):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d-%m-%Y").date()
    except ValueError as exc:
        raise click.ClickException("date must use DD-MM-YYYY") from exc


if __name__ == "__main__":
    main()
