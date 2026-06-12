#!/usr/bin/env python3
"""Receipt generator for Israeli card-payment gateway payloads."""

from __future__ import annotations

import asyncio
import hashlib
import html
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Optional

MONEY_QUANT = Decimal("0.01")
DEFAULT_VAT_RATE = Decimal("0.18")
DEFAULT_CURRENCY = "ILS"
OSEK_PATUR_CEILING_2026 = Decimal("122833")
ISRAEL_INVOICES_THRESHOLD_2026_JAN = Decimal("10000")
ISRAEL_INVOICES_THRESHOLD_2026_JUN = Decimal("5000")


class Gateway(str, Enum):
    """Supported Israeli payment gateways."""

    CARDCOM = "cardcom"
    TRANZILA = "tranzila"
    GROW = "grow"
    MESHULAM = "meshulam"
    PELECARD = "pelecard"


class ReceiptFormat(str, Enum):
    """Supported render formats."""

    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


class ReceiptValidationError(ValueError):
    """Raised when a receipt cannot be generated safely."""


@dataclass(frozen=True)
class VatBreakdown:
    """VAT split for a gross payment amount."""

    gross: Decimal
    net: Decimal
    vat: Decimal
    vat_rate: Decimal
    exempt_dealer: bool = False

    def as_display(self) -> dict[str, str]:
        return {
            "gross": format_money(self.gross),
            "net": format_money(self.net),
            "vat": format_money(self.vat),
            "vat_rate": f"{(self.vat_rate * Decimal('100')).quantize(Decimal('0.01'))}%",
            "exempt_dealer": str(self.exempt_dealer).lower(),
        }


@dataclass(frozen=True)
class NormalizedGatewayResult:
    """Gateway result after provider-specific field mapping."""

    gateway: Gateway
    success: bool
    transaction_id: str
    approval_number: str = ""
    amount: Optional[Decimal] = None
    currency: str = DEFAULT_CURRENCY
    masked_card: str = ""
    card_brand: str = ""
    document_number: str = ""
    document_url: str = ""
    raw_status: str = ""
    source_hash: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ReceiptRecord:
    """Data required to render a receipt draft."""

    gateway: Gateway
    business_name: str
    business_tax_id: str
    customer_name: str
    amount: Decimal
    currency: str
    payment_date: date
    transaction_id: str
    approval_number: str
    receipt_number: str
    masked_card: str = ""
    card_brand: str = ""
    document_number: str = ""
    document_url: str = ""
    allocation_number: str = ""
    source_hash: str = ""
    exempt_dealer: bool = False
    description: str = "Card payment"
    notes: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        errors: list[str] = []
        if not self.business_name.strip():
            errors.append("business_name is required")
        if not is_valid_israeli_id(self.business_tax_id):
            errors.append("business_tax_id must contain a valid 9-digit Israeli ID")
        if not self.customer_name.strip():
            errors.append("customer_name is required")
        if self.amount <= 0:
            errors.append("amount must be positive")
        if self.currency.upper() != "ILS":
            errors.append("currency must be ILS for Israeli receipt output")
        if not self.transaction_id.strip():
            errors.append("transaction_id is required")
        if not self.receipt_number.strip():
            errors.append("receipt_number is required")
        if contains_raw_pan(asdict(self)):
            errors.append("raw card number detected; use masked card or last4 only")
        if errors:
            raise ReceiptValidationError("; ".join(errors))


