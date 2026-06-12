from __future__ import annotations

import asyncio
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional, Sequence

Environment = Literal["sandbox", "production"]
Channel = Literal["email", "sms", "whatsapp", "phone"]
MaintenanceSeverity = Literal["low", "medium", "high", "urgent"]
MaintenanceStatus = Literal["open", "scheduled", "waiting_for_tenant", "waiting_for_contractor", "completed", "cancelled"]
PaymentStatus = Literal["pending", "partial", "paid", "overdue"]

STANDARD_VAT_RATE = Decimal("0.18")
ISRAEL_INVOICE_ALLOCATION_THRESHOLDS_ILS: Dict[str, str] = {
    "2025-01-01": "20000.00",
    "2026-01-01": "10000.00",
    "2026-06-01": "5000.00",
}
BANK_OF_ISRAEL_SERIES_API_BASE = "https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS"
REFERENCE_VALIDATION_DATE = "2026-06-04"


class SchedulerError(ValueError):
    """Raised when scheduler input is invalid or a record cannot be found."""


@dataclass(slots=True)
class ClientConfig:
    environment: Environment = "sandbox"
    default_currency: str = "ILS"
    locale: str = "he-IL"
    timezone: str = "Asia/Jerusalem"
    vat_registered: bool = False
    payment_grace_days: int = 3

    def validate(self) -> None:
        if self.environment not in {"sandbox", "production"}:
            raise SchedulerError("environment must be sandbox or production")
        if self.payment_grace_days < 0:
            raise SchedulerError("payment_grace_days must be zero or positive")


@dataclass(slots=True)
class PropertyRecord:
    id: str
    address: str
    city: str
    apartment: str = ""
    owner_name: str = ""
    arnona_account: str = ""
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"))


@dataclass(slots=True)
class TenantRecord:
    id: str
    property_id: str
    full_name: str
    phone: str = ""
    email: str = ""
    preferred_channel: Channel = "email"
    id_number_last4: str = ""
    emergency_contact: str = ""
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"))


@dataclass(slots=True)
class LeaseRecord:
    id: str
    property_id: str
    tenant_id: str
    start_date: str
    end_date: str
    monthly_rent_ils: str
    due_day: int = 1
    deposit_ils: str = "0.00"
    payment_method: str = "bank_transfer"
    escalation_note: str = ""
    active: bool = True


@dataclass(slots=True)
class RentCharge:
    id: str
    lease_id: str
    tenant_id: str
    property_id: str
    due_date: str
    amount_ils: str
    status: PaymentStatus = "pending"
    paid_amount_ils: str = "0.00"
    paid_date: str = ""
    payment_method: str = ""
    reference: str = ""
    reminder_count: int = 0


@dataclass(slots=True)
class MaintenanceTask:
    id: str
    property_id: str
    title: str
    description: str
    severity: MaintenanceSeverity = "medium"
    status: MaintenanceStatus = "open"
    reported_by: str = ""
    due_date: str = ""
    contractor: str = ""
    estimated_cost_ils: str = "0.00"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"))
    completed_at: str = ""


@dataclass(slots=True)
class CommunicationLog:
    id: str
    tenant_id: str
    property_id: str
    channel: Channel
    subject: str
    body: str
    scheduled_for: str = ""
    sent_at: str = ""
    related_record_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"))


_EMPTY_DATA: Dict[str, List[Dict[str, Any]]] = {
    "properties": [],
    "tenants": [],
    "leases": [],
    "rent_charges": [],
    "maintenance": [],
    "communications": [],
}


