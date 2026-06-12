from __future__ import annotations

import hashlib
import asyncio, csv, dataclasses, json, re, unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Mapping, Optional, Sequence, Tuple

Direction = Literal["credit", "debit"]
Deductibility = Literal["likely", "partial", "unlikely", "review"]

class TransactionCategorizerError(ValueError):
    pass

@dataclass(frozen=True)
class RawTransaction:
    date: date
    description: str
    amount: Decimal
    currency: str = "ILS"
    balance: Optional[Decimal] = None
    reference: Optional[str] = None
    bank: Optional[str] = None
    source_file: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class CategorizationRule:
    id: str
    category: str
    subcategory: str
    patterns: Sequence[str]
    direction: Optional[Direction] = None
    vat_relevant: bool = False
    tax_deductibility: Deductibility = "review"
    confidence: float = 0.75
    priority: int = 100
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "CategorizationRule":
        patterns = data.get("patterns")
        if not isinstance(patterns, list) or not all(isinstance(p, str) for p in patterns):
            raise TransactionCategorizerError("Rule must include patterns as a list of strings.")
        direction = data.get("direction")
        if direction not in (None, "credit", "debit"):
            raise TransactionCategorizerError("Rule direction must be credit, debit, or null.")
        return cls(
            id=str(data["id"]),
            category=str(data["category"]),
            subcategory=str(data.get("subcategory", data["category"])),
            patterns=patterns,
            direction=direction,
            vat_relevant=bool(data.get("vat_relevant", False)),
            tax_deductibility=str(data.get("tax_deductibility", "review")),  # type: ignore[arg-type]
            confidence=float(data.get("confidence", 0.75)),
            priority=int(data.get("priority", 100)),
            amount_min=Decimal(str(data["amount_min"])) if data.get("amount_min") is not None else None,
            amount_max=Decimal(str(data["amount_max"])) if data.get("amount_max") is not None else None,
        )

@dataclass(frozen=True)
class CategorizedTransaction:
    date: date
    description: str
    normalized_description: str
    amount: Decimal
    direction: Direction
    category: str
    subcategory: str
    vat_relevant: bool
    tax_deductibility: Deductibility
    confidence: float
    rule_id: str
    flags: Tuple[str, ...] = ()
    currency: str = "ILS"
    balance: Optional[Decimal] = None
    reference: Optional[str] = None
    bank: Optional[str] = None
    source_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "description": self.description,
            "normalized_description": self.normalized_description,
            "amount": format_decimal(self.amount),
            "direction": self.direction,
            "category": self.category,
            "subcategory": self.subcategory,
            "vat_relevant": self.vat_relevant,
            "tax_deductibility": self.tax_deductibility,
            "confidence": round(self.confidence, 4),
            "rule_id": self.rule_id,
            "flags": ";".join(self.flags),
            "currency": self.currency,
            "balance": format_decimal(self.balance) if self.balance is not None else "",
            "reference": self.reference or "",
            "bank": self.bank or "",
            "source_file": self.source_file or "",
        }

def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "")
    text = text.replace("\u200f", " ").replace("\u200e", " ").replace("״", '"').replace("׳", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip().casefold()

def format_decimal(value: Optional[Decimal]) -> str:
    if value is None:
        return ""
    return format(value.quantize(Decimal("0.01")), "f")

def parse_israeli_amount(value: Any) -> Decimal:
    if value is None:
        raise TransactionCategorizerError("missing amount")
    text = str(value).strip()
    if not text:
        raise TransactionCategorizerError("missing amount")
    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]
    if text.endswith("-"):
        negative = True
        text = text[:-1]
    text = text.replace("₪", "").replace("NIS", "").replace("ILS", "").replace("\u200f", "").replace(" ", "")
    if text.startswith("-"):
        negative = True
        text = text[1:]
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".") if text.rfind(",") > text.rfind(".") else text.replace(",", "")
    elif "," in text:
        parts = text.split(",")
        text = "".join(parts) if len(parts[-1]) == 3 and len(parts) > 1 else text.replace(".", "").replace(",", ".")
    try:
        amount = Decimal(text)
    except InvalidOperation as exc:
        raise TransactionCategorizerError(f"bad amount format: {value!r}") from exc
    return -amount if negative else amount

