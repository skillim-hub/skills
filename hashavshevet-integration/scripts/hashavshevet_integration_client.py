"""Typed utilities and HTTP clients for Hashavshevet data integration.

The module is intentionally conservative: validate accounting-sensitive values
locally, keep official reporting as an export concern, and keep endpoint paths
configurable because vendor and Tax Authority deployments change over time.
"""

from __future__ import annotations

import asyncio
import csv
import json
import re
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import httpx

VAT_RATE_2026 = Decimal("0.18")
EXEMPT_DEALER_CEILING_2026 = Decimal("122833")
DEFAULT_CURRENCY = "ILS"

ALLOCATION_THRESHOLDS: tuple[tuple[date, Decimal], ...] = (
    (date(2026, 6, 1), Decimal("5000")),
    (date(2026, 1, 1), Decimal("10000")),
    (date(2025, 1, 1), Decimal("20000")),
    (date(2024, 5, 5), Decimal("25000")),
)


class HashavshevetIntegrationError(Exception):
    """Base error for integration validation and transport failures."""


class ValidationError(HashavshevetIntegrationError):
    """Raised when input data cannot be safely transformed."""


@dataclass(frozen=True)
class CompanyContext:
    """Business/company context for multi-company integration."""

    company_id: str
    company_name: str
    tax_year: int = 2026
    vat_rate: Decimal = VAT_RATE_2026
    currency: str = DEFAULT_CURRENCY

    @property
    def normalized_company_id(self) -> str:
        return normalize_vat_number(self.company_id)


