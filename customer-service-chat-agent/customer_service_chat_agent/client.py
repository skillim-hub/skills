"""Hebrew-first customer-service chat agent core library.

The library provides a small deterministic service layer for FAQ handling,
triage, handoff packets, ticket creation demos, and tests. Production systems
should connect the same interfaces to approved business knowledge, order
systems, accounting tools, payment providers, and helpdesk queues.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Protocol, Sequence


class Intent(str, Enum):
    """Supported customer-service intents."""

    HOURS = "hours"
    LOCATION = "location"
    PRICE = "price"
    QUOTE = "quote"
    ORDER_STATUS = "order_status"
    DELIVERY = "delivery"
    RETURN = "return"
    REFUND = "refund"
    PAYMENT = "payment"
    INVOICE = "invoice"
    BOOKING = "booking"
    TECH_SUPPORT = "tech_support"
    PRIVACY = "privacy"
    ACCESSIBILITY = "accessibility"
    COMPLAINT = "complaint"
    LEGAL = "legal"
    SAFETY = "safety"
    PROMPT_INJECTION = "prompt_injection"
    UNKNOWN = "unknown"


class Urgency(str, Enum):
    """Handoff urgency levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Environment(str, Enum):
    """Runtime environment marker used by examples and CLI."""

    SANDBOX = "sandbox"
    PRODUCTION = "production"


@dataclass(frozen=True)
class BusinessProfile:
    """Business configuration used by the agent."""

    public_name: str = "העסק"
    legal_name: str = ""
    locale: str = "he-IL"
    currency_symbol: str = "₪"
    date_format: str = "DD/MM/YYYY"
    hours: Mapping[str, str] = field(default_factory=lambda: {
        "sun-thu": "09:00-18:00",
        "fri": "09:00-13:00",
        "sat": "סגור",
    })
    address: str = ""
    service_area: str = "ישראל"
    vat_wording: str = "כולל מע״מ"
    human_sla: str = "יום עסקים אחד"
    contact_email: str = "support@example.co.il"
    phone: str = ""
    payment_methods: Sequence[str] = field(default_factory=lambda: ("אשראי", "ביט", "העברה בנקאית"))
    prices: Mapping[str, str] = field(default_factory=lambda: {
        "consultation": "₪250 כולל מע״מ",
        "ייעוץ": "₪250 כולל מע״מ",
    })
    return_policy: str = "החזרה נבדקת לפי מדיניות העסק, מצב המוצר ותאריך הרכישה."
    delivery_policy: str = "משלוח בדרך כלל נמשך 1-3 ימי עסקים, בהתאם לאזור ולחברת השליחויות."


@dataclass(frozen=True)
class CustomerContext:
    """Optional customer details available to the agent."""

    name: Optional[str] = None
    contact: Optional[str] = None
    order_number: Optional[str] = None
    language: str = "he"
    channel: str = "chat"


@dataclass(frozen=True)
class Classification:
    """Classification result for a customer message."""

    intent: Intent
    confidence: float
    urgency: Urgency = Urgency.NORMAL
    risk_flags: Sequence[str] = field(default_factory=tuple)
    requires_handoff: bool = False
    missing_fields: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class AgentResponse:
    """Customer-safe response and optional handoff payload."""

    message: str
    classification: Classification
    handoff: Optional[Mapping[str, Any]] = None
    collected_fields: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Ticket:
    """Created handoff ticket representation."""

    ticket_id: str
    status: str
    environment: Environment
    payload: Mapping[str, Any]


class OrderLookup(Protocol):
    """Protocol for synchronous order lookup integrations."""

    def __call__(self, order_number: str) -> Mapping[str, Any]:
        ...


class AsyncOrderLookup(Protocol):
    """Protocol for asynchronous order lookup integrations."""

    async def __call__(self, order_number: str) -> Mapping[str, Any]:
        ...


