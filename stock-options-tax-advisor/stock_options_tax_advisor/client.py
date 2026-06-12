from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import json
from dataclasses import dataclass, field
from enum import Enum
from math import inf
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


class GrantType(str, Enum):
    OPTIONS = "options"
    RSU = "rsu"
    ESPP = "espp"
    RESTRICTED_SHARES = "restricted_shares"


class TaxTrack(str, Enum):
    SECTION_102_CAPITAL = "102_capital"
    SECTION_102_INCOME = "102_income"
    SECTION_102_NON_TRUSTEE = "102_non_trustee"
    SECTION_3I = "3i"
    NON_EMPLOYEE = "non_employee"
    UNKNOWN = "unknown"


class HoldingPeriodAnchor(str, Enum):
    GRANT_YEAR_END = "grant_year_end"
    GRANT_DATE = "grant_date"
    TRUSTEE_DEPOSIT_DATE = "trustee_deposit_date"
    MANUAL = "manual"


@dataclass(frozen=True)
class TaxConstants:
    """Mutable-by-replacement assumptions for a specific Israeli tax year."""

    tax_year: int = 2026
    capital_gains_rate: float = 0.25
    controlling_shareholder_capital_rate: float = 0.30
    surtax_threshold: float = 721_560.0
    surtax_general_rate: float = 0.03
    surtax_extra_capital_rate: float = 0.02
    income_tax_brackets: Tuple[Tuple[float, float], ...] = (
        (84_120.0, 0.10),
        (120_720.0, 0.14),
        (228_000.0, 0.20),
        (301_200.0, 0.31),
        (560_280.0, 0.35),
        (inf, 0.47),
    )
    social_security_low_annual: float = 7_703.0 * 12.0
    social_security_cap_annual: float = 51_910.0 * 12.0
    social_security_low_rate: float = 0.0427
    social_security_high_rate: float = 0.1217


@dataclass(frozen=True)
class EquityScenario:
    """Single sale, vest, or purchase scenario modeled in ILS after FX conversion."""

    grant_type: GrantType
    track: TaxTrack
    quantity: float
    sale_price: float
    exercise_price: float = 0.0
    grant_date: Optional[dt.date] = None
    sale_date: Optional[dt.date] = None
    trustee_deposit_date: Optional[dt.date] = None
    manual_preferred_sale_date: Optional[dt.date] = None
    holding_period_anchor: HoldingPeriodAnchor = HoldingPeriodAnchor.GRANT_YEAR_END
    other_annual_income: float = 0.0
    fmv_at_grant: Optional[float] = None
    fmv_at_exercise: Optional[float] = None
    fmv_at_purchase: Optional[float] = None
    public_at_grant: bool = False
    trustee_approved: bool = False
    is_controlling_shareholder: bool = False
    currency: str = "ILS"
    fx_rate_to_ils: float = 1.0
    notes: Tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EquityScenario":
        payload = dict(data)
        for key, enum_type in {
            "grant_type": GrantType,
            "track": TaxTrack,
            "holding_period_anchor": HoldingPeriodAnchor,
        }.items():
            if payload.get(key) is not None:
                payload[key] = enum_type(payload[key])
        for key in ("grant_date", "sale_date", "trustee_deposit_date", "manual_preferred_sale_date"):
            if payload.get(key):
                payload[key] = parse_date(payload[key])
        if payload.get("notes") is not None:
            payload["notes"] = tuple(payload["notes"])
        return cls(**payload)

    def to_dict(self) -> Dict[str, Any]:
        raw = dataclasses.asdict(self)
        raw["grant_type"] = self.grant_type.value
        raw["track"] = self.track.value
        raw["holding_period_anchor"] = self.holding_period_anchor.value
        for key in ("grant_date", "sale_date", "trustee_deposit_date", "manual_preferred_sale_date"):
            if raw[key] is not None:
                raw[key] = raw[key].isoformat()
        raw["notes"] = list(raw["notes"])
        return raw


