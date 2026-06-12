"""Command-line interface for CRM conversation synchronization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .client import (
    CRMIntegrationClient,
    EnvironmentName,
    ProviderName,
    audit_template as build_audit_template,
    classify_business_purpose,
    is_explicit_opt_in_text,
    is_opt_out_text,
    load_thread_file,
    normalize_israeli_phone,
    redact_sensitive_text,
    result_to_dict,
    write_audit_events,
)

app = typer.Typer(help="Sync WhatsApp, email, and SMS conversations into CRM systems.")

PROVIDERS = {"monday", "hubspot", "salesforce"}
ENVIRONMENTS = {"sandbox", "production"}


def _provider(value: str) -> ProviderName:
    normalized = value.lower()
    if normalized not in PROVIDERS:
        raise typer.BadParameter("provider must be monday, hubspot, or salesforce")
    return normalized  # type: ignore[return-value]


def _environment(value: str) -> EnvironmentName:
    normalized = value.lower()
    if normalized not in ENVIRONMENTS:
        raise typer.BadParameter("env must be sandbox or production")
    return normalized  # type: ignore[return-value]


@app.command("normalize-phone")
def normalize_phone(phone: str) -> None:
    """Normalize a phone number to E.164."""
    typer.echo(normalize_israeli_phone(phone))


@app.command("validate-config")
def validate_config(
    provider: str = typer.Option(..., help="monday, hubspot, or salesforce"),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    base_url: str = typer.Option("", help="Required for Salesforce live sync."),
) -> None:
    """Validate local provider configuration without writing to CRM."""
    selected_provider = _provider(provider)
    selected_env = _environment(env)
    client = CRMIntegrationClient.from_env(selected_provider, environment=selected_env, base_url=base_url, dry_run=True)
    payload = {
        "provider": client.config.provider,
        "environment": client.config.environment,
        "base_url": base_url or ("salesforce-base-url-required" if selected_provider == "salesforce" else client.config.resolved_base_url()),
        "dry_run": client.config.dry_run,
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("dry-run")
def dry_run(
    provider: str = typer.Option(..., help="monday, hubspot, or salesforce"),
    input: Path = typer.Option(..., exists=True, readable=True, help="JSON thread file."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    business_purpose: str = typer.Option("service", help="sales, support, appointment, admin, or service."),
    base_url: str = typer.Option("", help="CRM base URL override."),
    monday_board_id: Optional[str] = typer.Option(None, help="Monday board id for preview."),
) -> None:
    """Preview CRM writes without network calls."""
    thread = load_thread_file(input)
    thread.business_purpose = business_purpose
    client = CRMIntegrationClient.from_env(_provider(provider), environment=_environment(env), base_url=base_url, dry_run=True, monday_board_id=monday_board_id)
    result = client.sync_thread(thread)
    typer.echo(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2))


@app.command("sync")
def sync(
    provider: str = typer.Option(..., help="monday, hubspot, or salesforce"),
    input: Path = typer.Option(..., exists=True, readable=True, help="JSON thread file."),
    env: str = typer.Option("sandbox", "--env", help="sandbox or production"),
    audit_log: Optional[Path] = typer.Option(None, help="Append audit events to JSONL."),
    base_url: str = typer.Option("", help="Required for Salesforce; optional override for other providers."),
    monday_board_id: Optional[str] = typer.Option(None, help="Monday board id."),
    live: bool = typer.Option(False, help="Write to the provider. Without this flag, perform a dry-run."),
    marketing_action: bool = typer.Option(False, help="Treat this run as a marketing action requiring opt-in."),
) -> None:
    """Sync one JSON thread file."""
    selected_env = _environment(env)
    thread = load_thread_file(input)
    client = CRMIntegrationClient.from_env(_provider(provider), environment=selected_env, base_url=base_url, dry_run=not live, monday_board_id=monday_board_id)
    result = client.sync_thread(thread, marketing_action=marketing_action)
    if audit_log:
        write_audit_events(audit_log, result.audit_events)
    typer.echo(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2))


@app.command("audit-template")
def audit_template(
    crm_object_id: Optional[str] = typer.Option(None, help="CRM object id from a create response."),
    provider: str = typer.Option("hubspot", help="monday, hubspot, or salesforce"),
) -> None:
    """Print an audit JSONL event template."""
    typer.echo(json.dumps(build_audit_template(crm_object_id=crm_object_id, provider=_provider(provider)), ensure_ascii=False, indent=2))


@app.command("classify")
def classify(text: str) -> None:
    """Classify a conversation snippet."""
    payload = {
        "business_purpose": classify_business_purpose(text),
        "opt_out": is_opt_out_text(text),
        "explicit_opt_in": is_explicit_opt_in_text(text),
        "redacted": redact_sensitive_text(text),
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    """Run the command-line interface."""
    app()


if __name__ == "__main__":
    main()
