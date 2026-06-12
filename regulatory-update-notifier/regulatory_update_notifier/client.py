"""Typed client utilities for Israeli regulatory update monitoring."""

from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import email.utils
import hashlib
import html
import json
import re
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse

import httpx


class SourceType(str, Enum):
    """Supported source formats."""

    ODATA = "odata"
    RSS = "rss"
    ATOM = "atom"
    HTML = "html"
    JSON = "json"
    PDF = "pdf"
    MANUAL = "manual"


class RuntimeEnvironment(str, Enum):
    """Supported runtime environments."""

    SANDBOX = "sandbox"
    PRODUCTION = "production"


class RegulatoryFetchError(RuntimeError):
    """Raised when a source cannot be retrieved."""


class RegulatoryParseError(RuntimeError):
    """Raised when source content cannot be parsed."""


@dataclass(slots=True)
class UpdateSource:
    """Configured Israeli legal or regulatory source."""

    name: str
    url: str
    source_type: SourceType | str
    regulator: str
    tags: list[str] = field(default_factory=list)
    industries: list[str] = field(default_factory=lambda: ["all"])
    jurisdiction: str = "IL"
    inline_text: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("source name is required")
        parsed = urlparse(self.url)
        if parsed.scheme not in {"http", "https", "file", "inline"}:
            raise ValueError("source url must use http, https, file, or inline scheme")
        if not isinstance(self.source_type, SourceType):
            self.source_type = SourceType(str(self.source_type))
        self.tags = [normalize_token(tag) for tag in self.tags if tag]
        self.industries = [normalize_token(industry) for industry in self.industries if industry] or ["all"]


@dataclass(slots=True)
class RegulatoryUpdate:
    """Parsed and scored regulatory update."""

    source: str
    title: str
    summary: str
    url: str
    published_at: dt.date | None
    regulator: str
    source_type: str
    tags: list[str] = field(default_factory=list)
    industries: list[str] = field(default_factory=list)
    raw_text: str = ""
    status: str = "background"
    severity: str = "low"
    score: int = 0
    id: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            self.id = stable_id(self.title, self.url, self.published_at.isoformat() if self.published_at else "")
        self.tags = [normalize_token(tag) for tag in self.tags if tag]
        self.industries = [normalize_token(industry) for industry in self.industries if industry]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "regulator": self.regulator,
            "source_type": self.source_type,
            "tags": list(self.tags),
            "industries": list(self.industries),
            "raw_text": self.raw_text,
            "status": self.status,
            "severity": self.severity,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "RegulatoryUpdate":
        """Create an update from a dictionary."""
        return cls(
            source=str(payload.get("source", "")),
            title=str(payload.get("title", "")),
            summary=str(payload.get("summary", "")),
            url=str(payload.get("url", "")),
            published_at=parse_date(payload.get("published_at")),
            regulator=str(payload.get("regulator", "")),
            source_type=str(payload.get("source_type", "")),
            tags=list(payload.get("tags", []) or []),
            industries=list(payload.get("industries", []) or []),
            raw_text=str(payload.get("raw_text", "")),
            status=str(payload.get("status", "background")),
            severity=str(payload.get("severity", "low")),
            score=int(payload.get("score", 0)),
            id=str(payload.get("id", "")),
        )


