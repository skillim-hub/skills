"""Local Israeli employee onboarding helper.

The module is installable with ``pip install -e .`` and can be imported with:

    from employee_onboarding_guide_client import EmployeeProfile, create_record

No network calls are made. Employee data stays in local JSON files.
"""

from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import json
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

DateSeparator = Literal["-", "/"]
EmploymentType = Literal["employee", "contractor", "unknown"]
SalaryType = Literal["monthly", "hourly", "commission", "mixed", "unknown"]
Language = Literal["en", "he"]
Environment = Literal["sandbox", "production"]

_DATE_RE = re.compile(r"^\d{2}[-/]\d{2}[-/]\d{4}$")


class EmployeeProfile:
    full_name: str
    start_date: str
    employment_type: EmploymentType = "employee"
    role: str = ""
    salary_type: SalaryType = "unknown"
    monthly_salary_nis: Optional[float] = None
    hourly_rate_nis: Optional[float] = None
    has_other_employer: bool = False
    has_active_pension: Optional[bool] = None
    foreign_worker: bool = False
    youth: bool = False
    remote: bool = False
    student: bool = False
    language: Language = "en"
    secure_channel: bool = True
    timekeeping_method: Optional[str] = None
    bank_details_received: bool = False
    pension_fund_name: Optional[str] = None
    tax_coordination_received: bool = False
    national_insurance_coordination_received: bool = False
    employment_notice_status: str = "missing"
    equipment_required: bool = False
    equipment_form_signed: bool = False


EmployeeProfile = dataclasses.dataclass(EmployeeProfile)


class ValidationResult:
    ok: bool
    errors: List[str] = dataclasses.field(default_factory=list)
    warnings: List[str] = dataclasses.field(default_factory=list)
    next_actions: List[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "next_actions": self.next_actions,
        }


ValidationResult = dataclasses.dataclass(ValidationResult)


def validate_date(value: str) -> bool:
    """Return True for a real DD-MM-YYYY or DD/MM/YYYY date."""

    if not _DATE_RE.match(value or ""):
        return False
    normalized = value.replace("/", "-")
    try:
        datetime.strptime(normalized, "%d-%m-%Y")
    except ValueError:
        return False
    return True


def normalize_date(value: str, language: Language = "en") -> str:
    """Return date in the preferred display format for the language."""

    if not validate_date(value):
        raise ValueError("date must use DD-MM-YYYY or DD/MM/YYYY format")
    dt = datetime.strptime(value.replace("/", "-"), "%d-%m-%Y")
    return dt.strftime("%d/%m/%Y" if language == "he" else "%d-%m-%Y")


def days_until(start_date: str, today: Optional[date] = None) -> Optional[int]:
    if not validate_date(start_date):
        return None
    today = today or date.today()
    target = datetime.strptime(start_date.replace("/", "-"), "%d-%m-%Y").date()
    return (target - today).days


def _optional_float(value: Any) -> Optional[float]:
    if value in (None, "", "null"):
        return None
    return float(value)


def _optional_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    return bool(value)


def profile_from_dict(data: Dict[str, Any]) -> EmployeeProfile:
    employee = data.get("employee", data)
    payroll = data.get("payroll", {})
    documents = data.get("documents", {})

    return EmployeeProfile(
        full_name=str(employee.get("full_name", data.get("full_name", ""))).strip(),
        start_date=str(employee.get("start_date", data.get("start_date", ""))).strip(),
        employment_type=employee.get("employment_type", data.get("employment_type", "employee")),
        role=str(employee.get("role", data.get("role", ""))).strip(),
        salary_type=payroll.get("salary_type", employee.get("salary_type", data.get("salary_type", "unknown"))),
        monthly_salary_nis=_optional_float(payroll.get("monthly_salary_nis", data.get("monthly_salary_nis"))),
        hourly_rate_nis=_optional_float(payroll.get("hourly_rate_nis", data.get("hourly_rate_nis"))),
        has_other_employer=bool(employee.get("has_other_employer", data.get("has_other_employer", False))),
        has_active_pension=_optional_bool(employee.get("has_active_pension", data.get("has_active_pension"))),
        foreign_worker=bool(employee.get("foreign_worker", data.get("foreign_worker", False))),
        youth=bool(employee.get("youth", data.get("youth", False))),
        remote=bool(employee.get("remote", data.get("remote", False))),
        student=bool(employee.get("student", data.get("student", False))),
        language=employee.get("language", data.get("language", "en")),
        secure_channel=bool(data.get("secure_channel", True)),
        timekeeping_method=employee.get("timekeeping_method", data.get("timekeeping_method")),
        bank_details_received=documents.get("bank_details", data.get("bank_details_received", "missing")) in {"received", True},
        pension_fund_name=employee.get("pension_fund_name", data.get("pension_fund_name")),
        tax_coordination_received=documents.get("tax_coordination", data.get("tax_coordination_received", "missing")) in {"received", True},
        national_insurance_coordination_received=documents.get("national_insurance_coordination", data.get("national_insurance_coordination_received", "missing")) in {"received", True},
        employment_notice_status=documents.get("employment_notice", data.get("employment_notice_status", "missing")),
        equipment_required=bool(employee.get("equipment_required", data.get("equipment_required", False))),
        equipment_form_signed=documents.get("equipment_form", data.get("equipment_form_signed", "missing")) in {"received", True},
    )


