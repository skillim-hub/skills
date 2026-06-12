"""Loan amortization calculations for Israeli fixed, prime-linked, and CPI-linked scenarios."""
from __future__ import annotations

import argparse
import asyncio
import csv
import dataclasses
import datetime as dt
import json
import math
import os
import sys
import uuid
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP, getcontext
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

getcontext().prec = 28

NIS = Decimal("0.01")


class RateType(str, Enum):
    """Supported rate mechanisms."""

    FIXED = "fixed"
    PRIME = "prime"
    CPI = "cpi"


class PaymentFrequency(str, Enum):
    """Supported repayment frequencies."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class AmortizationError(ValueError):
    """Raised when a loan scenario cannot be calculated."""


@dataclass(frozen=True)
class RateScenario:
    """Interest and index assumptions."""

    annual_interest_rate: Decimal = Decimal("0.06")
    rate_type: RateType = RateType.FIXED
    prime_rate: Optional[Decimal] = None
    prime_margin: Decimal = Decimal("0")
    annual_cpi_rate: Decimal = Decimal("0")
    payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RateScenario":
        rate_type = RateType(str(data.get("rate_type", "fixed")).lower())
        frequency = PaymentFrequency(str(data.get("payment_frequency", "monthly")).lower())
        prime_rate = data.get("prime_rate")
        return cls(
            annual_interest_rate=decimal_value(data.get("annual_interest_rate", "0.06")),
            rate_type=rate_type,
            prime_rate=None if prime_rate is None or prime_rate == "" else decimal_value(prime_rate),
            prime_margin=decimal_value(data.get("prime_margin", "0")),
            annual_cpi_rate=decimal_value(data.get("annual_cpi_rate", "0")),
            payment_frequency=frequency,
        )

    def annual_rate_for_period(self, period_number: int, rate_changes: Mapping[int, Decimal] | None = None) -> Decimal:
        """Return annual nominal interest rate for a 1-based payment period."""
        if rate_changes and period_number in rate_changes:
            return rate_changes[period_number]
        if self.rate_type == RateType.PRIME:
            if self.prime_rate is None:
                raise AmortizationError("prime_rate is required when rate_type is prime")
            return self.prime_rate + self.prime_margin
        return self.annual_interest_rate

    @property
    def periods_per_year(self) -> int:
        return 12 if self.payment_frequency == PaymentFrequency.MONTHLY else 4

    def periodic_cpi_rate(self) -> Decimal:
        if self.annual_cpi_rate == 0:
            return Decimal("0")
        return (Decimal("1") + self.annual_cpi_rate) ** (Decimal("1") / Decimal(self.periods_per_year)) - Decimal("1")


@dataclass(frozen=True)
class LoanScenario:
    """Complete loan scenario."""

    principal: Decimal
    term_months: int
    start_date: dt.date
    rate: RateScenario = field(default_factory=RateScenario)
    grace_months: int = 0
    balloon_percent: Decimal = Decimal("0")
    origination_fee: Decimal = Decimal("0")
    early_payment_fee: Decimal = Decimal("0")
    name: str = "loan"
    rate_changes: Mapping[int, Decimal] = field(default_factory=dict)
    extra_payments: Mapping[int, Decimal] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "LoanScenario":
        raw_rate = data.get("rate", data)
        rate = raw_rate if isinstance(raw_rate, RateScenario) else RateScenario.from_mapping(raw_rate)
        raw_start = str(data.get("start_date", dt.date.today().isoformat()))
        try:
            principal = decimal_value(data["principal"])
            term_months = int(data["term_months"])
        except KeyError as exc:
            raise AmortizationError(f"missing required field: {exc.args[0]}") from exc
        return cls(
            principal=principal,
            term_months=term_months,
            start_date=parse_date(raw_start),
            rate=rate,
            grace_months=int(data.get("grace_months", 0)),
            balloon_percent=decimal_value(data.get("balloon_percent", "0")),
            origination_fee=decimal_value(data.get("origination_fee", "0")),
            early_payment_fee=decimal_value(data.get("early_payment_fee", "0")),
            name=str(data.get("name", "loan")),
            rate_changes={int(k): decimal_value(v) for k, v in dict(data.get("rate_changes", {})).items()},
            extra_payments={int(k): decimal_value(v) for k, v in dict(data.get("extra_payments", {})).items()},
        )

    def validate(self) -> None:
        if self.principal <= 0:
            raise AmortizationError("principal must be positive")
        if self.term_months <= 0:
            raise AmortizationError("term_months must be positive")
        if self.grace_months < 0:
            raise AmortizationError("grace_months cannot be negative")
        if self.grace_months >= self.term_months:
            raise AmortizationError("grace_months must be shorter than term_months")
        if not (Decimal("0") <= self.balloon_percent < Decimal("1")):
            raise AmortizationError("balloon_percent must be between 0 and less than 1")
        if self.rate.rate_type == RateType.PRIME and self.rate.prime_rate is None:
            raise AmortizationError("prime_rate is required for prime loans")
        if self.rate.payment_frequency == PaymentFrequency.QUARTERLY and self.term_months % 3 != 0:
            raise AmortizationError("quarterly repayment requires term_months divisible by 3")


@dataclass(frozen=True)
class ScheduleRow:
    """One row in an amortization schedule."""

    period: int
    due_date: dt.date
    opening_balance: Decimal
    cpi_adjustment: Decimal
    indexed_balance: Decimal
    interest_rate_annual: Decimal
    interest: Decimal
    principal: Decimal
    extra_payment: Decimal
    total_payment: Decimal
    closing_balance: Decimal

    def as_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period,
            "due_date": self.due_date.isoformat(),
            "opening_balance": money(self.opening_balance),
            "cpi_adjustment": money(self.cpi_adjustment),
            "indexed_balance": money(self.indexed_balance),
            "interest_rate_annual": str(rate_pct(self.interest_rate_annual)),
            "interest": money(self.interest),
            "principal": money(self.principal),
            "extra_payment": money(self.extra_payment),
            "total_payment": money(self.total_payment),
            "closing_balance": money(self.closing_balance),
        }


@dataclass(frozen=True)
class ScheduleSummary:
    """Aggregate schedule totals."""

    principal: Decimal
    total_interest: Decimal
    total_cpi_adjustment: Decimal
    total_paid: Decimal
    fees: Decimal
    effective_cash_cost: Decimal
    final_balance: Decimal
    max_payment: Decimal
    periods: int

    def as_dict(self) -> Dict[str, Any]:
        return {
            "principal": money(self.principal),
            "total_interest": money(self.total_interest),
            "total_cpi_adjustment": money(self.total_cpi_adjustment),
            "total_paid": money(self.total_paid),
            "fees": money(self.fees),
            "effective_cash_cost": money(self.effective_cash_cost),
            "final_balance": money(self.final_balance),
            "max_payment": money(self.max_payment),
            "periods": self.periods,
        }


@dataclass(frozen=True)
class LoanSchedule:
    """Computed amortization schedule."""

    scenario: LoanScenario
    rows: List[ScheduleRow]
    summary: ScheduleSummary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario": {
                "name": self.scenario.name,
                "principal": money(self.scenario.principal),
                "term_months": self.scenario.term_months,
                "start_date": self.scenario.start_date.isoformat(),
                "rate_type": self.scenario.rate.rate_type.value,
                "payment_frequency": self.scenario.rate.payment_frequency.value,
            },
            "summary": self.summary.as_dict(),
            "rows": [row.as_dict() for row in self.rows],
        }

    def to_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def to_csv(self, path: str | Path) -> None:
        rows = [row.as_dict() for row in self.rows]
        with Path(path).open("w", newline="", encoding="utf-8") as fh:
            if not rows:
                return
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)


def decimal_value(value: Any) -> Decimal:
    """Convert numeric input to Decimal while accepting comma separators."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value).replace(",", "").strip())


