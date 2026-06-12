"""Utilities for Israeli supplier withholding-tax compliance staging.

This module is deliberately conservative: it calculates supplier withholding from
explicit supplier certificate data and prepares auditable staging rows for Form
856 workflows. It does not submit to the Israel Tax Authority and does not
hard-code category-rate tables.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from pathlib import Path
import csv
import json
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

MONEY_QUANT = Decimal("0.01")
PERCENT_QUANT = Decimal("0.01")
CURRENT_STANDARD_VAT_RATE = Decimal("0.18")
CURRENT_STANDARD_VAT_RATE_EFFECTIVE_FROM = date(2025, 1, 1)

OFFICIAL_URLS = {
    "report_126_856_upload": "https://www.gov.il/he/service/report126",
    "submission_confirmation_126_856": "https://www.gov.il/he/service/serving-approval-system",
    "logical_tests_126_856": "https://www.gov.il/he/service/logical-tests-for-reports-126-856",
    "withholding_certificates_and_bookkeeping": "https://www.gov.il/he/service/itc-gmishurim",
    "form_806_annual_certificate": "https://www.gov.il/he/service/itc806",
    "deductions_payment_online": "https://www.gov.il/he/service/payment-of-taxes-deductions",
    "tax_authority_api_index": "https://govextra.gov.il/taxes/innovation/home/api/",
    "software_houses_info": "https://www.gov.il/he/departments/targetaudience/taxes-adience-software",
}


class ComplianceError(ValueError):
    """Raised when required compliance inputs are missing or inconsistent."""


@dataclass(frozen=True)
class SupplierCertificate:
    """Supplier withholding certificate snapshot captured before payment."""

    supplier_tax_id: str
    rate_percent: Decimal
    valid_from: date
    valid_to: date
    source: str = "Israel Tax Authority certificate/service"
    certificate_reference: str = ""


@dataclass(frozen=True)
class SupplierPayment:
    """Supplier payment input used for withholding calculation."""

    payment_id: str
    supplier_tax_id: str
    payment_date: date
    amount_before_vat_ils: Decimal
    vat_ils: Decimal = Decimal("0.00")
    description: str = ""


@dataclass(frozen=True)
class WithholdingResult:
    """Calculated withholding result for audit trail and staging output."""

    payment_id: str
    supplier_tax_id: str
    payment_date: date
    amount_before_vat_ils: Decimal
    vat_ils: Decimal
    withholding_base_ils: Decimal
    rate_percent: Decimal
    withheld_ils: Decimal
    certificate_valid_to: date
    certificate_reference: str
    include_vat_in_base: bool


def parse_date(value: str | date | datetime) -> date:
    """Parse ISO date strings or return date values unchanged."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ComplianceError(f"Invalid date: {value!r}; expected YYYY-MM-DD") from exc


