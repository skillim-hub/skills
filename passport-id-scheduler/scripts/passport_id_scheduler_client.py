#!/usr/bin/env python3
"""Typed local helper for Israeli passport and Teudat Zehut appointment planning."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import textwrap
import urllib.parse
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Literal

OFFICIAL_LINKS: tuple[dict[str, str], ...] = (
    {"label": "gov.il Population and Immigration Authority", "url": "https://www.gov.il/he/departments/population_and_immigration_authority"},
    {"label": "gov.il services search", "url": "https://www.gov.il/"},
    {"label": "Official appointment channel", "url": "https://govisit.gov.il/"},
    {"label": "Personal government area", "url": "https://my.gov.il/"},
)
OFFICIAL_HOST_HINTS = ("gov.il", "my.gov.il", "govisit.gov.il")
DEFAULT_NEARBY_CITIES: dict[str, list[str]] = {
    "Tel Aviv-Yafo": ["Ramat Gan", "Givatayim", "Holon", "Bat Yam", "Bnei Brak"],
    "Jerusalem": ["Mevaseret Zion", "Modiin-Maccabim-Reut", "Beit Shemesh"],
    "Haifa": ["Krayot", "Nesher", "Tirat Carmel", "Akko"],
    "Beer Sheva": ["Omer", "Lehavim", "Dimona", "Netivot"],
    "Rishon LeZion": ["Holon", "Bat Yam", "Ness Ziona", "Rehovot"],
    "Netanya": ["Kfar Saba", "Hadera", "Herzliya"],
}
SERVICE_ALIASES: dict[str, str] = {
    "passport": "passport_renewal",
    "passport renewal": "passport_renewal",
    "renew passport": "passport_renewal",
    "new passport": "passport_new",
    "first passport": "passport_new",
    "lost passport": "passport_lost_stolen",
    "stolen passport": "passport_lost_stolen",
    "damaged passport": "passport_lost_stolen",
    "id": "id_renewal",
    "id card": "id_renewal",
    "teudat zehut": "id_renewal",
    "identity card": "id_renewal",
    "first id": "id_first",
    "new id": "id_first",
    "lost id": "id_lost_stolen",
    "stolen id": "id_lost_stolen",
    "biometric": "biometric_update",
    "biometric update": "biometric_update",
    "address": "address_update",
    "address update": "address_update",
    "name change": "name_status_update",
    "status update": "name_status_update",
    "חידוש דרכון": "passport_renewal",
    "דרכון ראשון": "passport_new",
    "דרכון אבד": "passport_lost_stolen",
    "תעודת זהות": "id_renewal",
    "תעודה ראשונה": "id_first",
    "תעודת זהות אבדה": "id_lost_stolen",
    "ביומטרי": "biometric_update",
    "עדכון כתובת": "address_update",
    "שינוי שם": "name_status_update",
}

class SchedulerError(ValueError): ...
class InvalidTeudatZehut(SchedulerError): ...
class InvalidPhone(SchedulerError): ...
class InvalidEmail(SchedulerError): ...
class InvalidDateWindow(SchedulerError): ...
class UnsupportedService(SchedulerError): ...
class NoCandidates(SchedulerError): ...
class UnsafeSource(SchedulerError): ...

class DocumentType(str, Enum):
    PASSPORT = "passport"
    ID_CARD = "id_card"
    BIOMETRIC = "biometric"
    ADDRESS = "address"
    NAME_STATUS = "name_status"

class ServiceType(str, Enum):
    PASSPORT_NEW = "passport_new"
    PASSPORT_RENEWAL = "passport_renewal"
    PASSPORT_LOST_STOLEN = "passport_lost_stolen"
    ID_FIRST = "id_first"
    ID_RENEWAL = "id_renewal"
    ID_LOST_STOLEN = "id_lost_stolen"
    BIOMETRIC_UPDATE = "biometric_update"
    ADDRESS_UPDATE = "address_update"
    NAME_STATUS_UPDATE = "name_status_update"

@dataclass(slots=True)
class ValidationResult:
    valid: bool
    normalized: str | None = None
    error: str | None = None
    code: str | None = None
    kind: str | None = None
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(slots=True)
class ApplicantProfile:
    full_name: str
    teudat_zehut: str
    phone: str
    email: str | None = None
    is_minor: bool = False
    current_document_available: bool = True
    notes: str | None = None
    def normalized(self) -> "ApplicantProfile":
        id_result = validate_teudat_zehut(self.teudat_zehut)
        phone_result = validate_israeli_phone(self.phone)
        if not id_result.valid:
            raise InvalidTeudatZehut(id_result.error or "Invalid Teudat Zehut")
        if not phone_result.valid:
            raise InvalidPhone(phone_result.error or "Invalid phone")
        if self.email and not validate_email(self.email):
            raise InvalidEmail("Invalid email address")
        return ApplicantProfile(
            full_name=self.full_name.strip(),
            teudat_zehut=id_result.normalized or self.teudat_zehut,
            phone=phone_result.normalized or self.phone,
            email=self.email.strip().lower() if self.email else None,
            is_minor=self.is_minor,
            current_document_available=self.current_document_available,
            notes=self.notes,
        )

@dataclass(slots=True)
class AppointmentPreference:
    preferred_city: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    earliest_time: time | None = None
    latest_time: time | None = None
    allow_nearby: bool = True
    radius_km: int = 25
    accessibility_required: bool = False
    preferred_language: Literal["en", "he"] = "en"
    def validate(self) -> None:
        if self.date_from and self.date_to:
            validate_date_window(self.date_from, self.date_to)
        if self.earliest_time and self.latest_time and self.earliest_time > self.latest_time:
            raise InvalidDateWindow("Earliest time cannot be later than latest time")
        if self.radius_km < 0:
            raise InvalidDateWindow("Radius cannot be negative")

@dataclass(slots=True)
class AppointmentRequest:
    service: ServiceType | str
    document_type: DocumentType | str | None = None
    applicants: list[ApplicantProfile] = field(default_factory=list)
    preference: AppointmentPreference = field(default_factory=AppointmentPreference)
    urgent_travel_date: date | None = None
    business_context: str | None = None
    notes: str | None = None
    def normalized(self) -> "AppointmentRequest":
        service = parse_service(self.service)
        document = parse_document_type(self.document_type, service)
        applicants = [applicant.normalized() for applicant in self.applicants]
        self.preference.validate()
        return AppointmentRequest(service, document, applicants, self.preference, self.urgent_travel_date, self.business_context, self.notes)

@dataclass(slots=True)
class AppointmentCandidate:
    bureau: str
    city: str
    date: date
    start_time: time
    end_time: time | None = None
    service: ServiceType | str | None = None
    address: str | None = None
    source_url: str | None = None
    accessible: bool = False
    notes: str | None = None
    score: int | None = None
    def key(self) -> tuple[str, str, str, str]:
        return (self.city.strip().lower(), self.bureau.strip().lower(), self.date.isoformat(), self.start_time.strftime("%H:%M"))
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["date"] = self.date.isoformat()
        data["display_date"] = display_date(self.date)
        data["start_time"] = self.start_time.strftime("%H:%M")
        data["end_time"] = self.end_time.strftime("%H:%M") if self.end_time else None
        data["service"] = parse_service(self.service).value if self.service else None
        return data

@dataclass(slots=True)
class AppointmentPlan:
    service: ServiceType
    document_type: DocumentType
    valid: bool
    errors: list[str]
    warnings: list[str]
    checklist: list[str]
    official_links: list[dict[str, str]]
    nearby_cities: list[str]
    privacy_notes: list[str]
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["service"] = self.service.value
        data["document_type"] = self.document_type.value
        return data

def validate_teudat_zehut(id_number: str) -> ValidationResult:
    if id_number is None:
        return ValidationResult(False, error="No ID supplied", code="ID_EMPTY")
    raw = str(id_number).strip()
    if not raw:
        return ValidationResult(False, error="No ID supplied", code="ID_EMPTY")
    if not raw.isdigit():
        return ValidationResult(False, error="ID must contain digits only", code="ID_NOT_DIGITS")
    if len(raw) > 9:
        return ValidationResult(False, error="ID cannot exceed 9 digits", code="ID_TOO_LONG")
    normalized = raw.zfill(9)
    if normalized == "000000000":
        return ValidationResult(False, normalized, "All-zero placeholder is invalid", "ID_ALL_ZERO")
    total = 0
    for index, digit in enumerate(normalized):
        value = int(digit) * (1 + (index % 2))
        if value > 9:
            value -= 9
        total += value
    if total % 10:
        return ValidationResult(False, normalized, "Check digit validation failed", "ID_CHECKSUM")
    return ValidationResult(True, normalized)

def validate_israeli_phone(phone: str) -> ValidationResult:
    if phone is None:
        return ValidationResult(False, error="No phone supplied", code="PHONE_EMPTY")
    raw = str(phone).strip()
    if not raw:
        return ValidationResult(False, error="No phone supplied", code="PHONE_EMPTY")
    if raw.startswith("*") or len(re.sub(r"\D", "", raw)) <= 5:
        return ValidationResult(False, error="Short codes are not valid appointment contacts", code="PHONE_SHORT_CODE")
    cleaned = re.sub(r"[\s\-().]", "", raw)
    if cleaned.startswith("+972"):
        cleaned = "0" + cleaned[4:]
    elif cleaned.startswith("972"):
        cleaned = "0" + cleaned[3:]
    if not cleaned.isdigit():
        return ValidationResult(False, error="Phone contains unsupported characters", code="PHONE_NOT_NUMERIC")
    if cleaned.startswith("1900") or cleaned.startswith("1919"):
        return ValidationResult(False, error="Premium numbers are not valid contacts", code="PHONE_PREMIUM")
    if re.fullmatch(r"05\d{8}", cleaned):
        return ValidationResult(True, cleaned, kind="mobile")
    if re.fullmatch(r"0[23489]\d{7}", cleaned):
        return ValidationResult(True, cleaned, kind="landline")
    if re.fullmatch(r"07[2346789]\d{7}", cleaned):
        return ValidationResult(True, cleaned, kind="voip")
    return ValidationResult(False, cleaned, "Unsupported Israeli phone prefix or length", "PHONE_UNSUPPORTED_PREFIX")

def normalize_phone(phone: str) -> str:
    result = validate_israeli_phone(phone)
    if not result.valid or not result.normalized:
        raise InvalidPhone(result.error or "Invalid Israeli phone number")
    return result.normalized

def validate_email(email: str) -> bool:
    return bool(email and len(email) <= 254 and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()))

def validate_date_window(date_from: date, date_to: date, *, max_days: int = 370) -> ValidationResult:
    if date_to < date_from:
        raise InvalidDateWindow("End date cannot be before start date")
    if (date_to - date_from).days + 1 > max_days:
        raise InvalidDateWindow(f"Date window cannot exceed {max_days} days")
    return ValidationResult(True, f"{date_from.isoformat()}:{date_to.isoformat()}")

def display_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")

def parse_date(value: str | date | None) -> date | None:
    if value is None or isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InvalidDateWindow("Dates must use ISO format YYYY-MM-DD") from exc

def parse_time(value: str | time | None) -> time | None:
    if value is None or isinstance(value, time):
        return value
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise InvalidDateWindow("Times must use HH:MM or HH:MM:SS") from exc

def parse_service(service: ServiceType | str | None) -> ServiceType:
    if isinstance(service, ServiceType):
        return service
    if service is None:
        raise UnsupportedService("Service is required")
    normalized = str(service).strip().lower().replace("-", "_")
    if normalized in SERVICE_ALIASES:
        normalized = SERVICE_ALIASES[normalized]
    try:
        return ServiceType(normalized)
    except ValueError as exc:
        raise UnsupportedService(f"Unsupported service: {service}") from exc

def parse_document_type(document_type: DocumentType | str | None, service: ServiceType | str) -> DocumentType:
    if isinstance(document_type, DocumentType):
        return document_type
    if document_type:
        normalized = str(document_type).strip().lower().replace("-", "_")
        try:
            return DocumentType(normalized)
        except ValueError as exc:
            raise UnsupportedService(f"Unsupported document type: {document_type}") from exc
    value = parse_service(service).value
    if value.startswith("passport"):
        return DocumentType.PASSPORT
    if value.startswith("id"):
        return DocumentType.ID_CARD
    if value.startswith("biometric"):
        return DocumentType.BIOMETRIC
    if value.startswith("address"):
        return DocumentType.ADDRESS
    return DocumentType.NAME_STATUS

def dedupe_keep_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set(); out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item); out.append(item)
    return out

def service_checklist(service: ServiceType | str, *, minor: bool = False, business: bool = False) -> list[str]:
    service_type = parse_service(service)
    items = ["Teudat Zehut", "Official appointment confirmation SMS/email"]
    if service_type in {ServiceType.PASSPORT_NEW, ServiceType.PASSPORT_RENEWAL}:
        items += ["Current passport if available", "Payment method if required by the official service"]
    elif service_type is ServiceType.PASSPORT_LOST_STOLEN:
        items += ["Other identifying document if available", "Loss/theft/damage documentation if required by official guidance", "Travel proof if using an urgent channel and official guidance requires it"]
    elif service_type is ServiceType.ID_FIRST:
        items += ["Parent or guardian identification if applicant is a minor", "Birth or relationship documentation if required"]
    elif service_type is ServiceType.ID_RENEWAL:
        items.append("Current Teudat Zehut if available")
    elif service_type is ServiceType.ID_LOST_STOLEN:
        items += ["Other identifying document if available", "Loss/theft/damage documentation if required by official guidance"]
    elif service_type is ServiceType.BIOMETRIC_UPDATE:
        items += ["Current biometric document if available", "Review official biometric consent and documentation instructions"]
    elif service_type is ServiceType.ADDRESS_UPDATE:
        items += ["Check online address update service before booking", "Proof of address only if official guidance requires it"]
    elif service_type is ServiceType.NAME_STATUS_UPDATE:
        items += ["Civil-status document such as marriage, divorce, or court order", "Current Teudat Zehut and passport if affected"]
    if minor:
        items += ["Parent/guardian consent documentation according to current official guidance", "Minor applicant presence if required by the official service"]
    if business:
        items.append("Post-receipt update list: bank, accountant, payroll, digital signature provider")
    return dedupe_keep_order(items)

def hebrew_checklist(service: ServiceType | str, *, minor: bool = False, business: bool = False) -> list[str]:
    service_type = parse_service(service)
    items = ["תעודת זהות", "אישור תור רשמי ב-SMS או בדוא״ל"]
    if service_type in {ServiceType.PASSPORT_NEW, ServiceType.PASSPORT_RENEWAL}:
        items += ["דרכון קיים אם יש", "אמצעי תשלום אם נדרש בעמוד הרשמי"]
    elif service_type is ServiceType.PASSPORT_LOST_STOLEN:
        items += ["מסמך מזהה חלופי אם יש", "דיווח על אובדן/גניבה/נזק אם ההנחיה הרשמית דורשת", "אישור נסיעה אם המסלול הדחוף דורש זאת"]
    elif service_type is ServiceType.ID_FIRST:
        items += ["תעודת זהות של הורה או אפוטרופוס", "מסמכי קשר משפחתי אם נדרש"]
    elif service_type is ServiceType.ID_RENEWAL:
        items.append("תעודת זהות קיימת אם יש")
    elif service_type is ServiceType.ID_LOST_STOLEN:
        items += ["מסמך מזהה חלופי אם יש", "דיווח על אובדן/גניבה/נזק אם נדרש"]
    elif service_type is ServiceType.BIOMETRIC_UPDATE:
        items += ["מסמך ביומטרי קיים אם יש", "בדיקת הנחיות הסכמה ותיעוד ביומטרי בעמוד הרשמי"]
    elif service_type is ServiceType.ADDRESS_UPDATE:
        items += ["בדיקת שירות עדכון כתובת מקוון לפני קביעת תור", "אסמכתת כתובת רק אם נדרש"]
    elif service_type is ServiceType.NAME_STATUS_UPDATE:
        items += ["מסמך מצב אישי כגון נישואים, גירושים או צו בית משפט", "תעודת זהות ודרכון אם מושפעים מהשינוי"]
    if minor:
        items += ["הסכמת הורה/אפוטרופוס לפי ההנחיה הרשמית", "נוכחות הקטין/ה אם נדרשת"]
    if business:
        items.append("רשימת עדכון לאחר קבלת המסמך: בנק, רואה חשבון, שכר, ספק חתימה דיגיטלית")
    return dedupe_keep_order(items)

def classify_service(text: str) -> ServiceType | None:
    lowered = text.strip().lower()
    for phrase, service in sorted(SERVICE_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if phrase.lower() in lowered:
            return ServiceType(service)
    return None

def official_service_links(query: str | None = None) -> list[dict[str, str]]:
    links = [dict(link) for link in OFFICIAL_LINKS]
    if query:
        links.append({"label": "gov.il search query", "url": f"https://www.gov.il/he/search?query={urllib.parse.quote_plus(query)}"})
    return links

def nearby_cities(city: str | None) -> list[str]:
    return DEFAULT_NEARBY_CITIES.get(city, []) if city else []

def is_official_source(url: str | None) -> bool:
    if not url:
        return True
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(host == hint or host.endswith("." + hint) for hint in OFFICIAL_HOST_HINTS)

def mask_teudat_zehut(id_number: str) -> str:
    result = validate_teudat_zehut(id_number)
    normalized = result.normalized or str(id_number).zfill(9)[-9:]
    return f"*****{normalized[-4:]}"

def privacy_notes() -> list[str]:
    return [
        "Do not store passwords, OTPs, payment card data, or biometric identifiers.",
        "Mask Teudat Zehut in logs and shared files.",
        "Delete temporary appointment data after it is no longer needed.",
        "For employee data, keep a lawful purpose and limit access.",
    ]

class PassportIdSchedulerClient:
    """Synchronous local helper client."""

    def validate_applicant(self, applicant: ApplicantProfile) -> ApplicantProfile:
        return applicant.normalized()

    def build_plan(self, request: AppointmentRequest) -> AppointmentPlan:
        warnings = ["Complete final booking only through the official appointment channel.", "Verify current official requirements before arrival."]
        try:
            normalized = request.normalized()
        except SchedulerError as exc:
            service = parse_service(request.service) if request.service else ServiceType.PASSPORT_RENEWAL
            document = parse_document_type(request.document_type, service)
            return AppointmentPlan(service, document, False, [str(exc)], warnings, [], official_service_links(str(request.service)), nearby_cities(request.preference.preferred_city), privacy_notes())
        if not normalized.applicants:
            warnings.append("No applicant profile supplied; collect applicant data before final booking.")
        minor = any(a.is_minor for a in normalized.applicants)
        business = bool(normalized.business_context)
        if minor:
            warnings.append("Minor workflow may require parent/guardian consent and presence.")
        if normalized.urgent_travel_date:
            days = (normalized.urgent_travel_date - date.today()).days
            if days <= 30:
                warnings.append("Travel date is close; use official urgent-travel guidance and do not assume issuance.")
        if normalized.service is ServiceType.ADDRESS_UPDATE:
            warnings.append("Check online self-service before booking an in-person appointment.")
        if normalized.preference.accessibility_required:
            warnings.append("Verify bureau accessibility from current official sources.")
        return AppointmentPlan(
            normalized.service,
            normalized.document_type,  # type: ignore[arg-type]
            True,
            [],
            dedupe_keep_order(warnings),
            service_checklist(normalized.service, minor=minor, business=business),
            official_service_links(normalized.service.value),
            nearby_cities(normalized.preference.preferred_city) if normalized.preference.allow_nearby else [],
            privacy_notes(),
        )

    def rank_candidates(self, request: AppointmentRequest, candidates: list[AppointmentCandidate]) -> list[AppointmentCandidate]:
        if not candidates:
            raise NoCandidates("At least one appointment candidate is required")
        normalized = request.normalized()
        unique: dict[tuple[str, str, str, str], AppointmentCandidate] = {}
        for candidate in candidates:
            if not is_official_source(candidate.source_url):
                raise UnsafeSource(f"Candidate source is not official: {candidate.source_url}")
            unique[candidate.key()] = candidate
        ranked = list(unique.values())
        for candidate in ranked:
            candidate.score = self._score_candidate(normalized, candidate)
        ranked.sort(key=lambda c: (-int(c.score or 0), c.date, c.start_time, c.city))
        return ranked

    def _score_candidate(self, request: AppointmentRequest, candidate: AppointmentCandidate) -> int:
        score = 50
        preference = request.preference
        candidate_service = parse_service(candidate.service) if candidate.service else request.service
        score += 20 if candidate_service == request.service else -20
        if preference.preferred_city and candidate.city.lower() == preference.preferred_city.lower():
            score += 15
        elif preference.preferred_city and candidate.city in nearby_cities(preference.preferred_city):
            score += 8
        if preference.date_from and candidate.date < preference.date_from:
            score -= 30
        if preference.date_to and candidate.date > preference.date_to:
            score -= 30
        if preference.earliest_time and candidate.start_time < preference.earliest_time:
            score -= 8
        if preference.latest_time and candidate.start_time > preference.latest_time:
            score -= 8
        if preference.accessibility_required:
            score += 12 if candidate.accessible else -18
        today = date.today()
        days_until_candidate = max((candidate.date - today).days, 0)
        if request.urgent_travel_date:
            days_until_travel = (request.urgent_travel_date - today).days
            score += 20 if candidate.date <= request.urgent_travel_date else -35
            if days_until_travel <= 30:
                score += max(0, 20 - days_until_candidate)
        else:
            score += max(0, 12 - min(days_until_candidate, 12))
        return max(0, min(100, score))


    def create_request_record(
        self,
        request: AppointmentRequest,
        *,
        environment: Literal["sandbox", "production"] = "sandbox",
    ) -> dict[str, Any]:
        """Create a local request record that can be stored and referenced by id."""
        if environment not in {"sandbox", "production"}:
            raise SchedulerError("Environment must be sandbox or production")
        normalized = request.normalized()
        payload = request_to_dict(normalized)
        digest_source = dumps_json({"environment": environment, "request": payload})
        request_id = "req_" + hashlib.sha256(digest_source.encode("utf-8")).hexdigest()[:12]
        return {
            "id": request_id,
            "environment": environment,
            "request": payload,
            "official_only": True,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }

    def create_ics(self, title: str, start_date: date, start_time: time, *, duration_minutes: int = 30, location: str = "", description: str = "") -> str:
        start = datetime.combine(start_date, start_time)
        end = start + timedelta(minutes=duration_minutes)
        fmt = lambda dt: dt.strftime("%Y%m%dT%H%M%S")
        safe_description = description.replace("\n", "\\n")
        uid = f"passport-id-{start.strftime('%Y%m%d%H%M%S')}-local"
        return textwrap.dedent(f"""\
        BEGIN:VCALENDAR
        VERSION:2.0
        PRODID:-//passport-id-scheduler//local//EN
        BEGIN:VEVENT
        UID:{uid}
        DTSTAMP:{fmt(datetime.now(timezone.utc).replace(tzinfo=None))}Z
        DTSTART:{fmt(start)}
        DTEND:{fmt(end)}
        SUMMARY:{title}
        LOCATION:{location}
        DESCRIPTION:{safe_description}
        END:VEVENT
        END:VCALENDAR
        """)

    def write_ics(self, path: str | Path, *args: Any, **kwargs: Any) -> Path:
        target = Path(path)
        target.write_text(self.create_ics(*args, **kwargs), encoding="utf-8")
        return target

class AsyncPassportIdSchedulerClient:
    def __init__(self, sync_client: PassportIdSchedulerClient | None = None) -> None:
        self.sync_client = sync_client or PassportIdSchedulerClient()
    async def validate_applicant(self, applicant: ApplicantProfile) -> ApplicantProfile:
        await asyncio.sleep(0); return self.sync_client.validate_applicant(applicant)
    async def build_plan(self, request: AppointmentRequest) -> AppointmentPlan:
        await asyncio.sleep(0); return self.sync_client.build_plan(request)
    async def rank_candidates(self, request: AppointmentRequest, candidates: list[AppointmentCandidate]) -> list[AppointmentCandidate]:
        await asyncio.sleep(0); return self.sync_client.rank_candidates(request, candidates)
    async def create_ics(self, *args: Any, **kwargs: Any) -> str:
        await asyncio.sleep(0); return self.sync_client.create_ics(*args, **kwargs)

def candidate_from_dict(data: dict[str, Any]) -> AppointmentCandidate:
    return AppointmentCandidate(
        bureau=data.get("bureau", "Population and Immigration Authority bureau"),
        city=data["city"],
        address=data.get("address"),
        date=parse_date(data["date"]) or date.today(),
        start_time=parse_time(data["start_time"]) or time(9, 0),
        end_time=parse_time(data.get("end_time")),
        service=data.get("service"),
        source_url=data.get("source_url"),
        accessible=bool(data.get("accessible", False)),
        notes=data.get("notes"),
    )

def request_from_dict(data: dict[str, Any]) -> AppointmentRequest:
    applicants = [
        ApplicantProfile(
            full_name=item.get("full_name", "Applicant"),
            teudat_zehut=item.get("teudat_zehut", "123456782"),
            phone=item.get("phone", "0521234567"),
            email=item.get("email"),
            is_minor=bool(item.get("is_minor", False)),
            current_document_available=bool(item.get("current_document_available", True)),
            notes=item.get("notes"),
        )
        for item in data.get("applicants", [])
    ]
    pref_data = data.get("preference", data)
    preference = AppointmentPreference(
        preferred_city=pref_data.get("preferred_city") or pref_data.get("city"),
        date_from=parse_date(pref_data.get("date_from")),
        date_to=parse_date(pref_data.get("date_to")),
        earliest_time=parse_time(pref_data.get("earliest_time")),
        latest_time=parse_time(pref_data.get("latest_time")),
        allow_nearby=bool(pref_data.get("allow_nearby", True)),
        radius_km=int(pref_data.get("radius_km", 25)),
        accessibility_required=bool(pref_data.get("accessibility_required", False)),
        preferred_language=pref_data.get("preferred_language", "en"),
    )
    return AppointmentRequest(
        service=data.get("service", "passport_renewal"),
        document_type=data.get("document_type"),
        applicants=applicants,
        preference=preference,
        urgent_travel_date=parse_date(data.get("urgent_travel_date")),
        business_context=data.get("business_context"),
        notes=data.get("notes"),
    )


def request_to_dict(request: AppointmentRequest) -> dict[str, Any]:
    """Return a JSON-safe request payload without inventing official state."""
    data: dict[str, Any] = {
        "service": parse_service(request.service).value,
        "document_type": parse_document_type(request.document_type, request.service).value,
        "applicants": [
            {
                "full_name": applicant.full_name,
                "teudat_zehut": applicant.teudat_zehut,
                "phone": applicant.phone,
                "email": applicant.email,
                "is_minor": applicant.is_minor,
                "current_document_available": applicant.current_document_available,
                "notes": applicant.notes,
            }
            for applicant in request.applicants
        ],
        "preference": {
            "preferred_city": request.preference.preferred_city,
            "date_from": request.preference.date_from.isoformat() if request.preference.date_from else None,
            "date_to": request.preference.date_to.isoformat() if request.preference.date_to else None,
            "earliest_time": request.preference.earliest_time.strftime("%H:%M") if request.preference.earliest_time else None,
            "latest_time": request.preference.latest_time.strftime("%H:%M") if request.preference.latest_time else None,
            "allow_nearby": request.preference.allow_nearby,
            "radius_km": request.preference.radius_km,
            "accessibility_required": request.preference.accessibility_required,
            "preferred_language": request.preference.preferred_language,
        },
        "urgent_travel_date": request.urgent_travel_date.isoformat() if request.urgent_travel_date else None,
        "business_context": request.business_context,
        "notes": request.notes,
    }
    return data

def plan_to_markdown(plan: AppointmentPlan, *, lang: Literal["en", "he"] = "en") -> str:
    if lang == "he":
        checklist = "\n".join(f"- {item}" for item in hebrew_checklist(plan.service))
        warnings = "\n".join(f"- {item}" for item in plan.warnings)
        return f"שירות: {plan.service.value}\nסוג מסמך: {plan.document_type.value}\nתקין: {'כן' if plan.valid else 'לא'}\n\nמסמכים:\n{checklist}\n\nהערות:\n{warnings}\n"
    checklist = "\n".join(f"- {item}" for item in plan.checklist)
    warnings = "\n".join(f"- {item}" for item in plan.warnings)
    links = "\n".join(f"- {link['label']}: {link['url']}" for link in plan.official_links)
    return f"Service: {plan.service.value}\nDocument type: {plan.document_type.value}\nValid: {plan.valid}\n\nChecklist:\n{checklist}\n\nWarnings:\n{warnings}\n\nOfficial links:\n{links}\n"

def dumps_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