def profile_to_dict(profile: EmployeeProfile) -> Dict[str, Any]:
    return dataclasses.asdict(profile)


def validate_profile(profile: EmployeeProfile, today: Optional[date] = None) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []
    actions: List[str] = []

    if not profile.full_name:
        errors.append("employee.full_name is required.")

    if not validate_date(profile.start_date):
        errors.append("employee.start_date must use DD-MM-YYYY or DD/MM/YYYY format.")

    if profile.employment_type == "employee":
        actions.append("Request completed Form 101 within 7 days of start and before payroll close when needed.")
        actions.append("Collect ID or passport details and bank details.")
    elif profile.employment_type == "contractor":
        warnings.append("Supplier workflow selected: do not request Form 101; use supplier onboarding.")
    else:
        warnings.append("Worker status is unclear: review employee versus supplier classification before work starts.")

    if profile.employment_type == "employee" and not profile.bank_details_received:
        warnings.append("Bank details missing: request bank, branch, account number, and confirmation if needed.")

    if profile.has_other_employer:
        if not profile.tax_coordination_received:
            warnings.append("Employee has another employer: request tax coordination before payroll close.")
        if not profile.national_insurance_coordination_received:
            warnings.append("Employee has another employer: ask payroll whether National Insurance coordination is required.")

    if profile.has_active_pension is True:
        if not profile.pension_fund_name:
            warnings.append("Active pension arrangement exists: collect fund name, account or policy number, and provider contact.")
        actions.append("Ask payroll or a licensed pension professional to confirm first pension deposit deadline.")
    elif profile.has_active_pension is False:
        warnings.append("No active pension arrangement declared: provide a neutral choice process and confirm default arrangement rules.")

    if profile.salary_type == "hourly" and not profile.timekeeping_method:
        warnings.append("Hourly or shift employee lacks timekeeping method: set clock-in or timesheet approval process.")

    if profile.remote:
        warnings.append("Remote employee: add equipment, data security, availability, and incident reporting instructions.")

    if profile.foreign_worker:
        errors.append("Foreign worker onboarding requires permit, visa, employer authorization, health insurance, and payroll review before work starts.")

    if profile.youth:
        warnings.append("Youth employee: verify age, permitted hours, role restrictions, and safety training.")

    if profile.student:
        warnings.append("Student status: request documentation only when relevant to a declared benefit or payroll need.")

    if not profile.secure_channel:
        warnings.append("Sensitive document channel is not approved: use restricted storage or secure upload.")

    if profile.employment_type == "employee" and profile.employment_notice_status not in {"drafted", "received"}:
        warnings.append("Employment notice or agreement status missing: draft and deliver written terms.")

    if profile.equipment_required and not profile.equipment_form_signed:
        warnings.append("Equipment required but no signed handover form exists: record serial numbers, condition, and return rules.")

    remaining = days_until(profile.start_date, today=today)
    if remaining is not None and 0 <= remaining <= 7:
        warnings.append("Start date is within 7 days: prioritize Form 101, payroll documents, bank details, written terms, and access setup.")

    return ValidationResult(ok=not errors, errors=errors, warnings=warnings, next_actions=actions)


def document_checklist(profile: EmployeeProfile) -> List[str]:
    if profile.employment_type == "contractor":
        return [
            "Supplier agreement or statement of work",
            "Supplier tax and withholding documents where applicable",
            "Supplier bank details",
            "Confidentiality and data access terms if relevant",
        ]

    items = [
        "Completed Form 101",
        "ID card or passport details",
        "Bank details for salary payment",
        "Written employment terms or employment agreement",
        "Pension fund, provident fund, or insurance arrangement details",
    ]
    if profile.has_other_employer:
        items.append("Tax coordination approval")
        items.append("National Insurance coordination approval if payroll confirms required")
    if profile.foreign_worker:
        items.append("Permit, visa, employer authorization, and health insurance review")
    if profile.youth:
        items.append("Age verification and restricted-work check")
    if profile.remote:
        items.append("Remote work and data security acknowledgment")
    if profile.equipment_required:
        items.append("Signed equipment handover form")
    return items


