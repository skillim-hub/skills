"""Typed helpers for Israeli invoices, receipts, credit notes, and allocation workflows."""

from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Literal, Mapping, Optional, Sequence, Tuple

Currency = Literal["ILS", "USD", "EUR", "GBP"]
DocumentType = Literal["tax_invoice", "receipt", "tax_invoice_receipt", "credit_note"]
IssuerStatus = Literal["morshe", "patur", "company"]
CustomerType = Literal["business", "consumer", "foreign", "nonprofit", "government"]
PaymentMethod = Literal[
    "cash",
    "bank_transfer",
    "credit_card",
    "cheque",
    "bit",
    "paybox",
    "withholding_tax",
    "other",
]
Environment = Literal["sandbox", "production"]

STANDARD_VAT_RATE = Decimal("0.18")
LEGACY_2024_VAT_RATE = Decimal("0.17")
VAT_RATE_CHANGE_2025 = date(2025, 1, 1)
ZERO = Decimal("0.00")
TWO_PLACES = Decimal("0.01")

SHAAM_SANDBOX_BASE_URL = "https://ita-api.taxes.gov.il/shaam/tsandbox"
SHAAM_PRODUCTION_BASE_URL = "https://ita-api.taxes.gov.il/shaam/production"
ALLOCATION_APPROVAL_ENDPOINT = "/Invoices/v2/Approval"
MULTI_ALLOCATION_APPROVAL_ENDPOINT = "/Multi-invoices/v2/MultiApproval"
INVOICE_DECISION_ENDPOINTS: Dict[str, str] = {
    "cancel": "/InvoiceDecisionApi/v1/Cancel",
    "continue": "/InvoiceDecisionApi/v1/Continue",
    "further_objection": "/InvoiceDecisionApi/v1/FurtherObjection",
}

DEFAULT_SHAAM_THRESHOLDS: Dict[str, Decimal] = {
    "2024-05-05": Decimal("25000"),
    "2025-01-01": Decimal("20000"),
    "2026-01-01": Decimal("10000"),
    "2026-06-01": Decimal("5000"),
}

HEBREW_TITLES: Dict[str, str] = {
    "tax_invoice": "חשבונית מס",
    "receipt": "קבלה",
    "tax_invoice_receipt": "חשבונית מס/קבלה",
    "credit_note": "חשבונית זיכוי",
}

HEBREW_STATUS: Dict[str, str] = {
    "morshe": "עוסק מורשה",
    "patur": "עוסק פטור",
    "company": "חברה בע״מ",
}

PAYMENT_LABELS_HE: Dict[str, str] = {
    "cash": "מזומן",
    "bank_transfer": "העברה בנקאית",
    "credit_card": "כרטיס אשראי",
    "cheque": "שיק",
    "bit": "ביט",
    "paybox": "פייבוקס",
    "withholding_tax": "ניכוי מס במקור",
    "other": "אחר",
}


def D(value: Any) -> Decimal:
    """Convert a JSON/Python value to Decimal without binary float artifacts."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    if value is None or value == "":
        return ZERO
    return Decimal(str(value).replace(",", "").strip())


def money(value: Any) -> str:
    """Format a value as a two-decimal money string."""
    return f"{D(value).quantize(TWO_PLACES, rounding=ROUND_HALF_UP):,.2f}"


def parse_date(value: Any) -> date:
    """Parse ISO or Israeli display dates."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not isinstance(value, str):
        raise TypeError(f"Unsupported date value: {value!r}")
    raw = value.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date must be YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY: {value!r}")


def format_date_he(value: Any) -> str:
    """Format a date as DD/MM/YYYY for Hebrew documents."""
    return parse_date(value).strftime("%d/%m/%Y")


def vat_rate_for_date(value: Any) -> Decimal:
    """Return the default standard VAT rate for the supplied date."""
    return STANDARD_VAT_RATE if parse_date(value) >= VAT_RATE_CHANGE_2025 else LEGACY_2024_VAT_RATE


