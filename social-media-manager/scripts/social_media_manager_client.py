#!/usr/bin/env python3
"""Typed social-media scheduling helper for Israeli organic content.

The module plans and validates posts for Facebook, Instagram, TikTok and
LinkedIn. It does not publish to external platforms. Use exported JSON/CSV in
approved publishing workflows.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import io
import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any, Iterable, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ISRAEL_TZ = "Asia/Jerusalem"
RTL_CHARS_RE = re.compile(r"[\u0590-\u05FF]")
HASHTAG_ALLOWED_RE = re.compile(r"[^\w\u0590-\u05FF]", flags=re.UNICODE)
PRICE_RE = re.compile(r"(₪\s?\d+|\d+\s?₪|\b\d+\s?(?:שח|ש\"ח)\b)")
REGULATED_CLAIM_RE = re.compile(
    r"(מרפא|מעלים|מבטיח|תשואה|רווח מובטח|ייעוץ משפטי|חיסכון מס מובטח|כאבי|אבחון רפואי)"
)
GIVEAWAY_RE = re.compile(r"(הגרלה|זכו|מתנה|חינם|פרס)")
SUBTITLE_FORMATS = {"reel", "video", "story_video", "short_video"}


class Platform(str, Enum):
    """Supported organic social platforms."""

    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"


class Severity(str, Enum):
    """Validation issue severity."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class PlatformRule:
    """Platform content constraints and scheduling preferences."""

    max_caption_chars: int
    max_hashtags: int
    media_required_formats: tuple[str, ...]
    suggested_days: tuple[int, ...]  # Monday=0, Sunday=6 in Python weekday terms.
    suggested_times: tuple[str, ...]
    frequency_label: str


@dataclass(frozen=True)
class BusinessProfile:
    """Business context used to tailor schedules."""

    name: str = "עסק מקומי"
    business_type: str = "local_service"
    city: str = "ישראל"
    audience: str = "דוברי עברית בישראל"
    shabbat_policy: str = "avoid"
    timezone: str = ISRAEL_TZ


@dataclass(frozen=True)
class BlackoutPeriod:
    """Date-level publishing blackout."""

    date_iso: str
    reason: str = "sensitive_date"
    commercial_only: bool = True


@dataclass(frozen=True)
class PostDraft:
    """Draft post before scheduling."""

    platform: str | Platform
    caption: str
    format: str = "text"
    title: str = ""
    hashtags: tuple[str, ...] = ()
    cta: str = ""
    media_count: int = 0
    contains_customer_image: bool = False
    contains_price: bool = False
    offer_terms: str = ""
    contains_personal_data: bool = False
    is_commercial: bool = True
    pillar: str = "education"

    def normalized_platform(self) -> Platform:
        return parse_platform(self.platform)


@dataclass(frozen=True)
class ValidationIssue:
    """Validation issue returned for a draft."""

    code: str
    severity: Severity
    message: str
    field: str = "caption"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "field": self.field,
        }


