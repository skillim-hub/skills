#!/usr/bin/env python3
"""Structured leave tracker for Israeli annual leave, sick days, miluim, birth and parenthood leave, and mourning days.

This module is intentionally self-contained. It does not call external services and it keeps all
statutory values configurable because Israeli employment terms often vary by work week, sector,
collective agreement, personal contract, and later legal updates.
"""
from __future__ import annotations

import asyncio
import csv
import dataclasses
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


class LeaveTrackerError(ValueError):
    """Base exception for leave tracker validation errors."""


class UnknownEmployeeError(LeaveTrackerError):
    """Raised when an event references an unknown employee."""


class AbsenceType(str, Enum):
    ANNUAL = "annual"
    SICK = "sick"
    MILUIM = "miluim"
    PARENTAL = "parental"
    MOURNING = "mourning"


ISRAEL_WORKDAYS_BY_WEEK: Dict[int, set[int]] = {
    # Python weekday(): Monday=0 ... Sunday=6
    5: {6, 0, 1, 2, 3},       # Sunday-Thursday
    6: {6, 0, 1, 2, 3, 4},    # Sunday-Friday
}

# Default net workday entitlement table for the statutory floor in net workdays.
# Use annual_override_days when a collective agreement, extension order, sector rule,
# personal contract, or employer policy is more generous. For many 5-day workplaces,
# the short-workweek extension order may grant higher net days from year 6 onward.
ANNUAL_ENTITLEMENT_NET_WORKDAYS: Dict[int, Dict[int, float]] = {
    5: {1: 12, 2: 12, 3: 12, 4: 12, 5: 12, 6: 14, 7: 15, 8: 16, 9: 17, 10: 18, 11: 19, 12: 20, 13: 20, 14: 20},
    6: {1: 14, 2: 14, 3: 14, 4: 14, 5: 14, 6: 16, 7: 18, 8: 19, 9: 20, 10: 21, 11: 22, 12: 23, 13: 24, 14: 24},
}