def parse_israeli_date(value: Any) -> date:
    if value is None or not str(value).strip():
        raise TransactionCategorizerError("missing date")
    text = str(value).strip()
    for fmt in ("%d-%m-%Y","%d/%m/%Y","%Y-%m-%d","%Y/%m/%d","%d.%m.%Y","%d-%m-%y","%d/%m/%y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise TransactionCategorizerError(f"bad date format: {value!r}")

def detect_bank(text: str) -> Optional[str]:
    normalized = normalize_text(text)
    candidates = {
        "Bank Hapoalim": ["הפועלים", "poalim", "hapoalim", "bank code 12", "בנק 12"],
        "Bank Leumi": ["לאומי", "leumi", "bank code 10", "בנק 10"],
        "Discount Bank": ["דיסקונט", "discount", "bank code 11", "בנק 11"],
        "Mizrahi-Tefahot": ["מזרחי", "טפחות", "mizrahi", "tefahot", "bank code 20"],
        "Mercantile": ["מרכנתיל", "mercantile"],
        "Bank Yahav": ["יהב", "yahav"],
    }
    for bank, patterns in candidates.items():
        if any(p in normalized for p in patterns):
            return bank
    return None

DEFAULT_RULES: Tuple[CategorizationRule, ...] = (
    CategorizationRule("tax_vat", "Taxes & Government", "VAT", [r'מע"?מ', "מס ערך מוסף", "vat"], "debit", True, "review", 0.97, 240),
    CategorizationRule("tax_income_tax", "Taxes & Government", "Income tax", ["מס הכנסה", "מקדמות מס"], "debit", False, "review", 0.96, 235),
    CategorizationRule("tax_national_insurance", "Taxes & Government", "National Insurance", ["ביטוח לאומי"], "debit", False, "review", 0.96, 235),
    CategorizationRule("tax_municipal", "Taxes & Government", "Municipal tax", ["ארנונה", "עיריית", "רשות מקומית"], "debit", True, "review", 0.91, 220),
    CategorizationRule("bank_fees", "Bank Fees & Interest", "Bank fees", ["עמל", "דמי ניהול", "מסלול עמלות", "bank fee", "account fee"], "debit", True, "likely", 0.92, 210),
    CategorizationRule("bank_interest", "Bank Fees & Interest", "Interest", ["ריבית חובה", "overdraft interest", "ריבית"], "debit", False, "review", 0.88, 205),
    CategorizationRule("loan_repayment", "Loans & Financing", "Loan repayment", ["החזר הלוואה", "הלוואה", "loan repayment", "mortgage", "משכנתא"], "debit", False, "review", 0.88, 200),
    CategorizationRule("credit_card_settlement", "Credit Card Settlement", "Card settlement", ["ישראכרט", "isracard", "max", "cal", "כרטיס אשראי"], "debit", False, "review", 0.84, 198),
    CategorizationRule("income_salary", "Income", "Salary", ["משכורת", "salary"], "credit", False, "review", 0.90, 195),
    CategorizationRule("income_card_settlement", "Income", "Card settlement", ["זיכוי ישראכרט", "זיכוי max", "זיכוי cal", "card settlement credit"], "credit", True, "review", 0.91, 190),
    CategorizationRule("income_client_transfer", "Income", "Client payment", ["העברה מלקוח", "תשלום לקוח", "חשבונית", "תקבול", "client payment", "invoice payment"], "credit", True, "review", 0.87, 185),
    CategorizationRule("software_cloud", "Software & Cloud", "Software subscription", ["google cloud", "aws", "amazon web services", "microsoft", "azure", "openai", "adobe", "zoom", "wix", "shopify", "github", "notion", "slack"], "debit", True, "likely", 0.88, 170),
    CategorizationRule("marketing_ads", "Marketing & Advertising", "Digital advertising", ["google ads", "facebook ads", "meta ads", "taboola", "outbrain", "טאבולה", "פייסבוק"], "debit", True, "likely", 0.89, 168),
    CategorizationRule("communications", "Communications", "Phone and internet", ["בזק", "bezeq", "סלקום", "cellcom", "פרטנר", "partner", "פלאפון", "pelephone", "hot", "הוט", "012"], "debit", True, "partial", 0.84, 160),
    CategorizationRule("travel_fuel", "Travel & Fuel", "Fuel and vehicle", ["פז", "paz", "סונול", "sonol", "דלק", "delek", "דור אלון", "טן", "חניה", "parking"], "debit", True, "partial", 0.82, 150),
    CategorizationRule("food_meals", "Food & Meals", "Meals", ["wolt", "תן ביס", "tenbis", "סיבוס", "cibus", "מסעד", "קפה", "restaurant"], "debit", True, "review", 0.79, 145),
    CategorizationRule("personal_groceries", "Personal/Review", "Groceries and household", ["שופרסל", "רמי לוי", "יוחננוף", "ויקטורי", "סופר", "supermarket", "סופר-פארם", "פארם"], "debit", False, "unlikely", 0.82, 142),
    CategorizationRule("rent_facilities", "Rent & Facilities", "Rent", ["שכירות", "דמי שכירות", "office lease", "חלל עבודה", "wework", "workspace"], "debit", True, "likely", 0.90, 155),
    CategorizationRule("insurance", "Insurance", "Insurance", ["ביטוח", "הראל", "מגדל", "מנורה", "כלל", "insurance"], "debit", True, "review", 0.82, 130),
    CategorizationRule("payroll", "Payroll & Benefits", "Payroll", ["שכר", "ניכויים", "פנסיה", "קופת גמל", "קרן השתלמות", "payroll"], "debit", False, "likely", 0.87, 152),
    CategorizationRule("professional_services", "Professional Services", "Accounting/legal/consulting", ['רואה חשבון', 'רו"ח', 'עו"ד', "עורך דין", "יועץ", "consultant", "accountant", "lawyer"], "debit", True, "likely", 0.86, 148),
    CategorizationRule("equipment_office", "Equipment & Office", "Equipment and supplies", ["ksp", "ivory", "אייבורי", "מחשב", "ציוד משרדי", "office depot", "printer"], "debit", True, "review", 0.84, 144),
    CategorizationRule("cash_withdrawal", "Cash Withdrawals", "ATM withdrawal", ["משיכת מזומן", "כספומט", "atm withdrawal"], "debit", False, "review", 0.93, 180),
    CategorizationRule("wallets", "Transfers & Wallets", "Digital wallet or transfer", ["bit", "paybox", "פייבוקס", "ביט", "העברה"], None, False, "review", 0.62, 70),
)

class BankTransactionCategorizer:
    COLUMN_ALIASES: Mapping[str, Tuple[str, ...]] = {
        "date": ("date", "bookingdate", "transactiondate", "valuedate", "תאריך", "תאריך עסקה", "תאריך ערך"),
        "description": ("description", "details", "transactioninformation", "merchant", "תיאור", "פרטים", "מהות פעולה", "שם בית עסק"),
        "amount": ("amount", "transactionamount", "סכום", "סכום עסקה"),
        "debit": ("debit", "debitamount", "withdrawal", "חובה", "סכום חובה", "משיכה"),
        "credit": ("credit", "creditamount", "deposit", "זכות", "סכום זכות", "הפקדה"),
        "balance": ("balance", "runningbalance", "יתרה", "יתרה לאחר פעולה"),
        "reference": ("reference", "transactionid", "אסמכתא", "מספר פעולה", "מזהה פעולה"),
        "bank": ("bank", "institution", "בנק"),
        "currency": ("currency", "מטבע"),
    }

    def __init__(self, rules: Optional[Sequence[CategorizationRule]] = None) -> None:
        self.rules = tuple(sorted(rules or DEFAULT_RULES, key=lambda r: r.priority, reverse=True))

    @classmethod
    def from_rule_file(cls, path: str | Path) -> "BankTransactionCategorizer":
        return cls(tuple(load_rules(path)) + DEFAULT_RULES)

    def parse_csv(self, path: str | Path, bank: Optional[str] = None) -> List[RawTransaction]:
        file_path = Path(path)
        text = read_text_with_fallback(file_path)
        if not text.strip():
            raise TransactionCategorizerError("empty-file")
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
        reader = csv.DictReader(text.splitlines(), dialect=dialect)
        if not reader.fieldnames:
            raise TransactionCategorizerError("missing-header")
        field_map = self._map_headers(reader.fieldnames)
        rows: List[RawTransaction] = []
        inferred_bank = bank or detect_bank(" ".join(reader.fieldnames))
        for row_number, row in enumerate(reader, start=2):
            if not any(str(v or "").strip() for v in row.values()):
                continue
            try:
                rows.append(self._parse_row(row, field_map, file_path, inferred_bank))
            except TransactionCategorizerError as exc:
                raise TransactionCategorizerError(f"row {row_number}: {exc}") from exc
        return rows

    def _map_headers(self, headers: Sequence[str]) -> Dict[str, str]:
        normalized_headers = {normalize_text(h): h for h in headers if h is not None}
        result: Dict[str, str] = {}
        for canonical, aliases in self.COLUMN_ALIASES.items():
            for alias in aliases:
                key = normalize_text(alias)
                if key in normalized_headers:
                    result[canonical] = normalized_headers[key]
                    break
        return result

    def _value(self, row: Mapping[str, Any], field_map: Mapping[str, str], canonical: str) -> str:
        original = field_map.get(canonical)
        return str(row.get(original, "")).strip() if original else ""

    def _parse_row(self, row: Mapping[str, Any], field_map: Mapping[str, str], path: Path, bank: Optional[str]) -> RawTransaction:
        raw_date = self._value(row, field_map, "date")
        raw_description = self._value(row, field_map, "description")
        if not raw_date:
            raise TransactionCategorizerError("missing-date")
        if not raw_description:
            raise TransactionCategorizerError("missing-description")
        raw_amount = self._value(row, field_map, "amount")
        debit = self._value(row, field_map, "debit")
        credit = self._value(row, field_map, "credit")
        if raw_amount:
            amount = parse_israeli_amount(raw_amount)
        elif debit or credit:
            amount = parse_israeli_amount(credit) if credit else -abs(parse_israeli_amount(debit))
        else:
            raise TransactionCategorizerError("missing-amount")
        balance_value = self._value(row, field_map, "balance")
        return RawTransaction(
            date=parse_israeli_date(raw_date),
            description=raw_description,
            amount=amount,
            currency=self._value(row, field_map, "currency") or "ILS",
            balance=parse_israeli_amount(balance_value) if balance_value else None,
            reference=self._value(row, field_map, "reference") or None,
            bank=self._value(row, field_map, "bank") or bank or detect_bank(raw_description),
            source_file=path.name,
            raw=dict(row),
        )

    def categorize(self, tx: RawTransaction) -> CategorizedTransaction:
        normalized = normalize_text(tx.description)
        direction: Direction = "credit" if tx.amount >= 0 else "debit"
        best_rule: Optional[CategorizationRule] = None
        for rule in self.rules:
            if rule.direction and rule.direction != direction:
                continue
            abs_amount = abs(tx.amount)
            if rule.amount_min is not None and abs_amount < rule.amount_min:
                continue
            if rule.amount_max is not None and abs_amount > rule.amount_max:
                continue
            if any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in rule.patterns):
                best_rule = rule
                break
        flags: List[str] = []
        if best_rule is None:
            category = "Uncategorized Income" if direction == "credit" else "Uncategorized Expense"
            subcategory = "Needs review"; vat_relevant = False; tax_deductibility: Deductibility = "review"; confidence = 0.25; rule_id = "fallback_uncategorized"
            flags.append("needs-review")
        else:
            category = best_rule.category; subcategory = best_rule.subcategory; vat_relevant = best_rule.vat_relevant
            tax_deductibility = best_rule.tax_deductibility; confidence = best_rule.confidence; rule_id = best_rule.id
            if category in {"Personal/Review","Transfers & Wallets","Credit Card Settlement","Loans & Financing"}:
                flags.append("needs-review")
            if category == "Income" and ("bit" in normalized or "paybox" in normalized or "פייבוקס" in normalized or "ביט" in normalized):
                flags.append("confirm-business-income")
            if direction == "credit" and category in {"Transfers & Wallets","Uncategorized Income"}:
                flags.append("confirm-business-income")
            if tax_deductibility in {"partial","review"} and direction == "debit" and "needs-review" not in flags:
                flags.append("needs-review")
        return CategorizedTransaction(tx.date, tx.description, normalized, tx.amount, direction, category, subcategory, vat_relevant, tax_deductibility, confidence, rule_id, tuple(flags), tx.currency, tx.balance, tx.reference, tx.bank, tx.source_file)

    def categorize_transactions(self, transactions: Iterable[RawTransaction]) -> List[CategorizedTransaction]:
        categorized = [self.categorize(tx) for tx in transactions]
        seen: Dict[Tuple[str, str, str], int] = {}
        out: List[CategorizedTransaction] = []
        for item in categorized:
            signature = (item.date.isoformat(), item.normalized_description, format_decimal(item.amount))
            if seen.get(signature, 0):
                item = dataclasses.replace(item, flags=tuple(dict.fromkeys(item.flags + ("possible-duplicate",))))
            seen[signature] = seen.get(signature, 0) + 1
            out.append(item)
        return out

    def categorize_file(self, input_path: str | Path, output_path: Optional[str | Path] = None, output_format: Literal["csv","json"] = "csv") -> Dict[str, Any]:
        transactions = self.parse_csv(input_path)
        categorized = self.categorize_transactions(transactions)
        summary = summarize(categorized)
        if output_path:
            export_transactions(categorized, output_path, output_format)
        return {"transactions": categorized, "summary": summary, "count": len(categorized)}

    async def acategorize_file(self, input_path: str | Path, output_path: Optional[str | Path] = None, output_format: Literal["csv","json"] = "csv") -> Dict[str, Any]:
        return await asyncio.to_thread(self.categorize_file, input_path, output_path, output_format)

