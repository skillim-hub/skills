#!/usr/bin/env python3
"""Typed client helpers for Israeli CBS data analysis.

The module supports synchronous and asynchronous calls to the CBS Price Indices
API and data.gov.il CKAN search. Calculations are deterministic and testable
without live network access by injecting an httpx transport.
"""

from __future__ import annotations

import asyncio
import csv
import datetime as _dt
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urljoin

import httpx

CBS_INDEX_API_BASE = "https://api.cbs.gov.il/index"
DATA_GOV_API_BASE = "https://data.gov.il/api/3/action"

KNOWN_INDEXES: dict[str, int] = {
    "cpi": 120010,
    "consumer_price_index": 120010,
    "madad": 120010,
    "housing": 40010,
    "apartment_prices": 40010,
    "producer_prices": 170030,
    "ppi": 170030,
    "building_input": 200010,
}

MONTH_NAME_TO_NUMBER = {
    "january": 1,
    "jan": 1,
    "ינואר": 1,
    "february": 2,
    "feb": 2,
    "פברואר": 2,
    "march": 3,
    "mar": 3,
    "מרץ": 3,
    "april": 4,
    "apr": 4,
    "אפריל": 4,
    "may": 5,
    "מאי": 5,
    "june": 6,
    "jun": 6,
    "יוני": 6,
    "july": 7,
    "jul": 7,
    "יולי": 7,
    "august": 8,
    "aug": 8,
    "אוגוסט": 8,
    "september": 9,
    "sep": 9,
    "ספטמבר": 9,
    "october": 10,
    "oct": 10,
    "אוקטובר": 10,
    "november": 11,
    "nov": 11,
    "נובמבר": 11,
    "december": 12,
    "dec": 12,
    "דצמבר": 12,
}


class CBSAPIError(RuntimeError):
    """Raised when an official data endpoint fails or returns unusable data."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        url: str | None = None,
        response_text: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.response_text = response_text


@dataclass(slots=True)
class CBSDataPoint:
    """One normalized index observation."""

    period: str
    year: int | None
    month: int | None
    value: float | None
    monthly_change: float | None = None
    annual_change: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def sortable_key(self) -> tuple[int, int]:
        """Return a safe key for chronological sorting."""
        return (self.year or 0, self.month or 0)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CBSSeries:
    """One normalized CBS index series."""

    code: int | str | None
    name: str
    points: list[CBSDataPoint]
    source_url: str
    retrieved_at: str
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def latest(self) -> CBSDataPoint | None:
        """Return the latest point by year and month when possible."""
        valid = [point for point in self.points if point.year is not None or point.month is not None]
        if valid:
            return max(valid, key=lambda point: point.sortable_key)
        return self.points[0] if self.points else None

    def recent(self, limit: int = 6) -> list[CBSDataPoint]:
        """Return recent points sorted newest first."""
        return sorted(self.points, key=lambda point: point.sortable_key, reverse=True)[:limit]

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "points": [point.to_dict() for point in self.points],
            "source_url": self.source_url,
            "retrieved_at": self.retrieved_at,
        }


@dataclass(slots=True)
class IndexationResult:
    """Result of an indexation calculation."""

    original_amount: float
    base_index: float
    target_index: float
    effective_target_index: float
    adjusted_amount: float
    difference: float
    percent_change: float
    formula: str
    floor_applied: bool = False
    rounded_to_shekel: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _today_iso() -> str:
    return _dt.date.today().isoformat()


def _to_float(value: Any) -> float | None:
    """Convert API number-like values into floats."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if math.isnan(value) if isinstance(value, float) else False:
            return None
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if cleaned in {"", "-", "—", "null", "None"}:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _extract_value(record: Mapping[str, Any]) -> float | None:
    """Extract the index value from common CBS response shapes."""
    for key in ("value", "index", "currBaseValue"):
        value = _to_float(record.get(key))
        if value is not None:
            return value

    curr_base = record.get("currBase")
    if isinstance(curr_base, Mapping):
        value = _to_float(curr_base.get("value"))
        if value is not None:
            return value

    bases = record.get("base")
    if isinstance(bases, Sequence) and not isinstance(bases, (str, bytes)):
        for base in bases:
            if isinstance(base, Mapping):
                value = _to_float(base.get("value"))
                if value is not None:
                    return value

    return None


