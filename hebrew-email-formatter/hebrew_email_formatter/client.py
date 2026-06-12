"""Professional Hebrew email formatting utilities."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

VAT_RATE = Decimal("0.18")
LOCALE = "he-IL"
DATE_FORMAT_LABEL = "DD/MM/YYYY"
DATE_FORMAT = "%d/%m/%Y"
ISRAEL_INVOICE_ALLOCATION_THRESHOLD_ILS = Decimal("5000")


class HebrewEmailError(ValueError):
    """Raised when a request contains an unsupported or invalid value."""


class Formality(str, Enum):
    FORMAL = "formal"
    NEUTRAL = "neutral"
    WARM = "warm"
    FIRM = "firm"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    PLURAL = "plural"
    NEUTRAL = "neutral"


class Purpose(str, Enum):
    PAYMENT_REMINDER = "payment_reminder"
    QUOTE = "quote"
    INVOICE_SENT = "invoice_sent"
    MEETING_REQUEST = "meeting_request"
    FOLLOW_UP = "follow_up"
    COMPLAINT_RESPONSE = "complaint_response"
    CONSUMER_COMPLAINT = "consumer_complaint"
    APOLOGY_DELAY = "apology_delay"
    CANCELLATION = "cancellation"
    STATUS_UPDATE = "status_update"


class SignatureStyle(str, Enum):
    MINIMAL = "minimal"
    BUSINESS = "business"
    TAX = "tax"


@dataclass(frozen=True)
class Contact:
    name: str = ""
    gender: Gender = Gender.NEUTRAL
    organization: str = ""
    title: str = ""
    is_company: bool = False

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "Contact":
        if not data:
            return cls()
        return cls(
            name=str(data.get("name", "") or ""),
            gender=parse_gender(data.get("gender", Gender.NEUTRAL)),
            organization=str(data.get("organization", "") or ""),
            title=str(data.get("title", "") or ""),
            is_company=bool(data.get("is_company", False)),
        )


@dataclass(frozen=True)
class Sender:
    name: str = ""
    gender: Gender = Gender.NEUTRAL
    business_name: str = ""
    role: str = ""
    phone: str = ""
    email: str = ""
    business_id: str = ""
    website: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "Sender":
        if not data:
            return cls()
        return cls(
            name=str(data.get("name", "") or ""),
            gender=parse_gender(data.get("gender", Gender.NEUTRAL)),
            business_name=str(data.get("business_name", "") or ""),
            role=str(data.get("role", "") or ""),
            phone=str(data.get("phone", "") or ""),
            email=str(data.get("email", "") or ""),
            business_id=str(data.get("business_id", "") or ""),
            website=str(data.get("website", "") or ""),
        )


@dataclass(frozen=True)
class EmailRequest:
    purpose: Purpose
    recipient: Contact = field(default_factory=Contact)
    sender: Sender = field(default_factory=Sender)
    formality: Formality = Formality.NEUTRAL
    facts: Mapping[str, Any] = field(default_factory=dict)
    signature_style: SignatureStyle = SignatureStyle.BUSINESS
    include_review_notes: bool = True
    environment: str = "sandbox"


@dataclass(frozen=True)
class EmailDraft:
    id: str
    subject: str
    body: str
    warnings: List[str] = field(default_factory=list)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def render(self, include_subject: bool = True, include_warnings: bool = True) -> str:
        parts: List[str] = []
        if include_subject:
            parts.extend([f"נושא: {self.subject}", ""])
        parts.append(self.body)
        if include_warnings and self.warnings:
            parts.extend(["", "הערות בדיקה:"])
            parts.extend(f"- {warning}" for warning in self.warnings)
        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "subject": self.subject,
            "body": self.body,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }

    def to_json(self, ensure_ascii: bool = False, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


def parse_gender(value: Any) -> Gender:
    if isinstance(value, Gender):
        return value
    normalized = str(value or "neutral").strip().lower()
    aliases = {
        "m": Gender.MALE, "male": Gender.MALE, "זכר": Gender.MALE,
        "f": Gender.FEMALE, "female": Gender.FEMALE, "נקבה": Gender.FEMALE,
        "plural": Gender.PLURAL, "team": Gender.PLURAL, "רבים": Gender.PLURAL,
        "neutral": Gender.NEUTRAL, "unknown": Gender.NEUTRAL, "לא ידוע": Gender.NEUTRAL, "": Gender.NEUTRAL,
    }
    if normalized not in aliases:
        raise HebrewEmailError(f"Unsupported gender: {value}")
    return aliases[normalized]


def parse_formality(value: Any) -> Formality:
    if isinstance(value, Formality):
        return value
    try:
        return Formality(str(value or "neutral").strip().lower())
    except ValueError as exc:
        raise HebrewEmailError(f"Unsupported formality: {value}") from exc


def parse_purpose(value: Any) -> Purpose:
    if isinstance(value, Purpose):
        return value
    try:
        return Purpose(str(value or "").strip().lower())
    except ValueError as exc:
        raise HebrewEmailError(f"Unsupported purpose: {value}") from exc


def parse_signature_style(value: Any) -> SignatureStyle:
    if isinstance(value, SignatureStyle):
        return value
    try:
        return SignatureStyle(str(value or "business").strip().lower())
    except ValueError as exc:
        raise HebrewEmailError(f"Unsupported signature style: {value}") from exc


def parse_environment(value: Any) -> str:
    normalized = str(value or "sandbox").strip().lower()
    if normalized not in {"sandbox", "production"}:
        raise HebrewEmailError("Environment must be sandbox or production")
    return normalized


def parse_decimal(value: Any) -> Decimal:
    if value is None or value == "":
        raise HebrewEmailError("Amount is required")
    if isinstance(value, Decimal):
        return value
    clean = str(value).replace(",", "").replace("₪", "").replace('ש"ח', "").strip()
    try:
        return Decimal(clean)
    except InvalidOperation as exc:
        raise HebrewEmailError(f"Invalid amount: {value}") from exc


def format_ils(value: Any, include_agorot: bool = False) -> str:
    amount = parse_decimal(value)
    if include_agorot:
        quantized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{quantized:,.2f} ₪"
    quantized = amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return f"{quantized:,.0f} ₪"


def vat_breakdown(net_amount: Any, vat_rate: Decimal = VAT_RATE) -> Dict[str, str]:
    net = parse_decimal(net_amount)
    vat = (net * vat_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    gross = (net + vat).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "net": format_ils(net, include_agorot=net != net.to_integral()),
        "vat": format_ils(vat, include_agorot=vat != vat.to_integral()),
        "gross": format_ils(gross, include_agorot=gross != gross.to_integral()),
        "vat_rate": f"{int(vat_rate * 100)}%",
    }


def parse_date(value: Any) -> Optional[date]:
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    patterns = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%d/%m/%y", "%d-%m-%y"]
    for pattern in patterns:
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    raise HebrewEmailError(f"Invalid date: {value}")


def format_date_il(value: Any) -> str:
    parsed = parse_date(value)
    if parsed is None:
        raise HebrewEmailError("Date is required")
    return parsed.strftime(DATE_FORMAT)


def clean_lines(lines: Iterable[str]) -> str:
    output: List[str] = []
    blank = False
    for line in lines:
        stripped = str(line).rstrip()
        if not stripped:
            if not blank:
                output.append("")
            blank = True
        else:
            output.append(stripped)
            blank = False
    while output and output[-1] == "":
        output.pop()
    return "\n".join(output)


def choose_greeting(recipient: Contact, formality: Formality) -> str:
    name = recipient.name.strip()
    if formality == Formality.WARM and name and not recipient.is_company:
        return f"היי {name},"
    if formality == Formality.FORMAL:
        if recipient.is_company and name:
            return f"לכבוד {name},"
        if name and any(token in name for token in ["מחלק", "אגף", "צוות", "שירות"]):
            return f"לכבוד {name},"
        if name and not recipient.is_company:
            return f"שלום {name},"
        return "שלום רב,"
    if recipient.gender == Gender.PLURAL and name:
        return f"שלום {name},"
    if recipient.is_company and not name:
        return "שלום רב,"
    if name:
        return f"שלום {name},"
    return "שלום,"


def choose_closing(formality: Formality) -> str:
    if formality in {Formality.FORMAL, Formality.FIRM}:
        return "בברכה,"
    if formality == Formality.WARM:
        return "תודה רבה,"
    return "תודה,"


def request_confirmation_phrase(gender: Gender) -> str:
    if gender == Gender.MALE:
        return "אשמח אם תוכל לאשר"
    if gender == Gender.FEMALE:
        return "אשמח אם תוכלי לאשר"
    if gender == Gender.PLURAL:
        return "אשמח אם תוכלו לאשר"
    return "אשמח לקבל אישור"


def update_request_phrase(gender: Gender) -> str:
    if gender == Gender.MALE:
        return "תעדכן בבקשה"
    if gender == Gender.FEMALE:
        return "תעדכני בבקשה"
    if gender == Gender.PLURAL:
        return "תעדכנו בבקשה"
    return "נא לעדכן"


def sender_apology(sender: Sender) -> str:
    if sender.gender == Gender.MALE:
        return "מתנצל על העיכוב"
    if sender.gender == Gender.FEMALE:
        return "מתנצלת על העיכוב"
    return "סליחה על העיכוב"


def build_signature(sender: Sender, closing: str = "תודה,", style: SignatureStyle = SignatureStyle.BUSINESS) -> str:
    lines: List[str] = [closing, sender.name or "[שם השולח]"]
    if style in {SignatureStyle.BUSINESS, SignatureStyle.TAX}:
        for value in [sender.business_name, sender.role, sender.phone, sender.email, sender.website]:
            if value:
                lines.append(value)
    elif style == SignatureStyle.MINIMAL:
        for value in [sender.phone, sender.email]:
            if value:
                lines.append(value)
    if style == SignatureStyle.TAX and sender.business_id:
        lines.append(sender.business_id)
    return "\n".join(lines)


def normalize_facts(facts: Mapping[str, Any] | None) -> Dict[str, Any]:
    normalized: Dict[str, Any] = dict(facts or {})
    for key in ["invoice_date", "due_date", "valid_until", "purchase_date", "requested_action_date", "previous_reminder_date", "new_delivery_date", "cancellation_date", "previous_date"]:
        if key in normalized and normalized[key]:
            normalized[key] = format_date_il(normalized[key])
    if "amount" in normalized and normalized["amount"] not in (None, ""):
        normalized["amount_formatted"] = format_ils(normalized["amount"], bool(normalized.get("include_agorot", False)))
    return normalized


def join_bullets(items: Sequence[str] | str | None) -> List[str]:
    if not items:
        return ["- [פירוט]"]
    if isinstance(items, str):
        split_items = [part.strip() for part in re.split(r"[;\n]", items) if part.strip()]
    else:
        split_items = [str(item).strip() for item in items if str(item).strip()]
    return [f"- {item}" for item in split_items] or ["- [פירוט]"]


def make_draft_id(subject: str, body: str) -> str:
    seed = f"{subject}\n{body}\n{uuid.uuid4()}".encode("utf-8")
    return "hef_" + hashlib.sha256(seed).hexdigest()[:16]


class HebrewEmailFormatterClient:
    """Synchronous Hebrew email formatter."""

    def compose(self, request: EmailRequest | Mapping[str, Any]) -> EmailDraft:
        if not isinstance(request, EmailRequest):
            request = self.request_from_mapping(request)
        facts = normalize_facts(request.facts)
        warnings = self.validate(request, facts)
        builders = {
            Purpose.PAYMENT_REMINDER: self.payment_reminder,
            Purpose.QUOTE: self.quote,
            Purpose.INVOICE_SENT: self.invoice_sent,
            Purpose.MEETING_REQUEST: self.meeting_request,
            Purpose.FOLLOW_UP: self.follow_up,
            Purpose.COMPLAINT_RESPONSE: self.complaint_response,
            Purpose.CONSUMER_COMPLAINT: self.consumer_complaint,
            Purpose.APOLOGY_DELAY: self.apology_delay,
            Purpose.CANCELLATION: self.cancellation,
            Purpose.STATUS_UPDATE: self.status_update,
        }
        return builders[request.purpose](request, facts, warnings)

    def request_from_mapping(self, data: Mapping[str, Any]) -> EmailRequest:
        return EmailRequest(
            purpose=parse_purpose(data.get("purpose")),
            recipient=Contact.from_mapping(data.get("recipient")),
            sender=Sender.from_mapping(data.get("sender")),
            formality=parse_formality(data.get("formality", "neutral")),
            facts=data.get("facts", {}) or {},
            signature_style=parse_signature_style(data.get("signature_style", "business")),
            include_review_notes=bool(data.get("include_review_notes", True)),
            environment=parse_environment(data.get("environment", "sandbox")),
        )

    def validate(self, request: EmailRequest, facts: Mapping[str, Any]) -> List[str]:
        warnings: List[str] = []
        if not request.recipient.name:
            warnings.append("HEF002_MISSING_RECIPIENT: שם הנמען חסר; נעשה שימוש בברכה כללית.")
        if not request.sender.name:
            warnings.append("HEF003_MISSING_SENDER: שם השולח חסר; יש להשלים לפני שליחה.")
        if request.recipient.gender == Gender.NEUTRAL:
            warnings.append("HEF008_GENDER_UNKNOWN: מגדר הנמען לא ידוע; נוסח המייל משתמש בניסוח ניטרלי.")
        if request.purpose == Purpose.QUOTE and facts.get("amount") and not facts.get("vat_status"):
            warnings.append('HEF006_VAT_STATUS_UNKNOWN: סטטוס מע"מ לא נמסר.')
        if request.purpose == Purpose.PAYMENT_REMINDER and not facts.get("due_date"):
            warnings.append("HEF007_INVOICE_MISSING_DUE_DATE: תאריך פירעון חסר.")
        if facts.get("sensitive_personal_data"):
            warnings.append("HEF010_PRIVACY_MINIMIZATION: מומלץ לצמצם מידע אישי רגיש שאינו הכרחי.")
        if facts.get("marketing_content"):
            warnings.append("HEF011_MARKETING_CONSENT: מומלץ להפריד תוכן שיווקי ממייל תפעולי.")
        if facts.get("mentions_attachment") and not facts.get("attachment_confirmed"):
            warnings.append("HEF012_ATTACHMENT_UNCONFIRMED: אין לציין קובץ מצורף לפני צירופו.")
        if facts.get("legal_escalation"):
            warnings.append("HEF009_LEGAL_REVIEW: יש לבדוק נוסח משפטי לפני שליחה.")
        return warnings

    def metadata(self, request: EmailRequest) -> Dict[str, Any]:
        return {"locale": LOCALE, "currency": "ILS", "date_format": DATE_FORMAT_LABEL, "formality": request.formality.value, "purpose": request.purpose.value, "environment": request.environment}

    def finalize(self, request: EmailRequest, subject: str, body: str, warnings: List[str]) -> EmailDraft:
        return EmailDraft(make_draft_id(subject, body), subject, body, warnings, self.metadata(request))

    def payment_reminder(self, request: EmailRequest, facts: Mapping[str, Any], warnings: List[str]) -> EmailDraft:
        invoice = facts.get("invoice_number", "[מספר]")
        subject = f"תזכורת לתשלום חשבונית {invoice}" if request.formality != Formality.FIRM else f"תשלום חשבונית {invoice} – תזכורת"
        amount = facts.get("amount_formatted", "[סכום] ₪")
        due = facts.get("due_date", "[תאריך פירעון]")
        invoice_date = facts.get("invoice_date", "[תאריך חשבונית]")
        lines = [choose_greeting(request.recipient, request.formality), ""]
        if request.formality == Formality.FIRM:
            previous = facts.get("previous_reminder_date")
            if previous:
                lines.append(f"בהמשך לתזכורת מיום {previous}, התשלום עבור חשבונית {invoice} טרם התקבל.")
            else:
                lines.append(f"בהמשך לחשבונית {invoice}, התשלום בסך {amount} טרם התקבל.")
            action_date = facts.get("requested_action_date", "[תאריך יעד]")
            lines.extend(["", f"תאריך הפירעון היה {due}. נא לעדכן עד {action_date} לגבי מועד התשלום הצפוי או להעביר אסמכתא אם התשלום כבר בוצע.", "", build_signature(request.sender, choose_closing(request.formality), request.signature_style)])
        else:
            lines.extend([f"רציתי לוודא שחשבונית {invoice} מיום {invoice_date} התקבלה אצלכם.", "", f"סכום לתשלום: {amount}", f"תאריך פירעון: {due}"])
            if facts.get("payment_terms"):
                lines.append(f"תנאי תשלום: {facts['payment_terms']}")
            lines.extend(["", "אשמח לקבל עדכון לגבי מועד התשלום הצפוי.", "", build_signature(request.sender, choose_closing(request.formality), request.signature_style)])
        return self.finalize(request, subject, clean_lines(lines), warnings)

    def quote(self, request: EmailRequest, facts: Mapping[str, Any], warnings: List[str]) -> EmailDraft:
        service = facts.get("service", facts.get("project", "[שירות/פרויקט]"))
        amount = facts.get("amount_formatted", "[סכום] ₪")
        vat = facts.get("vat_status") or '[בדיקה נדרשת: סטטוס מע"מ לא נמסר.]'
        lines = [choose_greeting(request.recipient, request.formality), "", f"בהמשך לשיחתנו, מצורפת הצעת מחיר עבור {service}.", "", "היקף העבודה:", *join_bullets(facts.get("scope") or facts.get("items")), "", f"לוחות זמנים: {facts.get('timeline', '[לוח זמנים]')}", f"עלות: {amount} {vat}", f"תוקף ההצעה: עד {facts.get('valid_until', '[תאריך תוקף]')}", "", "לאישור ההצעה, נא להשיב למייל זה עם אישור כתוב או להעביר הזמנת עבודה.", "", build_signature(request.sender, choose_closing(request.formality), request.signature_style)]
        return self.finalize(request, f"הצעת מחיר עבור {service}", clean_lines(lines), warnings)

    def invoice_sent(self, request: EmailRequest, facts: Mapping[str, Any], warnings: List[str]) -> EmailDraft:
        invoice = facts.get("invoice_number", "[מספר]")
        doc_type = facts.get("document_type", "חשבונית")
        service = facts.get("service", facts.get("period", "[שירות/תקופה]"))
        attachment_line = f"מצורפת {doc_type} {invoice} עבור {service}." if facts.get("attachment_confirmed") else f"{doc_type} {invoice} עבור {service} מוכנה לטיפול."
        lines = [choose_greeting(request.recipient, request.formality), "", attachment_line, "", f"סכום לתשלום: {facts.get('amount_formatted', '[סכום] ₪')}", f"תנאי תשלום: {facts.get('payment_terms', '[תנאי תשלום]')}", f"תאריך פירעון: {facts.get('due_date', '[תאריך פירעון]')}", "", "אשמח לעדכון אם נדרש פרט נוסף לצורך הטיפול בתשלום.", "", build_signature(request.sender, choose_closing(request.formality), request.signature_style)]
        return self.finalize(request, f"{doc_type} {invoice} עבור {service}", clean_lines(lines), warnings)

    def meeting_request(self, request: EmailRequest, facts: Mapping[str, Any], warnings: List[str]) -> EmailDraft:
        topic = facts.get("topic", "[נושא]")
        slots = facts.get("slots") or ["[יום], [DD/MM/YYYY], בשעה [שעה]", "[יום], [DD/MM/YYYY], בשעה [שעה]"]
        lines = [choose_greeting(request.recipient, request.formality), "", f"אשמח לתאם פגישה קצרה בנושא {topic}.", "", "להלן אפשרויות נוחות:", *join_bullets(slots), "", f"משך הפגישה המשוער: {facts.get('duration', '[משך]')}", f"הפגישה תתקיים {facts.get('medium', '[שיחת וידאו / טלפון / משרד / אצלכם]')}.", "", "אשמח לקבל אישור לאחת האפשרויות או הצעה למועד חלופי.", "", build_signature(request.sender, choose_closing(request.formality), request.signature_style)]
        return self.finalize(request, f"תיאום פגישה בנושא {topic}", clean_lines(lines), warnings)

    def follow_up(self, request: EmailRequest, facts: Mapping[str, Any], warnings: List[str]) -> EmailDraft:
        topic = facts.get("topic", "[נושא]")
        intro = f"בהמשך למייל מיום {facts['previous_date']}, רציתי לוודא שהנושא התקבל אצלכם." if facts.get("previous_date") else "רציתי לוודא שהמייל הקודם התקבל אצלכם."
        lines = [choose_greeting(request.recipient, request.formality), "", intro, "", facts.get("requested_action", "אשמח לקבל עדכון כשנוח."), "", build_signature(request.sender, choose_closing(request.formality), request.signature_style)]
        return self.finalize(request, f"מעקב בנושא {topic}", clean_lines(lines), warnings)

    def complaint_response(self, request: EmailRequest, facts: Mapping[str, Any], warnings: List[str]) -> EmailDraft:
        topic = facts.get("topic", "[נושא הפנייה]")
        lines = [choose_greeting(request.recipient, request.formality), "", "תודה שפנית ועדכנת בנושא. הפנייה התקבלה ונבדקת מול הגורם הרלוונטי.", "", f"נעדכן בכתב עד {facts.get('requested_action_date', '[תאריך יעד]')} לגבי {facts.get('resolution', 'אופן הטיפול והפתרון המוצע')}.", "", build_signature(request.sender, choose_closing(request.formality), request.signature_style)]
        return self.finalize(request, f"מענה לפנייה בנושא {topic}", clean_lines(lines), warnings)

    def consumer_complaint(self, request: EmailRequest, facts: Mapping[str, Any], warnings: List[str]) -> EmailDraft:
        product = facts.get("product", facts.get("service", "[מוצר/שירות]"))
        order = facts.get("order_number", "[מספר הזמנה/לקוח]")
        problem = facts.get("problem", "[תיאור הבעיה]")
        lines = [choose_greeting(request.recipient, Formality.FORMAL), "", f"בתאריך {facts.get('purchase_date', '[תאריך רכישה/הזמנה]')} רכשתי או הזמנתי {product}. לצערי, {problem}.", "", "פרטי הפנייה:", f"- מספר הזמנה או לקוח: {order}", f"- תאריך רכישה או הזמנה: {facts.get('purchase_date', '[תאריך רכישה/הזמנה]')}", f"- סכום העסקה: {facts.get('amount_formatted', '[סכום] ₪')}", f"- תיאור הבעיה: {problem}", "", f"אבקש לקבל מענה בכתב עד {facts.get('requested_action_date', '[תאריך יעד]')}, כולל פתרון מוצע: {facts.get('requested_resolution', '[החלפה / תיקון / זיכוי / החזר / אחר]')}.", "", build_signature(request.sender, choose_closing(Formality.FORMAL), request.signature_style)]
        return self.finalize(request, f"פנייה בנושא {product} – {order}", clean_lines(lines), warnings)

    def apology_delay(self, request: EmailRequest, facts: Mapping[str, Any], warnings: List[str]) -> EmailDraft:
        topic = facts.get("topic", "[נושא]")
        new_date = facts.get("new_delivery_date", facts.get("requested_action_date", "[תאריך יעד]"))
        lines = [choose_greeting(request.recipient, request.formality), "", f"{sender_apology(request.sender)} בעדכון לגבי {topic}. העבודה מתקדמת, והעדכון הבא יישלח עד {new_date}.", "", "תודה על הסבלנות. אעדכן אם יהיה שינוי בלוחות הזמנים.", "", build_signature(request.sender, choose_closing(request.formality), request.signature_style)]
        return self.finalize(request, f"עדכון לגבי {topic}", clean_lines(lines), warnings)

    def cancellation(self, request: EmailRequest, facts: Mapping[str, Any], warnings: List[str]) -> EmailDraft:
        service = facts.get("service", "[שירות/הזמנה]")
        account = facts.get("account_number", facts.get("order_number", "[מספר לקוח/הזמנה]"))
        date_text = facts.get("cancellation_date", facts.get("requested_action_date", "[תאריך ביטול מבוקש]"))
        lines = [choose_greeting(request.recipient, request.formality), "", f"אבקש לבטל את {service} המשויך למספר {account}, החל מיום {date_text}.", "", "אבקש לקבל אישור ביטול בכתב ולעדכן אם קיימת יתרה לתשלום או זכאות להחזר.", "", build_signature(request.sender, choose_closing(request.formality), request.signature_style)]
        return self.finalize(request, f"בקשת ביטול עבור {service}", clean_lines(lines), warnings)

    def status_update(self, request: EmailRequest, facts: Mapping[str, Any], warnings: List[str]) -> EmailDraft:
        project = facts.get("project", "[שם הפרויקט]")
        lines = [choose_greeting(request.recipient, request.formality), "", f"להלן עדכון קצר לגבי {project}:", "", "הושלם:", *join_bullets(facts.get("completed")), "", "בתכנון:", *join_bullets(facts.get("next")), "", "נקודות לתשומת לב:", *join_bullets(facts.get("attention")), "", build_signature(request.sender, choose_closing(request.formality), request.signature_style)]
        return self.finalize(request, f"עדכון סטטוס – {project}", clean_lines(lines), warnings)


class DraftStore:
    """Small local JSON store for CLI create/show workflows."""

    def __init__(self, directory: str | Path | None = None) -> None:
        if directory is None:
            directory = os.environ.get("HEF_DRAFT_DIR", ".hebrew_email_formatter/drafts")
        self.directory = Path(directory)

    def save(self, draft: EmailDraft) -> str:
        self.directory.mkdir(parents=True, exist_ok=True)
        (self.directory / f"{draft.id}.json").write_text(draft.to_json(), encoding="utf-8")
        return draft.id

    def load(self, draft_id: str) -> EmailDraft:
        path = self.directory / f"{draft_id}.json"
        if not path.exists():
            raise HebrewEmailError(f"Draft not found: {draft_id}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return EmailDraft(str(data["id"]), str(data["subject"]), str(data["body"]), list(data.get("warnings", [])), dict(data.get("metadata", {})))

    def list_ids(self) -> List[str]:
        if not self.directory.exists():
            return []
        return sorted(path.stem for path in self.directory.glob("hef_*.json"))


class AsyncHebrewEmailFormatterClient:
    """Async wrapper with output parity to the sync client."""

    def __init__(self, sync_client: Optional[HebrewEmailFormatterClient] = None) -> None:
        self.sync_client = sync_client or HebrewEmailFormatterClient()

    async def compose(self, request: EmailRequest | Mapping[str, Any]) -> EmailDraft:
        await asyncio.sleep(0)
        return self.sync_client.compose(request)
