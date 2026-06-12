#!/usr/bin/env python3
"""Typed WhatsApp scheduling client for Hebrew Israeli appointment workflows."""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Literal, Mapping, MutableMapping, Optional, Protocol, Sequence, Tuple, Union
from urllib import error, request
from zoneinfo import ZoneInfo

ISRAEL_TZ = ZoneInfo("Asia/Jerusalem")
DEFAULT_API_VERSION = "v25.0"
APPOINTMENT_STATUSES = {"draft","pending_customer","confirmed","reschedule_requested","cancelled","completed","no_show","blocked"}
OPT_OUT_KEYWORDS = {"הסר", "להסרה", "stop", "STOP", "אל תשלחו", "לא לשלוח"}
SENSITIVE_KEYWORDS = {"רפואי", "דחוף", "חירום", "תרופה", "אבחנה", "תביעה", "עורך דין", "חוב", "קטין"}


class WhatsAppSchedulingError(Exception):
    """Base error for scheduling client failures."""


class PhoneValidationError(WhatsAppSchedulingError, ValueError):
    """Raised when a phone number cannot be normalized."""


class AppointmentValidationError(WhatsAppSchedulingError, ValueError):
    """Raised when appointment data is invalid."""


class ProviderError(WhatsAppSchedulingError):
    """Raised when a provider request fails."""

    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"Provider request failed with HTTP {status_code}: {payload}")


class HttpTransport(Protocol):
    def post(self, url: str, headers: Mapping[str, str], json_body: Mapping[str, Any], timeout: float) -> Dict[str, Any]:
        """Send a JSON POST request and return decoded JSON."""


@dataclass
class UrllibTransport:
    def post(self, url: str, headers: Mapping[str, str], json_body: Mapping[str, Any], timeout: float) -> Dict[str, Any]:
        data = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        req = request.Request(url, data=data, headers={**headers, "Content-Type": "application/json"}, method="POST")
        try:
            with request.urlopen(req, timeout=timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                payload: Any = json.loads(body)
            except json.JSONDecodeError:
                payload = {"error": body}
            raise ProviderError(exc.code, payload) from exc


@dataclass
class Reminder:
    offset_minutes: int
    status: Literal["pending", "processing", "sent", "skipped", "failed"] = "pending"
    provider_message_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    template_name: str = "appointment_reminder_he"

    def idempotency_key(self, appointment_id: str) -> str:
        return f"{appointment_id}:{self.offset_minutes}:{self.template_name}"


@dataclass
class Appointment:
    customer_name: str
    customer_phone: str
    service_name: str
    start_at: datetime
    duration_minutes: int
    business_name: str
    appointment_id: str = field(default_factory=lambda: f"apt_{uuid.uuid4().hex[:12]}")
    staff_name: Optional[str] = None
    price_ils: Optional[Union[int, float]] = None
    location: Optional[str] = None
    status: Literal["draft","pending_customer","confirmed","reschedule_requested","cancelled","completed","no_show","blocked"] = "confirmed"
    notes: Optional[str] = None
    consent_source: str = "customer_requested_appointment"
    reminders: List[Reminder] = field(default_factory=lambda: [Reminder(1440), Reminder(120)])
    created_at: datetime = field(default_factory=lambda: datetime.now(ISRAEL_TZ))
    updated_at: datetime = field(default_factory=lambda: datetime.now(ISRAEL_TZ))

    @property
    def end_at(self) -> datetime:
        return self.start_at + timedelta(minutes=self.duration_minutes)


@dataclass
class IncomingWhatsAppEvent:
    from_phone: str
    message_id: str
    message_type: str
    text: str = ""
    customer_name: Optional[str] = None
    timestamp: Optional[int] = None


@dataclass
class SendResult:
    success: bool
    provider_message_id: Optional[str]
    raw: Dict[str, Any]


def ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ISRAEL_TZ)
    return dt.astimezone(ISRAEL_TZ)


def parse_datetime(value: Union[str, datetime]) -> datetime:
    if isinstance(value, datetime):
        return ensure_aware(value)
    normalized = value.replace("Z", "+00:00")
    try:
        return ensure_aware(datetime.fromisoformat(normalized))
    except ValueError as exc:
        raise AppointmentValidationError(f"Invalid ISO datetime: {value}") from exc


