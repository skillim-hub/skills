#!/usr/bin/env python3
"""Command-line helper for structured Israeli labor-law triage."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

import typer

from labor_law_advisor_client import LaborLawAdvisor


app = typer.Typer(
    name="labor-law-advisor",
    help="Structured Israeli labor-law calculations and triage. Verify date-sensitive rates before payroll action.",
    no_args_is_help=True,
)


def _advisor() -> LaborLawAdvisor:
    return LaborLawAdvisor()


def _validate_env(env: str) -> str:
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    return env


def _case_store_path() -> Path:
    configured = os.getenv("LABOR_LAW_ADVISOR_CASE_STORE")
    return Path(configured) if configured else Path.cwd() / ".labor-law-advisor-cases.json"


def _load_case_store() -> dict[str, Any]:
    path = _case_store_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"case store is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise typer.BadParameter(f"case store root must be an object: {path}")
    return data


def _save_case(case: dict[str, Any]) -> None:
    path = _case_store_path()
    store = _load_case_store()
    cases = store.setdefault("cases", {})
    cases[case["case_id"]] = case
    path.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _print(data: dict) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


def _env_float(name: str, default: Optional[float] = None) -> Optional[float]:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    return float(value)


@app.command("create-case")
def create_case(
    category: str = typer.Option(..., help="Case category, such as minimum-wage, overtime, severance, or parental-rights."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
    subject: Optional[str] = typer.Option(None, help="Optional local case subject."),
) -> None:
    """Create a local advisory case identifier for chained CLI workflows."""

    env = _validate_env(env)
    result = _advisor().create_case(category=category, environment=env, subject=subject)
    data = result.to_dict()
    _save_case(data)
    _print(data)


@app.command("case-summary")
def case_summary(
    case_id: str = typer.Option(..., help="Local case identifier returned by create-case."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Return a deterministic local summary for a case identifier."""

    env = _validate_env(env)
    store = _load_case_store()
    stored = store.get("cases", {}).get(case_id)
    if stored is None:
        raise typer.BadParameter("case_id was not found in the local case store")
    data = dict(stored)
    data["operation"] = "case_summary"
    data["environment"] = env
    data.setdefault("notes", []).append("Local helper record only; not a government filing number.")
    _print(data)