def shaam_threshold_for_date(
    value: Any, thresholds: Optional[Mapping[Any, Decimal]] = None
) -> Decimal:
    """Return the allocation threshold active on the supplied document date."""
    table: Mapping[Any, Decimal] = thresholds or DEFAULT_SHAAM_THRESHOLDS
    doc_date = parse_date(value)

    if all(isinstance(key, int) or str(key).isdigit() for key in table):
        year_table = {int(key): D(value) for key, value in table.items()}
        years = sorted(year_table)
        if doc_date.year in year_table:
            return D(year_table[doc_date.year])
        if doc_date.year < years[0]:
            return Decimal("Infinity")
        return D(year_table[years[-1]])

    effective_rules: List[Tuple[date, Decimal]] = []
    for raw_key, raw_value in table.items():
        effective_rules.append((parse_date(raw_key), D(raw_value)))
    effective_rules.sort(key=lambda item: item[0])

    active = Decimal("Infinity")
    for starts_at, amount in effective_rules:
        if doc_date >= starts_at:
            active = amount
        else:
            break
    return active


def normalize_tax_id(value: Optional[str]) -> str:
    """Return a digits-only Israeli identifier string."""
    if not value:
        return ""
    return "".join(ch for ch in str(value) if ch.isdigit())


def is_nine_digit_tax_id(value: Optional[str]) -> bool:
    """Check the generic 9-digit Israeli tax identifier format."""
    return len(normalize_tax_id(value)) == 9


def is_valid_israeli_id(value: str) -> bool:
    """Validate an Israeli personal ID checksum."""
    digits = normalize_tax_id(value).zfill(9)
    if len(digits) != 9 or not digits.isdigit():
        return False
    total = 0
    for index, char in enumerate(digits):
        multiplier = 1 if index % 2 == 0 else 2
        n = int(char) * multiplier
        total += n if n < 10 else n - 9
    return total % 10 == 0


@dataclass(frozen=True)
class Party:
    """Business, freelancer, consumer, or organization in the transaction."""

    name: str
    tax_id: str = ""
    status: Optional[IssuerStatus] = None
    customer_type: Optional[CustomerType] = None
    address: str = ""
    email: str = ""
    phone: str = ""

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Party":
        return cls(
            name=str(data.get("name", "")).strip(),
            tax_id=normalize_tax_id(data.get("tax_id", data.get("id", ""))),
            status=data.get("status"),
            customer_type=data.get("customer_type", data.get("type")),
            address=str(data.get("address", "")).strip(),
            email=str(data.get("email", "")).strip(),
            phone=str(data.get("phone", "")).strip(),
        )

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"name": self.name}
        if self.tax_id:
            out["tax_id"] = self.tax_id
        if self.status:
            out["status"] = self.status
        if self.customer_type:
            out["customer_type"] = self.customer_type
        if self.address:
            out["address"] = self.address
        if self.email:
            out["email"] = self.email
        if self.phone:
            out["phone"] = self.phone
        return out


@dataclass(frozen=True)
class LineItem:
    """Invoice or credit-note line with fixed and percentage discounts."""

    description: str
    quantity: Decimal = Decimal("1")
    unit: str = "יחידה"
    unit_price: Decimal = ZERO
    discount: Decimal = ZERO
    discount_percent: Decimal = ZERO
    vat_rate: Optional[Decimal] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LineItem":
        return cls(
            description=str(data.get("description", "")).strip(),
            quantity=D(data.get("quantity", 1)),
            unit=str(data.get("unit", "יחידה")),
            unit_price=D(data.get("unit_price", 0)),
            discount=D(data.get("discount", 0)),
            discount_percent=D(data.get("discount_percent", 0)),
            vat_rate=None if data.get("vat_rate") is None else D(data.get("vat_rate")),
        )

    def gross_before_discount(self) -> Decimal:
        return self.quantity * self.unit_price

    def discount_amount(self) -> Decimal:
        percentage_discount = self.gross_before_discount() * (self.discount_percent / Decimal("100"))
        return self.discount + percentage_discount

    def net(self) -> Decimal:
        value = self.gross_before_discount() - self.discount_amount()
        if value < ZERO:
            raise ValueError(f"Line discount exceeds line amount: {self.description}")
        return value

    def effective_vat_rate(self, default_rate: Decimal) -> Decimal:
        return default_rate if self.vat_rate is None else self.vat_rate

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "description": self.description,
            "quantity": str(self.quantity),
            "unit": self.unit,
            "unit_price": money(self.unit_price),
        }
        if self.discount:
            out["discount"] = money(self.discount)
        if self.discount_percent:
            out["discount_percent"] = str(self.discount_percent)
        if self.vat_rate is not None:
            out["vat_rate"] = str(self.vat_rate)
        return out


