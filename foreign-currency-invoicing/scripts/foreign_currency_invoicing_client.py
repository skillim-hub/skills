from __future__ import annotations

import asyncio
import csv
import datetime as dt
import hashlib
import io
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable, Mapping, Sequence

BOI_CURRENT_SINGLE_RATE_URL = "https://boi.org.il/PublicApi/GetExchangeRate"
BOI_CURRENT_RATE_LIST_URL = "https://boi.org.il/PublicApi/GetExchangeRates"
BOI_SDMX_EXR_BASE_URL = "https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0"
BOI_SINGLE_RATE_URL = BOI_SDMX_EXR_BASE_URL
BOI_RATE_LIST_URL = BOI_CURRENT_RATE_LIST_URL
MONEY_QUANT = Decimal("0.01")
RATE_QUANT = Decimal("0.000001")
DEFAULT_STORE_DIR = Path(".foreign-currency-invoicing/invoices")


class RateLookupError(RuntimeError):
    """Raised when a representative exchange rate cannot be fetched or parsed."""


class InvoiceValidationError(ValueError):
    """Raised when invoice input is invalid for calculation."""


class VatCategory(str, Enum):
    STANDARD = "standard"
    ZERO = "zero"
    EXEMPT = "exempt"
    REVERSE_CHARGE = "reverse_charge"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass(frozen=True)
class ExchangeRate:
    currency: str
    rate: Decimal
    unit: Decimal = Decimal("1")
    date: dt.date = field(default_factory=dt.date.today)
    source: str = "Bank of Israel"
    raw: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "currency", normalize_currency(self.currency))
        object.__setattr__(self, "rate", to_decimal(self.rate, "rate"))
        object.__setattr__(self, "unit", to_decimal(self.unit, "unit"))
        if self.unit <= 0:
            raise InvoiceValidationError("exchange rate unit must be positive")
        if self.rate <= 0:
            raise InvoiceValidationError("exchange rate must be positive")

    @property
    def ils_per_unit(self) -> Decimal:
        return (self.rate / self.unit).quantize(RATE_QUANT, rounding=ROUND_HALF_UP)

    def to_dict(self) -> dict[str, Any]:
        return {
            "currency": self.currency,
            "rate": decimal_to_str(self.rate, places="0.000000"),
            "unit": decimal_to_str(self.unit, places="0.######"),
            "date": format_il_date(self.date),
            "source": self.source,
            "ils_per_unit": decimal_to_str(self.ils_per_unit, places="0.000000"),
        }


@dataclass(frozen=True)
class InvoiceLine:
    description: str
    quantity: Decimal
    unit_price: Decimal
    vat_category: VatCategory | str = VatCategory.STANDARD
    discount: Decimal = Decimal("0")
    note: str = ""

    def __post_init__(self) -> None:
        if not str(self.description).strip():
            raise InvoiceValidationError("description is required")
        quantity = to_decimal(self.quantity, "quantity")
        unit_price = to_decimal(self.unit_price, "unit_price")
        discount = to_decimal(self.discount, "discount")
        if quantity < 0:
            raise InvoiceValidationError("quantity must not be negative")
        if unit_price < 0:
            raise InvoiceValidationError("unit_price must not be negative")
        if discount < 0:
            raise InvoiceValidationError("discount must not be negative")
        if discount > quantity * unit_price:
            raise InvoiceValidationError("discount cannot exceed line amount")
        object.__setattr__(self, "description", str(self.description).strip())
        object.__setattr__(self, "quantity", quantity)
        object.__setattr__(self, "unit_price", unit_price)
        object.__setattr__(self, "discount", discount)
        object.__setattr__(self, "vat_category", normalize_vat_category(self.vat_category))
        object.__setattr__(self, "note", str(self.note).strip())

    @property
    def net(self) -> Decimal:
        return self.quantity * self.unit_price - self.discount

    def to_dict(self) -> dict[str, str]:
        return {
            "description": self.description,
            "quantity": decimal_to_str(self.quantity),
            "unit_price": decimal_to_str(self.unit_price),
            "discount": decimal_to_str(self.discount),
            "vat_category": self.vat_category.value,
            "note": self.note,
        }


