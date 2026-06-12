"""Typed workflow client for Israeli HMO appointment booking.

The client creates compliant booking plans for official HMO channels. It does
not scrape portals, collect credentials, bypass queues, or diagnose medical
conditions.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import enum
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol


class HMO(str, enum.Enum):
    CLALIT = "clalit"
    MACCABI = "maccabi"
    MEUHEDET = "meuhedet"
    LEUMIT = "leumit"


class Urgency(str, enum.Enum):
    ROUTINE = "routine"
    SOON = "soon"
    SAME_DAY = "same_day"
    URGENT_SYMPTOMS = "urgent_symptoms"


class AgeGroup(str, enum.Enum):
    ADULT = "adult"
    CHILD = "child"
    INFANT = "infant"
    SENIOR = "senior"


class ReferralStatus(str, enum.Enum):
    HAS_REFERRAL = "has_referral"
    NO_REFERRAL = "no_referral"
    PENDING = "pending"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class Channel(str, enum.Enum):
    OFFICIAL_APP = "official_app"
    OFFICIAL_WEBSITE = "official_website"
    CALL_CENTER = "call_center"
    CLINIC_DESK = "clinic_desk"
    URGENT_CARE = "urgent_care"
    EMERGENCY = "emergency"
    TELEHEALTH = "telehealth"
    ADMIN_APPROVALS = "admin_approvals"


@dataclass(frozen=True)
class AppointmentRequest:
    hmo: HMO
    service: str
    city: str
    date_from: dt.date
    date_to: dt.date
    age_group: AgeGroup = AgeGroup.ADULT
    urgency: Urgency = Urgency.ROUTINE
    referral_status: ReferralStatus = ReferralStatus.UNKNOWN
    language: str = "he"
    time_preferences: tuple[str, ...] = ()
    accessibility: tuple[str, ...] = ()
    patient_authorized_helper: bool = True
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.service.strip():
            raise ValueError("service must not be empty")
        if not self.city.strip():
            raise ValueError("city must not be empty")
        if self.date_to < self.date_from:
            raise ValueError("date_to must be on or after date_from")
        if not self.patient_authorized_helper:
            raise ValueError("patient authorization is required for helper booking")


@dataclass(frozen=True)
class AppointmentOption:
    provider_name: str
    clinic_name: str
    city: str
    starts_at: dt.datetime
    channel: Channel
    language: str = "he"
    accessibility: tuple[str, ...] = ()
    requires_referral: bool = False
    preparation: tuple[str, ...] = ()


@dataclass(frozen=True)
class BookingPlan:
    request: AppointmentRequest
    recommended_channels: tuple[Channel, ...]
    specialty: str
    referral_required: str
    priority: str
    instructions: tuple[str, ...]
    hebrew_script: str
    english_script: str
    documents_to_prepare: tuple[str, ...]
    fallbacks: tuple[str, ...]
    warnings: tuple[str, ...]
    privacy_notice: str = "Do not send ID number, HMO password, SMS code, or medical files through this helper."

    def to_dict(self) -> dict[str, Any]:
        return {
            "hmo": self.request.hmo.value,
            "service": self.request.service,
            "city": self.request.city,
            "date_from": self.request.date_from.isoformat(),
            "date_to": self.request.date_to.isoformat(),
            "age_group": self.request.age_group.value,
            "urgency": self.request.urgency.value,
            "recommended_channels": [channel.value for channel in self.recommended_channels],
            "specialty": self.specialty,
            "referral_required": self.referral_required,
            "priority": self.priority,
            "instructions": list(self.instructions),
            "hebrew_script": self.hebrew_script,
            "english_script": self.english_script,
            "documents_to_prepare": list(self.documents_to_prepare),
            "fallbacks": list(self.fallbacks),
            "warnings": list(self.warnings),
            "privacy_notice": self.privacy_notice,
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


@dataclass(frozen=True)
class BookingResult:
    status: str
    plan: BookingPlan
    selected_option: AppointmentOption | None = None
    confirmation_number: str | None = None
    message: str = ""


class AppointmentAdapter(Protocol):
    def search(self, request: AppointmentRequest) -> list[AppointmentOption]:
        ...

    def book(self, request: AppointmentRequest, option: AppointmentOption) -> BookingResult:
        ...


class AsyncAppointmentAdapter(Protocol):
    async def search(self, request: AppointmentRequest) -> list[AppointmentOption]:
        ...

    async def book(self, request: AppointmentRequest, option: AppointmentOption) -> BookingResult:
        ...


HMO_HEBREW: Mapping[HMO, str] = {
    HMO.CLALIT: "כללית",
    HMO.MACCABI: "מכבי",
    HMO.MEUHEDET: "מאוחדת",
    HMO.LEUMIT: "לאומית",
}

HMO_CHANNELS: Mapping[HMO, tuple[Channel, ...]] = {
    hmo: (Channel.OFFICIAL_APP, Channel.OFFICIAL_WEBSITE, Channel.CALL_CENTER, Channel.CLINIC_DESK)
    for hmo in HMO
}

SPECIALTY_KEYWORDS: Mapping[str, tuple[str, ...]] = {
    "family_medicine": ("family", "רופא משפחה", "משפחה", "prescription", "sick note", "מרשם", "אישור מחלה"),
    "pediatrics": ("child", "children", "pediatric", "ילד", "ילדה", "ילדים", "תינוק"),
    "dermatology": ("skin", "rash", "mole", "dermat", "עור", "פריחה", "נקודת חן", "אקנה"),
    "orthopedics": ("knee", "back", "joint", "orthopedic", "אורתופד", "ברך", "גב", "מפרק"),
    "ophthalmology": ("eye", "vision", "ophthalm", "עיניים", "ראייה", "עין"),
    "ent": ("ear", "nose", "throat", "hearing", "אוזן", "אף", "גרון", "שמיעה", "אאג", "אא״ג"),
    "gynecology": ("pregnancy", "gynecology", "women", "הריון", "היריון", "נשים", "גינקולוג"),
    "gastroenterology": ("stomach", "reflux", "gastro", "בטן", "גסטרו", "ריפלוקס"),
    "cardiology": ("heart", "cardio", "לב", "קרדיולוג"),
    "neurology": ("neuro", "migraine", "נוירולוג", "מיגרנה"),
    "endocrinology": ("diabetes", "thyroid", "endo", "סוכרת", "בלוטת", "אנדוקרינולוג"),
    "psychiatry": ("psychiatry", "mental", "anxiety", "depression", "פסיכיאטר", "נפש", "חרדה", "דיכאון"),
    "allergy": ("allergy", "allergic", "אלרג", "אלרגיה"),
    "oncology": ("oncology", "cancer", "אונקולוג", "סרטן"),
    "imaging": ("mri", "ct", "ultrasound", "x-ray", "xray", "mammography", "דימות", "אולטרסאונד", "רנטגן", "ממוגרפיה"),
    "lab": ("blood test", "blood tests", "urine", "lab", "בדיקות דם", "בדיקת דם", "שתן", "מעבדה"),
    "nursing": ("nurse", "vaccine", "injection", "wound", "אחות", "חיסון", "זריקה", "פצע"),
    "physiotherapy": ("physio", "physical therapy", "פיזיותרפיה"),
    "admin": ("form 17", "tofess 17", "approval", "commitment", "טופס 17", "התחייבות", "אישור"),
    "telehealth": ("video", "online", "phone visit", "וידאו", "טלפוני", "מרחוק"),
}

REFERRAL_LIKELY = {"gastroenterology", "cardiology", "neurology", "endocrinology", "oncology", "physiotherapy"}
ORDER_LIKELY = {"imaging", "lab", "nursing", "physiotherapy"}
DIRECT_OFTEN = {"family_medicine", "pediatrics", "gynecology", "nursing", "lab", "telehealth"}

EMERGENCY_PATTERNS = (
    "chest pain", "severe shortness of breath", "shortness of breath", "stroke",
    "face droop", "sudden weakness", "fainting", "uncontrolled bleeding", "anaphylaxis",
    "severe allergic", "suicidal", "harm myself", "sudden vision loss", "vision loss",
    "infant fever", "כאבים בחזה", "קוצר נשימה", "שבץ", "חולשה פתאומית",
    "התעלפות", "דימום בלתי נשלט", "אובדן ראייה", "אובדנות", "לפגוע בעצמי",
)
SAME_DAY_HINTS = ("fever", "ear pain", "severe back pain", "high fever", "חום", "כאב אוזניים", "כאבי גב חזקים")


def parse_date(value: str | dt.date) -> dt.date:
    if isinstance(value, dt.date):
        return value
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError("unsupported date format; use YYYY-MM-DD or DD-MM-YYYY")


def normalize_hmo(value: str | HMO) -> HMO:
    if isinstance(value, HMO):
        return value
    aliases = {
        "clalit": HMO.CLALIT, "כללית": HMO.CLALIT,
        "maccabi": HMO.MACCABI, "מכבי": HMO.MACCABI,
        "meuhedet": HMO.MEUHEDET, "מאוחדת": HMO.MEUHEDET,
        "leumit": HMO.LEUMIT, "לאומית": HMO.LEUMIT,
    }
    try:
        return aliases[value.strip().lower()]
    except KeyError as exc:
        raise ValueError("supported HMOs: clalit, maccabi, meuhedet, leumit") from exc


def normalize_enum(enum_cls: type[enum.Enum], value: str | enum.Enum) -> enum.Enum:
    if isinstance(value, enum_cls):
        return value
    clean = str(value).strip().lower().replace("-", "_")
    for item in enum_cls:
        if item.value == clean or item.name.lower() == clean:
            return item
    raise ValueError(f"unsupported {enum_cls.__name__}: {value}")


def contains_sensitive_secret(text: str) -> bool:
    lowered = text.lower()
    if re.search(r"\b\d{9}\b", lowered):
        return True
    return any(token in lowered for token in ("password", "סיסמה", "סיסמא", "sms code", "otp", "one-time code"))


def has_emergency_red_flags(text: str, *, age_group: AgeGroup | str = AgeGroup.ADULT) -> bool:
    if not isinstance(age_group, AgeGroup):
        age_group = normalize_enum(AgeGroup, age_group)  # type: ignore[assignment]
    lowered = text.lower()
    if age_group == AgeGroup.INFANT and ("fever" in lowered or "חום" in lowered):
        return True
    return any(pattern in lowered for pattern in EMERGENCY_PATTERNS)


def _keyword_in_text(keyword: str, lowered: str) -> bool:
    key = keyword.lower()
    if any("\u0590" <= ch <= "\u05ff" for ch in key):
        return key in lowered
    if len(key) <= 4 and key.replace("-", "").isalpha():
        return re.search(rf"(?<![a-z0-9]){re.escape(key)}(?![a-z0-9])", lowered) is not None
    return key in lowered


def classify_specialty(service: str, *, age_group: AgeGroup = AgeGroup.ADULT) -> str:
    lowered = service.lower()
    imaging_terms = ("mri", "ct", "ultrasound", "x-ray", "xray", "mammography", "דימות", "אולטרסאונד", "רנטגן", "ממוגרפיה")
    if any(_keyword_in_text(term, lowered) for term in imaging_terms):
        return "imaging"
    if age_group in {AgeGroup.CHILD, AgeGroup.INFANT} and any(_keyword_in_text(k, lowered) for k in ("fever", "ear", "חום", "אוזן", "ילד", "ילדה")):
        return "pediatrics"
    scores: dict[str, int] = {}
    for specialty, keywords in SPECIALTY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if _keyword_in_text(keyword, lowered))
        if score:
            scores[specialty] = score
    return max(scores, key=scores.__getitem__) if scores else "unknown"


def referral_requirement(specialty: str, status: ReferralStatus) -> str:
    if specialty in ORDER_LIKELY:
        return "order_or_referral_present_verify_approval" if status == ReferralStatus.HAS_REFERRAL else "order_or_referral_likely_required"
    if specialty in REFERRAL_LIKELY:
        return "has_referral_verify_validity" if status == ReferralStatus.HAS_REFERRAL else "likely_required"
    if specialty in DIRECT_OFTEN:
        return "usually_direct_or_not_applicable"
    return "has_referral_verify_validity" if status == ReferralStatus.HAS_REFERRAL else "unknown_check_official_channel"


def format_he_date(date_value: dt.date) -> str:
    return date_value.strftime("%d/%m/%Y")


def build_request(
    *,
    hmo: str | HMO,
    service: str,
    city: str,
    date_from: str | dt.date,
    date_to: str | dt.date,
    age_group: str | AgeGroup = AgeGroup.ADULT,
    urgency: str | Urgency = Urgency.ROUTINE,
    referral_status: str | ReferralStatus = ReferralStatus.UNKNOWN,
    language: str = "he",
    time_preferences: Iterable[str] = (),
    accessibility: Iterable[str] = (),
    patient_authorized_helper: bool = True,
    notes: str = "",
) -> AppointmentRequest:
    return AppointmentRequest(
        hmo=normalize_hmo(hmo),
        service=service,
        city=city,
        date_from=parse_date(date_from),
        date_to=parse_date(date_to),
        age_group=normalize_enum(AgeGroup, age_group),  # type: ignore[arg-type]
        urgency=normalize_enum(Urgency, urgency),  # type: ignore[arg-type]
        referral_status=normalize_enum(ReferralStatus, referral_status),  # type: ignore[arg-type]
        language=language,
        time_preferences=tuple(time_preferences),
        accessibility=tuple(accessibility),
        patient_authorized_helper=patient_authorized_helper,
        notes=notes,
    )


def _hebrew_script(request: AppointmentRequest, referral: str) -> str:
    access = f" חשוב לוודא נגישות: {', '.join(request.accessibility)}." if request.accessibility else ""
    return (
        f"שלום, אני חבר/ת {HMO_HEBREW[request.hmo]} ומבקש/ת לקבוע תור ל{request.service} "
        f"באזור {request.city}, בין {format_he_date(request.date_from)} ל-{format_he_date(request.date_to)}. "
        f"מצב הפניה/הזמנה: {referral}. מה התור הראשון הזמין ומה צריך להביא?{access}"
    )


def _english_script(request: AppointmentRequest, referral: str) -> str:
    return (
        f"Hello, I need to book {request.service} through {request.hmo.value} near {request.city}, "
        f"between {request.date_from.isoformat()} and {request.date_to.isoformat()}. "
        f"Referral/order status: {referral}. What is first available, what should be brought, and what is the cancellation policy?"
    )


class HealthcareAppointmentBookerClient:
    def __init__(self, adapter: AppointmentAdapter | None = None) -> None:
        self.adapter = adapter

    def plan(self, request: AppointmentRequest) -> BookingPlan:
        text = f"{request.service} {request.notes}"
        warnings: list[str] = []
        if contains_sensitive_secret(text):
            warnings.append("Sensitive data detected. Remove ID numbers, passwords, SMS codes, and medical files.")
        if has_emergency_red_flags(text, age_group=request.age_group) or request.urgency == Urgency.URGENT_SYMPTOMS:
            warnings.append("Emergency red flags detected. Contact 101, emergency room, or urgent HMO hotline.")
            return BookingPlan(
                request=request,
                recommended_channels=(Channel.EMERGENCY,),
                specialty="emergency",
                referral_required="not_applicable",
                priority="urgent_escalation",
                instructions=("Do not wait for a routine appointment.", "Contact emergency services or urgent HMO care.", "Resume booking only after immediate safety is addressed."),
                hebrew_script="אם קיימים סימני אזהרה, אין להמתין לתור שגרתי. פנו למד״א 101, למיון או למוקד דחוף של הקופה.",
                english_script="If emergency red flags are present, do not wait for routine booking. Contact emergency services or urgent HMO care.",
                documents_to_prepare=("HMO card/app login if safe and relevant",),
                fallbacks=("101", "Emergency room", "HMO urgent hotline"),
                warnings=tuple(warnings),
            )

        specialty = classify_specialty(request.service, age_group=request.age_group)
        referral = referral_requirement(specialty, request.referral_status)
        if request.urgency == Urgency.SAME_DAY or any(h in text.lower() for h in SAME_DAY_HINTS):
            priority = "same_day"
            channels = (Channel.URGENT_CARE, Channel.TELEHEALTH, Channel.CALL_CENTER, Channel.CLINIC_DESK)
        elif specialty == "admin":
            priority = "administrative"
            channels = (Channel.ADMIN_APPROVALS, Channel.OFFICIAL_WEBSITE, Channel.CALL_CENTER)
        else:
            priority = request.urgency.value
            channels = HMO_CHANNELS[request.hmo]

        instructions = self._instructions(request, specialty, referral)
        if specialty == "unknown":
            warnings.append("Service taxonomy is unclear. Search by Hebrew term or ask the official channel.")
        return BookingPlan(
            request=request,
            recommended_channels=channels,
            specialty=specialty,
            referral_required=referral,
            priority=priority,
            instructions=tuple(instructions),
            hebrew_script=_hebrew_script(request, referral),
            english_script=_english_script(request, referral),
            documents_to_prepare=self._documents(specialty, referral),
            fallbacks=("Expand search to nearby cities.", "Remove provider preference.", "Try telehealth where suitable.", "Call clinic desk for cancellations.", "Call HMO service center for district alternatives."),
            warnings=tuple(warnings),
        )

    def _instructions(self, request: AppointmentRequest, specialty: str, referral: str) -> list[str]:
        if specialty == "imaging":
            return ["Verify imaging order/referral validity.", "Check approval/Form 17 if required.", "Confirm preparation through official channel.", "Book through HMO or contracted institute."]
        if specialty == "lab":
            return ["Verify active lab order.", "Check if appointment or walk-in is required.", "Confirm fasting and medication instructions through official channel."]
        if specialty == "pediatrics" and request.urgency == Urgency.SAME_DAY:
            return ["Search same-day pediatrician availability.", "Check HMO urgent pediatric clinic or nurse triage.", "Escalate if emergency red flags appear."]
        if "required" in referral and request.referral_status != ReferralStatus.HAS_REFERRAL:
            return ["Search official app to confirm direct booking.", "If blocked, book family doctor or submit referral request.", "Repeat specialist search after referral approval."]
        if specialty == "admin":
            return ["Use HMO administrative approvals channel.", "Upload documents only through official portal.", "Track submission date and response."]
        return ["Use official HMO app or website first.", "Search by Hebrew service name and city.", "Compare earliest slot, location, language, and accessibility.", "Save confirmation number and cancellation deadline."]

    def _documents(self, specialty: str, referral: str) -> tuple[str, ...]:
        docs = ["HMO card or official app login entered by the user"]
        if "referral" in referral or specialty in REFERRAL_LIKELY:
            docs.append("Referral if required")
        if "order" in referral or specialty in ORDER_LIKELY:
            docs.append("Doctor order/test request if required")
        if specialty in {"imaging", "admin"}:
            docs.append("Approval/Form 17/commitment if required")
        docs.append("Confirmation number after booking")
        return tuple(docs)

    def search(self, request: AppointmentRequest) -> list[AppointmentOption]:
        if Channel.EMERGENCY in self.plan(request).recommended_channels:
            return []
        return [] if self.adapter is None else self.adapter.search(request)

    def book(self, request: AppointmentRequest, option: AppointmentOption | None = None) -> BookingResult:
        plan = self.plan(request)
        if Channel.EMERGENCY in plan.recommended_channels:
            return BookingResult(status="escalated", plan=plan, message="Routine booking stopped because emergency red flags were detected.")
        if self.adapter is None or option is None:
            return BookingResult(status="manual_action_required", plan=plan, message="Use the official HMO channel. No credentials or SMS codes should be handled.")
        return self.adapter.book(request, option)

    def rank_options(self, request: AppointmentRequest, options: Iterable[AppointmentOption]) -> list[AppointmentOption]:
        required_access = set(request.accessibility)
        def score(option: AppointmentOption) -> tuple[int, dt.datetime]:
            value = 0
            if option.city.casefold() == request.city.casefold():
                value -= 20
            if required_access.issubset(set(option.accessibility)):
                value -= 10
            if request.language and option.language.casefold().startswith(request.language.casefold()):
                value -= 5
            return value, option.starts_at
        return sorted(options, key=score)


class AsyncHealthcareAppointmentBookerClient:
    def __init__(self, adapter: AsyncAppointmentAdapter | None = None) -> None:
        self.adapter = adapter
        self.sync_client = HealthcareAppointmentBookerClient()

    async def plan(self, request: AppointmentRequest) -> BookingPlan:
        await asyncio.sleep(0)
        return self.sync_client.plan(request)

    async def search(self, request: AppointmentRequest) -> list[AppointmentOption]:
        plan = await self.plan(request)
        if Channel.EMERGENCY in plan.recommended_channels:
            return []
        if self.adapter is None:
            return []
        return await self.adapter.search(request)

    async def book(self, request: AppointmentRequest, option: AppointmentOption | None = None) -> BookingResult:
        plan = await self.plan(request)
        if Channel.EMERGENCY in plan.recommended_channels:
            return BookingResult(status="escalated", plan=plan, message="Emergency escalation required.")
        if self.adapter is None or option is None:
            return BookingResult(status="manual_action_required", plan=plan, message="Use official HMO channel.")
        return await self.adapter.book(request, option)


class InMemoryAppointmentAdapter:
    def __init__(self, options: Iterable[AppointmentOption] = ()) -> None:
        self.options = list(options)

    def search(self, request: AppointmentRequest) -> list[AppointmentOption]:
        matching = [o for o in self.options if request.date_from <= o.starts_at.date() <= request.date_to]
        return HealthcareAppointmentBookerClient().rank_options(request, matching)

    def book(self, request: AppointmentRequest, option: AppointmentOption) -> BookingResult:
        plan = HealthcareAppointmentBookerClient(self).plan(request)
        if option.requires_referral and request.referral_status != ReferralStatus.HAS_REFERRAL:
            return BookingResult(status="blocked", plan=plan, selected_option=option, message="Referral required before booking.")
        return BookingResult(status="confirmed_demo", plan=plan, selected_option=option, confirmation_number=f"LOCAL-{option.starts_at:%Y%m%d%H%M}", message="Demo adapter only; use official channel in production.")


def plan_from_mapping(payload: Mapping[str, Any]) -> BookingPlan:
    return HealthcareAppointmentBookerClient().plan(build_request(
        hmo=payload["hmo"],
        service=payload["service"],
        city=payload["city"],
        date_from=payload["date_from"],
        date_to=payload["date_to"],
        age_group=payload.get("age_group", "adult"),
        urgency=payload.get("urgency", "routine"),
        referral_status=payload.get("referral_status", "unknown"),
        language=payload.get("language", "he"),
        time_preferences=payload.get("time_preferences", ()),
        accessibility=payload.get("accessibility", ()),
        patient_authorized_helper=payload.get("patient_authorized_helper", True),
        notes=payload.get("notes", ""),
    ))


def render_text_plan(plan: BookingPlan, *, hebrew: bool = False) -> str:
    if hebrew:
        lines = [
            "תוכנית קביעת תור",
            f"קופה: {HMO_HEBREW[plan.request.hmo]}",
            f"שירות: {plan.request.service}",
            f"אזור: {plan.request.city}",
            f"דחיפות: {plan.priority}",
            f"ניתוב: {plan.specialty}",
            f"הפניה/הזמנה: {plan.referral_required}",
            "ערוצים מומלצים: " + ", ".join(c.value for c in plan.recommended_channels),
            "פעולות:",
            *[f"- {i}" for i in plan.instructions],
            "נוסח פנייה:",
            plan.hebrew_script,
            "אזהרות:",
            *[f"- {w}" for w in (plan.warnings or ("אין",))],
        ]
        return "\n".join(lines)
    lines = [
        "Appointment booking plan",
        f"HMO: {plan.request.hmo.value}",
        f"Service: {plan.request.service}",
        f"Area: {plan.request.city}",
        f"Priority: {plan.priority}",
        f"Specialty routing: {plan.specialty}",
        f"Referral/order: {plan.referral_required}",
        "Recommended channels: " + ", ".join(c.value for c in plan.recommended_channels),
        "Instructions:",
        *[f"- {i}" for i in plan.instructions],
        "Booking script:",
        plan.english_script,
        "Warnings:",
        *[f"- {w}" for w in (plan.warnings or ("None",))],
    ]
    return "\n".join(lines)