def read_text_with_fallback(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1255"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")

def load_rules(path: str | Path) -> List[CategorizationRule]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("rules", [])
    if not isinstance(data, list):
        raise TransactionCategorizerError("Rules file must contain a list or an object with a rules list.")
    return [CategorizationRule.from_mapping(item) for item in data]

def export_transactions(transactions: Sequence[CategorizedTransaction], output_path: str | Path, output_format: Literal["csv","json"] = "csv") -> None:
    path = Path(output_path); path.parent.mkdir(parents=True, exist_ok=True)
    rows = [tx.to_dict() for tx in transactions]
    if output_format == "json" or path.suffix.lower() == ".json":
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"); return
    if not rows:
        path.write_text("", encoding="utf-8"); return
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)

def summarize(transactions: Sequence[CategorizedTransaction]) -> Dict[str, Any]:
    categories: Dict[str, Dict[str, Any]] = {}; review_count = 0; total_credit = Decimal("0"); total_debit = Decimal("0")
    for tx in transactions:
        bucket = categories.setdefault(tx.category, {"count": 0, "total": Decimal("0")})
        bucket["count"] += 1; bucket["total"] += tx.amount
        if tx.amount >= 0: total_credit += tx.amount
        else: total_debit += tx.amount
        if tx.flags: review_count += 1
    return {
        "count": len(transactions),
        "total_credit": format_decimal(total_credit),
        "total_debit": format_decimal(total_debit),
        "net": format_decimal(total_credit + total_debit),
        "review_count": review_count,
        "categories": {k: {"count": v["count"], "total": format_decimal(v["total"])} for k, v in sorted(categories.items())},
    }

