#!/usr/bin/env python3
"""Structured estimator for Israeli dental-treatment planning.

The module is intentionally local/offline. It gives planning-grade ranges and
validation warnings for Israeli consumers, freelancers, and small businesses
that need cash-flow planning before requesting binding quotes from a dentist.
"""

from __future__ import annotations

import asyncio
import csv
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Mapping, Sequence


MONEY = Decimal("0.01")
CURRENT_ISRAEL_VAT_RATE = Decimal("0.18")
CURRENT_ISRAEL_VAT_RATE_SOURCE_DATE = "04/06/2026"


class PlannerError(ValueError):
    """Base exception for invalid treatment-planning input."""


class UnknownTreatmentCodeError(PlannerError):
    """Raised when a treatment code is not present in the local catalog."""


class ValidationError(PlannerError):
    """Raised when strict validation is requested and the plan is unsafe."""


def _d(value: int | float | str | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)


def format_currency(value: int | float | str | Decimal) -> str:
    """Format a numeric value as Israeli shekels."""
    amount = _d(value)
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    return f"{sign}₪{amount:,.2f}"


def parse_israeli_date(value: str | None) -> date:
    """Parse DD/MM/YYYY, legacy DD-MM-YYYY, YYYY-MM-DD, or return today's date when omitted."""
    if not value:
        return date.today()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise PlannerError("date must use DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD")


ENVIRONMENTS = {"sandbox", "production"}

REGION_FACTORS: dict[str, Decimal] = {
    "tel_aviv": Decimal("1.12"),
    "center": Decimal("1.05"),
    "jerusalem": Decimal("1.06"),
    "haifa": Decimal("1.00"),
    "north": Decimal("0.95"),
    "south": Decimal("0.94"),
    "periphery": Decimal("0.90"),
    "eilat": Decimal("0.92"),
}

PROVIDER_PROFILES: dict[str, dict[str, Any]] = {
    "private": {
        "display_name": "Private dentist",
        "base_factor": Decimal("1.00"),
        "default_discount_pct": Decimal("0"),
        "notes": "Use for independent clinics and specialist-led private plans.",
    },
    "maccabident": {
        "display_name": "Maccabident",
        "base_factor": Decimal("0.78"),
        "default_discount_pct": Decimal("0"),
        "notes": "Use as a planning profile for HMO-affiliated clinic pricing.",
    },
    "clalit_smile": {
        "display_name": "Clalit Smile",
        "base_factor": Decimal("0.80"),
        "default_discount_pct": Decimal("0"),
        "notes": "Use as a planning profile for HMO-affiliated clinic pricing.",
    },
    "leumit_dental": {
        "display_name": "Leumit Dental",
        "base_factor": Decimal("0.82"),
        "default_discount_pct": Decimal("0"),
        "notes": "Use when comparing another Kupat Holim dental route.",
    },
    "meuhedet_dental": {
        "display_name": "Meuhedet Dental",
        "base_factor": Decimal("0.83"),
        "default_discount_pct": Decimal("0"),
        "notes": "Use when comparing another Kupat Holim dental route.",
    },
}

URGENCY_FACTORS: dict[str, Decimal] = {
    "routine": Decimal("1.00"),
    "soon": Decimal("1.05"),
    "urgent": Decimal("1.18"),
    "emergency": Decimal("1.30"),
}

