"""Typer CLI for the Social Security Benefit Checker."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from .client import (
    ApplicantProfile,
    BenefitType,
    Environment,
    LocalProfileStore,
    SocialSecurityBenefitChecker,
    load_profile_json,
)

app = typer.Typer(
    add_completion=False,
    help="Preliminary Israeli National Insurance benefit checker.",
)

BENEFIT_VALUES = [item.value for item in BenefitType]


def _checker(environment: Environment, store_dir: Optional[Path]) -> SocialSecurityBenefitChecker:
    store = LocalProfileStore(directory=store_dir, environment=environment)
    return SocialSecurityBenefitChecker(environment=environment, store=store)


def _print_json(payload: object) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def _read_profile(file: Optional[Path], json_text: Optional[str]) -> ApplicantProfile:
    if file is not None:
        return load_profile_json(file)
    if json_text:
        return ApplicantProfile.from_mapping(json.loads(json_text))
    env_json = os.environ.get("BENEFIT_CHECKER_PROFILE_JSON")
    if env_json:
        return ApplicantProfile.from_mapping(json.loads(env_json))
    raise typer.BadParameter("Provide --file, --json, or BENEFIT_CHECKER_PROFILE_JSON.")


@app.command("create-profile")
def create_profile(
    file: Optional[Path] = typer.Option(None, "--file", "-f", exists=True, dir_okay=False),
    json_text: Optional[str] = typer.Option(None, "--json", help="Applicant profile JSON string."),
    environment: Environment = typer.Option("sandbox", "--env", help="sandbox or production."),
    store_dir: Optional[Path] = typer.Option(None, "--store-dir", help="Local profile store directory."),
) -> None:
    """Create a local profile and print a response with profile_id."""

    checker = _checker(environment, store_dir)
    profile = _read_profile(file, json_text)
    _print_json(checker.create_profile(profile))


@app.command("check")
def check(
    profile_id: str = typer.Option(..., "--profile-id", help="Identifier returned by create-profile."),
    benefit: str = typer.Option("all", "--benefit", help="all or a supported benefit name."),
    environment: Environment = typer.Option("sandbox", "--env", help="sandbox or production."),
    store_dir: Optional[Path] = typer.Option(None, "--store-dir", help="Local profile store directory."),
) -> None:
    """Check a stored profile by profile_id."""

    checker = _checker(environment, store_dir)
    _print_json(checker.check_profile_id(profile_id, benefit=benefit))


@app.command("check-file")
def check_file_command(
    file: Path = typer.Option(..., "--file", "-f", exists=True, dir_okay=False),
    benefit: str = typer.Option("all", "--benefit", help="all or a supported benefit name."),
    environment: Environment = typer.Option("sandbox", "--env", help="sandbox or production."),
    store_dir: Optional[Path] = typer.Option(None, "--store-dir", help="Local profile store directory."),
) -> None:
    """Check a profile JSON file without saving it first."""

    checker = _checker(environment, store_dir)
    profile = load_profile_json(file)
    if benefit == "all":
        payload = {"environment": environment, "results": [item.to_dict() for item in checker.check_all(profile)]}
    else:
        payload = {"environment": environment, "results": [checker.check_benefit(benefit, profile).to_dict()]}
    _print_json(payload)


@app.command("workflow")
def workflow(
    file: Optional[Path] = typer.Option(None, "--file", "-f", exists=True, dir_okay=False),
    json_text: Optional[str] = typer.Option(None, "--json", help="Applicant profile JSON string."),
    environment: Environment = typer.Option("sandbox", "--env", help="sandbox or production."),
    store_dir: Optional[Path] = typer.Option(None, "--store-dir", help="Local profile store directory."),
) -> None:
    """Create a profile and screen every supported benefit in one operation."""

    checker = _checker(environment, store_dir)
    profile = _read_profile(file, json_text)
    _print_json(checker.run_application_workflow(profile))


@app.command("list-profiles")
def list_profiles(
    environment: Environment = typer.Option("sandbox", "--env", help="sandbox or production."),
    store_dir: Optional[Path] = typer.Option(None, "--store-dir", help="Local profile store directory."),
) -> None:
    """List locally stored profiles."""

    checker = _checker(environment, store_dir)
    _print_json({"environment": environment, "profiles": checker.list_profiles()})


@app.command("sample-profile")
def sample_profile() -> None:
    """Print a sample profile JSON document."""

    _print_json(
        {
            "age": 42,
            "resident": True,
            "employment_status": "unemployed",
            "monthly_income": 8500,
            "spouse_income": 0,
            "children_count": 2,
            "household_type": "single_parent",
            "qualifying_months": 14,
            "termination_reason": "laid_off",
            "registered_employment_service": True,
            "birth_dates": ["12/04/2018", "30/09/2021"],
        }
    )


def main() -> None:
    """Run the CLI application."""

    app()


if __name__ == "__main__":
    main()
