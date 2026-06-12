"""Typed helper client for Israeli travel-booking workflows.

The client performs deterministic planning, validation, currency conversion,
and supplier-message preparation. Connect live supplier APIs behind approval
gates, idempotency keys, and secure payment flows.
"""

from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import json
import re
import uuid
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Any, Literal, Mapping, Sequence


PRIMARY_DATE_FORMAT = "%d/%m/%Y"
LEGACY_DATE_FORMAT = "%d-%m-%Y"
SENSITIVE_PATTERNS = [
    re.compile(r"\b\d{16}\b"),
    re.compile(r"\b\d{9}\b"),
    re.compile(r"\b\d{6}\b"),
]


class TripType(str, Enum):
    DOMESTIC = "domestic"
    INTERNATIONAL = "international"
    MIXED = "mixed"


class BookingStatus(str, Enum):
    QUOTE = "quote"
    PENDING_APPROVAL = "pending_approval"
    BOOKED = "booked"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    BLOCKER = "blocker"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: Severity = Severity.WARNING

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "severity": self.severity.value}


@dataclass(frozen=True)
class Traveler:
    type: Literal["adult", "child", "infant"] = "adult"
    count: int = 1
    mobility_needs: bool = False

    def validate(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if self.count < 1:
            issues.append(ValidationIssue("MISSING_TRAVELER", "Traveler count must be at least 1.", Severity.BLOCKER))
        if self.type not in {"adult", "child", "infant"}:
            issues.append(ValidationIssue("INVALID_TRAVELER_TYPE", "Unsupported traveler type.", Severity.BLOCKER))
        return issues

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class Money:
    amount: Decimal | int | float | str
    currency: str = "ILS"

    def __post_init__(self) -> None:
        object.__setattr__(self, "currency", self.currency.upper())
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

    def rounded(self) -> "Money":
        return Money(self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), self.currency)

    def format(self, locale: str = "en") -> str:
        value = self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if self.currency == "ILS":
            return f"₪{value:,.2f}"
        return f"{self.currency} {value:,.2f}"

    def as_dict(self) -> dict[str, str]:
        return {"amount": str(self.amount), "currency": self.currency}


@dataclass(frozen=True)
class FXQuote:
    supplier: Money
    rate_to_ils: Decimal | int | float | str
    source: str = "manual"
    timestamp: str = field(default_factory=lambda: dt.datetime.now(dt.timezone.utc).isoformat())
    card_markup_percent: Decimal | int | float | str = Decimal("0")

    def __post_init__(self) -> None:
        if not isinstance(self.rate_to_ils, Decimal):
            object.__setattr__(self, "rate_to_ils", Decimal(str(self.rate_to_ils)))
        if not isinstance(self.card_markup_percent, Decimal):
            object.__setattr__(self, "card_markup_percent", Decimal(str(self.card_markup_percent)))

    @property
    def base_ils(self) -> Money:
        if self.supplier.currency == "ILS":
            return self.supplier.rounded()
        return Money(self.supplier.amount * self.rate_to_ils, "ILS").rounded()

    @property
    def markup(self) -> Money:
        if self.card_markup_percent <= 0:
            return Money(Decimal("0"), "ILS")
        return Money(self.base_ils.amount * self.card_markup_percent / Decimal("100"), "ILS").rounded()

    @property
    def total_ils(self) -> Money:
        return Money(self.base_ils.amount + self.markup.amount, "ILS").rounded()

    def as_dict(self) -> dict[str, Any]:
        return {
            "supplier": self.supplier.as_dict(),
            "rate_to_ils": str(self.rate_to_ils),
            "source": self.source,
            "timestamp": self.timestamp,
            "card_markup_percent": str(self.card_markup_percent),
            "base_ils": self.base_ils.as_dict(),
            "markup_ils": self.markup.as_dict(),
            "total_ils": self.total_ils.as_dict(),
        }


@dataclass(frozen=True)
class CostLine:
    label: str
    supplier: Money
    fx: FXQuote | None = None
    notes: str = ""

    @property
    def total_ils(self) -> Money:
        if self.fx:
            return self.fx.total_ils
        if self.supplier.currency == "ILS":
            return self.supplier.rounded()
        raise ValueError("Non-ILS cost line requires FXQuote")

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "supplier": self.supplier.as_dict(),
            "total_ils": self.total_ils.as_dict(),
            "notes": self.notes,
            "fx": self.fx.as_dict() if self.fx else None,
        }


