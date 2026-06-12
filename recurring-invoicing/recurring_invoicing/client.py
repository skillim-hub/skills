"""Recurring invoicing helpers for Israeli VAT and invoice-allocation workflows.

The module intentionally avoids network dependencies. Provide transport callables
when integrating with a real SHAAM gateway, ERP connector, or bookkeeping system.
"""

from __future__ import annotations

import asyncio
import calendar
import dataclasses
import enum
import json
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable, Literal, Mapping, Sequence

DEFAULT_VAT_RATE = Decimal("0.18")
VAT_RATE_BEFORE_2025 = Decimal("0.17")
DEFAULT_CURRENCY = "ILS"
DEFAULT_ALLOCATION_THRESHOLDS: dict[int, Decimal] = {
    2024: Decimal("25000.00"),
    2025: Decimal("20000.00"),
    2026: Decimal("10000.00"),
    2027: Decimal("5000.00"),
    2028: Decimal("5000.00"),
}
DEFAULT_ALLOCATION_THRESHOLD_DATES: tuple[tuple[date, Decimal], ...] = (
    (date(2024, 1, 1), Decimal("25000.00")),
    (date(2025, 1, 1), Decimal("20000.00")),
    (date(2026, 1, 1), Decimal("10000.00")),
    (date(2026, 6, 1), Decimal("5000.00")),
)

AllocationEnvironment = Literal["sandbox", "production"]
JsonMapping = Mapping[str, Any]
SyncTransport = Callable[[str, JsonMapping], JsonMapping]
AsyncTransport = Callable[[str, JsonMapping], Awaitable[JsonMapping]]


class RecurringInvoiceError(ValueError):
    """Raised when recurring invoice input is invalid."""


class SubscriptionStatus(str, enum.Enum):
    """Supported subscription lifecycle states."""

    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class DocumentType(str, enum.Enum):
    """Common Israeli document types used in recurring billing."""

    TAX_INVOICE = "tax_invoice"
    TAX_INVOICE_RECEIPT = "tax_invoice_receipt"
    RECEIPT = "receipt"
    CREDIT_TAX_INVOICE = "credit_tax_invoice"
    PROFORMA = "proforma"


class Interval(str, enum.Enum):
    """Supported recurrence intervals."""

    MONTHLY = "monthly"
    BIMONTHLY = "bimonthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass(slots=True)
class Customer:
    """Customer identity used on recurring invoices."""

    name: str
    tax_id: str
    email: str | None = None
    address: str | None = None
    vat_registered: bool = True

    def normalized_tax_id(self) -> str:
        """Return a cleaned 9-digit Israeli tax identifier."""
        return clean_israeli_tax_id(self.tax_id)


@dataclass(slots=True)
class LineItem:
    """Invoice line with quantity, unit price, and VAT treatment."""

    description: str
    quantity: Decimal | int | float | str
    unit_price: Decimal | int | float | str
    vat_rate: Decimal | int | float | str | None = None
    exempt: bool = False
    sku: str | None = None

    def normalized(self, issue_date: date | None = None) -> "LineItem":
        """Return a copy with Decimal values and default VAT rate."""
        rate = Decimal("0.00") if self.exempt else Decimal(str(self.vat_rate)) if self.vat_rate is not None else vat_rate_for_issue_date(issue_date or date.today())
        return LineItem(
            description=self.description.strip(),
            quantity=money(self.quantity),
            unit_price=money(self.unit_price),
            vat_rate=rate,
            exempt=self.exempt,
            sku=self.sku,
        )


