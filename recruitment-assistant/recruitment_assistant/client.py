from __future__ import annotations

import asyncio
import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Iterable, Literal, Sequence
from zoneinfo import ZoneInfo


Environment = Literal["sandbox", "production"]
Seniority = Literal["intern", "junior", "mid", "senior", "lead", "manager", "unknown"]
RoleFamily = Literal[
    "software",
    "product",
    "design",
    "marketing",
    "sales",
    "operations",
    "accounting",
    "customer_service",
    "administration",
    "logistics",
    "unknown",
]


class RecruitmentAssistantError(ValueError):
    """Base exception for validation and workflow errors."""


class ComplianceError(RecruitmentAssistantError):
    """Raised when a workflow attempts to use disallowed hiring criteria."""


class SchedulingError(RecruitmentAssistantError):
    """Raised when interview slots cannot be generated."""


@dataclass(slots=True)
class RoleProfile:
    title: str
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    seniority: Seniority = "unknown"
    role_family: RoleFamily = "unknown"
    location: str = "Israel"
    salary_min_ils: int | None = None
    salary_max_ils: int | None = None
    languages: list[str] = field(default_factory=list)
    must_have_terms: list[str] = field(default_factory=list)
    disallowed_terms: list[str] = field(default_factory=list)

    def normalized(self) -> "RoleProfile":
        return RoleProfile(
            title=self.title.strip(),
            required_skills=normalize_terms(self.required_skills),
            preferred_skills=normalize_terms(self.preferred_skills),
            seniority=normalize_seniority(self.seniority or self.title),
            role_family=normalize_role_family(self.role_family if self.role_family != "unknown" else self.title),
            location=self.location.strip() or "Israel",
            salary_min_ils=self.salary_min_ils,
            salary_max_ils=self.salary_max_ils,
            languages=normalize_terms(self.languages),
            must_have_terms=normalize_terms(self.must_have_terms),
            disallowed_terms=normalize_terms(self.disallowed_terms),
        )


@dataclass(slots=True)
class Candidate:
    name: str
    resume_text: str
    email: str | None = None
    phone: str | None = None
    languages: list[str] = field(default_factory=list)
    source: str = "manual"

    def normalized(self) -> "Candidate":
        extracted_email = self.email or extract_email(self.resume_text)
        extracted_phone = self.phone or extract_phone(self.resume_text)
        return Candidate(
            name=self.name.strip() or "Unknown candidate",
            resume_text=self.resume_text.strip(),
            email=extracted_email,
            phone=extracted_phone,
            languages=normalize_terms(self.languages or detect_languages(self.resume_text)),
            source=self.source.strip() or "manual",
        )


@dataclass(slots=True)
class ScreeningResult:
    candidate_id: str
    candidate_name: str
    score: int
    recommendation: Literal["advance", "review", "decline"]
    matched_required: list[str]
    missing_required: list[str]
    matched_preferred: list[str]
    detected_seniority: Seniority
    role_family: RoleFamily
    years_experience: float
    compliance_flags: list[str]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class InterviewSlot:
    candidate_id: str
    candidate_name: str
    start: str
    end: str
    timezone: str = "Asia/Jerusalem"
    channel: Literal["phone", "video", "onsite"] = "video"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class JobAdValidation:
    approved: bool
    flags: list[str]
    suggestions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ROLE_ALIASES: dict[RoleFamily, set[str]] = {
    "software": {"software", "developer", "engineer", "python", "full stack", "frontend", "backend", "מפתח", "מתכנת", "תוכנה", "פייתון"},
    "product": {"product", "pm", "product manager", "מוצר", "מנהל מוצר", "מנהלת מוצר"},
    "design": {"design", "ux", "ui", "figma", "מעצב", "מעצבת", "חוויית משתמש", "עיצוב"},
    "marketing": {"marketing", "digital", "ppc", "seo", "social", "שיווק", "דיגיטל", "קידום", "רשתות חברתיות"},
    "sales": {"sales", "account executive", "business development", "מכירות", "פיתוח עסקי", "נציג מכירות"},
    "operations": {"operations", "office manager", "ops", "תפעול", "מנהל תפעול", "מנהלת תפעול"},
    "accounting": {"bookkeeping", "accounting", "payroll", "חשבונות", "הנהלת חשבונות", "שכר", "רואה חשבון"},
    "customer_service": {"customer service", "support", "success", "שירות לקוחות", "תמיכה", "שימור לקוחות"},
    "administration": {"administration", "admin", "secretary", "office", "מזכירות", "אדמיניסטרציה", "ניהול משרד"},
    "logistics": {"logistics", "warehouse", "shipping", "supply", "לוגיסטיקה", "מחסן", "שילוח", "אספקה"},
}