PROVIDER_ENDPOINTS: dict[Gateway, dict[str, dict[str, str]]] = {
    Gateway.CARDCOM: {
        "low_profile_create": {
            "method": "POST",
            "url": "https://secure.cardcom.solutions/api/v11/LowProfile/Create",
            "purpose": "Create hosted payment page",
        },
        "low_profile_result": {
            "method": "POST",
            "url": "https://secure.cardcom.solutions/api/v11/LowProfile/GetLpResult",
            "purpose": "Fetch hosted payment result",
        },
        "create_document": {
            "method": "POST",
            "url": "https://secure.cardcom.solutions/api/v11/Documents/CreateDocument",
            "purpose": "Create provider document",
        },
    },
    Gateway.TRANZILA: {
        "payment_request": {
            "method": "POST",
            "url": "https://api.tranzila.com/v1/pr/create",
            "purpose": "Create payment request",
        },
        "credit_card_create": {
            "method": "POST",
            "url": "https://api.tranzila.com/v1/transaction/credit_card/create",
            "purpose": "Create credit-card transaction",
        },
        "handshake": {
            "method": "POST",
            "url": "https://api.tranzila.com/v1/handshake/create",
            "purpose": "Create iframe handshake",
        },
    },
    Gateway.GROW: {
        "create_payment_process": {
            "method": "POST",
            "url": "https://sandbox.meshulam.co.il/api/light/server/1.0/createPaymentProcess",
            "purpose": "Create payment process",
        },
        "create_transaction_with_token": {
            "method": "POST",
            "url": "https://sandbox.meshulam.co.il/api/light/server/1.0/createTransactionWithToken",
            "purpose": "Charge saved token",
        },
        "get_payment_link_info": {
            "method": "POST",
            "url": "https://sandbox.meshulam.co.il/api/light/server/1.0/getPaymentLinkInfo",
            "purpose": "Fetch payment link info",
        },
    },
    Gateway.MESHULAM: {},
    Gateway.PELECARD: {
        "add_receipt": {
            "method": "POST",
            "url": "https://gateway21.pelecard.biz/services/AddDebitTrxReceipt",
            "purpose": "Add receipt to debit transaction",
        },
        "debit_regular": {
            "method": "POST",
            "url": "https://gateway21.pelecard.biz/services/DebitRegularType",
            "purpose": "Debit regular transaction",
        },
        "pending_regular": {
            "method": "POST",
            "url": "https://gateway21.pelecard.biz/services/PendingRegularType",
            "purpose": "Create pending regular transaction",
        },
    },
}
PROVIDER_ENDPOINTS[Gateway.MESHULAM] = PROVIDER_ENDPOINTS[Gateway.GROW]


def to_decimal(value: Any) -> Decimal:
    """Convert a numeric value to a money-safe Decimal."""
    if value is None or value == "":
        raise ReceiptValidationError("amount is required")
    cleaned = str(value).replace(",", "").replace("₪", "").strip()
    return Decimal(cleaned).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def format_money(value: Decimal, currency: str = DEFAULT_CURRENCY) -> str:
    """Format ILS values for receipt output."""
    quantized = value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    if currency.upper() == "ILS":
        return f"₪{quantized:,.2f}"
    return f"{currency.upper()} {quantized:,.2f}"


def format_israeli_date(value: date) -> str:
    """Return DD-MM-YYYY display date."""
    return value.strftime("%d-%m-%Y")


def split_gross_amount(
    gross: Decimal,
    vat_rate: Decimal = DEFAULT_VAT_RATE,
    exempt_dealer: bool = False,
) -> VatBreakdown:
    """Split a gross amount into net and VAT components."""
    gross = gross.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    if exempt_dealer:
        return VatBreakdown(gross=gross, net=gross, vat=Decimal("0.00"), vat_rate=Decimal("0.00"), exempt_dealer=True)
    divisor = Decimal("1.00") + vat_rate
    net = (gross / divisor).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    vat = (gross - net).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    return VatBreakdown(gross=gross, net=net, vat=vat, vat_rate=vat_rate, exempt_dealer=False)


def is_valid_israeli_id(value: str) -> bool:
    """Validate a 9-digit Israeli ID/company-style checksum."""
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) > 9:
        return False
    digits = digits.zfill(9)
    total = 0
    for index, char in enumerate(digits):
        digit = int(char)
        step = digit * (1 if index % 2 == 0 else 2)
        if step > 9:
            step -= 9
        total += step
    return total % 10 == 0


def luhn_valid(number: str) -> bool:
    digits = [int(ch) for ch in re.sub(r"\D", "", number)]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def contains_raw_pan(data: Any) -> bool:
    """Detect raw payment card numbers in nested data."""
    allowed_key_parts = {"tax", "business_tax_id", "customer_tax_id", "id_number"}

    def walk(value: Any, key_path: str = "") -> bool:
        if isinstance(value, Mapping):
            for key, item in value.items():
                child_key = f"{key_path}.{key}" if key_path else str(key)
                if walk(item, child_key):
                    return True
            return False
        if isinstance(value, (list, tuple, set)):
            return any(walk(item, key_path) for item in value)
        if value is None:
            return False
        lowered = key_path.lower()
        if any(part in lowered for part in allowed_key_parts):
            return False
        text = str(value)
        for candidate in re.findall(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)", text):
            if "*" in candidate:
                continue
            if luhn_valid(candidate):
                return True
        return False

    return walk(data)