@dataclass(frozen=True)
class TravelRequest:
    trip_type: TripType
    origin: str
    destination: str
    start_date: str
    end_date: str
    travelers: Sequence[Traveler] = field(default_factory=lambda: [Traveler()])
    request_id: str | None = None
    business: bool = False
    needs_vat_invoice: bool = False
    passport_expiry: str | None = None
    nationality: str | None = None
    arrival_deadline: str | None = None
    bags: Sequence[str] = field(default_factory=list)
    separate_tickets: bool = False
    locale: Literal["en", "he"] = "en"
    environment: Literal["sandbox", "production"] = "sandbox"

    def __post_init__(self) -> None:
        if not isinstance(self.trip_type, TripType):
            object.__setattr__(self, "trip_type", TripType(self.trip_type))
        normalized_travelers = [
            traveler if isinstance(traveler, Traveler) else Traveler(**traveler)
            for traveler in self.travelers
        ]
        object.__setattr__(self, "travelers", normalized_travelers)
        if self.environment not in {"sandbox", "production"}:
            object.__setattr__(self, "environment", "sandbox")

    def start(self) -> dt.date:
        return parse_israeli_date(self.start_date)

    def end(self) -> dt.date:
        return parse_israeli_date(self.end_date)

    @property
    def total_travelers(self) -> int:
        return sum(t.count for t in self.travelers)

    def validate(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if not self.origin.strip() or not self.destination.strip():
            issues.append(ValidationIssue("MISSING_ROUTE", "Origin and destination are required.", Severity.BLOCKER))
        try:
            start = self.start()
            end = self.end()
            if end < start:
                issues.append(ValidationIssue("INVALID_DATE_RANGE", "End date must not be before start date.", Severity.BLOCKER))
        except ValueError:
            issues.append(ValidationIssue("INVALID_DATE_FORMAT", "Dates must use DD/MM/YYYY.", Severity.BLOCKER))
        if not self.travelers or self.total_travelers < 1:
            issues.append(ValidationIssue("MISSING_TRAVELER", "At least one traveler is required.", Severity.BLOCKER))
        for traveler in self.travelers:
            issues.extend(traveler.validate())
        if self.trip_type in {TripType.INTERNATIONAL, TripType.MIXED}:
            if not self.passport_expiry:
                issues.append(ValidationIssue("MISSING_PASSPORT_PROMPT", "International travel requires passport validity review.", Severity.WARNING))
            if not self.nationality:
                issues.append(ValidationIssue("MISSING_NATIONALITY", "International travel requires nationality for entry-rule prompts.", Severity.WARNING))
        if self.separate_tickets:
            issues.append(ValidationIssue("SEPARATE_TICKET_RISK", "Separate tickets may not protect missed connections.", Severity.WARNING))
        if self.needs_vat_invoice and not self.business:
            issues.append(ValidationIssue("VAT_INVOICE_WITHOUT_BUSINESS", "VAT invoice was requested for a non-business trip; verify need.", Severity.INFO))
        return issues

    def as_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "trip_type": self.trip_type.value,
            "origin": self.origin,
            "destination": self.destination,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "travelers": [t.as_dict() for t in self.travelers],
            "business": self.business,
            "needs_vat_invoice": self.needs_vat_invoice,
            "passport_expiry": self.passport_expiry,
            "nationality": self.nationality,
            "arrival_deadline": self.arrival_deadline,
            "bags": list(self.bags),
            "separate_tickets": self.separate_tickets,
            "locale": self.locale,
            "environment": self.environment,
        }


