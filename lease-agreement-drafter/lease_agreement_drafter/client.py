from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Sequence

Environment = Literal["sandbox", "production"]
CURRENT_ISRAEL_VAT_RATE = 0.18
ISRAEL_INVOICE_THRESHOLDS_2026 = {"from_2026_01_01": 10000, "from_2026_06_01": 5000}
PropertyType = Literal["apartment", "office"]
Severity = Literal["info", "warning", "error"]


class ValidationError(ValueError):
    """Raised when input cannot be converted into a draft request."""


@dataclass(frozen=True)
class Party:
    """Contract party data used in the generated draft."""

    name: str
    id_number: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    is_business: bool = False
    vat_number: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "Party":
        return cls(
            name=str(data.get("name", "")).strip(),
            id_number=str(data.get("id_number", data.get("idNumber", ""))).strip(),
            address=str(data.get("address", "")).strip(),
            phone=str(data.get("phone", "")).strip(),
            email=str(data.get("email", "")).strip(),
            is_business=bool(data.get("is_business", data.get("isBusiness", False))),
            vat_number=str(data.get("vat_number", data.get("vatNumber", ""))).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PropertyDetails:
    """Property data for apartment or office leases."""

    property_type: PropertyType
    address: str
    city: str = ""
    block: str = ""
    parcel: str = ""
    subparcel: str = ""
    area_sqm: float | None = None
    rooms: float | None = None
    parking: bool = False
    storage: bool = False
    furnished: bool = False
    permitted_use: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "PropertyDetails":
        property_type = str(data.get("property_type", data.get("propertyType", "apartment"))).strip().lower()
        if property_type not in {"apartment", "office"}:
            raise ValidationError("property_type must be apartment or office")
        return cls(
            property_type=property_type,  # type: ignore[arg-type]
            address=str(data.get("address", "")).strip(),
            city=str(data.get("city", "")).strip(),
            block=str(data.get("block", "")).strip(),
            parcel=str(data.get("parcel", "")).strip(),
            subparcel=str(data.get("subparcel", "")).strip(),
            area_sqm=_optional_float(data.get("area_sqm", data.get("areaSqm"))),
            rooms=_optional_float(data.get("rooms")),
            parking=bool(data.get("parking", False)),
            storage=bool(data.get("storage", False)),
            furnished=bool(data.get("furnished", False)),
            permitted_use=str(data.get("permitted_use", data.get("permittedUse", ""))).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TermDetails:
    """Commercial terms and lease period."""

    start_date: str
    end_date: str
    monthly_rent_ils: float
    security_deposit_ils: float = 0
    index_linked: bool = False
    vat_applies: bool = False
    management_fee_ils: float = 0
    option_months: int = 0
    notice_days: int = 60
    payment_day: int = 1

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "TermDetails":
        return cls(
            start_date=normalize_date(str(data.get("start_date", data.get("startDate", ""))).strip()),
            end_date=normalize_date(str(data.get("end_date", data.get("endDate", ""))).strip()),
            monthly_rent_ils=float(data.get("monthly_rent_ils", data.get("monthlyRentIls", 0)) or 0),
            security_deposit_ils=float(data.get("security_deposit_ils", data.get("securityDepositIls", 0)) or 0),
            index_linked=bool(data.get("index_linked", data.get("indexLinked", False))),
            vat_applies=bool(data.get("vat_applies", data.get("vatApplies", False))),
            management_fee_ils=float(data.get("management_fee_ils", data.get("managementFeeIls", 0)) or 0),
            option_months=int(data.get("option_months", data.get("optionMonths", 0)) or 0),
            notice_days=int(data.get("notice_days", data.get("noticeDays", 60)) or 60),
            payment_day=int(data.get("payment_day", data.get("paymentDay", 1)) or 1),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DraftRequest:
    """Structured request for generating a lease draft."""

    landlord: Party
    tenant: Party
    property: PropertyDetails
    terms: TermDetails
    language: Literal["he", "en"] = "he"
    special_conditions: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    include_guarantors: bool = False
    guarantors: list[Party] = field(default_factory=list)
    consumer_context: bool = False

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "DraftRequest":
        return cls(
            landlord=Party.from_mapping(_require_mapping(data, "landlord")),
            tenant=Party.from_mapping(_require_mapping(data, "tenant")),
            property=PropertyDetails.from_mapping(_require_mapping(data, "property")),
            terms=TermDetails.from_mapping(_require_mapping(data, "terms")),
            language=str(data.get("language", "he")).lower(),  # type: ignore[arg-type]
            special_conditions=[str(x) for x in data.get("special_conditions", data.get("specialConditions", []))],
            attachments=[str(x) for x in data.get("attachments", [])],
            include_guarantors=bool(data.get("include_guarantors", data.get("includeGuarantors", False))),
            guarantors=[Party.from_mapping(x) for x in data.get("guarantors", [])],
            consumer_context=bool(data.get("consumer_context", data.get("consumerContext", False))),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "landlord": self.landlord.to_dict(),
            "tenant": self.tenant.to_dict(),
            "property": self.property.to_dict(),
            "terms": self.terms.to_dict(),
            "language": self.language,
            "special_conditions": list(self.special_conditions),
            "attachments": list(self.attachments),
            "include_guarantors": self.include_guarantors,
            "guarantors": [g.to_dict() for g in self.guarantors],
            "consumer_context": self.consumer_context,
        }


@dataclass(frozen=True)
class AuditFinding:
    """Validation finding returned by draft and template scan operations."""

    code: str
    severity: Severity
    message: str
    recommendation: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class DraftResult:
    """Draft response that can be serialized to JSON or saved as Markdown."""

    id: str
    status: Literal["drafted", "needs_review"]
    title: str
    markdown: str
    findings: list[AuditFinding]
    checklist: list[str]
    environment: Environment = "sandbox"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "title": self.title,
            "markdown": self.markdown,
            "findings": [finding.to_dict() for finding in self.findings],
            "checklist": list(self.checklist),
            "environment": self.environment,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


ERROR_CATALOG: dict[str, str] = {
    "MISSING_PARTY_NAME": "A landlord or tenant name is missing.",
    "MISSING_PROPERTY_ADDRESS": "Property address is missing.",
    "INVALID_DATE_RANGE": "Lease end date must be after start date.",
    "MISSING_RENT": "Monthly rent must be greater than zero.",
    "RESIDENTIAL_DEPOSIT_CAP": "Residential security exceeds the statutory cap that usually applies to covered apartment leases.",
    "VAT_ON_APARTMENT": "VAT was marked for an apartment lease. Residential rent for periods up to 25 years is generally VAT-exempt unless a specific exception applies.",
    "OFFICE_WITHOUT_USE": "Office permitted use is missing.",
    "NO_REPAIR_CLAUSE": "Template may lack repair timing language.",
    "NO_HANDOVER_PROTOCOL": "Template may lack a handover protocol.",
    "NO_EARLY_TERMINATION_BALANCE": "Template may allow one-sided early termination.",
}

REPAIR_TERMS = (
    "repair",
    "repairs",
    "defect",
    "urgent defect",
    "תיקון",
    "תיקונים",
    "פגם",
    "פגם דחוף",
)

HANDOVER_TERMS = (
    "handover",
    "protocol",
    "inventory",
    "מסירה",
    "פרוטוקול",
    "מצאי",
)

EARLY_TERMINATION_TERMS = (
    "early termination",
    "mutual termination",
    "סיום מוקדם",
    "הודעה מוקדמת",
    "זכות מקבילה",
)


def normalize_date(value: str) -> str:
    """Normalize DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD into DD/MM/YYYY."""

    value = value.strip()
    if not value:
        return ""
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    raise ValidationError(f"Unsupported date format: {value}. Use DD/MM/YYYY.")


def parse_local_date(value: str) -> datetime:
    normalized = normalize_date(value)
    return datetime.strptime(normalized, "%d/%m/%Y")


def months_between(start: str, end: str) -> float:
    start_dt = parse_local_date(start)
    end_dt = parse_local_date(end)
    days = (end_dt - start_dt).days
    return max(days / 30.4375, 0)


def covered_residential_lease(request: DraftRequest) -> bool:
    """Return whether common Fair Rent Law amendment checks should be applied."""

    if request.property.property_type != "apartment":
        return False
    months = months_between(request.terms.start_date, request.terms.end_date)
    return 3 < months <= 120 and request.terms.monthly_rent_ils <= 20000


def residential_deposit_cap(request: DraftRequest) -> float:
    """Calculate the common residential guarantee cap: lower of one third of total rent or three months rent."""

    months = months_between(request.terms.start_date, request.terms.end_date)
    total_rent = request.terms.monthly_rent_ils * months
    return round(min(total_rent / 3, request.terms.monthly_rent_ils * 3), 2)


def build_request(data: Mapping[str, Any] | DraftRequest) -> DraftRequest:
    if isinstance(data, DraftRequest):
        return data
    return DraftRequest.from_mapping(data)


def load_request_file(path: str | Path) -> DraftRequest:
    file_path = Path(path)
    data = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        raise ValidationError("request file must contain a JSON object")
    return DraftRequest.from_mapping(data)


class LeaseAgreementDrafterClient:
    """Local client for validating, drafting, scanning, and exporting Israeli lease drafts."""

    def __init__(self, api_key: str | None = None, environment: Environment = "sandbox", locale: str = "he-IL") -> None:
        if environment not in {"sandbox", "production"}:
            raise ValidationError("environment must be sandbox or production")
        self.api_key = api_key or ""
        self.environment: Environment = environment
        self.locale = locale

    @classmethod
    def from_env(cls, environment: Environment | None = None) -> "LeaseAgreementDrafterClient":
        env = environment or os.getenv("LEASE_DRAFTER_ENV", "sandbox")
        if env not in {"sandbox", "production"}:
            raise ValidationError("LEASE_DRAFTER_ENV must be sandbox or production")
        return cls(
            api_key=os.getenv("LEASE_DRAFTER_API_KEY", ""),
            environment=env,  # type: ignore[arg-type]
            locale=os.getenv("LEASE_DRAFTER_LOCALE", "he-IL"),
        )

    def validate(self, request: Mapping[str, Any] | DraftRequest) -> list[AuditFinding]:
        draft_request = build_request(request)
        findings: list[AuditFinding] = []
        if not draft_request.landlord.name:
            findings.append(AuditFinding("MISSING_PARTY_NAME", "error", ERROR_CATALOG["MISSING_PARTY_NAME"], "Add the landlord legal name."))
        if not draft_request.tenant.name:
            findings.append(AuditFinding("MISSING_PARTY_NAME", "error", ERROR_CATALOG["MISSING_PARTY_NAME"], "Add the tenant legal name."))
        if not draft_request.property.address:
            findings.append(AuditFinding("MISSING_PROPERTY_ADDRESS", "error", ERROR_CATALOG["MISSING_PROPERTY_ADDRESS"], "Add street, number, city, and registry details when available."))
        if draft_request.terms.monthly_rent_ils <= 0:
            findings.append(AuditFinding("MISSING_RENT", "error", ERROR_CATALOG["MISSING_RENT"], "Set monthly_rent_ils to a positive amount."))
        if parse_local_date(draft_request.terms.end_date) <= parse_local_date(draft_request.terms.start_date):
            findings.append(AuditFinding("INVALID_DATE_RANGE", "error", ERROR_CATALOG["INVALID_DATE_RANGE"], "Set end_date after start_date."))
        if covered_residential_lease(draft_request):
            cap = residential_deposit_cap(draft_request)
            if draft_request.terms.security_deposit_ils > cap:
                findings.append(AuditFinding(
                    "RESIDENTIAL_DEPOSIT_CAP",
                    "warning",
                    f"Security deposit is ₪{draft_request.terms.security_deposit_ils:,.0f}; common residential cap is about ₪{cap:,.0f}.",
                    "Reduce security or document a reviewed exception before signing.",
                ))
        if draft_request.property.property_type == "apartment" and draft_request.terms.vat_applies:
            findings.append(AuditFinding("VAT_ON_APARTMENT", "warning", ERROR_CATALOG["VAT_ON_APARTMENT"], "Remove VAT unless tax advice confirms a specific exception."))
        if draft_request.property.property_type == "office" and not draft_request.property.permitted_use:
            findings.append(AuditFinding("OFFICE_WITHOUT_USE", "warning", ERROR_CATALOG["OFFICE_WITHOUT_USE"], "Define the permitted business activity and any restrictions."))
        if draft_request.include_guarantors and not draft_request.guarantors:
            findings.append(AuditFinding("MISSING_GUARANTOR_DETAILS", "warning", "Guarantors were requested but no guarantor details were supplied.", "Add guarantor names and identifiers or remove the guarantee section."))
        return findings

    async def validate_async(self, request: Mapping[str, Any] | DraftRequest) -> list[AuditFinding]:
        await asyncio.sleep(0)
        return self.validate(request)

    def draft(self, request: Mapping[str, Any] | DraftRequest) -> DraftResult:
        draft_request = build_request(request)
        findings = self.validate(draft_request)
        title = self._title(draft_request)
        markdown = self._render_markdown(draft_request, findings)
        status: Literal["drafted", "needs_review"] = "needs_review" if any(f.severity == "error" for f in findings) else "drafted"
        checklist = self.production_checklist(draft_request)
        return DraftResult(
            id=self._stable_id(draft_request),
            status=status,
            title=title,
            markdown=markdown,
            findings=findings,
            checklist=checklist,
            environment=self.environment,
        )

    async def draft_async(self, request: Mapping[str, Any] | DraftRequest) -> DraftResult:
        await asyncio.sleep(0)
        return self.draft(request)

    def scan_template(self, text: str) -> list[AuditFinding]:
        findings: list[AuditFinding] = []
        lower_text = text.lower()
        if not any(term.lower() in lower_text for term in REPAIR_TERMS):
            findings.append(AuditFinding("NO_REPAIR_CLAUSE", "warning", ERROR_CATALOG["NO_REPAIR_CLAUSE"], "Add urgent and ordinary repair timing duties."))
        if not any(term.lower() in lower_text for term in HANDOVER_TERMS):
            findings.append(AuditFinding("NO_HANDOVER_PROTOCOL", "warning", ERROR_CATALOG["NO_HANDOVER_PROTOCOL"], "Attach a delivery protocol with meter readings, keys, and defects."))
        if not any(term.lower() in lower_text for term in EARLY_TERMINATION_TERMS):
            findings.append(AuditFinding("NO_EARLY_TERMINATION_BALANCE", "warning", ERROR_CATALOG["NO_EARLY_TERMINATION_BALANCE"], "Balance early termination rights for both parties."))
        return findings

    async def scan_template_async(self, text: str) -> list[AuditFinding]:
        await asyncio.sleep(0)
        return self.scan_template(text)

    def render_clause_index(self, result: DraftResult) -> list[str]:
        lines = []
        for line in result.markdown.splitlines():
            if line.startswith("## "):
                lines.append(line.replace("## ", "", 1).strip())
        return lines

    def export_markdown(self, result: DraftResult, path: str | Path) -> Path:
        output = Path(path)
        output.write_text(result.markdown, encoding="utf-8")
        return output

    def production_checklist(self, request: Mapping[str, Any] | DraftRequest) -> list[str]:
        draft_request = build_request(request)
        checklist = [
            "Verify identity numbers and signing authority.",
            "Attach registry extract or ownership authorization when available.",
            "Record meter readings and key count on handover.",
            "Confirm payment method, due date, and receipt process.",
            "Review insurance, liability, and defect disclosure before signing.",
        ]
        if draft_request.property.property_type == "apartment":
            checklist.extend([
                "Check whether Fair Rent Law amendment protections apply.",
                "Confirm the apartment is fit for residence on delivery.",
                "Keep residential guarantee within the lower of statutory cap and negotiated risk.",
            ])
        else:
            checklist.extend([
                "Confirm VAT treatment and tax invoice obligations.",
                "Confirm municipal tax, management fee, signage, and business license allocation.",
                "Confirm accessibility and permitted use restrictions.",
            ])
        return checklist

    def current_vat_rate(self) -> float:
        """Return the verified standard Israeli VAT rate used for 2026 drafting warnings."""
        return CURRENT_ISRAEL_VAT_RATE

    def invoice_allocation_thresholds(self) -> dict[str, int]:
        """Return 2026 Israel Invoice allocation-number thresholds in new shekels."""
        return dict(ISRAEL_INVOICE_THRESHOLDS_2026)

    def request_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "required": ["landlord", "tenant", "property", "terms"],
            "properties": {
                "landlord": {"type": "object", "required": ["name"]},
                "tenant": {"type": "object", "required": ["name"]},
                "property": {"type": "object", "required": ["property_type", "address"]},
                "terms": {"type": "object", "required": ["start_date", "end_date", "monthly_rent_ils"]},
            },
            "date_format": "DD/MM/YYYY",
            "currency": "ILS",
        }

    def error_catalog(self) -> dict[str, str]:
        return dict(ERROR_CATALOG)

    def _title(self, request: DraftRequest) -> str:
        label = "Apartment Lease" if request.property.property_type == "apartment" else "Office Lease"
        return f"{label}: {request.property.address}"

    def _stable_id(self, request: DraftRequest) -> str:
        payload = json.dumps(request.to_dict(), ensure_ascii=False, sort_keys=True)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
        return f"lease_{digest}"

    def _render_markdown(self, request: DraftRequest, findings: Sequence[AuditFinding]) -> str:
        if request.language == "en":
            return self._render_english(request, findings)
        return self._render_hebrew(request, findings)

    def _render_hebrew(self, request: DraftRequest, findings: Sequence[AuditFinding]) -> str:
        property_label = "דירה" if request.property.property_type == "apartment" else "משרד"
        vat_line = "בתוספת מע\"מ בשיעור 18% לפי הדין החל" if request.terms.vat_applies else "ללא מע\"מ אלא אם דין מחייב אחרת"
        usage = request.property.permitted_use or ("מגורים בלבד" if request.property.property_type == "apartment" else "שימוש משרדי כמוסכם בכתב")
        extras = "\n".join(f"- {condition}" for condition in request.special_conditions) or "- אין תנאים מיוחדים מעבר לאמור בטיוטה זו."
        finding_lines = "\n".join(f"- {f.code}: {f.message}" for f in findings) or "- לא נמצאו כשלים מבניים בבדיקה הראשונית."
        return f"""# טיוטת הסכם שכירות - {property_label}

מסמך זה הוא טיוטה תפעולית לבדיקה מקצועית לפני חתימה. ודא התאמה לדין העדכני ולנסיבות העסקה.

## צדדים

משכיר: {request.landlord.name}, מספר מזהה {request.landlord.id_number or "לא נמסר"}, כתובת {request.landlord.address or "לא נמסרה"}.

שוכר: {request.tenant.name}, מספר מזהה {request.tenant.id_number or "לא נמסר"}, כתובת {request.tenant.address or "לא נמסרה"}.

## המושכר

סוג נכס: {property_label}.

כתובת: {request.property.address}, {request.property.city}.

גוש: {request.property.block or "לא נמסר"}; חלקה: {request.property.parcel or "לא נמסרה"}; תת חלקה: {request.property.subparcel or "לא נמסרה"}.

שטח: {request.property.area_sqm or "לא נמסר"} מ\"ר. שימוש מותר: {usage}.

## תקופת השכירות

תחילת תקופה: {request.terms.start_date}. סיום תקופה: {request.terms.end_date}.

אופציה: {request.terms.option_months} חודשים, כפופה למסירת הודעה מוקדמת של {request.terms.notice_days} ימים ולכך שלא קיימת הפרה יסודית.

## דמי שכירות ותשלומים

דמי השכירות החודשיים: ₪{request.terms.monthly_rent_ils:,.0f}, לתשלום עד יום {request.terms.payment_day} בכל חודש, {vat_line}.

דמי ניהול חודשיים, אם חלים: ₪{request.terms.management_fee_ils:,.0f}.

הצמדה למדד: {"חלה לפי מנגנון מפורט בנספח התשלומים" if request.terms.index_linked else "לא חלה אלא אם נוסף נספח חתום"}.

## בטוחות

סכום בטוחה מוסכם: ₪{request.terms.security_deposit_ils:,.0f}. הפעל בטוחה רק בשל חוב מוכח, נזק שאינו בלאי סביר, או הפרה שלא תוקנה לאחר הודעה בכתב. בהשכרת דירה שחלים עליה תיקוני חוק השכירות, בדוק את תקרת הבטוחות לפני חתימה.

## מצב המושכר ותיקונים

מסור את המושכר כשהוא מתאים לשימוש המוסכם, נקי, בטוח ותקין. ערוך פרוטוקול מסירה הכולל תמונות, מוני מים וחשמל, מספר מפתחות, ציוד, ליקויים ידועים ומועדי תיקון. תקן פגם דחוף בתוך זמן קצר וללא דיחוי; תקן פגם רגיל בתוך פרק זמן סביר ובהתאם לדין החל.

## שימוש, ביטוח ואחריות

השתמש במושכר רק למטרה המותרת. אל תבצע שינוי מבני, העברת זכויות, שכירות משנה או הצבת שילוט ללא הסכמה בכתב. החזק ביטוח מתאים לפי אופי השימוש, והימנע מהטלת אחריות על צד שאינה תואמת דין קוגנטי.

## סיום מוקדם והפרות

קבע זכות סיום מוקדם רק אם היא הדדית או מאוזנת כנדרש. שלח הודעה בכתב לפני מימוש בטוחה, ביטול או פינוי, למעט מקרה שבו הדין מאפשר פעולה מיידית. שמור אסמכתאות לכל תשלום, הודעה ותיקון.

## תנאים מיוחדים

{extras}

## ממצאי בדיקה

{finding_lines}

## נספחים נדרשים

- צילום תעודות מזהות או אישורי מורשי חתימה.
- נספח תשלומים ובטוחות.
- פרוטוקול מסירה ומצאי.
- אישור בעלות או הרשאה להשכרה כאשר הדבר רלוונטי.
"""

    def _render_english(self, request: DraftRequest, findings: Sequence[AuditFinding]) -> str:
        property_label = "apartment" if request.property.property_type == "apartment" else "office"
        vat_line = "plus VAT at 18% under current Israeli law" if request.terms.vat_applies else "without VAT unless law requires otherwise"
        usage = request.property.permitted_use or ("residential use only" if request.property.property_type == "apartment" else "office use as agreed in writing")
        extras = "\n".join(f"- {condition}" for condition in request.special_conditions) or "- No special conditions beyond this draft."
        finding_lines = "\n".join(f"- {f.code}: {f.message}" for f in findings) or "- No structural issues found in the initial check."
        return f"""# Draft Lease Agreement - {property_label.title()}

Use this operational draft for professional review before signature. Verify current law and deal facts before execution.

## Parties

Landlord: {request.landlord.name}, identifier {request.landlord.id_number or "not provided"}, address {request.landlord.address or "not provided"}.

Tenant: {request.tenant.name}, identifier {request.tenant.id_number or "not provided"}, address {request.tenant.address or "not provided"}.

## Premises

Property type: {property_label}.

Address: {request.property.address}, {request.property.city}.

Block: {request.property.block or "not provided"}; parcel: {request.property.parcel or "not provided"}; subparcel: {request.property.subparcel or "not provided"}.

Area: {request.property.area_sqm or "not provided"} sqm. Permitted use: {usage}.

## Lease Term

Start date: {request.terms.start_date}. End date: {request.terms.end_date}.

Option: {request.terms.option_months} months, subject to {request.terms.notice_days} days prior notice and no uncured material breach.

## Rent and Payments

Monthly rent: ₪{request.terms.monthly_rent_ils:,.0f}, payable by day {request.terms.payment_day} of each month, {vat_line}.

Monthly management fee, if applicable: ₪{request.terms.management_fee_ils:,.0f}.

Index linkage: {"applies under a detailed payment appendix" if request.terms.index_linked else "does not apply unless added in a signed appendix"}.

## Security

Agreed security amount: ₪{request.terms.security_deposit_ils:,.0f}. Enforce security only for proven debt, damage beyond reasonable wear, or an uncured breach after written notice. For covered residential apartment leases, check the statutory security cap before signature.

## Condition and Repairs

Deliver the premises fit for the agreed use, clean, safe, and functional. Prepare a handover protocol covering photos, utility meter readings, keys, inventory, known defects, and repair dates. Fix urgent defects promptly; fix ordinary defects within a reasonable period and under applicable law.

## Use, Insurance, and Liability

Use the premises only for the permitted use. Do not make structural changes, transfer rights, sublease, or place signage without written consent. Maintain insurance suitable for the use and avoid liability allocation that conflicts with mandatory law.

## Early Termination and Breach

Set early termination rights only when mutual or legally balanced. Send written notice before enforcing security, termination, or eviction unless immediate action is legally permitted. Keep evidence for every payment, notice, and repair.

## Special Conditions

{extras}

## Review Findings

{finding_lines}

## Required Appendices

- Identity documents or corporate signing approvals.
- Payment and security appendix.
- Handover and inventory protocol.
- Ownership confirmation or authority to lease when relevant.
"""


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _require_mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, Mapping):
        raise ValidationError(f"{key} must be an object")
    return value
