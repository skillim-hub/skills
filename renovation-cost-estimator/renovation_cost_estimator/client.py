"""Israeli renovation cost estimator.

The module provides a typed local estimator for planning budgets, contractor
quote review, and small-business fit-out checks. It does not call external
services. Verify VAT, official indices, permits, and licensing before relying
on an estimate for a binding decision.
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple


class EstimatorError(ValueError):
    """Raised when estimator input is invalid."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class FinishLevel(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    LUXURY = "luxury"


class ScopeLevel(str, Enum):
    COSMETIC = "cosmetic"
    PARTIAL = "partial"
    FULL = "full"
    SHELL = "shell"
    OFFICE_FITOUT = "office_fitout"
    RETAIL_FITOUT = "retail_fitout"
    COMMERCIAL_FITOUT = "commercial_fitout"


@dataclass(frozen=True)
class Range:
    low: float
    expected: float
    high: float

    def __post_init__(self) -> None:
        if self.low < 0 or self.expected < 0 or self.high < 0:
            raise EstimatorError("NEGATIVE_RANGE", "range values must be non-negative")
        if not self.low <= self.expected <= self.high:
            raise EstimatorError("INVALID_RANGE", "range values must be ordered low <= expected <= high")

    def scale(self, factor: float) -> "Range":
        return Range(self.low * factor, self.expected * factor, self.high * factor)

    def add(self, other: "Range") -> "Range":
        return Range(self.low + other.low, self.expected + other.expected, self.high + other.high)

    def to_dict(self) -> Dict[str, int]:
        return {"low": round_to_100(self.low), "expected": round_to_100(self.expected), "high": round_to_100(self.high)}


@dataclass(frozen=True)
class LineItem:
    category: str
    quantity: float
    description: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "LineItem":
        return cls(
            category=str(data.get("category", "")).strip(),
            quantity=float(data.get("quantity", 0)),
            description=str(data.get("description", "")).strip(),
        )


