"""Calculation primitives for Israeli installment plans.

The package is local and deterministic. It does not call external services.
Use Decimal for money, provide explicit dates, and keep consumer-facing legal
wording under professional review before production use.
"""

from __future__ import annotations

import asyncio
import calendar
import json
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, getcontext
from typing import Any, Iterable, Mapping, Sequence

getcontext().prec = 34

MONEY = Decimal("0.01")
PERCENT = Decimal("100")
CURRENT_ISRAEL_VAT_RATE_PERCENT = Decimal("18")
CURRENT_ISRAEL_VAT_EFFECTIVE_DATE = date(2025, 1, 1)
STANDARD_CANCELLATION_FEE_PERCENT_CAP = Decimal("5")
STANDARD_CANCELLATION_FEE_NIS_CAP = Decimal("100.00")
ISRAEL_INVOICE_ALLOCATION_THRESHOLD_PRE_VAT_JAN_2026 = Decimal("10000")
ISRAEL_INVOICE_ALLOCATION_THRESHOLD_PRE_VAT_JUN_2026 = Decimal("5000")


class InstallmentCalculationError(ValueError):
    """Raised when installment input is invalid."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def to_dict(self) -> dict[str, str]:
        """Return a machine-readable error body."""
        return {"code": self.code, "message": self.message}


def _decimal(value: Decimal | int | float | str | None, default: str = "0") -> Decimal:
    if value is None:
        value = default
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        value = str(value)
    if isinstance(value, str):
        value = value.strip().replace("₪", "").replace(",", "")
        if not value:
            value = default
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise InstallmentCalculationError("INVALID_DECIMAL", f"Invalid decimal value: {value!r}") from exc


def money(value: Decimal | int | float | str | None, quantum: Decimal | str = MONEY) -> Decimal:
    """Convert a value to Decimal money using ROUND_HALF_UP.

    The quantum is a true increment. For example, a quantum of 0.05 rounds
    to the nearest five agorot rather than merely keeping two decimals.
    """
    q = _decimal(quantum, "0.01")
    if q <= 0:
        raise InstallmentCalculationError("ROUNDING_MUST_BE_POSITIVE", "Rounding must be positive")
    amount = _decimal(value)
    rounded_units = (amount / q).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return (rounded_units * q).quantize(q, rounding=ROUND_HALF_UP)


def percentage(value: Decimal | int | float | str | None) -> Decimal:
    """Convert a percent input to Decimal without dividing by 100."""
    return _decimal(value, "0")


def format_ils(value: Decimal | int | float | str | None) -> str:
    """Format a value as Israeli shekels."""
    return f"₪{money(value):,.2f}"


def gross_from_net(net_price: Decimal | int | float | str | None, vat_rate_percent: Decimal | int | float | str = CURRENT_ISRAEL_VAT_RATE_PERCENT) -> Decimal:
    """Return VAT-inclusive gross amount from a VAT-exclusive net amount."""
    net = money(net_price)
    rate = percentage(vat_rate_percent)
    if rate < 0:
        raise InstallmentCalculationError("RATE_MUST_NOT_BE_NEGATIVE", "VAT rate must not be negative")
    return money(net * (Decimal("1") + rate / PERCENT))


def vat_components_from_gross(gross_price: Decimal | int | float | str | None, vat_rate_percent: Decimal | int | float | str = CURRENT_ISRAEL_VAT_RATE_PERCENT) -> dict[str, str]:
    """Split a VAT-inclusive gross amount into net, VAT, and gross components."""
    gross = money(gross_price)
    rate = percentage(vat_rate_percent)
    if rate < 0:
        raise InstallmentCalculationError("RATE_MUST_NOT_BE_NEGATIVE", "VAT rate must not be negative")
    if rate == 0:
        net = gross
    else:
        net = money(gross / (Decimal("1") + rate / PERCENT))
    vat = money(gross - net)
    return {"net_price": str(net), "vat_amount": str(vat), "gross_price": str(gross), "vat_rate_percent": str(rate)}


def statutory_cancellation_fee_cap(transaction_total: Decimal | int | float | str | None) -> Decimal:
    """Return the lower of 5 percent of transaction total or ₪100.

    This helper models the common statutory cap used for qualifying Israeli
    consumer cancellation cases. Apply only after confirming that the specific
    transaction has a statutory cancellation right and no exception applies.
    """
    total = money(transaction_total)
    if total < 0:
        raise InstallmentCalculationError("PRICE_MUST_BE_POSITIVE", "Transaction total must not be negative")
    percent_fee = money(total * STANDARD_CANCELLATION_FEE_PERCENT_CAP / PERCENT)
    return money(min(percent_fee, STANDARD_CANCELLATION_FEE_NIS_CAP))


def parse_date(value: str | date | None) -> date | None:
    """Parse YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY."""
    if value is None or isinstance(value, date):
        return value
    raw = value.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise InstallmentCalculationError("INVALID_DATE", "Use YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY")


def format_date_il(value: date | None) -> str:
    """Format a date as DD/MM/YYYY."""
    if value is None:
        return ""
    return value.strftime("%d/%m/%Y")


def add_months(value: date, months: int, preferred_day: int | None = None) -> date:
    """Add whole months and clip the day to the end of the target month."""
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    wanted_day = preferred_day if preferred_day is not None else value.day
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(wanted_day, last_day))


@dataclass(frozen=True)
class InstallmentRequest:
    """Input for an installment calculation."""

    cash_price: Decimal | int | float | str
    installments: int
    down_payment: Decimal | int | float | str = "0"
    annual_interest_rate: Decimal | int | float | str = "0"
    upfront_fee: Decimal | int | float | str = "0"
    upfront_fee_percent: Decimal | int | float | str = "0"
    per_installment_fee: Decimal | int | float | str = "0"
    first_due_date: str | date | None = None
    payment_day: int | None = None
    vat_included: bool = True
    consumer_context: bool = True
    label: str | None = None
    rounding: Decimal | int | float | str = "0.01"

    def normalized(self) -> "NormalizedInstallmentRequest":
        """Validate and normalize raw input values."""
        rounding = _decimal(self.rounding, "0.01")
        if rounding <= 0:
            raise InstallmentCalculationError("ROUNDING_MUST_BE_POSITIVE", "Rounding must be positive")
        cash_price = money(self.cash_price, rounding)
        if cash_price <= 0:
            raise InstallmentCalculationError("PRICE_MUST_BE_POSITIVE", "Cash price must be greater than zero")
        if not isinstance(self.installments, int) or self.installments <= 0:
            raise InstallmentCalculationError("INSTALLMENTS_MUST_BE_POSITIVE", "Installments must be a positive integer")
        down_payment = money(self.down_payment, rounding)
        if down_payment < 0 or down_payment >= cash_price:
            raise InstallmentCalculationError("DOWN_PAYMENT_OUT_OF_RANGE", "Down payment must be at least zero and less than cash price")
        annual_rate = percentage(self.annual_interest_rate)
        if annual_rate < 0:
            raise InstallmentCalculationError("RATE_MUST_NOT_BE_NEGATIVE", "Annual interest rate must not be negative")
        upfront_fee = money(self.upfront_fee, rounding)
        upfront_fee_percent = percentage(self.upfront_fee_percent)
        per_installment_fee = money(self.per_installment_fee, rounding)
        if upfront_fee < 0 or upfront_fee_percent < 0 or per_installment_fee < 0:
            raise InstallmentCalculationError("FEE_MUST_NOT_BE_NEGATIVE", "Fees must not be negative")
        if self.payment_day is not None and not 1 <= self.payment_day <= 31:
            raise InstallmentCalculationError("PAYMENT_DAY_OUT_OF_RANGE", "Payment day must be between 1 and 31")
        first_due_date = parse_date(self.first_due_date)
        return NormalizedInstallmentRequest(
            cash_price=cash_price,
            installments=self.installments,
            down_payment=down_payment,
            annual_interest_rate=annual_rate,
            upfront_fee=upfront_fee,
            upfront_fee_percent=upfront_fee_percent,
            per_installment_fee=per_installment_fee,
            first_due_date=first_due_date,
            payment_day=self.payment_day,
            vat_included=bool(self.vat_included),
            consumer_context=bool(self.consumer_context),
            label=self.label,
            rounding=rounding,
        )


@dataclass(frozen=True)
class NormalizedInstallmentRequest:
    """Validated calculation request."""

    cash_price: Decimal
    installments: int
    down_payment: Decimal
    annual_interest_rate: Decimal
    upfront_fee: Decimal
    upfront_fee_percent: Decimal
    per_installment_fee: Decimal
    first_due_date: date | None
    payment_day: int | None
    vat_included: bool
    consumer_context: bool
    label: str | None
    rounding: Decimal


@dataclass(frozen=True)
class PaymentLine:
    """One installment row."""

    number: int
    due_date: date | None
    principal: Decimal
    interest: Decimal
    fee: Decimal
    payment: Decimal
    balance: Decimal

    def to_dict(self) -> dict[str, Any]:
        """Serialize the payment row."""
        return {
            "number": self.number,
            "due_date": format_date_il(self.due_date),
            "principal": str(self.principal),
            "interest": str(self.interest),
            "fee": str(self.fee),
            "payment": str(self.payment),
            "balance": str(self.balance),
        }


@dataclass(frozen=True)
class DisclosureCheck:
    """A customer-facing disclosure check."""

    code: str
    status: str
    message: str

    def to_dict(self) -> dict[str, str]:
        """Serialize the check."""
        return {"code": self.code, "status": self.status, "message": self.message}


@dataclass(frozen=True)
class InstallmentPlan:
    """Calculated installment plan with schedule and disclosure data."""

    request: NormalizedInstallmentRequest
    financed_amount: Decimal
    upfront_fee: Decimal
    base_installment: Decimal
    regular_payment: Decimal
    total_interest: Decimal
    total_fees: Decimal
    total_payments: Decimal
    finance_charge: Decimal
    cost_above_cash_price: Decimal
    effective_annual_cost_percent: Decimal | None
    schedule: tuple[PaymentLine, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)
    disclosure_checks: tuple[DisclosureCheck, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the plan for JSON output."""
        return {
            "label": self.request.label,
            "cash_price": str(self.request.cash_price),
            "down_payment": str(self.request.down_payment),
            "financed_amount": str(self.financed_amount),
            "installments": self.request.installments,
            "annual_interest_rate": str(self.request.annual_interest_rate),
            "upfront_fee": str(self.upfront_fee),
            "per_installment_fee": str(self.request.per_installment_fee),
            "base_installment": str(self.base_installment),
            "regular_payment": str(self.regular_payment),
            "total_interest": str(self.total_interest),
            "total_fees": str(self.total_fees),
            "total_payments": str(self.total_payments),
            "finance_charge": str(self.finance_charge),
            "cost_above_cash_price": str(self.cost_above_cash_price),
            "effective_annual_cost_percent": None if self.effective_annual_cost_percent is None else str(self.effective_annual_cost_percent),
            "vat_included": self.request.vat_included,
            "consumer_context": self.request.consumer_context,
            "schedule": [line.to_dict() for line in self.schedule],
            "warnings": list(self.warnings),
            "disclosure_checks": [check.to_dict() for check in self.disclosure_checks],
        }

    def to_json(self, **kwargs: Any) -> str:
        """Serialize the plan as JSON."""
        options = {"ensure_ascii": False, "indent": 2}
        options.update(kwargs)
        return json.dumps(self.to_dict(), **options)

    def disclosure_table(self) -> str:
        """Return a compact text disclosure summary."""
        effective = "n/a" if self.effective_annual_cost_percent is None else f"{self.effective_annual_cost_percent:.2f}%"
        lines = [
            f"Cash price: {format_ils(self.request.cash_price)}",
            f"Down payment: {format_ils(self.request.down_payment)}",
            f"Financed amount: {format_ils(self.financed_amount)}",
            f"Installments: {self.request.installments}",
            f"Nominal annual rate: {self.request.annual_interest_rate:.4f}%",
            f"Regular payment: {format_ils(self.regular_payment)}",
            f"Total interest: {format_ils(self.total_interest)}",
            f"Total fees: {format_ils(self.total_fees)}",
            f"Total paid: {format_ils(self.total_payments)}",
            f"Cost above cash price: {format_ils(self.cost_above_cash_price)}",
            f"Effective annual cost estimate: {effective}",
        ]
        return "\n".join(lines)

    def schedule_rows(self) -> list[dict[str, Any]]:
        """Return schedule rows as dictionaries."""
        return [line.to_dict() for line in self.schedule]