def format_israeli_date(dt: datetime) -> str:
    return ensure_aware(dt).strftime("%d/%m/%Y")


def format_israeli_time(dt: datetime) -> str:
    return ensure_aware(dt).strftime("%H:%M")


def format_price_ils(value: Optional[Union[int, float]]) -> str:
    if value is None:
        return ""
    amount = str(int(value)) if float(value).is_integer() else f"{float(value):.2f}".rstrip("0").rstrip(".")
    return f"₪{amount}"


def normalize_israeli_phone(phone: str) -> str:
    if not isinstance(phone, str) or not phone.strip():
        raise PhoneValidationError("Phone number is required")
    if re.search(r"[A-Za-zא-ת]", phone):
        raise PhoneValidationError("Phone number must not contain letters")
    clean = re.sub(r"[\s\-().+]", "", phone)
    if not clean.isdigit():
        raise PhoneValidationError("Phone number must contain digits only")
    if clean.startswith("00"):
        clean = clean[2:]
    if clean.startswith("972"):
        local = "0" + clean[3:]
    elif clean.startswith("0"):
        local = clean
    else:
        raise PhoneValidationError("Israeli number must start with 0, +972, or 972")
    mobile = re.fullmatch(r"05\d{8}", local)
    landline = re.fullmatch(r"0[2-489]\d{7}", local) or re.fullmatch(r"0[2-489]\d{8}", local)
    if not (mobile or landline):
        raise PhoneValidationError(f"Unsupported Israeli phone format: {phone}")
    return "972" + local[1:]



def prefix_hebrew_b(value: str) -> str:
    """Return a natural Hebrew location prefix for a business name."""
    cleaned = value.strip()
    if cleaned.startswith("ה") and len(cleaned) > 1:
        return "ב" + cleaned[1:]
    return "ב" + cleaned

def display_israeli_phone(phone: str) -> str:
    normalized = normalize_israeli_phone(phone)
    local = "0" + normalized[3:]
    if local.startswith("05") and len(local) == 10:
        return f"{local[:3]}-{local[3:6]}-{local[6:]}"
    if len(local) == 9:
        return f"{local[:2]}-{local[2:5]}-{local[5:]}"
    if len(local) == 10:
        return f"{local[:3]}-{local[3:6]}-{local[6:]}"
    return local


def is_opt_out_text(text: str) -> bool:
    stripped = text.strip()
    lowered = stripped.lower()
    return stripped in OPT_OUT_KEYWORDS or lowered in {kw.lower() for kw in OPT_OUT_KEYWORDS}


def requires_human_escalation(text: str) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in SENSITIVE_KEYWORDS)


def is_business_time(
    dt: Union[str, datetime],
    open_time: time = time(8, 0),
    close_time: time = time(20, 0),
    allow_friday: bool = False,
    allow_saturday: bool = False,
) -> bool:
    value = parse_datetime(dt)
    weekday = value.weekday()  # Monday=0, Friday=4, Saturday=5, Sunday=6
    if weekday == 4 and not allow_friday:
        return False
    if weekday == 5 and not allow_saturday:
        return False
    current_time = value.time().replace(tzinfo=None)
    return open_time <= current_time < close_time


