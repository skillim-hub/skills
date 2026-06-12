"""Local Hebrew-English translation assistance utilities.

The module is deterministic and network-free. It provides terminology
replacement, register guidance, idiom handling, date localization, quality
checks, and small job-storage helpers for CLI workflows.
"""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping

HEBREW_RE = re.compile(r"[\u0590-\u05FF]")
NIKUD_RE = re.compile(r"[\u0591-\u05BD\u05BF\u05C1-\u05C2\u05C4-\u05C5\u05C7]")
LTR_TOKEN_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_.:/@#-]*\b")
ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
DDMMYYYY_SLASH_RE = re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b")
NUMBER_RE = re.compile(r"(?<![\w])(?:₪\s*)?\d[\d,]*(?:\.\d+)?%?")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PROTECTED_RE = re.compile(r"https?://\S+|www\.\S+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")

ISRAEL_REFERENCE_FACTS: dict[str, str] = {
    "access_date": "03/06/2026",
    "vat_rate_percent": "18",
    "vat_effective_date": "01/01/2025",
    "invoice_allocation_threshold_before_vat": "5,000 ₪",
    "invoice_allocation_threshold_effective_date": "01/06/2026",
    "invoice_allocation_scope_note": "For tax invoices above the legal threshold before VAT; verify against the Tax Authority before relying on the value.",
}


class Direction(str, Enum):
    """Supported translation directions."""

    AUTO = "auto"
    EN_TO_HE = "en-to-he"
    HE_TO_EN = "he-to-en"


class Register(str, Enum):
    """Supported writing registers."""

    FORMAL = "formal"
    BUSINESS = "business"
    CASUAL = "casual"
    SUPPORT = "support"
    LEGAL = "legal"
    ACCOUNTING = "accounting"


class Environment(str, Enum):
    """Storage and execution environment label."""

    SANDBOX = "sandbox"
    PRODUCTION = "production"


class HelperError(ValueError):
    """Structured helper error with a stable code."""

    code: str
    message: str

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class TranslationRequest:
    """Translation request accepted by the helper."""

    text: str
    direction: Direction = Direction.AUTO
    register: Register = Register.BUSINESS
    audience: str | None = None
    industry: str | None = None
    preserve_terms: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class TranslationResult:
    """Translation result with notes and validation metadata."""

    source_text: str
    translation: str
    direction: Direction
    register: Register
    notes: list[str]
    detected_terms: dict[str, str]
    warnings: list[str]
    quality_checks: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""

        data = asdict(self)
        data["direction"] = self.direction.value
        data["register"] = self.register.value
        return data

    def to_json(self, *, ensure_ascii: bool = False, indent: int | None = 2) -> str:
        """Return a JSON string."""

        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


@dataclass(frozen=True)
class StoredTranslation:
    """Stored translation job generated through the helper."""

    id: str
    environment: Environment
    request: TranslationRequest
    result: TranslationResult
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""

        return {
            "id": self.id,
            "environment": self.environment.value,
            "created_at": self.created_at,
            "request": {
                "text": self.request.text,
                "direction": self.request.direction.value,
                "register": self.request.register.value,
                "audience": self.request.audience,
                "industry": self.request.industry,
                "preserve_terms": list(self.request.preserve_terms),
            },
            "result": self.result.to_dict(),
        }

    def to_json(self, *, ensure_ascii: bool = False, indent: int | None = 2) -> str:
        """Return a JSON string."""

        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


