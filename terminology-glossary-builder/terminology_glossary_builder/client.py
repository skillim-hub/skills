"""Offline-first English-Hebrew glossary builder with Israeli authoritative citations."""
from __future__ import annotations

import asyncio
import csv
import hashlib
import io
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Sequence

Audience = Literal["small_business", "freelancer", "consumer", "general"]
Environment = Literal["sandbox", "production"]
LanguageMode = Literal["bilingual", "english", "hebrew"]
OutputFormat = Literal["markdown", "json", "csv"]

HEBREW_RE = re.compile(r"[\u0590-\u05FF]")
NIKUD_RE = re.compile(r"[\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7]")
SPLIT_RE = re.compile(r"[\n,;|/]+")
SHEKEL_RE = re.compile(r"₪\s?\d|\d\s?₪")
DATE_DDMMYYYY_RE = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")


@dataclass(frozen=True)
class CitationSource:
    """Authoritative Israeli source used to support glossary entries."""

    key: str
    title_en: str
    title_he: str
    authority: str
    url: str
    source_type: str
    jurisdiction: str = "Israel"
    update_frequency: str = "Check before publication"
    access_notes: str = "Open public source unless the source states otherwise."

    def citation(self, language: Literal["en", "he"] = "en") -> str:
        title = self.title_he if language == "he" else self.title_en
        return f"{title} — {self.authority}: {self.url}"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class TermTemplate:
    """Reusable definition and translation template for an industry term."""

    canonical_en: str
    canonical_he: str
    definition_en: str
    definition_he: str
    industries: tuple[str, ...]
    source_keys: tuple[str, ...]
    usage_note_en: str = ""
    usage_note_he: str = ""
    warning_en: str = ""
    warning_he: str = ""


@dataclass
class GlossaryEntry:
    """Single bilingual glossary entry."""

    term_en: str
    term_he: str
    definition_en: str
    definition_he: str
    industry: str
    sources: list[CitationSource] = field(default_factory=list)
    usage_note_en: str = ""
    usage_note_he: str = ""
    warning_en: str = ""
    warning_he: str = ""
    original_term: str = ""

    @property
    def source_keys(self) -> list[str]:
        return [source.key for source in self.sources]

    def to_dict(self) -> dict[str, Any]:
        data = {
            "term_en": self.term_en,
            "term_he": self.term_he,
            "definition_en": self.definition_en,
            "definition_he": self.definition_he,
            "industry": self.industry,
            "sources": [source.to_dict() for source in self.sources],
            "source_keys": self.source_keys,
            "usage_note_en": self.usage_note_en,
            "usage_note_he": self.usage_note_he,
            "warning_en": self.warning_en,
            "warning_he": self.warning_he,
            "original_term": self.original_term,
        }
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GlossaryEntry":
        sources = [CitationSource(**source) for source in data.get("sources", [])]
        return cls(
            term_en=str(data.get("term_en", "")),
            term_he=str(data.get("term_he", "")),
            definition_en=str(data.get("definition_en", "")),
            definition_he=str(data.get("definition_he", "")),
            industry=str(data.get("industry", "general")),
            sources=sources,
            usage_note_en=str(data.get("usage_note_en", "")),
            usage_note_he=str(data.get("usage_note_he", "")),
            warning_en=str(data.get("warning_en", "")),
            warning_he=str(data.get("warning_he", "")),
            original_term=str(data.get("original_term", "")),
        )


