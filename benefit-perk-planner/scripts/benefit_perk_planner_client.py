"""Benefit and perk planning client for Israeli small businesses, freelancers, consumers, and employees."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal


EntityType = Literal["employer", "freelancer", "consumer", "employee"]
Goal = Literal["retention", "equity", "cost_control", "tax_efficiency", "wellbeing", "simplicity"]
Environment = Literal["sandbox", "production"]

VERIFIED_2026_CHECKPOINTS: dict[str, str] = {
    "vat_rate": "18% from 01/01/2025",
    "employee_pension_baseline": "18.5% total: 6% employee, 6.5% employer pension, 6% severance",
    "self_employed_pension": "4.45% and 12.55% brackets; verify current average wage",
    "israel_invoice_threshold": "₪10,000 from 01/01/2026; ₪5,000 from 01/06/2026",
    "api_webhooks": "webhooks not publicly confirmed; do not invent; require official or vendor documentation",
}


class PlannerError(ValueError):
    """Raised when planner input is invalid."""


class Severity(str, Enum):
    """Planning issue severity."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class BenefitItem:
    """Single benefit recommendation."""

    name: str
    monthly_cost_ils: float
    eligibility: str
    rules: str
    owner: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable item."""
        return asdict(self)


@dataclass(slots=True)
class PlanningIssue:
    """Risk, assumption, or implementation issue."""

    code: str
    severity: Severity
    message: str
    action: str

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable issue."""
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass(slots=True)
class BenefitRequest:
    """Planner request."""

    entity_type: EntityType
    monthly_budget_ils: float | None = None
    employee_count: int | None = None
    gross_salary_ils: float | None = None
    monthly_income_ils: float | None = None
    goals: list[Goal] = field(default_factory=list)
    work_model: str = "unspecified"
    location: str = "Israel"
    existing_benefits: list[str] = field(default_factory=list)
    cash_buffer_months: float | None = None
    includes_contractors: bool = False
    wants_keren_hishtalmut: bool = False
    wants_meal_benefit: bool = True
    wants_wellness: bool = True
    notes: str = ""

    def validate(self) -> None:
        """Validate request."""
        if self.entity_type not in {"employer", "freelancer", "consumer", "employee"}:
            raise PlannerError(f"unsupported entity_type: {self.entity_type}")
        numeric_fields = {
            "monthly_budget_ils": self.monthly_budget_ils,
            "employee_count": self.employee_count,
            "gross_salary_ils": self.gross_salary_ils,
            "monthly_income_ils": self.monthly_income_ils,
            "cash_buffer_months": self.cash_buffer_months,
        }
        for name, value in numeric_fields.items():
            if value is not None and value < 0:
                raise PlannerError(f"{name} must not be negative")