def generate_checklist(profile: EmployeeProfile) -> str:
    start = normalize_date(profile.start_date, "en") if validate_date(profile.start_date) else profile.start_date
    result = validate_profile(profile)
    lines = [
        f"# Onboarding Checklist: {profile.full_name or '{{employee_name}}'}",
        "",
        f"Start date: {start or '{{start_date_dd_mm_yyyy}}'}",
        f"Role: {profile.role or '{{role}}'}",
        "",
        "## Employee documents",
    ]
    lines.extend(f"- [ ] {item}" for item in document_checklist(profile))
    lines.extend([
        "",
        "## Manager actions",
        "- [ ] Confirm job title, manager, salary basis, schedule, and workplace.",
        "- [ ] Prepare written terms.",
        "- [ ] Prepare equipment, access, and first-day agenda.",
        "- [ ] Set timekeeping and absence reporting route.",
        "- [ ] Schedule 7-day and 30-day check-ins.",
        "",
        "## Payroll handoff",
        "- [ ] Legal name and ID or passport.",
        "- [ ] Start date in DD-MM-YYYY.",
        "- [ ] Salary basis and amounts in ₪.",
        "- [ ] Form 101 and coordination approvals.",
        "- [ ] Bank details.",
        "- [ ] Pension status and fund details.",
        "- [ ] Benefits, travel reimbursement, and taxable perks.",
        "",
        "## Training",
        "- [ ] Safety and emergency route.",
        "- [ ] Prevention of sexual harassment reporting route.",
        "- [ ] Privacy, confidentiality, and secure document handling.",
        "- [ ] Role systems and escalation process.",
    ])
    if result.warnings:
        lines.append("")
        lines.append("## Warnings")
        lines.extend(f"- {item}" for item in result.warnings)
    if result.errors:
        lines.append("")
        lines.append("## Blocking issues")
        lines.extend(f"- {item}" for item in result.errors)
    return "\n".join(lines) + "\n"


def generate_hebrew_checklist(profile: EmployeeProfile) -> str:
    start = normalize_date(profile.start_date, "he") if validate_date(profile.start_date) else profile.start_date
    result = validate_profile(profile)
    terms = {
        "Completed Form 101": "טופס 101 מלא",
        "ID card or passport details": "צילום תעודת זהות וספח או פרטי דרכון",
        "Bank details for salary payment": "פרטי חשבון בנק להעברת שכר",
        "Written employment terms or employment agreement": "הודעה לעובד או הסכם העסקה",
        "Pension fund, provident fund, or insurance arrangement details": "פרטי קרן פנסיה, קופת גמל או ביטוח מנהלים",
        "Tax coordination approval": "אישור תיאום מס",
        "National Insurance coordination approval if payroll confirms required": "אישור תיאום ביטוח לאומי אם חשבות השכר אישרה שנדרש",
        "Permit, visa, employer authorization, and health insurance review": "בדיקת היתר, אשרה, אישור מעסיק וביטוח רפואי",
        "Age verification and restricted-work check": "אימות גיל ובדיקת מגבלות העסקת נוער",
        "Remote work and data security acknowledgment": "אישור עבודה מרחוק ואבטחת מידע",
        "Signed equipment handover form": "טופס מסירת ציוד חתום",
    }
    lines = [
        f"# רשימת קליטה: {profile.full_name or '{{employee_name}}'}",
        "",
        f"תאריך תחילת עבודה: {start or '{{start_date_dd_mm_yyyy}}'}",
        f"תפקיד: {profile.role or '{{role}}'}",
        "",
        "## מסמכי עובד",
    ]
    lines.extend(f"- [ ] {terms.get(item, item)}" for item in document_checklist(profile))
    lines.extend([
        "",
        "## פעולות מנהל",
        "- [ ] אשר תפקיד, מנהל ישיר, סוג שכר, היקף עבודה ומקום עבודה.",
        "- [ ] הכן הודעה לעובד או הסכם העסקה.",
        "- [ ] הכן ציוד, הרשאות וסדר יום ליום הראשון.",
        "- [ ] קבע שיטת דיווח שעות והיעדרויות.",
        "- [ ] קבע שיחות לאחר 7 ימים ולאחר 30 ימים.",
        "",
        "## מסירה לחשבות שכר",
        "- [ ] שם מלא ומספר תעודת זהות או דרכון.",
        "- [ ] תאריך תחילת עבודה בפורמט DD/MM/YYYY.",
        "- [ ] סוג שכר וסכומים ב-₪.",
        "- [ ] טופס 101 ואישורי תיאום.",
        "- [ ] פרטי בנק.",
        "- [ ] מצב פנסיוני ופרטי קופה.",
        "- [ ] הטבות, החזר נסיעות ושווי מס.",
    ])
    if result.warnings:
        lines.append("")
        lines.append("## אזהרות לבדיקה")
        lines.extend(f"- {item}" for item in result.warnings)
    if result.errors:
        lines.append("")
        lines.append("## חסמים")
        lines.extend(f"- {item}" for item in result.errors)
    return "\n".join(lines) + "\n"


