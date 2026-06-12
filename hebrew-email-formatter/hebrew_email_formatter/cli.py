"""Command line interface for Hebrew Email Formatter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import (
    Contact,
    DraftStore,
    EmailRequest,
    HebrewEmailError,
    HebrewEmailFormatterClient,
    Sender,
    format_date_il,
    format_ils,
    parse_environment,
    parse_formality,
    parse_gender,
    parse_purpose,
)


app = typer.Typer(help="Compose professional Hebrew email drafts with Israeli localization.")


def make_request(
    purpose: str,
    recipient: str,
    recipient_gender: str,
    sender: str,
    sender_gender: str,
    formality: str,
    amount: str,
    invoice_number: str,
    invoice_date: str,
    due_date: str,
    payment_terms: str,
    service: str,
    topic: str,
    valid_until: str,
    vat_status: str,
    requested_action_date: str,
    phone: str,
    email: str,
    env_name: str,
) -> EmailRequest:
    facts = {
        key: value
        for key, value in {
            "amount": amount,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "due_date": due_date,
            "payment_terms": payment_terms,
            "service": service,
            "topic": topic,
            "valid_until": valid_until,
            "vat_status": vat_status,
            "requested_action_date": requested_action_date,
        }.items()
        if value
    }
    return EmailRequest(
        purpose=parse_purpose(purpose),
        formality=parse_formality(formality),
        recipient=Contact(name=recipient, gender=parse_gender(recipient_gender)),
        sender=Sender(name=sender, gender=parse_gender(sender_gender), phone=phone, email=email),
        facts=facts,
        environment=parse_environment(env_name),
    )


@app.command()
def amount(
    value: str = typer.Argument(..., help="Amount to format."),
    agorot: bool = typer.Option(False, "--agorot", help="Keep two decimal places."),
) -> None:
    """Format an amount as Israeli shekels."""
    typer.echo(format_ils(value, include_agorot=agorot))


@app.command()
def date(value: str = typer.Argument(..., help="Date in DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD.")) -> None:
    """Normalize a date to DD/MM/YYYY."""
    typer.echo(format_date_il(value))


@app.command()
def compose(
    purpose: str = typer.Option(...),
    recipient: str = typer.Option(""),
    recipient_gender: str = typer.Option("neutral"),
    sender: str = typer.Option(""),
    sender_gender: str = typer.Option("neutral"),
    formality: str = typer.Option("neutral"),
    amount: str = typer.Option(""),
    invoice_number: str = typer.Option(""),
    invoice_date: str = typer.Option(""),
    due_date: str = typer.Option(""),
    payment_terms: str = typer.Option(""),
    service: str = typer.Option(""),
    topic: str = typer.Option(""),
    valid_until: str = typer.Option(""),
    vat_status: str = typer.Option(""),
    requested_action_date: str = typer.Option(""),
    phone: str = typer.Option(""),
    email: str = typer.Option(""),
    env_name: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON response."),
) -> None:
    """Compose a draft without saving it."""
    request = make_request(
        purpose, recipient, recipient_gender, sender, sender_gender, formality, amount, invoice_number,
        invoice_date, due_date, payment_terms, service, topic, valid_until, vat_status,
        requested_action_date, phone, email, env_name
    )
    draft = HebrewEmailFormatterClient().compose(request)
    typer.echo(draft.to_json() if json_output else draft.render())


@app.command()
def create(
    purpose: str = typer.Option(...),
    recipient: str = typer.Option(""),
    recipient_gender: str = typer.Option("neutral"),
    sender: str = typer.Option(""),
    sender_gender: str = typer.Option("neutral"),
    formality: str = typer.Option("neutral"),
    amount: str = typer.Option(""),
    invoice_number: str = typer.Option(""),
    invoice_date: str = typer.Option(""),
    due_date: str = typer.Option(""),
    payment_terms: str = typer.Option(""),
    service: str = typer.Option(""),
    topic: str = typer.Option(""),
    valid_until: str = typer.Option(""),
    vat_status: str = typer.Option(""),
    requested_action_date: str = typer.Option(""),
    phone: str = typer.Option(""),
    email: str = typer.Option(""),
    env_name: str = typer.Option("sandbox", "--env", help="sandbox or production."),
    json_output: bool = typer.Option(True, "--json/--text", help="Print JSON response by default."),
) -> None:
    """Create a local draft and print its identifier."""
    request = make_request(
        purpose, recipient, recipient_gender, sender, sender_gender, formality, amount, invoice_number,
        invoice_date, due_date, payment_terms, service, topic, valid_until, vat_status,
        requested_action_date, phone, email, env_name
    )
    draft = HebrewEmailFormatterClient().compose(request)
    DraftStore().save(draft)
    typer.echo(draft.to_json() if json_output else draft.render())


@app.command()
def show(
    draft_id: str = typer.Argument(..., help="Draft id returned by create."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON response."),
) -> None:
    """Show a saved local draft by id."""
    draft = DraftStore().load(draft_id)
    typer.echo(draft.to_json() if json_output else draft.render())


@app.command()
def from_json(
    path: Path = typer.Argument(..., exists=True, readable=True, help="Path to JSON request file."),
    env_name: Optional[str] = typer.Option(None, "--env", help="Override request environment."),
    save: bool = typer.Option(False, "--save", help="Save and return a reusable draft id."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON response."),
) -> None:
    """Compose a draft from a JSON request file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if env_name:
        data["environment"] = parse_environment(env_name)
    draft = HebrewEmailFormatterClient().compose(data)
    if save:
        DraftStore().save(draft)
    typer.echo(draft.to_json() if json_output or save else draft.render())


def main() -> None:
    try:
        app()
    except HebrewEmailError as exc:
        typer.echo(f"שגיאה: {exc}", err=True)
        raise typer.Exit(2) from exc


if __name__ == "__main__":
    main()
