"""Typed alert and public-shelter client.

The module provides:
- synchronous and asynchronous alert fetching through configurable sources
- safe parsing for JSON and callback-wrapped payloads
- Hebrew and English locality normalization
- local CSV/JSON/GeoJSON public-shelter loading
- nearest-shelter ranking
- watch creation and watch checking helpers for CLI workflows
"""

from __future__ import annotations

import asyncio
import csv
import datetime as _dt
import hashlib
import io
import json
import math
import re
import unicodedata
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable, Mapping, Optional, Sequence

DEFAULT_ALERTS_URL = "https://www.oref.org.il/WarningMessages/alert/alerts.json"
DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
    "Referer": "https://www.oref.org.il/",
    "Cache-Control": "no-cache",
    "User-Agent": "red-alert-shelter-finder/1.4.0",
}
ISRAEL_LAT_RANGE = (29.0, 34.0)
ISRAEL_LON_RANGE = (33.0, 36.0)

Transport = Callable[[str, float, Mapping[str, str]], str]
AsyncTransport = Callable[[str, float, Mapping[str, str]], Awaitable[str]]


class AlertClientError(RuntimeError):
    """Base error for alert and shelter client failures."""


class AlertParseError(AlertClientError):
    """Raised when an alert payload cannot be parsed safely."""


class ShelterDataError(AlertClientError):
    """Raised when shelter data is invalid."""


class WatchError(AlertClientError):
    """Raised when a watch record is invalid or missing."""


@dataclass(frozen=True)
class Alert:
    """Normalized alert record."""

    message_id: str
    title: str
    areas: tuple[str, ...]
    category: str = ""
    timestamp: str = ""
    raw: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["areas"] = list(self.areas)
        data["raw"] = dict(self.raw)
        return data


