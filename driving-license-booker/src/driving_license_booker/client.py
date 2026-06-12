"""Structured client for Israeli driving-license booking workflows.

The module does not automate protected government websites. It prepares validated
handoff payloads, keeps local workflow state, and supports adapter injection for
organizations that operate against approved internal gateways.
"""
from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import json
import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Protocol


class Environment(str, Enum):
    """Supported runtime environments."""

    SANDBOX = "sandbox"
    PRODUCTION = "production"


class BookingKind(str, Enum):
    """Supported booking workflow types."""

    LICENSE_RENEWAL = "license_renewal"
    BUREAU_APPOINTMENT = "bureau_appointment"
    PRACTICAL_TEST = "practical_test"


class BookingStatus(str, Enum):
    """Local workflow states."""

    DRAFT = "draft"
    READY_FOR_HANDOFF = "ready_for_handoff"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    NEEDS_ATTENTION = "needs_attention"


class LicenseClass(str, Enum):
    """Common Israeli license classes used by the workflow."""

    A = "A"
    A1 = "A1"
    A2 = "A2"
    B = "B"
    C1 = "C1"
    C = "C"
    D = "D"


@dataclass(frozen=True)
class TimeWindow:
    """Preferred appointment window."""

    date: dt.date
    start_time: dt.time | None = None
    end_time: dt.time | None = None
    city: str | None = None
    branch: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "start_time": self.start_time.isoformat(timespec="minutes") if self.start_time else None,
            "end_time": self.end_time.isoformat(timespec="minutes") if self.end_time else None,
            "city": self.city,
            "branch": self.branch,
        }


@dataclass(frozen=True)
class Applicant:
    """Applicant or driver details."""

    full_name: str
    national_id: str
    phone: str
    license_number: str | None = None
    email: str | None = None
    date_of_birth: dt.date | None = None
    license_class: LicenseClass | str = LicenseClass.B

    def normalized(self) -> "Applicant":
        client = DrivingLicenseBookerClient()
        return dataclasses.replace(
            self,
            national_id=client.normalize_israeli_id(self.national_id),
            phone=client.normalize_phone(self.phone),
        )

    def to_dict(self) -> dict[str, Any]:
        normalized = self.normalized()
        return {
            "full_name": normalized.full_name,
            "national_id": normalized.national_id,
            "phone": normalized.phone,
            "license_number": normalized.license_number,
            "email": normalized.email,
            "date_of_birth": normalized.date_of_birth.isoformat() if normalized.date_of_birth else None,
            "license_class": str(normalized.license_class.value if isinstance(normalized.license_class, LicenseClass) else normalized.license_class),
        }


@dataclass(frozen=True)
class BookingRequest:
    """Validated booking request before handoff."""

    kind: BookingKind | str
    applicant: Applicant
    windows: tuple[TimeWindow, ...] = field(default_factory=tuple)
    service_city: str | None = None
    notes: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind_value = self.kind.value if isinstance(self.kind, BookingKind) else str(self.kind)
        return {
            "kind": kind_value,
            "applicant": self.applicant.to_dict(),
            "windows": [window.to_dict() for window in self.windows],
            "service_city": self.service_city,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class BookingResponse:
    """Local response returned after workflow creation."""

    request_id: str
    status: BookingStatus | str
    kind: BookingKind | str
    created_at: str
    next_steps: tuple[str, ...]
    payload: Mapping[str, Any]
    confirmation_number: str | None = None
    appointment_reference: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "status": self.status.value if isinstance(self.status, BookingStatus) else str(self.status),
            "kind": self.kind.value if isinstance(self.kind, BookingKind) else str(self.kind),
            "created_at": self.created_at,
            "next_steps": list(self.next_steps),
            "payload": dict(self.payload),
            "confirmation_number": self.confirmation_number,
            "appointment_reference": self.appointment_reference,
        }


class Transport(Protocol):
    """Adapter protocol for approved organizational gateways."""

    def create(self, payload: Mapping[str, Any]) -> Mapping[str, Any]: ...

    def get(self, request_id: str) -> Mapping[str, Any]: ...

    def cancel(self, request_id: str, reason: str | None = None) -> Mapping[str, Any]: ...


