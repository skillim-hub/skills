#!/usr/bin/env python3
"""Typed catalog helper for Israeli SKU, VAT, price, and stock workflows."""

from __future__ import annotations

import asyncio
import csv
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

MONEY_QUANT = Decimal("0.01")
SKU_PATTERN = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")
DEFAULT_CURRENCY = "ILS"


class CatalogError(ValueError):
    """Base validation error for catalog operations."""


class DuplicateSKUError(CatalogError):
    """Raised when an SKU already exists."""


class ItemNotFoundError(CatalogError):
    """Raised when a requested SKU does not exist."""


def decimal_from(value: str | int | float | Decimal, *, field_name: str = "value") -> Decimal:
    """Convert a supported input to Decimal using string conversion."""
    if isinstance(value, Decimal):
        result = value
    else:
        text = str(value).strip().replace("₪", "").replace(",", "")
        if text.endswith("%"):
            text = text[:-1].strip()
            try:
                return (Decimal(text) / Decimal("100")).quantize(Decimal("0.0001"))
            except InvalidOperation as exc:
                raise CatalogError(f"{field_name} must be decimal-compatible") from exc
        try:
            result = Decimal(text)
        except InvalidOperation as exc:
            raise CatalogError(f"{field_name} must be decimal-compatible") from exc
    if result.is_nan():
        raise CatalogError(f"{field_name} must not be NaN")
    return result


