"""Typed client for public data.gov.il CKAN endpoints.

The client uses only the Python standard library for HTTP transport. The
asynchronous wrapper keeps the same method names and delegates calls to worker
threads, which keeps dependencies small and predictable.
"""

from __future__ import annotations

import asyncio
import csv
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Union

JSONMapping = Dict[str, Any]
Filters = Optional[Mapping[str, Any]]
Fields = Optional[Union[str, Sequence[str]]]
DEFAULT_BASE_URL = "https://data.gov.il/api/3"
ENV_BASE_URLS = {
    "production": ("DATAGOVIL_BASE_URL", "DATAGOVIL_PRODUCTION_BASE_URL"),
    "sandbox": ("DATAGOVIL_SANDBOX_BASE_URL", "DATAGOVIL_BASE_URL_SANDBOX"),
}


class DatagovError(Exception):
    """Base exception for client errors."""


class DatagovHTTPError(DatagovError):
    """HTTP-level or connection-level error."""

    def __init__(self, status: Optional[int], message: str, body: str = "") -> None:
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {message}" if status else message)


class DatagovAPIError(DatagovError):
    """CKAN application-level error where success is false."""

    def __init__(self, error: Any) -> None:
        self.error = error
        super().__init__(f"CKAN API error: {error}")


class DatagovDecodeError(DatagovError):
    """Raised when the endpoint returns invalid or unexpected JSON."""


@dataclass(frozen=True)
class RequestConfig:
    """HTTP settings for data.gov.il requests."""

    base_url: str = DEFAULT_BASE_URL
    timeout: float = 30.0
    user_agent: str = "datagovil-explorer/2.2.0"
    max_retries: int = 2
    retry_backoff: float = 0.25


def base_url_for_env(env: str, default: str = DEFAULT_BASE_URL) -> str:
    """Return the base URL configured for production or sandbox."""

    normalized = env.strip().lower()
    if normalized not in ENV_BASE_URLS:
        raise ValueError("env must be sandbox or production")
    for name in ENV_BASE_URLS[normalized]:
        value = os.getenv(name)
        if value:
            return value.rstrip("/")
    return default.rstrip("/")


def _clean_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def _fields_to_string(fields: Fields) -> Optional[str]:
    if fields is None:
        return None
    if isinstance(fields, str):
        return fields
    return ",".join(str(field) for field in fields)


def _remove_none(params: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in params.items() if value is not None}


def parse_filter_pairs(pairs: Sequence[str]) -> Dict[str, str]:
    """Parse repeated key=value CLI filters into a dictionary."""

    filters: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Filter must be key=value: {pair}")
        key, value = pair.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Filter key is empty: {pair}")
        filters[key] = value.strip()
    return filters


def format_israeli_date(iso_date: str) -> str:
    """Format an ISO date or timestamp as DD/MM/YYYY."""

    if not iso_date or len(iso_date) < 10:
        return iso_date
    head = iso_date[:10]
    parts = head.split("-")
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        yyyy, mm, dd = parts
        return f"{dd}/{mm}/{yyyy}"
    return iso_date


def format_shekel(amount: Union[int, float, str]) -> str:
    """Format a number as Israeli shekel text."""

    value = float(str(amount).replace(",", "").replace("₪", "").strip())
    if value.is_integer():
        return f"₪{int(value):,}"
    return f"₪{value:,.2f}"


def extract_first_dataset_id(search_response: Mapping[str, Any]) -> Optional[str]:
    """Return the first dataset identifier from a package_search result."""

    results = search_response.get("results")
    if not isinstance(results, list) or not results:
        return None
    first = results[0]
    if not isinstance(first, Mapping):
        return None
    value = first.get("name") or first.get("id")
    return str(value) if value else None


def extract_first_resource_id(dataset_response: Mapping[str, Any], *, prefer_datastore: bool = True) -> Optional[str]:
    """Return the first useful resource id from a package_show result."""

    resources = dataset_response.get("resources")
    if not isinstance(resources, list):
        return None
    candidates = [item for item in resources if isinstance(item, Mapping)]
    if prefer_datastore:
        for item in candidates:
            if item.get("datastore_active") is True and item.get("id"):
                return str(item["id"])
    for item in candidates:
        if item.get("id"):
            return str(item["id"])
    return None


