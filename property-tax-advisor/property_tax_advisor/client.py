#!/usr/bin/env python3
"""Typed helper for Israeli property-tax triage examples.

The module uses sample rates and simplified brackets for deterministic triage.
Official municipal orders and Israel Tax Authority publications control production use.
"""

from __future__ import annotations

import asyncio
import dataclasses
import datetime as _dt
import json
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


class AdvisorError(ValueError):
    """Structured validation error raised by helper functions."""

    def __init__(self, code: str, message: str, field: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.field = field
        self.message = message

    def to_dict(self) -> Dict[str, str | None]:
        return {"code": self.code, "message": self.message, "field": self.field}


class Authority(str, Enum):
    MUNICIPALITY = "municipality"
    TAX_AUTHORITY = "tax_authority"
    LOCAL_PLANNING_COMMITTEE = "local_planning_committee"
    UNKNOWN = "unknown"


class TaxType(str, Enum):
    ARNONA = "arnona"
    MAS_RECHUSH = "mas_rechush"
    PURCHASE_TAX = "purchase_tax"
    BETTERMENT_LEVY = "betterment_levy"
    LAND_APPRECIATION_TAX = "land_appreciation_tax"
    MUNICIPAL_FEE = "municipal_fee"


class Usage(str, Enum):
    RESIDENTIAL = "residential"
    OFFICE = "office"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    WAREHOUSE = "warehouse"
    WORKSHOP = "workshop"
    CLINIC = "clinic"
    PARKING = "parking"
    VACANT = "vacant"


class BuyerProfile(str, Enum):
    SINGLE_HOME = "single_home"
    ADDITIONAL_HOME = "additional_home"
    REPLACEMENT_HOME = "replacement_home"
    NON_RESIDENT = "non_resident"
    COMMERCIAL_ASSET = "commercial_asset"
    RELIEF_CATEGORY = "relief_category"


@dataclass(frozen=True)
class MunicipalRate:
    municipality: str
    zone: str
    usage: str
    annual_rate_per_sqm: float
    label: str


@dataclass(frozen=True)
class DiscountRule:
    key: str
    label: str
    percent: float
    max_area_sqm: Optional[float] = None
    max_months: Optional[int] = None
    requires_documents: Tuple[str, ...] = ()
    warning: str = ""


@dataclass(frozen=True)
class ArnonaInput:
    municipality: str
    area_sqm: float
    zone: str
    usage: str
    months: int = 2
    discount: Optional[str] = None
    discount_months: Optional[int] = None


@dataclass(frozen=True)
class AssessmentResult:
    tax_type: str
    authority: str
    amount: float
    currency: str = "ILS"
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tax_type": self.tax_type,
            "authority": self.authority,
            "amount": round_money(self.amount),
            "currency": self.currency,
            "details": _jsonable(self.details),
            "warnings": list(self.warnings),
            "next_actions": list(self.next_actions),
        }


@dataclass(frozen=True)
class AppealIssue:
    key: str
    label: str
    evidence: Tuple[str, ...]
    requested_fix: str


