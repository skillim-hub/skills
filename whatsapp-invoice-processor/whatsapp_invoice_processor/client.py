#!/usr/bin/env python3
"""Typed helper for parsing OCR text from WhatsApp invoice images."""

from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable, Literal, Optional

Status = Literal["accepted", "needs_review", "rejected", "duplicate", "unsupported"]
DocumentType = Literal["חשבונית מס", "חשבונית מס/קבלה", "קבלה", "חשבונית זיכוי", "unsupported"]
Currency = Literal["ILS", "USD", "EUR", "UNKNOWN"]

DEFAULT_VAT_RATES: tuple[tuple[str, Optional[str], Decimal], ...] = (
    ("2025-01-01", None, Decimal("0.18")),
    ("2015-10-01", "2024-12-31", Decimal("0.17")),
)

DEFAULT_ALLOCATION_THRESHOLDS: tuple[tuple[str, Optional[str], Decimal], ...] = (
    ("2024-05-05", "2024-12-31", Decimal("25000")),
    ("2025-01-01", "2025-12-31", Decimal("20000")),
    ("2026-01-01", "2026-05-31", Decimal("10000")),
    ("2026-06-01", None, Decimal("5000")),
)
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".txt"}
UNSUPPORTED_DOCUMENT_MARKERS = ("חשבונית פרופורמה", "פרופורמה", "pro forma", "הצעת מחיר", "quote", "דרישת תשלום", "payment request")
VAT_ALIASES = ('מע"מ', "מע״מ", "מעמ", "מס ערך מוסף", "vat")
TOTAL_ALIASES = ('סה"כ לתשלום', "סה״כ לתשלום", "סך הכל לתשלום", "סך הכול לתשלום", 'סה"כ', "סה״כ", "סך הכל", "סך הכול", "total due", "grand total", "total")
SUBTOTAL_ALIASES = ('לפני מע"מ', "לפני מע״מ", 'סה"כ לפני מע"מ', "סה״כ לפני מע״מ", "subtotal", "taxable amount")

_AMOUNT_RE = re.compile(r'(?<!\d)(?:₪|שח|ש"ח|\$|€|ils|usd|eur)?\s*(-?\d{1,3}(?:[,.\s]\d{3})*(?:[,.]\d{1,2})|-?\d+(?:[,.]\d{1,2})?)\s*(?:₪|שח|ש"ח|\$|€|ils|usd|eur)?', re.I)
_TAX_ID_RE = re.compile(r"(?:ח\.?פ\.?|ע\.?מ\.?|עוסק\s+מורשה|עוסק\s+פטור|מספר\s+עוסק|ת\.?ז\.?)\s*[:#-]?\s*(\d{8,9})")
_DATE_RE = re.compile(r"(?<!\d)(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})(?!\d)")
_ISO_DATE_RE = re.compile(r"(?<!\d)(\d{4})-(\d{1,2})-(\d{1,2})(?!\d)")
_ALLOCATION_RE = re.compile(r"(?:מספר\s+הקצאה|מס'\s+הקצאה|מס׳\s+הקצאה|הקצאה|חשבונית\s+ישראל)\s*[:#-]?\s*(\d{6,20})")
_HEB_LETTER_RE = re.compile(r"[א-ת]")


@dataclass(frozen=True)
class ProcessingConfig:
    vat_rates: tuple[tuple[str, Optional[str], Decimal], ...] = DEFAULT_VAT_RATES
    vat_tolerance: Decimal = Decimal("0.02")
    min_confidence_for_accept: Decimal = Decimal("0.85")
    default_ocr_confidence: Decimal = Decimal("0.92")
    require_invoice_number: bool = True
    require_tax_id_for_tax_invoice: bool = False
    allocation_policy_enabled: bool = False
    allocation_threshold_before_vat: Optional[Decimal] = None
    today: Optional[dt.date] = None

    @classmethod
    def from_env(cls, *, env: str = "sandbox") -> "ProcessingConfig":
        from decimal import Decimal
        import os
        if env not in {"sandbox", "production"}:
            raise ValueError("environment must be sandbox or production")
        threshold_raw = os.getenv("WHATSAPP_INVOICE_ALLOCATION_THRESHOLD")
        today_raw = os.getenv("WHATSAPP_INVOICE_TODAY")
        policy_date = parse_policy_date(today_raw) if today_raw else dt.date.today()
        enabled = os.getenv("WHATSAPP_INVOICE_ALLOCATION_REQUIRED", "false").lower() in {"1", "true", "yes", "on"}
        threshold = Decimal(threshold_raw) if threshold_raw else (allocation_threshold_for_date(policy_date) if enabled and env == "production" else None)
        return cls(
            allocation_policy_enabled=enabled,
            allocation_threshold_before_vat=threshold,
            today=policy_date,
            default_ocr_confidence=Decimal(os.getenv("WHATSAPP_INVOICE_DEFAULT_OCR_CONFIDENCE", "0.92")),
            min_confidence_for_accept=Decimal(os.getenv("WHATSAPP_INVOICE_MIN_CONFIDENCE", "0.85")),
            require_tax_id_for_tax_invoice=os.getenv("WHATSAPP_INVOICE_REQUIRE_TAX_ID", "false").lower() in {"1", "true", "yes", "on"},
        )


