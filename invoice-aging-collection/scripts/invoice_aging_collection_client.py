"""Typed invoice aging and Hebrew collection reminder helper.

The module is intentionally dependency-light so it can run inside a skill package,
CI job, or local bookkeeping workflow. It calculates due dates, classifies aging,
renders Hebrew reminders, and returns dry-run delivery payloads for WhatsApp/email.
"""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol


ILS = "ILS"
DATE_FORMAT = "%d/%m/%Y"
LEGACY_DATE_FORMAT = "%d-%m-%Y"
ISO_DATE_FORMAT = "%Y-%m-%d"


class InvoiceStatus(str, Enum):
    OPEN = "open"
    PAID = "paid"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class AgingBucket(str, Enum):
    NOT_DUE = "not_due"
    CURRENT = "current"
    DAYS_30 = "30"
    DAYS_45 = "45"
    DAYS_60 = "60"
    DAYS_75 = "75"
    DAYS_90_PLUS = "90_plus"
    PAID = "paid"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class ReminderStage(str, Enum):
    NONE = "none"
    FRIENDLY_WHATSAPP = "friendly_whatsapp"
    FOLLOWUP_WHATSAPP = "followup_whatsapp"
    FORMAL_EMAIL = "formal_email"
    LEGAL_WARNING = "legal_warning"
    FINAL_NOTICE = "final_notice"


class Channel(str, Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    REGISTERED_MAIL = "registered_mail"


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    invoice_id: str | None = None
    client_id: str | None = None


@dataclass(frozen=True)
class PartialPayment:
    date: date
    amount: Decimal
    reference: str = ""


@dataclass(frozen=True)
class ClientAccount:
    client_id: str
    name: str
    email: str = ""
    whatsapp: str = ""
    mailing_address: str = ""
    entity_type: str = "business"


@dataclass(frozen=True)
class BusinessProfile:
    name: str
    payment_instructions: str = ""
    default_currency: str = ILS
    email_sender: str = ""


@dataclass
class Invoice:
    invoice_id: str
    client_id: str
    issue_date: date
    amount: Decimal
    currency: str = ILS
    status: InvoiceStatus = InvoiceStatus.OPEN
    due_date: date | None = None
    submitted_date: date | None = None
    payment_terms_days: int | None = None
    partial_payments: list[PartialPayment] = field(default_factory=list)
    paid_date: date | None = None
    dispute_reason: str = ""
    promised_payment_date: date | None = None
    last_stage: ReminderStage = ReminderStage.NONE

    def resolved_due_date(self) -> date:
        """Return the best available due date.

        Priority:
        1. Explicit due date.
        2. Issue date + configured payment terms.
        3. End of issue month + 45 days as a conservative local default.
        """
        if self.due_date:
            return self.due_date
        if self.payment_terms_days is not None:
            return self.issue_date + timedelta(days=self.payment_terms_days)
        return end_of_month(self.issue_date) + timedelta(days=45)

    def amount_paid(self) -> Decimal:
        return money(sum((p.amount for p in self.partial_payments), Decimal("0.00")))

    def outstanding_amount(self) -> Decimal:
        if self.status in {InvoiceStatus.PAID, InvoiceStatus.CANCELLED}:
            return Decimal("0.00")
        outstanding = self.amount - self.amount_paid()
        return money(max(outstanding, Decimal("0.00")))

    def age_days(self, as_of: date) -> int:
        return (as_of - self.resolved_due_date()).days

    def is_active(self) -> bool:
        return self.status == InvoiceStatus.OPEN and self.outstanding_amount() > Decimal("0.00")


@dataclass(frozen=True)
class Reminder:
    invoice_id: str
    client_id: str
    client_name: str
    stage: ReminderStage
    channel: Channel
    recipient: str
    subject: str
    body: str
    scheduled_date: date
    requires_human_review: bool
    dry_run: bool = True

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "invoice_id": self.invoice_id,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "stage": self.stage.value,
            "channel": self.channel.value,
            "recipient": self.recipient,
            "subject": self.subject,
            "body": self.body,
            "scheduled_date": format_date(self.scheduled_date),
            "requires_human_review": self.requires_human_review,
            "dry_run": self.dry_run,
            "message_hash": "sha256:" + hashlib.sha256(self.body.encode("utf-8")).hexdigest(),
        }
        return payload