@dataclass(frozen=True)
class Shelter:
    """Public shelter location."""

    name: str
    latitude: float
    longitude: float
    address: str = ""
    city: str = ""
    accessibility: str = ""
    opening_status: str = ""
    source: str = ""
    distance_m: Optional[float] = None

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any], *, source: str = "") -> "Shelter":
        """Create a shelter from a CSV/JSON-like mapping."""

        def first(*names: str) -> Any:
            for name in names:
                if name in row and row[name] not in (None, ""):
                    return row[name]
            return ""

        name = str(first("name", "shem", "שם", "Name", "SHELTER_NAME", "id", "identifier")).strip()
        if not name:
            name = "מקלט ציבורי"

        lat_raw = first("latitude", "lat", "Latitude", "LAT", "y", "Y", "קו רוחב")
        lon_raw = first("longitude", "lon", "lng", "Longitude", "LON", "LNG", "x", "X", "קו אורך")
        try:
            lat = float(lat_raw)
            lon = float(lon_raw)
        except (TypeError, ValueError) as exc:
            raise ShelterDataError(f"Invalid shelter coordinates for {name!r}") from exc

        validate_coordinates(lat, lon)

        return cls(
            name=name,
            latitude=lat,
            longitude=lon,
            address=str(first("address", "כתובת", "Address", "street", "רחוב")).strip(),
            city=str(first("city", "יישוב", "ישוב", "City", "municipality")).strip(),
            accessibility=str(first("accessibility", "נגישות", "accessible")).strip(),
            opening_status=str(first("opening_status", "status", "סטטוס")).strip(),
            source=source or str(first("source", "מקור")).strip(),
        )

    def with_distance(self, distance_m: float) -> "Shelter":
        """Return a copy with a calculated distance."""

        return Shelter(
            name=self.name,
            latitude=self.latitude,
            longitude=self.longitude,
            address=self.address,
            city=self.city,
            accessibility=self.accessibility,
            opening_status=self.opening_status,
            source=self.source,
            distance_m=distance_m,
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if data["distance_m"] is not None:
            data["distance_m"] = round(float(data["distance_m"]), 1)
        return data


@dataclass(frozen=True)
class Watch:
    """Saved locality watch configuration."""

    watch_id: str
    area: str
    canonical_area: str
    environment: str
    created_at: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def now_iso() -> str:
    """Return local ISO timestamp."""

    return _dt.datetime.now(_dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def strip_hebrew_niqqud(value: str) -> str:
    """Remove Hebrew vowel marks and cantillation marks."""

    return "".join(ch for ch in value if not ("\u0591" <= ch <= "\u05C7"))


def normalize_area(value: str) -> str:
    """Normalize locality and alert-area names for matching."""

    text = unicodedata.normalize("NFKC", str(value or "")).strip()
    text = strip_hebrew_niqqud(text)
    text = text.replace("׳", "'").replace("`", "'").replace("’", "'")
    text = text.replace("״", '"').replace("“", '"').replace("”", '"')
    text = re.sub(r"[‐‑‒–—−]+", "-", text)
    text = re.sub(r"\s*-\s*", " - ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def validate_coordinates(latitude: float, longitude: float, *, israel_bounds: bool = True) -> None:
    """Validate coordinate values and optional Israel-focused bounds."""

    if not (-90 <= latitude <= 90):
        raise ShelterDataError(f"Latitude out of range: {latitude}")
    if not (-180 <= longitude <= 180):
        raise ShelterDataError(f"Longitude out of range: {longitude}")
    if israel_bounds:
        if not (ISRAEL_LAT_RANGE[0] <= latitude <= ISRAEL_LAT_RANGE[1]) or not (
            ISRAEL_LON_RANGE[0] <= longitude <= ISRAEL_LON_RANGE[1]
        ):
            raise ShelterDataError(
                f"Coordinates outside Israel-focused bounds: latitude={latitude}, longitude={longitude}"
            )


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in meters."""

    validate_coordinates(lat1, lon1, israel_bounds=False)
    validate_coordinates(lat2, lon2, israel_bounds=False)
    radius_m = 6_371_000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius_m * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def alerts_to_json(alerts: Sequence[Alert]) -> str:
    """Serialize alerts as readable JSON."""

    return json.dumps([a.to_dict() for a in alerts], ensure_ascii=False, indent=2)


def shelters_to_json(shelters: Sequence[Shelter]) -> str:
    """Serialize shelters as readable JSON."""

    return json.dumps([s.to_dict() for s in shelters], ensure_ascii=False, indent=2)


def _default_transport(url: str, timeout: float, headers: Mapping[str, str]) -> str:
    req = urllib.request.Request(url, headers=dict(headers), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            return body.decode(charset, errors="replace")
    except urllib.error.HTTPError as exc:
        raise AlertClientError(f"Alert feed returned HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise AlertClientError(f"Alert feed unavailable: {exc.reason}") from exc


class RedAlertShelterFinderClient:
    """Client for alerts, watches, and nearest-shelter lookup."""

    def __init__(
        self,
        *,
        alerts_url: str = DEFAULT_ALERTS_URL,
        timeout: float = 10.0,
        headers: Optional[Mapping[str, str]] = None,
        aliases: Optional[Mapping[str, str]] = None,
        transport: Optional[Transport] = None,
        async_transport: Optional[AsyncTransport] = None,
        now_provider: Callable[[], str] = now_iso,
    ) -> None:
        self.alerts_url = alerts_url
        self.timeout = float(timeout)
        self.headers = {**DEFAULT_HEADERS, **dict(headers or {})}
        base_aliases = {
            "תא": "תל אביב - יפו",
            "תל אביב": "תל אביב - יפו",
            "tel aviv": "תל אביב - יפו",
            "tlv": "תל אביב - יפו",
            "jerusalem": "ירושלים",
            "haifa": "חיפה",
            "beer sheva": "באר שבע",
            "beersheba": "באר שבע",
            "ashdod": "אשדוד",
            "rishon lezion": "ראשון לציון",
            "rishon leziyyon": "ראשון לציון",
            "petah tikva": "פתח תקווה",
            "petach tikva": "פתח תקווה",
            "ramat gan": "רמת גן",
        }
        if aliases:
            base_aliases.update(aliases)
        self.aliases = {normalize_area(k): normalize_area(v) for k, v in base_aliases.items()}
        self._transport = transport or _default_transport
        self._async_transport = async_transport
        self._now_provider = now_provider

    def canonical_area(self, value: str) -> str:
        normalized = normalize_area(value)
        return self.aliases.get(normalized, normalized)

    def parse_payload_text(self, text: str) -> Any:
        """Parse JSON or callback-wrapped JSON text."""

        cleaned = str(text or "").lstrip("\ufeff").strip()
        if not cleaned:
            return []
        if cleaned[0] not in "[{":
            match = re.search(r"^[\w.$]+\((.*)\)\s*;?$", cleaned, flags=re.DOTALL)
            if match:
                cleaned = match.group(1).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise AlertParseError(f"Could not parse alert payload as JSON: {exc}") from exc

    def parse_alert_payload(self, payload: Any) -> list[Alert]:
        """Normalize supported alert payload variants into Alert objects."""

        if isinstance(payload, str):
            payload = self.parse_payload_text(payload)

        if payload in (None, "", []):
            return []

        if isinstance(payload, list):
            if not payload:
                return []
            if all(isinstance(item, str) for item in payload):
                return [
                    Alert(
                        message_id="",
                        title="",
                        areas=tuple(str(item).strip() for item in payload if str(item).strip()),
                        timestamp=self._now_provider(),
                        raw={"data": payload},
                    )
                ]
            alerts: list[Alert] = []
            for item in payload:
                alerts.extend(self.parse_alert_payload(item))
            return alerts

        if not isinstance(payload, Mapping):
            raise AlertParseError(f"Unsupported alert payload type: {type(payload).__name__}")

        data = payload.get("data", payload.get("areas", payload.get("cities", [])))
        if data in (None, "", []):
            return []

        if isinstance(data, str):
            areas = [part.strip() for part in re.split(r"[,;|]", data) if part.strip()]
        elif isinstance(data, Iterable):
            areas = [str(part).strip() for part in data if str(part).strip()]
        else:
            raise AlertParseError("Alert payload data field must be a string or list")

        if not areas:
            return []

        message_id = str(payload.get("id", payload.get("message_id", payload.get("alert_id", ""))))
        title = str(payload.get("title", payload.get("desc", payload.get("description", ""))))
        category = str(payload.get("cat", payload.get("category", "")))
        timestamp = str(payload.get("time", payload.get("timestamp", ""))) or self._now_provider()

        return [
            Alert(
                message_id=message_id,
                title=title,
                areas=tuple(areas),
                category=category,
                timestamp=timestamp,
                raw=dict(payload),
            )
        ]

    def fetch_current_alerts(self) -> list[Alert]:
        """Fetch and parse current alerts synchronously."""

        text = self._transport(self.alerts_url, self.timeout, self.headers)
        return self.parse_alert_payload(text)

    async def fetch_current_alerts_async(self) -> list[Alert]:
        """Fetch and parse current alerts asynchronously."""

        if self._async_transport:
            text = await self._async_transport(self.alerts_url, self.timeout, self.headers)
        else:
            text = await asyncio.to_thread(self._transport, self.alerts_url, self.timeout, self.headers)
        return self.parse_alert_payload(text)

    def area_in_alerts(self, area: str, alerts: Sequence[Alert]) -> bool:
        """Return True when the area matches any active alert area."""

        target = self.canonical_area(area)
        return any(self.canonical_area(active_area) == target for alert in alerts for active_area in alert.areas)

    def status_for_area(self, area: str, alerts: Optional[Sequence[Alert]] = None) -> dict[str, Any]:
        """Return a JSON-serializable area status object."""

        active_alerts = list(alerts if alerts is not None else self.fetch_current_alerts())
        target = self.canonical_area(area)
        matched = [
            alert.to_dict()
            for alert in active_alerts
            if any(self.canonical_area(active_area) == target for active_area in alert.areas)
        ]
        return {
            "area": area,
            "canonical_area": target,
            "active": bool(matched),
            "alerts": matched,
            "checked_at": self._now_provider(),
        }

    def action_steps(self, *, active: bool, outside: bool = False, business: bool = False) -> list[str]:
        """Return neutral imperative action steps."""

        if active:
            steps = [
                "Enter the nearest protected space immediately.",
                "Remain inside until official guidance permits exit.",
            ]
            if outside:
                steps.append("Use the closest protected space available; do not travel to a farther shelter during the alarm.")
            if business:
                steps.extend(
                    [
                        "Stop service, checkout, and dispatch.",
                        "Guide staff and customers through the marked route.",
                        "Check staff and customer status before resuming operations.",
                    ]
                )
            return steps

        steps = [
            "Keep the route to the protected space clear.",
            "Keep official alert notifications active.",
            "Treat a feed failure or siren as requiring immediate protective action.",
        ]
        if business:
            steps.append("Review the shift procedure and assign a protected-space lead.")
        return steps

    def create_watch(self, area: str, *, environment: str = "sandbox") -> Watch:
        """Create a deterministic watch record for a locality."""

        if environment not in {"sandbox", "production"}:
            raise WatchError("environment must be sandbox or production")
        canonical = self.canonical_area(area)
        digest = hashlib.sha256(f"{environment}:{canonical}".encode("utf-8")).hexdigest()[:12]
        return Watch(
            watch_id=f"watch_{digest}",
            area=area,
            canonical_area=canonical,
            environment=environment,
            created_at=self._now_provider(),
        )

    def save_watch(self, watch: Watch, path: str | Path) -> None:
        """Save a watch record as JSON."""

        Path(path).write_text(json.dumps(watch.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def load_watch(self, path: str | Path, watch_id: str) -> Watch:
        """Load and validate a saved watch record."""

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("watch_id") != watch_id:
            raise WatchError("watch_id does not match the saved watch file")
        return Watch(
            watch_id=str(payload["watch_id"]),
            area=str(payload["area"]),
            canonical_area=str(payload["canonical_area"]),
            environment=str(payload["environment"]),
            created_at=str(payload["created_at"]),
        )

    def check_watch(self, watch: Watch, alerts: Optional[Sequence[Alert]] = None) -> dict[str, Any]:
        """Check current status for a saved watch."""

        status = self.status_for_area(watch.area, alerts)
        status["watch_id"] = watch.watch_id
        status["environment"] = watch.environment
        return status

    def load_shelters_text(self, text: str, *, format_hint: str = "", source: str = "") -> list[Shelter]:
        """Load shelter records from CSV, JSON list, JSON object, or GeoJSON."""

        stripped = text.lstrip("\ufeff").strip()
        if not stripped:
            return []
        hint = format_hint.lower().strip()
        if hint == "csv" or (not hint and not stripped.startswith(("{", "["))):
            reader = csv.DictReader(io.StringIO(stripped))
            return [Shelter.from_mapping(row, source=source) for row in reader]

        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ShelterDataError(f"Could not parse shelter data: {exc}") from exc

        return self.load_shelters_payload(payload, source=source)

    def load_shelters_payload(self, payload: Any, *, source: str = "") -> list[Shelter]:
        """Load shelter records from JSON-like payloads."""

        if isinstance(payload, list):
            return [Shelter.from_mapping(item, source=source) for item in payload]

        if not isinstance(payload, Mapping):
            raise ShelterDataError("Shelter payload must be a list, object, or GeoJSON FeatureCollection")

        if payload.get("type") == "FeatureCollection":
            shelters: list[Shelter] = []
            for feature in payload.get("features", []):
                geometry = feature.get("geometry") or {}
                properties = dict(feature.get("properties") or {})
                coordinates = geometry.get("coordinates") or []
                if geometry.get("type") == "Point" and len(coordinates) >= 2:
                    properties["longitude"] = coordinates[0]
                    properties["latitude"] = coordinates[1]
                shelters.append(Shelter.from_mapping(properties, source=source))
            return shelters

        if "shelters" in payload and isinstance(payload["shelters"], list):
            return [Shelter.from_mapping(item, source=source) for item in payload["shelters"]]

        return [Shelter.from_mapping(payload, source=source)]

    def load_shelters_file(self, path: str | Path, *, source: str = "") -> list[Shelter]:
        """Load shelters from a local CSV/JSON/GeoJSON file."""

        p = Path(path)
        hint = p.suffix.lower().lstrip(".")
        return self.load_shelters_text(p.read_text(encoding="utf-8"), format_hint=hint, source=source or str(p))

    def nearest_shelters(
        self,
        latitude: float,
        longitude: float,
        shelters: Sequence[Shelter],
        *,
        limit: int = 5,
        max_distance_m: Optional[float] = None,
    ) -> list[Shelter]:
        """Return nearest shelters sorted by distance and name."""

        validate_coordinates(float(latitude), float(longitude))
        if limit < 1:
            raise ShelterDataError("limit must be at least 1")

        ranked: list[Shelter] = []
        for shelter in shelters:
            distance = haversine_m(latitude, longitude, shelter.latitude, shelter.longitude)
            if max_distance_m is None or distance <= max_distance_m:
                ranked.append(shelter.with_distance(distance))
        ranked.sort(key=lambda s: (float("inf") if s.distance_m is None else s.distance_m, s.name))
        return ranked[:limit]


__all__ = [
    "Alert",
    "AlertClientError",
    "AlertParseError",
    "AsyncTransport",
    "DEFAULT_ALERTS_URL",
    "DEFAULT_HEADERS",
    "RedAlertShelterFinderClient",
    "Shelter",
    "ShelterDataError",
    "Transport",
    "Watch",
    "WatchError",
    "alerts_to_json",
    "haversine_m",
    "normalize_area",
    "now_iso",
    "shelters_to_json",
    "strip_hebrew_niqqud",
    "validate_coordinates",
]
