"""Israeli freelancer tax estimation primitives.

This module performs local planning estimates only. Verify current-year rates,
thresholds, portal data, and professional guidance before filing or payment.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping

MoneyLike = str | int | float | Decimal
TWOPLACES = Decimal("0.01")
ZERO = Decimal("0")
VALID_ENVIRONMENTS = {"sandbox", "production"}
CONFIG_ENV_KEYS = {
    "vat_rate": "FTC_VAT_RATE",
    "osek_patur_threshold_annual": "FTC_OSEK_PATUR_THRESHOLD_ANNUAL",
    "osek_patur_warning_ratio": "FTC_OSEK_PATUR_WARNING_RATIO",
    "national_insurance_reduced_rate": "FTC_NI_REDUCED_RATE",
    "national_insurance_regular_rate": "FTC_NI_REGULAR_RATE",
    "national_insurance_reduced_threshold_annual": "FTC_NI_REDUCED_THRESHOLD_ANNUAL",
    "national_insurance_annual_ceiling": "FTC_NI_ANNUAL_CEILING",
    "micro_business_normative_expense_rate": "FTC_MICRO_BUSINESS_EXPENSE_RATE",
    "currency": "FTC_CURRENCY",
}


class CalculatorError(ValueError):
    """Raised when calculator input or configuration is invalid."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class BusinessType(str, Enum):
    """Supported Israeli freelancer VAT statuses."""

    OSEK_PATUR = "osek-patur"
    OSEK_MURSHE = "osek-murshe"


class AdvanceBase(str, Enum):
    """Supported income-tax advance bases."""

    REVENUE = "revenue"
    PROFIT = "profit"


def to_decimal(value: MoneyLike, *, field_name: str = "value") -> Decimal:
    """Convert a value to Decimal and reject non-finite values."""

    if isinstance(value, Decimal):
        result = value
    else:
        try:
            result = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise CalculatorError("invalid_decimal", f"{field_name} must be a decimal value.") from exc
    if not result.is_finite():
        raise CalculatorError("invalid_decimal", f"{field_name} must be a finite decimal value.")
    return result


