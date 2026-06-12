"""Offline-first helper for Israeli influencer collaboration workflows.

The module provides typed data structures, scoring utilities, Hebrew outreach
generation, disclosure checks, campaign planning, and performance summaries.
It is intentionally local and deterministic. External platform APIs can be
connected by wrapping the import/export methods.
"""

from __future__ import annotations

import asyncio
import csv
import json
import math
import re
import statistics
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple



DEFAULT_ISRAEL_VAT_RATE = 0.18
DEFAULT_ISRAEL_VAT_EFFECTIVE_DATE = date(2025, 1, 1)

class MarketSegment(str, Enum):
    """Common Israeli collaboration segments."""

    FOOD = "food"
    BEAUTY = "beauty"
    FASHION = "fashion"
    PARENTING = "parenting"
    FITNESS = "fitness"
    TECH = "tech"
    TRAVEL = "travel"
    FINANCE = "finance"
    LOCAL_SERVICES = "local_services"
    GENERAL = "general"


class Platform(str, Enum):
    """Supported social platforms."""

    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    BLOG = "blog"
    OTHER = "other"


class CollaborationGoal(str, Enum):
    """Supported campaign objectives."""

    AWARENESS = "awareness"
    LEADS = "leads"
    SALES = "sales"
    FOOT_TRAFFIC = "foot_traffic"
    CONTENT_REUSE = "content_reuse"


@dataclass(frozen=True)
class InfluencerProfile:
    """Profile data required for scoring and outreach."""

    handle: str
    display_name: str
    platform: Platform
    niche: str
    followers: int
    avg_views: int
    avg_likes: int
    avg_comments: int
    location: str = "Israel"
    audience_israel_pct: float = 0.75
    audience_age_min: int = 18
    audience_age_max: int = 54
    contact_email: Optional[str] = None
    past_brand_conflicts: Sequence[str] = field(default_factory=tuple)
    notes: str = ""


@dataclass(frozen=True)
class CampaignBrief:
    """Campaign inputs used for planning, scoring, and templates."""

    business_name: str
    product_or_service: str
    goal: CollaborationGoal
    target_locations: Sequence[str]
    target_segments: Sequence[MarketSegment]
    budget_ils: float
    start_date: date
    end_date: date
    required_disclosure: str = "פרסומת"
    usage_rights_days: int = 30
    deliverables: Sequence[str] = field(default_factory=lambda: ("story", "reel"))
    coupon_code: Optional[str] = None


@dataclass(frozen=True)
class ScoreBreakdown:
    """Normalized score result."""

    handle: str
    total_score: float
    fit_score: float
    engagement_score: float
    israel_relevance_score: float
    budget_score: float
    risk_score: float
    recommendation: str
    reasons: Sequence[str]


@dataclass(frozen=True)
class OutreachMessage:
    """Generated outreach copy."""

    subject: str
    body: str
    language: str
    disclosure_line: str
    follow_up_body: str


@dataclass(frozen=True)
class CampaignMetric:
    """Performance record for a single creator or post."""

    handle: str
    spend_ils: float
    impressions: int
    views: int
    clicks: int
    leads: int
    sales: int
    revenue_ils: float
    date_reported: date


@dataclass(frozen=True)
class CampaignSummary:
    """Aggregated campaign performance."""

    spend_ils: float
    impressions: int
    views: int
    clicks: int
    leads: int
    sales: int
    revenue_ils: float
    cpm_ils: float
    cpc_ils: float
    cpl_ils: float
    cost_per_sale_ils: float
    roas: float
    conversion_rate: float
    recommendations: Sequence[str]