@dataclass(frozen=True)
class Recommendation:
    status: BookingStatus
    title: str
    summary: str
    cost_lines: Sequence[CostLine]
    issues: Sequence[ValidationIssue]
    checklist: Sequence[str]
    request_id: str | None = None

    @property
    def total_ils(self) -> Money:
        total = sum((line.total_ils.amount for line in self.cost_lines), Decimal("0"))
        return Money(total, "ILS").rounded()

    def as_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "status": self.status.value,
            "title": self.title,
            "summary": self.summary,
            "total_ils": self.total_ils.as_dict(),
            "issues": [i.as_dict() for i in self.issues],
            "checklist": list(self.checklist),
            "cost_lines": [line.as_dict() for line in self.cost_lines],
        }

    def to_markdown(self, locale: str = "en") -> str:
        return self._to_markdown_he() if locale == "he" else self._to_markdown_en()

    def _to_markdown_en(self) -> str:
        rows = "\n".join(
            f"| {line.label} | {line.supplier.format()} | {line.total_ils.format()} | {line.notes or '-'} |"
            for line in self.cost_lines
        )
        issue_rows = "\n".join(f"- {i.code}: {i.message}" for i in self.issues) or "- None"
        checklist = "\n".join(f"{idx}. {item}" for idx, item in enumerate(self.checklist, 1))
        request_line = f"Request ID: {self.request_id}\n" if self.request_id else ""
        return f"""## Booking recommendation

{request_line}Status: {self.status.value}
{self.title}

{self.summary}

### Cost breakdown
| Item | Supplier currency | ₪ estimate | Notes |
|---|---:|---:|---|
{rows}

Total estimate: {self.total_ils.format()}

### Issues and warnings
{issue_rows}

### Required checks
{checklist}
"""

    def _to_markdown_he(self) -> str:
        rows = "\n".join(
            f"| {line.label} | {line.supplier.format('he')} | {line.total_ils.format('he')} | {line.notes or '-'} |"
            for line in self.cost_lines
        )
        issue_rows = "\n".join(f"- {i.code}: {i.message}" for i in self.issues) or "- אין"
        checklist = "\n".join(f"{idx}. {item}" for idx, item in enumerate(self.checklist, 1))
        request_line = f"מזהה בקשה: {self.request_id}\n" if self.request_id else ""
        return f"""## המלצת הזמנה

{request_line}סטטוס: {self.status.value}
{self.title}

{self.summary}

### פירוט עלויות
| רכיב | מטבע ספק | אומדן בש״ח | הערות |
|---|---:|---:|---|
{rows}

סה״כ משוער: {self.total_ils.format('he')}

### בעיות ואזהרות
{issue_rows}

### בדיקות נדרשות
{checklist}
"""


def parse_israeli_date(value: str) -> dt.date:
    for fmt in (PRIMARY_DATE_FORMAT, LEGACY_DATE_FORMAT):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError("Dates must use DD/MM/YYYY")


def format_israeli_date(value: dt.date) -> str:
    return value.strftime(PRIMARY_DATE_FORMAT)


def redact_sensitive(text: str) -> str:
    redacted = text
    for pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def detect_domestic_eilat(destination: str) -> bool:
    normalized = destination.casefold()
    return any(token in normalized for token in ["eilat", "אילת", "ramon", "רמון"])


def detect_shabbat_risk(date_value: str) -> bool:
    day = parse_israeli_date(date_value).weekday()
    return day in {4, 5}


def calculate_fx(
    amount: float | Decimal,
    currency: str,
    rate_to_ils: float | Decimal = 1,
    card_markup_percent: float | Decimal = 0,
    source: str = "manual",
) -> FXQuote:
    return FXQuote(
        supplier=Money(Decimal(str(amount)), currency),
        rate_to_ils=Decimal(str(rate_to_ils)),
        card_markup_percent=Decimal(str(card_markup_percent)),
        source=source,
    )


def invoice_request_he(booking_reference: str, business_name: str, tax_id: str, email: str) -> str:
    return (
        "שלום,\n"
        f"אבקש לשלוח חשבונית מס/קבלה עבור הזמנה {booking_reference}.\n"
        "פרטי העסק לחשבונית:\n"
        f"שם העסק: {business_name}\n"
        f"מספר עוסק/ח.פ.: {tax_id}\n"
        f"דוא״ל למשלוח: {email}\n\n"
        "תודה."
    )


def cancellation_request(booking_reference: str, traveler_name: str, check_in: str) -> str:
    return (
        f"Please cancel booking {booking_reference} for {traveler_name}, check-in {check_in}.\n"
        "Before processing, confirm the cancellation fee, refund amount, refund currency, "
        "and expected refund date. Please send written confirmation."
    )