@dataclass(slots=True)
class AlertProfile:
    """Reusable monitoring profile for a business, freelancer, or consumer."""

    name: str
    industries: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    locale: str = "he"
    environment: RuntimeEnvironment | str = RuntimeEnvironment.SANDBOX
    id: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("profile name is required")
        if not isinstance(self.environment, RuntimeEnvironment):
            self.environment = RuntimeEnvironment(str(self.environment))
        self.industries = [normalize_token(item) for item in self.industries if item]
        self.keywords = [str(item).strip() for item in self.keywords if str(item).strip()]
        if not self.id:
            self.id = stable_id(self.name, ",".join(self.industries), ",".join(self.keywords), self.locale)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable profile."""
        return {
            "id": self.id,
            "name": self.name,
            "industries": list(self.industries),
            "keywords": list(self.keywords),
            "locale": self.locale,
            "environment": self.environment.value if isinstance(self.environment, RuntimeEnvironment) else str(self.environment),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "AlertProfile":
        """Create a profile from a dictionary."""
        return cls(
            id=str(payload.get("id", "")),
            name=str(payload.get("name", "")),
            industries=list(payload.get("industries", []) or []),
            keywords=list(payload.get("keywords", []) or []),
            locale=str(payload.get("locale", "he")),
            environment=str(payload.get("environment", RuntimeEnvironment.SANDBOX.value)),
        )


MANDATORY_TERMS = {
    "must", "shall", "required", "mandatory", "obligation",
    "חובה", "חייב", "חייבת", "יידרש", "נדרש", "נדרשת", "עליו", "עליה",
}
DRAFT_TERMS = {"draft", "memorandum", "consultation", "comments", "טיוטה", "תזכיר", "הערות הציבור", "להערות"}
BILL_TERMS = {"bill", "proposal", "הצעת חוק", "קריאה", "ועדה"}
ENACTED_TERMS = {"reshumot", "official gazette", "regulations", "law", "רשומות", "תקנות", "צו", "חוק"}
ENFORCEMENT_TERMS = {"fine", "penalty", "sanction", "enforcement", "inspection", "קנס", "עיצום", "אכיפה", "ביקורת", "סנקציה"}

INDUSTRY_SYNONYMS: dict[str, set[str]] = {
    "freelancer": {"freelancer", "self-employed", "sole trader", "עצמאי", "עוסק", "עוסק פטור", "עוסק מורשה"},
    "ecommerce": {"ecommerce", "online store", "online-sales", "distance selling", "חנות מקוונת", "מסחר מקוון", "מכר מרחוק"},
    "retail": {"retail", "shop", "store", "קמעונאות", "חנות"},
    "consumers": {"consumer", "consumers", "צרכן", "צרכנים", "צרכנות"},
    "employer": {"employer", "employees", "payroll", "מעסיק", "עובדים", "שכר", "תלוש"},
    "food": {"restaurant", "cafe", "food", "מסעדה", "בית קפה", "מזון"},
    "health": {"health", "clinic", "medical", "בריאות", "מרפאה", "רפואי"},
    "finance": {"bank", "credit", "payment", "insurance", "finance", "בנק", "אשראי", "תשלום", "ביטוח"},
    "import": {"import", "customs", "standards", "יבוא", "מכס", "תקן", "תקינה"},
    "privacy": {"privacy", "personal data", "database", "פרטיות", "מידע אישי", "מאגר מידע"},
    "labor": {"labor", "employment", "work", "minimum wage", "עבודה", "שכר מינימום", "שעות עבודה"},
    "professional-services": {"consultant", "professional services", "ייעוץ", "שירותים מקצועיים", "רואה חשבון", "עורך דין"},
}


def normalize_token(value: str) -> str:
    """Normalize a token used for matching."""
    return re.sub(r"\s+", "-", value.strip().lower())


def normalize_title(value: str) -> str:
    """Normalize a title for deduplication."""
    cleaned = html.unescape(value)
    cleaned = re.sub(r"[\W_]+", " ", cleaned, flags=re.UNICODE)
    return re.sub(r"\s+", " ", cleaned).strip().lower()


def stable_id(*parts: str) -> str:
    """Return a stable short content identifier."""
    joined = "|".join(normalize_title(part) for part in parts if part)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:12]


def strip_html(text: str) -> str:
    """Return visible text from HTML."""
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</(p|div|li|h1|h2|h3|article|section)>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"[ \t\r\f\v]+", " ", text).strip()


def parse_date(value: Any) -> dt.date | None:
    """Parse common Israeli and web date formats."""
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    text = str(value).strip()
    if not text:
        return None
    iso_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if iso_match:
        try:
            return dt.date(int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3)))
        except ValueError:
            return None
    il_match = re.search(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})\b", text)
    if il_match:
        day, month, year = (int(il_match.group(1)), int(il_match.group(2)), int(il_match.group(3)))
        if year < 100:
            year += 2000
        try:
            return dt.date(year, month, day)
        except ValueError:
            return None
    try:
        parsed = email.utils.parsedate_to_datetime(text)
        if parsed:
            return parsed.date()
    except (TypeError, ValueError, IndexError):
        return None
    return None


def format_il_date(value: dt.date | None) -> str:
    """Format dates as DD/MM/YYYY for Israeli Hebrew output."""
    return value.strftime("%d/%m/%Y") if value else "לא ידוע"


def detect_dates(text: str) -> list[dt.date]:
    """Detect explicit dates in text."""
    candidates = re.findall(r"\d{4}-\d{2}-\d{2}|\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b", text)
    seen: set[str] = set()
    dates: list[dt.date] = []
    for candidate in candidates:
        parsed = parse_date(candidate)
        if parsed and parsed.isoformat() not in seen:
            dates.append(parsed)
            seen.add(parsed.isoformat())
    return dates


def detect_shekel_amounts(text: str) -> list[str]:
    """Extract shekel amounts."""
    amounts: list[str] = []
    for pattern in [r"₪\s?\d[\d,]*(?:\.\d+)?", r"\d[\d,]*(?:\.\d+)?\s?ש\"ח", r"\d[\d,]*(?:\.\d+)?\s?₪"]:
        amounts.extend(re.findall(pattern, text))
    return list(dict.fromkeys(amounts))


def classify_status(source: UpdateSource, text: str) -> str:
    """Classify legal status from source type and text."""
    lower = text.lower()
    source_name = f"{source.name} {source.regulator}".lower()
    combined = f"{lower} {source_name}"
    if source.source_type == SourceType.ODATA or any(term in combined for term in BILL_TERMS):
        if any(term in combined for term in DRAFT_TERMS):
            return "draft-regulation"
        return "bill"
    if any(term in combined for term in DRAFT_TERMS):
        return "draft-regulation"
    if any(term in combined for term in ENFORCEMENT_TERMS):
        return "enforcement"
    if "reshumot" in combined or "רשומות" in combined:
        dates = detect_dates(text)
        if dates and min(dates) > dt.date.today():
            return "future-effective"
        return "enacted"
    guidance_terms = {"guidance", "guideline", "circular", "faq", "הנחיה", "חוזר", "שאלות ותשובות", "עמדה"}
    if source.source_type in {SourceType.HTML, SourceType.PDF, SourceType.JSON, SourceType.MANUAL} and any(term in combined for term in guidance_terms):
        return "guidance"
    if any(term in combined for term in ENACTED_TERMS):
        return "enacted"
    return "background"


def classify_severity(text: str, status: str, score: int = 0) -> str:
    """Classify severity from text, status, and score."""
    lower = text.lower()
    has_deadline = bool(detect_dates(text) or re.search(r"(within|תוך)\s+\d+\s+(days|ימים|יום)", lower))
    has_penalty = any(term in lower for term in ENFORCEMENT_TERMS)
    has_mandatory = any(term in lower for term in MANDATORY_TERMS)
    if status in {"effective-now", "future-effective", "enacted", "enforcement"} and (has_penalty or has_deadline or has_mandatory or score >= 80):
        return "critical" if score >= 80 or has_penalty else "high"
    if status == "draft-regulation":
        return "medium" if score < 70 else "high"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def infer_industries(text: str) -> list[str]:
    """Infer industries from text."""
    lower = text.lower()
    found: list[str] = []
    for industry, terms in INDUSTRY_SYNONYMS.items():
        if any(term.lower() in lower for term in terms):
            found.append(industry)
    return found


def score_update(update: RegulatoryUpdate, industries: Sequence[str] | None = None, keywords: Sequence[str] | None = None) -> int:
    """Score an update for a monitoring profile."""
    profile_industries = {normalize_token(item) for item in (industries or [])}
    update_industries = {normalize_token(item) for item in update.industries} | set(infer_industries(update.raw_text + " " + update.title))
    score = 0
    if "all" in update_industries:
        score += 10
    if profile_industries and update_industries & profile_industries:
        score += 30
    if profile_industries and any(ind in {"consumers", "freelancer", "employer"} for ind in update_industries):
        score += 10
    if not profile_industries and update_industries:
        score += 15
    lower = f"{update.title} {update.summary} {update.raw_text}".lower()
    if any(term in lower for term in MANDATORY_TERMS):
        score += 15
    if detect_dates(lower) or re.search(r"(within|תוך)\s+\d+\s+(days|ימים|יום)", lower):
        score += 15
    if any(term in lower for term in ENFORCEMENT_TERMS):
        score += 10
    if detect_shekel_amounts(lower):
        score += 5
    if keywords and any(keyword.lower() in lower for keyword in keywords):
        score += 20
    if update.status in {"enacted", "effective-now", "future-effective", "enforcement"}:
        score += 10
    return max(0, min(score, 100))


def matches_filter(update: RegulatoryUpdate, industries: Sequence[str] | None = None, keywords: Sequence[str] | None = None) -> bool:
    """Return whether an update matches profile filters."""
    if industries:
        profile = {normalize_token(item) for item in industries}
        item_industries = {normalize_token(item) for item in update.industries} | set(infer_industries(update.raw_text + " " + update.title))
        if "all" not in item_industries and not (profile & item_industries):
            text = f"{update.title} {update.summary} {update.raw_text}".lower()
            if not any(ind.replace("-", " ") in text for ind in profile):
                return False
    if keywords:
        text = f"{update.title} {update.summary} {update.raw_text}".lower()
        if not any(keyword.lower() in text for keyword in keywords):
            return False
    return True


def deduplicate_updates(updates: Iterable[RegulatoryUpdate]) -> list[RegulatoryUpdate]:
    """Deduplicate updates by stable title, URL, and date."""
    chosen: dict[str, RegulatoryUpdate] = {}
    for update in updates:
        key = stable_id(update.url or normalize_title(update.title), normalize_title(update.title), update.published_at.isoformat() if update.published_at else "")
        existing = chosen.get(key)
        if not existing or update.score > existing.score:
            chosen[key] = update
    return list(chosen.values())


class RegulatoryMonitorClient:
    """Sync and async client for configured regulatory sources."""

    def __init__(
        self,
        sources: Sequence[UpdateSource] | None = None,
        *,
        timeout: float = 20.0,
        transport: httpx.BaseTransport | None = None,
        async_transport: httpx.AsyncBaseTransport | None = None,
        user_agent: str = "regulatory-update-notifier/2.1",
    ) -> None:
        self.sources = list(sources or [])
        self.timeout = timeout
        self.transport = transport
        self.async_transport = async_transport
        self.headers = {"User-Agent": user_agent, "Accept": "application/json, application/xml, text/xml, text/html, text/plain;q=0.9, */*;q=0.5"}

    @classmethod
    def from_config(cls, path: str | Path, **kwargs: Any) -> "RegulatoryMonitorClient":
        """Create a client from JSON or YAML config."""
        config_path = Path(path)
        payload = config_path.read_text(encoding="utf-8")
        if config_path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore
            except ImportError as exc:
                raise RuntimeError("PyYAML is required for YAML config") from exc
            data = yaml.safe_load(payload)
        else:
            data = json.loads(payload)
        sources = [UpdateSource(**item) for item in data.get("sources", [])]
        return cls(sources, **kwargs)

    def register_source(self, source: UpdateSource) -> None:
        """Add a source."""
        self.sources.append(source)

    def fetch_source(self, source: UpdateSource) -> str:
        """Fetch source content synchronously."""
        if source.url.startswith("inline://"):
            return source.inline_text or ""
        if source.url.startswith("file://"):
            return Path(source.url.replace("file://", "", 1)).read_text(encoding="utf-8")
        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers, transport=self.transport, follow_redirects=True) as sync_client:
                response = sync_client.get(source.url)
                response.raise_for_status()
                return response.text
        except httpx.HTTPError as exc:
            raise RegulatoryFetchError(f"failed to fetch {source.name}: {exc}") from exc

    async def afetch_source(self, source: UpdateSource) -> str:
        """Fetch source content asynchronously."""
        if source.url.startswith("inline://"):
            return source.inline_text or ""
        if source.url.startswith("file://"):
            return Path(source.url.replace("file://", "", 1)).read_text(encoding="utf-8")
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, transport=self.async_transport, follow_redirects=True) as async_client:
                response = await async_client.get(source.url)
                response.raise_for_status()
                return response.text
        except httpx.HTTPError as exc:
            raise RegulatoryFetchError(f"failed to fetch {source.name}: {exc}") from exc

    def parse_source_content(self, source: UpdateSource, content: str) -> list[RegulatoryUpdate]:
        """Parse content according to source type."""
        if not content.strip():
            return []
        if source.source_type in {SourceType.RSS, SourceType.ATOM} or content.lstrip().startswith("<rss") or "<feed" in content[:500].lower():
            return self._parse_xml(source, content)
        if source.source_type in {SourceType.JSON, SourceType.ODATA} or content.lstrip().startswith(("{", "[")):
            return self._parse_json(source, content)
        return self._parse_text_or_html(source, content)

    def collect_updates(
        self,
        *,
        since: dt.date | str | None = None,
        industries: Sequence[str] | None = None,
        keywords: Sequence[str] | None = None,
        profile: AlertProfile | None = None,
        minimum_score: int = 0,
        limit: int | None = None,
    ) -> list[RegulatoryUpdate]:
        """Fetch, parse, score, filter, and deduplicate updates."""
        if profile:
            industries = list(industries or []) + profile.industries
            keywords = list(keywords or []) + profile.keywords
        since_date = parse_date(since)
        updates: list[RegulatoryUpdate] = []
        for source in self.sources:
            content = self.fetch_source(source)
            parsed = self.parse_source_content(source, content)
            for update in parsed:
                update.status = classify_status(source, f"{update.title} {update.summary} {update.raw_text}")
                update.score = score_update(update, industries=industries, keywords=keywords)
                update.severity = classify_severity(f"{update.title} {update.summary} {update.raw_text}", update.status, update.score)
                if since_date and update.published_at and update.published_at < since_date:
                    continue
                if not matches_filter(update, industries=industries, keywords=keywords):
                    continue
                if update.score < minimum_score:
                    continue
                updates.append(update)
        updates = deduplicate_updates(updates)
        updates.sort(key=lambda item: (item.published_at or dt.date.min, item.score), reverse=True)
        return updates[:limit] if limit else updates

    async def acollect_updates(
        self,
        *,
        since: dt.date | str | None = None,
        industries: Sequence[str] | None = None,
        keywords: Sequence[str] | None = None,
        profile: AlertProfile | None = None,
        minimum_score: int = 0,
        limit: int | None = None,
    ) -> list[RegulatoryUpdate]:
        """Async version of collect_updates."""
        if profile:
            industries = list(industries or []) + profile.industries
            keywords = list(keywords or []) + profile.keywords
        since_date = parse_date(since)
        contents = await asyncio.gather(*(self.afetch_source(source) for source in self.sources))
        updates: list[RegulatoryUpdate] = []
        for source, content in zip(self.sources, contents):
            parsed = self.parse_source_content(source, content)
            for update in parsed:
                update.status = classify_status(source, f"{update.title} {update.summary} {update.raw_text}")
                update.score = score_update(update, industries=industries, keywords=keywords)
                update.severity = classify_severity(f"{update.title} {update.summary} {update.raw_text}", update.status, update.score)
                if since_date and update.published_at and update.published_at < since_date:
                    continue
                if not matches_filter(update, industries=industries, keywords=keywords):
                    continue
                if update.score < minimum_score:
                    continue
                updates.append(update)
        updates = deduplicate_updates(updates)
        updates.sort(key=lambda item: (item.published_at or dt.date.min, item.score), reverse=True)
        return updates[:limit] if limit else updates

    def _parse_xml(self, source: UpdateSource, content: str) -> list[RegulatoryUpdate]:
        try:
            xml_root = ET.fromstring(content)
        except ET.ParseError as exc:
            raise RegulatoryParseError(f"xml parse failed for {source.name}: {exc}") from exc
        updates: list[RegulatoryUpdate] = []
        for item in xml_root.findall(".//item"):
            title = first_text(item, ["title"]) or "Untitled regulatory item"
            link = first_text(item, ["link"]) or source.url
            summary = strip_html(first_text(item, ["description", "summary"]) or "")
            published = parse_date(first_text(item, ["pubDate", "published", "updated", "dc:date"]))
            updates.append(self._make_update(source, title, summary, link, published, item_to_text(item)))
        namespaces = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in xml_root.findall(".//atom:entry", namespaces) + xml_root.findall(".//entry"):
            title = first_text(entry, ["{http://www.w3.org/2005/Atom}title", "title"]) or "Untitled regulatory item"
            link = source.url
            for link_node in entry.findall("{http://www.w3.org/2005/Atom}link") + entry.findall("link"):
                href = link_node.attrib.get("href")
                if href:
                    link = href
                    break
            summary = strip_html(first_text(entry, ["{http://www.w3.org/2005/Atom}summary", "{http://www.w3.org/2005/Atom}content", "summary", "content"]) or "")
            published = parse_date(first_text(entry, ["{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated", "published", "updated"]))
            updates.append(self._make_update(source, title, summary, link, published, item_to_text(entry)))
        return updates

    def _parse_json(self, source: UpdateSource, content: str) -> list[RegulatoryUpdate]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RegulatoryParseError(f"json parse failed for {source.name}: {exc}") from exc
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = data.get("value") or data.get("items") or data.get("results") or data.get("publications") or data.get("data") or []
            if isinstance(records, dict):
                records = records.get("items") or records.get("results") or []
        else:
            records = []
        updates: list[RegulatoryUpdate] = []
        for record in records:
            if not isinstance(record, Mapping):
                continue
            title = pick(record, ["title", "Title", "name", "Name", "subject", "Subject", "BillName", "LawName", "PublicationName"]) or "Untitled regulatory item"
            summary = pick(record, ["summary", "Summary", "description", "Description", "explanation", "ExplanatoryNote", "body", "Body"]) or json.dumps(record, ensure_ascii=False)[:400]
            url = pick(record, ["url", "Url", "link", "Link", "document_url", "DocumentUrl"]) or source.url
            published = parse_date(pick(record, ["published_at", "published", "PublicationDate", "date", "Date", "LastUpdatedDate", "updated"]))
            updates.append(self._make_update(source, str(title), strip_html(str(summary)), str(url), published, json.dumps(record, ensure_ascii=False)))
        return updates

    def _parse_text_or_html(self, source: UpdateSource, content: str) -> list[RegulatoryUpdate]:
        text = strip_html(content) if "<" in content and ">" in content else content
        lines = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
        title = lines[0] if lines else source.name
        if len(title) > 180:
            title = source.name
        summary = " ".join(lines[1:6]) if len(lines) > 1 else text[:500]
        published = parse_date(text)
        return [self._make_update(source, title, summary, source.url, published, text[:4000])]

    def _make_update(self, source: UpdateSource, title: str, summary: str, url: str, published: dt.date | None, raw_text: str) -> RegulatoryUpdate:
        text = f"{title} {summary} {raw_text}"
        industries = sorted(set(source.industries) | set(infer_industries(text)))
        status = classify_status(source, text)
        update = RegulatoryUpdate(
            source=source.name,
            title=strip_html(title).strip(),
            summary=strip_html(summary).strip(),
            url=url or source.url,
            published_at=published,
            regulator=source.regulator,
            source_type=source.source_type.value,
            tags=source.tags,
            industries=industries,
            raw_text=raw_text,
            status=status,
        )
        update.score = score_update(update)
        update.severity = classify_severity(text, status, update.score)
        return update


def first_text(element: ET.Element, names: Sequence[str]) -> str | None:
    """Return first matching child text."""
    for name in names:
        child = element.find(name)
        if child is not None and child.text:
            return child.text.strip()
    return None


def item_to_text(element: ET.Element) -> str:
    """Serialize XML element text."""
    return " ".join(part.strip() for part in element.itertext() if part and part.strip())


def pick(record: Mapping[str, Any], keys: Sequence[str]) -> Any:
    """Return first present mapping value."""
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
    lower_map = {str(key).lower(): value for key, value in record.items()}
    for key in keys:
        value = lower_map.get(key.lower())
        if value not in (None, ""):
            return value
    return None


def summarize_update(update: RegulatoryUpdate, *, locale: str = "en") -> str:
    """Return a compact Markdown summary for an update."""
    amounts = detect_shekel_amounts(f"{update.title} {update.summary} {update.raw_text}")
    dates = detect_dates(f"{update.title} {update.summary} {update.raw_text}")
    if locale.lower().startswith("he"):
        deadline = format_il_date(dates[0] if dates else update.published_at)
        amount_text = f"\n- **סכומים שאותרו:** {', '.join(amounts)}" if amounts else ""
        return textwrap.dedent(
            f"""
            ### {update.title}

            - **מעמד:** {update.status}
            - **מקור:** {update.source} ({update.regulator})
            - **פורסם:** {format_il_date(update.published_at)}
            - **תחילה או מועד תגובה:** {deadline}
            - **רלוונטי ל:** {', '.join(update.industries) or 'לא סווג'}
            - **רמת התראה:** {update.severity} ({update.score}/100){amount_text}
            - **מה השתנה:** {update.summary or 'נדרש עיון במקור הרשמי.'}
            - **פעולות:** בדיקת תחולה, אימות מועד תחילה, עדכון נהלים ושמירת המקור הרשמי.
            - **אימות:** בדיקת הנוסח הרשמי לפני שינוי תהליך, דיווח או פרסום ללקוחות.
            """
        ).strip()
    deadline_en = dates[0].isoformat() if dates else (update.published_at.isoformat() if update.published_at else "unknown")
    amount_text = f"\n- **Detected amounts:** {', '.join(amounts)}" if amounts else ""
    return textwrap.dedent(
        f"""
        ### {update.title}

        - **Status:** {update.status}
        - **Source:** {update.source} ({update.regulator})
        - **Published:** {update.published_at.isoformat() if update.published_at else 'unknown'}
        - **Effective or response deadline:** {deadline_en}
        - **Relevant to:** {', '.join(update.industries) or 'unclassified'}
        - **Alert level:** {update.severity} ({update.score}/100){amount_text}
        - **What changed:** {update.summary or 'Review the official source.'}
        - **Actions:** Check applicability, verify commencement, update procedures, and save the official source.
        - **Verification:** Review the official text before changing a process or filing.
        """
    ).strip()


def make_digest(updates: Sequence[RegulatoryUpdate], *, locale: str = "en", title: str | None = None) -> str:
    """Create a Markdown digest."""
    if locale.lower().startswith("he"):
        heading = title or "דוח שינויי רגולציה בישראל"
        empty = "לא נמצאו עדכונים רלוונטיים."
    else:
        heading = title or "Israeli Regulatory Update Digest"
        empty = "No relevant updates found."
    if not updates:
        return f"# {heading}\n\n{empty}\n"
    body = "\n\n".join(summarize_update(update, locale=locale) for update in updates)
    return f"# {heading}\n\n{body}\n"


SANDBOX_RSS = """<?xml version="1.0"?>
<rss><channel>
<item><title>Consumer cancellation guidance</title><link>https://example.test/consumer-cancellation</link><pubDate>Mon, 01 Jun 2026 10:00:00 GMT</pubDate><description>הנחיה חדשה מחייבת חנויות במסחר מקוון להציג ביטול עסקה עד 30/06/2026. סכום לדוגמה ₪10,000.</description></item>
<item><title>Privacy database draft</title><link>https://example.test/privacy-draft</link><pubDate>Tue, 02 Jun 2026 10:00:00 GMT</pubDate><description>טיוטה להערות הציבור בנושא מאגר מידע ושירותים מקצועיים.</description></item>
</channel></rss>"""

SANDBOX_ODATA = json.dumps(
    {
        "value": [
            {
                "Name": "הצעת חוק חשבוניות דיגיטליות לעוסק מורשה",
                "PublicationDate": "2026-06-02",
                "Description": "הצעת חוק בנושא מסים, חשבונית מקוונת ועוסק מורשה. חובה להיערך עד 01/01/2027.",
                "Url": "https://example.test/digital-invoices",
            }
        ]
    },
    ensure_ascii=False,
)


def default_sources(environment: RuntimeEnvironment | str = RuntimeEnvironment.PRODUCTION) -> list[UpdateSource]:
    """Return a starter source registry."""
    if not isinstance(environment, RuntimeEnvironment):
        environment = RuntimeEnvironment(str(environment))
    if environment == RuntimeEnvironment.SANDBOX:
        return [
            UpdateSource(
                name="Sandbox consumer and privacy feed",
                url="inline://sandbox-consumer-feed",
                source_type=SourceType.RSS,
                regulator="Sandbox regulator",
                tags=["consumer", "privacy", "ecommerce"],
                industries=["ecommerce", "retail", "consumers", "privacy", "professional-services"],
                inline_text=SANDBOX_RSS,
            ),
            UpdateSource(
                name="Sandbox tax OData feed",
                url="inline://sandbox-tax-odata",
                source_type=SourceType.ODATA,
                regulator="Sandbox tax authority",
                tags=["tax", "invoices"],
                industries=["freelancer", "retail", "ecommerce"],
                inline_text=SANDBOX_ODATA,
            ),
        ]
    return [
        UpdateSource(name="Knesset bills", url="https://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_Bill", source_type=SourceType.ODATA, regulator="Knesset", tags=["bills", "primary-legislation"], industries=["all"]),
        UpdateSource(name="Reshumot official gazette", url="https://www.gov.il/he/departments/official_gazette", source_type=SourceType.HTML, regulator="Reshumot", tags=["official-gazette", "enacted"], industries=["all"]),
        UpdateSource(name="Tax Authority publications", url="https://www.gov.il/he/departments/israel_tax_authority", source_type=SourceType.HTML, regulator="Israel Tax Authority", tags=["tax", "vat", "invoices"], industries=["freelancer", "retail", "ecommerce"]),
        UpdateSource(name="Consumer Protection publications", url="https://www.gov.il/he/departments/consumer_protection_and_fair_trade_authority", source_type=SourceType.HTML, regulator="Consumer Protection and Fair Trade Authority", tags=["consumer", "ecommerce", "retail"], industries=["ecommerce", "retail", "consumers"]),
        UpdateSource(name="Privacy Protection Authority publications", url="https://www.gov.il/he/departments/the_privacy_protection_authority", source_type=SourceType.HTML, regulator="Privacy Protection Authority", tags=["privacy", "personal-data"], industries=["ecommerce", "health", "professional-services", "privacy"]),
        UpdateSource(name="Ministry of Labor publications", url="https://www.gov.il/he/departments/labor", source_type=SourceType.HTML, regulator="Ministry of Labor", tags=["labor", "employment"], industries=["employer", "labor"]),
        UpdateSource(name="Government Legislation Site consultations", url="https://www.tazkirim.gov.il/s/?language=iw", source_type=SourceType.HTML, regulator="Ministry of Justice", tags=["public-consultation", "drafts", "tazkirim"], industries=["all"]),
    ]


def source_to_dict(source: UpdateSource) -> dict[str, Any]:
    """Return a serializable source dictionary."""
    data = dataclasses.asdict(source)
    data["source_type"] = source.source_type.value if isinstance(source.source_type, SourceType) else str(source.source_type)
    return data


def save_updates(path: str | Path, updates: Sequence[RegulatoryUpdate]) -> None:
    """Save updates as JSON."""
    Path(path).write_text(json.dumps([item.to_dict() for item in updates], ensure_ascii=False, indent=2), encoding="utf-8")


def load_updates(path: str | Path) -> list[RegulatoryUpdate]:
    """Load updates from JSON."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [RegulatoryUpdate.from_dict(item) for item in payload]