@dataclass(frozen=True)
class Payment:
    """Receipt payment detail."""

    method: PaymentMethod
    amount: Decimal
    reference: str = ""
    paid_at: Optional[date] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Payment":
        paid_at = data.get("paid_at") or data.get("date")
        return cls(
            method=data.get("method", "other"),
            amount=D(data.get("amount", 0)),
            reference=str(data.get("reference", "")),
            paid_at=parse_date(paid_at) if paid_at else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"method": self.method, "amount": money(self.amount)}
        if self.reference:
            out["reference"] = self.reference
        if self.paid_at:
            out["paid_at"] = self.paid_at.isoformat()
        return out


@dataclass(frozen=True)
class Totals:
    """Calculated subtotal, VAT, and final total."""

    subtotal: Decimal
    vat: Decimal
    total: Decimal
    sign: int = 1

    def to_dict(self) -> Dict[str, str]:
        return {"subtotal": money(self.subtotal), "vat": money(self.vat), "total": money(self.total)}


@dataclass
class ValidationResult:
    """Validation errors and warnings."""

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def raise_for_errors(self) -> None:
        if self.errors:
            raise ValueError("; ".join(self.errors))

    def to_dict(self) -> Dict[str, Any]:
        return {"ok": self.ok, "errors": self.errors, "warnings": self.warnings}


