#!/usr/bin/env python3
"""Structured mortgage and loan eligibility helper for Israeli housing finance.

The module is intentionally self-contained. It does not call a lender, credit
bureau, government service, or Bank of Israel system. It performs deterministic
calculations from provided inputs so results can be audited, tested, and adapted
to a lender policy file.
"""

from __future__ import annotations

import asyncio
import json
import math
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence


class EligibilityError(ValueError):
    """Raised when an eligibility request is incomplete or inconsistent."""


class PropertyStatus(str, Enum):
    """Property status used for standard Israeli LTV caps."""

    SINGLE_HOME = "single_home"
    REPLACEMENT_HOME = "replacement_home"
    INVESTMENT_PROPERTY = "investment_property"


class EligibilityStatus(str, Enum):
    """Machine-readable eligibility outcome."""

    ELIGIBLE = "eligible"
    NEEDS_REVIEW = "needs_review"
    NOT_ELIGIBLE = "not_eligible"


LTV_LIMITS: dict[PropertyStatus, float] = {
    PropertyStatus.SINGLE_HOME: 0.75,
    PropertyStatus.REPLACEMENT_HOME: 0.70,
    PropertyStatus.INVESTMENT_PROPERTY: 0.50,
}

DEFAULT_DSR_LIMIT = 0.50
DEFAULT_DSR_REVIEW_THRESHOLD = 0.40
DEFAULT_ANNUAL_RATE = 0.0525
DEFAULT_TERM_YEARS = 25
MAX_TERM_YEARS = 30
NIS = "₪"


@dataclass(frozen=True)
class LoanTrack:
    """One mortgage track in a mixed Israeli mortgage offer."""

    name: str
    principal: float
    annual_rate: float = DEFAULT_ANNUAL_RATE
    term_years: int = DEFAULT_TERM_YEARS
    interest_only_months: int = 0

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "LoanTrack":
        return cls(
            name=str(data.get("name", "track")),
            principal=_positive_number(data.get("principal"), "track.principal", allow_zero=True),
            annual_rate=normalize_rate(data.get("annual_rate", DEFAULT_ANNUAL_RATE)),
            term_years=int(data.get("term_years", DEFAULT_TERM_YEARS)),
            interest_only_months=int(data.get("interest_only_months", 0)),
        )

    def validate(self) -> None:
        if not self.name.strip():
            raise EligibilityError("track.name must not be empty")
        _positive_number(self.principal, "track.principal", allow_zero=True)
        if self.annual_rate < 0:
            raise EligibilityError("track.annual_rate must not be negative")
        if not 1 <= self.term_years <= MAX_TERM_YEARS:
            raise EligibilityError(f"track.term_years must be between 1 and {MAX_TERM_YEARS}")
        if not 0 <= self.interest_only_months <= self.term_years * 12:
            raise EligibilityError("track.interest_only_months must be within the loan term")


@dataclass(frozen=True)
class IncomeRecord:
    """One verified or provisional income observation."""

    period: str
    net_income: float
    verified: bool = True
    weight: float = 1.0

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "IncomeRecord":
        return cls(
            period=str(data.get("period", "")),
            net_income=_positive_number(data.get("net_income"), "income_records.net_income", allow_zero=True),
            verified=bool(data.get("verified", True)),
            weight=float(data.get("weight", 1.0)),
        )

    def validate(self) -> None:
        if not self.period:
            raise EligibilityError("income_records.period must not be empty")
        _positive_number(self.net_income, "income_records.net_income", allow_zero=True)
        if self.weight <= 0:
            raise EligibilityError("income_records.weight must be positive")


