"""Core calculations for multi-line Israeli invoice aggregation."""
from __future__ import annotations

import asyncio, csv, json
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_DOWN, ROUND_HALF_UP, ROUND_UP, localcontext
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

ILS = "ILS"
AGOROT = Decimal("0.01")
DEFAULT_VAT_RATE = Decimal("0.18")  # Web-validated standard VAT rate as of 2026-06-02.

class AggregatorError(ValueError):
    """Base validation or calculation error."""

class MoneyFormatError(AggregatorError):
    """Raised when a money, quantity, or percent value cannot be parsed."""

class RoundingMode(str, Enum):
    HALF_UP = "half_up"
    DOWN = "down"
    UP = "up"

class DiscountType(str, Enum):
    AMOUNT = "amount"
    PERCENT = "percent"

class DiscountAllocationMethod(str, Enum):
    BY_NET = "by_net"
    BY_GROSS = "by_gross"
    EQUAL = "equal"

@dataclass(frozen=True)
class Discount:
    """A fixed amount or percentage discount."""
    type: DiscountType
    value: Decimal
    reason: str = ""

    @staticmethod
    def amount(value: str | Decimal | int | float, reason: str = "") -> "Discount":
        """Create a fixed-amount discount."""
        return Discount(DiscountType.AMOUNT, parse_decimal(value), reason)

    @staticmethod
    def percent(value: str | Decimal | int | float, reason: str = "") -> "Discount":
        """Create a percentage discount."""
        return Discount(DiscountType.PERCENT, parse_decimal(value), reason)

@dataclass(frozen=True)
class InvoiceLine:
    """Input line before calculation."""
    sku: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    vat_rate: Decimal = DEFAULT_VAT_RATE
    line_discount: Discount | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_mapping(data: Mapping[str, Any]) -> "InvoiceLine":
        """Create an invoice line from a mapping."""
        discount = None
        if data.get("discount_type") or data.get("discount_value") not in (None, ""):
            dtype = DiscountType(str(data.get("discount_type", "amount")).strip().lower())
            discount = Discount(dtype, parse_decimal(data.get("discount_value", "0")), str(data.get("discount_reason", "")))
        return InvoiceLine(
            sku=str(data.get("sku", "")),
            description=str(data.get("description", "")),
            quantity=parse_decimal(data.get("quantity", "1")),
            unit_price=parse_decimal(data.get("unit_price", "0")),
            vat_rate=normalize_rate(data.get("vat_rate", DEFAULT_VAT_RATE)),
            line_discount=discount,
            metadata={k:v for k,v in data.items() if k not in {"sku","description","quantity","unit_price","vat_rate","discount_type","discount_value","discount_reason"}},
        )

@dataclass(frozen=True)
class CalculatedLine:
    """Calculated line with exact and rounded values."""
    sku: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    vat_rate: Decimal
    gross_before_discount: Decimal
    line_discount_amount: Decimal
    invoice_discount_share: Decimal
    taxable_base: Decimal
    vat_amount_exact: Decimal
    vat_amount: Decimal
    total_with_vat_exact: Decimal
    total_with_vat: Decimal
    fractional_agorot_vat: Decimal
    fractional_agorot_total: Decimal
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class InvoiceTotals:
    """Invoice totals with exact and rounded values."""
    currency: str
    subtotal_before_discounts: Decimal
    line_discounts_total: Decimal
    invoice_discount_total: Decimal
    taxable_total: Decimal
    vat_total_exact: Decimal
    vat_total: Decimal
    grand_total_exact: Decimal
    grand_total: Decimal
    fractional_agorot_vat_total: Decimal
    fractional_agorot_grand_total: Decimal
    rounding_adjustment: Decimal

@dataclass(frozen=True)
class InvoiceResult:
    """Full calculation result."""
    invoice_id: str
    invoice_date: str
    vat_number: str
    currency: str
    environment: str
    lines: list[CalculatedLine]
    totals: InvoiceTotals
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary."""
        def convert(value: Any) -> Any:
            if isinstance(value, Decimal): return format(value, "f")
            if isinstance(value, Enum): return value.value
            if isinstance(value, list): return [convert(v) for v in value]
            if isinstance(value, dict): return {k: convert(v) for k,v in value.items()}
            if hasattr(value, "__dataclass_fields__"): return {k: convert(v) for k,v in asdict(value).items()}
            return value
        return convert(asdict(self))

    def to_json(self, indent: int = 2) -> str:
        """Return JSON with Hebrew-safe encoding."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