def q2(value: Decimal) -> Decimal:
    """Round money to two decimal places using half-up rounding."""

    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def decimal_to_json(value: Any) -> Any:
    """Convert Decimal-rich objects into JSON-friendly values."""

    if isinstance(value, Decimal):
        return f"{q2(value)}"
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: decimal_to_json(val) for key, val in asdict(value).items()}
    if isinstance(value, dict):
        return {key: decimal_to_json(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [decimal_to_json(item) for item in value]
    return value


@dataclass(frozen=True)
class TaxConfig:
    """Configurable planning defaults for Israeli freelancer estimates."""

    vat_rate: Decimal = Decimal("0.18")
    osek_patur_threshold_annual: Decimal = Decimal("122833")
    osek_patur_warning_ratio: Decimal = Decimal("0.90")
    national_insurance_reduced_rate: Decimal = Decimal("0.077")
    national_insurance_regular_rate: Decimal = Decimal("0.18")
    national_insurance_reduced_threshold_annual: Decimal = Decimal("92436")
    national_insurance_annual_ceiling: Decimal = Decimal("622920")
    micro_business_normative_expense_rate: Decimal = Decimal("0.30")
    currency: str = "ILS"

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "TaxConfig":
        kwargs: dict[str, Any] = {}
        known = {field_.name for field_ in fields(cls)}
        for key, value in data.items():
            if key not in known:
                continue
            kwargs[key] = str(value) if key == "currency" else to_decimal(value, field_name=key)
        config = cls(**kwargs)
        config.validate()
        return config

    def validate(self) -> None:
        for field_name in (
            "vat_rate",
            "osek_patur_warning_ratio",
            "national_insurance_reduced_rate",
            "national_insurance_regular_rate",
            "micro_business_normative_expense_rate",
        ):
            rate = getattr(self, field_name)
            if rate < ZERO or rate > Decimal("1"):
                raise CalculatorError("invalid_rate", f"{field_name} must be between 0 and 1.")
        for field_name in (
            "osek_patur_threshold_annual",
            "national_insurance_reduced_threshold_annual",
            "national_insurance_annual_ceiling",
        ):
            amount = getattr(self, field_name)
            if amount < ZERO:
                raise CalculatorError("negative_amount", f"{field_name} cannot be negative.")
        if self.national_insurance_annual_ceiling < self.national_insurance_reduced_threshold_annual:
            raise CalculatorError("invalid_threshold", "Annual National Insurance ceiling must be above the reduced threshold.")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly configuration dictionary."""

        return decimal_to_json(self)


@dataclass(frozen=True)
class FreelancerTaxInput:
    """Input payload for an annual freelancer estimate."""

    business_type: str
    annual_revenue_ils: MoneyLike
    deductible_expenses_ils: MoneyLike = Decimal("0")
    input_vat_ils: MoneyLike = Decimal("0")
    income_tax_advance_rate: MoneyLike = Decimal("0")
    income_tax_advance_base: str = "revenue"
    apply_micro_business_normative_expense: bool = False
    calculation_date: str = field(default_factory=lambda: date.today().isoformat())

    def normalized(self) -> "NormalizedTaxInput":
        try:
            business_type = BusinessType(self.business_type)
        except ValueError as exc:
            raise CalculatorError("invalid_business_type", "Business type must be osek-patur or osek-murshe.") from exc
        try:
            advance_base = AdvanceBase(self.income_tax_advance_base)
        except ValueError as exc:
            raise CalculatorError("invalid_advance_base", "Income-tax advance base must be revenue or profit.") from exc
        revenue = to_decimal(self.annual_revenue_ils, field_name="annual_revenue_ils")
        expenses = to_decimal(self.deductible_expenses_ils, field_name="deductible_expenses_ils")
        input_vat = to_decimal(self.input_vat_ils, field_name="input_vat_ils")
        advance_rate = to_decimal(self.income_tax_advance_rate, field_name="income_tax_advance_rate")
        for name, amount in {
            "annual_revenue_ils": revenue,
            "deductible_expenses_ils": expenses,
            "input_vat_ils": input_vat,
        }.items():
            if amount < ZERO:
                raise CalculatorError("negative_amount", f"{name} cannot be negative.")
        if advance_rate < ZERO or advance_rate > Decimal("1"):
            raise CalculatorError("invalid_rate", "income_tax_advance_rate must be between 0 and 1.")
        return NormalizedTaxInput(
            business_type=business_type,
            annual_revenue_ils=revenue,
            deductible_expenses_ils=expenses,
            input_vat_ils=input_vat,
            income_tax_advance_rate=advance_rate,
            income_tax_advance_base=advance_base,
            apply_micro_business_normative_expense=self.apply_micro_business_normative_expense,
            calculation_date=self.calculation_date,
        )


@dataclass(frozen=True)
class NormalizedTaxInput:
    business_type: BusinessType
    annual_revenue_ils: Decimal
    deductible_expenses_ils: Decimal
    input_vat_ils: Decimal
    income_tax_advance_rate: Decimal
    income_tax_advance_base: AdvanceBase
    apply_micro_business_normative_expense: bool
    calculation_date: str


@dataclass(frozen=True)
class VATResult:
    vat_rate: Decimal
    output_vat: Decimal
    input_vat_credit: Decimal
    vat_payable: Decimal
    vat_refund_position: Decimal
    threshold: Decimal
    threshold_utilization: Decimal


@dataclass(frozen=True)
class IncomeTaxAdvanceResult:
    advance_rate: Decimal
    advance_base: Decimal
    annual_advance: Decimal
    monthly_reserve: Decimal
    effective_expenses: Decimal
    expense_method: str
    base_method: str


@dataclass(frozen=True)
class NationalInsuranceResult:
    income_base: Decimal
    reduced_tier_base: Decimal
    regular_tier_base: Decimal
    capped_income_base: Decimal
    annual_contribution: Decimal
    monthly_reserve: Decimal
    reduced_rate: Decimal
    regular_rate: Decimal


@dataclass(frozen=True)
class TaxSummary:
    estimated_profit: Decimal
    total_annual_tax_reserve: Decimal
    recommended_monthly_reserve: Decimal


@dataclass(frozen=True)
class TaxReport:
    business_type: BusinessType
    currency: str
    calculation_date: str
    vat: VATResult
    income_tax_advances: IncomeTaxAdvanceResult
    national_insurance: NationalInsuranceResult
    summary: TaxSummary
    warnings: tuple[str, ...]
    assumptions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly report dictionary."""

        return decimal_to_json(self)

    def to_json(self, *, indent: int = 2) -> str:
        """Return the report as UTF-8 safe JSON text."""

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


@dataclass(frozen=True)
class ScenarioRecord:
    """Stored scenario metadata."""

    scenario_id: str
    input_path: str
    environment: str
    created_at: str
    payload: FreelancerTaxInput

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "input_path": self.input_path,
            "environment": self.environment,
            "created_at": self.created_at,
            "payload": input_to_json(self.payload),
        }


class FreelancerTaxCalculator:
    """Synchronous and asynchronous Israeli freelancer tax calculator."""

    def __init__(self, config: TaxConfig | None = None, *, environment: str = "sandbox") -> None:
        validate_environment(environment)
        self.config = config or TaxConfig()
        self.config.validate()
        self.environment = environment

    def calculate(self, payload: FreelancerTaxInput | Mapping[str, Any]) -> TaxReport:
        """Calculate a full annual estimate."""

        if isinstance(payload, Mapping):
            payload = FreelancerTaxInput(**payload)
        data = payload.normalized()
        warnings: list[str] = []
        assumptions = [
            "Revenue is entered excluding VAT.",
            "Expenses are entered excluding VAT when input VAT is provided separately.",
            "Income-tax advances use the selected base and the provided advance rate.",
            "National Insurance values are planning estimates; official BTL calculations may adjust the insured base for deductible National Insurance amounts and other status factors.",
            f"Environment is {self.environment}; no official portal connection is performed.",
        ]
        effective_expenses, expense_method = self._effective_expenses(data, warnings)
        estimated_profit = max(data.annual_revenue_ils - effective_expenses, ZERO)
        vat_result = self._calculate_vat(data, warnings)
        income_tax = self._calculate_income_tax_advances(data, estimated_profit, effective_expenses, expense_method, warnings)
        national_insurance = self._calculate_national_insurance(estimated_profit)
        total_reserve = q2(vat_result.vat_payable + income_tax.annual_advance + national_insurance.annual_contribution)
        monthly_reserve = q2(total_reserve / Decimal("12"))
        if data.income_tax_advance_rate == ZERO:
            warnings.append("Income-tax advance rate is zero; enter the official Tax Authority percentage when available.")
        warnings.append("Verify current VAT rate, osek patur ceiling, and National Insurance configuration before payment.")
        return TaxReport(
            business_type=data.business_type,
            currency=self.config.currency,
            calculation_date=data.calculation_date,
            vat=vat_result,
            income_tax_advances=income_tax,
            national_insurance=national_insurance,
            summary=TaxSummary(q2(estimated_profit), total_reserve, monthly_reserve),
            warnings=tuple(dict.fromkeys(warnings)),
            assumptions=tuple(assumptions),
        )

    async def calculate_async(self, payload: FreelancerTaxInput | Mapping[str, Any]) -> TaxReport:
        """Calculate one estimate asynchronously."""

        return await asyncio.to_thread(self.calculate, payload)

    def calculate_many(self, payloads: Iterable[FreelancerTaxInput | Mapping[str, Any]]) -> list[TaxReport]:
        """Calculate multiple scenarios synchronously."""

        return [self.calculate(payload) for payload in payloads]

    async def calculate_many_async(self, payloads: Iterable[FreelancerTaxInput | Mapping[str, Any]]) -> list[TaxReport]:
        """Calculate multiple scenarios concurrently."""

        tasks = [self.calculate_async(payload) for payload in payloads]
        return await asyncio.gather(*tasks)

    def assess_osek_patur_threshold(self, annual_revenue_ils: MoneyLike) -> dict[str, Any]:
        """Return threshold utilization and status for an osek patur scenario."""

        revenue = to_decimal(annual_revenue_ils, field_name="annual_revenue_ils")
        if revenue < ZERO:
            raise CalculatorError("negative_amount", "annual_revenue_ils cannot be negative.")
        threshold = self.config.osek_patur_threshold_annual
        utilization = ZERO if threshold == ZERO else revenue / threshold
        if revenue > threshold:
            status = "breached"
        elif utilization >= self.config.osek_patur_warning_ratio:
            status = "near-threshold"
        else:
            status = "ok"
        return {
            "annual_revenue_ils": f"{q2(revenue)}",
            "threshold": f"{q2(threshold)}",
            "threshold_utilization_percent": f"{q2(utilization * Decimal('100'))}",
            "status": status,
        }

    def gross_to_net_vat(self, gross_amount_ils: MoneyLike) -> dict[str, str]:
        """Split a VAT-inclusive osek murshe amount into net revenue and VAT."""

        gross = to_decimal(gross_amount_ils, field_name="gross_amount_ils")
        if gross < ZERO:
            raise CalculatorError("negative_amount", "gross_amount_ils cannot be negative.")
        divisor = Decimal("1") + self.config.vat_rate
        net = q2(gross / divisor)
        vat = q2(gross - net)
        return {"gross_amount_ils": f"{q2(gross)}", "net_revenue_ils": f"{net}", "vat_component_ils": f"{vat}"}

    def _effective_expenses(self, data: NormalizedTaxInput, warnings: list[str]) -> tuple[Decimal, str]:
        if data.apply_micro_business_normative_expense:
            if data.annual_revenue_ils > self.config.osek_patur_threshold_annual:
                raise CalculatorError("micro_business_ineligible", "Micro-business scenario cannot be applied above the configured osek patur ceiling.")
            warnings.append("Micro-business scenario applied for planning only; verify eligibility and reporting route before filing.")
            return q2(data.annual_revenue_ils * self.config.micro_business_normative_expense_rate), "micro_business_normative"
        return data.deductible_expenses_ils, "actual_expenses"

    def _calculate_vat(self, data: NormalizedTaxInput, warnings: list[str]) -> VATResult:
        threshold = self.config.osek_patur_threshold_annual
        threshold_utilization = ZERO if threshold == ZERO else data.annual_revenue_ils / threshold
        if data.business_type == BusinessType.OSEK_PATUR:
            if data.input_vat_ils > ZERO:
                warnings.append("Input VAT is ignored for osek patur; VAT paid may be part of the expense instead.")
            if data.annual_revenue_ils > threshold:
                warnings.append("Revenue exceeds the configured osek patur ceiling; review VAT registration immediately.")
            elif threshold_utilization >= self.config.osek_patur_warning_ratio:
                warnings.append("Revenue is near the configured osek patur ceiling; monitor monthly.")
            return VATResult(self.config.vat_rate, q2(ZERO), q2(ZERO), q2(ZERO), q2(ZERO), q2(threshold), q2(threshold_utilization * Decimal("100")))
        output_vat = q2(data.annual_revenue_ils * self.config.vat_rate)
        input_vat_credit = q2(data.input_vat_ils)
        net_vat = output_vat - input_vat_credit
        vat_payable = q2(max(net_vat, ZERO))
        refund = q2(max(-net_vat, ZERO))
        if refund > ZERO:
            warnings.append("Input VAT exceeds output VAT; confirm refund position with records and official filing rules.")
        if data.annual_revenue_ils > ZERO and data.input_vat_ils > data.annual_revenue_ils:
            warnings.append("Input VAT is unusually high relative to revenue; verify that only VAT components were entered.")
        return VATResult(self.config.vat_rate, output_vat, input_vat_credit, vat_payable, refund, q2(threshold), q2(threshold_utilization * Decimal("100")))

    def _calculate_income_tax_advances(
        self,
        data: NormalizedTaxInput,
        estimated_profit: Decimal,
        effective_expenses: Decimal,
        expense_method: str,
        warnings: list[str],
    ) -> IncomeTaxAdvanceResult:
        advance_base = data.annual_revenue_ils if data.income_tax_advance_base == AdvanceBase.REVENUE else max(estimated_profit, ZERO)
        annual_advance = q2(q2(advance_base) * data.income_tax_advance_rate)
        if data.deductible_expenses_ils > data.annual_revenue_ils and not data.apply_micro_business_normative_expense:
            warnings.append("Expenses exceed revenue; profit-based estimates are set to zero where relevant.")
        return IncomeTaxAdvanceResult(
            advance_rate=data.income_tax_advance_rate,
            advance_base=q2(max(advance_base, ZERO)),
            annual_advance=annual_advance,
            monthly_reserve=q2(annual_advance / Decimal("12")),
            effective_expenses=q2(effective_expenses),
            expense_method=expense_method,
            base_method=data.income_tax_advance_base.value,
        )

    def _calculate_national_insurance(self, estimated_profit: Decimal) -> NationalInsuranceResult:
        capped = min(max(estimated_profit, ZERO), self.config.national_insurance_annual_ceiling)
        reduced_base = min(capped, self.config.national_insurance_reduced_threshold_annual)
        regular_base = max(capped - reduced_base, ZERO)
        annual = q2(reduced_base * self.config.national_insurance_reduced_rate + regular_base * self.config.national_insurance_regular_rate)
        return NationalInsuranceResult(q2(estimated_profit), q2(reduced_base), q2(regular_base), q2(capped), annual, q2(annual / Decimal("12")), self.config.national_insurance_reduced_rate, self.config.national_insurance_regular_rate)


def validate_environment(environment: str) -> str:
    """Validate the sandbox or production environment label."""

    if environment not in VALID_ENVIRONMENTS:
        raise CalculatorError("invalid_environment", "Environment must be sandbox or production.")
    return environment


def input_to_json(payload: FreelancerTaxInput | Mapping[str, Any]) -> dict[str, Any]:
    """Return a normalized JSON-friendly input payload."""

    if isinstance(payload, Mapping):
        payload = FreelancerTaxInput(**payload)
    data = payload.normalized()
    return {
        "business_type": data.business_type.value,
        "annual_revenue_ils": f"{q2(data.annual_revenue_ils)}",
        "deductible_expenses_ils": f"{q2(data.deductible_expenses_ils)}",
        "input_vat_ils": f"{q2(data.input_vat_ils)}",
        "income_tax_advance_rate": f"{q2(data.income_tax_advance_rate)}",
        "income_tax_advance_base": data.income_tax_advance_base.value,
        "apply_micro_business_normative_expense": data.apply_micro_business_normative_expense,
        "calculation_date": data.calculation_date,
    }


def load_config(path: str | Path) -> TaxConfig:
    """Load calculator configuration from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return TaxConfig.from_mapping(data)


def load_environment_config(environment: str = "sandbox", environ: Mapping[str, str] | None = None) -> TaxConfig:
    """Load configuration overrides from environment variables."""

    validate_environment(environment)
    source = os.environ if environ is None else environ
    data = {field_name: source[env_key] for field_name, env_key in CONFIG_ENV_KEYS.items() if env_key in source and source[env_key] != ""}
    return TaxConfig.from_mapping(data)


def load_inputs(path: str | Path) -> FreelancerTaxInput:
    """Load one input payload from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return FreelancerTaxInput(**data)


def save_inputs(payload: FreelancerTaxInput | Mapping[str, Any], path: str | Path) -> Path:
    """Save an input payload as UTF-8 JSON."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(input_to_json(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def save_report(report: TaxReport, path: str | Path) -> Path:
    """Save a report as UTF-8 JSON."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report.to_json() + "\n", encoding="utf-8")
    return output


def example_config() -> dict[str, str]:
    """Return a JSON-friendly default configuration."""

    return TaxConfig().to_dict()


def format_ils(value: MoneyLike) -> str:
    """Format a value as Israeli shekel text."""

    return f"₪{q2(to_decimal(value)):,.2f}"


def format_date_il(value: str | date) -> str:
    """Format ISO dates as DD/MM/YYYY."""

    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed.strftime("%d/%m/%Y")


def human_summary(report: TaxReport) -> str:
    """Render a concise human-readable summary."""

    lines = [
        f"Business type: {report.business_type.value}",
        f"Calculation date: {format_date_il(report.calculation_date)}",
        f"VAT payable: {format_ils(report.vat.vat_payable)}",
        f"Income-tax advances: {format_ils(report.income_tax_advances.annual_advance)}",
        f"National Insurance and health estimate: {format_ils(report.national_insurance.annual_contribution)}",
        f"Estimated annual profit: {format_ils(report.summary.estimated_profit)}",
        f"Recommended monthly reserve: {format_ils(report.summary.recommended_monthly_reserve)}",
    ]
    if report.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in report.warnings)
    return "\n".join(lines)