@dataclass(slots=True)
class Subscription:
    """Recurring invoice plan for a single customer."""

    subscription_id: str
    customer: Customer
    line_items: list[LineItem]
    start_date: date
    interval: Interval = Interval.MONTHLY
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    end_date: date | None = None
    end_of_month: bool = True
    currency: str = DEFAULT_CURRENCY
    document_type: DocumentType = DocumentType.TAX_INVOICE
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate fields and raise RecurringInvoiceError for invalid state."""
        validate_subscription(self)


@dataclass(slots=True)
class InvoiceDocument:
    """Generated invoice document awaiting numbering or external submission."""

    invoice_id: str
    subscription_id: str
    issue_date: date
    customer: Customer
    line_items: list[LineItem]
    document_type: DocumentType
    currency: str
    subtotal: Decimal
    vat_amount: Decimal
    total: Decimal
    allocation_number: str | None = None
    references: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the invoice to JSON-friendly fields."""
        return invoice_to_dict(self)


@dataclass(slots=True)
class AllocationRequest:
    """Invoice allocation request payload wrapper."""

    environment: AllocationEnvironment
    business_tax_id: str
    invoice: InvoiceDocument
    client_transaction_id: str
    software_id: str | None = None


@dataclass(slots=True)
class AllocationResponse:
    """Normalized response from a SHAAM allocation endpoint or gateway."""

    allocation_number: str
    status: str
    raw: dict[str, Any]


