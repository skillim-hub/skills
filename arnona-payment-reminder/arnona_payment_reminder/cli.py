#!/usr/bin/env python3
"""Command-line interface for Arnona payment reminders."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import click

from .client import (
    ArnonaBill,
    ArnonaPaymentReminderClient,
    ArnonaValidationError,
    format_date,
    make_bill_id,
    parse_date,
)


def _load_bill(path: str | Path) -> ArnonaBill:
    return ArnonaBill.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def _client() -> ArnonaPaymentReminderClient:
    return ArnonaPaymentReminderClient.with_default_profiles()


def _store_path(store_dir: str | Path, bill_id: str) -> Path:
    return Path(store_dir) / f"{bill_id}.json"


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--env",
    "environment",
    type=click.Choice(["sandbox", "production"]),
    default=lambda: os.getenv("ARNONA_PAYMENT_REMINDER_ENV", "sandbox"),
    show_default="ARNONA_PAYMENT_REMINDER_ENV or sandbox",
    help="Execution environment label for local outputs.",
)
@click.pass_context
def cli(ctx: click.Context, environment: str) -> None:
    """Create reminders and instructions for Israeli municipal Arnona payments."""
    ctx.ensure_object(dict)
    ctx.obj["environment"] = environment


@cli.command("create")
@click.option("--municipality", required=True)
@click.option("--account-reference", required=True)
@click.option("--bill-number", required=True)
@click.option("--taxpayer-name", required=True)
@click.option("--property-address", required=True)
@click.option("--period-start", required=True, help="YYYY-MM-DD or DD/MM/YYYY.")
@click.option("--period-end", required=True, help="YYYY-MM-DD or DD/MM/YYYY.")
@click.option("--issue-date", required=True, help="YYYY-MM-DD or DD/MM/YYYY.")
@click.option("--due-date", required=True, help="YYYY-MM-DD or DD/MM/YYYY.")
@click.option("--amount-nis", required=True)
@click.option("--payer-id", default=None)
@click.option("--payment-url", default=None)
@click.option("--store-dir", default=".arnona-payments", show_default=True, type=click.Path(file_okay=False))
@click.option("--format", "output_format", type=click.Choice(["json", "text"]), default="json", show_default=True)
@click.pass_context
def create_cmd(
    ctx: click.Context,
    municipality: str,
    account_reference: str,
    bill_number: str,
    taxpayer_name: str,
    property_address: str,
    period_start: str,
    period_end: str,
    issue_date: str,
    due_date: str,
    amount_nis: str,
    payer_id: str | None,
    payment_url: str | None,
    store_dir: str,
    output_format: str,
) -> None:
    """Create a normalized local bill record and return its identifier."""
    payload: dict[str, Any] = {
        "municipality": municipality,
        "account_reference": account_reference,
        "bill_number": bill_number,
        "taxpayer_name": taxpayer_name,
        "property_address": property_address,
        "period_start": period_start,
        "period_end": period_end,
        "issue_date": issue_date,
        "due_date": due_date,
        "amount_nis": amount_nis,
        "status": "unpaid",
    }
    if payer_id:
        payload["payer_id"] = payer_id
    if payment_url:
        payload["payment_url"] = payment_url
    bill = ArnonaBill.from_dict(payload)
    warnings = _client().validate_bill(bill)
    bill_id = make_bill_id(bill)
    target_dir = Path(store_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = _store_path(target_dir, bill_id)
    target_path.write_text(json.dumps(bill.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    response = {
        "id": bill_id,
        "environment": ctx.obj.get("environment", "sandbox"),
        "path": str(target_path),
        "valid": True,
        "warnings": warnings,
    }
    if output_format == "json":
        click.echo(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        click.echo(f"{bill_id} {target_path}")


@cli.command("validate")
@click.argument("bill_json", type=click.Path(exists=True, dir_okay=False))
def validate_cmd(bill_json: str) -> None:
    """Validate a normalized Arnona bill JSON file."""
    try:
        bill = _load_bill(bill_json)
        warnings = _client().validate_bill(bill)
    except Exception as exc:  # pragma: no cover - click renders error path
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps({"valid": True, "warnings": warnings}, ensure_ascii=False, indent=2))


@cli.command("plan")
@click.argument("bill_json", type=click.Path(exists=True, dir_okay=False))
@click.option("--as-of", "as_of", default=None, help="Reference date, YYYY-MM-DD or DD/MM/YYYY.")
@click.option("--language", type=click.Choice(["en", "he"]), default="en", show_default=True)
@click.option("--include-past", is_flag=True, help="Include reminders whose send date already passed.")
@click.option("--format", "output_format", type=click.Choice(["json", "text"]), default="json", show_default=True)
def plan_cmd(bill_json: str, as_of: str | None, language: str, include_past: bool, output_format: str) -> None:
    """Build a reminder plan for one bill JSON file."""
    bill = _load_bill(bill_json)
    plan = _client().build_reminder_plan(
        bill, as_of=as_of, language=language, include_past=include_past  # type: ignore[arg-type]
    )
    if output_format == "json":
        click.echo(plan.to_json())
        return
    click.echo(f"Status: {plan.status}")
    click.echo(plan.instructions.summary)
    for event in plan.events:
        click.echo(f"- {event.send_on.isoformat()} [{event.severity}] {event.title}")


@cli.command("plan-id")
@click.argument("bill_id")
@click.option("--store-dir", default=".arnona-payments", show_default=True, type=click.Path(file_okay=False))
@click.option("--as-of", "as_of", default=None, help="Reference date, YYYY-MM-DD or DD/MM/YYYY.")
@click.option("--language", type=click.Choice(["en", "he"]), default="en", show_default=True)
@click.option("--include-past", is_flag=True)
@click.option("--format", "output_format", type=click.Choice(["json", "text"]), default="json", show_default=True)
def plan_id_cmd(
    bill_id: str,
    store_dir: str,
    as_of: str | None,
    language: str,
    include_past: bool,
    output_format: str,
) -> None:
    """Build a reminder plan from a bill identifier returned by create."""
    bill_path = _store_path(store_dir, bill_id)
    if not bill_path.exists():
        raise click.ClickException(f"No stored bill found for id {bill_id} in {store_dir}.")
    plan_cmd.callback(str(bill_path), as_of, language, include_past, output_format)  # type: ignore[attr-defined]


@cli.command("instructions")
@click.argument("bill_json", type=click.Path(exists=True, dir_okay=False))
@click.option("--language", type=click.Choice(["en", "he"]), default="en", show_default=True)
def instructions_cmd(bill_json: str, language: str) -> None:
    """Print payment instructions for one bill."""
    bill = _load_bill(bill_json)
    client = _client()
    profile = client.profile_for(bill.municipality)
    instructions = client.payment_instructions(bill, profile=profile, language=language)  # type: ignore[arg-type]
    click.echo(json.dumps(instructions.to_dict(), ensure_ascii=False, indent=2))


@cli.command("due-dates")
@click.argument("start_due_date")
@click.option("--count", default=6, show_default=True, type=int)
@click.option("--interval-months", default=2, show_default=True, type=int)
@click.option("--language", type=click.Choice(["en", "he"]), default="en", show_default=True)
def due_dates_cmd(start_due_date: str, count: int, interval_months: int, language: str) -> None:
    """Generate a bimonthly or custom due-date series."""
    dates = ArnonaPaymentReminderClient().next_due_dates(
        start_due_date, count=count, interval_months=interval_months
    )
    click.echo(json.dumps([format_date(item, language) for item in dates], ensure_ascii=False, indent=2))


@cli.command("export-ics")
@click.argument("bill_json", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_ics", type=click.Path(dir_okay=False))
@click.option("--as-of", "as_of", default=None, help="Reference date, YYYY-MM-DD or DD/MM/YYYY.")
@click.option("--language", type=click.Choice(["en", "he"]), default="en", show_default=True)
@click.option("--include-past", is_flag=True)
def export_ics_cmd(bill_json: str, output_ics: str, as_of: str | None, language: str, include_past: bool) -> None:
    """Export reminders to an ICS calendar file."""
    bill = _load_bill(bill_json)
    client = _client()
    plan = client.build_reminder_plan(bill, as_of=as_of, language=language, include_past=include_past)  # type: ignore[arg-type]
    client.save_ics(plan, output_ics)
    click.echo(str(Path(output_ics).resolve()))


@cli.command("sample-bill")
@click.argument("output_json", type=click.Path(dir_okay=False))
def sample_bill_cmd(output_json: str) -> None:
    """Write a sample bill JSON file."""
    payload = {
        "municipality": "Tel Aviv-Yafo",
        "account_reference": "123456789",
        "bill_number": "2026-ARN-000123",
        "taxpayer_name": "Sample Business Ltd.",
        "property_address": "Ibn Gabirol 1, Tel Aviv-Yafo",
        "period_start": "2026-01-01",
        "period_end": "2026-02-28",
        "issue_date": "2026-01-05",
        "due_date": "2026-02-28",
        "amount_nis": "1540.20",
        "status": "unpaid",
        "payer_id": "513456789",
    }
    Path(output_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    click.echo(str(Path(output_json).resolve()))


if __name__ == "__main__":
    cli()