@dataclass(frozen=True)
class TaxBreakdown:
    gross_proceeds: float
    cost_basis: float
    total_gain: float
    employment_income: float
    capital_gain: float
    ordinary_income_tax: float
    capital_gains_tax: float
    national_insurance_health: float
    surtax: float
    total_tax: float
    net_proceeds: float
    effective_tax_rate_on_gain: float
    holding_period_satisfied: Optional[bool]
    earliest_preferred_sale_date: Optional[dt.date]
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    assumptions: Tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, Any]:
        raw = dataclasses.asdict(self)
        if self.earliest_preferred_sale_date is not None:
            raw["earliest_preferred_sale_date"] = self.earliest_preferred_sale_date.isoformat()
        raw["warnings"] = list(raw["warnings"])
        raw["assumptions"] = list(raw["assumptions"])
        return raw

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class StockOptionsTaxAdvisorClient:
    """Synchronous local calculator for Israeli employee equity tax scenarios."""

    def __init__(self, constants: Optional[TaxConstants] = None, *, environment: str = "sandbox") -> None:
        self.constants = constants or TaxConstants()
        self.environment = normalize_environment(environment)

    def create_scenario(self, data: Mapping[str, Any]) -> EquityScenario:
        scenario = EquityScenario.from_dict(data)
        self._validate(scenario)
        return scenario

    def calculate(self, scenario: EquityScenario | Mapping[str, Any]) -> TaxBreakdown:
        scenario = self._coerce(scenario)
        self._validate(scenario)
        gross = scenario.quantity * scenario.sale_price * scenario.fx_rate_to_ils
        basis = scenario.quantity * scenario.exercise_price * scenario.fx_rate_to_ils
        total_gain = max(gross - basis, 0.0)
        warnings: List[str] = []
        assumptions: List[str] = []
        preferred_date = self.earliest_preferred_sale_date(scenario)
        holding_ok = self.holding_period_satisfied(scenario)

        if scenario.track in {TaxTrack.SECTION_102_CAPITAL, TaxTrack.SECTION_102_INCOME} and not scenario.trustee_approved:
            warnings.append("NO_TRUSTEE_CONFIRMATION: Section 102 trustee status and release date require trustee confirmation.")

        if holding_ok is False and scenario.track == TaxTrack.SECTION_102_CAPITAL:
            employment_income, capital_gain = total_gain, 0.0
            warnings.append("EARLY_SALE_RISK: sale date is before the preferred-treatment date; ordinary-income treatment is modeled.")
            assumptions.append("Early-sale fallback treats the full positive spread as employment income.")
        elif scenario.track == TaxTrack.SECTION_102_CAPITAL:
            employment_income, capital_gain = self._capital_track_components(scenario, total_gain)
            assumptions.append("Section 102 capital-gains track modeled with documented or assumed trustee compliance.")
        elif scenario.track == TaxTrack.SECTION_102_INCOME:
            employment_income, capital_gain = self._income_track_components(scenario)
            assumptions.append("Section 102 income track modeled as ordinary component plus later capital appreciation.")
        elif scenario.track in {TaxTrack.SECTION_102_NON_TRUSTEE, TaxTrack.SECTION_3I, TaxTrack.NON_EMPLOYEE, TaxTrack.UNKNOWN}:
            employment_income, capital_gain = self._non_102_components(scenario, total_gain)
            assumptions.append("Non-capital-track treatment modeled conservatively.")
            if scenario.track == TaxTrack.UNKNOWN:
                warnings.append("MISSING_TRACK: track is unknown; result is provisional.")
        else:
            employment_income, capital_gain = total_gain, 0.0

        if scenario.public_at_grant and scenario.fmv_at_grant is None:
            warnings.append("PUBLIC_SHARE_SPLIT_NEEDED: public-company grants may require FMV at grant.")
        if scenario.is_controlling_shareholder:
            warnings.append("CONTROLLING_HOLDER: 10%+ holder status may require 30% rate and professional review.")

        ordinary_tax = incremental_income_tax(scenario.other_annual_income, employment_income, self.constants)
        ni_health = incremental_social_security_health(scenario.other_annual_income, employment_income, self.constants)
        cap_rate = self.constants.controlling_shareholder_capital_rate if scenario.is_controlling_shareholder else self.constants.capital_gains_rate
        capital_tax = capital_gain * cap_rate
        surtax_value = incremental_surtax(scenario.other_annual_income, employment_income, capital_gain, self.constants)
        total_tax = ordinary_tax + ni_health + capital_tax + surtax_value
        net = gross - basis - total_tax
        effective = total_tax / total_gain if total_gain else 0.0
        return TaxBreakdown(
            gross_proceeds=round(gross, 2),
            cost_basis=round(basis, 2),
            total_gain=round(total_gain, 2),
            employment_income=round(employment_income, 2),
            capital_gain=round(capital_gain, 2),
            ordinary_income_tax=round(ordinary_tax, 2),
            capital_gains_tax=round(capital_tax, 2),
            national_insurance_health=round(ni_health, 2),
            surtax=round(surtax_value, 2),
            total_tax=round(total_tax, 2),
            net_proceeds=round(net, 2),
            effective_tax_rate_on_gain=round(effective, 6),
            holding_period_satisfied=holding_ok,
            earliest_preferred_sale_date=preferred_date,
            warnings=tuple(warnings),
            assumptions=tuple(assumptions),
        )

    def compare_tracks(self, scenario: EquityScenario | Mapping[str, Any]) -> Dict[str, TaxBreakdown]:
        scenario = self._coerce(scenario)
        out: Dict[str, TaxBreakdown] = {}
        for track in (TaxTrack.SECTION_102_CAPITAL, TaxTrack.SECTION_102_INCOME, TaxTrack.SECTION_3I):
            modified = dataclasses.replace(scenario, track=track)
            if track == TaxTrack.SECTION_102_INCOME and modified.fmv_at_exercise is None:
                modified = dataclasses.replace(modified, fmv_at_exercise=modified.sale_price)
            out[track.value] = self.calculate(modified)
        return out

    def earliest_preferred_sale_date(self, scenario: EquityScenario | Mapping[str, Any]) -> Optional[dt.date]:
        scenario = self._coerce(scenario)
        if scenario.holding_period_anchor == HoldingPeriodAnchor.MANUAL:
            return scenario.manual_preferred_sale_date
        if scenario.holding_period_anchor == HoldingPeriodAnchor.TRUSTEE_DEPOSIT_DATE:
            anchor = scenario.trustee_deposit_date
        elif scenario.holding_period_anchor == HoldingPeriodAnchor.GRANT_DATE:
            anchor = scenario.grant_date
        else:
            anchor = dt.date(scenario.grant_date.year, 12, 31) if scenario.grant_date else None
        return add_months(anchor, 24) if anchor else None

    def holding_period_satisfied(self, scenario: EquityScenario | Mapping[str, Any]) -> Optional[bool]:
        scenario = self._coerce(scenario)
        preferred = self.earliest_preferred_sale_date(scenario)
        if preferred is None or scenario.sale_date is None:
            return None
        return scenario.sale_date >= preferred

    def eligibility_notes(self, scenario: EquityScenario | Mapping[str, Any]) -> List[str]:
        scenario = self._coerce(scenario)
        notes: List[str] = []
        if scenario.track == TaxTrack.UNKNOWN:
            notes.append("Obtain grant letter or trustee confirmation of the Section 102 track.")
        if scenario.track in {TaxTrack.SECTION_102_CAPITAL, TaxTrack.SECTION_102_INCOME} and not scenario.trustee_approved:
            notes.append("Obtain trustee confirmation of plan status and release date.")
        if self.holding_period_satisfied(scenario) is False:
            notes.append("Sale date precedes preferred-treatment date; calculate early-sale treatment.")
        if scenario.public_at_grant and scenario.fmv_at_grant is None:
            notes.append("Obtain FMV at grant for public-company split.")
        if scenario.grant_type == GrantType.ESPP and scenario.fmv_at_purchase is None:
            notes.append("Obtain FMV at purchase for ESPP discount analysis.")
        if scenario.is_controlling_shareholder:
            notes.append("Confirm 10%+ holder tax rate and related-party rules.")
        return notes

    def export_case(self, scenario: EquityScenario | Mapping[str, Any]) -> Dict[str, Any]:
        scenario_obj = self._coerce(scenario)
        return {"scenario": scenario_obj.to_dict(), "result": self.calculate(scenario_obj).to_dict()}

    def _capital_track_components(self, scenario: EquityScenario, total_gain: float) -> Tuple[float, float]:
        if scenario.public_at_grant and scenario.fmv_at_grant is not None:
            embedded = max((scenario.fmv_at_grant - scenario.exercise_price) * scenario.quantity * scenario.fx_rate_to_ils, 0.0)
            ordinary = min(total_gain, embedded)
            return ordinary, max(total_gain - ordinary, 0.0)
        return 0.0, total_gain

    def _income_track_components(self, scenario: EquityScenario) -> Tuple[float, float]:
        if scenario.fmv_at_exercise is None:
            raise ValueError("fmv_at_exercise is required for 102_income")
        fmv = scenario.fmv_at_exercise * scenario.fx_rate_to_ils
        sale = scenario.sale_price * scenario.fx_rate_to_ils
        exercise = scenario.exercise_price * scenario.fx_rate_to_ils
        employment = max((fmv - exercise) * scenario.quantity, 0.0)
        capital = max((sale - fmv) * scenario.quantity, 0.0)
        return employment, capital

    def _non_102_components(self, scenario: EquityScenario, total_gain: float) -> Tuple[float, float]:
        if scenario.grant_type == GrantType.ESPP and scenario.fmv_at_purchase is not None:
            purchase = scenario.exercise_price * scenario.fx_rate_to_ils
            fmv_purchase = scenario.fmv_at_purchase * scenario.fx_rate_to_ils
            sale = scenario.sale_price * scenario.fx_rate_to_ils
            discount = max((fmv_purchase - purchase) * scenario.quantity, 0.0)
            later_gain = max((sale - fmv_purchase) * scenario.quantity, 0.0)
            return discount, later_gain
        return total_gain, 0.0

    def _validate(self, scenario: EquityScenario) -> None:
        if scenario.quantity <= 0:
            raise ValueError("quantity must be positive")
        if scenario.sale_price < 0:
            raise ValueError("sale_price must be non-negative")
        if scenario.exercise_price < 0:
            raise ValueError("exercise_price must be non-negative")
        if scenario.other_annual_income < 0:
            raise ValueError("other_annual_income must be non-negative")
        if scenario.currency.upper() != "ILS" and scenario.fx_rate_to_ils <= 0:
            raise ValueError("fx_rate_to_ils is required for non-ILS currency")
        if scenario.track == TaxTrack.SECTION_102_INCOME and scenario.fmv_at_exercise is None:
            raise ValueError("fmv_at_exercise is required for 102_income")
        if scenario.grant_type == GrantType.ESPP and scenario.track in {TaxTrack.SECTION_3I, TaxTrack.NON_EMPLOYEE} and scenario.fmv_at_purchase is None:
            raise ValueError("fmv_at_purchase is required for ESPP non-102 discount split")

    def _coerce(self, scenario: EquityScenario | Mapping[str, Any]) -> EquityScenario:
        return scenario if isinstance(scenario, EquityScenario) else EquityScenario.from_dict(scenario)