@dataclass
class MemoryTicketStore:
    """Simple in-memory ticket store for CLI and examples."""

    tickets: MutableMapping[str, Ticket] = field(default_factory=dict)

    def create(self, payload: Mapping[str, Any], environment: Environment = Environment.SANDBOX) -> Ticket:
        """Create a ticket and return its generated identifier."""
        ticket_id = f"TCK-{uuid.uuid4().hex[:8].upper()}"
        ticket = Ticket(ticket_id=ticket_id, status="open", environment=environment, payload=dict(payload))
        self.tickets[ticket_id] = ticket
        return ticket

    def get(self, ticket_id: str) -> Optional[Ticket]:
        """Return a ticket by identifier."""
        return self.tickets.get(ticket_id)


@dataclass
class CustomerServiceChatAgent:
    """Rule-based helper suitable for tests, CLI demos, and integration scaffolding."""

    business: BusinessProfile = field(default_factory=BusinessProfile)
    order_lookup: Optional[OrderLookup] = None
    async_order_lookup: Optional[AsyncOrderLookup] = None
    ticket_store: MemoryTicketStore = field(default_factory=MemoryTicketStore)

    def classify(self, message: str, context: Optional[CustomerContext] = None) -> Classification:
        """Classify a customer message into intent, urgency, and handoff need."""
        text = normalize_text(message)
        risk_flags: List[str] = []

        if not text:
            return Classification(Intent.UNKNOWN, 0.2, missing_fields=("message",))

        if contains_prompt_injection(text):
            risk_flags.append("prompt_injection")
            if contains_any(text, ["refund", "החזר", "זיכוי"]):
                return Classification(Intent.REFUND, 0.95, Urgency.HIGH, tuple(risk_flags + ["refund_approval_needed"]), True)
            return Classification(Intent.PROMPT_INJECTION, 0.95, Urgency.HIGH, tuple(risk_flags), True)

        if contains_any(text, ["התאבד", "לפגוע בעצמי", "פגיעה עצמית", "איום", "איומים", "סכנה", "נפצע", "פציעה"]):
            return Classification(Intent.SAFETY, 0.95, Urgency.CRITICAL, ("safety",), True)

        if contains_any(text, ["תביעה", "אתבע", "עורך דין", "עו״ד", "עו\"ד", "חוקי", "לא חוקי"]):
            return Classification(Intent.LEGAL, 0.9, Urgency.HIGH, ("legal",), True)

        if contains_any(text, ["מחקו את המידע", "מחיקת מידע", "תמחקו אותי", "תמחקו את כל המידע", "הסירו אותי", "איזה מידע שמרתם", "ייצוא מידע", "פרטיות"]):
            return Classification(Intent.PRIVACY, 0.95, Urgency.HIGH, ("privacy_request",), True, missing_fields=("contact",) if not (context and context.contact) else ())

        if contains_any(text, ["קורא מסך", "נגיש", "נגישות", "לא נגיש"]):
            return Classification(Intent.ACCESSIBILITY, 0.9, Urgency.HIGH, ("accessibility",), True)

        if contains_any(text, ["חיוב כפול", "חייבתם פעמיים", "חייבתם אותי פעמיים", "ירד לי פעמיים", "לא אישרתי חיוב", "חיוב לא מורשה"]):
            return Classification(Intent.PAYMENT, 0.95, Urgency.HIGH, ("payment_dispute",), True, missing_fields=("order_number_or_payment_reference",))

        if contains_any(text, ["גנבים", "רמאים", "שירות גרוע", "בושה", "כועס", "זוועה"]):
            return Classification(Intent.COMPLAINT, 0.85, Urgency.HIGH, ("angry_customer",), True)

        if contains_any(text, ["החזר כספי", "תחזירו לי כסף", "refund", "זיכוי", "מוצר פגום", "שבור", "הגיע פגום"]):
            flags = ["refund_approval_needed"]
            if contains_any(text, ["פגום", "שבור", "damaged"]):
                flags.append("damaged_item")
            return Classification(Intent.REFUND, 0.95, Urgency.HIGH, tuple(flags), True, missing_fields=missing_order_field(context))

        if contains_any(text, ["להחזיר", "החזרה", "להחליף", "ביטול הזמנה", "לבטל הזמנה"]):
            return Classification(Intent.RETURN, 0.85, missing_fields=missing_order_field(context))

        if contains_any(text, ["חשבונית", "קבלה", "חשבונית מס", "ח.פ", "חפ", "עוסק פטור", "עוסק מורשה", "מע״מ", "מעמ"]):
            if contains_any(text, ["מה לרשום", "איך לחשב", "האם לגבות", "ייעוץ", "מס"]):
                return Classification(Intent.INVOICE, 0.9, Urgency.HIGH, ("accounting_interpretation",), True)
            return Classification(Intent.INVOICE, 0.88, missing_fields=("order_number", "billing_details"))

        if contains_any(text, ["איפה ההזמנה", "סטטוס הזמנה", "מספר הזמנה", "הזמנה", "מעקב"]):
            return Classification(Intent.ORDER_STATUS, 0.9, missing_fields=missing_order_field(context))

        if contains_any(text, ["משלוח", "שליח", "מתי יגיע", "איחר", "לא הגיע", "נמסר ולא קיבלתי"]):
            if contains_any(text, ["איחר", "לא הגיע", "נמסר ולא קיבלתי"]):
                return Classification(Intent.DELIVERY, 0.9, Urgency.HIGH, ("delivery_issue",), True, missing_fields=missing_order_field(context))
            return Classification(Intent.DELIVERY, 0.82)

        if contains_any(text, ["כמה עולה", "מחיר", "עלות", "תעריף", "הנחה"]):
            if contains_any(text, ["אתר", "פרויקט", "מותאם", "custom", "הצעת מחיר"]):
                return Classification(Intent.QUOTE, 0.86, missing_fields=("scope", "deadline"))
            return Classification(Intent.PRICE, 0.82)

        if contains_any(text, ["פתוחים", "שעות", "מתי אתם", "יום שישי", "בשישי", "היום"]):
            return Classification(Intent.HOURS, 0.82)

        if contains_any(text, ["איפה אתם", "כתובת", "מיקום", "חניה", "איך מגיעים"]):
            return Classification(Intent.LOCATION, 0.82)

        if contains_any(text, ["תור", "פגישה", "לקבוע", "זמינות", "מחר בערב"]):
            return Classification(Intent.BOOKING, 0.82, missing_fields=("service_type",))

        if contains_any(text, ["לא עובד", "תקלה", "להתחבר", "סיסמה", "קוד חד", "שגיאה"]):
            return Classification(Intent.TECH_SUPPORT, 0.82)

        if contains_any(text, ["ביט", "אשראי", "העברה בנקאית", "לשלם", "תשלום"]):
            return Classification(Intent.PAYMENT, 0.78)

        return Classification(Intent.UNKNOWN, 0.35, missing_fields=("intent",))

    def reply(self, message: str, context: Optional[CustomerContext] = None) -> AgentResponse:
        """Return a customer-safe reply and optional handoff payload."""
        context = context or CustomerContext()
        classification = self.classify(message, context)

        if classification.requires_handoff:
            handoff = self.create_handoff(message, classification, context)
            return AgentResponse(self._handoff_message(classification), classification, handoff)

        intent = classification.intent

        if intent is Intent.HOURS:
            msg = f"שעות הפעילות הן א׳-ה׳ {self.business.hours.get('sun-thu', 'לא הוגדר')} וביום ו׳ {self.business.hours.get('fri', 'לא הוגדר')}. בשבת: {self.business.hours.get('sat', 'לא הוגדר')}."
        elif intent is Intent.LOCATION:
            msg = self.business.address and f"הכתובת היא {self.business.address}." or "אין כתובת מאומתת להצגה. אפשר להשאיר פרטי קשר ונציג יחזור עם הכוונה."
        elif intent is Intent.PRICE:
            msg = self._price_reply(message)
        elif intent is Intent.QUOTE:
            msg = "כדי לתת הצעת מחיר מדויקת צריך סוג שירות, היקף עבודה ותאריך יעד רצוי. אחרי קבלת הפרטים אפשר להעביר לבדיקה."
        elif intent is Intent.ORDER_STATUS:
            msg = self._order_status_reply(context)
        elif intent is Intent.DELIVERY:
            msg = self.business.delivery_policy
        elif intent is Intent.RETURN:
            msg = f"{self.business.return_policy} כדי לבדוק התאמה למדיניות צריך מספר הזמנה, תאריך רכישה ומצב המוצר."
        elif intent is Intent.INVOICE:
            msg = "אפשר לטפל בזה. צריך מספר הזמנה, שם לחשבונית, ח.פ./ע.מ. אם מדובר בעסק, ודוא״ל לשליחה."
        elif intent is Intent.BOOKING:
            msg = "כדי לבדוק תור פנוי צריך סוג שירות ותאריך או טווח שעות רצוי. לא לקבוע תור בלי אישור מפורש."
        elif intent is Intent.TECH_SUPPORT:
            msg = "אפשר לנסות רענון, איפוס סיסמה דרך הקישור הרשמי או דפדפן אחר. לא לשלוח כאן סיסמה או קוד חד־פעמי. אם זה נמשך, כדאי לצרף דוא״ל חשבון ותיאור שגיאה."
        elif intent is Intent.PAYMENT:
            methods = ", ".join(self.business.payment_methods)
            msg = f"אפשר לשלם באמצעים המאושרים: {methods}. אין לשלוח מספר כרטיס אשראי מלא בצ׳אט."
        else:
            msg = "אשמח לעזור. אפשר לכתוב בכמה מילים מה צריך לבדוק?"

        return AgentResponse(msg, classification)

    async def areply(self, message: str, context: Optional[CustomerContext] = None) -> AgentResponse:
        """Asynchronous reply variant.

        Uses async order lookup when provided; otherwise falls back to sync logic.
        """
        context = context or CustomerContext()
        classification = self.classify(message, context)
        if classification.requires_handoff:
            handoff = self.create_handoff(message, classification, context)
            return AgentResponse(self._handoff_message(classification), classification, handoff)

        if classification.intent is Intent.ORDER_STATUS and context.order_number and self.async_order_lookup:
            try:
                data = await self.async_order_lookup(context.order_number)
                message_out = format_order_status(data)
                return AgentResponse(message_out, classification, collected_fields={"order": data})
            except Exception:
                handoff_classification = Classification(
                    Intent.ORDER_STATUS,
                    classification.confidence,
                    Urgency.HIGH,
                    ("tool_failure",),
                    True,
                )
                return AgentResponse(self._handoff_message(handoff_classification), handoff_classification, self.create_handoff(message, handoff_classification, context))

        return self.reply(message, context)

    def create_handoff(self, message: str, classification: Classification, context: Optional[CustomerContext] = None) -> Mapping[str, Any]:
        """Create a structured handoff packet."""
        context = context or CustomerContext()
        return {
            "customer_language": context.language,
            "customer_name": context.name,
            "contact": context.contact,
            "intent": classification.intent.value,
            "urgency": classification.urgency.value,
            "summary": summarize_for_handoff(message, classification),
            "details_collected": {
                "order_number": context.order_number,
                "channel": context.channel,
            },
            "risk_flags": list(classification.risk_flags),
            "recommended_next_action": recommended_next_action(classification),
        }

    def create_ticket(self, message: str, context: Optional[CustomerContext] = None, environment: Environment = Environment.SANDBOX) -> Ticket:
        """Create a handoff ticket and return its identifier."""
        context = context or CustomerContext()
        classification = self.classify(message, context)
        payload = self.create_handoff(message, classification, context)
        return self.ticket_store.create(payload, environment)

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get a ticket by identifier from the in-memory store."""
        return self.ticket_store.get(ticket_id)

    def _price_reply(self, message: str) -> str:
        text = normalize_text(message)
        for key, price in self.business.prices.items():
            if normalize_text(key) in text:
                return f"המחיר המאושר הוא {price}."
        if contains_any(text, ["ייעוץ", "שיחת ייעוץ", "consultation"]):
            return f"המחיר לשיחת ייעוץ הוא {self.business.prices.get('consultation', 'לא הוגדר')}."
        return "אין מחיר מאומת לשירות הזה. כדי לא להטעות, צריך להעביר פרטים להצעת מחיר."

    def _order_status_reply(self, context: CustomerContext) -> str:
        if not context.order_number:
            return "כדי לבדוק סטטוס הזמנה צריך מספר הזמנה או מספר טלפון ששויך להזמנה."
        if not self.order_lookup:
            return "אין כרגע חיבור מאומת לבדיקת הזמנות. אפשר להעביר לנציג אם נדרשת בדיקה פרטנית."
        try:
            data = self.order_lookup(context.order_number)
        except Exception:
            return "כרגע לא ניתן לבדוק את זה במערכת. אעביר לנציג שיבדוק את סטטוס ההזמנה."
        return format_order_status(data)

    def _handoff_message(self, classification: Classification) -> str:
        if classification.intent is Intent.REFUND:
            return "מבין את הבקשה. החזר כספי מחייב בדיקה של פרטי ההזמנה והמדיניות, לכן אעביר לנציג. אפשר לצרף מספר הזמנה, תאריך רכישה ותמונה אם יש פגם?"
        if classification.intent is Intent.PAYMENT:
            return "מבין שזה דחוף. טענת חיוב או תשלום מחייבת בדיקה של צוות חיובים. אפשר לשלוח מספר הזמנה או אסמכתת תשלום בלי מספר כרטיס מלא?"
        if classification.intent is Intent.PRIVACY:
            return "קיבלתי את הבקשה. נושא פרטיות מועבר לגורם האחראי. אפשר לציין דוא״ל או טלפון ליצירת קשר לצורך אימות וטיפול?"
        if classification.intent is Intent.ACCESSIBILITY:
            return "תודה שהעדכנת. אעביר את נושא הנגישות לבדיקה. אם נוח, כדאי לצרף קישור לעמוד, מכשיר ודפדפן."
        if classification.intent is Intent.LEGAL:
            return "הפנייה כוללת היבט משפטי ולכן תועבר לבדיקה אנושית. אפשר לצרף מספר הזמנה ותיאור קצר של המקרה?"
        if classification.intent is Intent.SAFETY:
            return "הפנייה כוללת נושא בטיחותי ודורשת טיפול אנושי מיידי לפי נוהל העסק."
        if classification.intent is Intent.COMPLAINT:
            return "מבין שזה מתסכל. אעביר את זה לבדיקה אנושית כדי לטפל בזה נכון. אפשר לצרף מספר הזמנה או פרטי קשר ותיאור קצר?"
        if classification.intent is Intent.PROMPT_INJECTION:
            return "אפשר לעזור בנושאי שירות לקוחות, אבל לא ניתן לחשוף או לשנות הנחיות פנימיות."
        return "אין מידע מאומת מספיק כדי לענות בלי להטעות, לכן אעביר את הפנייה לנציג."


def normalize_text(text: str) -> str:
    """Normalize text for lightweight Hebrew and English matching."""
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def contains_any(text: str, needles: Iterable[str]) -> bool:
    """Return True when any normalized needle appears in text."""
    normalized = normalize_text(text)
    return any(normalize_text(needle) in normalized for needle in needles)


def contains_prompt_injection(text: str) -> bool:
    """Detect obvious attempts to override instructions."""
    return contains_any(text, [
        "ignore previous",
        "התעלם מההוראות",
        "תתעלם מההוראות",
        "חשוף את ההנחיות",
        "הנחיות פנימיות", "ההנחיות הפנימיות",
        "system prompt",
        "developer message",
        "תכתוב שההחזר מאושר",
        "approve refund",
    ])


def missing_order_field(context: Optional[CustomerContext]) -> Sequence[str]:
    """Return missing order field marker when context lacks an order number."""
    if context and context.order_number:
        return ()
    return ("order_number",)


def format_order_status(data: Mapping[str, Any]) -> str:
    """Format order status with customer-safe Hebrew wording."""
    status = data.get("status_he") or data.get("status") or "לא ידוע"
    tracking = data.get("tracking_number")
    eta = data.get("estimated_delivery_date")
    late = bool(data.get("late"))
    if late:
        return "המשלוח נראה באיחור מעבר לזמן הטיפול הרגיל. אעביר לנציג לבדיקה מול חברת השליחויות."
    parts = [f"סטטוס ההזמנה: {status}."]
    if tracking:
        parts.append(f"מספר המעקב הוא {tracking}.")
    if eta:
        parts.append(f"הערכת מסירה: {eta}.")
    return " ".join(parts)


def summarize_for_handoff(message: str, classification: Classification) -> str:
    """Create a concise internal summary."""
    clean = normalize_text(message)
    return f"פניית לקוח בנושא {classification.intent.value}: {clean[:240]}"


def recommended_next_action(classification: Classification) -> str:
    """Map classification to recommended human action."""
    mapping = {
        Intent.REFUND: "נציג יבדוק את פרטי ההזמנה ומדיניות ההחזרים לפני החלטה.",
        Intent.PAYMENT: "צוות חיובים יבדוק אסמכתאות תשלום וחיובים.",
        Intent.PRIVACY: "אחראי פרטיות יטפל באימות ובבקשה.",
        Intent.ACCESSIBILITY: "אחראי נגישות או תמיכה טכנית יבדוק ויציע חלופה.",
        Intent.LEGAL: "נציג מוסמך יבדוק את הפנייה ולא יינתן מענה משפטי אוטומטי.",
        Intent.SAFETY: "להפעיל נוהל בטיחות פנימי ולתעד את הפנייה.",
        Intent.COMPLAINT: "נציג שירות בכיר יבדוק את פרטי המקרה ויחזור ללקוח.",
    }
    return mapping.get(classification.intent, "נציג יבדוק את הפנייה ויחזור לפי SLA.")


def load_business_profile(path: str | Path) -> BusinessProfile:
    """Load a business profile from JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    allowed = {field.name for field in dataclasses.fields(BusinessProfile)}
    filtered = {k: v for k, v in data.items() if k in allowed}
    return BusinessProfile(**filtered)


