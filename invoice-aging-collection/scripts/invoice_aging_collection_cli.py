"""Typer CLI for invoice aging and Hebrew collection reminders."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

import invoice_aging_collection_client as client_mod


app = typer.Typer(
    help="Track unpaid invoices, calculate aging, and generate Hebrew collection reminders."
)


def _print_json(payload) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("sample-data")
def sample_data(
    out: Path = typer.Option(..., "--out", "-o", help="Output JSON ledger path."),
) -> None:
    """Write a runnable sample ledger."""
    client_mod.save_ledger(out, client_mod.sample_ledger())
    typer.echo(f"Wrote {out}")


@app.command("validate")
def validate(
    ledger: Path = typer.Argument(..., help="Ledger JSON file."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Validate a ledger."""
    client = client_mod.InvoiceAgingClient.from_file(ledger)
    issues = client_mod.issues_to_dicts(client.validate())
    if json_output:
        _print_json({"issues": issues, "issue_count": len(issues)})
        return
    if not issues:
        typer.echo("Validation passed")
        return
    for issue in issues:
        typer.echo(f"{issue['severity'].upper()} {issue['code']}: {issue['message']}")
    raise typer.Exit(code=1 if any(i["severity"] == "error" for i in issues) else 0)


@app.command("create-invoice")
def create_invoice(
    ledger: Path = typer.Argument(..., help="Ledger JSON file to read."),
    client_id: str = typer.Option(..., "--client-id", help="Existing client ID."),
    issue_date: str = typer.Option(..., "--issue-date", help="Issue date, DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD."),
    amount: str = typer.Option(..., "--amount", help="Invoice amount before partial payments."),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Output ledger path. Defaults to overwriting the input ledger."),
    invoice_id: Optional[str] = typer.Option(None, "--invoice-id", help="Optional invoice ID. Generated when omitted."),
    due_date: Optional[str] = typer.Option(None, "--due-date", help="Optional explicit due date."),
    payment_terms_days: Optional[int] = typer.Option(None, "--payment-terms-days", help="Optional payment terms in days."),
    currency: str = typer.Option("ILS", "--currency", help="Currency code. ILS is supported by default."),
    json_output: bool = typer.Option(True, "--json/--text", help="Print JSON or a text confirmation."),
) -> None:
    """Append a new invoice to a ledger and return the created invoice ID."""
    data = client_mod.load_ledger(ledger)
    existing_ids = [item.get("invoice_id", "") for item in data.get("invoices", [])]
    invoice = client_mod.create_invoice_record(
        client_id=client_id,
        issue_date=issue_date,
        due_date=due_date,
        amount=amount,
        invoice_id=invoice_id,
        currency=currency,
        payment_terms_days=payment_terms_days,
        existing_invoice_ids=existing_ids,
    )
    data.setdefault("invoices", []).append(invoice)
    output_path = out or ledger
    client_mod.save_ledger(output_path, data)
    response = {"invoice": invoice, "invoice_id": invoice["invoice_id"], "ledger_path": str(output_path)}
    if json_output:
        _print_json(response)
    else:
        typer.echo(f"Created invoice {invoice['invoice_id']} in {output_path}")


@app.command("age")
def age(
    ledger: Path = typer.Argument(..., help="Ledger JSON file."),
    as_of: str = typer.Option(..., "--as-of", help="As-of date, DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD."),
    json_output: bool = typer.Option(True, "--json/--table", help="Print JSON or table-like output."),
) -> None:
    """Print an aging report."""
    client = client_mod.InvoiceAgingClient.from_file(ledger)
    report = client.aging_report(as_of)
    if json_output:
        _print_json(report)
        return
    typer.echo(f"As of {report['as_of']}")
    for row in report["invoices"]:
        typer.echo(
            f"{row['invoice_id']} | {row['client_name']} | {row['bucket']} | "
            f"{row['outstanding_amount']} | due {row['due_date']}"
        )