@dataclass(frozen=True)
class AgingRecord:
    invoice_id: str
    client_id: str
    client_name: str
    due_date: date
    age_days: int
    bucket: AgingBucket
    stage: ReminderStage
    amount: Decimal
    outstanding_amount: Decimal
    requires_human_review: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "invoice_id": self.invoice_id,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "due_date": format_date(self.due_date),
            "age_days": self.age_days,
            "bucket": self.bucket.value,
            "stage": self.stage.value,
            "amount": format_money(self.amount),
            "outstanding_amount": format_money(self.outstanding_amount),
            "requires_human_review": self.requires_human_review,
        }


class DeliveryTransport(Protocol):
    def send(self, reminder: Reminder) -> dict[str, Any]:
        ...


class AsyncDeliveryTransport(Protocol):
    async def send(self, reminder: Reminder) -> dict[str, Any]:
        ...


class DryRunTransport:
    """Return a delivery payload without contacting an external service."""

    def send(self, reminder: Reminder) -> dict[str, Any]:
        payload = reminder.to_payload()
        payload["delivery_status"] = "dry_run"
        return payload


class AsyncDryRunTransport:
    """Async dry-run transport."""

    async def send(self, reminder: Reminder) -> dict[str, Any]:
        await asyncio.sleep(0)
        payload = reminder.to_payload()
        payload["delivery_status"] = "dry_run"
        return payload


def parse_date(value: str | date | None) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    for fmt in (DATE_FORMAT, LEGACY_DATE_FORMAT, ISO_DATE_FORMAT):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value!r}")


def require_date(value: str | date, field_name: str = "date") -> date:
    parsed = parse_date(value)
    if parsed is None:
        raise ValueError(f"{field_name} is required")
    return parsed


def format_date(value: date) -> str:
    return value.strftime(DATE_FORMAT)


def money(value: Decimal | str | int | float) -> Decimal:
    try:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid amount: {value!r}") from exc
    return decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_money(value: Decimal | str | int | float, currency: str = ILS) -> str:
    amount = money(value)
    formatted = f"{amount:,.2f}"
    if currency == ILS:
        return f"₪{formatted}"
    return f"{formatted} {currency}"


def decimal_string(value: Decimal | str | int | float) -> str:
    return f"{money(value):.2f}"


def end_of_month(value: date) -> date:
    if value.month == 12:
        return date(value.year, 12, 31)
    return date(value.year, value.month + 1, 1) - timedelta(days=1)


def normalize_israeli_phone(phone: str) -> str:
    raw = re.sub(r"[\s\-()]", "", phone or "")
    if raw.startswith("+972"):
        normalized = raw
    elif raw.startswith("972"):
        normalized = "+" + raw
    elif raw.startswith("0") and len(raw) >= 9:
        normalized = "+972" + raw[1:]
    else:
        raise ValueError(f"Cannot normalize Israeli phone number: {phone!r}")
    if not re.fullmatch(r"\+972[0-9]{8,9}", normalized):
        raise ValueError(f"Invalid Israeli E.164 phone number: {phone!r}")
    return normalized


def bucket_for_invoice(invoice: Invoice, as_of: date) -> AgingBucket:
    if invoice.status == InvoiceStatus.PAID:
        return AgingBucket.PAID
    if invoice.status == InvoiceStatus.CANCELLED:
        return AgingBucket.CANCELLED
    if invoice.status == InvoiceStatus.DISPUTED:
        return AgingBucket.DISPUTED

    days = invoice.age_days(as_of)
    if days < 0:
        return AgingBucket.NOT_DUE
    if days < 30:
        return AgingBucket.CURRENT
    if days < 45:
        return AgingBucket.DAYS_30
    if days < 60:
        return AgingBucket.DAYS_45
    if days < 75:
        return AgingBucket.DAYS_60
    if days < 90:
        return AgingBucket.DAYS_75
    return AgingBucket.DAYS_90_PLUS


def stage_for_bucket(bucket: AgingBucket) -> ReminderStage:
    mapping = {
        AgingBucket.DAYS_30: ReminderStage.FRIENDLY_WHATSAPP,
        AgingBucket.DAYS_45: ReminderStage.FOLLOWUP_WHATSAPP,
        AgingBucket.DAYS_60: ReminderStage.FORMAL_EMAIL,
        AgingBucket.DAYS_75: ReminderStage.LEGAL_WARNING,
        AgingBucket.DAYS_90_PLUS: ReminderStage.FINAL_NOTICE,
    }
    return mapping.get(bucket, ReminderStage.NONE)


