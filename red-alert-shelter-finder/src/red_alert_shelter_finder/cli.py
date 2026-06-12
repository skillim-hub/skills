"""Command-line interface for alert and shelter workflows."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import click

from .client import (
    DEFAULT_ALERTS_URL,
    AlertClientError,
    RedAlertShelterFinderClient,
    ShelterDataError,
    WatchError,
    alerts_to_json,
    shelters_to_json,
)

SAMPLE_ALERTS = '{"id":"sandbox-demo","title":"ירי רקטות וטילים","data":["חיפה"]}'


def _env_payload_file(environment: str) -> str:
    key = "RED_ALERT_SANDBOX_ALERTS_FILE" if environment == "sandbox" else "RED_ALERT_PRODUCTION_ALERTS_FILE"
    return os.getenv(key, "")


def _transport_for_environment(environment: str, alerts_file: Optional[str]):
    payload_path = alerts_file or _env_payload_file(environment)
    if payload_path:
        def file_transport(url: str, timeout: float, headers: dict[str, str]) -> str:
            return Path(payload_path).read_text(encoding="utf-8")
        return file_transport
    if environment == "sandbox":
        return lambda url, timeout, headers: SAMPLE_ALERTS
    return None


def build_client(environment: str, alerts_url: Optional[str], timeout: float, alerts_file: Optional[str] = None) -> RedAlertShelterFinderClient:
    transport = _transport_for_environment(environment, alerts_file)
    return RedAlertShelterFinderClient(
        alerts_url=alerts_url or os.getenv("RED_ALERT_ALERTS_URL") or DEFAULT_ALERTS_URL,
        timeout=timeout,
        transport=transport,
    )


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Check alerts and find nearest public shelters."""


@main.command()
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--area", "-a", help="Locality or alert area to check.")
@click.option("--alerts-url", help="Override alert endpoint URL.")
@click.option("--alerts-file", type=click.Path(exists=True, dir_okay=False), help="Read alert payload from a local file.")
@click.option("--timeout", default=10.0, show_default=True, type=float, help="Network timeout in seconds.")
@click.option("--raw", is_flag=True, help="Print raw normalized alert list instead of area status.")
def alerts(environment: str, area: str | None, alerts_url: str | None, alerts_file: str | None, timeout: float, raw: bool) -> None:
    """Fetch current alerts and optionally check a locality."""

    c = build_client(environment, alerts_url, timeout, alerts_file)
    try:
        active_alerts = c.fetch_current_alerts()
        if raw or not area:
            click.echo(alerts_to_json(active_alerts))
            return
        click.echo(json.dumps(c.status_for_area(area, active_alerts), ensure_ascii=False, indent=2))
    except AlertClientError as exc:
        raise click.ClickException(str(exc)) from exc


@main.command("create-watch")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--area", required=True, help="Locality or alert area to watch.")
@click.option("--output", type=click.Path(dir_okay=False), help="Optional path for saved watch JSON.")
def create_watch(environment: str, area: str, output: str | None) -> None:
    """Create a locality watch record and print its watch_id."""

    c = build_client(environment, None, 10.0)
    watch = c.create_watch(area, environment=environment)
    if output:
        c.save_watch(watch, output)
    click.echo(json.dumps(watch.to_dict(), ensure_ascii=False, indent=2))


@main.command("check-watch")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--watch-id", required=True, help="Identifier returned by create-watch.")
@click.option("--watch-file", required=True, type=click.Path(exists=True, dir_okay=False), help="Saved watch JSON file.")
@click.option("--alerts-url", help="Override alert endpoint URL.")
@click.option("--alerts-file", type=click.Path(exists=True, dir_okay=False), help="Read alert payload from a local file.")
@click.option("--timeout", default=10.0, show_default=True, type=float, help="Network timeout in seconds.")
def check_watch(environment: str, watch_id: str, watch_file: str, alerts_url: str | None, alerts_file: str | None, timeout: float) -> None:
    """Check a saved watch by id."""

    c = build_client(environment, alerts_url, timeout, alerts_file)
    try:
        watch = c.load_watch(watch_file, watch_id)
        active_alerts = c.fetch_current_alerts()
        click.echo(json.dumps(c.check_watch(watch, active_alerts), ensure_ascii=False, indent=2))
    except (AlertClientError, WatchError) as exc:
        raise click.ClickException(str(exc)) from exc


@main.command()
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--lat", required=True, type=float, help="Current latitude.")
@click.option("--lon", required=True, type=float, help="Current longitude.")
@click.option("--shelters", "shelters_path", required=True, type=click.Path(exists=True, dir_okay=False), help="CSV/JSON/GeoJSON shelter file.")
@click.option("--limit", default=5, show_default=True, type=int, help="Maximum number of shelters to return.")
@click.option("--max-distance-m", type=float, help="Optional maximum distance in meters.")
def nearest(environment: str, lat: float, lon: float, shelters_path: str, limit: int, max_distance_m: float | None) -> None:
    """Find nearest shelters from a local dataset."""

    c = build_client(environment, None, 10.0)
    try:
        shelters = c.load_shelters_file(shelters_path)
        nearest_shelters = c.nearest_shelters(lat, lon, shelters, limit=limit, max_distance_m=max_distance_m)
        click.echo(shelters_to_json(nearest_shelters))
    except ShelterDataError as exc:
        raise click.ClickException(str(exc)) from exc


@main.command("business-procedure")
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--city", required=True, help="Business city/locality.")
@click.option("--business-type", default="small business", show_default=True, help="Business type.")
@click.option("--staff", default=1, show_default=True, type=int, help="Number of staff on shift.")
@click.option("--customers/--no-customers", default=True, show_default=True, help="Whether customers may be on site.")
@click.option("--deliveries/--no-deliveries", default=False, show_default=True, help="Whether deliveries or field staff are involved.")
def business_procedure(environment: str, city: str, business_type: str, staff: int, customers: bool, deliveries: bool) -> None:
    """Generate a neutral emergency procedure for a business."""

    procedure = {
        "environment": environment,
        "city": city,
        "business_type": business_type,
        "staff": staff,
        "steps": [
            "Keep the route to the protected space clear before opening.",
            "When an alert is received, stop service immediately.",
            "Enter the nearest protected space and remain there until official guidance permits exit.",
            "Check staff status before resuming operations.",
        ],
    }
    if customers:
        procedure["steps"].insert(2, "Guide customers through the marked route without collecting carts, bags, or payments.")
    if deliveries:
        procedure["steps"].append("Pause dispatch and require every rider or field worker to check in after the waiting period.")
    click.echo(json.dumps(procedure, ensure_ascii=False, indent=2))


@main.command()
@click.option("--env", "environment", type=click.Choice(["sandbox", "production"]), default="sandbox", show_default=True)
@click.option("--active/--inactive", default=False, show_default=True, help="Return steps for active or inactive status.")
@click.option("--outside/--inside", default=False, show_default=True, help="User is outside.")
@click.option("--business/--consumer", default=False, show_default=True, help="Business-oriented steps.")
def steps(environment: str, active: bool, outside: bool, business: bool) -> None:
    """Print recommended action steps."""

    c = build_client(environment, None, 10.0)
    click.echo(json.dumps(c.action_steps(active=active, outside=outside, business=business), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