def source_hash(payload: Mapping[str, Any]) -> str:
    """Return a stable hash for reconciliation."""
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _first(payload: Mapping[str, Any], *keys: str, default: str = "") -> Any:
    for key in keys:
        current: Any = payload
        found = True
        for part in key.split("."):
            if isinstance(current, Mapping) and part in current:
                current = current[part]
            else:
                found = False
                break
        if found and current not in (None, ""):
            return current
    return default


def _string(value: Any) -> str:
    return "" if value is None else str(value)


def normalize_gateway_payload(gateway: Gateway | str, payload: Mapping[str, Any]) -> NormalizedGatewayResult:
    """Normalize provider-specific gateway payload fields."""
    gateway = gateway if isinstance(gateway, Gateway) else Gateway(str(gateway).lower())
    if contains_raw_pan(payload):
        raise ReceiptValidationError("raw card number detected; use masked card or last4 only")
    digest = source_hash(payload)
    warnings: list[str] = []

    if gateway == Gateway.MESHULAM:
        gateway = Gateway.GROW

    amount_value = _first(payload, "Amount", "amount", "sum", "Total", "total", "data.amount", default="")
    amount = to_decimal(amount_value) if amount_value not in (None, "") else None
    currency = _string(_first(payload, "Currency", "currency", "ISOCoinId", "currencyCode", default=DEFAULT_CURRENCY))
    if currency in {"1", "ILS", "ils", "376"}:
        currency = DEFAULT_CURRENCY

    if gateway == Gateway.CARDCOM:
        raw_code = _string(_first(payload, "ResponseCode", "TranzactionInfo.ResponseCode", default=""))
        success = raw_code in {"0", "700", "701"}
        transaction_id = _string(_first(payload, "TranzactionId", "TranzactionInfo.TranzactionId", "LowProfileId", default=""))
        approval = _string(_first(payload, "ApprovalNumber", "TranzactionInfo.ApprovalNumber", default=""))
        document_number = _string(_first(payload, "DocumentNumber", "DocumentInfo.DocumentNumber", default=""))
        document_url = _string(_first(payload, "DocumentUrl", "DocumentInfo.DocumentUrl", default=""))
        masked = _string(_first(payload, "Last4", "CardLast4", "TranzactionInfo.Last4", "CreditCardNumber", default=""))
        if masked and not masked.startswith("*") and masked.isdigit() and len(masked) <= 4:
            masked = "****" + masked
        raw_status = raw_code or _string(_first(payload, "Description", default=""))
    elif gateway == Gateway.TRANZILA:
        raw_code = _string(_first(payload, "response_code", "Response", "code", "status", "status_code", default=""))
        success = raw_code.lower() in {"0", "000", "success", "approved", "ok", "paid", "1"}
        transaction_id = _string(_first(payload, "transaction_id", "transactionId", "index", "tranmode_id", "data.transaction_id", default=""))
        approval = _string(_first(payload, "auth_number", "authnr", "confirmation_code", "approval_number", default=""))
        document_number = _string(_first(payload, "document_number", "invoice_number", default=""))
        document_url = _string(_first(payload, "document_url", "invoice_url", default=""))
        masked = _string(_first(payload, "masked_card", "ccno", "last4", default=""))
        if masked.isdigit() and len(masked) <= 4:
            masked = "****" + masked
        raw_status = raw_code
    elif gateway == Gateway.GROW:
        raw_code = _string(_first(payload, "status", "statusCode", "response.status", "data.status", default=""))
        success = raw_code.lower() in {"success", "approved", "paid", "1", "0", "000", "ok"}
        transaction_id = _string(_first(payload, "transactionId", "transaction_id", "paymentId", "transactionToken", "data.transactionId", default=""))
        approval = _string(_first(payload, "asmachta", "authNumber", "approvalNumber", "transactionUniqueIdentifier", default=""))
        document_number = _string(_first(payload, "invoiceNumber", "documentNumber", default=""))
        document_url = _string(_first(payload, "invoiceUrl", "documentUrl", default=""))
        masked = _string(_first(payload, "cardSuffix", "last4", "maskedCard", default=""))
        if masked.isdigit() and len(masked) <= 4:
            masked = "****" + masked
        raw_status = raw_code
    elif gateway == Gateway.PELECARD:
        status = _string(_first(payload, "StatusCode", "statusCode", default=""))
        shva = _string(_first(payload, "ShvaResult", "ResultData.ShvaResult", default=""))
        success = status == "000" and shva in {"", "000"}
        transaction_id = _string(_first(payload, "PelecardTransactionId", "ResultData.PelecardTransactionId", default=""))
        approval = _string(_first(payload, "VoucherId", "ConfirmationKey", "ResultData.VoucherId", "ResultData.ConfirmationKey", default=""))
        document_number = _string(_first(payload, "Receipt", "Reciept", "ResultData.Receipt", "ResultData.Reciept", default=""))
        document_url = _string(_first(payload, "ReceiptUrl", "DocumentUrl", default=""))
        masked = _string(_first(payload, "CreditCardNumber", "ResultData.CreditCardNumber", "last4", default=""))
        raw_status = status or shva
    else:
        raise ReceiptValidationError(f"unsupported gateway: {gateway}")

    if success and not transaction_id:
        warnings.append("gateway success was detected but transaction_id is missing")
    if not success:
        warnings.append("gateway success could not be confirmed")

    return NormalizedGatewayResult(
        gateway=gateway,
        success=success,
        transaction_id=transaction_id,
        approval_number=approval,
        amount=amount,
        currency=currency,
        masked_card=masked,
        card_brand=_string(_first(payload, "CardBrand", "cardBrand", "CreditCardCompany", default="")),
        document_number=document_number,
        document_url=document_url,
        raw_status=raw_status,
        source_hash=digest,
        warnings=tuple(warnings),
    )


