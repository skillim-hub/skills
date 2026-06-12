"""Structured Bituach Leumi payment scheduler helper.

Use this module for local planning, reminders, CSV exports, JSON exports, and
calendar events. The calculations are planning aids only. Verify statutory
amounts, classifications, and deadlines in the official Bituach Leumi channels
before payment.
"""

from __future__ import annotations

import asyncio
import calendar
import csv
import io
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


VERSION = "2.2.0"
DEFAULT_CURRENCY = "ILS"


class SchedulerError(ValueError):
    """Base validation error for scheduler input."""


class BusinessType(str, Enum):
    SELF_EMPLOYED = "self-employed"
    EMPLOYER = "employer"
    SMALL_BUSINESS = "small-business"
    CONSUMER = "consumer"


class AdjustmentPolicy(str, Enum):
    NEXT_BUSINESS_DAY = "next-business-day"
    PREVIOUS_BUSINESS_DAY = "previous-business-day"
    KEEP_DATE = "keep-date"


class PaymentStatus(str, Enum):
    OVERDUE = "overdue"
    DUE_TODAY = "due-today"
    DUE_SOON = "due-soon"
    UPCOMING = "upcoming"
    PAID = "paid"


@dataclass(frozen=True)
class ContributionPolicy:
    """Configurable 2026 planning rates. Treat values as configuration, not legal advice."""

    reduced_threshold_nis: float = 7703.0
    self_employed_reduced_rate: float = 0.0770
    self_employed_regular_rate: float = 0.1800
    employer_combined_reduced_rate: float = 0.0878
    employer_combined_regular_rate: float = 0.1977
    consumer_monthly_default_nis: float = 266.0
    minimum_monthly_income_nis: float = 0.0

    def validate(self) -> None:
        if self.reduced_threshold_nis <= 0:
            raise SchedulerError("reduced_threshold_nis must be positive")
        rates = [
            self.self_employed_reduced_rate,
            self.self_employed_regular_rate,
            self.employer_combined_reduced_rate,
            self.employer_combined_regular_rate,
        ]
        if any(rate < 0 or rate > 1 for rate in rates):
            raise SchedulerError("rates must be between 0 and 1")
        if self.consumer_monthly_default_nis < 0:
            raise SchedulerError("consumer_monthly_default_nis cannot be negative")


@dataclass(frozen=True)
class ScheduleOptions:
    start_month: date
    months: int = 12
    due_day: int = 15
    adjustment_policy: AdjustmentPolicy = AdjustmentPolicy.NEXT_BUSINESS_DAY
    weekend_days: frozenset[int] = frozenset({4, 5})  # Friday, Saturday
    holidays: frozenset[date] = frozenset()
    reminder_days_before: tuple[int, ...] = (14, 7, 3, 1)
    reminder_adjustment_policy: AdjustmentPolicy = AdjustmentPolicy.PREVIOUS_BUSINESS_DAY

    def validate(self) -> None:
        if self.months <= 0 or self.months > 60:
            raise SchedulerError("months must be between 1 and 60")
        if self.due_day < 1 or self.due_day > 28:
            raise SchedulerError("due_day must be between 1 and 28 for predictable monthly schedules")
        if any(day < 0 or day > 365 for day in self.reminder_days_before):
            raise SchedulerError("reminder_days_before values must be between 0 and 365")
        if len(set(self.reminder_days_before)) != len(self.reminder_days_before):
            raise SchedulerError("reminder_days_before cannot contain duplicates")


