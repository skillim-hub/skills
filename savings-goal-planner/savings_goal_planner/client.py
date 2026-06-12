"""Structured helper for Israeli savings-goal planning.

The module performs deterministic financial calculations for major purchases,
business equipment, emergency funds, and retirement gaps. It does not provide
personal investment, pension, legal, or tax advice.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Literal, Mapping, Optional


RiskLevel = Literal["very_low", "low", "medium", "high"]
ContributionTiming = Literal["end", "beginning"]


class SavingsGoalError(ValueError):
    """Raised when an input cannot produce a meaningful savings calculation."""


@dataclass(frozen=True)
class VehicleOption:
    """Israeli savings or investment vehicle preset."""

    key: str
    english_name: str
    hebrew_name: str
    risk_level: RiskLevel
    min_horizon_months: int
    liquidity_days: Optional[int]
    default_annual_return: float
    default_annual_fee: float
    default_tax_rate_on_gain: float
    tax_treatment: str
    suitable_for: str
    caution: str


@dataclass(frozen=True)
class GoalRequest:
    """Request for a single savings goal."""

    goal_name: str
    target_amount: float
    months: int
    current_savings: float = 0.0
    current_monthly_savings: float = 0.0
    annual_return: Optional[float] = None
    annual_fee: Optional[float] = None
    tax_rate_on_gain: Optional[float] = None
    inflation_rate: float = 0.0
    amount_is_today_terms: bool = True
    contribution_timing: ContributionTiming = "end"
    vehicle_key: Optional[str] = None
    monthly_income: Optional[float] = None


@dataclass(frozen=True)
class SavingsPlanResult:
    """Result for a single savings goal."""

    goal_name: str
    target_amount_input: float
    target_future_value: float
    months: int
    years: float
    monthly_required: float
    current_monthly_savings: float
    total_new_contributions: float
    projected_current_savings_value: float
    projected_existing_monthly_value: float
    projected_total_value: float
    shortfall_at_current_rate: float
    effective_annual_return: float
    monthly_return: float
    inflation_rate: float
    vehicle: Optional[VehicleOption]
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.vehicle is not None:
            data["vehicle"] = asdict(self.vehicle)
        return data


@dataclass(frozen=True)
class RetirementRequest:
    """Request for a retirement gap calculation in today's shekels."""

    current_age: float
    retirement_age: float
    life_expectancy: float
    desired_monthly_spending_today: float
    expected_monthly_pension_today: float = 0.0
    current_retirement_savings: float = 0.0
    annual_real_return_accumulation: float = 0.04
    annual_real_return_retirement: float = 0.025
    contribution_timing: ContributionTiming = "end"


@dataclass(frozen=True)
class RetirementPlanResult:
    """Retirement gap result using real returns and today's shekels."""

    accumulation_months: int
    retirement_months: int
    monthly_income_gap_today: float
    required_nest_egg_today: float
    monthly_required_today: float
    projected_current_savings_today: float
    effective_annual_return_accumulation: float
    annual_real_return_retirement: float
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


EnvironmentName = Literal["sandbox", "production"]


@dataclass(frozen=True)
class StoredGoal:
    """Persisted goal calculation with a stable identifier."""

    id: str
    environment: EnvironmentName
    created_at: str
    request: GoalRequest
    result: SavingsPlanResult

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "environment": self.environment,
            "created_at": self.created_at,
            "request": asdict(self.request),
            "result": self.result.to_dict(),
        }