def make_sample_csv(path: str | Path) -> Path:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ["תאריך","תיאור","חובה","זכות","יתרה","אסמכתא"],
        ["02/01/2026",'מע"מ תקופתי',"1200.00","","18450.20","99123"],
        ["03/01/2026","העברה מלקוח - חשבונית 1042","","3500.00","21950.20","99124"],
        ["04/01/2026","עמלת מסלול עסקים","29.90","","21920.30","99125"],
        ["05/01/2026","ADOBE CREATIVE CLOUD","88.00","","21832.30","99126"],
        ["06/01/2026","BIT העברה","","250.00","22082.30","99127"],
    ]
    with target.open("w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh).writerows(rows)
    return target

def validate_file(path: str | Path) -> Dict[str, Any]:
    categorizer = BankTransactionCategorizer()
    transactions = categorizer.parse_csv(path)
    return {
        "valid": True,
        "count": len(transactions),
        "banks": sorted({tx.bank for tx in transactions if tx.bank}),
        "date_min": min((tx.date for tx in transactions), default=None).isoformat() if transactions else None,
        "date_max": max((tx.date for tx in transactions), default=None).isoformat() if transactions else None,
    }



def source_file_id(path: str | Path) -> str:
    """Return a stable local id for a statement file."""
    file_path = Path(path)
    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()[:16]
    return f"stmt_{digest}"


def registry_path(environment: str = "sandbox", base_dir: Optional[str | Path] = None) -> Path:
    """Return the local statement-id registry path for an environment."""
    if environment not in {"sandbox", "production"}:
        raise TransactionCategorizerError("environment must be sandbox or production")
    base = Path(base_dir) if base_dir else Path(".bank_transaction_categorizer")
    return base / environment / "registry.json"


def register_input(path: str | Path, environment: str = "sandbox", base_dir: Optional[str | Path] = None) -> Dict[str, str]:
    """Register a statement file and return its id, path, and environment."""
    file_path = Path(path)
    identifier = source_file_id(file_path)
    reg_path = registry_path(environment, base_dir)
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    registry: Dict[str, str] = {}
    if reg_path.exists():
        registry = json.loads(reg_path.read_text(encoding="utf-8"))
    registry[identifier] = str(file_path.resolve())
    reg_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"id": identifier, "path": str(file_path), "environment": environment}


