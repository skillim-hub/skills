"""Offline preliminary checker for common Israeli National Insurance benefits.

The module provides deterministic screening rules for operational triage. It does not call
government systems and does not decide entitlement. Verify all outputs against current National
Insurance Institute instructions, Employment Service status, medical committee decisions, and
applicable law before advising a claimant.
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Sequence

Status = Literal[
    "likely_eligible",
    "possibly_eligible",
    "not_likely",
    "insufficient_information",
]
Confidence = Literal["high", "medium", "low"]
Environment = Literal["sandbox", "production"]


class BenefitType(str, Enum):
    """Supported benefit families."""

    UNEMPLOYMENT = "unemployment"
    GENERAL_DISABILITY = "general_disability"
    CHILD_ALLOWANCE = "child_allowance"
    INCOME_SUPPLEMENT = "income_supplement"


class EmploymentStatus(str, Enum):
    """Normalized employment categories."""

    EMPLOYEE = "employee"
    SELF_EMPLOYED = "self_employed"
    MIXED = "mixed"
    UNEMPLOYED = "unemployed"
    NOT_WORKING = "not_working"
    UNPAID_LEAVE = "unpaid_leave"
    BUSINESS_OWNER = "business_owner"


class TerminationReason(str, Enum):
    """Normalized termination reasons for unemployment checks."""

    LAID_OFF = "laid_off"
    FIRED = "fired"
    END_OF_CONTRACT = "end_of_contract"
    RESIGNED = "resigned"
    RESIGNED_JUSTIFIED = "resigned_justified"
    UNPAID_LEAVE = "unpaid_leave"
    BUSINESS_CLOSED = "business_closed"
    UNKNOWN = "unknown"


class HouseholdType(str, Enum):
    """Household categories used for means-tested benefits."""

    SINGLE = "single"
    COUPLE = "couple"
    SINGLE_PARENT = "single_parent"


@dataclass(slots=True)
class ApplicantProfile:
    """Input profile for preliminary screening.

    Keep identity numbers, medical records, bank documents, and employer files outside this
    object unless a secure application layer is added. Amount fields are monthly New Israeli
    Shekel values.
    """

    age: int
    resident: bool
    employment_status: str = EmploymentStatus.NOT_WORKING.value
    monthly_income: float = 0.0
    spouse_income: float = 0.0
    children_count: int = 0
    dependents: int = 0
    household_type: str = HouseholdType.SINGLE.value
    qualifying_months: int = 0
    termination_reason: str = TerminationReason.UNKNOWN.value
    registered_employment_service: bool = False
    registered_within_3_months: bool = True
    claim_date: str | None = None
    birth_dates: list[str] = field(default_factory=list)
    medical_disability_percent: float | None = None
    highest_single_impairment_percent: float | None = None
    work_capacity_loss_percent: float | None = None
    assets_exceed_limit: bool = False
    vehicle_value_exceeds_limit: bool = False
    receives_other_benefit: bool = False
    alimony_or_pension_income: float = 0.0
    military_or_national_service_release_date: str | None = None
    business_closed: bool = False
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ApplicantProfile":
        """Create a profile from a mapping while ignoring unsupported keys."""

        fields = cls.__dataclass_fields__
        cleaned = {key: value for key, value in data.items() if key in fields}
        if "children" in data and "children_count" not in cleaned:
            cleaned["children_count"] = data["children"]
        if "single_parent" in data and "household_type" not in cleaned:
            cleaned["household_type"] = (
                HouseholdType.SINGLE_PARENT.value if data["single_parent"] else HouseholdType.SINGLE.value
            )
        return cls(**cleaned)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary."""

        return asdict(self)

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        """Serialize the profile as JSON."""

        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    def validate(self) -> list[str]:
        """Return validation issues that should be corrected before screening."""

        issues: list[str] = []
        if not isinstance(self.age, int) or self.age < 0 or self.age > 120:
            issues.append("AGE_OUT_OF_RANGE")
        if not isinstance(self.resident, bool):
            issues.append("RESIDENT_MUST_BE_BOOLEAN")
        for field_name in (
            "monthly_income",
            "spouse_income",
            "children_count",
            "dependents",
            "qualifying_months",
            "alimony_or_pension_income",
        ):
            value = getattr(self, field_name)
            if value is not None and value < 0:
                issues.append(f"{field_name.upper()}_NEGATIVE")
        for percent_field in (
            "medical_disability_percent",
            "highest_single_impairment_percent",
            "work_capacity_loss_percent",
        ):
            value = getattr(self, percent_field)
            if value is not None and (value < 0 or value > 100):
                issues.append(f"{percent_field.upper()}_OUT_OF_RANGE")
        if self.claim_date is not None:
            try:
                parse_date(self.claim_date)
            except ValueError:
                issues.append("CLAIM_DATE_INVALID")
        return issues


