#!/usr/bin/env python3
"""Typed helper library for Israeli event scheduling and Hebrew RSVP workflows."""

from __future__ import annotations

import asyncio
import csv
import json
import math
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Literal, Optional


CURRENT_ISRAEL_VAT_RATE = 0.18
ACUM_FAMILY_EVENT_LICENSE_NIS = 395.30
ISRAEL_INVOICE_ALLOCATION_THRESHOLDS: tuple[tuple[date, float], ...] = (
    (date(2026, 6, 1), 5_000.0),
    (date(2026, 1, 1), 10_000.0),
    (date(2025, 1, 1), 20_000.0),
    (date(2024, 1, 1), 25_000.0),
)


class EventType(str, Enum):
    WEDDING = "wedding"
    BAR_MITZVAH = "bar_mitzvah"
    BAT_MITZVAH = "bat_mitzvah"
    BRIT_MILAH = "brit_milah"
    NAMING_CEREMONY = "naming_ceremony"
    FAMILY_EVENT = "family_event"
    COMMUNITY_EVENT = "community_event"
    CUSTOMER_EVENT = "customer_event"


class RSVPStatus(str, Enum):
    CONFIRMED = "confirmed"
    DECLINED = "declined"
    TENTATIVE = "tentative"
    NO_RESPONSE = "no_response"


@dataclass(slots=True)
class Venue:
    name: str = ""
    city: str = ""
    capacity: int = 0
    minimum_guests: int = 0
    per_plate_nis: float = 0.0
    parking_spaces: int = 0
    kosher_certificate_required: bool = False
    accessibility_confirmed: bool = False
    weather_backup: str = ""
    notes: str = ""


@dataclass(slots=True)
class Guest:
    name: str
    phone: str = ""
    party_size_invited: int = 1
    party_size_confirmed: int = 0
    status: RSVPStatus = RSVPStatus.NO_RESPONSE
    group: str = ""
    children_count: int = 0
    dietary: str = ""
    accessibility: str = ""
    needs_transport: bool = False
    language: str = "he"
    notes: str = ""

    def normalized_phone(self) -> str:
        return normalize_israeli_phone(self.phone) if self.phone else ""


@dataclass(slots=True)
class Vendor:
    category: str
    name: str
    quote_nis: float
    deposit_nis: float = 0.0
    due_date: Optional[date] = None
    contract_signed: bool = False
    contact: str = ""
    vat_included: bool = True
    notes: str = ""


@dataclass(slots=True)
class Milestone:
    due_date: date
    title: str
    owner: str = "event_manager"
    urgency: Literal["low", "medium", "high", "critical"] = "medium"
    notes: str = ""


@dataclass(slots=True)
class EventPlan:
    event_type: EventType
    event_date: date
    title: str
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    city: str = ""
    venue: Venue = field(default_factory=Venue)
    guests: list[Guest] = field(default_factory=list)
    vendors: list[Vendor] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)
    timezone: str = "Asia/Jerusalem"
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def invited_people(self) -> int:
        return sum(max(0, guest.party_size_invited) for guest in self.guests)

    @property
    def confirmed_people(self) -> int:
        return sum(
            max(0, guest.party_size_confirmed)
            for guest in self.guests
            if guest.status == RSVPStatus.CONFIRMED
        )

    @property
    def expected_people(self) -> int:
        return sum(
            max(0, guest.party_size_confirmed or guest.party_size_invited)
            for guest in self.guests
            if guest.status in {RSVPStatus.CONFIRMED, RSVPStatus.TENTATIVE}
        )