EN_TO_HE_TERMS: dict[str, str] = {
    "tax invoice/receipt": "חשבונית מס/קבלה",
    "invoice-receipt": "חשבונית מס/קבלה",
    "tax invoice": "חשבונית מס",
    "invoice": "חשבונית",
    "receipt": "קבלה",
    "quote": "הצעת מחיר",
    "estimate": "הצעת מחיר",
    "proposal": "הצעה",
    "purchase order": "הזמנת רכש",
    "vat included": "כולל מע״מ",
    "plus vat": "בתוספת מע״מ",
    "vat": "מע״מ",
    "exempt dealer": "עוסק פטור",
    "licensed dealer": "עוסק מורשה",
    "vat-registered dealer": "עוסק מורשה",
    "private company limited": "חברה בע״מ",
    "withholding tax approval": "אישור ניכוי מס במקור",
    "withholding tax": "ניכוי מס במקור",
    "bookkeeping": "הנהלת חשבונות",
    "income tax": "מס הכנסה",
    "bank transfer": "העברה בנקאית",
    "credit card": "כרטיס אשראי",
    "direct debit": "הוראת קבע",
    "payment confirmation": "אישור תשלום",
    "payment method": "אמצעי תשלום",
    "order number": "מספר הזמנה",
    "cancellation fee": "דמי ביטול",
    "refund": "החזר כספי",
    "warranty": "אחריות",
    "delivery": "משלוח",
    "shipping": "משלוח",
    "self pickup": "איסוף עצמי",
    "pickup": "איסוף עצמי",
    "business days": "ימי עסקים",
    "business day": "יום עסקים",
    "privacy policy": "מדיניות פרטיות",
    "terms of use": "תנאי שימוש",
    "terms and conditions": "תנאים והגבלות",
    "accessibility statement": "הצהרת נגישות",
    "power of attorney": "ייפוי כוח",
    "lease agreement": "הסכם שכירות",
    "promissory note": "שטר חוב",
    "add to cart": "הוספה לסל",
    "checkout": "תשלום",
    "order summary": "סיכום הזמנה",
    "coupon code": "קוד קופון",
    "personal information": "מידע אישי",
    "service providers": "ספקי שירות",
    "data subject": "נושא מידע",
    "database registration": "רישום מאגר מידע",
}

HE_TO_EN_TERMS: dict[str, str] = {
    "חשבונית מס/קבלה": "tax invoice/receipt",
    "חשבונית מס": "tax invoice",
    "חשבונית": "invoice",
    "קבלה": "receipt",
    "הצעת מחיר": "quote",
    "הזמנת רכש": "purchase order",
    "כולל מע״מ": "VAT included",
    "כולל מע\"מ": "VAT included",
    "בתוספת מע״מ": "plus VAT",
    "בתוספת מע\"מ": "plus VAT",
    "מע״מ": "VAT",
    "מע\"מ": "VAT",
    "עוסק פטור": "exempt dealer",
    "עוסק מורשה": "licensed dealer",
    "חברה בע״מ": "private company limited",
    "חברה בע\"מ": "private company limited",
    "אישור ניכוי מס במקור": "withholding tax approval",
    "ניכוי מס במקור": "withholding tax",
    "הנהלת חשבונות": "bookkeeping",
    "מס הכנסה": "income tax",
    "העברה בנקאית": "bank transfer",
    "כרטיס אשראי": "credit card",
    "הוראת קבע": "direct debit",
    "אישור תשלום": "payment confirmation",
    "אמצעי תשלום": "payment method",
    "מספר הזמנה": "order number",
    "דמי ביטול": "cancellation fee",
    "החזר כספי": "refund",
    "אחריות": "warranty",
    "משלוח": "delivery",
    "איסוף עצמי": "self pickup",
    "ימי עסקים": "business days",
    "יום עסקים": "business day",
    "מדיניות פרטיות": "privacy policy",
    "תנאי שימוש": "terms of use",
    "תנאים והגבלות": "terms and conditions",
    "הצהרת נגישות": "accessibility statement",
    "ייפוי כוח": "power of attorney",
    "יפוי כוח": "power of attorney",
    "הסכם שכירות": "lease agreement",
    "שטר חוב": "promissory note",
    "הוספה לסל": "add to cart",
    "תשלום": "checkout",
    "סיכום הזמנה": "order summary",
    "קוד קופון": "coupon code",
    "מידע אישי": "personal information",
    "ספקי שירות": "service providers",
    "נושא מידע": "data subject",
    "רישום מאגר מידע": "database registration",
}