@dataclass(frozen=True)
class BusinessProfile:
    payer_name: str
    business_type: BusinessType
    israeli_id_or_company_hint: str | None = None
    monthly_income_nis: float | None = None
    monthly_payroll_nis: float | None = None
    amount_override_nis: float | None = None
    policy: ContributionPolicy = field(default_factory=ContributionPolicy)

    def validate(self) -> None:
        if not self.payer_name or not self.payer_name.strip():
            raise SchedulerError("payer_name is required")
        self.policy.validate()
        if self.amount_override_nis is not None and self.amount_override_nis < 0:
            raise SchedulerError("amount_override_nis cannot be negative")
        if self.monthly_income_nis is not None and self.monthly_income_nis < 0:
            raise SchedulerError("monthly_income_nis cannot be negative")
        if self.monthly_payroll_nis is not None and self.monthly_payroll_nis < 0:
            raise SchedulerError("monthly_payroll_nis cannot be negative")
        if self.business_type in {BusinessType.SELF_EMPLOYED, BusinessType.SMALL_BUSINESS}:
            if self.monthly_income_nis is None and self.amount_override_nis is None:
                raise SchedulerError("monthly_income_nis or amount_override_nis is required")
        if self.business_type == BusinessType.EMPLOYER:
            if self.monthly_payroll_nis is None and self.amount_override_nis is None:
                raise SchedulerError("monthly_payroll_nis or amount_override_nis is required")


@dataclass(frozen=True)
class Reminder:
    date: date
    days_before_due: int
    channel_hint: str = "calendar"
    note: str = "Prepare documents, verify amount, and pay before the adjusted due date."


@dataclass(frozen=True)
class PaymentObligation:
    obligation_id: str
    payer_name: str
    business_type: BusinessType
    period_start: date
    period_end: date
    statutory_due_date: date
    adjusted_due_date: date
    amount_nis: float
    currency: str
    status: PaymentStatus
    reminders: tuple[Reminder, ...]
    actions: tuple[str, ...]
    source_note: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["business_type"] = self.business_type.value
        data["status"] = self.status.value
        for key in ("period_start", "period_end", "statutory_due_date", "adjusted_due_date"):
            data[key] = getattr(self, key).isoformat()
        data["reminders"] = [
            {
                "date": reminder.date.isoformat(),
                "days_before_due": reminder.days_before_due,
                "channel_hint": reminder.channel_hint,
                "note": reminder.note,
            }
            for reminder in self.reminders
        ]
        return data


@dataclass(frozen=True)
class PaymentPlan:
    generated_at: datetime
    options: ScheduleOptions
    profile: BusinessProfile
    obligations: tuple[PaymentObligation, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at.astimezone(timezone.utc).isoformat(),
            "profile": {
                "payer_name": self.profile.payer_name,
                "business_type": self.profile.business_type.value,
                "israeli_id_or_company_hint": self.profile.israeli_id_or_company_hint,
                "monthly_income_nis": self.profile.monthly_income_nis,
                "monthly_payroll_nis": self.profile.monthly_payroll_nis,
                "amount_override_nis": self.profile.amount_override_nis,
            },
            "options": {
                "start_month": self.options.start_month.isoformat(),
                "months": self.options.months,
                "due_day": self.options.due_day,
                "adjustment_policy": self.options.adjustment_policy.value,
                "weekend_days": sorted(self.options.weekend_days),
                "holidays": sorted(day.isoformat() for day in self.options.holidays),
                "reminder_days_before": list(self.options.reminder_days_before),
                "reminder_adjustment_policy": self.options.reminder_adjustment_policy.value,
            },
            "obligations": [obligation.to_dict() for obligation in self.obligations],
        }


def parse_date(value: str) -> date:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    try:
        return datetime.strptime(value, "%Y-%m").date().replace(day=1)
    except ValueError as exc:
        raise SchedulerError("date must be YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY, or YYYY-MM") from exc


def parse_business_type(value: str) -> BusinessType:
    normalized = value.strip().lower().replace("_", "-")
    aliases = {
        "freelancer": BusinessType.SELF_EMPLOYED,
        "atzmai": BusinessType.SELF_EMPLOYED,
        "עצמאי": BusinessType.SELF_EMPLOYED,
        "company": BusinessType.EMPLOYER,
        "employer": BusinessType.EMPLOYER,
        "consumer": BusinessType.CONSUMER,
        "household": BusinessType.CONSUMER,
        "small-business": BusinessType.SMALL_BUSINESS,
        "small_business": BusinessType.SMALL_BUSINESS,
    }
    if normalized in aliases:
        return aliases[normalized]
    try:
        return BusinessType(normalized)
    except ValueError as exc:
        raise SchedulerError(f"unsupported business type: {value}") from exc


