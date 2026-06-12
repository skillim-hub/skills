"""Typed CRM conversation-sync client for Israeli businesses."""

from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Protocol, Sequence, cast

import httpx
import requests

ProviderName = Literal["monday", "hubspot", "salesforce"]
DEFAULT_HUBSPOT_API_VERSION = "2026-03"
DEFAULT_SALESFORCE_API_VERSION = "v67.0"
ChannelName = Literal["whatsapp", "email", "sms"]
DirectionName = Literal["inbound", "outbound", "system"]
EnvironmentName = Literal["sandbox", "production"]


class CRMIntegrationError(Exception):
    """Base integration error."""


class ValidationError(CRMIntegrationError):
    """Raised when local input is invalid."""


class ConsentRequiredError(CRMIntegrationError):
    """Raised when a marketing action lacks evidence of consent."""


class ProviderError(CRMIntegrationError):
    """Raised when a provider returns a non-success response."""

    def __init__(self, message: str, status_code: int | None = None, payload: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class RateLimitError(ProviderError):
    """Raised when a provider returns a rate-limit response."""


class SyncSession(Protocol):
    """Synchronous HTTP session protocol used for tests and adapters."""

    def post(self, url: str, headers: Mapping[str, str], json: Mapping[str, Any], timeout: int) -> Any:
        """Send a JSON POST request."""


@dataclass(slots=True)
class ProviderConfig:
    """Provider settings for one CRM sync run."""

    provider: ProviderName
    api_token: str
    base_url: str = ""
    monday_board_id: str | None = None
    monday_group_id: str = "topics"
    hubspot_api_version: str = DEFAULT_HUBSPOT_API_VERSION
    salesforce_api_version: str = DEFAULT_SALESFORCE_API_VERSION
    timeout_seconds: int = 30
    dry_run: bool = True
    environment: EnvironmentName = "sandbox"

    def resolved_base_url(self) -> str:
        """Return a provider base URL without a trailing slash."""
        if self.base_url:
            return self.base_url.rstrip("/")
        if self.provider == "monday":
            return "https://api.monday.com"
        if self.provider == "hubspot":
            return "https://api.hubapi.com"
        if self.provider == "salesforce":
            raise ValidationError("Salesforce requires base_url, for example https://example.my.salesforce.com")
        raise ValidationError(f"Unsupported provider: {self.provider}")


@dataclass(slots=True)
class Contact:
    """Customer or lead identity."""

    full_name: str
    phone: str | None = None
    email: str | None = None
    company: str | None = None
    city: str | None = None
    preferred_language: str = "he"
    external_id: str | None = None

    def normalized(self) -> "Contact":
        """Normalize name, phone, email, and optional fields."""
        phone = normalize_israeli_phone(self.phone) if self.phone else None
        email = canonical_email(self.email) if self.email else None
        name = normalize_name(self.full_name)
        if not phone and not email and not self.external_id:
            raise ValidationError("Contact requires phone, email, or external_id")
        return Contact(
            full_name=name,
            phone=phone,
            email=email,
            company=(self.company or "").strip() or None,
            city=(self.city or "").strip() or None,
            preferred_language=(self.preferred_language or "he").strip().lower(),
            external_id=(self.external_id or "").strip() or None,
        )


@dataclass(slots=True)
class ConversationMessage:
    """Single message from WhatsApp, email, or SMS."""

    source_message_id: str
    sent_at: str
    direction: DirectionName
    body: str
    sender: str | None = None
    attachments: list[dict[str, Any]] = field(default_factory=list)

    def clean_body(self) -> str:
        """Return body without surrounding whitespace."""
        return self.body.strip()

    def validate(self) -> None:
        """Validate required message fields."""
        if not self.source_message_id.strip():
            raise ValidationError("Message requires source_message_id")
        if self.direction not in ("inbound", "outbound", "system"):
            raise ValidationError(f"Unsupported direction: {self.direction}")
        if not self.clean_body() and not self.attachments:
            raise ValidationError("Message requires body or attachment metadata")
        parse_datetime(self.sent_at)


@dataclass(slots=True)
class ConsentRecord:
    """Marketing and service communication consent evidence."""

    marketing_opt_in: bool = False
    evidence: str | None = None
    captured_at: str | None = None
    channel: ChannelName | None = None
    service_context: str | None = None

    def validate_for_marketing(self) -> None:
        """Require evidence for marketing communication."""
        if self.marketing_opt_in and not (self.evidence and self.evidence.strip()):
            raise ConsentRequiredError("Marketing opt-in requires evidence")


@dataclass(slots=True)
class ConversationThread:
    """Conversation thread ready for CRM synchronization."""

    source_channel: ChannelName
    source_thread_id: str
    subject: str
    contact: Contact
    messages: list[ConversationMessage]
    consent: ConsentRecord = field(default_factory=ConsentRecord)
    business_purpose: str = "service"

    def normalized(self) -> "ConversationThread":
        """Normalize the thread and validate child objects."""
        if self.source_channel not in ("whatsapp", "email", "sms"):
            raise ValidationError(f"Unsupported source channel: {self.source_channel}")
        if not self.source_thread_id.strip():
            raise ValidationError("Thread requires source_thread_id")
        contact = self.contact.normalized()
        messages = dedupe_messages(sorted(self.messages, key=lambda msg: parse_datetime(msg.sent_at)))
        for message in messages:
            message.validate()
        if not messages:
            raise ValidationError("Thread requires at least one valid message")
        return ConversationThread(
            source_channel=self.source_channel,
            source_thread_id=self.source_thread_id.strip(),
            subject=self.subject.strip() or self.business_purpose,
            contact=contact,
            messages=messages,
            consent=self.consent,
            business_purpose=self.business_purpose.strip() or "service",
        )


@dataclass(slots=True)
class SyncResult:
    """Result returned by a dry-run or live synchronization."""

    provider: ProviderName
    dry_run: bool
    action: str
    contact_key: str
    crm_object_id: str | None
    message_count: int
    warnings: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)
    audit_events: list[dict[str, Any]] = field(default_factory=list)


