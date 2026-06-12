"""Command-line interface for Green Invoice integration tasks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

try:
    from .green_invoice_integration_client import (
        GreenInvoiceClient,
        GreenInvoiceConfig,
        build_simple_document_payload,
        verify_webhook_hmac,
    )
except ImportError:  # pragma: no cover - direct script execution
    from green_invoice_integration_client import (  # type: ignore
        GreenInvoiceClient,
        GreenInvoiceConfig,
        build_simple_document_payload,
        verify_webhook_hmac,
    )

app = typer.Typer(help="Green Invoice API CLI")


def _client(env: str, token: str | None) -> GreenInvoiceClient:
    return GreenInvoiceClient(token=token, config=GreenInvoiceConfig(environment=env))


def _print_json(data: Any) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


@app.command()
def auth(
    key_id: str = typer.Option(..., help="API key id"),
    key_secret: str = typer.Option(..., help="API key secret", hide_input=True),
    env: str = typer.Option("production", help="production or sandbox"),
) -> None:
    """Authenticate and print a bearer token."""
    with _client(env, None) as client:
        token = client.authenticate(key_id, key_secret)
    _print_json({"token": token.token})


@app.command()
def whoami(
    token: str = typer.Option(..., help="Bearer token"),
    env: str = typer.Option("production", help="production or sandbox"),
) -> None:
    """Verify credentials using the current token."""
    with _client(env, token) as client:
        _print_json(client.verify_credentials())


@app.command("create-client")
def create_client(
    token: str = typer.Option(..., help="Bearer token"),
    name: str = typer.Option(..., help="Customer name"),
    email: str = typer.Option(..., help="Customer email"),
    tax_id: str | None = typer.Option(None, help="Israeli tax id or company number"),
    env: str = typer.Option("production", help="production or sandbox"),
) -> None:
    """Create a customer."""
    payload: dict[str, Any] = {"name": name, "emails": [email], "country": "IL"}
    if tax_id:
        payload["taxId"] = tax_id
    with _client(env, token) as client:
        _print_json(client.create_client(payload))


@app.command("search-clients")
def search_clients(
    token: str = typer.Option(..., help="Bearer token"),
    term: str = typer.Option(..., help="Name, email, or tax id"),
    env: str = typer.Option("production", help="production or sandbox"),
) -> None:
    """Search customers."""
    with _client(env, token) as client:
        _print_json(client.search_clients(term))


@app.command("create-document")
def create_document(
    token: str = typer.Option(..., help="Bearer token"),
    document_type: int = typer.Option(..., "--type", help="Document type code, for example 320"),
    client_name: str = typer.Option(..., help="Customer name"),
    client_email: str = typer.Option(..., help="Customer email"),
    description: str = typer.Option(..., help="Line item description"),
    amount: float = typer.Option(..., help="Line item amount in document currency"),
    currency: str = typer.Option("ILS", help="Currency code"),
    date: str | None = typer.Option(None, help="ISO date, for example 2026-06-05"),
    payment_method: str | None = typer.Option(None, help="cash, check, credit-card, wire-transfer, paypal, app, other"),
    tax_included: bool = typer.Option(False, help="Amount already includes VAT"),
    env: str = typer.Option("production", help="production or sandbox"),
) -> None:
    """Create a document from a compact payload."""
    payload = build_simple_document_payload(
        document_type=document_type,
        client_name=client_name,
        client_email=client_email,
        description=description,
        amount=amount,
        currency=currency,
        date=date,
        payment_method=payment_method,
        tax_included=tax_included,
    )
    with _client(env, token) as client:
        _print_json(client.create_document(payload))


@app.command("list-documents")
def list_documents(
    token: str = typer.Option(..., help="Bearer token"),
    from_date: str | None = typer.Option(None, help="Start date YYYY-MM-DD"),
    to_date: str | None = typer.Option(None, help="End date YYYY-MM-DD"),
    document_type: int | None = typer.Option(None, "--type", help="Document type code"),
    env: str = typer.Option("production", help="production or sandbox"),
) -> None:
    """List documents with optional filters."""
    filters: dict[str, Any] = {}
    if from_date:
        filters["fromDate"] = from_date
    if to_date:
        filters["toDate"] = to_date
    if document_type is not None:
        filters["type"] = document_type
    with _client(env, token) as client:
        _print_json(client.list_documents(**filters))


@app.command("get-document")
def get_document(
    token: str = typer.Option(..., help="Bearer token"),
    document_id: str = typer.Option(..., help="Document id"),
    env: str = typer.Option("production", help="production or sandbox"),
) -> None:
    """Fetch one document."""
    with _client(env, token) as client:
        _print_json(client.get_document(document_id))


@app.command("cancel-document")
def cancel_document(
    token: str = typer.Option(..., help="Bearer token"),
    document_id: str = typer.Option(..., help="Document id"),
    reason: str | None = typer.Option(None, help="Cancellation reason"),
    env: str = typer.Option("production", help="production or sandbox"),
) -> None:
    """Call the document cancellation endpoint for accounts that expose it."""
    with _client(env, token) as client:
        _print_json(client.cancel_document(document_id, reason=reason))


@app.command("payment-link")
def payment_link(
    token: str = typer.Option(..., help="Bearer token"),
    amount: float = typer.Option(..., help="Amount"),
    description: str = typer.Option(..., help="Payment description"),
    client_name: str = typer.Option(..., help="Customer name"),
    client_email: str = typer.Option(..., help="Customer email"),
    currency: str = typer.Option("ILS", help="Currency"),
    endpoint: str = typer.Option("/payments/links", help="Account-specific payment-link endpoint"),
    env: str = typer.Option("production", help="production or sandbox"),
) -> None:
    """Create a payment-link request when the account exposes an endpoint."""
    payload = {
        "amount": amount,
        "currency": currency,
        "description": description,
        "client": {"name": client_name, "emails": [client_email], "country": "IL"},
    }
    with _client(env, token) as client:
        _print_json(client.create_payment_link(payload, endpoint=endpoint))


@app.command("webhook-verify")
def webhook_verify(
    secret: str = typer.Option(..., help="Webhook secret", hide_input=True),
    body_file: Path = typer.Option(..., exists=True, readable=True, help="Raw webhook body file"),
    signature: str = typer.Option(..., help="Hex HMAC or sha256=<hex>"),
) -> None:
    """Verify an HMAC-SHA256 webhook signature."""
    valid = verify_webhook_hmac(secret=secret, body=body_file.read_bytes(), signature=signature)
    _print_json({"valid": valid})


if __name__ == "__main__":
    app()
