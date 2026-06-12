
"""Local budget and cash-flow forecasting utilities for Israeli planning scenarios."""

from __future__ import annotations

import asyncio
import csv
import json
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Optional

Cadence = Literal["none", "monthly", "bimonthly", "manual"]
Status = Literal["ok", "buffer_warning", "negative_cash"]
Environment = Literal["sandbox", "production"]


class ForecastError(ValueError):
    """Raised when forecast input cannot be processed."""


@dataclass(frozen=True)
class Transaction:
    """A dated cash movement."""

    date: date
    amount: float
    description: str
    category: str = "general"
    taxable: bool = True
    gross: bool = True
    notes: str = ""

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "Transaction":
        try:
            raw_date = data["date"]
            amount = float(data["amount"])
        except KeyError as exc:
            raise ForecastError(f"Missing transaction field: {exc.args[0]}") from exc
        if amount < 0:
            raise ForecastError("NEGATIVE_AMOUNT: transaction amounts must be positive")
        return cls(
            date=parse_date(raw_date),
            amount=amount,
            description=str(data.get("description", "")),
            category=str(data.get("category", "general")),
            taxable=parse_bool(data.get("taxable", True)),
            gross=parse_bool(data.get("gross", True)),
            notes=str(data.get("notes", "")),
        )


@dataclass(frozen=True)
class TaxProfile:
    """Planning assumptions for Israeli tax-related reserves."""

    vat_rate: float = 0.0
    vat_cadence: Cadence = "none"
    vat_amounts_are_gross: bool = True
    income_tax_advance_rate: float = 0.0
    bituach_leumi_rate: float = 0.0
    withholding_tax_rate: float = 0.0
    reserve_mode: Literal["cash", "invoice", "none"] = "cash"
    reviewed_on: Optional[str] = None
    source_note: str = ""

    @classmethod
    def from_mapping(cls, data: Optional[dict[str, Any]]) -> "TaxProfile":
        data = data or {}
        cadence = str(data.get("vat_cadence", "none")).lower()
        if cadence not in {"none", "monthly", "bimonthly", "manual"}:
            raise ForecastError("UNKNOWN_CADENCE: use none, monthly, bimonthly, or manual")
        reserve_mode = str(data.get("reserve_mode", "cash")).lower()
        if reserve_mode not in {"cash", "invoice", "none"}:
            raise ForecastError("UNKNOWN_RESERVE_MODE: use cash, invoice, or none")
        profile = cls(
            vat_rate=float(data.get("vat_rate", 0.0)),
            vat_cadence=cadence,  # type: ignore[arg-type]
            vat_amounts_are_gross=parse_bool(data.get("vat_amounts_are_gross", True)),
            income_tax_advance_rate=float(data.get("income_tax_advance_rate", 0.0)),
            bituach_leumi_rate=float(data.get("bituach_leumi_rate", 0.0)),
            withholding_tax_rate=float(data.get("withholding_tax_rate", 0.0)),
            reserve_mode=reserve_mode,  # type: ignore[arg-type]
            reviewed_on=data.get("reviewed_on"),
            source_note=str(data.get("source_note", "")),
        )
        for name in ("vat_rate", "income_tax_advance_rate", "bituach_leumi_rate", "withholding_tax_rate"):
            value = getattr(profile, name)
            if value < 0:
                raise ForecastError(f"NEGATIVE_RATE: {name} must be non-negative")
            if value > 1:
                raise ForecastError(f"RATE_TOO_HIGH: {name} should be decimal, for example 0.18")
        return profile


