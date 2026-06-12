from __future__ import annotations

import asyncio
import hashlib
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Mapping, Optional


class Environment(str, Enum):
    """Runtime environment."""

    SANDBOX = "sandbox"
    PRODUCTION = "production"


class Channel(str, Enum):
    """Supported service channels."""

    WHATSAPP = "whatsapp"
    EMAIL = "email"
    CHAT = "chat"
    PHONE_NOTE = "phone_note"
    SOCIAL = "social"
    OTHER = "other"


class Language(str, Enum):
    """Supported customer language codes."""

    HE = "he"
    EN = "en"
    RU = "ru"
    AR = "ar"
    UNKNOWN = "unknown"


class Risk(str, Enum):
    """Operational risk level for a support message."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class SupportContext:
    """Known information about the customer interaction."""

    channel: Channel = Channel.CHAT
    order_id: Optional[str] = None
    customer_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    last4: Optional[str] = None
    amount: Optional[float] = None
    purchase_date: Optional[date] = None
    received_date: Optional[date] = None
    business_name: Optional[str] = None
    policy_hint: Optional[str] = None
    extra: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SupportAnalysis:
    """Structured result returned by the support helper."""

    language: Language
    intent: str
    risk: Risk
    reply: str
    internal_note: str
    missing_fields: list[str] = field(default_factory=list)
    escalation: Optional[str] = None
    case_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the result to JSON-ready data."""

        return {
            "language": self.language.value,
            "intent": self.intent,
            "risk": self.risk.value,
            "reply": self.reply,
            "internal_note": self.internal_note,
            "missing_fields": list(self.missing_fields),
            "escalation": self.escalation,
            "case_id": self.case_id,
        }


HEBREW_RE = re.compile(r"[\u0590-\u05FF]")
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")

HIGH_RISK_TERMS = (
    "lawyer",
    "attorney",
    "lawsuit",
    "chargeback",
    "privacy",
    "delete my data",
    "personal data",
    "data breach",
    "injury",
    "unsafe",
    "discrimination",
    "harassment",
    "self harm",
    "suicide",
    "עורך דין",
    "תביעה",
    "הכחשת עסקה",
    "פרטיות",
    "מחק",
    "מידע אישי",
    "דליפה",
    "פציעה",
    "מסוכן",
    "אפליה",
    "הטרדה",
    "محامي",
    "دعوى",
    "استرجاع بنكي",
    "خصوصية",
    "احذف",
    "بيانات شخصية",
    "تسريب",
    "إصابة",
    "خطر",
    "تمييز",
    "تحرش",
    "юрист",
    "адвокат",
    "иск",
    "чарджбэк",
    "конфиденциальность",
    "удалите данные",
    "персональные данные",
    "утечка",
    "травма",
    "опасно",
    "дискриминация",
)

MEDIUM_RISK_TERMS = (
    "refund",
    "return",
    "broken",
    "late",
    "charged twice",
    "duplicate charge",
    "cancel",
    "warranty",
    "החזר",
    "החזרה",
    "שבור",
    "תקול",
    "מאחר",
    "חויבתי פעמיים",
    "ביטול",
    "אחריות",
    "استرداد",
    "إرجاع",
    "مكسور",
    "تالف",
    "متأخر",
    "دفع مرتين",
    "إلغاء",
    "ضمان",
    "возврат",
    "верните деньги",
    "слом",
    "задерж",
    "двойное списание",
    "отмена",
    "гарант",
)