def allocation_threshold_for(payment_date: date) -> Decimal:
    """Return the Israel Invoices threshold for a payment date."""
    if payment_date >= date(2026, 6, 1):
        return ISRAEL_INVOICES_THRESHOLD_2026_JUN
    if payment_date >= date(2026, 1, 1):
        return ISRAEL_INVOICES_THRESHOLD_2026_JAN
    return Decimal("20000")


def allocation_warning(record: ReceiptRecord, vat: VatBreakdown) -> str:
    """Return a warning when an allocation number is likely required."""
    if record.exempt_dealer or record.allocation_number:
        return ""
    threshold = allocation_threshold_for(record.payment_date)
    if vat.net > threshold:
        return f"Israel Invoices allocation number likely required for B2B tax invoice above {format_money(threshold)} before VAT."
    return ""


class ReceiptGenerator:
    """Render receipt records to Markdown, HTML, or JSON."""

    def vat_breakdown(self, record: ReceiptRecord) -> VatBreakdown:
        record.validate()
        return split_gross_amount(record.amount, DEFAULT_VAT_RATE, record.exempt_dealer)

    def to_dict(self, record: ReceiptRecord) -> dict[str, Any]:
        vat = self.vat_breakdown(record)
        warning = allocation_warning(record, vat)
        data = {
            "receipt_number": record.receipt_number,
            "business": {
                "name": record.business_name,
                "tax_id": record.business_tax_id.zfill(9),
            },
            "customer": {"name": record.customer_name},
            "payment": {
                "gateway": record.gateway.value,
                "transaction_id": record.transaction_id,
                "approval_number": record.approval_number,
                "date": format_israeli_date(record.payment_date),
                "amount": str(record.amount.quantize(MONEY_QUANT)),
                "currency": record.currency,
                "masked_card": record.masked_card,
                "card_brand": record.card_brand,
            },
            "vat": vat.as_display(),
            "document": {
                "document_number": record.document_number,
                "document_url": record.document_url,
                "allocation_number": record.allocation_number,
            },
            "description": record.description,
            "source_hash": record.source_hash,
            "notes": list(record.notes),
            "warnings": [warning] if warning else [],
        }
        return data

    def render_markdown(self, record: ReceiptRecord) -> str:
        data = self.to_dict(record)
        payment = data["payment"]
        vat = data["vat"]
        doc = data["document"]
        lines = [
            f"# Receipt {data['receipt_number']}",
            "",
            f"Business: {data['business']['name']} ({data['business']['tax_id']})",
            f"Customer: {data['customer']['name']}",
            f"Date: {payment['date']}",
            f"Description: {data['description']}",
            "",
            "## Payment",
            "",
            f"- Gateway: {payment['gateway']}",
            f"- Transaction ID: {payment['transaction_id']}",
            f"- Approval/reference: {payment['approval_number'] or 'Not supplied'}",
            f"- Card: {payment['card_brand'] + ' ' if payment['card_brand'] else ''}{payment['masked_card'] or 'Masked data not supplied'}",
            f"- Gross amount: {vat['gross']}",
            "",
            "## VAT",
            "",
        ]
        if record.exempt_dealer:
            lines.extend([
                "- VAT status: Osek Patur / exempt dealer",
                "- VAT charged: ₪0.00",
                f"- Total paid: {vat['gross']}",
            ])
        else:
            lines.extend([
                f"- Net before VAT: {vat['net']}",
                f"- VAT rate: {vat['vat_rate']}",
                f"- VAT amount: {vat['vat']}",
                f"- Total paid: {vat['gross']}",
            ])
        if doc["document_number"] or doc["document_url"] or doc["allocation_number"]:
            lines.extend(["", "## Document references", ""])
            if doc["document_number"]:
                lines.append(f"- Provider document number: {doc['document_number']}")
            if doc["document_url"]:
                lines.append(f"- Provider document URL: {doc['document_url']}")
            if doc["allocation_number"]:
                lines.append(f"- Israel Invoices allocation number: {doc['allocation_number']}")
        if data["source_hash"]:
            lines.extend(["", f"Source hash: `{data['source_hash']}`"])
        if data["warnings"]:
            lines.extend(["", "## Warnings", ""])
            lines.extend(f"- {warning}" for warning in data["warnings"])
        lines.extend([
            "",
            "Generated from supplied gateway data. Validate against settlement and accounting records before final use.",
        ])
        return "\n".join(lines) + "\n"

    def render_html(self, record: ReceiptRecord) -> str:
        data = self.to_dict(record)
        payment = data["payment"]
        vat = data["vat"]
        warning_html = "".join(f"<li>{html.escape(w)}</li>" for w in data["warnings"])
        vat_rows = (
            f"<tr><th>VAT status</th><td>Osek Patur / exempt dealer</td></tr>"
            f"<tr><th>VAT charged</th><td>₪0.00</td></tr>"
            if record.exempt_dealer
            else f"<tr><th>Net before VAT</th><td>{html.escape(vat['net'])}</td></tr>"
            f"<tr><th>VAT rate</th><td>{html.escape(vat['vat_rate'])}</td></tr>"
            f"<tr><th>VAT amount</th><td>{html.escape(vat['vat'])}</td></tr>"
        )
        return f"""<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><title>Receipt {html.escape(data['receipt_number'])}</title></head>
<body>
<h1>Receipt {html.escape(data['receipt_number'])}</h1>
<table>
<tr><th>Business</th><td>{html.escape(data['business']['name'])} ({html.escape(data['business']['tax_id'])})</td></tr>
<tr><th>Customer</th><td>{html.escape(data['customer']['name'])}</td></tr>
<tr><th>Date</th><td>{html.escape(payment['date'])}</td></tr>
<tr><th>Gateway</th><td>{html.escape(payment['gateway'])}</td></tr>
<tr><th>Transaction ID</th><td>{html.escape(payment['transaction_id'])}</td></tr>
<tr><th>Approval/reference</th><td>{html.escape(payment['approval_number'] or 'Not supplied')}</td></tr>
<tr><th>Card</th><td>{html.escape((payment['card_brand'] + ' ') if payment['card_brand'] else '')}{html.escape(payment['masked_card'] or 'Masked data not supplied')}</td></tr>
{vat_rows}
<tr><th>Total paid</th><td>{html.escape(vat['gross'])}</td></tr>
</table>
{('<h2>Warnings</h2><ul>' + warning_html + '</ul>') if warning_html else ''}
<p>Generated from supplied gateway data. Validate against settlement and accounting records before final use.</p>
</body>
</html>
"""

    def render_json(self, record: ReceiptRecord) -> str:
        return json.dumps(self.to_dict(record), ensure_ascii=False, indent=2, default=str) + "\n"

    def render(self, record: ReceiptRecord, output_format: ReceiptFormat | str = ReceiptFormat.MARKDOWN) -> str:
        output_format = output_format if isinstance(output_format, ReceiptFormat) else ReceiptFormat(str(output_format).lower())
        if output_format == ReceiptFormat.MARKDOWN:
            return self.render_markdown(record)
        if output_format == ReceiptFormat.HTML:
            return self.render_html(record)
        if output_format == ReceiptFormat.JSON:
            return self.render_json(record)
        raise ReceiptValidationError(f"unsupported format: {output_format}")


