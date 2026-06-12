"""Lead qualification engine for Hebrew WhatsApp conversations in Israel."""

from __future__ import annotations

import asyncio
import csv
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Optional

Tier = Literal["hot", "warm", "nurture", "low_fit", "human", "support", "spam"]
Urgency = Literal["same_day", "this_week", "flexible", "unknown"]
EnvironmentName = Literal["sandbox", "production"]
DEFAULT_VAT_RATE = 0.18
DEFAULT_EXEMPT_DEALER_THRESHOLD_ILS_2026 = 122_833
ISRAEL_INVOICES_THRESHOLD_ILS_FROM_2026_06_01 = 5_000

CITY_ALIASES: dict[str, str] = {
    "תא": "תל אביב",
    "ת״א": "תל אביב",
    "תל אביב": "תל אביב",
    "תל-אביב": "תל אביב",
    "ראשון": "ראשון לציון",
    "ראשלצ": "ראשון לציון",
    "רשלצ": "ראשון לציון",
    "ראשון לציון": "ראשון לציון",
    "פתח תקווה": "פתח תקווה",
    "פת": "פתח תקווה",
    "פ״ת": "פתח תקווה",
    "חיפה": "חיפה",
    "ירושלים": "ירושלים",
    "באר שבע": "באר שבע",
    "רמת גן": "רמת גן",
    "גבעתיים": "גבעתיים",
    "חולון": "חולון",
    "בת ים": "בת ים",
    "הרצליה": "הרצליה",
    "רעננה": "רעננה",
    "כפר סבא": "כפר סבא",
    "נתניה": "נתניה",
    "אילת": "אילת",
}

SERVICE_KEYWORDS: dict[str, set[str]] = {
    "plumbing": {"נזילה", "אינסטלטור", "סתימה", "ביוב", "ברז", "צינור", "כיור"},
    "electrical": {"חשמל", "חשמלאי", "קצר", "לוח", "מפסק", "שקע", "ריח שרוף"},
    "legal": {"עורך דין", "עו״ד", "חוזה", "תביעה", "פיטרו", "פיטורין", "משפטי"},
    "accounting": {"רואה חשבון", "הנהלת חשבונות", "עוסק", "מע״מ", "מס", "חשבונית", "קבלה"},
    "clinic": {"טיפול", "כאבים", "מרפאה", "תור", "רופא", "מטפל", "ילד"},
    "course": {"קורס", "לימודים", "סדנה", "הכשרה", "שיעור"},
    "web_design": {"אתר", "דף נחיתה", "חנות", "וורדפרס", "עיצוב", "אפליקציה"},
    "retail_delivery": {"משלוח", "משלוחים", "מוצר", "מגש", "הזמנה"},
    "support": {"זיכוי", "החזר", "ביטול", "תלונה", "חשבונית מס", "קבלה"},
}

SENSITIVE_KEYWORDS = {
    "רפואי",
    "כאבים",
    "כאב",
    "פיטרו",
    "פיטורין",
    "תביעה",
    "עורך דין",
    "עו״ד",
    "מס אשלם",
    "חבות מס",
    "ילד",
    "קטין",
    "בהריון",
    "אלימות",
    "חירום",
    "ריח שרוף",
}

HUMAN_REQUEST_KEYWORDS = {"נציג", "אדם", "תתקשרו", "תתקשר", "לא בוט", "חזור אליי", "חזרה אליי"}
OPTOUT_KEYWORDS = {"הסרה", "להסיר", "תסירו", "די", "בטל", "לא לשלוח", "stop", "unsubscribe", "remove"}
SPAM_KEYWORDS = {"הלוואה מיידית", "קריפטו בטוח", "לחץ כאן", "זכית", "קזינו"}


@dataclass(slots=True)
class Budget:
    """Budget range in Israeli shekels."""

    min: int
    max: int