INTENT_TERMS: dict[str, tuple[str, ...]] = {
    "delivery_status": (
        "delivery",
        "shipment",
        "package",
        "tracking",
        "courier",
        "משלוח",
        "שליח",
        "חבילה",
        "מעקב",
        "הזמנה",
        "توصيل",
        "شحنة",
        "طرد",
        "تتبع",
        "طلب",
        "доставка",
        "посыл",
        "трек",
        "заказ",
    ),
    "refund_request": (
        "refund",
        "return",
        "money back",
        "cancel purchase",
        "החזר",
        "החזרה",
        "זיכוי",
        "ביטול עסקה",
        "استرداد",
        "إرجاع",
        "إلغاء",
        "возврат",
        "верните деньги",
        "отмена",
    ),
    "invoice_request": (
        "invoice",
        "receipt",
        "tax invoice",
        "חשבונית",
        "קבלה",
        "חשבונית מס",
        "מע״מ",
        'מע"מ',
        "فاتورة",
        "إيصال",
        "ضريبة",
        "счет",
        "счёт",
        "чек",
        "налог",
    ),
    "payment_issue": (
        "charged",
        "payment",
        "card",
        "duplicate charge",
        "חיוב",
        "תשלום",
        "כרטיס",
        "חויבתי",
        "دفع",
        "بطاقة",
        "خصم",
        "оплата",
        "карта",
        "списание",
    ),
    "appointment": (
        "appointment",
        "meeting",
        "reschedule",
        "תור",
        "פגישה",
        "לקבוע",
        "להזיז",
        "موعد",
        "لقاء",
        "تغيير الموعد",
        "встреч",
        "запис",
        "перенести",
    ),
    "privacy_request": (
        "privacy",
        "delete data",
        "personal data",
        "data request",
        "פרטיות",
        "מחק",
        "מידע אישי",
        "בקשת מידע",
        "خصوصية",
        "بيانات",
        "احذف",
        "данные",
        "удалите данные",
        "конфиденциальность",
    ),
    "complaint": (
        "complaint",
        "bad service",
        "terrible",
        "angry",
        "תלונה",
        "שירות גרוע",
        "מאוכזב",
        "شكوى",
        "خدمة سيئة",
        "غاضب",
        "жалоба",
        "плохой сервис",
        "недоволен",
    ),
}

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "delivery_status": ("order_id",),
    "refund_request": ("order_id", "purchase_date"),
    "invoice_request": ("order_id", "email"),
    "payment_issue": ("order_id", "last4"),
    "appointment": ("phone",),
    "privacy_request": ("email",),
    "complaint": ("order_id",),
    "general_support": (),
}

