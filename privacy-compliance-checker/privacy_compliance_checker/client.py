"""Deterministic privacy compliance helper for Israeli workflows.

The module provides local, typed checks for privacy operations. It does not
call external services and does not provide legal advice.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


class Severity(str, Enum):
    """Finding severity used in assessment reports."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class SecurityLevel(str, Enum):
    """Operational security level aligned to Israeli data-security thinking."""

    BASIC = "basic"
    MEDIUM = "medium"
    HIGH = "high"


class LawfulBasis(str, Enum):
    """GDPR-style lawful basis vocabulary with an unknown fallback."""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"
    UNKNOWN = "unknown"


ADEQUATE_DESTINATIONS = {
    "at",
    "austria",
    "be",
    "belgium",
    "bg",
    "bulgaria",
    "hr",
    "croatia",
    "cy",
    "cyprus",
    "cz",
    "czech republic",
    "dk",
    "denmark",
    "ee",
    "estonia",
    "fi",
    "finland",
    "fr",
    "france",
    "de",
    "germany",
    "gr",
    "greece",
    "hu",
    "hungary",
    "ie",
    "ireland",
    "it",
    "italy",
    "lv",
    "latvia",
    "lt",
    "lithuania",
    "lu",
    "luxembourg",
    "mt",
    "malta",
    "nl",
    "netherlands",
    "pl",
    "poland",
    "pt",
    "portugal",
    "ro",
    "romania",
    "sk",
    "slovakia",
    "si",
    "slovenia",
    "es",
    "spain",
    "se",
    "sweden",
    "uk",
    "united kingdom",
    "gb",
    "eea",
    "eu",
    "european union",
    "is",
    "iceland",
    "li",
    "liechtenstein",
    "no",
    "norway",
    "ch",
    "switzerland",
    "israel",
}

SENSITIVE_MARKERS = {
    "health",
    "medical",
    "genetic",
    "biometric",
    "sexual_orientation",
    "political_opinion",
    "religion",
    "criminal_record",
    "financial",
    "credit",
    "children",
    "precise_location",
    "national_id",
    "employment",
    "trade_union",
    "psychological",
    "welfare",
    "disability",
}

HIGH_RISK_SECTORS = {
    "health",
    "medical",
    "clinic",
    "finance",
    "banking",
    "insurance",
    "credit",
    "government",
    "municipality",
    "education",
    "children",
}

MANDATORY_REFERENCES = (
    "Israeli Privacy Protection Law, 5741-1981",
    "Protection of Privacy Regulations (Data Security), 5777-2017",
    "Israeli Privacy Protection Authority guidance on database security and breach handling",
    "GDPR Articles 5, 6, 12-23, 28, 30, 32, 33, 35, 44-49 where applicable",
)


@dataclass(frozen=True)
class Finding:
    """Single compliance finding."""

    code: str
    title: str
    severity: Severity
    description: str
    actions: tuple[str, ...] = field(default_factory=tuple)
    references: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable finding dictionary."""

        return {
            "code": self.code,
            "title": self.title,
            "severity": self.severity.value,
            "description": self.description,
            "actions": list(self.actions),
            "references": list(self.references),
        }


@dataclass(frozen=True)
class ChecklistItem:
    """Operational checklist item generated from an assessment."""

    id: str
    area: str
    task: str
    owner: str = "privacy owner"
    due_days: int = 30
    evidence: str = "documented record"
    status: str = "open"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable checklist dictionary."""

        return asdict(self)


@dataclass(frozen=True)
class AssessmentInput:
    """Input fields for a privacy workflow assessment."""

    business_name: str = "Unspecified activity"
    country: str = "Israel"
    record_count: int = 0
    authorized_users: int = 1
    sensitive_categories: tuple[str, ...] = field(default_factory=tuple)
    sector: str = "general"
    purposes: tuple[str, ...] = field(default_factory=tuple)
    data_subjects: tuple[str, ...] = field(default_factory=lambda: ("customers",))
    lawful_basis: LawfulBasis = LawfulBasis.UNKNOWN
    collects_children_data: bool = False
    cross_border: bool = False
    destinations: tuple[str, ...] = field(default_factory=tuple)
    processors: tuple[str, ...] = field(default_factory=tuple)
    direct_marketing: bool = False
    uses_tracking: bool = False
    uses_ai_profiling: bool = False
    data_broker: bool = False
    public_body: bool = False
    employee_monitoring: bool = False
    breach_recent: bool = False
    retention_months: int | None = None
    privacy_notice_ready: bool = False
    processor_contracts_ready: bool = False
    rights_process_ready: bool = False
    security_controls_ready: bool = False
    eu_targeting: bool = False
    eu_data_subjects: bool = False
    automated_decisions: bool = False

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AssessmentInput":
        """Create input from a mapping and normalize list-like values."""

        if not isinstance(payload, Mapping):
            raise TypeError("payload must be a mapping")
        data = dict(payload)
        for key in ("sensitive_categories", "purposes", "data_subjects", "destinations", "processors"):
            data[key] = _as_tuple(data.get(key, ()))
        if "lawful_basis" in data and not isinstance(data["lawful_basis"], LawfulBasis):
            data["lawful_basis"] = _parse_lawful_basis(data["lawful_basis"])
        allowed = set(cls.__dataclass_fields__)
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise ValueError(f"Unknown assessment fields: {', '.join(unknown)}")
        record_count = int(data.get("record_count", 0))
        authorized_users = int(data.get("authorized_users", 1))
        if record_count < 0:
            raise ValueError("record_count must be zero or greater")
        if authorized_users < 1:
            raise ValueError("authorized_users must be one or greater")
        if data.get("retention_months") is not None and int(data["retention_months"]) < 0:
            raise ValueError("retention_months must be zero or greater")
        data["record_count"] = record_count
        data["authorized_users"] = authorized_users
        if data.get("retention_months") is not None:
            data["retention_months"] = int(data["retention_months"])
        return cls(**data)


