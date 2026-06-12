#!/usr/bin/env python3
"""Typed helper for Hebrew customer-feedback collection campaigns.

The module is intentionally self-contained so it can be copied into an existing
automation repository. Network sending is optional and dry-run is the safe default.
"""

from __future__ import annotations

import asyncio
import csv
import dataclasses
import datetime as dt
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional, Protocol, Sequence
from urllib.parse import quote, quote_plus

try:  # optional runtime dependency
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore[assignment]


HEBREW_RE = re.compile(r"[\u0590-\u05FF]")
URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
INDEPENDENT_OPT_OUT_RE = re.compile(
    r"(^|\s)(הסר|הסרה|להסרה|stop|unsubscribe|עצור|בטל)(\s|$|:)",
    re.IGNORECASE,
)
INCENTIVE_RE = re.compile(
    r"(5\s*כוכבים|חמישה\s*כוכבים|דירוג\s*5|הנחה|קופון|מתנה|הגרלה|פרס)",
    re.IGNORECASE,
)
COMPLAINT_TAGS = {"open_complaint", "refund_pending", "chargeback", "dispute", "low_rating"}
SENSITIVE_WORDS = {
    "אבחון",
    "טיפול נפשי",
    "פסיכולוג",
    "פסיכיאטר",
    "תרופה",
    "בדיקה רפואית",
    "חוב",
    "עיקול",
    "תביעה",
}


class Channel(str, Enum):
    """Supported delivery channels."""

    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"


class ReviewPlatform(str, Enum):
    """Supported public or private review destinations."""

    GOOGLE = "google"
    FACEBOOK = "facebook"
    ZAP = "zap"
    EASY = "easy"
    MIDRAG = "midrag"
    B144 = "b144"
    CUSTOM = "custom"


class ConsentBasis(str, Enum):
    """Operational consent categories for campaign planning."""

    TRANSACTION_FOLLOWUP = "transaction_followup"
    EXPLICIT_OPT_IN = "explicit_opt_in"
    EXISTING_CUSTOMER = "existing_customer"
    MANUAL_REVIEW = "manual_review"
    NONE = "none"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class DeliveryStatus(str, Enum):
    PLANNED = "planned"
    SKIPPED = "skipped"
    DRY_RUN = "dry_run"
    QUEUED = "queued"
    FAILED = "failed"


@dataclass(frozen=True)
class ComplianceIssue:
    """Validation result item."""

    code: str
    message: str
    severity: Severity = Severity.WARNING


@dataclass(frozen=True)
class Contact:
    """Customer contact record."""

    full_name: str
    phone: str | None = None
    email: str | None = None
    consent: bool = True
    consent_basis: ConsentBasis = ConsentBasis.TRANSACTION_FOLLOWUP
    preferred_channel: Channel | None = None
    last_interaction_date: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    rating: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def first_name(self) -> str:
        clean = self.full_name.strip()
        if not clean:
            return "לקוח/ה"
        return clean.split()[0]


@dataclass(frozen=True)
class BusinessProfile:
    """Business configuration and review destinations."""

    display_name: str
    city: str | None = None
    google_place_id: str | None = None
    facebook_page_url: str | None = None
    zap_url: str | None = None
    easy_url: str | None = None
    midrag_url: str | None = None
    b144_url: str | None = None
    custom_review_url: str | None = None
    private_feedback_url: str | None = None
    support_email: str | None = None
    branch_name: str | None = None

    def branch_display(self) -> str:
        if self.branch_name:
            return f"{self.display_name} - {self.branch_name}"
        return self.display_name


@dataclass(frozen=True)
class Message:
    """Rendered outbound message."""

    channel: Channel
    to: str
    body: str
    subject: str | None = None
    review_url: str | None = None
    contact_name: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeliveryPlanItem:
    """Single planned campaign item."""

    contact: Contact
    message: Message | None
    status: DeliveryStatus
    issues: tuple[ComplianceIssue, ...] = field(default_factory=tuple)
    send_after: str | None = None