def q2(value: Decimal) -> Decimal:
    """Round a Decimal value to agorot."""
    return value.quantize(NIS, rounding=ROUND_HALF_UP)


def money(value: Decimal) -> str:
    """Format a Decimal as a two-decimal string."""
    return str(q2(value))


def rate_pct(value: Decimal) -> Decimal:
    """Return a decimal rate as a percentage value with four decimals."""
    return (value * Decimal("100")).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def parse_date(value: str) -> dt.date:
    """Parse ISO YYYY-MM-DD, Israeli DD-MM-YYYY, or Israeli DD/MM/YYYY date."""
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise AmortizationError("date must be YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY")


def add_months(date: dt.date, months: int) -> dt.date:
    """Add calendar months while preserving month-end behavior."""
    month = date.month - 1 + months
    year = date.year + month // 12
    month = month % 12 + 1
    day = min(date.day, days_in_month(year, month))
    return dt.date(year, month, day)


def days_in_month(year: int, month: int) -> int:
    """Return the number of days in a calendar month."""
    if month == 12:
        return 31
    return (dt.date(year, month + 1, 1) - dt.timedelta(days=1)).day


def periodic_payment(balance: Decimal, annual_rate: Decimal, periods: int, periods_per_year: int, balloon: Decimal = Decimal("0")) -> Decimal:
    """Calculate the remaining-period annuity payment."""
    if periods <= 0:
        return balance
    period_rate = annual_rate / Decimal(periods_per_year)
    if abs(period_rate) < Decimal("0.0000000001"):
        return (balance - balloon) / Decimal(periods)
    factor = (Decimal("1") + period_rate) ** Decimal(periods)
    return (balance * period_rate * factor - balloon * period_rate) / (factor - Decimal("1"))


