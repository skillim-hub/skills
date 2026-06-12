#!/usr/bin/env python3
"""Typed Arnona payment reminder client.

Build reminder schedules, payment instructions, validation reports, JSON exports,
and ICS calendar files for municipal property tax payments in Israel.
"""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence

Language = Literal["en", "he"]
BillStatus = Literal["paid", "overdue", "due_today", "due_soon", "upcoming"]
Severity = Literal["info", "warning", "urgent", "overdue"]


class ArnonaValidationError(ValueError):
    """Raised when a bill or profile cannot be used safely."""


def parse_date(value: str | date | datetime) -> date:
    """Parse ISO YYYY-MM-DD, Israeli DD/MM/YYYY, or DD-MM-YYYY date strings."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ArnonaValidationError(
        f"Invalid date '{value}'. Use YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY."
    )


def format_date(value: date, language: Language = "en") -> str:
    """Format date for English or Hebrew payment communications."""
    if language == "he":
        return value.strftime("%d/%m/%Y")
    return value.isoformat()


def money_nis(value: Decimal | float | int | str, language: Language = "en") -> str:
    """Format New Israeli Shekel amounts consistently."""
    amount = _as_decimal(value)
    rendered = f"{amount:,.2f}"
    if language == "he":
        return f"₪{rendered}"
    return f"₪{rendered}"


def _as_decimal(value: Decimal | float | int | str) -> Decimal:
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ArnonaValidationError(f"Invalid money amount '{value}'.") from exc


def _add_months(day: date, months: int) -> date:
    month = day.month - 1 + months
    year = day.year + month // 12
    month = month % 12 + 1
    dim = [31, 29 if _is_leap_year(year) else 28, 31, 30, 31, 30,
           31, 31, 30, 31, 30, 31][month - 1]
    return date(year, month, min(day.day, dim))


def _is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9א-ת]+", "-", value.strip()).strip("-").lower()
    return cleaned or "municipality"


@dataclass(slots=True)
class MunicipalityProfile:
    """Municipality-specific payment metadata."""

    name: str
    hebrew_name: str | None = None
    municipality_code: str | None = None
    payment_url: str | None = None
    service_url: str | None = None
    arnona_order_url: str | None = None
    payment_methods: list[str] = field(
        default_factory=lambda: ["credit_card", "bank_transfer", "standing_order"]
    )
    account_reference_label: str = "payer/account number"
    bill_reference_label: str = "bill/voucher number"
    identity_reference_label: str = "ID number or company number"
    supports_online_payment: bool = True
    supports_installments: bool = True
    notes: list[str] = field(default_factory=list)

    @property
    def effective_hebrew_name(self) -> str:
        return self.hebrew_name or self.name


@dataclass(slots=True)
class ArnonaBill:
    """A normalized municipal Arnona bill."""

    municipality: str
    account_reference: str
    bill_number: str
    taxpayer_name: str
    property_address: str
    period_start: date
    period_end: date
    issue_date: date
    due_date: date
    amount_nis: Decimal
    status: Literal["unpaid", "paid"] = "unpaid"
    payer_id: str | None = None
    payment_url: str | None = None
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ArnonaBill":
        required = [
            "municipality",
            "account_reference",
            "bill_number",
            "taxpayer_name",
            "property_address",
            "period_start",
            "period_end",
            "issue_date",
            "due_date",
            "amount_nis",
        ]
        missing = [field_name for field_name in required if not payload.get(field_name)]
        if missing:
            raise ArnonaValidationError(f"Missing required fields: {', '.join(missing)}")

        return cls(
            municipality=str(payload["municipality"]).strip(),
            account_reference=str(payload["account_reference"]).strip(),
            bill_number=str(payload["bill_number"]).strip(),
            taxpayer_name=str(payload["taxpayer_name"]).strip(),
            property_address=str(payload["property_address"]).strip(),
            period_start=parse_date(payload["period_start"]),
            period_end=parse_date(payload["period_end"]),
            issue_date=parse_date(payload["issue_date"]),
            due_date=parse_date(payload["due_date"]),
            amount_nis=_as_decimal(payload["amount_nis"]),
            status=str(payload.get("status", "unpaid")).strip().lower(),  # type: ignore[arg-type]
            payer_id=str(payload["payer_id"]).strip() if payload.get("payer_id") else None,
            payment_url=str(payload["payment_url"]).strip() if payload.get("payment_url") else None,
            notes=list(payload.get("notes", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "municipality": self.municipality,
            "account_reference": self.account_reference,
            "bill_number": self.bill_number,
            "taxpayer_name": self.taxpayer_name,
            "property_address": self.property_address,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "issue_date": self.issue_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "amount_nis": str(self.amount_nis),
            "status": self.status,
            "payer_id": self.payer_id,
            "payment_url": self.payment_url,
            "notes": self.notes,
        }


@dataclass(slots=True, frozen=True)
class ReminderRule:
    """A reminder offset relative to the due date."""

    days_before_due: int
    channel: Literal["calendar", "email", "sms", "task"] = "calendar"
    label: str = "standard"


@dataclass(slots=True)
class ReminderEvent:
    """One scheduled reminder."""

    send_on: date
    title: str
    message: str
    severity: Severity
    days_to_due: int
    channel: str
    bill_number: str
    municipality: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "send_on": self.send_on.isoformat(),
            "title": self.title,
            "message": self.message,
            "severity": self.severity,
            "days_to_due": self.days_to_due,
            "channel": self.channel,
            "bill_number": self.bill_number,
            "municipality": self.municipality,
        }


@dataclass(slots=True)
class PaymentInstruction:
    """Human-readable payment instructions for one bill."""

    summary: str
    required_fields: list[str]
    steps: list[str]
    warnings: list[str]
    payment_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReminderPlan:
    """Full output bundle for a bill."""

    bill: ArnonaBill
    status: BillStatus
    events: list[ReminderEvent]
    instructions: PaymentInstruction
    validation_warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "bill": self.bill.to_dict(),
            "status": self.status,
            "events": [event.to_dict() for event in self.events],
            "instructions": self.instructions.to_dict(),
            "validation_warnings": self.validation_warnings,
        }

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)


DEFAULT_REMINDER_RULES: tuple[ReminderRule, ...] = (
    ReminderRule(30, "calendar", "early"),
    ReminderRule(14, "calendar", "standard"),
    ReminderRule(7, "email", "standard"),
    ReminderRule(3, "sms", "urgent"),
    ReminderRule(1, "task", "urgent"),
    ReminderRule(0, "calendar", "due_today"),
    ReminderRule(-7, "task", "overdue_followup"),
)


class ArnonaPaymentReminderClient:
    """Build payment-reminder artifacts for Israeli Arnona bills."""

    def __init__(
        self,
        profiles: dict[str, MunicipalityProfile] | None = None,
        default_rules: Sequence[ReminderRule] = DEFAULT_REMINDER_RULES,
    ) -> None:
        self.profiles = profiles or {}
        self.default_rules = tuple(default_rules)

    @classmethod
    def with_default_profiles(cls) -> "ArnonaPaymentReminderClient":
        tel_aviv = MunicipalityProfile(
            name="Tel Aviv-Yafo",
            hebrew_name="תל אביב-יפו",
            municipality_code="5000",
            payment_url="https://tlvpay.tel-aviv.gov.il/he/s/arnona",
            service_url="https://www.tel-aviv.gov.il/en/Live/ArnonaAndCityTaxes/Pages/default.aspx",
            arnona_order_url="https://www.tel-aviv.gov.il/About/Pages/Payments.aspx",
            notes=["Verify the active municipal payment page and voucher fields before sending instructions."],
        )
        jerusalem = MunicipalityProfile(
            name="Jerusalem",
            hebrew_name="ירושלים",
            municipality_code="3000",
            payment_url="https://www.jerusalem.muni.il/he/residents/arnona/property-tax-payment/",
            service_url="https://www.jerusalem.muni.il/he/online-services/arnona/",
            arnona_order_url="https://www.jerusalem.muni.il/en/residents/arnona/annual-arnona/",
            notes=["Check whether the bill is assigned to residential, business, or mixed use."],
        )
        haifa = MunicipalityProfile(
            name="Haifa",
            hebrew_name="חיפה",
            municipality_code="4000",
            payment_url="https://www.haifa.muni.il/resident-service/arnona/tax-payment/",
            service_url="https://www.haifa.muni.il/resident-service/arnona/",
            arnona_order_url="https://www.haifa.muni.il/resident-service/arnona/",
        )
        profiles = {
            "tel-aviv": tel_aviv,
            "tel-aviv-yafo": tel_aviv,
            "tel-aviv-jaffa": tel_aviv,
            "תל-אביב-יפו": tel_aviv,
            "תל-אביב": tel_aviv,
            "jerusalem": jerusalem,
            "ירושלים": jerusalem,
            "haifa": haifa,
            "חיפה": haifa,
        }
        return cls(profiles=profiles)

    def register_profile(self, key: str, profile: MunicipalityProfile) -> None:
        self.profiles[_slugify(key)] = profile

    def profile_for(self, municipality: str) -> MunicipalityProfile:
        key = _slugify(municipality)
        if key in self.profiles:
            return self.profiles[key]
        normalized_name = municipality.strip()
        return MunicipalityProfile(name=normalized_name, hebrew_name=normalized_name)

    def validate_bill(self, bill: ArnonaBill | dict[str, Any]) -> list[str]:
        normalized = bill if isinstance(bill, ArnonaBill) else ArnonaBill.from_dict(bill)
        warnings: list[str] = []

        if normalized.status not in {"unpaid", "paid"}:
            raise ArnonaValidationError("status must be 'unpaid' or 'paid'.")

        if normalized.amount_nis <= Decimal("0.00"):
            raise ArnonaValidationError("amount_nis must be positive.")

        if normalized.period_start > normalized.period_end:
            raise ArnonaValidationError("period_start must be on or before period_end.")

        if normalized.issue_date > normalized.due_date:
            raise ArnonaValidationError("issue_date must be on or before due_date.")

        if len(normalized.bill_number) < 3:
            warnings.append("Bill number is unusually short; verify against the voucher.")

        if len(normalized.account_reference) < 3:
            warnings.append("Account reference is unusually short; verify the payer/account number.")

        if normalized.payer_id and not is_valid_israeli_id_or_company(normalized.payer_id):
            warnings.append("Payer identifier does not pass common Israeli ID/company validation.")

        if normalized.payment_url and not normalized.payment_url.startswith(("https://", "http://")):
            warnings.append("Payment URL does not look like a web URL.")

        return warnings

    def classify_bill(self, bill: ArnonaBill, as_of: date | str | None = None) -> BillStatus:
        as_of_date = parse_date(as_of or date.today())
        if bill.status == "paid":
            return "paid"
        days = (bill.due_date - as_of_date).days
        if days < 0:
            return "overdue"
        if days == 0:
            return "due_today"
        if days <= 7:
            return "due_soon"
        return "upcoming"

    def build_reminder_plan(
        self,
        bill: ArnonaBill | dict[str, Any],
        *,
        as_of: date | str | None = None,
        language: Language = "en",
        include_past: bool = False,
        rules: Sequence[ReminderRule] | None = None,
    ) -> ReminderPlan:
        normalized = bill if isinstance(bill, ArnonaBill) else ArnonaBill.from_dict(bill)
        warnings = self.validate_bill(normalized)
        as_of_date = parse_date(as_of or date.today())
        status = self.classify_bill(normalized, as_of_date)
        profile = self.profile_for(normalized.municipality)
        events = self._events_for_bill(
            normalized,
            profile=profile,
            as_of=as_of_date,
            language=language,
            include_past=include_past,
            rules=tuple(rules or self.default_rules),
        )
        instructions = self.payment_instructions(normalized, profile=profile, language=language)
        return ReminderPlan(
            bill=normalized,
            status=status,
            events=events,
            instructions=instructions,
            validation_warnings=warnings,
        )

    async def async_build_reminder_plan(
        self,
        bill: ArnonaBill | dict[str, Any],
        *,
        as_of: date | str | None = None,
        language: Language = "en",
        include_past: bool = False,
        rules: Sequence[ReminderRule] | None = None,
    ) -> ReminderPlan:
        return await asyncio.to_thread(
            self.build_reminder_plan,
            bill,
            as_of=as_of,
            language=language,
            include_past=include_past,
            rules=rules,
        )

    async def async_validate_bill(self, bill: ArnonaBill | dict[str, Any]) -> list[str]:
        return await asyncio.to_thread(self.validate_bill, bill)

    def _events_for_bill(
        self,
        bill: ArnonaBill,
        *,
        profile: MunicipalityProfile,
        as_of: date,
        language: Language,
        include_past: bool,
        rules: Sequence[ReminderRule],
    ) -> list[ReminderEvent]:
        if bill.status == "paid":
            return []

        events: list[ReminderEvent] = []
        for rule in rules:
            send_on = bill.due_date - timedelta(days=rule.days_before_due)
            if not include_past and send_on < as_of:
                continue
            days_to_due = (bill.due_date - send_on).days
            severity = self._severity(rule.days_before_due)
            title = self._title(bill, profile, rule.days_before_due, language)
            message = self._message(bill, profile, rule.days_before_due, language)
            events.append(
                ReminderEvent(
                    send_on=send_on,
                    title=title,
                    message=message,
                    severity=severity,
                    days_to_due=days_to_due,
                    channel=rule.channel,
                    bill_number=bill.bill_number,
                    municipality=profile.name,
                )
            )

        if not events and as_of > bill.due_date and bill.status != "paid":
            days_overdue = (as_of - bill.due_date).days
            events.append(
                ReminderEvent(
                    send_on=as_of,
                    title=self._overdue_title(bill, profile, language),
                    message=self._overdue_message(bill, profile, days_overdue, language),
                    severity="overdue",
                    days_to_due=-days_overdue,
                    channel="task",
                    bill_number=bill.bill_number,
                    municipality=profile.name,
                )
            )

        return sorted(events, key=lambda event: event.send_on)

    def _severity(self, days_before_due: int) -> Severity:
        if days_before_due < 0:
            return "overdue"
        if days_before_due <= 1:
            return "urgent"
        if days_before_due <= 7:
            return "warning"
        return "info"

    def _title(
        self,
        bill: ArnonaBill,
        profile: MunicipalityProfile,
        days_before_due: int,
        language: Language,
    ) -> str:
        if language == "he":
            name = profile.effective_hebrew_name
            if days_before_due < 0:
                return f"בדיקת פיגור בתשלום ארנונה - {name}"
            if days_before_due == 0:
                return f"היום מועד תשלום הארנונה - {name}"
            return f"תזכורת ארנונה: {days_before_due} ימים לתשלום - {name}"
        if days_before_due < 0:
            return f"Check overdue Arnona payment - {profile.name}"
        if days_before_due == 0:
            return f"Arnona payment due today - {profile.name}"
        return f"Arnona reminder: {days_before_due} days to pay - {profile.name}"

    def _message(
        self,
        bill: ArnonaBill,
        profile: MunicipalityProfile,
        days_before_due: int,
        language: Language,
    ) -> str:
        payment_url = bill.payment_url or profile.payment_url or "the municipality payment page"
        if language == "he":
            due = format_date(bill.due_date, "he")
            amount = money_nis(bill.amount_nis, "he")
            if days_before_due < 0:
                return (
                    f"בדוק אם חשבון הארנונה {bill.bill_number} שולם. "
                    f"מועד התשלום היה {due}, סכום החיוב {amount}. "
                    f"היכנס לאזור התשלומים של {profile.effective_hebrew_name}: {payment_url}."
                )
            if days_before_due == 0:
                return (
                    f"שלם היום את חשבון הארנונה {bill.bill_number}. "
                    f"סכום לתשלום: {amount}. כתובת נכס: {bill.property_address}. "
                    f"שמור אישור תשלום מספרי לאחר התשלום."
                )
            return (
                f"נותרו {days_before_due} ימים עד מועד תשלום הארנונה {due}. "
                f"סכום לתשלום: {amount}; מספר שובר: {bill.bill_number}; "
                f"מספר משלם/חשבון: {bill.account_reference}."
            )

        due = format_date(bill.due_date, "en")
        amount = money_nis(bill.amount_nis, "en")
        if days_before_due < 0:
            return (
                f"Check whether Arnona bill {bill.bill_number} was paid. "
                f"The due date was {due}; amount {amount}. "
                f"Use {payment_url} or contact the municipality before collection costs accrue."
            )
        if days_before_due == 0:
            return (
                f"Pay Arnona bill {bill.bill_number} today. Amount: {amount}. "
                f"Property: {bill.property_address}. Save the digital receipt after payment."
            )
        return (
            f"{days_before_due} days remain before the Arnona due date {due}. "
            f"Amount: {amount}; bill number: {bill.bill_number}; "
            f"payer/account number: {bill.account_reference}."
        )

    def _overdue_title(
        self, bill: ArnonaBill, profile: MunicipalityProfile, language: Language
    ) -> str:
        if language == "he":
            return f"ארנונה בפיגור - {profile.effective_hebrew_name}"
        return f"Overdue Arnona payment - {profile.name}"

    def _overdue_message(
        self,
        bill: ArnonaBill,
        profile: MunicipalityProfile,
        days_overdue: int,
        language: Language,
    ) -> str:
        if language == "he":
            return (
                f"חשבון הארנונה {bill.bill_number} בפיגור של {days_overdue} ימים. "
                f"שלם בהקדם או פנה למחלקת הגבייה של {profile.effective_hebrew_name}. "
                f"בדוק הצמדה, ריבית, הוצאות גבייה והסדר תשלומים לפני ביצוע תשלום חלקי."
            )
        return (
            f"Arnona bill {bill.bill_number} is {days_overdue} days overdue. "
            f"Pay promptly or contact {profile.name} collection services. "
            f"Check linkage, interest, collection costs, and payment arrangements before partial payment."
        )

    def payment_instructions(
        self,
        bill: ArnonaBill,
        *,
        profile: MunicipalityProfile | None = None,
        language: Language = "en",
    ) -> PaymentInstruction:
        resolved = profile or self.profile_for(bill.municipality)
        payment_url = bill.payment_url or resolved.payment_url
        if language == "he":
            account_label = "מספר משלם/חשבון"
            bill_label = "מספר שובר"
            identity_label = "מספר זהות או מספר חברה"
            summary = (
                f"הכן תשלום ארנונה ל-{resolved.effective_hebrew_name} עבור "
                f"{bill.property_address}, סכום {money_nis(bill.amount_nis, 'he')}."
            )
            required = [
                account_label,
                bill_label,
                identity_label,
                "סכום לתשלום",
                "תקופת חיוב",
            ]
            steps = [
                "פתח את אתר התשלומים הרשמי של הרשות המקומית או את הקישור שמופיע בשובר.",
                "בחר תשלום ארנונה/מסים עירוניים, לא תשלום מים או אגרות אחרות.",
                f"הזן {account_label}: {bill.account_reference}.",
                f"הזן {bill_label}: {bill.bill_number}.",
                "אמת את שם המשלם, כתובת הנכס, תקופת החיוב וסכום החיוב מול השובר.",
                "בחר אמצעי תשלום מתאים: כרטיס אשראי, העברה בנקאית, הוראת קבע או קופה עירונית.",
                "בצע את התשלום רק לאחר התאמה מלאה של פרטי הנכס והתקופה.",
                "שמור קבלה דיגיטלית, מספר אישור ותיעוד חשבונאי.",
            ]
            warnings = [
                "אל תשלם שובר שאינו תואם את כתובת הנכס או תקופת החיוב.",
                "בדוק אם קיימת הנחה, פטור, השגה פתוחה או הסדר תשלומים לפני תשלום מלא.",
                "בתשלום לאחר המועד בדוק ריבית, הצמדה והוצאות גבייה מול הרשות.",
            ]
        else:
            summary = (
                f"Prepare Arnona payment to {resolved.name} for {bill.property_address}, "
                f"amount {money_nis(bill.amount_nis, 'en')}."
            )
            required = [
                resolved.account_reference_label,
                resolved.bill_reference_label,
                resolved.identity_reference_label,
                "amount to pay",
                "billing period",
            ]
            steps = [
                "Open the official municipality payment page or the payment link printed on the voucher.",
                "Select Arnona or municipal taxes, not water, parking, education, or other fees.",
                f"Enter {resolved.account_reference_label}: {bill.account_reference}.",
                f"Enter {resolved.bill_reference_label}: {bill.bill_number}.",
                "Verify payer name, property address, billing period, and amount against the voucher.",
                "Choose an allowed payment method: credit card, bank transfer, standing order, or municipal cashier.",
                "Submit payment only after every property and period detail matches the bill.",
                "Save the receipt, confirmation number, and accounting record.",
            ]
            warnings = [
                "Do not pay a voucher that mismatches the property address or billing period.",
                "Check discount, exemption, objection, or installment status before paying the full amount.",
                "For late payment, verify interest, linkage, and collection costs with the municipality.",
            ]

        if not resolved.supports_online_payment and payment_url is None:
            warnings.append("Online payment is not marked as supported; prepare an offline payment route.")

        return PaymentInstruction(
            summary=summary,
            required_fields=required,
            steps=steps,
            warnings=warnings,
            payment_url=payment_url,
        )

    def next_due_dates(
        self,
        start_due_date: date | str,
        *,
        count: int = 6,
        interval_months: int = 2,
    ) -> list[date]:
        if count < 1:
            raise ArnonaValidationError("count must be at least 1.")
        if interval_months < 1:
            raise ArnonaValidationError("interval_months must be at least 1.")
        current = parse_date(start_due_date)
        dates: list[date] = []
        for index in range(count):
            dates.append(_add_months(current, index * interval_months))
        return dates

    def export_ics(self, plan: ReminderPlan, calendar_name: str = "Arnona reminders") -> str:
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//arnona-payment-reminder//EN",
            f"X-WR-CALNAME:{_ics_escape(calendar_name)}",
        ]
        for event in plan.events:
            uid = f"{uuid.uuid5(uuid.NAMESPACE_URL, event.bill_number + event.send_on.isoformat())}.arnona-payment-reminder.local"
            body = event.message + "\n\nBill: " + event.bill_number
            lines.extend(
                [
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
                    f"DTSTART;VALUE=DATE:{event.send_on.strftime('%Y%m%d')}",
                    f"SUMMARY:{_ics_escape(event.title)}",
                    f"DESCRIPTION:{_ics_escape(body)}",
                    "END:VEVENT",
                ]
            )
        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"

    def save_json(self, plan: ReminderPlan, path: str | Path) -> Path:
        target = Path(path)
        target.write_text(plan.to_json(), encoding="utf-8")
        return target

    def save_ics(self, plan: ReminderPlan, path: str | Path) -> Path:
        target = Path(path)
        target.write_text(self.export_ics(plan), encoding="utf-8")
        return target


def is_valid_israeli_id_or_company(value: str) -> bool:
    """Validate common 9-digit Israeli ID/company-number checksum."""
    digits = re.sub(r"\D", "", value)
    if len(digits) != 9:
        return False
    total = 0
    for index, char in enumerate(digits):
        num = int(char) * (1 if index % 2 == 0 else 2)
        total += num if num < 10 else num - 9
    return total % 10 == 0


def _ics_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def load_bill_file(path: str | Path) -> ArnonaBill:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return ArnonaBill.from_dict(payload)


def load_profiles_file(path: str | Path) -> dict[str, MunicipalityProfile]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    profiles: dict[str, MunicipalityProfile] = {}
    for key, item in payload.items():
        profiles[_slugify(key)] = MunicipalityProfile(**item)
    return profiles


def plan_from_file(
    bill_path: str | Path,
    *,
    profiles_path: str | Path | None = None,
    as_of: str | date | None = None,
    language: Language = "en",
    include_past: bool = False,
) -> ReminderPlan:
    profiles = load_profiles_file(profiles_path) if profiles_path else None
    client = ArnonaPaymentReminderClient.with_default_profiles() if profiles is None else ArnonaPaymentReminderClient(profiles=profiles)
    return client.build_reminder_plan(
        load_bill_file(bill_path),
        as_of=as_of,
        language=language,
        include_past=include_past,
    )


def make_bill_id(bill: ArnonaBill | dict[str, Any]) -> str:
    """Return a stable local identifier for a normalized bill."""
    normalized = bill if isinstance(bill, ArnonaBill) else ArnonaBill.from_dict(bill)
    seed = "|".join(
        [
            normalized.municipality,
            normalized.account_reference,
            normalized.bill_number,
            normalized.due_date.isoformat(),
            str(normalized.amount_nis),
        ]
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


__all__ = [
    "ArnonaBill",
    "ArnonaPaymentReminderClient",
    "ArnonaValidationError",
    "DEFAULT_REMINDER_RULES",
    "MunicipalityProfile",
    "PaymentInstruction",
    "ReminderEvent",
    "ReminderPlan",
    "ReminderRule",
    "format_date",
    "is_valid_israeli_id_or_company",
    "load_bill_file",
    "load_profiles_file",
    "make_bill_id",
    "money_nis",
    "parse_date",
    "plan_from_file",
]