@dataclass(frozen=True)
class MortgageRequest:
    """Inputs for one Israeli mortgage eligibility calculation."""

    property_value: float
    requested_loan_amount: float
    property_status: PropertyStatus = PropertyStatus.SINGLE_HOME
    net_monthly_income: float | None = None
    income_records: tuple[IncomeRecord, ...] = ()
    existing_monthly_debt: float = 0.0
    cash_equity: float | None = None
    annual_rate: float = DEFAULT_ANNUAL_RATE
    term_years: int = DEFAULT_TERM_YEARS
    dsr_limit: float = DEFAULT_DSR_LIMIT
    dsr_review_threshold: float = DEFAULT_DSR_REVIEW_THRESHOLD
    tracks: tuple[LoanTrack, ...] = ()
    notes: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "MortgageRequest":
        status_value = data.get("property_status", data.get("status", PropertyStatus.SINGLE_HOME.value))
        try:
            status = status_value if isinstance(status_value, PropertyStatus) else PropertyStatus(str(status_value))
        except ValueError as exc:
            valid = ", ".join(item.value for item in PropertyStatus)
            raise EligibilityError(f"property_status must be one of: {valid}") from exc

        records = tuple(IncomeRecord.from_mapping(item) for item in data.get("income_records", ()) or ())
        tracks = tuple(LoanTrack.from_mapping(item) for item in data.get("tracks", ()) or ())
        net_income = data.get("net_monthly_income", None)
        cash_equity = data.get("cash_equity", None)

        return cls(
            property_value=_positive_number(data.get("property_value"), "property_value"),
            requested_loan_amount=_positive_number(data.get("requested_loan_amount", data.get("loan_amount")), "requested_loan_amount", allow_zero=True),
            property_status=status,
            net_monthly_income=None if net_income is None else _positive_number(net_income, "net_monthly_income", allow_zero=True),
            income_records=records,
            existing_monthly_debt=_positive_number(data.get("existing_monthly_debt", 0.0), "existing_monthly_debt", allow_zero=True),
            cash_equity=None if cash_equity is None else _positive_number(cash_equity, "cash_equity", allow_zero=True),
            annual_rate=normalize_rate(data.get("annual_rate", DEFAULT_ANNUAL_RATE)),
            term_years=int(data.get("term_years", DEFAULT_TERM_YEARS)),
            dsr_limit=normalize_ratio(data.get("dsr_limit", DEFAULT_DSR_LIMIT), "dsr_limit"),
            dsr_review_threshold=normalize_ratio(data.get("dsr_review_threshold", DEFAULT_DSR_REVIEW_THRESHOLD), "dsr_review_threshold"),
            tracks=tracks,
            notes=tuple(str(item) for item in data.get("notes", ()) or ()),
        )

    def validate(self) -> None:
        _positive_number(self.property_value, "property_value")
        _positive_number(self.requested_loan_amount, "requested_loan_amount", allow_zero=True)
        if self.requested_loan_amount > self.property_value:
            raise EligibilityError("requested_loan_amount must not exceed property_value")
        if self.net_monthly_income is None and not self.income_records:
            raise EligibilityError("provide net_monthly_income or income_records")
        if self.net_monthly_income is not None:
            _positive_number(self.net_monthly_income, "net_monthly_income", allow_zero=True)
        for record in self.income_records:
            record.validate()
        _positive_number(self.existing_monthly_debt, "existing_monthly_debt", allow_zero=True)
        if self.cash_equity is not None:
            _positive_number(self.cash_equity, "cash_equity", allow_zero=True)
        if self.annual_rate < 0:
            raise EligibilityError("annual_rate must not be negative")
        if not 1 <= self.term_years <= MAX_TERM_YEARS:
            raise EligibilityError(f"term_years must be between 1 and {MAX_TERM_YEARS}")
        if not 0 < self.dsr_limit <= 1:
            raise EligibilityError("dsr_limit must be greater than 0 and up to 1")
        if not 0 < self.dsr_review_threshold <= self.dsr_limit:
            raise EligibilityError("dsr_review_threshold must be greater than 0 and up to dsr_limit")
        for track in self.tracks:
            track.validate()
        if self.tracks:
            track_total = sum(track.principal for track in self.tracks)
            if not math.isclose(track_total, self.requested_loan_amount, abs_tol=1.0):
                raise EligibilityError("sum of tracks.principal must equal requested_loan_amount within ₪1")


