"""Typed helper client for Israeli corporate-law workflows.

The module performs no network requests. It creates structured checklists,
validation results, case records, and workflow summaries that can be reviewed
by an Israeli professional before a filing or signature.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Sequence


RiskLevel = Literal["low", "medium", "high"]
EnvironmentName = Literal["sandbox", "production"]
ActionName = Literal[
    "incorporation",
    "annual_report",
    "share_transfer",
    "director_change",
    "shareholder_agreement",
    "due_diligence",
    "dormant_cleanup",
]

VALIDATED_ON = "02/06/2026"
VAT_STANDARD_RATE = 0.18
EXEMPT_DEALER_THRESHOLD_2026_ILS = 122_833
COMPANY_ANNUAL_FEE_2026 = {
    "reduced_until": "31/03/2026",
    "reduced_amount_ils": 1338,
    "regular_from": "01/04/2026",
    "regular_amount_ils": 1777,
}
PARTNERSHIP_ANNUAL_FEE_2026 = {
    "reduced_until": "31/03/2026",
    "reduced_amount_ils": 1333,
    "regular_from": "01/04/2026",
    "regular_amount_ils": 1771,
}


class WorkflowError(ValueError):
    """Raised when a workflow input is incomplete or inconsistent."""


class EntityRecommendation(str, Enum):
    """Entity paths to investigate."""

    INDIVIDUAL = "individual_business"
    PARTNERSHIP = "partnership_or_contractual_jv"
    PRIVATE_COMPANY = "private_company_limited_by_shares"
    NON_PROFIT = "non_profit_structure"
    REGULATED_REVIEW = "regulated_activity_review_required"


@dataclass(frozen=True)
class RegulatoryFact:
    """A dated regulatory fact validated during the web-validation pass."""

    key: str
    value: Any
    validated_on: str
    source_note: str

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class ActionPlanItem:
    """A single practical action item."""

    step: int
    title: str
    details: str
    owner: str = "business owner"
    professional_review: bool = False


@dataclass(frozen=True)
class DecisionResult:
    """Structured entity-choice or workflow decision output."""

    recommendation: str
    rationale: List[str]
    next_steps: List[ActionPlanItem]
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return {
            "recommendation": self.recommendation,
            "rationale": list(self.rationale),
            "next_steps": [asdict(item) for item in self.next_steps],
            "warnings": list(self.warnings),
        }

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        """Return formatted JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


@dataclass(frozen=True)
class CompanyProfile:
    """Basic company facts used by workflows."""

    company_number: str
    company_name: str
    registered_office: str
    directors: Sequence[str]
    shareholders: Sequence[str]
    report_year: Optional[int] = None


@dataclass(frozen=True)
class CorporateCase:
    """A lightweight case record used to chain workflow steps."""

    case_id: str
    environment: EnvironmentName
    business_activity: str
    owners_count: int
    created_on: str
    company_number: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return asdict(self)

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        """Return formatted JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


@dataclass(frozen=True)
class ChecklistResult:
    """Checklist result with blocking issues and escalation flags."""

    action: str
    items: List[ActionPlanItem]
    blockers: List[str] = field(default_factory=list)
    professional_review_triggers: List[str] = field(default_factory=list)
    case_id: Optional[str] = None
    environment: EnvironmentName = "sandbox"

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return {
            "action": self.action,
            "case_id": self.case_id,
            "environment": self.environment,
            "items": [asdict(item) for item in self.items],
            "blockers": list(self.blockers),
            "professional_review_triggers": list(self.professional_review_triggers),
        }

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        """Return formatted JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    def to_markdown(self) -> str:
        """Render a readable Markdown checklist."""
        lines = [f"# {self.action.replace('_', ' ').title()} Checklist", ""]
        if self.case_id:
            lines.extend([f"Case ID: `{self.case_id}`", f"Environment: `{self.environment}`", ""])
        if self.blockers:
            lines.append("## Blockers")
            lines.extend(f"- {item}" for item in self.blockers)
            lines.append("")
        lines.append("## Steps")
        for item in self.items:
            review = " Professional review required." if item.professional_review else ""
            lines.append(f"{item.step}. **{item.title}** - {item.details}{review}")
        if self.professional_review_triggers:
            lines.append("")
            lines.append("## Professional-review triggers")
            lines.extend(f"- {item}" for item in self.professional_review_triggers)
        return "\n".join(lines)