def parse_adjustment_policy(value: str) -> AdjustmentPolicy:
    normalized = value.strip().lower().replace("_", "-")
    try:
        return AdjustmentPolicy(normalized)
    except ValueError as exc:
        raise SchedulerError(f"unsupported adjustment policy: {value}") from exc


def parse_int_list(value: str) -> tuple[int, ...]:
    if not value.strip():
        return tuple()
    try:
        return tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise SchedulerError("expected comma-separated integers") from exc


def first_day_of_month(day: date) -> date:
    return day.replace(day=1)


def last_day_of_month(day: date) -> date:
    _, last_day = calendar.monthrange(day.year, day.month)
    return day.replace(day=last_day)


def add_months(day: date, months: int) -> date:
    month_zero = day.month - 1 + months
    year = day.year + month_zero // 12
    month = month_zero % 12 + 1
    _, last = calendar.monthrange(year, month)
    return date(year, month, min(day.day, last))


def is_business_day(day: date, weekend_days: Iterable[int] = (4, 5), holidays: Iterable[date] = ()) -> bool:
    return day.weekday() not in set(weekend_days) and day not in set(holidays)


def adjust_business_day(
    day: date,
    policy: AdjustmentPolicy,
    weekend_days: Iterable[int] = (4, 5),
    holidays: Iterable[date] = (),
) -> date:
    if policy == AdjustmentPolicy.KEEP_DATE:
        return day
    step = 1 if policy == AdjustmentPolicy.NEXT_BUSINESS_DAY else -1
    adjusted = day
    while not is_business_day(adjusted, weekend_days, holidays):
        adjusted += timedelta(days=step)
    return adjusted


def statutory_due_for_period(period_start: date, due_day: int = 15) -> date:
    return add_months(period_start.replace(day=due_day), 1)


def classify_status(due_date: date, today: date | None = None, paid: bool = False) -> PaymentStatus:
    if paid:
        return PaymentStatus.PAID
    reference = today or date.today()
    if due_date < reference:
        return PaymentStatus.OVERDUE
    if due_date == reference:
        return PaymentStatus.DUE_TODAY
    if due_date <= reference + timedelta(days=7):
        return PaymentStatus.DUE_SOON
    return PaymentStatus.UPCOMING


def format_nis(amount: float) -> str:
    return f"₪{amount:,.2f}"


def estimate_monthly_amount(profile: BusinessProfile) -> float:
    profile.validate()
    if profile.amount_override_nis is not None:
        return round(profile.amount_override_nis, 2)

    policy = profile.policy
    if profile.business_type in {BusinessType.SELF_EMPLOYED, BusinessType.SMALL_BUSINESS}:
        income = max(profile.monthly_income_nis or 0.0, policy.minimum_monthly_income_nis)
        reduced_part = min(income, policy.reduced_threshold_nis)
        regular_part = max(0.0, income - policy.reduced_threshold_nis)
        return round(
            reduced_part * policy.self_employed_reduced_rate
            + regular_part * policy.self_employed_regular_rate,
            2,
        )

    if profile.business_type == BusinessType.EMPLOYER:
        payroll = profile.monthly_payroll_nis or 0.0
        reduced_part = min(payroll, policy.reduced_threshold_nis)
        regular_part = max(0.0, payroll - policy.reduced_threshold_nis)
        return round(
            reduced_part * policy.employer_combined_reduced_rate
            + regular_part * policy.employer_combined_regular_rate,
            2,
        )

    return round(policy.consumer_monthly_default_nis, 2)