def _level_payment(principal: Decimal, monthly_rate: Decimal, installments: int, rounding: Decimal) -> Decimal:
    if monthly_rate == 0:
        return money(principal / installments, rounding)
    one = Decimal("1")
    factor = (one + monthly_rate) ** (-installments)
    return money(principal * monthly_rate / (one - factor), rounding)


def _due_date(first_due_date: date | None, index: int, payment_day: int | None) -> date | None:
    if first_due_date is None:
        return None
    return add_months(first_due_date, index, payment_day)


def _effective_annual_cost(financed_amount: Decimal, upfront_fee: Decimal, payments: Sequence[Decimal]) -> Decimal | None:
    net_received = float(financed_amount - upfront_fee)
    if net_received <= 0:
        return None
    if not payments:
        return None
    payment_values = [float(p) for p in payments]
    if sum(payment_values) <= net_received + 1e-9:
        return Decimal("0.00")

    def _present_value(rate: float) -> float:
        return sum(payment / ((1.0 + rate) ** idx) for idx, payment in enumerate(payment_values, start=1))

    low = 0.0
    high = 1.0
    while _present_value(high) > net_received and high < 100:
        high *= 2.0
    if high >= 100:
        return None
    for _ in range(120):
        mid = (low + high) / 2.0
        if _present_value(mid) > net_received:
            low = mid
        else:
            high = mid
    monthly = (low + high) / 2.0
    annual = ((1.0 + monthly) ** 12 - 1.0) * 100.0
    return Decimal(str(annual)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def disclosure_checklist(plan: InstallmentPlan) -> tuple[DisclosureCheck, ...]:
    """Build disclosure checks for consumer-facing Israeli use."""
    checks: list[DisclosureCheck] = []
    checks.append(DisclosureCheck("CASH_PRICE", "ok", "State the immediate-payment price before showing credit terms."))
    checks.append(DisclosureCheck("INSTALLMENT_COUNT", "ok", "State the number of installments and payment amount."))
    checks.append(DisclosureCheck("FEES", "ok" if plan.total_fees >= 0 else "review", "State every fixed, percentage, and per-installment fee."))
    checks.append(DisclosureCheck("DATES", "ok" if all(line.due_date for line in plan.schedule) else "review", "State due dates or provide the rule used to set them."))
    if plan.request.consumer_context:
        checks.append(DisclosureCheck("LEGAL_REVIEW", "review", "Review current Israeli consumer-credit, cancellation, and disclosure requirements before production use."))
    if not plan.request.vat_included:
        checks.append(DisclosureCheck("VAT", "review", "Mark VAT-exclusive pricing clearly and confirm invoice treatment."))
    else:
        checks.append(DisclosureCheck("VAT", "ok", "Consumer-facing amount is marked VAT-inclusive; current Israeli VAT baseline is 18 percent from 01/01/2025."))
    if plan.finance_charge > 0:
        checks.append(DisclosureCheck("CREDIT_COST", "ok", "Show total cost above cash price and effective annual cost estimate."))
    else:
        checks.append(DisclosureCheck("CREDIT_COST", "ok", "No finance charge was calculated."))
    return tuple(checks)


def calculate_plan(request: InstallmentRequest) -> InstallmentPlan:
    """Calculate an Israeli installment plan."""
    req = request.normalized()
    financed_amount = money(req.cash_price - req.down_payment, req.rounding)
    percent_fee = money(financed_amount * req.upfront_fee_percent / PERCENT, req.rounding)
    upfront_fee = money(req.upfront_fee + percent_fee, req.rounding)
    monthly_rate = req.annual_interest_rate / PERCENT / Decimal("12")
    base_payment = _level_payment(financed_amount, monthly_rate, req.installments, req.rounding)

    balance = financed_amount
    rows: list[PaymentLine] = []
    total_interest = Decimal("0.00")
    total_installment_payments = Decimal("0.00")
    rounding_adjusted = False
    for index in range(req.installments):
        interest = money(balance * monthly_rate, req.rounding)
        if index == req.installments - 1:
            principal = balance
            base_line_payment = money(principal + interest, req.rounding)
            if base_line_payment != base_payment:
                rounding_adjusted = True
        else:
            principal = money(base_payment - interest, req.rounding)
            if principal <= 0:
                raise InstallmentCalculationError("PAYMENT_DOES_NOT_AMORTIZE", "Payment does not reduce the balance")
            base_line_payment = base_payment
        balance = money(balance - principal, req.rounding)
        line_payment = money(base_line_payment + req.per_installment_fee, req.rounding)
        total_interest = money(total_interest + interest, req.rounding)
        total_installment_payments = money(total_installment_payments + line_payment, req.rounding)
        rows.append(PaymentLine(
            number=index + 1,
            due_date=_due_date(req.first_due_date, index, req.payment_day),
            principal=principal,
            interest=interest,
            fee=req.per_installment_fee,
            payment=line_payment,
            balance=balance,
        ))

    total_per_installment_fees = money(req.per_installment_fee * req.installments, req.rounding)
    total_fees = money(upfront_fee + total_per_installment_fees, req.rounding)
    finance_charge = money(total_interest + total_fees, req.rounding)
    total_payments = money(req.down_payment + upfront_fee + total_installment_payments, req.rounding)
    cost_above_cash = money(total_payments - req.cash_price, req.rounding)
    regular_payment = rows[0].payment if rows else Decimal("0.00")
    effective = _effective_annual_cost(financed_amount, upfront_fee, [row.payment for row in rows])

    warnings: list[str] = []
    if req.consumer_context:
        warnings.append("Consumer-facing use requires review of current Israeli price-display, cancellation, credit-disclosure, and VAT rules.")
    if req.first_due_date is None:
        warnings.append("No due dates supplied; disclose the date-setting rule before customer approval.")
    if req.per_installment_fee > 0 and req.annual_interest_rate == 0:
        warnings.append("Zero nominal interest with fees still creates a finance charge; disclose total cost above cash price.")
    if upfront_fee > financed_amount * Decimal("0.10"):
        warnings.append("Upfront fee exceeds 10 percent of the financed amount; check fairness, cancellation, and disclosure treatment.")
    if req.installments > 36:
        warnings.append("Long installment term; verify card-acquirer, bookkeeping, and consumer-credit treatment.")
    if not req.vat_included:
        warnings.append("VAT-exclusive amount; mark tax treatment clearly in quotes and invoices.")
    if effective is not None and effective > Decimal("30"):
        warnings.append("Effective annual cost estimate is high; show it prominently and review the offer before use.")
    if rounding_adjusted:
        warnings.append("Final installment was adjusted for rounding so the balance reaches zero.")

    plan = InstallmentPlan(
        request=req,
        financed_amount=financed_amount,
        upfront_fee=upfront_fee,
        base_installment=base_payment,
        regular_payment=regular_payment,
        total_interest=total_interest,
        total_fees=total_fees,
        total_payments=total_payments,
        finance_charge=finance_charge,
        cost_above_cash_price=cost_above_cash,
        effective_annual_cost_percent=effective,
        schedule=tuple(rows),
        warnings=tuple(warnings),
    )
    return replace(plan, disclosure_checks=disclosure_checklist(plan))


async def async_calculate_plan(request: InstallmentRequest) -> InstallmentPlan:
    """Async wrapper for calculate_plan."""
    await asyncio.sleep(0)
    return calculate_plan(request)


def compare_plans(requests: Iterable[InstallmentRequest]) -> list[InstallmentPlan]:
    """Calculate and sort plans by total paid."""
    plans = [calculate_plan(request) for request in requests]
    return sorted(plans, key=lambda plan: (plan.total_payments, plan.finance_charge, plan.request.installments))


async def async_compare_plans(requests: Iterable[InstallmentRequest]) -> list[InstallmentPlan]:
    """Async comparison wrapper."""
    await asyncio.sleep(0)
    return compare_plans(requests)


def estimate_refund(plan: InstallmentPlan, installments_paid: int, cancellation_fee: Decimal | int | float | str = "0") -> dict[str, Any]:
    """Estimate remaining balance and refund exposure after cancellation.

    This is an operational estimate, not a legal conclusion. Apply the actual
    contract, cancellation law, chargeback rules, and returned-goods policy.
    """
    if installments_paid < 0 or installments_paid > len(plan.schedule):
        raise InstallmentCalculationError("INSTALLMENTS_PAID_OUT_OF_RANGE", "Installments paid must be within the schedule")
    fee = money(cancellation_fee, plan.request.rounding)
    if fee < 0:
        raise InstallmentCalculationError("FEE_MUST_NOT_BE_NEGATIVE", "Cancellation fee must not be negative")
    paid_rows = plan.schedule[:installments_paid]
    unpaid_rows = plan.schedule[installments_paid:]
    paid_installments = money(sum((row.payment for row in paid_rows), Decimal("0.00")), plan.request.rounding)
    remaining_principal = Decimal("0.00") if not unpaid_rows else plan.schedule[installments_paid - 1].balance if installments_paid else plan.financed_amount
    remaining_scheduled = money(sum((row.payment for row in unpaid_rows), Decimal("0.00")), plan.request.rounding)
    paid_total = money(plan.request.down_payment + plan.upfront_fee + paid_installments, plan.request.rounding)
    estimated_settlement = money(remaining_principal + fee, plan.request.rounding)
    return {
        "installments_paid": installments_paid,
        "paid_total": str(paid_total),
        "remaining_principal": str(money(remaining_principal, plan.request.rounding)),
        "remaining_scheduled_payments": str(remaining_scheduled),
        "cancellation_fee": str(fee),
        "estimated_settlement_before_legal_adjustments": str(estimated_settlement),
        "note": "Use contract terms, current cancellation rules, card-acquirer policy, and bookkeeping guidance before issuing a refund or charge reversal.",
    }


class InstallmentClient:
    """Small sync and async facade for application code."""

    def __init__(self, environment: str = "sandbox") -> None:
        if environment not in {"sandbox", "production"}:
            raise InstallmentCalculationError("INVALID_ENVIRONMENT", "Environment must be sandbox or production")
        self.environment = environment

    def calculate(self, request: InstallmentRequest) -> InstallmentPlan:
        """Calculate a plan synchronously."""
        return calculate_plan(request)

    async def async_calculate(self, request: InstallmentRequest) -> InstallmentPlan:
        """Calculate a plan asynchronously."""
        return await async_calculate_plan(request)

    def compare(self, requests: Iterable[InstallmentRequest]) -> list[InstallmentPlan]:
        """Compare plans synchronously."""
        return compare_plans(requests)

    async def async_compare(self, requests: Iterable[InstallmentRequest]) -> list[InstallmentPlan]:
        """Compare plans asynchronously."""
        return await async_compare_plans(requests)

    def refund(self, plan: InstallmentPlan, installments_paid: int, cancellation_fee: Decimal | int | float | str = "0") -> dict[str, Any]:
        """Estimate cancellation/refund values."""
        return estimate_refund(plan, installments_paid, cancellation_fee)


def request_from_mapping(data: Mapping[str, Any]) -> InstallmentRequest:
    """Build an InstallmentRequest from mapping data."""
    return InstallmentRequest(
        cash_price=data["cash_price"],
        installments=int(data["installments"]),
        down_payment=data.get("down_payment", "0"),
        annual_interest_rate=data.get("annual_interest_rate", data.get("annual_rate", "0")),
        upfront_fee=data.get("upfront_fee", "0"),
        upfront_fee_percent=data.get("upfront_fee_percent", "0"),
        per_installment_fee=data.get("per_installment_fee", "0"),
        first_due_date=data.get("first_due_date"),
        payment_day=data.get("payment_day"),
        vat_included=bool(data.get("vat_included", True)),
        consumer_context=bool(data.get("consumer_context", True)),
        label=data.get("label"),
        rounding=data.get("rounding", "0.01"),
    )


__all__ = [
    "CURRENT_ISRAEL_VAT_EFFECTIVE_DATE",
    "CURRENT_ISRAEL_VAT_RATE_PERCENT",
    "DisclosureCheck",
    "ISRAEL_INVOICE_ALLOCATION_THRESHOLD_PRE_VAT_JAN_2026",
    "ISRAEL_INVOICE_ALLOCATION_THRESHOLD_PRE_VAT_JUN_2026",
    "STANDARD_CANCELLATION_FEE_NIS_CAP",
    "STANDARD_CANCELLATION_FEE_PERCENT_CAP",
    "InstallmentCalculationError",
    "InstallmentClient",
    "InstallmentPlan",
    "InstallmentRequest",
    "NormalizedInstallmentRequest",
    "PaymentLine",
    "add_months",
    "async_calculate_plan",
    "async_compare_plans",
    "calculate_plan",
    "compare_plans",
    "disclosure_checklist",
    "estimate_refund",
    "format_date_il",
    "gross_from_net",
    "format_ils",
    "money",
    "parse_date",
    "percentage",
    "request_from_mapping",
    "statutory_cancellation_fee_cap",
    "vat_components_from_gross",
]