def parse_israeli_date(value: str | date | datetime) -> date:
    """Parse DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, date, or datetime into a date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value!r}; expected DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD")


def format_israeli_date(value: date | datetime | str) -> str:
    """Format a value as DD/MM/YYYY."""
    return parse_israeli_date(value).strftime("%d/%m/%Y")


def format_nis(amount: float | int) -> str:
    """Format an amount in Israeli shekels."""
    rounded = int(round(float(amount)))
    return f"₪{rounded:,.0f}"


def israel_invoice_allocation_threshold(invoice_date: str | date | datetime) -> float | None:
    """Return the Israel invoice allocation threshold before VAT for the invoice date.

    The thresholds are operational planning values based on current Tax Authority
    guidance as verified on 04/06/2026. Check the official portal before issuing
    or accepting a tax invoice.
    """
    day = parse_israeli_date(invoice_date)
    for effective_date, threshold in ISRAEL_INVOICE_ALLOCATION_THRESHOLDS:
        if day >= effective_date:
            return threshold
    return None


def requires_israel_invoice_allocation(
    invoice_amount_before_vat_nis: float | int,
    invoice_date: str | date | datetime,
    *,
    customer_is_authorized_dealer: bool = True,
    customer_requested_allocation: bool = True,
    vat_amount_nis: float | int | None = None,
) -> bool:
    """Return whether an invoice should be flagged for allocation-number follow-up."""
    threshold = israel_invoice_allocation_threshold(invoice_date)
    if threshold is None:
        return False
    if not customer_is_authorized_dealer:
        return False
    if vat_amount_nis is not None and float(vat_amount_nis) <= 0:
        return False
    if not customer_requested_allocation:
        return False
    return float(invoice_amount_before_vat_nis) > threshold


def normalize_israeli_phone(phone: str) -> str:
    """Normalize common Israeli phone formats to +972 format."""
    raw = phone.strip()
    if not raw:
        raise ValueError("Phone number is empty")
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("00"):
        digits = digits[2:]
    if digits.startswith("972"):
        national = digits[3:]
        if national.startswith("0"):
            national = national[1:]
        if 8 <= len(national) <= 9:
            return "+972" + national
    if digits.startswith("0") and 9 <= len(digits) <= 10:
        return "+972" + digits[1:]
    if raw.startswith("+") and 8 <= len(digits) <= 15:
        return "+" + digits
    raise ValueError(f"Cannot normalize phone number: {phone!r}")


def calculate_brit_milah_target_date(
    birth_date: str | date | datetime,
    *,
    after_sunset: bool = False,
    medically_cleared: bool = True,
) -> dict[str, Any]:
    """Calculate an operational target date for brit milah planning.

    Jewish-law and medical edge cases require qualified confirmation. This helper
    returns a planning target and warnings only.
    """
    born = parse_israeli_date(birth_date)
    target = born + timedelta(days=8 if after_sunset else 7)
    warnings: list[str] = []
    if after_sunset:
        warnings.append("Birth after sunset can shift the halachic day; confirm with rabbinic authority.")
    if not medically_cleared:
        warnings.append("Medical clearance is not confirmed; postpone until cleared.")
    warnings.append("Verify Shabbat, holiday, jaundice, weight, and medical edge cases with qualified guidance.")
    return {"target_date": target, "target_date_display": format_israeli_date(target), "warnings": warnings}


def map_rsvp_status(value: str | RSVPStatus) -> RSVPStatus:
    """Map Hebrew/English free text to a controlled RSVP status."""
    if isinstance(value, RSVPStatus):
        return value
    text = str(value).strip().lower()
    confirmed = {"confirmed", "yes", "y", "כן", "מגיע", "מגיעה", "מגיעים", "אישר", "אישרה"}
    declined = {"declined", "no", "n", "לא", "לא מגיע", "לא מגיעה", "לא מגיעים"}
    tentative = {"tentative", "maybe", "אולי", "מתלבט", "מתלבטת", "נראה"}
    no_response = {"", "no_response", "pending", "אין תשובה", "לא ענו", "ללא מענה"}
    if text in confirmed:
        return RSVPStatus.CONFIRMED
    if text in declined:
        return RSVPStatus.DECLINED
    if text in tentative:
        return RSVPStatus.TENTATIVE
    if text in no_response:
        return RSVPStatus.NO_RESPONSE
    raise ValueError(f"Unsupported RSVP status: {value!r}")


class EventSchedulerClient:
    """Synchronous event planning helper."""

    def create_plan(
        self,
        *,
        event_type: EventType | str,
        event_date: str | date | datetime,
        title: str,
        city: str = "",
        venue: Venue | None = None,
    ) -> EventPlan:
        event_type_enum = EventType(event_type)
        return EventPlan(
            event_type=event_type_enum,
            event_date=parse_israeli_date(event_date),
            title=title,
            city=city,
            venue=venue or Venue(city=city),
        )

    def plan_response(self, plan: EventPlan, *, saved_path: str | Path | None = None) -> dict[str, Any]:
        """Return a small response object that can be chained by CLI or API callers."""
        response: dict[str, Any] = {
            "event_id": plan.event_id,
            "event_type": plan.event_type.value,
            "event_date": format_israeli_date(plan.event_date),
            "title": plan.title,
            "city": plan.city,
        }
        if saved_path is not None:
            response["path"] = str(saved_path)
        return response

    def require_event_id(self, plan: EventPlan, event_id: str) -> None:
        """Validate that a plan matches the caller-supplied event identifier."""
        if plan.event_id != event_id:
            raise ValueError("event_id does not match the plan file")

    def add_guest(self, plan: EventPlan, guest: Guest) -> EventPlan:
        """Append a guest to a plan and return the same plan for chaining."""
        if not guest.name.strip():
            raise ValueError("guest name is required")
        plan.guests.append(guest)
        return plan

    def build_rsvp_message(
        self,
        *,
        name: str,
        event_title: str,
        event_date: str | date | datetime,
        deadline: str | date | datetime | None = None,
        venue_name: str = "",
        opt_out: bool = True,
        final_logistics: bool = False,
        address: str = "",
        reception_time: str = "",
        ceremony_time: str = "",
        transport_note: str = "",
        contact_name: str = "",
    ) -> str:
        event_date_text = format_israeli_date(event_date)
        if final_logistics:
            return (
                f"שלום {name}, מחכים לראותך ב{event_title}.\n"
                f"הגעה: {venue_name or 'המקום שצוין בהזמנה'}"
                f"{', ' + address if address else ''}. "
                f"קבלת פנים: {reception_time or 'לפי ההזמנה'}. "
                f"טקס: {ceremony_time or 'לפי ההזמנה'}.\n"
                f"חניה/הסעה: {transport_note or 'פרטים נשלחו בנפרד'}. "
                f"במקרה שינוי, נא לעדכן את {contact_name or 'איש הקשר'}."
            )
        deadline_text = format_israeli_date(deadline) if deadline else ""
        if deadline_text:
            message = (
                f"שלום {name}, תזכורת קצרה לאישור הגעה ל{event_title} ב-{event_date_text}.\n"
                f"כדי לסגור סידורי הושבה וקייטרינג, נא להשיב עד {deadline_text}: "
                "מגיעים / לא מגיעים / עדיין לא בטוח."
            )
        else:
            message = (
                f"שלום {name}, נשמח לאישור הגעה ל{event_title} בתאריך {event_date_text}.\n"
                "נא להשיב במספר המגיעים, ילדים, רגישויות למזון וצורך בהסעה."
            )
        if opt_out:
            message += '\nלהסרה מרשימת עדכונים כתבו "הסר".'
        return message

    def estimate_budget(
        self,
        *,
        guest_count: int,
        per_plate_nis: float,
        fixed_costs_nis: float = 0.0,
        contingency_rate: float = 0.08,
    ) -> dict[str, Any]:
        if guest_count < 0:
            raise ValueError("guest_count must be non-negative")
        if per_plate_nis < 0 or fixed_costs_nis < 0:
            raise ValueError("costs must be non-negative")
        venue_total = guest_count * per_plate_nis
        subtotal = venue_total + fixed_costs_nis
        contingency = subtotal * contingency_rate
        total = subtotal + contingency
        return {
            "guest_count": guest_count,
            "per_plate_nis": per_plate_nis,
            "venue_total_nis": round(venue_total, 2),
            "fixed_costs_nis": round(fixed_costs_nis, 2),
            "contingency_nis": round(contingency, 2),
            "estimated_total_nis": round(total, 2),
            "estimated_total_display": format_nis(total),
        }

    def venue_capacity_check(self, *, expected_guests: int, venue: Venue) -> dict[str, Any]:
        warnings: list[str] = []
        status = "ok"
        if venue.capacity and expected_guests > venue.capacity:
            status = "over_capacity"
            warnings.append(f"Expected guests exceed capacity by {expected_guests - venue.capacity}.")
        if venue.minimum_guests and expected_guests < venue.minimum_guests:
            if status == "ok":
                status = "below_minimum"
            warnings.append(f"Expected guests are below venue minimum by {venue.minimum_guests - expected_guests}.")
        if not venue.accessibility_confirmed:
            warnings.append("Accessibility is not confirmed.")
        if venue.parking_spaces and expected_guests / 2 > venue.parking_spaces:
            warnings.append("Parking may be insufficient; consider shuttle or overflow lot.")
        return {"status": status, "expected_guests": expected_guests, "warnings": warnings}

    def generate_timeline(self, plan: EventPlan, *, today: str | date | datetime | None = None) -> list[Milestone]:
        event_date = plan.event_date
        milestones: list[Milestone]
        if plan.event_type == EventType.WEDDING:
            milestones = [
                Milestone(event_date - timedelta(days=270), "Define budget, guest bands, date constraints", "couple", "high"),
                Milestone(event_date - timedelta(days=210), "Shortlist venues and critical suppliers", "couple", "high"),
                Milestone(event_date - timedelta(days=150), "Sign venue and key supplier contracts", "couple", "critical"),
                Milestone(event_date - timedelta(days=90), "Earliest common planning checkpoint for marriage-file handling", "couple", "high"),
                Milestone(event_date - timedelta(days=45), "Send invitations and open RSVP tracking", "event_manager", "high"),
                Milestone(event_date - timedelta(days=21), "Latest common planning checkpoint for marriage-file handling", "couple", "critical"),
                Milestone(event_date - timedelta(days=14), "Freeze draft seating and transport manifest", "event_manager", "high"),
                Milestone(event_date - timedelta(days=3), "Verify music license, final count, suppliers, and payments", "event_manager", "critical"),
                Milestone(event_date - timedelta(days=1), "Send final logistics and print offline run sheet", "event_manager", "critical"),
            ]
        elif plan.event_type in {EventType.BAR_MITZVAH, EventType.BAT_MITZVAH}:
            milestones = [
                Milestone(event_date - timedelta(days=365), "Confirm Hebrew date, Torah portion, and synagogue slot", "family", "high"),
                Milestone(event_date - timedelta(days=180), "Choose event format and venue", "family", "high"),
                Milestone(event_date - timedelta(days=120), "Book photographer, DJ/activity, and lessons", "family", "medium"),
                Milestone(event_date - timedelta(days=42), "Send invitations with separate RSVP questions", "family", "high"),
                Milestone(event_date - timedelta(days=14), "Finalize seating, allergies, accessibility, and supervision", "event_manager", "critical"),
                Milestone(event_date - timedelta(days=3), "Confirm honors list, run sheet, and supplier arrivals", "family", "critical"),
            ]
        elif plan.event_type == EventType.BRIT_MILAH:
            milestones = [
                Milestone(event_date - timedelta(days=7), "Record birth time, medical status, and tentative ceremony date", "parents", "critical"),
                Milestone(event_date - timedelta(days=6), "Contact mohel or ceremony lead", "parents", "critical"),
                Milestone(event_date - timedelta(days=3), "Send conditional invitation to close guests", "family", "high"),
                Milestone(event_date - timedelta(days=2), "Confirm medical clearance, catering, chairs, parking, and quiet room", "family", "critical"),
                Milestone(event_date, "Run ceremony with non-parent logistics contact", "family", "critical"),
            ]
        else:
            milestones = [
                Milestone(event_date - timedelta(days=90), "Define event goal, budget, guest model, and compliance checkpoints", "organizer", "high"),
                Milestone(event_date - timedelta(days=60), "Book venue and key suppliers", "organizer", "high"),
                Milestone(event_date - timedelta(days=30), "Send invitations and start RSVP tracking", "organizer", "high"),
                Milestone(event_date - timedelta(days=10), "Finalize guest count, accessibility, dietary, and logistics", "organizer", "critical"),
                Milestone(event_date - timedelta(days=1), "Send final logistics and print offline run sheet", "organizer", "critical"),
            ]

        if today is not None:
            current = parse_israeli_date(today)
            for milestone in milestones:
                if milestone.due_date < current and milestone.urgency in {"high", "critical"}:
                    milestone.notes = (milestone.notes + " " if milestone.notes else "") + "Overdue relative to supplied date."
        plan.milestones = milestones
        return milestones

    def import_guests_csv(self, path: str | Path) -> list[Guest]:
        guests: list[Guest] = []
        with Path(path).open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                guests.append(
                    Guest(
                        name=row.get("name", "").strip(),
                        phone=row.get("phone", "").strip(),
                        party_size_invited=int(row.get("party_size_invited") or row.get("invited") or 1),
                        party_size_confirmed=int(row.get("party_size_confirmed") or row.get("confirmed_count") or 0),
                        status=map_rsvp_status(row.get("status", "no_response")),
                        group=row.get("group", "").strip(),
                        children_count=int(row.get("children_count") or 0),
                        dietary=row.get("dietary", "").strip(),
                        accessibility=row.get("accessibility", "").strip(),
                        needs_transport=str(row.get("needs_transport", "")).strip().lower() in {"1", "true", "yes", "כן"},
                        language=row.get("language", "he").strip() or "he",
                        notes=row.get("notes", "").strip(),
                    )
                )
        return guests

    def deduplicate_guests(self, guests: Iterable[Guest]) -> dict[str, Any]:
        unique: list[Guest] = []
        duplicates: list[tuple[Guest, Guest, str]] = []
        seen: dict[str, Guest] = {}
        for guest in guests:
            try:
                key = guest.normalized_phone() if guest.phone else f"name:{guest.name.strip().lower()}"
            except ValueError:
                key = f"name:{guest.name.strip().lower()}"
            if key in seen:
                duplicates.append((seen[key], guest, key))
                original = seen[key]
                original.party_size_invited = max(original.party_size_invited, guest.party_size_invited)
                original.party_size_confirmed = max(original.party_size_confirmed, guest.party_size_confirmed)
                if original.status == RSVPStatus.NO_RESPONSE:
                    original.status = guest.status
                if not original.dietary:
                    original.dietary = guest.dietary
                if not original.accessibility:
                    original.accessibility = guest.accessibility
                original.needs_transport = original.needs_transport or guest.needs_transport
            else:
                seen[key] = guest
                unique.append(guest)
        return {"unique": unique, "duplicates": duplicates}

    def rsvp_summary(self, guests: Iterable[Guest]) -> dict[str, Any]:
        guest_list = list(guests)
        households = len(guest_list)
        invited = sum(max(0, g.party_size_invited) for g in guest_list)
        confirmed = sum(max(0, g.party_size_confirmed) for g in guest_list if g.status == RSVPStatus.CONFIRMED)
        tentative = sum(max(0, g.party_size_confirmed or g.party_size_invited) for g in guest_list if g.status == RSVPStatus.TENTATIVE)
        declined_households = sum(1 for g in guest_list if g.status == RSVPStatus.DECLINED)
        no_response_households = sum(1 for g in guest_list if g.status == RSVPStatus.NO_RESPONSE)
        responded = households - no_response_households
        transport = sum(max(1, g.party_size_confirmed or g.party_size_invited) for g in guest_list if g.needs_transport)
        dietary = [g.name for g in guest_list if g.dietary]
        accessibility = [g.name for g in guest_list if g.accessibility]
        return {
            "households": households,
            "invited_people": invited,
            "confirmed_people": confirmed,
            "tentative_people": tentative,
            "declined_households": declined_households,
            "no_response_households": no_response_households,
            "response_rate": round(responded / households, 3) if households else 0.0,
            "transport_people": transport,
            "dietary_guest_names": dietary,
            "accessibility_guest_names": accessibility,
        }

    def assign_tables(self, guests: Iterable[Guest], *, table_size: int = 10) -> list[dict[str, Any]]:
        if table_size <= 0:
            raise ValueError("table_size must be positive")
        seated = [
            guest for guest in guests
            if guest.status == RSVPStatus.CONFIRMED and (guest.party_size_confirmed or guest.party_size_invited) > 0
        ]
        seated.sort(key=lambda g: (g.group, g.name))
        tables: list[dict[str, Any]] = []
        current: list[Guest] = []
        current_count = 0
        for guest in seated:
            size = guest.party_size_confirmed or guest.party_size_invited
            if current and current_count + size > table_size:
                tables.append({
                    "table_number": len(tables) + 1,
                    "guest_names": [g.name for g in current],
                    "people": current_count,
                    "groups": sorted({g.group for g in current if g.group}),
                })
                current = []
                current_count = 0
            current.append(guest)
            current_count += size
        if current:
            tables.append({
                "table_number": len(tables) + 1,
                "guest_names": [g.name for g in current],
                "people": current_count,
                "groups": sorted({g.group for g in current if g.group}),
            })
        return tables

    def transport_manifest(self, guests: Iterable[Guest], *, pickup_point: str = "") -> dict[str, Any]:
        riders = [
            {
                "name": guest.name,
                "phone": guest.phone,
                "people": max(1, guest.party_size_confirmed or guest.party_size_invited),
                "pickup_point": pickup_point,
            }
            for guest in guests
            if guest.needs_transport and guest.status in {RSVPStatus.CONFIRMED, RSVPStatus.TENTATIVE}
        ]
        total_people = sum(item["people"] for item in riders)
        recommended_bus_seats = int(math.ceil(total_people * 1.1))
        return {"riders": riders, "total_people": total_people, "recommended_bus_seats": recommended_bus_seats}

    def vendor_payment_schedule(
        self,
        vendors: Iterable[Vendor],
        *,
        event_date: str | date | datetime,
    ) -> list[dict[str, Any]]:
        event = parse_israeli_date(event_date)
        schedule: list[dict[str, Any]] = []
        for vendor in vendors:
            balance = max(0.0, vendor.quote_nis - vendor.deposit_nis)
            due = vendor.due_date or (event - timedelta(days=7))
            schedule.append({
                "vendor": vendor.name,
                "category": vendor.category,
                "deposit_nis": round(vendor.deposit_nis, 2),
                "balance_nis": round(balance, 2),
                "due_date": format_israeli_date(due),
                "contract_signed": vendor.contract_signed,
                "vat_included": vendor.vat_included,
                "warnings": self._vendor_warnings(vendor),
            })
        return schedule

    def tax_documentation_check(
        self,
        *,
        invoice_amount_before_vat_nis: float | int,
        invoice_date: str | date | datetime,
        customer_is_authorized_dealer: bool = True,
        customer_requested_allocation: bool = True,
        vat_amount_nis: float | int | None = None,
    ) -> dict[str, Any]:
        """Check Israeli VAT and invoice-allocation planning flags.

        This method does not issue an invoice or allocate a number. Use it to flag
        supplier invoices that should be checked in the official Israel Tax
        Authority system before payment or input-tax deduction.
        """
        amount = float(invoice_amount_before_vat_nis)
        if amount < 0:
            raise ValueError("invoice_amount_before_vat_nis must be non-negative")
        threshold = israel_invoice_allocation_threshold(invoice_date)
        required = requires_israel_invoice_allocation(
            amount,
            invoice_date,
            customer_is_authorized_dealer=customer_is_authorized_dealer,
            customer_requested_allocation=customer_requested_allocation,
            vat_amount_nis=vat_amount_nis,
        )
        warnings: list[str] = []
        if threshold is None:
            warnings.append("Invoice date is before the current allocation-number model window; verify manually.")
        elif required:
            warnings.append("Check official Israel Tax Authority allocation-number requirements before deduction.")
        if vat_amount_nis is None:
            warnings.append("VAT amount was not supplied; verify that the invoice states VAT explicitly.")
        return {
            "invoice_date": format_israeli_date(invoice_date),
            "current_vat_rate": CURRENT_ISRAEL_VAT_RATE,
            "current_vat_rate_display": "18%",
            "allocation_threshold_before_vat_nis": threshold,
            "allocation_threshold_display": format_nis(threshold) if threshold is not None else None,
            "allocation_required_follow_up": required,
            "warnings": warnings,
        }

    def music_license_checkpoint(
        self,
        *,
        event_type: EventType | str,
        event_date: str | date | datetime,
        is_business_event: bool = False,
        background_music_only: bool = False,
    ) -> dict[str, Any]:
        """Return an ACUM licensing checkpoint for an Israeli event.

        Current public rates can change. Treat the returned family-event fee as
        a planning value verified on 04/06/2026 and confirm on the ACUM portal.
        """
        event_type_text = EventType(event_type).value if event_type in EventType._value2member_map_ else str(event_type)
        event_day = parse_israeli_date(event_date)
        deadline = event_day - timedelta(days=3)
        if is_business_event:
            action = "check_business_event_tariff"
            fee = None
            warnings = [
                "Business events use a separate ACUM tariff; check audience tier and music type on the official portal.",
            ]
        else:
            action = "arrange_family_event_license_if_acum_repertoire_is_played"
            fee = ACUM_FAMILY_EVENT_LICENSE_NIS
            warnings = [
                "Family event fee is a planning value; confirm current ACUM terms before payment.",
            ]
        if background_music_only and not is_business_event:
            warnings.append("Background music at a family event can still require an ACUM family-event license.")
        return {
            "event_type": event_type_text,
            "event_date": format_israeli_date(event_day),
            "recommended_deadline": format_israeli_date(deadline),
            "action": action,
            "family_event_fee_nis": fee,
            "family_event_fee_display": format_nis(fee) if fee is not None else None,
            "deadline_buffer_hours": 72,
            "warnings": warnings,
        }

    def _vendor_warnings(self, vendor: Vendor) -> list[str]:
        warnings: list[str] = []
        if not vendor.contract_signed:
            warnings.append("Contract is not marked as signed.")
        if not vendor.vat_included:
            warnings.append("VAT inclusion is unclear or false; request itemized quote.")
        if vendor.deposit_nis > vendor.quote_nis:
            warnings.append("Deposit exceeds quote.")
        return warnings

    def privacy_risk_check(self, guests: Iterable[Guest]) -> list[str]:
        risks: list[str] = []
        sensitive_keywords = ["מחלה", "אבחון", "גירושין", "סכסוך", "תרופה", "נכות"]
        for guest in guests:
            text = " ".join([guest.notes, guest.dietary, guest.accessibility]).lower()
            if any(keyword in text for keyword in sensitive_keywords):
                risks.append(f"{guest.name}: review sensitive notes and minimize data.")
        return risks

    def message_compliance_check(
        self,
        *,
        message: str,
        contains_marketing: bool = False,
        has_consent: bool = False,
    ) -> list[str]:
        warnings: list[str] = []
        if contains_marketing and not has_consent:
            warnings.append("Marketing content requires a consent basis before bulk sending.")
        if ('הסר' not in message) and ("unsubscribe" not in message.lower()):
            warnings.append("Add an opt-out path for bulk messages where appropriate.")
        if len(message) > 1000:
            warnings.append("Message is long; split logistics from RSVP request.")
        return warnings

    def to_json(self, plan: EventPlan) -> str:
        def convert(value: Any) -> Any:
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, (date, datetime)):
                return value.isoformat()
            return value
        return json.dumps(asdict(plan), ensure_ascii=False, indent=2, default=convert)

    def save_plan(self, plan: EventPlan, path: str | Path) -> Path:
        output = Path(path)
        output.write_text(self.to_json(plan), encoding="utf-8")
        return output

    def load_plan(self, path: str | Path) -> EventPlan:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        venue_data = data.get("venue") or {}
        guests = [
            Guest(
                name=item["name"],
                phone=item.get("phone", ""),
                party_size_invited=int(item.get("party_size_invited", 1)),
                party_size_confirmed=int(item.get("party_size_confirmed", 0)),
                status=RSVPStatus(item.get("status", "no_response")),
                group=item.get("group", ""),
                children_count=int(item.get("children_count", 0)),
                dietary=item.get("dietary", ""),
                accessibility=item.get("accessibility", ""),
                needs_transport=bool(item.get("needs_transport", False)),
                language=item.get("language", "he"),
                notes=item.get("notes", ""),
            )
            for item in data.get("guests", [])
        ]
        vendors = [
            Vendor(
                category=item["category"],
                name=item["name"],
                quote_nis=float(item.get("quote_nis", 0)),
                deposit_nis=float(item.get("deposit_nis", 0)),
                due_date=parse_israeli_date(item["due_date"]) if item.get("due_date") else None,
                contract_signed=bool(item.get("contract_signed", False)),
                contact=item.get("contact", ""),
                vat_included=bool(item.get("vat_included", True)),
                notes=item.get("notes", ""),
            )
            for item in data.get("vendors", [])
        ]
        return EventPlan(
            event_type=EventType(data["event_type"]),
            event_date=parse_israeli_date(data["event_date"]),
            title=data["title"],
            event_id=data.get("event_id") or uuid.uuid4().hex,
            city=data.get("city", ""),
            venue=Venue(**venue_data),
            guests=guests,
            vendors=vendors,
            timezone=data.get("timezone", "Asia/Jerusalem"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
        )


class AsyncEventSchedulerClient:
    """Async wrapper for file and planning operations."""

    def __init__(self, client: EventSchedulerClient | None = None) -> None:
        self.client = client or EventSchedulerClient()

    async def create_plan(self, **kwargs: Any) -> EventPlan:
        return await asyncio.to_thread(self.client.create_plan, **kwargs)

    async def import_guests_csv(self, path: str | Path) -> list[Guest]:
        return await asyncio.to_thread(self.client.import_guests_csv, path)

    async def save_plan(self, plan: EventPlan, path: str | Path) -> Path:
        return await asyncio.to_thread(self.client.save_plan, plan, path)

    async def load_plan(self, path: str | Path) -> EventPlan:
        return await asyncio.to_thread(self.client.load_plan, path)

    async def rsvp_summary(self, guests: Iterable[Guest]) -> dict[str, Any]:
        return await asyncio.to_thread(self.client.rsvp_summary, list(guests))


__all__ = [
    "ACUM_FAMILY_EVENT_LICENSE_NIS",
    "AsyncEventSchedulerClient",
    "CURRENT_ISRAEL_VAT_RATE",
    "EventPlan",
    "EventSchedulerClient",
    "EventType",
    "Guest",
    "ISRAEL_INVOICE_ALLOCATION_THRESHOLDS",
    "Milestone",
    "RSVPStatus",
    "Vendor",
    "Venue",
    "calculate_brit_milah_target_date",
    "format_israeli_date",
    "israel_invoice_allocation_threshold",
    "format_nis",
    "map_rsvp_status",
    "normalize_israeli_phone",
    "requires_israel_invoice_allocation",
    "parse_israeli_date",
]
