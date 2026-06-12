#!/usr/bin/env python3
"""Typed helper for Israeli contract drafting workflows."""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

Language = Literal["he", "en"]
Severity = Literal["info", "low", "medium", "high"]
DEFAULT_VAT_RATE = 0.18  # Israeli standard VAT rate validated against official sources on 02/06/2026.


class ContractType(str, Enum):
    SERVICE_AGREEMENT = "service_agreement"
    FREELANCE_AGREEMENT = "freelance_agreement"
    CONSUMER_SERVICE = "consumer_service"
    NDA = "nda"
    SALE_OF_GOODS = "sale_of_goods"
    SUPPLY_AGREEMENT = "supply_agreement"
    WEBSITE_TERMS = "website_terms"
    IP_LICENSE = "ip_license"
    SETTLEMENT = "settlement"


@dataclass(slots=True)
class Party:
    name: str
    kind: str = "individual"
    id_number: str | None = None
    address: str | None = None
    contact_email: str | None = None
    role: str = "party"
    signatory_name: str | None = None
    signatory_title: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Party":
        return cls(
            name=str(data.get("name", "")).strip(),
            kind=str(data.get("kind", "individual")).strip() or "individual",
            id_number=_none_if_blank(data.get("id_number")),
            address=_none_if_blank(data.get("address")),
            contact_email=_none_if_blank(data.get("contact_email")),
            role=str(data.get("role", "party")).strip() or "party",
            signatory_name=_none_if_blank(data.get("signatory_name")),
            signatory_title=_none_if_blank(data.get("signatory_title")),
        )

    def id_label(self, language: Language = "he") -> str:
        lower_kind = self.kind.lower()
        if language == "he":
            if "company" in lower_kind or "חברה" in lower_kind:
                return "ח.פ."
            if "sole" in lower_kind or "עוסק" in lower_kind:
                return "ע.מ."
            if "nonprofit" in lower_kind or "עמותה" in lower_kind:
                return "מספר עמותה"
            return "ת.ז."
        if "company" in lower_kind:
            return "Company No."
        if "sole" in lower_kind:
            return "Business No."
        if "nonprofit" in lower_kind:
            return "Nonprofit No."
        return "ID No."

    def display(self, language: Language = "he") -> str:
        identifier = f", {self.id_label(language)} {self.id_number}" if self.id_number else ""
        address = f", {self.address}" if self.address else ""
        return f"{self.name}{identifier}{address}"


@dataclass(slots=True)
class ContractTerms:
    contract_type: ContractType = ContractType.SERVICE_AGREEMENT
    language: Language = "he"
    title: str | None = None
    date_text: str | None = None
    effective_date: str | None = None
    city: str | None = None
    parties: list[Party] = field(default_factory=list)
    description: str | None = None
    deliverables: list[str] = field(default_factory=list)
    exclusions: list[str] = field(default_factory=list)
    price_nis: float | None = None
    vat_included: bool | None = None
    vat_rate: float = DEFAULT_VAT_RATE
    payment_terms: str | None = None
    late_payment: str | None = None
    expenses: str | None = None
    term: str | None = None
    termination_notice_days: int | None = None
    cure_period_days: int | None = 14
    confidentiality: bool = True
    personal_data: bool = False
    sensitive_data: bool = False
    ip_ownership: str | None = None
    liability_cap_nis: float | None = None
    consumer_deal: bool = False
    cancellation_window_days: int | None = None
    dispute_resolution: str | None = None
    venue: str | None = None
    governing_law: str = "Israel"
    notes: list[str] = field(default_factory=list)
    employment_like_facts: list[str] = field(default_factory=list)
    regulated_activity: bool = False

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ContractTerms":
        return cls(
            contract_type=ContractType(str(data.get("contract_type", ContractType.SERVICE_AGREEMENT.value))),
            language=str(data.get("language", "he")),  # type: ignore[arg-type]
            title=_none_if_blank(data.get("title")),
            date_text=_none_if_blank(data.get("date_text")),
            effective_date=_none_if_blank(data.get("effective_date")),
            city=_none_if_blank(data.get("city")),
            parties=[Party.from_dict(p) for p in data.get("parties", [])],
            description=_none_if_blank(data.get("description")),
            deliverables=[str(x) for x in data.get("deliverables", [])],
            exclusions=[str(x) for x in data.get("exclusions", [])],
            price_nis=_float_or_none(data.get("price_nis")),
            vat_included=_bool_or_none(data.get("vat_included")),
            vat_rate=float(data.get("vat_rate", DEFAULT_VAT_RATE)),
            payment_terms=_none_if_blank(data.get("payment_terms")),
            late_payment=_none_if_blank(data.get("late_payment")),
            expenses=_none_if_blank(data.get("expenses")),
            term=_none_if_blank(data.get("term")),
            termination_notice_days=_int_or_none(data.get("termination_notice_days")),
            cure_period_days=_int_or_none(data.get("cure_period_days")) or 14,
            confidentiality=bool(data.get("confidentiality", True)),
            personal_data=bool(data.get("personal_data", False)),
            sensitive_data=bool(data.get("sensitive_data", False)),
            ip_ownership=_none_if_blank(data.get("ip_ownership")),
            liability_cap_nis=_float_or_none(data.get("liability_cap_nis")),
            consumer_deal=bool(data.get("consumer_deal", False)),
            cancellation_window_days=_int_or_none(data.get("cancellation_window_days")),
            dispute_resolution=_none_if_blank(data.get("dispute_resolution")),
            venue=_none_if_blank(data.get("venue")),
            governing_law=str(data.get("governing_law", "Israel")),
            notes=[str(x) for x in data.get("notes", [])],
            employment_like_facts=[str(x) for x in data.get("employment_like_facts", [])],
            regulated_activity=bool(data.get("regulated_activity", False)),
        )