@dataclass(frozen=True)
class InvoiceExtraction:
    status: Status
    document_type: DocumentType
    vendor_name: Optional[str]
    vendor_tax_id: Optional[str]
    invoice_number: Optional[str]
    issue_date: Optional[str]
    currency: Currency
    amount_before_vat: Optional[Decimal]
    vat_amount: Optional[Decimal]
    vat_rate: Optional[Decimal]
    total_amount: Optional[Decimal]
    allocation_number: Optional[str]
    confidence: Decimal
    warnings: tuple[str, ...] = field(default_factory=tuple)
    chat_reply_he: str = ""
    chat_reply_en: str = ""
    dedupe_key: Optional[str] = None
    raw_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        def clean(v: Any) -> Any:
            if isinstance(v, Decimal):
                return float(v)
            if isinstance(v, tuple):
                return list(v)
            return v
        return {f.name: clean(getattr(self, f.name)) for f in dataclasses.fields(self)}

    def to_json(self, *, ensure_ascii: bool = False, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


class InvoiceProcessor:
    def __init__(self, config: Optional[ProcessingConfig] = None) -> None:
        self.config = config or ProcessingConfig()
        self._seen_dedupe_keys: set[str] = set()

    def parse_text(self, text: str, *, source_name: str = "ocr.txt", ocr_confidence: Optional[Decimal | float | str] = None, known_duplicate_keys: Optional[Iterable[str]] = None) -> InvoiceExtraction:
        raw = text or ""
        normalized = normalize_text(raw)
        suffix = Path(source_name).suffix.lower()
        if suffix and suffix not in SUPPORTED_EXTENSIONS:
            return self._result("unsupported", "unsupported", None, None, None, None, "UNKNOWN", None, None, None, None, None, Decimal("0"), ("unsupported_media_type",), raw, None)
        if not normalized:
            return self._result("unsupported", "unsupported", None, None, None, None, "UNKNOWN", None, None, None, None, None, Decimal("0"), ("empty_text",), raw, None)

        doc_type = classify_document(normalized)
        vendor = extract_vendor_name(normalized)
        tax_id = extract_tax_id(normalized)
        number = extract_invoice_number(normalized)
        date = parse_issue_date(normalized)
        currency = detect_currency(normalized)
        subtotal = extract_subtotal_amount(normalized)
        vat = extract_vat_amount(normalized)
        total = extract_total_amount(normalized)
        allocation = extract_allocation_number(normalized)
        vat_rate = vat_rate_for_date(date, self.config) if date else None
        warnings: list[str] = []

        if doc_type == "unsupported":
            return self._result("unsupported", doc_type, vendor, tax_id, number, date, currency, subtotal, vat, vat_rate, total, allocation, Decimal("0.20"), ("unsupported_document_type",), raw, None)

        if total is not None and subtotal is not None and vat is None:
            possible = money(total - subtotal)
            if possible >= Decimal("0"):
                vat = possible
        if total is not None and vat is not None and subtotal is None:
            subtotal = money(total - vat)

        if vendor is None:
            warnings.append("missing_vendor_name")
        if self.config.require_invoice_number and number is None:
            warnings.append("missing_invoice_number")
        if date is None:
            warnings.append("missing_or_invalid_issue_date")
        elif is_far_future(date, self.config.today):
            warnings.append("future_issue_date")
        if total is None:
            warnings.append("missing_total_amount")
        if currency != "ILS":
            warnings.append("non_ils_currency")
        if doc_type in ("חשבונית מס", "חשבונית מס/קבלה") and self.config.require_tax_id_for_tax_invoice and tax_id is None:
            warnings.append("missing_vendor_tax_id")
        if doc_type in ("חשבונית מס", "חשבונית מס/קבלה") and vat is None and "עוסק פטור" not in normalized:
            warnings.append("missing_vat_amount")
        if not vat_is_consistent(subtotal, vat, total, vat_rate, self.config.vat_tolerance):
            warnings.append("vat_mismatch")
        if allocation_required(doc_type, subtotal, self.config) and not allocation:
            warnings.append("allocation_number_missing")

        confidence = calculate_confidence(
            warnings=warnings,
            ocr_confidence=to_decimal(ocr_confidence) if ocr_confidence is not None else self.config.default_ocr_confidence,
            has_vendor=vendor is not None,
            has_date=date is not None,
            has_total=total is not None,
            amount_consistent="vat_mismatch" not in warnings,
        )
        status: Status = "accepted"
        if confidence < self.config.min_confidence_for_accept or blocking_warnings(warnings):
            status = "needs_review"

        key = build_dedupe_key(vendor_tax_id=tax_id, vendor_name=vendor, document_type=doc_type, invoice_number=number, total_amount=total, issue_date=date)
        known = set(k for k in (known_duplicate_keys or []) if k) | self._seen_dedupe_keys
        if key and key in known:
            status = "duplicate"
            warnings.append("duplicate")
        elif key and status == "accepted":
            self._seen_dedupe_keys.add(key)

        return self._result(status, doc_type, vendor, tax_id, number, date, currency, subtotal, vat, vat_rate, total, allocation, confidence, tuple(dict.fromkeys(warnings)), raw, key)

    async def parse_text_async(self, text: str, **kwargs: Any) -> InvoiceExtraction:
        return await asyncio.to_thread(self.parse_text, text, **kwargs)

    def parse_file(self, path: str | Path, **kwargs: Any) -> InvoiceExtraction:
        p = Path(path)
        if p.suffix.lower() != ".txt":
            return self.parse_text("", source_name=p.name, **kwargs)
        return self.parse_text(p.read_text(encoding="utf-8"), source_name=p.name, **kwargs)

    async def parse_file_async(self, path: str | Path, **kwargs: Any) -> InvoiceExtraction:
        return await asyncio.to_thread(self.parse_file, path, **kwargs)

    def _result(self, status: Status, doc_type: DocumentType, vendor: Optional[str], tax_id: Optional[str], number: Optional[str], date: Optional[str], currency: Currency, subtotal: Optional[Decimal], vat: Optional[Decimal], vat_rate: Optional[Decimal], total: Optional[Decimal], allocation: Optional[str], confidence: Decimal, warnings: tuple[str, ...], raw: str, key: Optional[str]) -> InvoiceExtraction:
        r = InvoiceExtraction(status, doc_type, vendor, tax_id, number, date, currency, subtotal, vat, vat_rate, total, allocation, confidence, warnings, "", "", key, raw)
        return dataclasses.replace(r, chat_reply_he=format_reply_he(r), chat_reply_en=format_reply_en(r))


def normalize_text(text: str) -> str:
    fixed = unicodedata.normalize("NFKC", text or "")
    fixed = fixed.replace("׳", "'").replace("\u200f", "").replace("\u200e", "")
    fixed = re.sub(r"[\t\r]+", " ", fixed)
    fixed = re.sub(r"[ \u00a0]+", " ", fixed)
    return fixed.strip()


def classify_document(text: str) -> DocumentType:
    lower = text.lower()
    if any(m in lower for m in UNSUPPORTED_DOCUMENT_MARKERS):
        return "unsupported"
    if "חשבונית זיכוי" in text or "credit invoice" in lower:
        return "חשבונית זיכוי"
    if "חשבונית מס/קבלה" in text or "חשבונית מס קבלה" in text or "tax invoice/receipt" in lower:
        return "חשבונית מס/קבלה"
    if "חשבונית מס" in text or "tax invoice" in lower:
        return "חשבונית מס"
    if "קבלה" in text or "receipt" in lower:
        return "קבלה"
    return "unsupported"


def clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def extract_vendor_name(text: str) -> Optional[str]:
    skip = ("חשבונית", "קבלה", "תאריך", "מספר", "מס'", "מס׳", "סה", "סך", "מע", "לכבוד", "לקוח", "total", "invoice", "receipt", "vat", "ח.פ", "ע.מ", "עוסק", "date")
    for line in [clean_line(l) for l in text.splitlines() if clean_line(l)][:8]:
        if any(s in line.lower() for s in skip):
            continue
        if _HEB_LETTER_RE.search(line) or re.search(r"[A-Za-z]", line):
            if not re.fullmatch(r"[\d\W]+", line):
                return line.strip(" :-#")[:120]
    return None


def extract_tax_id(text: str) -> Optional[str]:
    m = _TAX_ID_RE.search(text)
    return m.group(1) if m else None


def extract_invoice_number(text: str) -> Optional[str]:
    patterns = [
        r"(?:חשבונית\s+מס/קבלה|חשבונית\s+מס|חשבונית|קבלה|מסמך)\s*(?:מס(?:פר)?|מס'|מס׳|#)?\s*[:#-]?\s*([A-Za-z0-9א-ת][A-Za-z0-9א-ת._/-]{0,24})",
        r"(?:invoice|receipt|document)\s*(?:no\.?|number|#)?\s*[:#-]?\s*([A-Za-z0-9][A-Za-z0-9._/-]{0,24})",
    ]
    for line in text.splitlines():
        if any(w in line.lower() for w in ("חשבונית", "קבלה", "מסמך", "invoice", "receipt", "document")):
            for pat in patterns:
                m = re.search(pat, line, re.I)
                if m:
                    c = m.group(1).strip(" .:-#")
                    if c and not looks_like_date(c) and not c.startswith(("מס", "קבלה")):
                        return c
    return None


def parse_issue_date(text: str) -> Optional[str]:
    m = _ISO_DATE_RE.search(text)
    if m:
        return safe_iso_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    for m in _DATE_RE.finditer(text):
        d, mo, y = map(int, m.groups())
        if y < 100:
            y += 2000 if y < 70 else 1900
        parsed = safe_iso_date(y, mo, d)
        if parsed:
            return parsed
    return None


def safe_iso_date(y: int, m: int, d: int) -> Optional[str]:
    try:
        return dt.date(y, m, d).isoformat()
    except ValueError:
        return None


def looks_like_date(value: str) -> bool:
    return bool(_DATE_RE.search(value) or _ISO_DATE_RE.search(value))


def extract_allocation_number(text: str) -> Optional[str]:
    m = _ALLOCATION_RE.search(text)
    return m.group(1) if m else None


def detect_currency(text: str) -> Currency:
    lower = text.lower()
    if "$" in text or "usd" in lower:
        return "USD"
    if "€" in text or "eur" in lower:
        return "EUR"
    if "₪" in text or "שח" in text or 'ש"ח' in text or "ils" in lower or _AMOUNT_RE.search(text):
        return "ILS"
    return "UNKNOWN"


def amounts_in_text(text: str) -> list[Decimal]:
    out = []
    for m in _AMOUNT_RE.finditer(text):
        # Ignore percentage rates such as 18% while keeping monetary values on the same line.
        next_char = text[m.end():m.end()+1]
        if next_char == "%":
            continue
        parsed = parse_money(m.group(1))
        if parsed is not None and abs(parsed) < Decimal("100000000"):
            out.append(parsed)
    return out


def parse_money(value: str) -> Optional[Decimal]:
    raw = value.strip().replace(" ", "")
    if "," in raw and "." in raw:
        raw = raw.replace(",", "") if raw.rfind(".") > raw.rfind(",") else raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        parts = raw.split(",")
        raw = "".join(parts[:-1]) + "." + parts[-1] if len(parts[-1]) in (1, 2) else raw.replace(",", "")
    elif raw.count(".") > 1:
        parts = raw.split(".")
        raw = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return money(Decimal(raw))
    except Exception:
        return None


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def to_decimal(value: Decimal | float | str) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def extract_labelled_amount(text: str, aliases: Iterable[str], exclude_aliases: Iterable[str] = ()) -> Optional[Decimal]:
    aliases_l = tuple(a.lower() for a in aliases)
    exclude_l = tuple(e.lower() for e in exclude_aliases)
    for line in text.splitlines():
        lower = line.lower()
        if exclude_l and any(e in lower for e in exclude_l):
            continue
        if any(a in lower for a in aliases_l):
            vals = amounts_in_text(line)
            if vals:
                return vals[-1]
    return None


def extract_subtotal_amount(text: str) -> Optional[Decimal]:
    return extract_labelled_amount(text, SUBTOTAL_ALIASES)


def extract_vat_amount(text: str) -> Optional[Decimal]:
    subtotal_lowers = tuple(a.lower() for a in SUBTOTAL_ALIASES)
    for line in text.splitlines():
        lower = line.lower()
        if any(s in lower for s in subtotal_lowers):
            continue
        if any(a.lower() in lower for a in VAT_ALIASES):
            vals = amounts_in_text(line)
            if vals:
                return vals[-1]
    return None


def extract_total_amount(text: str) -> Optional[Decimal]:
    labelled = extract_labelled_amount(text, TOTAL_ALIASES, SUBTOTAL_ALIASES + VAT_ALIASES)
    if labelled is not None:
        return labelled
    currency_lines = [line for line in text.splitlines() if any(marker in line.lower() for marker in ("₪", "שח", "ש\"ח", "ils", "$", "usd", "€", "eur"))]
    vals: list[Decimal] = []
    for line in currency_lines:
        vals.extend(amounts_in_text(line))
    return max(vals, key=lambda v: abs(v)) if vals else None


def parse_policy_date(value: str) -> dt.date:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError("policy date must be YYYY-MM-DD or DD/MM/YYYY")


def allocation_threshold_for_date(date_value: str | dt.date | None = None) -> Optional[Decimal]:
    if date_value is None:
        d = dt.date.today()
    elif isinstance(date_value, dt.date):
        d = date_value
    else:
        d = parse_policy_date(date_value)
    for start, end, threshold in DEFAULT_ALLOCATION_THRESHOLDS:
        start_d = dt.date.fromisoformat(start)
        end_d = dt.date.fromisoformat(end) if end else None
        if d >= start_d and (end_d is None or d <= end_d):
            return threshold
    return None


def vat_rate_for_date(issue_date: Optional[str], config: ProcessingConfig) -> Optional[Decimal]:
    if not issue_date:
        return None
    date_value = dt.date.fromisoformat(issue_date)
    for start, end, rate in config.vat_rates:
        s = dt.date.fromisoformat(start)
        e = dt.date.fromisoformat(end) if end else None
        if date_value >= s and (e is None or date_value <= e):
            return rate
    return None


def vat_is_consistent(subtotal: Optional[Decimal], vat: Optional[Decimal], total: Optional[Decimal], rate: Optional[Decimal], tolerance: Decimal) -> bool:
    if vat is None or total is None:
        return True
    if subtotal is not None and abs(money(subtotal + vat) - total) > tolerance:
        return False
    if subtotal is not None and rate is not None and subtotal > 0:
        expected = money(subtotal * rate)
        if abs(expected - vat) > max(tolerance, Decimal("0.25")):
            return False
    return True


def allocation_required(doc_type: DocumentType, subtotal: Optional[Decimal], config: ProcessingConfig) -> bool:
    return bool(config.allocation_policy_enabled and doc_type in ("חשבונית מס", "חשבונית מס/קבלה") and config.allocation_threshold_before_vat is not None and (subtotal is None or subtotal >= config.allocation_threshold_before_vat))


def is_far_future(issue_date: str, today: Optional[dt.date]) -> bool:
    current = today or dt.date.today()
    return dt.date.fromisoformat(issue_date) > current + dt.timedelta(days=366)


def blocking_warnings(warnings: Iterable[str]) -> bool:
    blockers = {"missing_vendor_name", "missing_invoice_number", "missing_or_invalid_issue_date", "missing_total_amount", "missing_vat_amount", "vat_mismatch", "allocation_number_missing", "future_issue_date", "non_ils_currency"}
    return any(w in blockers for w in warnings)


def calculate_confidence(*, warnings: Iterable[str], ocr_confidence: Decimal, has_vendor: bool, has_date: bool, has_total: bool, amount_consistent: bool) -> Decimal:
    score = Decimal("0.35") * ocr_confidence
    score += Decimal("0.20") if has_vendor else 0
    score += Decimal("0.15") if has_date else 0
    score += Decimal("0.15") if has_total else 0
    score += Decimal("0.15") if amount_consistent else 0
    score -= Decimal("0.04") * Decimal(len(tuple(warnings)))
    return max(Decimal("0.00"), min(Decimal("1.00"), score)).quantize(Decimal("0.01"))


def normalize_vendor_for_key(vendor_name: Optional[str]) -> Optional[str]:
    if not vendor_name:
        return None
    cleaned = re.sub(r"[\W_]+", "", normalize_text(vendor_name).lower(), flags=re.UNICODE)
    return cleaned or None


def build_dedupe_key(*, vendor_tax_id: Optional[str], vendor_name: Optional[str], document_type: DocumentType, invoice_number: Optional[str], total_amount: Optional[Decimal], issue_date: Optional[str]) -> Optional[str]:
    vendor = vendor_tax_id or normalize_vendor_for_key(vendor_name)
    if not (vendor and invoice_number and total_amount is not None and issue_date):
        return None
    raw = f"{vendor}|{document_type}|{invoice_number}|{money(total_amount)}|{issue_date}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def format_money(value: Optional[Decimal]) -> str:
    return "" if value is None else f"{money(value):,.2f}"


def format_date_he(issue_date: Optional[str]) -> str:
    if not issue_date:
        return "לא זוהה"
    return dt.date.fromisoformat(issue_date).strftime("%d/%m/%Y")


def humanize_warning_he(warning: str) -> str:
    labels = {
        "missing_vendor_name": "חסר שם ספק",
        "missing_invoice_number": "חסר מספר מסמך",
        "missing_or_invalid_issue_date": "חסר תאריך תקין",
        "future_issue_date": "תאריך המסמך עתידי מדי",
        "missing_total_amount": "חסר סכום סופי",
        "missing_vat_amount": "חסר סכום מע״מ",
        "vat_mismatch": "סכום המע״מ לא תואם לסכום הכולל",
        "allocation_number_missing": "חסר מספר הקצאה",
        "non_ils_currency": "המטבע אינו שקל ישראלי",
        "unsupported_document_type": "סוג המסמך אינו חשבונית או קבלה",
        "unsupported_media_type": "סוג הקובץ אינו נתמך",
        "empty_text": "לא צורף טקסט או מסמך",
    }
    return labels.get(warning, warning)


def format_reply_he(r: InvoiceExtraction) -> str:
    if r.status == "unsupported":
        if "empty_text" in r.warnings:
            return "נא לשלוח צילום חשבונית או קובץ PDF ברור."
        return "המסמך התקבל, אך לא זוהה כחשבונית מס או קבלה. נא לשלוח חשבונית/קבלה מלאה וברורה."
    if r.status == "duplicate":
        return f"המסמך כבר נקלט קודם: {r.document_type} מספר {r.invoice_number or 'לא זוהה'} מ״{r.vendor_name or 'ספק לא מזוהה'}״ על סך ₪{format_money(r.total_amount)}, תאריך {format_date_he(r.issue_date)}."
    if r.status == "needs_review":
        reason = humanize_warning_he(r.warnings[0] if r.warnings else "נדרשת בדיקה")
        return f"המסמך התקבל, אבל נדרש אימות ידני: {reason}. נא לשלוח צילום חד וברור של כל המסמך, כולל שם העסק, תאריך, מספר מסמך וסכום סופי."
    if r.vat_amount is None:
        return f"נקלטה {r.document_type} מ״{r.vendor_name or 'ספק לא מזוהה'}״ על סך ₪{format_money(r.total_amount)}, תאריך {format_date_he(r.issue_date)}. לא זוהה מע״מ במסמך. תודה."
    return f"נקלטה {r.document_type} מ״{r.vendor_name or 'ספק לא מזוהה'}״ על סך ₪{format_money(r.total_amount)}, כולל מע״מ ₪{format_money(r.vat_amount)}, תאריך {format_date_he(r.issue_date)}. מספר מסמך: {r.invoice_number or 'לא זוהה'}. תודה."


def format_reply_en(r: InvoiceExtraction) -> str:
    if r.status == "unsupported":
        return "Received the file, but it was not identified as a tax invoice or receipt. Send a clear full invoice/receipt image or PDF."
    if r.status == "duplicate":
        return f"This document was already received: {r.document_type} {r.invoice_number or ''} for ₪{format_money(r.total_amount)}."
    if r.status == "needs_review":
        return f"Received the document, but manual review is required: {r.warnings[0] if r.warnings else 'review required'}. Send a clear full image."
    vat = f", VAT ₪{format_money(r.vat_amount)}" if r.vat_amount is not None else ", VAT not detected"
    return f"Received {r.document_type} from {r.vendor_name or 'unknown vendor'} for ₪{format_money(r.total_amount)}{vat}, dated {r.issue_date or 'unknown date'}. Document number: {r.invoice_number or 'unknown'}."


def parse_invoice_text(text: str, **kwargs: Any) -> InvoiceExtraction:
    return InvoiceProcessor().parse_text(text, **kwargs)


async def parse_invoice_text_async(text: str, **kwargs: Any) -> InvoiceExtraction:
    return await InvoiceProcessor().parse_text_async(text, **kwargs)