def channel_for_stage(stage: ReminderStage) -> Channel | None:
    mapping = {
        ReminderStage.FRIENDLY_WHATSAPP: Channel.WHATSAPP,
        ReminderStage.FOLLOWUP_WHATSAPP: Channel.WHATSAPP,
        ReminderStage.FORMAL_EMAIL: Channel.EMAIL,
        ReminderStage.LEGAL_WARNING: Channel.EMAIL,
        ReminderStage.FINAL_NOTICE: Channel.REGISTERED_MAIL,
    }
    return mapping.get(stage)


def requires_human_review(stage: ReminderStage) -> bool:
    return stage in {
        ReminderStage.FORMAL_EMAIL,
        ReminderStage.LEGAL_WARNING,
        ReminderStage.FINAL_NOTICE,
    }


def is_business_day(value: date, blocked_dates: Iterable[date] = ()) -> bool:
    blocked = set(blocked_dates)
    return value.weekday() not in (4, 5) and value not in blocked


def next_business_day(value: date, blocked_dates: Iterable[date] = ()) -> date:
    current = value
    blocked = set(blocked_dates)
    while not is_business_day(current, blocked):
        current += timedelta(days=1)
    return current


def response_deadline(as_of: date, days: int, blocked_dates: Iterable[date] = ()) -> date:
    return next_business_day(as_of + timedelta(days=days), blocked_dates)


def render_message(
    *,
    business: BusinessProfile,
    client: ClientAccount,
    invoice: Invoice,
    stage: ReminderStage,
    as_of: date,
    blocked_dates: Iterable[date] = (),
) -> tuple[str, str]:
    amount = format_money(invoice.amount, invoice.currency)
    outstanding = format_money(invoice.outstanding_amount(), invoice.currency)
    issue = format_date(invoice.issue_date)
    due = format_date(invoice.resolved_due_date())
    deadline_7 = format_date(response_deadline(as_of, 7, blocked_dates))
    deadline_14 = format_date(response_deadline(as_of, 14, blocked_dates))
    payment = business.payment_instructions or "נא להעביר פרטי תשלום זמינים או ליצור קשר להסדרת התשלום."

    values = {
        "client_name": client.name,
        "invoice_id": invoice.invoice_id,
        "issue_date": issue,
        "amount": amount,
        "outstanding_amount": outstanding,
        "due_date": due,
        "business_name": business.name,
        "payment_instructions": payment,
        "deadline_7": deadline_7,
        "deadline_14": deadline_14,
    }

    if stage == ReminderStage.FRIENDLY_WHATSAPP:
        subject = ""
        body = (
            "היי {client_name},\n"
            "רציתי לוודא שקיבלת את חשבונית {invoice_id} מתאריך {issue_date} על סך {amount}.\n"
            "מועד התשלום היה {due_date}, ונשארה יתרה פתוחה של {outstanding_amount}.\n"
            "אשמח לעדכון לגבי מועד התשלום.\n"
            "תודה,\n"
            "{business_name}"
        )
    elif stage == ReminderStage.FOLLOWUP_WHATSAPP:
        subject = ""
        body = (
            "שלום {client_name},\n"
            "תזכורת נוספת לגבי חשבונית {invoice_id} שטרם שולמה.\n"
            "יתרה לתשלום: {outstanding_amount}\n"
            "מועד פירעון: {due_date}\n\n"
            "פרטי תשלום:\n"
            "{payment_instructions}\n\n"
            "נא לעדכן עד {deadline_7}.\n"
            "בברכה,\n"
            "{business_name}"
        )
    elif stage == ReminderStage.FORMAL_EMAIL:
        subject = "דרישת תשלום עבור חשבונית {invoice_id}"
        body = (
            "לכבוד {client_name},\n\n"
            "הנדון: דרישת תשלום עבור חשבונית {invoice_id}\n\n"
            "על פי הרישומים, חשבונית {invoice_id} מתאריך {issue_date} על סך {amount} "
            "טרם שולמה במלואה. מועד הפירעון היה {due_date}, והיתרה הפתוחה היא {outstanding_amount}.\n\n"
            "נא להסדיר את התשלום בתוך 7 ימים, עד {deadline_7}, או להעביר אסמכתה לתשלום שבוצע.\n\n"
            "פרטי תשלום:\n"
            "{payment_instructions}\n\n"
            "אם קיימת מחלוקת עניינית לגבי החשבונית, נא לפרט אותה בכתב כדי שניתן יהיה לבדוק את הנושא.\n\n"
            "בברכה,\n"
            "{business_name}"
        )
    elif stage == ReminderStage.LEGAL_WARNING:
        subject = "התראה לפני המשך טיפול בגביית חשבונית {invoice_id}"
        body = (
            "לכבוד {client_name},\n\n"
            "למרות פניות קודמות, חשבונית {invoice_id} מתאריך {issue_date} נותרה פתוחה.\n"
            "יתרת החוב: {outstanding_amount}\n"
            "מועד הפירעון: {due_date}\n\n"
            "נא להסדיר את התשלום בתוך 14 ימים, עד {deadline_14}.\n"
            "בהיעדר תשלום או הסדר כתוב, ייבחנו צעדים נוספים לגביית החוב, לרבות הכנת מכתב דרישה והגשת תביעה מתאימה.\n\n"
            "פרטי תשלום:\n"
            "{payment_instructions}\n\n"
            "בברכה,\n"
            "{business_name}"
        )
    elif stage == ReminderStage.FINAL_NOTICE:
        subject = "מכתב דרישה סופי עבור חשבונית {invoice_id}"
        body = (
            "לכבוד {client_name},\n\n"
            "הנדון: מכתב דרישה סופי לתשלום חשבונית {invoice_id}\n\n"
            "חשבונית {invoice_id} מתאריך {issue_date} נותרה פתוחה למרות פניות קודמות.\n"
            "יתרת החוב לתשלום: {outstanding_amount}\n"
            "מועד הפירעון המקורי: {due_date}\n\n"
            "נא להסדיר את התשלום בתוך 14 ימים, עד {deadline_14}. "
            "ככל שלא יתקבל תשלום או הסדר כתוב, ניתן יהיה לבחון נקיטת צעדים נוספים לגביית החוב בהתאם לדין.\n\n"
            "פרטי תשלום:\n"
            "{payment_instructions}\n\n"
            "בברכה,\n"
            "{business_name}"
        )
    else:
        return "", ""

    return subject.format(**values), body.format(**values)