class DatagovClient:
    """Synchronous CKAN client for public data.gov.il endpoints."""

    def __init__(
        self,
        config: Optional[RequestConfig] = None,
        *,
        opener: Optional[Any] = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config or RequestConfig()
        self._opener = opener or urllib.request.build_opener()
        self._sleep = sleep

    def action_url(self, action: str, params: Optional[Mapping[str, Any]] = None) -> str:
        """Build an encoded CKAN action URL."""

        action_name = action.strip("/")
        if action_name.startswith("action/"):
            action_name = action_name.split("/", 1)[1]
        url = f"{_clean_base_url(self.config.base_url)}/action/{action_name}"
        clean_params = _remove_none(params or {})
        if clean_params:
            query = urllib.parse.urlencode(clean_params, doseq=True)
            url = f"{url}?{query}"
        return url

    def get_action(self, action: str, params: Optional[Mapping[str, Any]] = None) -> JSONMapping:
        """Call a CKAN action and return the unwrapped result object."""

        url = self.action_url(action, params)
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": self.config.user_agent},
            method="GET",
        )
        last_error: Optional[DatagovError] = None
        attempts = max(1, self.config.max_retries + 1)
        for attempt in range(attempts):
            try:
                with self._opener.open(request, timeout=self.config.timeout) as response:
                    body = response.read().decode("utf-8")
                payload = json.loads(body)
                return self._unwrap_response(payload)
            except urllib.error.HTTPError as exc:
                body = ""
                try:
                    body = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    body = ""
                if exc.code in {429, 500, 502, 503, 504} and attempt < attempts - 1:
                    self._sleep(self.config.retry_backoff * (attempt + 1))
                    continue
                raise DatagovHTTPError(exc.code, exc.reason, body) from exc
            except urllib.error.URLError as exc:
                last_error = DatagovHTTPError(None, f"Connection error: {exc.reason}")
                if attempt < attempts - 1:
                    self._sleep(self.config.retry_backoff * (attempt + 1))
                    continue
                raise last_error from exc
            except json.JSONDecodeError as exc:
                raise DatagovDecodeError(f"Invalid JSON response from {url}") from exc
        if last_error:
            raise last_error
        raise DatagovError("Request failed without a captured error")

    @staticmethod
    def _unwrap_response(payload: Any) -> JSONMapping:
        if not isinstance(payload, dict):
            raise DatagovDecodeError("Expected JSON object response")
        if payload.get("success") is not True:
            raise DatagovAPIError(payload.get("error", payload))
        result = payload.get("result", {})
        if isinstance(result, dict):
            return result
        return {"value": result}

    def package_search(
        self,
        query: str,
        *,
        rows: int = 10,
        start: int = 0,
        fq: Optional[str] = None,
        sort: Optional[str] = None,
        extras: Optional[Mapping[str, Any]] = None,
    ) -> JSONMapping:
        """Search datasets with package_search."""

        if rows < 0 or start < 0:
            raise ValueError("rows and start must be non-negative")
        params: Dict[str, Any] = {"q": query, "rows": rows, "start": start, "fq": fq, "sort": sort}
        if extras:
            params.update(extras)
        return self.get_action("package_search", params)

    def package_show(self, dataset_id: str) -> JSONMapping:
        """Return metadata for a dataset by name or id."""

        return self.get_action("package_show", {"id": dataset_id})

    def resource_show(self, resource_id: str) -> JSONMapping:
        """Return metadata for a resource by id."""

        return self.get_action("resource_show", {"id": resource_id})

    def organization_list(self, *, all_fields: bool = False) -> JSONMapping:
        """List publishing organizations."""

        return self.get_action("organization_list", {"all_fields": str(all_fields).lower()})

    def tag_list(self) -> JSONMapping:
        """List tags exposed by the portal."""

        return self.get_action("tag_list")

    def datastore_search(
        self,
        resource_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
        fields: Fields = None,
        filters: Filters = None,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        include_total: bool = True,
        records_format: str = "objects",
    ) -> JSONMapping:
        """Query records from a datastore-enabled resource."""

        if limit < 0 or offset < 0:
            raise ValueError("limit and offset must be non-negative")
        params: Dict[str, Any] = {
            "resource_id": resource_id,
            "limit": limit,
            "offset": offset,
            "fields": _fields_to_string(fields),
            "q": q,
            "sort": sort,
            "include_total": str(include_total).lower(),
            "records_format": records_format,
        }
        if filters:
            params["filters"] = json.dumps(dict(filters), ensure_ascii=False, separators=(",", ":"))
        return self.get_action("datastore_search", params)

    def datastore_search_all(
        self,
        resource_id: str,
        *,
        page_size: int = 1000,
        max_records: Optional[int] = None,
        fields: Fields = None,
        filters: Filters = None,
        q: Optional[str] = None,
        sort: str = "_id asc",
    ) -> Iterator[JSONMapping]:
        """Yield all records from a resource using offset pagination."""

        if page_size <= 0:
            raise ValueError("page_size must be positive")
        offset = 0
        yielded = 0
        while True:
            remaining = None if max_records is None else max_records - yielded
            if remaining is not None and remaining <= 0:
                return
            limit = page_size if remaining is None else min(page_size, remaining)
            result = self.datastore_search(
                resource_id,
                limit=limit,
                offset=offset,
                fields=fields,
                filters=filters,
                q=q,
                sort=sort,
            )
            records = result.get("records", [])
            if not isinstance(records, list) or not records:
                return
            for record in records:
                if isinstance(record, dict):
                    yield record
                    yielded += 1
                    if max_records is not None and yielded >= max_records:
                        return
            if len(records) < limit:
                return
            offset += len(records)

    @staticmethod
    def tabular_resources(dataset: Mapping[str, Any]) -> List[JSONMapping]:
        """Return resources likely to be useful for tabular analysis."""

        resources = dataset.get("resources", [])
        if not isinstance(resources, list):
            return []
        tabular: List[JSONMapping] = []
        for resource in resources:
            if not isinstance(resource, dict):
                continue
            fmt = str(resource.get("format") or "").upper()
            if resource.get("datastore_active") is True or fmt in {"CSV", "XLS", "XLSX", "TSV", "JSON"}:
                tabular.append(dict(resource))
        return tabular

    @staticmethod
    def write_csv(records: Iterable[Mapping[str, Any]], path: Union[str, Path], *, encoding: str = "utf-8-sig") -> int:
        """Write records to CSV and return the number of rows written."""

        output_path = Path(path)
        rows = [dict(record) for record in records]
        fieldnames: List[str] = []
        seen = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.add(key)
                    fieldnames.append(str(key))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding=encoding) as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return len(rows)


