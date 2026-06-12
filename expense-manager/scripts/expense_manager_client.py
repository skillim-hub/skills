#!/usr/bin/env python3
"""Typed helper library for Israeli expense classification and accountant package export.

Run as a library from other scripts or import dynamically from this file path.
"""
from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

VAT_RATE = Decimal("0.18")
DEFAULT_EQUIPMENT_IMMEDIATE_EXPENSE_LIMIT_ILS = Decimal("1200")
DEFAULT_GIFT_CAP_ILS = Decimal("240")
DEFAULT_HOME_OFFICE_PERCENT = Decimal("0")
DEFAULT_CURRENCY = "ILS"


class EntityType(str, Enum):
    """Supported taxpayer/entity profiles."""

    OSEK_PATUR = "osek_patur"
    OSEK_MURSHE = "osek_murshe"
    COMPANY = "company"
    PRIVATE_CONSUMER = "private_consumer"


class ReviewSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    BLOCKER = "blocker"


@dataclass(frozen=True)
class BusinessConfig:
    """Classification settings supplied by the operator or caller."""

    entity_type: EntityType = EntityType.OSEK_MURSHE
    home_office_percent: Decimal = DEFAULT_HOME_OFFICE_PERCENT
    vehicle_business_vat_rate: Decimal = Decimal("0.6667")
    equipment_immediate_expense_limit_ils: Decimal = DEFAULT_EQUIPMENT_IMMEDIATE_EXPENSE_LIMIT_ILS
    gift_cap_ils: Decimal = DEFAULT_GIFT_CAP_ILS
    fiscal_year: int | None = None
    strict: bool = False


@dataclass(frozen=True)
class ExpenseInput:
    """One normalized expense row."""

    date: date
    vendor: str
    amount: Decimal
    description: str = ""
    currency: str = DEFAULT_CURRENCY
    amount_includes_vat: bool = True
    receipt_number: str | None = None
    document_type: str | None = None
    fx_rate_to_ils: Decimal = Decimal("1")
    tags: tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Rule:
    """Deterministic categorization rule."""

    category: str
    hebrew_category: str
    account_code: str
    deduction_rate: Decimal
    vat_reclaim_rate: Decimal
    keywords: tuple[str, ...]
    notes: str
    requires_documentation: tuple[str, ...] = ()
    capital_asset: bool = False
    depreciation_years: int | None = None
    priority: int = 100


@dataclass(frozen=True)
class ReviewFlag:
    severity: ReviewSeverity
    code: str
    message: str


@dataclass(frozen=True)
class ExpenseResult:
    """Classification output for one expense."""

    expense: ExpenseInput
    category: str
    hebrew_category: str
    account_code: str
    amount_ils: Decimal
    net_amount_ils: Decimal
    input_vat_ils: Decimal
    reclaimable_vat_ils: Decimal
    income_tax_base_ils: Decimal
    deductible_rate: Decimal
    deductible_amount_ils: Decimal
    non_deductible_amount_ils: Decimal
    confidence: Decimal
    rule_notes: str
    review_flags: tuple[ReviewFlag, ...] = field(default_factory=tuple)
    suggested_export_code: str | None = None
    depreciation_years: int | None = None

    def to_flat_dict(self) -> dict[str, Any]:
        """Return a CSV/JSON-friendly representation."""
        d = {
            "date": self.expense.date.strftime("%d/%m/%Y"),
            "vendor": self.expense.vendor,
            "description": self.expense.description,
            "currency": self.expense.currency,
            "amount_original": _decimal_to_str(self.expense.amount),
            "amount_ils": _decimal_to_str(self.amount_ils),
            "category": self.category,
            "hebrew_category": self.hebrew_category,
            "account_code": self.account_code,
            "net_amount_ils": _decimal_to_str(self.net_amount_ils),
            "input_vat_ils": _decimal_to_str(self.input_vat_ils),
            "reclaimable_vat_ils": _decimal_to_str(self.reclaimable_vat_ils),
            "income_tax_base_ils": _decimal_to_str(self.income_tax_base_ils),
            "deductible_rate": _decimal_to_str(self.deductible_rate),
            "deductible_amount_ils": _decimal_to_str(self.deductible_amount_ils),
            "non_deductible_amount_ils": _decimal_to_str(self.non_deductible_amount_ils),
            "confidence": _decimal_to_str(self.confidence),
            "rule_notes": self.rule_notes,
            "suggested_export_code": self.suggested_export_code or "",
            "depreciation_years": self.depreciation_years or "",
            "review_flags": "; ".join(f"{f.severity.value}:{f.code}:{f.message}" for f in self.review_flags),
            "receipt_number": self.expense.receipt_number or "",
            "document_type": self.expense.document_type or "",
        }
        return d