IDIOMS_HE_TO_EN: dict[str, dict[Register, str] | str] = {
    "סבבה": {
        Register.CASUAL: "Sounds good",
        Register.BUSINESS: "No problem",
        Register.SUPPORT: "No problem",
        Register.FORMAL: "Understood",
        Register.LEGAL: "Acknowledged",
        Register.ACCOUNTING: "Acknowledged",
    },
    "על הפנים": "very poor",
    "בראש טוב": "in a positive spirit",
    "בשורה התחתונה": "bottom line",
    "אין דברים כאלה": "exceptional",
    "חבל על הזמן": "excellent",
    "לא שווה להתעסק": "not worth the time",
    "עושה שכל": "makes sense",
    "תכלס": "in practice",
    "לסגור פינה": "take care of the remaining item",
    "על הדרך": "while handling it",
}

REGISTER_NOTES: dict[Register, str] = {
    Register.FORMAL: "Use restrained, respectful wording and avoid slang.",
    Register.BUSINESS: "Use concise commercial wording suitable for clients and suppliers.",
    Register.CASUAL: "Use natural conversational wording without becoming sloppy.",
    Register.SUPPORT: "Acknowledge the issue, explain the next step, and avoid blame.",
    Register.LEGAL: "Preserve legal effect and flag terms requiring professional review.",
    Register.ACCOUNTING: "Preserve accounting terms, amounts, dates, VAT references, and document type.",
}


def get_reference_facts() -> dict[str, str]:
    """Return source-sensitive Israeli reference facts verified for this release."""

    return dict(ISRAEL_REFERENCE_FACTS)

def _coerce_direction(value: Direction | str) -> Direction:
    try:
        return value if isinstance(value, Direction) else Direction(value)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in Direction)
        raise HelperError("INVALID_DIRECTION", f"Direction must be one of: {allowed}") from exc


def _coerce_register(value: Register | str) -> Register:
    try:
        return value if isinstance(value, Register) else Register(value)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in Register)
        raise HelperError("INVALID_REGISTER", f"Register must be one of: {allowed}") from exc


def _coerce_environment(value: Environment | str) -> Environment:
    try:
        return value if isinstance(value, Environment) else Environment(value)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in Environment)
        raise HelperError("INVALID_ENVIRONMENT", f"Environment must be one of: {allowed}") from exc


def detect_direction(text: str) -> Direction:
    """Detect the dominant translation direction."""

    stripped = text.strip()
    if not stripped:
        raise HelperError("EMPTY_TEXT", "Text must not be empty.")
    hebrew_chars = len(HEBREW_RE.findall(stripped))
    latin_chars = len(re.findall(r"[A-Za-z]", stripped))
    if hebrew_chars == 0:
        return Direction.EN_TO_HE
    if latin_chars == 0:
        return Direction.HE_TO_EN
    return Direction.HE_TO_EN if hebrew_chars >= latin_chars else Direction.EN_TO_HE


def contains_nikud(text: str) -> bool:
    """Return True when Hebrew vowel marks or cantillation marks are present."""

    return bool(NIKUD_RE.search(text))


def localize_date(value: str | date | datetime) -> str:
    """Convert a date to Israeli DD/MM/YYYY format."""

    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    if DDMMYYYY_SLASH_RE.fullmatch(value):
        return value
    match = ISO_DATE_RE.fullmatch(value)
    if match:
        year, month, day = match.groups()
        return f"{day}/{month}/{year}"
    raise HelperError("DATE_PARSE", "Date must be YYYY-MM-DD or DD/MM/YYYY.")


def localize_dates_in_text(text: str) -> str:
    """Convert ISO dates inside text to DD/MM/YYYY."""

    return ISO_DATE_RE.sub(lambda m: f"{m.group(3)}/{m.group(2)}/{m.group(1)}", text)


def _extract_numbers(text: str) -> list[str]:
    return NUMBER_RE.findall(text)