def action_items(business_type: BusinessType) -> tuple[str, ...]:
    if business_type == BusinessType.EMPLOYER:
        return (
            "Reconcile payroll totals for the wage month.",
            "Prepare or verify Form 102 reporting data.",
            "Confirm employee and employer contribution totals with payroll records.",
            "Pay through the official payment channel or approved bank arrangement.",
            "Save confirmation, Form 102 copy, and accounting journal entry.",
        )
    if business_type == BusinessType.CONSUMER:
        return (
            "Verify the personal debt, installment, or voluntary-payment amount in the personal area.",
            "Check whether collection fees, linkage, or interest changed.",
            "Pay through the official payment channel.",
            "Save payment confirmation and updated balance.",
        )
    return (
        "Check the current advance assessment and payment voucher.",
        "Compare the estimate with actual profit and accountant guidance.",
        "Update advances when income changes materially.",
        "Pay through the official payment channel or standing order.",
        "Save confirmation and bookkeeping entry.",
    )


def build_reminders(
    due_date: date,
    days_before: Sequence[int],
    adjustment_policy: AdjustmentPolicy,
    weekend_days: Iterable[int],
    holidays: Iterable[date],
) -> tuple[Reminder, ...]:
    reminders: list[Reminder] = []
    for days in sorted(days_before, reverse=True):
        reminder_date = due_date - timedelta(days=days)
        reminder_date = adjust_business_day(reminder_date, adjustment_policy, weekend_days, holidays)
        reminders.append(Reminder(date=reminder_date, days_before_due=days))
    return tuple(reminders)


def make_obligation_id(business_type: BusinessType, period_start: date) -> str:
    return f"BL-{business_type.value}-{period_start:%Y-%m}"


def generate_payment_plan(
    profile: BusinessProfile,
    options: ScheduleOptions,
    *,
    today: date | None = None,
) -> PaymentPlan:
    profile.validate()
    options.validate()

    obligations: list[PaymentObligation] = []
    start_month = first_day_of_month(options.start_month)
    amount = estimate_monthly_amount(profile)

    for offset in range(options.months):
        period_start = add_months(start_month, offset)
        period_end = last_day_of_month(period_start)
        statutory_due = statutory_due_for_period(period_start, options.due_day)
        adjusted_due = adjust_business_day(
            statutory_due,
            options.adjustment_policy,
            options.weekend_days,
            options.holidays,
        )
        reminders = build_reminders(
            adjusted_due,
            options.reminder_days_before,
            options.reminder_adjustment_policy,
            options.weekend_days,
            options.holidays,
        )
        obligations.append(
            PaymentObligation(
                obligation_id=make_obligation_id(profile.business_type, period_start),
                payer_name=profile.payer_name,
                business_type=profile.business_type,
                period_start=period_start,
                period_end=period_end,
                statutory_due_date=statutory_due,
                adjusted_due_date=adjusted_due,
                amount_nis=amount,
                currency=DEFAULT_CURRENCY,
                status=classify_status(adjusted_due, today=today),
                reminders=reminders,
                actions=action_items(profile.business_type),
                source_note=(
                    "Planning estimate. Verify classification, amount, due date, and payment "
                    "channel in official Bituach Leumi systems before payment."
                ),
            )
        )

    return PaymentPlan(
        generated_at=datetime.now(timezone.utc),
        options=options,
        profile=profile,
        obligations=tuple(obligations),
    )


async def generate_payment_plan_async(
    profile: BusinessProfile,
    options: ScheduleOptions,
    *,
    today: date | None = None,
) -> PaymentPlan:
    await asyncio.sleep(0)
    return generate_payment_plan(profile, options, today=today)


def next_due_obligation(plan: PaymentPlan, today: date | None = None) -> PaymentObligation | None:
    reference = today or date.today()
    future = [obligation for obligation in plan.obligations if obligation.adjusted_due_date >= reference]
    if not future:
        return None
    return min(future, key=lambda obligation: obligation.adjusted_due_date)


def to_json(plan: PaymentPlan, *, indent: int = 2) -> str:
    return json.dumps(plan.to_dict(), ensure_ascii=False, indent=indent, sort_keys=True)