class WhatsAppSchedulingClient:
    """Synchronous client for appointments and WhatsApp Cloud API payloads."""

    def __init__(
        self,
        access_token: str,
        phone_number_id: str,
        api_version: str = DEFAULT_API_VERSION,
        base_url: str = "https://graph.facebook.com",
        transport: Optional[HttpTransport] = None,
        timeout: float = 20.0,
    ) -> None:
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.api_version = api_version
        self.base_url = base_url.rstrip("/")
        self.transport = transport or UrllibTransport()
        self.timeout = timeout
        self.appointments: MutableMapping[str, Appointment] = {}
        self.sent_idempotency_keys: set[str] = set()

    @property
    def messages_url(self) -> str:
        return f"{self.base_url}/{self.api_version}/{self.phone_number_id}/messages"

    def _headers(self) -> Dict[str, str]:
        if not self.access_token:
            raise ProviderError(401, {"error": "Missing access token"})
        return {"Authorization": f"Bearer {self.access_token}"}

    def create_appointment(
        self,
        customer_name: str,
        customer_phone: str,
        service_name: str,
        start_at: Union[str, datetime],
        duration_minutes: int,
        business_name: str,
        staff_name: Optional[str] = None,
        price_ils: Optional[Union[int, float]] = None,
        location: Optional[str] = None,
        status: Literal["draft","pending_customer","confirmed","reschedule_requested","cancelled","completed","no_show","blocked"] = "confirmed",
        notes: Optional[str] = None,
        consent_source: str = "customer_requested_appointment",
    ) -> Appointment:
        if not customer_name.strip():
            raise AppointmentValidationError("Customer name is required")
        if not service_name.strip():
            raise AppointmentValidationError("Service name is required")
        if duration_minutes <= 0:
            raise AppointmentValidationError("Duration must be positive")
        if status not in APPOINTMENT_STATUSES:
            raise AppointmentValidationError(f"Unsupported status: {status}")
        appointment = Appointment(
            customer_name=customer_name.strip(),
            customer_phone=normalize_israeli_phone(customer_phone),
            service_name=service_name.strip(),
            start_at=parse_datetime(start_at),
            duration_minutes=duration_minutes,
            business_name=business_name.strip(),
            staff_name=staff_name.strip() if staff_name else None,
            price_ils=price_ils,
            location=location.strip() if location else None,
            status=status,
            notes=notes,
            consent_source=consent_source,
        )
        self.appointments[appointment.appointment_id] = appointment
        return appointment

    def update_appointment_status(self, appointment_id: str, status: str) -> Appointment:
        if status not in APPOINTMENT_STATUSES:
            raise AppointmentValidationError(f"Unsupported status: {status}")
        appointment = self.appointments[appointment_id]
        appointment.status = status  # type: ignore[assignment]
        appointment.updated_at = datetime.now(ISRAEL_TZ)
        if status in {"cancelled", "completed", "no_show", "blocked"}:
            for reminder in appointment.reminders:
                if reminder.status == "pending":
                    reminder.status = "skipped"
        return appointment

    def reschedule_appointment(self, appointment_id: str, new_start_at: Union[str, datetime]) -> Appointment:
        appointment = self.appointments[appointment_id]
        appointment.start_at = parse_datetime(new_start_at)
        appointment.updated_at = datetime.now(ISRAEL_TZ)
        appointment.status = "confirmed"
        appointment.reminders = [Reminder(1440), Reminder(120)]
        return appointment

    def build_confirmation_text(self, appointment: Appointment) -> str:
        detail_parts: List[str] = []
        if appointment.price_ils is not None:
            detail_parts.append(f"מחיר: {format_price_ils(appointment.price_ils)}.")
        if appointment.location:
            detail_parts.append(f"כתובת: {appointment.location}.")
        if appointment.staff_name:
            detail_parts.append(f"איש/אשת צוות: {appointment.staff_name}.")
        details = " ".join(detail_parts) or "פרטי התור נשמרו."
        return (
            f"שלום {appointment.customer_name}, נקבע לך תור ל{appointment.service_name} "
            f"{prefix_hebrew_b(appointment.business_name)} ביום {format_israeli_date(appointment.start_at)} "
            f"בשעה {format_israeli_time(appointment.start_at)}.\n"
            f"משך התור: {appointment.duration_minutes} דקות. {details}\n"
            "לאישור יש להשיב 1. לשינוי מועד יש להשיב 2. לביטול יש להשיב 3."
        )

    def build_reminder_text(self, appointment: Appointment, offset_minutes: int = 1440) -> str:
        when = f"ביום {format_israeli_date(appointment.start_at)}" if offset_minutes >= 1440 else "היום"
        location_line = f"\nכתובת: {appointment.location}." if appointment.location else ""
        return (
            f"תזכורת: התור שלך ל{appointment.service_name} {prefix_hebrew_b(appointment.business_name)} נקבע "
            f"{when} בשעה {format_israeli_time(appointment.start_at)}.{location_line}\n"
            "לאישור הגעה יש להשיב 1. לשינוי או ביטול יש להשיב 2."
        )

    def build_cancellation_text(self, appointment: Appointment) -> str:
        return (
            f"התור ל{appointment.service_name} בתאריך {format_israeli_date(appointment.start_at)} "
            f"בשעה {format_israeli_time(appointment.start_at)} בוטל.\n"
            'לקביעת מועד חדש יש להשיב "תור חדש".'
        )

    def build_template_parameters(self, appointment: Appointment) -> List[str]:
        optional = []
        if appointment.price_ils is not None:
            optional.append(f"מחיר: {format_price_ils(appointment.price_ils)}.")
        if appointment.location:
            optional.append(f"כתובת: {appointment.location}.")
        return [
            appointment.customer_name,
            appointment.service_name,
            appointment.business_name,
            format_israeli_date(appointment.start_at),
            format_israeli_time(appointment.start_at),
            str(appointment.duration_minutes),
            " ".join(optional) if optional else "פרטי התור נשמרו.",
        ]

    def template_payload(self, to: str, template_name: str, parameters: Sequence[str], language: str = "he") -> Dict[str, Any]:
        return {
            "messaging_product": "whatsapp",
            "to": normalize_israeli_phone(to),
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": [{"type": "body", "parameters": [{"type": "text", "text": str(value)} for value in parameters]}],
            },
        }

    def text_payload(self, to: str, text: str, preview_url: bool = False) -> Dict[str, Any]:
        if not text.strip():
            raise AppointmentValidationError("Message body is required")
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": normalize_israeli_phone(to),
            "type": "text",
            "text": {"preview_url": preview_url, "body": text},
        }

    def _post_message(self, payload: Mapping[str, Any]) -> SendResult:
        raw = self.transport.post(self.messages_url, self._headers(), payload, self.timeout)
        try:
            message_id = raw.get("messages", [{}])[0].get("id")
        except (AttributeError, IndexError):
            message_id = None
        return SendResult(success=bool(message_id), provider_message_id=message_id, raw=raw)

    def send_text(self, to: str, text: str, preview_url: bool = False, dry_run: bool = False) -> SendResult:
        payload = self.text_payload(to, text, preview_url)
        if dry_run:
            return SendResult(True, "dry-run", payload)
        return self._post_message(payload)

    def send_template(self, to: str, template_name: str, parameters: Sequence[str], language: str = "he", dry_run: bool = False) -> SendResult:
        payload = self.template_payload(to, template_name, parameters, language)
        if dry_run:
            return SendResult(True, "dry-run", payload)
        return self._post_message(payload)

    def send_appointment_confirmation(self, appointment: Appointment, template_name: str = "appointment_confirmation_he", as_template: bool = True, dry_run: bool = False) -> SendResult:
        if as_template:
            return self.send_template(appointment.customer_phone, template_name, self.build_template_parameters(appointment), "he", dry_run)
        return self.send_text(appointment.customer_phone, self.build_confirmation_text(appointment), dry_run=dry_run)

    def due_reminders(self, now: Optional[Union[str, datetime]] = None) -> List[Tuple[Appointment, Reminder]]:
        current = parse_datetime(now) if now is not None else datetime.now(ISRAEL_TZ)
        due: List[Tuple[Appointment, Reminder]] = []
        for appointment in self.appointments.values():
            if appointment.status != "confirmed" or appointment.start_at <= current:
                continue
            for reminder in appointment.reminders:
                send_at = appointment.start_at - timedelta(minutes=reminder.offset_minutes)
                if reminder.status == "pending" and send_at <= current:
                    due.append((appointment, reminder))
        return due

    def send_due_reminders(self, now: Optional[Union[str, datetime]] = None, dry_run: bool = False) -> List[SendResult]:
        results: List[SendResult] = []
        for appointment, reminder in self.due_reminders(now):
            key = reminder.idempotency_key(appointment.appointment_id)
            if key in self.sent_idempotency_keys:
                reminder.status = "skipped"
                continue
            result = self.send_text(appointment.customer_phone, self.build_reminder_text(appointment, reminder.offset_minutes), dry_run=dry_run)
            reminder.status = "sent" if result.success else "failed"
            reminder.provider_message_id = result.provider_message_id
            reminder.sent_at = parse_datetime(now) if now is not None else datetime.now(ISRAEL_TZ)
            self.sent_idempotency_keys.add(key)
            results.append(result)
        return results

    def parse_webhook_payload(self, payload: Mapping[str, Any]) -> List[IncomingWhatsAppEvent]:
        events: List[IncomingWhatsAppEvent] = []
        for entry in payload.get("entry", []):  # type: ignore[union-attr]
            for change in entry.get("changes", []):
                value = change.get("value", {})
                contacts = value.get("contacts", [])
                name_by_phone = {c.get("wa_id"): c.get("profile", {}).get("name") for c in contacts if isinstance(c, Mapping)}
                for message in value.get("messages", []):
                    message_type = message.get("type", "")
                    text = ""
                    if message_type == "text":
                        text = message.get("text", {}).get("body", "")
                    elif message_type == "button":
                        text = message.get("button", {}).get("text", "")
                    elif message_type == "interactive":
                        interactive = message.get("interactive", {})
                        text = interactive.get("button_reply", {}).get("title") or interactive.get("list_reply", {}).get("title") or ""
                    from_phone = str(message.get("from", ""))
                    events.append(IncomingWhatsAppEvent(
                        from_phone=from_phone,
                        message_id=str(message.get("id", "")),
                        message_type=message_type,
                        text=text,
                        customer_name=name_by_phone.get(from_phone),
                        timestamp=int(message["timestamp"]) if str(message.get("timestamp", "")).isdigit() else None,
                    ))
        return events

    @staticmethod
    def verify_webhook(mode: Optional[str], token: Optional[str], challenge: Optional[str], expected_token: str) -> Tuple[int, str]:
        if mode == "subscribe" and token == expected_token and challenge is not None:
            return 200, challenge
        return 403, "Forbidden"

    def classify_reply(self, text: str) -> Literal["confirm", "change_or_cancel", "cancel", "opt_out", "human", "unknown"]:
        stripped = text.strip()
        if is_opt_out_text(stripped):
            return "opt_out"
        if requires_human_escalation(stripped):
            return "human"
        if stripped == "1":
            return "confirm"
        if stripped == "2":
            return "change_or_cancel"
        if stripped == "3" or "בטל" in stripped or "לבטל" in stripped or "בטלי" in stripped:
            return "cancel"
        return "unknown"