class LocalJsonStore:
    """Small JSON-backed store for audit-friendly local workflow state."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self._records: dict[str, dict[str, Any]] = {}
        if self.path and self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self._records = {str(k): dict(v) for k, v in raw.items()}

    def save(self, record: Mapping[str, Any]) -> None:
        request_id = str(record["request_id"])
        self._records[request_id] = dict(record)
        self.flush()

    def get(self, request_id: str) -> dict[str, Any]:
        if request_id not in self._records:
            raise KeyError(f"booking request not found: {request_id}")
        return dict(self._records[request_id])

    def list(self) -> list[dict[str, Any]]:
        return [dict(value) for value in self._records.values()]

    def update(self, request_id: str, **changes: Any) -> dict[str, Any]:
        current = self.get(request_id)
        current.update(changes)
        self._records[request_id] = current
        self.flush()
        return dict(current)

    def flush(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._records, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


class DrivingLicenseBookerClient:
    """Sync client for license renewal and booking handoff workflows."""

    def __init__(
        self,
        environment: Environment | str = Environment.SANDBOX,
        *,
        transport: Transport | None = None,
        state_path: str | Path | None = None,
        now: dt.datetime | None = None,
    ) -> None:
        self.environment = Environment(environment)
        self.transport = transport
        self.store = LocalJsonStore(state_path)
        self._now = now

    @property
    def now(self) -> dt.datetime:
        return self._now or dt.datetime.now(dt.timezone.utc)

    def normalize_israeli_id(self, national_id: str) -> str:
        digits = re.sub(r"\D", "", national_id or "")
        if not 1 <= len(digits) <= 9:
            raise ValueError("Israeli ID must contain 1 to 9 digits")
        normalized = digits.zfill(9)
        if not self.validate_israeli_id(normalized):
            raise ValueError("Israeli ID checksum is invalid")
        return normalized

    def validate_israeli_id(self, national_id: str) -> bool:
        digits = re.sub(r"\D", "", national_id or "")
        if len(digits) != 9:
            return False
        total = 0
        for index, char in enumerate(digits):
            value = int(char) * (1 if index % 2 == 0 else 2)
            total += value if value < 10 else value - 9
        return total % 10 == 0

    def normalize_phone(self, phone: str) -> str:
        digits = re.sub(r"\D", "", phone or "")
        if digits.startswith("972"):
            digits = "0" + digits[3:]
        if len(digits) not in {9, 10} or not digits.startswith("0"):
            raise ValueError("Israeli phone number must start with 0 and contain 9 or 10 digits")
        return digits

    def format_local_date(self, value: dt.date | str) -> str:
        parsed = dt.date.fromisoformat(value) if isinstance(value, str) else value
        return parsed.strftime("%d/%m/%Y")

    def business_day_deadline(self, start: dt.date, days: int) -> dt.date:
        if days < 0:
            raise ValueError("days must be non-negative")
        current = start
        remaining = days
        while remaining:
            current += dt.timedelta(days=1)
            if current.weekday() < 5:
                remaining -= 1
        return current

    def build_service_links(self) -> dict[str, str]:
        return {
            "license_renewal": "https://www.gov.il/he/service/driving_license_renewal",
            "license_payment": "https://ecom.gov.il/voucherspa/input/209",
            "practical_test_payment": "https://ecom.gov.il/voucherspa/input/427",
            "transport_appointment_info": "https://www.gov.il/he/service/summoning-turn-transport",
            "licensing_bureau_appointment": "https://govisit.gov.il/he/authorities/authority/29",
            "driver_application_and_medical_declaration": "https://www.gov.il/he/service/apply_for_new_driver_drivers_license",
            "driver_student_area": "https://driverstudent.mot.gov.il",
            "license_information": "https://www.gov.il/en/departments/units/licensing_department",
        }

    def build_renewal_payload(
        self,
        applicant: Applicant,
        *,
        expiry_date: dt.date | str | None = None,
        include_payment_step: bool = True,
        notes: str | None = None,
    ) -> dict[str, Any]:
        normalized = applicant.normalized()
        expiry = dt.date.fromisoformat(expiry_date) if isinstance(expiry_date, str) else expiry_date
        payload = {
            "workflow": BookingKind.LICENSE_RENEWAL.value,
            "environment": self.environment.value,
            "applicant": normalized.to_dict(),
            "expiry_date": expiry.isoformat() if expiry else None,
            "include_payment_step": include_payment_step,
            "service_links": self.build_service_links(),
            "notes": notes,
        }
        return payload

    def build_bureau_appointment_payload(
        self,
        applicant: Applicant,
        windows: Iterable[TimeWindow],
        *,
        service_city: str | None = None,
        reason: str = "license renewal assistance",
        accessibility_needed: bool = False,
        notes: str | None = None,
    ) -> dict[str, Any]:
        window_tuple = tuple(windows)
        if not window_tuple:
            raise ValueError("at least one preferred time window is required")
        return {
            "workflow": BookingKind.BUREAU_APPOINTMENT.value,
            "environment": self.environment.value,
            "applicant": applicant.normalized().to_dict(),
            "windows": [window.to_dict() for window in window_tuple],
            "service_city": service_city,
            "reason": reason,
            "accessibility_needed": accessibility_needed,
            "service_links": self.build_service_links(),
            "notes": notes,
        }

    def build_practical_test_payload(
        self,
        applicant: Applicant,
        windows: Iterable[TimeWindow],
        *,
        teacher_name: str,
        teacher_phone: str,
        pickup_city: str | None = None,
        vehicle_class: LicenseClass | str = LicenseClass.B,
        notes: str | None = None,
    ) -> dict[str, Any]:
        window_tuple = tuple(windows)
        if not teacher_name.strip():
            raise ValueError("teacher_name is required")
        return {
            "workflow": BookingKind.PRACTICAL_TEST.value,
            "environment": self.environment.value,
            "applicant": applicant.normalized().to_dict(),
            "windows": [window.to_dict() for window in window_tuple],
            "teacher": {"name": teacher_name, "phone": self.normalize_phone(teacher_phone)},
            "pickup_city": pickup_city,
            "vehicle_class": vehicle_class.value if isinstance(vehicle_class, LicenseClass) else str(vehicle_class),
            "notes": notes,
        }

    def check_renewal_readiness(
        self,
        *,
        applicant: Applicant,
        expiry_date: dt.date,
        has_paid_fee: bool,
        medical_declaration_required: bool = False,
        medical_declaration_done: bool = False,
    ) -> dict[str, Any]:
        normalized = applicant.normalized()
        today = self.now.date()
        blockers: list[str] = []
        warnings: list[str] = []
        if expiry_date < today:
            warnings.append("license is already expired")
        if not has_paid_fee:
            blockers.append("renewal fee is not marked as paid")
        if medical_declaration_required and not medical_declaration_done:
            blockers.append("medical declaration is required before renewal completion")
        if not normalized.license_number:
            warnings.append("license number is missing")
        return {
            "ready": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "expiry_date": expiry_date.isoformat(),
            "expiry_date_local": self.format_local_date(expiry_date),
            "applicant": normalized.to_dict(),
        }

    def create_booking(self, request: BookingRequest | Mapping[str, Any]) -> BookingResponse:
        payload = request.to_dict() if isinstance(request, BookingRequest) else dict(request)
        kind = payload.get("kind") or payload.get("workflow")
        if not kind:
            raise ValueError("request kind is required")
        status = BookingStatus.READY_FOR_HANDOFF
        external_response: Mapping[str, Any] | None = None
        if self.transport:
            external_response = self.transport.create(payload)
            status = BookingStatus(str(external_response.get("status", BookingStatus.SUBMITTED.value)))
        request_id = str((external_response or {}).get("request_id") or uuid.uuid4())
        confirmation = str((external_response or {}).get("confirmation_number")) if (external_response or {}).get("confirmation_number") else None
        appointment_reference = str((external_response or {}).get("appointment_reference")) if (external_response or {}).get("appointment_reference") else None
        response = BookingResponse(
            request_id=request_id,
            status=status,
            kind=str(kind),
            created_at=self.now.isoformat(),
            next_steps=tuple(self._next_steps_for_kind(str(kind))),
            payload=payload,
            confirmation_number=confirmation,
            appointment_reference=appointment_reference,
        )
        self.store.save(response.to_dict())
        return response

    def get_booking(self, request_id: str) -> BookingResponse:
        if self.transport:
            record = dict(self.transport.get(request_id))
        else:
            record = self.store.get(request_id)
        return self._response_from_record(record)

    def cancel_booking(self, request_id: str, reason: str | None = None) -> BookingResponse:
        if self.transport:
            record = dict(self.transport.cancel(request_id, reason))
        else:
            record = self.store.update(
                request_id,
                status=BookingStatus.CANCELLED.value,
                cancellation_reason=reason,
                cancelled_at=self.now.isoformat(),
            )
        return self._response_from_record(record)

    def list_bookings(self, *, status: BookingStatus | str | None = None) -> list[BookingResponse]:
        records = self.store.list()
        if status:
            status_value = status.value if isinstance(status, BookingStatus) else str(status)
            records = [record for record in records if record.get("status") == status_value]
        return [self._response_from_record(record) for record in records]

    def serialize(self, response: BookingResponse | Mapping[str, Any]) -> str:
        payload = response.to_dict() if isinstance(response, BookingResponse) else dict(response)
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)

    def from_json(self, raw: str) -> BookingResponse:
        return self._response_from_record(json.loads(raw))

    def parse_create_response_id(self, response: BookingResponse | Mapping[str, Any] | str) -> str:
        if isinstance(response, BookingResponse):
            return response.request_id
        if isinstance(response, str):
            response = json.loads(response)
        for key in ("request_id", "id", "booking_id"):
            value = response.get(key)  # type: ignore[union-attr]
            if value:
                return str(value)
        raise ValueError("response does not contain a request id")

    def export_roster(self, applicants: Iterable[Applicant]) -> list[dict[str, Any]]:
        return [applicant.normalized().to_dict() for applicant in applicants]

    def make_teacher_message(
        self,
        *,
        applicant: Applicant,
        windows: Iterable[TimeWindow],
        teacher_name: str,
        pickup_city: str | None = None,
    ) -> str:
        lines = [
            f"שלום {teacher_name},",
            f"נדרש לתאם מבחן מעשי עבור {applicant.full_name}, דרגה {applicant.license_class.value if isinstance(applicant.license_class, LicenseClass) else applicant.license_class}.",
        ]
        if pickup_city:
            lines.append(f"עיר איסוף מועדפת: {pickup_city}.")
        formatted_windows = ", ".join(self.format_local_date(window.date) for window in windows)
        if formatted_windows:
            lines.append(f"חלונות מועדפים: {formatted_windows}.")
        lines.append("נא לאשר זמינות או להציע מועד חלופי.")
        return "\n".join(lines)

    def _next_steps_for_kind(self, kind: str) -> list[str]:
        if kind == BookingKind.LICENSE_RENEWAL.value:
            return [
                "Verify identity and license details on the official service.",
                "Pay the renewal fee only through an official payment page.",
                "Save the confirmation number and receipt in the customer record.",
            ]
        if kind == BookingKind.BUREAU_APPOINTMENT.value:
            return [
                "Open the official appointment service.",
                "Select Licensing Bureau service, city, and preferred time.",
                "Save appointment reference and reminder date.",
            ]
        if kind == BookingKind.PRACTICAL_TEST.value:
            return [
                "Coordinate with the authorized driving teacher.",
                "Confirm vehicle class, pickup city, and candidate availability.",
                "Record the final test date after teacher confirmation.",
            ]
        return ["Review request and complete official-service handoff."]

    def _response_from_record(self, record: Mapping[str, Any]) -> BookingResponse:
        return BookingResponse(
            request_id=str(record["request_id"]),
            status=str(record["status"]),
            kind=str(record["kind"]),
            created_at=str(record["created_at"]),
            next_steps=tuple(record.get("next_steps") or ()),
            payload=dict(record.get("payload") or {}),
            confirmation_number=record.get("confirmation_number"),
            appointment_reference=record.get("appointment_reference"),
        )


class AsyncDrivingLicenseBookerClient:
    """Async facade over the structured sync client."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._client = DrivingLicenseBookerClient(*args, **kwargs)

    async def create_booking(self, request: BookingRequest | Mapping[str, Any]) -> BookingResponse:
        await asyncio.sleep(0)
        return self._client.create_booking(request)

    async def get_booking(self, request_id: str) -> BookingResponse:
        await asyncio.sleep(0)
        return self._client.get_booking(request_id)

    async def cancel_booking(self, request_id: str, reason: str | None = None) -> BookingResponse:
        await asyncio.sleep(0)
        return self._client.cancel_booking(request_id, reason)

    async def list_bookings(self, *, status: BookingStatus | str | None = None) -> list[BookingResponse]:
        await asyncio.sleep(0)
        return self._client.list_bookings(status=status)


__all__ = [
    "Applicant",
    "AsyncDrivingLicenseBookerClient",
    "BookingKind",
    "BookingRequest",
    "BookingResponse",
    "BookingStatus",
    "DrivingLicenseBookerClient",
    "Environment",
    "LicenseClass",
    "LocalJsonStore",
    "TimeWindow",
]
