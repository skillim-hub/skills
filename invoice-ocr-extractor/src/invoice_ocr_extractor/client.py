from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Optional

SCHEMA_VERSION = "2.2.0"


class DocumentType(str, Enum):
    TAX_INVOICE_RECEIPT = "tax_invoice_receipt"
    TAX_INVOICE = "tax_invoice"
    RECEIPT = "receipt"
    INVOICE = "invoice"
    CREDIT_NOTE = "credit_note"
    PROFORMA = "proforma"
    UNKNOWN = "unknown"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DIGITAL_WALLET = "digital_wallet"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    PAYPAL = "paypal"
    UNKNOWN = "unknown"


class Currency(str, Enum):
    ILS = "ILS"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ExtractorConfig:
    default_vat_rate: float = 18.0
    infer_vat_when_rate_missing: bool = False
    infer_vat_when_rate_visible: bool = True
    vat_tolerance: float = 0.05
    low_confidence_threshold: float = 0.85
    locale: str = "he-IL"
    flag_missing_allocation_number: bool = True


@dataclass
class ExtractedInvoice:
    record_id: Optional[str] = None
    vendor: Optional[str] = None
    document_type: str = DocumentType.UNKNOWN.value
    document_number: Optional[str] = None
    date: Optional[str] = None
    currency: str = Currency.UNKNOWN.value
    total_gross: Optional[float] = None
    vat_amount: Optional[float] = None
    total_net: Optional[float] = None
    vat_rate: Optional[float] = None
    payment_method: str = PaymentMethod.UNKNOWN.value
    business_id: Optional[str] = None
    business_id_type: Optional[str] = None
    allocation_number: Optional[str] = None
    confidence: float = 0.0
    review_flags: list[str] = field(default_factory=list)
    raw_evidence: dict[str, str] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "record_id": self.record_id,
            "vendor": self.vendor,
            "document_type": self.document_type,
            "document_number": self.document_number,
            "date": self.date,
            "currency": self.currency,
            "total_gross": self.total_gross,
            "vat_amount": self.vat_amount,
            "total_net": self.total_net,
            "vat_rate": self.vat_rate,
            "payment_method": self.payment_method,
            "business_id": self.business_id,
            "business_id_type": self.business_id_type,
            "allocation_number": self.allocation_number,
            "confidence": round(self.confidence, 2),
            "review_flags": list(dict.fromkeys(self.review_flags)),
            "raw_evidence": dict(self.raw_evidence),
        }

    def to_json(self, *, ensure_ascii: bool = False, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


@dataclass(frozen=True)
class AmountCandidate:
    value: float
    kind: str
    score: int
    line: str


def normalize_ocr_text(text: str) -> str:
    if not text:
        return ""
    s = str(text).replace("\u200f", "").replace("\u200e", "").replace("\xa0", " ")
    lines: list[str] = []
    for line in s.splitlines():
        line = re.sub(r"(?<=\d)[Oo](?=\d|\.)", "0", line)
        line = re.sub(r"(?<=\d)[lI](?=\d|\.)", "1", line)
        line = re.sub(r"(?<=₪)\s*[lI](?=\d|\.)", "1", line)
        line = re.sub(r"(?<=₪)\s*[Oo](?=\d|\.)", "0", line)
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def _lines(text: str) -> list[str]:
    return [line.strip() for line in normalize_ocr_text(text).splitlines() if line.strip()]


def _round_money(value: float | Decimal) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def parse_amount(raw: str) -> Optional[float]:
    if raw is None:
        return None
    s = str(raw).strip()
    negative = "-" in s or ("(" in s and ")" in s)
    s = re.sub(r"(?<=\d)[Oo](?=\d|\.)", "0", s)
    s = re.sub(r"(?<=\d)[lI](?=\d|\.)", "1", s)
    s = re.sub(r"(?<=₪)\s*[lI](?=\d|\.)", "1", s)
    s = re.sub(r"(?<=₪)\s*[Oo](?=\d|\.)", "0", s)
    s = s.replace("₪", "").replace('ש"ח', "").replace("שח", "")
    s = re.sub(r"(NIS|ILS|USD|EUR|GBP|\$|€|£)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[^0-9,.-]", "", s).strip("-")
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        s = "".join(parts[:-1]) + "." + parts[-1] if len(parts[-1]) == 2 else s.replace(",", "")
    elif s.count(".") > 1:
        first, last = s.rsplit(".", 1)
        s = first.replace(".", "") + "." + last
    try:
        value = float(Decimal(s))
    except (InvalidOperation, ValueError):
        return None
    return _round_money(-abs(value) if negative else value)


_AMOUNT_RE = re.compile(
    r"[-(]?\s*(?:₪|ש\"ח|שח|NIS|ILS|USD|EUR|GBP|\$|€|£)?\s*\d[\d,.OoIl]*\s*(?:₪|ש\"ח|שח|NIS|ILS|USD|EUR|GBP|\$|€|£)?\)?",
    re.IGNORECASE,
)


def amounts_in_line(line: str) -> list[float]:
    values: list[float] = []
    for match in _AMOUNT_RE.finditer(line):
        if "%" in match.group(0) or "%" in line[match.end(): match.end() + 2]:
            continue
        parsed = parse_amount(match.group(0))
        if parsed is not None and abs(parsed) < 10000000:
            values.append(parsed)
    return values


def detect_currency(text: str) -> str:
    t = normalize_ocr_text(text).upper()
    if "USD" in t or "$" in t:
        return Currency.USD.value
    if "EUR" in t or "€" in t:
        return Currency.EUR.value
    if "GBP" in t or "£" in t:
        return Currency.GBP.value
    if "₪" in t or "NIS" in t or "ILS" in t or 'ש"ח' in t or "שח" in t:
        return Currency.ILS.value
    return Currency.UNKNOWN.value


def detect_document_type(text: str) -> str:
    t = re.sub(r"\s+", " ", normalize_ocr_text(text).lower())
    if "חשבונית זיכוי" in t or "credit note" in t:
        return DocumentType.CREDIT_NOTE.value
    if "פרופורמה" in t or "proforma" in t:
        return DocumentType.PROFORMA.value
    if "חשבונית מס קבלה" in t or "חשבונית מס/קבלה" in t or "tax invoice receipt" in t:
        return DocumentType.TAX_INVOICE_RECEIPT.value
    if "חשבונית מס" in t or "tax invoice" in t:
        return DocumentType.TAX_INVOICE.value
    if "קבלה" in t or "receipt" in t:
        return DocumentType.RECEIPT.value
    if "חשבונית עסקה" in t or re.search(r"\binvoice\b", t):
        return DocumentType.INVOICE.value
    return DocumentType.UNKNOWN.value


def detect_payment_method(text: str) -> str:
    t = normalize_ocr_text(text).lower()
    if any(token in t for token in ["bit", "paybox", "ביט", "פייבוקס"]):
        return PaymentMethod.DIGITAL_WALLET.value
    if "paypal" in t:
        return PaymentMethod.PAYPAL.value
    if any(token in t for token in ["אשראי", "credit card", "visa", "mastercard", "ישראכרט"]):
        return PaymentMethod.CREDIT_CARD.value
    if any(token in t for token in ["מזומן", "cash"]):
        return PaymentMethod.CASH.value
    if any(token in t for token in ["העברה בנקאית", "bank transfer", "wire"]):
        return PaymentMethod.BANK_TRANSFER.value
    if any(token in t for token in ["שיק", "cheque", "check"]):
        return PaymentMethod.CHEQUE.value
    return PaymentMethod.UNKNOWN.value


def parse_date(text: str, locale: str = "he-IL") -> tuple[Optional[str], Optional[str], list[str]]:
    t = normalize_ocr_text(text)
    output_format = "%d/%m/%Y" if locale.lower().startswith("he") else "%d/%m/%Y"
    iso = re.search(r"\b(20\d{2}|19\d{2})[-/.](\d{1,2})[-/.](\d{1,2})\b", t)
    if iso:
        year, month, day = map(int, iso.groups())
        try:
            return datetime(year, month, day).strftime(output_format), iso.group(0), []
        except ValueError:
            return None, iso.group(0), ["Invalid date"]
    pattern = r"(?:תאריך(?:\s+מסמך|\s+חשבונית|\s+קבלה)?|Invoice Date|Receipt Date|Document Date|Date)?[:\s-]*\b([0-3]?\d[./-][01]?\d[./-](?:\d{2}|\d{4}))\b"
    match = re.search(pattern, t, re.IGNORECASE)
    if not match:
        return None, None, []
    raw = match.group(1)
    day, month, year = [int(part) for part in re.split(r"[./-]", raw)]
    if year < 100:
        year += 2000 if year <= 69 else 1900
    try:
        dt = datetime(year, month, day)
    except ValueError:
        return None, raw, ["Invalid date"]
    flags = ["Ambiguous date; interpreted as DD/MM/YYYY"] if day <= 12 and month <= 12 else []
    return dt.strftime(output_format), raw, flags


def extract_business_id(text: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    t = normalize_ocr_text(text)
    patterns = [
        (r"(?:עוסק מורשה|מספר עוסק|ע\.?מ\.?|VAT No\.?|Dealer No\.?)[:\s-]*(\d{8,9})", "vat_dealer"),
        (r"(?:ח\.?פ\.?|Company No\.?|Reg\.? No\.?)[:\s-]*(\d{8,9})", "company_number"),
        (r"(?:ע\.?ר\.?|עמותה|Association No\.?)[:\s-]*(\d{8,9})", "association_number"),
    ]
    for pattern, kind in patterns:
        match = re.search(pattern, t, re.IGNORECASE)
        if match:
            return match.group(1), kind, match.group(0)
    return None, None, None


def extract_allocation_number(text: str) -> tuple[Optional[str], Optional[str]]:
    match = re.search(r"(?:מספר הקצאה|הקצאה|Allocation Number)[:\s-]*(\d{6,20})", normalize_ocr_text(text), re.IGNORECASE)
    return (match.group(1), match.group(0)) if match else (None, None)


def extract_vendor(text: str) -> tuple[Optional[str], Optional[str], list[str]]:
    banned = [
        "חשבונית", "קבלה", "מקור", "העתק", "סהכ", 'סה"כ', "תאריך", "invoice", "receipt", "total",
        "subtotal", "bill to", "customer", "לכבוד", "לקוח", "טל", "phone", 'מע"מ', "מעמ", "מע מ", "vat",
        "value added tax",
    ]
    candidates: list[tuple[int, str]] = []
    customer_mode = False
    for index, line in enumerate(_lines(text)[:14]):
        low = line.lower()
        if any(token in low for token in ["לכבוד", "לקוח", "bill to", "customer"]):
            customer_mode = True
            continue
        if customer_mode and not re.search(r"בע.?מ|עוסק|ח\.?פ|ltd|limited|company", line, re.IGNORECASE):
            continue
        if any(token in low for token in banned):
            continue
        if not re.search(r"[א-תA-Za-z]", line) or len(line) < 3:
            continue
        score = 20 - index
        if re.search(r"בע.?מ|עוסק מורשה|עוסק פטור|ח\.?פ\.?|ltd|limited|company|inc", line, re.IGNORECASE):
            score += 20
        if re.search(r"\d{8,9}", line):
            score -= 5
        candidates.append((score, line.strip(" :-")))
    if not candidates:
        return None, None, ["Vendor not found"]
    candidates.sort(reverse=True)
    return candidates[0][1], candidates[0][1], []


def _line_for(text: str, index: int) -> str:
    start = text.rfind("\n", 0, index) + 1
    end = text.find("\n", index)
    return text[start: len(text) if end == -1 else end]


def extract_document_number(text: str) -> tuple[Optional[str], Optional[str], list[str]]:
    t = normalize_ocr_text(text)
    patterns = [
        r"(?:מספר\s*(?:חשבונית|קבלה|מסמך)|Invoice\s*(?:No\.?|Number|#)|Receipt\s*(?:No\.?|Number|#)|Document\s*(?:No\.?|Number|#))[:\s#'״-]*([A-Z]{0,8}[-/]?\d[\w\-/]{0,25})",
        r"(?:חשבונית\s*מס\s*קבלה|חשבונית\s*מס/קבלה|חשבונית\s*זיכוי|חשבונית\s*מס|חשבונית|קבלה|Tax Invoice Receipt|Tax Invoice|Credit Note|Invoice|Receipt)(?:\s*(?:מספר|מס'|מס|No\.?|#|Number))?[:\s#'״-]*([A-Z]{0,8}[-/]?\d[\w\-/]{0,25})",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, t, re.IGNORECASE):
            candidate = match.group(1).strip(" :#'\"״")
            line = _line_for(t, match.start()).lower()
            excluded = ["ח.פ", "ע.מ", "vat no", "dealer", "טל", "phone", "אישור", "approval", "הקצאה", "allocation"]
            document_labels = ["חשבונית", "קבלה", "invoice", "receipt"]
            if any(token in line for token in excluded) and not any(token in line for token in document_labels):
                continue
            return candidate, match.group(0), []
    return None, None, ["Document number not found"]


def label_kind(line: str) -> tuple[str, int]:
    compact = re.sub(r"\s+", " ", line.lower())
    if any(token in compact for token in ['סה"כ לתשלום', "סהכ לתשלום", "סך לתשלום", 'סה"כ שולם', "סהכ שולם", "grand total", "total to pay", "amount paid", "total paid", 'לתשלום סה"כ', "לתשלום סהכ"]):
        return "gross", 100
    if any(token in compact for token in ['סה"כ לפני מע"מ', "סהכ לפני מעמ", 'לפני מע"מ', "subtotal", "before vat", "net", "taxable amount"]):
        return "net", 80
    if any(token in compact for token in ['מע"מ', "מעמ", "מע מ", "vat", "value added tax"]):
        return "vat", 80
    if any(token in compact for token in ["total", 'סה"כ', "סהכ"]):
        return "gross", 40
    return "unknown", 0


def amount_candidates(text: str) -> list[AmountCandidate]:
    candidates: list[AmountCandidate] = []
    for line in _lines(text):
        low = line.lower()
        skip_tokens = ["טל", "phone", "ח.פ", "ע.מ", "vat no", "מספר עוסק", "אישור", "approval", "הקצאה"]
        if any(token in low for token in skip_tokens) and not any(token in low for token in ['מע"מ', "מעמ", "vat"]):
            continue
        kind, score = label_kind(line)
        for value in amounts_in_line(line):
            candidates.append(AmountCandidate(value, kind, score, line))
    return candidates


def _pick(candidates: list[AmountCandidate], kind: str) -> tuple[Optional[float], Optional[str]]:
    filtered = [candidate for candidate in candidates if candidate.kind == kind]
    if not filtered:
        return None, None
    filtered.sort(key=lambda candidate: (candidate.score, abs(candidate.value)), reverse=True)
    return filtered[0].value, filtered[0].line


def extract_vat_rate(text: str) -> tuple[Optional[float], Optional[str]]:
    t = normalize_ocr_text(text)
    match = re.search(r'(?:מע"?מ|מעמ|מע מ|VAT|Value Added Tax)[^\n%]{0,20}?(\d{1,2}(?:[.,]\d+)?)\s*%', t, re.IGNORECASE)
    if not match:
        match = re.search(r'(\d{1,2}(?:[.,]\d+)?)\s*%[^\n]{0,20}(?:מע"?מ|מעמ|מע מ|VAT)', t, re.IGNORECASE)
    if not match:
        return None, None
    rate = parse_amount(match.group(1))
    return (float(rate), match.group(0)) if rate is not None and 0 <= rate <= 30 else (None, None)


def complete_amounts(result: ExtractedInvoice, text: str, config: ExtractorConfig) -> None:
    candidates = amount_candidates(text)
    gross, gross_line = _pick(candidates, "gross")
    net, net_line = _pick(candidates, "net")
    vat, vat_line = _pick(candidates, "vat")
    if gross is None and candidates:
        weak = [candidate for candidate in candidates if candidate.kind == "unknown"]
        if weak:
            gross = weak[-1].value
            gross_line = weak[-1].line
            result.review_flags.append("Gross total inferred from weak amount label")
    result.total_gross = gross
    result.total_net = net
    result.vat_amount = vat
    if gross_line:
        result.raw_evidence["total_gross"] = gross_line
    if net_line:
        result.raw_evidence["total_net"] = net_line
    if vat_line:
        result.raw_evidence["vat_amount"] = vat_line
    rate, rate_line = extract_vat_rate(text)
    if rate is not None:
        result.vat_rate = rate
        result.raw_evidence["vat_rate"] = rate_line or ""
    if "עוסק פטור" in text and result.vat_amount is None:
        if result.total_gross is not None:
            result.total_net = result.total_gross
            result.vat_amount = 0.0
            result.vat_rate = 0.0
        result.review_flags.append("Document indicates exempt dealer; VAT not inferred")
        return
    if result.vat_amount is None and result.total_gross is not None and result.vat_rate is not None and config.infer_vat_when_rate_visible:
        result.total_net = _round_money(result.total_gross / (1 + result.vat_rate / 100))
        result.vat_amount = _round_money(result.total_gross - result.total_net)
        result.review_flags.append("VAT inferred from gross total and visible VAT rate")
    if result.vat_amount is None and result.total_gross is not None and config.infer_vat_when_rate_missing:
        result.vat_rate = config.default_vat_rate
        result.total_net = _round_money(result.total_gross / (1 + result.vat_rate / 100))
        result.vat_amount = _round_money(result.total_gross - result.total_net)
        result.review_flags.append("VAT inferred using configured default rate")
    if result.total_gross is not None and result.total_net is not None and result.vat_amount is not None:
        if abs(_round_money(result.total_net + result.vat_amount) - result.total_gross) > config.vat_tolerance:
            result.review_flags.append("VAT math mismatch: net + VAT does not equal gross")
        elif result.vat_rate is None and result.total_net:
            result.vat_rate = _round_money((result.vat_amount / result.total_net) * 100)
    if result.vat_amount is None:
        result.review_flags.append("VAT not found")
    if result.total_gross is None:
        result.review_flags.append("Gross total not found")


def confidence(result: ExtractedInvoice, text: str) -> float:
    score = 0.0
    score += 0.20 if result.total_gross is not None else 0.0
    score += 0.15 if result.date else 0.0
    score += 0.15 if result.document_number else 0.0
    score += 0.15 if result.vendor else 0.0
    score += 0.20 if result.vat_amount is not None and "VAT math mismatch: net + VAT does not equal gross" not in result.review_flags else 0.0
    score += 0.10 if result.document_type != DocumentType.UNKNOWN.value else 0.0
    score += 0.05 if result.business_id else 0.0
    if len(normalize_ocr_text(text)) < 30:
        score -= 0.10
    if "VAT math mismatch: net + VAT does not equal gross" in result.review_flags:
        score -= 0.15
    if "Vendor not found" in result.review_flags:
        score -= 0.05
    if any("inferred" in flag.lower() for flag in result.review_flags):
        score -= 0.03
    return max(0.0, min(1.0, round(score, 4)))


def build_record_id(result: ExtractedInvoice, text: str) -> str:
    basis = {
        "vendor": result.vendor,
        "document_number": result.document_number,
        "date": result.date,
        "total_gross": result.total_gross,
        "business_id": result.business_id,
        "text_hash": hashlib.sha256(normalize_ocr_text(text).encode("utf-8")).hexdigest()[:16],
    }
    payload = json.dumps(basis, ensure_ascii=False, sort_keys=True)
    return "inv_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def _parse_local_date_value(date_value: Optional[str]) -> Optional[datetime]:
    if not date_value:
        return None
    value = str(date_value).strip()
    for pattern, order in [
        (r"^(\d{1,2})/(\d{1,2})/(\d{4})$", "dmy"),
        (r"^(\d{1,2})-(\d{1,2})-(\d{4})$", "dmy"),
        (r"^(\d{4})-(\d{1,2})-(\d{1,2})$", "ymd"),
    ]:
        match = re.match(pattern, value)
        if not match:
            continue
        a, b, c = map(int, match.groups())
        try:
            if order == "dmy":
                return datetime(c, b, a)
            return datetime(a, b, c)
        except ValueError:
            return None
    return None


def allocation_threshold_for_date(date_value: Optional[str]) -> Optional[float]:
    """Return the Israeli invoice-allocation amount-before-VAT threshold for a document date.

    The table follows Tax Authority public guidance validated on 2026-06-01:
    2025: above 20,000 ILS; 2026-01-01 through 2026-05-31: above 10,000 ILS;
    from 2026-06-01: above 5,000 ILS. Older 2024 pilot guidance used 25,000 ILS.
    """
    dt = _parse_local_date_value(date_value)
    if dt is None:
        return None
    if dt >= datetime(2026, 6, 1):
        return 5000.0
    if dt >= datetime(2026, 1, 1):
        return 10000.0
    if dt >= datetime(2025, 1, 1):
        return 20000.0
    if dt >= datetime(2024, 5, 5):
        return 25000.0
    return None


def amount_before_vat(invoice: ExtractedInvoice | dict[str, Any]) -> Optional[float]:
    data = invoice.to_dict() if isinstance(invoice, ExtractedInvoice) else dict(invoice)
    if data.get("total_net") is not None:
        return float(data["total_net"])
    if data.get("total_gross") is not None and data.get("vat_amount") is not None:
        return _round_money(float(data["total_gross"]) - float(data["vat_amount"]))
    return None


def requires_allocation_number(invoice: ExtractedInvoice | dict[str, Any]) -> bool:
    data = invoice.to_dict() if isinstance(invoice, ExtractedInvoice) else dict(invoice)
    if data.get("document_type") not in {DocumentType.TAX_INVOICE.value, DocumentType.TAX_INVOICE_RECEIPT.value}:
        return False
    if data.get("currency") not in {Currency.ILS.value, Currency.UNKNOWN.value, None}:
        return False
    threshold = allocation_threshold_for_date(data.get("date"))
    before_vat = amount_before_vat(data)
    return threshold is not None and before_vat is not None and before_vat > threshold


def add_allocation_review_flag(result: ExtractedInvoice, config: ExtractorConfig) -> None:
    if not config.flag_missing_allocation_number:
        return
    if result.allocation_number:
        return
    if requires_allocation_number(result):
        threshold = allocation_threshold_for_date(result.date)
        result.review_flags.append(
            f"Allocation number may be required for input VAT deduction; verify Tax Authority threshold above ₪{threshold:,.0f} before VAT"
        )


class InvoiceOCRExtractor:
    def __init__(self, config: Optional[ExtractorConfig] = None) -> None:
        self.config = config or ExtractorConfig()

    def extract_from_text(self, text: str) -> ExtractedInvoice:
        normalized = normalize_ocr_text(text)
        result = ExtractedInvoice()
        result.currency = detect_currency(normalized)
        result.document_type = detect_document_type(normalized)
        result.payment_method = detect_payment_method(normalized)
        vendor, vendor_evidence, vendor_flags = extract_vendor(normalized)
        result.vendor = vendor
        result.review_flags += vendor_flags
        if vendor_evidence:
            result.raw_evidence["vendor"] = vendor_evidence
        document_number, document_evidence, document_flags = extract_document_number(normalized)
        result.document_number = document_number
        result.review_flags += document_flags
        if document_evidence:
            result.raw_evidence["document_number"] = document_evidence
        date_value, date_evidence, date_flags = parse_date(normalized, self.config.locale)
        result.date = date_value
        result.review_flags += date_flags
        if date_evidence:
            result.raw_evidence["date"] = date_evidence
        business_id, business_type, business_evidence = extract_business_id(normalized)
        result.business_id = business_id
        result.business_id_type = business_type
        if business_evidence:
            result.raw_evidence["business_id"] = business_evidence
        allocation_number, allocation_evidence = extract_allocation_number(normalized)
        result.allocation_number = allocation_number
        if allocation_evidence:
            result.raw_evidence["allocation_number"] = allocation_evidence
        complete_amounts(result, normalized, self.config)
        add_allocation_review_flag(result, self.config)
        low = normalized.lower()
        if result.currency not in [Currency.UNKNOWN.value, Currency.ILS.value]:
            result.review_flags.append("Foreign currency; conversion rate required for local bookkeeping")
        if any(token in low for token in ["bit", "paybox", "ביט", "פייבוקס", "העברה בוצעה"]) and not any(token in low for token in ["חשבונית", "invoice", "קבלה", "receipt"]):
            result.review_flags.append("Payment confirmation may not be a tax invoice")
        if any(token in low for token in ["העתק", "copy", "duplicate"]):
            result.review_flags.append("Copy/duplicate indicator visible")
        if result.document_type == DocumentType.CREDIT_NOTE.value:
            credit_amounts = [value for value in [result.total_gross, result.total_net, result.vat_amount] if value is not None]
            if credit_amounts and all(value >= 0 for value in credit_amounts):
                result.review_flags.append("Credit note with positive displayed amounts; verify sign before import")
        if result.document_type == DocumentType.PROFORMA.value:
            result.review_flags.append("Proforma invoice; review before expense import")
        if result.document_type == DocumentType.UNKNOWN.value:
            result.review_flags.append("Document type not identified")
        result.review_flags = list(dict.fromkeys(result.review_flags))
        result.confidence = confidence(result, normalized)
        result.record_id = build_record_id(result, normalized)
        return result

    async def extract_from_text_async(self, text: str) -> ExtractedInvoice:
        return await asyncio.to_thread(self.extract_from_text, text)

    def extract_from_file(self, path: str | Path) -> ExtractedInvoice:
        input_path = Path(path)
        if not input_path.exists():
            raise FileNotFoundError(str(input_path))
        if input_path.suffix.lower() in [".txt", ".ocr", ".md"]:
            return self.extract_from_text(input_path.read_text(encoding="utf-8"))
        raise RuntimeError("OCR_ENGINE_UNAVAILABLE: provide OCR text or integrate an OCR engine for image/PDF input")

    async def extract_from_file_async(self, path: str | Path) -> ExtractedInvoice:
        return await asyncio.to_thread(self.extract_from_file, path)

    def batch_extract(self, folder: str | Path, pattern: str = "*.txt") -> list[tuple[Path, ExtractedInvoice]]:
        folder_path = Path(folder)
        if not folder_path.is_dir():
            raise NotADirectoryError(str(folder_path))
        return [(path, self.extract_from_file(path)) for path in sorted(folder_path.glob(pattern)) if path.is_file()]

    async def batch_extract_async(self, folder: str | Path, pattern: str = "*.txt") -> list[tuple[Path, ExtractedInvoice]]:
        return await asyncio.to_thread(self.batch_extract, folder, pattern)

    def allocation_threshold_for_date(self, date_value: Optional[str]) -> Optional[float]:
        return allocation_threshold_for_date(date_value)

    def requires_allocation_number(self, invoice: ExtractedInvoice | dict[str, Any]) -> bool:
        return requires_allocation_number(invoice)

    def validate(self, invoice: ExtractedInvoice | dict[str, Any], expected_id: Optional[str] = None) -> list[str]:
        data = invoice.to_dict() if isinstance(invoice, ExtractedInvoice) else dict(invoice)
        errors: list[str] = []
        if all(data.get(key) is not None for key in ["total_gross", "total_net", "vat_amount"]):
            if abs(float(data["total_net"]) + float(data["vat_amount"]) - float(data["total_gross"])) > self.config.vat_tolerance:
                errors.append("VAT_MATH_MISMATCH")
        if not data.get("vendor"):
            errors.append("VENDOR_MISSING")
        if not data.get("document_number"):
            errors.append("DOCUMENT_NUMBER_MISSING")
        if not data.get("date"):
            errors.append("DATE_MISSING")
        if expected_id is not None and data.get("record_id") != expected_id:
            errors.append("RECORD_ID_MISMATCH")
        return errors

    def to_review_queue_item(self, source: str | Path, invoice: ExtractedInvoice) -> dict[str, Any]:
        return {
            "source": str(source),
            "record_id": invoice.record_id,
            "confidence": round(invoice.confidence, 2),
            "review_required": invoice.confidence < self.config.low_confidence_threshold or bool(invoice.review_flags),
            "review_flags": list(invoice.review_flags),
            "data": invoice.to_dict(),
        }


def export_csv(rows: list[tuple[Path, ExtractedInvoice]], output_path: str | Path) -> None:
    fields = [
        "source_file", "record_id", "date", "vendor", "document_type", "document_number", "total_net",
        "vat_amount", "total_gross", "currency", "payment_method", "business_id", "confidence", "review_flags",
    ]
    with Path(output_path).open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for source, result in rows:
            data = result.to_dict()
            writer.writerow({
                key: "; ".join(data[key]) if key == "review_flags" else str(source) if key == "source_file" else data.get(key)
                for key in fields
            })


def load_invoice_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