@dataclass(frozen=True)
class SendResult:
    """Provider send result."""

    status: DeliveryStatus
    message_id: str | None = None
    provider_response: Mapping[str, Any] = field(default_factory=dict)
    error: str | None = None
    retryable: bool = False


class SyncTransport(Protocol):
    def __call__(self, channel: Channel, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


class AsyncTransport(Protocol):
    async def __call__(self, channel: Channel, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


class FeedbackCollectorError(Exception):
    """Base class for helper errors."""


class InvalidPhoneNumber(FeedbackCollectorError):
    """Raised when an Israeli phone number cannot be normalized."""


class MissingReviewDestination(FeedbackCollectorError):
    """Raised when a platform lacks the required destination configuration."""


class ConsentRequired(FeedbackCollectorError):
    """Raised when a contact cannot be sent to because consent is false."""


def contains_hebrew(text: str) -> bool:
    """Return true when text contains Hebrew characters."""

    return bool(HEBREW_RE.search(text))


def detect_opt_out(text: str) -> bool:
    """Detect common Hebrew and English opt-out replies."""

    return bool(INDEPENDENT_OPT_OUT_RE.search(text.strip()))


def normalize_israeli_phone(phone: str) -> str:
    """Normalize an Israeli phone number to E.164.

    Examples:
        050-123-4567 -> +972501234567
        972501234567 -> +972501234567
        +972501234567 -> +972501234567
    """

    original = phone
    cleaned = re.sub(r"[^\d+]", "", phone.strip())
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    if cleaned.startswith("+972"):
        digits = "972" + re.sub(r"\D", "", cleaned[4:])
    elif cleaned.startswith("972"):
        digits = cleaned
    elif cleaned.startswith("0"):
        digits = "972" + cleaned[1:]
    else:
        raise InvalidPhoneNumber(f"Cannot normalize Israeli phone number: {original}")

    if not re.fullmatch(r"972\d{8,9}", digits):
        raise InvalidPhoneNumber(f"Invalid Israeli phone number length: {original}")
    return "+" + digits


def is_probable_israeli_mobile(phone: str) -> bool:
    """Return true when a phone looks like an Israeli mobile number."""

    try:
        normalized = normalize_israeli_phone(phone)
    except InvalidPhoneNumber:
        return False
    return bool(re.fullmatch(r"\+9725\d{8}", normalized))


def build_review_url(platform: ReviewPlatform | str, business: BusinessProfile) -> str:
    """Build or return the configured review destination URL."""

    platform = ReviewPlatform(platform)
    if platform is ReviewPlatform.GOOGLE:
        if not business.google_place_id:
            raise MissingReviewDestination("google_place_id is required for Google review URLs")
        query = business.branch_display() or business.display_name
        return (
            "https://www.google.com/maps/search/?api=1"
            f"&query={quote_plus(query)}"
            f"&query_place_id={quote(business.google_place_id)}"
        )
    if platform is ReviewPlatform.FACEBOOK:
        if not business.facebook_page_url:
            raise MissingReviewDestination("facebook_page_url is required for Facebook reviews")
        return business.facebook_page_url.rstrip("/") + "/reviews/"
    if platform is ReviewPlatform.ZAP:
        if not business.zap_url:
            raise MissingReviewDestination("zap_url is required for Zap")
        return business.zap_url
    if platform is ReviewPlatform.EASY:
        if not business.easy_url:
            raise MissingReviewDestination("easy_url is required for Easy")
        return business.easy_url
    if platform is ReviewPlatform.MIDRAG:
        if not business.midrag_url:
            raise MissingReviewDestination("midrag_url is required for Midrag")
        return business.midrag_url
    if platform is ReviewPlatform.B144:
        if not business.b144_url:
            raise MissingReviewDestination("b144_url is required for B144")
        return business.b144_url
    if platform is ReviewPlatform.CUSTOM:
        if not business.custom_review_url:
            raise MissingReviewDestination("custom_review_url is required for custom reviews")
        return business.custom_review_url
    raise MissingReviewDestination(f"Unsupported review platform: {platform}")


def classify_rating(rating: int | None, scale_max: int = 5) -> str:
    """Classify a known satisfaction score."""

    if rating is None:
        return "unknown"
    if scale_max <= 5:
        if rating >= 5:
            return "promoter"
        if rating >= 4:
            return "passive"
        return "detractor"
    if rating >= 9:
        return "promoter"
    if rating >= 7:
        return "passive"
    return "detractor"


def choose_channel(contact: Contact, requested: Channel | None = None) -> Channel | None:
    """Choose a reachable channel for a contact."""

    if requested:
        return requested
    if contact.preferred_channel:
        return contact.preferred_channel
    if contact.phone and is_probable_israeli_mobile(contact.phone):
        return Channel.WHATSAPP
    if contact.email:
        return Channel.EMAIL
    if contact.phone:
        return Channel.SMS
    return None


def validate_contact_for_channel(contact: Contact, channel: Channel) -> tuple[ComplianceIssue, ...]:
    """Validate a contact before planning a message."""

    issues: list[ComplianceIssue] = []
    if not contact.consent or contact.consent_basis is ConsentBasis.NONE:
        issues.append(
            ComplianceIssue(
                "ConsentRequired",
                "Contact lacks a usable consent or transactional basis.",
                Severity.ERROR,
            )
        )
    if COMPLAINT_TAGS.intersection(set(contact.tags)):
        issues.append(
            ComplianceIssue(
                "OpenComplaint",
                "Contact has complaint/refund/dispute tags; use private recovery route.",
                Severity.ERROR,
            )
        )
    if channel in {Channel.WHATSAPP, Channel.SMS}:
        if not contact.phone:
            issues.append(ComplianceIssue("MissingPhone", "Phone is required for this channel.", Severity.ERROR))
        else:
            try:
                normalize_israeli_phone(contact.phone)
            except InvalidPhoneNumber as exc:
                issues.append(ComplianceIssue("InvalidPhoneNumber", str(exc), Severity.ERROR))
            if channel is Channel.SMS and contact.phone and not is_probable_israeli_mobile(contact.phone):
                issues.append(
                    ComplianceIssue("NonMobileSms", "SMS should be sent only to probable mobile numbers.", Severity.ERROR)
                )
    if channel is Channel.EMAIL and not contact.email:
        issues.append(ComplianceIssue("MissingEmail", "Email is required for email channel.", Severity.ERROR))
    return tuple(issues)


def validate_message(message: Message, require_unsubscribe: bool = True) -> tuple[ComplianceIssue, ...]:
    """Validate Hebrew message quality and compliance guardrails."""

    issues: list[ComplianceIssue] = []
    body = message.body.strip()
    if not contains_hebrew(body):
        issues.append(ComplianceIssue("NoHebrew", "Message should contain natural Hebrew.", Severity.WARNING))
    if URL_RE.match(body):
        issues.append(
            ComplianceIssue("UrlFirst", "Start with Hebrew text; put the URL on a separate line.", Severity.WARNING)
        )
    if require_unsubscribe and not detect_opt_out(body):
        issues.append(ComplianceIssue("UnsubscribeMissing", "Add opt-out wording such as: להסרה: השב/י הסר.", Severity.WARNING))
    if message.channel is Channel.SMS and len(body) > 160:
        issues.append(ComplianceIssue("LongSms", "SMS is longer than 160 characters; expect multi-segment cost.", Severity.INFO))
    if INCENTIVE_RE.search(body) and ("חוות דעת" in body or "דירוג" in body or "כוכבים" in body):
        issues.append(
            ComplianceIssue(
                "IncentiveRisk",
                "Avoid incentives or pressure tied to ratings or positive reviews.",
                Severity.WARNING,
            )
        )
    if any(word in body for word in SENSITIVE_WORDS):
        issues.append(
            ComplianceIssue(
                "SensitiveDetails",
                "Avoid sensitive details in review requests; use private-first wording.",
                Severity.WARNING,
            )
        )
    return tuple(issues)


def _recipient_for(contact: Contact, channel: Channel) -> str:
    if channel is Channel.EMAIL:
        if not contact.email:
            raise ValueError("Email channel requires contact.email")
        return contact.email
    if not contact.phone:
        raise ValueError(f"{channel.value} channel requires contact.phone")
    return normalize_israeli_phone(contact.phone)



def business_with_b_prefix(name: str) -> str:
    """Return a natural Hebrew ב + business reference when a leading ה is an article."""

    article_nouns = (
        "החנות",
        "המספרה",
        "הקליניקה",
        "המוסך",
        "הסטודיו",
        "המרפאה",
        "המשרד",
        "המסעדה",
        "המאפייה",
        "הקייטרינג",
        "המעבדה",
    )
    stripped = name.strip()
    if stripped.startswith(article_nouns):
        return "ב" + stripped[1:]
    return "ב" + stripped


def render_message(
    contact: Contact,
    business: BusinessProfile,
    platform: ReviewPlatform | str = ReviewPlatform.GOOGLE,
    channel: Channel | str = Channel.WHATSAPP,
    private_first: bool = False,
) -> Message:
    """Render a Hebrew review or private-feedback message."""

    channel = Channel(channel)
    platform = ReviewPlatform(platform)
    rating_class = classify_rating(contact.rating)
    use_private = private_first or rating_class == "detractor" or COMPLAINT_TAGS.intersection(set(contact.tags))

    if use_private:
        if not business.private_feedback_url:
            raise MissingReviewDestination("private_feedback_url is required for private-first or low-rating routes")
        review_url = business.private_feedback_url
        cta = "אפשר לשתף איך הייתה החוויה בקישור פרטי קצר?"
        helper = "זה עוזר לטפל במה שצריך בצורה מסודרת."
    else:
        review_url = build_review_url(platform, business)
        cta = "אפשר להשאיר חוות דעת קצרה כאן?"
        helper = "זה עוזר ללקוחות באזור למצוא שירות אמין."

    name = contact.first_name
    business_name = business.branch_display()

    if channel is Channel.WHATSAPP:
        body = (
            f"שלום {name}, תודה שבחרת {business_with_b_prefix(business_name)}.\n"
            f"{cta}\n"
            f"{review_url}\n"
            f"{helper}\n"
            "להסרה: השב/י הסר"
        )
        return Message(channel=channel, to=_recipient_for(contact, channel), body=body, review_url=review_url, contact_name=contact.full_name)

    if channel is Channel.SMS:
        if use_private:
            body = f"{name}, תודה שבחרת {business_with_b_prefix(business_name)}. משוב פרטי קצר: {review_url} להסרה: הסר"
        else:
            body = f"{name}, תודה שבחרת {business_with_b_prefix(business_name)}. חוות דעת קצרה תעזור ללקוחות באזור: {review_url} להסרה: הסר"
        return Message(channel=channel, to=_recipient_for(contact, channel), body=body, review_url=review_url, contact_name=contact.full_name)

    subject = "אפשר לבקש חוות דעת קצרה?"
    body = (
        f"שלום {name},\n\n"
        f"תודה על האמון {business_with_b_prefix(business_name)}.\n"
        f"{cta}\n"
        f"{review_url}\n\n"
    )
    if not use_private:
        body += (
            "אפשר גם להשיב למייל הזה עם משפט קצר לשימוש כהמלצה באתר.\n"
            "לא תפורסם המלצה עם שם מלא בלי אישור מפורש.\n\n"
        )
    body += 'להסרה מרשימת הודעות כאלה, אפשר להשיב "הסרה".'
    return Message(
        channel=channel,
        to=_recipient_for(contact, channel),
        subject=subject,
        body=body,
        review_url=review_url,
        contact_name=contact.full_name,
    )


def _jerusalem_tz() -> dt.tzinfo | None:
    if ZoneInfo is None:
        return None
    return ZoneInfo("Asia/Jerusalem")


def parse_datetime(value: str | dt.datetime | None) -> dt.datetime:
    """Parse ISO string or return current Jerusalem-local time."""

    if isinstance(value, dt.datetime):
        current = value
    elif value:
        current = dt.datetime.fromisoformat(value)
    else:
        tz = _jerusalem_tz()
        current = dt.datetime.now(tz=tz)
    if current.tzinfo is None and _jerusalem_tz() is not None:
        current = current.replace(tzinfo=_jerusalem_tz())
    return current


def is_quiet_time(moment: str | dt.datetime | None = None, holiday_dates: set[str] | None = None) -> bool:
    """Return true when the moment is outside default Israeli sending windows."""

    current = parse_datetime(moment)
    date_key = current.strftime("%d-%m-%Y")
    if holiday_dates and date_key in holiday_dates:
        return True
    # Python weekday: Monday=0, Sunday=6. Israel work week starts Sunday.
    weekday = current.weekday()
    hour_min = current.hour + current.minute / 60
    if weekday == 4 and hour_min >= 13:  # Friday
        return True
    if weekday == 5:  # Saturday
        return True
    if hour_min < 8.5 or hour_min > 20.5:
        return True
    return False


def next_safe_send_time(moment: str | dt.datetime | None = None) -> dt.datetime:
    """Return the next default safe send time in Israel."""

    current = parse_datetime(moment)
    candidate = current
    if candidate.hour + candidate.minute / 60 > 20.5:
        candidate = (candidate + dt.timedelta(days=1)).replace(hour=9, minute=30, second=0, microsecond=0)
    elif candidate.hour + candidate.minute / 60 < 8.5:
        candidate = candidate.replace(hour=9, minute=30, second=0, microsecond=0)

    while True:
        weekday = candidate.weekday()
        hour_min = candidate.hour + candidate.minute / 60
        if weekday == 4 and hour_min >= 13:
            candidate = (candidate + dt.timedelta(days=2)).replace(hour=9, minute=30, second=0, microsecond=0)
            continue
        if weekday == 5:
            candidate = (candidate + dt.timedelta(days=1)).replace(hour=9, minute=30, second=0, microsecond=0)
            continue
        if hour_min < 8.5:
            candidate = candidate.replace(hour=9, minute=30, second=0, microsecond=0)
            continue
        if hour_min > 20.5:
            candidate = (candidate + dt.timedelta(days=1)).replace(hour=9, minute=30, second=0, microsecond=0)
            continue
        return candidate


def read_contacts_csv(path: str | Path) -> list[Contact]:
    """Read contacts from UTF-8 CSV.

    Supported columns: full_name, phone, email, consent, consent_basis,
    preferred_channel, last_interaction_date, tags, rating.
    """

    contacts: list[Contact] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            tags = tuple(
                tag.strip()
                for tag in (row.get("tags") or "").replace(";", ",").split(",")
                if tag.strip()
            )
            preferred_raw = (row.get("preferred_channel") or "").strip().lower()
            basis_raw = (row.get("consent_basis") or ConsentBasis.TRANSACTION_FOLLOWUP.value).strip()
            rating_raw = (row.get("rating") or "").strip()
            contacts.append(
                Contact(
                    full_name=(row.get("full_name") or row.get("name") or "").strip(),
                    phone=(row.get("phone") or "").strip() or None,
                    email=(row.get("email") or "").strip() or None,
                    consent=(row.get("consent") or "true").strip().lower() not in {"false", "0", "no", "לא"},
                    consent_basis=ConsentBasis(basis_raw) if basis_raw in ConsentBasis._value2member_map_ else ConsentBasis.MANUAL_REVIEW,
                    preferred_channel=Channel(preferred_raw) if preferred_raw in Channel._value2member_map_ else None,
                    last_interaction_date=(row.get("last_interaction_date") or "").strip() or None,
                    tags=tags,
                    rating=int(rating_raw) if rating_raw.isdigit() else None,
                    metadata=dict(row),
                )
            )
    return contacts


def plan_campaign(
    contacts: Sequence[Contact],
    business: BusinessProfile,
    platform: ReviewPlatform | str = ReviewPlatform.GOOGLE,
    channel: Channel | str | None = None,
    private_first: bool = False,
    send_after: str | dt.datetime | None = None,
    suppression_keys: set[str] | None = None,
) -> list[DeliveryPlanItem]:
    """Plan a feedback campaign without sending."""

    items: list[DeliveryPlanItem] = []
    suppression_keys = suppression_keys or set()
    safe_time = next_safe_send_time(send_after).isoformat() if send_after else None

    for contact in contacts:
        selected = choose_channel(contact, Channel(channel) if channel else None)
        if selected is None:
            items.append(
                DeliveryPlanItem(
                    contact=contact,
                    message=None,
                    status=DeliveryStatus.SKIPPED,
                    issues=(ComplianceIssue("NoReachableChannel", "No reachable channel for contact.", Severity.ERROR),),
                    send_after=safe_time,
                )
            )
            continue

        normalized_or_email = contact.email or ""
        if selected in {Channel.WHATSAPP, Channel.SMS} and contact.phone:
            try:
                normalized_or_email = normalize_israeli_phone(contact.phone)
            except InvalidPhoneNumber:
                normalized_or_email = contact.phone

        if normalized_or_email in suppression_keys or contact.email in suppression_keys or contact.phone in suppression_keys:
            items.append(
                DeliveryPlanItem(
                    contact=contact,
                    message=None,
                    status=DeliveryStatus.SKIPPED,
                    issues=(ComplianceIssue("Suppressed", "Contact appears in suppression list.", Severity.ERROR),),
                    send_after=safe_time,
                )
            )
            continue

        issues = list(validate_contact_for_channel(contact, selected))
        if any(issue.severity is Severity.ERROR for issue in issues):
            items.append(
                DeliveryPlanItem(
                    contact=contact,
                    message=None,
                    status=DeliveryStatus.SKIPPED,
                    issues=tuple(issues),
                    send_after=safe_time,
                )
            )
            continue

        try:
            message = render_message(contact, business, platform=platform, channel=selected, private_first=private_first)
            issues.extend(validate_message(message))
            status = DeliveryStatus.PLANNED
        except FeedbackCollectorError as exc:
            message = None
            issues.append(ComplianceIssue(exc.__class__.__name__, str(exc), Severity.ERROR))
            status = DeliveryStatus.SKIPPED

        items.append(
            DeliveryPlanItem(
                contact=contact,
                message=message,
                status=status,
                issues=tuple(issues),
                send_after=safe_time,
            )
        )
    return items


def to_jsonable(value: Any) -> Any:
    """Convert dataclasses and enums to JSON-safe values."""

    if dataclasses.is_dataclass(value):
        return {k: to_jsonable(v) for k, v in dataclasses.asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [to_jsonable(v) for v in value]
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    return value


def export_plan_json(plan: Sequence[DeliveryPlanItem], path: str | Path | None = None) -> str:
    """Serialize a plan as UTF-8 JSON."""

    text = json.dumps([to_jsonable(item) for item in plan], ensure_ascii=False, indent=2)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    return text


def _payload_for_message(message: Message) -> Mapping[str, Any]:
    return {
        "channel": message.channel.value,
        "to": message.to,
        "subject": message.subject,
        "body": message.body,
        "review_url": message.review_url,
        "contact_name": message.contact_name,
    }


def default_sync_transport(channel: Channel, payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """Default transport placeholder.

    Configure a real provider adapter in production. Keeping the default as a
    clear failure prevents accidental live sends.
    """

    raise RuntimeError(f"No sync transport configured for {channel.value}")


async def default_async_transport(channel: Channel, payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """Default async transport placeholder."""

    raise RuntimeError(f"No async transport configured for {channel.value}")


class FeedbackCollectorClient:
    """Campaign planner and optional sender."""

    def __init__(
        self,
        business: BusinessProfile,
        platform: ReviewPlatform | str = ReviewPlatform.GOOGLE,
        sync_transport: SyncTransport | None = None,
        async_transport: AsyncTransport | None = None,
    ) -> None:
        self.business = business
        self.platform = ReviewPlatform(platform)
        self.sync_transport = sync_transport or default_sync_transport
        self.async_transport = async_transport or default_async_transport

    def plan(
        self,
        contacts: Sequence[Contact],
        channel: Channel | str | None = None,
        private_first: bool = False,
        send_after: str | dt.datetime | None = None,
        suppression_keys: set[str] | None = None,
    ) -> list[DeliveryPlanItem]:
        return plan_campaign(
            contacts,
            self.business,
            platform=self.platform,
            channel=channel,
            private_first=private_first,
            send_after=send_after,
            suppression_keys=suppression_keys,
        )

    def send_sync(self, messages: Sequence[Message], dry_run: bool = True) -> list[SendResult]:
        results: list[SendResult] = []
        for message in messages:
            payload = _payload_for_message(message)
            if dry_run:
                results.append(
                    SendResult(
                        status=DeliveryStatus.DRY_RUN,
                        message_id=f"dry_{message.channel.value}_{abs(hash(message.to))}",
                        provider_response={"payload": payload},
                    )
                )
                continue
            try:
                response = self.sync_transport(message.channel, payload)
                status = DeliveryStatus.QUEUED if response.get("status", "queued") in {"queued", "sent", "accepted"} else DeliveryStatus.FAILED
                results.append(
                    SendResult(
                        status=status,
                        message_id=str(response.get("message_id") or response.get("id") or ""),
                        provider_response=response,
                        retryable=bool(response.get("retryable", False)),
                    )
                )
            except Exception as exc:  # provider adapter may raise
                results.append(SendResult(status=DeliveryStatus.FAILED, error=str(exc), retryable=True))
        return results

    async def send_async(self, messages: Sequence[Message], dry_run: bool = True) -> list[SendResult]:
        if dry_run:
            return self.send_sync(messages, dry_run=True)

        async def send_one(message: Message) -> SendResult:
            payload = _payload_for_message(message)
            try:
                response = await self.async_transport(message.channel, payload)
                status = DeliveryStatus.QUEUED if response.get("status", "queued") in {"queued", "sent", "accepted"} else DeliveryStatus.FAILED
                return SendResult(
                    status=status,
                    message_id=str(response.get("message_id") or response.get("id") or ""),
                    provider_response=response,
                    retryable=bool(response.get("retryable", False)),
                )
            except Exception as exc:
                return SendResult(status=DeliveryStatus.FAILED, error=str(exc), retryable=True)

        return list(await asyncio.gather(*(send_one(message) for message in messages)))


def planned_messages(plan: Sequence[DeliveryPlanItem]) -> list[Message]:
    """Return messages from planned items only."""

    return [item.message for item in plan if item.status is DeliveryStatus.PLANNED and item.message is not None]


def summarize_plan(plan: Sequence[DeliveryPlanItem]) -> Mapping[str, Any]:
    """Return lightweight plan counts."""

    counts: dict[str, int] = {}
    issue_counts: dict[str, int] = {}
    for item in plan:
        counts[item.status.value] = counts.get(item.status.value, 0) + 1
        for issue in item.issues:
            issue_counts[issue.code] = issue_counts.get(issue.code, 0) + 1
    return {"total": len(plan), "statuses": counts, "issues": issue_counts}


__all__ = [
    "BusinessProfile",
    "Channel",
    "ComplianceIssue",
    "ConsentBasis",
    "Contact",
    "DeliveryPlanItem",
    "DeliveryStatus",
    "FeedbackCollectorClient",
    "InvalidPhoneNumber",
    "Message",
    "MissingReviewDestination",
    "ReviewPlatform",
    "SendResult",
    "Severity",
    "build_review_url",
    "business_with_b_prefix",
    "choose_channel",
    "classify_rating",
    "contains_hebrew",
    "detect_opt_out",
    "export_plan_json",
    "is_probable_israeli_mobile",
    "is_quiet_time",
    "next_safe_send_time",
    "normalize_israeli_phone",
    "plan_campaign",
    "planned_messages",
    "read_contacts_csv",
    "render_message",
    "summarize_plan",
    "to_jsonable",
    "validate_contact_for_channel",
    "validate_message",
]