@dataclass(frozen=True)
class AssessmentResult:
    """Full assessment output."""

    id: str
    environment: str
    created_at: str
    input: AssessmentInput
    security_level: SecurityLevel
    gdpr_applicable: bool
    israel_obligations: tuple[str, ...]
    findings: tuple[Finding, ...]
    checklist: tuple[ChecklistItem, ...]
    required_documents: tuple[str, ...]
    retention_recommendation: str
    transfer_controls: tuple[str, ...]
    breach_actions: tuple[str, ...]
    score: int

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable result dictionary."""

        data = asdict(self)
        data["input"]["lawful_basis"] = self.input.lawful_basis.value
        data["security_level"] = self.security_level.value
        data["findings"] = [finding.to_dict() for finding in self.findings]
        data["checklist"] = [item.to_dict() for item in self.checklist]
        return data

    def to_json(self) -> str:
        """Return formatted JSON with Unicode preserved."""

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_markdown(self) -> str:
        """Render the result as a practical Markdown report."""

        lines = [
            f"# Privacy compliance assessment: {self.input.business_name}",
            "",
            f"- Environment: `{self.environment}`",
            f"- Assessment ID: `{self.id}`",
            f"- Created: `{self.created_at}`",
            f"- Security level: `{self.security_level.value}`",
            f"- GDPR applicable: `{str(self.gdpr_applicable).lower()}`",
            f"- Score: `{self.score}/100`",
            "",
            "## Israeli compliance obligations",
        ]
        lines.extend(f"- {item}" for item in self.israel_obligations)
        lines.extend(["", "## Findings"])
        for finding in self.findings:
            lines.append(f"### {finding.code}: {finding.title}")
            lines.append(f"- Severity: `{finding.severity.value}`")
            lines.append(f"- Detail: {finding.description}")
            if finding.actions:
                lines.append("- Actions:")
                lines.extend(f"  - {action}" for action in finding.actions)
            if finding.references:
                lines.append("- References:")
                lines.extend(f"  - {ref}" for ref in finding.references)
            lines.append("")
        lines.extend(["## Checklist"])
        for item in self.checklist:
            lines.append(f"- [{item.status}] {item.id}: {item.task} ({item.area}, owner: {item.owner}, due: {item.due_days} days)")
        lines.extend(
            [
                "",
                "## Required documents",
                *[f"- {doc}" for doc in self.required_documents],
                "",
                "## Retention recommendation",
                self.retention_recommendation,
                "",
                "## Transfer controls",
                *[f"- {control}" for control in self.transfer_controls],
                "",
                "## Breach actions",
                *[f"- {action}" for action in self.breach_actions],
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    def checklist_markdown(self) -> str:
        """Render only the checklist as Markdown."""

        rows = ["| ID | Area | Task | Owner | Due days | Evidence | Status |", "|---|---|---|---|---:|---|---|"]
        for item in self.checklist:
            rows.append(
                f"| {item.id} | {item.area} | {item.task} | {item.owner} | {item.due_days} | {item.evidence} | {item.status} |"
            )
        return "\n".join(rows) + "\n"


SCENARIOS: dict[str, dict[str, Any]] = {
    "customer-club": {
        "business_name": "Neighborhood customer club",
        "record_count": 18000,
        "authorized_users": 4,
        "sensitive_categories": [],
        "sector": "retail",
        "purposes": ["loyalty benefits", "receipts", "direct marketing"],
        "lawful_basis": "consent",
        "direct_marketing": True,
        "uses_tracking": True,
        "cross_border": True,
        "destinations": ["United States"],
        "processors": ["email delivery provider", "analytics provider"],
        "retention_months": 36,
    },
    "freelancer-crm": {
        "business_name": "Freelancer lead list",
        "record_count": 350,
        "authorized_users": 1,
        "sector": "professional services",
        "purposes": ["client management", "invoicing"],
        "lawful_basis": "contract",
        "processors": ["cloud spreadsheet"],
        "retention_months": 84,
        "privacy_notice_ready": True,
    },
    "clinic": {
        "business_name": "Private clinic patient system",
        "record_count": 12000,
        "authorized_users": 9,
        "sensitive_categories": ["health", "national_id"],
        "sector": "clinic",
        "purposes": ["treatment", "billing", "appointment reminders"],
        "lawful_basis": "legal_obligation",
        "processors": ["appointment platform", "billing provider"],
        "retention_months": 120,
        "processor_contracts_ready": False,
    },
    "breach": {
        "business_name": "Misdirected customer export",
        "record_count": 4200,
        "authorized_users": 3,
        "sensitive_categories": ["financial"],
        "sector": "retail",
        "purposes": ["support"],
        "lawful_basis": "contract",
        "breach_recent": True,
        "security_controls_ready": False,
    },
    "saas-transfer": {
        "business_name": "Cloud workflow service",
        "record_count": 65000,
        "authorized_users": 25,
        "sensitive_categories": ["employment"],
        "sector": "software",
        "purposes": ["account management", "support", "product analytics"],
        "lawful_basis": "legitimate_interests",
        "cross_border": True,
        "destinations": ["Germany", "United States"],
        "processors": ["hosting provider", "support system", "log processor"],
        "eu_targeting": True,
        "eu_data_subjects": True,
        "uses_ai_profiling": True,
        "automated_decisions": False,
    },
}


class PrivacyComplianceCheckerClient:
    """Synchronous local client for assessment, storage, and reporting."""

    def __init__(self, environment: str | None = None, state_dir: str | os.PathLike[str] | None = None) -> None:
        """Initialize a client for sandbox or production workflows."""

        resolved = environment or os.getenv("PCC_ENV", "sandbox")
        if resolved not in {"sandbox", "production"}:
            raise ValueError("environment must be sandbox or production")
        self.environment = resolved
        default_dir = Path(os.getenv("PCC_STATE_DIR", ".pcc-state"))
        self.state_dir = Path(state_dir) if state_dir is not None else default_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def assess(self, payload: Mapping[str, Any] | AssessmentInput) -> AssessmentResult:
        """Generate a compliance assessment from a mapping or typed input."""

        assessment_input = payload if isinstance(payload, AssessmentInput) else AssessmentInput.from_mapping(payload)
        security_level = determine_security_level(assessment_input)
        gdpr_applicable = determine_gdpr_applicability(assessment_input)
        findings = tuple(generate_findings(assessment_input, security_level, gdpr_applicable))
        checklist = tuple(generate_checklist(assessment_input, security_level, gdpr_applicable, findings))
        result_id = make_assessment_id(assessment_input, self.environment)
        return AssessmentResult(
            id=result_id,
            environment=self.environment,
            created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            input=assessment_input,
            security_level=security_level,
            gdpr_applicable=gdpr_applicable,
            israel_obligations=tuple(generate_israel_obligations(assessment_input, security_level)),
            findings=findings,
            checklist=checklist,
            required_documents=tuple(generate_required_documents(assessment_input, gdpr_applicable)),
            retention_recommendation=generate_retention_recommendation(assessment_input),
            transfer_controls=tuple(generate_transfer_controls(assessment_input, gdpr_applicable)),
            breach_actions=tuple(generate_breach_actions(assessment_input, gdpr_applicable)),
            score=score_assessment(findings, security_level),
        )

    def validate(self, payload: Mapping[str, Any] | AssessmentInput) -> dict[str, Any]:
        """Validate input and return normalized values without saving state."""

        assessment_input = payload if isinstance(payload, AssessmentInput) else AssessmentInput.from_mapping(payload)
        warnings: list[str] = []
        if not assessment_input.purposes:
            warnings.append("Add at least one specific processing purpose.")
        if assessment_input.lawful_basis is LawfulBasis.UNKNOWN:
            warnings.append("Select a lawful basis before production use.")
        if assessment_input.cross_border and not assessment_input.destinations:
            warnings.append("List destination countries or regions for transfer review.")
        return {"valid": True, "warnings": warnings, "normalized": _input_to_dict(assessment_input)}

    def create(self, payload: Mapping[str, Any] | AssessmentInput) -> dict[str, Any]:
        """Assess and persist a record, returning the generated ID."""

        result = self.assess(payload)
        path = self._record_path(result.id)
        path.write_text(result.to_json(), encoding="utf-8")
        return {"id": result.id, "path": str(path), "environment": self.environment, "score": result.score}

    def get(self, assessment_id: str) -> dict[str, Any]:
        """Read a persisted assessment by ID."""

        path = self._record_path(assessment_id)
        if not path.exists():
            raise FileNotFoundError(f"assessment not found: {assessment_id}")
        return json.loads(path.read_text(encoding="utf-8"))

    def update(self, assessment_id: str, patch: Mapping[str, Any]) -> dict[str, Any]:
        """Patch the input of a persisted assessment and write a new assessment."""

        record = self.get(assessment_id)
        payload = dict(record.get("input", {}))
        payload.update(patch)
        result = self.assess(payload)
        path = self._record_path(assessment_id)
        updated = result.to_dict()
        updated["id"] = assessment_id
        path.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"id": assessment_id, "path": str(path), "environment": self.environment, "score": result.score}

    def list_records(self) -> list[dict[str, Any]]:
        """List persisted assessment summaries."""

        summaries: list[dict[str, Any]] = []
        for path in sorted(self.state_dir.glob("*.json")):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            summaries.append(
                {
                    "id": record.get("id", path.stem),
                    "business_name": record.get("input", {}).get("business_name"),
                    "score": record.get("score"),
                    "security_level": record.get("security_level"),
                    "created_at": record.get("created_at"),
                }
            )
        return summaries

    def delete(self, assessment_id: str) -> dict[str, Any]:
        """Delete a persisted assessment record."""

        path = self._record_path(assessment_id)
        if not path.exists():
            raise FileNotFoundError(f"assessment not found: {assessment_id}")
        path.unlink()
        return {"id": assessment_id, "deleted": True}

    def export_report(self, assessment_id: str, fmt: str = "markdown") -> str:
        """Export a persisted assessment as JSON or Markdown."""

        record = self.get(assessment_id)
        if fmt == "json":
            return json.dumps(record, ensure_ascii=False, indent=2)
        if fmt != "markdown":
            raise ValueError("fmt must be markdown or json")
        return record_to_markdown(record)

    def make_checklist(self, payload: Mapping[str, Any] | AssessmentInput) -> list[dict[str, Any]]:
        """Generate checklist items from input."""

        return [item.to_dict() for item in self.assess(payload).checklist]

    def template(self, scenario: str = "customer-club") -> dict[str, Any]:
        """Return a built-in scenario template."""

        return get_scenario(scenario)

    def _record_path(self, assessment_id: str) -> Path:
        safe = re_slug(assessment_id)
        return self.state_dir / f"{safe}.json"


class AsyncPrivacyComplianceCheckerClient:
    """Async wrapper around the synchronous local client."""

    def __init__(self, environment: str | None = None, state_dir: str | os.PathLike[str] | None = None) -> None:
        """Initialize the async client."""

        self._client = PrivacyComplianceCheckerClient(environment=environment, state_dir=state_dir)

    async def assess(self, payload: Mapping[str, Any] | AssessmentInput) -> AssessmentResult:
        """Generate an assessment asynchronously."""

        return await asyncio.to_thread(self._client.assess, payload)

    async def validate(self, payload: Mapping[str, Any] | AssessmentInput) -> dict[str, Any]:
        """Validate input asynchronously."""

        return await asyncio.to_thread(self._client.validate, payload)

    async def create(self, payload: Mapping[str, Any] | AssessmentInput) -> dict[str, Any]:
        """Create a persisted assessment asynchronously."""

        return await asyncio.to_thread(self._client.create, payload)

    async def get(self, assessment_id: str) -> dict[str, Any]:
        """Read a persisted assessment asynchronously."""

        return await asyncio.to_thread(self._client.get, assessment_id)

    async def update(self, assessment_id: str, patch: Mapping[str, Any]) -> dict[str, Any]:
        """Patch a persisted assessment asynchronously."""

        return await asyncio.to_thread(self._client.update, assessment_id, patch)

    async def list_records(self) -> list[dict[str, Any]]:
        """List persisted assessments asynchronously."""

        return await asyncio.to_thread(self._client.list_records)

    async def delete(self, assessment_id: str) -> dict[str, Any]:
        """Delete a persisted assessment asynchronously."""

        return await asyncio.to_thread(self._client.delete, assessment_id)


def assess(payload: Mapping[str, Any] | AssessmentInput, environment: str | None = None) -> AssessmentResult:
    """Convenience function for a one-off assessment."""

    return PrivacyComplianceCheckerClient(environment=environment).assess(payload)


async def assess_async(payload: Mapping[str, Any] | AssessmentInput, environment: str | None = None) -> AssessmentResult:
    """Convenience function for a one-off async assessment."""

    return await AsyncPrivacyComplianceCheckerClient(environment=environment).assess(payload)


def list_scenarios() -> list[str]:
    """Return available scenario names."""

    return sorted(SCENARIOS)


def get_scenario(name: str) -> dict[str, Any]:
    """Return a copy of a built-in scenario."""

    if name not in SCENARIOS:
        raise ValueError(f"unknown scenario: {name}")
    return json.loads(json.dumps(SCENARIOS[name], ensure_ascii=False))


def load_json(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Load a JSON object from a file."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON file must contain an object")
    return data


def determine_security_level(data: AssessmentInput) -> SecurityLevel:
    """Determine the Israeli data-security level for the workflow.

    The rule mirrors the Privacy Protection Authority guide to the Data
    Security Regulations: medium level is triggered by public-body databases,
    direct-mailing service or data-broker activity, or data with special
    sensitivity. High level applies when a medium-level database contains data
    about 100,000 or more people or has more than 100 authorized users.
    Record count alone at 10,000 is not a general medium-security trigger.
    """

    medium_triggered = has_medium_security_trigger(data)
    if medium_triggered and (data.record_count >= 100_000 or data.authorized_users > 100):
        return SecurityLevel.HIGH
    if medium_triggered:
        return SecurityLevel.MEDIUM
    return SecurityLevel.BASIC


def has_medium_security_trigger(data: AssessmentInput) -> bool:
    """Return whether the workflow has a medium-level Israeli security trigger."""

    sensitive = bool(_normalized_set(data.sensitive_categories))
    return bool(sensitive or data.public_body or data.data_broker or data.direct_marketing)


def needs_amendment13_registration_review(data: AssessmentInput) -> bool:
    """Return whether Amendment 13 registration duties need review."""

    return bool(data.public_body or (data.data_broker and data.record_count > 10_000))


def needs_amendment13_notification_review(data: AssessmentInput) -> bool:
    """Return whether Amendment 13 notification duties need review."""

    return bool(data.sensitive_categories and data.record_count > 100_000 and not needs_amendment13_registration_review(data))


def needs_dpo_review(data: AssessmentInput) -> bool:
    """Return whether appointment of a DPO should be assessed."""

    sensitive_large_scale = bool(data.sensitive_categories and data.record_count >= 100_000)
    monitoring_large_scale = bool((data.uses_tracking or data.employee_monitoring or data.uses_ai_profiling) and data.record_count >= 100_000)
    broker_large_scale = bool(data.data_broker and data.record_count > 10_000)
    return bool(data.public_body or broker_large_scale or sensitive_large_scale or monitoring_large_scale)


def determine_gdpr_applicability(data: AssessmentInput) -> bool:
    """Determine whether GDPR checks should be included."""

    subjects = " ".join(data.data_subjects).lower()
    destinations = " ".join(data.destinations).lower()
    return bool(
        data.eu_targeting
        or data.eu_data_subjects
        or "eu resident" in subjects
        or "eea" in subjects
        or "european union" in subjects
        or data.country.lower() in ADEQUATE_DESTINATIONS - {"israel"}
        or "european union" in destinations
        or "eea" in destinations
    )


def generate_findings(data: AssessmentInput, level: SecurityLevel, gdpr_applicable: bool) -> list[Finding]:
    """Generate deterministic compliance findings."""

    findings: list[Finding] = []

    if data.lawful_basis is LawfulBasis.UNKNOWN:
        findings.append(
            Finding(
                code="BASIS-001",
                title="Lawful basis is missing",
                severity=Severity.CRITICAL,
                description="Processing lacks a documented lawful basis. Complete the basis analysis before collecting additional personal data.",
                actions=(
                    "Map each purpose to consent, contract, legal obligation, legitimate interests, or another applicable basis.",
                    "Keep the signed approval or decision memo with the processing record.",
                ),
                references=("Israeli notice and consent expectations", "GDPR Article 6 where applicable"),
            )
        )

    if not data.purposes:
        findings.append(
            Finding(
                code="PURPOSE-001",
                title="Processing purposes are not defined",
                severity=Severity.WARNING,
                description="Personal data must be tied to clear purposes. Generic purposes make retention, notices, and access control unreliable.",
                actions=("Define one or more concrete purposes.", "Block secondary use until compatibility is assessed."),
                references=("Purpose limitation and transparency principles",),
            )
        )

    if level is not SecurityLevel.BASIC and not data.security_controls_ready:
        findings.append(
            Finding(
                code="SEC-001",
                title="Security controls need evidence",
                severity=Severity.CRITICAL if level is SecurityLevel.HIGH else Severity.WARNING,
                description=f"The workflow is classified as {level.value}. Evidence for access control, logging, backups, supplier controls, and incident response is required.",
                actions=(
                    "Create a database specification document.",
                    "Document roles, permissions, authentication, backups, logging, and review dates.",
                    "Test restoration and incident escalation before production use.",
                ),
                references=("Protection of Privacy Regulations (Data Security), 5777-2017",),
            )
        )

    if data.sensitive_categories and not data.privacy_notice_ready:
        findings.append(
            Finding(
                code="NOTICE-001",
                title="Privacy notice must cover sensitive data",
                severity=Severity.WARNING,
                description="Sensitive categories require specific transparency about categories, purposes, recipients, retention, transfers, and rights.",
                actions=(
                    "Publish a concise Hebrew notice before collection.",
                    "Add an English notice when targeting non-Hebrew or EU users.",
                ),
                references=("Israeli Privacy Protection Law notice duties", "GDPR Articles 12-14 where applicable"),
            )
        )

    if data.direct_marketing:
        findings.append(
            Finding(
                code="DM-001",
                title="Direct marketing controls required",
                severity=Severity.WARNING,
                description="Marketing lists require source tracking, clear opt-out, suppression-list handling, and separation from service messages.",
                actions=(
                    "Store consent or permissible source details per recipient.",
                    "Add an unsubscribe channel to each marketing message.",
                    "Do not reuse service data for unrelated marketing without a valid basis.",
                ),
                references=("Israeli direct mailing rules", "Anti-spam obligations may also apply"),
            )
        )

    if data.uses_tracking:
        findings.append(
            Finding(
                code="TRACK-001",
                title="Tracking and analytics require prior control",
                severity=Severity.WARNING,
                description="Non-essential analytics, advertising pixels, and session tools need transparent controls and blocking before consent when consent is the basis.",
                actions=(
                    "Classify each tracker as essential or optional.",
                    "Block optional trackers until consent is recorded.",
                    "Keep a tracker inventory and retention limit.",
                ),
                references=("Privacy Authority transparency guidance", "GDPR consent and ePrivacy-style expectations where applicable"),
            )
        )

    if data.cross_border:
        non_adequate = [country for country in data.destinations if country.strip().lower() not in ADEQUATE_DESTINATIONS]
        severity = Severity.CRITICAL if non_adequate and gdpr_applicable else Severity.WARNING
        findings.append(
            Finding(
                code="XFER-001",
                title="Cross-border transfer review required",
                severity=severity,
                description="Transfers outside Israel require destination, recipient, safeguard, and onward-transfer review. GDPR transfers require Chapter V safeguards when GDPR applies.",
                actions=(
                    "List each destination country and recipient.",
                    "Document adequacy, contractual safeguards, access controls, and onward-transfer limits.",
                    "For non-adequate destinations, complete transfer-impact analysis and supplementary measures where needed.",
                ),
                references=("Israeli transfer rules", "GDPR Articles 44-49 where applicable"),
            )
        )

    if data.processors and not data.processor_contracts_ready:
        findings.append(
            Finding(
                code="PROC-001",
                title="Processor contracts need completion",
                severity=Severity.WARNING,
                description="Processors must be bound by processing instructions, security duties, confidentiality, subprocessor controls, audit support, breach notice, and deletion or return.",
                actions=(
                    "Execute data-processing terms before production use.",
                    "Record subprocessors and transfer locations.",
                    "Review evidence from critical suppliers annually.",
                ),
                references=("Israeli outsourcing and data-security expectations", "GDPR Article 28 where applicable"),
            )
        )

    if data.collects_children_data:
        findings.append(
            Finding(
                code="CHILD-001",
                title="Children data requires enhanced safeguards",
                severity=Severity.CRITICAL if level is SecurityLevel.HIGH else Severity.WARNING,
                description="Children data requires age-appropriate notices, minimization, restricted sharing, and stronger consent controls.",
                actions=(
                    "Collect only required fields.",
                    "Add guardian workflow where required.",
                    "Disable profiling and marketing unless reviewed and justified.",
                ),
                references=("Privacy Authority expectations for minors", "GDPR child-specific protections where applicable"),
            )
        )

    if data.employee_monitoring:
        findings.append(
            Finding(
                code="EMP-001",
                title="Employee monitoring requires proportionality",
                severity=Severity.WARNING,
                description="Monitoring workers must be necessary, proportionate, transparent, and limited to a defined workplace purpose.",
                actions=(
                    "Document necessity and less intrusive alternatives.",
                    "Give employee notice before monitoring.",
                    "Restrict access to monitoring outputs.",
                ),
                references=("Israeli workplace privacy case law and Authority guidance",),
            )
        )

    if data.uses_ai_profiling or data.automated_decisions:
        findings.append(
            Finding(
                code="AUTO-001",
                title="Profiling or automated decisioning needs review",
                severity=Severity.WARNING if not data.automated_decisions else Severity.CRITICAL,
                description="Profiling and automated decisions can require impact assessment, explainability, human review, and opt-out or objection handling.",
                actions=(
                    "Map input data, model outputs, and decision effects.",
                    "Add human review for significant effects.",
                    "Record bias, accuracy, and retention controls.",
                ),
                references=("GDPR Articles 21-22 and 35 where applicable", "Privacy Authority transparency expectations"),
            )
        )

    if data.breach_recent:
        findings.append(
            Finding(
                code="IR-001",
                title="Breach triage is active",
                severity=Severity.CRITICAL,
                description="A recent event requires containment, evidence preservation, risk assessment, notification decision, and remediation tracking.",
                actions=(
                    "Open an incident log immediately.",
                    "Preserve access logs and affected-record samples.",
                    "Assess notification duties under Israeli rules and GDPR 72-hour reporting where applicable.",
                    "Send clear notices to affected people when required.",
                ),
                references=("Protection of Privacy Regulations (Data Security), 5777-2017", "GDPR Articles 33-34 where applicable"),
            )
        )

    if data.retention_months is None:
        findings.append(
            Finding(
                code="RET-001",
                title="Retention period is missing",
                severity=Severity.WARNING,
                description="Undefined retention creates excess-data risk and weakens responses to access and deletion requests.",
                actions=(
                    "Set a retention period per purpose.",
                    "Apply deletion, anonymization, or legal-hold rules at the end of the period.",
                ),
                references=("Storage limitation principle",),
            )
        )

    if not data.rights_process_ready:
        findings.append(
            Finding(
                code="RIGHTS-001",
                title="Rights process needs operational owner",
                severity=Severity.WARNING,
                description="Access, correction, deletion, objection, portability, and marketing opt-out requests need a defined intake and response process.",
                actions=(
                    "Create an intake mailbox or form.",
                    "Verify identity before disclosure.",
                    "Track deadlines, decisions, and response evidence.",
                ),
                references=("Israeli access and correction rights", "GDPR Articles 12-23 where applicable"),
            )
        )

    return findings or [
        Finding(
            code="OK-001",
            title="No critical gaps detected",
            severity=Severity.INFO,
            description="The supplied workflow has no deterministic critical finding. Keep records current and re-run after material changes.",
            actions=("Review processor and retention evidence quarterly.",),
            references=MANDATORY_REFERENCES,
        )
    ]


def generate_checklist(
    data: AssessmentInput,
    level: SecurityLevel,
    gdpr_applicable: bool,
    findings: Sequence[Finding],
) -> list[ChecklistItem]:
    """Generate checklist items tied to findings and baseline controls."""

    items = [
        ChecklistItem("INV-001", "inventory", "Document database name, controller, purposes, fields, sources, recipients, and retention.", due_days=14, evidence="database specification"),
        ChecklistItem("NOTICE-010", "transparency", "Publish or update privacy notice before collection.", due_days=14, evidence="versioned notice"),
        ChecklistItem("ACCESS-010", "security", "Review user roles and remove unnecessary access.", due_days=7, evidence="access review log"),
        ChecklistItem("RET-010", "retention", "Approve retention schedule and deletion method per purpose.", due_days=30, evidence="retention schedule"),
        ChecklistItem("RIGHTS-010", "rights", "Create request intake, identity check, deadline tracking, and response templates.", due_days=21, evidence="rights procedure"),
    ]
    if level is SecurityLevel.MEDIUM or level is SecurityLevel.HIGH:
        items.extend(
            [
                ChecklistItem("LOG-020", "security", "Enable access logging and review exceptional access.", due_days=14, evidence="logging configuration"),
                ChecklistItem("DR-020", "security", "Test backup restoration and document results.", due_days=30, evidence="restore test record"),
            ]
        )
    if level is SecurityLevel.HIGH:
        items.extend(
            [
                ChecklistItem("RISK-030", "governance", "Complete formal risk assessment and management approval.", due_days=21, evidence="risk assessment"),
                ChecklistItem("TRAIN-030", "governance", "Train authorized users on sensitive-data handling and incident reporting.", due_days=30, evidence="training log"),
            ]
        )
    if data.processors:
        items.append(ChecklistItem("PROC-020", "suppliers", "Execute processor terms and record subprocessors.", due_days=21, evidence="signed processing terms"))
    if data.cross_border:
        items.append(ChecklistItem("XFER-020", "transfers", "Complete transfer register and safeguard memo.", due_days=21, evidence="transfer assessment"))
    if data.direct_marketing:
        items.append(ChecklistItem("DM-020", "marketing", "Verify consent or source, unsubscribe, and suppression-list logic.", due_days=14, evidence="marketing control test"))
    if data.uses_tracking:
        items.append(ChecklistItem("TRACK-020", "tracking", "Block optional trackers until consent or documented legal basis applies.", due_days=14, evidence="tag test record"))
    if data.breach_recent:
        items.insert(0, ChecklistItem("IR-010", "incident", "Contain incident, preserve evidence, assess reporting duties, and track remediation.", due_days=1, evidence="incident log"))
    if gdpr_applicable:
        items.append(ChecklistItem("GDPR-020", "gdpr", "Maintain GDPR processing record and transfer basis for EU data subjects.", due_days=30, evidence="GDPR record"))
    finding_codes = {finding.code for finding in findings}
    if "AUTO-001" in finding_codes:
        items.append(ChecklistItem("AUTO-020", "profiling", "Document profiling logic, human review, objection route, and accuracy checks.", due_days=30, evidence="profiling assessment"))
    return items


def generate_israel_obligations(data: AssessmentInput, level: SecurityLevel) -> list[str]:
    """Generate Israeli-law operational obligations."""

    obligations = [
        "Prepare a database specification and processing inventory.",
        f"Apply {level.value} security controls under a practical reading of the Data Security Regulations.",
        "Provide clear notice about identity of the controller, purposes, recipients, retention, transfers, and rights.",
        "Operate access and correction rights handling with documented identity verification.",
    ]
    if needs_amendment13_registration_review(data):
        obligations.append("Check Amendment 13 registration duties for public-body databases or data-broker/direct-mailing service databases with more than 10,000 people.")
    if needs_amendment13_notification_review(data):
        obligations.append("Check Amendment 13 notice-to-authority duties for a special-sensitivity database with information on more than 100,000 people.")
    if needs_dpo_review(data):
        obligations.append("Assess appointment of a data protection officer and document contact details for filings or notices.")
    if data.direct_marketing:
        obligations.append("Operate direct-mailing source, consent, opt-out, and suppression controls.")
    if data.cross_border:
        obligations.append("Document cross-border transfer basis, destination, recipient, onward transfer, and safeguards.")
    if data.breach_recent:
        obligations.append("Open a security-incident log and assess notification duties without delay.")
    if data.collects_children_data:
        obligations.append("Apply enhanced transparency, minimization, guardian, and sharing controls for minors.")
    return obligations


def generate_required_documents(data: AssessmentInput, gdpr_applicable: bool) -> list[str]:
    """List documents that should exist before production use."""

    docs = [
        "database specification",
        "privacy notice",
        "retention schedule",
        "access-control matrix",
        "incident-response procedure",
        "rights-request procedure",
    ]
    if data.processors:
        docs.append("processor register and processing terms")
    if data.cross_border:
        docs.append("transfer assessment")
    if data.direct_marketing:
        docs.append("marketing consent and suppression register")
    if data.uses_tracking:
        docs.append("tracker inventory and consent configuration")
    if gdpr_applicable:
        docs.extend(["GDPR record of processing", "GDPR transfer basis", "data-protection impact assessment screening"])
    return docs


def generate_retention_recommendation(data: AssessmentInput) -> str:
    """Generate a retention recommendation."""

    if data.retention_months is None:
        return "Set a documented retention period per purpose before production use. Keep billing and legal records separately from marketing or analytics records."
    if data.retention_months == 0:
        return "Do not retain after immediate transaction completion unless a legal hold or statutory record duty applies."
    return f"Current retention is {data.retention_months} months. Verify that each purpose needs this duration and define deletion, anonymization, or legal-hold handling."


def generate_transfer_controls(data: AssessmentInput, gdpr_applicable: bool) -> list[str]:
    """Generate transfer controls."""

    if not data.cross_border:
        return ["No cross-border transfer was reported. Reassess before adding overseas hosting, support, analytics, or backup providers."]
    controls = ["Maintain a transfer register with country, recipient, purpose, safeguard, and onward-transfer status."]
    for destination in data.destinations or ("unspecified destination",):
        label = destination.strip() or "unspecified destination"
        if label.lower() in ADEQUATE_DESTINATIONS:
            controls.append(f"{label}: record adequacy or permitted-transfer rationale and processor controls.")
        else:
            controls.append(f"{label}: complete safeguard review, transfer-impact analysis, and supplementary controls where needed.")
    if gdpr_applicable:
        controls.append("For GDPR data, document Chapter V basis such as adequacy, standard contractual clauses, or another permitted mechanism.")
    return controls


def generate_breach_actions(data: AssessmentInput, gdpr_applicable: bool) -> list[str]:
    """Generate breach actions."""

    actions = [
        "Maintain incident intake, severity triage, containment, evidence preservation, notification decision, and remediation owner.",
        "Test the incident procedure at least annually or after a material system change.",
    ]
    if data.breach_recent:
        actions.insert(0, "For the active event, freeze relevant logs, identify affected records, contain access, and document decisions.")
        actions.append("Assess notification duties under Israeli data-security rules and notify the Privacy Protection Authority when required.")
        if gdpr_applicable:
            actions.append("Assess GDPR supervisory-authority reporting within 72 hours and affected-person notification where high risk exists.")
    return actions


def score_assessment(findings: Sequence[Finding], level: SecurityLevel) -> int:
    """Calculate a simple readiness score."""

    score = 100
    for finding in findings:
        if finding.severity is Severity.CRITICAL:
            score -= 18
        elif finding.severity is Severity.WARNING:
            score -= 7
        else:
            score -= 0
    if level is SecurityLevel.HIGH:
        score -= 5
    elif level is SecurityLevel.MEDIUM:
        score -= 2
    return max(0, min(100, score))


def make_assessment_id(data: AssessmentInput, environment: str) -> str:
    """Create a stable short ID for equivalent inputs on the same day."""

    payload = json.dumps(_input_to_dict(data), sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(f"{environment}:{payload}:{datetime.now(timezone.utc).date().isoformat()}".encode("utf-8")).hexdigest()
    return f"pcc-{digest[:12]}"


def record_to_markdown(record: Mapping[str, Any]) -> str:
    """Render a persisted record dictionary as Markdown."""

    title = record.get("input", {}).get("business_name", "Assessment")
    lines = [
        f"# Privacy compliance assessment: {title}",
        "",
        f"- Environment: `{record.get('environment')}`",
        f"- Assessment ID: `{record.get('id')}`",
        f"- Created: `{record.get('created_at')}`",
        f"- Security level: `{record.get('security_level')}`",
        f"- GDPR applicable: `{str(record.get('gdpr_applicable')).lower()}`",
        f"- Score: `{record.get('score')}/100`",
        "",
        "## Findings",
    ]
    for finding in record.get("findings", []):
        lines.extend(
            [
                f"### {finding.get('code')}: {finding.get('title')}",
                f"- Severity: `{finding.get('severity')}`",
                f"- Detail: {finding.get('description')}",
            ]
        )
        actions = finding.get("actions") or []
        if actions:
            lines.append("- Actions:")
            lines.extend(f"  - {action}" for action in actions)
        lines.append("")
    lines.append("## Checklist")
    for item in record.get("checklist", []):
        lines.append(f"- [{item.get('status')}] {item.get('id')}: {item.get('task')}")
    return "\n".join(lines).rstrip() + "\n"


def re_slug(value: str) -> str:
    """Return a conservative filename slug."""

    return "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)[:120]


def _parse_lawful_basis(value: Any) -> LawfulBasis:
    if isinstance(value, LawfulBasis):
        return value
    try:
        return LawfulBasis(str(value))
    except ValueError as exc:
        allowed = ", ".join(item.value for item in LawfulBasis)
        raise ValueError(f"lawful_basis must be one of: {allowed}") from exc


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value)
    return (str(value),)


def _normalized_set(values: Iterable[str]) -> set[str]:
    normalized = {value.strip().lower() for value in values if value.strip()}
    return {value for value in normalized if value in SENSITIVE_MARKERS or value}


def _input_to_dict(data: AssessmentInput) -> dict[str, Any]:
    result = asdict(data)
    result["lawful_basis"] = data.lawful_basis.value
    for key in ("sensitive_categories", "purposes", "data_subjects", "destinations", "processors"):
        result[key] = list(result[key])
    return result