SAMPLE_RATES: Dict[str, Dict[str, Dict[str, MunicipalRate]]] = {
    "tel-aviv": {
        "A": {
            "residential": MunicipalRate("tel-aviv", "A", "residential", 105.0, "Residential Zone A"),
            "office": MunicipalRate("tel-aviv", "A", "office", 380.0, "Office Zone A"),
            "commercial": MunicipalRate("tel-aviv", "A", "commercial", 420.0, "Commerce Zone A"),
            "warehouse": MunicipalRate("tel-aviv", "A", "warehouse", 125.0, "Warehouse Zone A"),
            "workshop": MunicipalRate("tel-aviv", "A", "workshop", 170.0, "Workshop Zone A"),
        },
        "B": {
            "residential": MunicipalRate("tel-aviv", "B", "residential", 92.0, "Residential Zone B"),
            "office": MunicipalRate("tel-aviv", "B", "office", 330.0, "Office Zone B"),
            "commercial": MunicipalRate("tel-aviv", "B", "commercial", 365.0, "Commerce Zone B"),
            "warehouse": MunicipalRate("tel-aviv", "B", "warehouse", 110.0, "Warehouse Zone B"),
        },
    },
    "jerusalem": {
        "A": {
            "residential": MunicipalRate("jerusalem", "A", "residential", 95.0, "Residential Zone A"),
            "office": MunicipalRate("jerusalem", "A", "office", 330.0, "Office Zone A"),
            "commercial": MunicipalRate("jerusalem", "A", "commercial", 360.0, "Commerce Zone A"),
            "clinic": MunicipalRate("jerusalem", "A", "clinic", 345.0, "Clinic Zone A"),
        },
        "B": {
            "residential": MunicipalRate("jerusalem", "B", "residential", 82.0, "Residential Zone B"),
            "office": MunicipalRate("jerusalem", "B", "office", 295.0, "Office Zone B"),
            "commercial": MunicipalRate("jerusalem", "B", "commercial", 320.0, "Commerce Zone B"),
            "warehouse": MunicipalRate("jerusalem", "B", "warehouse", 105.0, "Warehouse Zone B"),
        },
        "C": {
            "residential": MunicipalRate("jerusalem", "C", "residential", 70.0, "Residential Zone C"),
            "warehouse": MunicipalRate("jerusalem", "C", "warehouse", 92.0, "Warehouse Zone C"),
        },
    },
    "haifa": {
        "A": {
            "residential": MunicipalRate("haifa", "A", "residential", 88.0, "Residential Zone A"),
            "office": MunicipalRate("haifa", "A", "office", 300.0, "Office Zone A"),
            "commercial": MunicipalRate("haifa", "A", "commercial", 345.0, "Commerce Zone A"),
            "industrial": MunicipalRate("haifa", "A", "industrial", 145.0, "Industry Zone A"),
        },
        "B": {
            "residential": MunicipalRate("haifa", "B", "residential", 76.0, "Residential Zone B"),
            "office": MunicipalRate("haifa", "B", "office", 260.0, "Office Zone B"),
            "warehouse": MunicipalRate("haifa", "B", "warehouse", 90.0, "Warehouse Zone B"),
        },
    },
    "beer-sheva": {
        "A": {
            "residential": MunicipalRate("beer-sheva", "A", "residential", 72.0, "Residential Zone A"),
            "office": MunicipalRate("beer-sheva", "A", "office", 230.0, "Office Zone A"),
            "commercial": MunicipalRate("beer-sheva", "A", "commercial", 260.0, "Commerce Zone A"),
            "industrial": MunicipalRate("beer-sheva", "A", "industrial", 110.0, "Industry Zone A"),
        },
        "B": {
            "residential": MunicipalRate("beer-sheva", "B", "residential", 62.0, "Residential Zone B"),
            "warehouse": MunicipalRate("beer-sheva", "B", "warehouse", 70.0, "Warehouse Zone B"),
        },
    },
    "rishon-lezion": {
        "A": {
            "residential": MunicipalRate("rishon-lezion", "A", "residential", 86.0, "Residential Zone A"),
            "office": MunicipalRate("rishon-lezion", "A", "office", 285.0, "Office Zone A"),
            "commercial": MunicipalRate("rishon-lezion", "A", "commercial", 315.0, "Commerce Zone A"),
        },
        "B": {
            "residential": MunicipalRate("rishon-lezion", "B", "residential", 74.0, "Residential Zone B"),
            "warehouse": MunicipalRate("rishon-lezion", "B", "warehouse", 88.0, "Warehouse Zone B"),
        },
    },
    "petah-tikva": {
        "A": {
            "residential": MunicipalRate("petah-tikva", "A", "residential", 90.0, "Residential Zone A"),
            "office": MunicipalRate("petah-tikva", "A", "office", 310.0, "Office Zone A"),
            "commercial": MunicipalRate("petah-tikva", "A", "commercial", 340.0, "Commerce Zone A"),
            "warehouse": MunicipalRate("petah-tikva", "A", "warehouse", 100.0, "Warehouse Zone A"),
        }
    },
}