def money(value: Decimal | int | float | str) -> Decimal:
    """Convert a numeric value to a two-decimal Decimal."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def vat_rate_for_issue_date(issue_date: date) -> Decimal:
    """Return the default Israeli VAT rate for common recent periods."""
    if issue_date >= date(2025, 1, 1):
        return DEFAULT_VAT_RATE
    return VAT_RATE_BEFORE_2025


def clean_israeli_tax_id(value: str) -> str:
    """Return a 9-digit tax identifier, left padded when shorter."""
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if not digits:
        raise RecurringInvoiceError("Tax ID is empty.")
    if len(digits) > 9:
        raise RecurringInvoiceError("Israeli tax ID must contain no more than 9 digits.")
    return digits.zfill(9)


def is_valid_israeli_tax_id(value: str) -> bool:
    """Validate an Israeli 9-digit ID/company number checksum."""
    try:
        digits = clean_israeli_tax_id(value)
    except RecurringInvoiceError:
        return False
    total = 0
    for index, char in enumerate(digits):
        number = int(char) * (1 if index % 2 == 0 else 2)
        total += number if number < 10 else number - 9
    return total % 10 == 0


def add_months(source: date, months: int, end_of_month: bool = True) -> date:
    """Add calendar months while preserving month-end anchors when requested."""
    if months <= 0:
        raise RecurringInvoiceError("months must be positive.")
    year = source.year + (source.month - 1 + months) // 12
    month = (source.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    source_last_day = calendar.monthrange(source.year, source.month)[1]
    if end_of_month and source.day == source_last_day:
        day = last_day
    else:
        day = min(source.day, last_day)
    return date(year, month, day)


def next_issue_date(current: date, interval: Interval | str, end_of_month: bool = True) -> date:
    """Return the next issue date for a recurrence interval."""
    interval_value = Interval(interval)
    month_map = {
        Interval.MONTHLY: 1,
        Interval.BIMONTHLY: 2,
        Interval.QUARTERLY: 3,
        Interval.YEARLY: 12,
    }
    return add_months(current, month_map[interval_value], end_of_month=end_of_month)


def generate_schedule(subscription: Subscription, count: int = 12) -> list[date]:
    """Generate upcoming issue dates for an active subscription."""
    validate_subscription(subscription)
    if count < 1:
        raise RecurringInvoiceError("count must be at least 1.")
    dates: list[date] = []
    current = subscription.start_date
    while len(dates) < count:
        if subscription.end_date and current > subscription.end_date:
            break
        dates.append(current)
        current = next_issue_date(current, subscription.interval, subscription.end_of_month)
    return dates


def calculate_totals(items: Iterable[LineItem], issue_date: date | None = None) -> dict[str, Decimal]:
    """Calculate subtotal, VAT amount, and total for invoice lines."""
    issue = issue_date or date.today()
    subtotal = Decimal("0.00")
    vat_amount = Decimal("0.00")
    for item in items:
        normalized = item.normalized(issue)
        line_subtotal = money(normalized.quantity * normalized.unit_price)
        line_vat = Decimal("0.00") if normalized.exempt else money(line_subtotal * Decimal(str(normalized.vat_rate)))
        subtotal += line_subtotal
        vat_amount += line_vat
    subtotal = money(subtotal)
    vat_amount = money(vat_amount)
    return {"subtotal": subtotal, "vat_amount": vat_amount, "total": money(subtotal + vat_amount)}


def validate_subscription(subscription: Subscription) -> None:
    """Validate subscription fields before invoice generation."""
    if not subscription.subscription_id.strip():
        raise RecurringInvoiceError("subscription_id is required.")
    if subscription.status == SubscriptionStatus.CANCELLED:
        raise RecurringInvoiceError("Cancelled subscriptions cannot generate new invoices.")
    if subscription.status == SubscriptionStatus.PAUSED:
        raise RecurringInvoiceError("Paused subscriptions cannot generate new invoices.")
    if subscription.end_date and subscription.end_date < subscription.start_date:
        raise RecurringInvoiceError("end_date cannot be before start_date.")
    if not subscription.line_items:
        raise RecurringInvoiceError("At least one invoice line is required.")
    if subscription.currency != DEFAULT_CURRENCY:
        raise RecurringInvoiceError("Only ILS recurring invoices are supported by this helper.")
    normalized_tax_id = subscription.customer.normalized_tax_id()
    if subscription.customer.vat_registered and not is_valid_israeli_tax_id(normalized_tax_id):
        raise RecurringInvoiceError("Customer tax ID checksum is invalid.")
    for item in subscription.line_items:
        if not item.description.strip():
            raise RecurringInvoiceError("Line description is required.")
        if money(item.quantity) <= 0:
            raise RecurringInvoiceError("Line quantity must be positive.")
        if money(item.unit_price) < 0:
            raise RecurringInvoiceError("Line unit price cannot be negative.")


def build_invoice(
    subscription: Subscription,
    issue_date: date,
    invoice_sequence: int,
    allocation_number: str | None = None,
) -> InvoiceDocument:
    """Build an invoice from a subscription for a specific issue date."""
    validate_subscription(subscription)
    if subscription.end_date and issue_date > subscription.end_date:
        raise RecurringInvoiceError("issue_date is after subscription end_date.")
    normalized_items = [item.normalized(issue_date) for item in subscription.line_items]
    totals = calculate_totals(normalized_items, issue_date)
    return InvoiceDocument(
        invoice_id=f"{subscription.subscription_id}-{invoice_sequence:06d}",
        subscription_id=subscription.subscription_id,
        issue_date=issue_date,
        customer=subscription.customer,
        line_items=normalized_items,
        document_type=subscription.document_type,
        currency=subscription.currency,
        subtotal=totals["subtotal"],
        vat_amount=totals["vat_amount"],
        total=totals["total"],
        allocation_number=allocation_number,
    )


ThresholdSchedule = Sequence[tuple[date, Decimal | int | float | str]]


def threshold_for_issue_date(issue_date: date, thresholds: ThresholdSchedule | Mapping[int, Decimal] | None = None) -> Decimal:
    """Return the invoice-allocation threshold effective on the issue date.

    The default schedule reflects live 2026 Tax Authority guidance: NIS 10,000
    from 2026-01-01 and NIS 5,000 from 2026-06-01. A mapping keeps backward
    compatibility with older year-based callers, but date-based schedules are
    preferred because thresholds can change mid-year.
    """
    if isinstance(thresholds, Mapping):
        return threshold_for_year(issue_date.year, thresholds)
    schedule = thresholds or DEFAULT_ALLOCATION_THRESHOLD_DATES
    normalized = sorted((effective, money(amount)) for effective, amount in schedule)
    selected = normalized[0][1]
    for effective, amount in normalized:
        if issue_date >= effective:
            selected = amount
        else:
            break
    return money(selected)


def threshold_for_year(year: int, thresholds: Mapping[int, Decimal] | None = None) -> Decimal:
    """Return the allocation threshold at the beginning of a tax year.

    Prefer threshold_for_issue_date for production because official thresholds
    can change during the same calendar year.
    """
    table = thresholds or DEFAULT_ALLOCATION_THRESHOLDS
    if year in table:
        return money(table[year])
    prior_years = [known for known in table if known <= year]
    if prior_years:
        return money(table[max(prior_years)])
    return money(min(table.values()))


def should_request_allocation(
    invoice: InvoiceDocument,
    business_tax_id: str,
    thresholds: ThresholdSchedule | Mapping[int, Decimal] | None = None,
) -> bool:
    """Return whether an allocation number should be requested."""
    if not is_valid_israeli_tax_id(business_tax_id):
        raise RecurringInvoiceError("Business tax ID checksum is invalid.")
    if invoice.document_type not in {DocumentType.TAX_INVOICE, DocumentType.TAX_INVOICE_RECEIPT}:
        return False
    threshold = threshold_for_issue_date(invoice.issue_date, thresholds)
    return money(invoice.subtotal) >= threshold

def invoice_to_dict(invoice: InvoiceDocument) -> dict[str, Any]:
    """Serialize an invoice with Decimal and date fields converted to strings."""
    return {
        "invoice_id": invoice.invoice_id,
        "subscription_id": invoice.subscription_id,
        "issue_date": invoice.issue_date.isoformat(),
        "customer": {
            "name": invoice.customer.name,
            "tax_id": invoice.customer.normalized_tax_id(),
            "email": invoice.customer.email,
            "address": invoice.customer.address,
            "vat_registered": invoice.customer.vat_registered,
        },
        "document_type": invoice.document_type.value,
        "currency": invoice.currency,
        "line_items": [
            {
                "description": item.description,
                "quantity": str(money(item.quantity)),
                "unit_price": str(money(item.unit_price)),
                "vat_rate": str(item.vat_rate),
                "exempt": item.exempt,
                "sku": item.sku,
            }
            for item in invoice.line_items
        ],
        "subtotal": str(money(invoice.subtotal)),
        "vat_amount": str(money(invoice.vat_amount)),
        "total": str(money(invoice.total)),
        "allocation_number": invoice.allocation_number,
        "references": dict(invoice.references),
    }


def subscription_to_dict(subscription: Subscription) -> dict[str, Any]:
    """Serialize a subscription to JSON-friendly fields."""
    return {
        "subscription_id": subscription.subscription_id,
        "customer": {
            "name": subscription.customer.name,
            "tax_id": subscription.customer.normalized_tax_id(),
            "email": subscription.customer.email,
            "address": subscription.customer.address,
            "vat_registered": subscription.customer.vat_registered,
        },
        "line_items": [
            {
                "description": item.description,
                "quantity": str(money(item.quantity)),
                "unit_price": str(money(item.unit_price)),
                "vat_rate": str(item.vat_rate) if item.vat_rate is not None else None,
                "exempt": item.exempt,
                "sku": item.sku,
            }
            for item in subscription.line_items
        ],
        "start_date": subscription.start_date.isoformat(),
        "interval": subscription.interval.value,
        "status": subscription.status.value,
        "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
        "end_of_month": subscription.end_of_month,
        "currency": subscription.currency,
        "document_type": subscription.document_type.value,
        "metadata": dict(subscription.metadata),
    }


def subscription_from_dict(payload: Mapping[str, Any]) -> Subscription:
    """Deserialize a subscription from JSON-friendly fields."""
    customer_payload = payload["customer"]
    customer = Customer(
        name=str(customer_payload["name"]),
        tax_id=str(customer_payload["tax_id"]),
        email=customer_payload.get("email"),
        address=customer_payload.get("address"),
        vat_registered=bool(customer_payload.get("vat_registered", True)),
    )
    items = [
        LineItem(
            description=str(item["description"]),
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            vat_rate=item.get("vat_rate"),
            exempt=bool(item.get("exempt", False)),
            sku=item.get("sku"),
        )
        for item in payload.get("line_items", [])
    ]
    end_date = date.fromisoformat(payload["end_date"]) if payload.get("end_date") else None
    subscription = Subscription(
        subscription_id=str(payload["subscription_id"]),
        customer=customer,
        line_items=items,
        start_date=date.fromisoformat(str(payload["start_date"])),
        interval=Interval(str(payload.get("interval", Interval.MONTHLY.value))),
        status=SubscriptionStatus(str(payload.get("status", SubscriptionStatus.ACTIVE.value))),
        end_date=end_date,
        end_of_month=bool(payload.get("end_of_month", True)),
        currency=str(payload.get("currency", DEFAULT_CURRENCY)),
        document_type=DocumentType(str(payload.get("document_type", DocumentType.TAX_INVOICE.value))),
        metadata=dict(payload.get("metadata", {})),
    )
    subscription.validate()
    return subscription


def create_shaam_allocation_payload(request: AllocationRequest) -> dict[str, Any]:
    """Create a SHAAM allocation request payload with stable keys."""
    invoice = request.invoice
    if not should_request_allocation(invoice, request.business_tax_id):
        raise RecurringInvoiceError("Invoice does not require an allocation request under configured thresholds.")
    return {
        "environment": request.environment,
        "clientTransactionId": request.client_transaction_id,
        "softwareId": request.software_id,
        "business": {"taxId": clean_israeli_tax_id(request.business_tax_id)},
        "invoice": {
            "invoiceId": invoice.invoice_id,
            "documentType": invoice.document_type.value,
            "issueDate": invoice.issue_date.isoformat(),
            "currency": invoice.currency,
            "customer": {
                "name": invoice.customer.name,
                "taxId": invoice.customer.normalized_tax_id(),
            },
            "amounts": {
                "subtotal": str(money(invoice.subtotal)),
                "vatAmount": str(money(invoice.vat_amount)),
                "total": str(money(invoice.total)),
            },
            "lines": [
                {
                    "description": item.description,
                    "quantity": str(money(item.quantity)),
                    "unitPrice": str(money(item.unit_price)),
                    "vatRate": str(item.vat_rate),
                    "exempt": item.exempt,
                }
                for item in invoice.line_items
            ],
        },
    }


def parse_allocation_response(payload: JsonMapping) -> AllocationResponse:
    """Normalize an allocation response from common gateway shapes."""
    allocation_number = (
        payload.get("allocationNumber")
        or payload.get("allocation_number")
        or payload.get("confirmation_number")
        or payload.get("Confirmation_Number")
        or payload.get("confirmation", {}).get("allocationNumber")
        or payload.get("Message", {}).get("Confirmation_Number")
    )
    if not allocation_number:
        raise RecurringInvoiceError("Allocation response does not include an allocation number.")
    status = str(payload.get("status") or payload.get("state") or "approved")
    return AllocationResponse(allocation_number=str(allocation_number), status=status, raw=dict(payload))


def credit_note_for_invoice(invoice: InvoiceDocument, reason: str, credit_sequence: int) -> InvoiceDocument:
    """Create a credit tax invoice that reverses an invoice."""
    if not reason.strip():
        raise RecurringInvoiceError("Credit reason is required.")
    credit_items = [
        LineItem(
            description=f"Credit for {item.description}",
            quantity=item.quantity,
            unit_price=-money(item.unit_price),
            vat_rate=item.vat_rate,
            exempt=item.exempt,
            sku=item.sku,
        )
        for item in invoice.line_items
    ]
    totals = calculate_totals(credit_items, invoice.issue_date)
    return InvoiceDocument(
        invoice_id=f"{invoice.invoice_id}-CR-{credit_sequence:03d}",
        subscription_id=invoice.subscription_id,
        issue_date=date.today(),
        customer=invoice.customer,
        line_items=credit_items,
        document_type=DocumentType.CREDIT_TAX_INVOICE,
        currency=invoice.currency,
        subtotal=totals["subtotal"],
        vat_amount=totals["vat_amount"],
        total=totals["total"],
        references={"original_invoice_id": invoice.invoice_id, "reason": reason.strip()},
    )


class RecurringInvoicingClient:
    """In-memory recurring invoicing client with sync and async allocation helpers."""

    def __init__(
        self,
        business_tax_id: str,
        environment: AllocationEnvironment = "sandbox",
        software_id: str | None = None,
        sync_transport: SyncTransport | None = None,
        async_transport: AsyncTransport | None = None,
    ) -> None:
        if environment not in {"sandbox", "production"}:
            raise RecurringInvoiceError("environment must be sandbox or production.")
        self.business_tax_id = clean_israeli_tax_id(business_tax_id)
        if not is_valid_israeli_tax_id(self.business_tax_id):
            raise RecurringInvoiceError("Business tax ID checksum is invalid.")
        self.environment: AllocationEnvironment = environment
        self.software_id = software_id
        self._sync_transport = sync_transport
        self._async_transport = async_transport
        self._subscriptions: dict[str, Subscription] = {}
        self._invoice_sequences: dict[str, int] = {}

    def create_subscription(self, subscription: Subscription) -> dict[str, Any]:
        """Store a subscription after validation."""
        subscription.validate()
        if subscription.subscription_id in self._subscriptions:
            raise RecurringInvoiceError("Subscription already exists.")
        self._subscriptions[subscription.subscription_id] = subscription
        return subscription_to_dict(subscription)

    def get_subscription(self, subscription_id: str) -> Subscription:
        """Return a stored subscription."""
        try:
            return self._subscriptions[subscription_id]
        except KeyError as exc:
            raise RecurringInvoiceError("Subscription was not found.") from exc

    def list_subscriptions(self, status: SubscriptionStatus | str | None = None) -> list[dict[str, Any]]:
        """Return stored subscriptions, optionally filtered by status."""
        status_value = SubscriptionStatus(status) if status else None
        return [
            subscription_to_dict(subscription)
            for subscription in self._subscriptions.values()
            if status_value is None or subscription.status == status_value
        ]

    def pause_subscription(self, subscription_id: str, reason: str | None = None) -> dict[str, Any]:
        """Pause a stored subscription."""
        subscription = self.get_subscription(subscription_id)
        if subscription.status == SubscriptionStatus.CANCELLED:
            raise RecurringInvoiceError("Cancelled subscriptions cannot be paused.")
        subscription.status = SubscriptionStatus.PAUSED
        if reason:
            subscription.metadata["pause_reason"] = reason
        return subscription_to_dict(subscription)

    def resume_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Resume a paused subscription."""
        subscription = self.get_subscription(subscription_id)
        if subscription.status == SubscriptionStatus.CANCELLED:
            raise RecurringInvoiceError("Cancelled subscriptions cannot be resumed.")
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.metadata.pop("pause_reason", None)
        return subscription_to_dict(subscription)

    def cancel_subscription(self, subscription_id: str, effective_date: date | None = None, reason: str | None = None) -> dict[str, Any]:
        """Cancel a subscription and set an optional effective date."""
        subscription = self.get_subscription(subscription_id)
        subscription.status = SubscriptionStatus.CANCELLED
        if effective_date:
            subscription.end_date = effective_date
        if reason:
            subscription.metadata["cancellation_reason"] = reason
        return subscription_to_dict(subscription)

    def generate_schedule(self, subscription_id: str, count: int = 12) -> list[str]:
        """Generate upcoming issue dates for a stored subscription."""
        return [value.isoformat() for value in generate_schedule(self.get_subscription(subscription_id), count=count)]

    def generate_invoice(self, subscription_id: str, issue_date: date | None = None) -> dict[str, Any]:
        """Generate the next invoice dictionary for a subscription."""
        subscription = self.get_subscription(subscription_id)
        sequence = self._invoice_sequences.get(subscription_id, 0) + 1
        self._invoice_sequences[subscription_id] = sequence
        invoice = build_invoice(subscription, issue_date or date.today(), sequence)
        return invoice.to_dict()

    def request_allocation(self, invoice: InvoiceDocument | Mapping[str, Any], client_transaction_id: str) -> dict[str, Any]:
        """Create an allocation payload without submitting it."""
        document = invoice if isinstance(invoice, InvoiceDocument) else invoice_from_dict(invoice)
        request = AllocationRequest(
            environment=self.environment,
            business_tax_id=self.business_tax_id,
            invoice=document,
            client_transaction_id=client_transaction_id,
            software_id=self.software_id,
        )
        return create_shaam_allocation_payload(request)

    def submit_allocation(
        self,
        invoice: InvoiceDocument | Mapping[str, Any],
        client_transaction_id: str,
        endpoint: str = "/invoices/allocations",
    ) -> AllocationResponse:
        """Submit an allocation request using the configured synchronous transport."""
        if self._sync_transport is None:
            raise RecurringInvoiceError("sync_transport is required for submit_allocation.")
        payload = self.request_allocation(invoice, client_transaction_id)
        response = self._sync_transport(endpoint, payload)
        return parse_allocation_response(response)

    async def async_submit_allocation(
        self,
        invoice: InvoiceDocument | Mapping[str, Any],
        client_transaction_id: str,
        endpoint: str = "/invoices/allocations",
    ) -> AllocationResponse:
        """Submit an allocation request using the configured asynchronous transport."""
        payload = self.request_allocation(invoice, client_transaction_id)
        if self._async_transport is not None:
            response = await self._async_transport(endpoint, payload)
        elif self._sync_transport is not None:
            response = await asyncio.to_thread(self._sync_transport, endpoint, payload)
        else:
            raise RecurringInvoiceError("async_transport or sync_transport is required for async_submit_allocation.")
        return parse_allocation_response(response)

    def export_state(self, path: str | Path) -> None:
        """Export subscriptions and sequence counters to JSON."""
        payload = {
            "business_tax_id": self.business_tax_id,
            "environment": self.environment,
            "software_id": self.software_id,
            "subscriptions": [subscription_to_dict(item) for item in self._subscriptions.values()],
            "invoice_sequences": dict(self._invoice_sequences),
        }
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def import_state(self, path: str | Path) -> None:
        """Import subscriptions and sequence counters from JSON."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        self._subscriptions = {
            item["subscription_id"]: subscription_from_dict(item)
            for item in payload.get("subscriptions", [])
        }
        self._invoice_sequences = {str(key): int(value) for key, value in payload.get("invoice_sequences", {}).items()}


def invoice_from_dict(payload: Mapping[str, Any]) -> InvoiceDocument:
    """Deserialize an InvoiceDocument from JSON-friendly fields."""
    customer_payload = payload["customer"]
    customer = Customer(
        name=str(customer_payload["name"]),
        tax_id=str(customer_payload["tax_id"]),
        email=customer_payload.get("email"),
        address=customer_payload.get("address"),
        vat_registered=bool(customer_payload.get("vat_registered", True)),
    )
    items = [
        LineItem(
            description=str(item["description"]),
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            vat_rate=item.get("vat_rate"),
            exempt=bool(item.get("exempt", False)),
            sku=item.get("sku"),
        ).normalized(date.fromisoformat(str(payload["issue_date"])))
        for item in payload.get("line_items", [])
    ]
    issue = date.fromisoformat(str(payload["issue_date"]))
    return InvoiceDocument(
        invoice_id=str(payload["invoice_id"]),
        subscription_id=str(payload["subscription_id"]),
        issue_date=issue,
        customer=customer,
        line_items=items,
        document_type=DocumentType(str(payload["document_type"])),
        currency=str(payload.get("currency", DEFAULT_CURRENCY)),
        subtotal=money(payload["subtotal"]),
        vat_amount=money(payload["vat_amount"]),
        total=money(payload["total"]),
        allocation_number=payload.get("allocation_number"),
        references=dict(payload.get("references", {})),
    )
