from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from enum import Enum
from typing import Any, Iterable, Literal, Mapping, MutableMapping, Sequence

import httpx

MoneyInput = Decimal | int | float | str
JsonObject = dict[str, Any]

VAT_RATE = Decimal("0.18")
VAT_RATE_PERCENT = Decimal("18.00")
MONEY_QUANT = Decimal("0.01")
ALLOCATION_INVOICE_TYPES = {300, 305}
PRELIMINARY_ALLOCATION_DOCUMENT_TYPE = 332

THRESHOLD_SCHEDULE: tuple[tuple[date, Decimal], ...] = (
    (date(2026, 6, 1), Decimal("5000.00")),
    (date(2026, 1, 1), Decimal("10000.00")),
    (date(2025, 1, 1), Decimal("20000.00")),
    (date(2024, 5, 1), Decimal("25000.00")),
)


class Environment(str, Enum):
    SANDBOX = "sandbox"
    PRODUCTION = "production"


ENDPOINTS: Mapping[Environment, Mapping[str, str]] = {
    Environment.SANDBOX: {
        "approval": "https://ita-api.taxes.gov.il/shaam/tsandbox/Invoices/v2/Approval",
        "multi_approval": "https://ita-api.taxes.gov.il/shaam/tsandbox/Multi-invoices/v2/MultiApproval",
        "details": "https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/details",
        "confirmation_number": "https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/confirmationNumber",
        "decision_cancel": "https://ita-api.taxes.gov.il/shaam/tsandbox/InvoiceDecisionApi/v1/Cancel",
        "decision_continue": "https://ita-api.taxes.gov.il/shaam/tsandbox/InvoiceDecisionApi/v1/Continue",
        "decision_further_objection": "https://ita-api.taxes.gov.il/shaam/tsandbox/InvoiceDecisionApi/v1/FurtherObjection",
    },
    Environment.PRODUCTION: {
        "approval": "https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval",
        "multi_approval": "https://ita-api.taxes.gov.il/shaam/production/Multi-invoices/v2/MultiApproval",
        "details": "https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/details",
        "confirmation_number": "https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/confirmationNumber",
        "decision_cancel": "https://ita-api.taxes.gov.il/shaam/production/InvoiceDecisionApi/v1/Cancel",
        "decision_continue": "https://ita-api.taxes.gov.il/shaam/production/InvoiceDecisionApi/v1/Continue",
        "decision_further_objection": "https://ita-api.taxes.gov.il/shaam/production/InvoiceDecisionApi/v1/FurtherObjection",
    },
}


class InvoiceValidationError(ValueError):
    """Raised when an invoice payload fails local validation."""

    def __init__(self, issues: Sequence[str]):
        self.issues = list(issues)
        super().__init__("; ".join(self.issues))


class InvoiceAPIError(RuntimeError):
    """Raised for transport, authentication, permission, or server failures."""

    def __init__(self, message: str, *, status_code: int | None = None, payload: Any | None = None):
        self.status_code = status_code
        self.payload = payload
        super().__init__(message)


class InvoiceAuthenticationError(InvoiceAPIError):
    """Raised for 401 or 403 responses."""


class InvoicePermissionError(InvoiceAuthenticationError):
    """Raised for permission-specific 403 responses."""


def _to_decimal(value: MoneyInput, field_name: str = "value") -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc


def money(value: MoneyInput) -> Decimal:
    return _to_decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def decimal_to_json(value: MoneyInput) -> float:
    return float(money(value))


