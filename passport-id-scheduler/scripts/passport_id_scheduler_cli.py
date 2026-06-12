#!/usr/bin/env python3
"""Command-line interface for the Passport & ID Appointment Scheduler."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

import passport_id_scheduler_client as client

app = typer.Typer(help="Local helper for Israeli passport, Teudat Zehut, biometric document appointment planning.")


def _env_payload(env: str) -> dict[str, object]:
    normalized = env.lower().strip()
    if normalized not in {"sandbox", "production"}:
        raise typer.BadParameter("--env must be sandbox or production")
    prefix = f"PASSPORT_ID_SCHEDULER_{normalized.upper()}_"
    return {
        "environment": normalized,
        "base_url": os.getenv(prefix + "BASE_URL", "https://govisit.gov.il/" if normalized == "production" else "local-sandbox"),
        "api_token_configured": bool(os.getenv(prefix + "API_TOKEN") or os.getenv("PASSPORT_ID_SCHEDULER_API_TOKEN")),
    }


@app.command("validate-id")
def validate_id(id_number: str = typer.Argument(..., help="Israeli Teudat Zehut number")) -> None:
    """Validate a Teudat Zehut number."""
    result = client.validate_teudat_zehut(id_number)
    typer.echo(client.dumps_json(result.to_dict()))
    if not result.valid:
        raise typer.Exit(1)


@app.command("normalize-phone")
def normalize_phone(phone: str = typer.Argument(..., help="Israeli phone number")) -> None:
    """Normalize an Israeli phone number."""
    result = client.validate_israeli_phone(phone)
    typer.echo(client.dumps_json(result.to_dict()))
    if not result.valid:
        raise typer.Exit(1)


@app.command("classify")
def classify(text: str = typer.Argument(..., help="Free-text service description")) -> None:
    """Classify a free-text service description."""
    service = client.classify_service(text)
    typer.echo(client.dumps_json({"service": service.value if service else None}))
    if service is None:
        raise typer.Exit(1)


@app.command("checklist")
def checklist(
    service: str = typer.Option(..., "--service", "-s", help="Service key"),
    minor: bool = typer.Option(False, "--minor", help="Use minor workflow"),
    business: bool = typer.Option(False, "--business", help="Add small-business update notes"),
    lang: str = typer.Option("en", "--lang", help="en or he"),
) -> None:
    """Print a document checklist."""
    items = client.hebrew_checklist(service, minor=minor, business=business) if lang == "he" else client.service_checklist(service, minor=minor, business=business)
    typer.echo(client.dumps_json({"service": client.parse_service(service).value, "items": items}))


@app.command("create-request")
def create_request(
    service: str = typer.Option(..., "--service", "-s", help="Service key"),
    city: Optional[str] = typer.Option(None, "--city", "-c", help="Preferred city"),
    date_from: Optional[str] = typer.Option(None, "--date-from", help="ISO date YYYY-MM-DD"),
    date_to: Optional[str] = typer.Option(None, "--date-to", help="ISO date YYYY-MM-DD"),
    id_number: str = typer.Option("123456782", "--id-number", help="Applicant Teudat Zehut"),
    phone: str = typer.Option("0521234567", "--phone", help="Applicant phone"),
    full_name: str = typer.Option("Applicant", "--full-name", help="Applicant name"),
    minor: bool = typer.Option(False, "--minor", help="Applicant is a minor"),
    business: bool = typer.Option(False, "--business", help="Small-business/freelancer context"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write request record to JSON"),
) -> None:
    """Create a local request record and return an id for later commands."""
    env_data = _env_payload(env)
    request = client.AppointmentRequest(
        service=service,
        applicants=[client.ApplicantProfile(full_name=full_name, teudat_zehut=id_number, phone=phone, is_minor=minor)],
        preference=client.AppointmentPreference(
            preferred_city=city,
            date_from=client.parse_date(date_from),
            date_to=client.parse_date(date_to),
        ),
        business_context="business" if business else None,
    )
    record = client.PassportIdSchedulerClient().create_request_record(request, environment=env_data["environment"])  # type: ignore[arg-type]
    record["runtime"] = env_data
    if output:
        output.write_text(client.dumps_json(record), encoding="utf-8")
        record["written"] = str(output)
    typer.echo(client.dumps_json(record))


@app.command("show-request")
def show_request(
    input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="JSON request record"),
    request_id: str = typer.Option(..., "--request-id", help="Request id returned by create-request"),
) -> None:
    """Load a stored local request record by id."""
    data = json.loads(input.read_text(encoding="utf-8"))
    if data.get("id") != request_id:
        raise typer.BadParameter("request id not found in input file")
    typer.echo(client.dumps_json({"id": data["id"], "environment": data.get("environment"), "request": data.get("request")}))


@app.command("plan")
def plan(
    service: str = typer.Option(..., "--service", "-s", help="Service key"),
    city: Optional[str] = typer.Option(None, "--city", "-c", help="Preferred city"),
    date_from: Optional[str] = typer.Option(None, "--date-from", help="ISO date YYYY-MM-DD"),
    date_to: Optional[str] = typer.Option(None, "--date-to", help="ISO date YYYY-MM-DD"),
    minor: bool = typer.Option(False, "--minor", help="Applicant is a minor"),
    business: bool = typer.Option(False, "--business", help="Small-business/freelancer context"),
    accessibility: bool = typer.Option(False, "--accessibility", help="Accessibility needed"),
    lang: str = typer.Option("en", "--lang", help="en or he"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON instead of markdown"),
) -> None:
    """Build a local appointment preparation plan."""
    applicant = client.ApplicantProfile(full_name="Applicant", teudat_zehut="123456782", phone="0521234567", is_minor=minor)
    preference = client.AppointmentPreference(
        preferred_city=city,
        date_from=client.parse_date(date_from),
        date_to=client.parse_date(date_to),
        accessibility_required=accessibility,
        preferred_language="he" if lang == "he" else "en",
    )
    request = client.AppointmentRequest(
        service=service,
        applicants=[applicant],
        preference=preference,
        business_context="business" if business else None,
    )
    appointment_plan = client.PassportIdSchedulerClient().build_plan(request)
    typer.echo(client.dumps_json(appointment_plan.to_dict()) if json_output else client.plan_to_markdown(appointment_plan, lang="he" if lang == "he" else "en"))


@app.command("rank-slots")
def rank_slots(input: Path = typer.Option(..., "--input", "-i", exists=True, readable=True, help="JSON file with request and slots")) -> None:
    """Rank user-provided official appointment candidates."""
    data = json.loads(input.read_text(encoding="utf-8"))
    request = client.request_from_dict(data.get("request", data))
    candidates = [client.candidate_from_dict(item) for item in data.get("slots", [])]
    ranked = client.PassportIdSchedulerClient().rank_candidates(request, candidates)
    typer.echo(client.dumps_json({"ranked": [item.to_dict() for item in ranked]}))


@app.command("make-ics")
def make_ics(
    title: str = typer.Option(..., "--title", help="Calendar event title"),
    date_value: str = typer.Option(..., "--date", help="ISO date YYYY-MM-DD"),
    time_value: str = typer.Option(..., "--time", help="Time HH:MM"),
    location: str = typer.Option("", "--location", help="Appointment location"),
    description: str = typer.Option("", "--description", help="Event description"),
    output: Path = typer.Option(..., "--output", "-o", help="Output .ics path"),
) -> None:
    """Write a local calendar reminder."""
    client.PassportIdSchedulerClient().write_ics(
        output,
        title,
        client.parse_date(date_value),
        client.parse_time(time_value),
        location=location,
        description=description,
    )
    typer.echo(client.dumps_json({"written": str(output)}))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