@dataclass(slots=True)
class Consent:
    """Consent state for service follow-up and marketing."""

    privacy_notice_shown: bool = True
    service_followup: bool = True
    marketing: bool = False
    consent_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(slots=True)
class Customer:
    """Customer identity fields."""

    phone_e164: Optional[str] = None
    full_name: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None


@dataclass(slots=True)
class Qualification:
    """Qualification result."""

    score: int
    tier: Tier
    reasons: list[str]
    missing_fields: list[str]
    next_action: str
    next_question: str


@dataclass(slots=True)
class Lead:
    """Normalized lead record."""

    lead_id: str
    received_at: str
    channel: str
    language: str
    customer: Customer
    intent: str
    service_category: Optional[str]
    description: str
    urgency: Urgency
    budget_ils: Optional[Budget]
    consent: Consent
    qualification: Qualification
    raw_message: str
    environment: EnvironmentName = "sandbox"
    opt_out: bool = False
    sensitive: bool = False


def normalize_hebrew(text: str) -> str:
    """Normalize quotes, whitespace, and case for Hebrew matching."""
    text = text or ""
    text = text.replace("״", '"').replace("׳", "'").replace("₪", " שח ")
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def normalize_phone(phone: str | None) -> Optional[str]:
    """Normalize Israeli phone numbers to E.164 when possible."""
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("972") and len(digits) in {11, 12}:
        return f"+{digits}"
    if digits.startswith("0") and len(digits) == 10:
        return "+972" + digits[1:]
    if digits.startswith("5") and len(digits) == 9:
        return "+972" + digits
    if phone.startswith("+") and 8 <= len(digits) <= 15:
        return "+" + digits
    raise ValueError(f"Unsupported phone format: {phone}")