RULES: tuple[Rule, ...] = (
    Rule("professional_services", "שירותים מקצועיים", "6700", Decimal("1"), Decimal("1"), ("accountant", "bookkeeper", "cpa", "lawyer", "attorney", "consultant", "רו\"ח", "רואה חשבון", "עורך דין", "יועץ"), "Professional service used for business operations.", ("tax invoice",), priority=10),
    Rule("software_and_saas", "תוכנה ושירותי ענן", "6505", Decimal("1"), Decimal("1"), ("software", "saas", "cloud", "hosting", "domain", "github", "google workspace", "microsoft", "aws", "azure", "חשבונית ירוקה", "תוכנה", "אחסון", "דומיין"), "Business software, hosting, and digital services.", ("invoice",), priority=20),
    Rule("marketing_advertising", "שיווק ופרסום", "6600", Decimal("1"), Decimal("1"), ("ads", "advertising", "facebook", "meta", "google ads", "linkedin", "campaign", "printing", "flyer", "פרסום", "שיווק", "קמפיין", "דפוס"), "Advertising and customer acquisition expense.", ("invoice", "campaign evidence"), priority=30),
    Rule("office_rent", "שכירות משרד", "6300", Decimal("1"), Decimal("1"), ("office rent", "cowork", "wework", "rent office", "שכירות משרד", "חלל עבודה", "משרד"), "Dedicated office cost.", ("lease", "invoice"), priority=35),
    Rule("home_office", "משרד ביתי", "6310", Decimal("0"), Decimal("0"), ("home office", "home electricity", "home arnona", "home internet", "חשמל בית", "ארנונה בית", "משרד ביתי", "שכירות דירה"), "Apply configured home-office percentage only to a dedicated workspace.", ("floor area calculation",), priority=40),
    Rule("vehicle", "הוצאות רכב", "6400", Decimal("0.45"), Decimal("0.6667"), ("fuel", "gas", "petrol", "parking", "toll", "road 6", "car insurance", "garage", "maintenance", "דלק", "חניה", "כביש 6", "ביטוח רכב", "מוסך", "רכב"), "Mixed-use vehicle expenses: 45% income-tax default; VAT rate depends on business use and vehicle type.", ("tax invoice", "vehicle log if material"), priority=50),
    Rule("phone_internet", "טלפון ואינטרנט", "6510", Decimal("0.80"), Decimal("0.6667"), ("phone", "mobile", "cellular", "internet", "bezeq", "partner", "cellcom", "hot", "pelephone", "טלפון", "סלולרי", "אינטרנט", "בזק", "פרטנר", "סלקום", "הוט", "פלאפון"), "Mixed-use communication expense: 80% income-tax default; input VAT often requires mixed-use limitation.", ("tax invoice",), priority=55),
    Rule("workplace_refreshments", "כיבוד קל במקום העסק", "6555", Decimal("0.80"), Decimal("0.80"), ("coffee for office", "tea", "snacks", "refreshments", "water bar", "כיבוד קל", "קפה למשרד", "תה", "חטיפים", "בר מים"), "Light refreshments at the workplace, not restaurant hospitality.", ("invoice",), priority=60),
    Rule("domestic_hospitality", "אירוח בארץ", "6620", Decimal("0"), Decimal("0"), ("restaurant", "cafe", "coffee with client", "business lunch", "aroma", "ארומה", "מסעדה", "בית קפה", "ארוחת עסקית", "קפה עם לקוח"), "Domestic hospitality is generally disallowed unless a specific exception applies.", ("receipt", "business purpose"), priority=65),
    Rule("foreign_guest_hospitality", "אירוח אורחי חוץ", "6625", Decimal("1"), Decimal("1"), ("foreign guest", "overseas guest", "guest from abroad", "אורח חוץ", "אורחי חוץ", "לקוח מחו\"ל"), "Foreign guest hospitality may be deductible with guest identity and business purpose documented.", ("guest name", "country", "business purpose", "invoice"), priority=4),
    Rule("business_travel_abroad", "נסיעות עסקיות לחו\"ל", "6800", Decimal("1"), Decimal("1"), ("flight", "hotel abroad", "airbnb business", "conference abroad", "overseas travel", "טיסה", "מלון בחו\"ל", "נסיעה לחו\"ל", "כנס בחו\"ל"), "Business travel abroad requires purpose, dates, destination, and receipts; per-diem caps may apply.", ("itinerary", "receipts", "business purpose"), priority=70),
    Rule("office_supplies", "ציוד משרדי", "6500", Decimal("1"), Decimal("1"), ("office supplies", "paper", "ink", "printer toner", "stationery", "ציוד משרדי", "נייר", "דיו", "טונר", "מדפסת"), "Routine supplies used by the business.", ("invoice",), priority=80),
    Rule("capital_equipment", "רכוש קבוע ופחת", "7800", Decimal("0"), Decimal("1"), ("laptop", "computer", "monitor", "camera", "furniture", "desk", "chair", "מחשב", "לפטופ", "מסך", "מצלמה", "ריהוט", "שולחן", "כיסא"), "Capital asset above the immediate-expense threshold; depreciate instead of expensing immediately.", ("tax invoice", "asset register"), True, 3, priority=85),
    Rule("gifts", "מתנות ללקוחות", "6630", Decimal("1"), Decimal("1"), ("gift", "client gift", "holiday gift", "מתנה", "שי לחג", "מתנות ללקוחות"), "Client gifts are deductible only up to the annual per-recipient cap.", ("recipient list", "invoice"), priority=90),
    Rule("insurance_business", "ביטוח עסקי", "6560", Decimal("1"), Decimal("1"), ("business insurance", "professional liability", "cyber insurance", "ביטוח עסק", "אחריות מקצועית", "ביטוח סייבר"), "Business insurance premiums.", ("policy", "invoice"), priority=95),
    Rule("fines_penalties", "קנסות ועיצומים", "6990", Decimal("0"), Decimal("0"), ("fine", "penalty", "traffic ticket", "late filing", "קנס", "דוח", "עיצום", "איחור בדיווח"), "Fines and penalties are not deductible.", ("notice",), priority=5),
    Rule("personal", "הוצאה פרטית", "9990", Decimal("0"), Decimal("0"), ("personal", "clothing", "gym", "netflix", "groceries", "ביגוד", "חדר כושר", "נטפליקס", "סופר", "מצרכים"), "Personal expense; exclude from business deduction.", (), priority=6),
)