@dataclass(slots=True)
class BenefitPlan:
    """Planner response."""

    plan_id: str
    assumptions: list[str]
    recommended_package: list[BenefitItem]
    mandatory_checks: list[str]
    alternatives: list[dict[str, str]]
    implementation_steps: list[str]
    review_metrics: list[str]
    issues: list[PlanningIssue]
    estimated_monthly_cost_ils: float
    remaining_budget_ils: float | None
    environment: Environment = "sandbox"

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable plan."""
        return {
            "plan_id": self.plan_id,
            "environment": self.environment,
            "assumptions": self.assumptions,
            "recommended_package": [item.to_dict() for item in self.recommended_package],
            "mandatory_checks": self.mandatory_checks,
            "alternatives": self.alternatives,
            "implementation_steps": self.implementation_steps,
            "review_metrics": self.review_metrics,
            "issues": [issue.to_dict() for issue in self.issues],
            "estimated_monthly_cost_ils": round(self.estimated_monthly_cost_ils, 2),
            "remaining_budget_ils": None
            if self.remaining_budget_ils is None
            else round(self.remaining_budget_ils, 2),
        }

    def to_markdown(self) -> str:
        """Render plan as Markdown."""
        lines: list[str] = [
            "## Benefit plan",
            "",
            f"Plan ID: `{self.plan_id}`",
            f"Environment: `{self.environment}`",
            "",
            "### Assumptions",
        ]
        lines.extend(f"- {assumption}" for assumption in self.assumptions)
        lines.extend(
            [
                "",
                "### Recommended package",
                "| Benefit | Monthly cost | Eligibility | Rules | Admin owner |",
                "|---|---:|---|---|---|",
            ]
        )
        for item in self.recommended_package:
            lines.append(
                f"| {item.name} | ₪{item.monthly_cost_ils:,.0f} | {item.eligibility} | {item.rules} | {item.owner} |"
            )
        lines.extend(["", "### Mandatory checks"])
        lines.extend(f"- {check}" for check in self.mandatory_checks)
        lines.extend(["", "### Issues and safeguards"])
        if self.issues:
            for issue in self.issues:
                lines.append(
                    f"- **{issue.code} ({issue.severity.value})**: {issue.message} Action: {issue.action}"
                )
        else:
            lines.append("- No material issues identified from supplied inputs.")
        lines.extend(["", "### Alternatives considered"])
        lines.append("| Option | Pros | Cons | Use when |")
        lines.append("|---|---|---|---|")
        for alt in self.alternatives:
            lines.append(f"| {alt['option']} | {alt['pros']} | {alt['cons']} | {alt['use_when']} |")
        lines.extend(["", "### Implementation checklist"])
        lines.extend(f"{index}. {step}" for index, step in enumerate(self.implementation_steps, 1))
        lines.extend(["", "### Review metrics"])
        lines.extend(f"- {metric}" for metric in self.review_metrics)
        lines.append("")
        lines.append(f"Estimated monthly cost: ₪{self.estimated_monthly_cost_ils:,.0f}")
        if self.remaining_budget_ils is not None:
            lines.append(f"Remaining monthly budget: ₪{self.remaining_budget_ils:,.0f}")
        lines.append("")
        lines.append(
            "Verify current statutory rates, annual ceilings, provider terms, and payroll treatment before implementation."
        )
        return "\n".join(lines)


class BenefitPlannerClient:
    """Synchronous benefit planner."""

    def __init__(self, environment: Environment = "sandbox", conservative: bool = True) -> None:
        if environment not in {"sandbox", "production"}:
            raise PlannerError("environment must be sandbox or production")
        self.environment = environment
        self.conservative = conservative

    def plan(self, request: BenefitRequest) -> BenefitPlan:
        """Create a benefit plan without storing it."""
        request.validate()
        if request.entity_type == "employer":
            plan = self._plan_employer(request)
        elif request.entity_type == "freelancer":
            plan = self._plan_freelancer(request)
        elif request.entity_type == "consumer":
            plan = self._plan_consumer(request)
        else:
            plan = self._plan_employee(request)
        return plan

    def create_plan(self, request: BenefitRequest, store_dir: str | Path | None = None) -> dict[str, Any]:
        """Create, persist, and return a plan creation response with a plan_id."""
        plan = self.plan(request)
        store = Path(store_dir or os.environ.get("BENEFIT_PLANNER_STORE", ".benefit-perk-planner"))
        store.mkdir(parents=True, exist_ok=True)
        target = store / f"{plan.plan_id}.json"
        target.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return {"plan_id": plan.plan_id, "path": str(target), "environment": self.environment, "status": "created"}

    def get_plan(self, plan_id: str, store_dir: str | Path | None = None) -> dict[str, Any]:
        """Read a stored plan by plan_id."""
        if not re_plan_id(plan_id):
            raise PlannerError("plan_id must contain only letters, numbers, underscores, or hyphens")
        store = Path(store_dir or os.environ.get("BENEFIT_PLANNER_STORE", ".benefit-perk-planner"))
        target = store / f"{plan_id}.json"
        if not target.exists():
            raise PlannerError(f"plan not found: {plan_id}")
        return json.loads(target.read_text(encoding="utf-8"))

    def _new_plan(
        self,
        *,
        assumptions: list[str],
        recommended_package: list[BenefitItem],
        mandatory_checks: list[str],
        alternatives: list[dict[str, str]],
        implementation_steps: list[str],
        review_metrics: list[str],
        issues: list[PlanningIssue],
        estimated_monthly_cost_ils: float,
        remaining_budget_ils: float | None,
    ) -> BenefitPlan:
        return BenefitPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:12]}",
            assumptions=assumptions,
            recommended_package=recommended_package,
            mandatory_checks=mandatory_checks,
            alternatives=alternatives,
            implementation_steps=implementation_steps,
            review_metrics=review_metrics,
            issues=issues,
            estimated_monthly_cost_ils=estimated_monthly_cost_ils,
            remaining_budget_ils=remaining_budget_ils,
            environment=self.environment,
        )

    def _plan_employer(self, request: BenefitRequest) -> BenefitPlan:
        employees = request.employee_count or 10
        budget = request.monthly_budget_ils
        per_employee_budget = (budget / employees) if budget is not None and employees else None
        assumptions = [
            "Entity type: employer.",
            f"Employee count: {employees}.",
            f"Location: {request.location or 'Israel'}.",
            f"Work model: {request.work_model or 'unspecified'}.",
        ]
        if budget is None:
            assumptions.append("No budget supplied; balanced small-business tier used.")
            per_employee_budget = 650
            budget = per_employee_budget * employees
        else:
            assumptions.append(f"Monthly budget: ₪{budget:,.0f}.")

        package: list[BenefitItem] = [
            BenefitItem(
                name="Mandatory pension and severance administration",
                monthly_cost_ils=0,
                eligibility="employees",
                rules="configure payroll, fund details, remittance confirmation, and document retention",
                owner="payroll",
                notes=["Cost depends on salary and current legal requirements."],
            )
        ]
        issues: list[PlanningIssue] = []

        if request.wants_meal_benefit:
            daily_cap = 25 if per_employee_budget < 450 else 35 if per_employee_budget < 1000 else 45
            monthly_cap = min(daily_cap * 22, max(0, per_employee_budget * 0.65))
            package.append(
                BenefitItem(
                    name="Meal benefit",
                    monthly_cost_ils=monthly_cap * employees,
                    eligibility="active employees, pro-rated by eligible workdays",
                    rules=f"₪{daily_cap:.0f} daily cap and ₪{monthly_cap:.0f} monthly cap; add remote and leave rules",
                    owner="operations",
                    notes=["Compare Cibus, Tenbis, Sodexo/Pluxee-style providers, and reimbursement fallback."],
                )
            )

        if request.wants_wellness and per_employee_budget >= 300:
            wellness_cap = 75 if per_employee_budget < 600 else 120 if per_employee_budget < 1200 else 200
            package.append(
                BenefitItem(
                    name="Flexible wellness wallet",
                    monthly_cost_ils=wellness_cap * employees,
                    eligibility="all employees unless legally excluded",
                    rules=f"up to ₪{wellness_cap:.0f} per month against receipt; no medical details",
                    owner="payroll",
                    notes=["Use flexible categories rather than gym-only membership."],
                )
            )

        if request.wants_keren_hishtalmut or per_employee_budget >= 900 or "retention" in request.goals:
            est = min(max(per_employee_budget * 0.25, 0), 650) * employees
            package.append(
                BenefitItem(
                    name="Keren Hishtalmut review and rollout",
                    monthly_cost_ils=est,
                    eligibility="define transparent criteria or company-wide policy",
                    rules="verify current tax ceilings, contribution split, salary base, and payroll setup",
                    owner="finance",
                    notes=["Do not promise tax outcome before payroll/accountant review."],
                )
            )

        if "retention" in request.goals or per_employee_budget >= 500:
            learning = (100 if per_employee_budget < 900 else 200) * employees
            package.append(
                BenefitItem(
                    name="Learning and equipment reserve",
                    monthly_cost_ils=learning,
                    eligibility="employees after documented approval",
                    rules="annual cap, work-related categories, receipt or invoice required",
                    owner="manager",
                )
            )

        if request.includes_contractors:
            issues.append(
                PlanningIssue(
                    code="CONTRACTOR_RISK",
                    severity=Severity.HIGH,
                    message="Employee-style recurring benefits may create worker-classification risk for contractors.",
                    action="Separate contractor terms and obtain legal review before inclusion.",
                )
            )

        if not any("pension" in benefit.lower() for benefit in request.existing_benefits):
            issues.append(
                PlanningIssue(
                    code="COMPLIANCE_FIRST",
                    severity=Severity.HIGH,
                    message="Existing pension setup was not supplied.",
                    action="Confirm pension and severance setup before discretionary perks.",
                )
            )

        total = sum(item.monthly_cost_ils for item in package)
        if budget is not None and total > budget:
            issues.append(
                PlanningIssue(
                    code="OVER_BUDGET",
                    severity=Severity.MEDIUM,
                    message=f"Estimated package cost ₪{total:,.0f} exceeds budget ₪{budget:,.0f}.",
                    action="Reduce meal, wellness, or learning caps and keep mandatory checks.",
                )
            )
            scale_items(package, max_budget=budget, fixed_names={"Mandatory pension and severance administration"})
            total = sum(item.monthly_cost_ils for item in package)

        return self._new_plan(
            assumptions=assumptions,
            recommended_package=package,
            mandatory_checks=[
                "Pension and severance obligations, start dates, and remittance confirmations.",
                "Payroll tax treatment for each recurring benefit.",
                "VAT invoice and bookkeeping workflow.",
                "Privacy notice and vendor data processing terms.",
                "Part-time, leave, reserve duty, parental leave, unpaid leave, and termination rules.",
            ],
            alternatives=[
                {
                    "option": "Meal card provider",
                    "pros": "high visibility, strong employee value, reports",
                    "cons": "coverage and fees vary",
                    "use_when": "employees have useful provider coverage",
                },
                {
                    "option": "Receipt-based reimbursement",
                    "pros": "flexible and geographically inclusive",
                    "cons": "more admin and approval work",
                    "use_when": "provider coverage is weak",
                },
                {
                    "option": "Flexible wallet",
                    "pros": "supports equity and personal preferences",
                    "cons": "requires clear categories and payroll treatment",
                    "use_when": "workforce is hybrid or diverse",
                },
            ],
            implementation_steps=[
                "Confirm mandatory payroll, pension, and accounting setup.",
                "Approve written eligibility, caps, and exception rules.",
                "Compare provider coverage, fees, data terms, invoices, and exports.",
                "Configure payroll components and accounting categories.",
                "Pilot with a small group or first payroll cycle.",
                "Reconcile invoice, provider export, and payroll output.",
                "Publish review date and collect feedback after 90 days.",
            ],
            review_metrics=[
                "monthly budget variance",
                "employee utilization rate",
                "provider support issues",
                "payroll corrections",
                "exception requests",
                "equity complaints",
            ],
            issues=issues,
            estimated_monthly_cost_ils=total,
            remaining_budget_ils=None if request.monthly_budget_ils is None else request.monthly_budget_ils - total,
        )

    def _plan_freelancer(self, request: BenefitRequest) -> BenefitPlan:
        income = request.monthly_income_ils or request.gross_salary_ils
        budget = request.monthly_budget_ils
        if budget is None and income:
            budget = max(250, income * 0.08)
        elif budget is None:
            budget = 1500

        assumptions = [
            "Entity type: freelancer/self-employed.",
            f"Location: {request.location or 'Israel'}.",
            f"Monthly allocation used: ₪{budget:,.0f}.",
        ]
        if income:
            assumptions.append(f"Monthly income supplied: ₪{income:,.0f}.")
        else:
            assumptions.append("No income supplied; scenario allocation used.")

        issues: list[PlanningIssue] = []
        package: list[BenefitItem] = []

        if request.cash_buffer_months is None:
            issues.append(
                PlanningIssue(
                    code="MISSING_CASH_BUFFER",
                    severity=Severity.MEDIUM,
                    message="Cash buffer was not supplied.",
                    action="Validate emergency reserve before adding premium perks.",
                )
            )
        elif request.cash_buffer_months < 3:
            issues.append(
                PlanningIssue(
                    code="LOW_CASH_BUFFER",
                    severity=Severity.HIGH,
                    message="Cash buffer is below 3 months.",
                    action="Prioritize emergency reserve over discretionary perks.",
                )
            )

        reserve_share = 0.4 if request.cash_buffer_months is not None and request.cash_buffer_months < 3 else 0.15
        package.append(
            BenefitItem(
                name="Emergency and tax reserve",
                monthly_cost_ils=budget * reserve_share,
                eligibility="business owner",
                rules="separate reserve account for tax, National Insurance, VAT where relevant, and income volatility",
                owner="owner",
            )
        )
        package.append(
            BenefitItem(
                name="Pension contribution review",
                monthly_cost_ils=budget * 0.25,
                eligibility="self-employed person",
                rules="confirm mandatory contribution and current ceilings with accountant or pension adviser",
                owner="owner + accountant",
            )
        )
        package.append(
            BenefitItem(
                name="Keren Hishtalmut review",
                monthly_cost_ils=budget * 0.25,
                eligibility="self-employed person",
                rules="verify deductible/exempt ceilings for the current tax year",
                owner="owner + accountant",
            )
        )
        package.append(
            BenefitItem(
                name="Tools, insurance, and learning budget",
                monthly_cost_ils=budget * 0.35,
                eligibility="business use",
                rules="document receipts; classify business vs personal use before claiming",
                owner="owner",
            )
        )

        total = sum(item.monthly_cost_ils for item in package)
        if total > budget:
            scale_items(package, max_budget=budget, fixed_names=set())
            total = sum(item.monthly_cost_ils for item in package)

        return self._new_plan(
            assumptions=assumptions,
            recommended_package=package,
            mandatory_checks=[
                "Income tax, VAT if applicable, and National Insurance cash-flow planning.",
                "Mandatory pension contribution and current ceilings.",
                "Study fund treatment for self-employed status.",
                "Expense recognition and receipt retention.",
                "Insurance needs: professional liability, disability, cyber, health, and business interruption where relevant.",
            ],
            alternatives=[
                {
                    "option": "Higher savings allocation",
                    "pros": "improves resilience",
                    "cons": "less immediate comfort",
                    "use_when": "income is volatile or buffer is low",
                },
                {
                    "option": "Higher tools allocation",
                    "pros": "may increase revenue capacity",
                    "cons": "can become subscription creep",
                    "use_when": "tools directly support billable work",
                },
                {
                    "option": "Coworking or office allowance",
                    "pros": "improves routine and client presence",
                    "cons": "fixed monthly cost",
                    "use_when": "home office reduces productivity",
                },
            ],
            implementation_steps=[
                "Calculate 6 to 12 month average income.",
                "Separate business account, tax reserve, and owner drawings.",
                "Confirm pension, study fund, and National Insurance status.",
                "Classify expenses before claiming.",
                "Cancel unused subscriptions.",
                "Schedule quarterly accounting review.",
            ],
            review_metrics=[
                "cash buffer months",
                "tax reserve sufficiency",
                "subscription utilization",
                "equipment replacement reserve",
                "insurance coverage gaps",
            ],
            issues=issues,
            estimated_monthly_cost_ils=total,
            remaining_budget_ils=budget - total,
        )

    def _plan_consumer(self, request: BenefitRequest) -> BenefitPlan:
        budget = request.monthly_budget_ils or 600
        assumptions = [
            "Entity type: consumer.",
            f"Monthly benefit value or household perk budget: ₪{budget:,.0f}.",
            "Tax treatment depends on employer payroll confirmation when employer benefits are involved.",
        ]
        package = [
            BenefitItem(
                name="Usable-value comparison",
                monthly_cost_ils=0,
                eligibility="household or employee decision",
                rules="compare expected utilization, restrictions, expiry, and net cash alternative",
                owner="consumer",
            ),
            BenefitItem(
                name="High-use essentials allocation",
                monthly_cost_ils=budget * 0.7,
                eligibility="recurring needs",
                rules="prioritize food, transport, health, learning, or childcare based on actual use",
                owner="consumer",
            ),
            BenefitItem(
                name="Subscription cleanup reserve",
                monthly_cost_ils=budget * 0.3,
                eligibility="optional services",
                rules="cancel unused services before adding new perks",
                owner="consumer",
            ),
        ]
        total = sum(item.monthly_cost_ils for item in package)
        return self._new_plan(
            assumptions=assumptions,
            recommended_package=package,
            mandatory_checks=[
                "Compare net salary alternative to expected usable benefit.",
                "Check restrictions, expiration, portability, and cancellation terms.",
                "Avoid valuing unused perks at headline amount.",
            ],
            alternatives=[
                {
                    "option": "Cash salary",
                    "pros": "portable and flexible",
                    "cons": "may be taxable as salary",
                    "use_when": "benefit utilization is low",
                },
                {
                    "option": "Meal or wellness benefit",
                    "pros": "valuable when frequently used",
                    "cons": "provider lock-in and restrictions",
                    "use_when": "utilization is predictable",
                },
            ],
            implementation_steps=[
                "Estimate utilization percentage.",
                "Calculate usable value.",
                "Compare to net cash alternative.",
                "Check expiry and cancellation rules.",
                "Choose the option with higher risk-adjusted value.",
            ],
            review_metrics=[
                "actual monthly use",
                "unused balances",
                "subscription cancellations",
                "net value vs headline value",
            ],
            issues=[],
            estimated_monthly_cost_ils=total,
            remaining_budget_ils=0,
        )

    def _plan_employee(self, request: BenefitRequest) -> BenefitPlan:
        value = request.monthly_budget_ils or 600
        return self._new_plan(
            assumptions=[
                "Entity type: employee.",
                "Plan compares employer benefit options from an employee perspective.",
            ],
            recommended_package=[
                BenefitItem(
                    name="Benefit option analysis",
                    monthly_cost_ils=value,
                    eligibility="employee",
                    rules="calculate usable value after utilization, restrictions, and payroll treatment",
                    owner="employee",
                )
            ],
            mandatory_checks=[
                "Ask payroll how the benefit is treated.",
                "Check restrictions and expiry.",
                "Compare to net salary alternative.",
            ],
            alternatives=[
                {
                    "option": "Take benefit",
                    "pros": "good when fully used",
                    "cons": "restricted",
                    "use_when": "usage is predictable",
                },
                {
                    "option": "Take salary",
                    "pros": "flexible",
                    "cons": "taxed as salary",
                    "use_when": "usage is uncertain",
                },
            ],
            implementation_steps=[
                "Estimate expected monthly usage.",
                "Ask payroll for net treatment.",
                "Check provider coverage.",
                "Select higher risk-adjusted value.",
            ],
            review_metrics=["usable value", "unused balance", "provider coverage"],
            issues=[],
            estimated_monthly_cost_ils=value,
            remaining_budget_ils=None,
        )


class AsyncBenefitPlannerClient:
    """Asynchronous wrapper for the planner."""

    def __init__(self, client: BenefitPlannerClient | None = None) -> None:
        self.client = client or BenefitPlannerClient()

    async def plan(self, request: BenefitRequest) -> BenefitPlan:
        """Create a benefit plan asynchronously."""
        return await asyncio.to_thread(self.client.plan, request)

    async def create_plan(self, request: BenefitRequest, store_dir: str | Path | None = None) -> dict[str, Any]:
        """Create and persist a plan asynchronously."""
        return await asyncio.to_thread(self.client.create_plan, request, store_dir)

    async def get_plan(self, plan_id: str, store_dir: str | Path | None = None) -> dict[str, Any]:
        """Read a stored plan asynchronously."""
        return await asyncio.to_thread(self.client.get_plan, plan_id, store_dir)


def re_plan_id(plan_id: str) -> bool:
    """Return whether a plan identifier is safe for local file lookup."""
    return bool(plan_id) and all(ch.isalnum() or ch in {"_", "-"} for ch in plan_id)


def scale_items(items: list[BenefitItem], max_budget: float, fixed_names: set[str]) -> None:
    """Scale variable-cost items to fit max budget."""
    fixed_total = sum(item.monthly_cost_ils for item in items if item.name in fixed_names)
    variable = [item for item in items if item.name not in fixed_names and item.monthly_cost_ils > 0]
    variable_total = sum(item.monthly_cost_ils for item in variable)
    if variable_total <= 0:
        return
    available = max(0.0, max_budget - fixed_total)
    factor = min(1.0, available / variable_total)
    for item in variable:
        item.monthly_cost_ils = round(item.monthly_cost_ils * factor, 2)
        item.notes.append("Scaled to fit supplied budget.")


def load_request(path: str | Path) -> BenefitRequest:
    """Load request JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return BenefitRequest(**data)