def save_default_config(path: str | Path, environment: RuntimeEnvironment | str = RuntimeEnvironment.SANDBOX) -> None:
    """Save default source configuration."""
    payload = {"environment": str(environment), "sources": [source_to_dict(source) for source in default_sources(environment)]}
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_profile(path: str | Path, profile: AlertProfile) -> None:
    """Save a profile as JSON."""
    Path(path).write_text(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_profile(path: str | Path, profile_id: str | None = None) -> AlertProfile:
    """Load a profile from JSON and optionally verify its id."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    profile = AlertProfile.from_dict(payload)
    if profile_id and profile.id != profile_id:
        raise ValueError(f"profile id mismatch: expected {profile_id}, found {profile.id}")
    return profile


def create_profile(
    *,
    name: str,
    industries: Sequence[str] | None = None,
    keywords: Sequence[str] | None = None,
    locale: str = "he",
    environment: RuntimeEnvironment | str = RuntimeEnvironment.SANDBOX,
) -> AlertProfile:
    """Create a reusable monitoring profile."""
    return AlertProfile(name=name, industries=list(industries or []), keywords=list(keywords or []), locale=locale, environment=environment)


__all__ = [
    "AlertProfile",
    "RegulatoryFetchError",
    "RegulatoryMonitorClient",
    "RegulatoryParseError",
    "RegulatoryUpdate",
    "RuntimeEnvironment",
    "SourceType",
    "UpdateSource",
    "classify_severity",
    "classify_status",
    "create_profile",
    "deduplicate_updates",
    "default_sources",
    "detect_dates",
    "detect_shekel_amounts",
    "format_il_date",
    "infer_industries",
    "load_profile",
    "load_updates",
    "make_digest",
    "matches_filter",
    "normalize_title",
    "normalize_token",
    "parse_date",
    "save_default_config",
    "save_profile",
    "save_updates",
    "score_update",
    "stable_id",
    "strip_html",
    "summarize_update",
]