def detect_city(text: str) -> Optional[str]:
    """Detect an Israeli city or common alias."""
    normalized = normalize_hebrew(text)
    for alias, canonical in sorted(CITY_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if normalize_hebrew(alias) in normalized:
            return canonical
    return None


def detect_service(text: str) -> Optional[str]:
    """Detect a broad service category from Hebrew keywords."""
    normalized = normalize_hebrew(text)
    for service, keywords in SERVICE_KEYWORDS.items():
        for keyword in keywords:
            if normalize_hebrew(keyword) in normalized:
                return service
    return None


def detect_urgency(text: str) -> Urgency:
    """Detect urgency from Hebrew text."""
    normalized = normalize_hebrew(text)
    if any(term in normalized for term in ["היום", "דחוף", "עכשיו", "מיידי", "כמה שיותר מהר", "אסאפ", "asap"]):
        return "same_day"
    if any(term in normalized for term in ["השבוע", "שבוע הבא", "בימים הקרובים", "עד סוף החודש", "החודש"]):
        return "this_week"
    if any(term in normalized for term in ["אין לחץ", "לא דחוף", "גמיש", "רק בודק", "סתם בודק"]):
        return "flexible"
    return "unknown"


def detect_budget(text: str) -> Optional[Budget]:
    """Extract a simple budget in Israeli shekels."""
    normalized = normalize_hebrew(text).replace(",", "")
    range_match = re.search(r"(?:בין\s*)?(\d{2,7})\s*(?:-|עד|ל-?|ל־)\s*(\d{2,7})", normalized)
    if range_match:
        first = int(range_match.group(1))
        second = int(range_match.group(2))
        return Budget(min=min(first, second), max=max(first, second))
    budget_context = any(term in normalized for term in ["תקציב", "שח", "שקל", "שקלים", "מחיר", "עולה"])
    numbers = [int(n) for n in re.findall(r"\b\d{2,7}\b", normalized)]
    if numbers and budget_context:
        value = max(numbers)
        return Budget(min=value, max=value)
    return None


def is_opt_out(text: str) -> bool:
    """Return True when the user asks to stop marketing."""
    normalized = normalize_hebrew(text)
    return any(keyword in normalized for keyword in OPTOUT_KEYWORDS)


def is_spam(text: str) -> bool:
    """Return True for obvious spam."""
    normalized = normalize_hebrew(text)
    return any(keyword in normalized for keyword in SPAM_KEYWORDS)


def is_sensitive(text: str, service: Optional[str] = None) -> bool:
    """Return True for categories that should be handled by a person."""
    normalized = normalize_hebrew(text)
    if any(keyword in normalized for keyword in HUMAN_REQUEST_KEYWORDS):
        return True
    if any(normalize_hebrew(keyword) in normalized for keyword in SENSITIVE_KEYWORDS):
        if service in {"legal", "accounting", "clinic", "electrical"}:
            return True
        if any(keyword in normalized for keyword in ["ריח שרוף", "ילד", "קטין", "כאבים", "פיטרו", "מס אשלם"]):
            return True
    return False


def infer_intent(text: str, service: Optional[str]) -> str:
    """Infer a broad intent."""
    normalized = normalize_hebrew(text)
    if is_opt_out(text):
        return "opt_out"
    if "כמה עולה" in normalized or "מחיר" in normalized or "הצעת מחיר" in normalized:
        return "price_quote"
    if any(term in normalized for term in ["לקבוע", "תור", "שיחה", "תתקשר"]):
        return "booking"
    if service == "support":
        return "support"
    if service:
        return "service_request"
    return "unknown"


def build_next_question(missing_fields: list[str], tier: Tier, opt_out: bool = False, sensitive: bool = False) -> str:
    """Build the next Hebrew bot message."""
    if opt_out:
        return "הבקשה התקבלה. לא יישלחו אליך הודעות שיווקיות נוספות."
    if sensitive or tier == "human":
        return "כדי לטפל בזה נכון, הפנייה תועבר לנציג. אפשר להשאיר שם ושעה נוחה לחזרה?"
    if "service_category" in missing_fields and "city" in missing_fields:
        return "בשמחה. מה בדיוק צריך ובאיזו עיר?"
    if "service_category" in missing_fields:
        return "איזה שירות נדרש?"
    if "city" in missing_fields:
        return "באיזו עיר או אזור השירות נדרש?"
    if "urgency" in missing_fields:
        return "זה דחוף להיום, לשבוע הקרוב, או שאין לחץ?"
    if "phone" in missing_fields:
        return "אפשר מספר טלפון לחזרה?"
    return "תודה, הפרטים התקבלו. נציג יחזור אליך בהקדם."


def qualify_score(
    service: Optional[str],
    city: Optional[str],
    urgency: Urgency,
    budget: Optional[Budget],
    phone: Optional[str],
    description: str,
    consent: Consent,
    sensitive: bool,
    opt_out: bool,
    spam: bool,
) -> Qualification:
    """Calculate score, tier, reasons, and next action."""
    reasons: list[str] = []
    missing: list[str] = []
    score = 0

    if spam:
        return Qualification(0, "spam", ["spam_detected"], [], "suppress", "לא ניתן לטפל בפנייה זו.")

    if opt_out:
        return Qualification(
            0,
            "low_fit",
            ["opt_out_requested"],
            [],
            "suppress_marketing",
            build_next_question([], "low_fit", opt_out=True),
        )

    if service:
        score += 20
        reasons.append("service_detected")
    else:
        missing.append("service_category")

    if city:
        score += 15
        reasons.append("city_detected")
        if city == "אילת":
            score -= 10
            reasons.append("possible_out_of_area")
    else:
        missing.append("city")

    if urgency == "same_day":
        score += 15
        reasons.append("same_day_urgency")
    elif urgency == "this_week":
        score += 10
        reasons.append("near_term_urgency")
    elif urgency == "flexible":
        score += 4
        reasons.append("flexible_timing")
    else:
        missing.append("urgency")

    if budget:
        score += 15
        reasons.append("budget_detected")
    else:
        score += 7
        reasons.append("budget_unknown_neutral")

    if phone:
        score += 10
        reasons.append("phone_available")
    else:
        missing.append("phone")

    if len(description.strip()) >= 12:
        score += 10
        reasons.append("clear_description")

    if consent.service_followup:
        score += 5
        reasons.append("service_consent")

    if any(term in normalize_hebrew(description) for term in ["בעל העסק", "אני מחליט", "אני בעלים", "לעסק שלי"]):
        score += 10
        reasons.append("decision_maker")

    score = max(0, min(score, 100))

    if sensitive:
        tier: Tier = "human"
        next_action = "human_handoff"
        reasons.append("sensitive_or_human_requested")
    elif service == "support":
        tier = "support"
        next_action = "route_support"
    elif score >= 80 and service and (city or service in {"web_design", "course"}) and urgency in {"same_day", "this_week"}:
        tier = "hot"
        next_action = "call_customer"
    elif score >= 60:
        tier = "warm"
        next_action = "same_day_followup"
    elif score >= 35:
        tier = "nurture"
        next_action = "ask_followup"
    else:
        tier = "low_fit"
        next_action = "polite_decline_or_waitlist"

    return Qualification(score, tier, reasons, missing, next_action, build_next_question(missing, tier, sensitive=sensitive))


class LeadQualificationClient:
    """Sync and async client for local lead qualification."""

    def __init__(self, business_type: str = "general", service_area: Optional[Iterable[str]] = None, environment: EnvironmentName = "sandbox") -> None:
        self.business_type = business_type
        self.service_area = set(service_area or [])
        self.environment = environment

    def create_lead(
        self,
        message: str,
        phone: str | None = None,
        name: str | None = None,
        city: str | None = None,
        email: str | None = None,
        marketing_consent: bool = False,
        service_followup_consent: bool = True,
    ) -> Lead:
        """Create and qualify a lead synchronously."""
        normalized_phone = normalize_phone(phone) if phone else None
        detected_city = city or detect_city(message)
        service = detect_service(message)
        urgency = detect_urgency(message)
        budget = detect_budget(message)
        opt_out = is_opt_out(message)
        spam = is_spam(message)
        sensitive = is_sensitive(message, service)
        consent = Consent(service_followup=service_followup_consent, marketing=marketing_consent)
        qualification = qualify_score(
            service=service,
            city=detected_city,
            urgency=urgency,
            budget=budget,
            phone=normalized_phone,
            description=message,
            consent=consent,
            sensitive=sensitive,
            opt_out=opt_out,
            spam=spam,
        )
        now = datetime.now(timezone.utc).isoformat()
        lead_id_source = normalized_phone or re.sub(r"\W+", "", message)[:12] or "anonymous"
        lead_id = f"L-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{abs(hash((lead_id_source, message))) % 1000000:06d}"
        return Lead(
            lead_id=lead_id,
            received_at=now,
            channel="whatsapp",
            language="he",
            customer=Customer(phone_e164=normalized_phone, full_name=name, city=detected_city, email=email),
            intent=infer_intent(message, service),
            service_category=service,
            description=message,
            urgency=urgency,
            budget_ils=budget,
            consent=consent,
            qualification=qualification,
            raw_message=message,
            environment=self.environment,
            opt_out=opt_out,
            sensitive=sensitive,
        )

    def qualify(self, *args: Any, **kwargs: Any) -> Lead:
        """Backward-compatible alias for create_lead."""
        return self.create_lead(*args, **kwargs)

    async def acreate_lead(self, *args: Any, **kwargs: Any) -> Lead:
        """Create and qualify a lead asynchronously."""
        await asyncio.sleep(0)
        return self.create_lead(*args, **kwargs)

    async def aqualify(self, *args: Any, **kwargs: Any) -> Lead:
        """Backward-compatible alias for acreate_lead."""
        return await self.acreate_lead(*args, **kwargs)

    def get_lead(self, lead: Lead | dict[str, Any]) -> dict[str, Any]:
        """Return a normalized dictionary for a lead object or lead dictionary."""
        if isinstance(lead, Lead):
            return asdict(lead)
        return dict(lead)

    def qualify_many(self, rows: Iterable[dict[str, Any]]) -> list[Lead]:
        """Qualify many row dictionaries."""
        return [
            self.create_lead(
                message=str(row.get("message", "")),
                phone=row.get("phone"),
                name=row.get("name"),
                city=row.get("city") or None,
                email=row.get("email"),
                marketing_consent=str(row.get("marketing_consent", "")).lower() in {"1", "true", "yes", "כן"},
            )
            for row in rows
        ]

    async def aqualify_many(self, rows: Iterable[dict[str, Any]]) -> list[Lead]:
        """Qualify many rows asynchronously."""
        await asyncio.sleep(0)
        return self.qualify_many(rows)

    def to_dict(self, lead: Lead) -> dict[str, Any]:
        """Convert a lead dataclass to a plain dictionary."""
        return asdict(lead)

    def to_json(self, lead: Lead, *, ensure_ascii: bool = False, indent: int | None = 2) -> str:
        """Serialize a lead to JSON."""
        return json.dumps(asdict(lead), ensure_ascii=ensure_ascii, indent=indent)

    def batch_csv(self, input_path: str | Path, output_path: str | Path) -> list[Lead]:
        """Read leads from CSV and write qualified CSV."""
        input_path = Path(input_path)
        output_path = Path(output_path)
        with input_path.open("r", encoding="utf-8-sig", newline="") as fh:
            leads = self.qualify_many(csv.DictReader(fh))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "lead_id",
            "received_at",
            "phone_e164",
            "name",
            "city",
            "service_category",
            "urgency",
            "budget_min_ils",
            "budget_max_ils",
            "score",
            "tier",
            "next_action",
            "reasons",
            "missing_fields",
            "next_question",
            "opt_out",
            "sensitive",
            "environment",
        ]
        with output_path.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for lead in leads:
                writer.writerow(flatten_lead(lead))
        return leads