@dataclass
class DocumentSpec:
    """Structured document specification for drafting and validation."""

    document_type: DocumentType
    document_number: str
    issue_date: date
    issuer: Party
    customer: Party
    lines: List[LineItem]
    currency: Currency = "ILS"
    payments: List[Payment] = field(default_factory=list)
    vat_rate: Optional[Decimal] = None
    allocation_number: str = ""
    original_document_number: str = ""
    original_allocation_number: str = ""
    credit_reason: str = ""
    notes: str = ""
    zero_rate_basis: str = ""
    thresholds: Dict[Any, Decimal] = field(default_factory=lambda: dict(DEFAULT_SHAAM_THRESHOLDS))

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DocumentSpec":
        return cls(
            document_type=data.get("document_type", "tax_invoice"),
            document_number=str(data.get("document_number", "")).strip(),
            issue_date=parse_date(data.get("issue_date", date.today().isoformat())),
            issuer=Party.from_dict(data.get("issuer", {})),
            customer=Party.from_dict(data.get("customer", {})),
            lines=[LineItem.from_dict(item) for item in data.get("lines", [])],
            currency=data.get("currency", "ILS"),
            payments=[Payment.from_dict(item) for item in data.get("payments", [])],
            vat_rate=None if data.get("vat_rate") is None else D(data.get("vat_rate")),
            allocation_number=str(data.get("allocation_number", "")),
            original_document_number=str(data.get("original_document_number", "")),
            original_allocation_number=str(data.get("original_allocation_number", "")),
            credit_reason=str(data.get("credit_reason", "")),
            notes=str(data.get("notes", "")),
            zero_rate_basis=str(data.get("zero_rate_basis", "")),
            thresholds={k: D(v) for k, v in data.get("thresholds", DEFAULT_SHAAM_THRESHOLDS).items()},
        )

    def default_vat_rate(self) -> Decimal:
        if self.vat_rate is not None:
            return self.vat_rate
        if self.issuer.status == "patur" or self.document_type == "receipt":
            return ZERO
        return vat_rate_for_date(self.issue_date)

    def sign(self) -> int:
        return -1 if self.document_type == "credit_note" else 1

    def calculate_totals(self) -> Totals:
        default_rate = self.default_vat_rate()
        subtotal = ZERO
        vat = ZERO
        for line in self.lines:
            net = line.net()
            line_rate = ZERO if self.document_type == "receipt" else line.effective_vat_rate(default_rate)
            subtotal += net
            vat += net * line_rate
        sign = self.sign()
        subtotal = (subtotal * sign).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        vat = (vat * sign).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        total = (subtotal + vat).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        return Totals(subtotal=subtotal, vat=vat, total=total, sign=sign)

    def amount_before_vat_abs(self) -> Decimal:
        return abs(self.calculate_totals().subtotal)

    def has_nonzero_vat_component(self) -> bool:
        return abs(self.calculate_totals().vat) > ZERO

    def requires_allocation(self) -> bool:
        if self.document_type not in ("tax_invoice", "tax_invoice_receipt"):
            return False
        if self.issuer.status not in ("morshe", "company"):
            return False
        if self.customer.customer_type != "business":
            return False
        if not self.has_nonzero_vat_component():
            return False
        threshold = shaam_threshold_for_date(self.issue_date, self.thresholds)
        return self.amount_before_vat_abs() > threshold

    def validate(self) -> ValidationResult:
        result = ValidationResult()
        if self.document_type not in HEBREW_TITLES:
            result.errors.append(f"Unsupported document_type: {self.document_type}")
        if not self.document_number:
            result.errors.append("document_number is required")
        if not self.issuer.name:
            result.errors.append("issuer.name is required")
        if self.issuer.status not in ("morshe", "patur", "company"):
            result.errors.append("issuer.status must be morshe, patur, or company")
        if self.issuer.tax_id and not is_nine_digit_tax_id(self.issuer.tax_id):
            result.errors.append("issuer.tax_id must contain 9 digits")
        if not self.customer.name:
            result.errors.append("customer.name is required")
        if self.customer.tax_id and not is_nine_digit_tax_id(self.customer.tax_id):
            result.errors.append("customer.tax_id must contain 9 digits")
        if not self.lines and self.document_type != "receipt":
            result.errors.append("at least one line item is required")
        for index, line in enumerate(self.lines, start=1):
            if not line.description:
                result.errors.append(f"line {index}: description is required")
            if line.quantity <= ZERO:
                result.errors.append(f"line {index}: quantity must be positive")
            if line.unit_price < ZERO:
                result.errors.append(f"line {index}: unit_price cannot be negative")
            if line.discount < ZERO or line.discount_percent < ZERO:
                result.errors.append(f"line {index}: discount cannot be negative")
            try:
                line.net()
            except ValueError as exc:
                result.errors.append(str(exc))
        if self.issuer.status == "patur" and self.document_type in ("tax_invoice", "tax_invoice_receipt"):
            result.errors.append("osek patur cannot issue חשבונית מס or חשבונית מס/קבלה")
        if self.document_type in ("receipt", "tax_invoice_receipt") and not self.payments:
            result.errors.append("payment details are required for receipt documents")
        if self.document_type == "credit_note":
            if not self.original_document_number:
                result.errors.append("credit_note requires original_document_number")
            if not self.credit_reason:
                result.warnings.append("credit_note should include credit_reason")
        if self.requires_allocation() and not self.customer.tax_id:
            result.warnings.append("customer.tax_id is needed for an official allocation-number request")
        if self.requires_allocation() and not self.allocation_number:
            result.warnings.append("SHAAM allocation number is required before final B2B tax-invoice issuance")
        if self.zero_rate_basis:
            all_zero = all(
                line.effective_vat_rate(self.default_vat_rate()) == ZERO for line in self.lines
            )
            if not all_zero:
                result.warnings.append("zero_rate_basis is present but at least one line has non-zero VAT")
        if self.currency != "ILS" and "exchange" not in self.notes.lower() and "שער" not in self.notes:
            result.warnings.append("foreign-currency documents should include an exchange-rate note")
        return result

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "document_type": self.document_type,
            "document_number": self.document_number,
            "issue_date": self.issue_date.isoformat(),
            "issuer": self.issuer.to_dict(),
            "customer": self.customer.to_dict(),
            "currency": self.currency,
            "lines": [line.to_dict() for line in self.lines],
        }
        if self.payments:
            out["payments"] = [payment.to_dict() for payment in self.payments]
        if self.vat_rate is not None:
            out["vat_rate"] = str(self.vat_rate)
        for key in (
            "allocation_number",
            "original_document_number",
            "original_allocation_number",
            "credit_reason",
            "notes",
            "zero_rate_basis",
        ):
            value = getattr(self, key)
            if value:
                out[key] = value
        return out

    def to_shaam_payload(self) -> Dict[str, Any]:
        totals = self.calculate_totals()
        return {
            "document": {
                "type": self.document_type,
                "number": self.document_number,
                "issue_date": self.issue_date.isoformat(),
                "currency": self.currency,
            },
            "issuer": self.issuer.to_dict(),
            "customer": self.customer.to_dict(),
            "totals": {
                "amount_before_vat": money(totals.subtotal),
                "vat_rate_default": str(self.default_vat_rate()),
                "vat": money(totals.vat),
                "total": money(totals.total),
            },
            "allocation": {
                "required": self.requires_allocation(),
                "threshold": money(shaam_threshold_for_date(self.issue_date, self.thresholds)),
                "allocation_number": self.allocation_number,
            },
            "lines": [
                {
                    "description": line.description,
                    "quantity": str(line.quantity),
                    "unit": line.unit,
                    "unit_price": money(line.unit_price),
                    "net": money(line.net() * self.sign()),
                    "vat_rate": str(
                        ZERO
                        if self.document_type == "receipt"
                        else line.effective_vat_rate(self.default_vat_rate())
                    ),
                }
                for line in self.lines
            ],
        }