def resolve_input_id(identifier: str, environment: str = "sandbox", base_dir: Optional[str | Path] = None) -> Path:
    """Resolve a previously registered input id to a file path."""
    reg_path = registry_path(environment, base_dir)
    if not reg_path.exists():
        raise TransactionCategorizerError(f"No registry found for environment {environment}.")
    registry = json.loads(reg_path.read_text(encoding="utf-8"))
    if identifier not in registry:
        raise TransactionCategorizerError(f"Unknown input id: {identifier}")
    return Path(registry[identifier])


def create_sample_statement(
    output_path: str | Path,
    environment: str = "sandbox",
    base_dir: Optional[str | Path] = None,
) -> Dict[str, str]:
    """Create a sample statement and register it for chained CLI use."""
    path = make_sample_csv(output_path)
    return register_input(path, environment, base_dir)


__all__ = [
    "BankTransactionCategorizer",
    "CategorizationRule",
    "CategorizedTransaction",
    "DEFAULT_RULES",
    "RawTransaction",
    "TransactionCategorizerError",
    "create_sample_statement",
    "detect_bank",
    "export_transactions",
    "format_decimal",
    "load_rules",
    "make_sample_csv",
    "normalize_text",
    "parse_israeli_amount",
    "parse_israeli_date",
    "register_input",
    "resolve_input_id",
    "source_file_id",
    "summarize",
    "validate_file",
]