SENIORITY_ALIASES: dict[Seniority, set[str]] = {
    "intern": {"intern", "trainee", "student", "מתמחה", "סטודנט", "סטודנטית"},
    "junior": {"junior", "entry", "0-2", "0–2", "ג'וניור", "מתחיל", "מתחילה", "ללא ניסיון"},
    "mid": {"mid", "intermediate", "2-5", "2–5", "ביניים", "בעל ניסיון", "בעלת ניסיון"},
    "senior": {"senior", "5+", "6+", "בכיר", "בכירה", "מנוסה"},
    "lead": {"lead", "principal", "tech lead", "ראש צוות", "מוביל", "מובילה"},
    "manager": {"manager", "director", "head", "מנהל", "מנהלת", "ראש תחום"},
    "unknown": {"unknown"},
}

COMMON_SKILLS: set[str] = {
    "python", "javascript", "typescript", "react", "node", "sql", "excel", "priority", "sap",
    "quickbooks", "hashavshevet", "חשבשבת", "פריוריטי", "אקסל", "שירות לקוחות", "מכירות",
    "שיווק", "דיגיטל", "seo", "ppc", "figma", "canva", "crm", "hubspot", "salesforce",
    "payroll", "שכר", "הנהלת חשבונות", "חשבונות", "לוגיסטיקה", "מחסן", "תיאום פגישות",
    "יומן", "ניהול משרד", "wordpress", "shopify", "woocommerce", "analytics",
}

DISALLOWED_JOB_AD_TERMS: dict[str, str] = {
    "צעיר": "Avoid age preference. Describe required availability, workload, or experience instead.",
    "צעירה": "Avoid age preference. Describe required availability, workload, or experience instead.",
    "רווק": "Avoid marital-status criteria.",
    "רווקה": "Avoid marital-status criteria.",
    "ללא ילדים": "Avoid family-status criteria.",
    "אחרי צבא": "Avoid military-service criteria unless a documented legal or safety requirement applies.",
    "שירות צבאי": "Avoid military-service criteria unless role necessity is documented.",
    "גבר": "Avoid gender preference. Use neutral wording.",
    "אישה": "Avoid gender preference. Use neutral wording.",
    "מראה ייצוגי": "Avoid appearance-based criteria. Describe customer-facing communication requirements instead.",
    "native hebrew": "Avoid nationality or origin proxy. State language proficiency level instead.",
    "young": "Avoid age preference.",
    "single": "Avoid marital-status criteria.",
    "male": "Avoid gender preference.",
    "female": "Avoid gender preference.",
    "no kids": "Avoid family-status criteria.",
    "military service": "Avoid military-service criteria unless a documented legal or safety requirement applies.",
}

ISRAEL_TZ = ZoneInfo("Asia/Jerusalem")
ISRAEL_WEEKEND = {4, 5}  # Friday=4, Saturday=5


def normalize_terms(terms: Iterable[str]) -> list[str]:
    cleaned = []
    seen = set()
    for term in terms:
        value = str(term).strip().lower()
        if not value or value in seen:
            continue
        cleaned.append(value)
        seen.add(value)
    return cleaned


def stable_id(*parts: str) -> str:
    joined = "\n".join(parts).encode("utf-8")
    return hashlib.sha256(joined).hexdigest()[:16]