REPLY_TEMPLATES: dict[Language, dict[str, str]] = {
    Language.HE: {
        "delivery_status": "שלום{customer_part}, כדי לבדוק את סטטוס המשלוח יש לשלוח מספר הזמנה. לאחר אימות הפרטים תישלח תשובה עם הצעד הבא.",
        "refund_request": "שלום{customer_part}, בקשת ההחזר תיבדק לפי פרטי העסקה, מועד הרכישה ומדיניות העסק. יש לשלוח מספר הזמנה ותאריך רכישה בפורמט DD/MM/YYYY.",
        "invoice_request": "שלום{customer_part}, כדי להנפיק מסמך חשבונאי יש לשלוח מספר הזמנה וכתובת דואר אלקטרוני לקבלת המסמך. תיקון מסמך קיים מחייב בדיקה במערכת החשבונות.",
        "payment_issue": "שלום{customer_part}, חיוב כפול ייבדק מול פרטי העסקה וספק התשלומים. יש לשלוח מספר הזמנה וארבע ספרות אחרונות של אמצעי התשלום בלבד.",
        "appointment": "שלום{customer_part}, כדי לטפל בתור יש לשלוח מספר טלפון, מועד רצוי ושעות נוחות לחזרה.",
        "privacy_request": "שלום{customer_part}, בקשת פרטיות מחייבת אימות זהות וטיפול לפי נוהל העסק והדין החל. יש לשלוח כתובת דואר אלקטרוני לזיהוי הבקשה.",
        "complaint": "שלום{customer_part}, התלונה תיבדק מול פרטי ההזמנה ותיעוד השירות. יש לשלוח מספר הזמנה ותיאור קצר של מה שקרה.",
        "general_support": "שלום{customer_part}, תודה על הפנייה. יש לשלוח פרטים נוספים כדי לטפל בבקשה בצורה מדויקת.",
    },
    Language.EN: {
        "delivery_status": "Hello{customer_part}, send the order number to check the delivery status. After verification, the next step will be shared.",
        "refund_request": "Hello{customer_part}, the refund request will be checked against the transaction details, purchase date, and business policy. Send the order number and purchase date in DD/MM/YYYY format.",
        "invoice_request": "Hello{customer_part}, send the order number and email address for the accounting document. Corrections to an existing document require a check in the accounting system.",
        "payment_issue": "Hello{customer_part}, a duplicate charge will be checked against the transaction record and payment provider. Send the order number and only the last four digits of the payment method.",
        "appointment": "Hello{customer_part}, send a phone number, preferred date, and convenient hours for follow-up.",
        "privacy_request": "Hello{customer_part}, a privacy request requires identity verification and handling under the business procedure and applicable law. Send the email address linked to the request.",
        "complaint": "Hello{customer_part}, the complaint will be checked against the order details and service record. Send the order number and a short description of what happened.",
        "general_support": "Hello{customer_part}, thank you for contacting support. Send more details so the request can be handled accurately.",
    },
    Language.RU: {
        "delivery_status": "Здравствуйте{customer_part}, отправьте номер заказа для проверки статуса доставки. После проверки будет отправлен следующий шаг.",
        "refund_request": "Здравствуйте{customer_part}, запрос на возврат будет проверен по данным сделки, дате покупки и правилам бизнеса. Отправьте номер заказа и дату покупки в формате DD/MM/YYYY.",
        "invoice_request": "Здравствуйте{customer_part}, для подготовки бухгалтерского документа отправьте номер заказа и адрес электронной почты. Исправление существующего документа требует проверки в бухгалтерской системе.",
        "payment_issue": "Здравствуйте{customer_part}, двойное списание будет проверено по данным сделки и платежного провайдера. Отправьте номер заказа и только последние четыре цифры платежного средства.",
        "appointment": "Здравствуйте{customer_part}, отправьте номер телефона, желаемую дату и удобное время для связи.",
        "privacy_request": "Здравствуйте{customer_part}, запрос по персональным данным требует проверки личности и обработки по процедуре бизнеса и применимому праву. Отправьте адрес электронной почты, связанный с запросом.",
        "complaint": "Здравствуйте{customer_part}, жалоба будет проверена по данным заказа и истории обслуживания. Отправьте номер заказа и краткое описание произошедшего.",
        "general_support": "Здравствуйте{customer_part}, спасибо за обращение. Отправьте дополнительные детали, чтобы запрос был обработан точно.",
    },
    Language.AR: {
        "delivery_status": "مرحبًا{customer_part}، يرجى إرسال رقم الطلب لفحص حالة التوصيل. بعد التحقق سيتم إرسال الخطوة التالية.",
        "refund_request": "مرحبًا{customer_part}، سيتم فحص طلب الاسترداد وفق تفاصيل الصفقة وتاريخ الشراء وسياسة العمل. يرجى إرسال رقم الطلب وتاريخ الشراء بصيغة DD/MM/YYYY.",
        "invoice_request": "مرحبًا{customer_part}، لإصدار مستند محاسبي يرجى إرسال رقم الطلب وعنوان البريد الإلكتروني. تصحيح مستند قائم يتطلب فحصًا في نظام المحاسبة.",
        "payment_issue": "مرحبًا{customer_part}، سيتم فحص الخصم المكرر وفق سجل الصفقة ومزود الدفع. يرجى إرسال رقم الطلب وآخر أربع خانات فقط من وسيلة الدفع.",
        "appointment": "مرحبًا{customer_part}، يرجى إرسال رقم هاتف وتاريخ مفضل وساعات مناسبة للمتابعة.",
        "privacy_request": "مرحبًا{customer_part}، طلب الخصوصية يتطلب التحقق من الهوية والمعالجة وفق إجراءات العمل والقانون المطبق. يرجى إرسال عنوان البريد الإلكتروني المرتبط بالطلب.",
        "complaint": "مرحبًا{customer_part}، سيتم فحص الشكوى وفق تفاصيل الطلب وسجل الخدمة. يرجى إرسال رقم الطلب ووصفًا قصيرًا لما حدث.",
        "general_support": "مرحبًا{customer_part}، شكرًا لتواصلك. يرجى إرسال تفاصيل إضافية لمعالجة الطلب بدقة.",
    },
}

ESCALATION_TEXT: dict[Language, str] = {
    Language.HE: "להסלים לגורם מוסמך לפני שליחת תשובה סופית.",
    Language.EN: "Escalate to an authorized person before sending a final answer.",
    Language.RU: "Перед отправкой окончательного ответа передать ответственному специалисту.",
    Language.AR: "يجب التصعيد إلى جهة مخولة قبل إرسال رد نهائي.",
    Language.UNKNOWN: "Escalate if language or risk cannot be verified.",
}


