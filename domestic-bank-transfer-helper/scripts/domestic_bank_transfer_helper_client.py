from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import os
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class TransferMethod(str, Enum):
    AUTO = "auto"
    MASAV = "masav"
    ZAHAV = "zahav"


class RuntimeEnvironment(str, Enum):
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class ValidationCode(str, Enum):
    REQUIRED = "required"
    INVALID_BANK_CODE = "invalid_bank_code"
    UNKNOWN_BANK_CODE = "unknown_bank_code"
    INVALID_BRANCH_CODE = "invalid_branch_code"
    BRANCH_PADDED = "branch_padded"
    INVALID_ACCOUNT_NUMBER = "invalid_account_number"
    INVALID_AMOUNT = "invalid_amount"
    HIGH_VALUE_MASAV = "high_value_masav"
    VALUE_DATE_INVALID = "value_date_invalid"
    VALUE_DATE_PAST = "value_date_past"
    VALUE_DATE_CALENDAR_CHECK = "value_date_calendar_check"
    PURPOSE_MISSING = "purpose_missing"
    REFERENCE_TOO_LONG = "reference_too_long"
    METHOD_MISMATCH = "method_mismatch"
    CONFIRMATION_RECOMMENDED = "confirmation_recommended"
    PRODUCTION_REQUIRES_APPROVAL = "production_requires_approval"


KNOWN_BANKS: dict[str, str] = {
    "3": "Bank Esh Israel Ltd",
    "4": "Bank Yahav for State Employees Ltd",
    "9": "D.I. Postal Finance Ltd",
    "10": "Bank Leumi Le-Israel Ltd",
    "11": "Israel Discount Bank Ltd",
    "12": "Bank Hapoalim Ltd",
    "13": "Union Bank of Israel Ltd",
    "14": "Bank Otsar Hahayal Ltd",
    "15": "Ofek Credit Union Ltd",
    "17": "Mercantile Discount Bank Ltd",
    "18": "One Zero Digital Bank Ltd",
    "20": "Bank Mizrahi-Tefahot Ltd",
    "22": "Citibank N.A",
    "23": "HSBC Bank plc",
    "26": "U-Bank Ltd",
    "31": "First International Bank of Israel Ltd",
    "34": "Arab-Israeli Bank Ltd",
    "46": "Bank Massad Ltd",
    "50": "Bank Settlement Center Ltd. (MASAV)",
    "52": "Poalei Agudat Yisrael Bank Ltd",
    "54": "Bank of Jerusalem Ltd",
    "59": "Automatic Bank Services Ltd. (Shva)",
    "68": "Municipal Bank Ltd",
    "78": "Revolut Payments Israel Ltd",
}

DEFAULT_HIGH_VALUE_THRESHOLD_ILS = Decimal("1000000")
DEFAULT_REFERENCE_MAX_LENGTH = 35
DEFAULT_STATE_DIR_ENV = "DOMESTIC_TRANSFER_STATE_DIR"
DEFAULT_ENV_ENV = "DOMESTIC_TRANSFER_ENV"


class TransferValidationError(ValueError):
    def __init__(self, issues: Sequence["ValidationIssue"]) -> None:
        self.issues = list(issues)
        super().__init__("; ".join(f"{issue.code.value}: {issue.message}" for issue in self.issues))


@dataclass(frozen=True)
class ValidationIssue:
    severity: Severity
    code: ValidationCode
    field: str
    message: str
    suggestion: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity.value,
            "code": self.code.value,
            "field": self.field,
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass(frozen=True)
class TransferDecision:
    method: TransferMethod
    reasons: tuple[str, ...]
    cutoff_note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method.value,
            "reasons": list(self.reasons),
            "cutoff_note": self.cutoff_note,
        }


