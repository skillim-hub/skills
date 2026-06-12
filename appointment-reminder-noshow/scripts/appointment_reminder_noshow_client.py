"""Typed appointment reminder and no-show tracking client.

The module is intentionally provider-light: it can plan reminders without network
access and can send through mock, generic webhook, Twilio, or WhatsApp Cloud API
when credentials are supplied by the caller.
"""
from __future__ import annotations

import asyncio
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Sequence
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = "Asia/Jerusalem"
ISRAEL_MOBILE_RE = re.compile(r"^\+9725\d{8}$")


class ReminderError(ValueError):
    """Raised for validation and workflow errors."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class Channel(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"


class Provider(str, Enum):
    MOCK = "mock"
    TWILIO = "twilio"
    WHATSAPP_CLOUD = "whatsapp_cloud"
    GENERIC = "generic"


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    ATTENDED = "attended"
    NO_SHOW = "no_show"


@dataclass(frozen=True)
class Customer:
    id: str
    name: str
    phone_e164: str
    preferred_language: str = "he"
    consent_whatsapp: bool = False
    consent_sms: bool = False
    marketing_consent: bool = False

    def __post_init__(self) -> None:
        normalize_israeli_mobile(self.phone_e164)
        if self.preferred_language not in {"he", "en"}:
            raise ReminderError("LANGUAGE_UNSUPPORTED", "supported languages are 'he' and 'en'")


@dataclass(frozen=True)
class Appointment:
    id: str
    customer: Customer
    starts_at: datetime
    business_name: str
    service_name: str
    location: str = ""
    price_ils: int | None = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    cancel_until: datetime | None = None

    def __post_init__(self) -> None:
        if self.starts_at.tzinfo is None:
            raise ReminderError("TIMEZONE_MISSING", "appointment starts_at must include timezone")
        if not self.id:
            raise ReminderError("APPOINTMENT_ID_MISSING", "appointment id is required")
        if not self.business_name:
            raise ReminderError("BUSINESS_NAME_MISSING", "business name is required")


@dataclass(frozen=True)
class ReminderPolicy:
    hours_before: tuple[int, ...] = (48, 24, 3)
    timezone_name: str = DEFAULT_TIMEZONE
    quiet_start_hour: int = 21
    quiet_end_hour: int = 8
    quiet_evening_hour: int = 20
    quiet_evening_minute: int = 30
    prefer_whatsapp: bool = True
    allow_marketing: bool = False
    confirmation_keywords: tuple[str, ...] = ("1", "confirm", "מאשר", "מאשרת")
    reschedule_keywords: tuple[str, ...] = ("2", "reschedule", "שינוי", "מועד")
    cancel_keywords: tuple[str, ...] = ("3", "cancel", "בטל", "ביטול")

    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.timezone_name)


@dataclass(frozen=True)
class ReminderMessage:
    appointment_id: str
    customer_id: str
    channel: Channel
    send_at: datetime
    body: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["channel"] = self.channel.value
        payload["send_at"] = self.send_at.isoformat()
        return payload


@dataclass(frozen=True)
class ProviderResponse:
    success: bool
    status_code: int
    provider_message_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


def normalize_israeli_mobile(raw_phone: str) -> str:
    """Normalize an Israeli mobile number to E.164.

    Accepts local mobile numbers such as 050-123-4567 and E.164 numbers such as
    +972501234567. Raises ReminderError for landlines or invalid values.
    """

    compact = re.sub(r"[\s\-().]", "", raw_phone.strip())
    if compact.startswith("00"):
        compact = "+" + compact[2:]
    elif compact.startswith("+"):
        pass
    elif compact.startswith("972"):
        compact = "+" + compact
    elif compact.startswith("0"):
        compact = "+972" + compact[1:]
    else:
        compact = "+972" + compact

    if not ISRAEL_MOBILE_RE.match(compact):
        raise ReminderError("PHONE_INVALID", "expected an Israeli mobile number in E.164 format")
    return compact


def parse_datetime(value: str, timezone_name: str = DEFAULT_TIMEZONE) -> datetime:
    """Parse an ISO datetime and attach Asia/Jerusalem when timezone is absent."""

    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(timezone_name))
    return dt


def format_israeli_datetime(dt: datetime, language: str = "he") -> str:
    local = dt.astimezone(ZoneInfo(DEFAULT_TIMEZONE))
    if language == "he":
        return local.strftime("%d-%m-%Y בשעה %H:%M")
    return local.strftime("%d-%m-%Y at %H:%M")


def first_name(name: str) -> str:
    return name.strip().split()[0] if name.strip() else ""


class AppointmentReminderClient:
    """Plan reminders, send provider requests, and track no-show outcomes."""

    def __init__(
        self,
        policy: ReminderPolicy | None = None,
        provider: Provider | str = Provider.MOCK,
        credentials: Mapping[str, str] | None = None,
        request_json: Callable[[str, str, Mapping[str, str], bytes | None], tuple[int, dict[str, Any]]] | None = None,
    ) -> None:
        self.policy = policy or ReminderPolicy()
        self.provider = Provider(provider)
        self.credentials = dict(credentials or {})
        self._request_json = request_json or self._default_request_json

    def choose_channel(self, customer: Customer) -> Channel:
        if self.policy.prefer_whatsapp and customer.consent_whatsapp:
            return Channel.WHATSAPP
        if customer.consent_sms:
            return Channel.SMS
        if customer.consent_whatsapp:
            return Channel.WHATSAPP
        raise ReminderError("CONSENT_MISSING", "no permitted reminder channel is available")

    def plan_reminders(self, appointments: Iterable[Appointment], now: datetime | None = None) -> list[ReminderMessage]:
        local_now = now or datetime.now(self.policy.timezone())
        if local_now.tzinfo is None:
            local_now = local_now.replace(tzinfo=self.policy.timezone())
        planned: list[ReminderMessage] = []
        seen_keys: set[tuple[str, str, str]] = set()

        for appointment in appointments:
            channel = self.choose_channel(appointment.customer)
            for hours in self.policy.hours_before:
                raw_send_at = appointment.starts_at - timedelta(hours=hours)
                send_at, adjusted = self.apply_quiet_hours(raw_send_at)
                if send_at <= local_now:
                    continue
                body = self.render_reminder(appointment, channel)
                key = (appointment.id, channel.value, send_at.isoformat())
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                planned.append(
                    ReminderMessage(
                        appointment_id=appointment.id,
                        customer_id=appointment.customer.id,
                        channel=channel,
                        send_at=send_at,
                        body=body,
                        metadata={
                            "language": appointment.customer.preferred_language,
                            "hours_before": hours,
                            "template_type": "utility",
                            "quiet_hours_adjusted": adjusted,
                        },
                    )
                )
        return sorted(planned, key=lambda item: item.send_at)

    def apply_quiet_hours(self, send_at: datetime) -> tuple[datetime, bool]:
        local = send_at.astimezone(self.policy.timezone())
        hour = local.hour
        start = self.policy.quiet_start_hour
        end = self.policy.quiet_end_hour
        in_quiet = hour >= start or hour < end if start > end else start <= hour < end
        if not in_quiet:
            return local, False
        if hour < end:
            adjusted_date = (local - timedelta(days=1)).date()
        else:
            adjusted_date = local.date()
        adjusted = datetime(
            adjusted_date.year,
            adjusted_date.month,
            adjusted_date.day,
            self.policy.quiet_evening_hour,
            self.policy.quiet_evening_minute,
            tzinfo=self.policy.timezone(),
        )
        return adjusted, True

    def render_reminder(self, appointment: Appointment, channel: Channel | None = None) -> str:
        channel = channel or self.choose_channel(appointment.customer)
        language = appointment.customer.preferred_language
        when = format_israeli_datetime(appointment.starts_at, language)
        location = f"\nכתובת: {appointment.location}." if language == "he" and appointment.location else ""
        if language == "he":
            if channel == Channel.SMS:
                return f"תזכורת: התור שלך אצל {appointment.business_name} נקבע ל-{when}. לשינוי מועד נא להשיב 2 או ליצור קשר עם העסק."
            return (
                f"שלום {first_name(appointment.customer.name)}, תזכורת לתור אצל {appointment.business_name} ביום {when}."
                f"{location}\nלהגעה השיבי 1. לשינוי מועד השיבי 2. לביטול השיבי 3."
            )
        location_en = f" Location: {appointment.location}." if appointment.location else ""
        return (
            f"Reminder: your appointment with {appointment.business_name} is on {when}.{location_en} "
            "Reply 1 to confirm, 2 to reschedule, or 3 to cancel."
        )

    def render_rebooking_message(self, appointment: Appointment, slots: Sequence[datetime]) -> str:
        language = appointment.customer.preferred_language
        formatted_slots = [slot.astimezone(self.policy.timezone()).strftime("%d-%m-%Y %H:%M") for slot in slots]
        if language == "he":
            joined = ", ".join(formatted_slots[:-1]) + (" או " + formatted_slots[-1] if len(formatted_slots) > 1 else formatted_slots[0])
            return f"שלום {first_name(appointment.customer.name)}, נראה שלא הצלחת להגיע לתור היום. אפשר לקבוע מועד חדש: {joined}."
        joined_en = ", ".join(formatted_slots)
        return f"Hello {first_name(appointment.customer.name)}, it looks like the appointment was missed today. Available re-booking options: {joined_en}."

    def classify_reply(self, text: str) -> str:
        normalized = text.strip().lower()
        for keyword in self.policy.confirmation_keywords:
            if keyword.lower() in normalized:
                return "confirm"
        for keyword in self.policy.reschedule_keywords:
            if keyword.lower() in normalized:
                return "reschedule"
        for keyword in self.policy.cancel_keywords:
            if keyword.lower() in normalized:
                return "cancel"
        return "unknown"

    def send_message(self, message: ReminderMessage) -> ProviderResponse:
        if self.provider == Provider.MOCK:
            return ProviderResponse(True, 202, provider_message_id=f"mock-{message.appointment_id}-{int(message.send_at.timestamp())}", payload=message.to_dict())
        if self.provider == Provider.GENERIC:
            return self._send_generic(message)
        if self.provider == Provider.TWILIO:
            return self._send_twilio(message)
        if self.provider == Provider.WHATSAPP_CLOUD:
            return self._send_whatsapp_cloud(message)
        raise ReminderError("PROVIDER_UNSUPPORTED", f"unsupported provider {self.provider.value}")

    async def send_message_async(self, message: ReminderMessage) -> ProviderResponse:
        return await asyncio.to_thread(self.send_message, message)

    def _send_generic(self, message: ReminderMessage) -> ProviderResponse:
        url = self._credential("webhook_url")
        headers = {"Content-Type": "application/json"}
        token = self.credentials.get("webhook_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        status, payload = self._request_json(url, "POST", headers, json.dumps(message.to_dict()).encode("utf-8"))
        return self._provider_response_from_payload(status, payload)

    def _send_twilio(self, message: ReminderMessage) -> ProviderResponse:
        account_sid = self._credential("account_sid")
        from_value = self.credentials.get("from") or self.credentials.get("messaging_service_sid")
        if not from_value:
            raise ReminderError("TWILIO_SENDER_MISSING", "from or messaging_service_sid credential is required")
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        fields: dict[str, str] = {"To": message.metadata.get("to", ""), "Body": message.body}
        if not fields["To"]:
            fields["To"] = self._lookup_customer_phone(message)
        if self.credentials.get("messaging_service_sid"):
            fields["MessagingServiceSid"] = self.credentials["messaging_service_sid"]
        else:
            fields["From"] = from_value
        if self.credentials.get("status_callback"):
            fields["StatusCallback"] = self.credentials["status_callback"]
        data = urllib.parse.urlencode(fields).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        status, payload = self._request_json(url, "POST", headers, data)
        return self._provider_response_from_payload(status, payload)

    def _send_whatsapp_cloud(self, message: ReminderMessage) -> ProviderResponse:
        token = self._credential("token")
        phone_number_id = self._credential("phone_number_id")
        version = self.credentials.get("version", "v20.0")
        url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": self._lookup_customer_phone(message).replace("+", ""),
            "type": "text",
            "text": {"preview_url": False, "body": message.body},
        }
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        status, response_payload = self._request_json(url, "POST", headers, json.dumps(payload).encode("utf-8"))
        return self._provider_response_from_payload(status, response_payload)

    def _lookup_customer_phone(self, message: ReminderMessage) -> str:
        phone = message.metadata.get("phone_e164")
        if not phone:
            raise ReminderError("PHONE_MISSING", "message metadata must include phone_e164 for provider send")
        return normalize_israeli_mobile(str(phone))

    def _credential(self, key: str) -> str:
        value = self.credentials.get(key)
        if not value:
            raise ReminderError("CREDENTIAL_MISSING", f"missing credential: {key}")
        return value

    @staticmethod
    def _provider_response_from_payload(status: int, payload: dict[str, Any]) -> ProviderResponse:
        success = 200 <= status < 300
        provider_message_id = str(payload.get("sid") or payload.get("message_id") or payload.get("id") or "") or None
        error = payload.get("error") if isinstance(payload.get("error"), Mapping) else {}
        return ProviderResponse(
            success=success,
            status_code=status,
            provider_message_id=provider_message_id,
            error_code=str(error.get("code") or payload.get("error_code") or "") or None,
            error_message=str(error.get("message") or payload.get("error_message") or "") or None,
            payload=payload,
        )

    @staticmethod
    def _default_request_json(url: str, method: str, headers: Mapping[str, str], data: bytes | None) -> tuple[int, dict[str, Any]]:
        request = urllib.request.Request(url=url, method=method, headers=dict(headers), data=data)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read().decode("utf-8")
                return response.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                payload = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                payload = {"error_message": raw}
            return exc.code, payload


class NoShowTracker:
    """Track appointment outcomes and suggest re-booking slots."""

    def __init__(self, timezone_name: str = DEFAULT_TIMEZONE, business_start_hour: int = 9, business_end_hour: int = 17) -> None:
        self.timezone = ZoneInfo(timezone_name)
        self.business_start_hour = business_start_hour
        self.business_end_hour = business_end_hour
        self._events: list[dict[str, Any]] = []

    def record(self, appointment_id: str, customer_id: str, status: AppointmentStatus | str, occurred_at: datetime | None = None) -> None:
        status_value = AppointmentStatus(status).value
        timestamp = occurred_at or datetime.now(self.timezone)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=self.timezone)
        self._events.append(
            {
                "appointment_id": appointment_id,
                "customer_id": customer_id,
                "status": status_value,
                "occurred_at": timestamp.isoformat(),
            }
        )

    def stats(self) -> dict[str, Any]:
        completed = [event for event in self._events if event["status"] in {AppointmentStatus.ATTENDED.value, AppointmentStatus.NO_SHOW.value}]
        no_shows = [event for event in completed if event["status"] == AppointmentStatus.NO_SHOW.value]
        rate = len(no_shows) / len(completed) if completed else 0.0
        return {"completed_or_missed": len(completed), "no_show_count": len(no_shows), "no_show_rate": rate}

    def suggest_rebooking_slots(self, missed_start: datetime, count: int = 3) -> list[datetime]:
        if missed_start.tzinfo is None:
            missed_start = missed_start.replace(tzinfo=self.timezone)
        cursor = missed_start.astimezone(self.timezone) + timedelta(hours=2)
        slots: list[datetime] = []
        while len(slots) < count:
            if cursor.weekday() < 5 and self.business_start_hour <= cursor.hour < self.business_end_hour:
                slots.append(cursor.replace(minute=0, second=0, microsecond=0))
                cursor += timedelta(hours=4)
                continue
            cursor += timedelta(hours=1)
            if cursor.hour >= self.business_end_hour:
                next_day = (cursor + timedelta(days=1)).date()
                cursor = datetime(next_day.year, next_day.month, next_day.day, self.business_start_hour, 0, tzinfo=self.timezone)
        return slots

    @property
    def events(self) -> list[dict[str, Any]]:
        return list(self._events)


def appointment_from_dict(data: Mapping[str, Any]) -> Appointment:
    customer_data = data.get("customer")
    if not isinstance(customer_data, Mapping):
        raise ReminderError("CUSTOMER_MISSING", "appointment customer object is required")
    customer = Customer(
        id=str(customer_data["id"]),
        name=str(customer_data["name"]),
        phone_e164=normalize_israeli_mobile(str(customer_data["phone"])),
        preferred_language=str(customer_data.get("preferred_language", "he")),
        consent_whatsapp=bool(customer_data.get("consent_whatsapp", False)),
        consent_sms=bool(customer_data.get("consent_sms", False)),
        marketing_consent=bool(customer_data.get("marketing_consent", False)),
    )
    return Appointment(
        id=str(data["id"]),
        customer=customer,
        starts_at=parse_datetime(str(data["starts_at"])),
        business_name=str(data["business_name"]),
        service_name=str(data.get("service_name", "appointment")),
        location=str(data.get("location", "")),
        price_ils=int(data["price_ils"]) if data.get("price_ils") is not None else None,
        status=AppointmentStatus(str(data.get("status", AppointmentStatus.SCHEDULED.value))),
        cancel_until=parse_datetime(str(data["cancel_until"])) if data.get("cancel_until") else None,
    )
