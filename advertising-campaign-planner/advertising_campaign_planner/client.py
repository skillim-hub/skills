"""Typed campaign-planning helpers for Israeli advertising campaigns."""

from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import json
import math
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence


SUPPORTED_LANGUAGES = {"he", "ar", "ru", "en"}
CURRENT_VAT_RATE = 0.18
CURRENT_VAT_EFFECTIVE_DATE = "01/01/2025"
LANGUAGE_NAMES = {"he": "Hebrew", "ar": "Arabic", "ru": "Russian", "en": "English"}
REGULATED_FLAGS = {
    "health",
    "finance",
    "tax_advice",
    "minors",
    "alcohol",
    "lottery",
    "environmental",
    "real_estate",
    "employment",
    "cosmetics",
}
SENSITIVE_SECTORS = {
    "health",
    "medical",
    "clinic",
    "finance",
    "insurance",
    "investment",
    "loan",
    "tax",
    "legal",
    "real_estate",
    "education",
    "cosmetics",
    "alcohol",
}


class Goal(str, Enum):
    LEADS = "leads"
    BOOKINGS = "bookings"
    SALES = "sales"
    CALLS = "calls"
    STORE_VISITS = "store_visits"
    AWARENESS = "awareness"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    field: str
    severity: str = "error"


@dataclass(frozen=True)
class ROIEstimate:
    spend: float
    clicks: int
    conversions: int
    conversion_rate: float
    cost_per_click: float
    cost_per_conversion: float
    gross_profit: float
    roi: float
    break_even_conversions: int
    break_even_cpa: float
    interpretation: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class ChannelAllocation:
    channel: str
    budget: float
    percentage: int
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class CampaignRequest:
    business: str
    goal: Goal | str
    monthly_budget: float
    languages: Sequence[str] = field(default_factory=lambda: ["he"])
    cities: Sequence[str] = field(default_factory=list)
    sector: str = "general"
    audience: str = ""
    offer: str = ""
    avg_order_value: Optional[float] = None
    gross_margin: Optional[float] = None
    regulated_flags: Sequence[str] = field(default_factory=list)
    has_website: bool = True
    uses_remarketing: bool = False
    uses_direct_messages: bool = False
    service_languages: Optional[Sequence[str]] = None
    date: str = "03/06/2026"
    environment: str = "sandbox"

    def normalized_goal(self) -> Goal:
        if isinstance(self.goal, Goal):
            return self.goal
        return Goal(str(self.goal))

    def normalized_languages(self) -> List[str]:
        return [str(lang).lower() for lang in self.languages]

    def normalized_service_languages(self) -> List[str]:
        if self.service_languages is None:
            return self.normalized_languages()
        return [str(lang).lower() for lang in self.service_languages]


@dataclass
class CampaignPlan:
    campaign_summary: Dict[str, Any]
    assumptions: List[str]
    audience_segments: List[Dict[str, Any]]
    language_plan: List[Dict[str, Any]]
    channel_mix: List[ChannelAllocation]
    creative_brief: Dict[str, Any]
    compliance_flags: List[ValidationIssue]
    measurement_plan: List[str]
    roi_estimate: Optional[ROIEstimate]
    launch_checklist: List[str]
    optimization_plan_14_days: List[str]

    def to_dict(self) -> Dict[str, Any]:
        data = dataclasses.asdict(self)
        data["channel_mix"] = [item.to_dict() for item in self.channel_mix]
        data["compliance_flags"] = [dataclasses.asdict(item) for item in self.compliance_flags]
        data["roi_estimate"] = None if self.roi_estimate is None else self.roi_estimate.to_dict()
        return data

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