DISCOUNT_RULES: Dict[str, DiscountRule] = {
    "senior": DiscountRule(
        "senior",
        "Senior citizen / אזרח ותיק",
        0.30,
        max_area_sqm=100,
        requires_documents=("ID", "senior-citizen confirmation", "primary residence proof"),
        warning="Senior discounts depend on age, income, residence, and municipal implementation.",
    ),
    "disability": DiscountRule(
        "disability",
        "Disability / נכות",
        0.80,
        max_area_sqm=100,
        requires_documents=("disability approval", "ID", "primary residence proof"),
        warning="Disability discounts require specific official approval and may be capped.",
    ),
    "low_income": DiscountRule(
        "low_income",
        "Low income / הכנסה נמוכה",
        0.90,
        max_area_sqm=100,
        requires_documents=("income documents", "bank statements", "household declaration"),
        warning="Low-income discounts depend on annual tables and municipal discount committee review.",
    ),
    "new_immigrant": DiscountRule(
        "new_immigrant",
        "New immigrant / עולה חדש",
        0.90,
        max_area_sqm=100,
        max_months=12,
        requires_documents=("teudat oleh", "ID", "primary residence proof"),
        warning="New-immigrant discounts are time-limited and normally require formal application.",
    ),
    "soldier": DiscountRule(
        "soldier",
        "Soldier or national service / חייל או שירות לאומי",
        1.00,
        max_area_sqm=70,
        requires_documents=("service confirmation", "ID", "primary residence proof"),
        warning="Service-related discounts require current service confirmation and local processing.",
    ),
}

APPEAL_ISSUES: Dict[str, AppealIssue] = {
    "wrong_area": AppealIssue("wrong_area", "Taxable area is wrong", ("municipal measurement", "independent measurement", "floor plan", "photos"), "Correct the taxable sqm and recalculate charges."),
    "wrong_classification": AppealIssue("wrong_classification", "Property classification does not match actual use", ("photos", "business license", "lease", "invoices", "floor plan"), "Apply the classification that matches actual use."),
    "wrong_zone": AppealIssue("wrong_zone", "Wrong tariff zone", ("street table", "zone map", "municipal GIS screenshot"), "Apply the correct zone from the annual Arnona order."),
    "wrong_holder": AppealIssue("wrong_holder", "Wrong holder charged", ("lease", "sale agreement", "handover protocol", "ID/company details"), "Update holder and cancel charges outside the holding period."),
    "vacancy": AppealIssue("vacancy", "Vacant property exemption missing", ("photos", "utility readings", "inspection request", "lease termination"), "Apply vacant-property exemption if local criteria are met."),
    "discount_missing": AppealIssue("discount_missing", "Approved or eligible discount missing", ("eligibility certificate", "discount form", "income documents", "ID"), "Apply the discount from the permitted effective date."),
    "duplicate_billing": AppealIssue("duplicate_billing", "Duplicate billing for the same area", ("two bills", "account ledger", "floor plan", "municipal map"), "Cancel duplicate account and reverse duplicate charges."),
}

SAMPLE_PURCHASE_TAX_BRACKETS: Dict[str, List[Tuple[float, float]]] = {
    "single_home": [(1_978_745, 0.00), (2_347_040, 0.035), (6_055_070, 0.05), (20_183_565, 0.08), (math.inf, 0.10)],
    "replacement_home": [(1_978_745, 0.00), (2_347_040, 0.035), (6_055_070, 0.05), (20_183_565, 0.08), (math.inf, 0.10)],
    "additional_home": [(6_055_070, 0.08), (math.inf, 0.10)],
    "non_resident": [(6_055_070, 0.08), (math.inf, 0.10)],
    "commercial_asset": [(math.inf, 0.06)],
    "relief_category": [(math.inf, 0.005)],
}

MUNICIPALITY_ALIASES = {
    "tel aviv": "tel-aviv",
    "tel-aviv-yafo": "tel-aviv",
    "tlv": "tel-aviv",
    "תל אביב": "tel-aviv",
    "תל אביב-יפו": "tel-aviv",
    "jerusalem": "jerusalem",
    "ירושלים": "jerusalem",
    "haifa": "haifa",
    "חיפה": "haifa",
    "beer sheva": "beer-sheva",
    "beersheba": "beer-sheva",
    "באר שבע": "beer-sheva",
    "rishon lezion": "rishon-lezion",
    "ראשון לציון": "rishon-lezion",
    "petah tikva": "petah-tikva",
    "פתח תקווה": "petah-tikva",
}


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def round_money(value: float) -> float:
    return round(float(value) + 1e-9, 2)