def duplicate_charge_triage(amounts: Sequence[Money], supplier: str) -> dict[str, Any]:
    total_by_currency: dict[str, Decimal] = {}
    for money in amounts:
        total_by_currency[money.currency] = total_by_currency.get(money.currency, Decimal("0")) + money.amount
    return {
        "supplier": supplier,
        "charge_count": len(amounts),
        "currencies": sorted(total_by_currency),
        "totals": {currency: str(total) for currency, total in total_by_currency.items()},
        "actions": [
            "Distinguish authorization hold from captured charge.",
            "Request supplier payment ledger.",
            "Track refund currency and posting date.",
            "Store card statement evidence without full card number.",
        ],
    }


class TravelBookingClient:
    """Deterministic planning client for travel-booking workflows."""

    def __init__(
        self,
        *,
        base_currency: str = "ILS",
        default_fx_rates: Mapping[str, float | Decimal] | None = None,
        default_card_markup_percent: float | Decimal = 2.8,
        environment: Literal["sandbox", "production"] = "sandbox",
    ) -> None:
        self.base_currency = base_currency.upper()
        self.default_fx_rates = {k.upper(): Decimal(str(v)) for k, v in (default_fx_rates or {}).items()}
        self.default_card_markup_percent = Decimal(str(default_card_markup_percent))
        self.environment = environment

    def create_request(self, request: TravelRequest) -> dict[str, Any]:
        request_id = request.request_id or f"tb-{uuid.uuid4().hex[:12]}"
        request_with_id = dataclasses.replace(request, request_id=request_id, environment=self.environment)
        return {
            "request_id": request_id,
            "environment": self.environment,
            "status": "created",
            "request": request_with_id.as_dict(),
            "issues": [issue.as_dict() for issue in request_with_id.validate()],
        }

    def validate_request(self, request: TravelRequest) -> list[ValidationIssue]:
        return request.validate()

    def convert_to_ils(
        self,
        amount: float | Decimal,
        currency: str,
        *,
        rate_to_ils: float | Decimal | None = None,
        card_markup_percent: float | Decimal | None = None,
        source: str = "manual",
    ) -> FXQuote:
        currency = currency.upper()
        if currency == "ILS":
            rate = Decimal("1")
        elif rate_to_ils is not None:
            rate = Decimal(str(rate_to_ils))
        elif currency in self.default_fx_rates:
            rate = self.default_fx_rates[currency]
        else:
            raise ValueError(f"FX rate missing for {currency}")
        markup = self.default_card_markup_percent if card_markup_percent is None else Decimal(str(card_markup_percent))
        if currency == "ILS":
            markup = Decimal("0")
        return calculate_fx(amount, currency, rate, markup, source=source)

    def build_recommendation(self, request: TravelRequest, *, costs: Sequence[CostLine] | None = None) -> Recommendation:
        issues = list(self.validate_request(request))
        checklist = self._base_checklist(request)
        title, summary = self._route_summary(request)
        if costs is None:
            costs = self.estimate_default_costs(request)
        status = BookingStatus.QUOTE
        if any(issue.severity == Severity.BLOCKER for issue in issues):
            status = BookingStatus.FAILED
        return Recommendation(
            status=status,
            title=title,
            summary=summary,
            cost_lines=list(costs),
            issues=issues,
            checklist=checklist,
            request_id=request.request_id,
        )

    def quote_request(self, request: TravelRequest, *, costs: Sequence[CostLine] | None = None) -> Recommendation:
        return self.build_recommendation(request, costs=costs)

    async def async_build_recommendation(self, request: TravelRequest, *, costs: Sequence[CostLine] | None = None) -> Recommendation:
        await asyncio.sleep(0)
        return self.build_recommendation(request, costs=costs)

    def estimate_default_costs(self, request: TravelRequest) -> list[CostLine]:
        travelers = max(request.total_travelers, 1)
        if request.trip_type == TripType.DOMESTIC and detect_domestic_eilat(request.destination):
            return [
                CostLine("Domestic flight", Money(Decimal(560 * travelers), "ILS"), notes="Estimate; confirm baggage."),
                CostLine("Hotel", Money(Decimal(910 * travelers), "ILS"), notes="Request VAT invoice if business."),
                CostLine("Ramon transfer", Money(Decimal(120 * travelers), "ILS"), notes="Taxi/shuttle estimate."),
            ]
        if request.trip_type == TripType.DOMESTIC:
            return [
                CostLine("Rail / local transport", Money(Decimal(80 * travelers), "ILS"), notes="Verify schedule."),
                CostLine("Last-mile taxi", Money(Decimal(90), "ILS"), notes="Estimate."),
            ]
        if request.trip_type in {TripType.INTERNATIONAL, TripType.MIXED}:
            eur_rate = self.default_fx_rates.get("EUR", Decimal("3.3365"))
            flight = FXQuote(Money(Decimal(390 * travelers), "EUR"), eur_rate, source="manual", card_markup_percent=self.default_card_markup_percent)
            hotel = FXQuote(Money(Decimal(520), "EUR"), eur_rate, source="manual", card_markup_percent=self.default_card_markup_percent)
            return [
                CostLine("International flight", flight.supplier, flight, "Estimate; baggage may be extra."),
                CostLine("Hotel", hotel.supplier, hotel, "Check city tax and invoice type."),
            ]
        return [CostLine("Travel estimate", Money(Decimal(0), "ILS"), notes="No estimate available.")]

    def to_json(self, recommendation: Recommendation | dict[str, Any]) -> str:
        payload = recommendation.as_dict() if hasattr(recommendation, "as_dict") else recommendation
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def _route_summary(self, request: TravelRequest) -> tuple[str, str]:
        title = f"Trip: {request.origin} to {request.destination}, {request.start_date} to {request.end_date}"
        if request.locale == "he":
            title = f"מסלול: {request.origin} אל {request.destination}, {request.start_date} עד {request.end_date}"
        if request.trip_type == TripType.DOMESTIC and detect_domestic_eilat(request.destination):
            summary = "Prefer flight to Ramon plus transfer when speed matters; compare refundable hotel terms."
            if request.locale == "he":
                summary = "העדיפו טיסה לרמון והעברה לאילת כאשר זמן ההגעה חשוב; השוו תנאי ביטול של המלון."
            return title, summary
        if request.trip_type == TripType.DOMESTIC:
            summary = "Compare rail, bus, taxi, and last-mile timing by required arrival time."
            if request.locale == "he":
                summary = "השוו רכבת, אוטובוס, מונית והגעה אחרונה לפי שעת הגעה נדרשת."
            return title, summary
        summary = "Compare airfare, hotel, baggage, local taxes, passport prompts, and FX conversion."
        if request.locale == "he":
            summary = "השוו טיסה, מלון, כבודה, מסים מקומיים, בדיקת דרכון והמרת מטבע."
        return title, summary

    def _base_checklist(self, request: TravelRequest) -> list[str]:
        checklist = [
            "Confirm live availability and price before payment.",
            "Confirm cancellation deadline and fee.",
            "Confirm traveler names match required documents.",
        ]
        if request.trip_type in {TripType.INTERNATIONAL, TripType.MIXED}:
            checklist.extend([
                "Check passport validity and entry requirements with an official source.",
                "Confirm baggage and seat fees.",
                "Record FX source, rate, timestamp, and card markup estimate.",
                "Check local hotel taxes, deposits, and resort fees.",
            ])
        if request.trip_type == TripType.DOMESTIC:
            checklist.append("Check Shabbat, holiday, and service-disruption constraints.")
        if detect_domestic_eilat(request.destination):
            checklist.append("Add transfer between Ramon Airport and Eilat hotel.")
        if request.business or request.needs_vat_invoice:
            checklist.extend([
                "Request חשבונית מס/קבלה or appropriate supplier invoice.",
                "Store receipt, supplier name, business purpose, and approval record.",
            ])
        if request.separate_tickets:
            checklist.append("Document separate-ticket risk and compare protected alternative.")
        if detect_shabbat_risk(request.start_date):
            checklist.append("Review Friday/Saturday transport limitations.")
        return checklist


__all__ = [
    "BookingStatus",
    "CostLine",
    "FXQuote",
    "Money",
    "Recommendation",
    "Severity",
    "TravelBookingClient",
    "TravelRequest",
    "Traveler",
    "TripType",
    "ValidationIssue",
    "calculate_fx",
    "cancellation_request",
    "detect_domestic_eilat",
    "detect_shabbat_risk",
    "duplicate_charge_triage",
    "format_israeli_date",
    "invoice_request_he",
    "parse_israeli_date",
    "redact_sensitive",
]