@dataclass(frozen=True)
class CalculationOptions:
    """Calculation controls."""
    currency: str = ILS
    vat_rounding: RoundingMode = RoundingMode.HALF_UP
    total_rounding: RoundingMode = RoundingMode.HALF_UP
    invoice_discount_allocation: DiscountAllocationMethod = DiscountAllocationMethod.BY_NET
    allow_negative_lines: bool = False
    allow_zero_quantity: bool = False
    max_fractional_agorot_warning: Decimal = Decimal("0.10")
    environment: str = "sandbox"

def parse_decimal(value: Any) -> Decimal:
    """Parse a Decimal from money, percentage, integer, float, or string."""
    if isinstance(value, Decimal): return value
    if isinstance(value, int): return Decimal(value)
    if isinstance(value, float): return Decimal(str(value))
    if value is None: raise MoneyFormatError("Missing numeric value")
    text=str(value).strip().replace("₪","").replace("ILS","").replace(",","").replace("%","")
    if text=="": raise MoneyFormatError("Empty numeric value")
    try: return Decimal(text)
    except InvalidOperation as exc: raise MoneyFormatError(f"Invalid numeric value: {value!r}") from exc

def normalize_rate(value: Any) -> Decimal:
    """Normalize VAT rate. Accept 0.18, 18, 18%, and 0%."""
    if isinstance(value, str) and value.strip().endswith("%"): parsed=parse_decimal(value)/Decimal("100")
    else:
        parsed=parse_decimal(value)
        if parsed > 1: parsed = parsed / Decimal("100")
    if parsed < 0: raise AggregatorError("VAT rate cannot be negative")
    return parsed

def round_money(value: Decimal, mode: RoundingMode = RoundingMode.HALF_UP) -> Decimal:
    """Round a Decimal to one agorah."""
    rounding = ROUND_HALF_UP if mode == RoundingMode.HALF_UP else ROUND_DOWN if mode == RoundingMode.DOWN else ROUND_UP if mode == RoundingMode.UP else None
    if rounding is None: raise AggregatorError(f"Unsupported rounding mode: {mode}")
    return value.quantize(AGOROT, rounding=rounding)

def calculate_discount_amount(base_amount: Decimal, discount: Discount | None) -> Decimal:
    """Calculate discount amount from base amount."""
    if discount is None: return Decimal("0")
    if discount.value < 0: raise AggregatorError("Discount cannot be negative")
    if discount.type == DiscountType.PERCENT:
        if discount.value > 100: raise AggregatorError("Percent discount cannot exceed 100")
        return base_amount * discount.value / Decimal("100")
    if discount.type == DiscountType.AMOUNT:
        if discount.value > base_amount: raise AggregatorError("Fixed discount cannot exceed line amount")
        return discount.value
    raise AggregatorError(f"Unsupported discount type: {discount.type}")

def allocate_discount(amounts: Sequence[Decimal], total_discount: Decimal, method: DiscountAllocationMethod = DiscountAllocationMethod.BY_NET) -> list[Decimal]:
    """Allocate invoice-level discount and reconcile agorot deltas."""
    if total_discount < 0: raise AggregatorError("Invoice discount cannot be negative")
    if not amounts: return []
    if total_discount == 0: return [Decimal("0") for _ in amounts]
    positive_total=sum((a for a in amounts if a > 0), Decimal("0"))
    if method != DiscountAllocationMethod.EQUAL and positive_total <= 0: raise AggregatorError("Cannot allocate discount without positive basis amounts")
    if method != DiscountAllocationMethod.EQUAL and total_discount > positive_total: raise AggregatorError("Invoice discount cannot exceed allocation basis")
    with localcontext() as ctx:
        ctx.prec=28
        if method == DiscountAllocationMethod.EQUAL: raw=[total_discount/Decimal(len(amounts)) for _ in amounts]
        elif method in (DiscountAllocationMethod.BY_NET, DiscountAllocationMethod.BY_GROSS): raw=[(a/positive_total*total_discount) if a>0 else Decimal("0") for a in amounts]
        else: raise AggregatorError(f"Unsupported allocation method: {method}")
        rounded=[round_money(v) for v in raw]
        delta=round_money(total_discount)-sum(rounded, Decimal("0"))
        if delta != 0:
            cents=int((delta/AGOROT).to_integral_value())
            order=sorted(range(len(amounts)), key=lambda i:(raw[i]-rounded[i], amounts[i]), reverse=(cents>0))
            for i in order[:abs(cents)]: rounded[i] += AGOROT if cents > 0 else -AGOROT
        return rounded