@dataclass(frozen=True)
class InvoiceResult:
    invoice_id: str
    currency: str
    issue_date: dt.date
    exchange_rate: ExchangeRate
    vat_rate: Decimal
    totals: Mapping[str, Decimal]
    vat_breakdown: Mapping[str, Decimal]
    lines: Sequence[Mapping[str, Any]]
    warnings: Sequence[str] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.invoice_id,
            "currency": self.currency,
            "issue_date": format_il_date(self.issue_date),
            "exchange_rate": self.exchange_rate.to_dict(),
            "vat_rate": decimal_to_str(self.vat_rate, places="0.####"),
            "totals": {key: decimal_to_str(value) for key, value in self.totals.items()},
            "vat_breakdown": {key: decimal_to_str(value) for key, value in self.vat_breakdown.items()},
            "lines": list(self.lines),
            "warnings": list(self.warnings),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass(frozen=True)
class ForeignCurrencyInvoiceClient:
    base_url: str = BOI_SINGLE_RATE_URL
    timeout: float = 20.0
    store_dir: Path = DEFAULT_STORE_DIR

    def build_rate_url(self, currency: str, as_of_date: str | dt.date) -> str:
        return build_boi_rate_url(currency, as_of_date, base_url=self.base_url)

    def fetch_rate(self, currency: str, as_of_date: str | dt.date) -> ExchangeRate:
        return fetch_rate(currency, as_of_date, base_url=self.base_url, timeout=self.timeout)

    async def async_fetch_rate(self, currency: str, as_of_date: str | dt.date) -> ExchangeRate:
        return await async_fetch_rate(currency, as_of_date, base_url=self.base_url, timeout=self.timeout)

    def calculate(
        self,
        lines: Sequence[InvoiceLine | Mapping[str, Any]],
        currency: str,
        issue_date: str | dt.date,
        exchange_rate: ExchangeRate | Decimal | str | int | float | None = None,
        vat_rate: Decimal | str | None = None,
        round_per_line: bool = False,
    ) -> InvoiceResult:
        return calculate_invoice(
            lines,
            currency,
            issue_date,
            exchange_rate,
            vat_rate=vat_rate,
            round_per_line=round_per_line,
        )

    def calculate_from_json(
        self,
        line_payload: str | bytes | Sequence[Mapping[str, Any]],
        currency: str,
        issue_date: str | dt.date,
        exchange_rate: ExchangeRate | Decimal | str | int | float | None = None,
        vat_rate: Decimal | str | None = None,
    ) -> InvoiceResult:
        return invoice_from_json_lines(line_payload, currency, issue_date, exchange_rate, vat_rate=vat_rate)

    def save(self, result: InvoiceResult) -> Path:
        return save_invoice_result(result, self.store_dir)

    def load(self, invoice_id: str) -> dict[str, Any]:
        return load_invoice_result(invoice_id, self.store_dir)


def to_decimal(value: Any, field_name: str = "value") -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise InvoiceValidationError(f"{field_name} must be numeric") from exc


def quantize_money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def decimal_to_str(value: Decimal, places: str = "0.01") -> str:
    quant = Decimal(places.replace("#", "0")) if "#" in places else Decimal(places)
    rounded = Decimal(value).quantize(quant, rounding=ROUND_HALF_UP)
    text = format(rounded, "f")
    if "#" in places:
        text = text.rstrip("0").rstrip(".")
    return text


def normalize_currency(currency: str) -> str:
    code = str(currency).strip().upper()
    if len(code) != 3 or not code.isalpha():
        raise InvoiceValidationError("currency must be an ISO 4217-style 3-letter code")
    return code


def normalize_vat_category(value: VatCategory | str) -> VatCategory:
    if isinstance(value, VatCategory):
        return value
    normalized = str(value).strip().lower().replace("-", "_")
    aliases = {
        "regular": "standard",
        "standard_vat": "standard",
        "zero_rate": "zero",
        "reverse": "reverse_charge",
        "outside_scope": "out_of_scope",
    }
    normalized = aliases.get(normalized, normalized)
    try:
        return VatCategory(normalized)
    except ValueError as exc:
        allowed = ", ".join(category.value for category in VatCategory)
        raise InvoiceValidationError(f"unsupported VAT category; use one of: {allowed}") from exc


def parse_date(value: str | dt.date | dt.datetime) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    text = str(value).strip()
    if not text:
        raise InvoiceValidationError("date is required")
    if "T" in text:
        text = text.split("T", 1)[0]
    if " " in text and text[:10].count("-") == 2:
        text = text.split(" ", 1)[0]
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d.%m.%Y"):
        try:
            return dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise InvoiceValidationError("date must be YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY")


