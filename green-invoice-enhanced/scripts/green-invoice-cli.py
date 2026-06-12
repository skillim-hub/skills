#!/usr/bin/env python3
"""Command line interface for the Green Invoice API.

Install dependencies:

    python -m pip install httpx click

Examples:

    python scripts/green-invoice-cli.py --env sandbox auth verify
    python scripts/green-invoice-cli.py clients list
    python scripts/green-invoice-cli.py docs create payload.json
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import click

from green_invoice_client import GreenInvoiceClient, GreenInvoiceError


def load_json_arg(value: Optional[str]) -> Dict[str, Any]:
    """Load JSON from a string, file path, or stdin marker."""

    if not value:
        return {}
    if value == "-":
        return json.load(sys.stdin)
    path = Path(value)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def output(ctx: click.Context, data: Any, columns: Optional[Sequence[str]] = None) -> None:
    """Print JSON or a small plain-text table."""

    if ctx.obj.get("json"):
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
        return
    if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
        print_table(data["items"], columns=columns)
        return
    if isinstance(data, list):
        print_table(data, columns=columns)
        return
    click.echo(json.dumps(data, ensure_ascii=False, indent=2))


def print_table(rows: Sequence[Mapping[str, Any]], columns: Optional[Sequence[str]] = None) -> None:
    """Print a compact table."""

    if not rows:
        click.echo("No rows")
        return
    if columns is None:
        keys: List[str] = []
        for row in rows:
            for key in row.keys():
                if key not in keys and len(keys) < 8:
                    keys.append(key)
        columns = keys
    widths = {col: max(len(col), *(len(str(row.get(col, ""))) for row in rows)) for col in columns}
    header = "  ".join(col.ljust(widths[col]) for col in columns)
    sep = "  ".join("-" * widths[col] for col in columns)
    click.echo(header)
    click.echo(sep)
    for row in rows:
        click.echo("  ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns))


def make_client(ctx: click.Context) -> GreenInvoiceClient:
    """Build a client from CLI options and environment."""

    return GreenInvoiceClient(
        key_id=ctx.obj.get("key_id") or os.getenv("GREEN_INVOICE_KEY_ID"),
        key_secret=ctx.obj.get("key_secret") or os.getenv("GREEN_INVOICE_KEY_SECRET"),
        token=ctx.obj.get("token") or os.getenv("GREEN_INVOICE_TOKEN"),
        environment=ctx.obj.get("env"),
        base_url=ctx.obj.get("base_url") or os.getenv("GREEN_INVOICE_BASE_URL"),
    )


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--env", type=click.Choice(["production", "sandbox"]), default=lambda: os.getenv("GREEN_INVOICE_ENV", "production"), show_default=True)
@click.option("--base-url", default=None, help="Override base URL.")
@click.option("--key-id", default=None, help="API key id. Defaults to GREEN_INVOICE_KEY_ID.")
@click.option("--key-secret", default=None, help="API key secret. Defaults to GREEN_INVOICE_KEY_SECRET.")
@click.option("--token", default=None, help="Bearer token. Defaults to GREEN_INVOICE_TOKEN.")
@click.option("--json", "as_json", is_flag=True, help="Print JSON output.")
@click.pass_context
def gi(ctx: click.Context, env: str, base_url: Optional[str], key_id: Optional[str], key_secret: Optional[str], token: Optional[str], as_json: bool) -> None:
    """Green Invoice command line interface."""

    ctx.obj = {"env": env, "base_url": base_url, "key_id": key_id, "key_secret": key_secret, "token": token, "json": as_json}


@gi.group()
def auth() -> None:
    """Authentication commands."""


@auth.command("verify")
@click.pass_context
def auth_verify(ctx: click.Context) -> None:
    """Authenticate and print the active user profile."""

    client = make_client(ctx)
    try:
        client.authenticate()
        output(ctx, client.verify_auth())
    finally:
        client.close()


@gi.group()
def clients() -> None:
    """Client commands."""


@clients.command("list")
@click.option("--page", default=0, show_default=True)
@click.option("--page-size", default=25, show_default=True)
@click.option("--name", default=None)
@click.option("--email", default=None)
@click.option("--active/--inactive", default=None)
@click.pass_context
def clients_list(ctx: click.Context, page: int, page_size: int, name: Optional[str], email: Optional[str], active: Optional[bool]) -> None:
    """List or search clients."""

    payload: Dict[str, Any] = {"page": page, "pageSize": page_size}
    if name:
        payload["name"] = name
    if email:
        payload["email"] = email
    if active is not None:
        payload["active"] = active
    client = make_client(ctx)
    try:
        output(ctx, client.search_clients(payload), columns=["id", "name", "taxId", "active"])
    finally:
        client.close()


@clients.command("get")
@click.argument("client_id")
@click.pass_context
def clients_get(ctx: click.Context, client_id: str) -> None:
    """Get one client."""

    client = make_client(ctx)
    try:
        output(ctx, client.get_client(client_id))
    finally:
        client.close()


@clients.command("create")
@click.argument("payload")
@click.pass_context
def clients_create(ctx: click.Context, payload: str) -> None:
    """Create a client from JSON string, file path, or '-'."""

    client = make_client(ctx)
    try:
        output(ctx, client.create_client(load_json_arg(payload)))
    finally:
        client.close()


@clients.command("update")
@click.argument("client_id")
@click.argument("payload")
@click.pass_context
def clients_update(ctx: click.Context, client_id: str, payload: str) -> None:
    """Update a client from JSON string, file path, or '-'."""

    client = make_client(ctx)
    try:
        output(ctx, client.update_client(client_id, load_json_arg(payload)))
    finally:
        client.close()


@gi.group(name="docs")
def docs_group() -> None:
    """Document commands."""


@docs_group.command("create")
@click.argument("payload")
@click.pass_context
def docs_create(ctx: click.Context, payload: str) -> None:
    """Create a document from JSON string, file path, or '-'."""

    client = make_client(ctx)
    try:
        output(ctx, client.create_document(load_json_arg(payload)))
    finally:
        client.close()


@docs_group.command("get")
@click.argument("document_id")
@click.pass_context
def docs_get(ctx: click.Context, document_id: str) -> None:
    """Get one document."""

    client = make_client(ctx)
    try:
        output(ctx, client.get_document(document_id))
    finally:
        client.close()


@docs_group.command("list")
@click.option("--page", default=0, show_default=True)
@click.option("--page-size", default=25, show_default=True)
@click.option("--from-date", default=None)
@click.option("--to-date", default=None)
@click.option("--client-name", default=None)
@click.option("--type", "doc_type", multiple=True, type=int)
@click.pass_context
def docs_list(ctx: click.Context, page: int, page_size: int, from_date: Optional[str], to_date: Optional[str], client_name: Optional[str], doc_type: Sequence[int]) -> None:
    """List or search documents."""

    payload: Dict[str, Any] = {"page": page, "pageSize": page_size}
    if from_date:
        payload["fromDate"] = from_date
    if to_date:
        payload["toDate"] = to_date
    if client_name:
        payload["clientName"] = client_name
    if doc_type:
        payload["type"] = list(doc_type)
    client = make_client(ctx)
    try:
        output(ctx, client.search_documents(payload), columns=["id", "number", "type", "date", "clientName", "total", "currency"])
    finally:
        client.close()


@docs_group.command("email")
@click.argument("document_id")
@click.option("--to", "to_values", multiple=True, help="Recipient email. Can be repeated.")
@click.option("--subject", default=None)
@click.option("--message", default=None)
@click.option("--payload", default=None, help="Optional JSON payload string, file path, or '-'.")
@click.pass_context
def docs_email(ctx: click.Context, document_id: str, to_values: Sequence[str], subject: Optional[str], message: Optional[str], payload: Optional[str]) -> None:
    """Email a document."""

    body = load_json_arg(payload) if payload else {}
    if to_values:
        body["to"] = list(to_values)
    if subject:
        body["subject"] = subject
    if message:
        body["message"] = message
    client = make_client(ctx)
    try:
        output(ctx, client.email_document(document_id, body))
    finally:
        client.close()


@gi.group()
def items() -> None:
    """Catalog item commands."""


@items.command("list")
@click.option("--page", default=0, show_default=True)
@click.option("--page-size", default=25, show_default=True)
@click.option("--description", default=None)
@click.pass_context
def items_list(ctx: click.Context, page: int, page_size: int, description: Optional[str]) -> None:
    """List or search catalog items."""

    payload: Dict[str, Any] = {"page": page, "pageSize": page_size}
    if description:
        payload["description"] = description
    client = make_client(ctx)
    try:
        output(ctx, client.search_items(payload), columns=["id", "catalogNum", "description", "price", "currency", "active"])
    finally:
        client.close()


@items.command("create")
@click.argument("payload")
@click.pass_context
def items_create(ctx: click.Context, payload: str) -> None:
    """Create a catalog item from JSON string, file path, or '-'."""

    client = make_client(ctx)
    try:
        output(ctx, client.create_item(load_json_arg(payload)))
    finally:
        client.close()


@gi.group()
def payments() -> None:
    """Payment commands."""


@payments.command("record")
@click.argument("payload")
@click.pass_context
def payments_record(ctx: click.Context, payload: str) -> None:
    """Record a payment by creating a receipt document.

    Payload keys: client, payment, date, currency, linkedDocumentIds, description, remarks.
    """

    data = load_json_arg(payload)
    client_payload = data["client"]
    payment_payload = data["payment"]
    gi_client = make_client(ctx)
    try:
        result = gi_client.record_payment(
            client=client_payload,
            payment=payment_payload,
            date=data["date"],
            currency=data.get("currency", "ILS"),
            linked_document_ids=data.get("linkedDocumentIds", []),
            description=data.get("description", "Payment receipt"),
            remarks=data.get("remarks", ""),
        )
        output(ctx, result)
    finally:
        gi_client.close()


@gi.group()
def webhooks() -> None:
    """Webhook commands."""


@webhooks.command("list")
@click.pass_context
def webhooks_list(ctx: click.Context) -> None:
    """List webhooks."""

    client = make_client(ctx)
    try:
        output(ctx, client.list_webhooks(), columns=["id", "url", "active"])
    finally:
        client.close()


@webhooks.command("register")
@click.argument("payload")
@click.pass_context
def webhooks_register(ctx: click.Context, payload: str) -> None:
    """Register webhook from JSON string, file path, or '-'."""

    client = make_client(ctx)
    try:
        output(ctx, client.register_webhook(load_json_arg(payload)))
    finally:
        client.close()


@webhooks.command("delete")
@click.argument("webhook_id")
@click.pass_context
def webhooks_delete(ctx: click.Context, webhook_id: str) -> None:
    """Delete a webhook."""

    client = make_client(ctx)
    try:
        output(ctx, client.delete_webhook(webhook_id))
    finally:
        client.close()


@gi.group()
def expenses() -> None:
    """Expense commands."""


@expenses.command("list")
@click.option("--page", default=0, show_default=True)
@click.option("--page-size", default=25, show_default=True)
@click.option("--from-date", default=None)
@click.option("--to-date", default=None)
@click.option("--supplier-name", default=None)
@click.pass_context
def expenses_list(ctx: click.Context, page: int, page_size: int, from_date: Optional[str], to_date: Optional[str], supplier_name: Optional[str]) -> None:
    """List or search expenses."""

    payload: Dict[str, Any] = {"page": page, "pageSize": page_size}
    if from_date:
        payload["fromDate"] = from_date
    if to_date:
        payload["toDate"] = to_date
    if supplier_name:
        payload["supplierName"] = supplier_name
    client = make_client(ctx)
    try:
        output(ctx, client.search_expenses(payload), columns=["id", "date", "description", "amount", "currency"])
    finally:
        client.close()


@expenses.command("create")
@click.argument("payload")
@click.pass_context
def expenses_create(ctx: click.Context, payload: str) -> None:
    """Create an expense from JSON string, file path, or '-'."""

    client = make_client(ctx)
    try:
        output(ctx, client.create_expense(load_json_arg(payload)))
    finally:
        client.close()


def main() -> None:
    """Entry point."""

    try:
        gi()
    except GreenInvoiceError as exc:
        click.echo(json.dumps({"error": str(exc), "status_code": exc.status_code, "response": exc.response}, ensure_ascii=False, indent=2), err=True)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
