"""Installable package for the Annual Leave and Sick-Day Tracker."""

from .client import (
    ANNUAL_ENTITLEMENT_NET_WORKDAYS,
    AbsenceType,
    BalanceSnapshot,
    EmployeeProfile,
    LeaveEvent,
    LeaveTrackerClient,
    LeaveTrackerError,
    UnknownEmployeeError,
    annual_accrual_between,
    annual_entitlement_days,
    completed_years_on,
    count_workdays,
    format_il_date,
    money,
    parse_date,
    seniority_year_index,
    sick_accrual_between,
    sick_pay_equivalent_days,
    write_template_csvs,
)

__version__ = "1.2.0"

__all__ = [
    "ANNUAL_ENTITLEMENT_NET_WORKDAYS",
    "AbsenceType",
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
