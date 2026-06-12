"""Typer CLI for recurring invoicing workflows."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Optional

import typer

from .client import (
    Customer,
    Interval,
    LineItem,
    RecurringInvoiceError,
    RecurringInvoicingClient,
    Subscription,
    build_invoice,
    clean_israeli_tax_id,
    generate_schedule,
    is_valid_israeli_tax_id,
    should_request_allocation,
    subscription_from_dict,
)

app = typer.Typer(help="Recurring invoicing helper for Israeli VAT and invoice-allocation workflows.")


def echo_json(payload: object) -> None:
    """Print JSON with Israeli text preserved."""
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


@app.command("validate-id")
def validate_id(tax_id: str = typer.Argument(..., help="Israeli 9-digit tax ID, company number, or ID number.")) -> None:
    """Validate and normalize an Israeli tax ID."""
    normalized = clean_israeli_tax_id(tax_id)
    echo_json({"tax_id": normalized, "valid": is_valid_israeli_tax_id(normalized)})


@app.command("next-dates")
def next_dates(
    start: str = typer.Argument(..., help="Start date in YYYY-MM-DD format."),
    count: int = typer.Option(6, "--count", "-c", min=1, max=60, help="Number of dates to print."),
    interval: Interval = typer.Option(Interval.MONTHLY, "--interval", "-i", help="monthly, bimonthly, quarterly, or yearly."),
    end_of_month: bool = typer.Option(True, "--end-of-month/--no-end-of-month", help="Preserve month-end anchor."),
) -> None:
    """Print future issue dates."""
    customer = Customer(name="Example", tax_id="000000018")
    subscription = Subscription(
        subscription_id="preview",
        customer=customer,
        line_items=[LineItem(description="Preview", quantity="1", unit_price="1")],
        start_date=date.fromisoformat(start),
        interval=interval,
        end_of_month=end_of_month,
    )
    echo_json([{"iso": item.isoformat(), "display": item.strftime("%d/%m/%Y")} for item in generate_schedule(subscription, count=count)])


@app.command("create-subscription")
def create_subscription(
    subscription_id: str = typer.Option(..., "--subscription-id"),
    customer_name: str = typer.Option(..., "--customer-name"),
    customer_tax_id: str = typer.Option(..., "--customer-tax-id"),
    description: str = typer.Option(..., "--description"),
    unit_price: Decimal = typer.Option(..., "--unit-price"),
    start: str = typer.Option(..., "--start", help="YYYY-MM-DD"),
    quantity: Decimal = typer.Option(Decimal("1"), "--quantity"),
    interval: Interval = typer.Option(Interval.MONTHLY, "--interval"),
) -> None:
    """Create and print a subscription payload."""
    subscription = Subscription(
        subscription_id=subscription_id,
        customer=Customer(name=customer_name, tax_id=customer_tax_id),
        line_items=[LineItem(description=description, quantity=quantity, unit_price=unit_price)],
        start_date=date.fromisoformat(start),
        interval=interval,
    )
    client = RecurringInvoicingClient(business_tax_id="000000018")
    echo_json(client.create_subscription(subscription))


@app.command("invoice")
def invoice(
    subscription_file: Path = typer.Argument(..., exists=True, readable=True),
    issue_date: str = typer.Option(..., "--issue-date", help="YYYY-MM-DD"),
    sequence: int = typer.Option(1, "--sequence", min=1),
) -> None:
    """Build an invoice from a subscription JSON file."""
    payload = json.loads(subscription_file.read_text(encoding="utf-8"))
    subscription = subscription_from_dict(payload)
    echo_json(build_invoice(subscription, date.fromisoformat(issue_date), sequence).to_dict())


@app.command("allocation-required")
def allocation_required(
    invoice_file: Path = typer.Argument(..., exists=True, readable=True),
    business_tax_id: str = typer.Option(..., "--business-tax-id"),
) -> None:
    """Check whether an invoice requires an allocation request."""
    from .client import invoice_from_dict

    invoice_payload = json.loads(invoice_file.read_text(encoding="utf-8"))
    invoice_document = invoice_from_dict(invoice_payload)
    echo_json({"required": should_request_allocation(invoice_document, business_tax_id)})


def main() -> None:
    """Run the CLI app."""
    app()


if __name__ == "__main__":
    main()