def validate_lines(lines: Sequence[InvoiceLine], options: CalculationOptions) -> None:
    """Validate invoice lines."""
    if not lines: raise AggregatorError("At least one invoice line is required")
    if options.environment not in {"sandbox", "production"}: raise AggregatorError("Environment must be sandbox or production")
    for line in lines:
        label=line.sku or line.description
        if not options.allow_zero_quantity and line.quantity == 0: raise AggregatorError(f"Line {label!r} has zero quantity")
        if line.quantity < 0 and not options.allow_negative_lines: raise AggregatorError(f"Line {label!r} has negative quantity")
        if line.unit_price < 0 and not options.allow_negative_lines: raise AggregatorError(f"Line {label!r} has negative unit price")
        if line.vat_rate < 0: raise AggregatorError(f"Line {label!r} has negative VAT rate")

def aggregate_invoice(lines: Sequence[InvoiceLine | Mapping[str, Any]], *, invoice_id: str = "", invoice_date: str = "", vat_number: str = "", invoice_discount: Discount | None = None, options: CalculationOptions | None = None) -> InvoiceResult:
    """Aggregate an invoice and return line-level and total results."""
    options = options or CalculationOptions()
    normalized=[line if isinstance(line, InvoiceLine) else InvoiceLine.from_mapping(line) for line in lines]
    validate_lines(normalized, options)
    pre_net=[]; gross_values=[]; line_discount_values=[]
    for line in normalized:
        gross=line.quantity*line.unit_price
        disc=calculate_discount_amount(gross, line.line_discount)
        taxable_pre=gross-disc
        if taxable_pre < 0 and not options.allow_negative_lines: raise AggregatorError(f"Line {line.sku or line.description!r} taxable base is negative")
        gross_values.append(gross); line_discount_values.append(disc); pre_net.append(taxable_pre)
    invoice_discount_amount=calculate_discount_amount(sum(pre_net, Decimal("0")), invoice_discount)
    shares=allocate_discount(pre_net, invoice_discount_amount, options.invoice_discount_allocation)
    calculated=[]; warnings=[]
    for line,gross,disc,share in zip(normalized,gross_values,line_discount_values,shares):
        taxable=gross-disc-share
        if taxable < 0 and not options.allow_negative_lines: raise AggregatorError(f"Line {line.sku or line.description!r} taxable base is negative after invoice discount")
        vat_exact=taxable*line.vat_rate
        vat_rounded=round_money(vat_exact, options.vat_rounding)
        total_exact=taxable+vat_exact
        total_rounded=round_money(taxable+vat_rounded, options.total_rounding)
        calculated.append(CalculatedLine(line.sku,line.description,line.quantity,line.unit_price,line.vat_rate,gross,round_money(disc),share,round_money(taxable),vat_exact,vat_rounded,total_exact,total_rounded,vat_exact-vat_rounded,total_exact-total_rounded,dict(line.metadata)))
    subtotal=sum(gross_values, Decimal("0")); line_disc_total=sum(line_discount_values, Decimal("0"))
    taxable_total_exact=sum((ln.gross_before_discount-ln.line_discount_amount-ln.invoice_discount_share for ln in calculated), Decimal("0"))
    vat_total_exact=sum((ln.vat_amount_exact for ln in calculated), Decimal("0")); vat_total=sum((ln.vat_amount for ln in calculated), Decimal("0"))
    grand_total_exact=taxable_total_exact+vat_total_exact; grand_total=sum((ln.total_with_vat for ln in calculated), Decimal("0"))
    rounding_adjustment=grand_total-round_money(taxable_total_exact+vat_total, options.total_rounding)
    frac_vat=vat_total_exact-vat_total; frac_grand=grand_total_exact-grand_total
    if abs(frac_vat)>options.max_fractional_agorot_warning: warnings.append("VAT fractional agorot accumulation exceeds configured warning threshold")
    if abs(frac_grand)>options.max_fractional_agorot_warning: warnings.append("Grand total fractional agorot accumulation exceeds configured warning threshold")
    totals=InvoiceTotals(options.currency, round_money(subtotal), round_money(line_disc_total), round_money(invoice_discount_amount), round_money(taxable_total_exact), vat_total_exact, vat_total, grand_total_exact, grand_total, frac_vat, frac_grand, rounding_adjustment)
    return InvoiceResult(invoice_id, invoice_date, vat_number, options.currency, options.environment, calculated, totals, warnings)