def _coerce_context(context: SupportContext | Mapping[str, Any] | None) -> SupportContext:
    if context is None:
        return SupportContext()
    if isinstance(context, SupportContext):
        return context
    data = dict(context)
    if "channel" in data and isinstance(data["channel"], str):
        data["channel"] = Channel(data["channel"])
    for key in ("purchase_date", "received_date"):
        if isinstance(data.get(key), str):
            data[key] = _parse_date(data[key])
    allowed = {field.name for field in SupportContext.__dataclass_fields__.values()}
    return SupportContext(**{k: v for k, v in data.items() if k in allowed})


def _parse_date(value: str) -> date:
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError("date must use DD/MM/YYYY or ISO YYYY-MM-DD format")


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


class SupportAgentClient:
    """Rule-based helper for multilingual Israeli customer-service triage."""

    def __init__(
        self,
        *,
        environment: Environment | str = Environment.SANDBOX,
        business_name: Optional[str] = None,
        default_currency: str = "₪",
    ) -> None:
        self.environment = Environment(environment)
        self.business_name = business_name
        self.default_currency = default_currency

    def detect_language(self, text: str) -> Language:
        """Detect Hebrew, Arabic, Russian, English, or unknown from customer text."""

        if not text or not text.strip():
            return Language.UNKNOWN

        counts = {
            Language.HE: len(HEBREW_RE.findall(text)),
            Language.AR: len(ARABIC_RE.findall(text)),
            Language.RU: len(CYRILLIC_RE.findall(text)),
        }
        detected, count = max(counts.items(), key=lambda item: item[1])
        if count > 0:
            return detected
        if re.search(r"[A-Za-z]", text):
            return Language.EN
        return Language.UNKNOWN

    def classify_intent(self, text: str) -> str:
        """Classify the support intent using multilingual keywords."""

        for intent, terms in INTENT_TERMS.items():
            if _contains_any(text, terms):
                return intent
        return "general_support"

    def assess_risk(self, text: str, intent: Optional[str] = None) -> Risk:
        """Assess whether the request needs routine handling or escalation."""

        if _contains_any(text, HIGH_RISK_TERMS):
            return Risk.HIGH
        if intent == "privacy_request":
            return Risk.HIGH
        if _contains_any(text, MEDIUM_RISK_TERMS):
            return Risk.MEDIUM
        if intent in {"refund_request", "payment_issue"}:
            return Risk.MEDIUM
        return Risk.LOW

    def required_fields(self, intent: str) -> list[str]:
        """Return the required context fields for an intent."""

        return list(REQUIRED_FIELDS.get(intent, ()))

    def missing_fields(self, intent: str, context: SupportContext | Mapping[str, Any] | None = None) -> list[str]:
        """Return missing fields that should be requested from the customer."""

        ctx = _coerce_context(context)
        missing: list[str] = []
        for field_name in self.required_fields(intent):
            if not getattr(ctx, field_name):
                missing.append(field_name)
        return missing

    def format_currency(self, amount: float | int) -> str:
        """Format an amount for Israeli customer communication."""

        numeric = float(amount)
        if numeric.is_integer():
            return f"{self.default_currency}{int(numeric):,}"
        return f"{self.default_currency}{numeric:,.2f}"

    def format_date(self, value: date | datetime | str) -> str:
        """Format a date as DD/MM/YYYY."""

        if isinstance(value, datetime):
            date_value = value.date()
        elif isinstance(value, date):
            date_value = value
        elif isinstance(value, str):
            date_value = _parse_date(value)
        else:
            raise TypeError("value must be date, datetime, or supported date string")
        return date_value.strftime("%d/%m/%Y")

    def draft_reply(
        self,
        text: str,
        context: SupportContext | Mapping[str, Any] | None = None,
        *,
        force_language: Optional[Language | str] = None,
    ) -> SupportAnalysis:
        """Create a structured reply, internal note, missing-field list, and escalation hint."""

        ctx = _coerce_context(context)
        language = Language(force_language) if force_language else self.detect_language(text)
        if language == Language.UNKNOWN:
            language = Language.EN

        intent = self.classify_intent(text)
        risk = self.assess_risk(text, intent)
        missing = self.missing_fields(intent, ctx)
        customer_part = f" {ctx.customer_name}" if ctx.customer_name else ""

        reply = REPLY_TEMPLATES[language].get(intent, REPLY_TEMPLATES[language]["general_support"]).format(
            customer_part=customer_part
        )
        if ctx.amount is not None:
            reply += f" Amount on record: {self.format_currency(ctx.amount)}."
        if ctx.purchase_date is not None:
            reply += f" Purchase date on record: {self.format_date(ctx.purchase_date)}."

        escalation = ESCALATION_TEXT[language] if risk == Risk.HIGH else None
        case_id = self._case_id(text, ctx)
        internal_note = self._internal_note(intent, risk, missing, ctx, case_id)

        return SupportAnalysis(
            language=language,
            intent=intent,
            risk=risk,
            reply=reply,
            internal_note=internal_note,
            missing_fields=missing,
            escalation=escalation,
            case_id=case_id,
        )

    async def draft_reply_async(
        self,
        text: str,
        context: SupportContext | Mapping[str, Any] | None = None,
        *,
        force_language: Optional[Language | str] = None,
    ) -> SupportAnalysis:
        """Async variant of draft_reply for service frameworks."""

        await asyncio.sleep(0)
        return self.draft_reply(text, context, force_language=force_language)

    def create_case(
        self,
        text: str,
        context: SupportContext | Mapping[str, Any] | None = None,
        *,
        force_language: Optional[Language | str] = None,
    ) -> dict[str, Any]:
        """Create a local structured case response with a stable case identifier."""

        analysis = self.draft_reply(text, context, force_language=force_language)
        return {
            "case_id": analysis.case_id,
            "environment": self.environment.value,
            "analysis": analysis.to_dict(),
        }

    async def create_case_async(
        self,
        text: str,
        context: SupportContext | Mapping[str, Any] | None = None,
        *,
        force_language: Optional[Language | str] = None,
    ) -> dict[str, Any]:
        """Async variant of create_case."""

        await asyncio.sleep(0)
        return self.create_case(text, context, force_language=force_language)

    def add_message(
        self,
        case_id: str,
        text: str,
        context: SupportContext | Mapping[str, Any] | None = None,
        *,
        force_language: Optional[Language | str] = None,
    ) -> dict[str, Any]:
        """Analyze a follow-up message for an existing case."""

        if not case_id or not case_id.strip():
            raise ValueError("case_id is required")
        analysis = self.draft_reply(text, context, force_language=force_language)
        return {
            "case_id": case_id,
            "environment": self.environment.value,
            "analysis": analysis.to_dict(),
        }

    async def add_message_async(
        self,
        case_id: str,
        text: str,
        context: SupportContext | Mapping[str, Any] | None = None,
        *,
        force_language: Optional[Language | str] = None,
    ) -> dict[str, Any]:
        """Async variant of add_message."""

        await asyncio.sleep(0)
        return self.add_message(case_id, text, context, force_language=force_language)

    def _case_id(self, text: str, context: SupportContext) -> str:
        raw = "|".join(
            [
                self.environment.value,
                context.order_id or "",
                context.email or "",
                context.phone or "",
                text.strip().lower(),
            ]
        )
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
        return f"msa_{digest}"

    def _internal_note(self, intent: str, risk: Risk, missing: list[str], context: SupportContext, case_id: str) -> str:
        parts = [
            f"case_id={case_id}",
            f"intent={intent}",
            f"risk={risk.value}",
            f"channel={context.channel.value}",
        ]
        if missing:
            parts.append("missing=" + ",".join(missing))
        if context.order_id:
            parts.append(f"order_id={context.order_id}")
        return "; ".join(parts)


def format_analysis(analysis: SupportAnalysis | Mapping[str, Any]) -> dict[str, Any]:
    """Return JSON-ready output from a support analysis or response mapping."""

    if isinstance(analysis, SupportAnalysis):
        return analysis.to_dict()
    return dict(analysis)