def format_ils(value: float) -> str:
    return f"₪{round_money(value):,.2f}"


def parse_local_date(value: str) -> _dt.date:
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return _dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise AdvisorError("DATE_FORMAT", "Date must be DD/MM/YYYY or DD-MM-YYYY.", "date")


def normalize_municipality(value: str) -> str:
    key = value.strip().lower().replace("_", "-")
    return MUNICIPALITY_ALIASES.get(key, key)


def list_municipalities() -> List[str]:
    return sorted(SAMPLE_RATES)


def list_discounts() -> List[Dict[str, Any]]:
    return [_jsonable(rule) for rule in DISCOUNT_RULES.values()]


def get_rate(municipality: str, zone: str, usage: str) -> MunicipalRate:
    m = normalize_municipality(municipality)
    z = zone.strip().upper()
    u = usage.strip().lower().replace("-", "_")
    if m not in SAMPLE_RATES:
        raise AdvisorError("UNKNOWN_MUNICIPALITY", f"Municipality '{municipality}' is not in the sample table.", "municipality")
    if z not in SAMPLE_RATES[m]:
        raise AdvisorError("UNKNOWN_ZONE", f"Zone '{zone}' is not available for {m}.", "zone")
    if u not in SAMPLE_RATES[m][z]:
        raise AdvisorError("UNKNOWN_USAGE", f"Usage '{usage}' is not available for {m} zone {z}.", "usage")
    return SAMPLE_RATES[m][z][u]


def calculate_arnona(data: ArnonaInput | Mapping[str, Any]) -> AssessmentResult:
    if isinstance(data, Mapping):
        data = ArnonaInput(**data)
    if data.area_sqm <= 0:
        raise AdvisorError("INVALID_AREA", "Area must be positive.", "area_sqm")
    if data.months < 1 or data.months > 12:
        raise AdvisorError("INVALID_MONTHS", "Months must be from 1 to 12.", "months")
    rate = get_rate(data.municipality, data.zone, data.usage)
    annual_charge = data.area_sqm * rate.annual_rate_per_sqm
    period_charge = annual_charge * data.months / 12
    warnings = ["Sample rate used; verify against the current municipal Arnona order."]
    next_actions = [
        "Compare the classification, zone, area, and measurement method to the annual Arnona order.",
        "Check whether a statutory objection deadline appears on the bill.",
    ]
    discount_amount = 0.0
    discount_details: Dict[str, Any] | None = None
    if data.discount:
        discount_key = data.discount.strip().lower().replace("-", "_")
        if discount_key not in DISCOUNT_RULES:
            raise AdvisorError("UNKNOWN_DISCOUNT", f"Unknown discount '{data.discount}'.", "discount")
        rule = DISCOUNT_RULES[discount_key]
        eligible_area = min(data.area_sqm, rule.max_area_sqm) if rule.max_area_sqm else data.area_sqm
        eligible_months = data.discount_months if data.discount_months is not None else data.months
        if eligible_months < 0:
            raise AdvisorError("INVALID_DISCOUNT_MONTHS", "Discount months cannot be negative.", "discount_months")
        eligible_months = min(eligible_months, data.months)
        if rule.max_months is not None:
            eligible_months = min(eligible_months, rule.max_months)
        discount_base = eligible_area * rate.annual_rate_per_sqm * eligible_months / 12
        discount_amount = discount_base * rule.percent
        discount_details = {
            "key": rule.key,
            "label": rule.label,
            "percent": rule.percent,
            "eligible_area_sqm": eligible_area,
            "eligible_months": eligible_months,
            "required_documents": list(rule.requires_documents),
        }
        warnings.append(rule.warning)
        next_actions.append("Submit the official municipal discount form with supporting documents.")
    payable = period_charge - discount_amount
    details = {
        "municipality": rate.municipality,
        "usage": rate.usage,
        "zone": rate.zone,
        "area_sqm": float(data.area_sqm),
        "months": data.months,
        "annual_rate_per_sqm": rate.annual_rate_per_sqm,
        "annual_charge": round_money(annual_charge),
        "period_charge": round_money(period_charge),
        "discount_amount": round_money(discount_amount),
        "payable": round_money(payable),
        "rate_label": rate.label,
    }
    if discount_details:
        details["discount"] = discount_details
    return AssessmentResult(TaxType.ARNONA.value, Authority.MUNICIPALITY.value, payable, details=details, warnings=warnings, next_actions=next_actions)