class CampaignPlanner:
    """Create campaign plans and ROI estimates for Israeli advertising contexts."""

    def validate(self, request: CampaignRequest) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        if not request.business or len(request.business.strip()) < 2:
            issues.append(ValidationIssue("MISSING_BUSINESS", "Business name/type is required.", "business"))
        try:
            request.normalized_goal()
        except ValueError:
            issues.append(ValidationIssue("INVALID_GOAL", f"Goal must be one of: {', '.join(g.value for g in Goal)}.", "goal"))
        if request.monthly_budget <= 0:
            issues.append(ValidationIssue("INVALID_BUDGET", "Monthly budget must be greater than ₪0.", "monthly_budget"))
        if request.monthly_budget and request.monthly_budget < 1000:
            issues.append(ValidationIssue("TINY_BUDGET_FRAGMENTATION", "Budget below ₪1,000 should not be fragmented across multiple paid channels.", "monthly_budget", "warning"))
        for lang in request.normalized_languages():
            if lang not in SUPPORTED_LANGUAGES:
                issues.append(ValidationIssue("UNSUPPORTED_LANGUAGE", "Supported language codes are he, ar, ru, en.", "languages"))
        if request.gross_margin is not None and not (0 <= request.gross_margin <= 1):
            issues.append(ValidationIssue("INVALID_MARGIN", "Gross margin must be a decimal between 0 and 1.", "gross_margin"))
        if request.avg_order_value is not None and request.avg_order_value <= 0:
            issues.append(ValidationIssue("INVALID_AOV", "Average order value must be greater than ₪0.", "avg_order_value"))
        for flag in sorted(set(request.regulated_flags) - REGULATED_FLAGS):
            issues.append(ValidationIssue("UNKNOWN_REGULATED_FLAG", f"Unknown regulated flag: {flag}.", "regulated_flags", "warning"))
        if self._requires_regulated_review(request):
            issues.append(ValidationIssue("REGULATED_REVIEW_REQUIRED", "Regulated or sensitive advertising requires manual compliance review and claim substantiation.", "regulated_flags", "warning"))
        if request.uses_direct_messages:
            issues.append(ValidationIssue("DIRECT_MARKETING_CONSENT_REQUIRED", "Confirm opt-in, sender identity, and removal mechanism before email/SMS/WhatsApp marketing.", "uses_direct_messages", "warning"))
        if request.uses_remarketing:
            issues.append(ValidationIssue("PRIVACY_NOTICE_REQUIRED", "Verify privacy notice, audience source, consent/legal basis, and retention before remarketing.", "uses_remarketing", "warning"))
        missing_service = set(request.normalized_languages()) - set(request.normalized_service_languages())
        if missing_service:
            issues.append(ValidationIssue("NO_SERVICE_LANGUAGE", f"Do not advertise in languages that cannot be served professionally: {', '.join(sorted(missing_service))}.", "service_languages", "warning"))
        risky_offer = request.offer.lower()
        if any(term in risky_offer for term in ["guaranteed", "guarantee", "מובטח", "בטוח", "cure", "ריפוי"]):
            issues.append(ValidationIssue("UNSUPPORTED_CLAIM_RISK", "Avoid guarantees or treatment/result promises unless properly substantiated and permitted.", "offer", "warning"))
        if any(term in risky_offer for term in ["today only", "רק היום"]) and not any(char.isdigit() for char in risky_offer):
            issues.append(ValidationIssue("MATERIAL_TERMS_REQUIRED", "Urgency and discount claims need true dates and material conditions.", "offer", "warning"))
        return issues

    def plan(self, request: CampaignRequest) -> CampaignPlan:
        issues = self.validate(request)
        goal = request.normalized_goal() if not any(i.code == "INVALID_GOAL" for i in issues) else Goal.LEADS
        plan_id = create_plan_id(request)
        return CampaignPlan(
            campaign_summary={
                "plan_id": plan_id,
                "business": request.business,
                "goal": goal.value,
                "geography": list(request.cities) or ["Israel nationwide"],
                "budget": self.format_ils(request.monthly_budget),
                "date": request.date,
                "environment": request.environment,
                "risk_level": self._risk_level(request, issues),
            },
            assumptions=self._build_assumptions(request),
            audience_segments=self._audience_segments(request, goal),
            language_plan=self._language_plan(request),
            channel_mix=self.allocate_budget(goal, request.monthly_budget, request.sector, request.has_website),
            creative_brief=self._creative_brief(request, goal),
            compliance_flags=issues + self._compliance_actions(request),
            measurement_plan=self._measurement_plan(goal, request),
            roi_estimate=self._directional_roi(request, goal),
            launch_checklist=self._launch_checklist(request),
            optimization_plan_14_days=[
                "Day 0: verify conversion tracking, phone links, WhatsApp links, forms, UTM parameters, and budget caps.",
                "Day 3: review search terms, comments, disapprovals, landing-page errors, and spend pacing.",
                "Day 7: compare CPL/CPA with break-even economics and pause the weakest audience/keyword/creative.",
                "Day 14: scale by 15%–30%, hold, pivot the offer, or stop according to qualified lead and gross-profit data.",
            ],
        )

    async def aplan(self, request: CampaignRequest) -> CampaignPlan:
        await asyncio.sleep(0)
        return self.plan(request)

    def estimate_roi(self, *, spend: float, clicks: int, conversions: int, avg_order_value: float, gross_margin: float) -> ROIEstimate:
        if spend <= 0:
            raise ValueError("spend must be greater than 0")
        if clicks < 0 or conversions < 0:
            raise ValueError("clicks and conversions must be non-negative")
        if avg_order_value <= 0:
            raise ValueError("avg_order_value must be greater than 0")
        if not 0 <= gross_margin <= 1:
            raise ValueError("gross_margin must be between 0 and 1")
        conversion_rate = conversions / clicks if clicks else 0.0
        cpc = spend / clicks if clicks else 0.0
        cpa = spend / conversions if conversions else math.inf
        gross_profit = conversions * avg_order_value * gross_margin
        roi = (gross_profit - spend) / spend
        break_even_cpa = avg_order_value * gross_margin
        break_even_conversions = math.ceil(spend / break_even_cpa) if break_even_cpa else math.inf
        return ROIEstimate(
            spend=round(spend, 2),
            clicks=int(clicks),
            conversions=int(conversions),
            conversion_rate=round(conversion_rate, 4),
            cost_per_click=round(cpc, 2),
            cost_per_conversion=round(cpa, 2) if math.isfinite(cpa) else math.inf,
            gross_profit=round(gross_profit, 2),
            roi=round(roi, 4),
            break_even_conversions=int(break_even_conversions) if math.isfinite(break_even_conversions) else math.inf,
            break_even_cpa=round(break_even_cpa, 2),
            interpretation=self._interpret_roi(roi, cpa, break_even_cpa),
        )

    def allocate_budget(self, goal: Goal, monthly_budget: float, sector: str = "general", has_website: bool = True) -> List[ChannelAllocation]:
        if monthly_budget <= 0:
            raise ValueError("monthly_budget must be greater than 0")
        sector_l = sector.lower()
        if monthly_budget < 1000:
            split = [
                ("Primary high-intent channel", 80, "Avoid budget fragmentation; focus on search/calls or one lead form."),
                ("Tracking and follow-up", 20, "Use manual CRM, phone/WhatsApp tracking, and simple creative."),
            ]
        elif goal in {Goal.CALLS, Goal.LEADS, Goal.BOOKINGS} and not has_website:
            split = [
                ("Google Search or local intent", 60, "Capture active demand with call/WhatsApp extensions or lead form."),
                ("Platform lead form", 25, "Use only with clear privacy and consent text."),
                ("Creative/testing", 15, "Test two offer angles and one proof-led variant."),
            ]
        elif goal in {Goal.CALLS, Goal.LEADS, Goal.BOOKINGS}:
            split = [
                ("Google Search", 55, "Prioritize active local demand."),
                ("Social prospecting", 20, "Test problem-aware audiences and proof-led creative."),
                ("Retargeting", 15, "Re-engage visitors after privacy review."),
                ("Creative/testing", 10, "Refresh ad copy, landing hero, and testimonials."),
            ]
        elif goal == Goal.SALES:
            split = [
                ("Search/catalog", 35, "Capture product and brand demand."),
                ("Social prospecting", 35, "Test visual product angles and offers."),
                ("Retargeting", 20, "Recover visitors and cart/product viewers after privacy review."),
                ("Creative/testing", 10, "Test bundles, proof, and user-generated-style assets."),
            ]
        elif goal == Goal.STORE_VISITS:
            split = [
                ("Local search/maps", 45, "Capture nearby demand and opening-hours intent."),
                ("Local social reach", 35, "Build awareness in the service radius."),
                ("Offer testing", 10, "Test coupon or booking incentive."),
                ("Creative/testing", 10, "Test local proof and location assets."),
            ]
        else:
            split = [
                ("Social/video awareness", 50, "Create demand with broad creative testing."),
                ("Search capture", 20, "Capture branded and category demand."),
                ("Retargeting", 15, "Re-engage visitors after privacy review."),
                ("Creative/testing", 15, "Test message-market fit."),
            ]
        if any(token in sector_l for token in SENSITIVE_SECTORS):
            split = [(name, pct, rationale + " Add manual compliance review.") for name, pct, rationale in split]
        return [ChannelAllocation(channel=name, budget=round(monthly_budget * pct / 100, 2), percentage=pct, rationale=rationale) for name, pct, rationale in split]

    @staticmethod
    def format_ils(amount: float) -> str:
        return f"₪{amount:,.0f}"

    def _directional_roi(self, request: CampaignRequest, goal: Goal) -> Optional[ROIEstimate]:
        if request.avg_order_value is None or request.gross_margin is None or request.monthly_budget <= 0:
            return None
        cpc = 4.5 if goal in {Goal.SALES, Goal.AWARENESS} else 6.0
        conversion_rate = 0.025 if goal == Goal.SALES else 0.05
        if request.monthly_budget < 1500:
            conversion_rate *= 0.75
        clicks = max(0, int(request.monthly_budget / cpc))
        conversions = max(0, int(clicks * conversion_rate))
        return self.estimate_roi(
            spend=request.monthly_budget,
            clicks=clicks,
            conversions=conversions,
            avg_order_value=request.avg_order_value,
            gross_margin=request.gross_margin,
        )

    def _build_assumptions(self, request: CampaignRequest) -> List[str]:
        assumptions = []
        if not request.cities:
            assumptions.append("Geography treated as nationwide Israel because no city or region was provided.")
        if request.avg_order_value is None:
            assumptions.append("Average order value was not provided; ROI is directional and should use scenario estimates.")
        if request.gross_margin is None:
            assumptions.append("Gross margin was not provided; profitability cannot be confirmed from revenue alone.")
        if not request.audience:
            assumptions.append("Audience segments are inferred from business type and goal.")
        if request.monthly_budget < 2000:
            assumptions.append("Budget is low; use one primary channel before adding retargeting or multilingual splits.")
        return assumptions or ["Inputs are sufficient for an initial planning estimate; verify with live campaign data."]

    def _audience_segments(self, request: CampaignRequest, goal: Goal) -> List[Dict[str, Any]]:
        business = request.business.lower()
        if any(x in business for x in ["account", "tax", "רואה חשבון"]):
            return [
                {"name": "New self-employed workers", "need": "Open files and avoid reporting mistakes", "message_angle": "Start correctly with a clear checklist"},
                {"name": "Growing small businesses", "need": "Monthly reporting and tax planning", "message_angle": "Predictable service and professional availability"},
                {"name": "Russian-speaking business owners", "need": "Understand tax obligations in a comfortable language", "message_angle": "Professional service in Russian and Hebrew"},
            ]
        if any(x in business for x in ["clinic", "dental", "health", "מרפאה", "שיניים"]):
            return [
                {"name": "Local patients comparing providers", "need": "Trust, availability, credentials, and clear process", "message_angle": "Book a consultation with transparent next steps"},
                {"name": "Families in the service area", "need": "Accessible appointment times and reassurance", "message_angle": "Professional care close to home"},
            ]
        return [
            {"name": "High-intent local buyers", "need": "Find a reliable local provider", "message_angle": "Clear offer, location, proof, and immediate CTA"},
            {"name": "Comparison shoppers", "need": "Understand value, terms, and trust signals", "message_angle": "Transparent price conditions and customer proof"},
            {"name": "Retargeting audience", "need": "Resolve hesitation after visiting or engaging", "message_angle": "Reminder with proof, availability, and low-friction next step"},
        ]

    def _language_plan(self, request: CampaignRequest) -> List[Dict[str, Any]]:
        guidance = {
            "he": "Use direct Israeli Hebrew, clear offer terms, local proof, and right-to-left landing-page QA.",
            "ar": "Use native Arabic copy, region-aware service details, and Arabic-capable follow-up.",
            "ru": "Use natural Russian copy, avoid literal Hebrew phrasing, and route leads to Russian-capable service.",
            "en": "Use English for tourists, expats, B2B, or international audiences while keeping Israeli disclosure requirements.",
        }
        return [{"language": lang, "name": LANGUAGE_NAMES.get(lang, lang), "guidance": guidance.get(lang, "Unsupported language; remove or validate before launch.")} for lang in request.normalized_languages()]

    def _creative_brief(self, request: CampaignRequest, goal: Goal) -> Dict[str, Any]:
        cta = {
            Goal.LEADS: "Leave details",
            Goal.BOOKINGS: "Book a consultation",
            Goal.SALES: "Buy now",
            Goal.CALLS: "Call now",
            Goal.STORE_VISITS: "Navigate to store",
            Goal.AWARENESS: "Learn more",
        }[goal]
        return {
            "core_message": request.offer or "Use a clear local offer with proof, availability, and material conditions.",
            "primary_cta": cta,
            "variants": [
                "Problem-solution angle with local context.",
                "Proof-led angle using testimonials, credentials, or before/after only when lawful and substantiated.",
                "Offer-led angle with dates, VAT/delivery terms, and limitations shown near the CTA.",
            ],
            "localization": "Create separate copy checks for Hebrew, Arabic, Russian, and English rather than literal translation.",
        }

    def _measurement_plan(self, goal: Goal, request: CampaignRequest) -> List[str]:
        items = [
            "Use UTM parameters for every ad and language variant.",
            "Record source, campaign, language, city, and offer in CRM or a tracking sheet.",
            "Compare platform conversions with actual qualified leads, bookings, calls, or orders.",
        ]
        if goal in {Goal.LEADS, Goal.BOOKINGS, Goal.CALLS}:
            items += ["Track form submissions, phone clicks, answered calls, WhatsApp starts, appointment bookings, and qualified lead rate.", "Calculate CPL, qualified CPL, appointment rate, close rate, and break-even CPL."]
        elif goal == Goal.SALES:
            items += ["Track gross-profit ROAS, CPA, new customer rate, repeat purchase, refunds, shipping issues, and cancellations.", "Use gross profit rather than revenue for ROI decisions."]
        elif goal == Goal.STORE_VISITS:
            items += ["Track coupon redemptions, direction clicks, calls, point-of-sale campaign code, and visit-to-purchase rate."]
        else:
            items += ["Track reach, frequency, engaged visits, brand search lift proxy, and assisted conversions; avoid treating awareness metrics as sales."]
        return items

    def _launch_checklist(self, request: CampaignRequest) -> List[str]:
        checklist = [
            "Confirm business identity, service area, landing URL, phone, WhatsApp, and opening hours.",
            "Verify offer terms, dates, inventory, warranty, cancellation, delivery, and VAT treatment; use 18% VAT from 01/01/2025 unless a lawful exemption or zero-rate applies.",
            "Add privacy notice to any lead form or tracking-heavy funnel.",
            "Check accessibility basics: labels, contrast, keyboard navigation, captions, alt text, RTL layout.",
            "Prepare negative keywords, exclusions, and comment/message moderation.",
            "Define stop-loss thresholds for CPL/CPA, conversion rate, and lead quality.",
        ]
        if not request.has_website:
            checklist.append("Use platform lead forms or WhatsApp only with consent language and manual lead tracking.")
        if request.uses_direct_messages:
            checklist.append("Verify direct-marketing opt-in and removal mechanism before sending messages.")
        if request.uses_remarketing:
            checklist.append("Verify remarketing audience source, privacy notice, and retention before activation.")
        return checklist

    def _compliance_actions(self, request: CampaignRequest) -> List[ValidationIssue]:
        actions = [
            ValidationIssue("ACCESSIBILITY_CHECK_REQUIRED", "Check landing page, form, video, and document accessibility before launch.", "landing_page", "warning"),
            ValidationIssue("CONSUMER_TERMS_REQUIRED", "Show material offer terms, price conditions, VAT/delivery where relevant, and cancellation/warranty details.", "offer", "warning"),
        ]
        flags = set(request.regulated_flags)
        if "tax_advice" in flags:
            actions.append(ValidationIssue("TAX_CLAIM_REVIEW", "Do not guarantee tax savings or imply Israel Tax Authority endorsement.", "regulated_flags", "warning"))
        if "health" in flags or "cosmetics" in flags:
            actions.append(ValidationIssue("HEALTH_CLAIM_REVIEW", "Substantiate medical, cosmetic, supplement, before/after, and outcome claims.", "regulated_flags", "warning"))
        if "finance" in flags:
            actions.append(ValidationIssue("FINANCE_CLAIM_REVIEW", "Review licensing, risk disclosure, fees, suitability, and guarantees.", "regulated_flags", "warning"))
        if "minors" in flags:
            actions.append(ValidationIssue("MINORS_REVIEW", "Avoid manipulative child-directed targeting and verify parental consent needs.", "regulated_flags", "warning"))
        if "environmental" in flags:
            actions.append(ValidationIssue("ENVIRONMENTAL_CLAIM_REVIEW", "Substantiate green, natural, organic, eco, and sustainability claims.", "regulated_flags", "warning"))
        if "lottery" in flags:
            actions.append(ValidationIssue("PRIZE_PROMOTION_REVIEW", "Review chance-based promotion mechanics, eligibility, rules, and permit needs.", "regulated_flags", "warning"))
        return actions

    def _requires_regulated_review(self, request: CampaignRequest) -> bool:
        return bool(set(request.regulated_flags) & REGULATED_FLAGS) or any(token in request.sector.lower() for token in SENSITIVE_SECTORS)

    @staticmethod
    def _risk_level(request: CampaignRequest, issues: Sequence[ValidationIssue]) -> str:
        if any(i.code in {"INVALID_BUDGET", "INVALID_MARGIN", "UNSUPPORTED_LANGUAGE"} for i in issues):
            return "blocked_until_fixed"
        warning_count = sum(1 for i in issues if i.severity == "warning")
        if warning_count >= 3 or any(flag in request.regulated_flags for flag in ["health", "finance", "minors", "alcohol", "lottery"]):
            return "high"
        if warning_count:
            return "medium"
        return "low"

    @staticmethod
    def _interpret_roi(roi: float, cpa: float, break_even_cpa: float) -> str:
        pct = round(roi * 100, 1)
        if roi > 0.25:
            return f"Estimated gross-profit ROI is {pct}%; verify attribution, refunds, and marginal CPA before scaling."
        if roi >= 0:
            return f"Estimated gross-profit ROI is {pct}%; keep testing but monitor lead quality and cash flow."
        if math.isfinite(cpa) and cpa > break_even_cpa:
            return f"Estimated gross-profit ROI is {pct}%; CPA is above break-even and needs lower cost or higher conversion value."
        return f"Estimated gross-profit ROI is {pct}%; review assumptions before launch."