VEHICLES: Dict[str, VehicleOption] = {
    "cash_bank": VehicleOption(
        key="cash_bank",
        english_name="Bank cash or short notice deposit",
        hebrew_name="מזומן בבנק או פיקדון קצר",
        risk_level="very_low",
        min_horizon_months=0,
        liquidity_days=0,
        default_annual_return=0.005,
        default_annual_fee=0.0,
        default_tax_rate_on_gain=0.15,
        tax_treatment="Interest tax may apply. Check current withholding and indexation rules.",
        suitable_for="Emergency reserves, VAT and income-tax set-asides, near-term purchases.",
        caution="Usually loses purchasing power during high inflation.",
    ),
    "bank_deposit_fixed": VehicleOption(
        key="bank_deposit_fixed",
        english_name="Fixed bank deposit",
        hebrew_name="פיקדון בנקאי קצוב",
        risk_level="very_low",
        min_horizon_months=3,
        liquidity_days=None,
        default_annual_return=0.025,
        default_annual_fee=0.0,
        default_tax_rate_on_gain=0.15,
        tax_treatment="Interest tax depends on linkage and current law. Confirm the bank disclosure.",
        suitable_for="Known purchase date, low volatility needs, business cash reserve laddering.",
        caution="Early withdrawal can reduce or cancel interest.",
    ),
    "money_market_fund": VehicleOption(
        key="money_market_fund",
        english_name="Israeli money-market fund",
        hebrew_name="קרן כספית",
        risk_level="low",
        min_horizon_months=1,
        liquidity_days=1,
        default_annual_return=0.035,
        default_annual_fee=0.0015,
        default_tax_rate_on_gain=0.25,
        tax_treatment="Capital-gains tax rules vary by fund classification and investor status.",
        suitable_for="Short goals, liquidity, parking funds before supplier payments or tax advances.",
        caution="Not a bank deposit and not covered by deposit terms.",
    ),
    "government_bond_fund": VehicleOption(
        key="government_bond_fund",
        english_name="Israeli government bond fund",
        hebrew_name="קרן אג״ח ממשלתי",
        risk_level="low",
        min_horizon_months=18,
        liquidity_days=1,
        default_annual_return=0.04,
        default_annual_fee=0.005,
        default_tax_rate_on_gain=0.25,
        tax_treatment="Capital-gains tax generally applies to taxable accounts.",
        suitable_for="Medium-term goals where moderate price fluctuation is acceptable.",
        caution="Bond prices can fall when yields rise.",
    ),
    "taxable_brokerage_balanced": VehicleOption(
        key="taxable_brokerage_balanced",
        english_name="Balanced taxable portfolio",
        hebrew_name="תיק השקעות מאוזן חייב במס",
        risk_level="medium",
        min_horizon_months=36,
        liquidity_days=3,
        default_annual_return=0.055,
        default_annual_fee=0.008,
        default_tax_rate_on_gain=0.25,
        tax_treatment="Capital-gains tax generally applies on realized gains in taxable accounts.",
        suitable_for="Three-to-seven-year goals after emergency cash exists.",
        caution="Market drawdowns can coincide with the purchase date.",
    ),
    "equity_index_fund": VehicleOption(
        key="equity_index_fund",
        english_name="Global equity index fund",
        hebrew_name="קרן מחקה מניות גלובלית",
        risk_level="high",
        min_horizon_months=84,
        liquidity_days=3,
        default_annual_return=0.07,
        default_annual_fee=0.004,
        default_tax_rate_on_gain=0.25,
        tax_treatment="Capital-gains tax and foreign withholding may apply depending on wrapper.",
        suitable_for="Long-term wealth building and retirement accumulation.",
        caution="Unsuitable for money needed within a few years.",
    ),
    "keren_hishtalmut": VehicleOption(
        key="keren_hishtalmut",
        english_name="Training fund",
        hebrew_name="קרן השתלמות",
        risk_level="medium",
        min_horizon_months=72,
        liquidity_days=4,
        default_annual_return=0.06,
        default_annual_fee=0.006,
        default_tax_rate_on_gain=0.0,
        tax_treatment="Tax benefits depend on employee, self-employed, contribution limits, and withdrawal eligibility.",
        suitable_for="Six-year-plus goals for eligible employees or self-employed individuals.",
        caution="Do not treat non-liquid balances as available cash before eligibility.",
    ),
    "kupat_gemel_investment": VehicleOption(
        key="kupat_gemel_investment",
        english_name="Investment provident fund",
        hebrew_name="קופת גמל להשקעה",
        risk_level="medium",
        min_horizon_months=60,
        liquidity_days=4,
        default_annual_return=0.055,
        default_annual_fee=0.007,
        default_tax_rate_on_gain=0.25,
        tax_treatment="Annual contribution caps and tax rules must be checked for the relevant tax year.",
        suitable_for="Longer goals requiring flexible withdrawal compared with pension savings.",
        caution="Fees and investment track selection materially change outcomes.",
    ),
    "pension_fund": VehicleOption(
        key="pension_fund",
        english_name="Pension fund",
        hebrew_name="קרן פנסיה",
        risk_level="medium",
        min_horizon_months=120,
        liquidity_days=None,
        default_annual_return=0.055,
        default_annual_fee=0.005,
        default_tax_rate_on_gain=0.0,
        tax_treatment="Pension tax benefits, mandatory deposits, insurance cost, and annuity rules are personal.",
        suitable_for="Retirement income planning, not ordinary purchase funding.",
        caution="Early withdrawal can trigger severe tax and loss of insurance coverage.",
    ),
}