@dataclass(frozen=True)
class ForecastConfig:
    """Top-level forecast configuration."""

    opening_balance: float
    start_month: str
    months: int
    cash_in: list[Transaction] = field(default_factory=list)
    cash_out: list[Transaction] = field(default_factory=list)
    tax_profile: TaxProfile = field(default_factory=TaxProfile)
    buffer: float = 0.0
    opening_protected_reserve: float = 0.0
    environment: Environment = "sandbox"

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ForecastConfig":
        try:
            opening_balance = float(data["opening_balance"])
            start_month = str(data["start_month"])
            months = int(data["months"])
        except KeyError as exc:
            raise ForecastError(f"Missing forecast field: {exc.args[0]}") from exc
        validate_month(start_month)
        if months < 1:
            raise ForecastError("NEGATIVE_MONTHS: months must be at least 1")
        if months > 60:
            raise ForecastError("TOO_LONG: use 60 months or less")
        environment = str(data.get("environment", "sandbox")).lower()
        if environment not in {"sandbox", "production"}:
            raise ForecastError("UNKNOWN_ENVIRONMENT: use sandbox or production")
        return cls(
            opening_balance=opening_balance,
            start_month=start_month,
            months=months,
            cash_in=[Transaction.from_mapping(item) for item in data.get("cash_in", [])],
            cash_out=[Transaction.from_mapping(item) for item in data.get("cash_out", [])],
            tax_profile=TaxProfile.from_mapping(data.get("tax_profile")),
            buffer=float(data.get("buffer", 0.0)),
            opening_protected_reserve=float(data.get("opening_protected_reserve", 0.0)),
            environment=environment,  # type: ignore[arg-type]
        )


@dataclass(frozen=True)
class ForecastRow:
    """Monthly forecast result."""

    month: str
    opening_balance: float
    cash_in: float
    cash_out: float
    tax_reserved: float
    tax_paid: float
    closing_balance: float
    protected_reserve: float
    free_cash: float
    status: Status

    def as_dict(self) -> dict[str, Any]:
        return {
            "month": self.month,
            "opening_balance": round_money(self.opening_balance),
            "cash_in": round_money(self.cash_in),
            "cash_out": round_money(self.cash_out),
            "tax_reserved": round_money(self.tax_reserved),
            "tax_paid": round_money(self.tax_paid),
            "closing_balance": round_money(self.closing_balance),
            "protected_reserve": round_money(self.protected_reserve),
            "free_cash": round_money(self.free_cash),
            "status": self.status,
        }


@dataclass(frozen=True)
class ForecastResult:
    """Forecast output with summary and warnings."""

    rows: list[ForecastRow]
    warnings: list[str] = field(default_factory=list)
    forecast_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    environment: Environment = "sandbox"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def summary(self) -> dict[str, Any]:
        if not self.rows:
            return {"months": 0, "minimum_closing_balance": 0.0, "minimum_free_cash": 0.0, "first_negative_month": None}
        first_negative = next((row.month for row in self.rows if row.closing_balance < 0), None)
        return {
            "start_month": self.rows[0].month,
            "months": len(self.rows),
            "minimum_closing_balance": round_money(min(row.closing_balance for row in self.rows)),
            "minimum_free_cash": round_money(min(row.free_cash for row in self.rows)),
            "first_negative_month": first_negative,
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.forecast_id,
            "environment": self.environment,
            "created_at": self.created_at,
            "summary": self.summary,
            "rows": [row.as_dict() for row in self.rows],
            "warnings": list(self.warnings),
        }