def to_csv(plan: PaymentPlan) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "obligation_id",
            "payer_name",
            "business_type",
            "period_start",
            "period_end",
            "statutory_due_date",
            "adjusted_due_date",
            "amount_nis",
            "currency",
            "status",
            "source_note",
        ],
    )
    writer.writeheader()
    for obligation in plan.obligations:
        row = obligation.to_dict()
        row.pop("reminders", None)
        row.pop("actions", None)
        writer.writerow(row)
    return output.getvalue()


def _ics_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _ics_date(day: date) -> str:
    return day.strftime("%Y%m%d")


def to_ics(plan: PaymentPlan) -> str:
    generated = plan.generated_at.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//bituach-leumi-payment-scheduler//payment-schedule//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]
    for obligation in plan.obligations:
        summary = f"Bituach Leumi payment: {obligation.period_start:%m/%Y}"
        description = (
            f"Payer: {obligation.payer_name}\n"
            f"Type: {obligation.business_type.value}\n"
            f"Estimated amount: {format_nis(obligation.amount_nis)}\n"
            f"Statutory due date: {obligation.statutory_due_date.isoformat()}\n"
            f"Adjusted due date: {obligation.adjusted_due_date.isoformat()}\n"
            f"{obligation.source_note}"
        )
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{obligation.obligation_id}@bituach-leumi-payment-scheduler.local",
                f"DTSTAMP:{generated}",
                f"DTSTART;VALUE=DATE:{_ics_date(obligation.adjusted_due_date)}",
                f"DTEND;VALUE=DATE:{_ics_date(obligation.adjusted_due_date + timedelta(days=1))}",
                f"SUMMARY:{_ics_escape(summary)}",
                f"DESCRIPTION:{_ics_escape(description)}",
                "END:VEVENT",
            ]
        )
        for reminder in obligation.reminders:
            reminder_summary = f"Reminder: Bituach Leumi payment {obligation.period_start:%m/%Y}"
            lines.extend(
                [
                    "BEGIN:VEVENT",
                    f"UID:{obligation.obligation_id}-reminder-{reminder.days_before_due}@bituach-leumi-payment-scheduler.local",
                    f"DTSTAMP:{generated}",
                    f"DTSTART;VALUE=DATE:{_ics_date(reminder.date)}",
                    f"DTEND;VALUE=DATE:{_ics_date(reminder.date + timedelta(days=1))}",
                    f"SUMMARY:{_ics_escape(reminder_summary)}",
                    f"DESCRIPTION:{_ics_escape(reminder.note)}",
                    "END:VEVENT",
                ]
            )
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def to_text(plan: PaymentPlan) -> str:
    lines = [
        f"Payment plan for {plan.profile.payer_name}",
        f"Type: {plan.profile.business_type.value}",
        f"Generated: {plan.generated_at.date().isoformat()}",
        "",
    ]
    for obligation in plan.obligations:
        lines.extend(
            [
                f"{obligation.period_start:%m/%Y}: {format_nis(obligation.amount_nis)}",
                f"  Period: {obligation.period_start.isoformat()} to {obligation.period_end.isoformat()}",
                f"  Due: {obligation.adjusted_due_date.isoformat()} (statutory {obligation.statutory_due_date.isoformat()})",
                f"  Status: {obligation.status.value}",
                f"  Reminder dates: {', '.join(reminder.date.isoformat() for reminder in obligation.reminders)}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def plan_from_mapping(data: Mapping[str, Any], *, today: date | None = None) -> PaymentPlan:
    profile_data = data.get("profile", {})
    options_data = data.get("options", {})
    profile = BusinessProfile(
        payer_name=str(profile_data.get("payer_name", "payer")),
        business_type=parse_business_type(str(profile_data.get("business_type", "self-employed"))),
        israeli_id_or_company_hint=profile_data.get("israeli_id_or_company_hint"),
        monthly_income_nis=profile_data.get("monthly_income_nis"),
        monthly_payroll_nis=profile_data.get("monthly_payroll_nis"),
        amount_override_nis=profile_data.get("amount_override_nis"),
    )
    holidays = frozenset(parse_date(item) for item in options_data.get("holidays", []))
    options = ScheduleOptions(
        start_month=first_day_of_month(parse_date(str(options_data.get("start_month")))),
        months=int(options_data.get("months", 12)),
        due_day=int(options_data.get("due_day", 15)),
        adjustment_policy=parse_adjustment_policy(str(options_data.get("adjustment_policy", "next-business-day"))),
        holidays=holidays,
        reminder_days_before=tuple(int(item) for item in options_data.get("reminder_days_before", [14, 7, 3, 1])),
        reminder_adjustment_policy=parse_adjustment_policy(
            str(options_data.get("reminder_adjustment_policy", "previous-business-day"))
        ),
    )
    return generate_payment_plan(profile, options, today=today)




def make_plan_id(plan: PaymentPlan) -> str:
    """Build a deterministic local plan identifier from payer type and date range."""
    first = plan.obligations[0].period_start if plan.obligations else plan.options.start_month
    last = plan.obligations[-1].period_start if plan.obligations else plan.options.start_month
    safe_name = "".join(ch.lower() if ch.isalnum() else "-" for ch in plan.profile.payer_name).strip("-") or "payer"
    safe_name = "-".join(part for part in safe_name.split("-") if part)[:32]
    return f"{plan.profile.business_type.value}-{safe_name}-{first:%Y%m}-{last:%Y%m}"


def plan_record(plan: PaymentPlan, *, environment: str = "sandbox") -> dict[str, Any]:
    """Return a persisted local record containing the plan id and plan payload."""
    if environment not in {"sandbox", "production"}:
        raise SchedulerError("environment must be sandbox or production")
    return {
        "plan_id": make_plan_id(plan),
        "environment": environment,
        "created_at": plan.generated_at.astimezone(timezone.utc).isoformat(),
        "plan": plan.to_dict(),
    }


def save_plan_record(plan: PaymentPlan, directory: str | Path, *, environment: str = "sandbox") -> Path:
    """Save a local JSON plan record and return the file path."""
    target_dir = Path(directory)
    target_dir.mkdir(parents=True, exist_ok=True)
    record = plan_record(plan, environment=environment)
    target = target_dir / f"{record['plan_id']}.json"
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return target


def load_plan_record(plan_id: str, directory: str | Path) -> dict[str, Any]:
    """Load a local JSON plan record by id."""
    candidate = Path(directory) / f"{plan_id}.json"
    if not candidate.exists():
        raise SchedulerError(f"plan record not found: {plan_id}")
    try:
        return json.loads(candidate.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SchedulerError(f"plan record is not valid JSON: {plan_id}") from exc


def plan_from_record(record: Mapping[str, Any], *, today: date | None = None) -> PaymentPlan:
    """Recreate a PaymentPlan from a persisted local record."""
    plan_payload = record.get("plan")
    if not isinstance(plan_payload, Mapping):
        raise SchedulerError("record must contain a plan object")
    return plan_from_mapping(plan_payload, today=today)


__all__ = [
    "AdjustmentPolicy",
    "BusinessProfile",
    "BusinessType",
    "ContributionPolicy",
    "PaymentObligation",
    "PaymentPlan",
    "PaymentStatus",
    "Reminder",
    "ScheduleOptions",
    "SchedulerError",
    "action_items",
    "add_months",
    "adjust_business_day",
    "build_reminders",
    "classify_status",
    "estimate_monthly_amount",
    "first_day_of_month",
    "format_nis",
    "generate_payment_plan",
    "generate_payment_plan_async",
    "is_business_day",
    "last_day_of_month",
    "load_plan_record",
    "make_obligation_id",
    "make_plan_id",
    "next_due_obligation",
    "parse_adjustment_policy",
    "parse_business_type",
    "parse_date",
    "parse_int_list",
    "plan_from_mapping",
    "plan_from_record",
    "plan_record",
    "save_plan_record",
    "statutory_due_for_period",
    "to_csv",
    "to_ics",
    "to_json",
    "to_text",
]
