"""Command-line interface for Israeli event scheduling and Hebrew RSVP workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import (
    EventSchedulerClient,
    Guest,
    RSVPStatus,
    calculate_brit_milah_target_date,
    format_israeli_date,
    map_rsvp_status,
)

app = typer.Typer(help="Israeli event scheduler and Hebrew RSVP manager.")
client = EventSchedulerClient()


def _echo_json(data: object) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2, default=str))


@app.command()
def create_plan(
    event_type: str = typer.Option(..., "--event-type", help="wedding, bar_mitzvah, bat_mitzvah, brit_milah, etc."),
    date: str = typer.Option(..., "--date", help="Event date in DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD."),
    title: str = typer.Option(..., "--title", help="Event title."),
    city: str = typer.Option("", "--city", help="City or region."),
    output: Path = typer.Option(Path("event-plan.json"), "--output", "-o", help="JSON output path."),
) -> None:
    """Create a basic event plan JSON file and print a chainable response."""
    plan = client.create_plan(event_type=event_type, event_date=date, title=title, city=city)
    client.generate_timeline(plan)
    saved = client.save_plan(plan, output)
    _echo_json(client.plan_response(plan, saved_path=saved))


@app.command("add-guest")
def add_guest(
    plan_path: Path = typer.Option(..., "--plan", exists=True, readable=True, help="Plan JSON file."),
    event_id: str = typer.Option(..., "--event-id", help="Event identifier returned by create-plan."),
    name: str = typer.Option(..., "--name"),
    phone: str = typer.Option("", "--phone"),
    party_size: int = typer.Option(1, "--party-size", min=1),
    status: str = typer.Option("no_response", "--status"),
    group: str = typer.Option("", "--group"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write path. Defaults to --plan."),
) -> None:
    """Add a guest to an existing plan after validating the event id."""
    plan = client.load_plan(plan_path)
    client.require_event_id(plan, event_id)
    guest = Guest(
        name=name,
        phone=phone,
        party_size_invited=party_size,
        party_size_confirmed=party_size if map_rsvp_status(status) == RSVPStatus.CONFIRMED else 0,
        status=map_rsvp_status(status),
        group=group,
    )
    client.add_guest(plan, guest)
    saved = client.save_plan(plan, output or plan_path)
    _echo_json({"event_id": plan.event_id, "path": str(saved), "guest_count": len(plan.guests)})


@app.command()
def timeline(
    event_type: str = typer.Option(..., "--event-type"),
    date: str = typer.Option(..., "--date"),
    title: str = typer.Option("אירוע", "--title"),
) -> None:
    """Print a milestone timeline."""
    plan = client.create_plan(event_type=event_type, event_date=date, title=title)
    milestones = client.generate_timeline(plan)
    _echo_json([
        {
            "due_date": format_israeli_date(item.due_date),
            "urgency": item.urgency,
            "title": item.title,
            "owner": item.owner,
            "notes": item.notes,
        }
        for item in milestones
    ])


@app.command()
def budget(
    guests: int = typer.Option(..., "--guests", min=0),
    per_plate: float = typer.Option(..., "--per-plate", min=0),
    fixed_costs: float = typer.Option(0.0, "--fixed-costs", min=0),
    contingency: float = typer.Option(0.08, "--contingency", min=0),
) -> None:
    """Estimate event budget."""
    result = client.estimate_budget(
        guest_count=guests,
        per_plate_nis=per_plate,
        fixed_costs_nis=fixed_costs,
        contingency_rate=contingency,
    )
    _echo_json(result)


@app.command("rsvp-template")
def rsvp_template(
    name: str = typer.Option(..., "--name"),
    event_title: str = typer.Option(..., "--event-title"),
    date: str = typer.Option(..., "--date"),
    deadline: Optional[str] = typer.Option(None, "--deadline"),
    no_opt_out: bool = typer.Option(False, "--no-opt-out", help="Omit opt-out line."),
) -> None:
    """Print a Hebrew RSVP message."""
    typer.echo(
        client.build_rsvp_message(
            name=name,
            event_title=event_title,
            event_date=date,
            deadline=deadline,
            opt_out=not no_opt_out,
        )
    )


@app.command("brit-date")
def brit_date(
    birth_date: str = typer.Option(..., "--birth-date"),
    after_sunset: bool = typer.Option(False, "--after-sunset"),
    medically_cleared: bool = typer.Option(True, "--medically-cleared/--not-medically-cleared"),
) -> None:
    """Calculate an operational brit milah target date."""
    result = calculate_brit_milah_target_date(
        birth_date,
        after_sunset=after_sunset,
        medically_cleared=medically_cleared,
    )
    _echo_json(result)


@app.command()
def summary(csv_file: Path = typer.Option(..., "--csv", exists=True, readable=True)) -> None:
    """Summarize RSVP CSV data."""
    guests = client.import_guests_csv(csv_file)
    _echo_json(client.rsvp_summary(guests))


@app.command()
def tables(
    csv_file: Path = typer.Option(..., "--csv", exists=True, readable=True),
    table_size: int = typer.Option(10, "--table-size", min=1),
) -> None:
    """Assign confirmed guests to simple tables."""
    guests = client.import_guests_csv(csv_file)
    _echo_json(client.assign_tables(guests, table_size=table_size))


@app.command("transport")
def transport(
    csv_file: Path = typer.Option(..., "--csv", exists=True, readable=True),
    pickup_point: str = typer.Option("", "--pickup-point"),
) -> None:
    """Build a transport manifest from RSVP data."""
    guests = client.import_guests_csv(csv_file)
    _echo_json(client.transport_manifest(guests, pickup_point=pickup_point))



@app.command("tax-check")
def tax_check(
    amount_before_vat: float = typer.Option(..., "--amount-before-vat", min=0),
    invoice_date: str = typer.Option(..., "--invoice-date", help="Invoice date in DD/MM/YYYY."),
    vat_amount: Optional[float] = typer.Option(None, "--vat-amount", min=0),
    authorized_dealer: bool = typer.Option(True, "--authorized-dealer/--not-authorized-dealer"),
) -> None:
    """Check VAT and Israel invoice-allocation planning flags."""
    _echo_json(client.tax_documentation_check(
        invoice_amount_before_vat_nis=amount_before_vat,
        invoice_date=invoice_date,
        customer_is_authorized_dealer=authorized_dealer,
        vat_amount_nis=vat_amount,
    ))


@app.command("music-license")
def music_license(
    event_type: str = typer.Option(..., "--event-type"),
    date: str = typer.Option(..., "--date", help="Event date in DD/MM/YYYY."),
    business_event: bool = typer.Option(False, "--business-event"),
    background_music_only: bool = typer.Option(False, "--background-music-only"),
) -> None:
    """Print ACUM licensing checkpoint information for planning."""
    _echo_json(client.music_license_checkpoint(
        event_type=event_type,
        event_date=date,
        is_business_event=business_event,
        background_music_only=background_music_only,
    ))

def main() -> None:
    app()


if __name__ == "__main__":
    main()
