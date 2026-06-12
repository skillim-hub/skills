from __future__ import annotations

import asyncio
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Literal
from uuid import uuid4

DATE_PATTERN = re.compile(r"^\d{2}[-/]\d{2}[-/]\d{4}$")
ISRAELI_ID_PATTERN = re.compile(r"\b\d{9}\b")
PHONE_PATTERN = re.compile(r"\b(05\d)[-\s]?(\d{3})[-\s]?(\d{4})\b")


class AssistantError(ValueError):
    """Base error for workflow validation."""


class ConsentMissingError(AssistantError):
    """Raised when another adult's case lacks consent."""


class CredentialDataError(AssistantError):
    """Raised when credential-like data is supplied."""


class Urgency(str, Enum):
    ROUTINE = "routine"
    SOON = "soon"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class Fulfillment(str, Enum):
    PORTAL = "portal"
    PICKUP = "pickup"
    DELIVERY = "delivery"
    DOCTOR_MESSAGE = "doctor_message"
    PHONE = "phone"
    UNKNOWN = "unknown"


class RecommendedPath(str, Enum):
    ACTIVE_PRESCRIPTION_FULFILLMENT = "active_prescription_fulfillment"
    DOCTOR_RENEWAL = "doctor_renewal"
    URGENT_ESCALATION = "urgent_escalation"
    PHARMACY_VERIFICATION = "pharmacy_verification"
    CONSENT_REQUIRED = "consent_required"
    EMERGENCY_CARE = "emergency_care"


@dataclass(slots=True)
class RenewalCase:
    kupat_cholim: str
    medication_name: str
    supply_days: int
    consent_confirmed: bool = True
    patient_alias: str = "self"
    strength_form: str | None = None
    repeats_left: int | None = None
    valid_until: str | None = None
    last_dispensed: str | None = None
    preferred_fulfillment: Fulfillment = Fulfillment.UNKNOWN
    pharmacy: str | None = None
    active_visible: bool | None = None
    needs_cold_chain: bool = False
    controlled_medication: bool = False
    travel_date: str | None = None
    symptoms_or_distress: bool = False
    notes: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.preferred_fulfillment, str):
            self.preferred_fulfillment = Fulfillment(self.preferred_fulfillment)
        if self.supply_days < 0:
            raise AssistantError("supply_days cannot be negative.")
        if self.repeats_left is not None and self.repeats_left < 0:
            raise AssistantError("repeats_left cannot be negative.")
        if not self.medication_name.strip():
            raise AssistantError("medication_name is required.")
        for field_name in ("valid_until", "last_dispensed", "travel_date"):
            value = getattr(self, field_name)
            if value is not None:
                validate_date(value, field_name)
        if self.patient_alias not in {"self", "child"} and not self.consent_confirmed:
            raise ConsentMissingError("CONSENT_MISSING: explicit consent is required.")
        detect_credential_like_data(self.notes or "")

    @property
    def valid_until_date(self) -> date | None:
        if not self.valid_until:
            return None
        return parse_date(self.valid_until)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["preferred_fulfillment"] = self.preferred_fulfillment.value
        return data


@dataclass(slots=True)
class TriageResult:
    urgency: Urgency
    recommended_path: RecommendedPath
    next_actions: list[str]
    warnings: list[str] = field(default_factory=list)
    privacy_flags: list[str] = field(default_factory=list)
    follow_up: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["urgency"] = self.urgency.value
        data["recommended_path"] = self.recommended_path.value
        return data


@dataclass(slots=True)
class MessageDraft:
    subject: str
    body: str
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PharmacyChecklist:
    questions: list[str]
    warnings: list[str]
    fallback: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_date(value: str) -> str:
    validate_date(value)
    return value.replace("/", "-")


def parse_date(value: str) -> date:
    validate_date(value)
    return datetime.strptime(normalize_date(value), "%d-%m-%Y").date()


def format_date(value: date, *, separator: Literal["-", "/"] = "-") -> str:
    return value.strftime(f"%d{separator}%m{separator}%Y")


def format_ddmmyyyy(value: date) -> str:
    return format_date(value, separator="-")


def format_israeli_date(value: date) -> str:
    return format_date(value, separator="/")


def validate_date(value: str, field_name: str = "date") -> None:
    if not DATE_PATTERN.match(value):
        raise AssistantError(f"{field_name} must use DD-MM-YYYY or DD/MM/YYYY format.")
    try:
        datetime.strptime(normalize_date_unchecked(value), "%d-%m-%Y")
    except ValueError as exc:
        raise AssistantError(f"{field_name} is not a valid calendar date.") from exc