@dataclass(frozen=True)
class TimeSlot:
    """Recommended publishing time."""

    platform: Platform
    scheduled_at: datetime
    timezone: str = ISRAEL_TZ
    reason: str = "recommended_window"

    def to_dict(self) -> dict[str, str]:
        return {
            "platform": self.platform.value,
            "scheduled_at": self.scheduled_at.isoformat(),
            "timezone": self.timezone,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ScheduledPost:
    """Final schedule item for export."""

    local_id: str
    platform: Platform
    scheduled_at: datetime
    caption: str
    format: str
    hashtags: tuple[str, ...] = ()
    cta: str = ""
    pillar: str = "education"
    timezone: str = ISRAEL_TZ
    approval_status: str = "pending_owner_review"
    risk_flags: tuple[str, ...] = ()
    validation_issues: tuple[ValidationIssue, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "local_id": self.local_id,
            "platform": self.platform.value,
            "scheduled_at": self.scheduled_at.isoformat(),
            "display_date_he": self.scheduled_at.strftime("%d/%m/%Y"),
            "display_time": self.scheduled_at.strftime("%H:%M"),
            "timezone": self.timezone,
            "format": self.format,
            "pillar": self.pillar,
            "caption": self.caption,
            "hashtags": list(self.hashtags),
            "cta": self.cta,
            "approval_status": self.approval_status,
            "risk_flags": list(self.risk_flags),
            "validation_issues": [issue.to_dict() for issue in self.validation_issues],
        }


PLATFORM_RULES: dict[Platform, PlatformRule] = {
    Platform.FACEBOOK: PlatformRule(
        max_caption_chars=63206,
        max_hashtags=10,
        media_required_formats=("reel", "video"),
        suggested_days=(6, 1, 2, 3),  # Sunday, Tuesday, Wednesday, Thursday
        suggested_times=("09:00", "12:30", "19:00"),
        frequency_label="3-5 posts/week",
    ),
    Platform.INSTAGRAM: PlatformRule(
        max_caption_chars=2200,
        max_hashtags=30,
        media_required_formats=("post", "reel", "story", "carousel", "video"),
        suggested_days=(6, 0, 2, 3),
        suggested_times=("08:30", "12:00", "20:00"),
        frequency_label="3-5 posts/week + stories",
    ),
    Platform.TIKTOK: PlatformRule(
        max_caption_chars=2200,
        max_hashtags=12,
        media_required_formats=("video", "short_video", "reel"),
        suggested_days=(6, 1, 3),
        suggested_times=("12:00", "17:00", "21:00"),
        frequency_label="2-5 videos/week",
    ),
    Platform.LINKEDIN: PlatformRule(
        max_caption_chars=3000,
        max_hashtags=5,
        media_required_formats=("video", "carousel"),
        suggested_days=(6, 1, 2),
        suggested_times=("08:30", "11:30", "17:00"),
        frequency_label="2-3 posts/week",
    ),
}


CITY_ALIASES = {
    "ראשלצ": "ראשון לציון",
    "ראשון": "ראשון לציון",
    "תא": "תל אביב",
    "תא יפו": "תל אביב-יפו",
    "תל אביב": "תל אביב-יפו",
    "פ\"ת": "פתח תקווה",
    "פתח תקוה": "פתח תקווה",
    "ב\"ש": "באר שבע",
}


def parse_platform(value: str | Platform) -> Platform:
    """Parse a platform value or raise ValueError with supported options."""

    if isinstance(value, Platform):
        return value
    normalized = str(value).strip().lower()
    aliases = {
        "fb": "facebook",
        "meta": "facebook",
        "ig": "instagram",
        "insta": "instagram",
        "tt": "tiktok",
        "tik_tok": "tiktok",
        "li": "linkedin",
    }
    normalized = aliases.get(normalized, normalized)
    try:
        return Platform(normalized)
    except ValueError as exc:
        supported = ", ".join(platform.value for platform in Platform)
        raise ValueError(f"UNKNOWN_PLATFORM: use one of {supported}") from exc


def get_timezone(timezone: str = ISRAEL_TZ) -> ZoneInfo:
    """Return a ZoneInfo timezone, raising a clear ValueError when invalid."""

    try:
        return ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"INVALID_TIMEZONE: use an IANA timezone such as {ISRAEL_TZ}") from exc


def contains_hebrew(text: str) -> bool:
    """Return True when text contains Hebrew letters."""

    return bool(RTL_CHARS_RE.search(text or ""))


def normalize_caption(text: str) -> str:
    """Normalize text while preserving Hebrew, emoji, punctuation and line breaks."""

    if text is None:
        return ""
    normalized = unicodedata.normalize("NFC", str(text))
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def sanitize_hashtag(tag: str) -> str:
    """Return a readable hashtag with spaces and punctuation removed."""

    if not tag:
        return ""
    cleaned = normalize_caption(tag).strip()
    cleaned = cleaned.lstrip("#")
    cleaned = cleaned.replace(" ", "")
    cleaned = cleaned.replace("_", "")
    cleaned = HASHTAG_ALLOWED_RE.sub("", cleaned)
    if not cleaned:
        return ""
    return f"#{cleaned}"


