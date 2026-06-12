"""Typed client for Israeli Tabu land-registry adapter workflows.

Endpoint details are configurable. Connect the client to an approved gateway,
internal adapter, or local fixture transport.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence


class TabuClientError(Exception):
    """Base exception for client errors."""


class TabuValidationError(TabuClientError, ValueError):
    """Raised when input validation fails."""


class TabuApiError(TabuClientError):
    """Raised when an upstream service returns an error response."""

    def __init__(self, status_code: int, code: str, message: str, payload: Any | None = None) -> None:
        self.status_code = status_code
        self.code = code
        self.payload = payload
        super().__init__(f"{status_code} {code}: {message}")


@dataclass(frozen=True)
class ParcelId:
    """Normalized Israeli property identifier."""

    block: int
    parcel: int
    subparcel: int | None = None

    def __post_init__(self) -> None:
        for name, value, required in (
            ("block", self.block, True),
            ("parcel", self.parcel, True),
            ("subparcel", self.subparcel, False),
        ):
            if value is None and not required:
                continue
            if not isinstance(value, int):
                raise TabuValidationError(f"{name} must be an integer")
            if value <= 0:
                raise TabuValidationError(f"{name} must be positive")
            if value > 999999:
                raise TabuValidationError(f"{name} is unrealistically large")

    def to_query(self) -> dict[str, int]:
        query = {"block": self.block, "parcel": self.parcel}
        if self.subparcel is not None:
            query["subparcel"] = self.subparcel
        return query

    def display_he(self) -> str:
        text = f"גוש {self.block} חלקה {self.parcel}"
        if self.subparcel is not None:
            text += f" תת-חלקה {self.subparcel}"
        return text


@dataclass(frozen=True)
class Encumbrance:
    """Registered restriction, charge, caveat, lien, mortgage, or related right."""

    type: str
    beneficiary: str | None = None
    amount_ils: float | None = None
    registered_date: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "beneficiary": self.beneficiary,
            "amount_ils": self.amount_ils,
            "registered_date": self.registered_date,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class RightRecord:
    """Normalized right-holder row."""

    owner_name: str
    id_masked: str | None
    right_type: str
    share: str | None = None
    deed_date: str | None = None
    deed_number: str | None = None
    encumbrances: tuple[Encumbrance, ...] = field(default_factory=tuple)
    raw: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "owner_name": self.owner_name,
            "id_masked": self.id_masked,
            "right_type": self.right_type,
            "share": self.share,
            "deed_date": self.deed_date,
            "deed_number": self.deed_number,
            "encumbrances": [enc.to_dict() for enc in self.encumbrances],
        }


@dataclass(frozen=True)
class TabuExtract:
    """Normalized land-registry extract."""

    property_id: ParcelId | None
    address: str | None
    retrieved_at: str
    rights: tuple[RightRecord, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    raw: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "property_id": self.property_id.to_query() if self.property_id else None,
            "address": self.address,
            "retrieved_at": self.retrieved_at,
            "rights": [right.to_dict() for right in self.rights],
            "warnings": list(self.warnings),
            "raw": dict(self.raw),
        }

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    @property
    def has_encumbrances(self) -> bool:
        return any(right.encumbrances for right in self.rights)


@dataclass(frozen=True)
class ExtractOrder:
    """Order response for services that require a paid or asynchronous extract workflow."""

    order_id: str
    status: str
    created_at: str
    property_id: ParcelId | None = None
    payment_reference: str | None = None
    raw: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "status": self.status,
            "created_at": self.created_at,
            "property_id": self.property_id.to_query() if self.property_id else None,
            "payment_reference": self.payment_reference,
            "raw": dict(self.raw),
        }

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


@dataclass(frozen=True)
class TabuClientConfig:
    """Client configuration."""

    base_url: str
    api_key: str | None = None
    timeout_seconds: float = 20.0
    parcel_endpoint: str = "/tabu/parcel"
    address_endpoint: str = "/tabu/address"
    order_endpoint: str = "/tabu/extract-orders"
    user_agent: str = "land-registry-tabu-client/2.1"

    def normalized_base_url(self) -> str:
        if not self.base_url:
            raise TabuValidationError("base_url is required")
        return self.base_url.rstrip("/")


class JsonTransport(Protocol):
    """Protocol for synchronous JSON transports."""

    def request_json(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        body: Mapping[str, Any] | None,
        timeout: float,
    ) -> Mapping[str, Any]:
        ...


class UrllibJsonTransport:
    """Small standard-library HTTP transport for JSON APIs."""

    def request_json(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        body: Mapping[str, Any] | None,
        timeout: float,
    ) -> Mapping[str, Any]:
        encoded_body: bytes | None = None
        request_headers = dict(headers)
        if body is not None:
            encoded_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/json")
        request_headers.setdefault("Accept", "application/json")

        request = urllib.request.Request(url, data=encoded_body, method=method.upper(), headers=request_headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
                if not payload:
                    return {}
                return json.loads(payload)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                payload = {"message": raw}
            code = str(payload.get("code") or payload.get("error") or exc.reason or "HTTP_ERROR")
            message = str(payload.get("message") or payload.get("detail") or exc.reason or "HTTP error")
            raise TabuApiError(exc.code, code, message, payload) from exc
        except urllib.error.URLError as exc:
            raise TabuApiError(0, "NETWORK_ERROR", str(exc.reason), None) from exc
        except json.JSONDecodeError as exc:
            raise TabuApiError(0, "INVALID_JSON", str(exc), None) from exc


class FileJsonTransport:
    """Transport that returns JSON fixtures for request paths."""

    def __init__(self, fixture_path: str | os.PathLike[str], order_fixture_path: str | os.PathLike[str] | None = None) -> None:
        self.fixture_path = Path(fixture_path)
        self.order_fixture_path = Path(order_fixture_path) if order_fixture_path else None

    def request_json(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        body: Mapping[str, Any] | None,
        timeout: float,
    ) -> Mapping[str, Any]:
        if "/extract-orders" in url and self.order_fixture_path is not None:
            path = self.order_fixture_path
        else:
            path = self.fixture_path
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if method.upper() == "POST" and "/extract-orders" in url and "order_id" not in payload:
            payload = {
                "order_id": f"ORD-{uuid.uuid4().hex[:12]}",
                "status": "created",
                "created_at": _utc_now(),
                "property": body.get("property_id") if body else None,
                "payment_reference": body.get("payment_reference") if body else None,
                "raw": payload,
            }
        return payload


class LandRegistryTabuClient:
    """Synchronous and asynchronous client for Tabu adapter endpoints."""

    def __init__(self, config: TabuClientConfig, transport: JsonTransport | None = None) -> None:
        self.config = config
        self.transport = transport or UrllibJsonTransport()

    def get_by_parcel(self, parcel_id: ParcelId) -> TabuExtract:
        url = self._build_url(self.config.parcel_endpoint, parcel_id.to_query())
        payload = self.transport.request_json(
            "GET",
            url,
            headers=self._headers(),
            body=None,
            timeout=self.config.timeout_seconds,
        )
        return self.parse_extract(payload, fallback_property_id=parcel_id)

    async def async_get_by_parcel(self, parcel_id: ParcelId) -> TabuExtract:
        return await asyncio.to_thread(self.get_by_parcel, parcel_id)

    def search_by_address(self, *, city: str, street: str, house: str | int) -> TabuExtract:
        city = _required_text(city, "city")
        street = _required_text(street, "street")
        house_text = _required_text(str(house), "house")
        url = self._build_url(self.config.address_endpoint, {"city": city, "street": street, "house": house_text})
        payload = self.transport.request_json(
            "GET",
            url,
            headers=self._headers(),
            body=None,
            timeout=self.config.timeout_seconds,
        )
        return self.parse_extract(payload, fallback_property_id=None)

    async def async_search_by_address(self, *, city: str, street: str, house: str | int) -> TabuExtract:
        return await asyncio.to_thread(self.search_by_address, city=city, street=street, house=house)

    def create_extract_order(
        self,
        parcel_id: ParcelId,
        *,
        purpose: str = "due_diligence",
        language: str = "he",
        payment_reference: str | None = None,
        idempotency_key: str | None = None,
    ) -> ExtractOrder:
        body: dict[str, Any] = {
            "property_id": parcel_id.to_query(),
            "purpose": _required_text(purpose, "purpose"),
            "language": _required_text(language, "language"),
        }
        if payment_reference:
            body["payment_reference"] = payment_reference
        headers = self._headers()
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        url = self._build_url(self.config.order_endpoint, {})
        payload = self.transport.request_json(
            "POST",
            url,
            headers=headers,
            body=body,
            timeout=self.config.timeout_seconds,
        )
        return parse_order(payload, fallback_property_id=parcel_id)

    async def async_create_extract_order(self, parcel_id: ParcelId, **kwargs: Any) -> ExtractOrder:
        return await asyncio.to_thread(self.create_extract_order, parcel_id, **kwargs)

    def get_order_status(self, order_id: str) -> ExtractOrder:
        order_id = _required_text(order_id, "order_id")
        url = self._build_url(f"{self.config.order_endpoint}/{urllib.parse.quote(order_id)}", {})
        payload = self.transport.request_json(
            "GET",
            url,
            headers=self._headers(),
            body=None,
            timeout=self.config.timeout_seconds,
        )
        return parse_order(payload)

    async def async_get_order_status(self, order_id: str) -> ExtractOrder:
        return await asyncio.to_thread(self.get_order_status, order_id)

    def parse_extract(self, payload: Mapping[str, Any], *, fallback_property_id: ParcelId | None = None) -> TabuExtract:
        return parse_extract(payload, fallback_property_id=fallback_property_id)

    def _build_url(self, endpoint: str, params: Mapping[str, Any]) -> str:
        endpoint = "/" + endpoint.strip("/")
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        return f"{self.config.normalized_base_url()}{endpoint}" + (f"?{query}" if query else "")

    def _headers(self) -> dict[str, str]:
        headers = {"User-Agent": self.config.user_agent, "Accept": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers


def parse_extract(payload: Mapping[str, Any], *, fallback_property_id: ParcelId | None = None) -> TabuExtract:
    """Parse English/Hebrew adapter payload into a normalized extract."""

    if not isinstance(payload, Mapping):
        raise TabuValidationError("payload must be a mapping")

    property_payload = _first_mapping(payload, "property", "parcel", "נכס", "זיהוי נכס")
    property_id = _parse_property_id(property_payload) or fallback_property_id
    address = _first_text(property_payload, "address", "כתובת") or _first_text(payload, "address", "כתובת")
    rights_payload = _first_sequence(payload, "rights", "owners", "holders", "בעלי זכויות", "זכויות", "בעלויות")
    rights = tuple(_parse_right(row) for row in rights_payload if isinstance(row, Mapping))

    warnings = tuple(
        str(item)
        for item in _first_sequence(payload, "warnings", "risk_flags", "אזהרות", "דגלי סיכון")
        if str(item).strip()
    )
    if not rights and not warnings:
        warnings = ("No rights were parsed from the response; inspect raw payload.",)

    retrieved_at = _first_text(payload, "retrieved_at", "retrievedAt", "תאריך שליפה")
    if not retrieved_at:
        retrieved_at = _utc_now()

    return TabuExtract(
        property_id=property_id,
        address=address,
        retrieved_at=retrieved_at,
        rights=rights,
        warnings=warnings,
        raw=payload,
    )


def parse_order(payload: Mapping[str, Any], *, fallback_property_id: ParcelId | None = None) -> ExtractOrder:
    """Parse an extract-order response."""

    if not isinstance(payload, Mapping):
        raise TabuValidationError("payload must be a mapping")
    order_id = _first_text(payload, "order_id", "id", "orderId", "מספר הזמנה")
    if not order_id:
        order_id = f"ORD-{uuid.uuid4().hex[:12]}"
    status = _first_text(payload, "status", "מצב") or "created"
    created_at = _first_text(payload, "created_at", "createdAt", "תאריך יצירה") or _utc_now()
    property_payload = _first_mapping(payload, "property", "property_id", "נכס")
    property_id = _parse_property_id(property_payload) or fallback_property_id
    payment_reference = _first_text(payload, "payment_reference", "paymentReference", "אסמכתת תשלום")
    return ExtractOrder(
        order_id=order_id,
        status=status,
        created_at=created_at,
        property_id=property_id,
        payment_reference=payment_reference,
        raw=payload,
    )


def normalize_right_type(value: str) -> str:
    text = value.strip().lower()
    mapping = {
        "בעלות": "ownership",
        "ownership": "ownership",
        "חכירה": "lease",
        "lease": "lease",
        "חכירה לדורות": "long_lease",
        "long lease": "long_lease",
        "משכנתה": "mortgage",
        "משכנתא": "mortgage",
        "mortgage": "mortgage",
        "שעבוד": "lien",
        "lien": "lien",
        "עיקול": "attachment",
        "attachment": "attachment",
        "הערת אזהרה": "caveat",
        "caveat": "caveat",
        "זיקת הנאה": "easement",
        "easement": "easement",
    }
    return mapping.get(text, text.replace(" ", "_"))


def normalize_share(value: str | int | float | None) -> str | None:
    """Normalize common share formats to a compact fraction string."""

    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    if "/" in text:
        left, right = text.split("/", 1)
        try:
            fraction = Fraction(int(left.strip()), int(right.strip()))
        except (ValueError, ZeroDivisionError) as exc:
            raise TabuValidationError(f"invalid share fraction: {value}") from exc
        return f"{fraction.numerator}/{fraction.denominator}"

    if text.endswith("%"):
        try:
            fraction = Fraction(float(text[:-1].strip()) / 100).limit_denominator(1000)
        except ValueError as exc:
            raise TabuValidationError(f"invalid share percent: {value}") from exc
        return f"{fraction.numerator}/{fraction.denominator}"

    try:
        fraction = Fraction(float(text)).limit_denominator(1000)
        return f"{fraction.numerator}/{fraction.denominator}"
    except ValueError:
        return text


def normalize_date(value: str | None) -> str | None:
    """Normalize common ISO or Israeli dates to DD/MM/YYYY when possible."""

    if not value:
        return None
    text = value.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text[:10], fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return text


def validate_israeli_id(value: str | int) -> bool:
    """Validate a 9-digit Israeli identity number checksum."""

    digits = re.sub(r"\D", "", str(value))
    if not digits or len(digits) > 9:
        return False
    digits = digits.zfill(9)
    total = 0
    for index, char in enumerate(digits):
        num = int(char) * (1 if index % 2 == 0 else 2)
        if num > 9:
            num -= 9
        total += num
    return total % 10 == 0


def mask_identifier(value: str | int, *, visible_digits: int = 3) -> str:
    digits = re.sub(r"\D", "", str(value))
    if not digits:
        return ""
    if len(digits) <= visible_digits:
        return "*" * len(digits)
    return "*" * (len(digits) - visible_digits) + digits[-visible_digits:]


def extract_risk_flags(extract: TabuExtract) -> list[str]:
    """Create concise practical risk flags from a normalized extract."""

    flags: list[str] = []
    if extract.property_id is None:
        flags.append("Property identifier was not parsed; verify block/parcel/subparcel.")
    if not extract.rights:
        flags.append("No rights were parsed; inspect raw extract.")
    for right in extract.rights:
        if right.share is None:
            flags.append(f"Share is missing for {right.owner_name}.")
        for enc in right.encumbrances:
            if enc.type == "mortgage":
                flags.append("Mortgage requires release, consent, or escrow instructions before transfer.")
            elif enc.type == "caveat":
                flags.append("Caveat requires beneficiary and legal-basis review.")
            elif enc.type in {"attachment", "lien"}:
                flags.append("Attachment or lien requires legal review before relying on the property.")
            elif enc.type == "easement":
                flags.append("Easement may affect access, use, utilities, or business operations.")
            elif enc.type == "long_lease":
                flags.append("Long lease requires term, renewal, and transfer review.")
    for warning in extract.warnings:
        if warning not in flags:
            flags.append(warning)
    return flags


def _parse_property_id(payload: Mapping[str, Any] | None) -> ParcelId | None:
    if not payload:
        return None
    block = _first_value(payload, "block", "gush", "גוש")
    parcel = _first_value(payload, "parcel", "helka", "חלקה")
    subparcel = _first_value(payload, "subparcel", "tat_helka", "tatHelka", "תת חלקה", "תת-חלקה")
    if block is None or parcel is None:
        return None
    return ParcelId(_to_int(block, "block"), _to_int(parcel, "parcel"), _to_optional_int(subparcel, "subparcel"))


def _parse_right(row: Mapping[str, Any]) -> RightRecord:
    owner_name = _first_text(row, "owner_name", "holder_name", "name", "שם בעל זכות", "שם") or "Unknown right holder"
    raw_identifier = _first_text(row, "id", "identifier", "identity_number", "תעודת זהות", "מספר מזהה", "ח.פ.")
    right_type = _first_text(row, "right_type", "type", "סוג זכות") or "unknown"
    share_raw = _first_text(row, "share", "fraction", "חלק", "חלק יחסי")
    deed_date = normalize_date(_first_text(row, "deed_date", "date", "תאריך שטר", "תאריך"))
    deed_number = _first_text(row, "deed_number", "deed", "מספר שטר")
    encumbrances_payload = _first_sequence(row, "encumbrances", "restrictions", "שעבודים", "מגבלות", "הערות")
    encumbrances = tuple(_parse_encumbrance(item) for item in encumbrances_payload if isinstance(item, Mapping))
    return RightRecord(
        owner_name=owner_name,
        id_masked=mask_identifier(raw_identifier) if raw_identifier else None,
        right_type=normalize_right_type(right_type),
        share=normalize_share(share_raw) if share_raw else None,
        deed_date=deed_date,
        deed_number=deed_number,
        encumbrances=encumbrances,
        raw=row,
    )


def _parse_encumbrance(row: Mapping[str, Any]) -> Encumbrance:
    enc_type = _first_text(row, "type", "encumbrance_type", "סוג", "סוג שעבוד") or "unknown"
    beneficiary = _first_text(row, "beneficiary", "holder", "creditor", "מוטב", "נושה")
    amount = _first_value(row, "amount_ils", "amount", "סכום", "סכום בשח")
    date = normalize_date(_first_text(row, "registered_date", "date", "תאריך רישום", "תאריך"))
    notes = _first_text(row, "notes", "description", "הערות", "תיאור")
    return Encumbrance(
        type=normalize_right_type(enc_type),
        beneficiary=beneficiary,
        amount_ils=_to_optional_float(amount),
        registered_date=date,
        notes=notes,
    )


def _required_text(value: str, name: str) -> str:
    text = value.strip()
    if not text:
        raise TabuValidationError(f"{name} is required")
    return text


def _first_value(mapping: Mapping[str, Any] | None, *keys: str) -> Any | None:
    if not mapping:
        return None
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return None


def _first_text(mapping: Mapping[str, Any] | None, *keys: str) -> str | None:
    value = _first_value(mapping, *keys)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _first_mapping(mapping: Mapping[str, Any], *keys: str) -> Mapping[str, Any] | None:
    value = _first_value(mapping, *keys)
    return value if isinstance(value, Mapping) else None


def _first_sequence(mapping: Mapping[str, Any], *keys: str) -> Sequence[Any]:
    value = _first_value(mapping, *keys)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return []


def _to_int(value: Any, name: str) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise TabuValidationError(f"{name} must be an integer") from exc


def _to_optional_int(value: Any, name: str) -> int | None:
    if value in (None, ""):
        return None
    return _to_int(value, name)


def _to_optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "").replace("₪", "").strip())
    except ValueError:
        return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