@dataclass(slots=True)
class AllowanceResult:
    """Structured preliminary screening output."""

    benefit: str
    status: Status
    eligible: bool
    confidence: Confidence
    estimated_monthly_ils_min: float | None
    estimated_monthly_ils_max: float | None
    reasons: list[str]
    missing_info: list[str]
    documents: list[str]
    next_steps: list[str]
    warnings: list[str]
    reference_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary."""

        return asdict(self)

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        """Serialize the result as JSON."""

        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


@dataclass(slots=True)
class StoredProfile:
    """Saved profile metadata."""

    profile_id: str
    created_at: str
    environment: Environment
    profile: ApplicantProfile

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary."""

        return {
            "profile_id": self.profile_id,
            "created_at": self.created_at,
            "environment": self.environment,
            "profile": self.profile.to_dict(),
        }


def parse_date(value: str) -> date:
    """Parse ISO, Israeli, or compact day-month-year dates."""

    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def ils(value: float | int | None) -> str:
    """Format a New Israeli Shekel amount."""

    if value is None:
        return "unknown"
    return f"₪{float(value):,.0f}"


def load_profile_json(path: str | Path) -> ApplicantProfile:
    """Load an ApplicantProfile from a JSON file."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return ApplicantProfile.from_mapping(payload)


class LocalProfileStore:
    """Small JSON profile store for CLI workflows."""

    def __init__(self, directory: str | Path | None = None, environment: Environment = "sandbox") -> None:
        configured = directory or os.environ.get("BENEFIT_CHECKER_STORE")
        if configured:
            self.directory = Path(configured).expanduser()
        else:
            self.directory = Path.home() / ".social-security-benefit-checker" / environment
        self.environment: Environment = environment
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, profile: ApplicantProfile, profile_id: str | None = None) -> StoredProfile:
        """Save a profile and return the generated identifier."""

        profile.validate()
        resolved_id = profile_id or f"prof_{uuid.uuid4().hex[:12]}"
        stored = StoredProfile(
            profile_id=resolved_id,
            created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            environment=self.environment,
            profile=profile,
        )
        target = self.directory / f"{resolved_id}.json"
        target.write_text(json.dumps(stored.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return stored

    def load(self, profile_id: str) -> StoredProfile:
        """Load a stored profile by identifier."""

        target = self.directory / f"{profile_id}.json"
        if not target.exists():
            raise FileNotFoundError(f"Profile not found: {profile_id}")
        payload = json.loads(target.read_text(encoding="utf-8"))
        return StoredProfile(
            profile_id=payload["profile_id"],
            created_at=payload["created_at"],
            environment=payload.get("environment", self.environment),
            profile=ApplicantProfile.from_mapping(payload["profile"]),
        )

    def list_profiles(self) -> list[StoredProfile]:
        """Return saved profiles sorted by creation time."""

        items: list[StoredProfile] = []
        for path in sorted(self.directory.glob("prof_*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            items.append(
                StoredProfile(
                    profile_id=payload["profile_id"],
                    created_at=payload["created_at"],
                    environment=payload.get("environment", self.environment),
                    profile=ApplicantProfile.from_mapping(payload["profile"]),
                )
            )
        return sorted(items, key=lambda item: item.created_at)


class SocialSecurityBenefitChecker:
    """Rule engine for preliminary Israeli National Insurance benefit triage."""

    UNEMPLOYMENT_STANDARD_MONTHS = 12
    UNEMPLOYMENT_SHORT_SERVICE_MONTHS = 6
    UNEMPLOYMENT_MONTHLY_DAYS = 25
    UNEMPLOYMENT_DAILY_CEILING_FIRST_125 = 550.76
    UNEMPLOYMENT_WAGE_DIVISOR = 150.0
    UNEMPLOYMENT_DAILY_BASIC_AMOUNT_2026 = 415.0
    UNEMPLOYMENT_DAILY_CEILING_AFTER_125 = 367.17
    CHILD_ALLOWANCE_BY_ORDER_2026 = (173.0, 219.0, 219.0, 219.0, 173.0)
    CHILD_ALLOWANCE_BY_ORDER = CHILD_ALLOWANCE_BY_ORDER_2026
    GENERAL_DISABILITY_FULL_MONTHLY_ESTIMATE = 4711.0
    GENERAL_DISABILITY_PARTIAL_AMOUNT_BY_DEGREE_2026 = {
        60: 2718.0,
        65: 2894.0,
        74: 3211.0,
        75: 4711.0,
        100: 4711.0,
    }
    INCOME_SUPPORT_WORK_INCOME_CAPS_2026 = {
        "25_54": {
            "single": {0: 3654.0},
            "couple": {0: 5043.0, 1: 5579.0, 2: 6529.0},
            "single_parent": {1: 8914.0, 2: 9865.0},
        },
        "55_to_retirement": {
            "single": {0: 5232.0},
            "couple": {0: 7504.0, 1: 8330.0, 2: 9318.0},
            "single_parent": {1: 10774.0, 2: 12506.0},
        },
    }
    INCOME_SUPPORT_VEHICLE_VALUE_LIMIT_2026 = 46138.0
    INCOME_SUPPORT_RETIREMENT_VEHICLE_VALUE_LIMIT_2026 = 65343.0

    def __init__(
        self,
        *,
        environment: Environment = "sandbox",
        store: LocalProfileStore | None = None,
    ) -> None:
        if environment not in ("sandbox", "production"):
            raise ValueError("environment must be sandbox or production")
        self.environment: Environment = environment
        self.store = store or LocalProfileStore(environment=environment)

    def create_profile(self, profile: ApplicantProfile | Mapping[str, Any]) -> dict[str, Any]:
        """Persist a profile and return an identifier for the next workflow step."""

        resolved = profile if isinstance(profile, ApplicantProfile) else ApplicantProfile.from_mapping(profile)
        issues = resolved.validate()
        if issues:
            return {
                "created": False,
                "profile_id": None,
                "errors": issues,
                "environment": self.environment,
            }
        stored = self.store.save(resolved)
        return {
            "created": True,
            "profile_id": stored.profile_id,
            "created_at": stored.created_at,
            "environment": stored.environment,
        }

    def get_profile(self, profile_id: str) -> ApplicantProfile:
        """Load a profile from the local store."""

        return self.store.load(profile_id).profile

    def list_profiles(self) -> list[dict[str, Any]]:
        """List locally stored profile metadata."""

        return [
            {
                "profile_id": item.profile_id,
                "created_at": item.created_at,
                "environment": item.environment,
                "age": item.profile.age,
                "children_count": item.profile.children_count,
                "employment_status": item.profile.employment_status,
            }
            for item in self.store.list_profiles()
        ]

    def check_all(self, profile: ApplicantProfile) -> list[AllowanceResult]:
        """Run every supported benefit check."""

        issues = profile.validate()
        if issues:
            return [self._validation_result(issues)]
        return [
            self.check_unemployment(profile),
            self.check_general_disability(profile),
            self.check_child_allowance(profile),
            self.check_income_supplement(profile),
        ]

    def check_benefit(self, benefit: str | BenefitType, profile: ApplicantProfile) -> AllowanceResult:
        """Run one benefit check by normalized benefit name."""

        key = benefit.value if isinstance(benefit, BenefitType) else benefit
        if key == BenefitType.UNEMPLOYMENT.value:
            return self.check_unemployment(profile)
        if key == BenefitType.GENERAL_DISABILITY.value:
            return self.check_general_disability(profile)
        if key == BenefitType.CHILD_ALLOWANCE.value:
            return self.check_child_allowance(profile)
        if key == BenefitType.INCOME_SUPPLEMENT.value:
            return self.check_income_supplement(profile)
        raise ValueError(f"Unsupported benefit: {benefit}")

    async def async_check_all(self, profile: ApplicantProfile) -> list[AllowanceResult]:
        """Asynchronously run all checks for integration with async services."""

        return await asyncio.to_thread(self.check_all, profile)

    async def async_check_benefit(
        self, benefit: str | BenefitType, profile: ApplicantProfile
    ) -> AllowanceResult:
        """Asynchronously run a single benefit check."""

        return await asyncio.to_thread(self.check_benefit, benefit, profile)

    def check_profile_id(self, profile_id: str, benefit: str = "all") -> dict[str, Any]:
        """Load a stored profile and check all benefits or one benefit."""

        profile = self.get_profile(profile_id)
        if benefit == "all":
            results = [item.to_dict() for item in self.check_all(profile)]
        else:
            results = [self.check_benefit(benefit, profile).to_dict()]
        return {
            "profile_id": profile_id,
            "environment": self.environment,
            "results": results,
        }

    def run_application_workflow(self, profile: ApplicantProfile | Mapping[str, Any]) -> dict[str, Any]:
        """Create a local profile, screen all benefits, and return next actions."""

        resolved = profile if isinstance(profile, ApplicantProfile) else ApplicantProfile.from_mapping(profile)
        created = self.create_profile(resolved)
        if not created["created"]:
            return {"profile": created, "results": []}
        results = [result.to_dict() for result in self.check_all(resolved)]
        recommended = [
            result["benefit"]
            for result in results
            if result["status"] in ("likely_eligible", "possibly_eligible")
        ]
        return {
            "profile": created,
            "recommended_benefits": recommended,
            "results": results,
        }

    def documents_for(self, benefit: str | BenefitType) -> list[str]:
        """Return the standard document checklist for a benefit."""

        key = benefit.value if isinstance(benefit, BenefitType) else benefit
        if key == BenefitType.UNEMPLOYMENT.value:
            return [
                "Employment Service registration confirmation",
                "termination letter or end-of-contract notice",
                "recent payslips or employer wage report",
                "bank account confirmation",
            ]
        if key == BenefitType.GENERAL_DISABILITY.value:
            return [
                "medical summaries by condition",
                "specialist reports and test results",
                "income documentation",
                "functional limitation evidence",
            ]
        if key == BenefitType.CHILD_ALLOWANCE.value:
            return [
                "birth registration or population registry update",
                "bank account confirmation",
                "custody or guardianship document when relevant",
            ]
        if key == BenefitType.INCOME_SUPPLEMENT.value:
            return [
                "income documentation for all adults in the household",
                "bank statements and asset declarations",
                "Employment Service registration where required",
                "rent, mortgage, alimony, or pension documentation when relevant",
            ]
        raise ValueError(f"Unsupported benefit: {benefit}")

    def explain(self, result: AllowanceResult) -> str:
        """Create a plain-language explanation for an AllowanceResult."""

        amount = (
            "No monthly amount estimate is available."
            if result.estimated_monthly_ils_min is None
            else f"Estimated range: {ils(result.estimated_monthly_ils_min)} to {ils(result.estimated_monthly_ils_max)}."
        )
        reasons = " ".join(result.reasons)
        missing = (
            " Missing information: " + ", ".join(result.missing_info) + "."
            if result.missing_info
            else ""
        )
        return f"{result.benefit}: {result.status}. {amount} {reasons}{missing}".strip()

    def check_unemployment(self, profile: ApplicantProfile) -> AllowanceResult:
        """Screen for unemployment benefit eligibility."""

        reasons: list[str] = []
        missing: list[str] = []
        warnings: list[str] = []
        documents = self.documents_for(BenefitType.UNEMPLOYMENT)
        next_steps = [
            "Register with the Employment Service immediately.",
            "Submit the National Insurance unemployment claim with wage and termination documents.",
            "Check waiting-period rules if resignation was voluntary.",
        ]

        if not profile.resident:
            return self._negative(
                BenefitType.UNEMPLOYMENT.value,
                ["Residency is required for National Insurance unemployment screening."],
                documents,
                next_steps,
            )

        if profile.age < 20 or profile.age >= 67:
            return self._negative(
                BenefitType.UNEMPLOYMENT.value,
                ["Typical unemployment benefit age range is 20 to retirement age, with limited exceptions."],
                documents,
                next_steps,
            )

        if profile.employment_status in (
            EmploymentStatus.SELF_EMPLOYED.value,
            EmploymentStatus.BUSINESS_OWNER.value,
        ) and not profile.business_closed:
            return self._negative(
                BenefitType.UNEMPLOYMENT.value,
                ["Current self-employment without business closure usually blocks unemployment benefit."],
                documents,
                next_steps,
            )

        if profile.qualifying_months <= 0:
            missing.append("QUALIFYING_MONTHS")
        elif profile.qualifying_months < self.UNEMPLOYMENT_SHORT_SERVICE_MONTHS:
            reasons.append("Qualifying employment months are below the usual minimum.")
            return self._negative(BenefitType.UNEMPLOYMENT.value, reasons, documents, next_steps)

        if not profile.registered_employment_service:
            missing.append("EMPLOYMENT_SERVICE_REGISTRATION")
        elif not profile.registered_within_3_months:
            warnings.append("Late Employment Service registration can reduce or block recognized entitlement days.")

        if profile.termination_reason == TerminationReason.UNKNOWN.value:
            missing.append("TERMINATION_REASON")
        elif profile.termination_reason == TerminationReason.RESIGNED.value:
            warnings.append("Voluntary resignation can trigger a waiting period unless justified.")
            reasons.append("Employment ended by resignation.")
        elif profile.termination_reason in (
            TerminationReason.LAID_OFF.value,
            TerminationReason.FIRED.value,
            TerminationReason.END_OF_CONTRACT.value,
            TerminationReason.BUSINESS_CLOSED.value,
            TerminationReason.RESIGNED_JUSTIFIED.value,
            TerminationReason.UNPAID_LEAVE.value,
        ):
            reasons.append("Employment ended for a recognized unemployment pathway.")

        if missing:
            return AllowanceResult(
                benefit=BenefitType.UNEMPLOYMENT.value,
                status="insufficient_information",
                eligible=False,
                confidence="high",
                estimated_monthly_ils_min=None,
                estimated_monthly_ils_max=None,
                reasons=reasons or ["Core unemployment facts are missing."],
                missing_info=missing,
                documents=documents,
                next_steps=next_steps,
                warnings=warnings,
                reference_notes=[
                    "Unemployment checks depend on qualifying period, Employment Service registration, age, and reason for job separation."
                ],
            )

        estimate = self._estimate_unemployment(profile.monthly_income)
        status: Status = "likely_eligible"
        confidence: Confidence = "medium"
        if profile.termination_reason == TerminationReason.RESIGNED.value:
            status = "possibly_eligible"
            confidence = "low"
        return AllowanceResult(
            benefit=BenefitType.UNEMPLOYMENT.value,
            status=status,
            eligible=True,
            confidence=confidence,
            estimated_monthly_ils_min=round(estimate * 0.85, 2),
            estimated_monthly_ils_max=round(estimate, 2),
            reasons=reasons or ["The profile passes the preliminary unemployment screen."],
            missing_info=[],
            documents=documents,
            next_steps=next_steps,
            warnings=warnings,
            reference_notes=[
                "Estimated amount is a conservative planning range and is not an official calculation."
            ],
        )

    def check_general_disability(self, profile: ApplicantProfile) -> AllowanceResult:
        """Screen for general disability allowance eligibility."""

        documents = self.documents_for(BenefitType.GENERAL_DISABILITY)
        next_steps = [
            "Prepare a condition-by-condition medical file.",
            "Submit a general disability claim.",
            "Track the medical committee date and appeal deadline.",
        ]
        missing: list[str] = []
        warnings: list[str] = []

        if not profile.resident:
            return self._negative(
                BenefitType.GENERAL_DISABILITY.value,
                ["Israeli residency is required for this preliminary disability screen."],
                documents,
                next_steps,
            )
        if profile.age < 18 or profile.age >= 67:
            return self._negative(
                BenefitType.GENERAL_DISABILITY.value,
                ["General disability allowance usually applies from age 18 to retirement age."],
                documents,
                next_steps,
            )
        if profile.medical_disability_percent is None:
            missing.append("MEDICAL_DISABILITY_PERCENT")
        if profile.work_capacity_loss_percent is None:
            missing.append("WORK_CAPACITY_LOSS_PERCENT")
        if missing:
            return AllowanceResult(
                benefit=BenefitType.GENERAL_DISABILITY.value,
                status="insufficient_information",
                eligible=False,
                confidence="high",
                estimated_monthly_ils_min=None,
                estimated_monthly_ils_max=None,
                reasons=["Medical disability and earning-capacity information are required."],
                missing_info=missing,
                documents=documents,
                next_steps=next_steps,
                warnings=[],
                reference_notes=[
                    "The official decision is made through medical disability and earning-capacity determinations."
                ],
            )

        medical = profile.medical_disability_percent or 0
        capacity = profile.work_capacity_loss_percent or 0
        has_medical_path = medical >= 60 or (
            medical >= 40 and (profile.highest_single_impairment_percent or 0) >= 25
        )
        if not has_medical_path:
            return self._negative(
                BenefitType.GENERAL_DISABILITY.value,
                [
                    "Medical disability must usually be at least 60%, or at least 40% when one impairment is 25% or more."
                ],
                documents,
                next_steps,
            )
        if capacity < 60:
            return self._negative(
                BenefitType.GENERAL_DISABILITY.value,
                ["Degree of incapacity appears below the recognized 60% preliminary threshold."],
                documents,
                next_steps,
            )

        if profile.monthly_income > 0:
            warnings.append("Work income can reduce the benefit or affect the degree of incapacity.")

        estimate = self._estimate_general_disability_amount(capacity)
        return AllowanceResult(
            benefit=BenefitType.GENERAL_DISABILITY.value,
            status="likely_eligible",
            eligible=True,
            confidence="medium",
            estimated_monthly_ils_min=round(estimate, 2),
            estimated_monthly_ils_max=round(estimate, 2),
            reasons=["Medical and earning-capacity figures pass the preliminary screen."],
            missing_info=[],
            documents=documents,
            next_steps=next_steps,
            warnings=warnings,
            reference_notes=[
                "Use the official disability calculator and committee decision for final amounts."
            ],
        )

    def check_child_allowance(self, profile: ApplicantProfile) -> AllowanceResult:
        """Screen for child allowance eligibility."""

        documents = self.documents_for(BenefitType.CHILD_ALLOWANCE)
        next_steps = [
            "Confirm that each child is registered in the population registry.",
            "Verify the bank account used for National Insurance payments.",
            "Resolve custody or guardianship issues before relying on payment routing.",
        ]
        if not profile.resident:
            return self._negative(
                BenefitType.CHILD_ALLOWANCE.value,
                ["The parent or eligible guardian usually needs Israeli residency."],
                documents,
                next_steps,
            )
        if profile.children_count <= 0:
            return self._negative(
                BenefitType.CHILD_ALLOWANCE.value,
                ["No children were entered for child allowance screening."],
                documents,
                next_steps,
            )

        if profile.birth_dates:
            under_18 = 0
            today = date.today()
            missing_dates = False
            for raw in profile.birth_dates:
                try:
                    born = parse_date(raw)
                except ValueError:
                    missing_dates = True
                    continue
                years = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                if years < 18:
                    under_18 += 1
            if missing_dates:
                missing = ["VALID_CHILD_BIRTH_DATES"]
            else:
                missing = []
            count = under_18
        else:
            count = profile.children_count
            missing = ["CHILD_BIRTH_DATES"] if profile.children_count > 0 else []

        if count <= 0:
            return self._negative(
                BenefitType.CHILD_ALLOWANCE.value,
                ["No child under 18 was identified."],
                documents,
                next_steps,
            )

        amount = self._estimate_child_allowance(count)
        confidence: Confidence = "medium" if missing else "high"
        return AllowanceResult(
            benefit=BenefitType.CHILD_ALLOWANCE.value,
            status="likely_eligible" if not missing else "possibly_eligible",
            eligible=True,
            confidence=confidence,
            estimated_monthly_ils_min=amount,
            estimated_monthly_ils_max=amount,
            reasons=[f"{count} child or children appear to be in the eligible age range."],
            missing_info=missing,
            documents=documents,
            next_steps=next_steps,
            warnings=[
                "Payment routing can change in separation, guardianship, foster-care, or institutional-care cases."
            ],
            reference_notes=[
                "Birth order and law changes affect the official amount."
            ],
        )

    def check_income_supplement(self, profile: ApplicantProfile) -> AllowanceResult:
        """Screen for income supplement eligibility."""

        documents = self.documents_for(BenefitType.INCOME_SUPPLEMENT)
        next_steps = [
            "Calculate household income after allowed deductions.",
            "Collect asset, vehicle, and bank documentation.",
            "Register with the Employment Service when the work-test applies.",
            "Submit the income supplement claim with supporting documents.",
        ]
        reasons: list[str] = []
        warnings: list[str] = []
        missing: list[str] = []

        if not profile.resident:
            return self._negative(
                BenefitType.INCOME_SUPPLEMENT.value,
                ["Israeli residency is required for income supplement screening."],
                documents,
                next_steps,
            )
        if profile.age < 20 and profile.children_count == 0:
            return self._negative(
                BenefitType.INCOME_SUPPLEMENT.value,
                ["Applicants under 20 without dependent children generally need a specific exception."],
                documents,
                next_steps,
            )
        if profile.assets_exceed_limit:
            return self._negative(
                BenefitType.INCOME_SUPPLEMENT.value,
                ["Reported assets exceed the preliminary limit."],
                documents,
                next_steps,
            )
        if profile.vehicle_value_exceeds_limit:
            warnings.append(
                "Vehicle ownership or value above the 2026 screening limit can affect entitlement unless an exception applies."
            )
        if profile.receives_other_benefit:
            warnings.append("Concurrent benefit rules can reduce or block income supplement.")
        if profile.employment_status in (
            EmploymentStatus.UNEMPLOYED.value,
            EmploymentStatus.NOT_WORKING.value,
            EmploymentStatus.SELF_EMPLOYED.value,
            EmploymentStatus.BUSINESS_OWNER.value,
        ) and not profile.registered_employment_service:
            missing.append("EMPLOYMENT_SERVICE_REGISTRATION_OR_EXEMPTION")

        household_income = (
            profile.monthly_income + profile.spouse_income + profile.alimony_or_pension_income
        )
        income_cap = self._income_support_work_income_cap(profile)
        if household_income <= income_cap:
            reasons.append(
                f"Household income {ils(household_income)} is at or below the 2026 screening income cap {ils(income_cap)}."
            )
            status: Status = "likely_eligible" if not missing else "insufficient_information"
            confidence: Confidence = "medium"
            return AllowanceResult(
                benefit=BenefitType.INCOME_SUPPLEMENT.value,
                status=status,
                eligible=status == "likely_eligible",
                confidence=confidence,
                estimated_monthly_ils_min=None,
                estimated_monthly_ils_max=None,
                reasons=reasons,
                missing_info=missing,
                documents=documents,
                next_steps=next_steps,
                warnings=warnings,
                reference_notes=[
                    "Income supplement is means tested. Use the official calculator for the payment amount; the screening cap assumes work income is the only income."
                ],
            )

        return AllowanceResult(
            benefit=BenefitType.INCOME_SUPPLEMENT.value,
            status="not_likely",
            eligible=False,
            confidence="medium",
            estimated_monthly_ils_min=None,
            estimated_monthly_ils_max=None,
            reasons=[
                f"Household income {ils(household_income)} is above the 2026 screening income cap {ils(income_cap)}."
            ],
            missing_info=missing,
            documents=documents,
            next_steps=next_steps,
            warnings=warnings,
            reference_notes=[
                "Retest after income changes, separation, birth of a child, rent change, or asset change."
            ],
        )

    def _validation_result(self, issues: list[str]) -> AllowanceResult:
        return AllowanceResult(
            benefit="profile",
            status="insufficient_information",
            eligible=False,
            confidence="high",
            estimated_monthly_ils_min=None,
            estimated_monthly_ils_max=None,
            reasons=["Profile validation failed."],
            missing_info=issues,
            documents=[],
            next_steps=["Correct the profile and run screening again."],
            warnings=[],
            reference_notes=[],
        )

    def _negative(
        self,
        benefit: str,
        reasons: list[str],
        documents: list[str],
        next_steps: list[str],
    ) -> AllowanceResult:
        return AllowanceResult(
            benefit=benefit,
            status="not_likely",
            eligible=False,
            confidence="medium",
            estimated_monthly_ils_min=None,
            estimated_monthly_ils_max=None,
            reasons=reasons,
            missing_info=[],
            documents=documents,
            next_steps=next_steps,
            warnings=[],
            reference_notes=[],
        )

    def _estimate_unemployment(self, monthly_wage: float) -> float:
        if monthly_wage <= 0:
            return 0.0
        daily_wage = monthly_wage / self.UNEMPLOYMENT_WAGE_DIVISOR
        daily_estimate = min(daily_wage * 0.55, self.UNEMPLOYMENT_DAILY_CEILING_FIRST_125)
        return daily_estimate * self.UNEMPLOYMENT_MONTHLY_DAYS

    def _estimate_general_disability_amount(self, capacity_degree: float) -> float:
        """Return the closest 2026 monthly general disability amount for a recognized degree."""

        if capacity_degree >= 75:
            return self.GENERAL_DISABILITY_PARTIAL_AMOUNT_BY_DEGREE_2026[100]
        if capacity_degree >= 74:
            return self.GENERAL_DISABILITY_PARTIAL_AMOUNT_BY_DEGREE_2026[74]
        if capacity_degree >= 65:
            return self.GENERAL_DISABILITY_PARTIAL_AMOUNT_BY_DEGREE_2026[65]
        return self.GENERAL_DISABILITY_PARTIAL_AMOUNT_BY_DEGREE_2026[60]

    def _estimate_child_allowance(self, children_count: int) -> float:
        total = 0.0
        for index in range(children_count):
            if index < len(self.CHILD_ALLOWANCE_BY_ORDER):
                total += self.CHILD_ALLOWANCE_BY_ORDER[index]
            else:
                total += self.CHILD_ALLOWANCE_BY_ORDER[-1]
        return total

    def _income_support_work_income_cap(self, profile: ApplicantProfile) -> float:
        """Return a 2026 screening cap for work income when it is the only income."""

        age_band = "55_to_retirement" if profile.age >= 55 else "25_54"
        children_bucket = 0 if profile.children_count <= 0 else 1 if profile.children_count == 1 else 2
        if profile.household_type == HouseholdType.SINGLE_PARENT.value:
            household_key = "single_parent"
            children_bucket = 1 if children_bucket == 0 else children_bucket
        elif profile.household_type == HouseholdType.COUPLE.value:
            household_key = "couple"
        else:
            household_key = "single"
            children_bucket = 0
        caps = self.INCOME_SUPPORT_WORK_INCOME_CAPS_2026[age_band][household_key]
        return caps.get(children_bucket, caps[max(caps)])

    def _income_support_threshold(self, profile: ApplicantProfile) -> float:
        """Backward-compatible alias for the 2026 work-income screening cap."""

        return self._income_support_work_income_cap(profile)


def check_profile(profile_data: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Convenience function for a mapping-based all-benefits check."""

    checker = SocialSecurityBenefitChecker()
    profile = ApplicantProfile.from_mapping(profile_data)
    return [result.to_dict() for result in checker.check_all(profile)]


def check_file(path: str | Path, benefit: str = "all") -> dict[str, Any]:
    """Check a JSON profile file and return a serializable payload."""

    checker = SocialSecurityBenefitChecker()
    profile = load_profile_json(path)
    if benefit == "all":
        return {"results": [result.to_dict() for result in checker.check_all(profile)]}
    return {"results": [checker.check_benefit(benefit, profile).to_dict()]}