def normalize_israeli_phone(phone: str | None) -> str:
    """Normalize Israeli phone numbers to E.164."""
    if phone is None:
        raise ValidationError("Phone is required")
    raw = str(phone).strip()
    if not raw:
        raise ValidationError("Phone is empty")
    compact = re.sub(r"[\s().-]", "", raw).replace("־", "").replace("–", "")
    if compact.startswith("00"):
        compact = "+" + compact[2:]
    if compact.startswith("+"):
        digits = "+" + re.sub(r"\D", "", compact[1:])
        if re.fullmatch(r"\+\d{8,15}", digits):
            return digits
        raise ValidationError(f"Invalid E.164 phone: {phone}")
    digits = re.sub(r"\D", "", compact)
    if digits.startswith("972"):
        candidate = "+972" + digits[3:]
    elif digits.startswith("0") and len(digits) in (9, 10):
        candidate = "+972" + digits[1:]
    elif len(digits) in (8, 9) and digits[0] in "234589":
        candidate = "+972" + digits
    else:
        raise ValidationError(f"Invalid Israeli phone: {phone}")
    if not re.fullmatch(r"\+972\d{7,9}", candidate):
        raise ValidationError(f"Invalid Israeli phone length: {phone}")
    return candidate


def canonical_email(email: str | None) -> str:
    """Normalize an email address."""
    if email is None:
        raise ValidationError("Email is required")
    cleaned = email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", cleaned):
        raise ValidationError(f"Invalid email: {email}")
    return cleaned


def normalize_name(name: str) -> str:
    """Normalize a human name."""
    cleaned = re.sub(r"\s+", " ", (name or "").strip(" \t\r\n,.;:"))
    if not cleaned:
        raise ValidationError("Full name is required")
    return cleaned