@dataclass(frozen=True)
class MortgageResult:
    """Calculated eligibility output."""

    status: EligibilityStatus
    property_status: PropertyStatus
    property_value: float
    requested_loan_amount: float
    ltv_limit: float
    ltv: float
    required_equity: float
    provided_cash_equity: float | None
    net_monthly_income_used: float
    estimated_monthly_payment: float
    existing_monthly_debt: float
    dsr_limit: float
    dsr_review_threshold: float
    dsr: float
    max_loan_by_ltv: float
    max_monthly_payment_by_dsr: float
    max_loan_by_dsr: float
    binding_constraint: str
    reasons: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    recommendations: tuple[str, ...] = field(default_factory=tuple)
    track_payments: tuple[dict[str, float | str], ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["property_status"] = self.property_status.value
        return data

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def summary_lines(self) -> list[str]:
        return [
            f"Status: {self.status.value}",
            f"LTV: {self.ltv:.2%} / cap {self.ltv_limit:.2%}",
            f"Monthly payment: {format_nis(self.estimated_monthly_payment)}",
            f"DSR: {self.dsr:.2%} / limit {self.dsr_limit:.2%}",
            f"Binding constraint: {self.binding_constraint}",
        ]


def normalize_rate(value: Any) -> float:
    """Normalize annual interest rate input: 0.0525 or 5.25 both mean 5.25%."""

    rate = float(value)
    if rate < 0:
        raise EligibilityError("annual_rate must not be negative")
    if rate > 1:
        rate = rate / 100.0
    if rate > 0.5:
        raise EligibilityError("annual_rate appears too high after normalization")
    return rate


def normalize_ratio(value: Any, field_name: str) -> float:
    ratio = float(value)
    if ratio > 1:
        ratio = ratio / 100.0
    if not 0 < ratio <= 1:
        raise EligibilityError(f"{field_name} must be greater than 0 and up to 1")
    return ratio


def monthly_payment(principal: float, annual_rate: float, term_years: int, *, interest_only_months: int = 0) -> float:
    """Return the standard monthly amortizing payment after any interest-only period."""

    principal = _positive_number(principal, "principal", allow_zero=True)
    annual_rate = normalize_rate(annual_rate)
    if not 1 <= int(term_years) <= MAX_TERM_YEARS:
        raise EligibilityError(f"term_years must be between 1 and {MAX_TERM_YEARS}")
    months = int(term_years) * 12
    if not 0 <= int(interest_only_months) <= months:
        raise EligibilityError("interest_only_months must be within the loan term")
    amortizing_months = months - int(interest_only_months)
    if principal == 0:
        return 0.0
    if amortizing_months <= 0:
        return principal * (annual_rate / 12.0)
    monthly_rate = annual_rate / 12.0
    if monthly_rate == 0:
        return principal / amortizing_months
    factor = (1 + monthly_rate) ** amortizing_months
    return principal * monthly_rate * factor / (factor - 1)


def interest_only_payment(principal: float, annual_rate: float) -> float:
    principal = _positive_number(principal, "principal", allow_zero=True)
    annual_rate = normalize_rate(annual_rate)
    return principal * annual_rate / 12.0


def principal_from_payment(monthly_payment_amount: float, annual_rate: float, term_years: int) -> float:
    """Return maximum principal supported by a monthly payment under annuity math."""

    payment = _positive_number(monthly_payment_amount, "monthly_payment_amount", allow_zero=True)
    annual_rate = normalize_rate(annual_rate)
    if not 1 <= int(term_years) <= MAX_TERM_YEARS:
        raise EligibilityError(f"term_years must be between 1 and {MAX_TERM_YEARS}")
    months = int(term_years) * 12
    if payment == 0:
        return 0.0
    monthly_rate = annual_rate / 12.0
    if monthly_rate == 0:
        return payment * months
    return payment * (1 - (1 + monthly_rate) ** -months) / monthly_rate


def ltv_limit_for(status: PropertyStatus | str) -> float:
    if not isinstance(status, PropertyStatus):
        status = PropertyStatus(str(status))
    return LTV_LIMITS[status]


def max_loan_by_ltv(property_value: float, status: PropertyStatus | str) -> float:
    return _positive_number(property_value, "property_value") * ltv_limit_for(status)


def stabilize_net_income(records: Sequence[IncomeRecord | Mapping[str, Any]], *, trim_outliers: bool = False) -> float:
    """Return weighted average net monthly income from verified records."""

    normalized: list[IncomeRecord] = [
        item if isinstance(item, IncomeRecord) else IncomeRecord.from_mapping(item)
        for item in records
    ]
    for item in normalized:
        item.validate()
    verified = [item for item in normalized if item.verified]
    if not verified:
        raise EligibilityError("at least one verified income record is required")
    if trim_outliers and len(verified) >= 6:
        ordered = sorted(verified, key=lambda item: item.net_income)
        verified = ordered[1:-1]
    total_weight = sum(item.weight for item in verified)
    return sum(item.net_income * item.weight for item in verified) / total_weight


def build_default_track(request: MortgageRequest) -> LoanTrack:
    return LoanTrack(
        name="default",
        principal=request.requested_loan_amount,
        annual_rate=request.annual_rate,
        term_years=request.term_years,
    )


def calculate_eligibility(request: MortgageRequest | Mapping[str, Any]) -> MortgageResult:
    """Calculate LTV, payment, DSR, constraints, and recommendations."""

    if not isinstance(request, MortgageRequest):
        request = MortgageRequest.from_mapping(request)
    request.validate()

    income = (
        request.net_monthly_income
        if request.net_monthly_income is not None
        else stabilize_net_income(request.income_records, trim_outliers=True)
    )
    if income <= 0:
        raise EligibilityError("net monthly income must be greater than 0")

    ltv_limit = ltv_limit_for(request.property_status)
    ltv = request.requested_loan_amount / request.property_value
    ltv_cap_amount = max_loan_by_ltv(request.property_value, request.property_status)
    required_equity = request.property_value - request.requested_loan_amount

    tracks = request.tracks or (build_default_track(request),)
    track_rows: list[dict[str, float | str]] = []
    total_payment = 0.0
    for track in tracks:
        payment = monthly_payment(
            track.principal,
            track.annual_rate,
            track.term_years,
            interest_only_months=track.interest_only_months,
        )
        total_payment += payment
        track_rows.append(
            {
                "name": track.name,
                "principal": round(track.principal, 2),
                "annual_rate": round(track.annual_rate, 8),
                "term_years": float(track.term_years),
                "monthly_payment": round(payment, 2),
            }
        )

    dsr = (total_payment + request.existing_monthly_debt) / income
    available_payment_by_dsr = max(0.0, income * request.dsr_limit - request.existing_monthly_debt)
    dsr_amount = principal_from_payment(available_payment_by_dsr, request.annual_rate, request.term_years)

    reasons: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    if request.requested_loan_amount > ltv_cap_amount + 1e-7:
        reasons.append(f"Requested loan exceeds the standard LTV cap for {request.property_status.value}.")
        recommendations.append(
            f"Reduce the loan to {format_nis(ltv_cap_amount)} or increase equity by {format_nis(request.requested_loan_amount - ltv_cap_amount)}."
        )

    if request.cash_equity is not None and request.cash_equity + 1e-7 < required_equity:
        reasons.append("Provided cash equity is below the equity required by the purchase price and requested loan.")
        recommendations.append(
            f"Add at least {format_nis(required_equity - request.cash_equity)} in verified equity or lower the purchase price."
        )

    if total_payment > available_payment_by_dsr + 1e-7:
        reasons.append("Estimated monthly repayment exceeds the configured DSR limit.")
        recommendations.append(
            f"Reduce the monthly repayment to {format_nis(available_payment_by_dsr)}, extend the term within policy, lower the loan, or reduce other debt."
        )

    if dsr > request.dsr_review_threshold and dsr <= request.dsr_limit:
        warnings.append("DSR is above the review threshold and may require stronger income evidence or lender exception handling.")
        recommendations.append("Prepare bank statements, tax assessments, current accountant confirmation, and explanations for variable income.")

    if ltv > ltv_limit * 0.95 and ltv <= ltv_limit:
        warnings.append("LTV is close to the cap; valuation differences, fees, or linkage may change the outcome.")
        recommendations.append("Keep a buffer for appraisal differences, purchase tax, legal fees, broker fees, and moving costs.")

    verified_records = [record for record in request.income_records if record.verified]
    if request.income_records and len(verified_records) < 6:
        warnings.append("Income history contains fewer than six verified periods.")
        recommendations.append("Use at least 6-12 verified months for salaried borrowers and 12-24 months for freelancers or small businesses.")

    if reasons:
        status = EligibilityStatus.NOT_ELIGIBLE
    elif warnings:
        status = EligibilityStatus.NEEDS_REVIEW
    else:
        status = EligibilityStatus.ELIGIBLE

    binding_constraint = "ltv" if ltv_cap_amount < dsr_amount else "dsr"
    if request.cash_equity is not None and request.cash_equity < required_equity:
        binding_constraint = "cash_equity"

    return MortgageResult(
        status=status,
        property_status=request.property_status,
        property_value=round(request.property_value, 2),
        requested_loan_amount=round(request.requested_loan_amount, 2),
        ltv_limit=ltv_limit,
        ltv=ltv,
        required_equity=round(required_equity, 2),
        provided_cash_equity=None if request.cash_equity is None else round(request.cash_equity, 2),
        net_monthly_income_used=round(income, 2),
        estimated_monthly_payment=round(total_payment, 2),
        existing_monthly_debt=round(request.existing_monthly_debt, 2),
        dsr_limit=request.dsr_limit,
        dsr_review_threshold=request.dsr_review_threshold,
        dsr=dsr,
        max_loan_by_ltv=round(ltv_cap_amount, 2),
        max_monthly_payment_by_dsr=round(available_payment_by_dsr, 2),
        max_loan_by_dsr=round(dsr_amount, 2),
        binding_constraint=binding_constraint,
        reasons=tuple(reasons),
        warnings=tuple(dict.fromkeys(warnings)),
        recommendations=tuple(dict.fromkeys(recommendations)),
        track_payments=tuple(track_rows),
    )


class MortgageEligibilityClient:
    """Typed sync and async facade around the local calculator."""

    def __init__(
        self,
        *,
        default_annual_rate: float = DEFAULT_ANNUAL_RATE,
        default_term_years: int = DEFAULT_TERM_YEARS,
        default_dsr_limit: float = DEFAULT_DSR_LIMIT,
    ) -> None:
        self.default_annual_rate = normalize_rate(default_annual_rate)
        self.default_term_years = int(default_term_years)
        self.default_dsr_limit = normalize_ratio(default_dsr_limit, "default_dsr_limit")

    def calculate(self, request: MortgageRequest | Mapping[str, Any]) -> MortgageResult:
        if isinstance(request, Mapping):
            merged = {
                "annual_rate": self.default_annual_rate,
                "term_years": self.default_term_years,
                "dsr_limit": self.default_dsr_limit,
                **dict(request),
            }
            return calculate_eligibility(merged)
        return calculate_eligibility(request)

    async def acalculate(self, request: MortgageRequest | Mapping[str, Any]) -> MortgageResult:
        await asyncio.sleep(0)
        return self.calculate(request)

    def calculate_file(self, path: str | Path) -> MortgageResult:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return self.calculate(data)


def load_json_request(path: str | Path) -> MortgageRequest:
    return MortgageRequest.from_mapping(json.loads(Path(path).read_text(encoding="utf-8")))


def save_result(result: MortgageResult, path: str | Path) -> None:
    Path(path).write_text(result.to_json() + "\n", encoding="utf-8")


def format_nis(value: float) -> str:
    return f"{NIS}{value:,.0f}"


def _positive_number(value: Any, field_name: str, *, allow_zero: bool = False) -> float:
    if value is None:
        raise EligibilityError(f"{field_name} is required")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise EligibilityError(f"{field_name} must be numeric") from exc
    if not math.isfinite(number):
        raise EligibilityError(f"{field_name} must be finite")
    if allow_zero:
        if number < 0:
            raise EligibilityError(f"{field_name} must not be negative")
    elif number <= 0:
        raise EligibilityError(f"{field_name} must be greater than 0")
    return number


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Calculate Israeli mortgage eligibility from a JSON request.")
    parser.add_argument("request_json", help="Path to a JSON request file")
    parser.add_argument("--output", "-o", help="Optional path for JSON result")
    args = parser.parse_args()

    client = MortgageEligibilityClient()
    result = client.calculate_file(args.request_json)
    if args.output:
        save_result(result, args.output)
    print(result.to_json())
