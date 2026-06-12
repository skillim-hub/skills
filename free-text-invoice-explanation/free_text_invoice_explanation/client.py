from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass, field
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any, Iterable, Literal, Mapping, Sequence


Language = Literal["he", "en"]
DocumentType = Literal["tax_invoice", "invoice_receipt", "receipt", "credit_note", "proforma", "invoice"]
BusinessType = Literal["authorized_dealer", "exempt_dealer", "company", "nonprofit", "consumer"]
DetailLevel = Literal["short", "standard", "detailed"]
Environment = Literal["sandbox", "production"]


@dataclass(frozen=True)
class ValidationIssue:
    """A validation warning or error for an invoice explanation request."""

    code: str
    message: str
    severity: Literal["info", "warning", "error"] = "warning"
    field: str | None = None


@dataclass(frozen=True)
class InvoiceLine:
    """Single invoice line used to generate a plain-language explanation."""

    description: str
    quantity: Decimal | int | float | str = Decimal("1")
    unit_price: Decimal | int | float | str = Decimal("0")
    vat_rate: Decimal | int | float | str = Decimal("18")
    currency: str = "ILS"
    category: str | None = None
    service_period: str | None = None
    note: str | None = None
    reimbursable: bool = False
    reverse_charge: bool = False
    exempt_from_vat: bool = False

    def normalized(self) -> "InvoiceLine":
        return InvoiceLine(
            description=self.description.strip(),
            quantity=_to_decimal(self.quantity, "quantity"),
            unit_price=_to_decimal(self.unit_price, "unit_price"),
            vat_rate=_to_decimal(self.vat_rate, "vat_rate"),
            currency=self.currency.upper().strip(),
            category=self.category.strip() if self.category else None,
            service_period=self.service_period.strip() if self.service_period else None,
            note=self.note.strip() if self.note else None,
            reimbursable=self.reimbursable,
            reverse_charge=self.reverse_charge,
            exempt_from_vat=self.exempt_from_vat,
        )


@dataclass(frozen=True)
class InvoiceContext:
    """Business and document context for explanation wording."""

    business_type: BusinessType = "authorized_dealer"
    document_type: DocumentType = "tax_invoice"
    customer_type: Literal["business", "consumer", "accountant"] = "business"
    language: Language = "he"
    document_date: str | None = None
    business_name: str | None = None
    customer_name: str | None = None
    include_legal_caveat: bool = True
    environment: Environment = "sandbox"


@dataclass(frozen=True)
class ExplanationOptions:
    """Formatting and explanation options."""

    language: Language = "he"
    detail_level: DetailLevel = "standard"
    tone: Literal["plain", "formal"] = "plain"
    include_amount_breakdown: bool = True
    include_next_action: bool = True
    date_format: Literal["DD/MM/YYYY", "YYYY-MM-DD"] = "DD/MM/YYYY"