@dataclass(slots=True)
class RiskFinding:
    code: str
    severity: Severity
    message: str
    fix: str


@dataclass(slots=True)
class DraftResult:
    contract_markdown: str
    findings: list[RiskFinding]
    assumptions: list[str]
    checklist: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_markdown": self.contract_markdown,
            "findings": [asdict(f) for f in self.findings],
            "assumptions": list(self.assumptions),
            "checklist": list(self.checklist),
        }

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


class ContractDraftingClient:
    def validate(self, terms: ContractTerms) -> list[RiskFinding]:
        return scan_risks(terms)

    def draft(self, terms: ContractTerms) -> DraftResult:
        findings = scan_risks(terms)
        assumptions = build_assumptions(terms)
        checklist = production_checklist(terms)
        return DraftResult(render_contract(terms, findings=findings, assumptions=assumptions), findings, assumptions, checklist)

    async def async_validate(self, terms: ContractTerms) -> list[RiskFinding]:
        return await asyncio.to_thread(self.validate, terms)

    async def async_draft(self, terms: ContractTerms) -> DraftResult:
        return await asyncio.to_thread(self.draft, terms)

    def draft_from_json_file(self, path: str | Path) -> DraftResult:
        return self.draft(load_terms(path))

    async def async_draft_from_json_file(self, path: str | Path) -> DraftResult:
        return await asyncio.to_thread(self.draft_from_json_file, path)