@dataclass
class TransferRequest:
    recipient_name: str
    bank_code: str
    branch_code: str
    account_number: str
    amount_ils: Decimal | str | int | float
    payer_name: str = ""
    method: TransferMethod | str = TransferMethod.AUTO
    value_date: date | str | None = None
    purpose: str = ""
    reference: str = ""
    urgent: bool = False
    same_day: bool = False
    recurring: bool = False
    bulk_count: int = 1
    require_confirmation: bool = True
    approved_by: str = ""
    source_document_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationReport:
    valid: bool
    normalized: dict[str, Any]
    decision: TransferDecision
    issues: tuple[ValidationIssue, ...]

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == Severity.ERROR)

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == Severity.WARNING)

    @property
    def infos(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == Severity.INFO)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "normalized": self.normalized,
            "decision": self.decision.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii, default=str)


def normalize_digits(value: Any) -> str:
    output: list[str] = []
    for char in str(value or ""):
        try:
            output.append(str(unicodedata.digit(char)))
        except (TypeError, ValueError):
            if char.isdecimal():
                output.append(char)
    return "".join(output)


def normalize_bank_code(value: Any) -> str:
    digits = normalize_digits(value)
    return digits.lstrip("0") or ("0" if digits else "")


def normalize_branch_code(value: Any) -> str:
    digits = normalize_digits(value)
    if 1 <= len(digits) <= 3:
        return digits.zfill(3)
    return digits


def normalize_account_number(value: Any) -> str:
    return normalize_digits(value)


def normalize_environment(env: RuntimeEnvironment | str | None = None) -> RuntimeEnvironment:
    if isinstance(env, RuntimeEnvironment):
        return env
    raw = str(env or os.getenv(DEFAULT_ENV_ENV, RuntimeEnvironment.SANDBOX.value)).strip().lower()
    try:
        return RuntimeEnvironment(raw)
    except ValueError as exc:
        raise ValueError("env must be sandbox or production") from exc


def normalize_transfer_method(method: TransferMethod | str | None = None) -> TransferMethod:
    if isinstance(method, TransferMethod):
        return method
    raw = str(method or TransferMethod.AUTO.value).strip().lower()
    try:
        return TransferMethod(raw)
    except ValueError as exc:
        raise ValueError("method must be auto, masav, or zahav") from exc