def normalize_date_unchecked(value: str) -> str:
    return value.replace("/", "-")


def classify_urgency(
    supply_days: int,
    *,
    symptoms_or_distress: bool = False,
    holiday_or_weekend_risk: bool = False,
) -> Urgency:
    if symptoms_or_distress:
        return Urgency.EMERGENCY
    if supply_days <= 2:
        return Urgency.URGENT
    if supply_days <= 6 or holiday_or_weekend_risk:
        return Urgency.SOON
    return Urgency.ROUTINE


def is_expired(valid_until: str | None, *, today: date | None = None) -> bool:
    if not valid_until:
        return False
    return parse_date(valid_until) < (today or date.today())


def detect_credential_like_data(text: str) -> None:
    lowered = text.lower()
    markers = ("password", "passcode", "otp", "one-time code", "סיסמה", "קוד חד")
    if any(marker in lowered for marker in markers):
        raise CredentialDataError("PORTAL_CREDENTIAL_REQUESTED: do not share passwords or one-time codes.")


def mask_israeli_id(text: str) -> str:
    return ISRAELI_ID_PATTERN.sub("*********", text)


def mask_phone(text: str) -> str:
    return PHONE_PATTERN.sub(lambda m: f"{m.group(1)}-***{m.group(3)}", text)


def redact_sensitive_text(text: str, *, mask_id: bool = True, mask_phone_numbers: bool = True) -> str:
    redacted = text
    if mask_id:
        redacted = mask_israeli_id(redacted)
    if mask_phone_numbers:
        redacted = mask_phone(redacted)
    return redacted