def render_hebrew_markdown(spec: DocumentSpec) -> str:
    """Render a Hebrew markdown draft for review before official issuance."""
    validation = spec.validate()
    totals = spec.calculate_totals()
    title = HEBREW_TITLES.get(spec.document_type, spec.document_type)
    status = HEBREW_STATUS.get(str(spec.issuer.status), str(spec.issuer.status))
    currency_symbol = "₪" if spec.currency == "ILS" else spec.currency

    lines: List[str] = []
    lines.append(f"# {title} {spec.document_number}")
    lines.append("")
    lines.append(f"**תאריך:** {format_date_he(spec.issue_date)}")
    lines.append(f"**מנפיק:** {spec.issuer.name} | {status} {spec.issuer.tax_id}".rstrip())
    if spec.issuer.address:
        lines.append(f"**כתובת מנפיק:** {spec.issuer.address}")
    customer_suffix = f" | מספר: {spec.customer.tax_id}" if spec.customer.tax_id else ""
    lines.append(f"**לקוח:** {spec.customer.name}{customer_suffix}")
    if spec.customer.address:
        lines.append(f"**כתובת לקוח:** {spec.customer.address}")
    if spec.allocation_number:
        lines.append(f"**מספר הקצאה:** {spec.allocation_number}")
    if spec.original_document_number:
        lines.append(f"**מסמך מקור:** {spec.original_document_number}")
    if spec.original_allocation_number:
        lines.append(f"**מספר הקצאה מקורי:** {spec.original_allocation_number}")
    lines.append("")

    if spec.lines:
        lines.append("| תיאור | כמות | יחידה | מחיר יחידה | הנחה | סה״כ לפני מע״מ |")
        lines.append("|---|---:|---|---:|---:|---:|")
        for item in spec.lines:
            discount = item.discount_amount()
            net = item.net() * spec.sign()
            lines.append(
                f"| {item.description} | {item.quantity} | {item.unit} | "
                f"{currency_symbol}{money(item.unit_price)} | {currency_symbol}{money(discount)} | "
                f"{currency_symbol}{money(net)} |"
            )
        lines.append("")

    lines.append(f"**סה״כ לפני מע״מ:** {currency_symbol}{money(totals.subtotal)}")
    lines.append(f"**מע״מ:** {currency_symbol}{money(totals.vat)}")
    lines.append(f"**סה״כ:** {currency_symbol}{money(totals.total)}")

    if spec.payments:
        lines.append("")
        lines.append("## פרטי תשלום")
        for payment in spec.payments:
            paid_at = f", תאריך {format_date_he(payment.paid_at)}" if payment.paid_at else ""
            ref = f", אסמכתה {payment.reference}" if payment.reference else ""
            label = PAYMENT_LABELS_HE.get(str(payment.method), str(payment.method))
            lines.append(f"- {label}: {currency_symbol}{money(payment.amount)}{paid_at}{ref}")

    if spec.credit_reason:
        lines.append("")
        lines.append(f"**סיבת הזיכוי:** {spec.credit_reason}")
    if spec.zero_rate_basis:
        lines.append("")
        lines.append(f"**בסיס לשיעור אפס:** {spec.zero_rate_basis}")
    if spec.notes:
        lines.append("")
        lines.append("## הערות")
        lines.append(spec.notes)

    if validation.warnings:
        lines.append("")
        lines.append("## אזהרות לבדיקה")
        for warning in validation.warnings:
            lines.append(f"- {warning}")
    if validation.errors:
        lines.append("")
        lines.append("## שגיאות לפני הפקה")
        for error in validation.errors:
            lines.append(f"- {error}")

    lines.append("")
    return "\n".join(lines)