def format_il_date(value: dt.date | str) -> str:
    return parse_date(value).strftime("%d/%m/%Y")


def default_vat_rate(on_date: str | dt.date | dt.datetime) -> Decimal:
    date_value = parse_date(on_date)
    return Decimal("0.18") if date_value >= dt.date(2025, 1, 1) else Decimal("0.17")


def build_boi_rate_url(
    currency: str,
    as_of_date: str | dt.date,
    base_url: str = BOI_SDMX_EXR_BASE_URL,
) -> str:
    """Build the official Bank of Israel SDMX URL for a date-specific representative rate."""
    code = normalize_currency(currency)
    date_value = parse_date(as_of_date).isoformat()
    series_code = f"RER_{code}_ILS"
    clean_base = base_url.rstrip("/")
    if "FusionEdgeServer" not in clean_base:
        query = urllib.parse.urlencode({"key": code})
        separator = "&" if "?" in clean_base else "?"
        return f"{clean_base}{separator}{query}"
    query = urllib.parse.urlencode(
        {
            "startPeriod": date_value,
            "endPeriod": date_value,
            "format": "csv",
        }
    )
    return f"{clean_base}/{series_code}?{query}"


def build_boi_current_rate_url(
    currency: str,
    base_url: str = BOI_CURRENT_SINGLE_RATE_URL,
    *,
    as_xml: bool = False,
) -> str:
    """Build the official Bank of Israel current-rate API URL for a single currency."""
    code = normalize_currency(currency)
    params: dict[str, str] = {"key": code}
    if as_xml:
        params["asXml"] = "true"
    query = urllib.parse.urlencode(params)
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{query}"