CATALOG: dict[str, dict[str, Any]] = {
    "exam": {"description": "Comprehensive dental examination", "category": "diagnostic", "price_min": 150, "price_max": 350, "visits": 1, "minutes": 30, "requires": []},
    "xray_bitewing": {"description": "Bitewing X-ray set", "category": "diagnostic", "price_min": 120, "price_max": 280, "visits": 1, "minutes": 15, "requires": []},
    "panoramic_xray": {"description": "Panoramic dental X-ray", "category": "diagnostic", "price_min": 180, "price_max": 450, "visits": 1, "minutes": 20, "requires": []},
    "cleaning": {"description": "Dental hygienist cleaning", "category": "preventive", "price_min": 220, "price_max": 420, "visits": 1, "minutes": 45, "requires": []},
    "fluoride_child": {"description": "Fluoride treatment for a child", "category": "preventive", "price_min": 60, "price_max": 160, "visits": 1, "minutes": 15, "requires": ["exam"]},
    "sealant_child": {"description": "Child fissure sealant", "category": "preventive", "price_min": 80, "price_max": 220, "visits": 1, "minutes": 20, "requires": ["exam"]},
    "filling_small": {"description": "Small composite filling", "category": "restorative", "price_min": 350, "price_max": 750, "visits": 1, "minutes": 45, "requires": ["exam"]},
    "filling_large": {"description": "Large composite filling", "category": "restorative", "price_min": 550, "price_max": 1100, "visits": 1, "minutes": 60, "requires": ["exam"]},
    "root_canal_anterior": {"description": "Anterior root canal treatment", "category": "endodontics", "price_min": 1200, "price_max": 2300, "visits": 2, "minutes": 150, "requires": ["exam", "xray_bitewing"]},
    "root_canal_molar": {"description": "Molar root canal treatment", "category": "endodontics", "price_min": 1800, "price_max": 3600, "visits": 2, "minutes": 180, "requires": ["exam", "xray_bitewing"]},
    "crown_porcelain": {"description": "Porcelain crown", "category": "prosthodontics", "price_min": 2200, "price_max": 4500, "visits": 3, "minutes": 180, "requires": ["exam"]},
    "implant": {"description": "Dental implant placement", "category": "surgery", "price_min": 3500, "price_max": 7000, "visits": 3, "minutes": 180, "requires": ["exam", "panoramic_xray"]},
    "implant_crown": {"description": "Implant-supported crown", "category": "prosthodontics", "price_min": 2500, "price_max": 5200, "visits": 3, "minutes": 160, "requires": ["implant"]},
    "extraction_simple": {"description": "Simple tooth extraction", "category": "surgery", "price_min": 400, "price_max": 900, "visits": 1, "minutes": 45, "requires": ["exam"]},
    "extraction_surgical": {"description": "Surgical tooth extraction", "category": "surgery", "price_min": 950, "price_max": 2400, "visits": 1, "minutes": 75, "requires": ["exam", "panoramic_xray"]},
    "periodontal_scaling": {"description": "Deep periodontal scaling", "category": "periodontics", "price_min": 800, "price_max": 1800, "visits": 2, "minutes": 120, "requires": ["exam"]},
    "whitening": {"description": "Teeth whitening", "category": "aesthetic", "price_min": 900, "price_max": 2500, "visits": 1, "minutes": 75, "requires": ["exam", "cleaning"]},
    "night_guard": {"description": "Night guard for bruxism", "category": "appliance", "price_min": 700, "price_max": 1800, "visits": 2, "minutes": 60, "requires": ["exam"]},
    "orthodontic_consult": {"description": "Orthodontic consultation", "category": "orthodontics", "price_min": 250, "price_max": 700, "visits": 1, "minutes": 40, "requires": []},
    "aligner_case": {"description": "Clear aligner treatment case", "category": "orthodontics", "price_min": 12000, "price_max": 26000, "visits": 8, "minutes": 360, "requires": ["orthodontic_consult"]},
    "denture_partial": {"description": "Partial removable denture", "category": "prosthodontics", "price_min": 3500, "price_max": 8500, "visits": 5, "minutes": 240, "requires": ["exam"]},
    "emergency_visit": {"description": "Emergency dental visit", "category": "emergency", "price_min": 300, "price_max": 900, "visits": 1, "minutes": 30, "requires": []},
}


@dataclass(slots=True)
class InsurancePlan:
    name: str = "self_pay"
    discount_pct: Decimal = Decimal("0")
    annual_limit_ils: Decimal | None = None
    used_annual_ils: Decimal = Decimal("0")
    waiting_period_met: bool = True
    covered_categories: list[str] | None = None
    category_discount_pct: dict[str, Decimal] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "InsurancePlan":
        if not data:
            return cls()
        category_discount_pct = {str(k): Decimal(str(v)) for k, v in data.get("category_discount_pct", {}).items()}
        annual_limit = data.get("annual_limit_ils")
        return cls(
            name=str(data.get("name", "self_pay")),
            discount_pct=Decimal(str(data.get("discount_pct", "0"))),
            annual_limit_ils=None if annual_limit in (None, "") else Decimal(str(annual_limit)),
            used_annual_ils=Decimal(str(data.get("used_annual_ils", "0"))),
            waiting_period_met=bool(data.get("waiting_period_met", True)),
            covered_categories=list(data["covered_categories"]) if data.get("covered_categories") else None,
            category_discount_pct=category_discount_pct,
        )

    def discount_for_category(self, category: str) -> Decimal:
        if not self.waiting_period_met:
            return Decimal("0")
        if self.covered_categories is not None and category not in self.covered_categories:
            return Decimal("0")
        return self.category_discount_pct.get(category, self.discount_pct)


