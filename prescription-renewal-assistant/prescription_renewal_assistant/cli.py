from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from .client import (
    Fulfillment,
    PrescriptionRenewalClient,
    RenewalCase,
    expense_record,
    pharmacy_checklist,
    redact_sensitive_text,
)

app = typer.Typer(help="Privacy-first Israeli prescription-renewal workflow helper.", no_args_is_help=True)


def default_store_path() -> Path:
    return Path(os.environ.get("PRA_CASE_STORE", ".pra_cases.json"))


def print_json(data: object) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


def build_case(
    kupat_cholim: str,
    medication_name: str,
    supply_days: int,
    consent_confirmed: bool,
    patient_alias: str,
    strength_form: Optional[str],
    repeats_left: Optional[int],
    valid_until: Optional[str],
    last_dispensed: Optional[str],
    preferred_fulfillment: Fulfillment,
    pharmacy: Optional[str],
    active_visible: Optional[bool],
    needs_cold_chain: bool,
    controlled_medication: bool,
    travel_date: Optional[str],
    symptoms_or_distress: bool,
) -> RenewalCase:
    return RenewalCase(
        kupat_cholim=kupat_cholim,
        medication_name=medication_name,
        supply_days=supply_days,
        consent_confirmed=consent_confirmed,
        patient_alias=patient_alias,
        strength_form=strength_form,
        repeats_left=repeats_left,
        valid_until=valid_until,
        last_dispensed=last_dispensed,
        preferred_fulfillment=preferred_fulfillment,
        pharmacy=pharmacy,
        active_visible=active_visible,
        needs_cold_chain=needs_cold_chain,
        controlled_medication=controlled_medication,
        travel_date=travel_date,
        symptoms_or_distress=symptoms_or_distress,
    )


@app.command()
def create(
    kupat_cholim: str = typer.Option(...),
    medication_name: str = typer.Option(...),
    supply_days: int = typer.Option(..., min=0),
    consent_confirmed: bool = typer.Option(False, "--consent-confirmed"),
    patient_alias: str = typer.Option("self"),
    strength_form: Optional[str] = typer.Option(None),
    repeats_left: Optional[int] = typer.Option(None, min=0),
    valid_until: Optional[str] = typer.Option(None),
    last_dispensed: Optional[str] = typer.Option(None),
    preferred_fulfillment: Fulfillment = typer.Option(Fulfillment.UNKNOWN),
    pharmacy: Optional[str] = typer.Option(None),
    active_visible: Optional[bool] = typer.Option(None),
    needs_cold_chain: bool = typer.Option(False, "--cold-chain"),
    controlled_medication: bool = typer.Option(False, "--controlled"),
    travel_date: Optional[str] = typer.Option(None),
    symptoms_or_distress: bool = typer.Option(False, "--symptoms-or-distress"),
    store: Path = typer.Option(default_store_path, "--store"),
) -> None:
    """Create a local case, triage it, and return a reusable case ID."""
    case = build_case(
        kupat_cholim,
        medication_name,
        supply_days,
        consent_confirmed,
        patient_alias,
        strength_form,
        repeats_left,
        valid_until,
        last_dispensed,
        preferred_fulfillment,
        pharmacy,
        active_visible,
        needs_cold_chain,
        controlled_medication,
        travel_date,
        symptoms_or_distress,
    )
    client = PrescriptionRenewalClient()
    case_id = client.create_case(case, store_path=store)
    result = client.triage(case)
    print_json({"case_id": case_id, "store": str(store), "triage": result.to_dict()})