def parse_invoice_date(value: str | date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError("date must be YYYY-MM-DD or DD-MM-YYYY")


def calculate_vat_amount(payment_amount: MoneyInput, rate: Decimal = VAT_RATE) -> Decimal:
    return money(_to_decimal(payment_amount, "payment_amount") * rate)


def calculate_total_including_vat(payment_amount: MoneyInput, vat_amount: MoneyInput | None = None) -> Decimal:
    vat = calculate_vat_amount(payment_amount) if vat_amount is None else money(vat_amount)
    return money(_to_decimal(payment_amount, "payment_amount") + vat)


def normalize_vat_number(value: int | str) -> str:
    digits = "".join(ch for ch in str(value).strip() if ch.isdigit())
    if len(digits) > 9:
        raise ValueError("VAT number must not exceed 9 digits")
    return digits.zfill(9)


def is_valid_vat_number(value: int | str) -> bool:
    try:
        digits = normalize_vat_number(value)
    except ValueError:
        return False
    if digits == "000000000" or len(digits) != 9:
        return False
    total = 0
    for index, char in enumerate(digits):
        number = int(char) * (1 if index % 2 == 0 else 2)
        if number > 9:
            number -= 9
        total += number
    return total % 10 == 0


def threshold_for(invoice_date: str | date | datetime) -> Decimal:
    parsed = parse_invoice_date(invoice_date)
    for effective_date, threshold in THRESHOLD_SCHEDULE:
        if parsed >= effective_date:
            return threshold
    return Decimal("Infinity")


def requires_allocation(
    *,
    invoice_type: int,
    payment_amount: MoneyInput,
    invoice_date: str | date | datetime,
    seller_is_vat_registered: bool = True,
    buyer_is_vat_registered: bool = True,
    israeli_b2b: bool = True,
) -> bool:
    if not seller_is_vat_registered or not buyer_is_vat_registered or not israeli_b2b:
        return False
    if int(invoice_type) not in ALLOCATION_INVOICE_TYPES:
        return False
    return money(payment_amount) > threshold_for(invoice_date)


def shortened_allocation_number(confirmation_number: str | int) -> str:
    digits = "".join(ch for ch in str(confirmation_number) if ch.isdigit())
    if len(digits) < 9:
        raise ValueError("confirmation number must contain at least 9 digits")
    return digits[-9:]


@dataclass(slots=True)
class LineItem:
    index: int
    description: str
    quantity: MoneyInput
    price_per_unit: MoneyInput
    discount: MoneyInput = Decimal("0.00")
    total_amount: MoneyInput | None = None
    vat_rate: MoneyInput = VAT_RATE_PERCENT
    vat_amount: MoneyInput | None = None
    catalog_id: str | None = None
    category: str | None = None
    measurement_unit: str | None = None

    def computed_total(self) -> Decimal:
        total = _to_decimal(self.quantity, "quantity") * _to_decimal(self.price_per_unit, "price_per_unit")
        total -= _to_decimal(self.discount, "discount")
        return money(total)

    def computed_vat(self) -> Decimal:
        rate_percent = _to_decimal(self.vat_rate, "vat_rate")
        return money(self.computed_total() * (rate_percent / Decimal("100")))

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.index < 1:
            issues.append("line item index must be positive")
        if not self.description.strip():
            issues.append(f"line {self.index}: description is required")
        if _to_decimal(self.quantity, "quantity") <= 0:
            issues.append(f"line {self.index}: quantity must be positive")
        if _to_decimal(self.price_per_unit, "price_per_unit") < 0:
            issues.append(f"line {self.index}: price_per_unit must not be negative")
        if _to_decimal(self.discount, "discount") < 0:
            issues.append(f"line {self.index}: discount must not be negative")
        if self.total_amount is not None and money(self.total_amount) != self.computed_total():
            issues.append(f"line {self.index}: total_amount does not match quantity, price, and discount")
        if self.vat_amount is not None and money(self.vat_amount) != self.computed_vat():
            issues.append(f"line {self.index}: vat_amount does not match line total and vat_rate")
        return issues

    def to_api_dict(self) -> JsonObject:
        data: JsonObject = {
            "index": self.index,
            "description": self.description,
            "quantity": decimal_to_json(self.quantity),
            "price_per_unit": decimal_to_json(self.price_per_unit),
            "discount": decimal_to_json(self.discount),
            "total_amount": decimal_to_json(self.total_amount if self.total_amount is not None else self.computed_total()),
            "vat_rate": decimal_to_json(self.vat_rate),
            "vat_amount": decimal_to_json(self.vat_amount if self.vat_amount is not None else self.computed_vat()),
        }
        for key in ("catalog_id", "category", "measurement_unit"):
            value = getattr(self, key)
            if value:
                data[key] = value
        return data

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "LineItem":
        return cls(
            index=int(payload.get("index", payload.get("line_number", 1))),
            description=str(payload.get("description", payload.get("item_description", ""))),
            quantity=payload.get("quantity", 1),
            price_per_unit=payload.get("price_per_unit", 0),
            discount=payload.get("discount", 0),
            total_amount=payload.get("total_amount"),
            vat_rate=payload.get("vat_rate", VAT_RATE_PERCENT),
            vat_amount=payload.get("vat_amount"),
            catalog_id=payload.get("catalog_id"),
            category=payload.get("category"),
            measurement_unit=payload.get("measurement_unit"),
        )


@dataclass(slots=True)
class InvoiceApprovalRequest:
    invoice_id: str
    invoice_type: int
    vat_number: int | str
    customer_vat_number: int | str | None
    customer_name: str
    invoice_date: str | date
    invoice_issuance_date: str | date
    accounting_software_number: int | str
    amount_before_discount: MoneyInput
    discount: MoneyInput
    payment_amount: MoneyInput
    vat_amount: MoneyInput
    payment_amount_including_vat: MoneyInput
    union_vat_number: int | str | None = None
    authorized_company: int | str | None = None
    user_id: int | str | None = None
    user_name: str | None = None
    invoice_reference_number: str | None = None
    invoice_note: str | None = None
    action: int | None = None
    items: list[LineItem] = field(default_factory=list)
    israeli_b2b: bool = True

    def local_validation_errors(self) -> list[str]:
        issues: list[str] = []
        if not str(self.invoice_id).strip():
            issues.append("invoice_id is required")
        if int(self.invoice_type) <= 0:
            issues.append("invoice_type must be a positive official document type code")
        if not is_valid_vat_number(self.vat_number):
            issues.append("vat_number must be a valid 9-digit Israeli VAT number")
        if self.customer_vat_number is not None and not is_valid_vat_number(self.customer_vat_number):
            issues.append("customer_vat_number must be a valid 9-digit Israeli VAT number")
        if self.accounting_software_number is None or not str(self.accounting_software_number).strip():
            issues.append("accounting_software_number is required")
        try:
            printed_date = parse_invoice_date(self.invoice_date)
            issue_date = parse_invoice_date(self.invoice_issuance_date)
            if issue_date < printed_date - timedelta(days=31):
                issues.append("invoice_issuance_date is unexpectedly earlier than invoice_date")
        except ValueError as exc:
            issues.append(str(exc))
            printed_date = date.today()
        if money(self.discount) < 0:
            issues.append("discount must not be negative")
        if money(self.amount_before_discount) - money(self.discount) != money(self.payment_amount):
            issues.append("payment_amount must equal amount_before_discount minus discount")
        expected_total = money(self.payment_amount) + money(self.vat_amount)
        if expected_total != money(self.payment_amount_including_vat):
            issues.append("payment_amount_including_vat must equal payment_amount plus vat_amount")
        if money(self.vat_amount) > 0:
            expected_vat = calculate_vat_amount(self.payment_amount)
            if money(self.vat_amount) != expected_vat:
                issues.append(f"vat_amount must be {expected_vat} at 18% VAT")
        if self.action == 3 and money(self.vat_amount) != Decimal("0.00"):
            issues.append("reverse charge action requires zero VAT amount")
        needs_allocation = requires_allocation(
            invoice_type=int(self.invoice_type),
            payment_amount=self.payment_amount,
            invoice_date=printed_date,
            buyer_is_vat_registered=self.customer_vat_number is not None,
            israeli_b2b=self.israeli_b2b,
        )
        if self.israeli_b2b and int(self.invoice_type) in ALLOCATION_INVOICE_TYPES and money(self.payment_amount) > threshold_for(printed_date):
            if self.customer_vat_number is None:
                issues.append("customer_vat_number is required for above-threshold Israeli B2B tax invoices")
        if needs_allocation and not self.customer_name.strip():
            issues.append("customer_name is required for allocation requests")
        for item in self.items:
            issues.extend(item.validate())
        return issues

    def raise_for_validation_errors(self) -> None:
        issues = self.local_validation_errors()
        if issues:
            raise InvoiceValidationError(issues)

    def needs_allocation(self) -> bool:
        return requires_allocation(
            invoice_type=int(self.invoice_type),
            payment_amount=self.payment_amount,
            invoice_date=self.invoice_date,
            buyer_is_vat_registered=self.customer_vat_number is not None,
            israeli_b2b=self.israeli_b2b,
        )

    def to_api_dict(self) -> JsonObject:
        payload: JsonObject = {
            "invoice_id": self.invoice_id,
            "invoice_type": int(self.invoice_type),
            "vat_number": int(normalize_vat_number(self.vat_number)),
            "customer_name": self.customer_name,
            "invoice_date": parse_invoice_date(self.invoice_date).isoformat(),
            "invoice_issuance_date": parse_invoice_date(self.invoice_issuance_date).isoformat(),
            "accounting_software_number": int(normalize_vat_number(self.accounting_software_number)),
            "amount_before_discount": decimal_to_json(self.amount_before_discount),
            "discount": decimal_to_json(self.discount),
            "payment_amount": decimal_to_json(self.payment_amount),
            "vat_amount": decimal_to_json(self.vat_amount),
            "payment_amount_including_vat": decimal_to_json(self.payment_amount_including_vat),
        }
        optional_values: Mapping[str, Any] = {
            "customer_vat_number": self.customer_vat_number,
            "union_vat_number": self.union_vat_number,
            "authorized_company": self.authorized_company,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "invoice_reference_number": self.invoice_reference_number,
            "invoice_note": self.invoice_note,
            "action": self.action,
        }
        for key, value in optional_values.items():
            if value is None or value == "":
                continue
            if key.endswith("vat_number") or key in {"authorized_company", "user_id"}:
                payload[key] = int(normalize_vat_number(value))
            elif key == "action":
                payload[key] = int(value)
            else:
                payload[key] = value
        if self.items:
            payload["items"] = [item.to_api_dict() for item in self.items]
        return payload

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "InvoiceApprovalRequest":
        items_payload = payload.get("items") or payload.get("Items") or []
        return cls(
            invoice_id=str(payload.get("invoice_id", payload.get("Invoice_ID", ""))),
            invoice_type=int(payload.get("invoice_type", payload.get("Invoice_Type", 0))),
            vat_number=payload.get("vat_number", payload.get("Vat_Number", "")),
            customer_vat_number=payload.get("customer_vat_number", payload.get("Customer_VAT_Number")),
            customer_name=str(payload.get("customer_name", payload.get("Customer_Name", ""))),
            invoice_date=payload.get("invoice_date", payload.get("Invoice_Date", "")),
            invoice_issuance_date=payload.get("invoice_issuance_date", payload.get("Invoice_Issuance_Date", payload.get("invoice_date", ""))),
            accounting_software_number=payload.get("accounting_software_number", payload.get("Accounting_Software_Number", "")),
            amount_before_discount=payload.get("amount_before_discount", payload.get("Amount_Before_Discount", 0)),
            discount=payload.get("discount", payload.get("Discount", 0)),
            payment_amount=payload.get("payment_amount", payload.get("Payment_Amount", 0)),
            vat_amount=payload.get("vat_amount", payload.get("VAT_Amount", 0)),
            payment_amount_including_vat=payload.get("payment_amount_including_vat", payload.get("Payment_Amount_Including_VAT", 0)),
            union_vat_number=payload.get("union_vat_number"),
            authorized_company=payload.get("authorized_company"),
            user_id=payload.get("user_id"),
            user_name=payload.get("user_name"),
            invoice_reference_number=payload.get("invoice_reference_number", payload.get("Invoice_Reference_Number")),
            invoice_note=payload.get("invoice_note", payload.get("Invoice_Note")),
            action=payload.get("action", payload.get("Action")),
            items=[LineItem.from_payload(item) for item in items_payload],
            israeli_b2b=bool(payload.get("israeli_b2b", True)),
        )


@dataclass(slots=True)
class ApprovalResponse:
    status: int
    approved: bool
    confirmation_number: str
    message: Any
    raw: Mapping[str, Any]
    transaction_id: str | None = None

    @property
    def errors(self) -> list[Mapping[str, Any]]:
        message = self.message
        if isinstance(message, Mapping):
            errors = message.get("errors", [])
            return list(errors) if isinstance(errors, list) else []
        return []

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "ApprovalResponse":
        status = int(payload.get("status", payload.get("Status", 0)))
        confirmation = str(payload.get("confirmation_number", payload.get("Confirmation_Number", "0")))
        approved_value = payload.get("approved")
        approved = bool(approved_value) if approved_value is not None else confirmation not in {"", "0", "None"}
        return cls(
            status=status,
            approved=approved,
            confirmation_number=confirmation,
            message=payload.get("message", payload.get("Message", "")),
            raw=payload,
            transaction_id=payload.get("transaction_id"),
        )


class InvoiceComplianceClient:
    def __init__(
        self,
        access_token: str,
        environment: Environment | str = Environment.SANDBOX,
        *,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.access_token = access_token
        self.environment = Environment(environment)
        self.timeout = timeout
        self.transport = transport

    @property
    def endpoints(self) -> Mapping[str, str]:
        return ENDPOINTS[self.environment]

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _handle_http_response(self, response: httpx.Response) -> JsonObject:
        try:
            payload: Any = response.json()
        except ValueError:
            payload = {"message": response.text}
        if response.status_code == 401:
            raise InvoiceAuthenticationError("Tax Authority API returned 401 Unauthorized", status_code=401, payload=payload)
        if response.status_code == 403:
            raise InvoicePermissionError("Tax Authority API returned 403 Forbidden", status_code=403, payload=payload)
        if response.status_code >= 500:
            raise InvoiceAPIError("Tax Authority API returned a server error", status_code=response.status_code, payload=payload)
        if not isinstance(payload, dict):
            raise InvoiceAPIError("Tax Authority API returned non-object JSON", status_code=response.status_code, payload=payload)
        return payload

    def _post_json(self, endpoint_key: str, payload: Mapping[str, Any]) -> JsonObject:
        with httpx.Client(timeout=self.timeout, transport=self.transport if isinstance(self.transport, httpx.BaseTransport) else None) as client:
            response = client.post(self.endpoints[endpoint_key], headers=self._headers(), json=dict(payload))
            return self._handle_http_response(response)

    async def _apost_json(self, endpoint_key: str, payload: Mapping[str, Any]) -> JsonObject:
        async_transport = self.transport if isinstance(self.transport, httpx.AsyncBaseTransport) else None
        async with httpx.AsyncClient(timeout=self.timeout, transport=async_transport) as client:
            response = await client.post(self.endpoints[endpoint_key], headers=self._headers(), json=dict(payload))
            return self._handle_http_response(response)

    def request_approval(self, request: InvoiceApprovalRequest) -> ApprovalResponse:
        request.raise_for_validation_errors()
        return ApprovalResponse.from_payload(self._post_json("approval", request.to_api_dict()))

    async def async_request_approval(self, request: InvoiceApprovalRequest) -> ApprovalResponse:
        request.raise_for_validation_errors()
        return ApprovalResponse.from_payload(await self._apost_json("approval", request.to_api_dict()))

    def request_multi_approval(self, requests: Sequence[InvoiceApprovalRequest]) -> JsonObject:
        if not requests:
            raise InvoiceValidationError(["at least one invoice is required"])
        for request in requests:
            request.raise_for_validation_errors()
        first = requests[0]
        payload = {
            "vat_number": int(normalize_vat_number(first.vat_number)),
            "union_vat_number": int(normalize_vat_number(first.union_vat_number)) if first.union_vat_number else 0,
            "invoices_amount": len(requests),
            "invoices_payment_amount": decimal_to_json(sum((money(req.payment_amount) for req in requests), Decimal("0.00"))),
            "invoices_vat_amount": decimal_to_json(sum((money(req.vat_amount) for req in requests), Decimal("0.00"))),
            "invoices_list": [request.to_api_dict() for request in requests],
        }
        return self._post_json("multi_approval", payload)

    async def async_request_multi_approval(self, requests: Sequence[InvoiceApprovalRequest]) -> JsonObject:
        if not requests:
            raise InvoiceValidationError(["at least one invoice is required"])
        for request in requests:
            request.raise_for_validation_errors()
        first = requests[0]
        payload = {
            "vat_number": int(normalize_vat_number(first.vat_number)),
            "union_vat_number": int(normalize_vat_number(first.union_vat_number)) if first.union_vat_number else 0,
            "invoices_amount": len(requests),
            "invoices_payment_amount": decimal_to_json(sum((money(req.payment_amount) for req in requests), Decimal("0.00"))),
            "invoices_vat_amount": decimal_to_json(sum((money(req.vat_amount) for req in requests), Decimal("0.00"))),
            "invoices_list": [request.to_api_dict() for request in requests],
        }
        return await self._apost_json("multi_approval", payload)

    def get_invoice_details(self, *, customer_vat_number: int | str, confirmation_number: str, vat_number: int | str | None = None) -> JsonObject:
        payload: JsonObject = {
            "Customer_VAT_Number": int(normalize_vat_number(customer_vat_number)),
            "Confirmation_Number": str(confirmation_number),
        }
        if vat_number is not None:
            payload["Vat_Number"] = int(normalize_vat_number(vat_number))
        return self._post_json("details", payload)

    def get_confirmation_number(
        self,
        *,
        customer_vat_number: int | str,
        vat_number: int | str,
        payment_amount: MoneyInput,
        vat_amount: MoneyInput,
        invoice_date: str | date,
        invoice_reference_number: str | None = None,
    ) -> JsonObject:
        payload: JsonObject = {
            "Customer_VAT_Number": int(normalize_vat_number(customer_vat_number)),
            "Vat_Number": int(normalize_vat_number(vat_number)),
            "Payment_Amount": decimal_to_json(payment_amount),
            "VAT_Amount": decimal_to_json(vat_amount),
            "Invoice_Date": parse_invoice_date(invoice_date).isoformat(),
        }
        if invoice_reference_number:
            payload["Invoice_Reference_Number"] = invoice_reference_number
        return self._post_json("confirmation_number", payload)

    def submit_decision(
        self,
        *,
        decision: Literal["cancel", "continue", "further_objection"],
        invoice_id: str,
        vat_number: int | str,
        accounting_software_number: int | str,
        authorized_company: int | str | None = None,
        user_id: int | str | None = None,
        user_name: str | None = None,
    ) -> JsonObject:
        endpoint_key = f"decision_{decision}"
        if endpoint_key not in self.endpoints:
            raise ValueError("decision must be cancel, continue, or further_objection")
        payload: JsonObject = {
            "invoice_id": invoice_id,
            "vat_number": int(normalize_vat_number(vat_number)),
            "accounting_software_number": int(normalize_vat_number(accounting_software_number)),
        }
        if authorized_company:
            payload["authorized_company"] = int(normalize_vat_number(authorized_company))
        if user_id:
            payload["user_id"] = int(normalize_vat_number(user_id))
        if user_name:
            payload["user_name"] = user_name
        return self._post_json(endpoint_key, payload)


def validate_invoice_payload(payload: Mapping[str, Any]) -> list[str]:
    return InvoiceApprovalRequest.from_payload(payload).local_validation_errors()
