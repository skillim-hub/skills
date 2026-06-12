"""CLI for creating and reviewing privacy-safe Israeli HMO appointment booking plans."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import typer

from healthcare_appointment_booker_client import (
    AgeGroup,
    HealthcareAppointmentBookerClient,
    build_request,
    contains_sensitive_secret,
    has_emergency_red_flags,
    normalize_enum,
    classify_specialty,
    render_text_plan,
)

app = typer.Typer(
    name="healthcare-appointment-booker",
    help="Create privacy-safe Israeli HMO appointment booking plans through official-channel workflows.",
    no_args_is_help=True,
)


def _default_store() -> Path:
    return Path.home() / ".healthcare_appointment_booker" / "plans.json"


def _read_store(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_store(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _plan_id(plan_dict: dict[str, Any]) -> str:
    payload = json.dumps(plan_dict, ensure_ascii=False, sort_keys=True)
    return "plan_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _build_plan(
    hmo: str,
    service: str,
    city: str,
    date_from: str,
    date_to: str,
    age_group: str,
    urgency: str,
    referral_status: str,
    language: str,
    accessibility: list[str] | None,
    time_preference: list[str] | None,
    notes: str,
):
    request = build_request(
        hmo=hmo,
        service=service,
        city=city,
        date_from=date_from,
        date_to=date_to,
        age_group=age_group,
        urgency=urgency,
        referral_status=referral_status,
        language=language,
        accessibility=tuple(accessibility or ()),
        time_preferences=tuple(time_preference or ()),
        notes=notes,
    )
    return HealthcareAppointmentBookerClient().plan(request)


@app.command()
def create(
    hmo: str = typer.Option(..., help="clalit, maccabi, meuhedet, leumit"),
    service: str = typer.Option(..., help="Requested service or appointment goal"),
    city: str = typer.Option(..., help="Preferred city or area"),
    date_from: str = typer.Option(..., help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY"),
    date_to: str = typer.Option(..., help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY"),
    age_group: str = typer.Option("adult", help="adult, child, infant, senior"),
    urgency: str = typer.Option("routine", help="routine, soon, same_day, urgent_symptoms"),
    referral_status: str = typer.Option("unknown", help="has_referral, no_referral, pending, unknown, not_applicable"),
    language: str = typer.Option("he", help="Preferred output/service language"),
    accessibility: list[str] | None = typer.Option(None, help="Accessibility requirement; repeat as needed"),
    time_preference: list[str] | None = typer.Option(None, help="Time preference; repeat as needed"),
    notes: str = typer.Option("", help="Optional non-sensitive notes"),
    store: Path | None = typer.Option(None, help="Plan store path; defaults to a user-local JSON file"),
) -> None:
    """Create a booking plan, persist it locally, and print a response containing an id."""
    store_path = store or _default_store()
    plan = _build_plan(
        hmo, service, city, date_from, date_to, age_group, urgency,
        referral_status, language, accessibility, time_preference, notes
    )
    plan_dict = plan.to_dict()
    plan_id = _plan_id(plan_dict)
    data = _read_store(store_path)
    data[plan_id] = plan_dict
    _write_store(store_path, data)
    typer.echo(json.dumps({"id": plan_id, "plan": plan_dict}, ensure_ascii=False, indent=2))


@app.command()
def show(
    id: str = typer.Option(..., "--id", help="Plan id returned by create"),
    store: Path | None = typer.Option(None, help="Plan store path; defaults to a user-local JSON file"),
    format: str = typer.Option("json", "--format", "-f", help="json or text"),
    language: str = typer.Option("en", help="Use he for Hebrew text output"),
) -> None:
    """Show a previously created plan by id."""
    data = _read_store(store or _default_store())
    if id not in data:
        raise typer.BadParameter("plan id not found in the selected store")
    plan_dict = data[id]
    if format == "json":
        typer.echo(json.dumps({"id": id, "plan": plan_dict}, ensure_ascii=False, indent=2))
        return
    if format != "text":
        raise typer.BadParameter("format must be json or text")
    req = plan_dict
    plan = _build_plan(
        req["hmo"], req["service"], req["city"], req["date_from"], req["date_to"],
        req.get("age_group", "adult"), req.get("urgency", "routine"),
        req.get("referral_status", "unknown"), language, [], [], ""
    )
    typer.echo(render_text_plan(plan, hebrew=language.lower().startswith("he")))


@app.command()
def plan(
    hmo: str = typer.Option(..., help="clalit, maccabi, meuhedet, leumit"),
    service: str = typer.Option(..., help="Requested service or appointment goal"),
    city: str = typer.Option(..., help="Preferred city or area"),
    date_from: str = typer.Option(..., help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY"),
    date_to: str = typer.Option(..., help="YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY"),
    age_group: str = typer.Option("adult", help="adult, child, infant, senior"),
    urgency: str = typer.Option("routine", help="routine, soon, same_day, urgent_symptoms"),
    referral_status: str = typer.Option("unknown", help="has_referral, no_referral, pending, unknown, not_applicable"),
    language: str = typer.Option("he", help="Preferred output/service language"),
    accessibility: list[str] | None = typer.Option(None, help="Accessibility requirement; repeat as needed"),
    time_preference: list[str] | None = typer.Option(None, help="Time preference; repeat as needed"),
    notes: str = typer.Option("", help="Optional non-sensitive notes"),
    format: str = typer.Option("json", "--format", "-f", help="json or text"),
) -> None:
    """Print a booking plan without storing it."""
    plan_obj = _build_plan(
        hmo, service, city, date_from, date_to, age_group, urgency,
        referral_status, language, accessibility, time_preference, notes
    )
    if format == "json":
        typer.echo(plan_obj.to_json())
    elif format == "text":
        typer.echo(render_text_plan(plan_obj, hebrew=language.lower().startswith("he")))
    else:
        raise typer.BadParameter("format must be json or text")


@app.command()
def route(
    service: str = typer.Argument(..., help="Appointment goal"),
    age_group: str = typer.Option("adult", help="adult, child, infant, senior"),
) -> None:
    """Classify the likely specialty route."""
    age = normalize_enum(AgeGroup, age_group)
    typer.echo(classify_specialty(service, age_group=age))


@app.command()
def emergency_check(
    text: str = typer.Argument(..., help="Symptom text to screen for escalation"),
    age_group: str = typer.Option("adult", help="adult, child, infant, senior"),
) -> None:
    """Return whether emergency red flags are detected."""
    age = normalize_enum(AgeGroup, age_group)
    result = has_emergency_red_flags(text, age_group=age)
    typer.echo(json.dumps({"emergency_red_flags": result}, ensure_ascii=False, indent=2))


@app.command()
def privacy_check(
    text: str = typer.Argument(..., help="Text to screen for sensitive identifiers or secrets"),
) -> None:
    """Detect text that may contain ID numbers, passwords, or SMS codes."""
    result = contains_sensitive_secret(text)
    typer.echo(json.dumps({"privacy_risk": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
