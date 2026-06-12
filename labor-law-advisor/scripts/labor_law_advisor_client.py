#!/usr/bin/env python3
"""Structured Israeli labor-law helper.

Deterministic calculations and triage helpers for common Israeli labor-law
questions. This module provides legal information support, not legal advice.
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional


Currency = "ILS"


class RiskLevel(str, Enum):
    """Triage risk labels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class MinimumWageRate:
    """Minimum wage rate with effective date."""

    effective_date: date
    monthly: float
    hourly: float
    source_note: str = (
        "Default rate included in this package; verify against the Ministry of Labor "
        "for the relevant pay month before payroll action."
    )


@dataclass
class AdvisoryResult:
    """Base serializable result."""

    operation: str
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key, value in list(data.items()):
            if isinstance(value, date):
                data[key] = value.isoformat()
            if isinstance(value, Enum):
                data[key] = value.value
        return data


@dataclass
class MinimumWageResult(AdvisoryResult):
    required: float = 0.0
    actual: float = 0.0
    shortfall: float = 0.0
    compliant: bool = True
    currency: str = Currency
    effective_date: date = field(default_factory=lambda: DEFAULT_MINIMUM_WAGE.effective_date)


@dataclass
class OvertimeResult(AdvisoryResult):
    regular_hours: float = 0.0
    first_overtime_hours: float = 0.0
    additional_overtime_hours: float = 0.0
    regular_pay: float = 0.0
    first_overtime_pay: float = 0.0
    additional_overtime_pay: float = 0.0
    total_pay: float = 0.0
    currency: str = Currency


@dataclass
class SeveranceResult(AdvisoryResult):
    estimated_statutory: float = 0.0
    covered_by_section14_balance: Optional[float] = None
    possible_top_up: Optional[float] = None
    eligible_by_tenure: bool = False
    tenure_years: float = 0.0
    currency: str = Currency


@dataclass
class SickPayResult(AdvisoryResult):
    sick_days: int = 0
    paid_days_value: float = 0.0
    breakdown: List[Dict[str, float]] = field(default_factory=list)
    currency: str = Currency


@dataclass
class VacationResult(AdvisoryResult):
    years_of_service: int = 0
    gross_calendar_days: int = 0
    net_working_days: int = 0
    prorated_days: float = 0.0


@dataclass
class CollectiveCheckResult(AdvisoryResult):
    risk_level: RiskLevel = RiskLevel.LOW
    recommended_sources: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)


@dataclass
class ClassificationResult(AdvisoryResult):
    employee_indicators: int = 0
    contractor_indicators: int = 0
    risk_level: RiskLevel = RiskLevel.LOW
    indicators: Dict[str, str] = field(default_factory=dict)


@dataclass
class ParentalRightsResult(AdvisoryResult):
    risk_level: RiskLevel = RiskLevel.LOW
    permit_check_required: bool = False
    protected_statuses: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)


@dataclass
class AdvisoryCase(AdvisoryResult):
    case_id: str = ""
    category: str = "general"
    environment: str = "sandbox"
    subject: Optional[str] = None
    created_on: date = field(default_factory=date.today)
    inputs: Dict[str, Any] = field(default_factory=dict)
    next_action: str = "collect missing facts and verify official sources"


DEFAULT_MINIMUM_WAGE = MinimumWageRate(
    effective_date=date(2026, 4, 1),
    monthly=6443.85,
    hourly=35.40,
)

VACATION_TABLE = {
    1: (16, 12),
    2: (16, 12),
    3: (16, 12),
    4: (16, 12),
    5: (16, 12),
    6: (18, 14),
    7: (21, 15),
    8: (22, 16),
    9: (23, 17),
    10: (24, 18),
    11: (25, 19),
    12: (26, 20),
    13: (27, 20),
}

CONVALESCENCE_DAYS = {
    1: 5,
    2: 6,
    3: 6,
    4: 7,
    5: 7,
    6: 7,
    7: 7,
    8: 7,
    9: 7,
    10: 7,
    11: 8,
    12: 8,
    13: 8,
    14: 8,
    15: 8,
    16: 9,
    17: 9,
    18: 9,
    19: 9,
}