def parse_amount_ils(value: Decimal | str | int | float) -> Decimal | None:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    text = str(value or "").strip().replace("₪", "").replace(",", "").replace(" ", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def parse_value_date(value: date | str | None) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None


def format_ils(amount: Decimal | str | int | float | None) -> str:
    parsed = parse_amount_ils(amount if amount is not None else "")
    if parsed is None:
        return "₪"
    return f"₪{parsed:,.2f}"


def format_local_date(value: date | str | None) -> str:
    parsed = parse_value_date(value)
    return parsed.strftime("%d/%m/%Y") if parsed else ""


def recommend_transfer_method(
    request: TransferRequest,
    amount: Decimal | None = None,
    *,
    high_value_threshold_ils: Decimal = DEFAULT_HIGH_VALUE_THRESHOLD_ILS,
) -> TransferDecision:
    method = normalize_transfer_method(request.method)
    parsed_amount = amount if amount is not None else parse_amount_ils(request.amount_ils)
    if method in {TransferMethod.MASAV, TransferMethod.ZAHAV}:
        cutoff = (
            "Check the bank's Zahav same-day operating window before submission."
            if method == TransferMethod.ZAHAV
            else "Expect bank processing windows and next-business-day settlement behavior."
        )
        return TransferDecision(method, ("Explicit method selected.",), cutoff)
    if request.urgent or request.same_day:
        return TransferDecision(
            TransferMethod.ZAHAV,
            ("Same-day or urgent payment requested.",),
            "Submit during the bank's Zahav operating window and verify irrevocability.",
        )
    if parsed_amount is not None and parsed_amount >= high_value_threshold_ils:
        return TransferDecision(
            TransferMethod.ZAHAV,
            (f"Amount is at or above ₪{high_value_threshold_ils:,.0f}.",),
            "Use maker-checker approval and verify recipient details by a trusted channel.",
        )
    if request.bulk_count and request.bulk_count > 1:
        return TransferDecision(
            TransferMethod.MASAV,
            ("Multiple transfers fit a batch workflow.",),
            "Prepare a batch, validate every row, then submit before the bank's batch cutoff.",
        )
    if request.recurring:
        return TransferDecision(
            TransferMethod.MASAV,
            ("Recurring non-urgent payment requested.",),
            "Confirm standing-order or batch timing with the bank.",
        )
    return TransferDecision(
        TransferMethod.MASAV,
        ("Non-urgent single transfer.",),
        "Allow normal bank processing time and avoid last-minute payroll or supplier deadlines.",
    )


def _issue(
    issues: list[ValidationIssue],
    severity: Severity,
    code: ValidationCode,
    field: str,
    message: str,
    suggestion: str = "",
) -> None:
    issues.append(ValidationIssue(severity, code, field, message, suggestion))


def validate_transfer(
    request: TransferRequest,
    *,
    today: date | None = None,
    env: RuntimeEnvironment | str | None = None,
    high_value_threshold_ils: Decimal = DEFAULT_HIGH_VALUE_THRESHOLD_ILS,
    reference_max_length: int = DEFAULT_REFERENCE_MAX_LENGTH,
) -> ValidationReport:
    today = today or date.today()
    environment = normalize_environment(env)
    issues: list[ValidationIssue] = []
    bank_code = normalize_bank_code(request.bank_code)
    branch_code = normalize_branch_code(request.branch_code)
    raw_branch_digits = normalize_digits(request.branch_code)
    account_number = normalize_account_number(request.account_number)
    amount = parse_amount_ils(request.amount_ils)
    value_date = parse_value_date(request.value_date)
    method = normalize_transfer_method(request.method)
    decision = recommend_transfer_method(request, amount, high_value_threshold_ils=high_value_threshold_ils)

    if not str(request.recipient_name or "").strip():
        _issue(issues, Severity.ERROR, ValidationCode.REQUIRED, "recipient_name", "Recipient name is required.")
    if not bank_code:
        _issue(issues, Severity.ERROR, ValidationCode.REQUIRED, "bank_code", "Bank code is required.")
    elif not bank_code.isdigit() or not (1 <= len(bank_code) <= 3):
        _issue(
            issues,
            Severity.ERROR,
            ValidationCode.INVALID_BANK_CODE,
            "bank_code",
            "Bank code must contain one to three digits after normalization.",
            "Use the code displayed by the recipient's bank.",
        )
    elif bank_code not in KNOWN_BANKS:
        _issue(
            issues,
            Severity.WARNING,
            ValidationCode.UNKNOWN_BANK_CODE,
            "bank_code",
            f"Bank code {bank_code} is not in the local reference table.",
            "Verify the code with the recipient or the bank before submission.",
        )

    if not raw_branch_digits:
        _issue(issues, Severity.ERROR, ValidationCode.REQUIRED, "branch_code", "Branch code is required.")
    elif not raw_branch_digits.isdigit() or len(raw_branch_digits) > 3:
        _issue(
            issues,
            Severity.ERROR,
            ValidationCode.INVALID_BRANCH_CODE,
            "branch_code",
            "Branch code must contain one to three digits.",
            "Use a three-digit branch code. Preserve leading zeroes.",
        )
    elif len(raw_branch_digits) < 3:
        _issue(
            issues,
            Severity.WARNING,
            ValidationCode.BRANCH_PADDED,
            "branch_code",
            f"Branch code was normalized from {raw_branch_digits} to {branch_code}.",
            "Confirm that leading zero padding matches the bank form.",
        )

    if not account_number:
        _issue(issues, Severity.ERROR, ValidationCode.REQUIRED, "account_number", "Account number is required.")
    elif not account_number.isdigit() or not (4 <= len(account_number) <= 12):
        _issue(
            issues,
            Severity.ERROR,
            ValidationCode.INVALID_ACCOUNT_NUMBER,
            "account_number",
            "Account number must contain 4 to 12 digits after removing separators.",
            "Copy the number from the recipient's bank confirmation without adding the branch code.",
        )

    if amount is None:
        _issue(issues, Severity.ERROR, ValidationCode.INVALID_AMOUNT, "amount_ils", "Amount must be a valid number.")
    elif amount <= 0:
        _issue(issues, Severity.ERROR, ValidationCode.INVALID_AMOUNT, "amount_ils", "Amount must be greater than zero.")
    elif method == TransferMethod.MASAV and amount >= high_value_threshold_ils:
        _issue(
            issues,
            Severity.WARNING,
            ValidationCode.HIGH_VALUE_MASAV,
            "method",
            "High-value MASAV transfer selected.",
            "Consider Zahav, additional approval, and recipient detail verification.",
        )

    if request.value_date not in (None, "") and value_date is None:
        _issue(
            issues,
            Severity.ERROR,
            ValidationCode.VALUE_DATE_INVALID,
            "value_date",
            "Value date must use YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY.",
        )
    elif value_date is not None:
        if value_date < today:
            _issue(
                issues,
                Severity.ERROR,
                ValidationCode.VALUE_DATE_PAST,
                "value_date",
                "Value date is in the past.",
                "Select today or a future Israeli banking business day.",
            )
        if value_date.weekday() == 4:
            _issue(
                issues,
                Severity.WARNING,
                ValidationCode.VALUE_DATE_CALENDAR_CHECK,
                "value_date",
                "Friday value date selected; Israeli banking and Zahav days can be short business days.",
                "Check the Bank of Israel operating-day calendar and the bank's cutoff before submission.",
            )
        elif value_date.weekday() == 5:
            _issue(
                issues,
                Severity.WARNING,
                ValidationCode.VALUE_DATE_CALENDAR_CHECK,
                "value_date",
                "Saturday value date selected; Israeli banking and Zahav systems are typically closed.",
                "Choose an Israeli banking business day or confirm an exceptional bank instruction.",
            )

    if not str(request.purpose or "").strip():
        _issue(
            issues,
            Severity.WARNING,
            ValidationCode.PURPOSE_MISSING,
            "purpose",
            "Purpose is empty.",
            "Add invoice number, salary month, rent, refund, or tax period.",
        )

    if request.reference and len(request.reference) > reference_max_length:
        _issue(
            issues,
            Severity.WARNING,
            ValidationCode.REFERENCE_TOO_LONG,
            "reference",
            f"Reference is longer than {reference_max_length} characters.",
            "Shorten the reference to avoid truncation.",
        )

    if method == TransferMethod.MASAV and decision.method == TransferMethod.ZAHAV:
        _issue(
            issues,
            Severity.WARNING,
            ValidationCode.METHOD_MISMATCH,
            "method",
            "Selected method conflicts with urgency or amount signals.",
            "Review Zahav suitability before using MASAV.",
        )

    if request.require_confirmation and amount is not None and amount >= Decimal("10000"):
        _issue(
            issues,
            Severity.INFO,
            ValidationCode.CONFIRMATION_RECOMMENDED,
            "recipient",
            "Independent recipient-detail confirmation is recommended for this amount.",
            "Confirm bank, branch, and account using a trusted channel before submission.",
        )

    if environment == RuntimeEnvironment.PRODUCTION and amount is not None and amount >= Decimal("50000") and not request.approved_by:
        _issue(
            issues,
            Severity.WARNING,
            ValidationCode.PRODUCTION_REQUIRES_APPROVAL,
            "approved_by",
            "Production transfer above ₪50,000 has no approver recorded.",
            "Record the approver before copying details into the bank portal.",
        )

    normalized = {
        "payer_name": str(request.payer_name or "").strip(),
        "recipient_name": str(request.recipient_name or "").strip(),
        "bank_code": bank_code,
        "bank_name": KNOWN_BANKS.get(bank_code, ""),
        "branch_code": branch_code,
        "account_number": account_number,
        "redacted_account_number": redact_account(account_number),
        "amount_ils": str(amount) if amount is not None else "",
        "amount_display": format_ils(amount),
        "method": decision.method.value,
        "requested_method": method.value,
        "value_date": value_date.isoformat() if value_date else "",
        "value_date_display": format_local_date(value_date),
        "purpose": str(request.purpose or "").strip(),
        "reference": str(request.reference or "").strip(),
        "urgent": bool(request.urgent),
        "same_day": bool(request.same_day),
        "recurring": bool(request.recurring),
        "bulk_count": int(request.bulk_count or 1),
        "approved_by": str(request.approved_by or "").strip(),
        "source_document_id": str(request.source_document_id or "").strip(),
        "environment": environment.value,
    }
    return ValidationReport(not any(issue.severity == Severity.ERROR for issue in issues), normalized, decision, tuple(issues))


async def async_validate_transfer(request: TransferRequest, **kwargs: Any) -> ValidationReport:
    return await asyncio.to_thread(validate_transfer, request, **kwargs)


def build_bank_form_payload(request: TransferRequest, **kwargs: Any) -> dict[str, Any]:
    report = validate_transfer(request, **kwargs)
    if report.errors:
        raise TransferValidationError(report.errors)
    return {
        "transfer": report.normalized,
        "decision": report.decision.to_dict(),
        "warnings": [issue.to_dict() for issue in report.warnings],
        "infos": [issue.to_dict() for issue in report.infos],
    }


def format_report(report: ValidationReport, *, language: str = "en") -> str:
    if language.lower().startswith("he"):
        lines = [
            "סטטוס: תקין" if report.valid else "סטטוס: נדרש תיקון",
            f"מסלול העברה מומלץ: {report.decision.method.value.upper()}",
            f"סכום: {report.normalized.get('amount_display', '')}",
            f"תאריך ערך: {report.normalized.get('value_date_display', '')}",
            f"בנק/סניף/חשבון: {report.normalized.get('bank_code')}/{report.normalized.get('branch_code')}/{report.normalized.get('account_number')}",
        ]
        if report.issues:
            lines.append("בדיקות:")
            lines.extend(
                f"- {issue.severity.value}: {issue.field}: {issue.message} {issue.suggestion}".strip()
                for issue in report.issues
            )
        return "\n".join(lines)

    lines = [
        "Status: valid" if report.valid else "Status: fixes required",
        f"Recommended method: {report.decision.method.value.upper()}",
        f"Amount: {report.normalized.get('amount_display', '')}",
        f"Value date: {report.normalized.get('value_date_display', '')}",
        f"Bank/branch/account: {report.normalized.get('bank_code')}/{report.normalized.get('branch_code')}/{report.normalized.get('account_number')}",
    ]
    if report.issues:
        lines.append("Checks:")
        lines.extend(
            f"- {issue.severity.value}: {issue.field}: {issue.message}"
            + (f" Suggestion: {issue.suggestion}" if issue.suggestion else "")
            for issue in report.issues
        )
    return "\n".join(lines)


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "כן", "אמת"}