def normalize_channel(channel: str) -> ChannelName:
    """Normalize channel aliases."""
    normalized = channel.strip().lower().replace("-", "_")
    aliases = {
        "wa": "whatsapp",
        "whatsapp_business": "whatsapp",
        "mail": "email",
        "gmail": "email",
        "text": "sms",
        "message": "sms",
        "מסרון": "sms",
        "דואל": "email",
    }
    value = aliases.get(normalized, normalized)
    if value not in ("whatsapp", "email", "sms"):
        raise ValidationError(f"Unsupported channel: {channel}")
    return cast(ChannelName, value)


def parse_il_date(value: str) -> datetime:
    """Parse Israeli localized dates in DD/MM/YYYY format."""
    try:
        return datetime.strptime(value.strip(), "%d/%m/%Y")
    except ValueError as exc:
        raise ValidationError(f"Date must use DD/MM/YYYY: {value}") from exc


def format_il_date(value: datetime) -> str:
    """Format a date as DD/MM/YYYY."""
    return value.strftime("%d/%m/%Y")


def parse_datetime(value: str) -> datetime:
    """Parse ISO 8601 or DD/MM/YYYY HH:MM:SS timestamps."""
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        try:
            return datetime.strptime(text, "%d/%m/%Y %H:%M:%S")
        except ValueError as exc:
            raise ValidationError(f"Invalid datetime: {value}") from exc


def build_dedupe_key(contact: Contact) -> str:
    """Build a deterministic deduplication key."""
    normalized = contact.normalized()
    if normalized.external_id:
        return f"external:{normalized.external_id}"
    if normalized.phone:
        return f"phone:{normalized.phone}"
    if normalized.email:
        return f"email:{normalized.email}"
    raise ValidationError("Cannot build dedupe key without identifier")


def split_hebrew_name(full_name: str) -> tuple[str, str]:
    """Split a Hebrew full name into first and last name components."""
    parts = normalize_name(full_name).split(" ")
    if len(parts) == 1:
        return "", parts[0]
    return " ".join(parts[:-1]), parts[-1]


def classify_business_purpose(text: str) -> str:
    """Classify a message into a business purpose bucket."""
    lowered = text.lower()
    if any(term in lowered for term in ["הצעת מחיר", "מחיר", "quote", "demo", "כמה עולה"]):
        return "sales"
    if any(term in lowered for term in ["חשבונית", "קבלה", "מסמכים", "ניכוי מס", "ניהול ספרים"]):
        return "admin"
    if any(term in lowered for term in ["לא הגיע", "תקול", "שבור", "אחריות", "complaint"]):
        return "support"
    if any(term in lowered for term in ["תור", "לקבוע", "פגישה", "appointment"]):
        return "appointment"
    return "service"


def is_opt_out_text(text: str) -> bool:
    """Detect common opt-out phrases."""
    return text.strip().lower() in {"הסר", "די", "stop", "unsubscribe", "remove", "בטל"}


def is_explicit_opt_in_text(text: str) -> bool:
    """Detect common explicit opt-in phrases."""
    normalized = text.strip().lower()
    terms = ["מאשר", "מאשרת", "מסכים", "מסכימה", "לקבל עדכונים", "לקבל מבצעים", "i agree", "opt in", "subscribe", "yes send"]
    return any(term in normalized for term in terms)