def flatten_lead(lead: Lead) -> dict[str, Any]:
    """Flatten a lead for CSV export."""
    budget = lead.budget_ils
    return {
        "lead_id": lead.lead_id,
        "received_at": lead.received_at,
        "phone_e164": lead.customer.phone_e164,
        "name": lead.customer.full_name,
        "city": lead.customer.city,
        "service_category": lead.service_category,
        "urgency": lead.urgency,
        "budget_min_ils": budget.min if budget else "",
        "budget_max_ils": budget.max if budget else "",
        "score": lead.qualification.score,
        "tier": lead.qualification.tier,
        "next_action": lead.qualification.next_action,
        "reasons": "|".join(lead.qualification.reasons),
        "missing_fields": "|".join(lead.qualification.missing_fields),
        "next_question": lead.qualification.next_question,
        "opt_out": lead.opt_out,
        "sensitive": lead.sensitive,
        "environment": lead.environment,
    }


__all__ = [
    "Budget",
    "CITY_ALIASES",
    "Consent",
    "Customer",
    "Lead",
    "LeadQualificationClient",
    "Qualification",
    "SERVICE_KEYWORDS",
    "detect_budget",
    "detect_city",
    "detect_service",
    "detect_urgency",
    "flatten_lead",
    "infer_intent",
    "is_opt_out",
    "is_sensitive",
    "is_spam",
    "normalize_hebrew",
    "normalize_phone",
    "DEFAULT_VAT_RATE",
    "DEFAULT_EXEMPT_DEALER_THRESHOLD_ILS_2026",
    "ISRAEL_INVOICES_THRESHOLD_ILS_FROM_2026_06_01",
    "qualify_score",
]
