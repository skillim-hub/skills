"""Command line interface for Hashavshevet integration helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from hashavshevet_integration_client import (
    VAT_RATE_2026,
    btkn_entries_from_records,
    calculate_vat,
    coerce_date,
    format_money,
    generate_btkn_file,
    gross_from_net,
    invoice_allocation_threshold,
    is_plausible_israeli_vat_number,
    load_json_records,
    read_csv_auto,
    read_text_auto,
    requires_allocation_number,
    validate_invoice_payload,
    write_csv_utf8_bom,
)

app = typer.Typer(help="Hashavshevet export/import, VAT, BTKN, and staging utilities.")


@app.command()
def vat(
    net_amount: str = typer.Argument(..., help="Net amount before VAT."),
    invoice_date: str = typer.Option("2026-06-05", "--date", help="Invoice date in YYYY-MM-DD or DD-MM-YYYY."),
    customer_vat: Optional[str] = typer.Option(None, "--customer-vat", help="Customer authorized dealer/company number."),
    document_type: str = typer.Option("tax_invoice", "--document-type", help="tax_invoice, tax_invoice_receipt, receipt, credit_note."),
) -> None:
    """Calculate VAT and allocation-number requirement."""
    date_value = coerce_date(invoice_date)
    payload = {
        "date": date_value.strftime("%d-%m-%Y"),
        "net": format_money(net_amount),
        "vat_rate": format_money(VAT_RATE_2026),
        "vat": format_money(calculate_vat(net_amount)),
        "gross": format_money(gross_from_net(net_amount)),
        "allocation_threshold": format_money(invoice_allocation_threshold(date_value)),
        "allocation_required": requires_allocation_number(
            net_amount,
            date_value,
            document_type=document_type,
            customer_vat_number=customer_vat,
        ),
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("validate-vat-number")
def validate_vat_number(value: str) -> None:
    """Validate the shape of an Israeli VAT/company number."""
    valid = is_plausible_israeli_vat_number(value)
    typer.echo("valid" if valid else "invalid")
    raise typer.Exit(0 if valid else 2)


@app.command("convert-encoding")
def convert_encoding(source: Path, target: Path) -> None:
    """Convert Hebrew text exports to UTF-8."""
    target.write_text(read_text_auto(source), encoding="utf-8")
    typer.echo(str(target))


@app.command("csv-to-json")
def csv_to_json(source: Path, target: Path) -> None:
    """Convert a Hashavshevet CSV export to UTF-8 JSON."""
    target.write_text(json.dumps(read_csv_auto(source), ensure_ascii=False, indent=2), encoding="utf-8")
    typer.echo(str(target))


@app.command("json-to-csv")
def json_to_csv(source: Path, target: Path) -> None:
    """Convert JSON records to UTF-8 BOM CSV for Excel and staging imports."""
    write_csv_utf8_bom(load_json_records(source), target)
    typer.echo(str(target))


@app.command("generate-btkn")
def generate_btkn(source_json: Path, target: Path, encoding: str = typer.Option("windows-1255", "--encoding")) -> None:
    """Generate a deterministic BTKN transfer text file from JSON rows."""
    entries = btkn_entries_from_records(load_json_records(source_json))
    generate_btkn_file(entries, target, encoding=encoding)
    typer.echo(str(target))


@app.command("validate-invoice")
def validate_invoice(source_json: Path) -> None:
    """Validate invoice payload before SHAAM allocation submission."""
    payload = json.loads(source_json.read_text(encoding="utf-8"))
    errors = validate_invoice_payload(payload)
    if errors:
        for error in errors:
            typer.echo(error, err=True)
        raise typer.Exit(2)
    typer.echo("valid")


@app.command("sample-config")
def sample_config(target: Path) -> None:
    """Write a multi-company configuration template."""
    payload = {
        "companies": [
            {
                "company_id": "514087337",
                "name": "Example Ltd",
                "base_url": "https://api.example.local",
                "currency": "ILS",
                "vat_rate": "0.18",
            }
        ],
        "imports": {
            "customers_path": "/accounts",
            "journal_entries_path": "/journal-transactions",
            "invoice_allocation_path": "/Invoices/v1/Approval",
        },
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    typer.echo(str(target))


if __name__ == "__main__":
    app()