@app.command()
def triage(
    case_id: Optional[str] = typer.Option(None),
    store: Path = typer.Option(default_store_path, "--store"),
    kupat_cholim: Optional[str] = typer.Option(None),
    medication_name: Optional[str] = typer.Option(None),
    supply_days: Optional[int] = typer.Option(None, min=0),
    consent_confirmed: bool = typer.Option(False, "--consent-confirmed"),
    patient_alias: str = typer.Option("self"),
    strength_form: Optional[str] = typer.Option(None),
    repeats_left: Optional[int] = typer.Option(None, min=0),
    valid_until: Optional[str] = typer.Option(None),
    last_dispensed: Optional[str] = typer.Option(None),
    preferred_fulfillment: Fulfillment = typer.Option(Fulfillment.UNKNOWN),
    pharmacy: Optional[str] = typer.Option(None),
    active_visible: Optional[bool] = typer.Option(None),
    needs_cold_chain: bool = typer.Option(False, "--cold-chain"),
    controlled_medication: bool = typer.Option(False, "--controlled"),
    travel_date: Optional[str] = typer.Option(None),
    symptoms_or_distress: bool = typer.Option(False, "--symptoms-or-distress"),
) -> None:
    """Triage an existing case ID or direct case fields."""
    client = PrescriptionRenewalClient()
    if case_id:
        case = client.load_case(case_id, store_path=store)
    else:
        if kupat_cholim is None or medication_name is None or supply_days is None:
            raise typer.BadParameter("Provide --case-id or direct case fields.")
        case = build_case(
            kupat_cholim,
            medication_name,
            supply_days,
            consent_confirmed,
            patient_alias,
            strength_form,
            repeats_left,
            valid_until,
            last_dispensed,
            preferred_fulfillment,
            pharmacy,
            active_visible,
            needs_cold_chain,
            controlled_medication,
            travel_date,
            symptoms_or_distress,
        )
    print_json(client.triage(case).to_dict())


@app.command()
def message(
    case_id: str = typer.Option(...),
    language: str = typer.Option("en"),
    store: Path = typer.Option(default_store_path, "--store"),
) -> None:
    """Generate a doctor or clinic message from a stored case ID."""
    if language not in {"en", "he"}:
        raise typer.BadParameter("language must be en or he")
    client = PrescriptionRenewalClient()
    case = client.load_case(case_id, store_path=store)
    print_json(client.doctor_message(case, language=language).to_dict())  # type: ignore[arg-type]


@app.command()
def checklist(
    case_id: Optional[str] = typer.Option(None),
    store: Path = typer.Option(default_store_path, "--store"),
    pharmacy: Optional[str] = typer.Option(None),
    delivery: bool = typer.Option(False, "--delivery"),
    pickup: bool = typer.Option(False, "--pickup"),
    cold_chain: bool = typer.Option(False, "--cold-chain"),
    controlled: bool = typer.Option(False, "--controlled"),
    price: bool = typer.Option(True, "--price/--no-price"),
) -> None:
    """Build a pharmacy verification checklist."""
    if delivery and pickup:
        raise typer.BadParameter("Choose either --delivery or --pickup, not both.")

    fulfillment = Fulfillment.UNKNOWN
    if delivery:
        fulfillment = Fulfillment.DELIVERY
    if pickup:
        fulfillment = Fulfillment.PICKUP

    if case_id:
        case = PrescriptionRenewalClient().load_case(case_id, store_path=store)
        pharmacy = pharmacy or case.pharmacy
        if fulfillment is Fulfillment.UNKNOWN:
            fulfillment = case.preferred_fulfillment
        cold_chain = cold_chain or case.needs_cold_chain
        controlled = controlled or case.controlled_medication

    result = pharmacy_checklist(
        pharmacy=pharmacy,
        fulfillment=fulfillment,
        needs_cold_chain=cold_chain,
        controlled_medication=controlled,
        price_check=price,
    )
    print_json(result.to_dict())


@app.command()
def redact(text: str = typer.Argument(...)) -> None:
    """Mask Israeli ID numbers and mobile phone numbers."""
    typer.echo(redact_sensitive_text(text))


@app.command()
def expense(
    vendor: str = typer.Option(...),
    amount_nis: float = typer.Option(..., min=0),
    paid_on: str = typer.Option(...),
    category: str = typer.Option("medical/pharmacy expense"),
) -> None:
    """Create a privacy-minimized expense record."""
    print_json(expense_record(vendor=vendor, amount_nis=amount_nis, paid_on=paid_on, category=category))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