@dataclass(frozen=True)
class CreatedDocument:
    """Stored document identifier and source document."""

    id: str
    environment: Environment
    document: DocumentSpec
    path: Path

    def to_response(self) -> Dict[str, Any]:
        totals = self.document.calculate_totals().to_dict()
        return {
            "id": self.id,
            "environment": self.environment,
            "document_type": self.document.document_type,
            "document_number": self.document.document_number,
            "totals": totals,
            "allocation_required": self.document.requires_allocation(),
            "stored_at": str(self.path),
        }


class DocumentStore:
    """Simple local JSON store used by the CLI examples."""

    def __init__(self, root: str | Path = ".invoice-generator-store") -> None:
        self.root = Path(root)

    def environment_dir(self, environment: Environment) -> Path:
        directory = self.root / environment
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def build_id(self, spec: DocumentSpec) -> str:
        raw = json.dumps(spec.to_dict(), ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def create(self, spec: DocumentSpec, environment: Environment = "sandbox") -> CreatedDocument:
        validation = spec.validate()
        validation.raise_for_errors()
        document_id = self.build_id(spec)
        path = self.environment_dir(environment) / f"{document_id}.json"
        write_json(spec.to_dict(), path)
        return CreatedDocument(id=document_id, environment=environment, document=spec, path=path)

    def load(self, document_id: str, environment: Environment = "sandbox") -> DocumentSpec:
        path = self.environment_dir(environment) / f"{document_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Document id not found in {environment}: {document_id}")
        return load_spec(path)

    def resolve(self, source: str | Path, environment: Environment = "sandbox") -> DocumentSpec:
        candidate = Path(str(source))
        if candidate.exists():
            return load_spec(candidate)
        return self.load(str(source), environment)