async def aggregate_invoice_async(lines: Sequence[InvoiceLine | Mapping[str, Any]], *, invoice_id: str = "", invoice_date: str = "", vat_number: str = "", invoice_discount: Discount | None = None, options: CalculationOptions | None = None) -> InvoiceResult:
    """Async wrapper for event-loop based applications."""
    await asyncio.sleep(0)
    return aggregate_invoice(lines, invoice_id=invoice_id, invoice_date=invoice_date, vat_number=vat_number, invoice_discount=invoice_discount, options=options)

def load_lines_from_json(path: str | Path) -> list[InvoiceLine]:
    """Load invoice lines from JSON."""
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict): data=data.get("lines", [])
    if not isinstance(data, list): raise AggregatorError("JSON input must be a list or an object with a 'lines' array")
    return [InvoiceLine.from_mapping(item) for item in data]

def load_lines_from_csv(path: str | Path) -> list[InvoiceLine]:
    """Load invoice lines from CSV."""
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return [InvoiceLine.from_mapping(row) for row in csv.DictReader(handle)]

def save_result_json(result: InvoiceResult, path: str | Path) -> None:
    """Save result JSON."""
    Path(path).write_text(result.to_json()+"\n", encoding="utf-8")

def format_summary(result: InvoiceResult) -> str:
    """Format a CLI summary."""
    t=result.totals
    lines=[f"Invoice: {result.invoice_id or '-'}", f"Date: {result.invoice_date or '-'}", f"VAT number: {result.vat_number or '-'}", f"Environment: {result.environment}", f"Currency: {t.currency}", f"Subtotal before discounts: {t.subtotal_before_discounts}", f"Line discounts: {t.line_discounts_total}", f"Invoice discount: {t.invoice_discount_total}", f"Taxable total: {t.taxable_total}", f"VAT total: {t.vat_total}", f"Grand total: {t.grand_total}", f"Rounding adjustment: {t.rounding_adjustment}"]
    if result.warnings: lines += ["Warnings:"] + [f"- {w}" for w in result.warnings]
    return "\n".join(lines)

def parse_discount(discount_type: str | None, discount_value: str | None) -> Discount | None:
    """Parse optional discount fields."""
    if not discount_type and not discount_value: return None
    return Discount(DiscountType((discount_type or "amount").lower()), parse_decimal(discount_value or "0"))

def create_sample_invoice(path: str | Path, *, environment: str = "sandbox") -> dict[str, str]:
    """Create a sample invoice and return a creation response."""
    if environment not in {"sandbox", "production"}: raise AggregatorError("Environment must be sandbox or production")
    invoice_id="SAMPLE-2026-0001" if environment=="sandbox" else "DRAFT-2026-0001"
    payload={"id": invoice_id, "environment": environment, "lines":[{"sku":"CONSULT","description":"Consulting hour","quantity":"3.5","unit_price":"250","vat_rate":"18%","discount_type":"percent","discount_value":"10"},{"sku":"DELIVERY","description":"Courier delivery","quantity":"1","unit_price":"39.90","vat_rate":"18%"}]}
    target=Path(path); target.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return {"id": invoice_id, "environment": environment, "input_file": str(target)}