@dataclass(slots=True)
class TreatmentItem:
    code: str
    tooth: str | None = None
    quantity: int = 1
    urgency: str = "routine"
    override_price_ils: Decimal | None = None
    notes: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "TreatmentItem":
        if "code" not in data:
            raise PlannerError("each treatment item must include code")
        quantity = int(data.get("quantity", 1))
        if quantity < 1:
            raise PlannerError("quantity must be at least 1")
        override = data.get("override_price_ils")
        urgency = str(data.get("urgency", "routine"))
        if urgency not in URGENCY_FACTORS:
            raise PlannerError(f"unsupported urgency: {urgency}")
        return cls(
            code=str(data["code"]),
            tooth=None if data.get("tooth") in (None, "") else str(data.get("tooth")),
            quantity=quantity,
            urgency=urgency,
            override_price_ils=None if override in (None, "") else _d(override),
            notes=str(data.get("notes", "")),
        )


@dataclass(slots=True)
class PatientContext:
    provider: str = "private"
    region: str = "center"
    insurance: InsurancePlan = field(default_factory=InsurancePlan)
    include_vat: bool = False
    vat_rate: Decimal = CURRENT_ISRAEL_VAT_RATE
    start_date: date = field(default_factory=date.today)
    max_visits_per_month: int = 4
    strict: bool = False

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "PatientContext":
        data = data or {}
        provider = str(data.get("provider", "private"))
        region = str(data.get("region", "center"))
        if provider not in PROVIDER_PROFILES:
            raise PlannerError(f"unsupported provider: {provider}")
        if region not in REGION_FACTORS:
            raise PlannerError(f"unsupported region: {region}")
        max_visits = int(data.get("max_visits_per_month", 4))
        if max_visits < 1:
            raise PlannerError("max_visits_per_month must be at least 1")
        return cls(
            provider=provider,
            region=region,
            insurance=InsurancePlan.from_mapping(data.get("insurance")),
            include_vat=bool(data.get("include_vat", False)),
            vat_rate=Decimal(str(data.get("vat_rate", str(CURRENT_ISRAEL_VAT_RATE)))),
            start_date=parse_israeli_date(data.get("start_date")),
            max_visits_per_month=max_visits,
            strict=bool(data.get("strict", False)),
        )


@dataclass(slots=True)
class EstimateLine:
    code: str
    description: str
    category: str
    tooth: str | None
    quantity: int
    urgency: str
    visits: int
    minutes: int
    gross_ils: Decimal
    covered_ils: Decimal
    patient_ils: Decimal
    vat_ils: Decimal
    total_with_vat_ils: Decimal
    notes: str = ""


