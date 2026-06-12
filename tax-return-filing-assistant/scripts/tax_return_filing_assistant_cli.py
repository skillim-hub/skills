"""Command-line interface for the Israeli tax-return filing helper."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal

import click

from tax_return_filing_assistant_client import (
    FilingProfile,
    LocalProfileStore,
    TaxReturnAssistantClient,
    load_profile,
    save_json,
)

Environment = Literal["sandbox", "production"]


def _state_path() -> Path | None:
    raw = os.environ.get("TAX_ASSISTANT_STATE_PATH")
    return Path(raw) if raw else None


def _client() -> TaxReturnAssistantClient:
    return TaxReturnAssistantClient(profile_store=LocalProfileStore(_state_path()))


def _env_value(env: str | None) -> Environment:
    value = (env or os.environ.get("TAX_ASSISTANT_ENV") or "sandbox").strip().lower()
    if value not in {"sandbox", "production"}:
        raise click.BadParameter("env must be sandbox or production")
    return value  # type: ignore[return-value]


def _json_echo(data: Any) -> None:
    click.echo(json.dumps(data, ensure_ascii=False, indent=2))


def _profile_from_options(
    tax_year: int | None,
    taxpayer_type: str,
    salary_only: bool,
    wants_refund: bool,
    business_income: bool,
    annual_turnover_ils: float,
    has_employees: bool,
    paid_suppliers: bool,
    foreign_income: bool,
    capital_gains: bool,
    rental_income: bool,
    online: bool,
    represented_by_cpa: bool,
    notes: str,
) -> FilingProfile:
    year = tax_year if tax_year is not None else int(os.environ.get("TAX_ASSISTANT_TAX_YEAR", "0") or 0)
    return FilingProfile(
        tax_year=year or None,
        taxpayer_type=taxpayer_type,
        salary_only=salary_only,
        wants_refund=wants_refund,
        business_income=business_income,
        annual_turnover_ils=annual_turnover_ils,
        has_employees=has_employees,
        paid_suppliers=paid_suppliers,
        foreign_income=foreign_income,
        capital_gains=capital_gains,
        rental_income=rental_income,
        is_online=online,
        represented_by_cpa=represented_by_cpa,
        notes=notes,
    )


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Prepare Israeli tax-return workflows offline."""


@cli.command("create-profile")
@click.option("--env", "env_name", type=click.Choice(["sandbox", "production"]), default=None)
@click.option("--tax-year", type=int, default=None)
@click.option("--taxpayer-type", default="sole_proprietor", show_default=True)
@click.option("--salary-only/--not-salary-only", default=False, show_default=True)
@click.option("--wants-refund/--no-refund", default=False, show_default=True)
@click.option("--business-income/--no-business-income", default=True, show_default=True)
@click.option("--annual-turnover-ils", type=float, default=0.0, show_default=True)
@click.option("--has-employees/--no-employees", default=False, show_default=True)
@click.option("--paid-suppliers/--no-paid-suppliers", default=False, show_default=True)
@click.option("--foreign-income/--no-foreign-income", default=False, show_default=True)
@click.option("--capital-gains/--no-capital-gains", default=False, show_default=True)
@click.option("--rental-income/--no-rental-income", default=False, show_default=True)
@click.option("--online/--paper", default=True, show_default=True)
@click.option("--represented-by-cpa/--not-represented", default=False, show_default=True)
@click.option("--notes", default="", show_default=True)
def create_profile(
    env_name: str | None,
    tax_year: int | None,
    taxpayer_type: str,
    salary_only: bool,
    wants_refund: bool,
    business_income: bool,
    annual_turnover_ils: float,
    has_employees: bool,
    paid_suppliers: bool,
    foreign_income: bool,
    capital_gains: bool,
    rental_income: bool,
    online: bool,
    represented_by_cpa: bool,
    notes: str,
) -> None:
    """Create a local profile and print a JSON ID response."""

    profile = _profile_from_options(
        tax_year,
        taxpayer_type,
        salary_only,
        wants_refund,
        business_income,
        annual_turnover_ils,
        has_employees,
        paid_suppliers,
        foreign_income,
        capital_gains,
        rental_income,
        online,
        represented_by_cpa,
        notes,
    )
    stored = _client().create_profile(profile, _env_value(env_name))
    _json_echo(stored.to_dict())