_RISK_ORDER = {"very_low": 0, "low": 1, "medium": 2, "high": 3}


def _validate_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise SavingsGoalError(f"{name} must be non-negative")


def _validate_rate(name: str, value: float, lower_bound: float = -0.999, upper_bound: float = 1.0) -> None:
    if value <= lower_bound or value > upper_bound:
        raise SavingsGoalError(f"{name} must be greater than {lower_bound} and at most {upper_bound}")


def monthly_rate_from_annual(annual_return: float) -> float:
    """Convert an effective annual return to an effective monthly return."""

    _validate_rate("annual_return", annual_return)
    return (1.0 + annual_return) ** (1.0 / 12.0) - 1.0


def effective_annual_return(
    annual_return: float,
    annual_fee: float = 0.0,
    tax_rate_on_gain: float = 0.0,
) -> float:
    """Approximate annual return after annual fees and tax drag on positive gains.

    The calculation intentionally stays conservative and deterministic. Actual
    Israeli taxation can depend on linkage, wrapper, fund classification,
    realization timing, residency, and personal status.
    """

    _validate_rate("annual_return", annual_return)
    _validate_non_negative("annual_fee", annual_fee)
    if annual_fee >= 1:
        raise SavingsGoalError("annual_fee must be below 1.0")
    if not 0 <= tax_rate_on_gain <= 1:
        raise SavingsGoalError("tax_rate_on_gain must be between 0 and 1")

    after_fee = annual_return - annual_fee
    if after_fee > 0:
        return after_fee * (1.0 - tax_rate_on_gain)
    return after_fee


def annuity_future_value_factor(
    monthly_return: float,
    months: int,
    contribution_timing: ContributionTiming = "end",
) -> float:
    """Future-value factor for equal monthly deposits."""

    if months <= 0:
        raise SavingsGoalError("months must be greater than zero")
    if contribution_timing not in ("end", "beginning"):
        raise SavingsGoalError("contribution_timing must be 'end' or 'beginning'")
    if abs(monthly_return) < 1e-12:
        factor = float(months)
    else:
        factor = ((1.0 + monthly_return) ** months - 1.0) / monthly_return
    if contribution_timing == "beginning":
        factor *= 1.0 + monthly_return
    return factor


def project_balance(
    current_savings: float,
    monthly_deposit: float,
    months: int,
    annual_return: float,
    contribution_timing: ContributionTiming = "end",
) -> float:
    """Project a balance with current savings and equal monthly deposits."""

    _validate_non_negative("current_savings", current_savings)
    _validate_non_negative("monthly_deposit", monthly_deposit)
    if months <= 0:
        raise SavingsGoalError("months must be greater than zero")
    monthly_return = monthly_rate_from_annual(annual_return)
    current_future_value = current_savings * (1.0 + monthly_return) ** months
    deposit_future_value = monthly_deposit * annuity_future_value_factor(
        monthly_return, months, contribution_timing
    )
    return current_future_value + deposit_future_value


def future_target_amount(
    target_amount: float,
    months: int,
    inflation_rate: float = 0.0,
    amount_is_today_terms: bool = True,
) -> float:
    """Convert a target to the expected future nominal target amount."""

    _validate_non_negative("target_amount", target_amount)
    if months <= 0:
        raise SavingsGoalError("months must be greater than zero")
    _validate_rate("inflation_rate", inflation_rate)
    if not amount_is_today_terms:
        return target_amount
    return target_amount * (1.0 + inflation_rate) ** (months / 12.0)