def money(value: float | Decimal) -> Decimal:
    """Round monetary or day-equivalent values to two decimals."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def parse_date(value: str | date) -> date:
    """Parse ISO YYYY-MM-DD or Israeli DD/MM/YYYY dates."""
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise LeaveTrackerError(f"Invalid date '{value}'. Use YYYY-MM-DD or DD/MM/YYYY.")


def format_il_date(value: date) -> str:
    """Format a date as DD/MM/YYYY."""
    return value.strftime("%d/%m/%Y")


def daterange(start: date, end: date) -> Iterable[date]:
    """Yield all dates between start and end, inclusive."""
    if end < start:
        raise LeaveTrackerError("end_date must be on or after start_date")
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def count_workdays(start: str | date, end: str | date, work_week_days: int = 5) -> float:
    """Count Israeli workdays between two dates, inclusive."""
    start_date = parse_date(start)
    end_date = parse_date(end)
    if work_week_days not in ISRAEL_WORKDAYS_BY_WEEK:
        raise LeaveTrackerError("work_week_days must be 5 or 6")
    allowed = ISRAEL_WORKDAYS_BY_WEEK[work_week_days]
    return float(sum(1 for day in daterange(start_date, end_date) if day.weekday() in allowed))


def months_touched(start: date, end: date) -> int:
    """Count calendar months touched by an employment period."""
    if end < start:
        return 0
    return (end.year - start.year) * 12 + end.month - start.month + 1


def completed_years_on(hire_date: date, as_of: date) -> int:
    """Return completed employment years as of a given date."""
    if as_of < hire_date:
        return 0
    years = as_of.year - hire_date.year
    if (as_of.month, as_of.day) < (hire_date.month, hire_date.day):
        years -= 1
    return max(0, years)


def seniority_year_index(hire_date: date, as_of: date) -> int:
    """Return the current statutory seniority year index, starting at 1."""
    return completed_years_on(hire_date, as_of) + 1


def annual_entitlement_days(hire_date: str | date, as_of: str | date, work_week_days: int = 5, override: Optional[float] = None) -> float:
    """Return annual entitlement for the seniority year in net workdays."""
    if override is not None:
        return float(override)
    hd = parse_date(hire_date)
    ad = parse_date(as_of)
    if work_week_days not in ANNUAL_ENTITLEMENT_NET_WORKDAYS:
        raise LeaveTrackerError("work_week_days must be 5 or 6")
    table = ANNUAL_ENTITLEMENT_NET_WORKDAYS[work_week_days]
    index = min(seniority_year_index(hd, ad), max(table))
    return float(table[index])


def annual_accrual_between(
    hire_date: str | date,
    as_of: str | date,
    work_week_days: int = 5,
    annual_override_days: Optional[float] = None,
) -> float:
    """Accrue annual leave from hire date to as_of using calendar-year proration.

    The calculation assumes the employee remains employed through as_of and accrues a fraction of
    each calendar year's entitlement based on months touched in that year. Round final balance to
    two decimals; do not round each month.
    """
    hd = parse_date(hire_date)
    ad = parse_date(as_of)
    if ad < hd:
        return 0.0

    total = Decimal("0")
    for year in range(hd.year, ad.year + 1):
        period_start = max(hd, date(year, 1, 1))
        period_end = min(ad, date(year, 12, 31))
        months = months_touched(period_start, period_end)
        entitlement = Decimal(str(annual_entitlement_days(hd, date(year, 12, 31), work_week_days, annual_override_days)))
        total += entitlement * Decimal(months) / Decimal(12)
    return float(money(total))


def sick_accrual_between(
    hire_date: str | date,
    as_of: str | date,
    monthly_accrual: float = 1.5,
    cap_days: float = 90,
) -> float:
    """Accrue sick days at the configured monthly rate, capped by the configured maximum."""
    hd = parse_date(hire_date)
    ad = parse_date(as_of)
    accrued = Decimal(months_touched(hd, ad)) * Decimal(str(monthly_accrual))
    capped = min(accrued, Decimal(str(cap_days)))
    return float(money(capped))


def sick_pay_equivalent_days(days: float) -> float:
    """Calculate statutory paid-day equivalents for one continuous sick event.

    Default schedule: first day 0%, second and third days 50%, fourth day onward 100%.
    """
    remaining = Decimal(str(days))
    if remaining <= 0:
        return 0.0
    paid = Decimal("0")
    # first day
    first = min(remaining, Decimal("1"))
    paid += first * Decimal("0")
    remaining -= first
    # second and third day
    second_third = min(remaining, Decimal("2"))
    paid += second_third * Decimal("0.5")
    remaining -= second_third
    # fourth onward
    if remaining > 0:
        paid += remaining
    return float(money(paid))


@dataclass(slots=True)
class EmployeeProfile:
    employee_id: str
    name: str
    hire_date: date | str
    work_week_days: int = 5
    opening_annual_balance: float = 0.0
    opening_sick_balance: float = 0.0
    annual_override_days: Optional[float] = None
    sick_monthly_accrual: float = 1.5
    sick_cap_days: float = 90.0
    mourning_paid_days_limit: float = 7.0
    notes: str = ""

    def __post_init__(self) -> None:
        self.hire_date = parse_date(self.hire_date)
        if self.work_week_days not in ISRAEL_WORKDAYS_BY_WEEK:
            raise LeaveTrackerError("work_week_days must be 5 or 6")
        if not self.employee_id:
            raise LeaveTrackerError("employee_id is required")
        if self.sick_cap_days < 0 or self.sick_monthly_accrual < 0:
            raise LeaveTrackerError("sick accrual settings must be non-negative")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "hire_date": format_il_date(self.hire_date),
            "work_week_days": self.work_week_days,
            "opening_annual_balance": self.opening_annual_balance,
            "opening_sick_balance": self.opening_sick_balance,
            "annual_override_days": self.annual_override_days,
            "sick_monthly_accrual": self.sick_monthly_accrual,
            "sick_cap_days": self.sick_cap_days,
            "mourning_paid_days_limit": self.mourning_paid_days_limit,
            "notes": self.notes,
        }


@dataclass(slots=True)
class LeaveEvent:
    employee_id: str
    absence_type: AbsenceType | str
    start_date: date | str
    end_date: date | str
    days: Optional[float] = None
    approved: bool = True
    reference: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        self.start_date = parse_date(self.start_date)
        self.end_date = parse_date(self.end_date)
        if self.end_date < self.start_date:
            raise LeaveTrackerError("event end_date must be on or after start_date")
        self.absence_type = AbsenceType(self.absence_type)
        if self.days is not None and self.days < 0:
            raise LeaveTrackerError("event days must be non-negative")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "absence_type": self.absence_type.value,
            "start_date": format_il_date(self.start_date),
            "end_date": format_il_date(self.end_date),
            "days": self.days,
            "approved": self.approved,
            "reference": self.reference,
            "notes": self.notes,
        }


@dataclass(slots=True)
class BalanceSnapshot:
    employee_id: str
    as_of: date
    annual_accrued: float
    annual_used: float
    annual_balance: float
    sick_accrued: float
    sick_used: float
    sick_balance: float
    sick_paid_equivalent_days: float
    miluim_days: float
    parental_days: float
    mourning_days: float
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "as_of": format_il_date(self.as_of),
            "annual_accrued": self.annual_accrued,
            "annual_used": self.annual_used,
            "annual_balance": self.annual_balance,
            "sick_accrued": self.sick_accrued,
            "sick_used": self.sick_used,
            "sick_balance": self.sick_balance,
            "sick_paid_equivalent_days": self.sick_paid_equivalent_days,
            "miluim_days": self.miluim_days,
            "parental_days": self.parental_days,
            "mourning_days": self.mourning_days,
            "warnings": "; ".join(self.warnings),
        }


class LeaveTrackerClient:
    """In-memory leave tracker with sync and async APIs."""

    def __init__(self, employees: Optional[Sequence[EmployeeProfile]] = None, events: Optional[Sequence[LeaveEvent]] = None) -> None:
        self.employees: Dict[str, EmployeeProfile] = {}
        self.events: List[LeaveEvent] = []
        for employee in employees or []:
            self.add_employee(employee)
        for event in events or []:
            self.record_event(event)

    def add_employee(self, employee: EmployeeProfile) -> EmployeeProfile:
        self.employees[employee.employee_id] = employee
        return employee

    def record_event(self, event: LeaveEvent) -> LeaveEvent:
        if event.employee_id not in self.employees:
            raise UnknownEmployeeError(f"Unknown employee_id '{event.employee_id}'")
        if event.days is None:
            employee = self.employees[event.employee_id]
            event.days = count_workdays(event.start_date, event.end_date, employee.work_week_days)
        self.events.append(event)
        return event

    def employee_events(self, employee_id: str, as_of: str | date) -> List[LeaveEvent]:
        if employee_id not in self.employees:
            raise UnknownEmployeeError(f"Unknown employee_id '{employee_id}'")
        cutoff = parse_date(as_of)
        return [
            event for event in self.events
            if event.employee_id == employee_id and event.approved and event.start_date <= cutoff
        ]

    def balance(self, employee_id: str, as_of: str | date) -> BalanceSnapshot:
        if employee_id not in self.employees:
            raise UnknownEmployeeError(f"Unknown employee_id '{employee_id}'")
        employee = self.employees[employee_id]
        cutoff = parse_date(as_of)
        events = self.employee_events(employee_id, cutoff)

        annual_accrued_total = employee.opening_annual_balance + annual_accrual_between(
            employee.hire_date, cutoff, employee.work_week_days, employee.annual_override_days
        )
        sick_accrued_total = min(
            employee.opening_sick_balance + sick_accrual_between(employee.hire_date, cutoff, employee.sick_monthly_accrual, employee.sick_cap_days),
            employee.sick_cap_days,
        )

        annual_used = sum(float(event.days or 0) for event in events if event.absence_type == AbsenceType.ANNUAL)
        sick_events = [event for event in events if event.absence_type == AbsenceType.SICK]
        sick_used = sum(float(event.days or 0) for event in sick_events)
        sick_paid = sum(sick_pay_equivalent_days(float(event.days or 0)) for event in sick_events)
        miluim = sum(float(event.days or 0) for event in events if event.absence_type == AbsenceType.MILUIM)
        parental = sum(float(event.days or 0) for event in events if event.absence_type == AbsenceType.PARENTAL)
        mourning = sum(float(event.days or 0) for event in events if event.absence_type == AbsenceType.MOURNING)

        annual_balance = float(money(Decimal(str(annual_accrued_total)) - Decimal(str(annual_used))))
        sick_balance = float(money(Decimal(str(sick_accrued_total)) - Decimal(str(sick_used))))

        warnings: List[str] = []
        if annual_balance < 0:
            warnings.append("Annual leave balance is negative; confirm advance leave approval or payroll deduction rules.")
        if sick_balance < 0:
            warnings.append("Sick balance is negative; confirm whether unpaid sick leave or other arrangement applies.")
        for event in sick_events:
            if event.days and event.days > 30:
                warnings.append("Long sick event detected; verify medical certificates and disability/National Insurance handling.")
        if mourning > employee.mourning_paid_days_limit:
            warnings.append("Mourning absence exceeds default paid-day limit; verify collective agreement or employer policy.")

        return BalanceSnapshot(
            employee_id=employee_id,
            as_of=cutoff,
            annual_accrued=float(money(annual_accrued_total)),
            annual_used=float(money(annual_used)),
            annual_balance=annual_balance,
            sick_accrued=float(money(sick_accrued_total)),
            sick_used=float(money(sick_used)),
            sick_balance=sick_balance,
            sick_paid_equivalent_days=float(money(sick_paid)),
            miluim_days=float(money(miluim)),
            parental_days=float(money(parental)),
            mourning_days=float(money(mourning)),
            warnings=warnings,
        )

    def balances(self, as_of: str | date) -> List[BalanceSnapshot]:
        return [self.balance(employee_id, as_of) for employee_id in sorted(self.employees)]

    async def abalance(self, employee_id: str, as_of: str | date) -> BalanceSnapshot:
        return await asyncio.to_thread(self.balance, employee_id, as_of)

    async def abalances(self, as_of: str | date) -> List[BalanceSnapshot]:
        return await asyncio.to_thread(self.balances, as_of)

    @classmethod
    def from_csv(cls, employees_csv: str | Path, events_csv: Optional[str | Path] = None) -> "LeaveTrackerClient":
        client = cls()
        with Path(employees_csv).open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                client.add_employee(EmployeeProfile(
                    employee_id=row["employee_id"],
                    name=row.get("name", row["employee_id"]),
                    hire_date=row["hire_date"],
                    work_week_days=int(row.get("work_week_days") or 5),
                    opening_annual_balance=float(row.get("opening_annual_balance") or 0),
                    opening_sick_balance=float(row.get("opening_sick_balance") or 0),
                    annual_override_days=float(row["annual_override_days"]) if row.get("annual_override_days") else None,
                    sick_monthly_accrual=float(row.get("sick_monthly_accrual") or 1.5),
                    sick_cap_days=float(row.get("sick_cap_days") or 90),
                    mourning_paid_days_limit=float(row.get("mourning_paid_days_limit") or 7),
                    notes=row.get("notes", ""),
                ))
        if events_csv:
            with Path(events_csv).open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    client.record_event(LeaveEvent(
                        employee_id=row["employee_id"],
                        absence_type=row["absence_type"],
                        start_date=row["start_date"],
                        end_date=row["end_date"],
                        days=float(row["days"]) if row.get("days") else None,
                        approved=str(row.get("approved", "true")).strip().lower() not in {"false", "0", "no", "לא"},
                        reference=row.get("reference", ""),
                        notes=row.get("notes", ""),
                    ))
        return client

    def export_balances_csv(self, output_path: str | Path, as_of: str | date) -> Path:
        path = Path(output_path)
        rows = [snapshot.to_dict() for snapshot in self.balances(as_of)]
        fieldnames = [
            "employee_id", "as_of", "annual_accrued", "annual_used", "annual_balance",
            "sick_accrued", "sick_used", "sick_balance", "sick_paid_equivalent_days",
            "miluim_days", "parental_days", "mourning_days", "warnings",
        ]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return path


EMPLOYEE_TEMPLATE_FIELDS = [
    "employee_id", "name", "hire_date", "work_week_days", "opening_annual_balance",
    "opening_sick_balance", "annual_override_days", "sick_monthly_accrual",
    "sick_cap_days", "mourning_paid_days_limit", "notes",
]

EVENT_TEMPLATE_FIELDS = [
    "employee_id", "absence_type", "start_date", "end_date", "days", "approved", "reference", "notes",
]


def write_template_csvs(directory: str | Path) -> Tuple[Path, Path]:
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    employees_path = output / "employees.csv"
    events_path = output / "events.csv"
    with employees_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EMPLOYEE_TEMPLATE_FIELDS)
        writer.writeheader()
        writer.writerow({
            "employee_id": "E001",
            "name": "Dana Levi",
            "hire_date": "01/01/2024",
            "work_week_days": 5,
            "opening_annual_balance": 0,
            "opening_sick_balance": 0,
            "annual_override_days": "",
            "sick_monthly_accrual": 1.5,
            "sick_cap_days": 90,
            "mourning_paid_days_limit": 7,
            "notes": "Example employee",
        })
    with events_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EVENT_TEMPLATE_FIELDS)
        writer.writeheader()
        writer.writerow({
            "employee_id": "E001",
            "absence_type": "annual",
            "start_date": "18/08/2024",
            "end_date": "22/08/2024",
            "days": "",
            "approved": "true",
            "reference": "VAC-2024-001",
            "notes": "Auto-counts Sunday-Thursday workdays",
        })
    return employees_path, events_path


__all__ = [
    "AbsenceType",
    "ANNUAL_ENTITLEMENT_NET_WORKDAYS",
    "BalanceSnapshot",
    "EmployeeProfile",
    "LeaveEvent",
    "LeaveTrackerClient",
    "LeaveTrackerError",
    "UnknownEmployeeError",
    "annual_accrual_between",
    "annual_entitlement_days",
    "completed_years_on",
    "count_workdays",
    "format_il_date",
    "money",
    "parse_date",
    "seniority_year_index",
    "sick_accrual_between",
    "sick_pay_equivalent_days",
    "write_template_csvs",
]