@dataclass(slots=True)
class TreatmentEstimate:
    provider: str
    provider_display_name: str
    region: str
    generated_on: str
    subtotal_ils: Decimal
    covered_ils: Decimal
    patient_before_vat_ils: Decimal
    vat_ils: Decimal
    total_patient_ils: Decimal
    visits: int
    chair_minutes: int
    warnings: list[str]
    assumptions: list[str]
    lines: list[EstimateLine]
    schedule: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        def convert(value: Any) -> Any:
            if isinstance(value, Decimal):
                return float(value)
            if isinstance(value, list):
                return [convert(v) for v in value]
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            return value
        return convert(asdict(self))

    def to_markdown(self) -> str:
        rows = ["| Code | Description | Qty | Visits | Gross | Covered | Patient |", "|---|---:|---:|---:|---:|---:|---:|"]
        for line in self.lines:
            rows.append(
                f"| {line.code} | {line.description} | {line.quantity} | {line.visits} | "
                f"{format_currency(line.gross_ils)} | {format_currency(line.covered_ils)} | "
                f"{format_currency(line.total_with_vat_ils)} |"
            )
        warnings = "\n".join(f"- {w}" for w in self.warnings) or "- None"
        assumptions = "\n".join(f"- {a}" for a in self.assumptions) or "- None"
        schedule = "\n".join(
            f"- {entry['date']}: visit {entry['visit_number']} — {entry['code']} ({entry['minutes']} min)"
            for entry in self.schedule
        )
        return (
            f"# Dental treatment estimate\n\nProvider: {self.provider_display_name}\n\nRegion: {self.region}\n\n"
            + "\n".join(rows)
            + "\n\n"
            f"Subtotal: {format_currency(self.subtotal_ils)}\n\n"
            f"Estimated coverage: {format_currency(self.covered_ils)}\n\n"
            f"Patient total: {format_currency(self.total_patient_ils)}\n\n"
            f"Visits: {self.visits}; chair time: {self.chair_minutes} minutes\n\n"
            f"## Warnings\n{warnings}\n\n## Assumptions\n{assumptions}\n\n## Draft schedule\n{schedule or '- Not generated'}\n"
        )


def treatment_catalog() -> dict[str, dict[str, Any]]:
    """Return a copy of the built-in treatment catalog."""
    return json.loads(json.dumps(CATALOG))


def sample_plan() -> dict[str, Any]:
    """Return a representative Israeli dental-treatment plan request."""
    return {
        "context": {
            "provider": "private",
            "region": "center",
            "start_date": date.today().strftime("%d/%m/%Y"),
            "insurance": {
                "name": "supplementary_example",
                "discount_pct": 25,
                "annual_limit_ils": 3000,
                "used_annual_ils": 400,
                "waiting_period_met": True,
                "covered_categories": ["diagnostic", "preventive", "restorative", "endodontics"],
            },
        },
        "treatments": [
            {"code": "exam"},
            {"code": "xray_bitewing"},
            {"code": "cleaning"},
            {"code": "filling_small", "tooth": "16"},
            {"code": "root_canal_molar", "tooth": "46", "urgency": "soon"},
            {"code": "crown_porcelain", "tooth": "46"},
        ],
    }