def default_store_dir() -> Path:
    """Return the default scenario store directory."""

    return Path(os.environ.get("FTC_STORE_DIR", ".freelancer-tax-calculator/scenarios"))


def make_scenario_id(payload: FreelancerTaxInput | Mapping[str, Any], *, created_at: str | None = None) -> str:
    """Create a stable short ID from payload content and creation time."""

    stamp = created_at or datetime.now(timezone.utc).isoformat()
    raw = json.dumps(input_to_json(payload), ensure_ascii=False, sort_keys=True) + stamp
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def create_scenario(
    payload: FreelancerTaxInput | Mapping[str, Any],
    *,
    store_dir: str | Path | None = None,
    environment: str = "sandbox",
) -> ScenarioRecord:
    """Persist an input scenario and return a record with its ID."""

    validate_environment(environment)
    if isinstance(payload, Mapping):
        payload = FreelancerTaxInput(**payload)
    created_at = datetime.now(timezone.utc).isoformat()
    scenario_id = make_scenario_id(payload, created_at=created_at)
    directory = Path(store_dir) if store_dir else default_store_dir()
    path = directory / f"{scenario_id}.json"
    save_inputs(payload, path)
    return ScenarioRecord(scenario_id, str(path), environment, created_at, payload)


def load_scenario(scenario_id: str, *, store_dir: str | Path | None = None) -> FreelancerTaxInput:
    """Load a saved scenario by ID."""

    if not scenario_id or any(char in scenario_id for char in "/\\"):
        raise CalculatorError("invalid_scenario_id", "Scenario ID is invalid.")
    directory = Path(store_dir) if store_dir else default_store_dir()
    path = directory / f"{scenario_id}.json"
    if not path.exists():
        raise CalculatorError("scenario_not_found", f"Scenario {scenario_id} was not found.")
    return load_inputs(path)


def report_to_json(report: TaxReport, *, indent: int = 2) -> str:
    """Return report JSON with stable Unicode behavior."""

    return json.dumps(report.to_dict(), ensure_ascii=False, indent=indent)


def gross_to_net_vat(gross_amount_ils: MoneyLike, *, config: TaxConfig | None = None) -> dict[str, str]:
    """Split a VAT-inclusive amount without instantiating the calculator explicitly."""

    return FreelancerTaxCalculator(config).gross_to_net_vat(gross_amount_ils)


__all__ = [
    "AdvanceBase", "BusinessType", "CalculatorError", "FreelancerTaxCalculator",
    "FreelancerTaxInput", "IncomeTaxAdvanceResult", "NationalInsuranceResult",
    "ScenarioRecord", "TaxConfig", "TaxReport", "TaxSummary", "VATResult",
    "create_scenario", "decimal_to_json", "default_store_dir", "example_config",
    "format_date_il", "format_ils", "gross_to_net_vat", "human_summary",
    "input_to_json", "load_config", "load_environment_config", "load_inputs",
    "load_scenario", "make_scenario_id", "q2", "report_to_json", "save_inputs",
    "save_report", "to_decimal", "validate_environment",
]
