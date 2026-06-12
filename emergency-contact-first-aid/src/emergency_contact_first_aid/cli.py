"""Typer CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import DEFAULT_EMERGENCY_SERVICES, EmergencyInfoClient

app = typer.Typer(help="Emergency contact and first-aid local CLI")


def numbers(json_output: bool = typer.Option(False, "--json"), env: str = typer.Option("sandbox", "--env")) -> None:
    if json_output:
        typer.echo(json.dumps(DEFAULT_EMERGENCY_SERVICES, ensure_ascii=False, indent=2))
    else:
        for key, value in DEFAULT_EMERGENCY_SERVICES.items():
            typer.echo(f"{key}: {value}")


def create_profile(
    profile_name: str = typer.Option(..., "--profile-name"),
    address: str = typer.Option(..., "--address"),
    locality: str = typer.Option(..., "--locality"),
    contact_name: str = typer.Option(..., "--contact-name"),
    contact_phone: str = typer.Option(..., "--contact-phone"),
    store_dir: Path = typer.Option(Path(".ecfa-sandbox"), "--store-dir"),
    env: str = typer.Option("sandbox", "--env"),
) -> None:
    client = EmergencyInfoClient()
    result = client.create_profile(profile_name, address, locality, contact_name, contact_phone, store_dir, env)
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


def validate(
    profile: Optional[Path] = typer.Argument(None),
    profile_id: Optional[str] = typer.Option(None, "--profile-id"),
    store_dir: Path = typer.Option(Path(".ecfa-sandbox"), "--store-dir"),
    strict: bool = typer.Option(False, "--strict"),
    env: str = typer.Option("sandbox", "--env"),
) -> None:
    client = EmergencyInfoClient()
    loaded = client.load_profile_by_id(profile_id, store_dir) if profile_id else client.load_profile(profile)
    result = client.validate_profile(loaded, strict_privacy=strict)
    typer.echo(json.dumps(result.to_mapping(), ensure_ascii=False, indent=2))
    if not result.ok:
        raise typer.Exit(1)


def wallet_card(
    profile: Optional[Path] = typer.Argument(None),
    profile_id: Optional[str] = typer.Option(None, "--profile-id"),
    store_dir: Path = typer.Option(Path(".ecfa-sandbox"), "--store-dir"),
    env: str = typer.Option("sandbox", "--env"),
) -> None:
    client = EmergencyInfoClient()
    loaded = client.load_profile_by_id(profile_id, store_dir) if profile_id else client.load_profile(profile)
    typer.echo(client.render_wallet_card(loaded))


def redact(
    profile: Optional[Path] = typer.Argument(None),
    profile_id: Optional[str] = typer.Option(None, "--profile-id"),
    store_dir: Path = typer.Option(Path(".ecfa-sandbox"), "--store-dir"),
    env: str = typer.Option("sandbox", "--env"),
) -> None:
    client = EmergencyInfoClient()
    loaded = client.load_profile_by_id(profile_id, store_dir) if profile_id else client.load_profile(profile)
    typer.echo(json.dumps(client.redact_profile(loaded), ensure_ascii=False, indent=2))


def triage(
    scenario: str = typer.Option(..., "--scenario"),
    age_group: str = typer.Option("adult", "--age-group"),
    conscious: Optional[bool] = typer.Option(None, "--conscious"),
    breathing: Optional[bool] = typer.Option(None, "--breathing"),
    severe_bleeding: bool = typer.Option(False, "--severe-bleeding"),
    chest_pain: bool = typer.Option(False, "--chest-pain"),
    stroke_signs: bool = typer.Option(False, "--stroke-signs"),
    env: str = typer.Option("sandbox", "--env"),
) -> None:
    client = EmergencyInfoClient()
    result = client.triage(
        scenario,
        age_group=age_group,
        conscious=conscious,
        breathing=breathing,
        severe_bleeding=severe_bleeding,
        chest_pain=chest_pain,
        stroke_signs=stroke_signs,
    )
    typer.echo(json.dumps(result.to_mapping(), ensure_ascii=False, indent=2))


app.command("numbers")(numbers)
app.command("create-profile")(create_profile)
app.command("validate")(validate)
app.command("wallet-card")(wallet_card)
app.command("redact")(redact)
app.command("triage")(triage)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