def _protect_segments(text: str) -> tuple[str, dict[str, str]]:
    protected: dict[str, str] = {}

    def repl(match: re.Match[str]) -> str:
        token = f"__PROTECTED_{len(protected)}__"
        protected[token] = match.group(0)
        return token

    return PROTECTED_RE.sub(repl, text), protected


def _restore_segments(text: str, protected: Mapping[str, str]) -> str:
    restored = text
    for token, value in protected.items():
        restored = restored.replace(token, value)
    return restored


def _replace_terms(text: str, mapping: Mapping[str, str]) -> tuple[str, dict[str, str]]:
    """Replace known terms while preserving URLs and email addresses."""

    working, protected = _protect_segments(text)
    detected: dict[str, str] = {}
    for source in sorted(mapping, key=len, reverse=True):
        target = mapping[source]
        if HEBREW_RE.search(source):
            pattern = re.compile(re.escape(source))
        else:
            pattern = re.compile(rf"(?<![\w/.-]){re.escape(source)}(?![\w/-])", flags=re.IGNORECASE)
        if pattern.search(working):
            working = pattern.sub(target, working)
            detected[source] = target
    return _restore_segments(working, protected), detected


def _apply_idioms(text: str, register: Register) -> tuple[str, dict[str, str]]:
    detected: dict[str, str] = {}
    updated = text
    negative_cues = ("לא שווה", "בזבוז", "מיותר", "אין טעם")
    for source, target_spec in IDIOMS_HE_TO_EN.items():
        if source not in updated:
            continue
        if source == "חבל על הזמן" and any(cue in updated for cue in negative_cues):
            target = "not worth the time"
        elif isinstance(target_spec, dict):
            target = target_spec.get(register, target_spec.get(Register.BUSINESS, source))
        else:
            target = target_spec
        detected[source] = target
        updated = updated.replace(source, target)
    return updated, detected


def _quality_checks(source: str, translation: str, direction: Direction) -> dict[str, bool]:
    source_numbers = _extract_numbers(source)
    return {
        "numbers_preserved": all(number in translation for number in source_numbers),
        "urls_preserved": all(url in translation for url in URL_RE.findall(source)),
        "emails_preserved": all(email in translation for email in EMAIL_RE.findall(source)),
        "has_hebrew_output": bool(HEBREW_RE.search(translation)) if direction == Direction.EN_TO_HE else True,
        "has_english_output": bool(re.search(r"[A-Za-z]", translation)) if direction == Direction.HE_TO_EN else True,
        "no_nikud": not contains_nikud(translation),
    }


def result_to_markdown(result: TranslationResult) -> str:
    """Render a result as concise Markdown."""

    lines = [
        "# Translation",
        "",
        result.translation,
        "",
        "## Metadata",
        f"- Direction: {result.direction.value}",
        f"- Register: {result.register.value}",
    ]
    if result.detected_terms:
        lines.extend(["", "## Detected terms"])
        lines.extend(f"- `{source}` -> `{target}`" for source, target in result.detected_terms.items())
    if result.notes:
        lines.extend(["", "## Notes"])
        lines.extend(f"- {note}" for note in result.notes)
    if result.warnings:
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    return "\n".join(lines)