def _round_money(value: float) -> float:
    return round(float(value) + 1e-9, 2)


def _validate_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative")


class LaborLawAdvisor:
    """Deterministic helper for Israeli labor-law triage and calculations."""

    def __init__(self, minimum_wage_rate: MinimumWageRate = DEFAULT_MINIMUM_WAGE) -> None:
        self.minimum_wage_rate = minimum_wage_rate
        self._cases: Dict[str, AdvisoryCase] = {}

    def create_case(
        self,
        *,
        category: str,
        environment: str = "sandbox",
        subject: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> AdvisoryCase:
        """Create a local advisory case record and return its identifier."""

        if environment not in {"sandbox", "production"}:
            raise ValueError("environment must be sandbox or production")
        category = category.strip().lower()
        if not category:
            raise ValueError("category must not be empty")
        payload = dict(inputs or {})
        seed = f"{environment}|{category}|{subject or ''}|{sorted(payload.items())}|{len(self._cases)}"
        case_id = "ll-" + str(abs(hash(seed)))[:10]
        result = AdvisoryCase(
            operation="create_case",
            case_id=case_id,
            category=category,
            environment=environment,
            subject=subject,
            inputs=payload,
            notes=["Local helper record only. Do not treat the identifier as a government filing number."],
        )
        self._cases[case_id] = result
        return result

    async def acreate_case(self, **kwargs: Any) -> AdvisoryCase:
        await asyncio.sleep(0)
        return self.create_case(**kwargs)

    def case_summary(self, *, case_id: str) -> AdvisoryCase:
        """Return a previously created local advisory case record."""

        if case_id not in self._cases:
            raise ValueError("case_id was not found in this advisor instance")
        result = self._cases[case_id]
        result.operation = "case_summary"
        return result

    async def acase_summary(self, **kwargs: Any) -> AdvisoryCase:
        await asyncio.sleep(0)
        return self.case_summary(**kwargs)

    def minimum_wage(
        self,
        *,
        monthly_salary: Optional[float] = None,
        hourly_wage: Optional[float] = None,
        regular_hours: Optional[float] = None,
        position_fraction: float = 1.0,
    ) -> MinimumWageResult:
        """Check minimum wage compliance for a monthly or hourly worker."""

        if not 0 < position_fraction <= 1:
            raise ValueError("position_fraction must be greater than 0 and at most 1")
        if monthly_salary is None and hourly_wage is None:
            raise ValueError("provide monthly_salary or hourly_wage")
        if monthly_salary is not None and hourly_wage is not None:
            raise ValueError("provide only one of monthly_salary or hourly_wage")

        notes = [self.minimum_wage_rate.source_note]
        if monthly_salary is not None:
            _validate_non_negative("monthly_salary", monthly_salary)
            required = self.minimum_wage_rate.monthly * position_fraction
            actual = monthly_salary
        else:
            assert hourly_wage is not None
            _validate_non_negative("hourly_wage", hourly_wage)
            if regular_hours is None:
                regular_hours = 1.0
                notes.append("regular_hours omitted; shortfall is calculated for one hour.")
            _validate_non_negative("regular_hours", regular_hours)
            required = self.minimum_wage_rate.hourly * regular_hours
            actual = hourly_wage * regular_hours

        shortfall = max(required - actual, 0.0)
        return MinimumWageResult(
            operation="minimum_wage",
            required=_round_money(required),
            actual=_round_money(actual),
            shortfall=_round_money(shortfall),
            compliant=shortfall <= 0.005,
            effective_date=self.minimum_wage_rate.effective_date,
            notes=notes,
        )

    async def aminimum_wage(self, **kwargs: Any) -> MinimumWageResult:
        await asyncio.sleep(0)
        return self.minimum_wage(**kwargs)

    def overtime(
        self,
        *,
        hourly_rate: float,
        daily_hours: float,
        daily_threshold: float = 8.6,
        first_overtime_limit: float = 2.0,
    ) -> OvertimeResult:
        """Calculate daily overtime using 125% and 150% blocks."""

        for name, value in {
            "hourly_rate": hourly_rate,
            "daily_hours": daily_hours,
            "daily_threshold": daily_threshold,
            "first_overtime_limit": first_overtime_limit,
        }.items():
            _validate_non_negative(name, value)

        regular_hours = min(daily_hours, daily_threshold)
        overtime_hours = max(daily_hours - daily_threshold, 0.0)
        first_ot = min(overtime_hours, first_overtime_limit)
        additional_ot = max(overtime_hours - first_overtime_limit, 0.0)

        regular_pay = regular_hours * hourly_rate
        first_pay = first_ot * hourly_rate * 1.25
        additional_pay = additional_ot * hourly_rate * 1.50
        total = regular_pay + first_pay + additional_pay

        return OvertimeResult(
            operation="overtime",
            regular_hours=round(regular_hours, 4),
            first_overtime_hours=round(first_ot, 4),
            additional_overtime_hours=round(additional_ot, 4),
            regular_pay=_round_money(regular_pay),
            first_overtime_pay=_round_money(first_pay),
            additional_overtime_pay=_round_money(additional_pay),
            total_pay=_round_money(total),
            notes=[
                "Daily calculation only. Check weekly threshold, night work, weekly rest, holidays, permits, and collective agreements."
            ],
        )

    async def aovertime(self, **kwargs: Any) -> OvertimeResult:
        await asyncio.sleep(0)
        return self.overtime(**kwargs)

    def weekly_overtime_hours(self, *, weekly_hours: float, weekly_threshold: float = 42.0) -> float:
        """Return weekly overtime hours before daily double-counting adjustments."""

        _validate_non_negative("weekly_hours", weekly_hours)
        _validate_non_negative("weekly_threshold", weekly_threshold)
        return round(max(weekly_hours - weekly_threshold, 0.0), 4)

    async def aweekly_overtime_hours(self, **kwargs: Any) -> float:
        await asyncio.sleep(0)
        return self.weekly_overtime_hours(**kwargs)

    def severance(
        self,
        *,
        monthly_salary: float,
        years: float = 0.0,
        months: float = 0.0,
        section14_balance: Optional[float] = None,
    ) -> SeveranceResult:
        """Estimate statutory severance using last monthly salary times tenure."""

        _validate_non_negative("monthly_salary", monthly_salary)
        _validate_non_negative("years", years)
        _validate_non_negative("months", months)
        if months >= 12:
            raise ValueError("months must be below 12; add full years to years")
        tenure_years = years + months / 12.0
        estimated = monthly_salary * tenure_years
        eligible = tenure_years >= 1.0
        top_up: Optional[float] = None

        if section14_balance is not None:
            _validate_non_negative("section14_balance", section14_balance)
            top_up = max(estimated - section14_balance, 0.0)

        notes = [
            "Estimate only. Check dismissal/resignation reason, Section 14 scope, fixed additions, variable pay, fund reports, Form 161, and release letters."
        ]
        if not eligible:
            notes.append("Tenure is below one year; statutory severance may not apply unless special continuity or avoidance rules apply.")

        return SeveranceResult(
            operation="severance",
            estimated_statutory=_round_money(estimated),
            covered_by_section14_balance=_round_money(section14_balance) if section14_balance is not None else None,
            possible_top_up=_round_money(top_up) if top_up is not None else None,
            eligible_by_tenure=eligible,
            tenure_years=round(tenure_years, 4),
            notes=notes,
        )

    async def aseverance(self, **kwargs: Any) -> SeveranceResult:
        await asyncio.sleep(0)
        return self.severance(**kwargs)

    def sick_pay(self, *, daily_wage: float, sick_days: int, accrued_days: Optional[float] = None) -> SickPayResult:
        """Calculate statutory sick pay: 0%, 50%, 50%, then 100%."""

        _validate_non_negative("daily_wage", daily_wage)
        if sick_days < 0:
            raise ValueError("sick_days must be non-negative")
        payable_days = sick_days
        notes = ["Statutory baseline. Check collective agreement, contract, medical certificate, and accrued balance."]
        if accrued_days is not None:
            _validate_non_negative("accrued_days", accrued_days)
            payable_days = min(sick_days, int(accrued_days))
            if accrued_days < sick_days:
                notes.append("Accrued sick balance is lower than absence length; unpaid or contractual treatment may apply for excess days.")

        breakdown: List[Dict[str, float]] = []
        total = 0.0
        for day in range(1, payable_days + 1):
            if day == 1:
                rate = 0.0
            elif day in (2, 3):
                rate = 0.5
            else:
                rate = 1.0
            amount = daily_wage * rate
            breakdown.append({"day": float(day), "rate": rate, "amount": _round_money(amount)})
            total += amount

        return SickPayResult(
            operation="sick_pay",
            sick_days=sick_days,
            paid_days_value=_round_money(total),
            breakdown=breakdown,
            notes=notes,
        )

    async def asick_pay(self, **kwargs: Any) -> SickPayResult:
        await asyncio.sleep(0)
        return self.sick_pay(**kwargs)

    def vacation(self, *, years_of_service: int, workweek_days: int = 5, position_fraction: float = 1.0) -> VacationResult:
        """Return statutory annual vacation baseline for seniority."""

        if years_of_service < 1:
            raise ValueError("years_of_service must be at least 1")
        if workweek_days not in (5, 6):
            raise ValueError("workweek_days must be 5 or 6")
        if not 0 < position_fraction <= 1:
            raise ValueError("position_fraction must be greater than 0 and at most 1")

        gross, net5 = VACATION_TABLE.get(years_of_service, (28, 20))
        net = net5 if workweek_days == 5 else gross
        return VacationResult(
            operation="vacation",
            years_of_service=years_of_service,
            gross_calendar_days=gross,
            net_working_days=net,
            prorated_days=round(net * position_fraction, 2),
            notes=[
                "Statutory baseline. Part-time accrual can depend on actual days worked; check contract and collective agreement."
            ],
        )

    async def avacation(self, **kwargs: Any) -> VacationResult:
        await asyncio.sleep(0)
        return self.vacation(**kwargs)

    def convalescence_days(self, *, years_of_service: int) -> int:
        """Return private-sector baseline convalescence days by seniority."""

        if years_of_service < 1:
            return 0
        return CONVALESCENCE_DAYS.get(years_of_service, 10)

    async def aconvalescence_days(self, **kwargs: Any) -> int:
        await asyncio.sleep(0)
        return self.convalescence_days(**kwargs)

    def collective_check(
        self,
        *,
        sector: str = "",
        histadrut_dues_on_payslip: bool = False,
        workplace_committee: bool = False,
        public_sector: bool = False,
    ) -> CollectiveCheckResult:
        """Triage likelihood that a collective agreement or extension order must be checked."""

        sector_normalized = sector.strip().lower()
        high_signal_sectors = {
            "cleaning", "security", "construction", "transport", "hotel", "hotels",
            "caregiving", "nursing", "agriculture", "manpower", "public", "education",
            "catering", "שמירה", "ניקיון", "בניין", "הסעות", "מלונאות", "סיעוד",
            "חקלאות", "חינוך",
        }
        signals = 0
        if sector_normalized in high_signal_sectors:
            signals += 2
        if any(term in sector_normalized for term in high_signal_sectors if len(term) > 3):
            signals += 2
        if histadrut_dues_on_payslip:
            signals += 2
        if workplace_committee:
            signals += 2
        if public_sector:
            signals += 2

        if signals >= 4:
            risk = RiskLevel.HIGH
        elif signals >= 2:
            risk = RiskLevel.MEDIUM
        else:
            risk = RiskLevel.LOW

        return CollectiveCheckResult(
            operation="collective_check",
            risk_level=risk,
            recommended_sources=[
                "Ministry of Labor collective agreements database",
                "Sector extension orders",
                "Employment agreement and payslips",
                "Worker committee or union communications if available",
            ],
            next_steps=[
                "Identify employer legal name, sector, site, and job title.",
                "Search for workplace collective agreement and sector extension order.",
                "Compare coverage clauses and apply the most favorable lawful floor.",
            ],
            notes=["Histadrut dues are a signal to investigate; they do not alone prove every claimed term."],
        )

    async def acollective_check(self, **kwargs: Any) -> CollectiveCheckResult:
        await asyncio.sleep(0)
        return self.collective_check(**kwargs)

    def classification_risk(
        self,
        *,
        integrated_in_business: bool = False,
        fixed_schedule: bool = False,
        uses_company_tools: bool = False,
        single_client: bool = False,
        can_send_substitute: bool = True,
        invoices_with_vat: bool = True,
    ) -> ClassificationResult:
        """Triage employee-vs-contractor classification risk."""

        indicators: Dict[str, str] = {}
        employee_score = 0
        contractor_score = 0
        checks = {
            "integrated_in_business": integrated_in_business,
            "fixed_schedule": fixed_schedule,
            "uses_company_tools": uses_company_tools,
            "single_client": single_client,
            "personal_service_required": not can_send_substitute,
        }
        for key, value in checks.items():
            if value:
                employee_score += 1
                indicators[key] = "employee"
            else:
                contractor_score += 1
                indicators[key] = "contractor"

        if invoices_with_vat:
            contractor_score += 1
            indicators["invoices_with_vat"] = "contractor"
        else:
            employee_score += 1
            indicators["invoices_with_vat"] = "employee"

        if employee_score >= 5:
            risk = RiskLevel.HIGH
        elif employee_score >= 3:
            risk = RiskLevel.MEDIUM
        else:
            risk = RiskLevel.LOW

        return ClassificationResult(
            operation="classification_risk",
            employee_indicators=employee_score,
            contractor_indicators=contractor_score,
            risk_level=risk,
            indicators=indicators,
            notes=["Classification is fact-sensitive. Courts evaluate the whole relationship, not only invoices or contract labels."],
        )

    async def aclassification_risk(self, **kwargs: Any) -> ClassificationResult:
        await asyncio.sleep(0)
        return self.classification_risk(**kwargs)

    def parental_rights_triage(
        self,
        *,
        pregnant: bool = False,
        fertility_treatment: bool = False,
        birth_or_parenting_period: bool = False,
        returned_from_parental_leave: bool = False,
        employer_action: str = "none",
        months_employed: float = 0.0,
    ) -> ParentalRightsResult:
        """Triage protected-status risk for pregnancy, fertility, and parenting matters."""

        _validate_non_negative("months_employed", months_employed)
        statuses: List[str] = []
        if pregnant:
            statuses.append("pregnancy")
        if fertility_treatment:
            statuses.append("fertility_treatment")
        if birth_or_parenting_period:
            statuses.append("birth_or_parenting_period")
        if returned_from_parental_leave:
            statuses.append("return_from_parental_leave")

        action = employer_action.strip().lower()
        adverse = action in {"dismissal", "termination", "reduction", "pay_cut", "non_renewal", "hours_cut"}
        permit = bool(statuses and adverse)
        if permit and months_employed >= 6:
            risk = RiskLevel.CRITICAL
        elif permit:
            risk = RiskLevel.HIGH
        elif statuses:
            risk = RiskLevel.MEDIUM
        else:
            risk = RiskLevel.LOW

        next_steps = [
            "Confirm exact dates, tenure, employer knowledge, and proposed action.",
            "Check whether a Ministry of Labor permit is required before action.",
            "Preserve neutral business documentation and avoid pressure to resign.",
        ]
        if not statuses:
            next_steps.append("No protected parenting status supplied; continue ordinary labor-law analysis.")

        return ParentalRightsResult(
            operation="parental_rights_triage",
            risk_level=risk,
            permit_check_required=permit,
            protected_statuses=statuses,
            next_steps=next_steps,
            notes=["Protected-status rules are high risk. Escalate before dismissal, non-renewal, pay cut, or hours reduction."],
        )

    async def aparental_rights_triage(self, **kwargs: Any) -> ParentalRightsResult:
        await asyncio.sleep(0)
        return self.parental_rights_triage(**kwargs)


def format_ils(amount: float) -> str:
    """Format a number as Israeli shekels."""

    return f"₪{amount:,.2f}"


__all__ = [
    "AdvisoryCase",
    "AdvisoryResult",
    "ClassificationResult",
    "CollectiveCheckResult",
    "DEFAULT_MINIMUM_WAGE",
    "LaborLawAdvisor",
    "MinimumWageRate",
    "MinimumWageResult",
    "OvertimeResult",
    "ParentalRightsResult",
    "RiskLevel",
    "SeveranceResult",
    "SickPayResult",
    "VacationResult",
    "format_ils",
]