def fetch_url_bytes(url: str, timeout: float = 20.0) -> bytes:
    request = urllib.request.Request(url, headers={"Accept": "text/csv, application/json, application/xml"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_rate(
    currency: str,
    as_of_date: str | dt.date,
    *,
    base_url: str = BOI_SINGLE_RATE_URL,
    timeout: float = 20.0,
    fetcher: Callable[[str], bytes | str] | None = None,
) -> ExchangeRate:
    url = build_boi_rate_url(currency, as_of_date, base_url=base_url)
    loader = fetcher or (lambda target: fetch_url_bytes(target, timeout=timeout))
    try:
        payload = loader(url)
    except Exception as exc:
        raise RateLookupError(f"failed to fetch Bank of Israel rate: {exc}") from exc
    parsed = parse_boi_rate_response(payload, currency)
    if parsed.date > parse_date(as_of_date):
        raise RateLookupError("Bank of Israel response date is after the requested issue date")
    return parsed


async def async_fetch_rate(
    currency: str,
    as_of_date: str | dt.date,
    *,
    base_url: str = BOI_SINGLE_RATE_URL,
    timeout: float = 20.0,
    fetcher: Callable[[str], bytes | str] | None = None,
    async_fetcher: Callable[[str], Awaitable[bytes | str]] | None = None,
) -> ExchangeRate:
    url = build_boi_rate_url(currency, as_of_date, base_url=base_url)
    if async_fetcher is not None:
        try:
            payload = await async_fetcher(url)
        except Exception as exc:
            raise RateLookupError(f"failed to fetch Bank of Israel rate: {exc}") from exc
        return parse_boi_rate_response(payload, currency)
    return await asyncio.to_thread(
        fetch_rate,
        currency,
        as_of_date,
        base_url=base_url,
        timeout=timeout,
        fetcher=fetcher,
    )


def resolve_rate_with_fallback(
    currency: str,
    as_of_date: str | dt.date,
    *,
    max_lookback_days: int = 7,
    base_url: str = BOI_SINGLE_RATE_URL,
    timeout: float = 20.0,
    fetcher: Callable[[str], bytes | str] | None = None,
) -> ExchangeRate:
    date_value = parse_date(as_of_date)
    last_error: Exception | None = None
    for offset in range(max_lookback_days + 1):
        candidate = date_value - dt.timedelta(days=offset)
        try:
            return fetch_rate(
                currency,
                candidate,
                base_url=base_url,
                timeout=timeout,
                fetcher=fetcher,
            )
        except Exception as exc:
            last_error = exc
    raise RateLookupError(f"no representative rate found within {max_lookback_days} days") from last_error


def parse_boi_rate_response(payload: bytes | str | Mapping[str, Any], currency: str) -> ExchangeRate:
    code = normalize_currency(currency)
    if isinstance(payload, Mapping):
        return _parse_boi_json(payload, code)
    text = payload.decode("utf-8-sig") if isinstance(payload, bytes) else str(payload)
    stripped = text.strip()
    if not stripped:
        raise RateLookupError("empty Bank of Israel response")
    if stripped.startswith("<"):
        return _parse_boi_xml(stripped, code)
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        return _parse_boi_csv(stripped, code)
    return _parse_boi_json(data, code)


def calculate_invoice(
    lines: Sequence[InvoiceLine | Mapping[str, Any]],
    currency: str,
    issue_date: str | dt.date,
    exchange_rate: ExchangeRate | Decimal | str | int | float | None = None,
    *,
    vat_rate: Decimal | str | None = None,
    round_per_line: bool = False,
    source: str = "manual",
) -> InvoiceResult:
    code = normalize_currency(currency)
    date_value = parse_date(issue_date)
    normalized_lines = [line if isinstance(line, InvoiceLine) else InvoiceLine(**line) for line in lines]
    if not normalized_lines:
        raise InvoiceValidationError("at least one invoice line is required")

    rate_obj = normalize_exchange_rate(code, date_value, exchange_rate, source)
    vat = to_decimal(vat_rate, "vat_rate") if vat_rate is not None else default_vat_rate(date_value)
    if vat < 0:
        raise InvoiceValidationError("vat_rate must not be negative")

    net_foreign = Decimal("0")
    vat_foreign = Decimal("0")
    net_ils = Decimal("0")
    vat_ils = Decimal("0")
    breakdown = {category.value: Decimal("0") for category in VatCategory}
    rendered_lines: list[dict[str, Any]] = []
    warnings: list[str] = []

    for line in normalized_lines:
        net_line_foreign = line.net
        net_line_ils_unrounded = net_line_foreign * rate_obj.ils_per_unit
        applies_standard_vat = line.vat_category is VatCategory.STANDARD
        vat_line_ils_unrounded = net_line_ils_unrounded * vat if applies_standard_vat else Decimal("0")
        vat_line_foreign = net_line_foreign * vat if applies_standard_vat else Decimal("0")
        if round_per_line:
            net_line_ils = quantize_money(net_line_ils_unrounded)
            vat_line_ils = quantize_money(vat_line_ils_unrounded)
        else:
            net_line_ils = net_line_ils_unrounded
            vat_line_ils = vat_line_ils_unrounded

        net_foreign += net_line_foreign
        vat_foreign += vat_line_foreign
        net_ils += net_line_ils
        vat_ils += vat_line_ils
        breakdown[line.vat_category.value] += vat_line_ils_unrounded

        if line.vat_category in {VatCategory.ZERO, VatCategory.EXEMPT, VatCategory.REVERSE_CHARGE} and not line.note:
            warnings.append(f"line '{line.description}' uses {line.vat_category.value}; retain supporting evidence")
        if line.vat_category is VatCategory.OUT_OF_SCOPE and not line.note:
            warnings.append(f"line '{line.description}' is out_of_scope; document the reason")

        rendered_lines.append(
            {
                "description": line.description,
                "quantity": decimal_to_str(line.quantity),
                "unit_price": decimal_to_str(line.unit_price),
                "discount": decimal_to_str(line.discount),
                "net_foreign": decimal_to_str(quantize_money(net_line_foreign)),
                "net_ils": decimal_to_str(quantize_money(net_line_ils_unrounded)),
                "vat_category": line.vat_category.value,
                "vat_ils": decimal_to_str(quantize_money(vat_line_ils_unrounded)),
                "note": line.note,
            }
        )

    totals = {
        "net_foreign": quantize_money(net_foreign),
        "vat_foreign": quantize_money(vat_foreign),
        "total_foreign": quantize_money(net_foreign + vat_foreign),
        "net_ils": quantize_money(net_ils),
        "vat_ils": quantize_money(vat_ils),
        "total_ils": quantize_money(net_ils + vat_ils),
    }
    temporary = {
        "currency": code,
        "issue_date": format_il_date(date_value),
        "rate": rate_obj.to_dict(),
        "vat_rate": decimal_to_str(vat, places="0.####"),
        "totals": {key: decimal_to_str(value) for key, value in totals.items()},
        "lines": rendered_lines,
    }
    invoice_id = generate_invoice_id(temporary)
    return InvoiceResult(
        invoice_id=invoice_id,
        currency=code,
        issue_date=date_value,
        exchange_rate=rate_obj,
        vat_rate=vat,
        totals=totals,
        vat_breakdown={key: quantize_money(value) for key, value in breakdown.items()},
        lines=rendered_lines,
        warnings=warnings,
    )


def normalize_exchange_rate(
    currency: str,
    date_value: dt.date,
    exchange_rate: ExchangeRate | Decimal | str | int | float | None,
    source: str,
) -> ExchangeRate:
    if isinstance(exchange_rate, ExchangeRate):
        if exchange_rate.currency != currency:
            raise InvoiceValidationError("exchange rate currency does not match invoice currency")
        return exchange_rate
    if exchange_rate is None:
        if currency == "ILS":
            return ExchangeRate(currency="ILS", rate=Decimal("1"), unit=Decimal("1"), date=date_value, source=source)
        raise InvoiceValidationError("exchange rate is required for non-ILS invoices")
    return ExchangeRate(
        currency=currency,
        rate=to_decimal(exchange_rate, "exchange_rate"),
        unit=Decimal("1"),
        date=date_value,
        source=source,
    )


def invoice_from_json_lines(
    line_payload: str | bytes | Sequence[Mapping[str, Any]],
    currency: str,
    issue_date: str | dt.date,
    exchange_rate: ExchangeRate | Decimal | str | int | float | None = None,
    *,
    vat_rate: Decimal | str | None = None,
) -> InvoiceResult:
    if isinstance(line_payload, bytes):
        data = json.loads(line_payload.decode("utf-8"))
    elif isinstance(line_payload, str):
        data = json.loads(line_payload)
    else:
        data = line_payload
    if not isinstance(data, Sequence) or isinstance(data, (str, bytes, bytearray)):
        raise InvoiceValidationError("line payload must be a JSON array")
    return calculate_invoice(data, currency, issue_date, exchange_rate, vat_rate=vat_rate)


def generate_invoice_id(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "fci_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def save_invoice_result(result: InvoiceResult, store_dir: str | Path = DEFAULT_STORE_DIR) -> Path:
    directory = Path(store_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{result.invoice_id}.json"
    target.write_text(result.to_json() + "\n", encoding="utf-8")
    return target


def load_invoice_result(invoice_id: str, store_dir: str | Path = DEFAULT_STORE_DIR) -> dict[str, Any]:
    safe_id = str(invoice_id).strip()
    if not safe_id.startswith("fci_") or "/" in safe_id or "\\" in safe_id:
        raise InvoiceValidationError("invoice_id must be a generated fci identifier")
    target = Path(store_dir) / f"{safe_id}.json"
    if not target.exists():
        raise FileNotFoundError(f"invoice not found: {safe_id}")
    return json.loads(target.read_text(encoding="utf-8"))


def load_lines_from_file(path: str | Path) -> list[Mapping[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise InvoiceValidationError("lines file must contain a JSON array")
    return data


def sample_lines() -> list[dict[str, str]]:
    return [
        {
            "description": "Consulting services",
            "quantity": "10",
            "unit_price": "200.00",
            "vat_category": "zero",
            "note": "Qualifying foreign-resident service; retain evidence.",
        }
    ]


def render_invoice_disclaimer(result: InvoiceResult) -> str:
    return (
        f"Exchange rate: {result.exchange_rate.currency} "
        f"{result.exchange_rate.ils_per_unit} ILS per unit on {format_il_date(result.exchange_rate.date)}. "
        "Retain the rate source and VAT classification evidence with the accounting records."
    )


def _parse_boi_json(data: Any, currency: str) -> ExchangeRate:
    matches: list[Mapping[str, Any]] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            found_code = _first_present(
                node,
                "key",
                "currency",
                "currencyCode",
                "CurrencyCode",
                "CURRENCYCODE",
            )
            if found_code and str(found_code).strip().upper() == currency:
                matches.append(node)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(data)
    if not matches and isinstance(data, Mapping):
        rate_hint = _first_present(data, "currentExchangeRate", "exchangeRate", "rate", "RATE")
        if rate_hint is not None:
            matches.append(data)
    if not matches:
        raise RateLookupError("currency not found in Bank of Israel response")
    return _exchange_rate_from_mapping(matches[0], currency)


def _exchange_rate_from_mapping(node: Mapping[str, Any], currency: str) -> ExchangeRate:
    rate = _first_present(node, "currentExchangeRate", "exchangeRate", "rate", "RATE")
    if rate is None:
        raise RateLookupError("rate value missing from Bank of Israel response")
    unit = _first_present(node, "unit", "unitOfCurrency", "Unit", "UNIT") or 1
    date_raw = _first_present(node, "lastUpdate", "date", "asOfDate", "rateDate", "LAST_UPDATE", "Date")
    date_value = parse_date(date_raw) if date_raw else dt.date.today()
    return ExchangeRate(
        currency=currency,
        rate=to_decimal(rate, "rate"),
        unit=to_decimal(unit, "unit"),
        date=date_value,
        source="Bank of Israel",
        raw=dict(node),
    )


def _parse_boi_csv(text: str, currency: str) -> ExchangeRate:
    """Parse Bank of Israel SDMX CSV output for one representative exchange-rate series."""
    sample = text.lstrip("\ufeff").strip()
    if not sample:
        raise RateLookupError("empty Bank of Israel CSV response")
    reader = csv.DictReader(io.StringIO(sample))
    if not reader.fieldnames:
        raise RateLookupError("Bank of Israel response is not valid JSON, XML, or CSV")
    normalized_headers = {name: name.strip().upper() for name in reader.fieldnames}
    for row in reader:
        cleaned = {normalized_headers.get(key, key.strip().upper()): (value or "").strip() for key, value in row.items()}
        code = (
            cleaned.get("BASE_CURRENCY")
            or cleaned.get("מטבע בסיס")
            or cleaned.get("CURRENCY")
            or cleaned.get("KEY")
        )
        series = cleaned.get("SERIES_CODE") or cleaned.get("קוד סדרה") or ""
        if not code and series.startswith("RER_"):
            parts = series.split("_")
            if len(parts) >= 3:
                code = parts[1]
        if code and code.upper() != currency:
            continue
        rate = (
            cleaned.get("OBS_VALUE")
            or cleaned.get("VALUE")
            or cleaned.get("RATE")
            or cleaned.get("ערך")
            or cleaned.get("שער יציג")
        )
        if not rate:
            continue
        unit = cleaned.get("UNIT_MULT") or cleaned.get("UNIT") or cleaned.get("יחידות") or "1"
        # SDMX UNIT_MULT is a power-of-ten multiplier, not a quoted currency unit. Treat 0 or blank as one unit.
        if str(unit).strip() in {"", "0"}:
            unit = "1"
        date_raw = cleaned.get("TIME_PERIOD") or cleaned.get("DATE") or cleaned.get("תאריך")
        return ExchangeRate(
            currency=currency,
            rate=to_decimal(rate, "rate"),
            unit=to_decimal(unit, "unit"),
            date=parse_date(date_raw) if date_raw else dt.date.today(),
            source="Bank of Israel SDMX",
            raw=cleaned,
        )
    raise RateLookupError("currency not found in Bank of Israel CSV response")


def _parse_boi_xml(text: str, currency: str) -> ExchangeRate:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise RateLookupError("Bank of Israel XML response is invalid") from exc

    for element in root.iter():
        fields = {child.tag.upper(): (child.text or "").strip() for child in list(element)}
        code = fields.get("CURRENCYCODE") or fields.get("KEY") or fields.get("CURRENCY")
        if code and code.upper() == currency:
            return ExchangeRate(
                currency=currency,
                rate=to_decimal(fields.get("RATE"), "rate"),
                unit=to_decimal(fields.get("UNIT") or "1", "unit"),
                date=parse_date(fields.get("LAST_UPDATE") or fields.get("DATE") or dt.date.today()),
                source="Bank of Israel",
                raw=fields,
            )

    if root.tag.upper() == "CURRENCY":
        fields = {child.tag.upper(): (child.text or "").strip() for child in list(root)}
        code = fields.get("CURRENCYCODE") or fields.get("KEY") or currency
        if code.upper() == currency and "RATE" in fields:
            return ExchangeRate(
                currency=currency,
                rate=to_decimal(fields.get("RATE"), "rate"),
                unit=to_decimal(fields.get("UNIT") or "1", "unit"),
                date=parse_date(fields.get("LAST_UPDATE") or fields.get("DATE") or dt.date.today()),
                source="Bank of Israel",
                raw=fields,
            )

    raise RateLookupError("currency not found in Bank of Israel XML response")


def _first_present(mapping: Mapping[str, Any], *keys: str) -> Any | None:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return None