class DentalTreatmentPlannerClient:
    """Typed sync and async client for local treatment-plan estimation."""

    def __init__(
        self,
        catalog: Mapping[str, Mapping[str, Any]] | None = None,
        provider_profiles: Mapping[str, Mapping[str, Any]] | None = None,
        region_factors: Mapping[str, Decimal] | None = None,
        environment: str = "sandbox",
    ) -> None:
        if environment not in ENVIRONMENTS:
            raise PlannerError(f"unsupported environment: {environment}")
        self.environment = environment
        self.catalog: dict[str, Mapping[str, Any]] = dict(catalog or CATALOG)
        self.provider_profiles: dict[str, Mapping[str, Any]] = dict(provider_profiles or PROVIDER_PROFILES)
        self.region_factors: dict[str, Decimal] = dict(region_factors or REGION_FACTORS)

    def validate_plan(self, plan: Mapping[str, Any]) -> list[str]:
        """Return validation warnings. Raise only for malformed input."""
        context = PatientContext.from_mapping(plan.get("context", {}))
        items = [TreatmentItem.from_mapping(item) for item in plan.get("treatments", [])]
        if not items:
            raise PlannerError("plan must contain at least one treatment")
        warnings: list[str] = []
        codes = {item.code for item in items}
        for item in items:
            catalog_entry = self._entry(item.code)
            for requirement in catalog_entry.get("requires", []):
                if requirement not in codes:
                    warnings.append(f"{item.code} usually requires {requirement}; add it or confirm that it is already completed.")
        if any(item.urgency in {"urgent", "emergency"} for item in items) and "emergency_visit" not in codes:
            warnings.append("Urgent pain, swelling, trauma, or fever requires same-day clinical triage.")
        if "implant" in codes and "panoramic_xray" not in codes:
            warnings.append("Implant planning usually needs panoramic imaging or CBCT before a binding quote.")
        if "whitening" in codes and ("cleaning" not in codes or "exam" not in codes):
            warnings.append("Whitening should follow examination and cleaning, especially with active decay or gum disease.")
        if context.include_vat:
            warnings.append("VAT at 18% was added because include_vat=true; verify whether the invoice item is taxable.")
        if context.insurance.annual_limit_ils is not None and context.insurance.used_annual_ils > context.insurance.annual_limit_ils:
            warnings.append("Used annual benefit is greater than the stated annual limit; coverage is likely exhausted.")
        if context.strict and warnings:
            raise ValidationError("; ".join(warnings))
        return warnings


    def create_plan(self, plan: Mapping[str, Any], plan_id: str | None = None) -> dict[str, Any]:
        """Return a validated plan envelope with a stable id for CLI chaining."""
        import uuid
        warnings = self.validate_plan(plan)
        selected_id = plan_id or str(plan.get("plan_id") or uuid.uuid4())
        return {
            "plan_id": selected_id,
            "environment": self.environment,
            "created_on": date.today().strftime("%d/%m/%Y"),
            "warnings": warnings,
            "plan": dict(plan),
        }

    def estimate(self, plan: Mapping[str, Any]) -> TreatmentEstimate:
        """Estimate the patient cost, provider coverage, visit count, and schedule."""
        context = PatientContext.from_mapping(plan.get("context", {}))
        items = [TreatmentItem.from_mapping(item) for item in plan.get("treatments", [])]
        if not items:
            raise PlannerError("plan must contain at least one treatment")

        warnings = self.validate_plan(plan)
        provider = self.provider_profiles[context.provider]
        provider_factor = Decimal(str(provider["base_factor"]))
        region_factor = self.region_factors[context.region]
        remaining_coverage: Decimal | None = None
        if context.insurance.annual_limit_ils is not None:
            remaining_coverage = max(Decimal("0"), context.insurance.annual_limit_ils - context.insurance.used_annual_ils)

        lines: list[EstimateLine] = []
        subtotal = Decimal("0")
        covered_total = Decimal("0")
        patient_before_vat = Decimal("0")
        vat_total = Decimal("0")
        total_visits = 0
        total_minutes = 0

        for item in items:
            entry = self._entry(item.code)
            unit_price = item.override_price_ils if item.override_price_ils is not None else self._catalog_midpoint(entry)
            gross = _d(unit_price * Decimal(item.quantity) * provider_factor * region_factor * URGENCY_FACTORS[item.urgency])
            discount_pct = context.insurance.discount_for_category(str(entry["category"]))
            potential_coverage = _d(gross * (discount_pct / Decimal("100")))
            if remaining_coverage is not None:
                covered = min(potential_coverage, remaining_coverage)
                remaining_coverage = max(Decimal("0"), remaining_coverage - covered)
            else:
                covered = potential_coverage
            patient = _d(gross - covered)
            vat = _d(patient * context.vat_rate) if context.include_vat else Decimal("0.00")
            total_with_vat = _d(patient + vat)
            visits = int(entry["visits"]) * item.quantity
            minutes = int(entry["minutes"]) * item.quantity
            lines.append(EstimateLine(item.code, str(entry["description"]), str(entry["category"]), item.tooth, item.quantity, item.urgency, visits, minutes, gross, covered, patient, vat, total_with_vat, item.notes))
            subtotal += gross
            covered_total += covered
            patient_before_vat += patient
            vat_total += vat
            total_visits += visits
            total_minutes += minutes

        assumptions = [
            "Amounts are planning estimates, not binding medical quotes.",
            "HMO and supplementary-plan eligibility depends on membership, waiting periods, annual caps, age, and plan rules.",
            "Private-clinic prices vary by specialist, materials, lab work, imaging, sedation, and complications.",
            "Clinical sequencing must be confirmed by a licensed dentist before committing to treatment.",
        ]
        schedule = self.build_schedule(lines, context.start_date, context.max_visits_per_month)
        return TreatmentEstimate(
            provider=context.provider,
            provider_display_name=str(provider["display_name"]),
            region=context.region,
            generated_on=date.today().isoformat(),
            subtotal_ils=_d(subtotal),
            covered_ils=_d(covered_total),
            patient_before_vat_ils=_d(patient_before_vat),
            vat_ils=_d(vat_total),
            total_patient_ils=_d(patient_before_vat + vat_total),
            visits=total_visits,
            chair_minutes=total_minutes,
            warnings=warnings,
            assumptions=assumptions,
            lines=lines,
            schedule=schedule,
        )

    async def async_estimate(self, plan: Mapping[str, Any]) -> TreatmentEstimate:
        """Async wrapper for applications that standardize around awaitable clients."""
        await asyncio.sleep(0)
        return self.estimate(plan)

    def compare_providers(self, plan: Mapping[str, Any], providers: Sequence[str] = ("private", "maccabident", "clalit_smile")) -> list[TreatmentEstimate]:
        """Return estimates for multiple providers using the same treatment list and context."""
        estimates: list[TreatmentEstimate] = []
        base_context = dict(plan.get("context", {}))
        for provider in providers:
            if provider not in self.provider_profiles:
                raise PlannerError(f"unsupported provider: {provider}")
            copied = {"context": {**base_context, "provider": provider}, "treatments": list(plan.get("treatments", []))}
            estimates.append(self.estimate(copied))
        return sorted(estimates, key=lambda estimate: estimate.total_patient_ils)

    def build_schedule(self, lines: Sequence[EstimateLine], start: date, max_visits_per_month: int = 4) -> list[dict[str, Any]]:
        """Generate a simple draft schedule with weekly spacing and monthly throttling using DD/MM/YYYY dates."""
        if max_visits_per_month < 1:
            raise PlannerError("max_visits_per_month must be at least 1")
        schedule: list[dict[str, Any]] = []
        current = start
        visits_in_month: dict[tuple[int, int], int] = {}
        visit_number = 1
        for line in lines:
            for part in range(1, line.visits + 1):
                key = (current.year, current.month)
                while visits_in_month.get(key, 0) >= max_visits_per_month:
                    current = (current.replace(day=1) + timedelta(days=32)).replace(day=1)
                    key = (current.year, current.month)
                visits_in_month[key] = visits_in_month.get(key, 0) + 1
                schedule.append({"visit_number": visit_number, "date": current.strftime("%d/%m/%Y"), "code": line.code, "description": line.description, "minutes": max(15, round(line.minutes / max(line.visits, 1))), "part": part, "parts": line.visits})
                visit_number += 1
                current += timedelta(days=7)
        return schedule

    def export_catalog_csv(self, path: str | Path) -> Path:
        """Write the current catalog to CSV."""
        destination = Path(path)
        with destination.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["code", "description", "category", "price_min", "price_max", "visits", "minutes", "requires"])
            writer.writeheader()
            for code, entry in self.catalog.items():
                row = dict(entry)
                row["code"] = code
                row["requires"] = ",".join(row.get("requires", []))
                writer.writerow(row)
        return destination

    def _entry(self, code: str) -> Mapping[str, Any]:
        try:
            return self.catalog[code]
        except KeyError as exc:
            raise UnknownTreatmentCodeError(f"unknown treatment code: {code}") from exc

    @staticmethod
    def _catalog_midpoint(entry: Mapping[str, Any]) -> Decimal:
        return _d((Decimal(str(entry["price_min"])) + Decimal(str(entry["price_max"]))) / Decimal("2"))


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(data: Mapping[str, Any], path: str | Path) -> Path:
    destination = Path(path)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return destination


def estimate_from_file(path: str | Path) -> TreatmentEstimate:
    return DentalTreatmentPlannerClient().estimate(load_json(path))


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Estimate an Israeli dental-treatment plan from JSON.")
    parser.add_argument("plan", nargs="?", help="Path to a treatment-plan JSON file")
    parser.add_argument("--sample", action="store_true", help="Print a sample request JSON")
    parser.add_argument("--markdown", action="store_true", help="Print a Markdown estimate")
    args = parser.parse_args()
    if args.sample:
        print(json.dumps(sample_plan(), ensure_ascii=False, indent=2))
        return
    if not args.plan:
        parser.error("provide a plan path or --sample")
    estimate = estimate_from_file(args.plan)
    print(estimate.to_markdown() if args.markdown else json.dumps(estimate.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