class HebrewTranslationAssistant:
    """Deterministic helper for Hebrew-English translation workflows."""

    def __init__(self, *, storage_dir: str | Path | None = None) -> None:
        base = storage_dir or Path.home() / ".hebrew_translation_assistant"
        self.storage_dir = Path(base)
        self.jobs_dir = self.storage_dir / "jobs"

    def reference_facts(self) -> dict[str, str]:
        """Return source-sensitive Israeli reference facts verified for this release."""

        return get_reference_facts()

    def translate_text(
        self,
        text: str,
        *,
        direction: Direction | str = Direction.AUTO,
        register: Register | str = Register.BUSINESS,
        audience: str | None = None,
        industry: str | None = None,
        preserve_terms: Iterable[str] = (),
    ) -> TranslationResult:
        """Translate or adapt text with terminology and register support."""

        request = TranslationRequest(
            text=text,
            direction=_coerce_direction(direction),
            register=_coerce_register(register),
            audience=audience,
            industry=industry,
            preserve_terms=tuple(preserve_terms),
        )
        return self.translate_request(request)

    async def atranslate_text(self, *args: Any, **kwargs: Any) -> TranslationResult:
        """Asynchronous wrapper for translate_text."""

        await asyncio.sleep(0)
        return self.translate_text(*args, **kwargs)

    def translate_request(self, request: TranslationRequest) -> TranslationResult:
        """Translate a structured request."""

        if not request.text.strip():
            raise HelperError("EMPTY_TEXT", "Text must not be empty.")
        direction = request.direction if request.direction != Direction.AUTO else detect_direction(request.text)
        register = request.register
        notes = [REGISTER_NOTES[register]]
        warnings: list[str] = []

        source = localize_dates_in_text(request.text)
        if contains_nikud(source):
            warnings.append("Source contains nikud; remove vowel marks from technical prose unless quoted text requires them.")
        if request.audience:
            notes.append(f"Audience: {request.audience}.")
        if request.industry:
            notes.append(f"Industry context: {request.industry}.")
        if request.preserve_terms:
            notes.append("Preserved terms: " + ", ".join(request.preserve_terms) + ".")

        if direction == Direction.EN_TO_HE:
            translated, detected = _replace_terms(source, EN_TO_HE_TERMS)
            if "please" in source.lower() and "נא" not in translated:
                translated = re.sub(r"\b[Pp]lease\b", "נא", translated)
            if "₪" not in translated and "shekel" in translated.lower():
                translated = re.sub(r"\bshekels?\b", "₪", translated, flags=re.IGNORECASE)
            if not HEBREW_RE.search(translated):
                translated = f"[טיוטה עברית לפי משלב {register.value}] {translated}"
        else:
            translated, detected = _replace_terms(source, HE_TO_EN_TERMS)
            translated, idioms = _apply_idioms(translated, register)
            detected.update(idioms)

        for term in request.preserve_terms:
            if term and term not in translated:
                translated += f" {term}"

        if register == Register.ACCOUNTING:
            warnings.append("Accounting-sensitive content: verify document type, VAT treatment, withholding tax, and totals.")
        if register == Register.LEGAL:
            warnings.append("Legal-sensitive content: verify legal effect against current official sources before publication.")
        if register == Register.SUPPORT and direction == Direction.EN_TO_HE and "מצטערים" not in translated and "sorry" in source.lower():
            translated = re.sub(r"\b[Ss]orry\b", "מצטערים", translated)
        if any(word in source.lower() for word in ("privacy", "consent", "personal information")) or any(
            word in source for word in ("פרטיות", "הסכמה", "מידע אישי")
        ):
            warnings.append("Privacy-sensitive content: preserve consent, purpose, retention, and data-subject terminology.")

        checks = _quality_checks(request.text, translated, direction)
        return TranslationResult(
            source_text=request.text,
            translation=translated,
            direction=direction,
            register=register,
            notes=notes,
            detected_terms=detected,
            warnings=warnings,
            quality_checks=checks,
        )

    async def atranslate_request(self, request: TranslationRequest) -> TranslationResult:
        """Asynchronous wrapper for translate_request."""

        await asyncio.sleep(0)
        return self.translate_request(request)

    def review_text(
        self,
        text: str,
        *,
        direction: Direction | str = Direction.AUTO,
        register: Register | str = Register.BUSINESS,
    ) -> dict[str, Any]:
        """Review text and return detected risks without changing storage."""

        result = self.translate_text(text, direction=direction, register=register)
        return {
            "direction": result.direction.value,
            "register": result.register.value,
            "detected_terms": result.detected_terms,
            "warnings": result.warnings,
            "notes": result.notes,
            "quality_checks": result.quality_checks,
        }

    async def areview_text(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Asynchronous wrapper for review_text."""

        await asyncio.sleep(0)
        return self.review_text(*args, **kwargs)

    def glossary_lookup(self, term: str) -> dict[str, str]:
        """Look up a term in both glossary directions."""

        if not term.strip():
            raise HelperError("EMPTY_TERM", "Term must not be empty.")
        lowered = term.lower()
        matches: dict[str, str] = {}
        for source, target in {**EN_TO_HE_TERMS, **HE_TO_EN_TERMS}.items():
            if lowered in source.lower() or lowered in target.lower():
                matches[source] = target
        if not matches:
            raise HelperError("TERM_NOT_FOUND", "No glossary match found.")
        return matches

    async def aglossary_lookup(self, term: str) -> dict[str, str]:
        """Asynchronous wrapper for glossary_lookup."""

        await asyncio.sleep(0)
        return self.glossary_lookup(term)

    def export_glossary(self) -> dict[str, dict[str, str]]:
        """Export both glossaries."""

        return {"en_to_he": dict(EN_TO_HE_TERMS), "he_to_en": dict(HE_TO_EN_TERMS)}

    def validate_text(self, text: str) -> dict[str, bool]:
        """Return standalone validation checks for source text."""

        return {
            "not_empty": bool(text.strip()),
            "contains_hebrew": bool(HEBREW_RE.search(text)),
            "contains_latin": bool(re.search(r"[A-Za-z]", text)),
            "contains_nikud": contains_nikud(text),
            "contains_url": bool(URL_RE.search(text)),
            "contains_email": bool(EMAIL_RE.search(text)),
        }

    def create_request(
        self,
        text: str,
        *,
        direction: Direction | str = Direction.AUTO,
        register: Register | str = Register.BUSINESS,
        audience: str | None = None,
        industry: str | None = None,
        preserve_terms: Iterable[str] = (),
        environment: Environment | str = Environment.SANDBOX,
    ) -> StoredTranslation:
        """Create, translate, store, and return a local translation job."""

        env = _coerce_environment(environment)
        request = TranslationRequest(
            text=text,
            direction=_coerce_direction(direction),
            register=_coerce_register(register),
            audience=audience,
            industry=industry,
            preserve_terms=tuple(preserve_terms),
        )
        result = self.translate_request(request)
        job = StoredTranslation(
            id=str(uuid.uuid4()),
            environment=env,
            request=request,
            result=result,
            created_at=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        (self.jobs_dir / f"{job.id}.json").write_text(job.to_json(), encoding="utf-8")
        return job

    async def acreate_request(self, *args: Any, **kwargs: Any) -> StoredTranslation:
        """Asynchronous wrapper for create_request."""

        await asyncio.sleep(0)
        return self.create_request(*args, **kwargs)

    def get_request(self, request_id: str) -> dict[str, Any]:
        """Read a stored job by id."""

        if not request_id.strip():
            raise HelperError("EMPTY_ID", "Request id must not be empty.")
        path = self.jobs_dir / f"{request_id}.json"
        if not path.exists():
            raise HelperError("REQUEST_NOT_FOUND", f"No stored request found for id {request_id}.")
        return json.loads(path.read_text(encoding="utf-8"))

    def list_requests(self) -> list[dict[str, Any]]:
        """Return stored jobs sorted by creation time."""

        if not self.jobs_dir.exists():
            return []
        jobs = [json.loads(path.read_text(encoding="utf-8")) for path in self.jobs_dir.glob("*.json")]
        return sorted(jobs, key=lambda item: item.get("created_at", ""))


__all__ = [
    "Direction",
    "Register",
    "Environment",
    "HelperError",
    "TranslationRequest",
    "TranslationResult",
    "StoredTranslation",
    "HebrewTranslationAssistant",
    "contains_nikud",
    "detect_direction",
    "get_reference_facts",
    "localize_date",
    "localize_dates_in_text",
    "result_to_markdown",
]
