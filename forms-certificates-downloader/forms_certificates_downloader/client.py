#!/usr/bin/env python3
"""Typed client for Israeli public form and certificate discovery."""
from __future__ import annotations

import asyncio
import csv
import dataclasses
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import html
import json
import mimetypes
import os
from pathlib import Path
import re
import ssl
import tempfile
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

try:
    from importlib import resources
except ImportError:  # pragma: no cover
    resources = None  # type: ignore[assignment]


DEFAULT_USER_AGENT = "forms-certificates-downloader/2.2.0 public-document-client"
DOCUMENT_EXTENSIONS = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".zip")
HEBREW_FINALS = str.maketrans({"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"})
ENVIRONMENTS = ("sandbox", "production")


class DownloaderError(RuntimeError):
    """Base exception for downloader failures."""


class SourceNotFoundError(DownloaderError):
    """Raised when a requested source does not exist in the registry."""


class FetchError(DownloaderError):
    """Raised when a URL cannot be fetched."""


class ParseError(DownloaderError):
    """Raised when a portal response cannot be parsed."""


class RequestNotFoundError(DownloaderError):
    """Raised when a saved request id cannot be found."""


@dataclass(frozen=True)
class PortalSource:
    """Public index page that can contain official form or certificate links."""

    name: str
    authority: str
    index_url: str
    portal_type: str = "public-index"
    language: str = "he"
    base_url: Optional[str] = None
    tags: Tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "PortalSource":
        return cls(
            name=str(value["name"]),
            authority=str(value["authority"]),
            index_url=str(value["index_url"]),
            portal_type=str(value.get("portal_type", "public-index")),
            language=str(value.get("language", "he")),
            base_url=str(value["base_url"]) if value.get("base_url") else None,
            tags=tuple(str(x) for x in value.get("tags", [])),
            notes=str(value.get("notes", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "authority": self.authority,
            "index_url": self.index_url,
            "portal_type": self.portal_type,
            "language": self.language,
            "base_url": self.base_url,
            "tags": list(self.tags),
            "notes": self.notes,
        }


@dataclass
class DocumentRecord:
    """Discovered or downloaded document record."""

    authority: str
    title: str
    source_url: str
    document_url: str
    document_type: str
    version_hint: Optional[str] = None
    checksum_sha256: Optional[str] = None
    fetched_at: Optional[str] = None
    path: Optional[str] = None
    size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        stable = normalize_key(self.document_url) or slugify(self.title)
        return f"{slugify(self.authority)}::{stable}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "authority": self.authority,
            "title": self.title,
            "source_url": self.source_url,
            "document_url": self.document_url,
            "document_type": self.document_type,
            "version_hint": self.version_hint,
            "checksum_sha256": self.checksum_sha256,
            "fetched_at": self.fetched_at,
            "path": self.path,
            "size_bytes": self.size_bytes,
            "metadata": self.metadata,
            "key": self.key,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "DocumentRecord":
        return cls(
            authority=str(value["authority"]),
            title=str(value["title"]),
            source_url=str(value["source_url"]),
            document_url=str(value["document_url"]),
            document_type=str(value.get("document_type", "unknown")),
            version_hint=value.get("version_hint"),
            checksum_sha256=value.get("checksum_sha256"),
            fetched_at=value.get("fetched_at"),
            path=value.get("path"),
            size_bytes=value.get("size_bytes"),
            metadata=dict(value.get("metadata", {})),
        )


@dataclass(frozen=True)
class VersionChange:
    """Version-tracking result for one document key."""

    status: str
    key: str
    title: str
    previous_checksum: Optional[str] = None
    current_checksum: Optional[str] = None
    previous_path: Optional[str] = None
    current_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class DownloadRequest:
    """Saved discovery/download request."""

    request_id: str
    source_name: str
    query: Optional[str]
    limit: int
    env: str = "production"
    created_at: str = field(default_factory=lambda: utc_now_iso())

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "DownloadRequest":
        return cls(
            request_id=str(value["request_id"]),
            source_name=str(value["source_name"]),
            query=str(value["query"]) if value.get("query") is not None else None,
            limit=int(value.get("limit", 20)),
            env=str(value.get("env", "production")),
            created_at=str(value.get("created_at") or utc_now_iso()),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "source_name": self.source_name,
            "query": self.query,
            "limit": self.limit,
            "env": self.env,
            "created_at": self.created_at,
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_hebrew(value: str) -> str:
    """Normalize Hebrew final letters and whitespace for query matching."""
    return re.sub(r"\s+", " ", value.strip().translate(HEBREW_FINALS)).lower()


def slugify(value: str, max_length: int = 90) -> str:
    value = html.unescape(unquote(value))
    value = normalize_hebrew(value)
    value = re.sub(r"https?://", "", value)
    value = re.sub(r"[^\w\u0590-\u05FF.-]+", "-", value, flags=re.UNICODE)
    value = value.strip("-_.") or "document"
    return value[:max_length].strip("-_.") or "document"


def normalize_key(url: str) -> str:
    parsed = urlparse(url)
    path = unquote(parsed.path or "")
    if parsed.scheme == "file":
        return slugify(Path(path).name)
    host = parsed.netloc.lower()
    clean_path = re.sub(r"/+", "/", path).strip("/")
    return slugify(f"{host}/{clean_path}")


def sanitize_filename(title: str, extension: str = "") -> str:
    extension = extension or ""
    if extension and not extension.startswith("."):
        extension = "." + extension
    base = slugify(title, max_length=110)
    if extension and not base.lower().endswith(extension.lower()):
        base += extension
    return base


def detect_document_type(url: str, content_type: Optional[str] = None) -> str:
    url_path = urlparse(url).path.lower()
    suffix = Path(unquote(url_path)).suffix.lower()
    content_type = (content_type or "").lower()
    if suffix == ".pdf" or "application/pdf" in content_type:
        return "pdf"
    if suffix in {".doc", ".docx"} or "word" in content_type:
        return "word"
    if suffix in {".xls", ".xlsx", ".csv"} or "spreadsheet" in content_type or "excel" in content_type:
        return "spreadsheet"
    if suffix == ".zip" or "zip" in content_type:
        return "archive"
    return "html" if "html" in content_type else "unknown"


def extract_version_hint(title_or_url: str) -> Optional[str]:
    text = html.unescape(unquote(title_or_url))
    patterns = [
        r"(?:גרסה|מהדורה|version|v\.?)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+){0,3})",
        r"(?:עודכן|עדכון|updated|revision)\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
        r"\b(20[0-9]{2})\b",
        r"\b([0-9]{2}-[0-9]{4})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def validate_teudat_zehut(id_number: str) -> bool:
    """Return True when the value is a structurally valid Israeli identity number."""
    value = re.sub(r"\D", "", id_number or "")
    if not value:
        return False
    value = value.zfill(9)
    if len(value) != 9 or value == "000000000":
        return False
    total = 0
    for index, char in enumerate(value):
        digit = int(char)
        weight = 1 if index % 2 == 0 else 2
        product = digit * weight
        total += product if product < 10 else product - 9
    return total % 10 == 0


def normalize_israeli_phone(phone: str) -> Dict[str, Any]:
    """Validate and normalize Israeli mobile and landline numbers."""
    original = phone
    cleaned = re.sub(r"[\s().-]", "", phone or "")
    if cleaned.startswith("+972"):
        cleaned = "0" + cleaned[4:]
    elif cleaned.startswith("972"):
        cleaned = "0" + cleaned[3:]
    if re.fullmatch(r"05[0-9]{8}", cleaned):
        return {
            "valid": True,
            "type": "mobile",
            "local": f"{cleaned[:3]}-{cleaned[3:]}",
            "international": f"+972-{cleaned[1:3]}-{cleaned[3:]}",
            "digits": cleaned,
            "input": original,
        }
    if re.fullmatch(r"0[2-9][0-9]{7}", cleaned):
        return {
            "valid": True,
            "type": "landline",
            "local": f"{cleaned[:2]}-{cleaned[2:]}",
            "international": f"+972-{cleaned[1:2]}-{cleaned[2:]}",
            "digits": cleaned,
            "input": original,
        }
    return {"valid": False, "error": "Invalid Israeli phone number", "input": original}


def validate_mikud(value: str) -> bool:
    """Return True for seven-digit Israeli postal codes."""
    return bool(re.fullmatch(r"\d{7}", re.sub(r"\D", "", value or "")))


def looks_like_document_url(url: str, extensions: Sequence[str] = DOCUMENT_EXTENSIONS) -> bool:
    path = unquote(urlparse(url).path).lower()
    return any(path.endswith(ext.lower()) for ext in extensions)


def query_matches(text: str, query: Optional[str]) -> bool:
    if not query:
        return True
    haystack = normalize_hebrew(text)
    for token in normalize_hebrew(query).split():
        if token and token not in haystack:
            return False
    return True


def parse_anchor_candidates(
    html_text: str,
    base_url: str,
    extensions: Sequence[str] = DOCUMENT_EXTENSIONS,
) -> List[Tuple[str, str]]:
    """Extract document-looking links from an HTML page."""
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ParseError("BeautifulSoup is required for HTML discovery") from exc

    soup = BeautifulSoup(html_text, "html.parser")
    candidates: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        if not href:
            continue
        absolute = urljoin(base_url, href)
        if not looks_like_document_url(absolute, extensions):
            continue
        text = " ".join(anchor.get_text(" ", strip=True).split())
        if not text:
            text = Path(unquote(urlparse(absolute).path)).name or absolute
        if absolute in seen:
            continue
        seen.add(absolute)
        candidates.append((text, absolute))
    return candidates


def _read_file_url(url: str) -> Tuple[bytes, Dict[str, str]]:
    parsed = urlparse(url)
    path = Path(unquote(parsed.path))
    data = path.read_bytes()
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return data, {"content-type": ctype, "content-length": str(len(data))}


def default_fetcher(url: str, timeout: float, user_agent: str) -> Tuple[bytes, Dict[str, str]]:
    """Fetch a URL and return bytes plus lowercase response headers."""
    parsed = urlparse(url)
    if parsed.scheme == "file":
        return _read_file_url(url)
    if parsed.scheme not in {"http", "https"}:
        raise FetchError(f"Unsupported URL scheme: {parsed.scheme}")
    request = Request(url, headers={"User-Agent": user_agent, "Accept": "*/*"})
    try:
        context = ssl.create_default_context()
        with urlopen(request, timeout=timeout, context=context) as response:
            data = response.read()
            headers = {k.lower(): v for k, v in response.headers.items()}
            return data, headers
    except HTTPError as exc:
        raise FetchError(f"HTTP {exc.code} while fetching {url}") from exc
    except URLError as exc:
        raise FetchError(f"Network error while fetching {url}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise FetchError(f"Timeout while fetching {url}") from exc


def _package_registry_path() -> Optional[Path]:
    if resources is None:
        return None
    try:
        resource = resources.files("forms_certificates_downloader.data").joinpath("portal-registry.json")
        with resources.as_file(resource) as path:
            return Path(path)
    except Exception:
        return None


def _hardcoded_registry() -> List[PortalSource]:
    return [
        PortalSource(
            name='tax-authority-gov-il',
            authority='Israel Tax Authority',
            index_url='https://www.gov.il/he/departments/israel_tax_authority',
            base_url='https://www.gov.il',
            tags=('tax', 'vat', 'income-tax', 'certificates', 'forms'),
            notes='Current public Tax Authority department page. Use public discovery only; authenticated filing and private certificates remain manual.',
        ),
        PortalSource(
            name='tax-authority-public-forms',
            authority='Israel Tax Authority',
            index_url='https://www.gov.il/he/departments/topics/income_tax_israel_tax_authority',
            base_url='https://www.gov.il',
            tags=('tax', 'income-tax', 'forms', 'tofes', 'freelancer', 'annual-report'),
            notes='Current public income-tax topic page. Use focused queries such as 1301, 106, 1214, or the Hebrew form name.',
        ),
        PortalSource(
            name='bituach-leumi-forms',
            authority='National Insurance Institute',
            index_url='https://www.btl.gov.il/טפסים%20ואישורים/forms/Pages/default.aspx',
            base_url='https://www.btl.gov.il',
            tags=('national-insurance', 'benefits', 'forms', 'consumer', 'employers'),
            notes='Public National Insurance forms. Some forms can be filled online, but automated submission is out of scope.',
        ),
        PortalSource(
            name='bituach-leumi-certificates',
            authority='National Insurance Institute',
            index_url='https://www.btl.gov.il/טפסים%20ואישורים/אישורים/Pages/default.aspx',
            base_url='https://www.btl.gov.il',
            tags=('national-insurance', 'certificates', 'benefits', 'consumer'),
            notes='Public certificate information page. Certificates that require the personal service site remain manual.',
        ),
        PortalSource(
            name='gov-il-services',
            authority='Government Services Portal',
            index_url='https://www.gov.il/he/services',
            base_url='https://www.gov.il',
            tags=('gov-il', 'services', 'ministries', 'public-index', 'certificates'),
            notes='General services and information page. Use a query and a small limit to avoid broad discovery.',
        ),
        PortalSource(
            name='corporations-authority',
            authority='Corporations Authority',
            index_url='https://www.gov.il/he/departments/israeli_corporations_authority',
            base_url='https://www.gov.il',
            tags=('companies', 'amuta', 'registrar', 'forms', 'small-business', 'nonprofits'),
            notes='Current public Corporations Authority department page. Authenticated filings and paid company-file review remain manual.',
        )
    ]

def load_registry(path: os.PathLike[str] | str) -> List[PortalSource]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    items = raw["sources"] if isinstance(raw, dict) and "sources" in raw else raw
    return [PortalSource.from_dict(item) for item in items]


def default_registry() -> List[PortalSource]:
    """Return package default sources for major public Israeli indexes."""
    path = _package_registry_path()
    if path and path.exists():
        try:
            return load_registry(path)
        except Exception:
            return _hardcoded_registry()
    return _hardcoded_registry()


def save_registry(path: os.PathLike[str] | str, sources: Sequence[PortalSource]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"sources": [source.to_dict() for source in sources]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output


class FormsCertificatesClient:
    """Sync and async client for public forms/certificates discovery and tracking."""

    def __init__(
        self,
        download_dir: os.PathLike[str] | str,
        manifest_path: os.PathLike[str] | str | None = None,
        registry: Sequence[PortalSource] | None = None,
        timeout: float = 30.0,
        user_agent: str = DEFAULT_USER_AGENT,
        fetcher: Optional[Callable[[str, float, str], Tuple[bytes, Dict[str, str]]]] = None,
        env: str = "production",
    ) -> None:
        if env not in ENVIRONMENTS:
            raise ValueError(f"env must be one of: {', '.join(ENVIRONMENTS)}")
        self.env = env
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = Path(manifest_path) if manifest_path else self.download_dir / "manifest.json"
        self.requests_dir = self.download_dir / "requests"
        self.registry = {source.name: source for source in (registry or default_registry())}
        self.timeout = timeout
        self.user_agent = user_agent
        self.fetcher = fetcher or default_fetcher

    @classmethod
    def from_registry_path(
        cls,
        download_dir: os.PathLike[str] | str,
        registry_path: os.PathLike[str] | str,
        **kwargs: Any,
    ) -> "FormsCertificatesClient":
        return cls(download_dir=download_dir, registry=load_registry(registry_path), **kwargs)

    def list_sources(self) -> List[PortalSource]:
        return sorted(self.registry.values(), key=lambda source: source.name)

    def get_source(self, name: str) -> PortalSource:
        try:
            return self.registry[name]
        except KeyError as exc:
            raise SourceNotFoundError(f"Unknown source: {name}") from exc

    def load_manifest(self) -> Dict[str, Any]:
        if not self.manifest_path.exists():
            return {"schema_version": 1, "updated_at": None, "documents": {}}
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def save_manifest(self, manifest: Mapping[str, Any]) -> None:
        payload = dict(manifest)
        payload["schema_version"] = int(payload.get("schema_version", 1))
        payload["updated_at"] = utc_now_iso()
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.manifest_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.manifest_path)

    def fetch(self, url: str) -> Tuple[bytes, Dict[str, str]]:
        return self.fetcher(url, self.timeout, self.user_agent)

    async def async_fetch(self, url: str) -> Tuple[bytes, Dict[str, str]]:
        return await asyncio.to_thread(self.fetch, url)

    def discover(
        self,
        source_name: str,
        query: Optional[str] = None,
        extensions: Sequence[str] = DOCUMENT_EXTENSIONS,
        max_results: int = 100,
    ) -> List[DocumentRecord]:
        source = self.get_source(source_name)
        data, headers = self.fetch(source.index_url)
        content_type = headers.get("content-type", "")
        base_url = source.base_url or source.index_url
        stripped = data[:4096].lstrip().lower()
        if looks_like_document_url(source.index_url, extensions):
            title = Path(unquote(urlparse(source.index_url).path)).name or source.name
            records = [(title, source.index_url)]
        elif "html" in content_type or source.index_url.startswith("file:") or stripped.startswith(b"<!doctype") or b"<a " in stripped:
            text = data.decode("utf-8", errors="replace")
            records = parse_anchor_candidates(text, base_url=base_url, extensions=extensions)
        else:
            raise ParseError(f"Unsupported index content type for {source.index_url}: {content_type or 'unknown'}")

        results: List[DocumentRecord] = []
        for title, url in records:
            combined = f"{title} {url}"
            if not query_matches(combined, query):
                continue
            doc_type = detect_document_type(url)
            results.append(
                DocumentRecord(
                    authority=source.authority,
                    title=title,
                    source_url=source.index_url,
                    document_url=url,
                    document_type=doc_type,
                    version_hint=extract_version_hint(combined),
                    metadata={"source_name": source.name, "tags": list(source.tags), "env": self.env},
                )
            )
            if len(results) >= max_results:
                break
        return results

    async def async_discover(
        self,
        source_name: str,
        query: Optional[str] = None,
        extensions: Sequence[str] = DOCUMENT_EXTENSIONS,
        max_results: int = 100,
    ) -> List[DocumentRecord]:
        return await asyncio.to_thread(self.discover, source_name, query, extensions, max_results)

    def download(self, record: DocumentRecord, filename: Optional[str] = None) -> DocumentRecord:
        data, headers = self.fetch(record.document_url)
        content_type = headers.get("content-type")
        doc_type = detect_document_type(record.document_url, content_type)
        ext = Path(unquote(urlparse(record.document_url).path)).suffix
        if not ext:
            guessed = mimetypes.guess_extension(content_type or "")
            ext = guessed or (".pdf" if doc_type == "pdf" else ".bin")
        authority_dir = self.download_dir / slugify(record.authority)
        authority_dir.mkdir(parents=True, exist_ok=True)
        output_name = filename or sanitize_filename(record.title, ext)
        output_path = authority_dir / output_name
        with tempfile.NamedTemporaryFile(delete=False, dir=str(authority_dir)) as handle:
            handle.write(data)
            tmp_name = handle.name
        Path(tmp_name).replace(output_path)
        record.checksum_sha256 = sha256_bytes(data)
        record.fetched_at = utc_now_iso()
        record.path = str(output_path)
        record.size_bytes = len(data)
        record.document_type = doc_type
        return record

    async def async_download(self, record: DocumentRecord, filename: Optional[str] = None) -> DocumentRecord:
        return await asyncio.to_thread(self.download, record, filename)

    def track_records(self, records: Iterable[DocumentRecord]) -> List[VersionChange]:
        manifest = self.load_manifest()
        docs: Dict[str, Any] = dict(manifest.get("documents", {}))
        changes: List[VersionChange] = []
        for record in records:
            if not record.checksum_sha256:
                raise DownloaderError(f"Record has no checksum; download before tracking: {record.title}")
            previous = docs.get(record.key)
            if previous is None:
                changes.append(
                    VersionChange(
                        status="added",
                        key=record.key,
                        title=record.title,
                        current_checksum=record.checksum_sha256,
                        current_path=record.path,
                    )
                )
            elif previous.get("checksum_sha256") != record.checksum_sha256:
                changes.append(
                    VersionChange(
                        status="updated",
                        key=record.key,
                        title=record.title,
                        previous_checksum=previous.get("checksum_sha256"),
                        current_checksum=record.checksum_sha256,
                        previous_path=previous.get("path"),
                        current_path=record.path,
                    )
                )
            else:
                changes.append(
                    VersionChange(
                        status="unchanged",
                        key=record.key,
                        title=record.title,
                        previous_checksum=previous.get("checksum_sha256"),
                        current_checksum=record.checksum_sha256,
                        previous_path=previous.get("path"),
                        current_path=record.path,
                    )
                )
            docs[record.key] = record.to_dict()
        manifest["documents"] = docs
        self.save_manifest(manifest)
        return changes

    def refresh_source(
        self,
        source_name: str,
        query: Optional[str] = None,
        max_results: int = 100,
    ) -> Tuple[List[DocumentRecord], List[VersionChange]]:
        discovered = self.discover(source_name, query=query, max_results=max_results)
        downloaded = [self.download(record) for record in discovered]
        return downloaded, self.track_records(downloaded)

    async def async_refresh_source(
        self,
        source_name: str,
        query: Optional[str] = None,
        max_results: int = 100,
    ) -> Tuple[List[DocumentRecord], List[VersionChange]]:
        discovered = await self.async_discover(source_name, query=query, max_results=max_results)
        downloaded = await asyncio.gather(*(self.async_download(record) for record in discovered))
        return list(downloaded), self.track_records(downloaded)

    def refresh_all(self, query: Optional[str] = None, max_results_per_source: int = 100) -> Tuple[List[DocumentRecord], List[VersionChange]]:
        all_records: List[DocumentRecord] = []
        all_changes: List[VersionChange] = []
        for source in self.list_sources():
            records, changes = self.refresh_source(source.name, query=query, max_results=max_results_per_source)
            all_records.extend(records)
            all_changes.extend(changes)
        return all_records, all_changes

    def find_manifest_records(self, query: str, authority: Optional[str] = None) -> List[DocumentRecord]:
        manifest = self.load_manifest()
        results: List[DocumentRecord] = []
        for raw in manifest.get("documents", {}).values():
            record = DocumentRecord.from_dict(raw)
            if authority and normalize_hebrew(authority) not in normalize_hebrew(record.authority):
                continue
            if query_matches(f"{record.title} {record.document_url} {record.authority}", query):
                results.append(record)
        return results

    def export_manifest_csv(self, output_path: os.PathLike[str] | str) -> Path:
        manifest = self.load_manifest()
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = [DocumentRecord.from_dict(raw).to_dict() for raw in manifest.get("documents", {}).values()]
        fields = [
            "key",
            "authority",
            "title",
            "document_type",
            "version_hint",
            "checksum_sha256",
            "fetched_at",
            "size_bytes",
            "source_url",
            "document_url",
            "path",
        ]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field) for field in fields})
        return path

    def create_download_request(
        self,
        source_name: str,
        query: Optional[str] = None,
        limit: int = 20,
        env: Optional[str] = None,
    ) -> DownloadRequest:
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        self.get_source(source_name)
        request_env = env or self.env
        if request_env not in ENVIRONMENTS:
            raise ValueError(f"env must be one of: {', '.join(ENVIRONMENTS)}")
        request = DownloadRequest(
            request_id=uuid4().hex,
            source_name=source_name,
            query=query,
            limit=limit,
            env=request_env,
        )
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        path = self.requests_dir / f"{request.request_id}.json"
        path.write_text(json.dumps(request.to_dict(), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return request

    def load_download_request(self, request_id: str) -> DownloadRequest:
        if not re.fullmatch(r"[a-f0-9]{32}", request_id or ""):
            raise RequestNotFoundError(f"Invalid request id: {request_id}")
        path = self.requests_dir / f"{request_id}.json"
        if not path.exists():
            raise RequestNotFoundError(f"Unknown request id: {request_id}")
        return DownloadRequest.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def run_download_request(self, request_id: str, track: bool = True) -> Dict[str, Any]:
        request = self.load_download_request(request_id)
        records = self.discover(request.source_name, query=request.query, max_results=request.limit)
        downloaded = [self.download(record) for record in records]
        changes = self.track_records(downloaded) if track else []
        return {
            "request_id": request.request_id,
            "source_name": request.source_name,
            "query": request.query,
            "env": request.env,
            "downloaded": [record.to_dict() for record in downloaded],
            "changes": [change.to_dict() for change in changes],
        }


__all__ = [
    "DOCUMENT_EXTENSIONS",
    "ENVIRONMENTS",
    "PortalSource",
    "DocumentRecord",
    "VersionChange",
    "DownloadRequest",
    "FormsCertificatesClient",
    "DownloaderError",
    "SourceNotFoundError",
    "FetchError",
    "ParseError",
    "RequestNotFoundError",
    "default_registry",
    "load_registry",
    "save_registry",
    "validate_teudat_zehut",
    "validate_mikud",
    "normalize_israeli_phone",
    "parse_anchor_candidates",
    "extract_version_hint",
    "detect_document_type",
    "sanitize_filename",
    "sha256_bytes",
    "query_matches",
]