def _none_if_blank(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y", "כן"}:
        return True
    if text in {"false", "0", "no", "n", "לא"}:
        return False
    return None


def format_ils(amount: float | int | None) -> str:
    if amount is None:
        return "₪[סכום]"
    value = float(amount)
    if value.is_integer():
        return f"₪{int(value):,}"
    return f"₪{value:,.2f}"


def parse_date_text(value: str | None) -> date | None:
    if not value:
        return None
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unsupported date format: {value!r}")


def format_date_ddmmyyyy(value: str | date | None) -> str:
    if value is None:
        return "[DD/MM/YYYY]"
    parsed = value if isinstance(value, date) else parse_date_text(value)
    return "[DD/MM/YYYY]" if parsed is None else parsed.strftime("%d/%m/%Y")


def normalize_israeli_id(id_number: str) -> str:
    text = re.sub(r"\s+", "", str(id_number))
    if not text.isdigit():
        raise ValueError("id_not_numeric")
    if len(text) > 9:
        raise ValueError("id_too_long")
    return text.zfill(9)


def validate_israeli_id(id_number: str) -> bool:
    normalized = normalize_israeli_id(id_number)
    total = 0
    for index, char in enumerate(normalized):
        digit = int(char)
        product = digit * (1 if index % 2 == 0 else 2)
        total += product if product <= 9 else (product // 10) + (product % 10)
    return total % 10 == 0


def calculate_vat(amount: float, rate: float = DEFAULT_VAT_RATE) -> dict[str, float]:
    if amount < 0:
        raise ValueError("amount_must_be_non_negative")
    if not 0 <= rate <= 1:
        raise ValueError("rate_must_be_between_0_and_1")
    vat = round(amount * rate, 2)
    return {"net": round(amount, 2), "vat": vat, "total": round(amount + vat, 2), "rate": rate}


def classify_risk_level(findings: Sequence[RiskFinding]) -> Severity:
    if any(f.severity == "high" for f in findings):
        return "high"
    if any(f.severity == "medium" for f in findings):
        return "medium"
    if any(f.severity == "low" for f in findings):
        return "low"
    return "info"


def has_creative_or_technical_work(terms: ContractTerms) -> bool:
    text = " ".join([terms.description or "", " ".join(terms.deliverables), terms.contract_type.value]).lower()
    keywords = ["design", "visual identity asset", "software", "code", "website", "app", "photograph", "content", "copywriting", "creative", "עיצוב", "סימן מזהה חזותי", "תוכנה", "קוד", "אתר", "אפליקציה", "צילום", "תוכן", "כתיבה"]
    return any(k in text for k in keywords)


def scan_risks(terms: ContractTerms) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    if len(terms.parties) < 2:
        findings.append(RiskFinding("missing_parties", "high", "Fewer than two parties were supplied.", "Add legal names, identifiers, addresses, and roles for all parties."))
    for party in terms.parties:
        if not party.name:
            findings.append(RiskFinding("missing_party_name", "high", "A party has no legal name.", "Insert the full legal name before signing."))
        if party.id_number and party.kind.lower() in {"individual", "person", "consumer"}:
            try:
                if not validate_israeli_id(party.id_number):
                    findings.append(RiskFinding("invalid_israeli_id", "medium", f"ID number for {party.name or 'a party'} failed checksum.", "Verify the ID number against official documents."))
            except ValueError as exc:
                findings.append(RiskFinding(str(exc), "medium", f"ID number for {party.name or 'a party'} is malformed.", "Use digits only, up to 9 digits."))
        if party.kind.lower() in {"company", "limited_company", "חברה"} and not party.signatory_title:
            findings.append(RiskFinding("signature_authority_missing", "medium", f"Company party {party.name or '[company]'} lacks a signatory title.", "Add signatory name/title and an authority representation."))
    paid_types = {ContractType.SERVICE_AGREEMENT, ContractType.FREELANCE_AGREEMENT, ContractType.CONSUMER_SERVICE, ContractType.SALE_OF_GOODS, ContractType.SUPPLY_AGREEMENT, ContractType.IP_LICENSE}
    if terms.contract_type in paid_types and terms.price_nis is None:
        findings.append(RiskFinding("missing_price", "medium", "Paid agreement has no price.", "Add a fee schedule, hourly rate, retainer, milestone price, or state that no fee applies."))
    if terms.price_nis is not None and terms.vat_included is None:
        findings.append(RiskFinding("vat_ambiguous", "medium", "Price is stated without saying whether VAT is included.", "State whether the amount includes VAT or is plus VAT at the lawful rate against lawful accounting documentation."))
    if terms.consumer_deal or terms.contract_type == ContractType.CONSUMER_SERVICE:
        findings.append(RiskFinding("consumer_cancellation_review", "medium", "Consumer-facing deal may require cancellation, disclosure, and refund review.", "Add a Consumer Protection Law review note and avoid waiving mandatory rights."))
    if terms.personal_data:
        findings.append(RiskFinding("privacy_schedule_required", "high" if terms.sensitive_data else "medium", "The transaction involves personal data.", "Add a privacy/data-security schedule covering purpose, access, security, incidents, and deletion."))
    if has_creative_or_technical_work(terms) and not terms.ip_ownership:
        findings.append(RiskFinding("ip_ownership_ambiguous", "medium", "Creative or technical deliverables are present without an IP ownership or license term.", "Specify assignment after payment, exclusive license, or non-exclusive license."))
    if terms.liability_cap_nis is None and terms.contract_type not in {ContractType.NDA, ContractType.SETTLEMENT}:
        findings.append(RiskFinding("liability_unbounded", "medium", "No liability cap was supplied.", "Add a cap tied to fees, insurance, or direct damages, with mandatory-law carve-outs."))
    if terms.employment_like_facts or _looks_employment_like(terms):
        findings.append(RiskFinding("worker_classification_risk", "high", "Facts may resemble employment rather than independent services.", "Add employment-law review and avoid using a service agreement to disguise employment."))
    if terms.regulated_activity:
        findings.append(RiskFinding("regulated_activity", "high", "The transaction appears to involve a regulated sector.", "Use specialist review for finance, medicine, insurance, credit, real estate, telecom, or similar activity."))
    if not terms.governing_law:
        findings.append(RiskFinding("jurisdiction_unclear", "low", "No governing law was supplied.", "Add an Israeli governing-law clause unless another law is intentionally selected."))
    return findings


def _looks_employment_like(terms: ContractTerms) -> bool:
    text = " ".join([terms.description or "", " ".join(terms.notes)]).lower()
    signals = ["fixed hours", "full time", "full-time", "exclusive", "manager approval", "company equipment", "שעות קבועות", "משרה מלאה", "בלעדיות", "ציוד הלקוח", "מנהל ישיר"]
    return terms.contract_type == ContractType.FREELANCE_AGREEMENT and any(s in text for s in signals)


def build_assumptions(terms: ContractTerms) -> list[str]:
    assumptions: list[str] = []
    if not terms.date_text:
        assumptions.append("Signing date is left as a placeholder.")
    if terms.price_nis is None:
        assumptions.append("Price is left as a placeholder.")
    if terms.vat_included is None:
        assumptions.append("VAT treatment must be confirmed before signing.")
    if not terms.venue:
        assumptions.append("Court venue is left for commercial/legal confirmation.")
    if terms.contract_type in {ContractType.SERVICE_AGREEMENT, ContractType.FREELANCE_AGREEMENT}:
        assumptions.append("The service provider is assumed to operate as an independent business.")
    if terms.personal_data:
        assumptions.append("A privacy/data-security schedule is required.")
    return assumptions


def production_checklist(terms: ContractTerms) -> list[str]:
    items = ["Verify legal names and identifiers.", "Confirm signatory authority.", "Confirm VAT treatment, lawful rate, and accounting-document wording.", "Confirm deliverables, exclusions, and acceptance criteria.", "Confirm termination and cure periods.", "Confirm IP ownership or license.", "Confirm liability cap and carve-outs.", "Confirm governing law and venue."]
    if terms.consumer_deal or terms.contract_type == ContractType.CONSUMER_SERVICE:
        items.append("Confirm consumer cancellation, disclosure, and refund wording.")
    if terms.personal_data:
        items.append("Confirm privacy/data-security schedule.")
    if terms.employment_like_facts:
        items.append("Obtain employment-classification review.")
    return items


def _title_for(terms: ContractTerms, language: Language) -> str:
    if terms.title:
        return terms.title
    he_titles = {ContractType.SERVICE_AGREEMENT: "הסכם למתן שירותים", ContractType.FREELANCE_AGREEMENT: "הסכם פרילנס", ContractType.CONSUMER_SERVICE: "הסכם שירות לצרכן", ContractType.NDA: "הסכם סודיות", ContractType.SALE_OF_GOODS: "הסכם מכר", ContractType.SUPPLY_AGREEMENT: "הסכם אספקה", ContractType.WEBSITE_TERMS: "תנאי שימוש", ContractType.IP_LICENSE: "הסכם רישיון קניין רוחני", ContractType.SETTLEMENT: "הסכם פשרה"}
    en_titles = {ContractType.SERVICE_AGREEMENT: "Service Agreement", ContractType.FREELANCE_AGREEMENT: "Freelance Services Agreement", ContractType.CONSUMER_SERVICE: "Consumer Service Agreement", ContractType.NDA: "Non-Disclosure Agreement", ContractType.SALE_OF_GOODS: "Sale of Goods Agreement", ContractType.SUPPLY_AGREEMENT: "Supply Agreement", ContractType.WEBSITE_TERMS: "Terms of Use", ContractType.IP_LICENSE: "Intellectual Property License Agreement", ContractType.SETTLEMENT: "Settlement Agreement"}
    return (he_titles if language == "he" else en_titles)[terms.contract_type]


def _party_lines(terms: ContractTerms, language: Language) -> list[str]:
    if not terms.parties:
        return ["[שם צד א׳], [מספר זיהוי], מכתובת [כתובת]", "[שם צד ב׳], [מספר זיהוי], מכתובת [כתובת]"] if language == "he" else ["[Party A], [ID/registration number], of [address]", "[Party B], [ID/registration number], of [address]"]
    return [p.display(language) + f" ({p.role})" for p in terms.parties]


def _vat_phrase(terms: ContractTerms, language: Language) -> str:
    if terms.vat_included is True:
        return "כולל מע״מ כדין" if language == "he" else "including VAT as required by law"
    if terms.vat_included is False:
        return "בתוספת מע״מ כדין" if language == "he" else "plus VAT as required by law"
    return "[כולל/בתוספת מע״מ]" if language == "he" else "[including/plus VAT]"


def _payment_text(terms: ContractTerms, language: Language) -> str:
    amount = format_ils(terms.price_nis)
    vat = _vat_phrase(terms, language)
    payment_terms = terms.payment_terms or ("[תנאי תשלום]" if language == "he" else "[payment terms]")
    if language == "he":
        return f"התמורה עבור השירותים תהיה {amount} {vat}. התשלום יבוצע {payment_terms} כנגד מסמך חשבונאי כדין."
    return f"The fees for the services are {amount} {vat}. Payment shall be made {payment_terms} against lawful accounting documentation."


def _deliverables_text(items: list[str], language: Language) -> str:
    if not items:
        return "- [תוצר/שירות]" if language == "he" else "- [deliverable/service]"
    return "\n".join(f"- {item}" for item in items)


def _findings_block(findings: Sequence[RiskFinding] | None, language: Language) -> str:
    if not findings:
        return ""
    if language == "he":
        lines = ["## הערות סיכון מחוץ להסכם", ""]
        for f in findings:
            lines.append(f"- **{f.severity} / {f.code}:** {f.message} תיקון מומלץ: {f.fix}")
    else:
        lines = ["## Risk notes outside the agreement", ""]
        for f in findings:
            lines.append(f"- **{f.severity} / {f.code}:** {f.message} Recommended fix: {f.fix}")
    return "\n".join(lines) + "\n\n"


def _assumptions_block(assumptions: Sequence[str] | None, language: Language) -> str:
    if not assumptions:
        return ""
    title = "## הנחות וחוסרים" if language == "he" else "## Assumptions and missing facts"
    return title + "\n\n" + "\n".join(f"- {a}" for a in assumptions) + "\n\n"


def render_contract(terms: ContractTerms, *, findings: Sequence[RiskFinding] | None = None, assumptions: Sequence[str] | None = None) -> str:
    return render_english_contract(terms, findings=findings, assumptions=assumptions) if terms.language == "en" else render_hebrew_contract(terms, findings=findings, assumptions=assumptions)


def render_hebrew_contract(terms: ContractTerms, *, findings: Sequence[RiskFinding] | None = None, assumptions: Sequence[str] | None = None) -> str:
    title = _title_for(terms, "he")
    signing_date = format_date_ddmmyyyy(terms.date_text)
    effective_date = format_date_ddmmyyyy(terms.effective_date) if terms.effective_date else "[DD/MM/YYYY]"
    parties = "\n\nלבין:\n".join(_party_lines(terms, "he"))
    description = terms.description or "[תיאור השירותים/העסקה]"
    term = terms.term or "[עד השלמת השירותים / לתקופה מוגדרת]"
    notice = terms.termination_notice_days if terms.termination_notice_days is not None else "[מספר]"
    cure = terms.cure_period_days or 14
    venue = terms.venue or "[עיר/מחוז]"
    ip = terms.ip_ownership or "הזכויות בתוצרים הסופיים יוסדרו לפי בחירה מסחרית בין הצדדים: העברה לאחר תשלום מלא או רישיון שימוש מוגדר."
    liability_cap = format_ils(terms.liability_cap_nis) if terms.liability_cap_nis else "סך התמורה ששולמה בפועל ב-12 החודשים שקדמו לאירוע"
    privacy = "נותן השירותים יעבד מידע אישי רק לצורך ביצוע ההסכם, יגביל גישה למורשים בלבד, ישמור על אמצעי אבטחה סבירים, יודיע ללקוח על אירוע אבטחה מהותי ללא דיחוי בלתי סביר, ולא יעביר מידע אישי לספק משנה ללא בסיס מתאים או אישור שנדרש לפי ההסכם." if terms.personal_data else "אם במהלך ביצוע ההסכם ייחשף צד למידע אישי, אותו צד ישתמש במידע רק לצורך ההסכם ויפעל בהתאם לדין החל."
    consumer = ""
    if terms.consumer_deal or terms.contract_type == ContractType.CONSUMER_SERVICE:
        days = terms.cancellation_window_days if terms.cancellation_window_days is not None else "[מספר]"
        consumer = f"\n## 12. הוראות צרכניות\nככל שהלקוח הוא צרכן, אין בהסכם זה כדי לגרוע מזכויות קוגנטיות לפי דין. תנאי ביטול, החזר ודמי ביטול יחולו רק במידה המותרת לפי דין ובהתאם לנסיבות העסקה. אם הדין מקנה ללקוח תקופת ביטול, יפעלו הצדדים לפי התקופה החלה; לצורכי הטיוטה סומנה תקופה של {days} ימים לבדיקה.\n"
    return _assumptions_block(assumptions, "he") + _findings_block(findings, "he") + f"""# {title}

נחתם ביום {signing_date}

בין:
{parties}

## 1. רקע ומטרת ההתקשרות
הצדדים מבקשים להתקשר בהסכם זה לצורך {description}. ההסכם ייכנס לתוקף ביום {effective_date}, אלא אם נקבע אחרת בכתב.

## 2. השירותים והתוצרים
נותן השירותים יספק את השירותים והתוצרים הבאים:

{_deliverables_text(terms.deliverables, "he")}

## 3. החרגות ותלויות
השירותים אינם כוללים את הפריטים הבאים, אלא אם הוסכם אחרת בכתב:
{_deliverables_text(terms.exclusions, "he") if terms.exclusions else "- [החרגות, תלויות, חומרים שעל הלקוח לספק]"}

## 4. לוח זמנים ואישור תוצרים
נותן השירותים ימסור את התוצרים לפי לוח הזמנים שיוסכם בנספח העבודה. הלקוח יבדוק כל תוצר בתוך [7] ימי עסקים ממועד המסירה וימסור הערות ענייניות ומרוכזות בכתב. שינוי מחוץ להיקף יתומחר ויאושר מראש בכתב.

## 5. התמורה ותנאי התשלום
{_payment_text(terms, "he")}
{("הוצאות: " + terms.expenses + ".") if terms.expenses else "הוצאות ישולמו רק אם אושרו מראש ובכתב."}
{("איחור בתשלום: " + terms.late_payment + ".") if terms.late_payment else "במקרה של איחור בתשלום שאינו שנוי במחלוקת, נותן השירותים רשאי למסור הודעה בכתב ולהשהות שירותים נוספים עד לתשלום."}

## 6. הצהרות הצדדים
כל צד מצהיר כי הוא מוסמך להתקשר בהסכם, כי החותם מטעמו מוסמך לחתום עליו, וכי ביצוע ההסכם לא יפר התחייבות אחרת שלו.

## 7. קניין רוחני
{ip} חומרים קיימים, ידע מקצועי, שיטות עבודה, תבניות, כלים, רכיבי קוד קודמים וחומרי צד שלישי אינם מועברים אלא אם צוין אחרת במפורש.

## 8. פרטיות ואבטחת מידע
{privacy}

## 9. סודיות
כל צד ישמור בסוד מידע סודי שקיבל מהצד השני, ישתמש בו רק לצורך ביצוע ההסכם, ויגלה אותו רק לעובדים, יועצים או ספקים הזקוקים לדעת אותו וכפופים לחובת סודיות. מידע שהיה ציבורי, ידוע קודם, פותח עצמאית או נדרש לגילוי לפי דין לא ייחשב מידע סודי.

## 10. אחריות והגבלת אחריות
כל צד יהיה אחראי לנזקים ישירים שנגרמו עקב הפרת ההסכם. אחריות נותן השירותים לא תעלה על {liability_cap}, למעט אחריות שאינה ניתנת להגבלה לפי דין, תרמית, זדון, הפרת סודיות חמורה או שימוש אסור בקניין רוחני.

## 11. תקופה וסיום
ההסכם יימשך {term}. כל צד רשאי לסיים את ההסכם בהודעה מוקדמת של {notice} ימים. במקרה של הפרה ניתנת לתיקון, הצד הנפגע ימסור הודעה בכתב ויאפשר תקופת תיקון של {cure} ימים. עם סיום ההסכם ישולמו סכומים עבור שירותים שבוצעו בפועל עד מועד הסיום.
{consumer}
## 13. יישוב מחלוקות, דין חל וסמכות שיפוט
הצדדים ינסו לפתור מחלוקת בתום לב באמצעות פנייה בכתב והידברות. על ההסכם יחולו דיני מדינת ישראל. סמכות השיפוט נתונה לבית המשפט המוסמך ב{venue}, בכפוף לכל דין קוגנטי.

## 14. הודעות
הודעות לפי הסכם זה יימסרו בכתב לכתובות או לדוא״ל שנמסרו על ידי הצדדים, וייחשבו כאילו נמסרו במועד המסירה בפועל או במועד אישור קבלה אלקטרוני.

## 15. שונות
הסכם זה מבטא את מלוא ההסכמות בין הצדדים בנושא ההתקשרות. שינוי להסכם יהיה בכתב בלבד. אם הוראה מסוימת תימצא בלתי תקפה, יתר הוראות ההסכם ימשיכו לחול.

## חתימות

נותן השירותים: ____________________   תאריך: __________

הלקוח: ____________________   תאריך: __________
"""


def render_english_contract(terms: ContractTerms, *, findings: Sequence[RiskFinding] | None = None, assumptions: Sequence[str] | None = None) -> str:
    title = _title_for(terms, "en")
    signing_date = format_date_ddmmyyyy(terms.date_text)
    effective_date = format_date_ddmmyyyy(terms.effective_date) if terms.effective_date else "[DD/MM/YYYY]"
    parties = "\n\nand:\n".join(_party_lines(terms, "en"))
    description = terms.description or "[description of services/transaction]"
    term = terms.term or "[until completion / fixed term]"
    notice = terms.termination_notice_days if terms.termination_notice_days is not None else "[number]"
    cure = terms.cure_period_days or 14
    venue = terms.venue or "[city/district]"
    ip = terms.ip_ownership or "Ownership or license of deliverables shall be selected by the parties: assignment after full payment or a defined license."
    liability_cap = format_ils(terms.liability_cap_nis) if terms.liability_cap_nis else "the fees actually paid during the 12 months preceding the event"
    privacy = "The provider shall process personal data only for the purpose of performing this agreement, restrict access to authorized personnel, maintain reasonable security measures, notify the customer of a material security incident without unreasonable delay, and avoid transferring personal data to a subcontractor without an appropriate basis or approval required by this agreement." if terms.personal_data else "If either party receives personal data during performance, that party shall use it only for the agreement and comply with applicable law."
    consumer = ""
    if terms.consumer_deal or terms.contract_type == ContractType.CONSUMER_SERVICE:
        days = terms.cancellation_window_days if terms.cancellation_window_days is not None else "[number]"
        consumer = f"\n## 12. Consumer provisions\nIf the customer is a consumer, nothing in this agreement derogates from mandatory rights under applicable law. Cancellation, refunds, and cancellation fees apply only to the extent permitted by law and according to the circumstances of the transaction. If applicable law grants a cancellation period, the parties shall follow the applicable period; this draft marks {days} days for review.\n"
    return _assumptions_block(assumptions, "en") + _findings_block(findings, "en") + f"""# {title}

Signed on {signing_date}

between:
{parties}

## 1. Background and purpose
The parties enter into this agreement for {description}. The agreement takes effect on {effective_date}, unless otherwise agreed in writing.

## 2. Services and deliverables
The provider shall provide the following services and deliverables:

{_deliverables_text(terms.deliverables, "en")}

## 3. Exclusions and dependencies
The services do not include the following items unless agreed otherwise in writing:
{_deliverables_text(terms.exclusions, "en") if terms.exclusions else "- [exclusions, dependencies, customer-provided materials]"}

## 4. Timeline and acceptance
The provider shall deliver the deliverables according to the agreed statement of work. The customer shall review each deliverable within [7] business days after delivery and provide specific consolidated comments in writing. Out-of-scope changes require prior written approval and pricing.

## 5. Fees and payment
{_payment_text(terms, "en")}
{("Expenses: " + terms.expenses + ".") if terms.expenses else "Expenses are reimbursable only if approved in advance in writing."}
{("Late payment: " + terms.late_payment + ".") if terms.late_payment else "For overdue undisputed amounts, the provider may give written notice and suspend further services until payment."}

## 6. Representations
Each party represents that it has authority to enter into this agreement, that its signatory is authorized to sign, and that performance will not breach another obligation.

## 7. Intellectual property
{ip} Pre-existing materials, know-how, methods, templates, tools, prior code, and third-party materials are not transferred unless expressly stated.

## 8. Privacy and data security
{privacy}

## 9. Confidentiality
Each party shall keep confidential information received from the other party confidential, use it only for performance of this agreement, and disclose it only to employees, advisers, or vendors who need to know it and are bound by confidentiality duties. Information that is public, previously known, independently developed, or required to be disclosed by law is excluded.

## 10. Liability and limitation of liability
Each party is responsible for direct damages caused by breach of this agreement. The provider's liability shall not exceed {liability_cap}, except for liability that cannot be limited by law, fraud, willful misconduct, serious confidentiality breach, or unauthorized use of intellectual property.

## 11. Term and termination
The agreement continues {term}. Either party may terminate with {notice} days' prior notice. For a remediable breach, the non-breaching party shall give written notice and allow a {cure}-day cure period. Upon termination, amounts for services actually performed through termination shall be paid.
{consumer}
## 13. Disputes, governing law, and venue
The parties shall first attempt to resolve disputes in good faith through written notice and discussion. This agreement is governed by the laws of the State of Israel. The competent courts in {venue} shall have jurisdiction, subject to mandatory law.

## 14. Notices
Notices under this agreement shall be sent in writing to the addresses or email addresses provided by the parties and are deemed delivered upon actual delivery or electronic confirmation of receipt.

## 15. Miscellaneous
This agreement contains the entire agreement between the parties regarding its subject matter. Amendments must be in writing. If any provision is invalid, the remaining provisions remain effective.

## Signatures

Provider: ____________________   Date: __________

Customer: ____________________   Date: __________
"""


def load_terms(path: str | Path) -> ContractTerms:
    return ContractTerms.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def save_draft(result: DraftResult, path: str | Path) -> Path:
    output = Path(path)
    output.write_text(result.contract_markdown, encoding="utf-8")
    return output


def sample_terms(name: str = "freelance-design", language: Language = "he") -> ContractTerms:
    if name == "consumer-repair":
        return ContractTerms(
            contract_type=ContractType.CONSUMER_SERVICE,
            language=language,
            title="הסכם שירות לתיקון מקרר" if language == "he" else "Refrigerator Repair Service Agreement",
            date_text="20/06/2026",
            effective_date="20/06/2026",
            parties=[Party("טכנאי שירות בע״מ", "company", "515000000", "חיפה", role="provider", signatory_title="מנכ״ל"), Party("רונית לוי", "individual", "123456782", "חיפה", role="consumer")],
            description="תיקון מקרר ביתי" if language == "he" else "home refrigerator repair",
            deliverables=["ביקור טכנאי", "אבחון תקלה", "החלפת חלק לפי צורך"],
            price_nis=650,
            vat_included=True,
            payment_terms="במועד סיום השירות" if language == "he" else "upon completion of service",
            consumer_deal=True,
            cancellation_window_days=14,
            liability_cap_nis=650,
        )
    if name == "nda":
        return ContractTerms(
            contract_type=ContractType.NDA,
            language=language,
            title="הסכם סודיות הדדי" if language == "he" else "Mutual Non-Disclosure Agreement",
            date_text="02/06/2026",
            parties=[Party("חברה א׳ בע״מ", "company", "515000001", "תל אביב", role="discloser/recipient", signatory_title="מנכ״ל"), Party("חברה ב׳ בע״מ", "company", "515000002", "רמת גן", role="discloser/recipient", signatory_title="סמנכ״ל")],
            description="בחינת שיתוף פעולה מסחרי" if language == "he" else "evaluation of a commercial collaboration",
            deliverables=["שימוש במידע רק למטרה המותרת"],
            confidentiality=True,
            term="שנתיים" if language == "he" else "two years",
        )
    return ContractTerms(
        contract_type=ContractType.FREELANCE_AGREEMENT,
        language=language,
        title="הסכם למתן שירותי עיצוב גרפי" if language == "he" else "Graphic Design Services Agreement",
        date_text="02/06/2026",
        effective_date="15/07/2026",
        parties=[Party("דנה כהן", "sole_proprietor", "123456782", "תל אביב", role="provider"), Party("רשת בתי קפה בע״מ", "company", "515000000", "רמת גן", role="customer", signatory_title="מנכ״ל")],
        description="עיצוב סימן מזהה חזותי ותבניות תפריט" if language == "he" else "visual identity refresh and menu templates",
        deliverables=["רענון סימן מזהה חזותי", "תבנית תפריט", "5 תבניות לרשתות חברתיות"],
        exclusions=["הדפסה", "רכישת פונטים", "צילום מוצרים"],
        price_nis=12000,
        vat_included=False,
        payment_terms="40% מקדמה ו-60% לאחר מסירה" if language == "he" else "40% advance and 60% after delivery",
        ip_ownership="הזכויות בתוצרים הסופיים יעברו ללקוח לאחר תשלום מלא; נותנת השירותים רשאית להציג את התוצרים בתיק עבודות." if language == "he" else "Final approved deliverables transfer to the customer after full payment; provider may display them in a portfolio.",
        liability_cap_nis=12000,
        termination_notice_days=14,
    )


def scenario_names() -> list[str]:
    return ["freelance-design", "consumer-repair", "nda"]


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Generate Israeli contract drafts from JSON.")
    parser.add_argument("input", nargs="?", help="Input JSON path.")
    parser.add_argument("--sample", choices=scenario_names(), help="Use a built-in sample.")
    parser.add_argument("--language", choices=["he", "en"], default="he")
    parser.add_argument("--output", help="Output markdown path.")
    args = parser.parse_args()
    client = ContractDraftingClient()
    if args.sample:
        terms = sample_terms(args.sample, args.language)  # type: ignore[arg-type]
    elif args.input:
        terms = load_terms(args.input)
    else:
        parser.error("Provide an input JSON path or --sample.")
    result = client.draft(terms)
    if args.output:
        save_draft(result, args.output)
    else:
        print(result.contract_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