@dataclass(frozen=True)
class ValidationResult:
    """Simple validation result."""

    valid: bool
    message: str
    normalized: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return asdict(self)

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        """Return formatted JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


class CorporateLawGuideClient:
    """Structured helper for Israeli corporate-law workflows."""

    def __init__(self, *, environment: EnvironmentName = "sandbox") -> None:
        self.environment = self._normalize_environment(environment)
        self._cases: Dict[str, CorporateCase] = {}

    def create_case(
        self,
        business_activity: str,
        owners_count: int,
        *,
        company_number: Optional[str] = None,
        notes: Optional[Sequence[str]] = None,
        environment: Optional[EnvironmentName] = None,
    ) -> CorporateCase:
        """Create an in-memory case and return an identifier for chained steps."""
        if owners_count < 1:
            raise WorkflowError("owners_count must be at least 1")
        activity = business_activity.strip()
        if not activity:
            raise WorkflowError("business_activity is required")
        env = self._normalize_environment(environment or self.environment)
        if company_number:
            validation = self.validate_company_number(company_number)
            if not validation.valid:
                raise WorkflowError(validation.message)
            company_number = validation.normalized
        case_id = self._case_id(activity, owners_count, company_number, env)
        record = CorporateCase(
            case_id=case_id,
            environment=env,
            business_activity=activity,
            owners_count=owners_count,
            created_on=date.today().strftime("%d/%m/%Y"),
            company_number=company_number,
            notes=list(notes or []),
        )
        self._cases[case_id] = record
        return record

    async def acreate_case(self, *args: Any, **kwargs: Any) -> CorporateCase:
        """Async wrapper for create_case."""
        await asyncio.sleep(0)
        return self.create_case(*args, **kwargs)

    def get_case(self, case_id: str) -> CorporateCase:
        """Return a previously created in-memory case."""
        try:
            return self._cases[case_id]
        except KeyError as exc:
            raise WorkflowError("case_id was not created in this client instance") from exc

    def validate_company_number(self, company_number: str) -> ValidationResult:
        """Validate the common nine-digit Israeli company-number format."""
        normalized = re.sub(r"\D", "", str(company_number))
        if len(normalized) != 9:
            return ValidationResult(
                valid=False,
                message="Israeli company numbers are commonly handled as 9-digit strings.",
                normalized=normalized or None,
            )
        return ValidationResult(
            valid=True,
            message="Company number format is plausible. Verify against an official extract.",
            normalized=normalized,
        )

    def normalize_date(self, value: str) -> ValidationResult:
        """Normalize DD/MM/YYYY, DD-MM-YYYY, or ISO date strings to DD/MM/YYYY."""
        value = value.strip()
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", value):
            day, month, year = map(int, value.split("/"))
            try:
                parsed = date(year, month, day)
            except ValueError as exc:
                return ValidationResult(False, f"Invalid DD/MM/YYYY date: {exc}", None)
            return ValidationResult(True, "Date is already in DD/MM/YYYY format.", parsed.strftime("%d/%m/%Y"))
        if re.fullmatch(r"\d{2}-\d{2}-\d{4}", value):
            day, month, year = map(int, value.split("-"))
            try:
                parsed = date(year, month, day)
            except ValueError as exc:
                return ValidationResult(False, f"Invalid DD-MM-YYYY date: {exc}", None)
            return ValidationResult(True, "Converted DD-MM-YYYY date to DD/MM/YYYY.", parsed.strftime("%d/%m/%Y"))
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            year, month, day = map(int, value.split("-"))
            try:
                parsed = date(year, month, day)
            except ValueError as exc:
                return ValidationResult(False, f"Invalid ISO date: {exc}", None)
            return ValidationResult(True, "Converted ISO date to DD/MM/YYYY.", parsed.strftime("%d/%m/%Y"))
        return ValidationResult(False, "Use DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD.", None)

    def classify_entity_need(
        self,
        business_activity: str,
        owners_count: int,
        liability_risk: RiskLevel = "medium",
        fundraising_plan: bool = False,
        regulated_activity: bool = False,
        non_profit_purpose: bool = False,
    ) -> DecisionResult:
        """Classify the entity structure that should be investigated first."""
        if owners_count < 1:
            raise WorkflowError("owners_count must be at least 1")
        activity = business_activity.strip()
        if not activity:
            raise WorkflowError("business_activity is required")

        rationale: List[str] = []
        warnings: List[str] = []
        steps: List[ActionPlanItem] = []

        if regulated_activity:
            recommendation = EntityRecommendation.REGULATED_REVIEW.value
            rationale.append("Regulated activity can require approval beyond corporate registration.")
            warnings.append("Do not start regulated activity only because an entity was registered.")
            steps.append(ActionPlanItem(1, "Map regulator", "Identify sector regulator and licensing path.", professional_review=True))
            steps.append(ActionPlanItem(2, "Choose entity", "Compare company, partnership, and licensing constraints.", professional_review=True))
            return DecisionResult(recommendation, rationale, steps, warnings)

        if non_profit_purpose:
            recommendation = EntityRecommendation.NON_PROFIT.value
            rationale.append("Public-benefit or non-profit purposes often fit an amuta or public-benefit company better.")
            steps.append(ActionPlanItem(1, "Define purpose", "Confirm whether profits may be distributed."))
            steps.append(ActionPlanItem(2, "Compare forms", "Compare amuta, public-benefit company, and ordinary company.", professional_review=True))
            return DecisionResult(recommendation, rationale, steps, warnings)

        if fundraising_plan or liability_risk == "high":
            recommendation = EntityRecommendation.PRIVATE_COMPANY.value
            rationale.append("Fundraising, liability exposure, employees, leases, contracts, or IP ownership usually justify company review.")
            steps.extend(
                [
                    ActionPlanItem(1, "Prepare names", "Create at least three Hebrew company-name alternatives."),
                    ActionPlanItem(2, "Design share capital", "Choose simple ordinary shares unless special rights are needed."),
                    ActionPlanItem(3, "Prepare articles", "Align articles with any shareholder agreement.", professional_review=True),
                    ActionPlanItem(4, "Plan tax registration", "Coordinate company, VAT, withholding, and National Insurance steps.", professional_review=True),
                ]
            )
        elif owners_count == 1 and liability_risk == "low":
            recommendation = EntityRecommendation.INDIVIDUAL.value
            rationale.append("A single low-risk freelancer may not need company overhead at the first stage.")
            steps.extend(
                [
                    ActionPlanItem(1, "Check tax status", "Compare exempt dealer, licensed dealer, and company with a CPA.", professional_review=True),
                    ActionPlanItem(2, "Protect contracts", "Use clear service terms, liability caps, and insurance where relevant."),
                ]
            )
        else:
            recommendation = EntityRecommendation.PARTNERSHIP.value
            rationale.append("Multiple owners without immediate fundraising should compare company and partnership governance.")
            warnings.append("A partnership can create personal liability if not structured carefully.")
            steps.extend(
                [
                    ActionPlanItem(1, "Draft owner terms", "Document ownership, authority, exit, expenses, and liability."),
                    ActionPlanItem(2, "Compare company", "Evaluate whether separate legal personality is worth the cost.", professional_review=True),
                ]
            )

        if owners_count == 2:
            warnings.append("Equal ownership can create deadlock; add a deadlock mechanism.")

        return DecisionResult(recommendation, rationale, steps, warnings)

    async def aclassify_entity_need(self, *args: Any, **kwargs: Any) -> DecisionResult:
        """Async wrapper for classify_entity_need."""
        await asyncio.sleep(0)
        return self.classify_entity_need(*args, **kwargs)

    def build_incorporation_checklist(
        self,
        owners_count: int,
        business_activity: str,
        regulated_activity: bool = False,
        foreign_shareholders: bool = False,
        *,
        case_id: Optional[str] = None,
    ) -> ChecklistResult:
        """Build a practical incorporation checklist."""
        if owners_count < 1:
            raise WorkflowError("owners_count must be at least 1")
        if not business_activity.strip():
            raise WorkflowError("business_activity is required")
        items = [
            ActionPlanItem(1, "Confirm structure", "Compare individual business, partnership, and private company."),
            ActionPlanItem(2, "Prepare company names", "Create at least three Hebrew alternatives and optional English name."),
            ActionPlanItem(3, "Design share structure", "Define authorized and issued shares, classes, and founder allocations."),
            ActionPlanItem(4, "Prepare articles", "Align articles with governance and share-transfer rules.", professional_review=True),
            ActionPlanItem(5, "Collect director consents", "Collect details and consent for each first director."),
            ActionPlanItem(6, "Submit incorporation", "Use the current Companies Authority process and archive confirmation."),
            ActionPlanItem(7, "Open statutory books", "Open shareholders register, directors register, minutes, and cap table."),
            ActionPlanItem(8, "Approve signing rights", "Adopt a bank signing-rights resolution after incorporation."),
            ActionPlanItem(9, "Coordinate tax files", "Coordinate income tax, VAT, withholding, and National Insurance.", professional_review=True),
        ]
        triggers: List[str] = []
        blockers: List[str] = []
        if regulated_activity:
            blockers.append("Regulated activity requires licensing analysis before launch.")
            triggers.append("Sector-specific licensing")
        if foreign_shareholders:
            triggers.append("Foreign shareholder identity, tax, bank, and sanctions review")
        if owners_count == 2:
            triggers.append("Deadlock mechanism for equal or near-equal founders")
        return ChecklistResult("incorporation", items, blockers, triggers, case_id=case_id, environment=self.environment)

    async def abuild_incorporation_checklist(self, *args: Any, **kwargs: Any) -> ChecklistResult:
        """Async wrapper for build_incorporation_checklist."""
        await asyncio.sleep(0)
        return self.build_incorporation_checklist(*args, **kwargs)

    def annual_report_checklist(
        self,
        company_number: str,
        year: int,
        has_changes: bool = False,
        *,
        case_id: Optional[str] = None,
    ) -> ChecklistResult:
        """Build annual-report and fee-status checklist."""
        validation = self.validate_company_number(company_number)
        blockers = [] if validation.valid else [validation.message]
        items = [
            ActionPlanItem(1, "Retrieve company extract", "Compare official status with internal records."),
            ActionPlanItem(2, "Confirm registered office", "Check address used for official notices."),
            ActionPlanItem(3, "Confirm directors", "Reconcile appointments and resignations."),
            ActionPlanItem(4, "Confirm shareholders", "Reconcile share register and cap table."),
            ActionPlanItem(5, "Check annual fee", "For 2026, verify whether ₪1,338 reduced fee or ₪1,777 regular fee applies before payment."),
            ActionPlanItem(6, "Prepare annual report", f"Prepare report for {year}."),
            ActionPlanItem(7, "Submit and archive", "Save filing confirmation and receipts."),
        ]
        triggers = []
        if has_changes:
            triggers.append("Share, director, address, or auditor changes need reconciliation before filing")
            items.insert(4, ActionPlanItem(5, "Reconcile changes", "Collect approvals for changes during the year.", professional_review=True))
            for idx, item in enumerate(items, start=1):
                items[idx - 1] = ActionPlanItem(idx, item.title, item.details, item.owner, item.professional_review)
        return ChecklistResult("annual_report", items, blockers, triggers, case_id=case_id, environment=self.environment)

    def share_transfer_checklist(
        self,
        seller_shares: int,
        transfer_quantity: int,
        family_transfer: bool = False,
        new_shareholder: bool = False,
        tax_review_done: bool = False,
        *,
        case_id: Optional[str] = None,
    ) -> ChecklistResult:
        """Build share-transfer checklist."""
        blockers: List[str] = []
        triggers: List[str] = []
        if seller_shares < transfer_quantity:
            blockers.append("Seller does not hold enough shares for the requested transfer.")
        if transfer_quantity <= 0:
            blockers.append("Transfer quantity must be positive.")
        if not tax_review_done:
            triggers.append("Tax review before closing")
        if family_transfer:
            triggers.append("Permitted-transfer and family tax review")
        if new_shareholder:
            triggers.append("Deed of adherence for new shareholder")

        items = [
            ActionPlanItem(1, "Read articles", "Identify transfer restrictions and approval requirements."),
            ActionPlanItem(2, "Read shareholder agreement", "Check right of first refusal, co-sale, sale-compulsion, lock-up, and permitted transfers."),
            ActionPlanItem(3, "Confirm seller balance", "Compare proposed transfer against shareholders register."),
            ActionPlanItem(4, "Obtain approvals", "Collect board/shareholder waivers or approvals.", professional_review=True),
            ActionPlanItem(5, "Prepare transfer deed", "Prepare signed transfer instrument and consideration record.", professional_review=True),
            ActionPlanItem(6, "Update register", "Update shareholders register only after completion."),
            ActionPlanItem(7, "Archive records", "Save approvals, deed, cap table, and tax memo."),
        ]
        return ChecklistResult("share_transfer", items, blockers, triggers, case_id=case_id, environment=self.environment)

    def director_change_checklist(
        self,
        action: Literal["appoint", "resign", "remove"],
        bank_signing_change: bool = False,
        *,
        case_id: Optional[str] = None,
    ) -> ChecklistResult:
        """Build director-change checklist."""
        if action not in {"appoint", "resign", "remove"}:
            raise WorkflowError("action must be appoint, resign, or remove")
        items = [
            ActionPlanItem(1, "Check articles", "Confirm who may approve the director change."),
            ActionPlanItem(2, "Collect document", "Collect consent, resignation letter, or removal approval."),
            ActionPlanItem(3, "Approve change", "Use the correct company organ and record minutes."),
            ActionPlanItem(4, "Update directors register", "Record effective date and details."),
            ActionPlanItem(5, "File update", "Submit registrar update where required."),
            ActionPlanItem(6, "Archive confirmation", "Save signed records and filing confirmation."),
        ]
        triggers = []
        if bank_signing_change:
            items.append(ActionPlanItem(7, "Update bank authority", "Adopt and deliver bank signing-rights resolution."))
            triggers.append("Bank signing rights are separate from director status")
        return ChecklistResult("director_change", items, [], triggers, case_id=case_id, environment=self.environment)

    def shareholder_agreement_scan(
        self,
        founders_count: int,
        equal_holdings: bool = False,
        investor_round: bool = False,
        family_company: bool = False,
        *,
        case_id: Optional[str] = None,
    ) -> ChecklistResult:
        """Build shareholder-agreement issue-scan checklist."""
        if founders_count < 1:
            raise WorkflowError("founders_count must be at least 1")
        items = [
            ActionPlanItem(1, "Reconcile cap table", "Match agreement percentages to statutory records."),
            ActionPlanItem(2, "Check board rights", "Define appointment, removal, observer, and quorum rights."),
            ActionPlanItem(3, "Check reserved matters", "List matters requiring special approval."),
            ActionPlanItem(4, "Check transfer restrictions", "Review right of first refusal, co-sale, sale-compulsion, lock-up, and permitted transfers."),
            ActionPlanItem(5, "Check leaver rules", "Review vesting, reverse vesting, good leaver, and bad leaver terms."),
            ActionPlanItem(6, "Check intellectual property", "Ensure founder and contractor intellectual property belongs to the company.", professional_review=True),
            ActionPlanItem(7, "Align articles", "Identify clauses that need articles implementation.", professional_review=True),
        ]
        triggers = []
        if equal_holdings and founders_count == 2:
            triggers.append("50/50 deadlock mechanism")
        if investor_round:
            triggers.append("Investor compatibility, securities, options, anti-dilution, and information rights")
        if family_company:
            triggers.append("Inheritance, divorce, related-party, and valuation mechanics")
        return ChecklistResult("shareholder_agreement", items, [], triggers, case_id=case_id, environment=self.environment)

    def due_diligence_checklist(self, *, case_id: Optional[str] = None) -> ChecklistResult:
        """Build investor or sale due-diligence checklist."""
        items = [
            ActionPlanItem(1, "Build folder index", "Create numbered folders for constitutional, ownership, minutes, intellectual property, tax, bank, and contracts."),
            ActionPlanItem(2, "Reconcile cap table", "Tie every share line to approval and register entry.", professional_review=True),
            ActionPlanItem(3, "Collect articles", "Include all amendments."),
            ActionPlanItem(4, "Collect minutes", "Include board and shareholder approvals."),
            ActionPlanItem(5, "Collect intellectual-property assignments", "Include founders, employees, and contractors.", professional_review=True),
            ActionPlanItem(6, "Check annual compliance", "Save annual reports and fee confirmations."),
            ActionPlanItem(7, "Check charges", "List bank or lender security interests."),
        ]
        return ChecklistResult("due_diligence", items, [], ["Financing or sale transaction"], case_id=case_id, environment=self.environment)

    def checklist_for_case(
        self,
        case_id: str,
        action: ActionName,
        **kwargs: Any,
    ) -> ChecklistResult:
        """Create a checklist tied to a case identifier."""
        case = self._cases.get(case_id)
        owners = int(kwargs.pop("owners_count", case.owners_count if case else 1))
        activity = str(kwargs.pop("business_activity", case.business_activity if case else "business activity"))
        if action == "incorporation":
            return self.build_incorporation_checklist(owners, activity, case_id=case_id, **kwargs)
        if action == "annual_report":
            company_number = kwargs.pop("company_number", case.company_number if case else None)
            if not company_number:
                raise WorkflowError("company_number is required for annual_report")
            return self.annual_report_checklist(company_number, int(kwargs.pop("year")), case_id=case_id, **kwargs)
        if action == "share_transfer":
            return self.share_transfer_checklist(case_id=case_id, **kwargs)
        if action == "director_change":
            return self.director_change_checklist(case_id=case_id, **kwargs)
        if action == "shareholder_agreement":
            return self.shareholder_agreement_scan(case_id=case_id, **kwargs)
        if action == "due_diligence":
            return self.due_diligence_checklist(case_id=case_id)
        if action == "dormant_cleanup":
            return self.dormant_cleanup_checklist(case_id=case_id)
        raise WorkflowError(f"Unsupported action: {action}")

    def dormant_cleanup_checklist(self, *, case_id: Optional[str] = None) -> ChecklistResult:
        """Build dormant-company cleanup checklist."""
        items = [
            ActionPlanItem(1, "Confirm activity", "Check assets, debts, employees, contracts, and bank accounts."),
            ActionPlanItem(2, "Check registrar status", "Review annual reports, annual fees, directors, address, and warnings."),
            ActionPlanItem(3, "Coordinate tax status", "Check income tax, VAT, withholding, and National Insurance files.", professional_review=True),
            ActionPlanItem(4, "Decide route", "Choose maintain, sell, merge, or liquidate after status review.", professional_review=True),
            ActionPlanItem(5, "Archive confirmations", "Save reports, fee receipts, tax confirmations, and closure documents."),
        ]
        return ChecklistResult("dormant_cleanup", items, [], ["Liquidation or insolvency review"], case_id=case_id, environment=self.environment)

    def get_regulatory_facts(self) -> List[RegulatoryFact]:
        """Return web-validated, dated regulatory facts bundled with the guide."""
        return [
            RegulatoryFact(
                key="vat_standard_rate",
                value=VAT_STANDARD_RATE,
                validated_on=VALIDATED_ON,
                source_note="Tax Authority VAT history and 2026 tax summaries confirmed 18%.",
            ),
            RegulatoryFact(
                key="company_annual_fee_2026",
                value=dict(COMPANY_ANNUAL_FEE_2026),
                validated_on=VALIDATED_ON,
                source_note="Companies Authority annual-fee service confirmed reduced and regular 2026 amounts.",
            ),
            RegulatoryFact(
                key="partnership_annual_fee_2026",
                value=dict(PARTNERSHIP_ANNUAL_FEE_2026),
                validated_on=VALIDATED_ON,
                source_note="Companies Authority annual-fee service confirmed reduced and regular 2026 partnership amounts.",
            ),
            RegulatoryFact(
                key="exempt_dealer_threshold_2026_ils",
                value=EXEMPT_DEALER_THRESHOLD_2026_ILS,
                validated_on=VALIDATED_ON,
                source_note="Tax Authority exempt-dealer service confirmed the 2026 threshold, subject to occupation exclusions.",
            ),
        ]

    def regulatory_facts_payload(self) -> Dict[str, Any]:
        """Return a compact regulatory-facts payload for JSON output."""
        return {fact.key: fact.value for fact in self.get_regulatory_facts()} | {"validated_on": VALIDATED_ON}

    def render_json(self, result: Any) -> str:
        """Render dataclass or structured result as JSON."""
        if hasattr(result, "to_dict"):
            payload = result.to_dict()
        elif hasattr(result, "__dataclass_fields__"):
            payload = asdict(result)
        else:
            payload = result
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def save_markdown(self, result: ChecklistResult, path: str | Path) -> Path:
        """Save a checklist as Markdown."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result.to_markdown() + "\n", encoding="utf-8")
        return target

    @staticmethod
    def _normalize_environment(environment: str) -> EnvironmentName:
        if environment not in {"sandbox", "production"}:
            raise WorkflowError("environment must be sandbox or production")
        return environment  # type: ignore[return-value]

    @staticmethod
    def _case_id(activity: str, owners_count: int, company_number: Optional[str], environment: str) -> str:
        seed = f"{environment}|{activity.lower()}|{owners_count}|{company_number or ''}|{uuid.uuid4().hex}"
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
        return f"clg_{digest}"


def load_client(*, environment: EnvironmentName = "sandbox") -> CorporateLawGuideClient:
    """Create a client instance."""
    return CorporateLawGuideClient(environment=environment)


__all__ = [
    "ActionPlanItem",
    "ChecklistResult",
    "CompanyProfile",
    "CorporateCase",
    "CorporateLawGuideClient",
    "RegulatoryFact",
    "DecisionResult",
    "EntityRecommendation",
    "ValidationResult",
    "WorkflowError",
    "load_client",
]

