"""Structured helper for Israeli prepayment and deposit handling.

Provides deterministic calculations and document workflow guidance for
prepayments, deposits, advances, retentions, credits, and final invoice settlement.
It does not submit documents to any authority and does not replace licensed
accounting advice.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import dataclasses
import datetime as _dt
import decimal
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Sequence

Decimal = decimal.Decimal
CENT = Decimal("0.01")


class DepositError(ValueError):
    """Raised when a prepayment/deposit workflow is invalid."""


class DocumentType(str, Enum):
    QUOTE = "quote"
    ORDER = "order"
    RECEIPT = "receipt"
    TAX_INVOICE = "tax_invoice"
    TAX_INVOICE_RECEIPT = "tax_invoice_receipt"
    FINAL_TAX_INVOICE = "final_tax_invoice"
    CREDIT_INVOICE = "credit_invoice"
    REFUND_RECEIPT = "refund_receipt"
    PROFORMA = "proforma"


class BusinessType(str, Enum):
    VAT_REGISTERED = "osek_murshe"
    VAT_EXEMPT = "osek_patur"
    NON_PROFIT = "amutah_or_malkar"
    CONSUMER = "consumer"


class DepositNature(str, Enum):
    ADVANCE_FOR_TAXABLE_SUPPLY = "advance_for_taxable_supply"
    SECURITY_DEPOSIT_HELD_IN_TRUST = "security_deposit_held_in_trust"
    REFUNDABLE_BOOKING_DEPOSIT = "refundable_booking_deposit"
    NON_REFUNDABLE_BOOKING_FEE = "non_refundable_booking_fee"
    RETENTION_HELD_BY_CUSTOMER = "retention_held_by_customer"
    GIFT_CARD_OR_CREDIT_BALANCE = "gift_card_or_credit_balance"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    BIT_PAYBOX_OR_DIGITAL_WALLET = "digital_wallet"
    OTHER = "other"


@dataclass(frozen=True)
class Money:
    """Money amount in ILS by default, rounded half-up to two decimals."""
    amount: Decimal | str | int | float
    currency: str = "ILS"

    def __post_init__(self) -> None:
        amt = Decimal(str(self.amount)).quantize(CENT, rounding=decimal.ROUND_HALF_UP)
        if amt < Decimal("0.00"):
            raise DepositError("Money amount cannot be negative")
        object.__setattr__(self, "amount", amt)
        object.__setattr__(self, "currency", self.currency.upper())

    def __add__(self, other: "Money") -> "Money":
        self._same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._same_currency(other)
        if other.amount > self.amount:
            raise DepositError("Subtraction would create a negative Money amount")
        return Money(self.amount - other.amount, self.currency)

    def _same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise DepositError(f"Currency mismatch: {self.currency} != {other.currency}")

    def as_dict(self) -> dict[str, Any]:
        return {"amount": str(self.amount), "currency": self.currency}

    def format_he(self) -> str:
        symbol = "₪" if self.currency == "ILS" else self.currency
        return f"{symbol}{self.amount:,.2f}"


@dataclass(frozen=True)
class Party:
    name: str
    tax_id: str | None = None
    email: str | None = None
    address: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class LineItem:
    description: str
    quantity: Decimal | str | int | float
    unit_price_ex_vat: Decimal | str | int | float
    vat_rate: Decimal | str | int | float = Decimal("0.18")

    def __post_init__(self) -> None:
        qty = Decimal(str(self.quantity))
        price = Decimal(str(self.unit_price_ex_vat))
        rate = Decimal(str(self.vat_rate))
        if qty <= 0:
            raise DepositError("Line item quantity must be positive")
        if price < 0:
            raise DepositError("Line item price cannot be negative")
        if rate < 0 or rate > Decimal("1"):
            raise DepositError("VAT rate must be between 0 and 1")
        object.__setattr__(self, "quantity", qty)
        object.__setattr__(self, "unit_price_ex_vat", price)
        object.__setattr__(self, "vat_rate", rate)

    @property
    def net(self) -> Decimal:
        return (self.quantity * self.unit_price_ex_vat).quantize(CENT, rounding=decimal.ROUND_HALF_UP)

    @property
    def vat(self) -> Decimal:
        return (self.net * self.vat_rate).quantize(CENT, rounding=decimal.ROUND_HALF_UP)

    @property
    def gross(self) -> Decimal:
        return (self.net + self.vat).quantize(CENT, rounding=decimal.ROUND_HALF_UP)

    def as_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "quantity": str(self.quantity),
            "unit_price_ex_vat": str(Decimal(str(self.unit_price_ex_vat)).quantize(CENT)),
            "vat_rate": str(Decimal(str(self.vat_rate))),
            "net": str(self.net),
            "vat": str(self.vat),
            "gross": str(self.gross),
        }


@dataclass(frozen=True)
class DepositRecord:
    deposit_id: str
    contract_id: str
    received_date: _dt.date
    amount: Money
    payer: Party
    payee: Party
    nature: DepositNature
    payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    refundable: bool = False
    applied_amount: Money | None = None
    reference: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        applied = self.applied_amount or Money("0.00", self.amount.currency)
        if applied.currency != self.amount.currency:
            raise DepositError("Applied amount currency must match deposit currency")
        if applied.amount > self.amount.amount:
            raise DepositError("Applied amount cannot exceed deposit amount")
        object.__setattr__(self, "applied_amount", applied)

    @property
    def remaining(self) -> Money:
        return Money(self.amount.amount - self.applied_amount.amount, self.amount.currency)

    def as_dict(self) -> dict[str, Any]:
        return {
            "deposit_id": self.deposit_id,
            "contract_id": self.contract_id,
            "received_date": self.received_date.isoformat(),
            "amount": self.amount.as_dict(),
            "payer": self.payer.as_dict(),
            "payee": self.payee.as_dict(),
            "nature": self.nature.value,
            "payment_method": self.payment_method.value,
            "refundable": self.refundable,
            "applied_amount": self.applied_amount.as_dict(),
            "remaining": self.remaining.as_dict(),
            "reference": self.reference,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class SettlementResult:
    subtotal_ex_vat: Money
    vat: Money
    total_inc_vat: Money
    deposit_applied: Money
    balance_due: Money
    overpayment: Money
    recommended_documents: list[DocumentType]
    warnings: list[str] = field(default_factory=list)
    journal_hint: list[str] = field(default_factory=list)
    deposit_reference: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "subtotal_ex_vat": self.subtotal_ex_vat.as_dict(),
            "vat": self.vat.as_dict(),
            "total_inc_vat": self.total_inc_vat.as_dict(),
            "deposit_applied": self.deposit_applied.as_dict(),
            "balance_due": self.balance_due.as_dict(),
            "overpayment": self.overpayment.as_dict(),
            "recommended_documents": [d.value for d in self.recommended_documents],
            "warnings": self.warnings,
            "journal_hint": self.journal_hint,
            "deposit_reference": self.deposit_reference,
        }


@dataclass(frozen=True)
class WorkflowRecommendation:
    receive_documents: list[DocumentType]
    settlement_documents: list[DocumentType]
    timing_notes: list[str]
    risk_notes: list[str]
    controls: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "receive_documents": [d.value for d in self.receive_documents],
            "settlement_documents": [d.value for d in self.settlement_documents],
            "timing_notes": self.timing_notes,
            "risk_notes": self.risk_notes,
            "controls": self.controls,
        }


def parse_date(value: str | _dt.date) -> _dt.date:
    """Parse ISO date or DD-MM-YYYY date."""
    if isinstance(value, _dt.date):
        return value
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return _dt.datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise DepositError("Date must be YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY")


def vat_rate_for_date(date: str | _dt.date, default_rate: Decimal | str = Decimal("0.18")) -> Decimal:
    """Return configured VAT rate for a date.

    The default is 18% for the package baseline. Verify against current Tax
    Authority publications before production use.
    """
    _ = parse_date(date)
    rate = Decimal(str(default_rate))
    if rate < 0 or rate > Decimal("1"):
        raise DepositError("VAT rate must be between 0 and 1")
    return rate


def classify_deposit(
    nature: DepositNature | str,
    business_type: BusinessType | str,
    *,
    refundable: bool,
    customer_has_invoice_requirement: bool = False,
) -> WorkflowRecommendation:
    """Recommend document workflow for a deposit/prepayment in Israel."""
    nature = DepositNature(nature)
    business_type = BusinessType(business_type)
    receive_docs: list[DocumentType] = []
    settle_docs: list[DocumentType] = []
    timing: list[str] = []
    risks: list[str] = []
    controls: list[str] = [
        "Use a unique deposit ID and link it to the quote, order, receipt, and final invoice.",
        "Reconcile the deposit liability/advance balance at month-end.",
        "Store customer approval, refund terms, payment reference, and settlement evidence.",
    ]

    if business_type == BusinessType.VAT_EXEMPT:
        receive_docs.append(DocumentType.RECEIPT)
        settle_docs.append(DocumentType.RECEIPT)
        timing.append("Issue a receipt for money received. Do not issue a tax invoice while classified as VAT-exempt.")
        if customer_has_invoice_requirement:
            risks.append("A VAT-exempt business cannot provide input-VAT documentation to the customer.")
        return WorkflowRecommendation(receive_docs, settle_docs, timing, risks, controls)

    if nature == DepositNature.SECURITY_DEPOSIT_HELD_IN_TRUST:
        receive_docs.append(DocumentType.RECEIPT)
        settle_docs.extend([DocumentType.REFUND_RECEIPT, DocumentType.FINAL_TAX_INVOICE])
        timing.append("Treat as money held against an obligation until it becomes consideration for a taxable supply.")
        risks.append("Do not recognize VAT or revenue merely because a refundable security deposit was received.")
    elif nature == DepositNature.RETENTION_HELD_BY_CUSTOMER:
        settle_docs.append(DocumentType.FINAL_TAX_INVOICE)
        timing.append("Track retention receivable separately from cash received and settle when released or credited.")
        risks.append("Do not confuse retention withheld by the customer with a deposit received from the customer.")
    elif nature == DepositNature.NON_REFUNDABLE_BOOKING_FEE:
        receive_docs.append(DocumentType.TAX_INVOICE_RECEIPT)
        settle_docs.append(DocumentType.FINAL_TAX_INVOICE)
        timing.append("A non-refundable fee is normally consideration; issue tax documentation when VAT liability arises.")
    elif nature == DepositNature.GIFT_CARD_OR_CREDIT_BALANCE:
        receive_docs.append(DocumentType.RECEIPT)
        settle_docs.extend([DocumentType.TAX_INVOICE, DocumentType.RECEIPT])
        timing.append("Track the unused balance until goods/services are supplied or the credit expires under applicable law.")
        risks.append("Consumer-protection rules may affect expiry, disclosure, and refunds.")
    elif nature == DepositNature.REFUNDABLE_BOOKING_DEPOSIT:
        receive_docs.append(DocumentType.RECEIPT)
        settle_docs.extend([DocumentType.TAX_INVOICE, DocumentType.RECEIPT, DocumentType.REFUND_RECEIPT])
        timing.append("Keep refundable booking deposits outside revenue until cancellation terms or final supply determine treatment.")
    else:
        receive_docs.extend([DocumentType.RECEIPT, DocumentType.TAX_INVOICE])
        settle_docs.append(DocumentType.FINAL_TAX_INVOICE)
        timing.append("For an advance that is part of the price, document both the cash receipt and the VAT/invoice event according to the applicable timing rule.")

    if business_type == BusinessType.NON_PROFIT:
        risks.append("Non-profit/Malkar treatment differs from ordinary VAT registration; validate document type and tax status.")

    return WorkflowRecommendation(receive_docs, settle_docs, timing, risks, controls)


def settle_invoice(
    line_items: Sequence[LineItem],
    deposit: Money | Decimal | str | int | float = "0.00",
    *,
    currency: str = "ILS",
    business_type: BusinessType | str = BusinessType.VAT_REGISTERED,
    deposit_already_tax_invoiced: bool = False,
    vat_rate_override: Decimal | str | None = None,
    deposit_reference: str | None = None,
) -> SettlementResult:
    """Calculate final invoice settlement after applying a deposit."""
    if not line_items:
        raise DepositError("At least one line item is required")
    business_type = BusinessType(business_type)
    deposit_money = deposit if isinstance(deposit, Money) else Money(deposit, currency)

    net = sum((item.net for item in line_items), Decimal("0.00")).quantize(CENT, rounding=decimal.ROUND_HALF_UP)
    if business_type == BusinessType.VAT_EXEMPT:
        vat = Decimal("0.00")
    else:
        vat = sum((item.vat for item in line_items), Decimal("0.00")).quantize(CENT, rounding=decimal.ROUND_HALF_UP)
        if vat_rate_override is not None:
            rate = Decimal(str(vat_rate_override))
            if rate < 0 or rate > Decimal("1"):
                raise DepositError("VAT rate must be between 0 and 1")
            vat = (net * rate).quantize(CENT, rounding=decimal.ROUND_HALF_UP)
    total = (net + vat).quantize(CENT, rounding=decimal.ROUND_HALF_UP)

    applied = min(deposit_money.amount, total).quantize(CENT, rounding=decimal.ROUND_HALF_UP)
    balance = (total - applied).quantize(CENT, rounding=decimal.ROUND_HALF_UP)
    overpay = max(Decimal("0.00"), deposit_money.amount - total).quantize(CENT, rounding=decimal.ROUND_HALF_UP)

    docs: list[DocumentType] = []
    warnings: list[str] = []
    journal: list[str] = []

    if business_type == BusinessType.VAT_EXEMPT:
        docs.append(DocumentType.RECEIPT)
        journal.append("Debit cash/customer deposit liability as applicable; credit revenue when service/goods supplied.")
    else:
        docs.append(DocumentType.FINAL_TAX_INVOICE)
        if balance > 0:
            docs.append(DocumentType.RECEIPT)
        if overpay > 0:
            docs.append(DocumentType.REFUND_RECEIPT)
            warnings.append("Deposit exceeds final invoice total; refund or maintain documented credit balance.")
        if deposit_money.amount > 0 and not deposit_already_tax_invoiced:
            warnings.append("Confirm whether the deposit should already have been tax-invoiced under the applicable VAT timing rule.")
        journal.append("Debit deposit liability/advance account for the applied amount.")
        journal.append("Credit customer balance or cash settlement for the balance due.")
        journal.append("Recognize VAT output according to the final tax invoice and prior tax invoices, avoiding double VAT.")

    return SettlementResult(
        subtotal_ex_vat=Money(net, currency),
        vat=Money(vat, currency),
        total_inc_vat=Money(total, currency),
        deposit_applied=Money(applied, currency),
        balance_due=Money(balance, currency),
        overpayment=Money(overpay, currency),
        recommended_documents=docs,
        warnings=warnings,
        journal_hint=journal,
        deposit_reference=deposit_reference,
    )


def build_deposit_record(
    *,
    deposit_id: str,
    contract_id: str,
    received_date: str | _dt.date,
    amount: Decimal | str | int | float,
    payer_name: str,
    payee_name: str,
    nature: DepositNature | str,
    payment_method: PaymentMethod | str = PaymentMethod.BANK_TRANSFER,
    currency: str = "ILS",
    refundable: bool = False,
    applied_amount: Decimal | str | int | float = "0.00",
    payer_tax_id: str | None = None,
    payee_tax_id: str | None = None,
    reference: str | None = None,
    notes: str | None = None,
) -> DepositRecord:
    """Construct a validated DepositRecord from primitive values."""
    return DepositRecord(
        deposit_id=deposit_id,
        contract_id=contract_id,
        received_date=parse_date(received_date),
        amount=Money(amount, currency),
        payer=Party(payer_name, payer_tax_id),
        payee=Party(payee_name, payee_tax_id),
        nature=DepositNature(nature),
        payment_method=PaymentMethod(payment_method),
        refundable=refundable,
        applied_amount=Money(applied_amount, currency),
        reference=reference,
        notes=notes,
    )


class PrepaymentDepositClient:
    """Synchronous facade around the workflow engine."""

    def classify(self, nature: DepositNature | str, business_type: BusinessType | str, *, refundable: bool, customer_has_invoice_requirement: bool = False) -> WorkflowRecommendation:
        return classify_deposit(nature, business_type, refundable=refundable, customer_has_invoice_requirement=customer_has_invoice_requirement)

    def settle(self, line_items: Sequence[LineItem], deposit: Money | Decimal | str | int | float = "0.00", *, currency: str = "ILS", business_type: BusinessType | str = BusinessType.VAT_REGISTERED, deposit_already_tax_invoiced: bool = False, vat_rate_override: Decimal | str | None = None, deposit_reference: str | None = None) -> SettlementResult:
        return settle_invoice(line_items, deposit, currency=currency, business_type=business_type, deposit_already_tax_invoiced=deposit_already_tax_invoiced, vat_rate_override=vat_rate_override, deposit_reference=deposit_reference)

    def create_record(self, **kwargs: Any) -> DepositRecord:
        return build_deposit_record(**kwargs)

    def export_records_csv(self, records: Sequence[DepositRecord], path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["deposit_id", "contract_id", "received_date", "amount", "currency", "payer_name", "payer_tax_id", "payee_name", "payee_tax_id", "nature", "payment_method", "refundable", "applied_amount", "remaining", "reference", "notes"])
            writer.writeheader()
            for rec in records:
                writer.writerow({
                    "deposit_id": rec.deposit_id,
                    "contract_id": rec.contract_id,
                    "received_date": rec.received_date.isoformat(),
                    "amount": str(rec.amount.amount),
                    "currency": rec.amount.currency,
                    "payer_name": rec.payer.name,
                    "payer_tax_id": rec.payer.tax_id or "",
                    "payee_name": rec.payee.name,
                    "payee_tax_id": rec.payee.tax_id or "",
                    "nature": rec.nature.value,
                    "payment_method": rec.payment_method.value,
                    "refundable": str(rec.refundable).lower(),
                    "applied_amount": str(rec.applied_amount.amount),
                    "remaining": str(rec.remaining.amount),
                    "reference": rec.reference or "",
                    "notes": rec.notes or "",
                })
        return target


class AsyncPrepaymentDepositClient:
    """Async facade for applications that standardize on awaitable clients."""
    def __init__(self, sync_client: PrepaymentDepositClient | None = None) -> None:
        self._sync = sync_client or PrepaymentDepositClient()

    async def classify(self, *args: Any, **kwargs: Any) -> WorkflowRecommendation:
        return await asyncio.to_thread(self._sync.classify, *args, **kwargs)

    async def settle(self, *args: Any, **kwargs: Any) -> SettlementResult:
        return await asyncio.to_thread(self._sync.settle, *args, **kwargs)

    async def create_record(self, **kwargs: Any) -> DepositRecord:
        return await asyncio.to_thread(self._sync.create_record, **kwargs)

    async def export_records_csv(self, records: Sequence[DepositRecord], path: str | Path) -> Path:
        return await asyncio.to_thread(self._sync.export_records_csv, records, path)


def _json_default(obj: Any) -> Any:
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    if isinstance(obj, (Decimal, _dt.date)):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _parse_line_item(raw: str, vat_rate: str) -> LineItem:
    parts = raw.split(":")
    if len(parts) not in (3, 4):
        raise DepositError("Line item must be description:quantity:unit_price_ex_vat[:vat_rate]")
    desc, qty, price = parts[:3]
    rate = parts[3] if len(parts) == 4 else vat_rate
    return LineItem(desc, qty, price, rate)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Israeli prepayment/deposit helper")
    sub = parser.add_subparsers(dest="command", required=True)

    classify_p = sub.add_parser("classify", help="Recommend document workflow for a deposit")
    classify_p.add_argument("--nature", required=True, choices=[x.value for x in DepositNature])
    classify_p.add_argument("--business-type", required=True, choices=[x.value for x in BusinessType])
    classify_p.add_argument("--refundable", action="store_true")
    classify_p.add_argument("--customer-has-invoice-requirement", action="store_true")

    settle_p = sub.add_parser("settle", help="Calculate final invoice settlement")
    settle_p.add_argument("--line", action="append", required=True, help="description:quantity:unit_price_ex_vat[:vat_rate]")
    settle_p.add_argument("--deposit", default="0.00")
    settle_p.add_argument("--currency", default="ILS")
    settle_p.add_argument("--business-type", default=BusinessType.VAT_REGISTERED.value, choices=[x.value for x in BusinessType])
    settle_p.add_argument("--vat-rate", default="0.18")
    settle_p.add_argument("--deposit-already-tax-invoiced", action="store_true")
    settle_p.add_argument("--deposit-reference")

    record_p = sub.add_parser("record", help="Create a validated deposit record")
    record_p.add_argument("--deposit-id", required=True)
    record_p.add_argument("--contract-id", required=True)
    record_p.add_argument("--received-date", required=True)
    record_p.add_argument("--amount", required=True)
    record_p.add_argument("--payer-name", required=True)
    record_p.add_argument("--payee-name", required=True)
    record_p.add_argument("--nature", required=True, choices=[x.value for x in DepositNature])
    record_p.add_argument("--payment-method", default=PaymentMethod.BANK_TRANSFER.value, choices=[x.value for x in PaymentMethod])
    record_p.add_argument("--currency", default="ILS")
    record_p.add_argument("--refundable", action="store_true")
    record_p.add_argument("--applied-amount", default="0.00")
    record_p.add_argument("--payer-tax-id")
    record_p.add_argument("--payee-tax-id")
    record_p.add_argument("--reference")
    record_p.add_argument("--notes")

    args = parser.parse_args(argv)
    client = PrepaymentDepositClient()

    if args.command == "classify":
        result = client.classify(args.nature, args.business_type, refundable=args.refundable, customer_has_invoice_requirement=args.customer_has_invoice_requirement)
    elif args.command == "settle":
        items = [_parse_line_item(line, args.vat_rate) for line in args.line]
        result = client.settle(items, args.deposit, currency=args.currency, business_type=args.business_type, vat_rate_override=args.vat_rate, deposit_already_tax_invoiced=args.deposit_already_tax_invoiced, deposit_reference=args.deposit_reference)
    elif args.command == "record":
        values = vars(args).copy()
        values.pop("command", None)
        result = client.create_record(**values)
    else:
        raise DepositError("Unsupported command")

    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
