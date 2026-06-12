"""Typed helper for planning Israeli event and webinar promotions.

The module is network-free. It validates event inputs, creates timezone-aware
schedules, generates Hebrew-first copy, builds UTM links, stores reusable event
profiles, and returns structured campaign plans.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from zoneinfo import ZoneInfo

ISRAEL_TZ = "Asia/Jerusalem"
STANDARD_VAT_RATE = 0.18
STANDARD_VAT_RATE_EFFECTIVE_DATE = "2025-01-01"
EXEMPT_DEALER_2026_TURNOVER_CEILING_NIS = 122_833
SUPPORTED_FORMATS = {
    "webinar",
    "workshop",
    "meetup",
    "course_preview",
    "launch",
    "clinic",
    "live_stream",
    "hybrid",
}
HEBREW_WEEKDAYS = {
    0: "יום שני",
    1: "יום שלישי",
    2: "יום רביעי",
    3: "יום חמישי",
    4: "יום שישי",
    5: "שבת",
    6: "יום ראשון",
}
DIRECT_CHANNELS = {"email", "sms", "whatsapp"}


class EventValidationError(ValueError):
    """Raised when event input cannot produce a safe, valid plan."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(slots=True)
class Reminder:
    """A planned campaign reminder."""

    label: str
    send_at: datetime
    channel: str
    purpose: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "send_at": self.send_at.isoformat(),
            "channel": self.channel,
            "purpose": self.purpose,
        }