def redact_sensitive_text(text: str) -> str:
    """Redact Israeli ID numbers, payment-card numbers, and short security codes."""
    redacted = re.sub(r"(?<!\d)\d{9}(?!\d)", "[REDACTED_ID]", text)
    redacted = re.sub(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)", "[REDACTED_CARD]", redacted)
    redacted = re.sub(r"(הקוד\s+(?:הוא|שלך)?\s*)\d{4,8}", r"\1[REDACTED_CODE]", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(code\s*(?:is|:)?\s*)\d{4,8}", r"\1[REDACTED_CODE]", redacted, flags=re.IGNORECASE)
    return redacted


def classify_message_direction(sender: str | None, business_numbers: Sequence[str]) -> DirectionName:
    """Infer whether a message was sent by the business or the customer."""
    if not sender:
        return "inbound"
    try:
        normalized_sender = normalize_israeli_phone(sender)
        normalized_business = {normalize_israeli_phone(number) for number in business_numbers}
    except ValidationError:
        return "inbound"
    return "outbound" if normalized_sender in normalized_business else "inbound"


def is_business_hours_il(dt: datetime) -> bool:
    """Return True during common Israeli business hours, Sunday through Thursday."""
    weekday = dt.weekday()
    return weekday in {6, 0, 1, 2, 3} and time(8, 0) <= dt.time() <= time(18, 0)


def dedupe_messages(messages: Sequence[ConversationMessage]) -> list[ConversationMessage]:
    """Remove duplicate source messages while preserving the first occurrence."""
    seen: set[str] = set()
    unique: list[ConversationMessage] = []
    for message in messages:
        key = message.source_message_id.strip()
        if key in seen:
            continue
        seen.add(key)
        unique.append(message)
    return unique


def make_idempotency_key(thread: ConversationThread, message: ConversationMessage, provider: ProviderName) -> str:
    """Build an idempotency key for audit and retry logic."""
    return f"{thread.source_channel}:{thread.source_thread_id}:{message.source_message_id}:{provider}"


def load_thread_from_mapping(data: Mapping[str, Any]) -> ConversationThread:
    """Load a conversation thread from a mapping."""
    contact_data = data.get("contact", {})
    thread_data = data.get("thread", data)
    consent_data = data.get("consent", {})
    contact = Contact(
        full_name=contact_data.get("full_name") or contact_data.get("name") or "Unknown",
        phone=contact_data.get("phone") or contact_data.get("phone_e164"),
        email=contact_data.get("email"),
        company=contact_data.get("company"),
        city=contact_data.get("city"),
        preferred_language=contact_data.get("preferred_language", "he"),
        external_id=contact_data.get("external_id"),
    )
    messages = [
        ConversationMessage(
            source_message_id=str(raw.get("source_message_id") or raw.get("id") or raw.get("message_id") or ""),
            sent_at=str(raw.get("sent_at") or raw.get("received_at") or datetime.now(timezone.utc).isoformat()),
            direction=cast(DirectionName, raw.get("direction") or "inbound"),
            sender=raw.get("sender"),
            body=str(raw.get("body") or raw.get("text") or raw.get("message") or ""),
            attachments=list(raw.get("attachments") or []),
        )
        for raw in thread_data.get("messages", data.get("messages", []))
    ]
    return ConversationThread(
        source_channel=normalize_channel(thread_data.get("source_channel") or data.get("source_channel") or "whatsapp"),
        source_thread_id=str(thread_data.get("source_thread_id") or data.get("source_thread_id") or "manual-thread"),
        subject=str(thread_data.get("subject") or data.get("subject") or "Conversation"),
        contact=contact,
        messages=messages,
        consent=ConsentRecord(
            marketing_opt_in=bool(consent_data.get("marketing_opt_in", False)),
            evidence=consent_data.get("evidence"),
            captured_at=consent_data.get("captured_at"),
            channel=normalize_channel(consent_data["channel"]) if consent_data.get("channel") else None,
            service_context=consent_data.get("service_context"),
        ),
        business_purpose=str(data.get("business_purpose") or thread_data.get("business_purpose") or "service"),
    )


def load_thread_file(path: str | Path) -> ConversationThread:
    """Load a JSON thread file."""
    return load_thread_from_mapping(json.loads(Path(path).read_text(encoding="utf-8")))


def write_audit_events(path: str | Path, events: Iterable[Mapping[str, Any]]) -> None:
    """Append audit events to a JSONL file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(dict(event), ensure_ascii=False, sort_keys=True) + "\n")


def provider_token_from_env(provider: ProviderName, environment: EnvironmentName = "sandbox") -> str:
    """Read a provider token from environment variables."""
    prefix = {"monday": "MONDAY", "hubspot": "HUBSPOT", "salesforce": "SALESFORCE"}[provider]
    names = [f"{prefix}_API_TOKEN_{environment.upper()}", f"{prefix}_API_TOKEN"]
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def result_to_dict(result: SyncResult) -> dict[str, Any]:
    """Convert a sync result to a JSON-serializable dictionary."""
    return asdict(result)


def audit_template(crm_object_id: str | None = None, provider: ProviderName = "hubspot") -> dict[str, Any]:
    """Return an audit JSONL event template."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "run_id": now,
        "idempotency_key": "source:thread:message:provider",
        "source_channel": "whatsapp",
        "source_thread_id": "thread-id",
        "source_message_id": "message-id",
        "crm_provider": provider,
        "crm_object_type": "contact",
        "crm_object_id": crm_object_id or "crm-id",
        "action": "sync_message",
        "status": "planned",
        "redacted": False,
        "created_at": now,
    }