class ShaamClient:
    """Small sync and async client for allocation-number requests."""

    def __init__(self, base_url: str, access_token: str, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.timeout = timeout

    def headers(self, idempotency_key: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
        }

    def idempotency_key(self, spec: DocumentSpec) -> str:
        return f"{spec.issuer.tax_id}:{spec.document_type}:{spec.document_number}:{spec.issue_date.isoformat()}"

    def request_allocation(
        self, spec: DocumentSpec, endpoint: str = ALLOCATION_APPROVAL_ENDPOINT
    ) -> Dict[str, Any]:
        """Submit an allocation request synchronously using requests.

        The helper sends the package semantic payload. Map it to the exact official schema in a production adapter before calling the Israel Tax Authority endpoint directly.
        """
        import requests

        validation = spec.validate()
        validation.raise_for_errors()
        response = requests.post(
            f"{self.base_url}{endpoint}",
            headers=self.headers(self.idempotency_key(spec)),
            json=spec.to_shaam_payload(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    async def request_allocation_async(
        self, spec: DocumentSpec, endpoint: str = ALLOCATION_APPROVAL_ENDPOINT
    ) -> Dict[str, Any]:
        """Submit an allocation request asynchronously using httpx.

        The helper sends the package semantic payload. Map it to the exact official schema in a production adapter before calling the Israel Tax Authority endpoint directly.
        """
        import httpx

        validation = spec.validate()
        validation.raise_for_errors()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers(self.idempotency_key(spec)),
                json=spec.to_shaam_payload(),
            )
            response.raise_for_status()
            return response.json()


def load_spec(path: str | Path) -> DocumentSpec:
    with open(path, "r", encoding="utf-8") as handle:
        return DocumentSpec.from_dict(json.load(handle))


def write_json(data: Mapping[str, Any], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sample_tax_invoice() -> Dict[str, Any]:
    return {
        "document_type": "tax_invoice",
        "document_number": "INV-2026-0042",
        "issue_date": "15/06/2026",
        "issuer": {
            "name": "יעל כהן ייעוץ",
            "tax_id": "123456789",
            "status": "morshe",
            "address": "רחוב הרצל 10, תל אביב",
            "email": "yael@example.co.il",
        },
        "customer": {
            "name": "חברת לקוח בע\"מ",
            "tax_id": "515555555",
            "customer_type": "business",
            "address": "דרך מנחם בגין 99, תל אביב",
        },
        "currency": "ILS",
        "lines": [
            {"description": "ייעוץ אסטרטגי", "quantity": "40", "unit": "שעה", "unit_price": "450.00"}
        ],
        "notes": "תנאי תשלום: שוטף + 30. הצג מספר הקצאה במסמך הסופי כאשר נדרש.",
    }


def sample_tax_invoice_receipt() -> Dict[str, Any]:
    data = sample_tax_invoice()
    data["document_type"] = "tax_invoice_receipt"
    data["document_number"] = "TIR-2026-0042"
    data["payments"] = [
        {"method": "bank_transfer", "amount": "21240.00", "reference": "TRX-9911", "paid_at": "15/06/2026"}
    ]
    return data


def sample_receipt_patur() -> Dict[str, Any]:
    return {
        "document_type": "receipt",
        "document_number": "REC-2026-0011",
        "issue_date": "12/03/2026",
        "issuer": {"name": "דני לוי תיקונים", "tax_id": "012345674", "status": "patur"},
        "customer": {"name": "לקוח פרטי", "customer_type": "consumer"},
        "currency": "ILS",
        "lines": [
            {"description": "תיקון בבית לקוח", "quantity": "1", "unit": "ביקור", "unit_price": "850.00"}
        ],
        "payments": [
            {"method": "bit", "amount": "850.00", "reference": "BIT-7781", "paid_at": "12/03/2026"}
        ],
    }


def sample_credit_note() -> Dict[str, Any]:
    return {
        "document_type": "credit_note",
        "document_number": "CN-2026-0007",
        "issue_date": "20/06/2026",
        "issuer": {"name": "יעל כהן ייעוץ", "tax_id": "123456789", "status": "morshe"},
        "customer": {"name": "חברת לקוח בע\"מ", "tax_id": "515555555", "customer_type": "business"},
        "currency": "ILS",
        "original_document_number": "INV-2026-0042",
        "original_allocation_number": "123456789012345",
        "credit_reason": "הנחה בדיעבד עקב חיוב יתר",
        "lines": [
            {"description": "זיכוי בגין חיוב יתר", "quantity": "1", "unit": "זיכוי", "unit_price": "500.00"}
        ],
    }


def sample_export_zero_rate() -> Dict[str, Any]:
    return {
        "document_type": "tax_invoice",
        "document_number": "EXP-2026-0020",
        "issue_date": "01/07/2026",
        "issuer": {"name": "סטודיו גליל", "tax_id": "123456789", "status": "morshe"},
        "customer": {"name": "Foreign Client Ltd", "customer_type": "foreign"},
        "currency": "USD",
        "vat_rate": "0",
        "zero_rate_basis": "יצוא שירות לתושב חוץ, בכפוף לבדיקת הזכאות לשיעור אפס",
        "lines": [
            {"description": "עיצוב ממשק", "quantity": "1", "unit": "פרויקט", "unit_price": "3000.00"}
        ],
        "notes": "שער המרה לפי שער יציג ביום 01/07/2026.",
    }


SAMPLES: Dict[str, Any] = {
    "tax-invoice": sample_tax_invoice,
    "tax-invoice-receipt": sample_tax_invoice_receipt,
    "receipt": sample_receipt_patur,
    "credit-note": sample_credit_note,
    "export-zero-rate": sample_export_zero_rate,
}


async def request_allocation_with_client(client: ShaamClient, spec: DocumentSpec) -> Dict[str, Any]:
    """Convenience coroutine for async integrations."""
    return await client.request_allocation_async(spec)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Small argparse entry point for the client helper."""
    import argparse

    parser = argparse.ArgumentParser(description="Render or inspect an Israeli document specification")
    parser.add_argument("input", nargs="?", help="JSON document spec")
    parser.add_argument("--sample", choices=sorted(SAMPLES), help="print a sample JSON spec")
    parser.add_argument("--shaam-payload", action="store_true", help="print semantic allocation payload")
    args = parser.parse_args(argv)

    if args.sample:
        print(json.dumps(SAMPLES[args.sample](), ensure_ascii=False, indent=2))
        return 0
    if not args.input:
        parser.error("input is required unless --sample is used")
    spec = load_spec(args.input)
    if args.shaam_payload:
        print(json.dumps(spec.to_shaam_payload(), ensure_ascii=False, indent=2))
    else:
        print(render_hebrew_markdown(spec))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
