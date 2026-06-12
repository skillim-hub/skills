"""Typed helper library for Israeli tax-return filing workflows.

The module performs offline preparation only. It does not submit returns or call Tax
Authority systems.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Sequence


Severity = Literal["info", "warning", "error"]


class TaxAssistantError(ValueError):
    """Base exception for local helper errors."""


class UnknownFormError(TaxAssistantError):
    """Raised when a form is not covered by the helper."""


class UnknownFieldError(TaxAssistantError):
    """Raised when a field ID is not found for a covered form."""


class FormType(str, Enum):
    """Covered Israeli tax forms."""

    FORM_1301 = "1301"
    FORM_135 = "135"
    FORM_126 = "126"
    FORM_856 = "856"
    FORM_6111 = "6111"

    @classmethod
    def parse(cls, value: str | "FormType") -> "FormType":
        if isinstance(value, cls):
            return value
        normalized = str(value).strip()
        for item in cls:
            if item.value == normalized:
                return item
        raise UnknownFormError(f"FORM_UNKNOWN: unsupported form {value!r}")


@dataclass(frozen=True)
class FilingProfile:
    """Facts used to recommend forms and calculate planning deadlines."""

    tax_year: int | None
    taxpayer_type: str = "individual"
    salary_only: bool = False
    wants_refund: bool = False
    business_income: bool = False
    annual_turnover_ils: float = 0.0
    has_employees: bool = False
    paid_suppliers: bool = False
    foreign_income: bool = False
    capital_gains: bool = False
    rental_income: bool = False
    is_online: bool = True
    represented_by_cpa: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable profile data."""

        return asdict(self)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "FilingProfile":
        allowed = {field_name for field_name in cls.__dataclass_fields__}
        clean: dict[str, Any] = {key: value for key, value in data.items() if key in allowed}
        if "tax_year" not in clean:
            clean["tax_year"] = None
        return cls(**clean)


@dataclass(frozen=True)
class FieldHelp:
    form: FormType
    field_id: str
    label_en: str
    label_he: str
    description: str
    required_when: str
    source_documents: tuple[str, ...]
    common_errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["form"] = self.form.value
        return data


@dataclass(frozen=True)
class Deadline:
    form: FormType
    due_date: _dt.date
    basis: str
    requires_official_confirmation: bool = True
    notes: str = ""

    def reminders(self, offsets: Sequence[int] | None = None) -> list[_dt.date]:
        if offsets is None:
            offsets = (60, 30, 14, 7, 0)
        dates = [self.due_date - _dt.timedelta(days=days) for days in offsets]
        return sorted(set(dates))

    def to_dict(self) -> dict[str, Any]:
        return {
            "form": self.form.value,
            "due_date": format_date(self.due_date),
            "basis": self.basis,
            "requires_official_confirmation": self.requires_official_confirmation,
            "notes": self.notes,
            "reminders": [format_date(day) for day in self.reminders()],
        }


@dataclass(frozen=True)
class ValidationIssue:
    severity: Severity
    code: str
    message: str
    field: str | None = None
    remediation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Recommendation:
    forms: tuple[FormType, ...]
    explanations: Mapping[str, str]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "forms": [form.value for form in self.forms],
            "explanations": dict(self.explanations),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class Checklist:
    form: FormType
    items: tuple[str, ...]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"form": self.form.value, "items": list(self.items), "warnings": list(self.warnings)}


def format_date(date_value: _dt.date) -> str:
    """Return DD/MM/YYYY date format."""

    return date_value.strftime("%d/%m/%Y")


def format_ils(amount: float | int) -> str:
    """Return a readable Israeli shekel amount."""

    return f"₪{amount:,.0f}" if float(amount).is_integer() else f"₪{amount:,.2f}"