def classification_to_dict(classification: Classification) -> Dict[str, Any]:
    """Convert a classification object to a JSON-ready dictionary."""
    return {
        "intent": classification.intent.value,
        "confidence": classification.confidence,
        "urgency": classification.urgency.value,
        "risk_flags": list(classification.risk_flags),
        "requires_handoff": classification.requires_handoff,
        "missing_fields": list(classification.missing_fields),
    }


def ticket_to_dict(ticket: Ticket) -> Dict[str, Any]:
    """Convert a ticket object to a JSON-ready dictionary."""
    return {
        "ticket_id": ticket.ticket_id,
        "status": ticket.status,
        "environment": ticket.environment.value,
        "payload": ticket.payload,
    }


def response_to_dict(response: AgentResponse) -> Dict[str, Any]:
    """Convert an AgentResponse to a JSON-ready dictionary."""
    return {
        "message": response.message,
        "classification": classification_to_dict(response.classification),
        "handoff": response.handoff,
        "collected_fields": dict(response.collected_fields),
    }


def response_to_json(response: AgentResponse) -> str:
    """Serialize an AgentResponse to JSON."""
    return json.dumps(response_to_dict(response), ensure_ascii=False, indent=2)


async def demo_async_reply(message: str) -> AgentResponse:
    """Small async demo helper."""
    async def lookup(order_number: str) -> Mapping[str, Any]:
        await asyncio.sleep(0)
        return {
            "order_id": order_number,
            "status_he": "נשלחה",
            "tracking_number": "IL123456789",
            "estimated_delivery_date": "05/06/2026",
            "late": False,
        }

    agent = CustomerServiceChatAgent(async_order_lookup=lookup)
    return await agent.areply(message, CustomerContext(order_number="10493"))


__all__ = [
    "AgentResponse",
    "BusinessProfile",
    "Classification",
    "CustomerContext",
    "CustomerServiceChatAgent",
    "Environment",
    "Intent",
    "MemoryTicketStore",
    "Ticket",
    "Urgency",
    "classification_to_dict",
    "contains_any",
    "contains_prompt_injection",
    "format_order_status",
    "load_business_profile",
    "normalize_text",
    "response_to_dict",
    "response_to_json",
    "ticket_to_dict",
]