def extract_email(text: str) -> str | None:
    match = re.search(r"[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = re.search(r"(?:\+972|0)(?:[-\s]?\d){8,10}", text)
    if not match:
        return None
    return re.sub(r"\s+", "", match.group(0))


def detect_languages(text: str) -> list[str]:
    languages: list[str] = []
    if re.search(r"[\u0590-\u05FF]", text):
        languages.append("hebrew")
    if re.search(r"[A-Za-z]", text):
        languages.append("english")
    if "ערבית" in text or "arabic" in text.lower():
        languages.append("arabic")
    if "רוסית" in text or "russian" in text.lower():
        languages.append("russian")
    return normalize_terms(languages)


def normalize_role_family(text: str) -> RoleFamily:
    value = (text or "").lower()
    for family, aliases in ROLE_ALIASES.items():
        if family in value:
            return family
        if any(alias.lower() in value for alias in aliases):
            return family
    return "unknown"


def normalize_seniority(text: str) -> Seniority:
    value = (text or "").lower()
    for level in ("lead", "manager", "senior", "mid", "junior", "intern"):
        aliases = SENIORITY_ALIASES[level]  # type: ignore[index]
        if level in value or any(alias.lower() in value for alias in aliases):
            return level  # type: ignore[return-value]
    years = extract_years_experience(value)
    if years >= 7:
        return "senior"
    if years >= 3:
        return "mid"
    if years > 0:
        return "junior"
    return "unknown"


def extract_years_experience(text: str) -> float:
    value = text.lower()
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|שנים|שנות)\s*(?:experience|ניסיון)?",
        r"(?:experience|ניסיון)\s*(?:of|של)?\s*(\d+(?:\.\d+)?)\+?",
        r"(\d+(?:\.\d+)?)\+?\s*שנות ניסיון",
    ]
    numbers: list[float] = []
    for pattern in patterns:
        for match in re.finditer(pattern, value):
            try:
                numbers.append(float(match.group(1)))
            except ValueError:
                continue
    return max(numbers) if numbers else 0.0


def extract_skills(text: str, extra_terms: Iterable[str] = ()) -> list[str]:
    value = text.lower()
    terms = set(COMMON_SKILLS)
    terms.update(normalize_terms(extra_terms))
    found = [term for term in terms if term and term.lower() in value]
    return sorted(found)


def validate_job_ad(text: str) -> JobAdValidation:
    value = text.lower()
    flags: list[str] = []
    suggestions: list[str] = []
    for term, suggestion in DISALLOWED_JOB_AD_TERMS.items():
        if term.lower() in value:
            flags.append(term)
            if suggestion not in suggestions:
                suggestions.append(suggestion)
    return JobAdValidation(approved=not flags, flags=flags, suggestions=suggestions)


def format_israeli_date(value: date | datetime) -> str:
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime("%d/%m/%Y")


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def next_business_day(start: date, holidays: set[date] | None = None) -> date:
    holidays = holidays or set()
    current = start
    while current.weekday() in ISRAEL_WEEKEND or current in holidays:
        current += timedelta(days=1)
    return current


def candidate_to_request(candidate: Candidate) -> dict[str, Any]:
    return asdict(candidate.normalized())


def role_to_request(role: RoleProfile) -> dict[str, Any]:
    return asdict(role.normalized())