DEFAULT_RULE = Rule("uncategorized_review", "לא מסווג - לבדיקה", "6999", Decimal("0"), Decimal("0"), tuple(), "No deterministic rule matched; require accountant review.", ("invoice",), priority=999)

DATE_FORMATS = ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d.%m.%Y")
COLUMN_ALIASES = {
    "date": ("date", "transaction_date", "תאריך", "תאריך עסקה"),
    "vendor": ("vendor", "supplier", "merchant", "payee", "ספק", "בית עסק", "שם ספק"),
    "amount": ("amount", "total", "sum", "debit", "סכום", "סהכ", "סה\"כ", "חיוב"),
    "description": ("description", "details", "memo", "תיאור", "פרטים", "הערות"),
    "currency": ("currency", "מטבע"),
    "receipt_number": ("receipt_number", "invoice", "invoice_number", "מספר חשבונית", "חשבונית"),
    "document_type": ("document_type", "doc_type", "סוג מסמך"),
    "fx_rate_to_ils": ("fx_rate_to_ils", "fx", "שער", "שער המרה"),
}


def q2(value: Decimal) -> Decimal:
    """Round monetary values to agorot."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _decimal_to_str(value: Decimal) -> str:
    return format(q2(value), "f")


def parse_decimal(value: Any) -> Decimal:
    """Parse amounts such as ₪1,234.50 or -300 into Decimal."""
    if isinstance(value, Decimal):
        return value
    if value is None:
        raise ValueError("missing decimal value")
    text = str(value).strip()
    text = text.replace("₪", "").replace(",", "").replace("ILS", "").strip()
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal value: {value!r}") from exc


def parse_date(value: Any) -> date:
    """Parse common Israeli and ISO date formats."""
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"unsupported date format: {value!r}; expected DD-MM-YYYY or YYYY-MM-DD")


def _lower_join(*parts: str) -> str:
    return " ".join(p for p in parts if p).lower()


def _find_column(row: Mapping[str, Any], logical_name: str) -> Any:
    aliases = {a.lower() for a in COLUMN_ALIASES[logical_name]}
    for key, value in row.items():
        if key.strip().lower() in aliases:
            return value
    return None


def expense_from_row(row: Mapping[str, Any]) -> ExpenseInput:
    """Convert a CSV/Excel row dictionary into ExpenseInput."""
    raw_date = _find_column(row, "date")
    raw_vendor = _find_column(row, "vendor")
    raw_amount = _find_column(row, "amount")
    if raw_date in (None, "") or raw_vendor in (None, "") or raw_amount in (None, ""):
        raise ValueError(f"row must contain date, vendor, and amount: {row}")
    currency = (_find_column(row, "currency") or DEFAULT_CURRENCY).strip().upper()
    fx_raw = _find_column(row, "fx_rate_to_ils")
    fx = parse_decimal(fx_raw) if fx_raw not in (None, "") else Decimal("1")
    return ExpenseInput(
        date=parse_date(raw_date),
        vendor=str(raw_vendor).strip(),
        amount=parse_decimal(raw_amount).copy_abs(),
        description=str(_find_column(row, "description") or "").strip(),
        currency=currency,
        amount_includes_vat=True,
        receipt_number=(str(_find_column(row, "receipt_number")).strip() if _find_column(row, "receipt_number") else None),
        document_type=(str(_find_column(row, "document_type")).strip() if _find_column(row, "document_type") else None),
        fx_rate_to_ils=fx,
        metadata=dict(row),
    )


def read_expenses_csv(path: str | Path, encoding: str = "utf-8-sig") -> list[ExpenseInput]:
    """Read expenses from a CSV file."""
    with Path(path).open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        return [expense_from_row(row) for row in reader]


def write_results_csv(results: Sequence[ExpenseResult], path: str | Path) -> Path:
    """Write classification results to CSV."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [r.to_flat_dict() for r in results]
    fieldnames = list(rows[0].keys()) if rows else list(ExpenseResult.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output


def _match_rule(expense: ExpenseInput) -> tuple[Rule, Decimal]:
    text = _lower_join(expense.vendor, expense.description, " ".join(expense.tags))
    scored: list[tuple[int, int, Rule]] = []
    for rule in RULES:
        hits = sum(1 for keyword in rule.keywords if keyword.lower() in text)
        if hits:
            scored.append((-hits, rule.priority, rule))
    if not scored:
        return DEFAULT_RULE, Decimal("0.25")
    scored.sort(key=lambda item: (item[0], item[1]))
    hits = -scored[0][0]
    confidence = min(Decimal("0.95"), Decimal("0.55") + Decimal(hits) * Decimal("0.15"))
    return scored[0][2], confidence


def _input_vat(amount_ils: Decimal, includes_vat: bool) -> tuple[Decimal, Decimal]:
    if not includes_vat:
        net = amount_ils
        vat = amount_ils * VAT_RATE
        return q2(net), q2(vat)
    net = amount_ils / (Decimal("1") + VAT_RATE)
    vat = amount_ils - net
    return q2(net), q2(vat)


def _flags(expense: ExpenseInput, rule: Rule, config: BusinessConfig, result_values: Mapping[str, Decimal]) -> tuple[ReviewFlag, ...]:
    flags: list[ReviewFlag] = []
    if not expense.receipt_number:
        flags.append(ReviewFlag(ReviewSeverity.WARNING, "missing_receipt", "Attach a tax invoice/receipt before package delivery."))
    if rule.category == "uncategorized_review":
        flags.append(ReviewFlag(ReviewSeverity.BLOCKER, "uncategorized", "Map manually or add a rule before accountant import."))
    if rule.category == "home_office" and config.home_office_percent <= 0:
        flags.append(ReviewFlag(ReviewSeverity.BLOCKER, "missing_home_office_percent", "Set dedicated workspace percentage."))
    if rule.category == "capital_equipment" and result_values["amount_ils"] <= config.equipment_immediate_expense_limit_ils:
        flags.append(ReviewFlag(ReviewSeverity.INFO, "small_equipment", "Amount is within the immediate-expense threshold; accountant may expense directly."))
    if rule.category == "business_travel_abroad":
        flags.append(ReviewFlag(ReviewSeverity.WARNING, "travel_docs_required", "Keep itinerary, purpose, destination, and receipts."))
    if rule.category == "foreign_guest_hospitality":
        flags.append(ReviewFlag(ReviewSeverity.WARNING, "foreign_guest_details_required", "Keep guest name, country, role, and business purpose."))
    if config.strict and flags:
        strict_flags = [f for f in flags if f.severity in {ReviewSeverity.WARNING, ReviewSeverity.BLOCKER}]
        if strict_flags:
            flags.append(ReviewFlag(ReviewSeverity.BLOCKER, "strict_mode", "Resolve warnings before export."))
    return tuple(flags)


def classify_expense(expense: ExpenseInput, config: BusinessConfig | None = None) -> ExpenseResult:
    """Classify a single expense deterministically."""
    config = config or BusinessConfig()
    rule, confidence = _match_rule(expense)
    amount_ils = q2(expense.amount * expense.fx_rate_to_ils)
    deduction_rate = rule.deduction_rate
    vat_reclaim_rate = rule.vat_reclaim_rate
    depreciation_years = rule.depreciation_years
    notes = rule.notes

    if config.entity_type == EntityType.PRIVATE_CONSUMER:
        deduction_rate = Decimal("0")
        vat_reclaim_rate = Decimal("0")
        notes = f"Private consumer mode: classification only. {notes}"
    elif config.entity_type == EntityType.OSEK_PATUR:
        vat_reclaim_rate = Decimal("0")
        notes = f"Osek Patur cannot reclaim input VAT. {notes}"

    if rule.category == "home_office":
        deduction_rate = max(Decimal("0"), min(Decimal("1"), config.home_office_percent / Decimal("100")))
        vat_reclaim_rate = deduction_rate if config.entity_type != EntityType.OSEK_PATUR else Decimal("0")
    elif rule.category == "vehicle":
        vat_reclaim_rate = config.vehicle_business_vat_rate if config.entity_type != EntityType.OSEK_PATUR else Decimal("0")
    elif rule.category == "capital_equipment" and amount_ils <= config.equipment_immediate_expense_limit_ils:
        deduction_rate = Decimal("1")
        depreciation_years = None
        notes = "Equipment within immediate-expense threshold; keep tax invoice and accountant approval."
    elif rule.category == "gifts" and amount_ils > config.gift_cap_ils:
        deduction_rate = config.gift_cap_ils / amount_ils
        notes = f"Client gift capped at {config.gift_cap_ils} ILS per recipient per year."

    net_amount, input_vat = _input_vat(amount_ils, expense.amount_includes_vat)
    reclaimable_vat = q2(input_vat * vat_reclaim_rate)
    income_tax_base = q2(amount_ils - reclaimable_vat)
    deductible_amount = q2(income_tax_base * deduction_rate)
    non_deductible = q2(income_tax_base - deductible_amount)
    values = {"amount_ils": amount_ils, "deductible_amount": deductible_amount}
    flags = _flags(expense, rule, config, values)

    return ExpenseResult(
        expense=expense,
        category=rule.category,
        hebrew_category=rule.hebrew_category,
        account_code=rule.account_code,
        amount_ils=amount_ils,
        net_amount_ils=net_amount,
        input_vat_ils=input_vat,
        reclaimable_vat_ils=reclaimable_vat,
        income_tax_base_ils=income_tax_base,
        deductible_rate=q2(deduction_rate * Decimal("100")),
        deductible_amount_ils=deductible_amount,
        non_deductible_amount_ils=non_deductible,
        confidence=q2(confidence * Decimal("100")),
        rule_notes=notes,
        review_flags=flags,
        suggested_export_code=f"IL-{rule.account_code}",
        depreciation_years=depreciation_years,
    )


def classify_many(expenses: Iterable[ExpenseInput], config: BusinessConfig | None = None) -> list[ExpenseResult]:
    """Classify many expenses."""
    config = config or BusinessConfig()
    return [classify_expense(expense, config) for expense in expenses]


async def async_classify_expense(expense: ExpenseInput, config: BusinessConfig | None = None) -> ExpenseResult:
    """Async wrapper for a single classification."""
    return await asyncio.to_thread(classify_expense, expense, config)


async def async_classify_many(expenses: Iterable[ExpenseInput], config: BusinessConfig | None = None) -> list[ExpenseResult]:
    """Async wrapper for batch classification."""
    expense_list = list(expenses)
    return await asyncio.gather(*(async_classify_expense(e, config) for e in expense_list))


def summarize_results(results: Sequence[ExpenseResult]) -> dict[str, Any]:
    """Create accountant-friendly totals by category and account code."""
    summary: dict[str, Any] = {
        "total_rows": len(results),
        "total_amount_ils": "0.00",
        "total_reclaimable_vat_ils": "0.00",
        "total_deductible_ils": "0.00",
        "total_non_deductible_ils": "0.00",
        "by_category": {},
        "review_flag_count": 0,
    }
    totals = {"amount": Decimal("0"), "vat": Decimal("0"), "deductible": Decimal("0"), "non": Decimal("0")}
    by_category: dict[str, dict[str, Decimal | int | str]] = {}
    flags = 0
    for r in results:
        totals["amount"] += r.amount_ils
        totals["vat"] += r.reclaimable_vat_ils
        totals["deductible"] += r.deductible_amount_ils
        totals["non"] += r.non_deductible_amount_ils
        flags += len(r.review_flags)
        bucket = by_category.setdefault(r.category, {"rows": 0, "account_code": r.account_code, "amount_ils": Decimal("0"), "deductible_ils": Decimal("0"), "reclaimable_vat_ils": Decimal("0")})
        bucket["rows"] = int(bucket["rows"]) + 1
        bucket["amount_ils"] = Decimal(bucket["amount_ils"]) + r.amount_ils
        bucket["deductible_ils"] = Decimal(bucket["deductible_ils"]) + r.deductible_amount_ils
        bucket["reclaimable_vat_ils"] = Decimal(bucket["reclaimable_vat_ils"]) + r.reclaimable_vat_ils
    summary["total_amount_ils"] = _decimal_to_str(totals["amount"])
    summary["total_reclaimable_vat_ils"] = _decimal_to_str(totals["vat"])
    summary["total_deductible_ils"] = _decimal_to_str(totals["deductible"])
    summary["total_non_deductible_ils"] = _decimal_to_str(totals["non"])
    summary["review_flag_count"] = flags
    summary["by_category"] = {
        k: {kk: (_decimal_to_str(vv) if isinstance(vv, Decimal) else vv) for kk, vv in v.items()}
        for k, v in sorted(by_category.items())
    }
    return summary


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def export_accountant_package(
    results: Sequence[ExpenseResult],
    output_dir: str | Path,
    package_name: str = "accountant-expense-package",
    source_files: Sequence[str | Path] = (),
) -> Path:
    """Export CSV, JSON summaries, import hints, manifest, and a ZIP package."""
    base = Path(output_dir)
    work = base / package_name
    if work.exists():
        shutil.rmtree(work)
    (work / "exports").mkdir(parents=True)
    (work / "source").mkdir()
    (work / "reports").mkdir()

    classifications = write_results_csv(results, work / "exports" / "expense-classification.csv")
    summary = summarize_results(results)
    (work / "reports" / "accountant-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    import_map = {
        "supported_import_style": "generic_csv",
        "common_targets": ["Hashavshevet", "Rivhit", "Priority", "iCount", "Green Invoice", "Excel for accountant review"],
        "field_mapping": {
            "date": "אסמכתא/תאריך",
            "vendor": "שם ספק",
            "account_code": "כרטיס/קוד חשבון",
            "amount_ils": "סכום ברוטו",
            "reclaimable_vat_ils": "מס תשומות לניכוי",
            "deductible_amount_ils": "הוצאה מוכרת",
            "review_flags": "בדיקות לפני קליטה",
        },
    }
    (work / "exports" / "import-mapping.json").write_text(json.dumps(import_map, ensure_ascii=False, indent=2), encoding="utf-8")
    (work / "README-accountant.md").write_text(
        "# Expense package for accountant\n\n"
        "Review `exports/expense-classification.csv`, verify rows with `review_flags`, then import using the target software CSV mapping.\n"
        "Keep original invoices outside this package or attach them in the `source` directory when available.\n",
        encoding="utf-8",
    )
    for source in source_files:
        src = Path(source)
        if src.exists() and src.is_file():
            shutil.copy2(src, work / "source" / src.name)
    manifest_lines = []
    for file in sorted(work.rglob("*")):
        if file.is_file():
            manifest_lines.append(f"{_hash_file(file)}  {file.relative_to(work)}")
    (work / "reports" / "sha256-manifest.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    zip_path = base / f"{package_name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for file in sorted(work.rglob("*")):
            if file.is_file():
                z.write(file, file.relative_to(work.parent))
    return zip_path


def classify_csv_file(input_csv: str | Path, output_csv: str | Path, config: BusinessConfig | None = None) -> list[ExpenseResult]:
    """Read a CSV, classify rows, and write a result CSV."""
    expenses = read_expenses_csv(input_csv)
    results = classify_many(expenses, config)
    write_results_csv(results, output_csv)
    return results




def make_expense_id(expense: ExpenseInput) -> str:
    """Create a stable short identifier from normalized expense fields."""
    payload = {
        "date": expense.date.isoformat(),
        "vendor": expense.vendor.strip().lower(),
        "amount": _decimal_to_str(expense.amount),
        "currency": expense.currency.upper(),
        "receipt_number": expense.receipt_number or "",
        "description": expense.description.strip().lower(),
    }
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return f"exp_{digest[:16]}"


def expense_to_record(expense: ExpenseInput) -> dict[str, Any]:
    """Serialize an expense into a JSON-ready record with a stable id."""
    return {
        "id": make_expense_id(expense),
        "date": expense.date.strftime("%d/%m/%Y"),
        "vendor": expense.vendor,
        "amount": _decimal_to_str(expense.amount),
        "currency": expense.currency,
        "description": expense.description,
        "amount_includes_vat": expense.amount_includes_vat,
        "receipt_number": expense.receipt_number or "",
        "document_type": expense.document_type or "",
        "fx_rate_to_ils": _decimal_to_str(expense.fx_rate_to_ils),
        "tags": list(expense.tags),
        "metadata": dict(expense.metadata),
    }


def expense_from_record(record: Mapping[str, Any]) -> ExpenseInput:
    """Deserialize a record produced through expense_to_record."""
    tags_value = record.get("tags") or ()
    return ExpenseInput(
        date=parse_date(record.get("date")),
        vendor=str(record.get("vendor", "")).strip(),
        amount=parse_decimal(record.get("amount")),
        description=str(record.get("description", "")).strip(),
        currency=str(record.get("currency", DEFAULT_CURRENCY)).upper(),
        amount_includes_vat=bool(record.get("amount_includes_vat", True)),
        receipt_number=str(record.get("receipt_number") or "") or None,
        document_type=str(record.get("document_type") or "") or None,
        fx_rate_to_ils=parse_decimal(record.get("fx_rate_to_ils", "1")),
        tags=tuple(str(t) for t in tags_value),
        metadata=dict(record.get("metadata") or {}),
    )


def create_expense_record(expense: ExpenseInput, output_path: str | Path | None = None) -> dict[str, Any]:
    """Return a JSON record for an expense and optionally write it to disk."""
    record = expense_to_record(expense)
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def classify_expense_record(
    record: Mapping[str, Any],
    expected_id: str | None = None,
    config: BusinessConfig | None = None,
) -> ExpenseResult:
    """Classify an expense record and optionally validate the caller-supplied id."""
    expense = expense_from_record(record)
    actual_id = make_expense_id(expense)
    supplied_id = expected_id or str(record.get("id", "")) or None
    if supplied_id and supplied_id != actual_id:
        raise ValueError(f"expense id mismatch: expected {supplied_id}, calculated {actual_id}")
    return classify_expense(expense, config)


class ExpenseManagerClient:
    """Small typed facade for sync and async expense workflows."""

    def __init__(self, config: BusinessConfig | None = None) -> None:
        self.config = config or BusinessConfig()

    def create_record(self, expense: ExpenseInput, output_path: str | Path | None = None) -> dict[str, Any]:
        return create_expense_record(expense, output_path)

    def classify(self, expense: ExpenseInput) -> ExpenseResult:
        return classify_expense(expense, self.config)

    def classify_record(self, record: Mapping[str, Any], expected_id: str | None = None) -> ExpenseResult:
        return classify_expense_record(record, expected_id, self.config)

    def classify_many(self, expenses: Iterable[ExpenseInput]) -> list[ExpenseResult]:
        return classify_many(expenses, self.config)

    async def classify_async(self, expense: ExpenseInput) -> ExpenseResult:
        return await async_classify_expense(expense, self.config)

    async def classify_many_async(self, expenses: Iterable[ExpenseInput]) -> list[ExpenseResult]:
        return await async_classify_many(expenses, self.config)

    def read_csv(self, path: str | Path, encoding: str = "utf-8-sig") -> list[ExpenseInput]:
        return read_expenses_csv(path, encoding)

    def write_csv(self, results: Sequence[ExpenseResult], path: str | Path) -> Path:
        return write_results_csv(results, path)

    def summarize(self, results: Sequence[ExpenseResult]) -> dict[str, Any]:
        return summarize_results(results)

    def export_package(
        self,
        results: Sequence[ExpenseResult],
        output_dir: str | Path,
        package_name: str = "accountant-expense-package",
        source_files: Sequence[str | Path] = (),
    ) -> Path:
        return export_accountant_package(results, output_dir, package_name, source_files)


__all__ = [
    "BusinessConfig",
    "DEFAULT_CURRENCY",
    "DEFAULT_EQUIPMENT_IMMEDIATE_EXPENSE_LIMIT_ILS",
    "DEFAULT_GIFT_CAP_ILS",
    "DEFAULT_HOME_OFFICE_PERCENT",
    "EntityType",
    "ExpenseInput",
    "ExpenseManagerClient",
    "ExpenseResult",
    "ReviewFlag",
    "ReviewSeverity",
    "Rule",
    "VAT_RATE",
    "async_classify_expense",
    "async_classify_many",
    "classify_csv_file",
    "classify_expense",
    "classify_expense_record",
    "classify_many",
    "create_expense_record",
    "expense_from_record",
    "expense_from_row",
    "expense_to_record",
    "export_accountant_package",
    "make_expense_id",
    "parse_date",
    "parse_decimal",
    "q2",
    "read_expenses_csv",
    "summarize_results",
    "write_results_csv",
]
