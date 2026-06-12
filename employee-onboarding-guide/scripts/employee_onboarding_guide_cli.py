"""Typer CLI for the local Israeli employee onboarding helper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from employee_onboarding_guide_client import (
    EmployeeProfile,
    create_record as create_record_client,
    generate_checklist,
    generate_employee_message,
    generate_hebrew_checklist,
    load_profile_file,
    load_record,
    validate_profile,
)

app = typer.Typer(help="Generate and validate Israeli employee onboarding materials.")


def _profile_from_options(
    name: str,
    start_date: str,
    employment_type: str,
    role: str,
    salary_type: str,
    hourly: bool,
    other_employer: bool,
    active_pension: bool,
    no_active_pension: bool,
    foreign_worker: bool,
    youth: bool,
    remote: bool,
    student: bool,
    language: str,
    insecure_channel: bool,
    timekeeping_method: Optional[str],
    bank_details_received: bool,
    pension_fund_name: Optional[str],
    tax_coordination_received: bool,
    national_insurance_coordination_received: bool,
    employment_notice_status: str,
    equipment_required: bool,
    equipment_form_signed: bool,
) -> EmployeeProfile:
    return EmployeeProfile(
        full_name=name,
        start_date=start_date,
        employment_type=employment_type,
        role=role,
        salary_type="hourly" if hourly else salary_type,
        has_other_employer=other_employer,
        has_active_pension=True if active_pension else False if no_active_pension else None,
        foreign_worker=foreign_worker,
        youth=youth,
        remote=remote,
        student=student,
        language=language,
        secure_channel=not insecure_channel,
        timekeeping_method=timekeeping_method,
        bank_details_received=bank_details_received,
        pension_fund_name=pension_fund_name,
        tax_coordination_received=tax_coordination_received,
        national_insurance_coordination_received=national_insurance_coordination_received,
        employment_notice_status=employment_notice_status,
        equipment_required=equipment_required,
        equipment_form_signed=equipment_form_signed,
    )


def create(
    name: str = typer.Option(...),
    start_date: str = typer.Option(...),
    env: str = typer.Option("sandbox"),
    employment_type: str = typer.Option("employee"),
    role: str = typer.Option(""),
    salary_type: str = typer.Option("unknown"),
    hourly: bool = typer.Option(False),
    other_employer: bool = typer.Option(False),
    active_pension: bool = typer.Option(False),
    no_active_pension: bool = typer.Option(False),
    foreign_worker: bool = typer.Option(False),
    youth: bool = typer.Option(False),
    remote: bool = typer.Option(False),
    student: bool = typer.Option(False),
    language: str = typer.Option("en"),
    insecure_channel: bool = typer.Option(False),
    timekeeping_method: Optional[str] = typer.Option(None),
    bank_details_received: bool = typer.Option(False),
    pension_fund_name: Optional[str] = typer.Option(None),
    tax_coordination_received: bool = typer.Option(False),
    national_insurance_coordination_received: bool = typer.Option(False),
    employment_notice_status: str = typer.Option("missing"),
    equipment_required: bool = typer.Option(False),
    equipment_form_signed: bool = typer.Option(False),
) -> None:
    """Create a local onboarding record and print its id."""

    profile = _profile_from_options(
        name,
        start_date,
        employment_type,
        role,
        salary_type,
        hourly,
        other_employer,
        active_pension,
        no_active_pension,
        foreign_worker,
        youth,
        remote,
        student,
        language,
        insecure_channel,
        timekeeping_method,
        bank_details_received,
        pension_fund_name,
        tax_coordination_received,
        national_insurance_coordination_received,
        employment_notice_status,
        equipment_required,
        equipment_form_signed,
    )
    response = create_record_client(profile, environment=env)
    typer.echo(json.dumps(response, ensure_ascii=False, indent=2))


def validate(
    id: Optional[str] = typer.Option(None),
    path: Optional[Path] = typer.Option(None),
    env: str = typer.Option("sandbox"),
) -> None:
    """Validate a record by id or JSON file path."""

    if id:
        profile = load_record(id, environment=env)
    elif path:
        profile = load_profile_file(path)
    else:
        raise typer.BadParameter("Pass --id or --path.")
    result = validate_profile(profile)
    typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    if not result.ok:
        raise typer.Exit(1)


def checklist(
    id: Optional[str] = typer.Option(None),
    path: Optional[Path] = typer.Option(None),
    env: str = typer.Option("sandbox"),
    language: str = typer.Option("en"),
    name: Optional[str] = typer.Option(None),
    start_date: Optional[str] = typer.Option(None),
    role: str = typer.Option(""),
    employment_type: str = typer.Option("employee"),
    salary_type: str = typer.Option("unknown"),
    hourly: bool = typer.Option(False),
    other_employer: bool = typer.Option(False),
    active_pension: bool = typer.Option(False),
    no_active_pension: bool = typer.Option(False),
    foreign_worker: bool = typer.Option(False),
    youth: bool = typer.Option(False),
    remote: bool = typer.Option(False),
    student: bool = typer.Option(False),
    insecure_channel: bool = typer.Option(False),
    timekeeping_method: Optional[str] = typer.Option(None),
    bank_details_received: bool = typer.Option(False),
    pension_fund_name: Optional[str] = typer.Option(None),
    tax_coordination_received: bool = typer.Option(False),
    national_insurance_coordination_received: bool = typer.Option(False),
    employment_notice_status: str = typer.Option("missing"),
    equipment_required: bool = typer.Option(False),
    equipment_form_signed: bool = typer.Option(False),
) -> None:
    """Generate a checklist from a record, JSON file, or direct options."""

    if id:
        profile = load_record(id, environment=env)
        profile.language = language
    elif path:
        profile = load_profile_file(path)
        profile.language = language
    else:
        if not name or not start_date:
            raise typer.BadParameter("Pass --id, --path, or both --name and --start-date.")
        profile = _profile_from_options(
            name,
            start_date,
            employment_type,
            role,
            salary_type,
            hourly,
            other_employer,
            active_pension,
            no_active_pension,
            foreign_worker,
            youth,
            remote,
            student,
            language,
            insecure_channel,
            timekeeping_method,
            bank_details_received,
            pension_fund_name,
            tax_coordination_received,
            national_insurance_coordination_received,
            employment_notice_status,
            equipment_required,
            equipment_form_signed,
        )
    text = generate_hebrew_checklist(profile) if language == "he" else generate_checklist(profile)
    typer.echo(text)


def message(
    name: str = typer.Option(...),
    due_date: str = typer.Option(...),
    language: str = typer.Option("en"),
) -> None:
    """Generate an employee-facing document request."""

    typer.echo(generate_employee_message(name, due_date, language))


def sample(path: Path = typer.Option(Path("onboarding-sample.json"))) -> None:
    """Write a sample onboarding profile."""

    payload = {
        "employee": {
            "full_name": "Dana Levi",
            "start_date": "01-09-2026",
            "employment_type": "employee",
            "role": "Sales Coordinator",
            "salary_type": "monthly",
            "has_other_employer": True,
            "has_active_pension": True
        },
        "payroll": {
            "monthly_salary_nis": 12000
        },
        "documents": {
            "form_101": "pending",
            "bank_details": "received",
            "tax_coordination": "missing",
            "national_insurance_coordination": "missing",
            "employment_notice": "drafted"
        }
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    typer.echo(json.dumps({"ok": True, "path": str(path)}, ensure_ascii=False, indent=2))


app.command()(create)
app.command()(validate)
app.command()(checklist)
app.command()(message)
app.command()(sample)


if __name__ == "__main__":
    app()
