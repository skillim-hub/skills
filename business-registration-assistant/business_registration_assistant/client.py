"""Structured helper for Israeli business registration preparation.

The module does not submit data to government systems. It produces deterministic
classification, checklist, warning, storage, and handoff outputs suitable for
review by a user, accountant, tax adviser, or authority representative.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Mapping


Status = Literal["osek_patur", "osek_murshe", "needs_review"]
Severity = Literal["info", "warning", "error"]


class RegistrationError(ValueError):
    """Raised when intake data is invalid."""


class WarningCode(str, Enum):
    CURRENT_THRESHOLD_REQUIRED = "CURRENT_THRESHOLD_REQUIRED"
    TURNOVER_EXCEEDS_CEILING = "TURNOVER_EXCEEDS_CEILING"
    REGULATED_PROFESSION = "REGULATED_PROFESSION"
    CLIENT_REQUIRES_TAX_INVOICE = "CLIENT_REQUIRES_TAX_INVOICE"
    LARGE_VAT_EXPENSES = "LARGE_VAT_EXPENSES"
    FOREIGN_CLIENT_VAT_COMPLEXITY = "FOREIGN_CLIENT_VAT_COMPLEXITY"
    BENEFIT_INTERACTION = "BENEFIT_INTERACTION"
    EMPLOYEE_PLUS_SELF_EMPLOYED = "EMPLOYEE_PLUS_SELF_EMPLOYED"
    PRIOR_FILE_REOPEN = "PRIOR_FILE_REOPEN"
    LATE_REGISTRATION = "LATE_REGISTRATION"
    IMPORT_EXPORT_COMPLEXITY = "IMPORT_EXPORT_COMPLEXITY"
    CASH_ACTIVITY = "CASH_ACTIVITY"
    BUSINESS_LICENSE_REVIEW = "BUSINESS_LICENSE_REVIEW"
    VAT_STATUS_NOT_TAX_EXEMPT = "VAT_STATUS_NOT_TAX_EXEMPT"


class ErrorCode(str, Enum):
    MISSING_ACTIVITY = "MISSING_ACTIVITY"
    MISSING_TURNOVER = "MISSING_TURNOVER"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    BANK_DOCUMENT_MISSING = "BANK_DOCUMENT_MISSING"
    CASE_NOT_FOUND = "CASE_NOT_FOUND"


@dataclass(frozen=True)
class Issue:
    code: str
    severity: Severity
    message: str


@dataclass(frozen=True)
class BusinessIntake:
    activity_description: str
    expected_annual_turnover_nis: float
    expected_monthly_profit_nis: float | None = None
    current_osek_patur_ceiling_nis: float | None = None
    planned_start_date: str | None = None
    actual_start_date: str | None = None
    registration_date: str | None = None
    regulated_profession: bool = False
    clients_require_tax_invoice: bool = False
    large_vat_bearing_expenses: bool = False
    foreign_clients: bool = False
    online_sales: bool = False
    import_export: bool = False
    currently_employee: bool = False
    receives_benefits: bool = False
    prior_self_employment_file: bool = False
    cash_payments: bool = False
    home_food_or_licensed_activity: bool = False
    work_location: str = "home"
    bank_ownership_confirmation: bool = True
    weekly_hours: float | None = None
    client_types: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "BusinessIntake":
        business = data.get("business", data)
        if not isinstance(business, Mapping):
            raise RegistrationError("business must be an object")

        activity = business.get("activity_description") or business.get("activity") or ""
        turnover = business.get("expected_annual_turnover_nis", business.get("turnover"))
        profit = business.get("expected_monthly_profit_nis", business.get("profit_monthly"))
        client_types_raw = business.get("client_types", ())

        if isinstance(client_types_raw, str):
            client_types = (client_types_raw,)
        else:
            client_types = tuple(client_types_raw or ())

        return cls(
            activity_description=str(activity),
            expected_annual_turnover_nis=_as_amount(turnover, "expected_annual_turnover_nis"),
            expected_monthly_profit_nis=_optional_amount(profit, "expected_monthly_profit_nis"),
            current_osek_patur_ceiling_nis=_optional_amount(
                business.get("current_osek_patur_ceiling_nis", business.get("ceiling")),
                "current_osek_patur_ceiling_nis",
            ),
            planned_start_date=_optional_str(business.get("planned_start_date")),
            actual_start_date=_optional_str(business.get("actual_start_date")),
            registration_date=_optional_str(business.get("registration_date")),
            regulated_profession=bool(business.get("regulated_profession", False)),
            clients_require_tax_invoice=bool(business.get("clients_require_tax_invoice", False)),
            large_vat_bearing_expenses=bool(business.get("large_vat_bearing_expenses", False)),
            foreign_clients=bool(business.get("foreign_clients", False)),
            online_sales=bool(business.get("online_sales", False)),
            import_export=bool(business.get("import_export", False)),
            currently_employee=bool(business.get("currently_employee", False)),
            receives_benefits=bool(business.get("receives_benefits", False)),
            prior_self_employment_file=bool(business.get("prior_self_employment_file", False)),
            cash_payments=bool(business.get("cash_payments", False)),
            home_food_or_licensed_activity=bool(
                business.get("home_food_or_licensed_activity", False)
            ),
            work_location=str(business.get("work_location", "home") or "home"),
            bank_ownership_confirmation=bool(business.get("bank_ownership_confirmation", True)),
            weekly_hours=_optional_amount(business.get("weekly_hours"), "weekly_hours"),
            client_types=client_types,
        )


@dataclass(frozen=True)
class Classification:
    recommended_status: Status
    confidence: Literal["low", "medium", "high"]
    reasons: tuple[str, ...]
    issues: tuple[Issue, ...]
    next_actions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommended_status": self.recommended_status,
            "confidence": self.confidence,
            "reasons": list(self.reasons),
            "issues": [asdict(issue) for issue in self.issues],
            "next_actions": list(self.next_actions),
        }


@dataclass(frozen=True)
class Checklist:
    required: tuple[str, ...]
    conditional: tuple[str, ...]
    missing: tuple[str, ...]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuthorityPlan:
    vat: tuple[str, ...]
    income_tax: tuple[str, ...]
    national_insurance: tuple[str, ...]
    bookkeeping: tuple[str, ...]
    professional_review: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FullPlan:
    intake: BusinessIntake
    classification: Classification
    checklist: Checklist
    authority_plan: AuthorityPlan

    def to_dict(self) -> dict[str, Any]:
        return {
            "intake": asdict(self.intake),
            "classification": self.classification.to_dict(),
            "checklist": self.checklist.to_dict(),
            "authority_plan": self.authority_plan.to_dict(),
        }


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_amount(value: Any, field_name: str) -> float:
    if value is None or value == "":
        raise RegistrationError(f"{ErrorCode.MISSING_TURNOVER.value}: {field_name} is required")
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise RegistrationError(f"{ErrorCode.INVALID_AMOUNT.value}: {field_name}") from exc
    if amount < 0:
        raise RegistrationError(f"{ErrorCode.INVALID_AMOUNT.value}: {field_name}")
    return amount


def _optional_amount(value: Any, field_name: str) -> float | None:
    if value is None or value == "":
        return None
    return _as_amount(value, field_name)


def _activity_is_vague(activity: str) -> bool:
    stripped = activity.strip()
    return len(stripped) < 3 or stripped.lower() in {"business", "freelance", "services", "work"}


def _activity_suggests_license(activity: str) -> bool:
    terms = {
        "architect",
        "architecture",
        "engineer",
        "engineering",
        "lawyer",
        "attorney",
        "doctor",
        "physician",
        "dentist",
        "accountant",
        "cpa",
        "appraiser",
        "surveyor",
        "insurance agent",
        "clinical",
        "therapy",
        "therapist",
        "אדריכל",
        "אדריכלות",
        "מהנדס",
        "הנדסה",
        "עורך דין",
        "רופא",
        "רופאה",
        "רואה חשבון",
        "שמאי",
        "מטפל קליני",
        "פסיכולוג",
    }
    lowered = activity.lower()
    return any(term in lowered for term in terms)


def _issue(code: WarningCode | ErrorCode | str, severity: Severity, message: str) -> Issue:
    return Issue(code=str(code.value if isinstance(code, Enum) else code), severity=severity, message=message)


def load_json_store(path: str | Path) -> dict[str, Any]:
    store_path = Path(path)
    if not store_path.exists():
        return {"cases": {}}
    return json.loads(store_path.read_text(encoding="utf-8"))


def save_json_store(path: str | Path, data: Mapping[str, Any]) -> None:
    store_path = Path(path)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_intake(path: str | Path) -> BusinessIntake:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError("PyYAML is required to load YAML files") from exc
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    return BusinessIntake.from_mapping(data)


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)


class BusinessRegistrationClient:
    """Deterministic helper for registration preparation."""

    def validate_intake(self, intake: BusinessIntake) -> tuple[Issue, ...]:
        issues: list[Issue] = []
        if _activity_is_vague(intake.activity_description):
            issues.append(
                _issue(ErrorCode.MISSING_ACTIVITY, "error", "Provide an exact business activity description.")
            )
        if intake.expected_annual_turnover_nis < 0:
            issues.append(
                _issue(ErrorCode.INVALID_AMOUNT, "error", "Expected annual turnover must be non-negative.")
            )
        if intake.expected_monthly_profit_nis is not None and intake.expected_monthly_profit_nis < 0:
            issues.append(
                _issue(ErrorCode.INVALID_AMOUNT, "error", "Expected monthly profit must be non-negative.")
            )
        if not intake.bank_ownership_confirmation:
            issues.append(
                _issue(
                    ErrorCode.BANK_DOCUMENT_MISSING,
                    "error",
                    "Prepare bank ownership confirmation, cancelled check, or bank letter.",
                )
            )
        return tuple(issues)

    def classify_status(self, intake: BusinessIntake) -> Classification:
        validation_issues = list(self.validate_intake(intake))
        hard_errors = [
            issue
            for issue in validation_issues
            if issue.severity == "error" and issue.code != ErrorCode.BANK_DOCUMENT_MISSING.value
        ]
        if hard_errors:
            return Classification(
                recommended_status="needs_review",
                confidence="low",
                reasons=("Required classification data is missing or invalid.",),
                issues=tuple(validation_issues),
                next_actions=("Correct intake data before choosing VAT status.",),
            )

        issues: list[Issue] = list(validation_issues)
        reasons: list[str] = []
        next_actions: list[str] = [
            "Verify current Tax Authority thresholds and occupation rules before filing.",
            "Prepare separate VAT, income tax, and Bituach Leumi steps.",
        ]

        regulated = intake.regulated_profession or _activity_suggests_license(intake.activity_description)
        exceeds_ceiling = False
        threshold_known = intake.current_osek_patur_ceiling_nis is not None

        if not threshold_known:
            issues.append(
                _issue(
                    WarningCode.CURRENT_THRESHOLD_REQUIRED,
                    "warning",
                    "Verify the current annual exempt dealer ceiling before filing.",
                )
            )
        else:
            ceiling = float(intake.current_osek_patur_ceiling_nis)
            if intake.expected_annual_turnover_nis > ceiling:
                exceeds_ceiling = True
                issues.append(
                    _issue(
                        WarningCode.TURNOVER_EXCEEDS_CEILING,
                        "warning",
                        "Expected annual turnover exceeds the supplied exempt dealer ceiling.",
                    )
                )
                reasons.append("Expected turnover exceeds the supplied exempt dealer ceiling.")
            else:
                reasons.append("Expected turnover is within the supplied exempt dealer ceiling.")

        if regulated:
            issues.append(
                _issue(
                    WarningCode.REGULATED_PROFESSION,
                    "warning",
                    "Activity may be excluded from עוסק פטור regardless of turnover.",
                )
            )
            reasons.append("Regulated or professional activity may require עוסק מורשה.")

        if intake.clients_require_tax_invoice:
            issues.append(
                _issue(
                    WarningCode.CLIENT_REQUIRES_TAX_INVOICE,
                    "warning",
                    "עוסק פטור cannot issue VAT tax invoices.",
                )
            )
            reasons.append("Clients require VAT tax invoices.")

        if intake.large_vat_bearing_expenses:
            issues.append(
                _issue(
                    WarningCode.LARGE_VAT_EXPENSES,
                    "warning",
                    "Large VAT-bearing expenses may make עוסק מורשה commercially preferable.",
                )
            )

        if intake.foreign_clients:
            issues.append(
                _issue(
                    WarningCode.FOREIGN_CLIENT_VAT_COMPLEXITY,
                    "warning",
                    "Foreign-client VAT treatment can be complex and needs professional review.",
                )
            )

        if intake.import_export:
            issues.append(
                _issue(
                    WarningCode.IMPORT_EXPORT_COMPLEXITY,
                    "warning",
                    "Import/export activity can create VAT, customs, and documentation complexity.",
                )
            )

        if intake.currently_employee:
            issues.append(
                _issue(
                    WarningCode.EMPLOYEE_PLUS_SELF_EMPLOYED,
                    "warning",
                    "Salaried employment does not remove the need to report self-employed income.",
                )
            )

        if intake.receives_benefits:
            issues.append(
                _issue(
                    WarningCode.BENEFIT_INTERACTION,
                    "warning",
                    "Self-employed income may affect Bituach Leumi benefits or unemployment.",
                )
            )

        if intake.prior_self_employment_file:
            issues.append(
                _issue(
                    WarningCode.PRIOR_FILE_REOPEN,
                    "warning",
                    "Prior self-employment file may require reopening checks and debt or credit review.",
                )
            )

        if intake.actual_start_date and intake.registration_date and intake.actual_start_date != intake.registration_date:
            issues.append(
                _issue(
                    WarningCode.LATE_REGISTRATION,
                    "warning",
                    "Activity date and registration date differ; check late-registration handling.",
                )
            )

        if intake.cash_payments:
            issues.append(
                _issue(
                    WarningCode.CASH_ACTIVITY,
                    "warning",
                    "Cash income must be documented and cash-use limits may apply.",
                )
            )

        if intake.home_food_or_licensed_activity:
            issues.append(
                _issue(
                    WarningCode.BUSINESS_LICENSE_REVIEW,
                    "warning",
                    "Activity may require municipal or professional licensing beyond tax registration.",
                )
            )

        issues.append(
            _issue(
                WarningCode.VAT_STATUS_NOT_TAX_EXEMPT,
                "info",
                "עוסק פטור is generally exempt from VAT collection, not from income tax or Bituach Leumi.",
            )
        )

        if exceeds_ceiling or regulated:
            status: Status = "osek_murshe"
            confidence = "high" if exceeds_ceiling else "medium"
            next_actions.append("Prepare authorized dealer VAT setup and VAT invoice process.")
        elif intake.clients_require_tax_invoice:
            status = "osek_murshe"
            confidence = "medium"
            next_actions.append("Confirm client invoice requirements and pricing before registration.")
        elif intake.large_vat_bearing_expenses or intake.import_export:
            status = "needs_review"
            confidence = "medium"
            reasons.append("Commercial VAT recovery or import/export treatment needs comparison.")
            next_actions.append("Compare עוסק פטור and עוסק מורשה with an accountant.")
        elif not threshold_known:
            status = "needs_review"
            confidence = "medium"
            reasons.append("Likely status depends on the current exempt dealer ceiling.")
        else:
            status = "osek_patur"
            confidence = "medium"
            reasons.append("No supplied fact requires authorized dealer status.")
            next_actions.append("Prepare exempt dealer receipt and annual turnover tracking process.")

        if not reasons:
            reasons.append("Classification requires more specific facts.")

        return Classification(
            recommended_status=status,
            confidence=confidence,
            reasons=tuple(dict.fromkeys(reasons)),
            issues=tuple(issues),
            next_actions=tuple(dict.fromkeys(next_actions)),
        )

    async def aclassify_status(self, intake: BusinessIntake) -> Classification:
        await asyncio.sleep(0)
        return self.classify_status(intake)

    def build_document_checklist(self, intake: BusinessIntake, status: Status | None = None) -> Checklist:
        classification = self.classify_status(intake) if status is None else None
        chosen_status = status or classification.recommended_status

        required = [
            "ID card and appendix or equivalent identity document",
            "Bank ownership confirmation, cancelled check, or bank letter",
            "Current address and contact details",
            "Planned start date",
            "Exact business activity description in Hebrew",
            "Expected annual turnover in ₪",
            "Expected monthly profit in ₪",
            "Expected weekly work hours for Bituach Leumi",
        ]
        conditional: list[str] = []
        missing: list[str] = []
        notes: list[str] = []

        if not intake.bank_ownership_confirmation:
            missing.append("Bank ownership confirmation")

        if intake.work_location not in {"home", "client_sites", "online", ""}:
            required.append("Lease, office agreement, or permission to use premises")

        if intake.regulated_profession or _activity_suggests_license(intake.activity_description):
            conditional.append("Professional license, registration certificate, or regulator approval")

        if intake.foreign_clients:
            conditional.extend(
                [
                    "Foreign client contracts",
                    "Customer residency or status evidence where relevant",
                    "Foreign payment processor statements",
                    "Currency conversion records",
                ]
            )

        if intake.online_sales:
            conditional.extend(
                [
                    "Platform seller reports",
                    "Payout statements",
                    "Platform fee records",
                    "Refund and chargeback records",
                ]
            )

        if intake.import_export:
            conditional.extend(["Import/export documents", "Customs and shipping records"])

        if intake.currently_employee:
            conditional.append("Recent salary information for tax and Bituach Leumi coordination")

        if intake.receives_benefits:
            conditional.append("Benefit or unemployment details for Bituach Leumi review")

        if intake.prior_self_employment_file:
            conditional.append("Prior file numbers and closure confirmations")

        if chosen_status == "osek_murshe":
            notes.append("Configure software for VAT tax invoices and VAT return tracking.")
        elif chosen_status == "osek_patur":
            notes.append("Configure software for receipts and annual turnover monitoring.")
        else:
            notes.append("Resolve review issues before final filing.")

        return Checklist(
            required=tuple(dict.fromkeys(required)),
            conditional=tuple(dict.fromkeys(conditional)),
            missing=tuple(dict.fromkeys(missing)),
            notes=tuple(dict.fromkeys(notes)),
        )

    async def abuild_document_checklist(self, intake: BusinessIntake, status: Status | None = None) -> Checklist:
        await asyncio.sleep(0)
        return self.build_document_checklist(intake, status)

    def build_authority_plan(self, intake: BusinessIntake, classification: Classification | None = None) -> AuthorityPlan:
        classification = classification or self.classify_status(intake)
        status = classification.recommended_status

        vat: list[str] = []
        income_tax: list[str] = [
            "Open income tax file for self-employed activity.",
            "Provide expected turnover, expected profit, activity description, and start date.",
            "Check whether clients require withholding tax and bookkeeping certificates.",
        ]
        national_insurance: list[str] = [
            "Report self-employed activity to Bituach Leumi separately from VAT and income tax.",
            "Provide expected monthly profit and weekly work hours.",
            "Update estimates when income or hours materially change.",
        ]
        bookkeeping: list[str] = [
            "Set up compliant bookkeeping before issuing documents.",
            "Keep income, expense, bank, and platform records in monthly folders.",
        ]
        professional_review: list[str] = []

        if status == "osek_patur":
            vat.extend(
                [
                    "Open VAT file as עוסק פטור after current ceiling and occupation checks.",
                    "Issue receipts, not VAT tax invoices.",
                    "Track annual turnover and annual exempt dealer declaration obligations.",
                ]
            )
        elif status == "osek_murshe":
            vat.extend(
                [
                    "Open VAT file as עוסק מורשה.",
                    "Charge VAT on taxable transactions and issue VAT tax invoices.",
                    "Calendar periodic VAT returns and payment deadlines.",
                ]
            )
        else:
            vat.extend(
                [
                    "Do not finalize VAT status until review issues are resolved.",
                    "Compare עוסק פטור and עוסק מורשה using current thresholds and occupation rules.",
                ]
            )

        review_codes = {
            WarningCode.REGULATED_PROFESSION.value,
            WarningCode.FOREIGN_CLIENT_VAT_COMPLEXITY.value,
            WarningCode.IMPORT_EXPORT_COMPLEXITY.value,
            WarningCode.BENEFIT_INTERACTION.value,
            WarningCode.LATE_REGISTRATION.value,
            WarningCode.PRIOR_FILE_REOPEN.value,
            WarningCode.BUSINESS_LICENSE_REVIEW.value,
        }
        for issue in classification.issues:
            if issue.code in review_codes:
                professional_review.append(issue.message)

        if intake.currently_employee:
            national_insurance.append("Mention concurrent salaried employment.")
            income_tax.append("Check whether tax coordination is needed.")

        if intake.receives_benefits:
            national_insurance.append("Confirm benefit impact before activity begins or payments are received.")

        if intake.foreign_clients:
            bookkeeping.append("Keep contracts, foreign-client status evidence, platform reports, and currency records.")

        if intake.cash_payments:
            bookkeeping.append("Issue receipts for cash income and observe cash-use restrictions.")

        return AuthorityPlan(
            vat=tuple(dict.fromkeys(vat)),
            income_tax=tuple(dict.fromkeys(income_tax)),
            national_insurance=tuple(dict.fromkeys(national_insurance)),
            bookkeeping=tuple(dict.fromkeys(bookkeeping)),
            professional_review=tuple(dict.fromkeys(professional_review)),
        )

    async def abuild_authority_plan(self, intake: BusinessIntake, classification: Classification | None = None) -> AuthorityPlan:
        await asyncio.sleep(0)
        return self.build_authority_plan(intake, classification)

    def build_full_plan(self, intake: BusinessIntake) -> FullPlan:
        classification = self.classify_status(intake)
        checklist = self.build_document_checklist(intake, classification.recommended_status)
        authority_plan = self.build_authority_plan(intake, classification)
        return FullPlan(intake=intake, classification=classification, checklist=checklist, authority_plan=authority_plan)

    async def abuild_full_plan(self, intake: BusinessIntake) -> FullPlan:
        classification = await self.aclassify_status(intake)
        checklist = await self.abuild_document_checklist(intake, classification.recommended_status)
        authority_plan = await self.abuild_authority_plan(intake, classification)
        return FullPlan(intake=intake, classification=classification, checklist=checklist, authority_plan=authority_plan)

    def create_case(self, intake: BusinessIntake, store_path: str | Path) -> dict[str, Any]:
        store = load_json_store(store_path)
        case_id = f"case_{uuid.uuid4().hex[:12]}"
        store.setdefault("cases", {})[case_id] = asdict(intake)
        save_json_store(store_path, store)
        return {"id": case_id, "status": "created", "store_path": str(store_path)}

    async def acreate_case(self, intake: BusinessIntake, store_path: str | Path) -> dict[str, Any]:
        await asyncio.sleep(0)
        return self.create_case(intake, store_path)

    def get_case(self, case_id: str, store_path: str | Path) -> BusinessIntake:
        store = load_json_store(store_path)
        try:
            data = store["cases"][case_id]
        except KeyError as exc:
            raise RegistrationError(f"{ErrorCode.CASE_NOT_FOUND.value}: {case_id}") from exc
        return BusinessIntake.from_mapping(data)

    async def aget_case(self, case_id: str, store_path: str | Path) -> BusinessIntake:
        await asyncio.sleep(0)
        return self.get_case(case_id, store_path)

    def build_plan_for_case(self, case_id: str, store_path: str | Path) -> FullPlan:
        return self.build_full_plan(self.get_case(case_id, store_path))

    async def abuild_plan_for_case(self, case_id: str, store_path: str | Path) -> FullPlan:
        intake = await self.aget_case(case_id, store_path)
        return await self.abuild_full_plan(intake)

    def migration_checklist(
        self,
        year_to_date_turnover_nis: float,
        forecast_remaining_turnover_nis: float,
        current_osek_patur_ceiling_nis: float,
    ) -> dict[str, Any]:
        ytd = _as_amount(year_to_date_turnover_nis, "year_to_date_turnover_nis")
        forecast = _as_amount(forecast_remaining_turnover_nis, "forecast_remaining_turnover_nis")
        ceiling = _as_amount(current_osek_patur_ceiling_nis, "current_osek_patur_ceiling_nis")
        total = ytd + forecast
        needed = total > ceiling
        return {
            "migration_needed": needed,
            "forecast_total_nis": total,
            "ceiling_nis": ceiling,
            "gap_nis": total - ceiling,
            "actions": [
                "Verify current exempt dealer ceiling.",
                "Contact accountant or VAT office before crossing the ceiling.",
                "Update invoice software for VAT invoices if migration is required.",
                "Clarify whether existing prices are before VAT or including VAT.",
                "Update Bituach Leumi and income tax estimates if profit changed.",
            ],
            "warnings": [
                "Do not delay receipts or split income artificially to avoid migration.",
                "Calculate turnover before expenses.",
            ],
        }

    def accountant_handoff(self, intake: BusinessIntake) -> dict[str, Any]:
        plan = self.build_full_plan(intake)
        return {
            "goal": "Open or update Israeli self-employed business files",
            "requested_or_recommended_vat_status": plan.classification.recommended_status,
            "confidence": plan.classification.confidence,
            "activity_description": intake.activity_description,
            "planned_start_date": intake.planned_start_date,
            "expected_annual_turnover_nis": intake.expected_annual_turnover_nis,
            "expected_monthly_profit_nis": intake.expected_monthly_profit_nis,
            "weekly_hours": intake.weekly_hours,
            "client_types": list(intake.client_types),
            "issues": [asdict(issue) for issue in plan.classification.issues],
            "documents_required": list(plan.checklist.required),
            "documents_conditional": list(plan.checklist.conditional),
            "questions": [
                "Confirm current annual exempt dealer ceiling.",
                "Confirm occupation eligibility for עוסק פטור.",
                "Confirm income tax advances and certificate needs.",
                "Confirm Bituach Leumi classification and contribution estimate.",
            ],
        }
