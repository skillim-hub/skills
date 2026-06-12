"""Typed client and helpers for Israeli parking, traffic, and toll fine workflows.

Use this module with an authorized issuer interface if one is separately provided, internal middleware, or mocked
transports. It does not scrape public portals, bypass CAPTCHA, or store payment
card data.
"""

from __future__ import annotations

import asyncio
import csv
import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Protocol
from urllib.parse import urljoin

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None  # type: ignore[assignment]


IssuerType = Literal["municipality", "police", "toll", "collection", "other"]
FineStatus = Literal[
    "new",
    "needs_issuer_identification",
    "lookup_not_found",
    "verified_unpaid",
    "verified_paid",
    "duplicate_payment_risk",
    "contest_candidate",
    "appeal_submitted",
    "liability_transfer_requested",
    "approved_for_payment",
    "paid",
    "cancelled",
    "rejected",
    "collection",
    "closed",
]
Decision = Literal["pay", "contest", "transfer", "escalate", "hold"]
EnvironmentName = Literal["sandbox", "production"]


class ParkingFineError(Exception):
    """Base package error."""


class ValidationError(ParkingFineError):
    """Input data is missing or malformed."""


class TransportError(ParkingFineError):
    """Remote or mocked transport failed."""


class FineNotFoundError(ParkingFineError):
    """No fine matched the supplied identifiers."""


class DuplicatePaymentRiskError(ParkingFineError):
    """Payment must pause until duplicate risk is cleared."""


class LegalEscalationRequired(ParkingFineError):
    """The case has legal consequences beyond simple payment."""


def normalize_vehicle_number(value: str) -> str:
    """Normalize Israeli vehicle plate by keeping digits only."""

    digits = re.sub(r"\D", "", value or "")
    if not 5 <= len(digits) <= 8:
        raise ValidationError("vehicle_number must contain 5 to 8 digits")
    return digits


def mask_identifier(value: str, visible: int = 4) -> str:
    """Mask an Israeli ID, company number, or customer identifier."""

    clean = re.sub(r"\s+", "", value or "")
    if not clean:
        return ""
    if len(clean) <= visible:
        return "*" * len(clean)
    return "*" * (len(clean) - visible) + clean[-visible:]


def parse_israeli_date(value: str | dt.date | None) -> dt.date | None:
    """Parse ISO or Israeli display dates.

    Accepted strings:
    - ``YYYY-MM-DD``
    - ``DD/MM/YYYY``
    - ``DD-MM-YYYY`` for backwards compatibility
    """

    if value is None or value == "":
        return None
    if isinstance(value, dt.date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValidationError(f"unsupported date format: {value!r}")


def format_he_date(value: str | dt.date | None) -> str:
    """Format a date as ``DD/MM/YYYY`` for Hebrew-facing materials."""

    parsed = parse_israeli_date(value)
    if parsed is None:
        return ""
    return parsed.strftime("%d/%m/%Y")


def to_money(value: str | int | float | Decimal) -> Decimal:
    """Convert money to Decimal with two agorot digits."""

    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"invalid amount: {value!r}") from exc
    if amount < Decimal("0.00"):
        raise ValidationError("amount must be non-negative")
    return amount


def money_str(value: str | int | float | Decimal) -> str:
    """Return a normalized ILS amount string."""

    return f"{to_money(value):.2f}"


def now_iso() -> str:
    """Return current local timestamp in ISO format."""

    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def build_case_id(
    vehicle_number: str,
    notice_number: str | None = None,
    *,
    created_on: str | dt.date | None = None,
) -> str:
    """Build a stable case identifier from date, plate, and notice."""

    plate = normalize_vehicle_number(vehicle_number)
    date_value = parse_israeli_date(created_on) or dt.date.today()
    notice = re.sub(r"[^A-Za-z0-9]+", "", notice_number or "no-notice")[:24]
    digest = hashlib.sha1(f"{plate}:{notice}:{date_value.isoformat()}".encode()).hexdigest()[:8]
    return f"{date_value.strftime('%Y%m%d')}-{plate}-{notice}-{digest}"