def required_monthly_savings(
    target_amount: float,
    months: int,
    current_savings: float = 0.0,
    current_monthly_savings: float = 0.0,
    annual_return: float = 0.0,
    annual_fee: float = 0.0,
    tax_rate_on_gain: float = 0.0,
    inflation_rate: float = 0.0,
    amount_is_today_terms: bool = True,
    contribution_timing: ContributionTiming = "end",
) -> float:
    """Compute the extra monthly savings needed to reach a target."""

    _validate_non_negative("current_savings", current_savings)
    _validate_non_negative("current_monthly_savings", current_monthly_savings)

    target_future = future_target_amount(target_amount, months, inflation_rate, amount_is_today_terms)
    net_annual = effective_annual_return(annual_return, annual_fee, tax_rate_on_gain)
    monthly_return = monthly_rate_from_annual(net_annual)
    current_future = current_savings * (1.0 + monthly_return) ** months
    existing_monthly_future = current_monthly_savings * annuity_future_value_factor(
        monthly_return, months, contribution_timing
    )
    remaining = target_future - current_future - existing_monthly_future
    if remaining <= 0:
        return 0.0
    factor = annuity_future_value_factor(monthly_return, months, contribution_timing)
    return remaining / factor


def build_goal_plan(request: GoalRequest) -> SavingsPlanResult:
    """Build a complete goal plan with warnings and a vehicle preset."""

    _validate_non_negative("target_amount", request.target_amount)
    _validate_non_negative("current_savings", request.current_savings)
    _validate_non_negative("current_monthly_savings", request.current_monthly_savings)
    if request.months <= 0:
        raise SavingsGoalError("months must be greater than zero")
    if request.monthly_income is not None:
        _validate_non_negative("monthly_income", request.monthly_income)

    vehicle = None
    if request.vehicle_key:
        try:
            vehicle = VEHICLES[request.vehicle_key]
        except KeyError as exc:
            raise SavingsGoalError(f"unknown vehicle_key: {request.vehicle_key}") from exc

    annual_return = request.annual_return
    annual_fee = request.annual_fee
    tax_rate = request.tax_rate_on_gain
    if vehicle is not None:
        annual_return = vehicle.default_annual_return if annual_return is None else annual_return
        annual_fee = vehicle.default_annual_fee if annual_fee is None else annual_fee
        tax_rate = vehicle.default_tax_rate_on_gain if tax_rate is None else tax_rate
    annual_return = 0.0 if annual_return is None else annual_return
    annual_fee = 0.0 if annual_fee is None else annual_fee
    tax_rate = 0.0 if tax_rate is None else tax_rate

    net_annual = effective_annual_return(annual_return, annual_fee, tax_rate)
    monthly_return = monthly_rate_from_annual(net_annual)
    target_future = future_target_amount(
        request.target_amount, request.months, request.inflation_rate, request.amount_is_today_terms
    )
    projected_current = request.current_savings * (1.0 + monthly_return) ** request.months
    projected_existing = request.current_monthly_savings * annuity_future_value_factor(
        monthly_return, request.months, request.contribution_timing
    )
    monthly_required = required_monthly_savings(
        target_amount=request.target_amount,
        months=request.months,
        current_savings=request.current_savings,
        current_monthly_savings=request.current_monthly_savings,
        annual_return=annual_return,
        annual_fee=annual_fee,
        tax_rate_on_gain=tax_rate,
        inflation_rate=request.inflation_rate,
        amount_is_today_terms=request.amount_is_today_terms,
        contribution_timing=request.contribution_timing,
    )
    projected_total = project_balance(
        current_savings=request.current_savings,
        monthly_deposit=request.current_monthly_savings + monthly_required,
        months=request.months,
        annual_return=net_annual,
        contribution_timing=request.contribution_timing,
    )
    shortfall_at_current = max(0.0, target_future - projected_current - projected_existing)
    warnings: List[str] = []

    if vehicle is not None and request.months < vehicle.min_horizon_months:
        warnings.append(
            f"{vehicle.english_name} is usually too volatile or constrained for a {request.months}-month horizon."
        )
    if vehicle is not None and vehicle.key in {"keren_hishtalmut", "pension_fund"}:
        warnings.append("Verify contribution eligibility, withdrawal eligibility, and current tax limits before use.")
    if request.inflation_rate > 0.06:
        warnings.append("Inflation assumption is high; test a lower and higher scenario.")
    if annual_return > 0.12:
        warnings.append("Annual return assumption is aggressive; include a downside case.")
    if request.monthly_income and monthly_required > 0.3 * request.monthly_income:
        warnings.append("Required monthly saving exceeds 30% of monthly income; extend the timeline or reduce the target.")
    if request.current_savings == 0 and request.months <= 6:
        warnings.append("Short horizon and no current savings leave little room for volatility or delays.")
    if target_future <= request.current_savings:
        warnings.append("Current savings already cover the nominal target before investment return.")

    return SavingsPlanResult(
        goal_name=request.goal_name,
        target_amount_input=request.target_amount,
        target_future_value=target_future,
        months=request.months,
        years=request.months / 12.0,
        monthly_required=monthly_required,
        current_monthly_savings=request.current_monthly_savings,
        total_new_contributions=monthly_required * request.months,
        projected_current_savings_value=projected_current,
        projected_existing_monthly_value=projected_existing,
        projected_total_value=projected_total,
        shortfall_at_current_rate=shortfall_at_current,
        effective_annual_return=net_annual,
        monthly_return=monthly_return,
        inflation_rate=request.inflation_rate,
        vehicle=vehicle,
        warnings=warnings,
    )