def request_from_mapping(data: Mapping[str, Any]) -> TransferRequest:
    return TransferRequest(
        payer_name=str(data.get("payer_name", "")),
        recipient_name=str(data.get("recipient_name", "")),
        bank_code=str(data.get("bank_code", "")),
        branch_code=str(data.get("branch_code", "")),
        account_number=str(data.get("account_number", "")),
        amount_ils=data.get("amount_ils", data.get("amount", "")),
        method=str(data.get("method", "auto")).lower(),
        value_date=data.get("value_date") or None,
        purpose=str(data.get("purpose", "")),
        reference=str(data.get("reference", "")),
        urgent=_to_bool(data.get("urgent", False)),
        same_day=_to_bool(data.get("same_day", False)),
        recurring=_to_bool(data.get("recurring", False)),
        bulk_count=int(data.get("bulk_count", 1) or 1),
        require_confirmation=_to_bool(data.get("require_confirmation", True)),
        approved_by=str(data.get("approved_by", "")),
        source_document_id=str(data.get("source_document_id", "")),
        metadata={key: value for key, value in data.items() if str(key).startswith("meta_")},
    )


def load_transfers_csv(path: str | Path) -> list[TransferRequest]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [request_from_mapping(row) for row in csv.DictReader(handle)]


def validate_transfers(requests: Iterable[TransferRequest], **kwargs: Any) -> list[ValidationReport]:
    return [validate_transfer(request, **kwargs) for request in requests]


