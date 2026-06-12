"""Israeli household, consumer, freelancer, and small-business budget planner.

The client is dependency-free and supports synchronous and asynchronous use,
CSV and JSON import/export, shekel formatting, VAT extraction, savings-goal
progress, validation warnings, and monthly summaries.
"""

from __future__ import annotations

import asyncio
import csv
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Literal, Mapping, Sequence, Tuple
from uuid import uuid4

Kind = Literal["income", "expense", "transfer"]

DEFAULT_CATEGORY_BUDGETS: Dict[str, float] = {
    "housing": 0.30,
    "arnona": 0.03,
    "utilities": 0.06,
    "food": 0.16,
    "transport": 0.10,
    "healthcare": 0.05,
    "insurance": 0.05,
    "communications": 0.03,
    "education_childcare": 0.10,
    "debt": 0.10,
    "tax_reserve": 0.15,
    "business": 0.10,
    "savings": 0.10,
    "leisure": 0.07,
    "cash": 0.05,
    "other": 0.05,
}

CATEGORY_ALIASES: Dict[str, str] = {
    "rent": "housing",
    "mortgage": "housing",
    "vaad bayit": "housing",
    "ועד בית": "housing",
    "שכר דירה": "housing",
    "משכנתה": "housing",
    "ארנונה": "arnona",
    "electricity": "utilities",
    "חשמל": "utilities",
    "water": "utilities",
    "מים": "utilities",
    "gas": "utilities",
    "גז": "utilities",
    "groceries": "food",
    "supermarket": "food",
    "סופר": "food",
    "מזון": "food",
    "delivery": "food",
    "משלוח": "food",
    "fuel": "transport",
    "parking": "transport",
    "rav-kav": "transport",
    "רב קו": "transport",
    "דלק": "transport",
    "health": "healthcare",
    "kupat cholim": "healthcare",
    "קופת חולים": "healthcare",
    "insurance": "insurance",
    "ביטוח": "insurance",
    "mobile": "communications",
    "internet": "communications",
    "סלולר": "communications",
    "childcare": "education_childcare",
    "גן": "education_childcare",
    "צהרון": "education_childcare",
    "loan": "debt",
    "installment": "debt",
    "הלוואה": "debt",
    "business": "business",
    "עסקי": "business",
    "vat": "tax_reserve",
    "מע״מ": "tax_reserve",
    "מעמ": "tax_reserve",
    "tax": "tax_reserve",
    "מס": "tax_reserve",
    "savings": "savings",
    "חיסכון": "savings",
    "cash": "cash",
    "מזומן": "cash",
}


class BudgetValidationError(ValueError):
    """Raised when a transaction, goal, month, date, or amount is invalid."""


@dataclass(frozen=True)
class Transaction:
    date: str
    amount: float
    kind: Kind
    category: str
    description: str = ""
    vendor: str = ""
    payment_method: str = ""
    vat_included: bool = False
    is_business: bool = False
    business_use_percent: float = 0.0
    normalize_months: int = 1
    tags: Tuple[str, ...] = field(default_factory=tuple)

    def normalized_amount(self) -> float:
        months = self.normalize_months if self.normalize_months > 0 else 1
        return round_money(self.amount / months)

    def parsed_date(self) -> date:
        return parse_israeli_date(self.date)

    def normalized_category(self) -> str:
        return normalize_category(self.category or self.description or self.vendor)


@dataclass(frozen=True)
class SavingsGoal:
    name: str
    target_amount: float
    current_amount: float
    due_date: str

    def gap(self) -> float:
        return max(round_money(self.target_amount - self.current_amount), 0.0)

    def parsed_due_date(self) -> date:
        return parse_israeli_date(self.due_date)


@dataclass
class BudgetPlan:
    month: str
    budget_id: str = field(default_factory=lambda: f"budget_{uuid4().hex[:12]}")
    currency: str = "ILS"
    transactions: List[Transaction] = field(default_factory=list)
    savings_goals: List[SavingsGoal] = field(default_factory=list)
    category_limits: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    environment: str = "sandbox"


