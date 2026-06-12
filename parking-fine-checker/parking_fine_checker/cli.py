"""Command-line interface for Parking Fine Checker."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import client

app = typer.Typer(help="Check and organize Israeli parking, traffic, and toll fine cases.")
console = Console()


def resolve_base_url(env: str, base_url: Optional[str]) -> str:
    if base_url:
        return base_url
    if env == "production":
        return os.getenv("PARKING_FINE_BASE_URL_PRODUCTION", "mock://local")
    return os.getenv("PARKING_FINE_BASE_URL_SANDBOX", "mock://local")


def resolve_token(env: str, token: Optional[str]) -> Optional[str]:
    if token:
        return token
    if env == "production":
        return os.getenv("PARKING_FINE_TOKEN_PRODUCTION")
    return os.getenv("PARKING_FINE_TOKEN_SANDBOX")


@app.command()
def create(
    issuer_type: str = typer.Option(..., help="municipality, police, toll, collection, or other"),
    vehicle_number: str = typer.Option(..., help="Israeli vehicle number"),
    notice_number: Optional[str] = typer.Option(None, help="Fine or notice number"),
    issuer_name: Optional[str] = typer.Option(None, help="Issuer name"),
    amount_ils: Optional[str] = typer.Option(None, help="Amount in ILS"),
    notice_date: Optional[str] = typer.Option(None, help="YYYY-MM-DD or DD/MM/YYYY"),
    due_date: Optional[str] = typer.Option(None, help="YYYY-MM-DD or DD/MM/YYYY"),
    env: str = typer.Option("sandbox", help="sandbox or production"),
    base_url: Optional[str] = typer.Option(None, help="Authorized API base URL"),
    token: Optional[str] = typer.Option(None, help="Bearer token for authorized integrations"),
) -> None:
    """Create a local or middleware case and print JSON."""

    api = client.ParkingFineClient(
        base_url=resolve_base_url(env, base_url),
        token=resolve_token(env, token),
    )
    record = api.create_case(
        issuer_type=issuer_type,
        issuer_name=issuer_name,
        vehicle_number=vehicle_number,
        notice_number=notice_number,
        amount_ils=amount_ils,
        notice_date=notice_date,
        due_date=due_date,
    )
    console.print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
    api.close()


@app.command()
def validate(
    issuer_type: str = typer.Option(..., help="municipality, police, toll, collection, or other"),
    vehicle_number: str = typer.Option(..., help="Israeli vehicle number"),
    notice_number: Optional[str] = typer.Option(None, help="Fine or notice number"),
    issuer_name: Optional[str] = typer.Option(None, help="Issuer name"),
    amount_ils: Optional[str] = typer.Option(None, help="Amount in ILS"),
    notice_date: Optional[str] = typer.Option(None, help="YYYY-MM-DD or DD/MM/YYYY"),
    due_date: Optional[str] = typer.Option(None, help="YYYY-MM-DD or DD/MM/YYYY"),
    env: str = typer.Option("sandbox", help="sandbox or production"),
) -> None:
    """Validate and normalize notice details."""

    request = client.FineLookupRequest(
        issuer_type=issuer_type,
        issuer_name=issuer_name,
        vehicle_number=vehicle_number,
        notice_number=notice_number,
        amount_ils=amount_ils,
        notice_date=notice_date,
        due_date=due_date,
        environment=env,
    )
    console.print(json.dumps(request.to_payload(redact=True), ensure_ascii=False, indent=2))


@app.command()
def lookup(
    issuer_type: str = typer.Option(...),
    vehicle_number: str = typer.Option(...),
    notice_number: Optional[str] = typer.Option(None),
    issuer_name: Optional[str] = typer.Option(None),
    case_id: Optional[str] = typer.Option(None, help="Case ID returned from create"),
    env: str = typer.Option("sandbox", help="sandbox or production"),
    base_url: Optional[str] = typer.Option(None, help="Authorized API base URL"),
    token: Optional[str] = typer.Option(None, help="Bearer token for authorized integrations"),
) -> None:
    """Look up a fine through a configured transport."""

    request = client.FineLookupRequest(
        issuer_type=issuer_type,
        issuer_name=issuer_name,
        vehicle_number=vehicle_number,
        notice_number=notice_number,
        case_id=case_id,
        environment=env,
    )
    api = client.ParkingFineClient(
        base_url=resolve_base_url(env, base_url),
        token=resolve_token(env, token),
    )
    result = api.lookup_fine(request)
    console.print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    api.close()


@app.command()
def checklist(
    issuer_type: str = typer.Option(...),
    status: str = typer.Option("new"),
    business_vehicle: bool = typer.Option(False, help="Add company/fleet steps"),
    vehicle_number: Optional[str] = typer.Option(None),
    notice_number: Optional[str] = typer.Option(None),
    case_id: Optional[str] = typer.Option(None, help="Case ID returned from create"),
) -> None:
    """Print an operational checklist."""

    items = client.build_checklist(
        issuer_type=issuer_type,
        status=status,
        business_vehicle=business_vehicle,
    )
    table = Table(title="Fine Handling Checklist")
    table.add_column("#", justify="right")
    table.add_column("Action")
    for index, item in enumerate(items, 1):
        table.add_row(str(index), item)
    console.print(table)
    if case_id:
        console.print(f"Case: {case_id}")
    if vehicle_number:
        console.print(f"Vehicle: {client.normalize_vehicle_number(vehicle_number)}")
    if notice_number:
        console.print(f"Notice: {notice_number}")


@app.command()
def decide(
    issuer_type: str = typer.Option(...),
    status: str = typer.Option("verified_unpaid"),
    payment_app_matches: bool = typer.Option(False),
    driver_known: bool = typer.Option(False),
    has_points_or_court: bool = typer.Option(False),
    collection_breakdown: bool = typer.Option(True),
    duplicate_risk: bool = typer.Option(False),
) -> None:
    """Recommend the next workflow decision."""

    decision = client.assess_case(
        issuer_type=issuer_type,
        status=status,
        payment_app_matches=payment_app_matches,
        driver_known=driver_known,
        has_points_or_court=has_points_or_court,
        collection_breakdown=collection_breakdown,
        duplicate_risk=duplicate_risk,
    )
    console.print(json.dumps({"decision": decision}, ensure_ascii=False, indent=2))


@app.command()
def memo(
    case_id: str = typer.Option(...),
    issuer_name: str = typer.Option(...),
    vehicle_number: str = typer.Option(...),
    notice_number: str = typer.Option(...),
    amount_ils: str = typer.Option(...),
    due_date: str = typer.Option(...),
    approver: str = typer.Option(...),
    reason: str = typer.Option("Official lookup matched vehicle, notice, amount, and due date."),
) -> None:
    """Generate a payment approval memo."""

    console.print(
        client.approval_memo(
            case_id=case_id,
            issuer_name=issuer_name,
            vehicle_number=vehicle_number,
            notice_number=notice_number,
            amount_ils=amount_ils,
            due_date=due_date,
            approver=approver,
            reason=reason,
        )
    )


@app.command("duplicates")
def duplicates_command(
    csv_path: Path = typer.Argument(..., exists=True, readable=True),
) -> None:
    """Find duplicate cases in a CSV fine register."""

    rows = client.load_cases_csv(csv_path)
    duplicates = client.detect_duplicates(rows)
    console.print(
        json.dumps(
            {
                "duplicate_count": len(duplicates),
                "duplicates": [
                    {"issuer_name": issuer, "vehicle_number": vehicle, "notice_number": notice}
                    for issuer, vehicle, notice in duplicates
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