_PHONE_RE = re.compile(r"^(?:\+972|0)(?:[23489]|5\d|7\d)-?\d{7}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_URGENT_WORDS = {"burst", "flood", "smoke", "fire", "electric", "sparks", "gas", "lock", "sewage", "הצפה", "שריפה", "חשמל", "גז", "ביוב"}
_HIGH_WORDS = {"leak", "mold", "damp", "no hot water", "boiler", "door", "window", "נזילה", "עובש", "דוד", "דלת", "חלון"}



def official_reference_values(as_of: str | date | None = None) -> Dict[str, Any]:
    """Return verified Israeli operational reference values used by the scheduler.

    The values are informational guardrails. They do not determine tax liability,
    issue invoices, or replace professional review.
    """
    target = parse_israeli_date(as_of) if as_of is not None else date.today()
    threshold = ""
    for effective_date, amount in sorted(ISRAEL_INVOICE_ALLOCATION_THRESHOLDS_ILS.items()):
        if date.fromisoformat(effective_date) <= target:
            threshold = amount
    return {
        "standard_vat_rate": f"{(STANDARD_VAT_RATE * 100).quantize(Decimal('1'))}%",
        "israel_invoice_allocation_threshold_ils": threshold,
        "bank_of_israel_series_api_base": BANK_OF_ISRAEL_SERIES_API_BASE,
        "reference_validation_date": REFERENCE_VALIDATION_DATE,
        "notes": [
            "Use approved accounting software for official invoices and receipts.",
            "Verify current Israel Tax Authority rules before production issuance.",
            "Use Bank of Israel representative rates only where the lease explicitly requires currency conversion.",
        ],
    }

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def parse_israeli_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    text = value.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise SchedulerError("date must use DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD")


def format_israeli_date(value: str | date) -> str:
    parsed = parse_israeli_date(value)
    return parsed.strftime("%d/%m/%Y")


def parse_money(value: str | int | float | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        amount = value
    else:
        text = str(value).replace("₪", "").replace(",", "").strip()
        if not text:
            raise SchedulerError("amount cannot be empty")
        try:
            amount = Decimal(text)
        except Exception as exc:  # pragma: no cover
            raise SchedulerError("amount must be numeric") from exc
    if amount < 0:
        raise SchedulerError("amount cannot be negative")
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def money_to_str(value: str | int | float | Decimal) -> str:
    return str(parse_money(value))


def validate_channel(value: str) -> Channel:
    if value not in {"email", "sms", "whatsapp", "phone"}:
        raise SchedulerError("preferred_channel must be email, sms, whatsapp, or phone")
    return value  # type: ignore[return-value]


def validate_phone(value: str, allow_empty: bool = True) -> str:
    if not value and allow_empty:
        return value
    normalized = value.replace(" ", "")
    if not _PHONE_RE.match(normalized):
        raise SchedulerError("phone must be an Israeli phone number such as 0501234567 or +972501234567")
    return normalized


def validate_email(value: str, allow_empty: bool = True) -> str:
    if not value and allow_empty:
        return value
    if not _EMAIL_RE.match(value):
        raise SchedulerError("email must be a valid email address")
    return value


def month_add(base: date, months: int, due_day: int) -> date:
    year = base.year + (base.month - 1 + months) // 12
    month = (base.month - 1 + months) % 12 + 1
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    return date(year, month, min(due_day, last_day))


class PropertyManagementScheduler:
    """Local-first scheduler for Israeli rental operations."""

    def __init__(self, store_path: str | Path | None = None, *, environment: Environment = "sandbox", config: ClientConfig | None = None) -> None:
        self.store_path = Path(store_path) if store_path else None
        self.config = config or ClientConfig(environment=environment)
        self.config.validate()
        self.data: Dict[str, List[Dict[str, Any]]] = json.loads(json.dumps(_EMPTY_DATA))
        if self.store_path and self.store_path.exists():
            self.load()

    def save(self) -> Path | None:
        if not self.store_path:
            return None
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.store_path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return self.store_path

    def load(self) -> None:
        if not self.store_path:
            raise SchedulerError("store_path is required for load")
        if not self.store_path.exists():
            self.data = json.loads(json.dumps(_EMPTY_DATA))
            return
        loaded = json.loads(self.store_path.read_text(encoding="utf-8"))
        self.data = json.loads(json.dumps(_EMPTY_DATA))
        for key in self.data:
            self.data[key] = list(loaded.get(key, []))

    def reset(self) -> None:
        self.data = json.loads(json.dumps(_EMPTY_DATA))
        self.save()

    def create_property(self, address: str, city: str, apartment: str = "", *, owner_name: str = "", arnona_account: str = "", notes: str = "") -> Dict[str, Any]:
        if not address.strip() or not city.strip():
            raise SchedulerError("address and city are required")
        record = PropertyRecord(
            id=generate_id("prop"),
            address=address.strip(),
            city=city.strip(),
            apartment=apartment.strip(),
            owner_name=owner_name.strip(),
            arnona_account=arnona_account.strip(),
            notes=notes.strip(),
        )
        item = asdict(record)
        self.data["properties"].append(item)
        self.save()
        return item

    def list_properties(self) -> List[Dict[str, Any]]:
        return list(self.data["properties"])

    def add_tenant(self, property_id: str, full_name: str, *, phone: str = "", email: str = "", preferred_channel: Channel = "email", id_number_last4: str = "", emergency_contact: str = "", notes: str = "") -> Dict[str, Any]:
        self._require("properties", property_id)
        if not full_name.strip():
            raise SchedulerError("full_name is required")
        channel = validate_channel(preferred_channel)
        phone = validate_phone(phone)
        email = validate_email(email)
        if channel == "email" and not email:
            raise SchedulerError("email is required when preferred_channel is email")
        if channel in {"sms", "whatsapp", "phone"} and not phone:
            raise SchedulerError("phone is required for the selected channel")
        record = TenantRecord(
            id=generate_id("ten"),
            property_id=property_id,
            full_name=full_name.strip(),
            phone=phone,
            email=email,
            preferred_channel=channel,
            id_number_last4=id_number_last4[-4:] if id_number_last4 else "",
            emergency_contact=emergency_contact.strip(),
            notes=notes.strip(),
        )
        item = asdict(record)
        self.data["tenants"].append(item)
        self.save()
        return item

    def create_lease(self, property_id: str, tenant_id: str, start_date: str | date, end_date: str | date, monthly_rent_ils: str | int | float | Decimal, *, due_day: int = 1, deposit_ils: str | int | float | Decimal = "0", payment_method: str = "bank_transfer", escalation_note: str = "") -> Dict[str, Any]:
        self._require("properties", property_id)
        self._require("tenants", tenant_id)
        start = parse_israeli_date(start_date)
        end = parse_israeli_date(end_date)
        if end < start:
            raise SchedulerError("end_date cannot be before start_date")
        if not 1 <= due_day <= 28:
            raise SchedulerError("due_day must be between 1 and 28")
        record = LeaseRecord(
            id=generate_id("lease"),
            property_id=property_id,
            tenant_id=tenant_id,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            monthly_rent_ils=money_to_str(monthly_rent_ils),
            due_day=due_day,
            deposit_ils=money_to_str(deposit_ils),
            payment_method=payment_method.strip() or "bank_transfer",
            escalation_note=escalation_note.strip(),
        )
        item = asdict(record)
        self.data["leases"].append(item)
        self.save()
        return item

    def schedule_rent(self, lease_id: str, from_date: str | date, *, months: int = 12, overwrite: bool = False) -> List[Dict[str, Any]]:
        lease = self._require("leases", lease_id)
        if months < 1 or months > 36:
            raise SchedulerError("months must be between 1 and 36")
        start = parse_israeli_date(from_date)
        lease_end = date.fromisoformat(lease["end_date"])
        created: List[Dict[str, Any]] = []
        if overwrite:
            self.data["rent_charges"] = [c for c in self.data["rent_charges"] if c["lease_id"] != lease_id]
        existing_keys = {(c["lease_id"], c["due_date"]) for c in self.data["rent_charges"]}
        for offset in range(months):
            due = month_add(start, offset, int(lease["due_day"]))
            if due > lease_end:
                break
            key = (lease_id, due.isoformat())
            if key in existing_keys:
                continue
            record = RentCharge(
                id=generate_id("rent"),
                lease_id=lease_id,
                tenant_id=lease["tenant_id"],
                property_id=lease["property_id"],
                due_date=due.isoformat(),
                amount_ils=lease["monthly_rent_ils"],
            )
            item = asdict(record)
            self.data["rent_charges"].append(item)
            created.append(item)
        self.save()
        return created

    def record_payment(self, charge_id: str, paid_date: str | date, amount_ils: str | int | float | Decimal, *, method: str = "bank_transfer", reference: str = "") -> Dict[str, Any]:
        charge = self._require("rent_charges", charge_id)
        amount = parse_money(amount_ils)
        expected = parse_money(charge["amount_ils"])
        if amount > expected:
            raise SchedulerError("paid amount cannot exceed charge amount")
        charge["paid_amount_ils"] = str(amount)
        charge["paid_date"] = parse_israeli_date(paid_date).isoformat()
        charge["payment_method"] = method
        charge["reference"] = reference
        charge["status"] = "paid" if amount == expected else "partial"
        self.save()
        return charge

    def mark_overdue(self, as_of: str | date | None = None) -> List[Dict[str, Any]]:
        today = parse_israeli_date(as_of) if as_of else date.today()
        changed: List[Dict[str, Any]] = []
        for charge in self.data["rent_charges"]:
            if charge["status"] in {"paid", "partial"}:
                continue
            due = date.fromisoformat(charge["due_date"])
            if today > due + timedelta(days=self.config.payment_grace_days):
                charge["status"] = "overdue"
                changed.append(charge)
        self.save()
        return changed

    def create_maintenance(self, property_id: str, title: str, description: str, *, reported_by: str = "", severity: MaintenanceSeverity | None = None, due_date: str | date | None = None, contractor: str = "", estimated_cost_ils: str | int | float | Decimal = "0") -> Dict[str, Any]:
        self._require("properties", property_id)
        if not title.strip() or not description.strip():
            raise SchedulerError("title and description are required")
        chosen = severity or self.suggest_maintenance_priority(f"{title} {description}")
        if chosen not in {"low", "medium", "high", "urgent"}:
            raise SchedulerError("severity must be low, medium, high, or urgent")
        record = MaintenanceTask(
            id=generate_id("task"),
            property_id=property_id,
            title=title.strip(),
            description=description.strip(),
            severity=chosen,
            reported_by=reported_by.strip(),
            due_date=parse_israeli_date(due_date).isoformat() if due_date else "",
            contractor=contractor.strip(),
            estimated_cost_ils=money_to_str(estimated_cost_ils),
        )
        item = asdict(record)
        self.data["maintenance"].append(item)
        self.save()
        return item

    def update_maintenance_status(self, task_id: str, status: MaintenanceStatus) -> Dict[str, Any]:
        if status not in {"open", "scheduled", "waiting_for_tenant", "waiting_for_contractor", "completed", "cancelled"}:
            raise SchedulerError("invalid maintenance status")
        task = self._require("maintenance", task_id)
        task["status"] = status
        if status == "completed" and not task.get("completed_at"):
            task["completed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        self.save()
        return task

    def suggest_maintenance_priority(self, issue_text: str) -> MaintenanceSeverity:
        lower = issue_text.lower()
        if any(word in lower for word in _URGENT_WORDS):
            return "urgent"
        if any(word in lower for word in _HIGH_WORDS):
            return "high"
        if len(lower) < 30:
            return "low"
        return "medium"

    def generate_tenant_message(self, kind: str, *, tenant_id: str | None = None, charge_id: str | None = None, task_id: str | None = None) -> Dict[str, str]:
        tenant: Optional[Dict[str, Any]] = self._require("tenants", tenant_id) if tenant_id else None
        if charge_id:
            charge = self._require("rent_charges", charge_id)
            tenant = self._require("tenants", charge["tenant_id"])
        if task_id:
            task = self._require("maintenance", task_id)
            tenant = tenant or self._find_first("tenants", "property_id", task["property_id"])
        name = tenant["full_name"] if tenant else "שלום"
        if kind == "rent_reminder":
            if not charge_id:
                raise SchedulerError("charge_id is required for rent_reminder")
            charge = self._require("rent_charges", charge_id)
            subject = f"תזכורת לתשלום שכר דירה עבור {format_israeli_date(charge['due_date'])}"
            body = f"שלום {name}, תזכורת לתשלום שכר דירה בסך ₪{charge['amount_ils']} עד {format_israeli_date(charge['due_date'])}. לאחר התשלום יש לשלוח אסמכתה."
        elif kind == "maintenance_update":
            if not task_id:
                raise SchedulerError("task_id is required for maintenance_update")
            task = self._require("maintenance", task_id)
            subject = f"עדכון טיפול בתקלה: {task['title']}"
            body = f"שלום {name}, הטיפול בפנייה '{task['title']}' נמצא בסטטוס {task['status']}. יש לתאם זמינות במקרה שנדרש ביקור בדירה."
        elif kind == "lease_renewal":
            if not tenant_id:
                raise SchedulerError("tenant_id is required for lease_renewal")
            subject = "בדיקת חידוש הסכם שכירות"
            body = f"שלום {name}, לקראת סיום תקופת השכירות יש לאשר האם קיימת כוונה לחדש את ההסכם ולתאם תנאים בכתב."
        else:
            raise SchedulerError("unsupported message kind")
        return {"subject": subject, "body": body}

    def log_communication(self, tenant_id: str, property_id: str, channel: Channel, subject: str, body: str, *, scheduled_for: str | date | None = None, sent_at: str | date | None = None, related_record_id: str = "") -> Dict[str, Any]:
        self._require("tenants", tenant_id)
        self._require("properties", property_id)
        record = CommunicationLog(
            id=generate_id("comm"),
            tenant_id=tenant_id,
            property_id=property_id,
            channel=validate_channel(channel),
            subject=subject.strip(),
            body=body.strip(),
            scheduled_for=parse_israeli_date(scheduled_for).isoformat() if scheduled_for else "",
            sent_at=parse_israeli_date(sent_at).isoformat() if sent_at else "",
            related_record_id=related_record_id,
        )
        item = asdict(record)
        self.data["communications"].append(item)
        self.save()
        return item

    def build_daily_agenda(self, target_date: str | date) -> Dict[str, Any]:
        day = parse_israeli_date(target_date)
        due_rent = [c for c in self.data["rent_charges"] if c["due_date"] == day.isoformat() and c["status"] != "paid"]
        overdue = self.mark_overdue(day)
        maintenance_due = [t for t in self.data["maintenance"] if t.get("due_date") == day.isoformat() and t["status"] not in {"completed", "cancelled"}]
        communications = [c for c in self.data["communications"] if c.get("scheduled_for") == day.isoformat() and not c.get("sent_at")]
        return {
            "date": day.isoformat(),
            "rent_due": due_rent,
            "rent_overdue": overdue,
            "maintenance_due": maintenance_due,
            "communications_due": communications,
            "counts": {
                "rent_due": len(due_rent),
                "rent_overdue": len(overdue),
                "maintenance_due": len(maintenance_due),
                "communications_due": len(communications),
            },
        }

    def export_accounting_pack(self, start_date: str | date, end_date: str | date) -> Dict[str, Any]:
        start = parse_israeli_date(start_date)
        end = parse_israeli_date(end_date)
        if end < start:
            raise SchedulerError("end_date cannot be before start_date")
        paid = []
        total = Decimal("0.00")
        for charge in self.data["rent_charges"]:
            if charge["status"] != "paid" or not charge.get("paid_date"):
                continue
            paid_date = date.fromisoformat(charge["paid_date"])
            if start <= paid_date <= end:
                paid.append(charge)
                total += parse_money(charge["paid_amount_ils"])
        open_maintenance = [t for t in self.data["maintenance"] if t["status"] not in {"completed", "cancelled"}]
        return {
            "period": {"start_date": start.isoformat(), "end_date": end.isoformat()},
            "currency": "ILS",
            "vat_registered": self.config.vat_registered,
            "paid_rent": paid,
            "open_maintenance": open_maintenance,
            "totals": {"paid_rent_ils": str(total.quantize(Decimal("0.01")))},
            "notes": [
                "Classify residential rent, commercial rent, deposits, reimbursements, and repairs separately.",
                "Check current Israel Tax Authority and bookkeeping requirements before issuing documents.",
            ],
        }

    async def acreate_property(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self.create_property(*args, **kwargs)

    async def aadd_tenant(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self.add_tenant(*args, **kwargs)

    async def acreate_lease(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self.create_lease(*args, **kwargs)

    async def aschedule_rent(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        await asyncio.sleep(0)
        return self.schedule_rent(*args, **kwargs)

    async def abuild_daily_agenda(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self.build_daily_agenda(*args, **kwargs)

    async def aexport_accounting_pack(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self.export_accounting_pack(*args, **kwargs)

    def _require(self, collection: str, record_id: str | None) -> Dict[str, Any]:
        if not record_id:
            raise SchedulerError("record id is required")
        for item in self.data[collection]:
            if item["id"] == record_id:
                return item
        raise SchedulerError(f"{collection} record not found: {record_id}")

    def _find_first(self, collection: str, field_name: str, value: str) -> Dict[str, Any] | None:
        for item in self.data[collection]:
            if item.get(field_name) == value:
                return item
        return None


__all__ = [
    "official_reference_values",
    "REFERENCE_VALIDATION_DATE",
    "BANK_OF_ISRAEL_SERIES_API_BASE",
    "ISRAEL_INVOICE_ALLOCATION_THRESHOLDS_ILS",
    "STANDARD_VAT_RATE",
    "ClientConfig",
    "CommunicationLog",
    "LeaseRecord",
    "MaintenanceTask",
    "PropertyManagementScheduler",
    "PropertyRecord",
    "RentCharge",
    "SchedulerError",
    "TenantRecord",
    "format_israeli_date",
    "generate_id",
    "money_to_str",
    "month_add",
    "parse_israeli_date",
    "parse_money",
    "validate_channel",
    "validate_email",
    "validate_phone",
]
