from __future__ import annotations

import asyncio
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo


ISRAEL_TZ = ZoneInfo("Asia/Jerusalem")


class Channel(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"
    PHONE_SCRIPT = "phone_script"
    CRM_TASK = "crm_task"


class EventType(str, Enum):
    SERVICE_COMPLETED = "service_completed"
    REVIEW_REQUEST = "review_request"
    INVOICE_DUE = "invoice_due"
    MISSING_DOCUMENTS = "missing_documents"
    APPOINTMENT_REMINDER = "appointment_reminder"
    DELIVERY_CHECKIN = "delivery_checkin"
    CONSUMER_FOLLOWUP = "consumer_followup"
    SERVICE_RECOVERY = "service_recovery"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"


class ConsentStatus(str, Enum):
    TRANSACTIONAL = "transactional"
    MARKETING_OPT_IN = "marketing_opt_in"
    OPTED_OUT = "opted_out"
    UNKNOWN = "unknown"


class Urgency(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


SENSITIVE_BUSINESS_TYPES = {
    "clinic",
    "medical",
    "therapy",
    "legal",
    "lawyer",
    "insurance",
    "debt",
    "minor",
    "tax_investigation",
}


@dataclass(frozen=True)
class BusinessContext:
    business_name: str
    business_type: str = "service"
    branch_name: Optional[str] = None
    timezone: str = "Asia/Jerusalem"
    friday_cutoff: time = time(12, 30)
    quiet_start: time = time(21, 0)
    quiet_end: time = time(8, 0)
    holiday_blackouts: Tuple[str, ...] = ()


@dataclass(frozen=True)
class FollowupRequest:
    business_name: str
    event_type: EventType | str
    event_date: str
    channel: Channel | str = Channel.WHATSAPP
    customer_name: Optional[str] = None
    review_url: Optional[str] = None
    payment_url: Optional[str] = None
    amount_ils: Optional[float] = None
    period_label: Optional[str] = None
    due_date: Optional[str] = None
    appointment_time: Optional[str] = None
    sentiment: Sentiment | str = Sentiment.UNKNOWN
    consent_status: ConsentStatus | str = ConsentStatus.TRANSACTIONAL
    urgency: Urgency | str = Urgency.NORMAL
    business_type: str = "service"
    branch_name: Optional[str] = None
    now: Optional[datetime] = None
    complaint_open: bool = False
    promotional_text: bool = False
    event_id: Optional[str] = None
    contact_id: Optional[str] = None
    phone: Optional[str] = None
    holiday_blackouts: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class FollowupPlan:
    should_send: bool
    recommended_send_at: Optional[datetime]
    timezone: str
    channel: Channel
    intent: EventType
    message_he: str
    compliance_notes: Tuple[str, ...]
    fallback_action: Optional[str]
    idempotency_key: str
    risk_flags: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "should_send": self.should_send,
            "recommended_send_at": self.recommended_send_at.isoformat() if self.recommended_send_at else None,
            "timezone": self.timezone,
            "channel": self.channel.value,
            "intent": self.intent.value,
            "message_he": self.message_he,
            "compliance_notes": list(self.compliance_notes),
            "fallback_action": self.fallback_action,
            "idempotency_key": self.idempotency_key,
            "risk_flags": list(self.risk_flags),
        }

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


def parse_israeli_date(value: str) -> date:
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Expected DD/MM/YYYY date, got {value!r}")


def format_israeli_date(value: date | datetime | str) -> str:
    if isinstance(value, str):
        return parse_israeli_date(value).strftime("%d/%m/%Y")
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    return value.strftime("%d/%m/%Y")


def parse_dd_mm_yyyy(value: str) -> date:
    return parse_israeli_date(value)


def format_dd_mm_yyyy(value: date | datetime | str) -> str:
    return format_israeli_date(value)


def format_ils(amount: float | int | str | None) -> str:
    if amount is None:
        return ""
    if isinstance(amount, str):
        cleaned = amount.replace("₪", "").replace(",", "").strip()
        amount_value = float(cleaned)
    else:
        amount_value = float(amount)
    if amount_value.is_integer():
        return f"₪{int(amount_value):,}"
    return f"₪{amount_value:,.2f}"


def normalize_israeli_mobile(phone: str) -> str:
    digits = re.sub(r"\D+", "", phone or "")
    if digits.startswith("972"):
        normalized = "+" + digits
    elif digits.startswith("0"):
        normalized = "+972" + digits[1:]
    elif digits.startswith("5") and len(digits) == 9:
        normalized = "+972" + digits
    else:
        raise ValueError("Invalid Israeli mobile number")
    if not re.fullmatch(r"\+9725\d{8}", normalized):
        raise ValueError("Invalid Israeli mobile number")
    return normalized


def is_opt_out_text(text: str) -> bool:
    normalized = (text or "").strip().lower()
    return normalized in {"הסר", "הסרה", "stop", "unsubscribe", "remove", "בטל"}


def greeting(customer_name: Optional[str]) -> str:
    clean = (customer_name or "").strip()
    return f"היי {clean}," if clean else "היי,"


def contains_unresolved_placeholders(text: str) -> bool:
    return bool(re.search(r"\{[a-zA-Z0-9_]+\}", text))


def is_sensitive_business_type(business_type: str) -> bool:
    return (business_type or "").strip().lower() in SENSITIVE_BUSINESS_TYPES


def normalize_key(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-zא-ת_-]+", "-", value.strip())
    return cleaned.strip("-") or "unknown"


def make_idempotency_key(request: FollowupRequest) -> str:
    event_id = request.event_id or "event"
    contact_id = request.contact_id or normalize_key(request.customer_name or request.phone or "contact")
    event_type = _enum(request.event_type, EventType).value
    event_date = format_israeli_date(request.event_date).replace("/", "")
    return f"{event_id}:{contact_id}:{event_type}:{event_date}"


def next_israeli_send_time(
    now: Optional[datetime] = None,
    *,
    intent: EventType = EventType.SERVICE_COMPLETED,
    urgency: Urgency = Urgency.NORMAL,
    holiday_blackouts: Sequence[str] = (),
) -> datetime:
    current = (now or datetime.now(ISRAEL_TZ)).astimezone(ISRAEL_TZ)
    minimum = current + (timedelta(minutes=10) if urgency == Urgency.HIGH else timedelta(minutes=30))
    slots = _slot_candidates(intent, urgency)

    for day_offset in range(0, 21):
        candidate_day = minimum.date() + timedelta(days=day_offset)
        for slot in slots:
            candidate = datetime.combine(candidate_day, slot, tzinfo=ISRAEL_TZ)
            if candidate < minimum:
                continue
            if _is_allowed_business_time(candidate, holiday_blackouts):
                return candidate
    raise RuntimeError("No allowed Israeli send window found in the next 21 days")


def render_message(request: FollowupRequest) -> str:
    intent = _enum(request.event_type, EventType)
    sentiment = _enum(request.sentiment, Sentiment)

    if request.complaint_open or sentiment == Sentiment.NEGATIVE or intent == EventType.SERVICE_RECOVERY:
        message = _support_recovery_message(request)
    elif intent == EventType.REVIEW_REQUEST:
        message = _review_request_message(request)
    elif intent == EventType.INVOICE_DUE:
        message = _invoice_message(request)
    elif intent == EventType.MISSING_DOCUMENTS:
        message = _missing_documents_message(request)
    elif intent == EventType.APPOINTMENT_REMINDER:
        message = _appointment_message(request)
    elif intent == EventType.DELIVERY_CHECKIN:
        message = _delivery_message(request)
    elif intent == EventType.CONSUMER_FOLLOWUP:
        message = _consumer_followup_message(request)
    else:
        message = _service_checkin_message(request)

    return _append_opt_out(message.strip(), request)


def plan_from_dict(data: Dict[str, Any]) -> FollowupPlan:
    request = FollowupRequest(**data)
    return FollowupSolicitorClient().generate_plan(request)


def load_requests_from_json(path: str | Path) -> List[FollowupRequest]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    items = payload if isinstance(payload, list) else [payload]
    return [FollowupRequest(**item) for item in items]


def plans_to_json(plans: Sequence[FollowupPlan]) -> str:
    return json.dumps([plan.to_dict() for plan in plans], ensure_ascii=False, indent=2)


def create_request_record(request: FollowupRequest, *, directory: str | Path = ".followup-review-solicitor/requests") -> Dict[str, str]:
    request_id = request.event_id or f"req_{uuid.uuid4().hex[:12]}"
    target_dir = Path(directory)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{request_id}.json"
    payload = {
        "business_name": request.business_name,
        "customer_name": request.customer_name,
        "event_type": _enum(request.event_type, EventType).value,
        "event_date": format_israeli_date(request.event_date),
        "channel": _enum(request.channel, Channel).value,
        "review_url": request.review_url,
        "payment_url": request.payment_url,
        "amount_ils": request.amount_ils,
        "period_label": request.period_label,
        "due_date": request.due_date,
        "appointment_time": request.appointment_time,
        "sentiment": _enum(request.sentiment, Sentiment).value,
        "consent_status": _enum(request.consent_status, ConsentStatus).value,
        "urgency": _enum(request.urgency, Urgency).value,
        "business_type": request.business_type,
        "branch_name": request.branch_name,
        "complaint_open": request.complaint_open,
        "promotional_text": request.promotional_text,
        "event_id": request_id,
        "contact_id": request.contact_id,
        "phone": request.phone,
        "holiday_blackouts": list(request.holiday_blackouts),
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"id": request_id, "path": str(target)}


def load_request_record(request_id: str, *, directory: str | Path = ".followup-review-solicitor/requests") -> FollowupRequest:
    path = Path(directory) / f"{request_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Request record not found: {request_id}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return FollowupRequest(**data)


class FollowupSolicitorClient:
    def validate(self, request: FollowupRequest) -> Tuple[bool, List[str], List[str], Optional[str]]:
        notes: List[str] = []
        risks: List[str] = []
        fallback: Optional[str] = None

        intent = _enum(request.event_type, EventType)
        sentiment = _enum(request.sentiment, Sentiment)
        consent = _enum(request.consent_status, ConsentStatus)

        if not request.business_name.strip() and intent != EventType.CONSUMER_FOLLOWUP:
            return False, ["Missing business name."], ["missing_business_name"], "Complete business name before customer-facing send."

        try:
            parse_israeli_date(request.event_date)
        except ValueError as exc:
            return False, [str(exc)], ["invalid_date"], "Use DD/MM/YYYY date format."

        if request.phone and _enum(request.channel, Channel) in {Channel.SMS, Channel.WHATSAPP}:
            try:
                normalize_israeli_mobile(request.phone)
            except ValueError:
                return False, ["Invalid Israeli mobile phone."], ["invalid_phone"], "Fix phone number before sending."

        if consent == ConsentStatus.OPTED_OUT:
            return False, ["Contact is opted out."], ["opted_out"], "Suppress contact and do not send."

        if request.promotional_text and consent != ConsentStatus.MARKETING_OPT_IN:
            return False, ["Promotional content requires marketing opt-in."], ["missing_marketing_consent"], "Remove promotion or collect valid opt-in."

        if request.complaint_open or sentiment == Sentiment.NEGATIVE:
            if intent == EventType.REVIEW_REQUEST:
                return False, ["Open complaint or negative sentiment blocks review request."], ["complaint_or_negative_sentiment"], "Send service recovery message instead."
            notes.append("Service recovery path selected because complaint or negative sentiment exists.")

        if intent == EventType.REVIEW_REQUEST:
            if sentiment != Sentiment.POSITIVE:
                return False, ["Review request requires positive customer signal."], ["missing_positive_signal"], "Send satisfaction check-in first."
            if not request.review_url:
                return False, ["Review URL is required for direct review request."], ["missing_review_url"], "Add review URL or send private feedback request."

        if is_sensitive_business_type(request.business_type):
            risks.append("sensitive_business_type")
            notes.append("Sensitive business type: keep wording generic and consider manual approval.")

        if intent == EventType.INVOICE_DUE:
            notes.append("Payment reminder must remain factual and non-threatening.")

        if intent in {EventType.SERVICE_COMPLETED, EventType.DELIVERY_CHECKIN}:
            notes.append("Review request should wait until satisfaction is confirmed.")

        if request.promotional_text:
            notes.append("Marketing opt-in present; opt-out text added where channel supports it.")
        else:
            notes.append("No promotional content detected.")

        return True, notes, risks, fallback

    def generate_plan(self, request: FollowupRequest) -> FollowupPlan:
        intent = _enum(request.event_type, EventType)
        channel = _enum(request.channel, Channel)
        urgency = _enum(request.urgency, Urgency)
        ok, notes, risks, fallback = self.validate(request)
        key = make_idempotency_key(request)

        if not ok:
            return FollowupPlan(False, None, "Asia/Jerusalem", channel, intent, "", tuple(notes), fallback, key, tuple(risks))

        message = render_message(request)
        if contains_unresolved_placeholders(message):
            return FollowupPlan(
                False,
                None,
                "Asia/Jerusalem",
                channel,
                intent,
                "",
                tuple(notes + ["Unresolved template placeholders detected."]),
                "Fix template variables before sending.",
                key,
                tuple(risks + ["unresolved_placeholders"]),
            )

        send_at = next_israeli_send_time(
            request.now,
            intent=intent,
            urgency=urgency,
            holiday_blackouts=request.holiday_blackouts,
        )

        return FollowupPlan(True, send_at, "Asia/Jerusalem", channel, intent, message, tuple(notes), fallback, key, tuple(risks))

    async def async_generate_plan(self, request: FollowupRequest) -> FollowupPlan:
        await asyncio.sleep(0)
        return self.generate_plan(request)

    def generate_many(self, requests: Iterable[FollowupRequest]) -> List[FollowupPlan]:
        return [self.generate_plan(request) for request in requests]


def _enum(value: Any, enum_type: type[Enum]) -> Enum:
    if isinstance(value, enum_type):
        return value
    return enum_type(str(value))


def _date_key(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y")


def _is_holiday(dt: datetime, holiday_blackouts: Sequence[str]) -> bool:
    normalized = {format_israeli_date(item) for item in holiday_blackouts or []}
    return _date_key(dt) in normalized


def _is_allowed_business_time(dt: datetime, holiday_blackouts: Sequence[str] = ()) -> bool:
    local = dt.astimezone(ISRAEL_TZ)
    if _is_holiday(local, holiday_blackouts):
        return False
    weekday = local.weekday()
    current = local.time()
    if weekday == 5:
        return False
    if weekday == 4 and current > time(12, 30):
        return False
    if current < time(8, 0) or current > time(21, 0):
        return False
    return True


def _slot_candidates(intent: EventType, urgency: Urgency) -> Tuple[time, ...]:
    if urgency == Urgency.HIGH:
        return (time(8, 30), time(9, 30), time(12, 30), time(16, 0), time(18, 30))
    if intent == EventType.REVIEW_REQUEST:
        return (time(10, 0), time(12, 30), time(18, 30))
    if intent == EventType.INVOICE_DUE:
        return (time(9, 30), time(12, 0), time(16, 30))
    if intent == EventType.MISSING_DOCUMENTS:
        return (time(9, 30), time(11, 30), time(15, 30))
    if intent == EventType.APPOINTMENT_REMINDER:
        return (time(8, 30), time(17, 30), time(18, 30))
    if intent == EventType.DELIVERY_CHECKIN:
        return (time(10, 0), time(18, 30))
    return (time(9, 30), time(12, 30), time(18, 30))


def _append_opt_out(message: str, request: FollowupRequest) -> str:
    channel = _enum(request.channel, Channel)
    consent = _enum(request.consent_status, ConsentStatus)
    if request.promotional_text or consent == ConsentStatus.MARKETING_OPT_IN:
        if channel == Channel.SMS:
            return f"{message}\nלהסרה: השיבו הסר"
        if channel == Channel.EMAIL:
            return f"{message}\n\nלהסרה מרשימת תפוצה ניתן להשיב למייל זה עם המילה הסרה."
    return message


def _support_recovery_message(request: FollowupRequest) -> str:
    return f"{greeting(request.customer_name)} תודה שעדכנת. חשוב לטפל בזה כמו שצריך. אפשר לשלוח כאן פירוט קצר או תמונה, ואבדוק את הנושא בהקדם."


def _service_checkin_message(request: FollowupRequest) -> str:
    return (
        f"{greeting(request.customer_name)} תודה שבחרת ב{request.business_name}. "
        f"רציתי לוודא שהכול תקין אחרי השירות מ-{format_israeli_date(request.event_date)}. "
        "אם יש משהו שדורש טיפול נוסף, אפשר לענות כאן ואטפל בזה בהקדם."
    )


def _review_request_message(request: FollowupRequest) -> str:
    return (
        f"{greeting(request.customer_name)} תודה על העדכון. "
        "אם השירות היה טוב עבורך, אפשר להשאיר חוות דעת קצרה כאן:\n"
        f"{request.review_url}\n"
        "זה עוזר ללקוחות נוספים להבין למה לצפות. תודה רבה."
    )


def _invoice_message(request: FollowupRequest) -> str:
    amount = format_ils(request.amount_ils) if request.amount_ils is not None else "הסכום הפתוח"
    payment = f"\nאפשר להסדיר תשלום כאן:\n{request.payment_url}" if request.payment_url else ""
    return (
        f"{greeting(request.customer_name)} תזכורת נעימה לגבי חשבונית מס/קבלה "
        f"מ-{format_israeli_date(request.event_date)} על סך {amount}.{payment}\n"
        "אם התשלום כבר בוצע, אפשר להתעלם מההודעה. תודה."
    )


def _missing_documents_message(request: FollowupRequest) -> str:
    period = request.period_label or "התקופה הרלוונטית"
    due = format_israeli_date(request.due_date) if request.due_date else "המועד שסוכם"
    return (
        f"{greeting(request.customer_name)} חסרים עדיין מסמכים להשלמת הדיווח עבור {period}. "
        f"נא לשלוח את החשבוניות/קבלות החסרות עד {due} כדי לאפשר הגשה בזמן. תודה."
    )


def _appointment_message(request: FollowupRequest) -> str:
    when = f" בתאריך {format_israeli_date(request.event_date)}"
    hour = f" בשעה {request.appointment_time}" if request.appointment_time else ""
    return (
        f"{greeting(request.customer_name)} תזכורת לפגישה עם {request.business_name}{when}{hour}. "
        "אם צריך לשנות מועד, נא לעדכן מראש. תודה."
    )


def _delivery_message(request: FollowupRequest) -> str:
    return (
        f"{greeting(request.customer_name)} רציתי לוודא שהמשלוח מ-{format_israeli_date(request.event_date)} הגיע תקין. "
        f"אם יש בעיה, אפשר לענות כאן. אם הכול בסדר, תודה על הבחירה ב{request.business_name}."
    )


def _consumer_followup_message(request: FollowupRequest) -> str:
    return (
        f"{greeting(request.customer_name)} אשמח לקבל עדכון לגבי הטיפול בפנייה מ-{format_israeli_date(request.event_date)}. "
        "אם חסר פרט נוסף מצדי, אפשר לעדכן כאן. תודה."
    )
