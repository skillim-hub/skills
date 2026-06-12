#!/usr/bin/env python3
"""Importable helper for Israeli pension contribution calculations.

The module contains deterministic calculations for employee and self-employed
pension deposits, training fund deposits, and manager's insurance comparisons.
Rates are versioned so payroll teams can update a single table each tax year.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Dict, List, Literal, Optional


Money = float
ProductType = Literal["pension_fund", "bituach_menahalim"]


@dataclass(frozen=True)
class RateTable:
    """Versioned rates and ceilings used by the calculator."""

    tax_year: int = 2026
    effective_from: str = "2026-01-01"
    currency: str = "ILS"

    employee_pension_rate: float = 0.06
    employer_pension_rate: float = 0.065
    employer_severance_min_rate: float = 0.06
    employer_severance_section14_rate: float = 0.0833

    hishtalmut_employee_rate: float = 0.025
    hishtalmut_employer_rate: float = 0.075
    hishtalmut_employee_salary_cap: Money = 15_712.0
    self_hishtalmut_deduction_cap: Money = 13_203.0
    self_hishtalmut_profit_exempt_cap: Money = 20_566.0
    self_hishtalmut_qualifying_income_cap: Money = 293_397.0

    average_wage_monthly: Money = 13_769.0
    comprehensive_pension_monthly_deposit_cap: Money = 5_645.29

    self_pension_low_rate: float = 0.0445
    self_pension_high_rate: float = 0.1255
    self_pension_age_min: int = 21
    default_retirement_age: int = 67

    self_pension_qualifying_income_cap: Money = 232_800.0
    self_pension_credit_contribution_cap: Money = 12_804.0
    self_pension_deduction_contribution_cap: Money = 25_608.0
    self_pension_credit_rate: float = 0.35


DEFAULT_RATES = RateTable()


@dataclass(frozen=True)
class EmployeeContributionResult:
    """Employee monthly contribution result."""

    tax_year: int
    product: ProductType
    gross_salary: Money
    pensionable_salary: Money
    section14_full: bool
    employee_pension: Money
    employer_pension: Money
    employer_severance: Money
    total_retirement_deposit: Money
    comprehensive_pension_fund_deposit: Money
    supplemental_or_policy_deposit: Money
    employee_hishtalmut: Money
    employer_hishtalmut: Money
    employer_hishtalmut_tax_free: Money
    employer_hishtalmut_taxable: Money
    total_hishtalmut: Money
    total_employee_cash_outflow: Money
    total_employer_cash_cost: Money
    total_monthly_deposit: Money
    annualized_total_deposit: Money
    notes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class SelfEmployedContributionResult:
    """Self-employed annual contribution result."""

    tax_year: int
    annual_net_taxable_income: Money
    monthly_net_taxable_income: Money
    age: int
    first_year_business: bool
    retirement_age_used: int
    mandatory_pension_annual: Money
    mandatory_pension_monthly_average: Money
    low_bracket_annual_income: Money
    high_bracket_annual_income: Money
    annual_pension_deposit_entered: Money
    pension_credit_base: Money
    estimated_pension_tax_credit: Money
    pension_deduction_base: Money
    remaining_pension_room_for_benefit: Money
    annual_hishtalmut_deposit_entered: Money
    hishtalmut_deductible_amount: Money
    hishtalmut_profit_exempt_deposit: Money
    hishtalmut_non_deductible_but_profit_exempt: Money
    notes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProductComparisonResult:
    """High-level comparison of retirement product deposits for a salary."""

    pension_fund: EmployeeContributionResult
    bituach_menahalim: EmployeeContributionResult
    headline: str
    cautions: List[str] = field(default_factory=list)


class ContributionInputError(ValueError):
    """Raised when calculation inputs are invalid."""


def _round_money(value: float) -> Money:
    """Round monetary values to agorot precision."""

    return round(float(value) + 1e-9, 2)


def _validate_non_negative(value: float, name: str) -> None:
    if value < 0:
        raise ContributionInputError(f"{name} must be non-negative")


def format_ils(value: float) -> str:
    """Format a number as Israeli shekels."""

    return f"₪{_round_money(value):,.2f}"


def employee_contributions(
    gross_salary: float,
    *,
    pensionable_salary: Optional[float] = None,
    product: ProductType = "pension_fund",
    include_hishtalmut: bool = False,
    section14_full: bool = False,
    rates: RateTable = DEFAULT_RATES,
) -> EmployeeContributionResult:
    """Calculate employee monthly pension and training fund deposits."""

    _validate_non_negative(gross_salary, "gross_salary")
    base_salary = gross_salary if pensionable_salary is None else pensionable_salary
    _validate_non_negative(base_salary, "pensionable_salary")

    if base_salary > gross_salary:
        raise ContributionInputError("pensionable_salary cannot exceed gross_salary")
    if product not in ("pension_fund", "bituach_menahalim"):
        raise ContributionInputError("product must be 'pension_fund' or 'bituach_menahalim'")

    severance_rate = rates.employer_severance_section14_rate if section14_full else rates.employer_severance_min_rate

    employee_pension = _round_money(base_salary * rates.employee_pension_rate)
    employer_pension = _round_money(base_salary * rates.employer_pension_rate)
    employer_severance = _round_money(base_salary * severance_rate)
    total_retirement = _round_money(employee_pension + employer_pension + employer_severance)

    if product == "pension_fund":
        comprehensive = min(total_retirement, rates.comprehensive_pension_monthly_deposit_cap)
        supplemental = max(0.0, total_retirement - rates.comprehensive_pension_monthly_deposit_cap)
    else:
        comprehensive = 0.0
        supplemental = total_retirement

    comprehensive = _round_money(comprehensive)
    supplemental = _round_money(supplemental)

    employee_hish = employer_hish = employer_hish_tax_free = employer_hish_taxable = 0.0
    notes: List[str] = []

    if include_hishtalmut:
        employee_hish = _round_money(gross_salary * rates.hishtalmut_employee_rate)
        employer_hish = _round_money(gross_salary * rates.hishtalmut_employer_rate)
        tax_free_basis = min(gross_salary, rates.hishtalmut_employee_salary_cap)
        employer_hish_tax_free = _round_money(tax_free_basis * rates.hishtalmut_employer_rate)
        employer_hish_taxable = _round_money(max(0.0, employer_hish - employer_hish_tax_free))
        if gross_salary > rates.hishtalmut_employee_salary_cap:
            notes.append("Employer training fund deposits above the salary ceiling are taxable income to the employee.")

    total_hishtalmut = _round_money(employee_hish + employer_hish)
    employee_outflow = _round_money(employee_pension + employee_hish)
    employer_cost = _round_money(employer_pension + employer_severance + employer_hish)
    total_monthly = _round_money(total_retirement + total_hishtalmut)

    if product == "pension_fund" and supplemental > 0:
        notes.append("Part of the retirement deposit exceeds the comprehensive pension fund monthly deposit ceiling; route the excess to a supplemental pension fund, provident fund, or other allowed product.")
    if product == "bituach_menahalim":
        if gross_salary <= rates.average_wage_monthly * 2:
            notes.append("For a new Bituach Menahalim policy from 01/09/2023, confirm eligibility; current rules generally require salary above twice the average wage and funding the comprehensive pension fund ceiling first. Legacy policies require separate review.")
        else:
            notes.append("For a new Bituach Menahalim policy from 01/09/2023, confirm that deposits up to the comprehensive pension fund ceiling are funded before routing eligible excess to the policy. Legacy policies require separate review.")
    if base_salary < gross_salary:
        notes.append("Pensionable salary is lower than gross salary; document the employment agreement and payroll components.")
    if section14_full:
        notes.append("Severance calculated at 8.33% for full Section 14 treatment.")
    else:
        notes.append("Severance calculated at the 6% minimum contribution rate.")

    return EmployeeContributionResult(
        tax_year=rates.tax_year,
        product=product,
        gross_salary=_round_money(gross_salary),
        pensionable_salary=_round_money(base_salary),
        section14_full=section14_full,
        employee_pension=employee_pension,
        employer_pension=employer_pension,
        employer_severance=employer_severance,
        total_retirement_deposit=total_retirement,
        comprehensive_pension_fund_deposit=comprehensive,
        supplemental_or_policy_deposit=supplemental,
        employee_hishtalmut=employee_hish,
        employer_hishtalmut=employer_hish,
        employer_hishtalmut_tax_free=employer_hish_tax_free,
        employer_hishtalmut_taxable=employer_hish_taxable,
        total_hishtalmut=total_hishtalmut,
        total_employee_cash_outflow=employee_outflow,
        total_employer_cash_cost=employer_cost,
        total_monthly_deposit=total_monthly,
        annualized_total_deposit=_round_money(total_monthly * 12),
        notes=notes,
    )


def self_employed_contributions(
    annual_net_taxable_income: float,
    *,
    age: int,
    first_year_business: bool = False,
    retirement_age: Optional[int] = None,
    annual_pension_deposit: Optional[float] = None,
    annual_hishtalmut_deposit: Optional[float] = None,
    rates: RateTable = DEFAULT_RATES,
) -> SelfEmployedContributionResult:
    """Calculate self-employed mandatory pension and tax-benefit ceilings."""

    _validate_non_negative(annual_net_taxable_income, "annual_net_taxable_income")
    if age < 0 or age > 130:
        raise ContributionInputError("age must be realistic")

    legal_retirement_age = retirement_age or rates.default_retirement_age
    _validate_non_negative(float(legal_retirement_age), "retirement_age")
    monthly_income = annual_net_taxable_income / 12.0
    half_avg = rates.average_wage_monthly / 2.0
    full_avg = rates.average_wage_monthly
    notes: List[str] = []
    low_monthly = high_monthly = mandatory_monthly = 0.0

    if first_year_business:
        notes.append("First business year marked as exempt from mandatory self-employed pension deposits.")
    elif age < rates.self_pension_age_min:
        notes.append("Age is below the mandatory self-employed pension threshold.")
    elif age >= legal_retirement_age:
        notes.append("Age is at or above the retirement-age threshold used by the calculator.")
    else:
        low_monthly = min(monthly_income, half_avg)
        high_monthly = max(0.0, min(monthly_income, full_avg) - half_avg)
        mandatory_monthly = low_monthly * rates.self_pension_low_rate + high_monthly * rates.self_pension_high_rate

    mandatory_annual = _round_money(mandatory_monthly * 12)

    pension_deposit = mandatory_annual if annual_pension_deposit is None else annual_pension_deposit
    hish_deposit = rates.self_hishtalmut_profit_exempt_cap if annual_hishtalmut_deposit is None else annual_hishtalmut_deposit
    _validate_non_negative(pension_deposit, "annual_pension_deposit")
    _validate_non_negative(hish_deposit, "annual_hishtalmut_deposit")

    qualifying_income = min(annual_net_taxable_income, rates.self_pension_qualifying_income_cap)
    max_credit_base = min(qualifying_income * 0.055, rates.self_pension_credit_contribution_cap)
    max_deduction_base = min(qualifying_income * 0.11, rates.self_pension_deduction_contribution_cap)
    pension_credit_base = min(pension_deposit, max_credit_base)
    remaining_deposit = max(0.0, pension_deposit - pension_credit_base)
    pension_deduction_base = min(remaining_deposit, max_deduction_base)
    remaining_room = max(0.0, max_credit_base + max_deduction_base - pension_deposit)

    hish_deduction_cap_by_income = min(annual_net_taxable_income * 0.045, rates.self_hishtalmut_deduction_cap)
    hish_deductible = min(hish_deposit, hish_deduction_cap_by_income)
    hish_profit_exempt = min(hish_deposit, rates.self_hishtalmut_profit_exempt_cap)
    hish_gap = max(0.0, hish_profit_exempt - hish_deductible)

    if annual_net_taxable_income > rates.average_wage_monthly * 12:
        notes.append("Mandatory self-employed pension deposits do not increase above the annual average-wage ceiling.")
    if hish_deposit > rates.self_hishtalmut_profit_exempt_cap:
        notes.append("Training fund deposits above the profit-exempt ceiling can still be deposited, but gains may lose the preferred exemption.")
    if pension_deposit < mandatory_annual:
        notes.append("Entered pension deposit is lower than the calculated mandatory annual amount.")

    return SelfEmployedContributionResult(
        tax_year=rates.tax_year,
        annual_net_taxable_income=_round_money(annual_net_taxable_income),
        monthly_net_taxable_income=_round_money(monthly_income),
        age=age,
        first_year_business=first_year_business,
        retirement_age_used=int(legal_retirement_age),
        mandatory_pension_annual=mandatory_annual,
        mandatory_pension_monthly_average=_round_money(mandatory_monthly),
        low_bracket_annual_income=_round_money(low_monthly * 12),
        high_bracket_annual_income=_round_money(high_monthly * 12),
        annual_pension_deposit_entered=_round_money(pension_deposit),
        pension_credit_base=_round_money(pension_credit_base),
        estimated_pension_tax_credit=_round_money(pension_credit_base * rates.self_pension_credit_rate),
        pension_deduction_base=_round_money(pension_deduction_base),
        remaining_pension_room_for_benefit=_round_money(remaining_room),
        annual_hishtalmut_deposit_entered=_round_money(hish_deposit),
        hishtalmut_deductible_amount=_round_money(hish_deductible),
        hishtalmut_profit_exempt_deposit=_round_money(hish_profit_exempt),
        hishtalmut_non_deductible_but_profit_exempt=_round_money(hish_gap),
        notes=notes,
    )


def compare_products(
    gross_salary: float,
    *,
    pensionable_salary: Optional[float] = None,
    include_hishtalmut: bool = False,
    section14_full: bool = False,
    rates: RateTable = DEFAULT_RATES,
) -> ProductComparisonResult:
    """Compare the deposit routing for pension fund and manager's insurance."""

    pension_fund = employee_contributions(
        gross_salary,
        pensionable_salary=pensionable_salary,
        product="pension_fund",
        include_hishtalmut=include_hishtalmut,
        section14_full=section14_full,
        rates=rates,
    )
    policy = employee_contributions(
        gross_salary,
        pensionable_salary=pensionable_salary,
        product="bituach_menahalim",
        include_hishtalmut=include_hishtalmut,
        section14_full=section14_full,
        rates=rates,
    )
    return ProductComparisonResult(
        pension_fund=pension_fund,
        bituach_menahalim=policy,
        headline="Total required split is identical before product fees; routing, insurance cost, and policy terms differ.",
        cautions=[
            "Compare management fees, disability cover, survivors cover, underwriting exclusions, and pre-2013 guaranteed annuity factors before replacing an existing policy.",
            "Use a licensed professional for product replacement, severance decisions, and high-balance cases.",
        ],
    )