def normalize_hashtags(tags: Iterable[str]) -> tuple[str, ...]:
    """Sanitize and deduplicate hashtags while preserving order."""

    seen: set[str] = set()
    output: list[str] = []
    for tag in tags:
        cleaned = sanitize_hashtag(tag)
        key = cleaned.casefold()
        if cleaned and key not in seen:
            output.append(cleaned)
            seen.add(key)
    return tuple(output)


def normalize_city(city: str) -> dict[str, Any]:
    """Normalize common Israeli city nicknames for local hashtags."""

    raw = normalize_caption(city)
    canonical = CITY_ALIASES.get(raw, raw)
    confidence = 0.94 if canonical != raw else 0.75
    hashtag = "#" + canonical.replace(" ", "").replace("-", "")
    return {
        "input": raw,
        "normalized_city_he": canonical,
        "hashtags": [sanitize_hashtag(hashtag)],
        "confidence": confidence,
    }


def _parse_clock(value: str) -> time:
    hours, minutes = value.split(":", 1)
    return time(int(hours), int(minutes))


def is_shabbat_window(moment: datetime) -> bool:
    """Return True for a conservative Friday afternoon through Saturday evening window."""

    local = moment.astimezone(get_timezone(ISRAEL_TZ))
    weekday = local.weekday()  # Monday=0, Friday=4, Saturday=5, Sunday=6.
    if weekday == 4 and local.time() >= time(15, 0):
        return True
    if weekday == 5 and local.time() < time(20, 30):
        return True
    return False


def date_from_iso(value: str | date | datetime) -> date:
    """Parse an ISO date-like value."""

    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def deterministic_id(platform: Platform, scheduled_at: datetime, caption: str) -> str:
    """Create a deterministic local ID for duplicate detection."""

    key = f"{platform.value}|{scheduled_at.isoformat()}|{normalize_caption(caption)[:80]}"
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
    return f"local-{digest}"