def deduplicate(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def choose_recommended_path(case: RenewalCase, *, today: date | None = None) -> RecommendedPath:
    urgency = classify_urgency(case.supply_days, symptoms_or_distress=case.symptoms_or_distress)
    if urgency is Urgency.EMERGENCY:
        return RecommendedPath.EMERGENCY_CARE
    if case.patient_alias not in {"self", "child"} and not case.consent_confirmed:
        return RecommendedPath.CONSENT_REQUIRED
    renewal_blocked = case.active_visible is False or case.repeats_left == 0 or is_expired(case.valid_until, today=today)
    if urgency is Urgency.URGENT and renewal_blocked:
        return RecommendedPath.URGENT_ESCALATION
    if renewal_blocked:
        return RecommendedPath.DOCTOR_RENEWAL
    if case.preferred_fulfillment in {Fulfillment.DELIVERY, Fulfillment.PICKUP, Fulfillment.PORTAL}:
        return RecommendedPath.PHARMACY_VERIFICATION
    return RecommendedPath.ACTIVE_PRESCRIPTION_FULFILLMENT


def triage_case(
    case: RenewalCase,
    *,
    today: date | None = None,
    holiday_or_weekend_risk: bool = False,
) -> TriageResult:
    urgency = classify_urgency(
        case.supply_days,
        symptoms_or_distress=case.symptoms_or_distress,
        holiday_or_weekend_risk=holiday_or_weekend_risk,
    )
    path = choose_recommended_path(case, today=today)
    warnings: list[str] = []
    privacy_flags: list[str] = []
    actions: list[str] = []

    if case.patient_alias != "self":
        privacy_flags.append("another_person_data")
        actions.append("Confirm consent or official authority before handling details.")

    if case.active_visible is False:
        warnings.append("Prescription is not visible as active.")
        actions.append("Verify the correct profile and request renewal.")

    if case.repeats_left == 0:
        warnings.append("No repeats remain.")
        actions.append("Send a doctor or clinic renewal request.")

    if is_expired(case.valid_until, today=today):
        warnings.append("Prescription validity appears expired.")
        actions.append("Request reissue or renewal from the doctor or clinic.")

    if case.needs_cold_chain:
        warnings.append("Confirm refrigerated handling before delivery.")
        actions.append("Ask about cold-chain packaging, handoff, and failed-delivery policy.")

    if case.controlled_medication:
        warnings.append("Follow official rules for controlled or restricted medication.")
        actions.append("Confirm identification, pickup, and delivery rules with official support.")

    if urgency is Urgency.EMERGENCY:
        actions.insert(0, "Seek immediate clinical or emergency care if symptoms or distress are present.")
    elif urgency is Urgency.URGENT:
        actions.insert(0, "Use urgent channels: call the clinic, HMO hotline, pharmacist, or urgent care.")
    elif urgency is Urgency.SOON:
        actions.insert(0, "Submit the request today and set follow-up for the next business day.")
    else:
        actions.insert(0, "Proceed through the normal official portal, app, or pharmacy workflow.")

    if case.preferred_fulfillment is Fulfillment.DELIVERY:
        actions.append("Confirm delivery availability, address, stock, restrictions, and total cost in ₪.")
    if case.preferred_fulfillment is Fulfillment.PICKUP:
        actions.append("Confirm branch stock, opening hours, and required identification.")
    if case.travel_date:
        actions.append(f"Include travel date {case.travel_date} and ask whether early dispensing is permitted.")

    actions.append("Record confirmation number, expected date, and next refill planning date.")
    follow_up = "next business day" if urgency in {Urgency.SOON, Urgency.URGENT} else "within 2 business days"

    return TriageResult(
        urgency=urgency,
        recommended_path=path,
        next_actions=deduplicate(actions),
        warnings=deduplicate(warnings),
        privacy_flags=deduplicate(privacy_flags),
        follow_up=follow_up,
    )


def infer_reason(case: RenewalCase) -> str:
    if case.repeats_left == 0:
        return "no repeats left"
    if case.valid_until and is_expired(case.valid_until):
        return "prescription expired"
    if case.active_visible is False:
        return "prescription is not visible as active"
    if case.travel_date:
        return f"refill needed before travel on {case.travel_date}"
    return "refill needed"


def build_doctor_message(
    case: RenewalCase,
    *,
    language: Literal["en", "he"] = "en",
    reason: str | None = None,
) -> MessageDraft:
    warnings = [
        "Do not include diagnosis unless the clinician requested it.",
        "Do not send portal passwords, one-time codes, payment-card details, or full ID numbers.",
    ]
    reason_text = reason or infer_reason(case)
    strength = case.strength_form or "unknown"
    last_dispensed = case.last_dispensed or "unknown"

    if language == "he":
        subject = "בקשה לחידוש מרשם"
        body = (
            "שלום,\n\n"
            "אבקש לבדוק חידוש מרשם עבור:\n"
            f"תרופה: {case.medication_name}\n"
            f"חוזק/צורת מתן: {strength}\n"
            f"ימי מלאי שנותרו: {case.supply_days}\n"
            f"תאריך ניפוק אחרון: {last_dispensed}\n"
            f"סיבת הפנייה: {reason_text}\n\n"
            "נא לעדכן האם ניתן לחדש את המרשם באופן דיגיטלי, "
            "או שנדרש תור, בדיקה, מסמך או בירור נוסף.\n\n"
            "תודה."
        )
    else:
        subject = "Prescription renewal request"
        body = (
            "Hello,\n\n"
            "Please review a prescription renewal request for:\n"
            f"Medication: {case.medication_name}\n"
            f"Strength/form: {strength}\n"
            f"Current supply remaining: {case.supply_days} days\n"
            f"Last dispensing date: {last_dispensed}\n"
            f"Reason for request: {reason_text}\n\n"
            "Please advise whether renewal can be completed digitally or whether an "
            "appointment, lab test, document, or additional review is required.\n\n"
            "Thank you."
        )
    return MessageDraft(subject=subject, body=body, warnings=warnings)


def pharmacy_checklist(
    *,
    pharmacy: str | None = None,
    fulfillment: Fulfillment = Fulfillment.UNKNOWN,
    needs_cold_chain: bool = False,
    controlled_medication: bool = False,
    price_check: bool = True,
) -> PharmacyChecklist:
    label = pharmacy or "the pharmacy"
    questions = [
        f"Can {label} see the active digital prescription?",
        "Is the medication in stock at the dispensing branch?",
        "What identification or authorization is required?",
    ]
    warnings: list[str] = []

    if fulfillment is Fulfillment.DELIVERY:
        questions.extend(
            [
                "Is prescription-medication delivery available for the address?",
                "What is the earliest delivery window?",
                "What happens if delivery fails?",
            ]
        )
    if fulfillment is Fulfillment.PICKUP:
        questions.extend(["What are branch opening hours?", "Can stock be reserved until pickup?"])
    if needs_cold_chain:
        questions.extend(
            [
                "How is refrigeration maintained until handoff?",
                "Is direct handoff required?",
                "How long may the package remain outside refrigeration?",
            ]
        )
        warnings.append("Do not proceed until cold-chain handling is confirmed.")
    if controlled_medication:
        questions.append("Are there special legal, identification, pickup, or delivery restrictions?")
        warnings.append("Use official instructions only for controlled or restricted medicines.")
    if price_check:
        questions.extend(
            [
                "What is the total price in ₪?",
                "Was the Kupat Cholim discount applied?",
                "Is generic substitution available and allowed?",
            ]
        )

    fallback = "Use pickup or another licensed pharmacy if delivery is unavailable or too slow." if fulfillment is Fulfillment.DELIVERY else None
    return PharmacyChecklist(questions=deduplicate(questions), warnings=deduplicate(warnings), fallback=fallback)


def expense_record(
    *,
    vendor: str,
    amount_nis: float,
    paid_on: str,
    category: str = "medical/pharmacy expense",
) -> dict[str, Any]:
    validate_date(paid_on, "paid_on")
    if amount_nis < 0:
        raise AssistantError("amount_nis cannot be negative.")
    return {
        "date": paid_on,
        "vendor": vendor,
        "amount": f"₪{amount_nis:,.2f}",
        "category": category,
        "contains_medical_detail": False,
    }


def generate_case_id(*, today: date | None = None) -> str:
    current = today or date.today()
    return f"RX-{current:%Y%m%d}-{uuid4().hex[:8].upper()}"


def save_case_json(case: RenewalCase, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(case.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def load_case_json(path: str | Path) -> RenewalCase:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data.get("preferred_fulfillment"), str):
        data["preferred_fulfillment"] = Fulfillment(data["preferred_fulfillment"])
    return RenewalCase(**data)


def store_case(case: RenewalCase, *, store_path: str | Path, case_id: str | None = None) -> str:
    target = Path(store_path)
    if target.exists():
        store = json.loads(target.read_text(encoding="utf-8"))
    else:
        store = {}
    identifier = case_id or generate_case_id()
    store[identifier] = case.to_dict()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")
    return identifier


def load_case_from_store(case_id: str, *, store_path: str | Path) -> RenewalCase:
    target = Path(store_path)
    store = json.loads(target.read_text(encoding="utf-8"))
    if case_id not in store:
        raise AssistantError(f"case_id not found: {case_id}")
    return RenewalCase(**store[case_id])


class PrescriptionRenewalClient:
    """Synchronous helper for prescription-renewal workflow planning."""

    def triage(self, case: RenewalCase, *, today: date | None = None) -> TriageResult:
        return triage_case(case, today=today)

    def doctor_message(self, case: RenewalCase, *, language: Literal["en", "he"] = "en") -> MessageDraft:
        return build_doctor_message(case, language=language)

    def pharmacy_questions(
        self,
        *,
        pharmacy: str | None = None,
        fulfillment: Fulfillment = Fulfillment.UNKNOWN,
        needs_cold_chain: bool = False,
        controlled_medication: bool = False,
    ) -> PharmacyChecklist:
        return pharmacy_checklist(
            pharmacy=pharmacy,
            fulfillment=fulfillment,
            needs_cold_chain=needs_cold_chain,
            controlled_medication=controlled_medication,
        )

    def redact(self, text: str) -> str:
        return redact_sensitive_text(text)

    def create_case(self, case: RenewalCase, *, store_path: str | Path, case_id: str | None = None) -> str:
        return store_case(case, store_path=store_path, case_id=case_id)

    def load_case(self, case_id: str, *, store_path: str | Path) -> RenewalCase:
        return load_case_from_store(case_id, store_path=store_path)


class AsyncPrescriptionRenewalClient:
    """Async helper for prescription-renewal workflow planning."""

    async def triage(self, case: RenewalCase, *, today: date | None = None) -> TriageResult:
        await asyncio.sleep(0)
        return triage_case(case, today=today)

    async def doctor_message(self, case: RenewalCase, *, language: Literal["en", "he"] = "en") -> MessageDraft:
        await asyncio.sleep(0)
        return build_doctor_message(case, language=language)

    async def pharmacy_questions(
        self,
        *,
        pharmacy: str | None = None,
        fulfillment: Fulfillment = Fulfillment.UNKNOWN,
        needs_cold_chain: bool = False,
        controlled_medication: bool = False,
    ) -> PharmacyChecklist:
        await asyncio.sleep(0)
        return pharmacy_checklist(
            pharmacy=pharmacy,
            fulfillment=fulfillment,
            needs_cold_chain=needs_cold_chain,
            controlled_medication=controlled_medication,
        )

    async def redact(self, text: str) -> str:
        await asyncio.sleep(0)
        return redact_sensitive_text(text)