@dataclass(frozen=True)
class Explanation:
    """Generated explanation with computed amounts and diagnostics."""

    line: InvoiceLine
    title: str
    plain_text: str
    amount_before_vat: Decimal
    vat_amount: Decimal
    amount_after_vat: Decimal
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)
    tags: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["amount_before_vat"] = _decimal_to_string(self.amount_before_vat)
        data["vat_amount"] = _decimal_to_string(self.vat_amount)
        data["amount_after_vat"] = _decimal_to_string(self.amount_after_vat)
        data["line"]["quantity"] = _decimal_to_string(self.line.normalized().quantity)
        data["line"]["unit_price"] = _decimal_to_string(self.line.normalized().unit_price)
        data["line"]["vat_rate"] = _decimal_to_string(self.line.normalized().vat_rate)
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class InvoiceExplanationClient:
    """Local explanation engine with synchronous and asynchronous methods."""

    def __init__(
        self,
        *,
        default_context: InvoiceContext | None = None,
        default_options: ExplanationOptions | None = None,
    ) -> None:
        self.default_context = default_context or InvoiceContext()
        self.default_options = default_options or ExplanationOptions(language=self.default_context.language)

    def validate_line(self, line: InvoiceLine, context: InvoiceContext | None = None) -> list[ValidationIssue]:
        ctx = context or self.default_context
        normalized = line.normalized()
        issues: list[ValidationIssue] = []
        if not normalized.description:
            issues.append(ValidationIssue("missing_description", "Line description is required.", "error", "description"))
        if normalized.quantity <= 0:
            issues.append(ValidationIssue("non_positive_quantity", "Quantity must be greater than zero.", "error", "quantity"))
        if normalized.unit_price < 0 and ctx.document_type != "credit_note":
            issues.append(ValidationIssue("negative_price", "Negative price should normally use a credit note.", "warning", "unit_price"))
        if normalized.vat_rate < 0 or normalized.vat_rate > 100:
            issues.append(ValidationIssue("invalid_vat_rate", "VAT rate must be between 0 and 100.", "error", "vat_rate"))
        if ctx.business_type == "exempt_dealer" and normalized.vat_rate != 0 and not normalized.exempt_from_vat:
            issues.append(ValidationIssue("exempt_dealer_vat", "Exempt dealer lines should not charge VAT.", "warning", "vat_rate"))
        if ctx.document_type == "receipt" and normalized.vat_rate != 0:
            issues.append(ValidationIssue("receipt_vat_language", "A receipt records payment; avoid presenting it as a tax invoice.", "warning", "document_type"))
        if normalized.reverse_charge and normalized.vat_rate != 0:
            issues.append(ValidationIssue("reverse_charge_vat", "Reverse charge lines usually show zero VAT on the supplier invoice.", "warning", "vat_rate"))
        if normalized.currency not in {"ILS", "NIS", "USD", "EUR", "GBP"}:
            issues.append(ValidationIssue("uncommon_currency", "Currency is uncommon for this helper; verify formatting manually.", "info", "currency"))
        return issues

    def explain_line(
        self,
        line: InvoiceLine | Mapping[str, Any],
        context: InvoiceContext | Mapping[str, Any] | None = None,
        options: ExplanationOptions | Mapping[str, Any] | None = None,
    ) -> Explanation:
        invoice_line = self._coerce_line(line).normalized()
        ctx = self._coerce_context(context)
        opts = self._coerce_options(options, ctx)
        issues = self.validate_line(invoice_line, ctx)
        amount_before_vat = money(invoice_line.quantity * invoice_line.unit_price)
        effective_vat_rate = Decimal("0") if invoice_line.exempt_from_vat or ctx.business_type == "exempt_dealer" or invoice_line.reverse_charge else invoice_line.vat_rate
        vat_amount = money(amount_before_vat * effective_vat_rate / Decimal("100"))
        amount_after_vat = money(amount_before_vat + vat_amount)
        tags = tuple(self.detect_edge_cases(invoice_line, ctx))
        title = self.make_title(invoice_line, ctx, opts)
        plain_text = self.render_explanation(
            invoice_line,
            ctx,
            opts,
            amount_before_vat=amount_before_vat,
            vat_amount=vat_amount,
            amount_after_vat=amount_after_vat,
            issues=issues,
            tags=tags,
        )
        return Explanation(
            line=invoice_line,
            title=title,
            plain_text=plain_text,
            amount_before_vat=amount_before_vat,
            vat_amount=vat_amount,
            amount_after_vat=amount_after_vat,
            issues=tuple(issues),
            tags=tags,
        )

    def explain_invoice(
        self,
        lines: Sequence[InvoiceLine | Mapping[str, Any]],
        context: InvoiceContext | Mapping[str, Any] | None = None,
        options: ExplanationOptions | Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        ctx = self._coerce_context(context)
        opts = self._coerce_options(options, ctx)
        explanations = [self.explain_line(line, ctx, opts) for line in lines]
        totals = self.summarize_totals(explanations)
        return {
            "context": asdict(ctx),
            "options": asdict(opts),
            "line_count": len(explanations),
            "explanations": [item.to_dict() for item in explanations],
            "totals": totals,
            "summary": self.render_invoice_summary(explanations, totals, ctx, opts),
        }

    async def async_explain_line(
        self,
        line: InvoiceLine | Mapping[str, Any],
        context: InvoiceContext | Mapping[str, Any] | None = None,
        options: ExplanationOptions | Mapping[str, Any] | None = None,
    ) -> Explanation:
        return await asyncio.to_thread(self.explain_line, line, context, options)

    async def async_explain_invoice(
        self,
        lines: Sequence[InvoiceLine | Mapping[str, Any]],
        context: InvoiceContext | Mapping[str, Any] | None = None,
        options: ExplanationOptions | Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await asyncio.to_thread(self.explain_invoice, lines, context, options)

    def load_invoice_payload(self, payload: str | bytes | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        if isinstance(payload, str):
            loaded = json.loads(payload)
            if not isinstance(loaded, dict):
                raise ValueError("Payload must be a JSON object.")
            return loaded
        return dict(payload)

    def explain_payload(self, payload: str | bytes | Mapping[str, Any]) -> dict[str, Any]:
        loaded = self.load_invoice_payload(payload)
        lines = loaded.get("lines")
        if not isinstance(lines, list):
            raise ValueError("Payload must include a lines list.")
        context = loaded.get("context")
        options = loaded.get("options")
        return self.explain_invoice(lines, context, options)

    def render_explanation(
        self,
        line: InvoiceLine,
        context: InvoiceContext,
        options: ExplanationOptions,
        *,
        amount_before_vat: Decimal,
        vat_amount: Decimal,
        amount_after_vat: Decimal,
        issues: Sequence[ValidationIssue],
        tags: Sequence[str],
    ) -> str:
        if options.language == "he":
            return self._render_hebrew(line, context, options, amount_before_vat, vat_amount, amount_after_vat, issues, tags)
        return self._render_english(line, context, options, amount_before_vat, vat_amount, amount_after_vat, issues, tags)

    def render_invoice_summary(
        self,
        explanations: Sequence[Explanation],
        totals: Mapping[str, str],
        context: InvoiceContext,
        options: ExplanationOptions,
    ) -> str:
        if options.language == "he":
            return (
                f"סיכום המסמך: {len(explanations)} שורות. "
                f"סה״כ לפני מע״מ {self.format_money(totals['amount_before_vat'], 'ILS')}, "
                f"מע״מ {self.format_money(totals['vat_amount'], 'ILS')}, "
                f"לתשלום {self.format_money(totals['amount_after_vat'], 'ILS')}."
            )
        return (
            f"Document summary: {len(explanations)} line items. "
            f"Subtotal {self.format_money(totals['amount_before_vat'], 'ILS')}, "
            f"VAT {self.format_money(totals['vat_amount'], 'ILS')}, "
            f"amount due {self.format_money(totals['amount_after_vat'], 'ILS')}."
        )

    def summarize_totals(self, explanations: Iterable[Explanation]) -> dict[str, str]:
        before = Decimal("0")
        vat = Decimal("0")
        after = Decimal("0")
        for explanation in explanations:
            before += explanation.amount_before_vat
            vat += explanation.vat_amount
            after += explanation.amount_after_vat
        return {
            "amount_before_vat": _decimal_to_string(money(before)),
            "vat_amount": _decimal_to_string(money(vat)),
            "amount_after_vat": _decimal_to_string(money(after)),
        }

    def detect_edge_cases(self, line: InvoiceLine, context: InvoiceContext | None = None) -> list[str]:
        ctx = context or self.default_context
        tags: list[str] = []
        if line.reimbursable:
            tags.append("reimbursement")
        if line.reverse_charge:
            tags.append("reverse_charge")
        if line.exempt_from_vat or ctx.business_type == "exempt_dealer":
            tags.append("vat_exempt")
        if ctx.document_type == "credit_note" or line.unit_price < 0:
            tags.append("credit")
        if line.service_period:
            tags.append("service_period")
        if line.quantity != 1:
            tags.append("quantity_based")
        return tags

    def make_title(self, line: InvoiceLine, context: InvoiceContext, options: ExplanationOptions) -> str:
        if options.language == "he":
            prefix = "זיכוי עבור" if context.document_type == "credit_note" else "הסבר עבור"
            return f"{prefix} {line.description}"
        prefix = "Credit for" if context.document_type == "credit_note" else "Explanation for"
        return f"{prefix} {line.description}"

    def format_money(self, value: Decimal | int | float | str, currency: str = "ILS") -> str:
        amount = money(_to_decimal(value, "value"))
        currency = currency.upper().strip()
        if currency in {"ILS", "NIS"}:
            return f"₪{amount:,.2f}"
        return f"{amount:,.2f} {currency}"

    def format_date(self, value: str | None, options: ExplanationOptions | None = None) -> str | None:
        if not value:
            return None
        opts = options or self.default_options
        parts = value.replace("/", "-").split("-")
        if len(parts) != 3:
            return value
        if len(parts[0]) == 4:
            yyyy, mm, dd = parts
        else:
            dd, mm, yyyy = parts
        if opts.date_format == "DD/MM/YYYY":
            return f"{dd.zfill(2)}/{mm.zfill(2)}/{yyyy}"
        return f"{yyyy}-{mm.zfill(2)}-{dd.zfill(2)}"

    def _render_hebrew(
        self,
        line: InvoiceLine,
        context: InvoiceContext,
        options: ExplanationOptions,
        amount_before_vat: Decimal,
        vat_amount: Decimal,
        amount_after_vat: Decimal,
        issues: Sequence[ValidationIssue],
        tags: Sequence[str],
    ) -> str:
        period = f" עבור תקופת השירות {line.service_period}" if line.service_period else ""
        base = f"השורה מתארת {line.description}{period}."
        quantity = f" הכמות היא {line.quantity} במחיר יחידה {self.format_money(line.unit_price, line.currency)}."
        vat_sentence = self._hebrew_vat_sentence(line, context, vat_amount, amount_after_vat)
        amount_sentence = (
            f" הסכום לפני מע״מ הוא {self.format_money(amount_before_vat, line.currency)}; "
            f"סכום המע״מ הוא {self.format_money(vat_amount, line.currency)}; "
            f"סה״כ לתשלום עבור השורה הוא {self.format_money(amount_after_vat, line.currency)}."
        )
        extras: list[str] = []
        if line.reimbursable:
            extras.append("מדובר בהחזר הוצאה, לכן כדאי לצרף אסמכתה ולהסביר שהחיוב משקף עלות ששולמה עבור הלקוח.")
        if context.document_type == "credit_note":
            extras.append("זהו זיכוי, לכן יש לקשר אותו למסמך המקורי ולציין את הסיבה לזיכוי.")
        if line.note:
            extras.append(f"הערה ללקוח: {line.note}.")
        if issues and options.detail_level != "short":
            extras.append("נדרשת בדיקה: " + "; ".join(issue.message for issue in issues) + ".")
        if context.include_legal_caveat and options.detail_level == "detailed":
            extras.append("יש לאמת את הסיווג, שיעור המע״מ וחובת הדיווח לפי המסמכים הרשמיים של העסק ולפי הדין החל.")
        next_action = ""
        if options.include_next_action:
            next_action = " פעולה מומלצת: להציג את ההסבר לצד השורה במסמך או בהודעת התשלום."
        parts = [base]
        if options.include_amount_breakdown:
            parts.extend([quantity, amount_sentence])
        parts.append(vat_sentence)
        parts.extend(extras)
        if next_action:
            parts.append(next_action)
        return " ".join(part.strip() for part in parts if part).strip()

    def _render_english(
        self,
        line: InvoiceLine,
        context: InvoiceContext,
        options: ExplanationOptions,
        amount_before_vat: Decimal,
        vat_amount: Decimal,
        amount_after_vat: Decimal,
        issues: Sequence[ValidationIssue],
        tags: Sequence[str],
    ) -> str:
        period = f" for the service period {line.service_period}" if line.service_period else ""
        base = f"This line describes {line.description}{period}."
        quantity = f" Quantity is {line.quantity} at a unit price of {self.format_money(line.unit_price, line.currency)}."
        amount_sentence = (
            f" Amount before VAT is {self.format_money(amount_before_vat, line.currency)}; "
            f"VAT is {self.format_money(vat_amount, line.currency)}; "
            f"total for this line is {self.format_money(amount_after_vat, line.currency)}."
        )
        vat_sentence = self._english_vat_sentence(line, context, vat_amount, amount_after_vat)
        extras: list[str] = []
        if line.reimbursable:
            extras.append("This is a reimbursable expense; attach supporting documentation and explain that the charge reflects a cost paid for the client.")
        if context.document_type == "credit_note":
            extras.append("This is a credit note; link it to the original document and state the reason for the credit.")
        if line.note:
            extras.append(f"Client note: {line.note}.")
        if issues and options.detail_level != "short":
            extras.append("Check required: " + "; ".join(issue.message for issue in issues) + ".")
        if context.include_legal_caveat and options.detail_level == "detailed":
            extras.append("Verify classification, VAT rate, and reporting duties against official business records and applicable law.")
        next_action = " Recommended action: show this explanation next to the line item or payment message." if options.include_next_action else ""
        parts = [base]
        if options.include_amount_breakdown:
            parts.extend([quantity, amount_sentence])
        parts.append(vat_sentence)
        parts.extend(extras)
        if next_action:
            parts.append(next_action)
        return " ".join(part.strip() for part in parts if part).strip()

    def _hebrew_vat_sentence(self, line: InvoiceLine, context: InvoiceContext, vat_amount: Decimal, amount_after_vat: Decimal) -> str:
        if context.business_type == "exempt_dealer" or line.exempt_from_vat:
            return "אין להוסיף מע״מ לשורה זו כאשר העסק מסווג כעוסק פטור או כאשר הפריט פטור ממע״מ."
        if line.reverse_charge:
            return "בחיוב במנגנון היפוך חיוב, יש לציין שהלקוח אחראי לבדיקת חובת המע״מ לפי הדין החל."
        if context.document_type == "receipt":
            return "קבלה מתעדת תשלום שהתקבל; אין להציג אותה כחשבונית מס."
        return f"שיעור המע״מ חושב לפי {line.vat_rate}% והתווסף לסכום השורה."

    def _english_vat_sentence(self, line: InvoiceLine, context: InvoiceContext, vat_amount: Decimal, amount_after_vat: Decimal) -> str:
        if context.business_type == "exempt_dealer" or line.exempt_from_vat:
            return "Do not add VAT to this line when the business is an exempt dealer or the item is VAT-exempt."
        if line.reverse_charge:
            return "For reverse charge wording, state that the customer should verify VAT obligations under the applicable rules."
        if context.document_type == "receipt":
            return "A receipt records payment received; do not present it as a tax invoice."
        return f"VAT was calculated at {line.vat_rate}% and added to this line."

    def _coerce_line(self, value: InvoiceLine | Mapping[str, Any]) -> InvoiceLine:
        if isinstance(value, InvoiceLine):
            return value
        return InvoiceLine(**dict(value))

    def _coerce_context(self, value: InvoiceContext | Mapping[str, Any] | None) -> InvoiceContext:
        if value is None:
            return self.default_context
        if isinstance(value, InvoiceContext):
            return value
        return InvoiceContext(**dict(value))

    def _coerce_options(
        self,
        value: ExplanationOptions | Mapping[str, Any] | None,
        context: InvoiceContext,
    ) -> ExplanationOptions:
        if value is None:
            if self.default_options.language != context.language:
                return ExplanationOptions(language=context.language)
            return self.default_options
        if isinstance(value, ExplanationOptions):
            return value
        return ExplanationOptions(**dict(value))


def _to_decimal(value: Decimal | int | float | str, field_name: str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be a decimal-compatible value.") from exc


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _decimal_to_string(value: Decimal | int | float | str) -> str:
    return format(money(_to_decimal(value, "value")), "f")


def explain_line(
    line: InvoiceLine | Mapping[str, Any],
    context: InvoiceContext | Mapping[str, Any] | None = None,
    options: ExplanationOptions | Mapping[str, Any] | None = None,
) -> Explanation:
    return InvoiceExplanationClient().explain_line(line, context, options)


def explain_invoice(
    lines: Sequence[InvoiceLine | Mapping[str, Any]],
    context: InvoiceContext | Mapping[str, Any] | None = None,
    options: ExplanationOptions | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return InvoiceExplanationClient().explain_invoice(lines, context, options)