class RecruitmentAssistantClient:
    """Synchronous local client for resume screening and interview scheduling."""

    def __init__(self, env: Environment = "sandbox", api_key: str | None = None, timezone_name: str = "Asia/Jerusalem") -> None:
        if env not in {"sandbox", "production"}:
            raise RecruitmentAssistantError("env must be sandbox or production")
        self.env = env
        self.api_key = api_key
        self.timezone = ZoneInfo(timezone_name)
        self._candidates: dict[str, Candidate] = {}
        self._results: dict[str, ScreeningResult] = {}

    @property
    def environment(self) -> Environment:
        return self.env

    def create_candidate(self, candidate: Candidate) -> dict[str, Any]:
        normalized = candidate.normalized()
        if not normalized.resume_text:
            raise RecruitmentAssistantError("resume_text is required")
        candidate_id = stable_id(normalized.name, normalized.email or "", normalized.resume_text[:500])
        self._candidates[candidate_id] = normalized
        return {"id": candidate_id, "candidate": candidate_to_request(normalized)}

    def get_candidate(self, candidate_id: str) -> Candidate:
        try:
            return self._candidates[candidate_id]
        except KeyError as exc:
            raise RecruitmentAssistantError(f"unknown candidate id: {candidate_id}") from exc

    def screen_resume(self, candidate: Candidate, role: RoleProfile) -> ScreeningResult:
        role_n = role.normalized()
        candidate_n = candidate.normalized()
        candidate_id = stable_id(candidate_n.name, candidate_n.email or "", candidate_n.resume_text[:500])
        skills = set(extract_skills(candidate_n.resume_text, role_n.required_skills + role_n.preferred_skills + role_n.languages))
        required = set(role_n.required_skills)
        preferred = set(role_n.preferred_skills)
        matched_required = sorted(required & skills)
        missing_required = sorted(required - skills)
        matched_preferred = sorted(preferred & skills)
        years = extract_years_experience(candidate_n.resume_text)
        detected_seniority = normalize_seniority(candidate_n.resume_text)
        compliance_flags = self._candidate_compliance_flags(candidate_n.resume_text, role_n)
        score = self._score(role_n, matched_required, missing_required, matched_preferred, years, detected_seniority, compliance_flags)
        recommendation: Literal["advance", "review", "decline"]
        if missing_required and score < 70:
            recommendation = "decline"
        elif score >= 78 and not compliance_flags:
            recommendation = "advance"
        else:
            recommendation = "review"
        notes = self._notes(role_n, candidate_n, missing_required, years, detected_seniority, compliance_flags)
        result = ScreeningResult(
            candidate_id=candidate_id,
            candidate_name=candidate_n.name,
            score=max(0, min(100, score)),
            recommendation=recommendation,
            matched_required=matched_required,
            missing_required=missing_required,
            matched_preferred=matched_preferred,
            detected_seniority=detected_seniority,
            role_family=role_n.role_family,
            years_experience=years,
            compliance_flags=compliance_flags,
            notes=notes,
        )
        self._results[candidate_id] = result
        return result

    def screen_batch(self, candidates: Sequence[Candidate], role: RoleProfile) -> list[ScreeningResult]:
        return [self.screen_resume(candidate, role) for candidate in candidates]

    def rank_candidates(self, candidates: Sequence[Candidate], role: RoleProfile) -> list[ScreeningResult]:
        return sorted(self.screen_batch(candidates, role), key=lambda result: (-result.score, result.candidate_name))

    def shortlist(self, candidates: Sequence[Candidate], role: RoleProfile, minimum_score: int = 75) -> list[ScreeningResult]:
        return [result for result in self.rank_candidates(candidates, role) if result.score >= minimum_score and result.recommendation != "decline"]

    def validate_job_ad(self, text: str) -> JobAdValidation:
        return validate_job_ad(text)

    def schedule_interviews(
        self,
        results: Sequence[ScreeningResult],
        start_date: str | date,
        interview_minutes: int = 45,
        daily_start: time = time(9, 0),
        daily_end: time = time(17, 0),
        channel: Literal["phone", "video", "onsite"] = "video",
        max_slots: int | None = None,
        holidays: set[date] | None = None,
    ) -> list[InterviewSlot]:
        if interview_minutes <= 0:
            raise SchedulingError("interview_minutes must be positive")
        if daily_start >= daily_end:
            raise SchedulingError("daily_start must be earlier than daily_end")
        if isinstance(start_date, str):
            current_day = parse_iso_date(start_date)
        else:
            current_day = start_date
        eligible = [result for result in results if result.recommendation in {"advance", "review"}]
        if max_slots is not None:
            eligible = eligible[:max_slots]
        slots: list[InterviewSlot] = []
        day = next_business_day(current_day, holidays)
        current_start = datetime.combine(day, daily_start, tzinfo=self.timezone)
        end_limit = datetime.combine(day, daily_end, tzinfo=self.timezone)
        duration = timedelta(minutes=interview_minutes)
        for result in eligible:
            while current_start + duration > end_limit or current_start.date().weekday() in ISRAEL_WEEKEND:
                day = next_business_day(current_start.date() + timedelta(days=1), holidays)
                current_start = datetime.combine(day, daily_start, tzinfo=self.timezone)
                end_limit = datetime.combine(day, daily_end, tzinfo=self.timezone)
            current_end = current_start + duration
            slots.append(
                InterviewSlot(
                    candidate_id=result.candidate_id,
                    candidate_name=result.candidate_name,
                    start=current_start.isoformat(),
                    end=current_end.isoformat(),
                    timezone=str(self.timezone),
                    channel=channel,
                )
            )
            current_start = current_end + timedelta(minutes=15)
        return slots

    def export_shortlist_json(self, results: Sequence[ScreeningResult]) -> str:
        return json.dumps([result.to_dict() for result in results], ensure_ascii=False, indent=2)

    def create_screening_request(self, candidate: Candidate, role: RoleProfile) -> dict[str, Any]:
        candidate_response = self.create_candidate(candidate)
        result = self.screen_resume(candidate, role)
        return {"id": candidate_response["id"], "result": result.to_dict()}

    def _score(
        self,
        role: RoleProfile,
        matched_required: Sequence[str],
        missing_required: Sequence[str],
        matched_preferred: Sequence[str],
        years: float,
        detected_seniority: Seniority,
        compliance_flags: Sequence[str],
    ) -> int:
        score = 35
        if role.required_skills:
            score += round(35 * (len(matched_required) / len(role.required_skills)))
        else:
            score += 20
        if role.preferred_skills:
            score += round(15 * (len(matched_preferred) / len(role.preferred_skills)))
        else:
            score += 5
        expected = {"intern": 0, "junior": 1, "mid": 3, "senior": 5, "lead": 6, "manager": 4}.get(role.seniority, 0)
        if years >= expected:
            score += 10
        elif expected and years < expected:
            score -= min(20, int((expected - years) * 5))
        if role.seniority != "unknown" and detected_seniority == role.seniority:
            score += 5
        if missing_required:
            score -= 12 * len(missing_required)
        if compliance_flags:
            score -= 10
        return score

    def _notes(
        self,
        role: RoleProfile,
        candidate: Candidate,
        missing_required: Sequence[str],
        years: float,
        detected_seniority: Seniority,
        compliance_flags: Sequence[str],
    ) -> list[str]:
        notes: list[str] = []
        if missing_required:
            notes.append("Verify missing required terms in an interview or request an updated resume.")
        if years == 0:
            notes.append("Resume does not state years of experience clearly.")
        if role.seniority != "unknown" and detected_seniority != "unknown" and role.seniority != detected_seniority:
            notes.append("Detected seniority differs from target seniority.")
        if not candidate.email:
            notes.append("Email address was not detected.")
        if not candidate.phone:
            notes.append("Israeli phone number was not detected.")
        notes.extend(compliance_flags)
        return notes

    def _candidate_compliance_flags(self, resume_text: str, role: RoleProfile) -> list[str]:
        flags: list[str] = []
        validation = validate_job_ad(" ".join(role.disallowed_terms))
        if validation.flags:
            flags.append("Remove disallowed criteria from role filters.")
        if any(term and term in resume_text.lower() for term in role.disallowed_terms):
            flags.append("Do not score candidates on disallowed personal criteria.")
        return flags