@cli.command("init-profile")
@click.option("--output", "output_path", type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.option("--tax-year", type=int, default=None)
def init_profile(output_path: Path, tax_year: int | None) -> None:
    """Write a safe starter profile JSON file."""

    profile = FilingProfile(
        tax_year=tax_year or int(os.environ.get("TAX_ASSISTANT_TAX_YEAR", "2025")),
        taxpayer_type="sole_proprietor",
        business_income=True,
        paid_suppliers=True,
        annual_turnover_ils=float(os.environ.get("TAX_ASSISTANT_TURNOVER_ILS", "420000")),
    )
    save_json(output_path, profile.to_dict())
    _json_echo({"path": str(output_path), "profile": profile.to_dict()})


@cli.command()
@click.option("--profile", "profile_path", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option("--profile-id", default=None)
def recommend(profile_path: str | None, profile_id: str | None) -> None:
    """Recommend relevant forms from a profile file or stored profile ID."""

    client = _client()
    profile = client.get_profile(profile_id).profile if profile_id else load_profile_required(profile_path)
    _json_echo(client.recommend_forms(profile).to_dict())


@cli.command()
@click.argument("form")
@click.option("--tax-year", type=int, default=None)
@click.option("--env", "env_name", type=click.Choice(["sandbox", "production"]), default=None)
@click.option("--online/--paper", default=True, show_default=True)
@click.option("--represented-by-cpa/--not-represented", default=False, show_default=True)
def deadline(form: str, tax_year: int | None, env_name: str | None, online: bool, represented_by_cpa: bool) -> None:
    """Show a planning deadline and reminders for one form."""

    profile = FilingProfile(
        tax_year=tax_year or int(os.environ.get("TAX_ASSISTANT_TAX_YEAR", "2025")),
        is_online=online,
        represented_by_cpa=represented_by_cpa,
    )
    deadline_obj = _client().calculate_deadlines(profile, [form])[0]
    data = deadline_obj.to_dict()
    data["environment"] = _env_value(env_name)
    _json_echo(data)


@cli.command()
@click.argument("form")
@click.argument("field_id", required=False)
def fields(form: str, field_id: str | None) -> None:
    """Show field help for a covered form."""

    result = _client().get_field_help(form, field_id)
    data = [item.to_dict() for item in result] if isinstance(result, list) else result.to_dict()
    _json_echo(data)


@cli.command()
@click.option("--profile", "profile_path", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option("--profile-id", default=None)
def checklist(profile_path: str | None, profile_id: str | None) -> None:
    """Generate document checklists for a profile."""

    client = _client()
    profile = client.get_profile(profile_id).profile if profile_id else load_profile_required(profile_path)
    _json_echo([entry.to_dict() for entry in client.build_checklist(profile)])


@cli.command()
@click.option("--profile", "profile_path", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option("--profile-id", default=None)
def validate(profile_path: str | None, profile_id: str | None) -> None:
    """Validate a profile and print issues."""

    client = _client()
    profile = client.get_profile(profile_id).profile if profile_id else load_profile_required(profile_path)
    _json_echo([issue.to_dict() for issue in client.validate_profile(profile)])


@cli.command()
@click.option("--profile", "profile_path", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option("--profile-id", default=None)
def report(profile_path: str | None, profile_id: str | None) -> None:
    """Generate a full local report JSON response."""

    client = _client()
    if profile_id:
        _json_echo(client.generate_report_by_id(profile_id))
        return
    _json_echo(client.generate_report(load_profile_required(profile_path)))


@cli.command("export-report")
@click.option("--profile", "profile_path", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option("--profile-id", default=None)
@click.option("--output", "output_path", type=click.Path(dir_okay=False, path_type=Path), required=True)
def export_report(profile_path: str | None, profile_id: str | None, output_path: Path) -> None:
    """Write a full local report JSON file."""

    client = _client()
    report_data = client.generate_report_by_id(profile_id) if profile_id else client.generate_report(load_profile_required(profile_path))
    save_json(output_path, report_data)
    _json_echo({"path": str(output_path)})


@cli.command("list-profiles")
def list_profiles() -> None:
    """List local profile IDs."""

    _json_echo({"ids": _client().list_profile_ids()})


@cli.command("delete-profile")
@click.argument("profile_id")
def delete_profile(profile_id: str) -> None:
    """Delete a local profile ID."""

    _json_echo({"id": profile_id, "deleted": _client().delete_profile(profile_id)})


def load_profile_required(profile_path: str | None) -> FilingProfile:
    if profile_path is None:
        env_path = os.environ.get("TAX_ASSISTANT_PROFILE")
        if not env_path:
            raise click.UsageError("Provide --profile, --profile-id, or TAX_ASSISTANT_PROFILE")
        profile_path = env_path
    return load_profile(profile_path)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