class CashFlowForecaster:
    """Synchronous forecast client."""

    def forecast(self, config: ForecastConfig | dict[str, Any]) -> ForecastResult:
        cfg = config if isinstance(config, ForecastConfig) else ForecastConfig.from_mapping(config)
        warnings = validate_warnings(cfg)
        opening = cfg.opening_balance
        protected = cfg.opening_protected_reserve
        reserve_queue: list[float] = []
        rows: list[ForecastRow] = []
        for idx, month in enumerate(month_sequence(cfg.start_month, cfg.months)):
            receipts = sum(t.amount for t in cfg.cash_in if to_month(t.date) == month)
            payments = sum(t.amount for t in cfg.cash_out if to_month(t.date) == month)
            reserved = estimate_tax_reserve([t for t in cfg.cash_in if to_month(t.date) == month], cfg.tax_profile)
            reserve_queue.append(reserved)
            tax_paid = scheduled_tax_payment(
                cadence=cfg.tax_profile.vat_cadence,
                month_index=idx,
                reserve_queue=reserve_queue,
                profile=cfg.tax_profile,
            )
            closing = opening + receipts - payments - tax_paid
            protected = max(0.0, protected + reserved - tax_paid)
            free_cash = closing - protected
            status: Status = "negative_cash" if closing < 0 else ("buffer_warning" if free_cash < cfg.buffer else "ok")
            rows.append(ForecastRow(month, opening, receipts, payments, reserved, tax_paid, closing, protected, free_cash, status))
            opening = closing
        return ForecastResult(rows=rows, warnings=warnings, environment=cfg.environment)

    def forecast_from_json(self, path: str | Path, *, environment: Environment | None = None) -> ForecastResult:
        data = load_json(path)
        if environment is not None:
            data["environment"] = environment
        return self.forecast(data)

    def forecast_from_csv(
        self,
        path: str | Path,
        *,
        opening_balance: float,
        start_month: str,
        months: int,
        tax_profile: Optional[dict[str, Any]] = None,
        buffer: float = 0.0,
        environment: Environment = "sandbox",
    ) -> ForecastResult:
        data = load_csv_as_config(
            path,
            opening_balance=opening_balance,
            start_month=start_month,
            months=months,
            tax_profile=tax_profile,
            buffer=buffer,
            environment=environment,
        )
        return self.forecast(data)


class AsyncCashFlowForecaster:
    """Async wrapper for integration in async applications."""

    def __init__(self, sync_client: Optional[CashFlowForecaster] = None) -> None:
        self.sync_client = sync_client or CashFlowForecaster()

    async def forecast(self, config: ForecastConfig | dict[str, Any]) -> ForecastResult:
        await asyncio.sleep(0)
        return self.sync_client.forecast(config)

    async def forecast_from_json(self, path: str | Path, *, environment: Environment | None = None) -> ForecastResult:
        await asyncio.sleep(0)
        return self.sync_client.forecast_from_json(path, environment=environment)