class SocialMediaManagerClient:
    """Client for validating and scheduling Israeli social-media content."""

    def __init__(
        self,
        profile: BusinessProfile | None = None,
        timezone: str = ISRAEL_TZ,
        blackout_periods: Sequence[BlackoutPeriod] | None = None,
        avoid_shabbat: bool = True,
    ) -> None:
        self.profile = profile or BusinessProfile(timezone=timezone)
        self.timezone_name = timezone or self.profile.timezone
        self.tz = get_timezone(self.timezone_name)
        self.blackout_periods = tuple(blackout_periods or ())
        self.avoid_shabbat = avoid_shabbat

    def normalize_caption(self, text: str) -> str:
        return normalize_caption(text)

    def sanitize_hashtag(self, tag: str) -> str:
        return sanitize_hashtag(tag)

    def normalize_hashtags(self, tags: Iterable[str]) -> tuple[str, ...]:
        return normalize_hashtags(tags)

    def normalize_city(self, city: str) -> dict[str, Any]:
        return normalize_city(city)

    def is_blocked_date(self, day: date, is_commercial: bool = True) -> bool:
        for blackout in self.blackout_periods:
            if date_from_iso(blackout.date_iso) == day:
                if blackout.commercial_only and not is_commercial:
                    continue
                return True
        return False

    def next_safe_datetime(self, start: datetime, is_commercial: bool = True) -> datetime:
        """Move a datetime to the next non-Shabbat, non-blackout moment."""

        current = start.astimezone(self.tz)
        for _ in range(45 * 24):
            if self.avoid_shabbat and is_shabbat_window(current):
                current += timedelta(hours=1)
                continue
            if self.is_blocked_date(current.date(), is_commercial=is_commercial):
                current = datetime.combine(current.date() + timedelta(days=1), time(8, 30), tzinfo=self.tz)
                continue
            return current
        raise RuntimeError("No safe datetime found within search window")

    def recommend_slots(
        self,
        platforms: Sequence[str | Platform],
        start_date: str | date | datetime | None = None,
        days: int = 14,
        is_commercial: bool = True,
    ) -> list[TimeSlot]:
        """Return recommended slots for the requested platforms."""

        if days < 1:
            return []
        start = date_from_iso(start_date or datetime.now(self.tz).date())
        parsed_platforms = [parse_platform(platform) for platform in platforms]
        slots: list[TimeSlot] = []
        for offset in range(days):
            current_date = start + timedelta(days=offset)
            for platform in parsed_platforms:
                rule = PLATFORM_RULES[platform]
                if current_date.weekday() not in rule.suggested_days:
                    continue
                for time_text in rule.suggested_times[:1]:
                    candidate = datetime.combine(current_date, _parse_clock(time_text), tzinfo=self.tz)
                    safe_candidate = self.next_safe_datetime(candidate, is_commercial=is_commercial)
                    if safe_candidate.date() != current_date and self.is_blocked_date(current_date, is_commercial):
                        continue
                    if self.avoid_shabbat and is_shabbat_window(candidate):
                        continue
                    slots.append(TimeSlot(platform=platform, scheduled_at=safe_candidate, timezone=self.timezone_name))
        slots.sort(key=lambda slot: (slot.scheduled_at, slot.platform.value))
        return slots

    async def async_recommend_slots(
        self,
        platforms: Sequence[str | Platform],
        start_date: str | date | datetime | None = None,
        days: int = 14,
        is_commercial: bool = True,
    ) -> list[TimeSlot]:
        """Async wrapper for schedule slot generation."""

        await asyncio.sleep(0)
        return self.recommend_slots(platforms, start_date=start_date, days=days, is_commercial=is_commercial)

    def validate_post(self, draft: PostDraft) -> tuple[bool, tuple[ValidationIssue, ...], tuple[str, ...]]:
        """Validate a draft and return validity, issues and risk flags."""

        platform = draft.normalized_platform()
        rule = PLATFORM_RULES[platform]
        caption = normalize_caption(draft.caption)
        hashtags = normalize_hashtags(draft.hashtags)
        issues: list[ValidationIssue] = []
        risk_flags: list[str] = []

        if len(caption) > rule.max_caption_chars:
            issues.append(
                ValidationIssue(
                    code="CAPTION_TOO_LONG",
                    severity=Severity.ERROR,
                    field="caption",
                    message=f"Caption has {len(caption)} characters; maximum for {platform.value} is {rule.max_caption_chars}.",
                )
            )

        if len(hashtags) > rule.max_hashtags:
            issues.append(
                ValidationIssue(
                    code="HASHTAG_LIMIT_EXCEEDED",
                    severity=Severity.ERROR,
                    field="hashtags",
                    message=f"{platform.value} accepts at most {rule.max_hashtags} planned hashtags in this helper.",
                )
            )

        if draft.format in rule.media_required_formats and draft.media_count < 1:
            issues.append(
                ValidationIssue(
                    code="MEDIA_REQUIRED",
                    severity=Severity.ERROR,
                    field="media_count",
                    message=f"{platform.value} format '{draft.format}' requires at least one approved media asset.",
                )
            )

        if draft.contains_customer_image or draft.contains_personal_data:
            risk_flags.append("consent_required")

        if draft.contains_price or PRICE_RE.search(caption):
            if not normalize_caption(draft.offer_terms):
                risk_flags.append("terms_required")

        if REGULATED_CLAIM_RE.search(caption):
            risk_flags.append("professional_review_required")

        if GIVEAWAY_RE.search(caption) and "תקנון" not in caption and "תנאי" not in caption:
            risk_flags.append("giveaway_terms_required")

        if draft.format in SUBTITLE_FORMATS:
            risk_flags.append("requires_subtitles_check")

        if platform == Platform.FACEBOOK and draft.format == "group_post":
            risk_flags.append("check_group_rules")

        if platform == Platform.LINKEDIN and len([tag for tag in hashtags if tag]) > 3:
            issues.append(
                ValidationIssue(
                    code="LINKEDIN_HASHTAG_DENSITY",
                    severity=Severity.WARNING,
                    field="hashtags",
                    message="LinkedIn posts usually perform better with a small number of focused hashtags.",
                )
            )

        valid = not any(issue.severity == Severity.ERROR for issue in issues)
        return valid, tuple(issues), tuple(dict.fromkeys(risk_flags))

    async def async_validate_post(self, draft: PostDraft) -> tuple[bool, tuple[ValidationIssue, ...], tuple[str, ...]]:
        """Async wrapper for post validation."""

        await asyncio.sleep(0)
        return self.validate_post(draft)

    def schedule_posts(
        self,
        drafts: Sequence[PostDraft],
        start_date: str | date | datetime | None = None,
        days: int = 14,
        deduplicate: bool = True,
    ) -> list[ScheduledPost]:
        """Validate and assign drafts to recommended slots."""

        if not drafts:
            return []
        platforms = [draft.normalized_platform() for draft in drafts]
        slots = self.recommend_slots(platforms, start_date=start_date, days=max(days, 1), is_commercial=True)
        if len(slots) < len(drafts):
            # Extend the horizon automatically for practical planning.
            slots = self.recommend_slots(platforms, start_date=start_date, days=max(days, 1) + 30, is_commercial=True)

        scheduled: list[ScheduledPost] = []
        used_ids: set[str] = set()
        slot_index = 0

        for draft in drafts:
            platform = draft.normalized_platform()
            while slot_index < len(slots) and slots[slot_index].platform != platform:
                slot_index += 1
            if slot_index >= len(slots):
                fallback = self.next_safe_datetime(
                    datetime.combine(date_from_iso(start_date or datetime.now(self.tz).date()), time(9, 0), tzinfo=self.tz)
                    + timedelta(days=len(scheduled))
                )
                slot = TimeSlot(platform=platform, scheduled_at=fallback, timezone=self.timezone_name, reason="fallback")
            else:
                slot = slots[slot_index]
                slot_index += 1

            normalized_caption_text = normalize_caption(draft.caption)
            hashtags = normalize_hashtags(draft.hashtags)
            valid, issues, risk_flags = self.validate_post(
                PostDraft(
                    platform=platform,
                    caption=normalized_caption_text,
                    format=draft.format,
                    title=draft.title,
                    hashtags=hashtags,
                    cta=draft.cta,
                    media_count=draft.media_count,
                    contains_customer_image=draft.contains_customer_image,
                    contains_price=draft.contains_price,
                    offer_terms=draft.offer_terms,
                    contains_personal_data=draft.contains_personal_data,
                    is_commercial=draft.is_commercial,
                    pillar=draft.pillar,
                )
            )
            local_id = deterministic_id(platform, slot.scheduled_at, normalized_caption_text)
            if deduplicate and local_id in used_ids:
                continue
            used_ids.add(local_id)
            scheduled.append(
                ScheduledPost(
                    local_id=local_id,
                    platform=platform,
                    scheduled_at=slot.scheduled_at,
                    caption=normalized_caption_text,
                    format=draft.format,
                    hashtags=hashtags,
                    cta=draft.cta,
                    pillar=draft.pillar,
                    timezone=self.timezone_name,
                    approval_status="pending_owner_review",
                    risk_flags=risk_flags,
                    validation_issues=issues,
                )
            )

        scheduled.sort(key=lambda item: (item.scheduled_at, item.platform.value))
        return scheduled

    async def async_schedule_posts(
        self,
        drafts: Sequence[PostDraft],
        start_date: str | date | datetime | None = None,
        days: int = 14,
        deduplicate: bool = True,
    ) -> list[ScheduledPost]:
        """Async wrapper for post scheduling."""

        await asyncio.sleep(0)
        return self.schedule_posts(drafts, start_date=start_date, days=days, deduplicate=deduplicate)

    def export_json(self, posts: Sequence[ScheduledPost], indent: int = 2) -> str:
        """Export scheduled posts as JSON."""

        return json.dumps([post.to_dict() for post in posts], ensure_ascii=False, indent=indent)

    def export_csv(self, posts: Sequence[ScheduledPost]) -> str:
        """Export scheduled posts as CSV with UTF-8 friendly content."""

        output = io.StringIO()
        fieldnames = [
            "local_id",
            "display_date_he",
            "display_time",
            "timezone",
            "platform",
            "format",
            "pillar",
            "caption",
            "hashtags",
            "cta",
            "approval_status",
            "risk_flags",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for post in posts:
            data = post.to_dict()
            row = {field: data.get(field, "") for field in fieldnames}
            row["hashtags"] = " ".join(data["hashtags"])
            row["risk_flags"] = ",".join(data["risk_flags"])
            writer.writerow(row)
        return output.getvalue()


def sample_drafts(platforms: Sequence[str | Platform], business_type: str = "עסק מקומי") -> list[PostDraft]:
    """Create simple sample drafts for quick planning."""

    drafts: list[PostDraft] = []
    for platform_value in platforms:
        platform = parse_platform(platform_value)
        if platform == Platform.LINKEDIN:
            drafts.append(
                PostDraft(
                    platform=platform,
                    format="text",
                    pillar="education",
                    caption=f"{business_type}: לקוחות לא צריכים עוד סיסמה שיווקית. הם צריכים להבין מה יוצא להם מזה.",
                    hashtags=("#עסקיםקטנים", "#שיווק"),
                    cta="כתבו בתגובות אם תרצו את הצ'ק-ליסט.",
                )
            )
        elif platform == Platform.TIKTOK:
            drafts.append(
                PostDraft(
                    platform=platform,
                    format="video",
                    pillar="education",
                    media_count=1,
                    caption=f"3 טעויות נפוצות לפני שבוחרים {business_type}",
                    hashtags=("#טיפים", "#עסקיםקטנים"),
                    cta="עקבו לעוד טיפים קצרים.",
                )
            )
        elif platform == Platform.INSTAGRAM:
            drafts.append(
                PostDraft(
                    platform=platform,
                    format="reel",
                    pillar="trust",
                    media_count=1,
                    caption=f"לפני שבוחרים {business_type}: בדקו את 3 הדברים האלה",
                    hashtags=("#עסקיםקטנים", "#ישראל"),
                    cta="שלחו הודעה לקבלת פרטים.",
                )
            )
        else:
            drafts.append(
                PostDraft(
                    platform=platform,
                    format="group_post",
                    pillar="local",
                    caption=f"שאלה לבעלי עסקים באזור: מה הכי חשוב לכם כשבוחרים {business_type}?",
                    hashtags=("#עסקיםקטנים",),
                    cta="כתבו בתגובות.",
                )
            )
    return drafts


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan Israeli social-media posts.")
    sub = parser.add_subparsers(dest="command", required=False)

    plan = sub.add_parser("plan", help="Create a sample content plan.")
    plan.add_argument("--platform", action="append", choices=[p.value for p in Platform], default=[])
    plan.add_argument("--days", type=int, default=14)
    plan.add_argument("--business-type", default="עסק מקומי")
    plan.add_argument("--start-date", default=None)
    plan.add_argument("--allow-shabbat", action="store_true")

    validate = sub.add_parser("validate", help="Validate a single caption.")
    validate.add_argument("--platform", required=True)
    validate.add_argument("--caption", required=True)
    validate.add_argument("--format", default="text")
    validate.add_argument("--media-count", type=int, default=0)
    validate.add_argument("--hashtag", action="append", default=[])

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if not args.command or args.command == "plan":
        platforms = args.platform or [Platform.FACEBOOK.value, Platform.INSTAGRAM.value, Platform.TIKTOK.value, Platform.LINKEDIN.value]
        client = SocialMediaManagerClient(avoid_shabbat=not getattr(args, "allow_shabbat", False))
        drafts = sample_drafts(platforms, business_type=getattr(args, "business_type", "עסק מקומי"))
        posts = client.schedule_posts(drafts, start_date=getattr(args, "start_date", None), days=getattr(args, "days", 14))
        print(client.export_json(posts))
        return 0

    if args.command == "validate":
        client = SocialMediaManagerClient()
        draft = PostDraft(
            platform=args.platform,
            caption=args.caption,
            format=args.format,
            media_count=args.media_count,
            hashtags=tuple(args.hashtag),
        )
        valid, issues, risk_flags = client.validate_post(draft)
        payload = {
            "valid": valid,
            "issues": [issue.to_dict() for issue in issues],
            "risk_flags": list(risk_flags),
            "normalized_caption": normalize_caption(args.caption),
            "hashtags": list(normalize_hashtags(args.hashtag)),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if valid else 2

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