class CreditCardReceiptClient:
    """Synchronous and asynchronous helper for receipt generation."""

    def __init__(self, generator: Optional[ReceiptGenerator] = None) -> None:
        self.generator = generator or ReceiptGenerator()

    def normalize(self, gateway: Gateway | str, payload: Mapping[str, Any]) -> NormalizedGatewayResult:
        return normalize_gateway_payload(gateway, payload)

    def build_record_from_gateway(
        self,
        gateway: Gateway | str,
        payload: Mapping[str, Any],
        *,
        business_name: str,
        business_tax_id: str,
        customer_name: str = "Customer",
        receipt_number: str = "",
        payment_date: Optional[date] = None,
        exempt_dealer: bool = False,
        allocation_number: str = "",
        description: str = "Card payment",
    ) -> ReceiptRecord:
        result = self.normalize(gateway, payload)
        if not result.success:
            raise ReceiptValidationError("gateway success could not be confirmed")
        if not result.amount:
            raise ReceiptValidationError("amount is required in gateway payload or manual record")
        today = payment_date or datetime.now(timezone.utc).date()
        receipt_number = receipt_number or f"RCPT-{result.gateway.value.upper()}-{result.transaction_id}"
        record = ReceiptRecord(
            gateway=result.gateway,
            business_name=business_name,
            business_tax_id=business_tax_id,
            customer_name=customer_name,
            amount=result.amount,
            currency=result.currency,
            payment_date=today,
            transaction_id=result.transaction_id,
            approval_number=result.approval_number,
            receipt_number=receipt_number,
            masked_card=result.masked_card,
            card_brand=result.card_brand,
            document_number=result.document_number,
            document_url=result.document_url,
            allocation_number=allocation_number,
            source_hash=result.source_hash,
            exempt_dealer=exempt_dealer,
            description=description,
            notes=result.warnings,
        )
        record.validate()
        return record

    def create_receipt(self, record: ReceiptRecord, output_format: ReceiptFormat | str = ReceiptFormat.MARKDOWN) -> str:
        return self.generator.render(record, output_format)

    async def async_create_receipt(self, record: ReceiptRecord, output_format: ReceiptFormat | str = ReceiptFormat.MARKDOWN) -> str:
        return await asyncio.to_thread(self.create_receipt, record, output_format)

    def create_receipt_from_gateway(
        self,
        gateway: Gateway | str,
        payload: Mapping[str, Any],
        *,
        business_name: str,
        business_tax_id: str,
        customer_name: str = "Customer",
        receipt_number: str = "",
        payment_date: Optional[date] = None,
        exempt_dealer: bool = False,
        allocation_number: str = "",
        description: str = "Card payment",
        output_format: ReceiptFormat | str = ReceiptFormat.MARKDOWN,
    ) -> str:
        record = self.build_record_from_gateway(
            gateway,
            payload,
            business_name=business_name,
            business_tax_id=business_tax_id,
            customer_name=customer_name,
            receipt_number=receipt_number,
            payment_date=payment_date,
            exempt_dealer=exempt_dealer,
            allocation_number=allocation_number,
            description=description,
        )
        return self.create_receipt(record, output_format)