async def calculate_arnona_async(data: ArnonaInput | Mapping[str, Any]) -> AssessmentResult:
    return await asyncio.to_thread(calculate_arnona, data)


def compare_home_office_scenarios(municipality: str, zone: str, total_area_sqm: float, business_area_sqm: float, business_usage: str = "office") -> AssessmentResult:
    if total_area_sqm <= 0:
        raise AdvisorError("INVALID_AREA", "Total area must be positive.", "total_area_sqm")
    if business_area_sqm < 0:
        raise AdvisorError("INVALID_AREA", "Business area cannot be negative.", "business_area_sqm")
    if business_area_sqm > total_area_sqm:
        raise AdvisorError("INVALID_AREA", "Business area cannot exceed total area.", "business_area_sqm")
    residential_rate = get_rate(municipality, zone, "residential")
    business_rate = get_rate(municipality, zone, business_usage)
    all_residential = total_area_sqm * residential_rate.annual_rate_per_sqm
    all_business = total_area_sqm * business_rate.annual_rate_per_sqm
    split = (total_area_sqm - business_area_sqm) * residential_rate.annual_rate_per_sqm + business_area_sqm * business_rate.annual_rate_per_sqm
    details = {
        "municipality": normalize_municipality(municipality),
        "zone": zone.strip().upper(),
        "total_area_sqm": total_area_sqm,
        "business_area_sqm": business_area_sqm,
        "residential_rate": residential_rate.annual_rate_per_sqm,
        "business_rate": business_rate.annual_rate_per_sqm,
        "all_residential": round_money(all_residential),
        "all_business": round_money(all_business),
        "split_residential_business": round_money(split),
        "potential_gap_all_business_vs_split": round_money(all_business - split),
    }
    return AssessmentResult(
        TaxType.ARNONA.value,
        Authority.MUNICIPALITY.value,
        split,
        details=details,
        warnings=["Scenario comparison only; mixed-use treatment depends on the municipal Arnona order and facts."],
        next_actions=["Prepare a marked floor plan and photos showing actual residential and business areas.", "Check whether the local order permits split classification."],
    )


async def compare_home_office_scenarios_async(*args: Any, **kwargs: Any) -> AssessmentResult:
    return await asyncio.to_thread(compare_home_office_scenarios, *args, **kwargs)


def marginal_tax(price: float, brackets: Sequence[Tuple[float, float]]) -> Tuple[float, List[Dict[str, float]]]:
    if price <= 0:
        raise AdvisorError("INVALID_PRICE", "Price must be positive.", "price")
    remaining = price
    lower = 0.0
    tax = 0.0
    rows: List[Dict[str, float]] = []
    for upper, rate in brackets:
        if remaining <= 0:
            break
        width = upper - lower if math.isfinite(upper) else remaining
        amount = min(remaining, width)
        row_tax = amount * rate
        rows.append({"from": round_money(lower), "to": round_money(upper) if math.isfinite(upper) else math.inf, "taxable_amount": round_money(amount), "rate": rate, "tax": round_money(row_tax)})
        tax += row_tax
        remaining -= amount
        lower = upper
    return round_money(tax), rows