def create_plan_id(request: CampaignRequest) -> str:
    payload = {
        "business": request.business,
        "goal": str(request.goal),
        "budget": request.monthly_budget,
        "cities": list(request.cities),
        "languages": list(request.languages),
        "date": request.date,
        "environment": request.environment,
    }
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    return f"plan_{digest}"


def campaign_request_from_mapping(data: Mapping[str, Any]) -> CampaignRequest:
    city_value = data.get("cities", data.get("city", []))
    cities = [city_value] if isinstance(city_value, str) else list(city_value or [])
    language_value = data.get("languages", data.get("language", ["he"]))
    languages = [language_value] if isinstance(language_value, str) else list(language_value or ["he"])
    return CampaignRequest(
        business=str(data.get("business", "")).strip(),
        goal=data.get("goal", Goal.LEADS.value),
        monthly_budget=float(data.get("monthly_budget", data.get("budget", 0))),
        languages=languages,
        cities=cities,
        sector=str(data.get("sector", "general")),
        audience=str(data.get("audience", "")),
        offer=str(data.get("offer", "")),
        avg_order_value=float(data["avg_order_value"]) if data.get("avg_order_value") is not None else None,
        gross_margin=float(data["gross_margin"]) if data.get("gross_margin") is not None else None,
        regulated_flags=list(data.get("regulated_flags", [])),
        has_website=bool(data.get("has_website", True)),
        uses_remarketing=bool(data.get("uses_remarketing", False)),
        uses_direct_messages=bool(data.get("uses_direct_messages", False)),
        service_languages=data.get("service_languages"),
        date=str(data.get("date", "03/06/2026")),
        environment=str(data.get("environment", "sandbox")),
    )


def save_plan(plan: CampaignPlan, state_file: str | Path) -> str:
    path = Path(state_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    data: Dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    payload = plan.to_dict()
    plan_id = str(payload["campaign_summary"]["plan_id"])
    data[plan_id] = payload
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan_id


def load_plan(plan_id: str, state_file: str | Path) -> Dict[str, Any]:
    path = Path(state_file)
    if not path.exists():
        raise FileNotFoundError(f"State file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if plan_id not in data:
        raise KeyError(f"Plan id not found: {plan_id}")
    return data[plan_id]


__all__ = [
    "CampaignPlanner",
    "CampaignPlan",
    "CampaignRequest",
    "ChannelAllocation",
    "Goal",
    "ROIEstimate",
    "SUPPORTED_LANGUAGES",
    "CURRENT_VAT_RATE",
    "CURRENT_VAT_EFFECTIVE_DATE",
    "ValidationIssue",
    "campaign_request_from_mapping",
    "create_plan_id",
    "save_plan",
    "load_plan",
]