@dataclass(slots=True)
class EventProfile:
    """Structured event intake profile."""

    event_name: str
    format: str
    audience: str
    date: str
    time: str
    duration_minutes: int
    price_nis: float = 0
    city: str | None = None
    capacity: int | None = None
    goal: Literal["registrations", "qualified_leads", "sales", "community", "education"] = "registrations"
    language: Literal["he", "en", "bilingual"] = "he"
    consent_status: Literal["opt_in", "unknown", "partner_owned", "transactional_only"] = "unknown"
    registration_url: str | None = None
    cancellation_terms: str | None = None
    accessibility_contact: str | None = None
    privacy_note: str | None = None
    vat_included: bool | None = None
    host_name: str | None = None
    recording_available: bool | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "EventProfile":
        normalized = dict(data)
        if "type" in normalized and "format" not in normalized:
            normalized["format"] = normalized.pop("type")
        return cls(
            event_name=str(normalized.get("event_name", "")).strip(),
            format=str(normalized.get("format", "webinar")).strip().lower(),
            audience=str(normalized.get("audience", "")).strip(),
            date=str(normalized.get("date", "")).strip(),
            time=str(normalized.get("time", "")).strip(),
            duration_minutes=int(normalized.get("duration_minutes", 60)),
            price_nis=float(normalized.get("price_nis", 0) or 0),
            city=(str(normalized["city"]).strip() if normalized.get("city") else None),
            capacity=(int(normalized["capacity"]) if normalized.get("capacity") not in (None, "") else None),
            goal=str(normalized.get("goal", "registrations")).strip().lower(),  # type: ignore[arg-type]
            language=str(normalized.get("language", "he")).strip().lower(),  # type: ignore[arg-type]
            consent_status=str(normalized.get("consent_status", "unknown")).strip().lower(),  # type: ignore[arg-type]
            registration_url=(str(normalized["registration_url"]).strip() if normalized.get("registration_url") else None),
            cancellation_terms=(str(normalized["cancellation_terms"]).strip() if normalized.get("cancellation_terms") else None),
            accessibility_contact=(str(normalized["accessibility_contact"]).strip() if normalized.get("accessibility_contact") else None),
            privacy_note=(str(normalized["privacy_note"]).strip() if normalized.get("privacy_note") else None),
            vat_included=normalized.get("vat_included"),
            host_name=(str(normalized["host_name"]).strip() if normalized.get("host_name") else None),
            recording_available=normalized.get("recording_available"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CampaignPlan:
    """Complete structured promotion plan."""

    event: EventProfile
    timezone: str
    starts_at: datetime
    ends_at: datetime
    runway_days: int
    recommended_channels: list[str]
    reminders: list[Reminder]
    compliance_flags: list[str]
    warnings: list[str]
    copy: dict[str, Any]
    utm_links: dict[str, str]
    checklist: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event.to_dict(),
            "timezone": self.timezone,
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat(),
            "runway_days": self.runway_days,
            "recommended_channels": self.recommended_channels,
            "reminders": [reminder.to_dict() for reminder in self.reminders],
            "compliance_flags": self.compliance_flags,
            "warnings": self.warnings,
            "copy": self.copy,
            "utm_links": self.utm_links,
            "checklist": self.checklist,
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


@dataclass(slots=True)
class StoredEventResponse:
    """Response returned after storing an event profile."""

    event_id: str
    event_path: str
    timezone: str
    next_step: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


def parse_ddmmyyyy(value: str) -> date:
    """Parse `DD-MM-YYYY` dates accepted by the machine interface."""

    if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", value or ""):
        raise EventValidationError("INVALID_DATE_FORMAT", "Use DD-MM-YYYY, for example 24-06-2026.")
    day, month, year = (int(part) for part in value.split("-"))
    try:
        return date(year, month, day)
    except ValueError as exc:
        raise EventValidationError("INVALID_DATE", str(exc)) from exc


def display_date_slashes(value: str | datetime) -> str:
    """Format a user-facing date as `DD/MM/YYYY`."""

    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    parsed = parse_ddmmyyyy(value)
    return parsed.strftime("%d/%m/%Y")


def parse_hhmm(value: str) -> time:
    """Parse `HH:MM` times in 24-hour format."""

    if not re.fullmatch(r"\d{2}:\d{2}", value or ""):
        raise EventValidationError("INVALID_TIME_FORMAT", "Use HH:MM, for example 20:00.")
    hour, minute = (int(part) for part in value.split(":"))
    try:
        return time(hour, minute)
    except ValueError as exc:
        raise EventValidationError("INVALID_TIME", str(exc)) from exc


def validate_event(profile: EventProfile) -> list[str]:
    """Validate input and return non-fatal warnings."""

    if not profile.event_name:
        raise EventValidationError("MISSING_EVENT_NAME", "Add a clear event name.")
    if not profile.audience:
        raise EventValidationError("MISSING_AUDIENCE", "Define one primary audience.")
    if profile.format not in SUPPORTED_FORMATS:
        raise EventValidationError("UNSUPPORTED_FORMAT", f"Use one of: {', '.join(sorted(SUPPORTED_FORMATS))}.")
    if profile.duration_minutes < 15 or profile.duration_minutes > 480:
        raise EventValidationError("INVALID_DURATION", "Use a duration between 15 and 480 minutes.")
    if profile.price_nis < 0:
        raise EventValidationError("INVALID_PRICE", "Price cannot be negative.")
    if profile.capacity is not None and profile.capacity <= 0:
        raise EventValidationError("INVALID_CAPACITY", "Capacity must be positive.")
    if profile.language not in {"he", "en", "bilingual"}:
        raise EventValidationError("UNSUPPORTED_LANGUAGE", "Use he, en, or bilingual.")
    if profile.consent_status not in {"opt_in", "unknown", "partner_owned", "transactional_only"}:
        raise EventValidationError("UNSUPPORTED_CONSENT_STATUS", "Use opt_in, unknown, partner_owned, or transactional_only.")

    start_date = parse_ddmmyyyy(profile.date)
    start_time = parse_hhmm(profile.time)
    warnings: list[str] = []

    if start_date.weekday() == 5:
        warnings.append("SATURDAY_EVENT: Saturday can underperform for general Israeli business audiences.")
    if start_date.weekday() == 4 and start_time >= time(13, 0):
        warnings.append("FRIDAY_AFTERNOON: Friday afternoon usually has lower response and attendance.")
    if profile.format in {"workshop", "meetup", "clinic", "hybrid"} and not profile.city:
        warnings.append("MISSING_CITY: Add city or venue details for local/offline events.")
    if profile.registration_url is None:
        warnings.append("MISSING_REGISTRATION_URL: Use a placeholder until the registration page is ready.")
    if profile.recording_available is None and profile.format in {"webinar", "live_stream", "hybrid"}:
        warnings.append("RECORDING_UNCLEAR: Do not promise replay until recording availability is confirmed.")
    return warnings


def starts_and_ends(profile: EventProfile) -> tuple[datetime, datetime]:
    """Return timezone-aware start and end datetimes."""

    local_date = parse_ddmmyyyy(profile.date)
    local_time = parse_hhmm(profile.time)
    tz = ZoneInfo(ISRAEL_TZ)
    starts_at = datetime.combine(local_date, local_time, tzinfo=tz)
    ends_at = starts_at + timedelta(minutes=profile.duration_minutes)
    return starts_at, ends_at


def recommended_runway_days(profile: EventProfile) -> int:
    """Return recommended minimum promotional runway."""

    if profile.format in {"workshop", "meetup", "clinic", "hybrid"}:
        return 30 if profile.price_nis > 0 else 21
    if profile.format == "course_preview":
        return 30
    if profile.price_nis > 0:
        return 21
    if profile.goal == "qualified_leads":
        return 14
    return 14


def recommended_channels(profile: EventProfile) -> list[str]:
    """Return a practical Israeli channel mix."""

    channels: list[str] = []
    if profile.consent_status == "opt_in":
        channels.extend(["email", "whatsapp"])
    elif profile.consent_status == "partner_owned":
        channels.append("partner_newsletter")
    else:
        channels.extend(["organic_social", "partner_posts"])

    if profile.format in {"workshop", "meetup", "clinic", "hybrid"} or profile.city:
        channels.extend(["google_business_profile", "local_facebook_groups", "instagram"])
    if profile.goal in {"qualified_leads", "sales"}:
        channels.extend(["linkedin", "retargeting"])
    if profile.format in {"webinar", "live_stream", "course_preview"}:
        channels.extend(["facebook", "linkedin", "email_reminder"])

    deduped: list[str] = []
    for channel in channels:
        if channel not in deduped:
            deduped.append(channel)
    return deduped


def generate_reminders(profile: EventProfile, starts_at: datetime) -> list[Reminder]:
    """Generate timezone-aware reminder schedule."""

    launch_hour = 10 if starts_at.hour < 17 else 20
    launch_at = (starts_at - timedelta(days=recommended_runway_days(profile))).replace(
        hour=launch_hour, minute=0, second=0, microsecond=0
    )
    reminders = [
        Reminder("launch", launch_at, "social", "Open registration with clear value and CTA."),
        Reminder("72h", starts_at - timedelta(hours=72), "email", "Reframe problem and repeat logistics."),
        Reminder("24h", starts_at - timedelta(hours=24), "email", "Send calendar/link/logistics and live-attendance reason."),
        Reminder("morning_of", starts_at.replace(hour=8, minute=30, second=0, microsecond=0), "email", "Send same-day link and preparation notes."),
    ]
    if profile.consent_status == "opt_in":
        reminders.append(
            Reminder("2h", starts_at - timedelta(hours=2), "whatsapp", "Short opt-in reminder with entry link and unsubscribe route.")
        )
    reminders.extend(
        [
            Reminder("post_event_1h", starts_at + timedelta(hours=1), "email", "Thank participants and send materials when available."),
            Reminder("post_event_24h", starts_at + timedelta(hours=24), "email", "Send replay/summary and one next step."),
        ]
    )
    return sorted(reminders, key=lambda item: item.send_at)


def compliance_flags(profile: EventProfile) -> list[str]:
    """Return operational compliance flags."""

    flags: list[str] = []
    if profile.consent_status != "opt_in":
        flags.append("Avoid promotional email/SMS/WhatsApp blasts unless documented consent or a valid basis exists.")
    if profile.consent_status == "opt_in":
        flags.append("Include advertiser identity and a simple unsubscribe method in direct promotional messages.")
    if profile.price_nis > 0:
        if not profile.cancellation_terms:
            flags.append("Add cancellation/refund terms before publishing a paid consumer-facing event.")
        if profile.vat_included is None:
            flags.append("State whether the ₪ price includes VAT where relevant.")
    if not profile.privacy_note:
        flags.append("Add a short privacy note explaining registration data use.")
    if not profile.accessibility_contact:
        flags.append("Add an accessibility or logistics contact line.")
    if profile.capacity is None:
        flags.append("Do not use scarcity claims such as 'last seats' unless real capacity is known.")
    if profile.recording_available is not True and profile.format in {"webinar", "live_stream", "hybrid"}:
        flags.append("Do not promise a replay unless recording is confirmed.")
    return flags


def hebrew_weekday(dt: datetime) -> str:
    """Return Hebrew weekday name for a datetime."""

    return HEBREW_WEEKDAYS[dt.weekday()]


def price_text(profile: EventProfile) -> str:
    """Format event price in Hebrew."""

    if profile.price_nis <= 0:
        return "ללא עלות"
    amount: int | float = int(profile.price_nis) if profile.price_nis == int(profile.price_nis) else profile.price_nis
    vat = ""
    if profile.vat_included is True:
        vat = " כולל מע״מ"
    elif profile.vat_included is False:
        vat = " לפני מע״מ"
    return f"₪{amount}{vat}"


def location_text(profile: EventProfile) -> str:
    """Return human-readable location text."""

    if profile.format in {"webinar", "live_stream", "course_preview"} and not profile.city:
        return "אונליין"
    if profile.city:
        return profile.city
    return "מיקום יימסר לנרשמים"


def generate_copy(profile: EventProfile, starts_at: datetime) -> dict[str, Any]:
    """Generate Hebrew-first copy set."""

    date_display = display_date_slashes(starts_at)
    time_display = starts_at.strftime("%H:%M")
    weekday = hebrew_weekday(starts_at)
    host = profile.host_name or "המנחה"
    location = location_text(profile)
    registration = profile.registration_url or "[קישור הרשמה]"
    price = price_text(profile)
    capacity_line = f"מספר המקומות מוגבל ל-{profile.capacity} משתתפים ומשתתפות." if profile.capacity else ""
    recording_line = (
        "הקלטה תישלח לנרשמים לאחר האירוע."
        if profile.recording_available is True
        else "פרטי הקלטה יימסרו רק אם תהיה הקלטה זמינה."
    )

    landing = (
        f"{profile.event_name}\n"
        f"{weekday}, {date_display}, בשעה {time_display} | {location} | {price}\n\n"
        f"מפגש מעשי עבור {profile.audience}. ב-{profile.duration_minutes} דקות נעבור על צעדים ברורים, "
        f"דוגמאות וכלים שאפשר ליישם מיד אחרי האירוע.\n\n"
        f"למי זה מתאים: {profile.audience} שרוצים להתקדם בצורה מסודרת בלי עודף תאוריה.\n"
        f"מה מקבלים: סדר פעולה, נקודות לבדיקה ושאלות שכדאי לשאול לפני שמיישמים.\n"
        f"{capacity_line}\n"
        f"{recording_line}\n\n"
        f"הרשמה: {registration}"
    ).strip()

    social = (
        f"{profile.audience}: אם הנושא של “{profile.event_name}” רלוונטי לכם, "
        f"ביום {date_display} בשעה {time_display} יתקיים מפגש מעשי ב{location}.\n\n"
        f"מה יהיה במפגש:\n"
        f"• פירוק הבעיה לצעדים פשוטים\n"
        f"• דוגמאות מהשטח\n"
        f"• זמן לשאלות וליישום\n\n"
        f"מחיר: {price}. הרשמה מראש: {registration}"
    )

    whatsapp = (
        f"היי, תזכורת קצרה: {profile.event_name} מתקיים היום בשעה {time_display}.\n"
        f"קישור/פרטים: {registration}\n"
        f"מומלץ להתחבר 5 דקות לפני.\n"
        f"להסרה מעדכונים: [קישור הסרה/איש קשר]"
    )

    email_subjects = [
        f"{profile.event_name} — ההרשמה נפתחה",
        f"מחר ב-{time_display}: {profile.event_name}",
        f"היום: קישור ופרטים חשובים ל-{profile.event_name}",
        f"תודה שהצטרפת ל-{profile.event_name}",
    ]

    follow_up = (
        f"תודה שהצטרפת ל-{profile.event_name}.\n\n"
        f"כאן אפשר לקבל את החומרים או הצעד הבא: [קישור]\n"
        f"אם עלו שאלות בעקבות המפגש, אפשר להשיב למייל הזה או לקבוע שיחת התאמה: [קישור]."
    )

    return {
        "landing_page": landing,
        "social_post": social,
        "whatsapp_reminder_opt_in_only": whatsapp,
        "email_subjects": email_subjects,
        "follow_up_email": follow_up,
        "notes": [
            "Use WhatsApp/SMS/email promotion only with proper consent.",
            "Keep price, time, capacity, and recording statements factual.",
            f"Host field used: {host}.",
        ],
    }


def safe_utm_value(value: str) -> str:
    """Normalize UTM values for predictable analytics."""

    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9_-]+", "_", lowered)
    lowered = re.sub(r"_+", "_", lowered).strip("_")
    return lowered or "event"


def build_utm_url(base_url: str, *, source: str, medium: str, campaign: str, content: str | None = None) -> str:
    """Build a UTM-tagged URL."""

    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise EventValidationError("INVALID_URL", "Use an absolute http(s) URL.")
    params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    params["utm_source"] = safe_utm_value(source)
    params["utm_medium"] = safe_utm_value(medium)
    params["utm_campaign"] = safe_utm_value(campaign)
    if content:
        params["utm_content"] = safe_utm_value(content)
    query = urlencode(params)
    return urlunparse(parsed._replace(query=query))


def generate_utm_links(profile: EventProfile, channels: Sequence[str]) -> dict[str, str]:
    """Generate UTM links for a registration URL if supplied."""

    if not profile.registration_url:
        return {}
    campaign = f"{profile.format}_{profile.date}_{safe_utm_value(profile.event_name)}"
    medium_map = {
        "email": "email",
        "email_reminder": "email",
        "whatsapp": "messaging",
        "sms": "messaging",
        "linkedin": "social",
        "facebook": "social",
        "instagram": "social",
        "organic_social": "social",
        "partner_posts": "partner",
        "partner_newsletter": "partner",
        "google_business_profile": "local",
        "local_facebook_groups": "local_social",
        "retargeting": "paid",
    }
    return {
        channel: build_utm_url(
            profile.registration_url,
            source=channel,
            medium=medium_map.get(channel, "campaign"),
            campaign=campaign,
            content="event_promo",
        )
        for channel in channels
    }


def production_checklist(profile: EventProfile) -> list[str]:
    """Return a launch checklist."""

    checklist = [
        "Confirm event title, audience, date, time, timezone, duration, price, and CTA.",
        "Review Hebrew copy for natural Israeli phrasing.",
        "Confirm registration URL and test the form.",
        "Add privacy note to registration page.",
        "Add accessibility/logistics contact.",
        "Generate UTM links for each channel.",
        "Schedule reminders in Asia/Jerusalem.",
        "Prepare follow-up email before launch.",
        "Archive final copy, landing page, consent source, and terms.",
    ]
    if profile.price_nis > 0:
        checklist.extend(
            [
                "Confirm whether price includes VAT.",
                "Add cancellation/refund terms.",
                "Prepare receipt/invoice workflow.",
            ]
        )
    if profile.format in {"workshop", "meetup", "clinic", "hybrid"}:
        checklist.extend(
            [
                "Confirm venue address, map link, parking, arrival instructions, and accessibility.",
                "Send preparation instructions to registrants.",
            ]
        )
    if profile.consent_status != "opt_in":
        checklist.append("Avoid direct promotional blasts until consent status is resolved.")
    return checklist


def stable_event_id(profile: EventProfile) -> str:
    """Create a deterministic short event identifier."""

    digest = hashlib.sha256(json.dumps(profile.to_dict(), ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return f"evt_{digest[:12]}"


def load_event(path: str | Path) -> dict[str, Any]:
    """Load event JSON from a path."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_plan(plan: CampaignPlan, path: str | Path) -> None:
    """Write a campaign plan to JSON."""

    Path(path).write_text(plan.to_json(indent=2) + "\n", encoding="utf-8")


def sample_event() -> dict[str, Any]:
    """Return a runnable sample event."""

    return {
        "event_name": "איך לתמחר שירותים בלי להפסיד לקוחות",
        "format": "webinar",
        "audience": "פרילנסרים בתחילת הדרך",
        "date": "24-06-2026",
        "time": "20:00",
        "duration_minutes": 60,
        "price_nis": 0,
        "goal": "qualified_leads",
        "language": "he",
        "consent_status": "opt_in",
        "registration_url": "https://example.co.il/register",
        "privacy_note": "הפרטים ישמשו להרשמה ותזכורות לאירוע.",
        "accessibility_contact": "access@example.co.il",
        "recording_available": True,
    }


class EventWebinarPromoterClient:
    """Synchronous and asynchronous planner."""

    def __init__(self, timezone: str = ISRAEL_TZ) -> None:
        if timezone != ISRAEL_TZ:
            ZoneInfo(timezone)
        self.timezone = timezone

    def validate(self, data: Mapping[str, Any] | EventProfile) -> list[str]:
        profile = data if isinstance(data, EventProfile) else EventProfile.from_mapping(data)
        return validate_event(profile)

    def plan(self, data: Mapping[str, Any] | EventProfile) -> CampaignPlan:
        profile = data if isinstance(data, EventProfile) else EventProfile.from_mapping(data)
        warnings = validate_event(profile)
        starts_at, ends_at = starts_and_ends(profile)
        channels = recommended_channels(profile)
        reminders = generate_reminders(profile, starts_at)
        flags = compliance_flags(profile)
        copy = generate_copy(profile, starts_at)
        utm_links = generate_utm_links(profile, channels)
        checklist = production_checklist(profile)
        return CampaignPlan(
            event=profile,
            timezone=self.timezone,
            starts_at=starts_at,
            ends_at=ends_at,
            runway_days=recommended_runway_days(profile),
            recommended_channels=channels,
            reminders=reminders,
            compliance_flags=flags,
            warnings=warnings,
            copy=copy,
            utm_links=utm_links,
            checklist=checklist,
        )

    def copy(self, data: Mapping[str, Any] | EventProfile) -> dict[str, Any]:
        profile = data if isinstance(data, EventProfile) else EventProfile.from_mapping(data)
        validate_event(profile)
        starts_at, _ = starts_and_ends(profile)
        return generate_copy(profile, starts_at)

    def checklist(self, data: Mapping[str, Any] | EventProfile) -> list[str]:
        profile = data if isinstance(data, EventProfile) else EventProfile.from_mapping(data)
        validate_event(profile)
        return production_checklist(profile)

    def create(self, data: Mapping[str, Any] | EventProfile, *, store_dir: str | Path = ".event-webinar-promoter") -> StoredEventResponse:
        profile = data if isinstance(data, EventProfile) else EventProfile.from_mapping(data)
        validate_event(profile)
        event_id = stable_event_id(profile)
        directory = Path(store_dir)
        directory.mkdir(parents=True, exist_ok=True)
        event_path = directory / f"{event_id}.json"
        event_path.write_text(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return StoredEventResponse(
            event_id=event_id,
            event_path=str(event_path),
            timezone=self.timezone,
            next_step=f"Run plan with event_id {event_id}.",
        )

    def load_created(self, event_id: str, *, store_dir: str | Path = ".event-webinar-promoter") -> dict[str, Any]:
        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "", event_id)
        if safe_id != event_id or not event_id.startswith("evt_"):
            raise EventValidationError("INVALID_EVENT_ID", "Use an event_id returned by create.")
        path = Path(store_dir) / f"{event_id}.json"
        if not path.exists():
            raise EventValidationError("EVENT_NOT_FOUND", f"No stored event found for {event_id}.")
        return load_event(path)

    async def avalidate(self, data: Mapping[str, Any] | EventProfile) -> list[str]:
        return await asyncio.to_thread(self.validate, data)

    async def aplan(self, data: Mapping[str, Any] | EventProfile) -> CampaignPlan:
        return await asyncio.to_thread(self.plan, data)

    async def acopy(self, data: Mapping[str, Any] | EventProfile) -> dict[str, Any]:
        return await asyncio.to_thread(self.copy, data)

    async def acreate(self, data: Mapping[str, Any] | EventProfile, *, store_dir: str | Path = ".event-webinar-promoter") -> StoredEventResponse:
        return await asyncio.to_thread(self.create, data, store_dir=store_dir)


def main() -> int:
    """Minimal direct execution entrypoint."""

    client = EventWebinarPromoterClient()
    plan = client.plan(sample_event())
    print(plan.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