def build_schedule(scenario: LoanScenario) -> LoanSchedule:
    """Build a full repayment schedule for a single loan scenario."""
    scenario.validate()
    ppy = scenario.rate.periods_per_year
    step_months = 12 // ppy
    periods = scenario.term_months // step_months
    grace_periods = math.ceil(scenario.grace_months / step_months)
    cpi_rate = scenario.rate.periodic_cpi_rate() if scenario.rate.rate_type == RateType.CPI else Decimal("0")
    balance = scenario.principal
    rows: List[ScheduleRow] = []

    for period in range(1, periods + 1):
        due_date = add_months(scenario.start_date, period * step_months)
        opening = balance
        cpi_adjustment = q2(opening * cpi_rate)
        indexed_balance = opening + cpi_adjustment
        annual_rate = scenario.rate.annual_rate_for_period(period, scenario.rate_changes)
        interest = q2(indexed_balance * (annual_rate / Decimal(ppy)))
        extra = q2(scenario.extra_payments.get(period, Decimal("0")))

        if period <= grace_periods:
            principal_component = min(indexed_balance, extra)
            total_payment = interest + principal_component
            closing = indexed_balance - principal_component
        else:
            remaining_periods = periods - period + 1
            balloon_value = q2(scenario.principal * scenario.balloon_percent) if remaining_periods > 1 else Decimal("0")
            payment = q2(periodic_payment(indexed_balance, annual_rate, remaining_periods, ppy, balloon_value))
            scheduled_principal = max(Decimal("0"), payment - interest)
            if remaining_periods == 1:
                scheduled_principal = indexed_balance
                payment = scheduled_principal + interest
            principal_component = min(indexed_balance, q2(scheduled_principal + extra))
            total_payment = interest + principal_component
            closing = indexed_balance - principal_component

        if closing < Decimal("0.005"):
            closing = Decimal("0")

        rows.append(
            ScheduleRow(
                period=period,
                due_date=due_date,
                opening_balance=q2(opening),
                cpi_adjustment=q2(cpi_adjustment),
                indexed_balance=q2(indexed_balance),
                interest_rate_annual=q2(annual_rate * Decimal("10000")) / Decimal("10000"),
                interest=q2(interest),
                principal=q2(principal_component),
                extra_payment=q2(extra),
                total_payment=q2(total_payment),
                closing_balance=q2(closing),
            )
        )
        balance = closing
        if balance == 0:
            break

    total_interest = sum((row.interest for row in rows), Decimal("0"))
    total_cpi = sum((row.cpi_adjustment for row in rows), Decimal("0"))
    total_paid = sum((row.total_payment for row in rows), Decimal("0"))
    fees = q2(scenario.origination_fee + scenario.early_payment_fee)
    max_payment = max((row.total_payment for row in rows), default=Decimal("0"))
    final_balance = rows[-1].closing_balance if rows else scenario.principal
    summary = ScheduleSummary(
        principal=scenario.principal,
        total_interest=q2(total_interest),
        total_cpi_adjustment=q2(total_cpi),
        total_paid=q2(total_paid),
        fees=fees,
        effective_cash_cost=q2(total_paid + fees - scenario.principal),
        final_balance=q2(final_balance),
        max_payment=q2(max_payment),
        periods=len(rows),
    )
    return LoanSchedule(scenario=scenario, rows=rows, summary=summary)


def compare_scenarios(scenarios: Sequence[LoanScenario]) -> List[Dict[str, Any]]:
    """Return comparable summary dictionaries sorted by effective cash cost."""
    results = []
    for scenario in scenarios:
        schedule = build_schedule(scenario)
        item = schedule.summary.as_dict()
        item["name"] = scenario.name
        item["rate_type"] = scenario.rate.rate_type.value
        item["term_months"] = scenario.term_months
        results.append(item)
    return sorted(results, key=lambda item: Decimal(item["effective_cash_cost"]))


async def async_build_schedule(scenario: LoanScenario) -> LoanSchedule:
    """Async wrapper for service integrations and batch workflows."""
    return await asyncio.to_thread(build_schedule, scenario)


async def async_compare_scenarios(scenarios: Sequence[LoanScenario]) -> List[Dict[str, Any]]:
    """Async wrapper for comparing many scenarios concurrently."""
    schedules = await asyncio.gather(*(async_build_schedule(s) for s in scenarios))
    rows = []
    for scenario, schedule in zip(scenarios, schedules):
        item = schedule.summary.as_dict()
        item["name"] = scenario.name
        item["rate_type"] = scenario.rate.rate_type.value
        item["term_months"] = scenario.term_months
        rows.append(item)
    return sorted(rows, key=lambda item: Decimal(item["effective_cash_cost"]))