@dataclass(frozen=True)
class VatBreakdown:
    gross_amount: float
    vat_rate: float
    net_before_vat: float
    vat_component: float


@dataclass(frozen=True)
class GoalProgress:
    name: str
    target_amount: float
    current_amount: float
    gap: float
    due_date: str
    months_remaining: int
    required_monthly_contribution: float
    status: str


@dataclass(frozen=True)
class BudgetSummary:
    budget_id: str
    month: str
    currency: str
    income_total: float
    expense_total: float
    transfer_total: float
    net_cash_flow: float
    savings_rate: float
    category_totals: Dict[str, float]
    business_expense_total: float
    household_expense_total: float
    vat_component_total: float
    goal_progress: List[GoalProgress]
    warnings: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def round_money(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def parse_israeli_date(value: str) -> date:
    value = str(value).strip()
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise BudgetValidationError(f"INVALID_DATE: expected DD-MM-YYYY, DD/MM/YYYY, or YYYY-MM-DD, got {value!r}")


def format_israeli_date(value: date | str, separator: str = "-") -> str:
    if isinstance(value, str):
        value = parse_israeli_date(value)
    if separator not in {"-", "/"}:
        raise BudgetValidationError("INVALID_SEPARATOR: use '-' or '/'")
    return value.strftime(f"%d{separator}%m{separator}%Y")


def parse_month(value: str) -> Tuple[int, int]:
    value = value.strip()
    for fmt in ("%m-%Y", "%m/%Y"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.month, parsed.year
        except ValueError:
            pass
    raise BudgetValidationError(f"INVALID_MONTH: expected MM-YYYY or MM/YYYY, got {value!r}")


def transaction_in_month(transaction: Transaction, month: str) -> bool:
    target_month, target_year = parse_month(month)
    parsed = transaction.parsed_date()
    return parsed.month == target_month and parsed.year == target_year


def normalize_category(value: str) -> str:
    cleaned = " ".join(str(value or "other").strip().lower().replace("_", " ").split())
    if not cleaned:
        return "other"
    if cleaned in DEFAULT_CATEGORY_BUDGETS:
        return cleaned
    if cleaned in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[cleaned]
    for key, category in CATEGORY_ALIASES.items():
        if key in cleaned:
            return category
    return cleaned.replace(" ", "_")


def format_shekel(amount: float, include_symbol: bool = True) -> str:
    sign = "-" if amount < 0 else ""
    amount_abs = abs(round_money(amount))
    formatted = f"{amount_abs:,.2f}"
    if formatted.endswith(".00"):
        formatted = formatted[:-3]
    return f"{sign}₪{formatted}" if include_symbol else f"{sign}{formatted}"


def extract_vat(gross_amount: float, vat_rate: float = 0.18) -> VatBreakdown:
    if vat_rate <= 0:
        raise BudgetValidationError("VAT_RATE_MISSING: vat_rate must be positive")
    gross = round_money(gross_amount)
    net = round_money(gross / (1 + vat_rate))
    vat = round_money(gross - net)
    return VatBreakdown(gross_amount=gross, vat_rate=vat_rate, net_before_vat=net, vat_component=vat)


def months_between(start: date, end: date) -> int:
    if end < start:
        return 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day >= start.day:
        months += 1
    return max(months, 1)


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    cleaned = str(value).strip().lower()
    return cleaned in {"1", "true", "yes", "y", "כן", "אמת"}


def _coerce_tags(value: Any) -> Tuple[str, ...]:
    if value is None or value == "":
        return tuple()
    if isinstance(value, (list, tuple)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return tuple(part.strip() for part in str(value).split("|") if part.strip())


def transaction_from_mapping(row: Mapping[str, Any]) -> Transaction:
    try:
        amount = float(row.get("amount", 0))
    except (TypeError, ValueError) as exc:
        raise BudgetValidationError(f"INVALID_AMOUNT: {row.get('amount')!r}") from exc
    kind = str(row.get("kind", "expense")).strip().lower()
    if kind not in {"income", "expense", "transfer"}:
        raise BudgetValidationError(f"UNKNOWN_KIND: {kind!r}")
    if amount == 0:
        raise BudgetValidationError("INVALID_AMOUNT: amount cannot be zero")
    normalized_months = int(row.get("normalize_months") or 1)
    return Transaction(
        date=format_israeli_date(str(row.get("date", ""))),
        amount=round_money(abs(amount)),
        kind=kind,  # type: ignore[arg-type]
        category=normalize_category(str(row.get("category") or row.get("description") or "other")),
        description=str(row.get("description", "") or ""),
        vendor=str(row.get("vendor", "") or ""),
        payment_method=str(row.get("payment_method", "") or ""),
        vat_included=_coerce_bool(row.get("vat_included", False)),
        is_business=_coerce_bool(row.get("is_business", False)),
        business_use_percent=float(row.get("business_use_percent") or 0.0),
        normalize_months=max(normalized_months, 1),
        tags=_coerce_tags(row.get("tags")),
    )


class HouseholdBudgetPlannerClient:
    """Synchronous client for creating, updating, validating, and summarizing budgets."""

    def __init__(self, plan: BudgetPlan | None = None, vat_rate: float = 0.18) -> None:
        self.plan = plan or BudgetPlan(month="01-2026")
        self.vat_rate = vat_rate

    @classmethod
    def for_month(
        cls,
        month: str,
        vat_rate: float = 0.18,
        *,
        budget_id: str | None = None,
        environment: str = "sandbox",
    ) -> "HouseholdBudgetPlannerClient":
        parse_month(month)
        plan = BudgetPlan(month=month, environment=environment)
        if budget_id:
            plan.budget_id = budget_id
        return cls(plan, vat_rate=vat_rate)

    @classmethod
    def from_json(cls, path: str | Path) -> "HouseholdBudgetPlannerClient":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        plan = BudgetPlan(
            month=data["month"],
            budget_id=data.get("budget_id", f"budget_{uuid4().hex[:12]}"),
            currency=data.get("currency", "ILS"),
            transactions=[transaction_from_mapping(item) for item in data.get("transactions", [])],
            savings_goals=[
                SavingsGoal(
                    name=str(item["name"]),
                    target_amount=round_money(float(item["target_amount"])),
                    current_amount=round_money(float(item["current_amount"])),
                    due_date=format_israeli_date(str(item["due_date"])),
                )
                for item in data.get("savings_goals", [])
            ],
            category_limits={str(k): float(v) for k, v in data.get("category_limits", {}).items()},
            notes=list(data.get("notes", [])),
            environment=data.get("environment", "sandbox"),
        )
        return cls(plan=plan, vat_rate=float(data.get("vat_rate", 0.18)))

    def to_json(self, path: str | Path) -> Path:
        payload = {
            "budget_id": self.plan.budget_id,
            "month": self.plan.month,
            "currency": self.plan.currency,
            "environment": self.plan.environment,
            "vat_rate": self.vat_rate,
            "transactions": [asdict(item) for item in self.plan.transactions],
            "savings_goals": [asdict(item) for item in self.plan.savings_goals],
            "category_limits": self.plan.category_limits,
            "notes": self.plan.notes,
        }
        output = Path(path)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return output

    def add_transaction(
        self,
        *,
        date: str,
        amount: float,
        kind: Kind,
        category: str,
        description: str = "",
        vendor: str = "",
        payment_method: str = "",
        vat_included: bool = False,
        is_business: bool = False,
        business_use_percent: float = 0.0,
        normalize_months: int = 1,
        tags: Sequence[str] = (),
    ) -> Transaction:
        transaction = transaction_from_mapping(
            {
                "date": date,
                "amount": amount,
                "kind": kind,
                "category": category,
                "description": description,
                "vendor": vendor,
                "payment_method": payment_method,
                "vat_included": vat_included,
                "is_business": is_business,
                "business_use_percent": business_use_percent,
                "normalize_months": normalize_months,
                "tags": list(tags),
            }
        )
        self.plan.transactions.append(transaction)
        return transaction

    def add_savings_goal(
        self,
        *,
        name: str,
        target_amount: float,
        current_amount: float,
        due_date: str,
    ) -> SavingsGoal:
        goal = SavingsGoal(
            name=name,
            target_amount=round_money(target_amount),
            current_amount=round_money(current_amount),
            due_date=format_israeli_date(due_date),
        )
        self.plan.savings_goals.append(goal)
        return goal

    def load_csv(self, path: str | Path) -> int:
        with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            count = 0
            for row in reader:
                self.plan.transactions.append(transaction_from_mapping(row))
                count += 1
        return count

    def export_csv(self, path: str | Path) -> Path:
        output = Path(path)
        fieldnames = [
            "date",
            "amount",
            "kind",
            "category",
            "description",
            "vendor",
            "payment_method",
            "vat_included",
            "is_business",
            "business_use_percent",
            "normalize_months",
            "tags",
        ]
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for item in self.plan.transactions:
                row = asdict(item)
                row["tags"] = "|".join(item.tags)
                writer.writerow(row)
        return output

    def transactions_for_month(self, month: str | None = None) -> List[Transaction]:
        selected = month or self.plan.month
        return [item for item in self.plan.transactions if transaction_in_month(item, selected)]

    def category_breakdown(self, month: str | None = None) -> Dict[str, float]:
        totals: Dict[str, float] = {}
        for item in self.transactions_for_month(month):
            if item.kind != "expense":
                continue
            category = item.normalized_category()
            totals[category] = round_money(totals.get(category, 0.0) + item.normalized_amount())
        return dict(sorted(totals.items(), key=lambda pair: pair[0]))

    def detect_duplicates(self) -> List[Tuple[Transaction, Transaction]]:
        seen: Dict[Tuple[str, float, str, str, str], Transaction] = {}
        duplicates: List[Tuple[Transaction, Transaction]] = []
        for item in self.plan.transactions:
            key = (
                item.date,
                round_money(item.amount),
                item.kind,
                item.vendor.strip().lower(),
                item.description.strip().lower(),
            )
            if key in seen:
                duplicates.append((seen[key], item))
            else:
                seen[key] = item
        return duplicates

    def goal_progress(self, today: date | None = None) -> List[GoalProgress]:
        anchor = today or date.today()
        progress: List[GoalProgress] = []
        for goal in self.plan.savings_goals:
            due = goal.parsed_due_date()
            gap = goal.gap()
            months = months_between(anchor, due)
            if gap == 0:
                required = 0.0
                status = "complete"
            elif due < anchor:
                required = gap
                status = "past_due"
            else:
                required = round_money(gap / months)
                status = "on_track" if required > 0 else "complete"
            progress.append(
                GoalProgress(
                    name=goal.name,
                    target_amount=goal.target_amount,
                    current_amount=goal.current_amount,
                    gap=gap,
                    due_date=goal.due_date,
                    months_remaining=months,
                    required_monthly_contribution=required,
                    status=status,
                )
            )
        return progress

    def validate(self) -> List[str]:
        warnings: List[str] = []
        if self.plan.currency != "ILS":
            warnings.append("UNSUPPORTED_CURRENCY: convert to actual ₪ settlement amounts.")
        if self.detect_duplicates():
            warnings.append("DUPLICATE_TRANSACTION: duplicate date/amount/vendor/description rows detected.")
        for item in self.plan.transactions:
            if item.kind == "expense" and item.normalized_category() in {"other", "misc", "miscellaneous"}:
                warnings.append("OTHER_CATEGORY: review uncategorized or other spending.")
            if item.kind == "expense" and item.payment_method == "cash" and item.amount >= 1000:
                warnings.append("CASH_REVIEW: large cash withdrawal needs manual category review.")
            if item.is_business and item.kind == "income" and not any(
                tag in {"tax_reserve", "vat_reserve"} for tag in item.tags
            ):
                warnings.append("BUSINESS_RESERVE: business income needs tax/VAT reserve review.")
            if item.business_use_percent < 0 or item.business_use_percent > 100:
                warnings.append("BUSINESS_USE_PERCENT: use a value between 0 and 100.")
            if item.normalize_months < 1:
                warnings.append("NORMALIZE_MONTHS: use 1 or more.")
        expense_total = sum(item.normalized_amount() for item in self.transactions_for_month() if item.kind == "expense")
        other_total = sum(
            item.normalized_amount()
            for item in self.transactions_for_month()
            if item.kind == "expense" and item.normalized_category() == "other"
        )
        if expense_total and (other_total / expense_total) > 0.05:
            warnings.append("OTHER_TOO_LARGE: other category exceeds 5% of monthly spending.")
        return sorted(set(warnings))

    def summary(self, month: str | None = None, today: date | None = None) -> BudgetSummary:
        selected = month or self.plan.month
        rows = self.transactions_for_month(selected)
        income_total = round_money(sum(item.normalized_amount() for item in rows if item.kind == "income"))
        expense_total = round_money(sum(item.normalized_amount() for item in rows if item.kind == "expense"))
        transfer_total = round_money(sum(item.normalized_amount() for item in rows if item.kind == "transfer"))
        net = round_money(income_total - expense_total)
        savings_rate = round_money(net / income_total) if income_total else 0.0
        category_totals = self.category_breakdown(selected)
        business_expense_total = round_money(
            sum(item.normalized_amount() for item in rows if item.kind == "expense" and item.is_business)
        )
        household_expense_total = round_money(expense_total - business_expense_total)
        vat_component_total = round_money(
            sum(extract_vat(item.normalized_amount(), self.vat_rate).vat_component for item in rows if item.vat_included)
        )
        warnings = self.validate()
        if income_total and expense_total > income_total:
            warnings.append("DEFICIT: expenses exceed income for the month.")
        if income_total:
            debt_total = category_totals.get("debt", 0.0)
            if debt_total / income_total > 0.25:
                warnings.append("DEBT_RISK: debt payments exceed 25% of income.")
        recommendations = self.recommendations(selected, income_total, expense_total, category_totals, warnings)
        return BudgetSummary(
            budget_id=self.plan.budget_id,
            month=selected,
            currency=self.plan.currency,
            income_total=income_total,
            expense_total=expense_total,
            transfer_total=transfer_total,
            net_cash_flow=net,
            savings_rate=savings_rate,
            category_totals=category_totals,
            business_expense_total=business_expense_total,
            household_expense_total=household_expense_total,
            vat_component_total=vat_component_total,
            goal_progress=self.goal_progress(today=today),
            warnings=sorted(set(warnings)),
            recommendations=recommendations,
        )

    def recommendations(
        self,
        month: str,
        income_total: float,
        expense_total: float,
        category_totals: Mapping[str, float],
        warnings: Sequence[str],
    ) -> List[str]:
        recs: List[str] = []
        if income_total == 0:
            recs.append("Add income sources before judging affordability.")
        if expense_total > income_total and income_total > 0:
            recs.append("Freeze non-essential purchases until the deficit is closed.")
        if category_totals.get("other", 0) > max(expense_total * 0.05, 1):
            recs.append("Review the largest 'other' transactions and recategorize them.")
        if category_totals.get("food", 0) > income_total * 0.18 and income_total > 0:
            recs.append("Split groceries, delivery, and restaurants, then cap delivery first.")
        if category_totals.get("debt", 0) > income_total * 0.25 and income_total > 0:
            recs.append("List debts by interest rate and protect minimum payments.")
        if any("BUSINESS_RESERVE" in warning for warning in warnings):
            recs.append("Separate business reserves before transferring money to the household.")
        if not self.plan.savings_goals:
            recs.append("Add at least one emergency-fund or sinking-fund savings goal.")
        if len(recs) < 3 and income_total > expense_total:
            recs.append("Automate a savings transfer immediately after income receipt.")
        return recs[:5]

    def render_text_summary(self, month: str | None = None) -> str:
        summary = self.summary(month=month)
        lines = [
            f"Budget ID: {summary.budget_id}",
            f"Budget month: {summary.month}",
            "Currency: ₪",
            f"Income: {format_shekel(summary.income_total)}",
            f"Expenses: {format_shekel(summary.expense_total)}",
            f"Net cash flow: {format_shekel(summary.net_cash_flow)}",
            f"Savings rate: {summary.savings_rate:.1%}",
            "",
            "Category totals:",
        ]
        for category, amount in summary.category_totals.items():
            lines.append(f"- {category}: {format_shekel(amount)}")
        if summary.goal_progress:
            lines.append("")
            lines.append("Savings goals:")
            for goal in summary.goal_progress:
                lines.append(
                    f"- {goal.name}: gap {format_shekel(goal.gap)}, "
                    f"required monthly {format_shekel(goal.required_monthly_contribution)}, status {goal.status}"
                )
        if summary.warnings:
            lines.append("")
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in summary.warnings)
        if summary.recommendations:
            lines.append("")
            lines.append("Recommended actions:")
            lines.extend(f"- {item}" for item in summary.recommendations)
        return "\n".join(lines)


class AsyncHouseholdBudgetPlannerClient:
    """Asynchronous wrapper around HouseholdBudgetPlannerClient."""

    def __init__(self, client: HouseholdBudgetPlannerClient | None = None) -> None:
        self.client = client or HouseholdBudgetPlannerClient.for_month("01-2026")

    @classmethod
    async def from_json(cls, path: str | Path) -> "AsyncHouseholdBudgetPlannerClient":
        client = await asyncio.to_thread(HouseholdBudgetPlannerClient.from_json, path)
        return cls(client)

    async def add_transaction(self, **kwargs: Any) -> Transaction:
        return await asyncio.to_thread(self.client.add_transaction, **kwargs)

    async def add_savings_goal(self, **kwargs: Any) -> SavingsGoal:
        return await asyncio.to_thread(self.client.add_savings_goal, **kwargs)

    async def load_csv(self, path: str | Path) -> int:
        return await asyncio.to_thread(self.client.load_csv, path)

    async def summary(self, month: str | None = None) -> BudgetSummary:
        return await asyncio.to_thread(self.client.summary, month)

    async def to_json(self, path: str | Path) -> Path:
        return await asyncio.to_thread(self.client.to_json, path)


def create_sample_plan(month: str = "05-2026", *, environment: str = "sandbox") -> HouseholdBudgetPlannerClient:
    client = HouseholdBudgetPlannerClient.for_month(month, environment=environment)
    client.add_transaction(date="01-05-2026", amount=15000, kind="income", category="salary", description="Net salary")
    client.add_transaction(
        date="10-05-2026",
        amount=3200,
        kind="income",
        category="business",
        description="Side project",
        is_business=True,
    )
    client.add_transaction(date="02-05-2026", amount=6200, kind="expense", category="housing", description="Rent")
    client.add_transaction(
        date="05-05-2026",
        amount=920,
        kind="expense",
        category="arnona",
        description="Bi-monthly arnona",
        normalize_months=2,
    )
    client.add_transaction(
        date="08-05-2026",
        amount=3900,
        kind="expense",
        category="food",
        description="Groceries and delivery",
    )
    client.add_transaction(
        date="15-05-2026",
        amount=860,
        kind="expense",
        category="transport",
        description="Fuel and parking",
    )
    client.add_savings_goal(name="Emergency fund", target_amount=30000, current_amount=18000, due_date="31-12-2026")
    return client


def create_budget(month: str, output: str | Path, *, environment: str = "sandbox") -> Dict[str, Any]:
    client = HouseholdBudgetPlannerClient.for_month(month, environment=environment)
    path = client.to_json(output)
    return {
        "budget_id": client.plan.budget_id,
        "month": client.plan.month,
        "environment": client.plan.environment,
        "path": str(path),
    }


def ensure_budget_id(client: HouseholdBudgetPlannerClient, budget_id: str | None) -> None:
    if budget_id and client.plan.budget_id != budget_id:
        raise BudgetValidationError(
            f"BUDGET_ID_MISMATCH: file contains {client.plan.budget_id!r}, received {budget_id!r}"
        )