def load_profile(path: str | Path) -> FilingProfile:
    """Load a filing profile from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TaxAssistantError("PROFILE_INVALID: profile JSON must be an object")
    return FilingProfile.from_mapping(data)


def save_json(path: str | Path, data: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> None:
    """Save a JSON object or array using UTF-8."""

    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class StoredProfile:
    """Persisted local profile reference for CLI workflows."""

    profile_id: str
    profile: FilingProfile
    environment: Literal["sandbox", "production"] = "sandbox"
    created_at: str = field(default_factory=lambda: _dt.datetime.now(_dt.timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.profile_id,
            "environment": self.environment,
            "created_at": self.created_at,
            "profile": self.profile.to_dict(),
        }


class LocalProfileStore:
    """JSON-backed local profile store for chained CLI examples."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else Path.home() / ".tax-return-filing-assistant" / "profiles.json"

    def create(self, profile: FilingProfile, environment: Literal["sandbox", "production"] = "sandbox") -> StoredProfile:
        profile_id = uuid.uuid4().hex[:12]
        stored = StoredProfile(profile_id=profile_id, profile=profile, environment=environment)
        data = self._read()
        data[profile_id] = stored.to_dict()
        self._write(data)
        return stored

    def get(self, profile_id: str) -> StoredProfile:
        data = self._read()
        if profile_id not in data:
            raise TaxAssistantError(f"PROFILE_NOT_FOUND: profile {profile_id!r} was not found")
        entry = data[profile_id]
        profile_data = entry.get("profile", {})
        if not isinstance(profile_data, dict):
            raise TaxAssistantError("PROFILE_INVALID: stored profile must be an object")
        return StoredProfile(
            profile_id=profile_id,
            profile=FilingProfile.from_mapping(profile_data),
            environment=entry.get("environment", "sandbox"),
            created_at=entry.get("created_at", ""),
        )

    def list_ids(self) -> list[str]:
        return sorted(self._read().keys())

    def delete(self, profile_id: str) -> bool:
        data = self._read()
        existed = profile_id in data
        if existed:
            data.pop(profile_id)
            self._write(data)
        return existed

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise TaxAssistantError("STORE_INVALID: profile store must contain a JSON object")
        return data

    def _write(self, data: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class FieldHelpRepository:
    """Local field-help repository for the five covered forms."""

    def __init__(self) -> None:
        self._fields: dict[FormType, dict[str, FieldHelp]] = {}
        for item in _FIELD_HELP:
            self._fields.setdefault(item.form, {})[item.field_id] = item

    def list_forms(self) -> list[FormType]:
        return list(FormType)

    def list_fields(self, form: str | FormType) -> list[FieldHelp]:
        form_type = FormType.parse(form)
        return list(self._fields.get(form_type, {}).values())

    def get(self, form: str | FormType, field_id: str) -> FieldHelp:
        form_type = FormType.parse(form)
        try:
            return self._fields[form_type][field_id]
        except KeyError as exc:
            raise UnknownFieldError(
                f"FIELD_UNKNOWN: field {field_id!r} is not available for Form {form_type.value}"
            ) from exc


class DeadlineCalculator:
    """Planning deadline calculator.

    Deadlines are defaults intended for reminders. Confirm current official
    instructions before filing.
    """

    def deadline_for(self, form: str | FormType, profile: FilingProfile) -> Deadline:
        form_type = FormType.parse(form)
        if profile.tax_year is None:
            raise TaxAssistantError("TAX_YEAR_MISSING: tax_year is required")
        if profile.tax_year < 2000 or profile.tax_year > 2100:
            raise TaxAssistantError("TAX_YEAR_RANGE: tax_year must be realistic")

        filing_year = profile.tax_year + 1

        if form_type == FormType.FORM_1301:
            if profile.tax_year == 2025:
                if profile.is_online or profile.represented_by_cpa:
                    return Deadline(
                        form_type,
                        _dt.date(2026, 6, 30),
                        "Official 2025 online Form 1301 planning deadline.",
                        True,
                        "Use this statutory planning date unless a verified representative extension applies.",
                    )
                return Deadline(
                    form_type,
                    _dt.date(2026, 5, 29),
                    "Official 2025 non-online Form 1301 planning deadline.",
                    True,
                    "Confirm whether non-online filing is allowed for the taxpayer before relying on this date.",
                )
            if profile.is_online or profile.represented_by_cpa:
                return Deadline(
                    form_type,
                    _dt.date(filing_year, 6, 30),
                    "Generic online annual individual return planning deadline for the filing year after tax year.",
                    True,
                    "Confirm the Tax Authority announcement and any representative extension for this tax year.",
                )
            return Deadline(
                form_type,
                _dt.date(filing_year, 5, 31),
                "Generic non-online annual individual return planning deadline for the filing year after tax year.",
                True,
                "Confirm whether paper filing is available and what deadline applies.",
            )

        if form_type == FormType.FORM_135:
            return Deadline(
                form_type,
                _dt.date(profile.tax_year + 6, 12, 31),
                "Refund-claim limitation planning date, commonly calculated as six years after the tax year.",
                True,
                "File earlier when the limitation period is near and verify official limitation rules.",
            )

        if form_type == FormType.FORM_126:
            if profile.tax_year == 2025:
                return Deadline(
                    form_type,
                    _dt.date(2026, 5, 31),
                    "Officially extended 2025 annual employer report planning deadline.",
                    True,
                    "Confirm online transmission and approval requirements for Form 126/856 before filing.",
                )
            return Deadline(
                form_type,
                _dt.date(filing_year, 4, 30),
                "Generic employer annual salary report planning deadline.",
                True,
                "Confirm the current payroll-report broadcast deadline.",
            )

        if form_type == FormType.FORM_856:
            if profile.tax_year == 2025:
                return Deadline(
                    form_type,
                    _dt.date(2026, 5, 31),
                    "Officially extended 2025 annual supplier-withholding report planning deadline.",
                    True,
                    "Confirm online transmission and approval requirements for Form 126/856 before filing.",
                )
            return Deadline(
                form_type,
                _dt.date(filing_year, 4, 30),
                "Generic supplier payment annual report planning deadline.",
                True,
                "Confirm current withholding-report instructions.",
            )

        if form_type == FormType.FORM_6111:
            base = self.deadline_for(FormType.FORM_1301, profile)
            return Deadline(
                form_type,
                base.due_date,
                "Standardized financial statement planning deadline aligned to the related annual return.",
                True,
                "Confirm whether Form 6111 is required and which annual return controls the deadline.",
            )

        raise UnknownFormError(f"FORM_UNKNOWN: unsupported form {form_type.value}")

    def deadlines_for(self, forms: Iterable[str | FormType], profile: FilingProfile) -> list[Deadline]:
        return [self.deadline_for(form, profile) for form in forms]


class TaxReturnAssistantClient:
    """Synchronous offline client for preparation workflows."""

    DEFAULT_6111_PLANNING_THRESHOLD_ILS = 300_000

    def __init__(
        self,
        field_repository: FieldHelpRepository | None = None,
        deadline_calculator: DeadlineCalculator | None = None,
        planning_6111_threshold_ils: float | None = None,
        profile_store: LocalProfileStore | None = None,
    ) -> None:
        self.fields = field_repository or FieldHelpRepository()
        self.deadlines = deadline_calculator or DeadlineCalculator()
        self.profile_store = profile_store or LocalProfileStore()
        self.planning_6111_threshold_ils = (
            float(planning_6111_threshold_ils)
            if planning_6111_threshold_ils is not None
            else float(self.DEFAULT_6111_PLANNING_THRESHOLD_ILS)
        )


    def create_profile(
        self, profile: FilingProfile, environment: Literal["sandbox", "production"] = "sandbox"
    ) -> StoredProfile:
        """Persist a local profile and return an ID for chained CLI commands."""

        if environment not in {"sandbox", "production"}:
            raise TaxAssistantError("ENV_INVALID: environment must be sandbox or production")
        return self.profile_store.create(profile, environment)

    def get_profile(self, profile_id: str) -> StoredProfile:
        """Return a persisted local profile by ID."""

        return self.profile_store.get(profile_id)

    def list_profile_ids(self) -> list[str]:
        """Return persisted local profile IDs."""

        return self.profile_store.list_ids()

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a persisted local profile by ID."""

        return self.profile_store.delete(profile_id)

    def generate_report_by_id(self, profile_id: str) -> dict[str, Any]:
        """Generate a report for a profile stored by CLI ID."""

        stored = self.get_profile(profile_id)
        report = self.generate_report(stored.profile)
        report["id"] = stored.profile_id
        report["environment"] = stored.environment
        return report

    def recommend_forms(self, profile: FilingProfile) -> Recommendation:
        issues = self.validate_profile(profile)
        if any(issue.code == "TAX_YEAR_MISSING" and issue.severity == "error" for issue in issues):
            forms: list[FormType] = []
        else:
            forms = []

        explanations: dict[str, str] = {}
        warnings: list[str] = []

        complex_individual = any(
            [
                profile.business_income,
                profile.foreign_income,
                profile.capital_gains,
                profile.rental_income,
                profile.taxpayer_type in {"sole_proprietor", "freelancer", "self_employed"},
            ]
        )

        if profile.salary_only and profile.wants_refund and not complex_individual:
            forms.append(FormType.FORM_135)
            explanations["135"] = (
                "Short salaried return is suitable for a salary-only refund workflow when no full "
                "annual return obligation is present."
            )
        elif complex_individual or profile.taxpayer_type in {"individual", "sole_proprietor", "freelancer", "self_employed"}:
            if complex_individual:
                forms.append(FormType.FORM_1301)
                explanations["1301"] = (
                    "Individual annual return is needed because business, rental, capital, foreign, "
                    "or other full-return facts are present."
                )

        if profile.has_employees:
            forms.append(FormType.FORM_126)
            explanations["126"] = "Employer annual salary report may be needed because employees were paid."

        if profile.paid_suppliers:
            forms.append(FormType.FORM_856)
            explanations["856"] = (
                "Supplier payments report may be needed because non-employee suppliers or service "
                "providers were paid."
            )

        if profile.annual_turnover_ils >= self.planning_6111_threshold_ils:
            forms.append(FormType.FORM_6111)
            explanations["6111"] = (
                "Standardized financial statement may be needed because annual turnover is at or "
                "above the planning threshold."
            )
            warnings.append(
                "Verify Form 6111 requirement and current threshold with official instructions for the tax year."
            )

        if profile.salary_only and profile.wants_refund and complex_individual:
            warnings.append("Form 135 is usually not enough when business, rental, foreign, or capital-gain facts exist.")

        for issue in issues:
            if issue.severity == "warning":
                warnings.append(issue.message)

        unique_forms = tuple(dict.fromkeys(forms))
        return Recommendation(unique_forms, explanations, tuple(dict.fromkeys(warnings)))

    def calculate_deadlines(
        self, profile: FilingProfile, forms: Sequence[str | FormType] | None = None
    ) -> list[Deadline]:
        if forms is None:
            forms = self.recommend_forms(profile).forms
        return self.deadlines.deadlines_for(forms, profile)

    def get_field_help(self, form: str | FormType, field_id: str | None = None) -> FieldHelp | list[FieldHelp]:
        if field_id is None:
            return self.fields.list_fields(form)
        return self.fields.get(form, field_id)

    def build_checklist(
        self, profile: FilingProfile, forms: Sequence[str | FormType] | None = None
    ) -> list[Checklist]:
        if forms is None:
            forms = self.recommend_forms(profile).forms
        result: list[Checklist] = []
        for form in forms:
            form_type = FormType.parse(form)
            items = list(_BASE_CHECKLIST[form_type])
            warnings: list[str] = []
            if form_type == FormType.FORM_1301:
                if profile.business_income:
                    items.extend(["Profit and loss report", "Expense ledger", "Income tax advances"])
                if profile.foreign_income:
                    items.append("Foreign income and foreign tax paid schedule")
                    warnings.append("Foreign income may require professional review.")
                if profile.capital_gains:
                    items.append("Bank Form 867 or broker realized-gain report")
                if profile.rental_income:
                    items.append("Rental contracts and annual rental income schedule")
            if form_type == FormType.FORM_6111:
                warnings.append("Verify current requirement and account-code mapping before filing.")
            result.append(Checklist(form_type, tuple(dict.fromkeys(items)), tuple(warnings)))
        return result

    def validate_profile(self, profile: FilingProfile) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        if profile.tax_year is None:
            issues.append(
                ValidationIssue(
                    "error",
                    "TAX_YEAR_MISSING",
                    "Tax year is required before form selection or deadline planning.",
                    "tax_year",
                    "Add a four-digit tax year.",
                )
            )
        elif profile.tax_year < 2000 or profile.tax_year > 2100:
            issues.append(
                ValidationIssue(
                    "error",
                    "TAX_YEAR_RANGE",
                    "Tax year is outside the supported planning range.",
                    "tax_year",
                    "Use a realistic tax year and verify historical instructions.",
                )
            )

        if profile.salary_only and (
            profile.business_income or profile.foreign_income or profile.capital_gains or profile.rental_income
        ):
            issues.append(
                ValidationIssue(
                    "warning",
                    "PROFILE_INCONSISTENT",
                    "Salary-only refund facts conflict with business, rental, foreign, or capital-gain income.",
                    "salary_only",
                    "Use Form 1301 workflow unless official rules allow a short return.",
                )
            )

        if profile.annual_turnover_ils < 0:
            issues.append(
                ValidationIssue(
                    "error",
                    "NEGATIVE_TURNOVER",
                    "Annual turnover cannot be negative.",
                    "annual_turnover_ils",
                    "Use zero or the correct positive turnover.",
                )
            )

        if profile.annual_turnover_ils >= self.planning_6111_threshold_ils:
            issues.append(
                ValidationIssue(
                    "warning",
                    "FORM_6111_REQUIREMENT_CHECK",
                    "Turnover is at or above the planning threshold for a Form 6111 requirement check.",
                    "annual_turnover_ils",
                    "Verify current Form 6111 instructions for the filing year.",
                )
            )

        if profile.notes and _looks_like_sensitive_data(profile.notes):
            issues.append(
                ValidationIssue(
                    "warning",
                    "PERSONAL_DATA_RISK",
                    "Notes appear to contain identity, bank, or other sensitive numeric details.",
                    "notes",
                    "Redact personal data and keep only totals or masked identifiers.",
                )
            )

        return issues

    def generate_report(self, profile: FilingProfile) -> dict[str, Any]:
        recommendation = self.recommend_forms(profile)
        deadlines = self.calculate_deadlines(profile, recommendation.forms)
        checklist = self.build_checklist(profile, recommendation.forms)
        validation = self.validate_profile(profile)
        return {
            "profile": profile.to_dict(),
            "recommendation": recommendation.to_dict(),
            "deadlines": [deadline.to_dict() for deadline in deadlines],
            "checklists": [entry.to_dict() for entry in checklist],
            "validation": [issue.to_dict() for issue in validation],
            "official_verification_required": True,
        }


class AsyncTaxReturnAssistantClient:
    """Async wrapper for the synchronous client."""

    def __init__(self, client: TaxReturnAssistantClient | None = None) -> None:
        self._client = client or TaxReturnAssistantClient()


    async def create_profile(
        self, profile: FilingProfile, environment: Literal["sandbox", "production"] = "sandbox"
    ) -> StoredProfile:
        return await asyncio.to_thread(self._client.create_profile, profile, environment)

    async def get_profile(self, profile_id: str) -> StoredProfile:
        return await asyncio.to_thread(self._client.get_profile, profile_id)

    async def list_profile_ids(self) -> list[str]:
        return await asyncio.to_thread(self._client.list_profile_ids)

    async def delete_profile(self, profile_id: str) -> bool:
        return await asyncio.to_thread(self._client.delete_profile, profile_id)

    async def generate_report_by_id(self, profile_id: str) -> dict[str, Any]:
        return await asyncio.to_thread(self._client.generate_report_by_id, profile_id)

    async def recommend_forms(self, profile: FilingProfile) -> Recommendation:
        return await asyncio.to_thread(self._client.recommend_forms, profile)

    async def calculate_deadlines(
        self, profile: FilingProfile, forms: Sequence[str | FormType] | None = None
    ) -> list[Deadline]:
        return await asyncio.to_thread(self._client.calculate_deadlines, profile, forms)

    async def get_field_help(
        self, form: str | FormType, field_id: str | None = None
    ) -> FieldHelp | list[FieldHelp]:
        return await asyncio.to_thread(self._client.get_field_help, form, field_id)

    async def build_checklist(
        self, profile: FilingProfile, forms: Sequence[str | FormType] | None = None
    ) -> list[Checklist]:
        return await asyncio.to_thread(self._client.build_checklist, profile, forms)

    async def validate_profile(self, profile: FilingProfile) -> list[ValidationIssue]:
        return await asyncio.to_thread(self._client.validate_profile, profile)

    async def generate_report(self, profile: FilingProfile) -> dict[str, Any]:
        return await asyncio.to_thread(self._client.generate_report, profile)


def _looks_like_sensitive_data(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    if len(digits) >= 9:
        return True
    return bool(re.search(r"\b\d{2,3}-\d{3,}-\d{2,}\b", value))


_BASE_CHECKLIST: dict[FormType, tuple[str, ...]] = {
    FormType.FORM_1301: (
        "Tax year confirmation",
        "Personal details and family status",
        "Form 106 from each employer, if any",
        "Business profit and loss report, if any",
        "Deductions and credits evidence",
        "Withholding and advance-payment confirmations",
        "Official deadline verification",
    ),
    FormType.FORM_135: (
        "Tax year confirmation",
        "Form 106 from each employer",
        "Refund bank account confirmation",
        "Refund reason and supporting documents",
        "Donation receipts, if claimed",
        "Limitation-period check",
        "Official deadline verification",
    ),
    FormType.FORM_126: (
        "Employer withholding file details",
        "Annual payroll export",
        "Monthly payroll registers",
        "Forms 106 issued to employees",
        "Income tax withholding payment confirmations",
        "National Insurance reports",
        "Employee identity validation",
        "Official transmission instructions",
    ),
    FormType.FORM_856: (
        "Supplier ledger cards",
        "Payment register",
        "Supplier identity details",
        "Withholding certificates by payment date",
        "Monthly withholding payment confirmations",
        "Payment type mapping",
        "Official file-format instructions",
    ),
    FormType.FORM_6111: (
        "Closed trial balance",
        "Profit and loss report",
        "Balance sheet",
        "Fixed asset and depreciation schedule",
        "Inventory and receivables schedules",
        "Tax adjustment schedule",
        "Account-code mapping",
        "Official Form 6111 requirement verification",
    ),
}


_FIELD_HELP: tuple[FieldHelp, ...] = (
    FieldHelp(FormType.FORM_1301, "personal_details", "Personal details", "פרטים אישיים", "Report taxpayer identity, address, marital status, spouse and dependents as applicable.", "Always required for Form 1301.", ("Identity details", "Family-status records", "Bank confirmation for refund"), ("Omitting leading zeros", "Using outdated address", "Mismatching spouse details")),
    FieldHelp(FormType.FORM_1301, "employment_income", "Employment income", "הכנסת עבודה", "Use Form 106 totals from every employer to report salary, taxable benefits, deductions, and tax withheld.", "Required when salary income exists.", ("Form 106", "Final payslips", "Tax coordination approvals"), ("Missing one employer", "Counting net salary instead of taxable salary", "Ignoring taxable benefits")),
    FieldHelp(FormType.FORM_1301, "business_income", "Business income", "הכנסה מעסק או משלח יד", "Report annual gross receipts, deductible expenses, and net profit from the business records.", "Required when self-employment or professional income exists.", ("Profit and loss report", "Receipt book or income export", "Expense ledger"), ("Treating owner drawings as expenses", "Mixing private and business expenses", "Not reconciling revenue")),
    FieldHelp(FormType.FORM_1301, "rental_income", "Rental income", "הכנסה משכירות", "Summarize rental income and support the selected tax track where available.", "Required when rental income exists.", ("Rental contracts", "Bank deposits", "Expense records"), ("Wrong track", "Ignoring partial ownership", "Missing foreign rental income")),
    FieldHelp(FormType.FORM_1301, "capital_gains", "Capital gains", "רווחי הון", "Report realized gains, losses, withholding, and supporting schedules.", "Required when securities, assets, or other capital gains exist.", ("Form 867", "Broker statements", "Transaction reports"), ("Using unrealized gains", "Forgetting foreign broker reports", "Not carrying losses correctly")),
    FieldHelp(FormType.FORM_1301, "foreign_income", "Foreign income", "הכנסות מחו״ל", "Classify foreign-source income and collect evidence for foreign tax paid and reporting relief if claimed.", "Required when foreign income or assets exist.", ("Foreign statements", "Foreign tax certificates", "Residency/relief evidence"), ("Assuming automatic exemption", "Missing currency conversion", "Ignoring disclosure obligations")),
    FieldHelp(FormType.FORM_1301, "donations_46", "Recognized donations", "תרומות לפי סעיף 46", "Use receipts from recognized institutions and verify taxpayer name and tax year.", "Required when claiming donation credit.", ("Donation receipt", "Institution recognition evidence"), ("Receipt not in taxpayer name", "Wrong tax year", "Institution not recognized")),
    FieldHelp(FormType.FORM_1301, "prepayments", "Prepayments and withholding", "מקדמות וניכוי במקור", "Credit income-tax advances and withholding against final liability.", "Required when tax was prepaid or withheld.", ("Tax Authority account statement", "Withholding certificates", "Payment confirmations"), ("Payment posted to wrong year", "Duplicate withholding", "Spouse allocation error")),

    FieldHelp(FormType.FORM_135, "employee_details", "Employee details", "פרטי עובד", "Identify the refund claimant and refund bank account.", "Always required for Form 135.", ("Identity details", "Bank confirmation"), ("Closed bank account", "Address mismatch", "Unnecessary full ID copies")),
    FieldHelp(FormType.FORM_135, "form_106_totals", "Form 106 totals", "סיכומי טופס 106", "Combine all annual employer certificates for the tax year.", "Required when salary income exists.", ("Form 106 from each employer", "Final payslips if Form 106 is missing"), ("Missing employer", "Using monthly payslips as final totals", "Overlapping jobs not reconciled")),
    FieldHelp(FormType.FORM_135, "refund_reason", "Refund reason", "סיבת ההחזר", "Explain the credit, deduction, employment gap, or coordination issue that may create a refund.", "Required when claiming a refund.", ("Donation receipts", "Tax coordination", "National Insurance certificates", "Pension certificates"), ("Credit already used by employer", "No evidence", "Duplicate spouse claim")),
    FieldHelp(FormType.FORM_135, "limitation_period", "Limitation period", "תקופת התיישנות", "Check the latest practical date for claiming a refund for the tax year.", "Required for older years.", ("Tax year", "Filing date"), ("Waiting until year-end", "Using filing year as tax year", "Ignoring official limitation rules")),

    FieldHelp(FormType.FORM_126, "employer_id", "Employer identification", "זיהוי מעסיק", "Use the withholding file and registered employer details.", "Always required for Form 126.", ("Withholding file details", "Payroll software settings"), ("Wrong withholding file", "Branch confusion", "Old employer name")),
    FieldHelp(FormType.FORM_126, "employee_id", "Employee identity", "זיהוי עובד", "Report each employee with valid identity details and employment months.", "Required for every employee.", ("Employee master file", "Employment agreements", "Payroll register"), ("Invalid check digit", "Missing leading zero", "Duplicate employee")),
    FieldHelp(FormType.FORM_126, "taxable_salary", "Taxable salary", "שכר חייב", "Report annual taxable salary and benefits per employee.", "Required when wages were paid.", ("Annual payroll export", "Monthly payslips", "Form 106"), ("Net salary used", "Benefits omitted", "Retroactive pay missing")),
    FieldHelp(FormType.FORM_126, "tax_withheld", "Tax withheld", "מס שנוכה", "Report income tax withheld from salary and reconcile to monthly payments.", "Required when tax was withheld.", ("Payroll ledger", "Payment confirmations"), ("Payment posted to wrong month", "Negative correction ignored", "Rounding mismatch")),
    FieldHelp(FormType.FORM_126, "national_insurance", "National Insurance", "ביטוח לאומי ומס בריאות", "Reconcile National Insurance and health tax deductions and employer portions where relevant.", "Required for employee payroll reporting.", ("National Insurance reports", "Payroll export"), ("Wrong employee category", "Maternity/reserve duty not handled", "Mismatch to monthly reports")),

    FieldHelp(FormType.FORM_856, "supplier_id", "Supplier identification", "זיהוי ספק", "Report the legal recipient identity: individual ID, authorized dealer, company, or other registered number.", "Required for every reported supplier.", ("Supplier master data", "Invoices", "Withholding certificate"), ("Using trade name instead of legal entity", "Wrong company number", "Merging two entities")),
    FieldHelp(FormType.FORM_856, "payment_type", "Payment type", "סוג תשלום", "Classify the payment type according to current instructions.", "Required for every payment record.", ("Invoice", "Contract", "Ledger card"), ("Mixing goods and services", "Employee wage reported as supplier", "Foreign supplier not reviewed")),
    FieldHelp(FormType.FORM_856, "gross_payment", "Gross payment", "סכום תשלום ברוטו", "Report annual gross reportable payments using the base required by current instructions.", "Required when a reportable payment exists.", ("Payment register", "Supplier ledger", "Invoices and credit notes"), ("VAT base confusion", "Credit notes omitted", "Negative annual total")),
    FieldHelp(FormType.FORM_856, "withholding_rate", "Withholding rate", "שיעור ניכוי במקור", "Use the valid Tax Authority withholding certificate for each payment date; split periods when rates change.", "Required when withholding rules apply.", ("Supplier withholding certificate", "Payment dates", "Supplier ledger"), ("Expired certificate", "Certificate belongs to another entity", "Applying one rate to the full year")),
    FieldHelp(FormType.FORM_856, "tax_withheld", "Tax withheld", "מס שנוכה במקור", "Report tax actually withheld and reconcile to remittances.", "Required when tax was withheld.", ("Withholding payment confirmations", "Supplier ledger"), ("Withheld but not remitted", "Rounding mismatch", "Wrong month")),

    FieldHelp(FormType.FORM_6111, "reporting_period", "Reporting period", "תקופת הדיווח", "Identify the tax year and accounting period covered by the standardized financial statement.", "Always required for Form 6111.", ("Trial balance", "Entity records"), ("Short year not marked", "Wrong tax year", "Old entity details")),
    FieldHelp(FormType.FORM_6111, "revenue", "Revenue", "הכנסות", "Map revenue accounts to the correct standardized item codes.", "Required when business revenue exists.", ("Closed trial balance", "P&L report", "VAT reconciliation"), ("Revenue mismatch", "Manual journals omitted", "Wrong code mapping")),
    FieldHelp(FormType.FORM_6111, "expenses", "Expenses", "הוצאות", "Map operating, salary, rent, finance, depreciation, and other expenses to standardized codes.", "Required when expenses exist.", ("P&L report", "Expense ledger", "Payroll summary"), ("Private expenses included", "Non-deductible fines not adjusted", "Depreciation mismatch")),
    FieldHelp(FormType.FORM_6111, "balance_sheet", "Balance sheet", "מאזן", "Map assets, liabilities, and equity balances after year-end close.", "Required when balance sheet reporting applies.", ("Balance sheet", "Trial balance", "Bank reconciliation"), ("Balance sheet does not balance", "Opening balances wrong", "Owner drawings misclassified")),
    FieldHelp(FormType.FORM_6111, "tax_adjustments", "Tax adjustments", "התאמות למס", "Document accounting-to-tax adjustments such as depreciation differences and non-deductible expenses.", "Required when accounting profit differs from taxable income.", ("Tax adjustment schedule", "Depreciation schedule", "Prior-year loss support"), ("No support for adjustments", "Loss carryforward not approved", "Fines deducted")),
)


def default_profile() -> FilingProfile:
    """Return a safe example profile without personal identifiers."""

    return FilingProfile(
        tax_year=_dt.date.today().year - 1,
        taxpayer_type="sole_proprietor",
        salary_only=False,
        wants_refund=False,
        business_income=True,
        annual_turnover_ils=0,
        has_employees=False,
        paid_suppliers=False,
        foreign_income=False,
        capital_gains=False,
        rental_income=False,
        is_online=True,
        represented_by_cpa=False,
    )


__all__ = [
    "AsyncTaxReturnAssistantClient",
    "Checklist",
    "Deadline",
    "DeadlineCalculator",
    "FieldHelp",
    "FieldHelpRepository",
    "FilingProfile",
    "LocalProfileStore",
    "FormType",
    "Recommendation",
    "StoredProfile",
    "TaxAssistantError",
    "TaxReturnAssistantClient",
    "UnknownFieldError",
    "UnknownFormError",
    "ValidationIssue",
    "default_profile",
    "format_date",
    "format_ils",
    "load_profile",
    "save_json",
]