def estimate_purchase_tax(price: float, buyer_profile: str = BuyerProfile.SINGLE_HOME.value, contract_date: str | None = None) -> AssessmentResult:
    if price <= 0:
        raise AdvisorError("INVALID_PRICE", "Price must be positive.", "price")
    profile = buyer_profile.strip().lower().replace("-", "_")
    if profile not in SAMPLE_PURCHASE_TAX_BRACKETS:
        raise AdvisorError("UNKNOWN_BUYER_PROFILE", f"Unknown buyer profile '{buyer_profile}'.", "buyer_profile")
    parsed_date = parse_local_date(contract_date) if contract_date else None
    tax, rows = marginal_tax(price, SAMPLE_PURCHASE_TAX_BRACKETS[profile])
    details = {
        "price": round_money(price),
        "buyer_profile": profile,
        "contract_date": parsed_date.strftime("%d/%m/%Y") if parsed_date else None,
        "estimated_tax": round_money(tax),
        "effective_rate": round(tax / price, 6),
        "brackets": rows,
    }
    actions = ["Verify current Israel Tax Authority brackets for the contract date.", "Confirm buyer family-unit status and existing property interests."]
    if profile == BuyerProfile.REPLACEMENT_HOME.value:
        actions.append("Calendar the deadline for selling the previous apartment.")
    return AssessmentResult(
        TaxType.PURCHASE_TAX.value,
        Authority.TAX_AUTHORITY.value,
        tax,
        details=details,
        warnings=["Sample brackets are not official. Verify current Israel Tax Authority brackets before filing."],
        next_actions=actions,
    )


async def estimate_purchase_tax_async(*args: Any, **kwargs: Any) -> AssessmentResult:
    return await asyncio.to_thread(estimate_purchase_tax, *args, **kwargs)


def estimate_betterment_levy(planning_uplift: float, ownership_share: float = 1.0, exemption: bool = False) -> AssessmentResult:
    if planning_uplift < 0:
        raise AdvisorError("INVALID_UPLIFT", "Planning uplift cannot be negative.", "planning_uplift")
    if ownership_share <= 0 or ownership_share > 1:
        raise AdvisorError("INVALID_SHARE", "Ownership share must be > 0 and <= 1.", "ownership_share")
    levy = 0.0 if exemption else planning_uplift * ownership_share * 0.5
    details = {"planning_uplift": round_money(planning_uplift), "ownership_share": ownership_share, "exemption_assumed": bool(exemption), "levy_rate": 0.5, "estimated_levy": round_money(levy)}
    warnings = ["A licensed appraiser should review any material betterment-levy assessment.", "Exemptions depend on strict statutory conditions and local committee facts."]
    return AssessmentResult(
        TaxType.BETTERMENT_LEVY.value,
        Authority.LOCAL_PLANNING_COMMITTEE.value,
        levy,
        details=details,
        warnings=warnings,
        next_actions=["Request the local committee appraiser report and plan references.", "Check deadline for counter-appraisal, review, or appeal."],
    )


async def estimate_betterment_levy_async(*args: Any, **kwargs: Any) -> AssessmentResult:
    return await asyncio.to_thread(estimate_betterment_levy, *args, **kwargs)


def assess_mas_rechush(property_kind: str, damage_type: str | None = None, incident_date: str | None = None) -> AssessmentResult:
    parsed_date = parse_local_date(incident_date) if incident_date else None
    normalized_damage = (damage_type or "").strip().lower().replace("-", "_")
    direct_damage = normalized_damage in {"war_direct", "hostile_act", "rocket", "security_event"}
    details = {"property_kind": property_kind, "damage_type": normalized_damage or None, "incident_date": parsed_date.strftime("%d/%m/%Y") if parsed_date else None, "ordinary_annual_tax_expected": False, "compensation_track_likely": direct_damage}
    if direct_damage:
        next_actions = ["Photograph damage before full repair when safe.", "Preserve invoices, ownership or tenancy proof, and official incident confirmations.", "Submit through the Israel Tax Authority Property Tax and Compensation Fund route."]
        warnings = ["Eligibility and compensation amount depend on official recognition, evidence, inspections, and regulations."]
    else:
        next_actions = ["Inspect the notice issuer and legal basis if a demand exists.", "Check whether the issue is actually Arnona, purchase tax, betterment levy, or collection debt."]
        warnings = ["Do not treat Mas Rechush as a routine annual homeowner tax without a current official notice."]
    return AssessmentResult(TaxType.MAS_RECHUSH.value, Authority.TAX_AUTHORITY.value, 0.0, details=details, warnings=warnings, next_actions=next_actions)


async def assess_mas_rechush_async(*args: Any, **kwargs: Any) -> AssessmentResult:
    return await asyncio.to_thread(assess_mas_rechush, *args, **kwargs)