def save_plan(plan: BenefitPlan, path: str | Path, fmt: Literal["json", "md"] = "json") -> None:
    """Save plan to disk."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        target.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    elif fmt == "md":
        target.write_text(plan.to_markdown(), encoding="utf-8")
    else:
        raise PlannerError(f"unsupported format: {fmt}")


def plan_from_dict(data: dict[str, Any]) -> BenefitPlan:
    """Plan from dictionary input."""
    environment = data.pop("environment", "sandbox")
    return BenefitPlannerClient(environment=environment).plan(BenefitRequest(**data))


def request_from_env(entity_type: EntityType, environment: Environment = "sandbox") -> BenefitRequest:
    """Build a request from environment variables for examples and automation."""
    budget = os.getenv("BENEFIT_PLANNER_BUDGET_ILS")
    employees = os.getenv("BENEFIT_PLANNER_EMPLOYEE_COUNT")
    income = os.getenv("BENEFIT_PLANNER_MONTHLY_INCOME_ILS")
    cash_buffer = os.getenv("BENEFIT_PLANNER_CASH_BUFFER_MONTHS")
    goals = [goal.strip() for goal in os.getenv("BENEFIT_PLANNER_GOALS", "").split(",") if goal.strip()]
    return BenefitRequest(
        entity_type=entity_type,
        monthly_budget_ils=float(budget) if budget else None,
        employee_count=int(employees) if employees else None,
        monthly_income_ils=float(income) if income else None,
        goals=goals,  # type: ignore[arg-type]
        work_model=os.getenv("BENEFIT_PLANNER_WORK_MODEL", "unspecified"),
        location=os.getenv("BENEFIT_PLANNER_LOCATION", "Israel"),
        existing_benefits=[
            value.strip()
            for value in os.getenv("BENEFIT_PLANNER_EXISTING_BENEFITS", "").split(",")
            if value.strip()
        ],
        cash_buffer_months=float(cash_buffer) if cash_buffer else None,
        includes_contractors=os.getenv("BENEFIT_PLANNER_INCLUDES_CONTRACTORS", "false").lower() == "true",
        wants_keren_hishtalmut=os.getenv("BENEFIT_PLANNER_WANTS_KEREN_HISHTALMUT", "false").lower() == "true",
    )


__all__ = [
    "AsyncBenefitPlannerClient",
    "BenefitItem",
    "BenefitPlan",
    "BenefitPlannerClient",
    "BenefitRequest",
    "PlannerError",
    "PlanningIssue",
    "Severity",
    "load_request",
    "plan_from_dict",
    "request_from_env",
    "VERIFIED_2026_CHECKPOINTS",
    "save_plan",
]