class ForecastStore:
    """Local JSON-file store for saved forecast runs."""

    def __init__(self, directory: str | Path = ".forecasts") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, result: ForecastResult) -> str:
        path = self.directory / f"{result.forecast_id}.json"
        path.write_text(json.dumps(result.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return result.forecast_id

    def load(self, forecast_id: str) -> dict[str, Any]:
        if not forecast_id or not all(ch in "0123456789abcdef" for ch in forecast_id.lower()):
            raise ForecastError("INVALID_ID: forecast id must be hexadecimal")
        path = self.directory / f"{forecast_id}.json"
        if not path.exists():
            raise ForecastError(f"MISSING_FORECAST: {forecast_id}")
        return json.loads(path.read_text(encoding="utf-8"))


def parse_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ForecastError("INVALID_DATE: use YYYY-MM-DD") from exc


def validate_month(value: str) -> None:
    if not isinstance(value, str) or len(value) != 7 or value[4] != "-":
        raise ForecastError("INVALID_MONTH: use YYYY-MM")
    year, month = value.split("-")
    if not (year.isdigit() and month.isdigit() and 1 <= int(month) <= 12):
        raise ForecastError("INVALID_MONTH: use YYYY-MM")


def to_month(value: date) -> str:
    return f"{value.year:04d}-{value.month:02d}"


def month_sequence(start_month: str, months: int) -> list[str]:
    validate_month(start_month)
    year, month = int(start_month[:4]), int(start_month[5:])
    output: list[str] = []
    for _ in range(months):
        output.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            year += 1
            month = 1
    return output


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "כן"}:
        return True
    if text in {"0", "false", "no", "n", "לא"}:
        return False
    return bool(value)


def estimate_tax_reserve(transactions: Iterable[Transaction], profile: TaxProfile) -> float:
    if profile.reserve_mode == "none":
        return 0.0
    total = 0.0
    for transaction in transactions:
        if not transaction.taxable:
            continue
        amount = transaction.amount
        vat = 0.0
        if profile.vat_cadence != "none" and profile.vat_rate > 0:
            if transaction.gross:
                vat = amount * profile.vat_rate / (1 + profile.vat_rate)
                taxable_base = amount - vat
            else:
                vat = amount * profile.vat_rate
                taxable_base = amount
        else:
            taxable_base = amount
        total += vat + taxable_base * profile.income_tax_advance_rate + taxable_base * profile.bituach_leumi_rate
    return round_money(total)


def scheduled_tax_payment(*, cadence: Cadence, month_index: int, reserve_queue: list[float], profile: TaxProfile) -> float:
    if profile.reserve_mode == "none" or cadence in {"none", "manual"}:
        return 0.0
    if cadence == "monthly":
        return 0.0 if month_index == 0 else round_money(reserve_queue[month_index - 1])
    if cadence == "bimonthly":
        return round_money(sum(reserve_queue[max(0, month_index - 2):month_index])) if month_index > 0 and month_index % 2 == 0 else 0.0
    raise ForecastError("UNKNOWN_CADENCE: use none, monthly, bimonthly, or manual")


def validate_warnings(config: ForecastConfig) -> list[str]:
    warnings: list[str] = []
    if config.tax_profile.vat_cadence != "none" and not config.tax_profile.reviewed_on:
        warnings.append("UNVERIFIED_TAX_RATE: add reviewed_on after checking current official values")
    if config.buffer <= 0:
        warnings.append("NO_BUFFER: set a minimum cash buffer for production use")
    if not config.cash_in and not config.cash_out:
        warnings.append("EMPTY_FORECAST: add at least one expected cash movement")
    if config.environment == "production" and "verify" not in config.tax_profile.source_note.lower():
        warnings.append("PRODUCTION_REVIEW: document official verification before relying on production output")
    return warnings


def load_json(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        raise ForecastError(f"MISSING_FILE: {file_path}")
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ForecastError(f"JSON_PARSE_ERROR: {exc}") from exc


def load_csv_as_config(
    path: str | Path,
    *,
    opening_balance: float,
    start_month: str,
    months: int,
    tax_profile: Optional[dict[str, Any]] = None,
    buffer: float = 0.0,
    environment: Environment = "sandbox",
) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        raise ForecastError(f"MISSING_FILE: {file_path}")
    cash_in: list[dict[str, Any]] = []
    cash_out: list[dict[str, Any]] = []
    with file_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"date", "amount", "direction", "description"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ForecastError("CSV_SCHEMA_ERROR: include date, amount, direction, description")
        for row in reader:
            transaction = {
                "date": row["date"],
                "amount": float(row["amount"]),
                "description": row.get("description", ""),
                "category": row.get("category") or "general",
                "taxable": parse_bool(row.get("taxable", True)),
                "gross": parse_bool(row.get("gross", True)),
                "notes": row.get("notes", ""),
            }
            direction = row["direction"].strip().lower()
            if direction in {"in", "income", "cash_in", "receipt"}:
                cash_in.append(transaction)
            elif direction in {"out", "expense", "cash_out", "payment"}:
                cash_out.append(transaction)
            else:
                raise ForecastError("CSV_SCHEMA_ERROR: direction must be in or out")
    return {
        "opening_balance": opening_balance,
        "start_month": start_month,
        "months": months,
        "cash_in": cash_in,
        "cash_out": cash_out,
        "tax_profile": tax_profile or {},
        "buffer": buffer,
        "environment": environment,
    }


def write_csv(result: ForecastResult, path: str | Path) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["month", "opening_balance", "cash_in", "cash_out", "tax_reserved", "tax_paid", "closing_balance", "protected_reserve", "free_cash", "status"]
    with file_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([row.as_dict() for row in result.rows])


def round_money(value: float) -> float:
    return round(float(value) + 0.0000001, 2)


def format_ils(value: float) -> str:
    return f"₪{round_money(value):,.2f}"


def format_he_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def compare_results(results: dict[str, ForecastResult]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for name, result in results.items():
        summary = result.summary
        output.append({
            "scenario": name,
            "minimum_closing_balance": summary["minimum_closing_balance"],
            "minimum_free_cash": summary["minimum_free_cash"],
            "first_negative_month": summary["first_negative_month"],
        })
    return output