def provider_endpoint(gateway: Gateway | str, action: str) -> dict[str, str]:
    gateway_value = Gateway(str(gateway).lower())
    actions = PROVIDER_ENDPOINTS[gateway_value]
    if action not in actions:
        available = ", ".join(sorted(actions))
        raise ReceiptValidationError(f"unknown action {action!r}; available actions: {available}")
    return dict(actions[action])


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ReceiptValidationError("input JSON must be an object")
    return data


def write_text(path: str | Path, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8")


def sample_payload(gateway: Gateway | str = Gateway.CARDCOM) -> dict[str, Any]:
    gateway = gateway if isinstance(gateway, Gateway) else Gateway(str(gateway).lower())
    if gateway == Gateway.MESHULAM:
        gateway = Gateway.GROW
    if gateway == Gateway.CARDCOM:
        return {"ResponseCode": 0, "TranzactionId": "123456", "ApprovalNumber": "ABC123", "Amount": "118.00", "Last4": "1234", "CardBrand": "Visa"}
    if gateway == Gateway.TRANZILA:
        return {"status": "success", "transaction_id": "TZ-789", "confirmation_code": "CONF7", "amount": "118.00", "last4": "1234"}
    if gateway == Gateway.GROW:
        return {"status": "success", "transactionId": "GR-456", "asmachta": "ASM456", "sum": "118.00", "cardSuffix": "1234"}
    if gateway == Gateway.PELECARD:
        return {"StatusCode": "000", "PelecardTransactionId": "PL-321", "VoucherId": "86-001-006", "ShvaResult": "000", "total": "118.00", "CreditCardNumber": "45******1234"}
    raise ReceiptValidationError(f"unsupported gateway: {gateway}")