class AsyncWhatsAppSchedulingClient:
    """Async wrapper around the synchronous client."""

    def __init__(self, sync_client: WhatsAppSchedulingClient) -> None:
        self.sync_client = sync_client

    async def send_text(self, to: str, text: str, preview_url: bool = False, dry_run: bool = False) -> SendResult:
        return await asyncio.to_thread(self.sync_client.send_text, to, text, preview_url, dry_run)

    async def send_template(self, to: str, template_name: str, parameters: Sequence[str], language: str = "he", dry_run: bool = False) -> SendResult:
        return await asyncio.to_thread(self.sync_client.send_template, to, template_name, parameters, language, dry_run)

    async def send_appointment_confirmation(self, appointment: Appointment, template_name: str = "appointment_confirmation_he", as_template: bool = True, dry_run: bool = False) -> SendResult:
        return await asyncio.to_thread(self.sync_client.send_appointment_confirmation, appointment, template_name, as_template, dry_run)

    async def send_due_reminders(self, now: Optional[Union[str, datetime]] = None, dry_run: bool = False) -> List[SendResult]:
        return await asyncio.to_thread(self.sync_client.send_due_reminders, now, dry_run)

__all__ = [
    "APPOINTMENT_STATUSES",
    "DEFAULT_API_VERSION",
    "ISRAEL_TZ",
    "Appointment",
    "AppointmentValidationError",
    "AsyncWhatsAppSchedulingClient",
    "HttpTransport",
    "IncomingWhatsAppEvent",
    "PhoneValidationError",
    "ProviderError",
    "Reminder",
    "SendResult",
    "UrllibTransport",
    "WhatsAppSchedulingClient",
    "WhatsAppSchedulingError",
    "display_israeli_phone",
    "prefix_hebrew_b",
    "ensure_aware",
    "format_israeli_date",
    "format_israeli_time",
    "format_price_ils",
    "is_business_time",
    "is_opt_out_text",
    "normalize_israeli_phone",
    "parse_datetime",
    "requires_human_escalation",
]