async def async_validate_transfers(requests: Iterable[TransferRequest], **kwargs: Any) -> list[ValidationReport]:
    return await asyncio.gather(*(async_validate_transfer(request, **kwargs) for request in requests))


def redact_account(account_number: str, *, visible: int = 4) -> str:
    digits = normalize_account_number(account_number)
    if len(digits) <= visible:
        return "*" * len(digits)
    return "*" * (len(digits) - visible) + digits[-visible:]


def state_file_path(env: RuntimeEnvironment | str | None = None, storage_dir: str | Path | None = None) -> Path:
    environment = normalize_environment(env)
    base_dir = Path(storage_dir or os.getenv(DEFAULT_STATE_DIR_ENV, ".domestic-bank-transfer-helper"))
    return base_dir / f"{environment.value}-records.json"


def _load_records(env: RuntimeEnvironment | str | None = None, storage_dir: str | Path | None = None) -> dict[str, Any]:
    path = state_file_path(env, storage_dir)
    if not path.exists():
        return {"records": {}}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or "records" not in data or not isinstance(data["records"], dict):
        raise ValueError(f"Invalid state file: {path}")
    return data


def _save_records(data: Mapping[str, Any], env: RuntimeEnvironment | str | None = None, storage_dir: str | Path | None = None) -> Path:
    path = state_file_path(env, storage_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, default=str)
        handle.write("\n")
    return path