def parse_partial_payments(raw: Any) -> list[PartialPayment]:
    if not raw:
        return []
    if isinstance(raw, str):
        raw = json.loads(raw)
    payments = []
    for item in raw:
        payments.append(
            PartialPayment(
                date=require_date(item["date"], "partial payment date"),
                amount=money(item["amount"]),
                reference=str(item.get("reference", "")),
            )
        )
    return payments


def invoice_from_dict(data: Mapping[str, Any]) -> Invoice:
    status = InvoiceStatus(str(data.get("status", "open")).lower())
    last_stage_raw = str(data.get("last_stage", "none") or "none")
    return Invoice(
        invoice_id=str(data["invoice_id"]),
        client_id=str(data["client_id"]),
        issue_date=require_date(data["issue_date"], "issue_date"),
        due_date=parse_date(data.get("due_date")),
        submitted_date=parse_date(data.get("submitted_date")),
        amount=money(data["amount"]),
        currency=str(data.get("currency", ILS) or ILS).upper(),
        status=status,
        payment_terms_days=(
            int(data["payment_terms_days"])
            if data.get("payment_terms_days") not in (None, "")
            else None
        ),
        partial_payments=parse_partial_payments(data.get("partial_payments", [])),
        paid_date=parse_date(data.get("paid_date")),
        dispute_reason=str(data.get("dispute_reason", "")),
        promised_payment_date=parse_date(data.get("promised_payment_date")),
        last_stage=ReminderStage(last_stage_raw),
    )


def client_from_dict(data: Mapping[str, Any]) -> ClientAccount:
    whatsapp = str(data.get("whatsapp", "") or "")
    if whatsapp:
        try:
            whatsapp = normalize_israeli_phone(whatsapp)
        except ValueError:
            whatsapp = str(data.get("whatsapp", "") or "")
    return ClientAccount(
        client_id=str(data["client_id"]),
        name=str(data["name"]),
        email=str(data.get("email", "") or ""),
        whatsapp=whatsapp,
        mailing_address=str(data.get("mailing_address", "") or ""),
        entity_type=str(data.get("entity_type", "business") or "business"),
    )


def business_from_dict(data: Mapping[str, Any] | None) -> BusinessProfile:
    data = data or {}
    return BusinessProfile(
        name=str(data.get("name", "העסק") or "העסק"),
        payment_instructions=str(data.get("payment_instructions", "") or ""),
        default_currency=str(data.get("default_currency", ILS) or ILS).upper(),
        email_sender=str(data.get("email_sender", "") or ""),
    )