def load_scenario(path: str | Path) -> LoanScenario:
    """Load one scenario from JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return LoanScenario.from_mapping(data)


def load_scenarios(path: str | Path) -> List[LoanScenario]:
    """Load a list of scenarios from JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "scenarios" in data:
        data = data["scenarios"]
    if isinstance(data, dict):
        data = [data]
    return [LoanScenario.from_mapping(item) for item in data]


def scenario_to_mapping(scenario: LoanScenario) -> Dict[str, Any]:
    """Serialize a scenario to JSON-ready values."""
    return {
        "name": scenario.name,
        "principal": money(scenario.principal),
        "term_months": scenario.term_months,
        "start_date": scenario.start_date.strftime("%d/%m/%Y"),
        "rate_type": scenario.rate.rate_type.value,
        "annual_interest_rate": str(scenario.rate.annual_interest_rate),
        "prime_rate": None if scenario.rate.prime_rate is None else str(scenario.rate.prime_rate),
        "prime_margin": str(scenario.rate.prime_margin),
        "annual_cpi_rate": str(scenario.rate.annual_cpi_rate),
        "payment_frequency": scenario.rate.payment_frequency.value,
        "grace_months": scenario.grace_months,
        "balloon_percent": str(scenario.balloon_percent),
        "origination_fee": money(scenario.origination_fee),
        "early_payment_fee": money(scenario.early_payment_fee),
        "rate_changes": {str(k): str(v) for k, v in scenario.rate_changes.items()},
        "extra_payments": {str(k): str(v) for k, v in scenario.extra_payments.items()},
    }


def default_registry_path() -> Path:
    """Return the scenario registry path used by quick-start examples."""
    return Path(os.environ.get("LOAN_PLANNER_REGISTRY", ".loan_planner_scenarios.json"))


def read_registry(path: str | Path | None = None) -> Dict[str, Any]:
    """Read the local scenario registry."""
    registry_path = Path(path) if path else default_registry_path()
    if not registry_path.exists():
        return {"scenarios": {}}
    return json.loads(registry_path.read_text(encoding="utf-8"))


def write_registry(registry: Mapping[str, Any], path: str | Path | None = None) -> None:
    """Write the local scenario registry."""
    registry_path = Path(path) if path else default_registry_path()
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")


def create_scenario_record(data: Mapping[str, Any], registry_path: str | Path | None = None) -> Dict[str, Any]:
    """Validate and store a scenario, returning a reusable local identifier."""
    scenario = LoanScenario.from_mapping(data)
    scenario.validate()
    scenario_id = str(uuid.uuid4())[:12]
    registry = read_registry(registry_path)
    registry.setdefault("scenarios", {})[scenario_id] = scenario_to_mapping(scenario)
    write_registry(registry, registry_path)
    return {"id": scenario_id, "scenario": scenario_to_mapping(scenario)}


def resolve_scenario(value: str | Path, registry_path: str | Path | None = None) -> LoanScenario:
    """Resolve a scenario from a file path or local registry identifier."""
    candidate = Path(str(value))
    if candidate.exists():
        return load_scenario(candidate)
    registry = read_registry(registry_path)
    try:
        data = registry["scenarios"][str(value)]
    except KeyError as exc:
        raise AmortizationError(f"scenario id not found: {value}") from exc
    return LoanScenario.from_mapping(data)


def public_api_names() -> List[str]:
    """Return public callable and class names exported by this module."""
    names = []
    for name, value in globals().items():
        if name.startswith("_"):
            continue
        if dataclasses.is_dataclass(value) or callable(value):
            if getattr(value, "__module__", __name__) == __name__:
                names.append(name)
    return sorted(names)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Small argparse entry point kept for script compatibility."""
    parser = argparse.ArgumentParser(description="Build Israeli loan amortization schedules.")
    parser.add_argument("scenario", help="Path to JSON scenario file or registry scenario id")
    parser.add_argument("--json", dest="json_path", help="Write schedule JSON to this path")
    parser.add_argument("--csv", dest="csv_path", help="Write schedule CSV to this path")
    parser.add_argument("--compare", action="store_true", help="Treat input as a scenario list and print comparison")
    parser.add_argument("--registry", help="Scenario registry path")
    args = parser.parse_args(argv)

    try:
        if args.compare:
            scenarios = load_scenarios(args.scenario)
            print(json.dumps(compare_scenarios(scenarios), ensure_ascii=False, indent=2))
            return 0
        schedule = build_schedule(resolve_scenario(args.scenario, args.registry))
        if args.json_path:
            schedule.to_json(args.json_path)
        if args.csv_path:
            schedule.to_csv(args.csv_path)
        print(json.dumps(schedule.summary.as_dict(), ensure_ascii=False, indent=2))
        return 0
    except (AmortizationError, KeyError, json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