@dataclass(slots=True)
class CaseRecord:
    """Local case record used before official lookup or payment."""

    case_id: str
    issuer_type: IssuerType
    vehicle_number: str
    notice_number: str | None = None
    issuer_name: str | None = None
    status: FineStatus = "new"
    amount_ils: Decimal | None = None
    notice_date: dt.date | None = None
    due_date: dt.date | None = None
    created_at: str = field(default_factory=now_iso)

    def __post_init__(self) -> None:
        self.vehicle_number = normalize_vehicle_number(self.vehicle_number)
        if self.amount_ils is not None:
            self.amount_ils = to_money(self.amount_ils)
        if self.notice_date is not None:
            self.notice_date = parse_israeli_date(self.notice_date)
        if self.due_date is not None:
            self.due_date = parse_israeli_date(self.due_date)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "issuer_type": self.issuer_type,
            "issuer_name": self.issuer_name,
            "vehicle_number": self.vehicle_number,
            "notice_number": self.notice_number,
            "status": self.status,
            "amount_ils": money_str(self.amount_ils) if self.amount_ils is not None else None,
            "notice_date": self.notice_date.isoformat() if self.notice_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at,
        }


@dataclass(slots=True)
class FineLookupRequest:
    issuer_type: IssuerType
    vehicle_number: str
    notice_number: str | None = None
    issuer_name: str | None = None
    recipient_identifier: str | None = None
    account_number: str | None = None
    notice_date: dt.date | None = None
    due_date: dt.date | None = None
    amount_ils: Decimal | None = None
    case_id: str | None = None
    environment: EnvironmentName = "sandbox"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        allowed = {"municipality", "police", "toll", "collection", "other"}
        if self.issuer_type not in allowed:
            raise ValidationError(f"issuer_type must be one of {sorted(allowed)}")
        if self.environment not in {"sandbox", "production"}:
            raise ValidationError("environment must be sandbox or production")
        self.vehicle_number = normalize_vehicle_number(self.vehicle_number)
        if self.notice_number is not None:
            self.notice_number = str(self.notice_number).strip()
            if not self.notice_number:
                raise ValidationError("notice_number cannot be empty")
        if self.notice_date is not None:
            self.notice_date = parse_israeli_date(self.notice_date)
        if self.due_date is not None:
            self.due_date = parse_israeli_date(self.due_date)
        if self.notice_date and self.due_date and self.due_date < self.notice_date:
            raise ValidationError("due_date cannot be before notice_date")
        if self.amount_ils is not None:
            self.amount_ils = to_money(self.amount_ils)

    def to_payload(self, redact: bool = False) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "environment": self.environment,
            "issuer_type": self.issuer_type,
            "issuer_name": self.issuer_name,
            "vehicle_number": self.vehicle_number,
            "notice_number": self.notice_number,
            "recipient_identifier": mask_identifier(self.recipient_identifier or "")
            if redact
            else self.recipient_identifier,
            "account_number": self.account_number,
            "notice_date": self.notice_date.isoformat() if self.notice_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "amount_ils": money_str(self.amount_ils) if self.amount_ils is not None else None,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class FineLookupResult:
    status: FineStatus
    vehicle_number: str
    issuer_type: IssuerType
    notice_number: str | None = None
    issuer_name: str | None = None
    amount_ils: Decimal | None = None
    due_date: dt.date | None = None
    payment_allowed: bool = False
    appeal_allowed: bool = False
    case_id: str | None = None
    payment_reference: str | None = None
    appeal_reference: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.vehicle_number = normalize_vehicle_number(self.vehicle_number)
        if self.amount_ils is not None:
            self.amount_ils = to_money(self.amount_ils)
        if self.due_date is not None:
            self.due_date = parse_israeli_date(self.due_date)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "FineLookupResult":
        status = payload.get("status", "lookup_not_found")
        vehicle = payload.get("vehicle_number") or payload.get("plate") or "00000"
        issuer_type = payload.get("issuer_type", "other")
        return cls(
            status=status,
            vehicle_number=vehicle,
            issuer_type=issuer_type,
            notice_number=payload.get("notice_number"),
            issuer_name=payload.get("issuer_name"),
            amount_ils=payload.get("amount_ils") or payload.get("total_amount_ils"),
            due_date=payload.get("due_date"),
            payment_allowed=bool(payload.get("payment_allowed", False)),
            appeal_allowed=bool(payload.get("appeal_allowed", False)),
            case_id=payload.get("case_id"),
            payment_reference=payload.get("payment_reference"),
            appeal_reference=payload.get("appeal_reference"),
            raw=dict(payload),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "status": self.status,
            "vehicle_number": self.vehicle_number,
            "issuer_type": self.issuer_type,
            "notice_number": self.notice_number,
            "issuer_name": self.issuer_name,
            "amount_ils": money_str(self.amount_ils) if self.amount_ils is not None else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "payment_allowed": self.payment_allowed,
            "appeal_allowed": self.appeal_allowed,
            "payment_reference": self.payment_reference,
            "appeal_reference": self.appeal_reference,
        }