class AsyncStockOptionsTaxAdvisorClient:
    """Async wrapper around the local calculator."""

    def __init__(self, sync_client: Optional[StockOptionsTaxAdvisorClient] = None, *, environment: str = "sandbox") -> None:
        self.sync_client = sync_client or StockOptionsTaxAdvisorClient(environment=environment)

    async def calculate(self, scenario: EquityScenario | Mapping[str, Any]) -> TaxBreakdown:
        return await asyncio.to_thread(self.sync_client.calculate, scenario)

    async def compare_tracks(self, scenario: EquityScenario | Mapping[str, Any]) -> Dict[str, TaxBreakdown]:
        return await asyncio.to_thread(self.sync_client.compare_tracks, scenario)

    async def calculate_many(self, scenarios: Sequence[EquityScenario | Mapping[str, Any]]) -> List[TaxBreakdown]:
        return list(await asyncio.gather(*(self.calculate(s) for s in scenarios)))

    async def export_case(self, scenario: EquityScenario | Mapping[str, Any]) -> Dict[str, Any]:
        return await asyncio.to_thread(self.sync_client.export_case, scenario)


def normalize_environment(value: str | None) -> str:
    env = (value or "sandbox").strip().lower()
    if env not in {"sandbox", "production"}:
        raise ValueError("environment must be sandbox or production")
    return env