class AsyncRecruitmentAssistantClient:
    """Asynchronous wrapper around the synchronous client."""

    def __init__(self, env: Environment = "sandbox", api_key: str | None = None, timezone_name: str = "Asia/Jerusalem") -> None:
        self._client = RecruitmentAssistantClient(env=env, api_key=api_key, timezone_name=timezone_name)

    @property
    def environment(self) -> Environment:
        return self._client.environment

    async def create_candidate(self, candidate: Candidate) -> dict[str, Any]:
        return await asyncio.to_thread(self._client.create_candidate, candidate)

    async def get_candidate(self, candidate_id: str) -> Candidate:
        return await asyncio.to_thread(self._client.get_candidate, candidate_id)

    async def screen_resume(self, candidate: Candidate, role: RoleProfile) -> ScreeningResult:
        return await asyncio.to_thread(self._client.screen_resume, candidate, role)

    async def screen_batch(self, candidates: Sequence[Candidate], role: RoleProfile) -> list[ScreeningResult]:
        return await asyncio.to_thread(self._client.screen_batch, candidates, role)

    async def rank_candidates(self, candidates: Sequence[Candidate], role: RoleProfile) -> list[ScreeningResult]:
        return await asyncio.to_thread(self._client.rank_candidates, candidates, role)

    async def shortlist(self, candidates: Sequence[Candidate], role: RoleProfile, minimum_score: int = 75) -> list[ScreeningResult]:
        return await asyncio.to_thread(self._client.shortlist, candidates, role, minimum_score)

    async def validate_job_ad(self, text: str) -> JobAdValidation:
        return await asyncio.to_thread(self._client.validate_job_ad, text)

    async def schedule_interviews(
        self,
        results: Sequence[ScreeningResult],
        start_date: str | date,
        interview_minutes: int = 45,
        daily_start: time = time(9, 0),
        daily_end: time = time(17, 0),
        channel: Literal["phone", "video", "onsite"] = "video",
        max_slots: int | None = None,
        holidays: set[date] | None = None,
    ) -> list[InterviewSlot]:
        return await asyncio.to_thread(
            self._client.schedule_interviews,
            results,
            start_date,
            interview_minutes,
            daily_start,
            daily_end,
            channel,
            max_slots,
            holidays,
        )

    async def export_shortlist_json(self, results: Sequence[ScreeningResult]) -> str:
        return await asyncio.to_thread(self._client.export_shortlist_json, results)

    async def create_screening_request(self, candidate: Candidate, role: RoleProfile) -> dict[str, Any]:
        return await asyncio.to_thread(self._client.create_screening_request, candidate, role)