def present_value_of_monthly_withdrawals(
    monthly_amount: float,
    months: int,
    annual_return: float,
    payment_timing: ContributionTiming = "beginning",
) -> float:
    """Present value of a monthly withdrawal stream."""

    _validate_non_negative("monthly_amount", monthly_amount)
    if months <= 0:
        raise SavingsGoalError("months must be greater than zero")
    monthly_return = monthly_rate_from_annual(annual_return)
    if abs(monthly_return) < 1e-12:
        pv = monthly_amount * months
    else:
        pv = monthly_amount * (1.0 - (1.0 + monthly_return) ** (-months)) / monthly_return
    if payment_timing == "beginning":
        pv *= 1.0 + monthly_return
    elif payment_timing != "end":
        raise SavingsGoalError("payment_timing must be 'end' or 'beginning'")
    return pv


def build_retirement_plan(request: RetirementRequest) -> RetirementPlanResult:
    """Calculate retirement gap using real returns and today's shekels."""

    if request.current_age < 0:
        raise SavingsGoalError("current_age must be non-negative")
    if request.retirement_age <= request.current_age:
        raise SavingsGoalError("retirement_age must be greater than current_age")
    if request.life_expectancy <= request.retirement_age:
        raise SavingsGoalError("life_expectancy must be greater than retirement_age")
    _validate_non_negative("desired_monthly_spending_today", request.desired_monthly_spending_today)
    _validate_non_negative("expected_monthly_pension_today", request.expected_monthly_pension_today)
    _validate_non_negative("current_retirement_savings", request.current_retirement_savings)

    accumulation_months = int(round((request.retirement_age - request.current_age) * 12))
    retirement_months = int(round((request.life_expectancy - request.retirement_age) * 12))
    monthly_gap = max(0.0, request.desired_monthly_spending_today - request.expected_monthly_pension_today)
    nest_egg = present_value_of_monthly_withdrawals(
        monthly_gap, retirement_months, request.annual_real_return_retirement, "beginning"
    )
    monthly_required = required_monthly_savings(
        target_amount=nest_egg,
        months=accumulation_months,
        current_savings=request.current_retirement_savings,
        current_monthly_savings=0.0,
        annual_return=request.annual_real_return_accumulation,
        annual_fee=0.0,
        tax_rate_on_gain=0.0,
        inflation_rate=0.0,
        amount_is_today_terms=False,
        contribution_timing=request.contribution_timing,
    )
    projected_current = project_balance(
        request.current_retirement_savings,
        0.0,
        accumulation_months,
        request.annual_real_return_accumulation,
        request.contribution_timing,
    )
    warnings: List[str] = []
    if monthly_gap == 0:
        warnings.append("Expected pension income covers desired spending in this simplified model.")
    if request.annual_real_return_accumulation > 0.06:
        warnings.append("Real accumulation return is aggressive; test a lower-return scenario.")
    if request.life_expectancy < 90:
        warnings.append("Consider a longevity stress test to age 95 or 100.")

    return RetirementPlanResult(
        accumulation_months=accumulation_months,
        retirement_months=retirement_months,
        monthly_income_gap_today=monthly_gap,
        required_nest_egg_today=nest_egg,
        monthly_required_today=monthly_required,
        projected_current_savings_today=projected_current,
        effective_annual_return_accumulation=request.annual_real_return_accumulation,
        annual_real_return_retirement=request.annual_real_return_retirement,
        warnings=warnings,
    )