@dataclass(slots=True)
class PaymentPreparation:
    case_id: str
    amount_ils: Decimal
    official_payment_url: str
    expires_at: str | None = None
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "PaymentPreparation":
        return cls(
            case_id=str(payload["case_id"]),
            amount_ils=to_money(payload["amount_ils"]),
            official_payment_url=str(payload["official_payment_url"]),
            expires_at=payload.get("expires_at"),
            warnings=list(payload.get("warnings", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "amount_ils": money_str(self.amount_ils),
            "official_payment_url": self.official_payment_url,
            "expires_at": self.expires_at,
            "warnings": self.warnings,
        }


@dataclass(slots=True)
class AppealSubmission:
    appeal_reference: str
    status: FineStatus
    submitted_at: str
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "AppealSubmission":
        return cls(
            appeal_reference=str(payload["appeal_reference"]),
            status=payload.get("status", "appeal_submitted"),
            submitted_at=str(payload.get("submitted_at") or now_iso()),
            warnings=list(payload.get("warnings", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "appeal_reference": self.appeal_reference,
            "status": self.status,
            "submitted_at": self.submitted_at,
            "warnings": self.warnings,
        }


class SyncTransport(Protocol):
    def post(self, path: str, json_data: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


class AsyncTransport(Protocol):
    async def post(self, path: str, json_data: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


class HttpxSyncTransport:
    """Authorized HTTP transport for permitted issuer interfaces or internal middleware."""

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        timeout: float = 20.0,
    ) -> None:
        if httpx is None:
            raise TransportError("httpx is required for HTTP transport")
        self.base_url = base_url.rstrip("/") + "/"
        self.client = httpx.Client(timeout=timeout)
        self.token = token

    def post(self, path: str, json_data: Mapping[str, Any]) -> Mapping[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        url = urljoin(self.base_url, path.lstrip("/"))
        response = self.client.post(url, json=dict(json_data), headers=headers)
        if response.status_code == 404:
            raise FineNotFoundError("fine not found")
        if response.status_code >= 400:
            raise TransportError(f"HTTP {response.status_code}: {response.text[:200]}")
        return response.json()

    def close(self) -> None:
        self.client.close()


class HttpxAsyncTransport:
    """Async authorized HTTP transport for permitted issuer interfaces or middleware."""

    def __init__(self, base_url: str, token: str | None = None, timeout: float = 20.0) -> None:
        if httpx is None:
            raise TransportError("httpx is required for HTTP transport")
        self.base_url = base_url.rstrip("/") + "/"
        self.client = httpx.AsyncClient(timeout=timeout)
        self.token = token

    async def post(self, path: str, json_data: Mapping[str, Any]) -> Mapping[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        url = urljoin(self.base_url, path.lstrip("/"))
        response = await self.client.post(url, json=dict(json_data), headers=headers)
        if response.status_code == 404:
            raise FineNotFoundError("fine not found")
        if response.status_code >= 400:
            raise TransportError(f"HTTP {response.status_code}: {response.text[:200]}")
        return response.json()

    async def close(self) -> None:
        await self.client.aclose()


class MockFineTransport:
    """In-memory transport for examples and tests."""

    def __init__(self, fixtures: Iterable[Mapping[str, Any]] | None = None) -> None:
        self.fixtures: dict[tuple[str, str | None], dict[str, Any]] = {}
        self.calls: list[dict[str, Any]] = []
        for item in fixtures or []:
            plate = normalize_vehicle_number(str(item.get("vehicle_number", "")))
            notice = item.get("notice_number")
            self.fixtures[(plate, str(notice) if notice is not None else None)] = dict(item)

    def post(self, path: str, json_data: Mapping[str, Any]) -> Mapping[str, Any]:
        self.calls.append({"path": path, "json": dict(json_data)})
        if path.endswith("/cases"):
            case_id = json_data.get("case_id") or build_case_id(
                str(json_data.get("vehicle_number", "")),
                str(json_data.get("notice_number") or "no-notice"),
            )
            return {**dict(json_data), "case_id": case_id, "status": json_data.get("status", "new")}
        if path.endswith("/lookup") or path == "/fines/lookup":
            plate = normalize_vehicle_number(str(json_data.get("vehicle_number", "")))
            notice_raw = json_data.get("notice_number")
            notice = str(notice_raw) if notice_raw is not None else None
            payload = self.fixtures.get((plate, notice))
            if payload is None:
                return {
                    "case_id": json_data.get("case_id"),
                    "status": "lookup_not_found",
                    "vehicle_number": plate,
                    "issuer_type": json_data.get("issuer_type", "other"),
                    "notice_number": notice,
                    "payment_allowed": False,
                    "appeal_allowed": False,
                }
            return {**payload, "case_id": json_data.get("case_id") or payload.get("case_id")}
        if path.endswith("/payment-intents") or path == "/fines/payment-intents":
            amount = money_str(json_data["amount_ils"])
            return {
                "case_id": json_data.get("case_id", "mock-case"),
                "amount_ils": amount,
                "official_payment_url": "https://official.example/pay/mock-case",
                "expires_at": None,
            }
        if path.endswith("/appeals") or path == "/fines/appeals":
            return {
                "appeal_reference": "APL-MOCK-001",
                "status": "appeal_submitted",
                "submitted_at": now_iso(),
            }
        raise TransportError(f"unsupported mock path: {path}")


class AsyncMockFineTransport:
    """Async wrapper for MockFineTransport."""

    def __init__(self, fixtures: Iterable[Mapping[str, Any]] | None = None) -> None:
        self.inner = MockFineTransport(fixtures)

    @property
    def calls(self) -> list[dict[str, Any]]:
        return self.inner.calls

    async def post(self, path: str, json_data: Mapping[str, Any]) -> Mapping[str, Any]:
        await asyncio.sleep(0)
        return self.inner.post(path, json_data)


class ParkingFineClient:
    """Synchronous fine workflow client."""

    def __init__(
        self,
        base_url: str = "mock://local",
        token: str | None = None,
        transport: SyncTransport | None = None,
    ) -> None:
        self.transport = transport or (
            MockFineTransport(default_fixtures()) if base_url.startswith("mock://")
            else HttpxSyncTransport(base_url=base_url, token=token)
        )

    def create_case(
        self,
        *,
        issuer_type: IssuerType,
        vehicle_number: str,
        notice_number: str | None = None,
        issuer_name: str | None = None,
        amount_ils: str | int | float | Decimal | None = None,
        notice_date: str | dt.date | None = None,
        due_date: str | dt.date | None = None,
    ) -> CaseRecord:
        case_id = build_case_id(vehicle_number, notice_number)
        record = CaseRecord(
            case_id=case_id,
            issuer_type=issuer_type,
            issuer_name=issuer_name,
            vehicle_number=vehicle_number,
            notice_number=notice_number,
            amount_ils=to_money(amount_ils) if amount_ils is not None else None,
            notice_date=parse_israeli_date(notice_date),
            due_date=parse_israeli_date(due_date),
        )
        payload = self.transport.post("/fines/cases", record.to_dict())
        return CaseRecord(
            case_id=str(payload.get("case_id") or record.case_id),
            issuer_type=payload.get("issuer_type", record.issuer_type),
            issuer_name=payload.get("issuer_name", record.issuer_name),
            vehicle_number=payload.get("vehicle_number", record.vehicle_number),
            notice_number=payload.get("notice_number", record.notice_number),
            status=payload.get("status", record.status),
            amount_ils=payload.get("amount_ils", record.amount_ils),
            notice_date=payload.get("notice_date", record.notice_date),
            due_date=payload.get("due_date", record.due_date),
            created_at=payload.get("created_at", record.created_at),
        )

    def lookup_fine(self, request: FineLookupRequest) -> FineLookupResult:
        payload = self.transport.post("/fines/lookup", request.to_payload())
        return FineLookupResult.from_payload(payload)

    def prepare_payment(
        self,
        case_id: str,
        amount_ils: str | int | float | Decimal,
        *,
        status: FineStatus = "approved_for_payment",
    ) -> PaymentPreparation:
        if status in {"verified_paid", "paid", "cancelled"}:
            raise DuplicatePaymentRiskError("case is already closed or paid")
        if status not in {"approved_for_payment", "verified_unpaid"}:
            raise ValidationError("payment requires verified_unpaid or approved_for_payment status")
        payload = self.transport.post(
            "/fines/payment-intents",
            {"case_id": case_id, "amount_ils": money_str(amount_ils)},
        )
        return PaymentPreparation.from_payload(payload)

    def submit_appeal(
        self,
        case_id: str,
        grounds: str,
        evidence: Iterable[Mapping[str, Any]] | None = None,
        appeal_type: str = "cancellation",
    ) -> AppealSubmission:
        if not grounds.strip():
            raise ValidationError("grounds are required")
        payload = self.transport.post(
            "/fines/appeals",
            {
                "case_id": case_id,
                "appeal_type": appeal_type,
                "grounds": grounds.strip(),
                "evidence": list(evidence or []),
            },
        )
        return AppealSubmission.from_payload(payload)

    def close(self) -> None:
        close = getattr(self.transport, "close", None)
        if callable(close):
            close()


class ParkingFineAsyncClient:
    """Asynchronous fine workflow client."""

    def __init__(
        self,
        base_url: str = "mock://local",
        token: str | None = None,
        transport: AsyncTransport | None = None,
    ) -> None:
        self.transport = transport or (
            AsyncMockFineTransport(default_fixtures()) if base_url.startswith("mock://")
            else HttpxAsyncTransport(base_url=base_url, token=token)
        )

    async def create_case(
        self,
        *,
        issuer_type: IssuerType,
        vehicle_number: str,
        notice_number: str | None = None,
        issuer_name: str | None = None,
        amount_ils: str | int | float | Decimal | None = None,
        notice_date: str | dt.date | None = None,
        due_date: str | dt.date | None = None,
    ) -> CaseRecord:
        case_id = build_case_id(vehicle_number, notice_number)
        record = CaseRecord(
            case_id=case_id,
            issuer_type=issuer_type,
            issuer_name=issuer_name,
            vehicle_number=vehicle_number,
            notice_number=notice_number,
            amount_ils=to_money(amount_ils) if amount_ils is not None else None,
            notice_date=parse_israeli_date(notice_date),
            due_date=parse_israeli_date(due_date),
        )
        payload = await self.transport.post("/fines/cases", record.to_dict())
        return CaseRecord(
            case_id=str(payload.get("case_id") or record.case_id),
            issuer_type=payload.get("issuer_type", record.issuer_type),
            issuer_name=payload.get("issuer_name", record.issuer_name),
            vehicle_number=payload.get("vehicle_number", record.vehicle_number),
            notice_number=payload.get("notice_number", record.notice_number),
            status=payload.get("status", record.status),
            amount_ils=payload.get("amount_ils", record.amount_ils),
            notice_date=payload.get("notice_date", record.notice_date),
            due_date=payload.get("due_date", record.due_date),
            created_at=payload.get("created_at", record.created_at),
        )

    async def lookup_fine(self, request: FineLookupRequest) -> FineLookupResult:
        payload = await self.transport.post("/fines/lookup", request.to_payload())
        return FineLookupResult.from_payload(payload)

    async def prepare_payment(
        self,
        case_id: str,
        amount_ils: str | int | float | Decimal,
        *,
        status: FineStatus = "approved_for_payment",
    ) -> PaymentPreparation:
        if status in {"verified_paid", "paid", "cancelled"}:
            raise DuplicatePaymentRiskError("case is already closed or paid")
        if status not in {"approved_for_payment", "verified_unpaid"}:
            raise ValidationError("payment requires verified_unpaid or approved_for_payment status")
        payload = await self.transport.post(
            "/fines/payment-intents",
            {"case_id": case_id, "amount_ils": money_str(amount_ils)},
        )
        return PaymentPreparation.from_payload(payload)

    async def submit_appeal(
        self,
        case_id: str,
        grounds: str,
        evidence: Iterable[Mapping[str, Any]] | None = None,
        appeal_type: str = "cancellation",
    ) -> AppealSubmission:
        if not grounds.strip():
            raise ValidationError("grounds are required")
        payload = await self.transport.post(
            "/fines/appeals",
            {
                "case_id": case_id,
                "appeal_type": appeal_type,
                "grounds": grounds.strip(),
                "evidence": list(evidence or []),
            },
        )
        return AppealSubmission.from_payload(payload)

    async def close(self) -> None:
        close = getattr(self.transport, "close", None)
        if callable(close):
            result = close()
            if hasattr(result, "__await__"):
                await result


def default_fixtures() -> list[dict[str, Any]]:
    """Return deterministic examples for CLI and tests."""

    return [
        {
            "case_id": "case-muni-1001",
            "status": "verified_unpaid",
            "vehicle_number": "1234567",
            "issuer_type": "municipality",
            "issuer_name": "Example Municipality",
            "notice_number": "1001",
            "amount_ils": "250.00",
            "due_date": "2026-06-08",
            "payment_allowed": True,
            "appeal_allowed": True,
        },
        {
            "case_id": "case-toll-paid",
            "status": "verified_paid",
            "vehicle_number": "7654321",
            "issuer_type": "toll",
            "issuer_name": "Road 6 Example",
            "notice_number": "TOLL-PAID",
            "amount_ils": "42.80",
            "due_date": "2026-05-20",
            "payment_allowed": False,
            "appeal_allowed": False,
            "payment_reference": "RCPT-1",
        },
        {
            "case_id": "case-col-1",
            "status": "collection",
            "vehicle_number": "1111111",
            "issuer_type": "collection",
            "issuer_name": "Collection Example",
            "notice_number": "COL-1",
            "amount_ils": "343.40",
            "due_date": "2026-05-01",
            "payment_allowed": False,
            "appeal_allowed": False,
        },
    ]


def classify_issuer(text: str) -> IssuerType:
    """Classify issuer from free text."""

    value = (text or "").lower()
    hebrew = text or ""
    if any(token in value for token in ("police", "traffic")) or "משטרה" in hebrew:
        return "police"
    if any(token in value for token in ("road 6", "highway 6", "toll", "tunnel", "fast lane")):
        return "toll"
    if any(token in hebrew for token in ("כביש 6", "אגרה", "מנהרות", "נתיב מהיר")):
        return "toll"
    if any(token in value for token in ("collection", "law office")) or "גבייה" in hebrew:
        return "collection"
    if any(token in value for token in ("municipality", "city", "local")):
        return "municipality"
    if any(token in hebrew for token in ("עיריית", "עירייה", "מועצה", "רשות מקומית")):
        return "municipality"
    return "other"


def assess_case(
    *,
    issuer_type: IssuerType,
    status: FineStatus,
    payment_app_matches: bool = False,
    driver_known: bool = False,
    has_points_or_court: bool = False,
    collection_breakdown: bool = True,
    duplicate_risk: bool = False,
) -> Decision:
    """Return a conservative workflow decision."""

    if has_points_or_court or issuer_type == "police" and status == "verified_unpaid":
        return "escalate"
    if duplicate_risk or status in {"verified_paid", "paid", "cancelled", "appeal_submitted"}:
        return "hold"
    if issuer_type == "collection" and not collection_breakdown:
        return "hold"
    if payment_app_matches:
        return "contest"
    if driver_known and issuer_type in {"municipality", "police"}:
        return "transfer"
    if status == "verified_unpaid":
        return "pay"
    return "hold"


def build_checklist(
    issuer_type: IssuerType,
    *,
    status: FineStatus = "new",
    business_vehicle: bool = False,
) -> list[str]:
    """Build an operational checklist for the case."""

    items = [
        "Save the original notice in the case folder.",
        "Normalize vehicle number and record notice number.",
        "Verify the case through the official issuer channel.",
        "Save screenshot or PDF of lookup result.",
        "Record amount, due date, and status in the register.",
    ]
    if issuer_type == "municipality":
        items.extend(
            [
                "Check parking app, resident permit, disabled card, loading permit, and signage evidence.",
                "Use the municipal appeal channel if contest evidence exists.",
            ]
        )
    elif issuer_type == "police":
        items.extend(
            [
                "Check for points, summons, court date, or license consequences.",
                "Escalate before treating as ordinary payment.",
            ]
        )
    elif issuer_type == "toll":
        items.extend(
            [
                "Request trip itemization.",
                "Separate toll principal from enforcement and collection fees.",
                "Check subscription, transponder, lease, or fleet account.",
            ]
        )
    elif issuer_type == "collection":
        items.extend(
            [
                "Verify original issuer and original notice number.",
                "Request itemized debt breakdown before payment.",
            ]
        )
    if business_vehicle:
        items.extend(
            [
                "Identify driver from logs, calendar, GPS, parking app, or vehicle assignment.",
                "Review accounting treatment and employee reimbursement policy.",
            ]
        )
    if status == "lookup_not_found":
        items.append("Contact the issuer and keep evidence of failed lookup.")
    return items


def approval_memo(
    *,
    case_id: str,
    issuer_name: str,
    vehicle_number: str,
    notice_number: str,
    amount_ils: str | int | float | Decimal,
    due_date: str | dt.date,
    approver: str,
    reason: str = "Official lookup matched vehicle, notice, amount, and due date.",
) -> str:
    """Create a neutral payment approval memo."""

    vehicle = normalize_vehicle_number(vehicle_number)
    due = parse_israeli_date(due_date)
    return "\n".join(
        [
            f"Case: {case_id}",
            f"Issuer: {issuer_name}",
            f"Vehicle: {vehicle}",
            f"Notice: {notice_number}",
            f"Amount: ₪{money_str(amount_ils)}",
            f"Due date: {format_he_date(due)}",
            "Decision: Approved for payment",
            f"Reason: {reason}",
            f"Approved by: {approver}",
        ]
    )


def load_cases_csv(path: str | Path) -> list[dict[str, str]]:
    """Load a fine register CSV."""

    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def detect_duplicates(rows: Iterable[Mapping[str, Any]]) -> list[tuple[str, str, str]]:
    """Detect duplicate issuer/vehicle/notice combinations."""

    seen: set[tuple[str, str, str]] = set()
    duplicates: list[tuple[str, str, str]] = []
    for row in rows:
        issuer = str(row.get("issuer_name", "")).strip().lower()
        vehicle_raw = str(row.get("vehicle_number", ""))
        notice = str(row.get("notice_number", "")).strip()
        if not vehicle_raw or not notice:
            continue
        try:
            vehicle = normalize_vehicle_number(vehicle_raw)
        except ValidationError:
            continue
        key = (issuer, vehicle, notice)
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    return duplicates


def redact_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Redact sensitive values from logs."""

    redacted = dict(payload)
    for key in ("recipient_identifier", "id_number", "company_number"):
        if redacted.get(key):
            redacted[key] = mask_identifier(str(redacted[key]))
    if redacted.get("card_number"):
        redacted["card_number"] = "[removed]"
    return redacted


def save_json(path: str | Path, data: Mapping[str, Any]) -> None:
    """Write JSON with UTF-8 encoding."""

    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


__all__ = [
    "AppealSubmission",
    "AsyncMockFineTransport",
    "CaseRecord",
    "Decision",
    "DuplicatePaymentRiskError",
    "EnvironmentName",
    "FineLookupRequest",
    "FineLookupResult",
    "FineNotFoundError",
    "FineStatus",
    "HttpxAsyncTransport",
    "HttpxSyncTransport",
    "IssuerType",
    "LegalEscalationRequired",
    "MockFineTransport",
    "ParkingFineAsyncClient",
    "ParkingFineClient",
    "ParkingFineError",
    "PaymentPreparation",
    "TransportError",
    "ValidationError",
    "approval_memo",
    "assess_case",
    "build_case_id",
    "build_checklist",
    "classify_issuer",
    "default_fixtures",
    "detect_duplicates",
    "format_he_date",
    "load_cases_csv",
    "mask_identifier",
    "money_str",
    "normalize_vehicle_number",
    "parse_israeli_date",
    "redact_payload",
    "save_json",
    "to_money",
]