def _extract_year(record: Mapping[str, Any]) -> int | None:
    for key in ("year", "Year", "periodYear"):
        raw = _to_float(record.get(key))
        if raw is not None:
            return int(raw)
    return None


def _extract_month(record: Mapping[str, Any]) -> int | None:
    for key in ("month", "Month", "periodMonth"):
        raw = _to_float(record.get(key))
        if raw is not None and 1 <= int(raw) <= 12:
            return int(raw)

    month_desc = record.get("monthDesc") or record.get("monthName") or record.get("monthHeb")
    if isinstance(month_desc, str):
        normalized = month_desc.strip().lower()
        return MONTH_NAME_TO_NUMBER.get(normalized)
    return None


def _period_label(record: Mapping[str, Any], year: int | None, month: int | None) -> str:
    for key in ("period", "date", "periodLabel"):
        value = record.get(key)
        if value:
            return str(value)

    month_desc = record.get("monthDesc") or record.get("monthName")
    if year and month:
        return f"{month:02d}-{year}"
    if year and month_desc:
        return f"{month_desc} {year}"
    if year:
        return str(year)
    return "unknown"


def _series_entries(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Return series containers from known CBS response shapes."""
    candidates: list[Any] = []
    for key in ("month", "data", "series", "results"):
        value = payload.get(key)
        if value:
            candidates.append(value)

    for candidate in candidates:
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, Mapping)]
        if isinstance(candidate, Mapping):
            return [candidate]

    if "date" in payload:
        return [payload]
    return []


def parse_price_series(
    payload: Mapping[str, Any],
    *,
    index_id: int | str | None = None,
    source_url: str = "",
    retrieved_at: str | None = None,
) -> CBSSeries:
    """Normalize a CBS Price Indices API payload into a CBSSeries."""
    series_entries = _series_entries(payload)
    if not series_entries:
        return CBSSeries(
            code=index_id,
            name="unknown",
            points=[],
            source_url=source_url,
            retrieved_at=retrieved_at or _today_iso(),
            raw=dict(payload),
        )

    selected = series_entries[0]
    raw_points = selected.get("date") or selected.get("points") or selected.get("values") or []
    if isinstance(raw_points, Mapping):
        raw_points = [raw_points]
    if not isinstance(raw_points, list):
        raw_points = []

    code = selected.get("code") or selected.get("mainCode") or index_id
    name = str(selected.get("name") or selected.get("chapterName") or selected.get("title") or "CBS index")
    points: list[CBSDataPoint] = []

    for item in raw_points:
        if not isinstance(item, Mapping):
            continue
        year = _extract_year(item)
        month = _extract_month(item)
        value = _extract_value(item)
        monthly_change = _to_float(item.get("percent") or item.get("monthlyChange"))
        annual_change = _to_float(item.get("percentYear") or item.get("annualChange"))
        points.append(
            CBSDataPoint(
                period=_period_label(item, year, month),
                year=year,
                month=month,
                value=value,
                monthly_change=monthly_change,
                annual_change=annual_change,
                raw=dict(item),
            )
        )

    return CBSSeries(
        code=code,
        name=name,
        points=points,
        source_url=source_url,
        retrieved_at=retrieved_at or _today_iso(),
        raw=dict(payload),
    )


def calculate_indexation(
    *,
    original_amount: float,
    base_index: float,
    target_index: float,
    floor_zero: bool = False,
    round_to_shekel: bool = False,
) -> IndexationResult:
    """Calculate an index-linked amount using index levels."""
    if original_amount < 0:
        raise ValueError("original_amount must be non-negative")
    if base_index <= 0:
        raise ValueError("base_index must be positive")
    if target_index <= 0:
        raise ValueError("target_index must be positive")

    effective_target = max(base_index, target_index) if floor_zero else target_index
    ratio = effective_target / base_index
    raw_adjusted = original_amount * ratio
    adjusted = round(raw_adjusted) if round_to_shekel else raw_adjusted
    difference = adjusted - original_amount
    percent_change = (ratio - 1) * 100
    notes: list[str] = [
        "Use only when the agreement names this index and does not override the formula."
    ]
    if floor_zero and target_index < base_index:
        notes.append("Floor applied: target index below base index, so the original amount was preserved.")
    if round_to_shekel:
        notes.append("Rounded to the nearest shekel at the final step.")

    return IndexationResult(
        original_amount=float(original_amount),
        base_index=float(base_index),
        target_index=float(target_index),
        effective_target_index=float(effective_target),
        adjusted_amount=float(adjusted),
        difference=float(difference),
        percent_change=float(percent_change),
        formula=f"{original_amount} × ({effective_target} / {base_index})",
        floor_applied=bool(floor_zero and target_index < base_index),
        rounded_to_shekel=round_to_shekel,
        notes=notes,
    )


def format_nis(amount: float, *, decimals: int = 2) -> str:
    """Format a shekel amount for Israeli-facing output."""
    return f"₪{amount:,.{decimals}f}"


def detect_trend(points: Sequence[CBSDataPoint], *, tolerance: float = 0.05) -> str:
    """Detect a simple direction from recent points."""
    usable = [point for point in sorted(points, key=lambda p: p.sortable_key) if point.value is not None]
    if len(usable) < 2:
        return "insufficient-data"
    first = usable[0].value or 0
    last = usable[-1].value or 0
    pct = ((last / first) - 1) * 100 if first else 0
    if pct > tolerance:
        return "rising"
    if pct < -tolerance:
        return "falling"
    return "stable"


def build_market_brief(
    *,
    question: str,
    geography: str,
    series: CBSSeries | None = None,
    assumptions: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Create a structured planning brief from available CBS evidence."""
    latest = series.latest if series else None
    trend = detect_trend(series.points[-6:] if series else [])
    return {
        "question": question,
        "geography": geography,
        "retrieved_at": _today_iso(),
        "series": series.name if series else None,
        "series_code": series.code if series else None,
        "latest_period": latest.period if latest else None,
        "latest_value": latest.value if latest else None,
        "trend": trend,
        "signals": [
            {
                "name": "price_pressure",
                "interpretation": (
                    "Recent index values suggest upward price pressure."
                    if trend == "rising"
                    else "Recent index values do not show upward pressure."
                    if trend in {"falling", "stable"}
                    else "More data is required."
                ),
            },
            {
                "name": "geography",
                "interpretation": (
                    f"Use CBS locality or district data for {geography}; add field research for competition."
                ),
            },
        ],
        "assumptions": list(assumptions or []),
        "limitations": [
            "CBS data may have publication lag and revisions.",
            "A market brief is not a revenue forecast, legal opinion, tax opinion, or valuation.",
        ],
    }


class CBSDataAnalyzerClient:
    """Synchronous client for CBS and data.gov.il workflows."""

    def __init__(
        self,
        *,
        cbs_base_url: str = CBS_INDEX_API_BASE,
        data_gov_base_url: str = DATA_GOV_API_BASE,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.cbs_base_url = cbs_base_url.rstrip("/")
        self.data_gov_base_url = data_gov_base_url.rstrip("/")
        default_headers = {
            "Accept": "application/json",
            "User-Agent": "cbs-data-analyzer/2.2",
        }
        if headers:
            default_headers.update(headers)
        self._client = httpx.Client(timeout=timeout, transport=transport, headers=default_headers)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "CBSDataAnalyzerClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _get_json(self, url: str, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        try:
            response = self._client.get(url, params=params)
        except httpx.HTTPError as exc:
            raise CBSAPIError(f"Request failed: {exc}", url=url) from exc

        if response.status_code >= 400:
            raise CBSAPIError(
                f"Endpoint returned HTTP {response.status_code}",
                status_code=response.status_code,
                url=str(response.url),
                response_text=response.text[:500],
            )

        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise CBSAPIError(
                "Endpoint did not return valid JSON",
                status_code=response.status_code,
                url=str(response.url),
                response_text=response.text[:500],
            ) from exc

        if not isinstance(data, dict):
            raise CBSAPIError(
                "Endpoint returned JSON that is not an object",
                status_code=response.status_code,
                url=str(response.url),
                response_text=response.text[:500],
            )
        return data

    def get_catalog(self) -> dict[str, Any]:
        """Fetch the CBS Price Indices catalog."""
        url = f"{self.cbs_base_url}/catalog/catalog"
        return self._get_json(url, {"format": "json"})

    def search_catalog(self, query: str) -> list[dict[str, Any]]:
        """Search the CBS Price Indices catalog by name, code, or text."""
        q = query.strip().lower()
        if not q:
            return []
        catalog = self.get_catalog()
        chapters = catalog.get("chapters") or catalog.get("result") or []
        if not isinstance(chapters, list):
            return []
        matches: list[dict[str, Any]] = []
        for item in chapters:
            if not isinstance(item, Mapping):
                continue
            searchable = " ".join(str(value) for value in item.values() if value is not None).lower()
            if q in searchable:
                matches.append(dict(item))
        return matches

    def get_price_index(
        self,
        index_id: int | str,
        *,
        start_period: str | None = None,
        end_period: str | None = None,
        last: int | None = None,
        coef: bool | None = None,
        download: bool = False,
    ) -> CBSSeries:
        """Fetch one CBS price-index series by mainCode.

        The CBS Price Indices API documents ``startPeriod`` and ``endPeriod``
        as ``mm-yyyy`` strings, ``last`` as a positive count of recent objects,
        and ``coef`` as a flag for chaining coefficients.
        """
        url = f"{self.cbs_base_url}/data/price"
        params: dict[str, Any] = {"id": index_id, "format": "json", "download": str(download).lower()}
        if start_period:
            params["startPeriod"] = start_period
        if end_period:
            params["endPeriod"] = end_period
        if last is not None:
            if last <= 0:
                raise ValueError("last must be positive")
            params["last"] = last
        if coef is not None:
            params["coef"] = str(coef).lower()
        data = self._get_json(url, params)
        source = str(httpx.URL(url, params={key: str(value) for key, value in params.items()}))
        return parse_price_series(data, index_id=index_id, source_url=source)

    def get_known_index(self, key: str) -> CBSSeries:
        """Fetch a known common index by key."""
        normalized = key.strip().lower().replace("-", "_")
        if normalized not in KNOWN_INDEXES:
            raise KeyError(f"Unknown index key: {key}")
        return self.get_price_index(KNOWN_INDEXES[normalized])

    def latest_price(self, index_id: int | str) -> CBSDataPoint | None:
        """Fetch the latest point for a price index."""
        return self.get_price_index(index_id).latest

    def search_data_gov(
        self,
        query: str,
        *,
        rows: int = 10,
        organization: str = "lamas",
    ) -> dict[str, Any]:
        """Search data.gov.il datasets, filtered to the CBS organization by default."""
        url = f"{self.data_gov_base_url}/package_search"
        params = {"q": query, "rows": rows, "fq": f"organization:{organization}"}
        return self._get_json(url, params)

    def export_series_csv(self, series: CBSSeries, path: str | Path) -> Path:
        """Write a normalized series to CSV."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["period", "year", "month", "value", "monthly_change", "annual_change"],
            )
            writer.writeheader()
            for point in series.points:
                writer.writerow(
                    {
                        "period": point.period,
                        "year": point.year,
                        "month": point.month,
                        "value": point.value,
                        "monthly_change": point.monthly_change,
                        "annual_change": point.annual_change,
                    }
                )
        return target


class AsyncCBSDataAnalyzerClient:
    """Asynchronous client for CBS and data.gov.il workflows."""

    def __init__(
        self,
        *,
        cbs_base_url: str = CBS_INDEX_API_BASE,
        data_gov_base_url: str = DATA_GOV_API_BASE,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.cbs_base_url = cbs_base_url.rstrip("/")
        self.data_gov_base_url = data_gov_base_url.rstrip("/")
        default_headers = {
            "Accept": "application/json",
            "User-Agent": "cbs-data-analyzer/2.2",
        }
        if headers:
            default_headers.update(headers)
        self._client = httpx.AsyncClient(timeout=timeout, transport=transport, headers=default_headers)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncCBSDataAnalyzerClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def _get_json(self, url: str, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        try:
            response = await self._client.get(url, params=params)
        except httpx.HTTPError as exc:
            raise CBSAPIError(f"Request failed: {exc}", url=url) from exc

        if response.status_code >= 400:
            raise CBSAPIError(
                f"Endpoint returned HTTP {response.status_code}",
                status_code=response.status_code,
                url=str(response.url),
                response_text=response.text[:500],
            )

        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise CBSAPIError(
                "Endpoint did not return valid JSON",
                status_code=response.status_code,
                url=str(response.url),
                response_text=response.text[:500],
            ) from exc

        if not isinstance(data, dict):
            raise CBSAPIError(
                "Endpoint returned JSON that is not an object",
                status_code=response.status_code,
                url=str(response.url),
                response_text=response.text[:500],
            )
        return data

    async def get_catalog(self) -> dict[str, Any]:
        url = f"{self.cbs_base_url}/catalog/catalog"
        return await self._get_json(url, {"format": "json"})

    async def search_catalog(self, query: str) -> list[dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return []
        catalog = await self.get_catalog()
        chapters = catalog.get("chapters") or catalog.get("result") or []
        if not isinstance(chapters, list):
            return []
        return [
            dict(item)
            for item in chapters
            if isinstance(item, Mapping)
            and q in " ".join(str(value) for value in item.values() if value is not None).lower()
        ]

    async def get_price_index(
        self,
        index_id: int | str,
        *,
        start_period: str | None = None,
        end_period: str | None = None,
        last: int | None = None,
        coef: bool | None = None,
        download: bool = False,
    ) -> CBSSeries:
        """Fetch one CBS price-index series by mainCode."""
        url = f"{self.cbs_base_url}/data/price"
        params: dict[str, Any] = {"id": index_id, "format": "json", "download": str(download).lower()}
        if start_period:
            params["startPeriod"] = start_period
        if end_period:
            params["endPeriod"] = end_period
        if last is not None:
            if last <= 0:
                raise ValueError("last must be positive")
            params["last"] = last
        if coef is not None:
            params["coef"] = str(coef).lower()
        data = await self._get_json(url, params)
        source = str(httpx.URL(url, params={key: str(value) for key, value in params.items()}))
        return parse_price_series(data, index_id=index_id, source_url=source)

    async def get_known_index(self, key: str) -> CBSSeries:
        normalized = key.strip().lower().replace("-", "_")
        if normalized not in KNOWN_INDEXES:
            raise KeyError(f"Unknown index key: {key}")
        return await self.get_price_index(KNOWN_INDEXES[normalized])

    async def latest_price(self, index_id: int | str) -> CBSDataPoint | None:
        return (await self.get_price_index(index_id)).latest

    async def search_data_gov(
        self,
        query: str,
        *,
        rows: int = 10,
        organization: str = "lamas",
    ) -> dict[str, Any]:
        url = f"{self.data_gov_base_url}/package_search"
        params = {"q": query, "rows": rows, "fq": f"organization:{organization}"}
        return await self._get_json(url, params)


async def _async_demo(index_id: int = 120010) -> dict[str, Any]:
    """Return a tiny async demo payload."""
    async with AsyncCBSDataAnalyzerClient() as client:
        series = await client.get_price_index(index_id)
        latest = series.latest
        return {
            "series": series.name,
            "latest_period": latest.period if latest else None,
            "latest_value": latest.value if latest else None,
        }


if __name__ == "__main__":
    print(asyncio.run(_async_demo()))