def parse_date(value: str | dt.date) -> dt.date:
    if isinstance(value, dt.date):
        return value
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"invalid date: {value!r}; use YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY")


def add_months(value: dt.date, months: int) -> dt.date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, days_in_month(year, month))
    return dt.date(year, month, day)


def days_in_month(year: int, month: int) -> int:
    next_month = dt.date(year + (month // 12), (month % 12) + 1, 1)
    return (next_month - dt.timedelta(days=1)).day


def income_tax(income: float, constants: Optional[TaxConstants] = None) -> float:
    constants = constants or TaxConstants()
    taxable = max(income, 0.0)
    previous = 0.0
    tax = 0.0
    for limit, rate in constants.income_tax_brackets:
        band = max(min(taxable, limit) - previous, 0.0)
        tax += band * rate
        previous = limit
        if taxable <= limit:
            break
    return tax


def incremental_income_tax(base_income: float, added_income: float, constants: Optional[TaxConstants] = None) -> float:
    constants = constants or TaxConstants()
    if added_income <= 0:
        return 0.0
    return income_tax(base_income + added_income, constants) - income_tax(base_income, constants)


def social_security_health(employment_income: float, constants: Optional[TaxConstants] = None) -> float:
    constants = constants or TaxConstants()
    income = max(min(employment_income, constants.social_security_cap_annual), 0.0)
    low = min(income, constants.social_security_low_annual)
    high = max(income - constants.social_security_low_annual, 0.0)
    return low * constants.social_security_low_rate + high * constants.social_security_high_rate


def incremental_social_security_health(base_employment_income: float, added_employment_income: float, constants: Optional[TaxConstants] = None) -> float:
    constants = constants or TaxConstants()
    if added_employment_income <= 0:
        return 0.0
    return social_security_health(base_employment_income + added_employment_income, constants) - social_security_health(base_employment_income, constants)


def incremental_surtax(other_income: float, employment_income: float, capital_income: float, constants: Optional[TaxConstants] = None) -> float:
    constants = constants or TaxConstants()
    base_total = max(other_income, 0.0)
    non_capital_after = max(other_income + employment_income, 0.0)
    total_after = max(other_income + employment_income + capital_income, 0.0)
    base_excess = max(base_total - constants.surtax_threshold, 0.0)
    after_excess = max(total_after - constants.surtax_threshold, 0.0)
    general = max(after_excess - base_excess, 0.0) * constants.surtax_general_rate
    remaining = max(constants.surtax_threshold - non_capital_after, 0.0)
    capital_above = max(capital_income - remaining, 0.0)
    return general + capital_above * constants.surtax_extra_capital_rate


def format_ils(value: float) -> str:
    return f"₪{value:,.0f}"


def summarize_breakdown(breakdown: TaxBreakdown) -> str:
    lines = [
        f"Gross proceeds: {format_ils(breakdown.gross_proceeds)}",
        f"Cost basis: {format_ils(breakdown.cost_basis)}",
        f"Total gain: {format_ils(breakdown.total_gain)}",
        f"Employment income: {format_ils(breakdown.employment_income)}",
        f"Capital gain: {format_ils(breakdown.capital_gain)}",
        f"Income tax: {format_ils(breakdown.ordinary_income_tax)}",
        f"Capital gains tax: {format_ils(breakdown.capital_gains_tax)}",
        f"National Insurance and health: {format_ils(breakdown.national_insurance_health)}",
        f"Surtax: {format_ils(breakdown.surtax)}",
        f"Total tax: {format_ils(breakdown.total_tax)}",
        f"Net proceeds: {format_ils(breakdown.net_proceeds)}",
        f"Effective tax rate on gain: {breakdown.effective_tax_rate_on_gain:.2%}",
    ]
    if breakdown.earliest_preferred_sale_date:
        lines.append(f"Earliest preferred sale date: {breakdown.earliest_preferred_sale_date.isoformat()}")
    if breakdown.holding_period_satisfied is not None:
        lines.append(f"Holding period satisfied: {breakdown.holding_period_satisfied}")
    if breakdown.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {w}" for w in breakdown.warnings)
    return "\n".join(lines)


__all__ = [
    "GrantType",
    "TaxTrack",
    "HoldingPeriodAnchor",
    "TaxConstants",
    "EquityScenario",
    "TaxBreakdown",
    "StockOptionsTaxAdvisorClient",
    "AsyncStockOptionsTaxAdvisorClient",
    "normalize_environment",
    "parse_date",
    "add_months",
    "days_in_month",
    "income_tax",
    "incremental_income_tax",
    "social_security_health",
    "incremental_social_security_health",
    "incremental_surtax",
    "format_ils",
    "summarize_breakdown",
]