@dataclass
class ProjectInput:
    project_name: str = "Renovation project"
    city: str = ""
    property_type: str = "apartment"
    area_sqm: float = 0.0
    scope_level: str = "partial"
    finish_level: str = "standard"
    rooms: int = 0
    bathrooms: int = 0
    kitchens: int = 0
    wet_rooms: int = 0
    building_year: Optional[int] = None
    floor: Optional[int] = None
    has_elevator: Optional[bool] = None
    occupied: bool = False
    include_vat: bool = True
    vat_rate: float = 0.18
    requires_business_license: bool = False
    commercial_public_access: bool = False
    signage: bool = False
    food_business: bool = False
    structural_changes: bool = False
    contractor_quote_total: Optional[float] = None
    contractor_quote_includes_vat: Optional[bool] = None
    language: str = "en"
    line_items: List[LineItem] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ProjectInput":
        return cls(
            project_name=str(data.get("project_name", "Renovation project")),
            city=str(data.get("city", "")),
            property_type=str(data.get("property_type", "apartment")),
            area_sqm=float(data.get("area_sqm", 0)),
            scope_level=str(data.get("scope_level", "partial")),
            finish_level=str(data.get("finish_level", "standard")),
            rooms=int(data.get("rooms", 0) or 0),
            bathrooms=int(data.get("bathrooms", 0) or 0),
            kitchens=int(data.get("kitchens", 0) or 0),
            wet_rooms=int(data.get("wet_rooms", 0) or 0),
            building_year=data.get("building_year"),
            floor=data.get("floor"),
            has_elevator=data.get("has_elevator"),
            occupied=bool(data.get("occupied", False)),
            include_vat=bool(data.get("include_vat", True)),
            vat_rate=float(data.get("vat_rate", 0.18)),
            requires_business_license=bool(data.get("requires_business_license", False)),
            commercial_public_access=bool(data.get("commercial_public_access", False)),
            signage=bool(data.get("signage", False)),
            food_business=bool(data.get("food_business", False)),
            structural_changes=bool(data.get("structural_changes", False)),
            contractor_quote_total=data.get("contractor_quote_total"),
            contractor_quote_includes_vat=data.get("contractor_quote_includes_vat"),
            language=str(data.get("language", "en")),
            line_items=[LineItem.from_mapping(item) for item in (data.get("line_items") or [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["line_items"] = [asdict(item) for item in self.line_items]
        return data


@dataclass(frozen=True)
class Risk:
    level: str
    topic: str
    action: str


@dataclass(frozen=True)
class ProjectRecord:
    id: str
    environment: str
    project: ProjectInput
    path: str


@dataclass
class EstimateResult:
    project_name: str
    currency: str
    estimate_date: str
    confidence: str
    totals: Dict[str, int]
    direct_range: Dict[str, int]
    assumptions: List[str]
    risks: List[Risk]
    line_breakdown: List[Dict[str, Any]]
    quote_review: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["risks"] = [asdict(risk) for risk in self.risks]
        return data

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)

    def to_text(self, language: str = "en") -> str:
        if language.lower().startswith("he"):
            lines = [
                f"אומדן: {self.project_name}",
                f"תאריך: {self.estimate_date}",
                f"רמת ודאות: {self.confidence}",
                f"סה״כ צפוי: {format_ils(self.totals['total_expected'])}",
                "הנחות:",
            ]
            lines.extend(f"- {item}" for item in self.assumptions)
            lines.append("סיכונים ופעולות:")
            lines.extend(f"- {risk.level}: {risk.topic} — {risk.action}" for risk in self.risks)
            return "\n".join(lines)

        lines = [
            f"Estimate: {self.project_name}",
            f"Date: {self.estimate_date}",
            f"Confidence: {self.confidence}",
            f"Expected total: {format_ils(self.totals['total_expected'])}",
            "Assumptions:",
        ]
        lines.extend(f"- {item}" for item in self.assumptions)
        lines.append("Risks and actions:")
        lines.extend(f"- {risk.level}: {risk.topic} — {risk.action}" for risk in self.risks)
        return "\n".join(lines)


def round_to_100(value: float) -> int:
    return int(round(value / 100.0) * 100)


def format_ils(value: float) -> str:
    return f"₪{int(round(value)):,}"


BASE_BENCHMARKS: Dict[str, Dict[str, Range]] = {
    "cosmetic": {
        "basic": Range(650, 875, 1100),
        "standard": Range(1000, 1350, 1700),
        "premium": Range(1600, 2100, 2600),
        "luxury": Range(2500, 3250, 4200),
    },
    "partial": {
        "basic": Range(1500, 2100, 2700),
        "standard": Range(2500, 3400, 4300),
        "premium": Range(4000, 5250, 6500),
        "luxury": Range(6500, 8500, 11000),
    },
    "full": {
        "basic": Range(3000, 4000, 5000),
        "standard": Range(4500, 6000, 7500),
        "premium": Range(7000, 9000, 11000),
        "luxury": Range(11000, 14000, 18000),
    },
    "shell": {
        "basic": Range(4500, 5750, 7000),
        "standard": Range(6500, 8250, 10000),
        "premium": Range(9000, 11500, 14000),
        "luxury": Range(14000, 18000, 24000),
    },
    "office_fitout": {
        "basic": Range(2000, 2900, 3800),
        "standard": Range(3500, 4750, 6000),
        "premium": Range(5500, 7250, 9000),
        "luxury": Range(9000, 12000, 16000),
    },
    "retail_fitout": {
        "basic": Range(2800, 3900, 5000),
        "standard": Range(4500, 6250, 8000),
        "premium": Range(7500, 9750, 12000),
        "luxury": Range(12000, 16000, 22000),
    },
    "commercial_fitout": {
        "basic": Range(3500, 5000, 6500),
        "standard": Range(6000, 8000, 10000),
        "premium": Range(9000, 11500, 14000),
        "luxury": Range(14000, 18500, 25000),
    },
}

LINE_ITEM_RATES: Dict[str, Tuple[str, Range]] = {
    "demolition": ("m² demolition and removal", Range(90, 160, 280)),
    "floor_tiling": ("m² floor tiling", Range(220, 380, 650)),
    "wall_tile": ("m² wet-area wall tile", Range(260, 450, 750)),
    "paint": ("m² wall/ceiling paint", Range(35, 55, 90)),
    "gypsum_partition": ("m² gypsum partition", Range(220, 350, 550)),
    "interior_door": ("interior door", Range(1000, 1800, 3500)),
    "electrical_point": ("electrical point", Range(250, 450, 850)),
    "electrical_panel": ("electrical panel upgrade", Range(3000, 6500, 14000)),
    "plumbing_point": ("plumbing point", Range(550, 950, 1800)),
    "bathroom_waterproofing": ("bathroom waterproofing", Range(2500, 4500, 8500)),
    "bathroom_refresh": ("bathroom refresh", Range(18000, 32000, 55000)),
    "bathroom_full": ("full bathroom", Range(35000, 65000, 110000)),
    "guest_toilet": ("guest toilet", Range(12000, 30000, 60000)),
    "kitchen_refresh": ("kitchen refresh", Range(18000, 50000, 110000)),
    "kitchen_full": ("full kitchen", Range(45000, 120000, 240000)),
    "home_office": ("home office", Range(8000, 30000, 70000)),
    "shopfront": ("shopfront", Range(20000, 80000, 180000)),
    "fire_safety_allowance": ("fire safety allowance", Range(8000, 25000, 70000)),
    "accessibility_review": ("accessibility review", Range(6000, 20000, 60000)),
    "signage": ("signage", Range(5000, 18000, 60000)),
    "low_voltage": ("low voltage point", Range(250, 450, 900)),
}

CITY_FACTORS = {
    "tel aviv": Range(1.05, 1.10, 1.18),
    "תל אביב": Range(1.05, 1.10, 1.18),
    "jerusalem": Range(1.04, 1.08, 1.16),
    "ירושלים": Range(1.04, 1.08, 1.16),
    "haifa": Range(1.02, 1.06, 1.12),
    "חיפה": Range(1.02, 1.06, 1.12),
}

COMMERCIAL_TYPES = {"shop", "office", "clinic", "retail", "store", "salon", "restaurant", "cafe", "commercial"}


def validate_environment(environment: str) -> str:
    normalized = environment.strip().lower()
    if normalized not in {"sandbox", "production"}:
        raise EstimatorError("INVALID_ENVIRONMENT", "environment must be sandbox or production")
    return normalized


def validate_project(project: ProjectInput) -> None:
    if project.area_sqm <= 0:
        raise EstimatorError("INVALID_AREA", "area_sqm must be greater than zero")
    normalize_enum(project.finish_level, FinishLevel, "UNKNOWN_FINISH_LEVEL")
    normalize_enum(project.scope_level, ScopeLevel, "UNKNOWN_SCOPE_LEVEL")
    if not 0 <= project.vat_rate <= 1:
        raise EstimatorError("INVALID_VAT_RATE", "vat_rate must be between 0 and 1")
    for item in project.line_items:
        if item.quantity < 0:
            raise EstimatorError("NEGATIVE_QUANTITY", f"{item.category} has negative quantity")
        if item.category not in LINE_ITEM_RATES:
            raise EstimatorError("UNKNOWN_LINE_ITEM", f"unsupported line item category '{item.category}'")


def normalize_enum(value: str, enum_type: Any, code: str) -> str:
    raw = str(value).strip().lower()
    valid_values = {item.value for item in enum_type}
    if raw not in valid_values:
        raise EstimatorError(code, f"unsupported value '{value}', expected one of {sorted(valid_values)}")
    return raw


def multiply_ranges(first: Range, second: Range) -> Range:
    return Range(first.low * second.low, first.expected * second.expected, first.high * second.high)


def city_factor(city: str) -> Range:
    city_value = city.lower()
    for key, factor in CITY_FACTORS.items():
        if key in city_value:
            return factor
    return Range(1, 1, 1)


def combined_factor(project: ProjectInput) -> Range:
    factor = city_factor(project.city)
    if project.floor is not None and project.has_elevator is False and project.floor > 2:
        factor = multiply_ranges(factor, Range(1.03, 1.07, 1.14))
    if project.building_year is not None and int(project.building_year) < 1980:
        factor = multiply_ranges(factor, Range(1.08, 1.15, 1.30))
    if project.occupied:
        factor = multiply_ranges(factor, Range(1.05, 1.10, 1.20))
    if project.structural_changes:
        factor = multiply_ranges(factor, Range(1.05, 1.12, 1.25))
    return factor


def line_item_costs(project: ProjectInput) -> Tuple[Range, List[Dict[str, Any]]]:
    total = Range(0, 0, 0)
    rows: List[Dict[str, Any]] = []
    for item in project.line_items:
        description, rate = LINE_ITEM_RATES[item.category]
        cost = rate.scale(item.quantity)
        total = total.add(cost)
        rows.append(
            {
                "category": item.category,
                "description": item.description or description,
                "quantity": item.quantity,
                **cost.to_dict(),
            }
        )
    return total, rows


def room_allowances(project: ProjectInput) -> Tuple[Range, List[Dict[str, Any]]]:
    total = Range(0, 0, 0)
    rows: List[Dict[str, Any]] = []

    if project.bathrooms and not any(item.category.startswith("bathroom") for item in project.line_items):
        factor = 0.45 if project.scope_level in {"partial", "full", "shell"} else 1.0
        cost = LINE_ITEM_RATES["bathroom_full"][1].scale(project.bathrooms).scale(factor)
        total = total.add(cost)
        rows.append({"category": "bathroom_allowance", "quantity": project.bathrooms, **cost.to_dict()})

    if project.kitchens and not any(item.category.startswith("kitchen") for item in project.line_items):
        factor = 0.35 if project.scope_level in {"partial", "full", "shell"} else 1.0
        cost = LINE_ITEM_RATES["kitchen_full"][1].scale(project.kitchens).scale(factor)
        total = total.add(cost)
        rows.append({"category": "kitchen_allowance", "quantity": project.kitchens, **cost.to_dict()})

    return total, rows


def commercial_allowances(project: ProjectInput) -> Tuple[Range, List[Dict[str, Any]], List[str]]:
    total = Range(0, 0, 0)
    rows: List[Dict[str, Any]] = []
    assumptions: List[str] = []
    property_type = project.property_type.lower()
    is_commercial = (
        property_type in COMMERCIAL_TYPES
        or project.scope_level in {"office_fitout", "retail_fitout", "commercial_fitout"}
        or project.requires_business_license
        or project.commercial_public_access
    )
    if not is_commercial:
        return total, rows, assumptions

    assumptions.append("Commercial use requires lease, municipal, fire-safety, accessibility, and signage review where relevant.")

    if project.requires_business_license:
        cost = LINE_ITEM_RATES["fire_safety_allowance"][1]
        total = total.add(cost)
        rows.append({"category": "fire_safety_allowance", "quantity": 1, **cost.to_dict()})

    if project.commercial_public_access or property_type in {"clinic", "shop", "retail", "store", "restaurant", "cafe"}:
        cost = LINE_ITEM_RATES["accessibility_review"][1]
        total = total.add(cost)
        rows.append({"category": "accessibility_review", "quantity": 1, **cost.to_dict()})

    if project.signage or property_type in {"shop", "retail", "store", "restaurant", "cafe"}:
        cost = LINE_ITEM_RATES["signage"][1]
        total = total.add(cost)
        rows.append({"category": "signage", "quantity": 1, **cost.to_dict()})

    if project.food_business or property_type in {"restaurant", "cafe"}:
        cost = Range(15000, 45000, 120000)
        total = total.add(cost)
        rows.append({"category": "food_business_systems", "quantity": 1, **cost.to_dict()})
        assumptions.append("Food business may require ventilation, washable surfaces, drainage, grease trap, and health or municipal review.")

    return total, rows, assumptions


def contingency_rate(project: ProjectInput) -> Range:
    low, expected, high = (0.08, 0.10, 0.12) if project.scope_level == "cosmetic" else (0.10, 0.15, 0.20)
    if project.building_year is not None and int(project.building_year) < 1980:
        low, expected, high = low + 0.05, expected + 0.06, high + 0.10
    if project.occupied:
        low, expected, high = low + 0.03, expected + 0.05, high + 0.08
    if project.requires_business_license or project.commercial_public_access:
        low, expected, high = low + 0.05, expected + 0.08, high + 0.10
    if project.structural_changes:
        low, expected, high = low + 0.08, expected + 0.10, high + 0.15
    return Range(min(low, 0.35), min(expected, 0.45), min(high, 0.60))


def professional_fee_rate(project: ProjectInput) -> Range:
    if project.scope_level in {"commercial_fitout", "retail_fitout", "office_fitout", "shell"} or project.structural_changes:
        return Range(0.06, 0.10, 0.15)
    if project.scope_level == "cosmetic":
        return Range(0, 0.03, 0.06)
    return Range(0.03, 0.07, 0.12)


def build_assumptions(project: ProjectInput) -> List[str]:
    items = [
        f"Benchmark scope level: {project.scope_level}",
        f"Finish level: {project.finish_level}",
        f"VAT {'included in headline totals' if project.include_vat else 'excluded from headline totals'} at modeled rate {project.vat_rate:.0%}.",
        "Verify current VAT rate, CBS construction input indices, and written market quotes before production use.",
    ]
    if project.city:
        items.append(f"City/locality adjustment considered for {project.city}.")
    if project.floor is not None and project.has_elevator is False and project.floor > 2:
        items.append("No-elevator access above second floor increases hauling, waste, and labor costs.")
    if project.building_year is not None and int(project.building_year) < 1980:
        items.append("Pre-1980 building increases hidden infrastructure and demolition risk.")
    if project.occupied:
        items.append("Occupied renovation requires protection, phasing, cleaning, and productivity allowance.")
    if project.structural_changes:
        items.append("Structural changes require engineer review and may require permit checks.")
    return items


def build_risks(project: ProjectInput) -> List[Risk]:
    risks: List[Risk] = []
    if project.bathrooms or project.wet_rooms:
        risks.append(Risk("medium", "wet rooms", "confirm waterproofing method, plumbing scope, flood test, and warranty"))
    if project.kitchens:
        risks.append(Risk("medium", "kitchen specification", "request cabinet, counter, sink, faucet, appliance, and electrical assumptions"))
    if project.building_year is not None and int(project.building_year) < 1980:
        risks.append(Risk("high", "old building", "inspect plumbing, electrical panel, dampness, asbestos suspicion, and prior alterations"))
    if project.floor is not None and project.has_elevator is False and project.floor > 2:
        risks.append(Risk("medium", "site access", "confirm stair protection, waste route, working hours, and hauling cost"))
    if project.occupied:
        risks.append(Risk("medium", "occupied work", "define dust protection, temporary services, daily clean-up, and phase plan"))
    if project.requires_business_license:
        risks.append(Risk("high", "business licensing", "check municipal business license requirements before signing construction contract"))
    if project.commercial_public_access:
        risks.append(Risk("high", "accessibility", "check accessibility obligations for public-facing premises"))
        risks.append(Risk("medium", "fire safety", "check emergency lighting, exit signs, extinguishers, detection, and approval path"))
    if project.signage:
        risks.append(Risk("medium", "signage", "check municipal signage approval and facade rules"))
    if project.food_business:
        risks.append(Risk("high", "food business systems", "check ventilation, grease trap, washable surfaces, drainage, and health or municipal requirements"))
    if project.structural_changes:
        risks.append(Risk("high", "structural work", "obtain engineer review and permit guidance before pricing as construction work"))

    return risks or [Risk("low", "scope definition", "measure quantities and request at least three comparable written quotes")]


def build_quote_review(project: ProjectInput, expected_including_vat: int) -> Optional[Dict[str, Any]]:
    if project.contractor_quote_total is None:
        return None

    quote = float(project.contractor_quote_total)
    normalized = quote * (1 + project.vat_rate) if project.contractor_quote_includes_vat is False else quote
    ratio = normalized / expected_including_vat if expected_including_vat else math.nan
    risk = "high" if ratio < 0.80 else "medium" if ratio > 1.25 else "medium-low"
    action = (
        "request quantities, exclusions, VAT status, material specs, warranty, insurance, and licensed-trade evidence"
        if risk == "high"
        else "compare completeness, included scope, exclusions, and payment terms"
    )
    return {
        "quote_total_input": int(round(quote)),
        "quote_includes_vat": project.contractor_quote_includes_vat,
        "normalized_including_vat": round_to_100(normalized),
        "benchmark_expected_including_vat": expected_including_vat,
        "ratio_to_benchmark": round(ratio, 2),
        "risk": risk,
        "action": action,
    }


class RenovationCostEstimatorClient:
    """Typed local client for Israeli renovation planning estimates."""

    def __init__(self, default_vat_rate: float = 0.18, store_dir: str | Path | None = None) -> None:
        if not 0 <= default_vat_rate <= 1:
            raise EstimatorError("INVALID_VAT_RATE", "default_vat_rate must be between 0 and 1")
        self.default_vat_rate = default_vat_rate
        self.store_dir = Path(store_dir or os.getenv("RENOVATION_ESTIMATOR_STORE", ".renovation-estimator-store"))

    def estimate(self, project: ProjectInput | Mapping[str, Any]) -> EstimateResult:
        project_input = ProjectInput.from_mapping(project) if isinstance(project, Mapping) else project
        if project_input.vat_rate == 0.18 and self.default_vat_rate != 0.18:
            project_input.vat_rate = self.default_vat_rate
        validate_project(project_input)

        scope = normalize_enum(project_input.scope_level, ScopeLevel, "UNKNOWN_SCOPE_LEVEL")
        finish = normalize_enum(project_input.finish_level, FinishLevel, "UNKNOWN_FINISH_LEVEL")
        base = BASE_BENCHMARKS[scope][finish].scale(project_input.area_sqm)
        line_total, line_rows = line_item_costs(project_input)
        room_total, room_rows = room_allowances(project_input)
        commercial_total, commercial_rows, commercial_assumptions = commercial_allowances(project_input)

        direct = multiply_ranges(base.add(line_total).add(room_total).add(commercial_total), combined_factor(project_input))
        contingency = Range(
            direct.low * contingency_rate(project_input).low,
            direct.expected * contingency_rate(project_input).expected,
            direct.high * contingency_rate(project_input).high,
        )
        professional = Range(
            direct.low * professional_fee_rate(project_input).low,
            direct.expected * professional_fee_rate(project_input).expected,
            direct.high * professional_fee_rate(project_input).high,
        )
        before_vat = direct.add(contingency).add(professional)
        vat = before_vat.scale(project_input.vat_rate)
        after_vat = before_vat.add(vat)
        headline = after_vat if project_input.include_vat else before_vat

        assumptions = build_assumptions(project_input)
        assumptions.extend(commercial_assumptions)
        line_breakdown = [
            {
                "category": "base_benchmark",
                "description": f"{project_input.scope_level}/{project_input.finish_level} x {project_input.area_sqm:g} m²",
                **base.to_dict(),
            }
        ]
        line_breakdown.extend(line_rows)
        line_breakdown.extend(room_rows)
        line_breakdown.extend(commercial_rows)

        expected_including_vat = round_to_100(after_vat.expected)
        result = EstimateResult(
            project_name=project_input.project_name,
            currency="ILS",
            estimate_date=date.today().strftime("%d/%m/%Y") if project_input.language.lower().startswith("he") else date.today().isoformat(),
            confidence="concept" if project_input.line_items else "rough",
            totals={
                "direct_low": round_to_100(direct.low),
                "direct_expected": round_to_100(direct.expected),
                "direct_high": round_to_100(direct.high),
                "contingency_low": round_to_100(contingency.low),
                "contingency_expected": round_to_100(contingency.expected),
                "contingency_high": round_to_100(contingency.high),
                "professional_fees_low": round_to_100(professional.low),
                "professional_fees_expected": round_to_100(professional.expected),
                "professional_fees_high": round_to_100(professional.high),
                "vat_low": round_to_100(vat.low),
                "vat_expected": round_to_100(vat.expected),
                "vat_high": round_to_100(vat.high),
                "total_low": round_to_100(headline.low),
                "total_expected": round_to_100(headline.expected),
                "total_high": round_to_100(headline.high),
                "total_including_vat_expected": expected_including_vat,
                "total_excluding_vat_expected": round_to_100(before_vat.expected),
            },
            direct_range=direct.to_dict(),
            assumptions=assumptions,
            risks=build_risks(project_input),
            line_breakdown=line_breakdown,
        )
        result.quote_review = build_quote_review(project_input, expected_including_vat)
        return result

    async def estimate_async(self, project: ProjectInput | Mapping[str, Any]) -> EstimateResult:
        await asyncio.sleep(0)
        return self.estimate(project)

    def validate(self, project: ProjectInput | Mapping[str, Any]) -> bool:
        project_input = ProjectInput.from_mapping(project) if isinstance(project, Mapping) else project
        validate_project(project_input)
        return True

    def benchmarks(self) -> Dict[str, Any]:
        return {
            "base_benchmarks": {
                scope: {finish: range_value.to_dict() for finish, range_value in finish_map.items()}
                for scope, finish_map in BASE_BENCHMARKS.items()
            },
            "line_item_rates": {
                key: {"description": description, **range_value.to_dict()}
                for key, (description, range_value) in LINE_ITEM_RATES.items()
            },
        }

    def create_project(self, project: ProjectInput | Mapping[str, Any], environment: str = "sandbox") -> ProjectRecord:
        environment = validate_environment(environment)
        project_input = ProjectInput.from_mapping(project) if isinstance(project, Mapping) else project
        validate_project(project_input)
        project_id = f"prj_{uuid.uuid4().hex[:12]}"
        target_dir = self.store_dir / environment
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{project_id}.json"
        target.write_text(json.dumps(project_input.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return ProjectRecord(id=project_id, environment=environment, project=project_input, path=str(target))

    def load_project(self, project_id: str, environment: str = "sandbox") -> ProjectInput:
        environment = validate_environment(environment)
        if not project_id.startswith("prj_"):
            raise EstimatorError("INVALID_PROJECT_ID", "project id must start with prj_")
        path = self.store_dir / environment / f"{project_id}.json"
        if not path.exists():
            raise EstimatorError("PROJECT_NOT_FOUND", f"project id {project_id} was not found in {environment}")
        return ProjectInput.from_mapping(json.loads(path.read_text(encoding="utf-8")))

    def estimate_by_id(self, project_id: str, environment: str = "sandbox") -> EstimateResult:
        return self.estimate(self.load_project(project_id, environment=environment))


def load_project(path: str | Path) -> ProjectInput:
    return ProjectInput.from_mapping(json.loads(Path(path).read_text(encoding="utf-8")))


def save_estimate(result: EstimateResult, path: str | Path) -> None:
    Path(path).write_text(result.to_json(), encoding="utf-8")


def estimate_from_json(path: str | Path) -> EstimateResult:
    return RenovationCostEstimatorClient().estimate(load_project(path))


__all__ = [
    "EstimatorError",
    "FinishLevel",
    "ScopeLevel",
    "Range",
    "LineItem",
    "ProjectInput",
    "Risk",
    "ProjectRecord",
    "EstimateResult",
    "RenovationCostEstimatorClient",
    "validate_environment",
    "validate_project",
    "load_project",
    "save_estimate",
    "estimate_from_json",
    "format_ils",
]