def _stable_record_id(normalized: Mapping[str, Any], created_at: str) -> str:
    key_fields = {
        "created_at": created_at,
        "recipient_name": normalized.get("recipient_name", ""),
        "bank_code": normalized.get("bank_code", ""),
        "branch_code": normalized.get("branch_code", ""),
        "account_number": normalized.get("account_number", ""),
        "amount_ils": normalized.get("amount_ils", ""),
        "reference": normalized.get("reference", ""),
    }
    digest = hashlib.sha256(json.dumps(key_fields, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return f"dtf_{digest[:16]}"


def create_transfer_record(
    request: TransferRequest,
    *,
    env: RuntimeEnvironment | str | None = None,
    storage_dir: str | Path | None = None,
    today: date | None = None,
) -> dict[str, Any]:
    environment = normalize_environment(env)
    report = validate_transfer(request, today=today, env=environment)
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    record_id = _stable_record_id(report.normalized, created_at)
    record = {
        "id": record_id,
        "environment": environment.value,
        "created_at": created_at,
        "status": "ready_for_review" if report.valid else "needs_correction",
        "report": report.to_dict(),
    }
    data = _load_records(environment, storage_dir)
    data["records"][record_id] = record
    _save_records(data, environment, storage_dir)
    return record


def get_transfer_record(
    record_id: str,
    *,
    env: RuntimeEnvironment | str | None = None,
    storage_dir: str | Path | None = None,
) -> dict[str, Any]:
    data = _load_records(env, storage_dir)
    try:
        return data["records"][record_id]
    except KeyError as exc:
        raise KeyError(f"Transfer record not found: {record_id}") from exc


def list_transfer_records(
    *,
    env: RuntimeEnvironment | str | None = None,
    storage_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    data = _load_records(env, storage_dir)
    records = list(data["records"].values())
    return sorted(records, key=lambda record: record.get("created_at", ""), reverse=True)


def record_payload(
    record_id: str,
    *,
    env: RuntimeEnvironment | str | None = None,
    storage_dir: str | Path | None = None,
) -> dict[str, Any]:
    record = get_transfer_record(record_id, env=env, storage_dir=storage_dir)
    report_data = record["report"]
    if not report_data["valid"]:
        issues = [
            ValidationIssue(
                severity=Severity(issue["severity"]),
                code=ValidationCode(issue["code"]),
                field=issue["field"],
                message=issue["message"],
                suggestion=issue.get("suggestion", ""),
            )
            for issue in report_data["issues"]
            if issue["severity"] == Severity.ERROR.value
        ]
        raise TransferValidationError(issues)
    return {
        "id": record["id"],
        "environment": record["environment"],
        "transfer": report_data["normalized"],
        "decision": report_data["decision"],
        "warnings": [issue for issue in report_data["issues"] if issue["severity"] == Severity.WARNING.value],
        "infos": [issue for issue in report_data["issues"] if issue["severity"] == Severity.INFO.value],
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate an Israeli domestic bank-transfer request.")
    parser.add_argument("--recipient-name", required=True)
    parser.add_argument("--bank-code", required=True)
    parser.add_argument("--branch-code", required=True)
    parser.add_argument("--account-number", required=True)
    parser.add_argument("--amount-ils", required=True)
    parser.add_argument("--method", default="auto", choices=[method.value for method in TransferMethod])
    parser.add_argument("--value-date", default=None)
    parser.add_argument("--purpose", default="")
    parser.add_argument("--reference", default="")
    parser.add_argument("--urgent", action="store_true")
    parser.add_argument("--same-day", action="store_true")
    parser.add_argument("--env", default=os.getenv(DEFAULT_ENV_ENV, "sandbox"), choices=[env.value for env in RuntimeEnvironment])
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()
    request = TransferRequest(
        recipient_name=args.recipient_name,
        bank_code=args.bank_code,
        branch_code=args.branch_code,
        account_number=args.account_number,
        amount_ils=args.amount_ils,
        method=args.method,
        value_date=args.value_date,
        purpose=args.purpose,
        reference=args.reference,
        urgent=args.urgent,
        same_day=args.same_day,
    )
    report = validate_transfer(request, env=args.env)
    print(report.to_json() if args.json_output else format_report(report))
    return 0 if report.valid else 2


__all__ = [
    "DEFAULT_HIGH_VALUE_THRESHOLD_ILS",
    "DEFAULT_REFERENCE_MAX_LENGTH",
    "KNOWN_BANKS",
    "RuntimeEnvironment",
    "Severity",
    "TransferDecision",
    "TransferMethod",
    "TransferRequest",
    "TransferValidationError",
    "ValidationCode",
    "ValidationIssue",
    "ValidationReport",
    "async_validate_transfer",
    "async_validate_transfers",
    "build_bank_form_payload",
    "create_transfer_record",
    "format_ils",
    "format_local_date",
    "format_report",
    "get_transfer_record",
    "list_transfer_records",
    "load_transfers_csv",
    "normalize_account_number",
    "normalize_bank_code",
    "normalize_branch_code",
    "normalize_digits",
    "normalize_environment",
    "normalize_transfer_method",
    "parse_amount_ils",
    "parse_value_date",
    "record_payload",
    "redact_account",
    "recommend_transfer_method",
    "request_from_mapping",
    "state_file_path",
    "validate_transfer",
    "validate_transfers",
]


if __name__ == "__main__":
    raise SystemExit(main())