def to_decimal(value: Decimal | int | float | str, *, field: str = "amount") -> Decimal:
    """Convert values to Decimal using string conversion for floats."""
    try:
        return Decimal(str(value)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ComplianceError(f"Invalid {field}: {value!r}") from exc


def normalize_israeli_tax_id(value: str | int) -> str:
    """Return a zero-padded 9-digit Israeli tax identifier string."""
    text = "".join(ch for ch in str(value).strip() if ch.isdigit())
    if len(text) > 9 or not text:
        raise ComplianceError("Israeli tax identifiers must contain 1-9 digits before zero padding")
    return text.zfill(9)


def current_vat_rate(as_of: str | date | datetime | None = None) -> Decimal:
    """Return the standard Israeli VAT rate confirmed for dates from 2025-01-01 onward."""
    effective_date = parse_date(as_of) if as_of is not None else date.today()
    if effective_date < CURRENT_STANDARD_VAT_RATE_EFFECTIVE_FROM:
        raise ComplianceError(
            "This package only web-validated the current 18% VAT rate effective from 2025-01-01 onward"
        )
    return CURRENT_STANDARD_VAT_RATE


def validate_rate_percent(rate_percent: Decimal | int | float | str) -> Decimal:
    """Validate an explicit supplier certificate rate percentage."""
    try:
        rate = Decimal(str(rate_percent)).quantize(PERCENT_QUANT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ComplianceError(f"Invalid withholding rate: {rate_percent!r}") from exc
    if rate < Decimal("0") or rate > Decimal("100"):
        raise ComplianceError("Withholding rate must be between 0 and 100 percent")
    return rate


def supplier_certificate_from_mapping(data: Mapping[str, object]) -> SupplierCertificate:
    """Build a SupplierCertificate from JSON/CSV-like data."""
    return SupplierCertificate(
        supplier_tax_id=normalize_israeli_tax_id(data["supplier_tax_id"]),
        rate_percent=validate_rate_percent(data["rate_percent"]),
        valid_from=parse_date(data["valid_from"]),
        valid_to=parse_date(data["valid_to"]),
        source=str(data.get("source", "Israel Tax Authority certificate/service")),
        certificate_reference=str(data.get("certificate_reference", "")),
    )


def supplier_payment_from_mapping(data: Mapping[str, object]) -> SupplierPayment:
    """Build a SupplierPayment from JSON/CSV-like data."""
    return SupplierPayment(
        payment_id=str(data["payment_id"]),
        supplier_tax_id=normalize_israeli_tax_id(data["supplier_tax_id"]),
        payment_date=parse_date(data["payment_date"]),
        amount_before_vat_ils=to_decimal(data["amount_before_vat_ils"], field="amount_before_vat_ils"),
        vat_ils=to_decimal(data.get("vat_ils", "0"), field="vat_ils"),
        description=str(data.get("description", "")),
    )


def validate_certificate_for_payment(certificate: SupplierCertificate, payment_date: str | date | datetime) -> None:
    """Raise if the supplier certificate is not valid on the payment date."""
    paid_on = parse_date(payment_date)
    if not (certificate.valid_from <= paid_on <= certificate.valid_to):
        raise ComplianceError(
            f"Certificate for {certificate.supplier_tax_id} is not valid on {paid_on.isoformat()}"
        )


def calculate_withholding_base(
    amount_before_vat_ils: Decimal | int | float | str,
    vat_ils: Decimal | int | float | str = Decimal("0.00"),
    *,
    include_vat_in_base: bool = False,
) -> Decimal:
    """Calculate the base used for withholding.

    Default behaviour excludes VAT from the withholding base. Set
    include_vat_in_base=True only when the payer's accountant/legal workflow has
    determined that VAT belongs in the relevant base for that specific case.
    """
    net = to_decimal(amount_before_vat_ils, field="amount_before_vat_ils")
    vat = to_decimal(vat_ils, field="vat_ils")
    if net < 0 or vat < 0:
        raise ComplianceError("Payment and VAT amounts must be non-negative")
    base = net + vat if include_vat_in_base else net
    return base.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def calculate_withholding(
    payment: SupplierPayment,
    certificate: SupplierCertificate,
    *,
    include_vat_in_base: bool = False,
) -> WithholdingResult:
    """Calculate withholding from an explicit payment and supplier certificate."""
    if payment.supplier_tax_id != certificate.supplier_tax_id:
        raise ComplianceError("Payment supplier tax ID and certificate supplier tax ID do not match")
    validate_certificate_for_payment(certificate, payment.payment_date)
    rate = validate_rate_percent(certificate.rate_percent)
    base = calculate_withholding_base(
        payment.amount_before_vat_ils,
        payment.vat_ils,
        include_vat_in_base=include_vat_in_base,
    )
    withheld = (base * rate / Decimal("100")).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    return WithholdingResult(
        payment_id=payment.payment_id,
        supplier_tax_id=payment.supplier_tax_id,
        payment_date=payment.payment_date,
        amount_before_vat_ils=payment.amount_before_vat_ils,
        vat_ils=payment.vat_ils,
        withholding_base_ils=base,
        rate_percent=rate,
        withheld_ils=withheld,
        certificate_valid_to=certificate.valid_to,
        certificate_reference=certificate.certificate_reference,
        include_vat_in_base=include_vat_in_base,
    )


def summarize_by_supplier(results: Iterable[WithholdingResult]) -> Dict[str, Dict[str, Decimal | int]]:
    """Aggregate calculated results by supplier tax ID."""
    summary: Dict[str, Dict[str, Decimal | int]] = {}
    for row in results:
        item = summary.setdefault(
            row.supplier_tax_id,
            {
                "payment_count": 0,
                "amount_before_vat_ils": Decimal("0.00"),
                "vat_ils": Decimal("0.00"),
                "withholding_base_ils": Decimal("0.00"),
                "withheld_ils": Decimal("0.00"),
            },
        )
        item["payment_count"] = int(item["payment_count"]) + 1
        item["amount_before_vat_ils"] = Decimal(item["amount_before_vat_ils"]) + row.amount_before_vat_ils
        item["vat_ils"] = Decimal(item["vat_ils"]) + row.vat_ils
        item["withholding_base_ils"] = Decimal(item["withholding_base_ils"]) + row.withholding_base_ils
        item["withheld_ils"] = Decimal(item["withheld_ils"]) + row.withheld_ils
    return summary


def build_form856_staging_rows(
    payments: Sequence[SupplierPayment],
    certificates: Mapping[str, SupplierCertificate],
    *,
    include_vat_in_base: bool = False,
) -> List[Dict[str, str]]:
    """Create auditable staging rows for a Form 856 preparation workflow.

    These rows are intentionally not a certified Tax Authority fixed-width file.
    Use the official 856 file-structure document and the Tax Authority simulator
    before transmission.
    """
    rows: List[Dict[str, str]] = []
    for payment in payments:
        cert = certificates.get(payment.supplier_tax_id)
        if cert is None:
            raise ComplianceError(f"Missing supplier certificate for {payment.supplier_tax_id}")
        result = calculate_withholding(payment, cert, include_vat_in_base=include_vat_in_base)
        rows.append(
            {
                "payment_id": result.payment_id,
                "supplier_tax_id": result.supplier_tax_id,
                "payment_date": result.payment_date.isoformat(),
                "amount_before_vat_ils": f"{result.amount_before_vat_ils:.2f}",
                "vat_ils": f"{result.vat_ils:.2f}",
                "withholding_base_ils": f"{result.withholding_base_ils:.2f}",
                "rate_percent": f"{result.rate_percent:.2f}",
                "withheld_ils": f"{result.withheld_ils:.2f}",
                "certificate_valid_to": result.certificate_valid_to.isoformat(),
                "certificate_reference": result.certificate_reference,
                "include_vat_in_base": str(result.include_vat_in_base).lower(),
            }
        )
    return rows


def validate_form856_submission_inputs(rows: Sequence[Mapping[str, str]]) -> List[str]:
    """Return validation warnings/errors for staging rows before official simulation."""
    issues: List[str] = []
    seen_ids = set()
    required = {
        "payment_id",
        "supplier_tax_id",
        "payment_date",
        "amount_before_vat_ils",
        "vat_ils",
        "withholding_base_ils",
        "rate_percent",
        "withheld_ils",
        "certificate_valid_to",
    }
    for idx, row in enumerate(rows, start=1):
        missing = required - set(row)
        if missing:
            issues.append(f"row {idx}: missing fields {sorted(missing)}")
            continue
        if row["payment_id"] in seen_ids:
            issues.append(f"row {idx}: duplicate payment_id {row['payment_id']}")
        seen_ids.add(row["payment_id"])
        try:
            normalize_israeli_tax_id(row["supplier_tax_id"])
            parse_date(row["payment_date"])
            parse_date(row["certificate_valid_to"])
            validate_rate_percent(row["rate_percent"])
            for money_field in ("amount_before_vat_ils", "vat_ils", "withholding_base_ils", "withheld_ils"):
                if to_decimal(row[money_field], field=money_field) < 0:
                    issues.append(f"row {idx}: {money_field} is negative")
        except ComplianceError as exc:
            issues.append(f"row {idx}: {exc}")
    return issues


def write_staging_csv(rows: Sequence[Mapping[str, str]], output_path: str | Path) -> Path:
    """Write Form 856 staging rows to CSV."""
    if not rows:
        raise ComplianceError("No rows to write")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def load_certificates_json(path: str | Path) -> Dict[str, SupplierCertificate]:
    """Load supplier certificates from JSON array keyed by normalized tax ID."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    certs = [supplier_certificate_from_mapping(item) for item in data]
    return {cert.supplier_tax_id: cert for cert in certs}


def load_payments_csv(path: str | Path) -> List[SupplierPayment]:
    """Load supplier payments from CSV."""
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return [supplier_payment_from_mapping(row) for row in csv.DictReader(handle)]


def official_service_urls() -> Dict[str, str]:
    """Return official/public URLs referenced by this package."""
    return dict(OFFICIAL_URLS)


def validation_checklist(tax_year: int) -> List[str]:
    """Return a concise operational checklist for annual Form 856 preparation."""
    return [
        f"Collect supplier certificate snapshots valid during tax year {tax_year} payments.",
        "Calculate withholding from explicit certificate rates; do not infer rates from supplier category alone.",
        "Reconcile staging totals to bookkeeping records and periodic deductions reports before annual submission.",
        "Generate the official Form 856 file using the current Tax Authority file-structure specification.",
        "Run the official 126/856 logical-tests simulator before transmission.",
        "Transmit through the official 126/856 service or approved SHAAM/representative channel.",
        "Complete the separate 126/856 submission-confirmation step and retain the online confirmation.",
    ]


def to_jsonable(result: WithholdingResult) -> Dict[str, str | bool]:
    """Return a JSON-serializable representation of a calculation result."""
    data = asdict(result)
    for key, value in list(data.items()):
        if isinstance(value, Decimal):
            data[key] = f"{value:.2f}"
        elif isinstance(value, date):
            data[key] = value.isoformat()
    return data