def build_appeal_packet(municipality: str, property_number: str, issues: Iterable[str], facts: Optional[str] = None) -> Dict[str, Any]:
    issue_list = []
    evidence: List[str] = []
    fixes: List[str] = []
    for key in issues:
        normalized = key.strip().lower().replace("-", "_")
        if normalized not in APPEAL_ISSUES:
            raise AdvisorError("UNKNOWN_APPEAL_ISSUE", f"Unknown appeal issue '{key}'.", "issues")
        issue = APPEAL_ISSUES[normalized]
        issue_list.append({"key": issue.key, "label": issue.label})
        evidence.extend(issue.evidence)
        fixes.append(issue.requested_fix)
    return {
        "municipality": normalize_municipality(municipality),
        "property_number": property_number,
        "issues": issue_list,
        "facts": facts or "",
        "evidence_checklist": sorted(set(evidence)),
        "requested_fixes": fixes,
        "outline": ["Identify the assessed property and billing period.", "State each disputed field separately.", "Attach evidence and calculation impact.", "Request a written decision and corrected account ledger.", "Calendar objection or appeal deadline."],
    }


def classify_tax_question(text: str) -> Dict[str, Any]:
    lower = text.lower()
    scores = {
        TaxType.ARNONA.value: _count_terms(lower, text, ["arnona", "ארנונה", "municipal"]),
        TaxType.MAS_RECHUSH.value: _count_terms(lower, text, ["mas rechush", "מס רכוש", "rocket", "war damage", "פעולת איבה"]),
        TaxType.PURCHASE_TAX.value: _count_terms(lower, text, ["purchase tax", "מס רכישה", "buy", "רכישה"]),
        TaxType.BETTERMENT_LEVY.value: _count_terms(lower, text, ["betterment", "היטל השבחה", "plan", "תוכנית", "permit", "היתר"]),
        TaxType.LAND_APPRECIATION_TAX.value: _count_terms(lower, text, ["mas shevach", "מס שבח", "sale", "מכירה"]),
    }
    best = max(scores, key=scores.get)
    authority = {
        TaxType.ARNONA.value: Authority.MUNICIPALITY.value,
        TaxType.MAS_RECHUSH.value: Authority.TAX_AUTHORITY.value,
        TaxType.PURCHASE_TAX.value: Authority.TAX_AUTHORITY.value,
        TaxType.BETTERMENT_LEVY.value: Authority.LOCAL_PLANNING_COMMITTEE.value,
        TaxType.LAND_APPRECIATION_TAX.value: Authority.TAX_AUTHORITY.value,
    }[best]
    confidence = scores[best] / max(1, sum(scores.values()))
    if scores[best] == 0:
        best = TaxType.MUNICIPAL_FEE.value
        authority = Authority.UNKNOWN.value
        confidence = 0.0
    return {"tax_type": best, "authority": authority, "confidence": round(confidence, 3), "scores": scores}


def _count_terms(lower: str, original: str, terms: Sequence[str]) -> int:
    return sum(1 for term in terms if term in lower or term in original)


def validate_arnona_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = ["municipality", "area_sqm", "zone", "usage"]
    missing = [field for field in required if field not in payload or payload[field] in (None, "")]
    if missing:
        raise AdvisorError("MISSING_FIELD", f"Missing required field(s): {', '.join(missing)}", ",".join(missing))
    result = calculate_arnona(payload)
    return result.to_dict()


def to_json(data: Any, *, ensure_ascii: bool = False) -> str:
    return json.dumps(_jsonable(data), ensure_ascii=ensure_ascii, indent=2, sort_keys=True)