def recommend_vehicle_candidates(
    horizon_months: int,
    risk_tolerance: Literal["very_low", "low", "medium", "high"] = "medium",
    liquidity_need: Literal["same_day", "few_days", "locked_ok"] = "few_days",
    tax_advantaged_available: bool = False,
) -> List[Dict[str, Any]]:
    """Rank informational vehicle candidates for the stated horizon and constraints."""

    if horizon_months <= 0:
        raise SavingsGoalError("horizon_months must be greater than zero")
    if risk_tolerance not in _RISK_ORDER:
        raise SavingsGoalError("risk_tolerance must be one of very_low, low, medium, high")
    if liquidity_need not in ("same_day", "few_days", "locked_ok"):
        raise SavingsGoalError("liquidity_need must be same_day, few_days, or locked_ok")

    max_risk = _RISK_ORDER[risk_tolerance]
    results: List[Dict[str, Any]] = []
    for vehicle in VEHICLES.values():
        reasons: List[str] = []
        score = 100
        risk_score = _RISK_ORDER[vehicle.risk_level]
        if risk_score > max_risk:
            score -= 35 + 10 * (risk_score - max_risk)
            reasons.append("risk level exceeds stated tolerance")
        else:
            score += 6
            reasons.append("risk level fits stated tolerance")
        if horizon_months < vehicle.min_horizon_months:
            score -= 45
            reasons.append("horizon is shorter than the usual minimum")
        else:
            score += min(20, (horizon_months - vehicle.min_horizon_months) // 12 + 4)
            reasons.append("horizon fits the vehicle constraint")
        if liquidity_need == "same_day" and vehicle.liquidity_days not in (0, 1):
            score -= 25
            reasons.append("liquidity may be too slow")
        elif liquidity_need == "few_days" and vehicle.liquidity_days is None:
            score -= 20
            reasons.append("liquidity may be locked or restricted")
        else:
            score += 4
            reasons.append("liquidity appears compatible")
        if tax_advantaged_available and vehicle.key in {"keren_hishtalmut", "pension_fund"}:
            score += 15
            reasons.append("tax-advantaged wrapper may be available subject to eligibility")
        if vehicle.key == "pension_fund" and horizon_months < 120:
            score -= 30
            reasons.append("pension savings should not fund ordinary purchases")

        results.append(
            {
                "key": vehicle.key,
                "english_name": vehicle.english_name,
                "hebrew_name": vehicle.hebrew_name,
                "risk_level": vehicle.risk_level,
                "score": score,
                "reasons": reasons,
                "caution": vehicle.caution,
            }
        )
    return sorted(results, key=lambda item: item["score"], reverse=True)



def _default_store_path(environment: EnvironmentName = "sandbox") -> Path:
    base = Path.home() / ".savings-goal-planner"
    return base / f"{environment}-goals.json"


def _goal_request_from_dict(data: Mapping[str, Any]) -> GoalRequest:
    return GoalRequest(
        goal_name=str(data.get("goal_name", "Savings goal")),
        target_amount=float(data["target_amount"]),
        months=int(data["months"]),
        current_savings=float(data.get("current_savings", 0.0)),
        current_monthly_savings=float(data.get("current_monthly_savings", 0.0)),
        annual_return=None if data.get("annual_return") is None else float(data["annual_return"]),
        annual_fee=None if data.get("annual_fee") is None else float(data["annual_fee"]),
        tax_rate_on_gain=None if data.get("tax_rate_on_gain") is None else float(data["tax_rate_on_gain"]),
        inflation_rate=float(data.get("inflation_rate", 0.0)),
        amount_is_today_terms=bool(data.get("amount_is_today_terms", True)),
        contribution_timing=data.get("contribution_timing", "end"),  # type: ignore[arg-type]
        vehicle_key=data.get("vehicle_key"),
        monthly_income=None if data.get("monthly_income") is None else float(data["monthly_income"]),
    )


def _stored_goal_from_dict(data: Mapping[str, Any]) -> StoredGoal:
    request = _goal_request_from_dict(data["request"])
    result = build_goal_plan(request)
    return StoredGoal(
        id=str(data["id"]),
        environment=data.get("environment", "sandbox"),  # type: ignore[arg-type]
        created_at=str(data["created_at"]),
        request=request,
        result=result,
    )


class GoalRepository:
    """Small JSON-backed repository for chained CLI workflows."""

    def __init__(self, path: str | Path | None = None, environment: EnvironmentName = "sandbox") -> None:
        if environment not in ("sandbox", "production"):
            raise SavingsGoalError("environment must be sandbox or production")
        self.environment = environment
        self.path = Path(path) if path is not None else _default_store_path(environment)

    def list_goals(self) -> List[StoredGoal]:
        data = self._load()
        return [_stored_goal_from_dict(item) for item in data]

    def create_goal(self, request: GoalRequest) -> StoredGoal:
        result = build_goal_plan(request)
        record = StoredGoal(
            id=uuid4().hex,
            environment=self.environment,
            created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            request=request,
            result=result,
        )
        data = self._load()
        data.append(record.to_dict())
        self._save(data)
        return record

    def get_goal(self, goal_id: str) -> StoredGoal:
        for record in self.list_goals():
            if record.id == goal_id:
                return record
        raise SavingsGoalError(f"goal not found: {goal_id}")

    def delete_goal(self, goal_id: str) -> bool:
        data = self._load()
        remaining = [item for item in data if item.get("id") != goal_id]
        changed = len(remaining) != len(data)
        if changed:
            self._save(remaining)
        return changed

    def _load(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SavingsGoalError(f"store file is not valid JSON: {self.path}") from exc
        if not isinstance(data, list):
            raise SavingsGoalError(f"store file must contain a JSON array: {self.path}")
        return data  # type: ignore[return-value]

    def _save(self, data: List[Dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



class SavingsGoalPlannerClient:
    """Typed synchronous and asynchronous facade."""

    def vehicles(self) -> Mapping[str, VehicleOption]:
        return VEHICLES

    def calculate_goal(self, request: GoalRequest) -> SavingsPlanResult:
        return build_goal_plan(request)

    async def calculate_goal_async(self, request: GoalRequest) -> SavingsPlanResult:
        await asyncio.sleep(0)
        return self.calculate_goal(request)

    def calculate_retirement(self, request: RetirementRequest) -> RetirementPlanResult:
        return build_retirement_plan(request)

    async def calculate_retirement_async(self, request: RetirementRequest) -> RetirementPlanResult:
        await asyncio.sleep(0)
        return self.calculate_retirement(request)

    def recommend_vehicles(
        self,
        horizon_months: int,
        risk_tolerance: Literal["very_low", "low", "medium", "high"] = "medium",
        liquidity_need: Literal["same_day", "few_days", "locked_ok"] = "few_days",
        tax_advantaged_available: bool = False,
    ) -> List[Dict[str, Any]]:
        return recommend_vehicle_candidates(
            horizon_months=horizon_months,
            risk_tolerance=risk_tolerance,
            liquidity_need=liquidity_need,
            tax_advantaged_available=tax_advantaged_available,
        )

    def create_goal(
        self,
        request: GoalRequest,
        store_path: str | Path | None = None,
        environment: EnvironmentName = "sandbox",
    ) -> StoredGoal:
        return GoalRepository(store_path, environment).create_goal(request)

    async def create_goal_async(
        self,
        request: GoalRequest,
        store_path: str | Path | None = None,
        environment: EnvironmentName = "sandbox",
    ) -> StoredGoal:
        await asyncio.sleep(0)
        return self.create_goal(request, store_path, environment)

    def get_goal(
        self,
        goal_id: str,
        store_path: str | Path | None = None,
        environment: EnvironmentName = "sandbox",
    ) -> StoredGoal:
        return GoalRepository(store_path, environment).get_goal(goal_id)

    def list_goals(
        self,
        store_path: str | Path | None = None,
        environment: EnvironmentName = "sandbox",
    ) -> List[StoredGoal]:
        return GoalRepository(store_path, environment).list_goals()


def format_ils(amount: float) -> str:
    """Format an amount in Israeli shekels."""

    return f"₪{amount:,.2f}"


__all__ = [
    "EnvironmentName",
    "GoalRepository",
    "GoalRequest",
    "RetirementRequest",
    "RetirementPlanResult",
    "SavingsGoalError",
    "SavingsGoalPlannerClient",
    "SavingsPlanResult",
    "StoredGoal",
    "VehicleOption",
    "VEHICLES",
    "annuity_future_value_factor",
    "build_goal_plan",
    "build_retirement_plan",
    "effective_annual_return",
    "format_ils",
    "future_target_amount",
    "monthly_rate_from_annual",
    "present_value_of_monthly_withdrawals",
    "project_balance",
    "recommend_vehicle_candidates",
    "_goal_request_from_dict",
    "required_monthly_savings",
]
