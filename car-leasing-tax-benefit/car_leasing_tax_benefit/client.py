"""Israeli Shovi Rechev company-car benefit calculator.

The package loads local tax-year rule tables, validates vehicle inputs, and
calculates monthly and annual imputed benefit values for Israeli company cars.
"""

from __future__ import annotations

import asyncio
import csv
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DATA_PATH = Path(__file__).resolve().parent / "data" / "tax_authority_tables.json"
ROOT_DATA_PATH = PACKAGE_ROOT / "data" / "tax_authority_tables.json"
DEFAULT_TABLE_PATH = PACKAGE_DATA_PATH if PACKAGE_DATA_PATH.exists() else ROOT_DATA_PATH
DEFAULT_STORE_PATH = Path(os.getenv("CAR_LEASING_TAX_BENEFIT_STORE", str(Path.cwd() / ".car_leasing_tax_benefit_requests.json")))


class CalculatorError(ValueError):
    """Base error for validation and calculation failures."""


class RuleTableError(CalculatorError):
    """Raised when a tax rule table is missing or inconsistent."""


class UnsupportedCategoryError(CalculatorError):
    """Raised when a selected vehicle category cannot use the selected formula."""


class InputValidationError(CalculatorError):
    """Raised when a request contains invalid business or vehicle data."""


def money(value: Decimal) -> Decimal:
    """Round a monetary amount to two decimal places."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def decimal_value(value: Any, field_name: str) -> Decimal:
    """Parse a value as Decimal with a field-specific error message."""
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise InputValidationError(f"{field_name} must be numeric") from exc
    if result.is_nan():
        raise InputValidationError(f"{field_name} must be numeric")
    return result


@dataclass(frozen=True)
class VehicleInput:
    """Input record for one vehicle calculation."""

    original_price_ils: Decimal
    category: str = "private_combustion"
    tax_year: int = 2026
    employee_marginal_tax_rate: Decimal = Decimal("0.35")
    months_available: int = 12
    private_use_ratio: Decimal = Decimal("1")
    license_plate: Optional[str] = None
    employee_name: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "VehicleInput":
        """Create a typed vehicle input from a mapping."""
        return cls(
            original_price_ils=decimal_value(payload.get("original_price_ils"), "original_price_ils"),
            category=str(payload.get("category", "private_combustion")),
            tax_year=int(payload.get("tax_year", 2026)),
            employee_marginal_tax_rate=decimal_value(
                payload.get("employee_marginal_tax_rate", "0.35"),
                "employee_marginal_tax_rate",
            ),
            months_available=int(payload.get("months_available", 12)),
            private_use_ratio=decimal_value(payload.get("private_use_ratio", "1"), "private_use_ratio"),
            license_plate=payload.get("license_plate") or None,
            employee_name=payload.get("employee_name") or None,
            notes=payload.get("notes") or None,
        )


@dataclass(frozen=True)
class CalculationTrace:
    """Traceable formula inputs and warnings."""

    formula: str
    base_linear_rate: Decimal
    gross_monthly_value_ils: Decimal
    price_ceiling_ils: Decimal
    capped_price_ils: Decimal
    category_reduction_ils: Decimal
    private_use_ratio: Decimal
    months_available: int
    rule_effective_from: str
    rule_effective_to: str
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class TaxResult:
    """Calculation result for one vehicle."""

    category: str
    category_he: str
    tax_year: int
    original_price_ils: Decimal
    monthly_imputed_value_ils: Decimal
    annual_imputed_value_ils: Decimal
    estimated_monthly_tax_cost_ils: Decimal
    estimated_annual_tax_cost_ils: Decimal
    employee_marginal_tax_rate: Decimal
    license_plate: Optional[str]
    employee_name: Optional[str]
    trace: CalculationTrace

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a JSON-serializable dictionary."""
        def convert(value: Any) -> Any:
            if isinstance(value, Decimal):
                return str(value)
            if isinstance(value, list):
                return [convert(item) for item in value]
            if isinstance(value, dict):
                return {key: convert(item) for key, item in value.items()}
            return value

        return convert(asdict(self))