@app.command("reminders")
def reminders(
    ledger: Path = typer.Argument(..., help="Ledger JSON file."),
    as_of: str = typer.Option(..., "--as-of", help="As-of date, DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD."),
    channel: Optional[str] = typer.Option(None, "--channel", help="whatsapp, email, or registered_mail."),
    dry_run: bool = typer.Option(True, "--dry-run/--live", help="Generate dry-run reminders by default."),
    json_output: bool = typer.Option(True, "--json/--text", help="Print JSON or message text."),
) -> None:
    """Generate reminders due on the as-of date."""
    client = client_mod.InvoiceAgingClient.from_file(ledger)
    payloads = [r.to_payload() for r in client.reminders_due(as_of, channel=channel, dry_run=dry_run)]
    if json_output:
        _print_json({"reminders": payloads, "count": len(payloads)})
        return
    for reminder in payloads:
        typer.echo("=" * 72)
        typer.echo(f"{reminder['invoice_id']} | {reminder['stage']} | {reminder['channel']}")
        if reminder["subject"]:
            typer.echo(f"Subject: {reminder['subject']}")
        typer.echo(reminder["body"])


@app.command("render")
def render(
    ledger: Path = typer.Argument(..., help="Ledger JSON file."),
    invoice_id: str = typer.Option(..., "--invoice-id", help="Invoice ID."),
    stage: str = typer.Option(..., "--stage", help="Reminder stage."),
    as_of: str = typer.Option("today", "--as-of", help="As-of date or 'today'."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON payload."),
) -> None:
    """Render one reminder for one invoice."""
    if as_of == "today":
        from datetime import date
        as_of = date.today().strftime("%d/%m/%Y")
    client = client_mod.InvoiceAgingClient.from_file(ledger)
    reminder = client.render_for_invoice(invoice_id, stage, as_of)
    payload = reminder.to_payload()
    if json_output:
        _print_json(payload)
        return
    if payload["subject"]:
        typer.echo(f"Subject: {payload['subject']}")
    typer.echo(payload["body"])


@app.command("dispatch")
def dispatch(
    ledger: Path = typer.Argument(..., help="Ledger JSON file."),
    as_of: str = typer.Option(..., "--as-of", help="As-of date, DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD."),
    channel: Optional[str] = typer.Option(None, "--channel", help="Optional channel filter."),
    dry_run: bool = typer.Option(True, "--dry-run/--live", help="Dry-run by default."),
    approve_formal: bool = typer.Option(False, "--approve-formal", help="Allow non-dry-run formal/legal stages."),
) -> None:
    """Dispatch due reminders through the dry-run transport or a configured replacement transport."""
    client = client_mod.InvoiceAgingClient.from_file(ledger)
    results = client.send_due(
        as_of,
        channel=channel,
        dry_run=dry_run,
        require_approval=not approve_formal,
    )
    _print_json({"results": results, "count": len(results)})


@app.command("import-csv")
def import_csv_cmd(
    csv_path: Path = typer.Argument(..., help="CSV export path."),
    out: Path = typer.Option(..., "--out", "-o", help="Output ledger JSON path."),
) -> None:
    """Convert a CSV export into the JSON ledger format."""
    ledger = client_mod.import_csv(csv_path)
    client_mod.save_ledger(out, ledger)
    typer.echo(f"Wrote {out}")


@app.command("evidence")
def evidence(
    ledger: Path = typer.Argument(..., help="Ledger JSON file."),
    client_id: str = typer.Option(..., "--client-id", help="Client ID."),
    as_of: str = typer.Option(..., "--as-of", help="As-of date."),
    out: Optional[Path] = typer.Option(None, "--out", help="Optional output JSON path."),
) -> None:
    """Build a collection evidence checklist for one client."""
    client = client_mod.InvoiceAgingClient.from_file(ledger)
    pack = client.evidence_pack(client_id, as_of)
    if out:
        client_mod.save_ledger(out, pack)
        typer.echo(f"Wrote {out}")
    else:
        _print_json(pack)


@app.command("client-summary")
def client_summary(
    ledger: Path = typer.Argument(..., help="Ledger JSON file."),
    as_of: str = typer.Option(..., "--as-of", help="As-of date."),
) -> None:
    """Print outstanding balance summarized by client."""
    client = client_mod.InvoiceAgingClient.from_file(ledger)
    _print_json({"clients": client.client_summary(as_of)})


def main() -> None:
    app()


if __name__ == "__main__":
    main()