def normalize_handle(value: str) -> str:
    """Return a clean handle without platform prefixes."""
    cleaned = value.strip()
    cleaned = re.sub(r"^https?://(www\.)?", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^(instagram\.com|tiktok\.com|youtube\.com|facebook\.com|linkedin\.com)/", "", cleaned, flags=re.I)
    cleaned = cleaned.strip("/ ")
    cleaned = cleaned.lstrip("@")
    if not cleaned:
        raise ValueError("handle must not be empty")
    return cleaned


def safe_divide(numerator: float, denominator: float) -> float:
    """Divide safely and return zero for empty denominators."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """Clamp a numeric score."""
    return max(low, min(high, value))


def detect_market_segment(text: str) -> MarketSegment:
    """Detect a likely market segment from Hebrew or English text."""
    t = text.lower()
    rules = {
        MarketSegment.FOOD: ["food", "restaurant", "coffee", "cafe", "מסעד", "אוכל", "קפה", "מאפ"],
        MarketSegment.BEAUTY: ["beauty", "makeup", "cosmetic", "טיפוח", "איפור", "קוסמט"],
        MarketSegment.FASHION: ["fashion", "style", "clothes", "אופנה", "סטייל", "ביגוד"],
        MarketSegment.PARENTING: ["parent", "mom", "dad", "kids", "הורים", "ילדים", "אמהות", "אבא"],
        MarketSegment.FITNESS: ["fitness", "gym", "sport", "כושר", "ספורט", "פילאטיס", "יוגה"],
        MarketSegment.TECH: ["tech", "startup", "software", "טכנולוג", "תוכנה", "סטארט"],
        MarketSegment.TRAVEL: ["travel", "hotel", "tour", "טיול", "מלון", "חופשה", "תייר"],
        MarketSegment.FINANCE: ["finance", "money", "tax", "כסף", "פיננס", "מס", "חשבונ"],
        MarketSegment.LOCAL_SERVICES: ["clinic", "law", "repair", "service", "קליניקה", "עורך דין", "תיקון", "שירות"],
    }
    for segment, keywords in rules.items():
        if any(keyword in t for keyword in keywords):
            return segment
    return MarketSegment.GENERAL


def engagement_rate(profile: InfluencerProfile) -> float:
    """Calculate engagement rate based on average likes and comments."""
    return safe_divide(profile.avg_likes + profile.avg_comments, profile.followers)


def estimated_reach(profile: InfluencerProfile) -> int:
    """Estimate practical local reach for a creator."""
    reach_source = profile.avg_views if profile.avg_views > 0 else profile.followers * 0.35
    return int(round(reach_source * profile.audience_israel_pct))


def estimate_creator_fee_ils(profile: InfluencerProfile, deliverables: Sequence[str] | None = None) -> float:
    """Estimate a planning fee in new Israeli shekels.

    The estimate is not a market quote. Use it to create budget bands before
    negotiation.
    """
    deliverables = tuple(deliverables or ("story", "reel"))
    reach = estimated_reach(profile)
    base = max(350.0, reach / 1000 * 70)
    platform_multiplier = {
        Platform.INSTAGRAM: 1.0,
        Platform.TIKTOK: 0.9,
        Platform.YOUTUBE: 1.4,
        Platform.FACEBOOK: 0.75,
        Platform.LINKEDIN: 1.25,
        Platform.BLOG: 1.1,
        Platform.OTHER: 0.8,
    }[profile.platform]
    deliverable_multiplier = 1 + max(0, len(deliverables) - 1) * 0.35
    engagement_multiplier = 1 + min(0.5, engagement_rate(profile) * 5)
    return round(base * platform_multiplier * deliverable_multiplier * engagement_multiplier, 2)


def validate_profile(profile: InfluencerProfile) -> List[str]:
    """Return validation errors for profile data."""
    errors: List[str] = []
    try:
        normalize_handle(profile.handle)
    except ValueError as exc:
        errors.append(str(exc))
    if profile.followers < 0:
        errors.append("followers must be non-negative")
    if profile.avg_views < 0 or profile.avg_likes < 0 or profile.avg_comments < 0:
        errors.append("metrics must be non-negative")
    if not 0 <= profile.audience_israel_pct <= 1:
        errors.append("audience_israel_pct must be between 0 and 1")
    if profile.audience_age_min < 0 or profile.audience_age_max < profile.audience_age_min:
        errors.append("audience age range is invalid")
    return errors


def validate_campaign_brief(brief: CampaignBrief) -> List[str]:
    """Return validation errors for a campaign brief."""
    errors: List[str] = []
    if not brief.business_name.strip():
        errors.append("business_name is required")
    if not brief.product_or_service.strip():
        errors.append("product_or_service is required")
    if brief.budget_ils <= 0:
        errors.append("budget_ils must be positive")
    if brief.end_date < brief.start_date:
        errors.append("end_date must be on or after start_date")
    if brief.usage_rights_days < 0:
        errors.append("usage_rights_days must be non-negative")
    if not brief.deliverables:
        errors.append("at least one deliverable is required")
    return errors


def score_influencer(profile: InfluencerProfile, brief: CampaignBrief) -> ScoreBreakdown:
    """Score creator fit for an Israeli business campaign."""
    profile_errors = validate_profile(profile)
    brief_errors = validate_campaign_brief(brief)
    if profile_errors or brief_errors:
        raise ValueError("; ".join(profile_errors + brief_errors))

    detected = detect_market_segment(f"{profile.niche} {profile.notes}")
    target_set = set(brief.target_segments)
    fit_score = 100.0 if detected in target_set else 55.0 if MarketSegment.GENERAL in target_set else 35.0
    if any(loc.lower() in profile.location.lower() for loc in brief.target_locations):
        fit_score = min(100.0, fit_score + 15.0)

    er = engagement_rate(profile)
    engagement_score = clamp((er / 0.04) * 85 + min(15, math.log10(max(profile.avg_views, 1)) * 3))

    israel_relevance_score = clamp(profile.audience_israel_pct * 100)
    estimated_fee = estimate_creator_fee_ils(profile, brief.deliverables)
    budget_score = clamp(100 - max(0, estimated_fee - brief.budget_ils) / brief.budget_ils * 100)

    conflict_penalty = min(60, len(profile.past_brand_conflicts) * 20)
    suspicious_penalty = 0.0
    if profile.followers > 0 and profile.avg_views / profile.followers < 0.03:
        suspicious_penalty += 20
    if er < 0.005 and profile.followers > 10000:
        suspicious_penalty += 15
    risk_score = clamp(100 - conflict_penalty - suspicious_penalty)

    total = round(
        fit_score * 0.30
        + engagement_score * 0.25
        + israel_relevance_score * 0.20
        + budget_score * 0.15
        + risk_score * 0.10,
        2,
    )

    reasons: List[str] = []
    if detected in target_set:
        reasons.append(f"niche matches {detected.value}")
    else:
        reasons.append(f"detected niche {detected.value} is not a direct target")
    reasons.append(f"estimated local reach {estimated_reach(profile)}")
    reasons.append(f"estimated fee ₪{estimated_fee:,.0f}")
    if profile.past_brand_conflicts:
        reasons.append("brand conflict history requires manual review")
    if suspicious_penalty:
        reasons.append("metric pattern requires authenticity review")

    if total >= 80:
        recommendation = "shortlist"
    elif total >= 60:
        recommendation = "manual_review"
    else:
        recommendation = "skip"

    return ScoreBreakdown(
        handle=normalize_handle(profile.handle),
        total_score=total,
        fit_score=round(fit_score, 2),
        engagement_score=round(engagement_score, 2),
        israel_relevance_score=round(israel_relevance_score, 2),
        budget_score=round(budget_score, 2),
        risk_score=round(risk_score, 2),
        recommendation=recommendation,
        reasons=tuple(reasons),
    )


def rank_influencers(profiles: Sequence[InfluencerProfile], brief: CampaignBrief, limit: int | None = None) -> List[ScoreBreakdown]:
    """Score and rank profiles by total score."""
    scored = [score_influencer(profile, brief) for profile in profiles]
    scored.sort(key=lambda item: item.total_score, reverse=True)
    return scored[:limit] if limit else scored


def validate_disclosure(text: str, required_disclosure: str = "פרסומת") -> Tuple[bool, List[str]]:
    """Check whether Hebrew sponsorship disclosure is clear enough."""
    normalized = re.sub(r"\s+", " ", text.strip())
    accepted = {required_disclosure, "בשיתוף", "ממומן", "תוכן שיווקי", "שיתוף פעולה מסחרי"}
    found = [term for term in accepted if term in normalized]
    issues: List[str] = []
    if not found:
        issues.append("missing clear commercial disclosure")
    if found and normalized.find(found[0]) > 80:
        issues.append("disclosure appears too late")
    if "#ad" in normalized.lower() and not found:
        issues.append("English-only disclosure is not enough for Hebrew audience")
    return (not issues, issues)


def generate_outreach_message(
    profile: InfluencerProfile,
    brief: CampaignBrief,
    tone: str = "professional",
    include_price_anchor: bool = True,
) -> OutreachMessage:
    """Generate a Hebrew outreach message for Israeli collaboration."""
    clean_handle = normalize_handle(profile.handle)
    fee = estimate_creator_fee_ils(profile, brief.deliverables)
    deliverables = ", ".join(brief.deliverables)
    locations = ", ".join(brief.target_locations)
    date_range = f"{brief.start_date.strftime('%d/%m/%Y')} עד {brief.end_date.strftime('%d/%m/%Y')}"
    price_line = f"\nטווח תקציב מוצע לשלב ראשון: עד ₪{min(brief.budget_ils, fee):,.0f}, לפני מע\"מ ככל שרלוונטי." if include_price_anchor else ""
    if tone == "warm":
        opening = f"היי {profile.display_name}, התוכן שלך סביב {profile.niche} מרגיש מתאים לקהל של {locations}."
    elif tone == "direct":
        opening = f"שלום {profile.display_name}, נבחנת התאמה לשיתוף פעולה מסחרי עם {brief.business_name}."
    else:
        opening = f"שלום {profile.display_name}, יש התאמה אפשרית בין הקהל שלך לבין {brief.business_name}."

    body = (
        f"{opening}\n\n"
        f"המוצר או השירות: {brief.product_or_service}.\n"
        f"מטרת הקמפיין: {brief.goal.value}.\n"
        f"תוצרים מוצעים: {deliverables}.\n"
        f"חלון פעילות: {date_range}.\n"
        f"נדרשת הצגת גילוי מסחרי ברור, למשל: {brief.required_disclosure}.\n"
        f"זכויות שימוש בתוכן: {brief.usage_rights_days} ימים, בכפוף לאישור כתוב ולסיכום תנאים."
        f"{price_line}\n\n"
        f"כדאי לשלוח מדיה קיט עדכני, נתוני קהל בישראל, תעריף, ותנאים לשימוש חוזר בתוכן.\n"
        f"תודה."
    )
    follow_up = (
        f"שלום {profile.display_name}, מעקב קצר לגבי ההצעה לשיתוף פעולה עם {brief.business_name}. "
        f"כדאי להשיב עם זמינות, תעריף, ונתוני קהל בישראל כדי להתקדם לסיכום מסודר."
    )
    return OutreachMessage(
        subject=f"הצעה לשיתוף פעולה מסחרי עם {brief.business_name}",
        body=body,
        language="he",
        disclosure_line=f"גילוי נדרש בפרסום: {brief.required_disclosure}",
        follow_up_body=follow_up,
    )


def build_campaign_plan(profiles: Sequence[InfluencerProfile], brief: CampaignBrief, max_creators: int = 5) -> Dict[str, Any]:
    """Create a shortlist, budget allocation, and operational checklist."""
    if max_creators <= 0:
        raise ValueError("max_creators must be positive")
    shortlist = [item for item in rank_influencers(profiles, brief) if item.recommendation != "skip"][:max_creators]
    if not shortlist:
        return {
            "business_name": brief.business_name,
            "shortlist": [],
            "budget_allocation": {},
            "checklist": ["collect more profiles", "verify niche fit", "recheck budget"],
        }

    total_score = sum(item.total_score for item in shortlist)
    allocations = {
        item.handle: round(brief.budget_ils * safe_divide(item.total_score, total_score), 2)
        for item in shortlist
    }
    checklist = [
        "verify identity and contact route",
        "request recent audience screenshots",
        "confirm commercial disclosure wording",
        "agree deliverables and due dates in writing",
        "record invoice or receipt requirements",
        "track coupon code and link parameters",
        "save post links and screenshots after publication",
    ]
    return {
        "business_name": brief.business_name,
        "date_range": [brief.start_date.isoformat(), brief.end_date.isoformat()],
        "shortlist": [asdict(item) for item in shortlist],
        "budget_allocation": allocations,
        "checklist": checklist,
    }


def summarize_campaign(metrics: Sequence[CampaignMetric]) -> CampaignSummary:
    """Aggregate campaign metrics and calculate core efficiency measures."""
    spend = sum(item.spend_ils for item in metrics)
    impressions = sum(item.impressions for item in metrics)
    views = sum(item.views for item in metrics)
    clicks = sum(item.clicks for item in metrics)
    leads = sum(item.leads for item in metrics)
    sales = sum(item.sales for item in metrics)
    revenue = sum(item.revenue_ils for item in metrics)
    recommendations: List[str] = []

    cpm = safe_divide(spend, impressions) * 1000
    cpc = safe_divide(spend, clicks)
    cpl = safe_divide(spend, leads)
    cps = safe_divide(spend, sales)
    roas = safe_divide(revenue, spend)
    conversion_rate = safe_divide(sales, clicks)

    if roas < 1:
        recommendations.append("pause broad scaling until offer, landing page, or creator fit improves")
    if cpc > 8 and clicks > 0:
        recommendations.append("test a stronger call to action and clearer benefit")
    if leads > 0 and sales == 0:
        recommendations.append("inspect follow-up process and sales response time")
    if not recommendations:
        recommendations.append("keep the best creators and negotiate content reuse")

    return CampaignSummary(
        spend_ils=round(spend, 2),
        impressions=impressions,
        views=views,
        clicks=clicks,
        leads=leads,
        sales=sales,
        revenue_ils=round(revenue, 2),
        cpm_ils=round(cpm, 2),
        cpc_ils=round(cpc, 2),
        cpl_ils=round(cpl, 2),
        cost_per_sale_ils=round(cps, 2),
        roas=round(roas, 2),
        conversion_rate=round(conversion_rate, 4),
        recommendations=tuple(recommendations),
    )


def profile_from_dict(data: Mapping[str, Any]) -> InfluencerProfile:
    """Create a profile from dictionary data."""
    return InfluencerProfile(
        handle=str(data["handle"]),
        display_name=str(data.get("display_name") or data["handle"]),
        platform=Platform(str(data.get("platform", "instagram"))),
        niche=str(data.get("niche", "")),
        followers=int(data.get("followers", 0)),
        avg_views=int(data.get("avg_views", 0)),
        avg_likes=int(data.get("avg_likes", 0)),
        avg_comments=int(data.get("avg_comments", 0)),
        location=str(data.get("location", "Israel")),
        audience_israel_pct=float(data.get("audience_israel_pct", 0.75)),
        audience_age_min=int(data.get("audience_age_min", 18)),
        audience_age_max=int(data.get("audience_age_max", 54)),
        contact_email=data.get("contact_email"),
        past_brand_conflicts=tuple(filter(None, str(data.get("past_brand_conflicts", "")).split("|"))) if not isinstance(data.get("past_brand_conflicts"), list) else tuple(data.get("past_brand_conflicts", [])),
        notes=str(data.get("notes", "")),
    )


def brief_from_dict(data: Mapping[str, Any]) -> CampaignBrief:
    """Create a campaign brief from dictionary data."""
    def parse_date(value: Any) -> date:
        if isinstance(value, date):
            return value
        text = str(value)
        if "/" in text:
            return datetime.strptime(text, "%d/%m/%Y").date()
        return date.fromisoformat(text)

    return CampaignBrief(
        business_name=str(data["business_name"]),
        product_or_service=str(data["product_or_service"]),
        goal=CollaborationGoal(str(data.get("goal", "awareness"))),
        target_locations=tuple(data.get("target_locations", ["Israel"])),
        target_segments=tuple(MarketSegment(str(item)) for item in data.get("target_segments", ["general"])),
        budget_ils=float(data["budget_ils"]),
        start_date=parse_date(data["start_date"]),
        end_date=parse_date(data["end_date"]),
        required_disclosure=str(data.get("required_disclosure", "פרסומת")),
        usage_rights_days=int(data.get("usage_rights_days", 30)),
        deliverables=tuple(data.get("deliverables", ["story", "reel"])),
        coupon_code=data.get("coupon_code"),
    )


def load_profiles_csv(path: str | Path) -> List[InfluencerProfile]:
    """Load profiles from a CSV file."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [profile_from_dict(row) for row in csv.DictReader(handle)]


def write_json(path: str | Path, payload: Any) -> None:
    """Write JSON with Hebrew-safe output."""
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def read_json(path: str | Path) -> Any:
    """Read JSON from disk."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


class InfluencerCollaborationClient:
    """Sync client for local influencer collaboration operations."""

    def score_profile(self, profile: InfluencerProfile, brief: CampaignBrief) -> ScoreBreakdown:
        return score_influencer(profile, brief)

    def rank_profiles(self, profiles: Sequence[InfluencerProfile], brief: CampaignBrief, limit: int | None = None) -> List[ScoreBreakdown]:
        return rank_influencers(profiles, brief, limit=limit)

    def estimate_fee(self, profile: InfluencerProfile, deliverables: Sequence[str] | None = None) -> float:
        return estimate_creator_fee_ils(profile, deliverables)

    def generate_outreach(self, profile: InfluencerProfile, brief: CampaignBrief, tone: str = "professional") -> OutreachMessage:
        return generate_outreach_message(profile, brief, tone=tone)

    def validate_disclosure(self, text: str, required_disclosure: str = "פרסומת") -> Tuple[bool, List[str]]:
        return validate_disclosure(text, required_disclosure=required_disclosure)

    def build_plan(self, profiles: Sequence[InfluencerProfile], brief: CampaignBrief, max_creators: int = 5) -> Dict[str, Any]:
        return build_campaign_plan(profiles, brief, max_creators=max_creators)

    def summarize_metrics(self, metrics: Sequence[CampaignMetric]) -> CampaignSummary:
        return summarize_campaign(metrics)

    def load_profiles_csv(self, path: str | Path) -> List[InfluencerProfile]:
        return load_profiles_csv(path)

    def read_json(self, path: str | Path) -> Any:
        return read_json(path)

    def write_json(self, path: str | Path, payload: Any) -> None:
        write_json(path, payload)


class AsyncInfluencerCollaborationClient:
    """Async facade for callers that operate inside event loops."""

    def __init__(self) -> None:
        self._sync = InfluencerCollaborationClient()

    async def score_profile(self, profile: InfluencerProfile, brief: CampaignBrief) -> ScoreBreakdown:
        return await asyncio.to_thread(self._sync.score_profile, profile, brief)

    async def rank_profiles(self, profiles: Sequence[InfluencerProfile], brief: CampaignBrief, limit: int | None = None) -> List[ScoreBreakdown]:
        return await asyncio.to_thread(self._sync.rank_profiles, profiles, brief, limit)

    async def estimate_fee(self, profile: InfluencerProfile, deliverables: Sequence[str] | None = None) -> float:
        return await asyncio.to_thread(self._sync.estimate_fee, profile, deliverables)

    async def generate_outreach(self, profile: InfluencerProfile, brief: CampaignBrief, tone: str = "professional") -> OutreachMessage:
        return await asyncio.to_thread(self._sync.generate_outreach, profile, brief, tone)

    async def validate_disclosure(self, text: str, required_disclosure: str = "פרסומת") -> Tuple[bool, List[str]]:
        return await asyncio.to_thread(self._sync.validate_disclosure, text, required_disclosure)

    async def build_plan(self, profiles: Sequence[InfluencerProfile], brief: CampaignBrief, max_creators: int = 5) -> Dict[str, Any]:
        return await asyncio.to_thread(self._sync.build_plan, profiles, brief, max_creators)

    async def summarize_metrics(self, metrics: Sequence[CampaignMetric]) -> CampaignSummary:
        return await asyncio.to_thread(self._sync.summarize_metrics, metrics)


__all__ = [
    "AsyncInfluencerCollaborationClient",
    "CampaignBrief",
    "CampaignMetric",
    "CampaignSummary",
    "CollaborationGoal",
    "DEFAULT_ISRAEL_VAT_EFFECTIVE_DATE",
    "DEFAULT_ISRAEL_VAT_RATE",
    "InfluencerCollaborationClient",
    "InfluencerProfile",
    "MarketSegment",
    "OutreachMessage",
    "Platform",
    "ScoreBreakdown",
    "brief_from_dict",
    "build_campaign_plan",
    "detect_market_segment",
    "engagement_rate",
    "estimate_creator_fee_ils",
    "estimated_reach",
    "generate_outreach_message",
    "load_profiles_csv",
    "normalize_handle",
    "profile_from_dict",
    "rank_influencers",
    "read_json",
    "safe_divide",
    "score_influencer",
    "summarize_campaign",
    "validate_campaign_brief",
    "validate_disclosure",
    "validate_profile",
    "write_json",
]