@dataclass
class GlossaryResult:
    """Complete glossary build result."""

    id: str
    title: str
    industry: str
    audience: Audience
    language_mode: LanguageMode
    environment: Environment
    entries: list[GlossaryEntry]
    source_registry_version: str = "2026-06-03"
    created_at: str = field(default_factory=lambda: date.today().strftime("%d/%m/%Y"))
    warnings: list[str] = field(default_factory=list)

    @property
    def entry_count(self) -> int:
        return len(self.entries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "industry": self.industry,
            "audience": self.audience,
            "language_mode": self.language_mode,
            "environment": self.environment,
            "source_registry_version": self.source_registry_version,
            "created_at": self.created_at,
            "warnings": list(self.warnings),
            "entry_count": self.entry_count,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GlossaryResult":
        return cls(
            id=str(data.get("id", "")),
            title=str(data.get("title", "English-Hebrew Terminology Glossary")),
            industry=str(data.get("industry", "general")),
            audience=str(data.get("audience", "general")),  # type: ignore[arg-type]
            language_mode=str(data.get("language_mode", "bilingual")),  # type: ignore[arg-type]
            environment=str(data.get("environment", "sandbox")),  # type: ignore[arg-type]
            entries=[GlossaryEntry.from_dict(entry) for entry in data.get("entries", [])],
            source_registry_version=str(data.get("source_registry_version", "2026-06-03")),
            created_at=str(data.get("created_at", date.today().strftime("%d/%m/%Y"))),
            warnings=[str(item) for item in data.get("warnings", [])],
        )


SOURCE_REGISTRY: dict[str, CitationSource] = {
    "govil": CitationSource("govil", "GOV.IL service and rights portal", "פורטל השירותים והזכויות GOV.IL", "Government of Israel", "https://www.gov.il/", "official_portal"),
    "data_gov_il": CitationSource("data_gov_il", "Israel Open Data API", "מאגר הנתונים הממשלתי הפתוחים", "Government ICT Authority", "https://data.gov.il/api/3/action/package_search", "open_data_api"),
    "tax_authority": CitationSource("tax_authority", "Israel Tax Authority", "רשות המסים בישראל", "Israel Tax Authority", "https://www.gov.il/he/departments/israel_tax_authority/govil-landing-page", "tax_authority"),
    "btl": CitationSource("btl", "National Insurance Institute", "המוסד לביטוח לאומי", "National Insurance Institute of Israel", "https://www.btl.gov.il/", "social_security_authority"),
    "labor": CitationSource("labor", "Ministry of Labor", "משרד העבודה", "Government of Israel", "https://www.gov.il/he/departments/ministry_of_labor/govil-landing-page", "labor_authority"),
    "finance_ministry": CitationSource("finance_ministry", "Ministry of Finance", "משרד האוצר", "Government of Israel", "https://www.gov.il/he/departments/ministry_of_finance", "finance_ministry"),
    "consumer_protection": CitationSource("consumer_protection", "Consumer Protection and Fair Trade Authority", "הרשות להגנת הצרכן ולסחר הוגן", "Government of Israel", "https://www.gov.il/he/departments/consumer_protection_and_fair_trade_authority/govil-landing-page", "consumer_authority"),
    "privacy": CitationSource("privacy", "Privacy Protection Authority", "הרשות להגנת הפרטיות", "Government of Israel", "https://www.gov.il/he/departments/the_privacy_protection_authority/govil-landing-page", "privacy_authority"),
    "corporations": CitationSource("corporations", "Corporations Authority", "רשות התאגידים", "Government of Israel", "https://www.gov.il/he/departments/corporations_authority/govil-landing-page", "corporate_registry"),
    "standards": CitationSource("standards", "Standards Institution of Israel", "מכון התקנים הישראלי", "Standards Institution of Israel", "https://www.sii.org.il/", "standards_body"),
    "boi": CitationSource("boi", "Bank of Israel", "בנק ישראל", "Bank of Israel", "https://www.boi.org.il/", "central_bank"),
    "isa": CitationSource("isa", "Israel Securities Authority", "רשות ניירות ערך", "Israel Securities Authority", "https://www.isa.gov.il/", "securities_regulator"),
    "accessibility": CitationSource("accessibility", "Commission for Equal Rights of Persons with Disabilities", "נציבות שוויון זכויות לאנשים עם מוגבלות", "Ministry of Justice", "https://www.gov.il/he/departments/commission_for_equal_rights_of_persons_with_disabilities/govil-landing-page", "accessibility_authority"),
}

TERM_LIBRARY: dict[str, TermTemplate] = {
    "value added tax": TermTemplate("Value Added Tax (VAT)", "מס ערך מוסף (מע\"מ)", "An indirect tax charged on most supplies of goods and services in Israel, collected by a business and reported to the Tax Authority.", "מס עקיף המוטל על רוב העסקאות בישראל; העסק גובה אותו מהלקוח ומדווח עליו לרשות המסים.", ("tax", "accounting", "retail", "freelance"), ("tax_authority",), "The standard Israeli VAT rate is 18% from 01/01/2025 and was double-confirmed on 03/06/2026; recheck before publishing rates.", "שיעור המע\"מ הכללי בישראל הוא 18% מיום 01/01/2025 ואומת שוב ביום 03/06/2026; יש לבדוק שוב לפני פרסום שיעורים.", "Rates and reporting rules are date-sensitive.", "השיעורים וכללי הדיווח תלויי תאריך."),
    "withholding tax": TermTemplate("Withholding tax", "ניכוי מס במקור", "Tax deducted by the payer from a payment and transferred to the Tax Authority for the payee.", "מס שהמשלם מנכה מתוך תשלום ומעביר לרשות המסים בשם מקבל התשלום.", ("tax", "accounting", "freelance"), ("tax_authority",), "Ask for a valid withholding tax certificate before setting a rate.", "יש לבקש אישור ניכוי מס במקור בתוקף לפני קביעת שיעור."),
    "tax invoice": TermTemplate("Tax invoice", "חשבונית מס", "A document issued by a VAT-registered business to document a taxable transaction and VAT component.", "מסמך שעוסק מורשה מוציא לתיעוד עסקה חייבת במע\"מ ולפירוט רכיב המע\"מ.", ("tax", "accounting", "retail", "freelance"), ("tax_authority",), "Do not treat a receipt as a tax invoice unless the document states both functions.", "אין להתייחס לקבלה כחשבונית מס אלא אם המסמך מציין במפורש את שני התפקידים."),
    "receipt": TermTemplate("Receipt", "קבלה", "A document confirming payment receipt, separate from tax documentation unless combined with an invoice.", "מסמך המאשר שהתקבל תשלום; הוא נפרד מתיעוד המס של המכירה אלא אם הוא משולב בחשבונית.", ("accounting", "retail", "freelance"), ("tax_authority",)),
    "exempt dealer": TermTemplate("Exempt dealer", "עוסק פטור", "A self-employed business category that generally does not charge VAT and is limited by annual turnover thresholds and professional exclusions.", "סיווג של עצמאי שבדרך כלל אינו גובה מע\"מ, בכפוף לתקרת מחזור שנתית ולחריגים מקצועיים.", ("tax", "accounting", "freelance"), ("tax_authority",), "Check the annual threshold and excluded professions before using this label.", "יש לבדוק את התקרה השנתית ואת רשימת המקצועות שאינם זכאים לסיווג זה.", "Thresholds change. Treat numeric limits as date-sensitive.", "התקרות משתנות. יש להתייחס לסכומים כנתונים תלויי תאריך."),
    "licensed dealer": TermTemplate("Licensed dealer", "עוסק מורשה", "A VAT-registered self-employed business that charges VAT, issues tax invoices, and submits VAT reports.", "עצמאי הרשום במע\"מ, גובה מע\"מ, מוציא חשבוניות מס ומגיש דיווחי מע\"מ.", ("tax", "accounting", "freelance"), ("tax_authority",)),
    "invoice allocation number": TermTemplate("Invoice allocation number", "מספר הקצאה לחשבונית", "A Tax Authority allocation identifier used in Israeli digital invoicing controls for certain invoices.", "מזהה הקצאה של רשות המסים המשמש בבקרות החשבוניות הדיגיטליות בישראל עבור חשבוניות מסוימות.", ("tax", "accounting", "retail"), ("tax_authority",), "The threshold is above 10,000 ₪ from 01/01/2026 and above 5,000 ₪ from 01/06/2026, confirmed on 03/06/2026.", "התקרה היא מעל 10,000 ₪ מיום 01/01/2026 ומעל 5,000 ₪ מיום 01/06/2026, לפי אימות מיום 03/06/2026.", "Rules, thresholds, and dates are sensitive; verify before publication.", "הכללים, התקרות והמועדים רגישים לשינוי; חובה לאמת לפני פרסום."),
    "national insurance contributions": TermTemplate("National Insurance contributions", "דמי ביטוח לאומי", "Mandatory payments to the National Insurance Institute based on status and income rules.", "תשלומי חובה למוסד לביטוח לאומי בהתאם למעמד המבוטח ולכללי ההכנסה.", ("freelance", "employment", "tax"), ("btl",), "For a self-employed adult before retirement age, 2026 total rates are 7.7% up to 7,703 ₪ and 18% above that up to 51,910 ₪, confirmed on 03/06/2026.", "לעצמאי מגיל 18 ועד גיל פרישה, השיעורים הכוללים בשנת 2026 הם 7.7% עד 7,703 ₪ ו-18% מעל סכום זה עד 51,910 ₪, לפי אימות מיום 03/06/2026."),
    "pension contributions": TermTemplate("Pension contributions", "הפרשות לפנסיה", "Payments made into pension savings according to employment, self-employment, and pension rules.", "תשלומים לחיסכון פנסיוני בהתאם לכללי עבודה, עצמאים והסדרים פנסיוניים.", ("employment", "freelance"), ("finance_ministry", "labor"), "For self-employed pension duty, official guidance uses 4.45% for the first tier and 12.55% for the second tier; confirmed on 03/06/2026.", "בחובת פנסיה לעצמאים, ההנחיה הרשמית משתמשת ב-4.45% ברובד הראשון וב-12.55% ברובד השני; אומת ביום 03/06/2026."),
    "consumer cancellation": TermTemplate("Consumer cancellation", "ביטול עסקה צרכנית", "A consumer right to cancel certain transactions under Israeli consumer protection rules, subject to type, timing, and exceptions.", "זכות צרכן לבטל עסקאות מסוימות לפי דיני הגנת הצרכן בישראל, בכפוף לסוג העסקה, למועד ולחריגים.", ("consumer", "retail", "ecommerce"), ("consumer_protection",), "Many online and service transactions use a 14-day cancellation window; common cancellation fees are capped at 5% or 100 ₪, whichever is lower, as confirmed on 03/06/2026.", "בעסקאות מקוונות ובשירותים רבים חל חלון ביטול של 14 ימים; דמי ביטול נפוצים מוגבלים ל-5% או 100 ₪, לפי הנמוך, לפי אימות מיום 03/06/2026."),
    "warranty certificate": TermTemplate("Warranty certificate", "תעודת אחריות", "A document describing warranty terms, responsible party, scope, period, and service conditions.", "מסמך המפרט את תנאי האחריות, הגורם האחראי, היקף האחריות, תקופתה ותנאי השירות.", ("consumer", "retail"), ("consumer_protection", "standards")),
    "privacy policy": TermTemplate("Privacy policy", "מדיניות פרטיות", "A public notice explaining how personal data is collected, used, retained, shared, and protected.", "הודעה לציבור המסבירה כיצד נאסף, נעשה בו שימוש, נשמר, מועבר ומוגן מידע אישי.", ("privacy", "web", "ecommerce"), ("privacy",), "Use plain language and match the actual data practices.", "יש להשתמש בלשון ברורה ולהתאים את המסמך לפעילות המידע בפועל."),
    "database registration": TermTemplate("Database registration or notice", "רישום או הודעה על מאגר מידע", "Registration, notice, or compliance handling for a database when Israeli privacy rules require it.", "רישום, הודעה או טיפול בעמידה בדרישות לגבי מאגר מידע כאשר דיני הגנת הפרטיות בישראל מחייבים זאת.", ("privacy", "web"), ("privacy",), "Amendment 13 narrowed database registration and added a notice obligation for certain databases; confirm applicability with current Privacy Protection Authority guidance.", "תיקון 13 צמצם את חובת הרישום והוסיף חובת הודעה לגבי מאגרים מסוימים; יש לאמת תחולה מול הנחיות הרשות להגנת הפרטיות."),
    "accessibility statement": TermTemplate("Accessibility statement", "הצהרת נגישות", "A website or service notice describing accessibility arrangements and contact details for accessibility requests.", "הודעה באתר או בשירות המתארת הסדרי נגישות ופרטי קשר לפניות נגישות.", ("web", "consumer", "retail"), ("accessibility",)),
    "company extract": TermTemplate("Company extract", "נסח חברה", "An official company record that presents registration details, status, directors, shareholders, liens, and similar corporate data when available.", "רישום רשמי של חברה המציג פרטי רישום, סטטוס, דירקטורים, בעלי מניות, שעבודים ונתונים תאגידיים דומים כאשר הם קיימים.", ("corporate",), ("corporations", "data_gov_il")),
    "private company": TermTemplate("Private company", "חברה פרטית", "A company incorporated under Israeli company law that is not publicly traded, subject to applicable corporate reporting duties.", "חברה שהתאגדה לפי דיני החברות בישראל ואינה נסחרת בציבור, בכפוף לחובות הדיווח התאגידיות החלות עליה.", ("corporate",), ("corporations",)),
    "import declaration": TermTemplate("Import declaration", "רשימון יבוא", "A customs document or electronic declaration used to clear goods imported into Israel.", "מסמך מכס או הצהרה אלקטרונית המשמשים לשחרור טובין שיובאו לישראל.", ("import", "retail"), ("tax_authority", "govil")),
    "standard mark": TermTemplate("Standard mark", "תו תקן", "A mark indicating conformity with a relevant Israeli standard when issued under the applicable standards framework.", "סימון המעיד על התאמה לתקן ישראלי רלוונטי כאשר הוא ניתן לפי מסגרת התקינה החלה.", ("import", "retail", "consumer"), ("standards",)),
    "restricted account": TermTemplate("Restricted account", "חשבון מוגבל", "A bank account subject to statutory restrictions, often due to repeated dishonored checks under applicable banking rules.", "חשבון בנק הכפוף להגבלות לפי דין, בדרך כלל עקב חזרת שיקים חוזרת לפי כללי הבנקאות החלים.", ("banking", "consumer", "finance"), ("boi",)),
    "prospectus": TermTemplate("Prospectus", "תשקיף", "A disclosure document used for certain securities offerings, subject to Israeli securities regulation.", "מסמך גילוי המשמש בהצעות מסוימות של ניירות ערך, בכפוף לדיני ניירות ערך בישראל.", ("finance", "corporate"), ("isa",)),
}

SYNONYMS: dict[str, str] = {
    "vat": "value added tax",
    "מע\"מ": "value added tax",
    "מס ערך מוסף": "value added tax",
    "ניכוי מס במקור": "withholding tax",
    "חשבונית מס": "tax invoice",
    "חשבונית": "tax invoice",
    "קבלה": "receipt",
    "עוסק פטור": "exempt dealer",
    "עוסק מורשה": "licensed dealer",
    "מספר הקצאה": "invoice allocation number",
    "מספר הקצאה לחשבונית": "invoice allocation number",
    "דמי ביטוח לאומי": "national insurance contributions",
    "הפרשות לפנסיה": "pension contributions",
    "ביטול עסקה": "consumer cancellation",
    "ביטול עסקה צרכנית": "consumer cancellation",
    "תעודת אחריות": "warranty certificate",
    "מדיניות פרטיות": "privacy policy",
    "database registration or notice": "database registration",
    "database notice": "database registration",
    "רישום מאגר מידע": "database registration",
    "רישום או הודעה על מאגר מידע": "database registration",
    "חובת הודעה על מאגר מידע": "database registration",
    "הודעה על מאגר מידע": "database registration",
    "מאגר מידע": "database registration",
    "הצהרת נגישות": "accessibility statement",
    "נסח חברה": "company extract",
    "חברה פרטית": "private company",
    "רשימון יבוא": "import declaration",
    "תו תקן": "standard mark",
    "חשבון מוגבל": "restricted account",
    "תשקיף": "prospectus",
}

INDUSTRY_DEFAULT_SOURCES: dict[str, tuple[str, ...]] = {
    "tax": ("tax_authority", "data_gov_il"),
    "accounting": ("tax_authority",),
    "freelance": ("tax_authority", "btl", "finance_ministry"),
    "employment": ("labor", "finance_ministry", "btl"),
    "consumer": ("consumer_protection", "govil"),
    "retail": ("consumer_protection", "tax_authority", "standards"),
    "ecommerce": ("consumer_protection", "privacy", "accessibility"),
    "privacy": ("privacy",),
    "web": ("privacy", "accessibility"),
    "corporate": ("corporations", "data_gov_il"),
    "import": ("tax_authority", "standards", "govil"),
    "banking": ("boi",),
    "finance": ("boi", "isa"),
    "general": ("govil",),
}

SAMPLE_TERMS: dict[str, tuple[str, ...]] = {
    "tax": ("Value Added Tax", "Withholding tax", "Tax invoice", "Receipt", "Invoice allocation number"),
    "freelance": ("Exempt dealer", "Licensed dealer", "Withholding tax", "National Insurance contributions", "Pension contributions"),
    "consumer": ("Consumer cancellation", "Warranty certificate", "Restricted account"),
    "retail": ("Value Added Tax", "Warranty certificate", "Consumer cancellation", "Standard mark"),
    "privacy": ("Privacy policy", "Database registration", "Accessibility statement"),
    "corporate": ("Company extract", "Private company", "Prospectus"),
    "import": ("Import declaration", "Standard mark", "Value Added Tax"),
    "general": ("Value Added Tax", "Privacy policy", "Consumer cancellation"),
}


def normalize_term(term: str) -> str:
    """Normalize a raw term for matching against synonyms and templates."""
    cleaned = term.strip().strip("-•*0123456789.()[]{}: \t")
    cleaned = re.sub(r"\s+", " ", cleaned)
    lowered = cleaned.casefold().replace("׳", "'").replace("“", '"').replace("”", '"')
    return SYNONYMS.get(lowered, lowered)


def detect_language(text: str) -> Literal["he", "en", "mixed"]:
    """Detect whether text is Hebrew, English, or mixed."""
    has_hebrew = bool(HEBREW_RE.search(text))
    has_latin = bool(re.search(r"[A-Za-z]", text))
    if has_hebrew and has_latin:
        return "mixed"
    return "he" if has_hebrew else "en"


def unique_preserve_order(items: Iterable[str]) -> list[str]:
    """Return unique non-empty strings while preserving first appearance."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        item = str(item).strip()
        key = normalize_term(item)
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def today_il() -> str:
    """Return today's date in DD/MM/YYYY format."""
    return date.today().strftime("%d/%m/%Y")


def validate_environment(environment: str) -> Environment:
    """Validate sandbox or production environment labels."""
    if environment not in {"sandbox", "production"}:
        raise ValueError("environment must be sandbox or production")
    return environment  # type: ignore[return-value]


def build_sample_terms(industry: str = "general") -> list[str]:
    """Return a starter list of terms for an industry."""
    return list(SAMPLE_TERMS.get(industry, SAMPLE_TERMS["general"]))


def make_glossary_id(title: str, terms: Sequence[str], environment: Environment = "sandbox") -> str:
    """Create a stable-looking but unique glossary identifier."""
    seed = "|".join([title, environment, *terms, str(uuid.uuid4())])
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"gls_{digest}"


class GlossaryStore:
    """JSON file store for create/export CLI workflows."""

    def __init__(self, path: str | Path = ".terminology-glossaries.json") -> None:
        self.path = Path(path)

    def read_all(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"glossaries": {}}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def write_all(self, payload: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def create(self, result: GlossaryResult) -> dict[str, Any]:
        data = self.read_all()
        data.setdefault("glossaries", {})[result.id] = result.to_dict()
        self.write_all(data)
        return {"id": result.id, "path": str(self.path), "entry_count": result.entry_count, "warnings": result.warnings}

    def get(self, glossary_id: str) -> GlossaryResult:
        data = self.read_all().get("glossaries", {})
        if glossary_id not in data:
            raise KeyError(f"Glossary not found: {glossary_id}")
        return GlossaryResult.from_dict(data[glossary_id])

    def list(self) -> list[dict[str, Any]]:
        data = self.read_all().get("glossaries", {})
        return [
            {
                "id": key,
                "title": value.get("title"),
                "industry": value.get("industry"),
                "entry_count": value.get("entry_count", len(value.get("entries", []))),
                "created_at": value.get("created_at"),
            }
            for key, value in sorted(data.items())
        ]


class GlossaryBuilder:
    """Build, validate, serialize, and store bilingual Israeli terminology glossaries."""

    def __init__(
        self,
        source_registry: Mapping[str, CitationSource] | None = None,
        term_library: Mapping[str, TermTemplate] | None = None,
    ) -> None:
        self.source_registry = dict(source_registry or SOURCE_REGISTRY)
        self.term_library = dict(term_library or TERM_LIBRARY)

    def parse_terms(self, text_or_terms: str | Iterable[str]) -> list[str]:
        if isinstance(text_or_terms, str):
            raw = [chunk for chunk in SPLIT_RE.split(text_or_terms) if chunk.strip()]
        else:
            raw = [str(item) for item in text_or_terms if str(item).strip()]
        return unique_preserve_order(raw)

    def source(self, key: str) -> CitationSource:
        try:
            return self.source_registry[key]
        except KeyError as exc:
            raise KeyError(f"Unknown source key: {key}") from exc

    def sources_for_industry(self, industry: str) -> list[CitationSource]:
        keys = INDUSTRY_DEFAULT_SOURCES.get(industry, INDUSTRY_DEFAULT_SOURCES["general"])
        return [self.source(key) for key in keys if key in self.source_registry]

    def resolve_term(self, term: str, industry: str = "general") -> GlossaryEntry:
        normalized = normalize_term(term)
        template = self.term_library.get(normalized)
        if template is None:
            sources = self.sources_for_industry(industry)
            language = detect_language(term)
            return GlossaryEntry(
                term_en="Review translation" if language == "he" else term.strip(),
                term_he=term.strip() if language == "he" else "נדרש תרגום מקצועי",
                definition_en="Unverified term. Add an authoritative Israeli source, confirm the professional meaning, and validate the Hebrew-English pairing before publication.",
                definition_he="מונח לא מאומת. יש להוסיף מקור ישראלי מוסמך, לאשר את המשמעות המקצועית ולוודא את התאמת התרגום לפני פרסום.",
                industry=industry,
                sources=sources,
                warning_en="Review required before external use.",
                warning_he="נדרשת בדיקה לפני שימוש חיצוני.",
                original_term=term,
            )
        sources = [self.source(key) for key in template.source_keys if key in self.source_registry]
        return GlossaryEntry(
            term_en=template.canonical_en,
            term_he=template.canonical_he,
            definition_en=template.definition_en,
            definition_he=template.definition_he,
            industry=industry if industry != "general" else template.industries[0],
            sources=sources,
            usage_note_en=template.usage_note_en,
            usage_note_he=template.usage_note_he,
            warning_en=template.warning_en,
            warning_he=template.warning_he,
            original_term=term,
        )

    def build_glossary(
        self,
        terms: str | Iterable[str],
        *,
        industry: str = "general",
        audience: Audience = "general",
        title: str = "English-Hebrew Terminology Glossary",
        language_mode: LanguageMode = "bilingual",
        environment: Environment = "sandbox",
        max_terms: int | None = None,
        sort_terms: bool = True,
    ) -> GlossaryResult:
        environment = validate_environment(environment)
        parsed = self.parse_terms(terms)
        if max_terms is not None:
            if max_terms <= 0:
                raise ValueError("max_terms must be positive")
            parsed = parsed[:max_terms]
        if sort_terms:
            parsed = sorted(parsed, key=lambda item: normalize_term(item))
        result = GlossaryResult(
            id=make_glossary_id(title, parsed, environment),
            title=title,
            industry=industry,
            audience=audience,
            language_mode=language_mode,
            environment=environment,
            entries=[self.resolve_term(term, industry) for term in parsed],
        )
        result.warnings = self.quality_checks(result)
        return result

    async def abuild_glossary(self, *args: Any, **kwargs: Any) -> GlossaryResult:
        return await asyncio.to_thread(self.build_glossary, *args, **kwargs)

    def quality_checks(self, result: GlossaryResult) -> list[str]:
        warnings: list[str] = []
        if not result.entries:
            warnings.append("No terms were provided.")
        for entry in result.entries:
            if not entry.sources:
                warnings.append(f"{entry.original_term or entry.term_en}: missing authoritative source.")
            if "Review" in entry.term_en or "נדרש" in entry.term_he:
                warnings.append(f"{entry.original_term}: translation or definition needs professional review.")
            numeric_text = " ".join([entry.definition_en, entry.definition_he, entry.usage_note_en, entry.usage_note_he])
            if SHEKEL_RE.search(numeric_text) and not DATE_DDMMYYYY_RE.search(numeric_text):
                warnings.append(f"{entry.term_en}: amount in ₪ should include a DD/MM/YYYY validity date.")
            if NIKUD_RE.search(entry.definition_he + entry.usage_note_he + entry.warning_he):
                warnings.append(f"{entry.term_he}: Hebrew technical prose contains nikud.")
        return warnings

    def to_markdown(self, result: GlossaryResult, *, localization: Literal["en", "he"] = "en") -> str:
        lines: list[str] = []
        if localization == "he":
            lines.extend([
                f"# {result.title}",
                "",
                f"תאריך יצירה: {result.created_at}",
                f"ענף: {result.industry}",
                f"סביבה: {result.environment}",
                "",
                "| מונח בעברית | מונח באנגלית | הגדרה | מקורות | הערות |",
                "|---|---|---|---|---|",
            ])
            for entry in result.entries:
                sources = "<br>".join(source.citation("he") for source in entry.sources)
                notes = " ".join(part for part in [entry.usage_note_he, entry.warning_he] if part)
                lines.append(f"| {entry.term_he} | {entry.term_en} | {entry.definition_he} | {sources} | {notes} |")
            if result.warnings:
                lines.extend(["", "## בדיקות נדרשות", *[f"- {warning}" for warning in result.warnings]])
            return "\n".join(lines) + "\n"
        lines.extend([
            f"# {result.title}",
            "",
            f"Created: {result.created_at}",
            f"Industry: {result.industry}",
            f"Environment: {result.environment}",
            "",
            "| English term | Hebrew term | Definition | Sources | Notes |",
            "|---|---|---|---|---|",
        ])
        for entry in result.entries:
            sources = "<br>".join(source.citation("en") for source in entry.sources)
            notes = " ".join(part for part in [entry.usage_note_en, entry.warning_en] if part)
            lines.append(f"| {entry.term_en} | {entry.term_he} | {entry.definition_en} | {sources} | {notes} |")
        if result.warnings:
            lines.extend(["", "## Required checks", *[f"- {warning}" for warning in result.warnings]])
        return "\n".join(lines) + "\n"

    def to_json(self, result: GlossaryResult) -> str:
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n"

    def to_csv(self, result: GlossaryResult) -> str:
        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=["term_en", "term_he", "definition_en", "definition_he", "industry", "source_keys", "warnings"],
        )
        writer.writeheader()
        for entry in result.entries:
            writer.writerow(
                {
                    "term_en": entry.term_en,
                    "term_he": entry.term_he,
                    "definition_en": entry.definition_en,
                    "definition_he": entry.definition_he,
                    "industry": entry.industry,
                    "source_keys": ";".join(entry.source_keys),
                    "warnings": " ".join(part for part in [entry.warning_en, entry.warning_he] if part),
                }
            )
        return buffer.getvalue()

    def validate_source_registry(self) -> list[str]:
        errors: list[str] = []
        for key, source in self.source_registry.items():
            if key != source.key:
                errors.append(f"Registry key mismatch: {key} != {source.key}")
            if not source.url.startswith("https://"):
                errors.append(f"{key}: source URL must use https")
            if not source.title_en or not source.title_he:
                errors.append(f"{key}: source titles are required")
        for key, template in self.term_library.items():
            for source_key in template.source_keys:
                if source_key not in self.source_registry:
                    errors.append(f"{key}: unknown source key {source_key}")
            if NIKUD_RE.search(template.definition_he + template.usage_note_he + template.warning_he):
                errors.append(f"{key}: Hebrew prose contains nikud")
        return errors

    def create_glossary(
        self,
        terms: str | Iterable[str],
        *,
        store_path: str | Path = ".terminology-glossaries.json",
        industry: str = "general",
        audience: Audience = "general",
        title: str = "English-Hebrew Terminology Glossary",
        language_mode: LanguageMode = "bilingual",
        environment: Environment = "sandbox",
    ) -> dict[str, Any]:
        result = self.build_glossary(
            terms,
            industry=industry,
            audience=audience,
            title=title,
            language_mode=language_mode,
            environment=environment,
        )
        return GlossaryStore(store_path).create(result)

    def get_glossary(self, glossary_id: str, *, store_path: str | Path = ".terminology-glossaries.json") -> GlossaryResult:
        return GlossaryStore(store_path).get(glossary_id)

    def list_glossaries(self, *, store_path: str | Path = ".terminology-glossaries.json") -> list[dict[str, Any]]:
        return GlossaryStore(store_path).list()

    def export_glossary(
        self,
        glossary_id: str,
        *,
        store_path: str | Path = ".terminology-glossaries.json",
        output_format: OutputFormat = "markdown",
        localization: Literal["en", "he"] = "en",
    ) -> str:
        result = self.get_glossary(glossary_id, store_path=store_path)
        if output_format == "json":
            return self.to_json(result)
        if output_format == "csv":
            return self.to_csv(result)
        if output_format == "markdown":
            return self.to_markdown(result, localization=localization)
        raise ValueError("output_format must be markdown, json, or csv")


def build_glossary_json(terms: str | Iterable[str], **kwargs: Any) -> str:
    """Convenience function returning glossary JSON."""
    return GlossaryBuilder().to_json(GlossaryBuilder().build_glossary(terms, **kwargs))


__all__ = [
    "Audience",
    "CitationSource",
    "Environment",
    "GlossaryBuilder",
    "GlossaryEntry",
    "GlossaryResult",
    "GlossaryStore",
    "LanguageMode",
    "OutputFormat",
    "SOURCE_REGISTRY",
    "TERM_LIBRARY",
    "build_glossary_json",
    "build_sample_terms",
    "detect_language",
    "make_glossary_id",
    "normalize_term",
    "today_il",
    "unique_preserve_order",
    "validate_environment",
]