class AsyncDatagovClient:
    """Asynchronous wrapper around DatagovClient using asyncio.to_thread."""

    def __init__(self, client: Optional[DatagovClient] = None) -> None:
        self.client = client or DatagovClient()

    async def __aenter__(self) -> "AsyncDatagovClient":
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None

    async def get_action(self, action: str, params: Optional[Mapping[str, Any]] = None) -> JSONMapping:
        return await asyncio.to_thread(self.client.get_action, action, params)

    async def package_search(self, query: str, **kwargs: Any) -> JSONMapping:
        return await asyncio.to_thread(self.client.package_search, query, **kwargs)

    async def package_show(self, dataset_id: str) -> JSONMapping:
        return await asyncio.to_thread(self.client.package_show, dataset_id)

    async def resource_show(self, resource_id: str) -> JSONMapping:
        return await asyncio.to_thread(self.client.resource_show, resource_id)

    async def organization_list(self, *, all_fields: bool = False) -> JSONMapping:
        return await asyncio.to_thread(self.client.organization_list, all_fields=all_fields)

    async def tag_list(self) -> JSONMapping:
        return await asyncio.to_thread(self.client.tag_list)

    async def datastore_search(self, resource_id: str, **kwargs: Any) -> JSONMapping:
        return await asyncio.to_thread(self.client.datastore_search, resource_id, **kwargs)

    async def datastore_search_all(self, resource_id: str, **kwargs: Any) -> List[JSONMapping]:
        return await asyncio.to_thread(lambda: list(self.client.datastore_search_all(resource_id, **kwargs)))


__all__ = [
    "AsyncDatagovClient", "DEFAULT_BASE_URL", "DatagovAPIError",
    "DatagovClient", "DatagovDecodeError", "DatagovError",
    "DatagovHTTPError", "ENV_BASE_URLS", "Fields", "Filters",
    "JSONMapping", "RequestConfig", "base_url_for_env",
    "extract_first_dataset_id", "extract_first_resource_id",
    "format_israeli_date", "format_shekel", "parse_filter_pairs",
]
