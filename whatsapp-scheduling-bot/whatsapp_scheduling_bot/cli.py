#!/usr/bin/env python3
"""Command-line helper for Hebrew WhatsApp appointment scheduling."""

from __future__ import annotations

import json
import os
from typing import Optional

import typer

from .client import (
    WhatsAppSchedulingClient,
    display_israeli_phone,
    normalize_israeli_phone,
)

app = typer.Typer(help="Hebrew WhatsApp appointment scheduling helper for Israeli businesses.")


def _client(env: str = "sandbox") -> WhatsAppSchedulingClient:
    prefix = "WHATSAPP" if env == "production" else "WHATSAPP_SANDBOX"
    return WhatsAppSchedulingClient(
        access_token=os.getenv(f"{prefix}_ACCESS_TOKEN", os.getenv("WHATSAPP_ACCESS_TOKEN", "")),
        phone_number_id=os.getenv(f"{prefix}_PHONE_ID", os.getenv("WHATSAPP_PHONE_ID", "")),
        api_version=os.getenv("WHATSAPP_API_VERSION", "v25.0"),
        base_url=os.getenv("WHATSAPP_BASE_URL", "https://graph.facebook.com"),
    )


@app.command("validate-phone")
def validate_phone(phone: str) -> None:
    """Normalize an Israeli phone number for WhatsApp Cloud API."""
    try:
        normalized = normalize_israeli_phone(phone)
        display = display_israeli_phone(phone)
    except Exception as exc:
        typer.echo(f"invalid: {exc}")
        raise typer.Exit(code=1)
    typer.echo(json.dumps({"input": phone, "normalized": normalized, "display": display}, ensure_ascii=False, indent=2))


@app.command("confirm")
def confirm(
    to: str = typer.Option(..., help="Customer phone, e.g. 054-123-4567"),
    customer: str = typer.Option(..., help="Customer first name"),
    service: str = typer.Option(..., help="Service name in Hebrew"),
    start: str = typer.Option(..., help="ISO datetime, e.g. 2026-06-18T10:30:00+03:00"),
    duration: int = typer.Option(45, help="Duration in minutes"),
    business: str = typer.Option(os.getenv("BOT_BUSINESS_NAME", "העסק"), help="Business name in Hebrew"),
    price: Optional[float] = typer.Option(None, help="Price in ₪"),
    location: Optional[str] = typer.Option(None, help="Address in Hebrew"),
    template: bool = typer.Option(False, help="Send as approved WhatsApp template"),
    template_name: str = typer.Option("appointment_confirmation_he", help="Template name"),
    dry_run: bool = typer.Option(True, help="Print payload/text without sending"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
) -> None:
    """Create a confirmation message or send it through WhatsApp."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    bot = _client(env)
    appointment = bot.create_appointment(
        customer_name=customer,
        customer_phone=to,
        service_name=service,
        start_at=start,
        duration_minutes=duration,
        business_name=business,
        price_ils=price,
        location=location,
    )
    if dry_run:
        payload = bot.template_payload(to, template_name, bot.build_template_parameters(appointment))
        typer.echo(bot.build_confirmation_text(appointment))
        typer.echo("---")
        typer.echo(json.dumps({"appointment_id": appointment.appointment_id, "payload": payload}, ensure_ascii=False, indent=2))
        return
    result = bot.send_appointment_confirmation(appointment, template_name=template_name, as_template=template, dry_run=False)
    typer.echo(json.dumps(result.raw, ensure_ascii=False, indent=2))


@app.command("reminder-preview")
def reminder_preview(
    to: str = typer.Option(..., help="Customer phone"),
    customer: str = typer.Option(..., help="Customer first name"),
    service: str = typer.Option(..., help="Service name"),
    start: str = typer.Option(..., help="ISO datetime"),
    duration: int = typer.Option(45, help="Duration in minutes"),
    business: str = typer.Option(os.getenv("BOT_BUSINESS_NAME", "העסק"), help="Business name"),
    location: Optional[str] = typer.Option(None, help="Address"),
    offset: int = typer.Option(1440, help="Reminder offset in minutes"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
) -> None:
    """Preview a Hebrew reminder."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    bot = _client(env)
    appointment = bot.create_appointment(customer, to, service, start, duration, business, location=location)
    typer.echo(json.dumps({"appointment_id": appointment.appointment_id, "text": bot.build_reminder_text(appointment, offset)}, ensure_ascii=False, indent=2))


@app.command("webhook-verify")
def webhook_verify(
    mode: str = typer.Option(..., "--mode"),
    token: str = typer.Option(..., "--token"),
    challenge: str = typer.Option(..., "--challenge"),
    expected_token: str = typer.Option(..., "--expected-token"),
) -> None:
    """Check Meta webhook verification behavior."""
    status, body = WhatsAppSchedulingClient.verify_webhook(mode, token, challenge, expected_token)
    typer.echo(json.dumps({"status": status, "body": body}, ensure_ascii=False, indent=2))


@app.command("classify")
def classify(text: str, env: str = typer.Option("sandbox", "--env", help="sandbox or production")) -> None:
    """Classify a customer reply."""
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    bot = _client(env)
    typer.echo(json.dumps({"classification": bot.classify_reply(text)}, ensure_ascii=False, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