def to_plain_dict(value: Any) -> Dict[str, Any]:
    """Convert a result dataclass to a JSON-ready dictionary."""

    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return value
    raise TypeError("value must be a dataclass result or dictionary")


def to_json(value: Any, *, indent: int = 2) -> str:
    """Serialize a result dataclass as JSON."""

    return json.dumps(to_plain_dict(value), ensure_ascii=False, indent=indent, sort_keys=True)



def _canonical_payload(value: Any) -> str:
    """Serialize a calculation payload for stable hashing."""

    return json.dumps(to_plain_dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_calculation_id(kind: str, result: Any, *, environment: str = "sandbox") -> str:
    """Build a deterministic, non-secret identifier for a calculation result."""

    if environment not in {"sandbox", "production"}:
        raise ContributionInputError("environment must be 'sandbox' or 'production'")
    digest = hashlib.sha256(f"{environment}:{kind}:{_canonical_payload(result)}".encode("utf-8")).hexdigest()[:16]
    tax_year = to_plain_dict(result).get("tax_year", DEFAULT_RATES.tax_year)
    return f"pcc-{environment}-{tax_year}-{digest}"


def create_calculation_record(kind: str, result: Any, *, environment: str = "sandbox", source: str = "client") -> Dict[str, Any]:
    """Wrap a calculation result in a portable record with an id."""

    if kind not in {"employee", "self_employed", "compare", "rates"}:
        raise ContributionInputError("kind must be employee, self_employed, compare, or rates")
    payload = to_plain_dict(result)
    return {
        "id": build_calculation_id(kind, result, environment=environment),
        "environment": environment,
        "kind": kind,
        "source": source,
        "result": payload,
    }


class PensionContributionCalculatorClient:
    """Synchronous and asynchronous structured helper."""

    def __init__(self, rates: RateTable = DEFAULT_RATES) -> None:
        self.rates = rates

    def calculate_employee(self, gross_salary: float, *, pensionable_salary: Optional[float] = None, product: ProductType = "pension_fund", include_hishtalmut: bool = False, section14_full: bool = False) -> EmployeeContributionResult:
        return employee_contributions(gross_salary, pensionable_salary=pensionable_salary, product=product, include_hishtalmut=include_hishtalmut, section14_full=section14_full, rates=self.rates)

    async def acalculate_employee(self, gross_salary: float, *, pensionable_salary: Optional[float] = None, product: ProductType = "pension_fund", include_hishtalmut: bool = False, section14_full: bool = False) -> EmployeeContributionResult:
        return await asyncio.to_thread(self.calculate_employee, gross_salary, pensionable_salary=pensionable_salary, product=product, include_hishtalmut=include_hishtalmut, section14_full=section14_full)

    def calculate_self_employed(self, annual_net_taxable_income: float, *, age: int, first_year_business: bool = False, retirement_age: Optional[int] = None, annual_pension_deposit: Optional[float] = None, annual_hishtalmut_deposit: Optional[float] = None) -> SelfEmployedContributionResult:
        return self_employed_contributions(annual_net_taxable_income, age=age, first_year_business=first_year_business, retirement_age=retirement_age, annual_pension_deposit=annual_pension_deposit, annual_hishtalmut_deposit=annual_hishtalmut_deposit, rates=self.rates)

    async def acalculate_self_employed(self, annual_net_taxable_income: float, *, age: int, first_year_business: bool = False, retirement_age: Optional[int] = None, annual_pension_deposit: Optional[float] = None, annual_hishtalmut_deposit: Optional[float] = None) -> SelfEmployedContributionResult:
        return await asyncio.to_thread(self.calculate_self_employed, annual_net_taxable_income, age=age, first_year_business=first_year_business, retirement_age=retirement_age, annual_pension_deposit=annual_pension_deposit, annual_hishtalmut_deposit=annual_hishtalmut_deposit)

    def compare_products(self, gross_salary: float, *, pensionable_salary: Optional[float] = None, include_hishtalmut: bool = False, section14_full: bool = False) -> ProductComparisonResult:
        return compare_products(gross_salary, pensionable_salary=pensionable_salary, include_hishtalmut=include_hishtalmut, section14_full=section14_full, rates=self.rates)

    async def acompare_products(self, gross_salary: float, *, pensionable_salary: Optional[float] = None, include_hishtalmut: bool = False, section14_full: bool = False) -> ProductComparisonResult:
        return await asyncio.to_thread(self.compare_products, gross_salary, pensionable_salary=pensionable_salary, include_hishtalmut=include_hishtalmut, section14_full=section14_full)


    def create_record(self, kind: str, result: Any, *, environment: str = "sandbox", source: str = "client") -> Dict[str, Any]:
        """Create a portable record for a result produced by the helper."""

        return create_calculation_record(kind, result, environment=environment, source=source)

    async def acreate_record(self, kind: str, result: Any, *, environment: str = "sandbox", source: str = "client") -> Dict[str, Any]:
        """Create a portable record asynchronously."""

        return await asyncio.to_thread(self.create_record, kind, result, environment=environment, source=source)


def load_rates_from_json(path: str) -> RateTable:
    """Load a partial rate table from JSON and merge it with defaults."""

    data = json.loads(open(path, "r", encoding="utf-8").read())
    allowed = set(RateTable.__dataclass_fields__.keys())
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ContributionInputError(f"Unknown rate fields: {', '.join(unknown)}")
    merged = asdict(DEFAULT_RATES)
    merged.update(data)
    return RateTable(**merged)


def main() -> None:
    """Small direct-run helper for smoke testing."""

    client = PensionContributionCalculatorClient()
    print(to_json(client.calculate_employee(20_000, include_hishtalmut=True)))


if __name__ == "__main__":
    main()