def load_ledger(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_ledger(path: str | Path, ledger: Mapping[str, Any]) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(ledger, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sample_ledger() -> dict[str, Any]:
    return {
        "business": {
            "name": "סטודיו דוגמה",
            "payment_instructions": "בנק 12, סניף 345, חשבון 67890",
            "default_currency": ILS,
        },
        "clients": [
            {
                "client_id": "c-100",
                "name": 'לקוח לדוגמה בע"מ',
                "email": "client@example.co.il",
                "whatsapp": "+972501234567",
                "mailing_address": "רחוב הדוגמה 1, תל אביב",
            }
        ],
        "invoices": [
            {
                "invoice_id": "INV-100",
                "client_id": "c-100",
                "issue_date": "01/01/2026",
                "due_date": "31/01/2026",
                "amount": "2500.00",
                "currency": ILS,
                "status": "open",
                "partial_payments": [{"date": "10/03/2026", "amount": "500.00"}],
            },
            {
                "invoice_id": "INV-101",
                "client_id": "c-100",
                "issue_date": "01/03/2026",
                "due_date": "30/04/2026",
                "amount": "900.00",
                "currency": ILS,
                "status": "open",
                "partial_payments": [],
            },
        ],
        "blocked_dates": ["23/04/2026"],
    }


class InvoiceAgingClient:
    def __init__(self, ledger: Mapping[str, Any]):
        self.raw_ledger = dict(ledger)
        self.business = business_from_dict(self.raw_ledger.get("business", {}))
        self.clients = {
            client.client_id: client
            for client in (client_from_dict(item) for item in self.raw_ledger.get("clients", []))
        }
        self.invoices = [invoice_from_dict(item) for item in self.raw_ledger.get("invoices", [])]
        self.blocked_dates = {
            require_date(item, "blocked_date") for item in self.raw_ledger.get("blocked_dates", [])
        }

    @classmethod
    def from_file(cls, path: str | Path) -> "InvoiceAgingClient":
        return cls(load_ledger(path))

    @classmethod
    def from_sample(cls) -> "InvoiceAgingClient":
        return cls(sample_ledger())

    def validate(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        invoice_ids: set[str] = set()

        for client in self.clients.values():
            if client.whatsapp:
                try:
                    normalize_israeli_phone(client.whatsapp)
                except ValueError as exc:
                    issues.append(
                        ValidationIssue(
                            code="BAD_PHONE",
                            message=str(exc),
                            severity=ValidationSeverity.WARNING,
                            client_id=client.client_id,
                        )
                    )

        for invoice in self.invoices:
            if invoice.invoice_id in invoice_ids:
                issues.append(
                    ValidationIssue(
                        code="DUPLICATE_INVOICE_ID",
                        message=f"Duplicate invoice ID {invoice.invoice_id}",
                        invoice_id=invoice.invoice_id,
                    )
                )
            invoice_ids.add(invoice.invoice_id)

            if invoice.client_id not in self.clients:
                issues.append(
                    ValidationIssue(
                        code="UNKNOWN_CLIENT",
                        message=f"Invoice references unknown client {invoice.client_id}",
                        invoice_id=invoice.invoice_id,
                        client_id=invoice.client_id,
                    )
                )

            if invoice.amount <= Decimal("0.00"):
                issues.append(
                    ValidationIssue(
                        code="BAD_AMOUNT",
                        message="Invoice amount must be positive",
                        invoice_id=invoice.invoice_id,
                    )
                )

            if invoice.currency != ILS:
                issues.append(
                    ValidationIssue(
                        code="UNSUPPORTED_CURRENCY",
                        message=f"Unsupported currency {invoice.currency}",
                        invoice_id=invoice.invoice_id,
                    )
                )

            if invoice.amount_paid() > invoice.amount:
                issues.append(
                    ValidationIssue(
                        code="PARTIAL_PAYMENTS_EXCEED_AMOUNT",
                        message="Partial payments exceed invoice amount",
                        invoice_id=invoice.invoice_id,
                    )
                )

            if invoice.due_date and invoice.due_date < invoice.issue_date:
                issues.append(
                    ValidationIssue(
                        code="DUE_BEFORE_ISSUE",
                        message="Due date is before issue date; confirm data",
                        severity=ValidationSeverity.WARNING,
                        invoice_id=invoice.invoice_id,
                    )
                )

            if invoice.paid_date and invoice.status == InvoiceStatus.OPEN:
                issues.append(
                    ValidationIssue(
                        code="PAID_DATE_OPEN_STATUS",
                        message="Paid date exists but invoice status is open",
                        severity=ValidationSeverity.WARNING,
                        invoice_id=invoice.invoice_id,
                    )
                )

        return issues

    def aging_records(self, as_of: str | date) -> list[AgingRecord]:
        as_of_date = require_date(as_of, "as_of")
        records: list[AgingRecord] = []
        for invoice in self.invoices:
            client = self.clients.get(invoice.client_id)
            if client is None:
                continue
            bucket = bucket_for_invoice(invoice, as_of_date)
            stage = stage_for_bucket(bucket)
            records.append(
                AgingRecord(
                    invoice_id=invoice.invoice_id,
                    client_id=invoice.client_id,
                    client_name=client.name,
                    due_date=invoice.resolved_due_date(),
                    age_days=invoice.age_days(as_of_date),
                    bucket=bucket,
                    stage=stage,
                    amount=invoice.amount,
                    outstanding_amount=invoice.outstanding_amount(),
                    requires_human_review=requires_human_review(stage),
                )
            )
        return records

    def aging_report(self, as_of: str | date) -> dict[str, Any]:
        records = self.aging_records(as_of)
        bucket_totals: dict[str, Decimal] = {}
        for record in records:
            bucket_totals.setdefault(record.bucket.value, Decimal("0.00"))
            bucket_totals[record.bucket.value] += record.outstanding_amount

        return {
            "as_of": format_date(require_date(as_of, "as_of")),
            "totals": {
                "open_invoices": sum(1 for r in records if r.outstanding_amount > 0),
                "outstanding_amount": decimal_string(sum((r.outstanding_amount for r in records), Decimal("0.00"))),
                "currency": ILS,
            },
            "bucket_totals": {key: decimal_string(value) for key, value in sorted(bucket_totals.items())},
            "requires_human_review": sum(1 for r in records if r.requires_human_review),
            "invoices": [record.to_dict() for record in records],
        }

    def find_invoice(self, invoice_id: str) -> Invoice:
        for invoice in self.invoices:
            if invoice.invoice_id == invoice_id:
                return invoice
        raise KeyError(f"Invoice not found: {invoice_id}")

    def _recipient_for(self, client: ClientAccount, stage: ReminderStage) -> tuple[Channel, str] | None:
        channel = channel_for_stage(stage)
        if channel == Channel.WHATSAPP and client.whatsapp:
            return channel, client.whatsapp
        if channel == Channel.EMAIL and client.email:
            return channel, client.email
        if channel == Channel.REGISTERED_MAIL and client.mailing_address:
            return channel, client.mailing_address
        return None

    def render_for_invoice(
        self,
        invoice_id: str,
        stage: str | ReminderStage,
        as_of: str | date,
        *,
        scheduled_date: str | date | None = None,
        dry_run: bool = True,
    ) -> Reminder:
        stage_value = stage if isinstance(stage, ReminderStage) else ReminderStage(stage)
        as_of_date = require_date(as_of, "as_of")
        invoice = self.find_invoice(invoice_id)
        client = self.clients[invoice.client_id]
        subject, body = render_message(
            business=self.business,
            client=client,
            invoice=invoice,
            stage=stage_value,
            as_of=as_of_date,
            blocked_dates=self.blocked_dates,
        )
        recipient_info = self._recipient_for(client, stage_value)
        if recipient_info is None:
            channel = channel_for_stage(stage_value) or Channel.EMAIL
            recipient = ""
        else:
            channel, recipient = recipient_info
        send_date = next_business_day(require_date(scheduled_date, "scheduled_date") if scheduled_date else as_of_date, self.blocked_dates)
        return Reminder(
            invoice_id=invoice.invoice_id,
            client_id=client.client_id,
            client_name=client.name,
            stage=stage_value,
            channel=channel,
            recipient=recipient,
            subject=subject,
            body=body,
            scheduled_date=send_date,
            requires_human_review=requires_human_review(stage_value),
            dry_run=dry_run,
        )

    def reminders_due(
        self,
        as_of: str | date,
        *,
        channel: str | Channel | None = None,
        dry_run: bool = True,
    ) -> list[Reminder]:
        as_of_date = require_date(as_of, "as_of")
        requested_channel = Channel(channel) if channel else None
        reminders: list[Reminder] = []
        for record in self.aging_records(as_of_date):
            if record.stage == ReminderStage.NONE:
                continue
            invoice = self.find_invoice(record.invoice_id)
            if not invoice.is_active():
                continue
            if invoice.promised_payment_date and as_of_date <= invoice.promised_payment_date:
                continue
            reminder = self.render_for_invoice(
                record.invoice_id,
                record.stage,
                as_of_date,
                dry_run=dry_run,
            )
            if not reminder.recipient:
                continue
            if requested_channel and reminder.channel != requested_channel:
                continue
            reminders.append(reminder)
        return reminders

    def send_due(
        self,
        as_of: str | date,
        *,
        transport: DeliveryTransport | None = None,
        channel: str | Channel | None = None,
        dry_run: bool = True,
        require_approval: bool = True,
    ) -> list[dict[str, Any]]:
        transport = transport or DryRunTransport()
        results = []
        for reminder in self.reminders_due(as_of, channel=channel, dry_run=dry_run):
            if require_approval and reminder.requires_human_review and not dry_run:
                results.append({**reminder.to_payload(), "delivery_status": "blocked_human_review_required"})
                continue
            results.append(transport.send(reminder))
        return results

    async def async_send_due(
        self,
        as_of: str | date,
        *,
        transport: AsyncDeliveryTransport | None = None,
        channel: str | Channel | None = None,
        dry_run: bool = True,
        require_approval: bool = True,
    ) -> list[dict[str, Any]]:
        transport = transport or AsyncDryRunTransport()
        results = []
        for reminder in self.reminders_due(as_of, channel=channel, dry_run=dry_run):
            if require_approval and reminder.requires_human_review and not dry_run:
                results.append({**reminder.to_payload(), "delivery_status": "blocked_human_review_required"})
                continue
            results.append(await transport.send(reminder))
        return results

    def client_summary(self, as_of: str | date) -> list[dict[str, Any]]:
        records = self.aging_records(as_of)
        grouped: dict[str, dict[str, Any]] = {}
        for record in records:
            if record.outstanding_amount <= 0:
                continue
            item = grouped.setdefault(
                record.client_id,
                {
                    "client_id": record.client_id,
                    "client_name": record.client_name,
                    "invoice_count": 0,
                    "outstanding_amount": Decimal("0.00"),
                    "oldest_due_date": record.due_date,
                    "highest_bucket": record.bucket.value,
                },
            )
            item["invoice_count"] += 1
            item["outstanding_amount"] += record.outstanding_amount
            if record.due_date < item["oldest_due_date"]:
                item["oldest_due_date"] = record.due_date
            item["highest_bucket"] = max(
                item["highest_bucket"],
                record.bucket.value,
                key=lambda b: bucket_rank(AgingBucket(b)),
            )

        return [
            {
                **item,
                "outstanding_amount": decimal_string(item["outstanding_amount"]),
                "oldest_due_date": format_date(item["oldest_due_date"]),
            }
            for item in grouped.values()
        ]

    def evidence_pack(self, client_id: str, as_of: str | date) -> dict[str, Any]:
        client = self.clients[client_id]
        records = [r for r in self.aging_records(as_of) if r.client_id == client_id and r.outstanding_amount > 0]
        return {
            "client": {
                "client_id": client.client_id,
                "name": client.name,
                "email": client.email,
                "whatsapp": client.whatsapp,
                "mailing_address": client.mailing_address,
            },
            "as_of": format_date(require_date(as_of, "as_of")),
            "invoices": [record.to_dict() for record in records],
            "evidence_checklist": [
                "signed agreement, quote, or order",
                "invoice copy",
                "proof of invoice delivery",
                "proof of service or product delivery",
                "payment ledger",
                "WhatsApp reminders",
                "email reminders with headers",
                "registered-mail receipt",
                "client replies",
            ],
        }


def bucket_rank(bucket: AgingBucket) -> int:
    order = {
        AgingBucket.NOT_DUE: 0,
        AgingBucket.CURRENT: 1,
        AgingBucket.DAYS_30: 2,
        AgingBucket.DAYS_45: 3,
        AgingBucket.DAYS_60: 4,
        AgingBucket.DAYS_75: 5,
        AgingBucket.DAYS_90_PLUS: 6,
        AgingBucket.DISPUTED: 7,
        AgingBucket.PAID: -1,
        AgingBucket.CANCELLED: -1,
    }
    return order[bucket]


def import_csv(csv_path: str | Path) -> dict[str, Any]:
    clients: dict[str, dict[str, Any]] = {}
    invoices: list[dict[str, Any]] = []
    required = {
        "invoice_id",
        "client_id",
        "client_name",
        "issue_date",
        "amount",
        "currency",
        "status",
    }

    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV_MISSING_COLUMN: {', '.join(sorted(missing))}")
        for row in reader:
            client_id = row["client_id"].strip()
            clients.setdefault(
                client_id,
                {
                    "client_id": client_id,
                    "name": row["client_name"].strip(),
                    "email": row.get("email", "").strip(),
                    "whatsapp": row.get("whatsapp", "").strip(),
                    "mailing_address": row.get("mailing_address", "").strip(),
                },
            )
            invoice = {
                "invoice_id": row["invoice_id"].strip(),
                "client_id": client_id,
                "issue_date": row["issue_date"].strip(),
                "due_date": row.get("due_date", "").strip(),
                "amount": decimal_string(row["amount"].strip()),
                "currency": row.get("currency", ILS).strip().upper() or ILS,
                "status": row.get("status", "open").strip().lower() or "open",
                "partial_payments": [],
            }
            invoices.append(invoice)

    return {
        "business": {"name": "העסק", "payment_instructions": "", "default_currency": ILS},
        "clients": list(clients.values()),
        "invoices": invoices,
        "blocked_dates": [],
    }


def next_invoice_id(existing_ids: Iterable[str], prefix: str = "INV") -> str:
    """Return the next invoice ID using the provided prefix and numeric suffix."""
    numbers: list[int] = []
    pattern = re.compile(rf"^{re.escape(prefix)}[-_]?(\d+)$", re.IGNORECASE)
    for existing_id in existing_ids:
        match = pattern.fullmatch(str(existing_id))
        if match:
            numbers.append(int(match.group(1)))
    next_number = (max(numbers) + 1) if numbers else 100
    return f"{prefix}-{next_number}"


def create_invoice_record(
    *,
    client_id: str,
    issue_date: str | date,
    amount: Decimal | str | int | float,
    invoice_id: str | None = None,
    due_date: str | date | None = None,
    currency: str = ILS,
    status: str | InvoiceStatus = InvoiceStatus.OPEN,
    payment_terms_days: int | None = None,
    existing_invoice_ids: Iterable[str] = (),
) -> dict[str, Any]:
    """Create a validated invoice dictionary suitable for appending to a ledger."""
    resolved_id = invoice_id or next_invoice_id(existing_invoice_ids)
    status_value = status.value if isinstance(status, InvoiceStatus) else str(status).lower()
    record: dict[str, Any] = {
        "invoice_id": resolved_id,
        "client_id": client_id,
        "issue_date": format_date(require_date(issue_date, "issue_date")),
        "amount": decimal_string(amount),
        "currency": currency.upper(),
        "status": status_value,
        "partial_payments": [],
    }
    parsed_due = parse_date(due_date)
    if parsed_due:
        record["due_date"] = format_date(parsed_due)
    if payment_terms_days is not None:
        record["payment_terms_days"] = int(payment_terms_days)
    # Re-parse through the normal model to catch bad amounts, dates, currency casing, or status.
    invoice_from_dict(record)
    return record


def issues_to_dicts(issues: Iterable[ValidationIssue]) -> list[dict[str, Any]]:
    return [
        {
            "code": issue.code,
            "message": issue.message,
            "severity": issue.severity.value,
            "invoice_id": issue.invoice_id,
            "client_id": issue.client_id,
        }
        for issue in issues
    ]


__all__ = [
    "AgingBucket",
    "AgingRecord",
    "AsyncDryRunTransport",
    "BusinessProfile",
    "Channel",
    "ClientAccount",
    "DryRunTransport",
    "Invoice",
    "InvoiceAgingClient",
    "InvoiceStatus",
    "PartialPayment",
    "Reminder",
    "ReminderStage",
    "ValidationIssue",
    "ValidationSeverity",
    "bucket_for_invoice",
    "create_invoice_record",
    "channel_for_stage",
    "decimal_string",
    "end_of_month",
    "format_date",
    "format_money",
    "import_csv",
    "issues_to_dicts",
    "load_ledger",
    "money",
    "next_business_day",
    "next_invoice_id",
    "normalize_israeli_phone",
    "parse_date",
    "render_message",
    "requires_human_review",
    "sample_ledger",
    "save_ledger",
    "stage_for_bucket",
]
