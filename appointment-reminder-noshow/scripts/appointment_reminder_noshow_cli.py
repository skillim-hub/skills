"""Command-line interface for appointment reminders and no-show tracking."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import click

try:
    from appointment_reminder_noshow_client import (
        Appointment,
        AppointmentReminderClient,
        AppointmentStatus,
        Channel,
        Customer,
        NoShowTracker,
        Provider,
        ReminderMessage,
        ReminderPolicy,
        appointment_from_dict,
        normalize_israeli_mobile,
        parse_datetime,
    )
except ImportError:  # pragma: no cover - supports package-style execution
    from scripts.appointment_reminder_noshow_client import (  # type: ignore
        Appointment,
        AppointmentReminderClient,
        AppointmentStatus,
        Channel,
        Customer,
        NoShowTracker,
        Provider,
        ReminderMessage,
        ReminderPolicy,
        appointment_from_dict,
        normalize_israeli_mobile,
        parse_datetime,
    )


def _json_dump(value: Any) -> None:
    click.echo(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _policy(hours_before: str) -> ReminderPolicy:
    hours = tuple(int(part.strip()) for part in hours_before.split(",") if part.strip())
    return ReminderPolicy(hours_before=hours or (48, 24, 3))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Plan reminders, render messages, send provider requests, and track no-shows."""


@cli.command("validate-phone")
@click.argument("phone")
def validate_phone(phone: str) -> None:
    """Normalize an Israeli mobile phone to E.164."""

    click.echo(normalize_israeli_mobile(phone))


@cli.command("message")
@click.option("--customer-id", default="customer-1", show_default=True)
@click.option("--appointment-id", default="appointment-1", show_default=True)
@click.option("--name", required=True)
@click.option("--phone", required=True)
@click.option("--starts-at", required=True, help="ISO datetime, for example 2026-06-18T15:30:00+03:00")
@click.option("--business-name", required=True)
@click.option("--service-name", default="appointment", show_default=True)
@click.option("--location", default="", show_default=True)
@click.option("--language", type=click.Choice(["he", "en"]), default="he", show_default=True)
@click.option("--channel", type=click.Choice(["whatsapp", "sms"]), default=None)
@click.option("--consent-whatsapp/--no-consent-whatsapp", default=True, show_default=True)
@click.option("--consent-sms/--no-consent-sms", default=True, show_default=True)
def message_command(
    customer_id: str,
    appointment_id: str,
    name: str,
    phone: str,
    starts_at: str,
    business_name: str,
    service_name: str,
    location: str,
    language: str,
    channel: str | None,
    consent_whatsapp: bool,
    consent_sms: bool,
) -> None:
    """Render one reminder message as JSON."""

    customer = Customer(
        id=customer_id,
        name=name,
        phone_e164=normalize_israeli_mobile(phone),
        preferred_language=language,
        consent_whatsapp=consent_whatsapp,
        consent_sms=consent_sms,
    )
    appointment = Appointment(
        id=appointment_id,
        customer=customer,
        starts_at=parse_datetime(starts_at),
        business_name=business_name,
        service_name=service_name,
        location=location,
    )
    client = AppointmentReminderClient()
    chosen_channel = Channel(channel) if channel else client.choose_channel(customer)
    rendered = ReminderMessage(
        appointment_id=appointment.id,
        customer_id=customer.id,
        channel=chosen_channel,
        send_at=appointment.starts_at,
        body=client.render_reminder(appointment, chosen_channel),
        metadata={"phone_e164": customer.phone_e164, "language": language, "template_type": "utility"},
    )
    _json_dump(rendered.to_dict())


@cli.command("plan")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--now", default=None, help="ISO datetime for deterministic planning")
@click.option("--hours-before", default="48,24,3", show_default=True)
def plan_command(input_path: Path, now: str | None, hours_before: str) -> None:
    """Plan reminders for appointments from a JSON file."""

    data = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise click.ClickException("input JSON must be a list of appointment objects")
    appointments = [appointment_from_dict(item) for item in data]
    client = AppointmentReminderClient(policy=_policy(hours_before))
    planned = client.plan_reminders(appointments, now=parse_datetime(now) if now else None)
    _json_dump([item.to_dict() for item in planned])


@cli.command("send")
@click.option("--message-json", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--provider", type=click.Choice([item.value for item in Provider]), default="mock", show_default=True)
def send_command(message_json: Path, provider: str) -> None:
    """Send a rendered message through the selected provider."""

    payload = json.loads(message_json.read_text(encoding="utf-8"))
    message = ReminderMessage(
        appointment_id=payload["appointment_id"],
        customer_id=payload["customer_id"],
        channel=Channel(payload["channel"]),
        send_at=parse_datetime(payload["send_at"]),
        body=payload["body"],
        metadata=payload.get("metadata", {}),
    )
    credentials = {
        "account_sid": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "from": os.getenv("TWILIO_FROM", ""),
        "messaging_service_sid": os.getenv("TWILIO_MESSAGING_SERVICE_SID", ""),
        "status_callback": os.getenv("STATUS_CALLBACK_URL", ""),
        "token": os.getenv("WHATSAPP_TOKEN", ""),
        "phone_number_id": os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        "version": os.getenv("WHATSAPP_GRAPH_VERSION", "v20.0"),
        "webhook_url": os.getenv("GENERIC_WEBHOOK_URL", ""),
        "webhook_token": os.getenv("GENERIC_WEBHOOK_TOKEN", ""),
    }
    client = AppointmentReminderClient(provider=provider, credentials={key: value for key, value in credentials.items() if value})
    response = client.send_message(message)
    _json_dump(response.__dict__)


@cli.command("stats")
@click.option("--events", "events_path", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
def stats_command(events_path: Path) -> None:
    """Calculate no-show stats from event JSON."""

    data = json.loads(events_path.read_text(encoding="utf-8"))
    tracker = NoShowTracker()
    for event in data:
        tracker.record(event["appointment_id"], event["customer_id"], AppointmentStatus(event["status"]), parse_datetime(event["occurred_at"]))
    _json_dump(tracker.stats())


@cli.command("suggest-rebooking")
@click.option("--missed-start", required=True, help="ISO datetime of missed appointment")
@click.option("--count", default=3, show_default=True)
def suggest_rebooking_command(missed_start: str, count: int) -> None:
    """Suggest re-booking slots after a missed appointment."""

    tracker = NoShowTracker()
    slots = tracker.suggest_rebooking_slots(parse_datetime(missed_start), count=count)
    _json_dump([slot.isoformat() for slot in slots])


if __name__ == "__main__":
    cli()