def money(value: str | int | float | Decimal) -> Decimal:
    """Round a value to two decimal places using common commercial rounding."""
    return decimal_from(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def decimal_text(value: str | int | float | Decimal, *, places: str = "0.01") -> str:
    """Return a normalized decimal string."""
    return str(decimal_from(value).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def normalize_sku(sku: str) -> str:
    """Normalize and validate an internal SKU."""
    normalized = sku.strip().upper()
    if not normalized:
        raise CatalogError("SKU is required")
    if not SKU_PATTERN.match(normalized):
        raise CatalogError("SKU must use uppercase Latin letters, digits, and hyphens")
    return normalized


def now_utc() -> str:
    """Return an ISO timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def calculate_price_with_vat(price_before_vat: str | Decimal, vat_rate: str | Decimal) -> Decimal:
    """Calculate a VAT-inclusive price rounded to 2 decimals."""
    base = decimal_from(price_before_vat, field_name="price_before_vat")
    rate = decimal_from(vat_rate, field_name="vat_rate")
    return money(base * (Decimal("1") + rate))


def calculate_price_before_vat(price_with_vat: str | Decimal, vat_rate: str | Decimal) -> Decimal:
    """Calculate a before-VAT price rounded to 2 decimals."""
    final = decimal_from(price_with_vat, field_name="price_with_vat")
    rate = decimal_from(vat_rate, field_name="vat_rate")
    if rate <= Decimal("-1"):
        raise CatalogError("vat_rate must be greater than -1")
    return money(final / (Decimal("1") + rate))


def validate_vat_rate(vat_rate: str | Decimal) -> Decimal:
    """Validate VAT rate as a decimal fraction between 0 and 1."""
    rate = decimal_from(vat_rate, field_name="vat_rate")
    if rate < Decimal("0") or rate > Decimal("1"):
        raise CatalogError("vat_rate must be between 0 and 1")
    return rate


@dataclass(slots=True)
class CatalogItem:
    """A single product or service catalog row."""

    sku: str
    name: str
    unit: str
    price_before_vat: str
    vat_rate: str = "0.18"
    stock_quantity: str = "0"
    reorder_point: str = "0"
    category: str = ""
    name_en: str = ""
    barcode: str = ""
    supplier_name: str = ""
    supplier_sku: str = ""
    active: bool = True
    tax_treatment: str = "standard_domestic_vat"
    notes: str = ""
    updated_at: str = field(default_factory=now_utc)

    def __post_init__(self) -> None:
        self.sku = normalize_sku(self.sku)
        self.name = self.name.strip()
        self.unit = self.unit.strip() or "unit"
        if not self.name:
            raise CatalogError("name is required")
        validate_vat_rate(self.vat_rate)
        if decimal_from(self.price_before_vat, field_name="price_before_vat") < 0:
            raise CatalogError("price_before_vat must be non-negative")
        decimal_from(self.stock_quantity, field_name="stock_quantity")
        if decimal_from(self.reorder_point, field_name="reorder_point") < 0:
            raise CatalogError("reorder_point must be non-negative")
        if self.barcode and not self.barcode.isdigit():
            raise CatalogError("barcode must contain digits only")
        self.price_before_vat = decimal_text(self.price_before_vat)
        self.vat_rate = str(validate_vat_rate(self.vat_rate).normalize())
        self.stock_quantity = str(decimal_from(self.stock_quantity, field_name="stock_quantity").normalize())
        self.reorder_point = str(decimal_from(self.reorder_point, field_name="reorder_point").normalize())

    @property
    def price_with_vat(self) -> str:
        return str(calculate_price_with_vat(self.price_before_vat, self.vat_rate))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["price_with_vat"] = self.price_with_vat
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CatalogItem":
        clean = dict(data)
        clean.pop("price_with_vat", None)
        if "name_he" in clean and "name" not in clean:
            clean["name"] = clean.pop("name_he")
        allowed = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in clean.items() if k in allowed})


@dataclass(slots=True)
class StockMovement:
    """An auditable stock change."""

    sku: str
    quantity_delta: str
    reason: str
    reference: str = ""
    note: str = ""
    timestamp: str = field(default_factory=now_utc)

    def __post_init__(self) -> None:
        self.sku = normalize_sku(self.sku)
        if not self.reason.strip():
            raise CatalogError("reason is required")
        decimal_from(self.quantity_delta, field_name="quantity_delta")
        self.quantity_delta = str(decimal_from(self.quantity_delta, field_name="quantity_delta").normalize())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "StockMovement":
        return cls(**dict(data))


class InventoryCatalog:
    """Synchronous catalog manager for JSON and CSV files."""

    def __init__(self, *, currency: str = DEFAULT_CURRENCY, items: Iterable[CatalogItem] | None = None) -> None:
        self.currency = currency
        self.items: dict[str, CatalogItem] = {}
        self.movements: list[StockMovement] = []
        if items:
            for item in items:
                self.add_item(item)

    def add_item(self, item: CatalogItem, *, replace: bool = False) -> CatalogItem:
        if item.sku in self.items and not replace:
            raise DuplicateSKUError(f"SKU already exists: {item.sku}")
        if item.barcode:
            conflict = self.find_by_barcode(item.barcode)
            if conflict and conflict.sku != item.sku and conflict.active and item.active:
                raise CatalogError(f"barcode already used by active SKU: {conflict.sku}")
        item.updated_at = now_utc()
        self.items[item.sku] = item
        return item

    def update_item(self, sku: str, **changes: Any) -> CatalogItem:
        item = self.get_item(sku)
        data = asdict(item)
        data.update(changes)
        data["sku"] = item.sku
        updated = CatalogItem.from_dict(data)
        return self.add_item(updated, replace=True)

    def retire_item(self, sku: str, *, note: str = "") -> CatalogItem:
        item = self.get_item(sku)
        combined_note = item.notes
        if note:
            combined_note = (combined_note + " | " if combined_note else "") + note
        return self.update_item(item.sku, active=False, notes=combined_note)

    def get_item(self, sku: str) -> CatalogItem:
        normalized = normalize_sku(sku)
        try:
            return self.items[normalized]
        except KeyError as exc:
            raise ItemNotFoundError(f"SKU not found: {normalized}") from exc

    def find_by_barcode(self, barcode: str) -> CatalogItem | None:
        for item in self.items.values():
            if item.barcode == barcode:
                return item
        return None

    def list_items(self, *, active_only: bool = False, category: str | None = None) -> list[CatalogItem]:
        results = list(self.items.values())
        if active_only:
            results = [item for item in results if item.active]
        if category is not None:
            results = [item for item in results if item.category == category]
        return sorted(results, key=lambda item: item.sku)

    def adjust_stock(self, sku: str, quantity_delta: str | int | Decimal, *, reason: str, reference: str = "", note: str = "") -> StockMovement:
        item = self.get_item(sku)
        delta = decimal_from(quantity_delta, field_name="quantity_delta")
        new_quantity = decimal_from(item.stock_quantity, field_name="stock_quantity") + delta
        movement = StockMovement(sku=item.sku, quantity_delta=str(delta), reason=reason, reference=reference, note=note)
        self.movements.append(movement)
        self.update_item(item.sku, stock_quantity=str(new_quantity))
        return movement

    def set_stock_from_count(self, sku: str, counted_quantity: str | int | Decimal, *, reference: str, note: str = "") -> StockMovement | None:
        item = self.get_item(sku)
        counted = decimal_from(counted_quantity, field_name="counted_quantity")
        current = decimal_from(item.stock_quantity, field_name="stock_quantity")
        delta = counted - current
        if delta == 0:
            return None
        return self.adjust_stock(item.sku, delta, reason="count_adjustment", reference=reference, note=note)

    def low_stock(self, *, include_inactive: bool = False) -> list[CatalogItem]:
        results: list[CatalogItem] = []
        for item in self.items.values():
            if not include_inactive and not item.active:
                continue
            if decimal_from(item.reorder_point) <= 0:
                continue
            if decimal_from(item.stock_quantity) <= decimal_from(item.reorder_point):
                results.append(item)
        return sorted(results, key=lambda item: (item.supplier_name, item.category, item.sku))

    def validate(self) -> list[str]:
        errors: list[str] = []
        seen_barcodes: dict[str, str] = {}
        for item in self.items.values():
            try:
                CatalogItem.from_dict(item.to_dict())
            except CatalogError as exc:
                errors.append(f"{item.sku}: {exc}")
            if item.barcode and item.active:
                other = seen_barcodes.get(item.barcode)
                if other:
                    errors.append(f"{item.sku}: barcode also used by {other}")
                seen_barcodes[item.barcode] = item.sku
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "currency": self.currency,
            "items": [item.to_dict() for item in self.list_items()],
            "movements": [movement.to_dict() for movement in self.movements],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "InventoryCatalog":
        catalog = cls(currency=str(data.get("currency", DEFAULT_CURRENCY)))
        for raw in data.get("items", []):
            catalog.add_item(CatalogItem.from_dict(raw))
        for raw_movement in data.get("movements", []):
            catalog.movements.append(StockMovement.from_dict(raw_movement))
        return catalog

    def save_json(self, path: str | Path) -> Path:
        target = Path(path)
        target.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    @classmethod
    def load_json(cls, path: str | Path) -> "InventoryCatalog":
        source = Path(path)
        if not source.exists():
            raise FileNotFoundError(source)
        return cls.from_dict(json.loads(source.read_text(encoding="utf-8")))

    def export_csv(self, path: str | Path, *, include_inactive: bool = False, utf8_bom: bool = False) -> Path:
        target = Path(path)
        encoding = "utf-8-sig" if utf8_bom else "utf-8"
        fields = [
            "sku", "name", "name_en", "category", "unit", "price_before_vat", "vat_rate", "price_with_vat",
            "stock_quantity", "reorder_point", "barcode", "supplier_name", "supplier_sku", "active", "tax_treatment", "notes", "updated_at"
        ]
        with target.open("w", encoding=encoding, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for item in self.list_items(active_only=not include_inactive):
                row = item.to_dict()
                writer.writerow({field: row.get(field, "") for field in fields})
        return target

    @classmethod
    def import_csv(cls, path: str | Path, *, currency: str = DEFAULT_CURRENCY, replace: bool = False) -> "InventoryCatalog":
        source = Path(path)
        catalog = cls(currency=currency)
        with source.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise CatalogError("CSV must include a header row")
            for row_number, row in enumerate(reader, start=2):
                if not any((value or "").strip() for value in row.values()):
                    continue
                try:
                    item = CatalogItem.from_dict(row)
                    catalog.add_item(item, replace=replace)
                except Exception as exc:
                    raise CatalogError(f"CSV row {row_number}: {exc}") from exc
        return catalog

    def merge(self, other: "InventoryCatalog", *, replace: bool = False) -> None:
        for item in other.list_items():
            self.add_item(item, replace=replace)


class AsyncInventoryCatalog:
    """Async wrapper around file operations for applications that need awaitable APIs."""

    def __init__(self, catalog: InventoryCatalog | None = None) -> None:
        self.catalog = catalog or InventoryCatalog()

    async def save_json(self, path: str | Path) -> Path:
        return await asyncio.to_thread(self.catalog.save_json, path)

    @classmethod
    async def load_json(cls, path: str | Path) -> "AsyncInventoryCatalog":
        catalog = await asyncio.to_thread(InventoryCatalog.load_json, path)
        return cls(catalog)

    async def export_csv(self, path: str | Path, *, include_inactive: bool = False, utf8_bom: bool = False) -> Path:
        return await asyncio.to_thread(self.catalog.export_csv, path, include_inactive=include_inactive, utf8_bom=utf8_bom)

    @classmethod
    async def import_csv(cls, path: str | Path, *, currency: str = DEFAULT_CURRENCY, replace: bool = False) -> "AsyncInventoryCatalog":
        catalog = await asyncio.to_thread(InventoryCatalog.import_csv, path, currency=currency, replace=replace)
        return cls(catalog)

    async def add_item(self, item: CatalogItem, *, replace: bool = False) -> CatalogItem:
        return await asyncio.to_thread(self.catalog.add_item, item, replace=replace)

    async def adjust_stock(self, sku: str, quantity_delta: str | int | Decimal, *, reason: str, reference: str = "", note: str = "") -> StockMovement:
        return await asyncio.to_thread(self.catalog.adjust_stock, sku, quantity_delta, reason=reason, reference=reference, note=note)


def consumer_export_rows(catalog: InventoryCatalog) -> list[dict[str, str]]:
    """Return sanitized consumer price-list rows."""
    rows: list[dict[str, str]] = []
    for item in catalog.list_items(active_only=True):
        rows.append({
            "sku": item.sku,
            "name": item.name,
            "unit": item.unit,
            "price_with_vat": item.price_with_vat,
            "currency": catalog.currency,
            "notes": "מחיר כולל מע״מ" if item.vat_rate != "0" else item.notes,
        })
    return rows


def b2b_export_rows(catalog: InventoryCatalog) -> list[dict[str, str]]:
    """Return B2B price-list rows with VAT details."""
    rows: list[dict[str, str]] = []
    for item in catalog.list_items(active_only=True):
        rows.append({
            "sku": item.sku,
            "name": item.name,
            "unit": item.unit,
            "price_before_vat": item.price_before_vat,
            "vat_rate": item.vat_rate,
            "price_with_vat": item.price_with_vat,
            "currency": catalog.currency,
        })
    return rows


__all__ = [
    "CatalogError",
    "DuplicateSKUError",
    "ItemNotFoundError",
    "CatalogItem",
    "StockMovement",
    "InventoryCatalog",
    "AsyncInventoryCatalog",
    "decimal_from",
    "money",
    "decimal_text",
    "normalize_sku",
    "calculate_price_with_vat",
    "calculate_price_before_vat",
    "validate_vat_rate",
    "consumer_export_rows",
    "b2b_export_rows",
]