@dataclass(frozen=True)
class CustomerSupplier:
    """Customer or supplier master-data row."""

    account_id: str
    name: str
    vat_number: str | None = None
    email: str | None = None
    phone: str | None = None
    account_type: str = "customer"
    payment_terms_days: int = 0

    def normalized(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.vat_number:
            payload["vat_number"] = normalize_vat_number(self.vat_number)
        return payload


@dataclass(frozen=True)
class JournalEntryLine:
    """Single debit or credit line."""

    account_id: str
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    description: str = ""
    reference: str = ""

    def __post_init__(self) -> None:
        if self.debit < 0 or self.credit < 0:
            raise ValidationError("Debit and credit amounts must be non-negative.")
        if self.debit and self.credit:
            raise ValidationError("A single line cannot contain both debit and credit amounts.")


@dataclass(frozen=True)
class JournalEntry:
    """Balanced journal entry with one or more debit/credit lines."""

    entry_id: str
    entry_date: date
    lines: tuple[JournalEntryLine, ...]
    company_id: str
    memo: str = ""
    allocation_number: str | None = None

    @property
    def total_debit(self) -> Decimal:
        return sum((line.debit for line in self.lines), Decimal("0"))

    @property
    def total_credit(self) -> Decimal:
        return sum((line.credit for line in self.lines), Decimal("0"))

    def is_balanced(self) -> bool:
        return quantize_money(self.total_debit) == quantize_money(self.total_credit)

    def validate(self) -> None:
        if not self.lines:
            raise ValidationError("Journal entry must contain at least one line.")
        if not self.is_balanced():
            raise ValidationError("Journal entry is not balanced.")


@dataclass(frozen=True)
class BTKNEntry:
    """Portable transfer row used by the CLI for deterministic BTKN text bundles.

    Treat this as an integration bundle format, not as an official Tax Authority
    structure. Use OPENFORMAT/BKMV exports for official audit handoff.
    """

    company_id: str
    entry_id: str
    entry_date: date
    debit_account: str
    credit_account: str
    net_amount: Decimal
    vat_amount: Decimal = Decimal("0")
    description: str = ""
    reference: str = ""
    allocation_number: str = ""


def normalize_vat_number(value: str | int) -> str:
    digits = re.sub(r"\D+", "", str(value))
    if len(digits) != 9:
        raise ValidationError("Israeli VAT/company number must contain exactly 9 digits.")
    return digits


def is_plausible_israeli_vat_number(value: str | int) -> bool:
    try:
        digits = normalize_vat_number(value)
    except ValidationError:
        return False
    return len(set(digits)) > 1


def coerce_date(value: str | date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValidationError("Date must use YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY.")


def quantize_money(value: Decimal | str | int | float) -> Decimal:
    amount = parse_amount(value)
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def parse_amount(value: Decimal | str | int | float) -> Decimal:
    try:
        amount = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError) as exc:
        raise ValidationError(f"Invalid amount: {value!r}") from exc
    return amount


def format_money(value: Decimal | str | int | float) -> str:
    return f"{quantize_money(value):.2f}"


def calculate_vat(net_amount: Decimal | str | int | float, vat_rate: Decimal = VAT_RATE_2026) -> Decimal:
    return quantize_money(parse_amount(net_amount) * vat_rate)


def gross_from_net(net_amount: Decimal | str | int | float, vat_rate: Decimal = VAT_RATE_2026) -> Decimal:
    return quantize_money(parse_amount(net_amount) + calculate_vat(net_amount, vat_rate))


def invoice_allocation_threshold(invoice_date: str | date | datetime) -> Decimal:
    checked_date = coerce_date(invoice_date)
    for effective_date, threshold in ALLOCATION_THRESHOLDS:
        if checked_date >= effective_date:
            return threshold
    return Decimal("999999999999")


def requires_allocation_number(
    net_amount: Decimal | str | int | float,
    invoice_date: str | date | datetime,
    *,
    document_type: str = "tax_invoice",
    customer_vat_number: str | int | None = None,
    has_vat: bool = True,
) -> bool:
    if document_type not in {"tax_invoice", "tax_invoice_receipt"}:
        return False
    if not has_vat or not customer_vat_number:
        return False
    if not is_plausible_israeli_vat_number(customer_vat_number):
        return False
    return parse_amount(net_amount) > invoice_allocation_threshold(invoice_date)


def detect_hebrew_encoding(raw: bytes) -> str:
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "windows-1255"


def read_text_auto(path: str | Path) -> str:
    data = Path(path).read_bytes()
    return data.decode(detect_hebrew_encoding(data), errors="replace")


def parse_fixed_width_lines(lines: Iterable[str], schema: Mapping[str, tuple[int, int]]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for line in lines:
        if not line.strip():
            continue
        records.append({
            field: line[start:end].strip() if len(line) > start else ""
            for field, (start, end) in schema.items()
        })
    return records


def read_csv_auto(path: str | Path) -> list[dict[str, str]]:
    text = read_text_auto(path)
    rows = list(csv.DictReader(text.splitlines()))
    return [dict(row) for row in rows]


def write_csv_utf8_bom(records: Sequence[Mapping[str, Any]], path: str | Path) -> None:
    if not records:
        Path(path).write_text("", encoding="utf-8-sig")
        return
    fieldnames = list(records[0].keys())
    with Path(path).open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            writer.writerow({key: _simple_value(value) for key, value in row.items()})


def load_json_records(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return list(payload["records"])
    if isinstance(payload, list):
        return list(payload)
    raise ValidationError("JSON input must be a list or an object containing a records list.")


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, Decimal):
        return format_money(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    return value


def _simple_value(value: Any) -> str:
    if isinstance(value, Decimal):
        return format_money(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return "" if value is None else str(value)


def _btkn_line(entry: BTKNEntry) -> str:
    return "|".join([
        "BTKN1",
        normalize_vat_number(entry.company_id),
        entry.entry_id,
        coerce_date(entry.entry_date).strftime("%d-%m-%Y"),
        entry.debit_account,
        entry.credit_account,
        format_money(entry.net_amount),
        format_money(entry.vat_amount),
        entry.reference,
        entry.allocation_number,
        entry.description.replace("\n", " ").replace("|", " "),
    ])


def btkn_entries_from_records(records: Sequence[Mapping[str, Any]]) -> list[BTKNEntry]:
    entries: list[BTKNEntry] = []
    for row in records:
        entries.append(BTKNEntry(
            company_id=str(row["company_id"]),
            entry_id=str(row["entry_id"]),
            entry_date=coerce_date(row["entry_date"]),
            debit_account=str(row["debit_account"]),
            credit_account=str(row["credit_account"]),
            net_amount=parse_amount(row["net_amount"]),
            vat_amount=parse_amount(row.get("vat_amount", "0")),
            description=str(row.get("description", "")),
            reference=str(row.get("reference", "")),
            allocation_number=str(row.get("allocation_number", "")),
        ))
    return entries


def generate_btkn_file(entries: Sequence[BTKNEntry], output_path: str | Path, *, encoding: str = "windows-1255") -> Path:
    output = Path(output_path)
    lines = [
        "BTKN1|COUNT|GENERATED_AT",
        f"BTKN1|{len(entries)}|{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
    ]
    lines.extend(_btkn_line(entry) for entry in entries)
    output.write_text("\n".join(lines) + "\n", encoding=encoding)
    return output


def build_openformat_skeleton(company: CompanyContext, entries: Sequence[JournalEntry]) -> dict[str, str]:
    """Create a validation-friendly OPENFORMAT/BKMV skeleton for dry runs.

    The official generator inside the accounting system remains the source of
    truth for audit files. This skeleton supports record counting and handoff
    rehearsal in tests and staging environments.
    """

    for entry in entries:
        entry.validate()
    generated = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    ini = "\n".join([
        "[OPENFORMAT]",
        f"CompanyId={company.normalized_company_id}",
        f"CompanyName={company.company_name}",
        f"TaxYear={company.tax_year}",
        f"GeneratedAt={generated}",
        f"B100Count={len(entries)}",
    ]) + "\n"

    data_lines = [
        f"A100|{company.normalized_company_id}|{company.company_name}|{company.tax_year}",
    ]
    for entry in entries:
        data_lines.append(
            f"B100|{entry.entry_id}|{entry.entry_date.strftime('%Y-%m-%d')}|"
            f"{format_money(entry.total_debit)}|{format_money(entry.total_credit)}|{entry.memo}"
        )
    data_lines.append(f"Z900|{len(data_lines) + 1}")
    return {"INI.TXT": ini, "BKMVDATA.TXT": "\n".join(data_lines) + "\n"}


def validate_invoice_payload(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("company_id", "invoice_number", "invoice_date", "customer_vat_number", "net_amount")
    for key in required:
        if not payload.get(key):
            errors.append(f"Missing required field: {key}")
    for key in ("company_id", "customer_vat_number"):
        if payload.get(key) and not is_plausible_israeli_vat_number(payload[key]):
            errors.append(f"Invalid Israeli VAT/company number: {key}")
    try:
        if payload.get("invoice_date"):
            coerce_date(payload["invoice_date"])
    except ValidationError as exc:
        errors.append(str(exc))
    try:
        if payload.get("net_amount") is not None and parse_amount(payload["net_amount"]) < 0:
            errors.append("net_amount must be non-negative")
    except ValidationError as exc:
        errors.append(str(exc))
    return errors


class HashavshevetIntegrationClient:
    """Synchronous HTTP client for Hashavshevet/WizCloud-style APIs."""

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.transport = transport

    def _url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_json(self, path: str, *, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
            response = client.get(self._url(path), headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()

    def post_json(self, path: str, payload: Mapping[str, Any] | Any) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
            response = client.post(self._url(path), headers=self._headers(), json=to_jsonable(payload))
            response.raise_for_status()
            return response.json()

    def sync_customer_supplier(self, record: CustomerSupplier | Mapping[str, Any], *, path: str = "/accounts") -> dict[str, Any]:
        payload = record.normalized() if isinstance(record, CustomerSupplier) else dict(record)
        return self.post_json(path, payload)

    def push_journal_entry(self, entry: JournalEntry, *, path: str = "/journal-transactions") -> dict[str, Any]:
        entry.validate()
        return self.post_json(path, entry)

    def pull_journal_entries(
        self,
        *,
        company_id: str,
        from_date: str | date,
        to_date: str | date,
        path: str = "/journal-transactions",
    ) -> dict[str, Any]:
        return self.get_json(path, params={
            "company_id": normalize_vat_number(company_id),
            "from_date": coerce_date(from_date).isoformat(),
            "to_date": coerce_date(to_date).isoformat(),
        })

    def request_invoice_allocation(self, payload: Mapping[str, Any], *, path: str = "/Invoices/v1/Approval") -> dict[str, Any]:
        errors = validate_invoice_payload(payload)
        if errors:
            raise ValidationError("; ".join(errors))
        return self.post_json(path, payload)


class AsyncHashavshevetIntegrationClient(HashavshevetIntegrationClient):
    """Async HTTP client with the same payload helpers as the sync client."""

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | httpx.BaseTransport | None = None,
    ) -> None:
        super().__init__(base_url, token=token, timeout=timeout, transport=None)
        self.async_transport = transport

    async def aget_json(self, path: str, *, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout, transport=self.async_transport) as client:
            response = await client.get(self._url(path), headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()

    async def apost_json(self, path: str, payload: Mapping[str, Any] | Any) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout, transport=self.async_transport) as client:
            response = await client.post(self._url(path), headers=self._headers(), json=to_jsonable(payload))
            response.raise_for_status()
            return response.json()

    async def async_sync_customer_supplier(self, record: CustomerSupplier | Mapping[str, Any], *, path: str = "/accounts") -> dict[str, Any]:
        payload = record.normalized() if isinstance(record, CustomerSupplier) else dict(record)
        return await self.apost_json(path, payload)


def run_async(coro: Any) -> Any:
    return asyncio.run(coro)