@app.command("min-wage")
def min_wage(
    monthly_salary: Optional[float] = typer.Option(None, help="Gross monthly base salary in ₪."),
    hourly_wage: Optional[float] = typer.Option(None, help="Hourly base wage in ₪."),
    regular_hours: Optional[float] = typer.Option(None, help="Regular hours in the pay period for hourly checks."),
    position_fraction: float = typer.Option(1.0, help="Position fraction, e.g. 0.5 for 50%."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Check minimum wage compliance."""

    monthly_salary = _env_float("LABOR_LAW_ADVISOR_MONTHLY_SALARY", monthly_salary)
    hourly_wage = _env_float("LABOR_LAW_ADVISOR_HOURLY_WAGE", hourly_wage)
    regular_hours = _env_float("LABOR_LAW_ADVISOR_REGULAR_HOURS", regular_hours)
    position_fraction = float(os.getenv("LABOR_LAW_ADVISOR_POSITION_FRACTION", position_fraction))
    result = _advisor().minimum_wage(
        monthly_salary=monthly_salary,
        hourly_wage=hourly_wage,
        regular_hours=regular_hours,
        position_fraction=position_fraction,
    )
    data = result.to_dict()
    data["environment"] = env
    _print(data)


@app.command("overtime")
def overtime(
    hourly_rate: float = typer.Option(..., help="Hourly wage in ₪."),
    daily_hours: float = typer.Option(..., help="Hours worked in the day."),
    daily_threshold: float = typer.Option(8.6, help="Regular daily threshold."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Calculate daily overtime blocks."""

    hourly_rate = float(os.getenv("LABOR_LAW_ADVISOR_HOURLY_RATE", hourly_rate))
    daily_hours = float(os.getenv("LABOR_LAW_ADVISOR_DAILY_HOURS", daily_hours))
    daily_threshold = float(os.getenv("LABOR_LAW_ADVISOR_DAILY_THRESHOLD", daily_threshold))
    result = _advisor().overtime(hourly_rate=hourly_rate, daily_hours=daily_hours, daily_threshold=daily_threshold)
    data = result.to_dict()
    data["environment"] = env
    _print(data)


@app.command("weekly-overtime")
def weekly_overtime(
    weekly_hours: float = typer.Option(..., help="Total weekly hours."),
    weekly_threshold: float = typer.Option(42.0, help="Weekly threshold."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Return weekly overtime hours before daily double-counting adjustments."""

    weekly_hours = float(os.getenv("LABOR_LAW_ADVISOR_WEEKLY_HOURS", weekly_hours))
    weekly_threshold = float(os.getenv("LABOR_LAW_ADVISOR_WEEKLY_THRESHOLD", weekly_threshold))
    hours = _advisor().weekly_overtime_hours(weekly_hours=weekly_hours, weekly_threshold=weekly_threshold)
    _print({"operation": "weekly_overtime", "weekly_overtime_hours": hours, "environment": env})


@app.command("severance")
def severance(
    monthly_salary: float = typer.Option(..., help="Last monthly salary in ₪."),
    years: float = typer.Option(0.0, help="Full years of service."),
    months: float = typer.Option(0.0, help="Additional months, below 12."),
    section14_balance: Optional[float] = typer.Option(None, help="Severance component already in pension/provident fund."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Estimate statutory severance and possible Section 14 top-up."""

    monthly_salary = float(os.getenv("LABOR_LAW_ADVISOR_MONTHLY_SALARY", monthly_salary))
    years = float(os.getenv("LABOR_LAW_ADVISOR_TENURE_YEARS", years))
    months = float(os.getenv("LABOR_LAW_ADVISOR_TENURE_MONTHS", months))
    section14_balance = _env_float("LABOR_LAW_ADVISOR_SECTION14_BALANCE", section14_balance)
    result = _advisor().severance(
        monthly_salary=monthly_salary,
        years=years,
        months=months,
        section14_balance=section14_balance,
    )
    data = result.to_dict()
    data["environment"] = env
    _print(data)


@app.command("sick-pay")
def sick_pay(
    daily_wage: float = typer.Option(..., help="Daily wage in ₪."),
    sick_days: int = typer.Option(..., help="Number of sick days."),
    accrued_days: Optional[float] = typer.Option(None, help="Available accrued sick days."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Calculate statutory sick-pay baseline."""

    daily_wage = float(os.getenv("LABOR_LAW_ADVISOR_DAILY_WAGE", daily_wage))
    sick_days = int(os.getenv("LABOR_LAW_ADVISOR_SICK_DAYS", sick_days))
    accrued_days = _env_float("LABOR_LAW_ADVISOR_ACCRUED_SICK_DAYS", accrued_days)
    result = _advisor().sick_pay(daily_wage=daily_wage, sick_days=sick_days, accrued_days=accrued_days)
    data = result.to_dict()
    data["environment"] = env
    _print(data)


@app.command("vacation")
def vacation(
    years: int = typer.Option(..., help="Years of service."),
    workweek_days: int = typer.Option(5, help="5 or 6 day workweek."),
    position_fraction: float = typer.Option(1.0, help="Position fraction."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Return statutory annual vacation baseline."""

    years = int(os.getenv("LABOR_LAW_ADVISOR_TENURE_YEARS", years))
    workweek_days = int(os.getenv("LABOR_LAW_ADVISOR_WORKWEEK_DAYS", workweek_days))
    position_fraction = float(os.getenv("LABOR_LAW_ADVISOR_POSITION_FRACTION", position_fraction))
    result = _advisor().vacation(
        years_of_service=years,
        workweek_days=workweek_days,
        position_fraction=position_fraction,
    )
    data = result.to_dict()
    data["environment"] = env
    _print(data)


@app.command("collective-check")
def collective_check(
    sector: str = typer.Option(..., help="Sector or industry."),
    employer_type: str = typer.Option("", help="Employer type or trade association if known."),
    worker_role: str = typer.Option("", help="Worker role."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Triage possible collective agreement or extension order coverage."""

    public_sector = employer_type.strip().lower() in {"public", "government", "municipality", "public-sector"}
    result = _advisor().collective_check(
        sector=" ".join(part for part in [sector, employer_type, worker_role] if part),
        public_sector=public_sector,
    )
    data = result.to_dict()
    data["environment"] = env
    _print(data)


@app.command("classification-risk")
def classification_risk(
    exclusive_service: bool = typer.Option(False, help="Works mainly for one payer."),
    integrated_into_business: bool = typer.Option(False, help="Integrated into the business organization."),
    uses_employer_tools: bool = typer.Option(False, help="Uses payer equipment or systems."),
    sets_own_schedule: bool = typer.Option(False, help="Controls schedule independently."),
    invoices_multiple_clients: bool = typer.Option(False, help="Invoices multiple unrelated clients."),
    hires_substitutes: bool = typer.Option(False, help="Can send substitutes or employees."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Assess employee-vs-contractor misclassification risk."""

    result = _advisor().classification_risk(
        integrated_in_business=integrated_into_business,
        fixed_schedule=not sets_own_schedule,
        uses_company_tools=uses_employer_tools,
        single_client=exclusive_service and not invoices_multiple_clients,
        can_send_substitute=hires_substitutes,
        invoices_with_vat=invoices_multiple_clients,
    )
    data = result.to_dict()
    data["environment"] = env
    _print(data)


@app.command("parental-rights")
def parental_rights(
    pregnant: bool = typer.Option(False, help="Pregnancy status."),
    fertility_treatment: bool = typer.Option(False, help="Fertility treatment status."),
    after_parental_leave: bool = typer.Option(False, help="Recently returned from birth and parenting period."),
    dismissal_or_change: bool = typer.Option(False, help="Dismissal, non-renewal, pay cut, or hours reduction is contemplated."),
    tenure_months: int = typer.Option(0, help="Tenure in months."),
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
) -> None:
    """Triage protected parental or pregnancy-related status."""

    employer_action = "dismissal" if dismissal_or_change else "none"
    result = _advisor().parental_rights_triage(
        pregnant=pregnant,
        fertility_treatment=fertility_treatment,
        returned_from_parental_leave=after_parental_leave,
        employer_action=employer_action,
        months_employed=tenure_months,
    )
    data = result.to_dict()
    data["environment"] = env
    _print(data)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