class RequestStore:
    """Small JSON-file store for create-then-calculate CLI workflows."""

    def __init__(self, path: Path | str = DEFAULT_STORE_PATH) -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, Any]:
        """Load stored requests from disk."""
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise InputValidationError(f"Request store is not valid JSON: {self.path}") from exc
        if not isinstance(payload, dict):
            raise InputValidationError(f"Request store must contain a JSON object: {self.path}")
        return payload

    def save(self, payload: Dict[str, Any]) -> None:
        """Persist stored requests to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def create(self, vehicle: Mapping[str, Any], environment: str = "sandbox") -> Dict[str, Any]:
        """Create a request record and return its identifier."""
        if environment not in {"sandbox", "production"}:
            raise InputValidationError("environment must be sandbox or production")
        request_id = f"clr_{uuid.uuid4().hex[:12]}"
        data = self.load()
        data[request_id] = {"id": request_id, "environment": environment, "vehicle": dict(vehicle)}
        self.save(data)
        return data[request_id]

    def get(self, request_id: str) -> Mapping[str, Any]:
        """Return a stored request by identifier."""
        data = self.load()
        try:
            return data[request_id]
        except KeyError as exc:
            raise InputValidationError(f"request id not found: {request_id}") from exc


class CarLeasingTaxBenefitClient:
    """Synchronous and asynchronous helper for Shovi Rechev calculations."""

    def __init__(self, table_path: Path | str = DEFAULT_TABLE_PATH) -> None:
        self.table_path = Path(table_path)
        self.tables = self.load_tables(self.table_path)

    @staticmethod
    def load_tables(path: Path) -> Dict[str, Any]:
        """Load and validate the local rule-table JSON."""
        if not path.exists():
            raise RuleTableError(f"Rule table not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuleTableError(f"Rule table is not valid JSON: {path}") from exc
        if "annual_rules" not in data:
            raise RuleTableError("Rule table missing annual_rules")
        return data

    def available_years(self) -> List[int]:
        """Return tax years available in the loaded rule table."""
        return sorted(int(year) for year in self.tables["annual_rules"].keys())

    def categories(self, tax_year: int = 2026) -> Dict[str, Dict[str, Any]]:
        """Return category rules for a tax year."""
        year_rules = self.year_rules(tax_year)
        return dict(year_rules["categories"])

    def year_rules(self, tax_year: int) -> Mapping[str, Any]:
        """Return rule data for one tax year."""
        key = str(tax_year)
        try:
            return self.tables["annual_rules"][key]
        except KeyError as exc:
            years = ", ".join(str(year) for year in self.available_years())
            raise RuleTableError(f"No rules for tax_year={tax_year}. Available years: {years}") from exc

    def validate(self, vehicle: VehicleInput) -> List[str]:
        """Validate input and return non-fatal warnings."""
        warnings: List[str] = []
        validation = self.tables.get("validation", {})
        min_price = decimal_value(validation.get("min_price_ils", 1), "min_price_ils")
        max_price = decimal_value(validation.get("max_reasonable_price_ils", 2000000), "max_reasonable_price_ils")
        min_months = int(validation.get("min_months", 1))
        max_months = int(validation.get("max_months", 12))

        if vehicle.original_price_ils < min_price:
            raise InputValidationError("original_price_ils must be positive")
        if vehicle.original_price_ils > max_price:
            warnings.append("original_price_ils is unusually high; verify coordinated original price.")
        if not (Decimal("0") <= vehicle.employee_marginal_tax_rate <= Decimal("1")):
            raise InputValidationError("employee_marginal_tax_rate must be between 0 and 1")
        if not (Decimal("0") <= vehicle.private_use_ratio <= Decimal("1")):
            raise InputValidationError("private_use_ratio must be between 0 and 1")
        if not (min_months <= vehicle.months_available <= max_months):
            raise InputValidationError(f"months_available must be between {min_months} and {max_months}")

        year_rules = self.year_rules(vehicle.tax_year)
        categories = year_rules.get("categories", {})
        if vehicle.category not in categories:
            raise UnsupportedCategoryError(f"Unknown category '{vehicle.category}' for tax_year={vehicle.tax_year}")
        category_rule = categories[vehicle.category]
        if not category_rule.get("allowed", True):
            raise UnsupportedCategoryError(
                f"Category '{vehicle.category}' requires a dedicated rule and cannot use the private-car linear formula"
            )
        if vehicle.private_use_ratio != Decimal("1"):
            warnings.append("Partial private-use ratio is a planning assumption; confirm payroll treatment with a qualified adviser.")
        return warnings

    def calculate(self, vehicle: VehicleInput | Mapping[str, Any]) -> TaxResult:
        """Calculate Shovi Rechev for one vehicle."""
        request = vehicle if isinstance(vehicle, VehicleInput) else VehicleInput.from_mapping(vehicle)
        warnings = self.validate(request)
        year_rules = self.year_rules(request.tax_year)
        category_rule = year_rules["categories"][request.category]

        base_rate = decimal_value(
            year_rules.get("base_linear_rate", self.tables.get("default_private_vehicle_rate", "0.0248")),
            "base_linear_rate",
        )
        category_reduction = decimal_value(category_rule.get("monthly_reduction_ils", 0), "monthly_reduction_ils")
        price_ceiling = decimal_value(year_rules.get("price_ceiling_ils", request.original_price_ils), "price_ceiling_ils")
        capped_price = min(request.original_price_ils, price_ceiling)
        if request.original_price_ils > price_ceiling:
            warnings.append("original_price_ils exceeds the tax-year coordinated-price ceiling; calculation used the ceiling.")
        gross_monthly = money(capped_price * base_rate)
        monthly_after_reduction = gross_monthly - category_reduction
        if monthly_after_reduction < Decimal("0"):
            monthly_after_reduction = Decimal("0.00")
        adjusted_monthly = money(monthly_after_reduction * request.private_use_ratio)
        annual_value = money(adjusted_monthly * Decimal(request.months_available))
        monthly_tax_cost = money(adjusted_monthly * request.employee_marginal_tax_rate)
        annual_tax_cost = money(annual_value * request.employee_marginal_tax_rate)

        trace = CalculationTrace(
            formula="max(min(original_price_ils, price_ceiling_ils) * base_linear_rate - category_reduction_ils, 0) * private_use_ratio",
            base_linear_rate=base_rate,
            gross_monthly_value_ils=gross_monthly,
            price_ceiling_ils=price_ceiling,
            capped_price_ils=capped_price,
            category_reduction_ils=category_reduction,
            private_use_ratio=request.private_use_ratio,
            months_available=request.months_available,
            rule_effective_from=str(year_rules.get("effective_from", "")),
            rule_effective_to=str(year_rules.get("effective_to", "")),
            warnings=warnings,
        )
        return TaxResult(
            category=request.category,
            category_he=str(category_rule.get("he", request.category)),
            tax_year=request.tax_year,
            original_price_ils=money(request.original_price_ils),
            monthly_imputed_value_ils=adjusted_monthly,
            annual_imputed_value_ils=annual_value,
            estimated_monthly_tax_cost_ils=monthly_tax_cost,
            estimated_annual_tax_cost_ils=annual_tax_cost,
            employee_marginal_tax_rate=request.employee_marginal_tax_rate,
            license_plate=request.license_plate,
            employee_name=request.employee_name,
            trace=trace,
        )

    async def calculate_async(self, vehicle: VehicleInput | Mapping[str, Any]) -> TaxResult:
        """Asynchronously calculate Shovi Rechev for one vehicle."""
        await asyncio.sleep(0)
        return self.calculate(vehicle)

    def calculate_many(self, vehicles: Iterable[VehicleInput | Mapping[str, Any]]) -> List[TaxResult]:
        """Calculate Shovi Rechev for multiple vehicles."""
        return [self.calculate(vehicle) for vehicle in vehicles]

    async def calculate_many_async(self, vehicles: Iterable[VehicleInput | Mapping[str, Any]]) -> List[TaxResult]:
        """Asynchronously calculate multiple vehicles."""
        await asyncio.sleep(0)
        return self.calculate_many(vehicles)

    def calculate_request_id(self, request_id: str, store_path: Path | str = DEFAULT_STORE_PATH) -> TaxResult:
        """Calculate a stored request by identifier."""
        stored = RequestStore(store_path).get(request_id)
        vehicle = stored.get("vehicle", {})
        return self.calculate(vehicle)

    def export_csv(self, results: Sequence[TaxResult], output_path: Path | str) -> Path:
        """Export calculation results to a UTF-8-SIG CSV file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "employee_name",
            "license_plate",
            "tax_year",
            "category",
            "category_he",
            "original_price_ils",
            "monthly_imputed_value_ils",
            "annual_imputed_value_ils",
            "estimated_monthly_tax_cost_ils",
            "estimated_annual_tax_cost_ils",
            "employee_marginal_tax_rate",
        ]
        with path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                row = result.to_dict()
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        return path


__all__ = [
    "CalculationTrace",
    "CalculatorError",
    "CarLeasingTaxBenefitClient",
    "InputValidationError",
    "RequestStore",
    "RuleTableError",
    "TaxResult",
    "UnsupportedCategoryError",
    "VehicleInput",
    "decimal_value",
    "money",
]