def create_case(tax_type: str, subject: str, taxpayer_type: str = "consumer", environment: str = "sandbox") -> Dict[str, Any]:
    """Create a deterministic local case descriptor for workflow chaining.

    The helper does not persist data or contact an authority. It returns a case_id that can be passed
    to get_case_next_steps or a downstream workflow system.
    """
    normalized_tax = tax_type.strip().lower().replace("-", "_")
    valid_tax_types = {item.value for item in TaxType}
    if normalized_tax not in valid_tax_types:
        raise AdvisorError("UNKNOWN_TAX_TYPE", f"Unknown tax type '{tax_type}'.", "tax_type")
    normalized_env = environment.strip().lower()
    if normalized_env not in {"sandbox", "production"}:
        raise AdvisorError("INVALID_ENVIRONMENT", "Environment must be sandbox or production.", "environment")
    clean_subject = " ".join(subject.strip().split())
    if not clean_subject:
        raise AdvisorError("MISSING_SUBJECT", "Subject is required.", "subject")
    seed = f"{normalized_tax}|{taxpayer_type.strip().lower()}|{clean_subject}".encode("utf-8")
    import hashlib

    digest = hashlib.sha256(seed).hexdigest()[:10].upper()
    case_id = f"PTA-{digest}"
    return {
        "case_id": case_id,
        "tax_type": normalized_tax,
        "subject": clean_subject,
        "taxpayer_type": taxpayer_type.strip().lower() or "consumer",
        "environment": normalized_env,
        "status": "created",
        "next_command": f"case-next-steps --case-id {case_id} --tax-type {normalized_tax}",
    }


def get_case_next_steps(case_id: str, tax_type: str) -> Dict[str, Any]:
    """Return workflow steps for a local case identifier."""
    clean_case_id = case_id.strip().upper()
    if not re_match_case_id(clean_case_id):
        raise AdvisorError("INVALID_CASE_ID", "Case id must look like PTA-XXXXXXXXXX.", "case_id")
    normalized_tax = tax_type.strip().lower().replace("-", "_")
    if normalized_tax == TaxType.ARNONA.value:
        steps = [
            "Collect the Arnona bill, annual municipal order, property sketch, and occupancy dates.",
            "Compare assessed area, classification, zone, holder, discounts, and vacant-property status.",
            "Prepare one evidence bundle per disputed field before filing an objection or service request.",
        ]
    elif normalized_tax == TaxType.MAS_RECHUSH.value:
        steps = [
            "Photograph damage safely, preserve repair invoices, and keep official incident confirmations.",
            "Check the Israel Tax Authority Property Tax and Compensation Fund route for the incident.",
            "Separate direct physical damage from ordinary insurance, business interruption, or municipal issues.",
        ]
    elif normalized_tax == TaxType.PURCHASE_TAX.value:
        steps = [
            "Verify buyer family-unit status and current Israel Tax Authority brackets for the contract date.",
            "Collect purchase agreement, identity details, declarations, and prior-property information.",
            "Calendar filing and payment deadlines with transaction counsel or tax adviser.",
        ]
    elif normalized_tax == TaxType.BETTERMENT_LEVY.value:
        steps = [
            "Request the local committee assessment, plan references, and determining date.",
            "Check realization event, ownership share, exemptions, and appraiser challenge deadlines.",
            "Compare planning uplift assumptions with an independent real-estate appraiser when material.",
        ]
    else:
        steps = [
            "Identify the issuing authority, statutory basis, deadline, and payment route.",
            "Separate factual disputes from exemption or hardship requests.",
            "Collect official notices, contracts, photographs, and correspondence before responding.",
        ]
    return {"case_id": clean_case_id, "tax_type": normalized_tax, "steps": steps}


def re_match_case_id(value: str) -> bool:
    import re

    return re.fullmatch(r"PTA-[A-F0-9]{10}", value) is not None


__all__ = [
    "AdvisorError", "ArnonaInput", "AssessmentResult", "Authority", "BuyerProfile", "TaxType", "Usage",
    "calculate_arnona", "calculate_arnona_async", "compare_home_office_scenarios",
    "compare_home_office_scenarios_async", "estimate_purchase_tax", "estimate_purchase_tax_async",
    "estimate_betterment_levy", "estimate_betterment_levy_async", "assess_mas_rechush",
    "assess_mas_rechush_async", "build_appeal_packet", "classify_tax_question", "format_ils",
    "get_rate", "list_discounts", "list_municipalities", "marginal_tax", "normalize_municipality",
    "parse_local_date", "round_money", "to_json", "validate_arnona_payload", "create_case",
    "get_case_next_steps", "SAMPLE_PURCHASE_TAX_BRACKETS",
]
