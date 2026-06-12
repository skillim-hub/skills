"""Command line interface for driving-license booking workflows."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import click

from .client import Applicant, BookingKind, BookingRequest, DrivingLicenseBookerClient, LicenseClass, TimeWindow


def _client(env: str, state: str | None) -> DrivingLicenseBookerClient:
    return DrivingLicenseBookerClient(environment=env, state_path=state)


def _applicant(name: str, national_id: str, phone: str, license_number: str | None, email: str | None, license_class: str) -> Applicant:
    return Applicant(
        full_name=name,
        national_id=national_id,
        phone=phone,
        license_number=license_number,
        email=email,
        license_class=license_class,
    )


def _window(date_value: str, city: str | None = None, branch: str | None = None) -> TimeWindow:
    return TimeWindow(date=dt.date.fromisoformat(date_value), city=city, branch=branch)


def _print(payload: Any) -> None:
    if hasattr(payload, "to_dict"):
        payload = payload.to_dict()
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Prepare and track Israeli driving-license workflows."""


@main.command("service-links")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
def service_links(environment: str) -> None:
    """Print official-service links used during handoff."""
    _print(DrivingLicenseBookerClient(environment=environment).build_service_links())


@main.command("create-renewal")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--state", type=click.Path(path_type=Path), default=".driving-license-booker.json", show_default=True)
@click.option("--name", required=True)
@click.option("--national-id", required=True)
@click.option("--phone", required=True)
@click.option("--license-number")
@click.option("--email")
@click.option("--license-class", default="B", show_default=True)
@click.option("--expiry-date", required=True, help="ISO date, for example 2026-08-31")
def create_renewal(environment: str, state: Path, name: str, national_id: str, phone: str, license_number: str | None, email: str | None, license_class: str, expiry_date: str) -> None:
    """Create a local license-renewal handoff record."""
    client = _client(environment, str(state))
    applicant = _applicant(name, national_id, phone, license_number, email, license_class)
    payload = client.build_renewal_payload(applicant, expiry_date=expiry_date)
    response = client.create_booking({"kind": BookingKind.LICENSE_RENEWAL.value, **payload})
    _print(response)


@main.command("create-office")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--state", type=click.Path(path_type=Path), default=".driving-license-booker.json", show_default=True)
@click.option("--name", required=True)
@click.option("--national-id", required=True)
@click.option("--phone", required=True)
@click.option("--license-number")
@click.option("--email")
@click.option("--license-class", default="B", show_default=True)
@click.option("--date", "date_value", required=True, help="ISO date, for example 2026-07-15")
@click.option("--city", required=True)
@click.option("--branch")
@click.option("--accessibility-needed", is_flag=True)
def create_office(environment: str, state: Path, name: str, national_id: str, phone: str, license_number: str | None, email: str | None, license_class: str, date_value: str, city: str, branch: str | None, accessibility_needed: bool) -> None:
    """Create a Licensing Bureau appointment handoff record."""
    client = _client(environment, str(state))
    applicant = _applicant(name, national_id, phone, license_number, email, license_class)
    payload = client.build_bureau_appointment_payload(applicant, [_window(date_value, city, branch)], service_city=city, accessibility_needed=accessibility_needed)
    response = client.create_booking({"kind": BookingKind.BUREAU_APPOINTMENT.value, **payload})
    _print(response)


@main.command("create-practical")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--state", type=click.Path(path_type=Path), default=".driving-license-booker.json", show_default=True)
@click.option("--name", required=True)
@click.option("--national-id", required=True)
@click.option("--phone", required=True)
@click.option("--license-number")
@click.option("--email")
@click.option("--license-class", default="B", show_default=True)
@click.option("--date", "date_value", required=True)
@click.option("--teacher-name", required=True)
@click.option("--teacher-phone", required=True)
@click.option("--pickup-city")
def create_practical(environment: str, state: Path, name: str, national_id: str, phone: str, license_number: str | None, email: str | None, license_class: str, date_value: str, teacher_name: str, teacher_phone: str, pickup_city: str | None) -> None:
    """Create a practical-test coordination handoff record."""
    client = _client(environment, str(state))
    applicant = _applicant(name, national_id, phone, license_number, email, license_class)
    payload = client.build_practical_test_payload(applicant, [_window(date_value, pickup_city)], teacher_name=teacher_name, teacher_phone=teacher_phone, pickup_city=pickup_city, vehicle_class=license_class)
    response = client.create_booking({"kind": BookingKind.PRACTICAL_TEST.value, **payload})
    _print(response)


@main.command("get")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--state", type=click.Path(path_type=Path), default=".driving-license-booker.json", show_default=True)
@click.argument("request_id")
def get(environment: str, state: Path, request_id: str) -> None:
    """Read a local workflow record by request id."""
    _print(_client(environment, str(state)).get_booking(request_id))


@main.command("cancel")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--state", type=click.Path(path_type=Path), default=".driving-license-booker.json", show_default=True)
@click.option("--reason")
@click.argument("request_id")
def cancel(environment: str, state: Path, request_id: str, reason: str | None) -> None:
    """Mark a local workflow record as cancelled."""
    _print(_client(environment, str(state)).cancel_booking(request_id, reason))


@main.command("list")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--state", type=click.Path(path_type=Path), default=".driving-license-booker.json", show_default=True)
@click.option("--status")
def list_records(environment: str, state: Path, status: str | None) -> None:
    """List local workflow records."""
    _print([record.to_dict() for record in _client(environment, str(state)).list_bookings(status=status)])


@main.command("readiness")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--name", required=True)
@click.option("--national-id", required=True)
@click.option("--phone", required=True)
@click.option("--license-number")
@click.option("--expiry-date", required=True)
@click.option("--paid/--not-paid", default=False, show_default=True)
@click.option("--medical-required", is_flag=True)
@click.option("--medical-done", is_flag=True)
def readiness(environment: str, name: str, national_id: str, phone: str, license_number: str | None, expiry_date: str, paid: bool, medical_required: bool, medical_done: bool) -> None:
    """Check renewal readiness before official handoff."""
    client = DrivingLicenseBookerClient(environment=environment)
    applicant = Applicant(name, national_id, phone, license_number=license_number)
    _print(client.check_renewal_readiness(applicant=applicant, expiry_date=dt.date.fromisoformat(expiry_date), has_paid_fee=paid, medical_declaration_required=medical_required, medical_declaration_done=medical_done))


@main.command("teacher-message")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--name", required=True)
@click.option("--national-id", required=True)
@click.option("--phone", required=True)
@click.option("--license-class", default="B", show_default=True)
@click.option("--date", "date_value", required=True)
@click.option("--teacher-name", required=True)
@click.option("--pickup-city")
def teacher_message(environment: str, name: str, national_id: str, phone: str, license_class: str, date_value: str, teacher_name: str, pickup_city: str | None) -> None:
    """Print a Hebrew practical-test coordination message."""
    client = DrivingLicenseBookerClient(environment=environment)
    applicant = Applicant(name, national_id, phone, license_class=license_class)
    _print({"message": client.make_teacher_message(applicant=applicant, windows=[_window(date_value, pickup_city)], teacher_name=teacher_name, pickup_city=pickup_city)})


if __name__ == "__main__":
    main()
