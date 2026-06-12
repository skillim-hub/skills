"""Estimate Israeli Mas Shevach for real-estate sale planning.

This module is deterministic and network-free. It validates inputs, calculates
gain, CPI indexation, simple linear allocation, warnings, assumptions, and
local case storage for CLI workflows.
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class PropertyType(str, Enum):
    RESIDENTIAL_APARTMENT = "residential_apartment"
    LAND = "land"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    OTHER = "other"


class SellerResidency(str, Enum):
    ISRAEL_RESIDENT = "israel_resident"
    FOREIGN_RESIDENT = "foreign_resident"
    UNKNOWN = "unknown"


class SellerType(str, Enum):
    INDIVIDUAL = "individual"
    COMPANY = "company"
    PARTNERSHIP = "partnership"
    TRUST = "trust"
    ESTATE = "estate"
    UNKNOWN = "unknown"


SUPPORTED_EXEMPTIONS = {
    None,
    "",
    "single_apartment",
    "inherited_apartment",
    "gift_continuity",
    "replacement_apartment",
    "none",
}


@dataclass(frozen=True)
class TaxInputs:
    purchase_date: date
    sale_date: date
    purchase_price: float
    sale_price: float
    purchase_costs: float = 0.0
    sale_costs: float = 0.0
    improvements: float = 0.0
    depreciation_claimed: float = 0.0
    ownership_share: float = 1.0
    property_type: PropertyType = PropertyType.RESIDENTIAL_APARTMENT
    is_qualifying_residential_apartment: bool = False
    seller_residency: SellerResidency = SellerResidency.UNKNOWN
    seller_type: SellerType = SellerType.INDIVIDUAL
    cpi_purchase: Optional[float] = None
    cpi_sale: Optional[float] = None
    linear_relief_start_date: date = date(2014, 1, 1)
    tax_rate: float = 0.25
    exemption_code: Optional[str] = None
    notes: str = ""

    @staticmethod
    def parse_date(value: Any) -> date:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if not isinstance(value, str):
            raise ValueError("Date must be a date object or string")
        value = value.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Invalid date: {value}. Use YYYY-MM-DD or DD/MM/YYYY.")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaxInputs":
        payload = dict(data)
        payload["purchase_date"] = cls.parse_date(payload["purchase_date"])
        payload["sale_date"] = cls.parse_date(payload["sale_date"])
        if "linear_relief_start_date" in payload and payload["linear_relief_start_date"]:
            payload["linear_relief_start_date"] = cls.parse_date(payload["linear_relief_start_date"])
        if "property_type" in payload and not isinstance(payload["property_type"], PropertyType):
            payload["property_type"] = PropertyType(payload["property_type"])
        if "seller_residency" in payload and not isinstance(payload["seller_residency"], SellerResidency):
            payload["seller_residency"] = SellerResidency(payload["seller_residency"])
        if "seller_type" in payload and not isinstance(payload["seller_type"], SellerType):
            payload["seller_type"] = SellerType(payload["seller_type"])
        return cls(**payload)

    def to_json_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        for key in ("purchase_date", "sale_date", "linear_relief_start_date"):
            if isinstance(payload.get(key), date):
                payload[key] = payload[key].isoformat()
        for key in ("property_type", "seller_residency", "seller_type"):
            value = payload.get(key)
            if isinstance(value, Enum):
                payload[key] = value.value
        return payload


@dataclass(frozen=True)
class TaxEstimate:
    adjusted_basis: float
    net_sale_proceeds: float
    gross_gain: float
    seller_gross_gain: float
    indexed_basis: Optional[float]
    inflationary_gain: float
    real_gain: float
    seller_real_gain: float
    total_holding_days: int
    linear_taxable_days: int
    linear_taxable_share: float
    taxable_real_gain: float
    estimated_tax: float
    warnings: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def rounded(self, places: int = 2) -> Dict[str, Any]:
        result = self.to_dict()
        for key, value in list(result.items()):
            if isinstance(value, float):
                result[key] = round(value, places)
        return result


@dataclass(frozen=True)
class CaseRecord:
    case_id: str
    environment: str
    inputs: TaxInputs
    created_at: str
    storage_path: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "environment": self.environment,
            "inputs": self.inputs.to_json_dict(),
            "created_at": self.created_at,
            "storage_path": self.storage_path,
        }


def default_case_dir(environment: str = "sandbox") -> Path:
    env_dir = os.getenv("MAS_SHEVACH_CASE_DIR")
    if env_dir:
        return Path(env_dir).expanduser()
    return Path.home() / ".mas_shevach_cases" / environment


def now_utc_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _validate_environment(environment: str) -> str:
    normalized = environment.strip().lower()
    if normalized not in {"sandbox", "production"}:
        raise ValueError("Environment must be 'sandbox' or 'production'")
    return normalized


def _validate(inputs: TaxInputs) -> None:
    if inputs.sale_date <= inputs.purchase_date:
        raise ValueError("Sale date must be after purchase date")
    money_fields = {
        "purchase_price": inputs.purchase_price,
        "sale_price": inputs.sale_price,
        "purchase_costs": inputs.purchase_costs,
        "sale_costs": inputs.sale_costs,
        "improvements": inputs.improvements,
        "depreciation_claimed": inputs.depreciation_claimed,
    }
    for name, value in money_fields.items():
        if value < 0:
            raise ValueError(f"{name} must be non-negative")
    if not (0 < inputs.ownership_share <= 1):
        raise ValueError("Ownership share must be > 0 and <= 1")
    if inputs.tax_rate < 0 or inputs.tax_rate > 1:
        raise ValueError("Tax rate must be between 0 and 1")
    if (inputs.cpi_purchase is None) ^ (inputs.cpi_sale is None):
        raise ValueError("Both CPI values must be supplied together")
    if inputs.cpi_purchase is not None and (inputs.cpi_purchase <= 0 or inputs.cpi_sale <= 0):
        raise ValueError("CPI values must be positive")
    if inputs.exemption_code not in SUPPORTED_EXEMPTIONS:
        raise ValueError(f"Unsupported exemption code: {inputs.exemption_code}")


def linear_allocation(inputs: TaxInputs) -> tuple[int, int, float]:
    total_days = (inputs.sale_date - inputs.purchase_date).days
    taxable_start = max(inputs.purchase_date, inputs.linear_relief_start_date)
    if inputs.sale_date <= inputs.linear_relief_start_date:
        taxable_days = 0
    else:
        taxable_days = max(0, (inputs.sale_date - taxable_start).days)
    taxable_days = min(taxable_days, total_days)
    share = taxable_days / total_days if total_days else 0.0
    return total_days, taxable_days, share


def build_warnings(inputs: TaxInputs, gross_gain: float, real_gain: float) -> List[str]:
    warnings: List[str] = []
    if inputs.cpi_purchase is None:
        warnings.append("CPI indexation not applied; verify official Central Bureau of Statistics CPI values.")
    elif inputs.cpi_sale < inputs.cpi_purchase:
        warnings.append("CPI at sale is lower than CPI at purchase; verify that both CPI values use the same base.")
    if gross_gain < 0 or real_gain < 0:
        warnings.append("Calculation indicates a loss; tax may be zero but reporting and loss treatment require review.")
    if inputs.property_type in {PropertyType.COMMERCIAL, PropertyType.MIXED_USE}:
        warnings.append("Business, rental, VAT, and depreciation issues require professional review.")
    if inputs.property_type == PropertyType.LAND:
        warnings.append("Land is not eligible for residential-apartment exemptions in this simplified model.")
    if inputs.seller_residency == SellerResidency.FOREIGN_RESIDENT:
        warnings.append("Foreign-resident seller: verify exemption eligibility, documentation, and withholding.")
    if inputs.seller_type != SellerType.INDIVIDUAL:
        warnings.append("Non-individual seller: verify company, partnership, trust, estate, VAT, and accounting rules.")
    if inputs.exemption_code in {"single_apartment", "inherited_apartment", "gift_continuity", "replacement_apartment"}:
        warnings.append(f"Exemption '{inputs.exemption_code}' is flagged for review and is not automatically applied.")
    lowered_notes = inputs.notes.lower()
    if "tama" in lowered_notes or "urban renewal" in lowered_notes or "פינוי" in inputs.notes:
        warnings.append("Urban renewal or combination transaction detected; advanced review required.")
    if inputs.property_type == PropertyType.COMMERCIAL and inputs.depreciation_claimed == 0:
        warnings.append("Commercial asset has no depreciation entered; confirm depreciation claimed or claimable.")
    if inputs.seller_type == SellerType.INDIVIDUAL and inputs.tax_rate == 0.25:
        warnings.append("Default 25% rate excludes high-income surtax and additional capital-income tax where applicable.")
    return warnings


def build_assumptions(inputs: TaxInputs, linear_share: float) -> List[str]:
    assumptions = [
        f"Tax rate assumed at {inputs.tax_rate:.2%}.",
        f"Linear relief start date assumed as {inputs.linear_relief_start_date.isoformat()}.",
        f"Ownership share applied as {inputs.ownership_share:.6g}.",
    ]
    if inputs.is_qualifying_residential_apartment:
        assumptions.append("Property treated as a qualifying residential apartment for linear allocation only.")
    else:
        assumptions.append("No qualifying residential-apartment status assumed.")
    if linear_share == 0:
        assumptions.append("Linear taxable share is 0 under the configured relief-date model.")
    elif linear_share == 1:
        assumptions.append("Linear taxable share is 100% under the configured relief-date model.")
    return assumptions


def estimate_tax(inputs: TaxInputs) -> TaxEstimate:
    _validate(inputs)

    adjusted_basis = (
        inputs.purchase_price
        + inputs.purchase_costs
        + inputs.improvements
        - inputs.depreciation_claimed
    )
    net_sale_proceeds = inputs.sale_price - inputs.sale_costs
    gross_gain = net_sale_proceeds - adjusted_basis
    seller_gross_gain = gross_gain * inputs.ownership_share

    indexed_basis: Optional[float] = None
    inflationary_gain = 0.0
    real_gain = gross_gain

    if inputs.cpi_purchase is not None and inputs.cpi_sale is not None:
        indexed_basis = adjusted_basis * (inputs.cpi_sale / inputs.cpi_purchase)
        inflationary_gain = max(0.0, indexed_basis - adjusted_basis)
        real_gain = net_sale_proceeds - indexed_basis

    real_gain = max(0.0, real_gain)
    seller_real_gain = real_gain * inputs.ownership_share

    total_days, taxable_days, linear_share = linear_allocation(inputs)

    if inputs.property_type == PropertyType.RESIDENTIAL_APARTMENT and inputs.is_qualifying_residential_apartment:
        taxable_real_gain = seller_real_gain * linear_share
    else:
        taxable_real_gain = seller_real_gain

    taxable_real_gain = max(0.0, taxable_real_gain)
    estimated_tax = taxable_real_gain * inputs.tax_rate

    return TaxEstimate(
        adjusted_basis=adjusted_basis,
        net_sale_proceeds=net_sale_proceeds,
        gross_gain=gross_gain,
        seller_gross_gain=seller_gross_gain,
        indexed_basis=indexed_basis,
        inflationary_gain=inflationary_gain,
        real_gain=real_gain,
        seller_real_gain=seller_real_gain,
        total_holding_days=total_days,
        linear_taxable_days=taxable_days,
        linear_taxable_share=linear_share,
        taxable_real_gain=taxable_real_gain,
        estimated_tax=estimated_tax,
        warnings=build_warnings(inputs, gross_gain, real_gain),
        assumptions=build_assumptions(inputs, linear_share),
    )


async def estimate_tax_async(inputs: TaxInputs) -> TaxEstimate:
    await asyncio.sleep(0)
    return estimate_tax(inputs)


def estimate_from_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    inputs = TaxInputs.from_dict(data)
    return estimate_tax(inputs).to_dict()


def create_case(
    inputs: TaxInputs,
    environment: str = "sandbox",
    case_dir: Optional[Path] = None,
) -> CaseRecord:
    _validate(inputs)
    normalized_env = _validate_environment(environment)
    storage_dir = Path(case_dir) if case_dir is not None else default_case_dir(normalized_env)
    storage_dir.mkdir(parents=True, exist_ok=True)
    case_id = uuid.uuid4().hex[:12]
    path = storage_dir / f"{case_id}.json"
    record = CaseRecord(
        case_id=case_id,
        environment=normalized_env,
        inputs=inputs,
        created_at=now_utc_iso(),
        storage_path=str(path),
    )
    path.write_text(json.dumps(record.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def load_case(case_id: str, environment: str = "sandbox", case_dir: Optional[Path] = None) -> CaseRecord:
    normalized_env = _validate_environment(environment)
    storage_dir = Path(case_dir) if case_dir is not None else default_case_dir(normalized_env)
    path = storage_dir / f"{case_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Case not found: {case_id}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    inputs = TaxInputs.from_dict(payload["inputs"])
    return CaseRecord(
        case_id=payload["case_id"],
        environment=payload.get("environment", normalized_env),
        inputs=inputs,
        created_at=payload.get("created_at", ""),
        storage_path=str(path),
    )


def estimate_case(case_id: str, environment: str = "sandbox", case_dir: Optional[Path] = None) -> TaxEstimate:
    record = load_case(case_id=case_id, environment=environment, case_dir=case_dir)
    return estimate_tax(record.inputs)


def format_nis(value: float) -> str:
    return f"₪{value:,.2f}"


def summarize(estimate: TaxEstimate) -> str:
    lines = [
        f"Estimated Mas Shevach: {format_nis(estimate.estimated_tax)}",
        f"Taxable real gain: {format_nis(estimate.taxable_real_gain)}",
        f"Real gain: {format_nis(estimate.real_gain)}",
        f"Gross gain: {format_nis(estimate.gross_gain)}",
        f"Linear taxable share: {estimate.linear_taxable_share:.2%}",
    ]
    if estimate.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in estimate.warnings)
    if estimate.assumptions:
        lines.append("Assumptions:")
        lines.extend(f"- {assumption}" for assumption in estimate.assumptions)
    return "\n".join(lines)


__all__ = [
    "PropertyType",
    "SellerResidency",
    "SellerType",
    "TaxInputs",
    "TaxEstimate",
    "CaseRecord",
    "default_case_dir",
    "linear_allocation",
    "build_warnings",
    "build_assumptions",
    "estimate_tax",
    "estimate_tax_async",
    "estimate_from_dict",
    "create_case",
    "load_case",
    "estimate_case",
    "format_nis",
    "summarize",
]