class CRMIntegrationClient:
    """Sync normalized conversations into a configured CRM provider."""

    def __init__(self, config: ProviderConfig, session: SyncSession | None = None) -> None:
        """Create a client."""
        self.config = config
        self.session = session or requests.Session()

    @classmethod
    def from_env(
        cls,
        provider: ProviderName,
        *,
        environment: EnvironmentName = "sandbox",
        base_url: str = "",
        dry_run: bool | None = None,
        monday_board_id: str | None = None,
    ) -> "CRMIntegrationClient":
        """Create a client from environment variables."""
        token = provider_token_from_env(provider, environment)
        effective_dry_run = environment == "sandbox" if dry_run is None else dry_run
        if not token and not effective_dry_run:
            prefix = {"monday": "MONDAY", "hubspot": "HUBSPOT", "salesforce": "SALESFORCE"}[provider]
            raise ValidationError(f"Missing token environment variable: {prefix}_API_TOKEN")
        base = base_url or os.getenv(f"{provider.upper()}_BASE_URL", "")
        board = monday_board_id or os.getenv("MONDAY_BOARD_ID", "") or None
        return cls(
            ProviderConfig(
                provider=provider,
                api_token=token or "dry-run-token",
                base_url=base,
                monday_board_id=board,
                dry_run=effective_dry_run,
                environment=environment,
            )
        )

    def build_payload(self, thread: ConversationThread) -> dict[str, Any]:
        """Build the provider-specific request payload."""
        normalized = thread.normalized()
        if self.config.provider == "monday":
            return self._build_monday_payload(normalized)
        if self.config.provider == "hubspot":
            return self._build_hubspot_payload(normalized)
        if self.config.provider == "salesforce":
            return self._build_salesforce_payload(normalized)
        raise ValidationError(f"Unsupported provider: {self.config.provider}")

    def sync_thread(self, thread: ConversationThread, *, marketing_action: bool = False) -> SyncResult:
        """Synchronize one conversation thread."""
        normalized = thread.normalized()
        if marketing_action:
            normalized.consent.validate_for_marketing()
            if not normalized.consent.marketing_opt_in:
                raise ConsentRequiredError("Marketing action requires explicit opt-in")
        payload = self.build_payload(normalized)
        contact_key = build_dedupe_key(normalized.contact)
        warnings = self._warnings(normalized)
        status = "planned" if self.config.dry_run else "pending"
        audit_events = self._build_audit_events(normalized, crm_object_id=None, status=status)
        if self.config.dry_run:
            return SyncResult(self.config.provider, True, "planned_sync", contact_key, None, len(normalized.messages), warnings, payload, audit_events)
        response_payload = self._post_payload(payload)
        crm_id = extract_crm_id(self.config.provider, response_payload)
        audit_events = self._build_audit_events(normalized, crm_object_id=crm_id, status="success")
        return SyncResult(self.config.provider, False, "synced", contact_key, crm_id, len(normalized.messages), warnings, payload, audit_events)

    async def async_sync_thread(self, thread: ConversationThread, *, marketing_action: bool = False) -> SyncResult:
        """Asynchronously synchronize one conversation thread."""
        normalized = thread.normalized()
        if marketing_action:
            normalized.consent.validate_for_marketing()
            if not normalized.consent.marketing_opt_in:
                raise ConsentRequiredError("Marketing action requires explicit opt-in")
        payload = self.build_payload(normalized)
        contact_key = build_dedupe_key(normalized.contact)
        warnings = self._warnings(normalized)
        if self.config.dry_run:
            await asyncio.sleep(0)
            return SyncResult(self.config.provider, True, "planned_sync", contact_key, None, len(normalized.messages), warnings, payload, self._build_audit_events(normalized, crm_object_id=None, status="planned"))
        response_payload = await self._apost_payload(payload)
        crm_id = extract_crm_id(self.config.provider, response_payload)
        return SyncResult(self.config.provider, False, "synced", contact_key, crm_id, len(normalized.messages), warnings, payload, self._build_audit_events(normalized, crm_object_id=crm_id, status="success"))

    def create_response_summary(self, result: SyncResult) -> dict[str, Any]:
        """Return a minimal create response suitable for shell chaining."""
        return {
            "provider": result.provider,
            "crm_object_id": result.crm_object_id,
            "contact_key": result.contact_key,
            "message_count": result.message_count,
        }

    def _headers(self) -> dict[str, str]:
        if self.config.provider == "monday":
            return {"Authorization": self.config.api_token, "Content-Type": "application/json"}
        return {"Authorization": f"Bearer {self.config.api_token}", "Content-Type": "application/json"}

    def _endpoint(self) -> str:
        base = self.config.resolved_base_url()
        if self.config.provider == "monday":
            return f"{base}/v2"
        if self.config.provider == "hubspot":
            version = self.config.hubspot_api_version.strip().strip("/") or DEFAULT_HUBSPOT_API_VERSION
            return f"{base}/crm/objects/{version}/contacts"
        if self.config.provider == "salesforce":
            version = self.config.salesforce_api_version.strip().strip("/") or DEFAULT_SALESFORCE_API_VERSION
            if not version.startswith("v"):
                version = f"v{version}"
            return f"{base}/services/data/{version}/sobjects/Lead"
        raise ValidationError(f"Unsupported provider: {self.config.provider}")

    def _post_payload(self, payload: Mapping[str, Any]) -> Any:
        response = self.session.post(self._endpoint(), headers=self._headers(), json=payload, timeout=self.config.timeout_seconds)
        return handle_response(response)

    async def _apost_payload(self, payload: Mapping[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.post(self._endpoint(), headers=self._headers(), json=payload)
        return handle_response(response)

    def _warnings(self, thread: ConversationThread) -> list[str]:
        warnings: list[str] = []
        if not thread.consent.marketing_opt_in:
            warnings.append("marketing_opt_in_false")
        if any(message.attachments for message in thread.messages):
            warnings.append("attachments_metadata_review")
        if any(redact_sensitive_text(message.body) != message.body for message in thread.messages):
            warnings.append("sensitive_text_redacted")
        return warnings

    def _build_audit_events(self, thread: ConversationThread, *, crm_object_id: str | None, status: str) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        return [
            {
                "idempotency_key": make_idempotency_key(thread, message, self.config.provider),
                "source_channel": thread.source_channel,
                "source_thread_id": thread.source_thread_id,
                "source_message_id": message.source_message_id,
                "crm_provider": self.config.provider,
                "crm_object_id": crm_object_id,
                "action": "sync_message",
                "status": status,
                "redacted": redact_sensitive_text(message.body) != message.body,
                "created_at": now,
            }
            for message in thread.messages
        ]

    def _last_message_summary(self, thread: ConversationThread) -> str:
        message = thread.messages[-1]
        clean = redact_sensitive_text(message.clean_body())
        return f"{format_il_date(parse_datetime(message.sent_at))} {thread.source_channel} {message.direction}: {clean}"

    def _conversation_note(self, thread: ConversationThread) -> str:
        return "\n".join(f"{format_il_date(parse_datetime(m.sent_at))} {m.direction}: {redact_sensitive_text(m.clean_body())}" for m in thread.messages)

    def _build_monday_payload(self, thread: ConversationThread) -> dict[str, Any]:
        board_id = self.config.monday_board_id or ("DRY_RUN_BOARD" if self.config.dry_run else None)
        if board_id is None:
            raise ValidationError("Monday sync requires monday_board_id")
        values = {
            "phone": {"phone": thread.contact.phone, "countryShortName": "IL"} if thread.contact.phone else None,
            "email": {"email": thread.contact.email, "text": thread.contact.email} if thread.contact.email else None,
            "channel": {"label": thread.source_channel.title()},
            "last_message": self._last_message_summary(thread),
            "source_thread_id": thread.source_thread_id,
            "consent": {"label": "Marketing Opt-In" if thread.consent.marketing_opt_in else "Service Only"},
        }
        return {
            "query": "mutation ($board: ID!, $group: String!, $name: String!, $values: JSON!) { create_item(board_id: $board, group_id: $group, item_name: $name, column_values: $values) { id name } }",
            "variables": {
                "board": board_id,
                "group": self.config.monday_group_id,
                "name": thread.contact.full_name,
                "values": json.dumps({k: v for k, v in values.items() if v is not None}, ensure_ascii=False),
            },
        }

    def _build_hubspot_payload(self, thread: ConversationThread) -> dict[str, Any]:
        first, last = split_hebrew_name(thread.contact.full_name)
        properties = {
            "firstname": first,
            "lastname": last,
            "phone": thread.contact.phone,
            "email": thread.contact.email,
            "company": thread.contact.company,
            "lifecyclestage": "lead" if classify_business_purpose(self._conversation_note(thread)) == "sales" else "customer",
            "crm_source_channel": thread.source_channel,
            "crm_source_thread_id": thread.source_thread_id,
            "crm_marketing_opt_in": str(thread.consent.marketing_opt_in).lower(),
            "hs_language": thread.contact.preferred_language,
            "external_id": thread.contact.external_id,
        }
        return {"properties": {key: value for key, value in properties.items() if value}}

    def _build_salesforce_payload(self, thread: ConversationThread) -> dict[str, Any]:
        first, last = split_hebrew_name(thread.contact.full_name)
        payload = {
            "FirstName": first or None,
            "LastName": last,
            "Company": thread.contact.company or thread.contact.full_name,
            "Phone": thread.contact.phone,
            "Email": thread.contact.email,
            "LeadSource": thread.source_channel.title(),
            "Source_Channel__c": thread.source_channel.title(),
            "Source_Thread_ID__c": thread.source_thread_id,
            "Marketing_Opt_In__c": thread.consent.marketing_opt_in,
            "Consent_Evidence__c": thread.consent.evidence,
            "External_ID__c": thread.contact.external_id,
            "Description": self._conversation_note(thread),
            "Status": "Open - Not Contacted" if classify_business_purpose(self._conversation_note(thread)) == "sales" else "Working",
        }
        return {key: value for key, value in payload.items() if value is not None}


def handle_response(response: Any) -> Any:
    """Convert provider responses to payloads or typed exceptions."""
    status_code = int(getattr(response, "status_code", 0))
    try:
        payload = response.json()
    except Exception:
        payload = getattr(response, "text", "")
    if status_code == 429:
        raise RateLimitError("Provider rate limit", status_code=status_code, payload=payload)
    if status_code < 200 or status_code >= 300:
        raise ProviderError(f"Provider error {status_code}", status_code=status_code, payload=payload)
    return payload


def extract_crm_id(provider: ProviderName, payload: Any) -> str | None:
    """Extract a created CRM object id from common provider responses."""
    if not isinstance(payload, Mapping):
        return None
    if provider == "monday":
        data = payload.get("data", {})
        if isinstance(data, Mapping):
            item = data.get("create_item") or data.get("create_update")
            if isinstance(item, Mapping) and item.get("id"):
                return str(item.get("id"))
    if provider in ("hubspot", "salesforce") and payload.get("id"):
        return str(payload.get("id"))
    return None