def generate_employee_message(name: str, due_date: str, language: Language = "en") -> str:
    due = normalize_date(due_date, language)
    if language == "he":
        return (
            f"שלום {name},\n\n"
            f"שלח/י את המסמכים הבאים עד {due}:\n\n"
            "1. טופס 101 מלא לשנת המס הנוכחית, למסירה בתוך 7 ימים מתחילת העבודה.\n"
            "2. צילום תעודת זהות וספח או פרטי דרכון.\n"
            "3. פרטי חשבון בנק להעברת שכר.\n"
            "4. פרטי קרן פנסיה, קופת גמל או ביטוח מנהלים, אם קיים הסדר פעיל.\n"
            "5. אישור תיאום מס אם קיימת הכנסה ממעסיק נוסף או ממשלם קצבה.\n"
            "6. אישור תיאום ביטוח לאומי, אם רלוונטי.\n"
            "7. הודעה לעובד או הסכם העסקה חתומים.\n\n"
            "העבר/י מסמכים רגישים בערוץ מאובטח בלבד.\n"
        )

    return (
        f"Hello {name},\n\n"
        f"Send the following items by {due}:\n\n"
        "1. Completed Form 101 for the current tax year, submitted within 7 days of starting work.\n"
        "2. ID card or passport details.\n"
        "3. Bank account details for salary payment.\n"
        "4. Pension fund or insurance arrangement details, if an active arrangement exists.\n"
        "5. Tax coordination approval if income is received from another employer or pension payer.\n"
        "6. National Insurance coordination approval, if relevant.\n"
        "7. Signed written terms or employment agreement.\n\n"
        "Use a secure transfer route for sensitive documents.\n"
    )


def storage_dir_from_env(environment: Environment = "sandbox") -> Path:
    override = os.getenv("ONBOARDING_DATA_DIR")
    if override:
        return Path(override)
    return Path(".onboarding-records") / environment


def make_record_id(profile: EmployeeProfile, environment: Environment = "sandbox") -> str:
    payload = json.dumps(profile_to_dict(profile), ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256((environment + "|" + payload).encode("utf-8")).hexdigest()[:10]
    return f"rec_{digest}"


def create_record(profile: EmployeeProfile, environment: Environment = "sandbox", storage_dir: Optional[Path] = None) -> Dict[str, Any]:
    storage = storage_dir or storage_dir_from_env(environment)
    storage.mkdir(parents=True, exist_ok=True)
    record_id = make_record_id(profile, environment)
    path = storage / f"{record_id}.json"
    payload = {
        "id": record_id,
        "environment": environment,
        "employee": profile_to_dict(profile),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"id": record_id, "environment": environment, "record_file": str(path), "ok": True}


def load_record(record_id: str, environment: Environment = "sandbox", storage_dir: Optional[Path] = None) -> EmployeeProfile:
    storage = storage_dir or storage_dir_from_env(environment)
    path = storage / f"{record_id}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return profile_from_dict(data.get("employee", data))


def load_profile_file(path: str | Path) -> EmployeeProfile:
    return profile_from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def save_text(path: str | Path, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")


async def async_validate_profile(profile: EmployeeProfile) -> ValidationResult:
    await asyncio.sleep(0)
    return validate_profile(profile)


async def async_create_record(profile: EmployeeProfile, environment: Environment = "sandbox", storage_dir: Optional[Path] = None) -> Dict[str, Any]:
    await asyncio.sleep(0)
    return create_record(profile, environment=environment, storage_dir=storage_dir)


async def async_generate_checklist(profile: EmployeeProfile) -> str:
    await asyncio.sleep(0)
    return generate_hebrew_checklist(profile) if profile.language == "he" else generate_checklist(profile)


__all__ = [
    "EmployeeProfile",
    "ValidationResult",
    "validate_date",
    "normalize_date",
    "days_until",
    "profile_from_dict",
    "profile_to_dict",
    "validate_profile",
    "document_checklist",
    "generate_checklist",
    "generate_hebrew_checklist",
    "generate_employee_message",
    "create_record",
    "load_record",
    "load_profile_file",
    "save_text",
    "async_validate_profile",
    "async_create_record",
    "async_generate_checklist",
]
