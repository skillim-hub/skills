from __future__ import annotations

import asyncio
import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Sequence
from urllib.parse import urlencode

try:
    import httpx
except Exception:  # pragma: no cover - optional at import time
    httpx = None  # type: ignore[assignment]

DealType = Literal["rent", "sale", "commercial_rent", "commercial_sale"]
SourceName = Literal["yad2", "madlan", "komo"]
EnvironmentName = Literal["sandbox", "production"]


class ClientError(ValueError):
    """Raised when user input cannot produce a safe search plan."""


class SearchEnvironment(str, Enum):
    SANDBOX = "sandbox"
    PRODUCTION = "production"

    @classmethod
    def parse(cls, value: str | None) -> "SearchEnvironment":
        normalized = (value or "sandbox").strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            raise ClientError("environment must be sandbox or production") from exc


@dataclass(frozen=True)
class SearchCriteria:
    city: str
    deal_type: DealType = "rent"
    neighborhoods: tuple[str, ...] = field(default_factory=tuple)
    min_price: int | None = None
    max_price: int | None = None
    min_rooms: float | None = None
    max_rooms: float | None = None
    property_types: tuple[str, ...] = field(default_factory=tuple)
    min_floor: int | None = None
    max_floor: int | None = None
    accessible: bool | None = None
    balcony: bool | None = None
    parking: bool | None = None
    pets_allowed: bool | None = None
    entry_date: str | None = None
    max_commute_minutes: int | None = None
    sources: tuple[SourceName, ...] = ("yad2", "madlan", "komo")
    notes: str | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "SearchCriteria":
        list_fields = {"neighborhoods", "property_types", "sources"}
        clean: dict[str, Any] = {}
        for key, value in payload.items():
            if value is None:
                continue
            if key in list_fields:
                clean[key] = tuple(_split_values(value))
            else:
                clean[key] = value
        return cls(**clean)

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class SourceLink:
    source: SourceName
    url: str
    label: str
    manual_steps: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class Listing:
    title: str
    source: str
    city: str
    neighborhood: str | None = None
    price: int | None = None
    rooms: float | None = None
    floor: int | None = None
    url: str | None = None
    published_at: str | None = None
    broker: bool | None = None
    parking: bool | None = None
    balcony: bool | None = None
    accessible: bool | None = None
    pets_allowed: bool | None = None
    notes: str | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "Listing":
        return cls(
            title=str(payload.get("title") or payload.get("address") or "Listing"),
            source=str(payload.get("source") or "manual"),
            city=str(payload.get("city") or ""),
            neighborhood=_optional_str(payload.get("neighborhood")),
            price=_optional_int(payload.get("price")),
            rooms=_optional_float(payload.get("rooms")),
            floor=_optional_int(payload.get("floor")),
            url=_optional_str(payload.get("url")),
            published_at=_optional_str(payload.get("published_at")),
            broker=_optional_bool(payload.get("broker")),
            parking=_optional_bool(payload.get("parking")),
            balcony=_optional_bool(payload.get("balcony")),
            accessible=_optional_bool(payload.get("accessible")),
            pets_allowed=_optional_bool(payload.get("pets_allowed")),
            notes=_optional_str(payload.get("notes")),
        )

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class CostEstimate:
    first_month_cash_needed: int
    recurring_monthly_cost: int
    components: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class SearchPlan:
    plan_id: str
    environment: EnvironmentName
    created_at: str
    criteria: SearchCriteria
    links: tuple[SourceLink, ...]
    review_checklist: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "environment": self.environment,
            "created_at": self.created_at,
            "criteria": self.criteria.to_dict(),
            "links": [link.to_dict() for link in self.links],
            "review_checklist": list(self.review_checklist),
            "warnings": list(self.warnings),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass(frozen=True)
class RankedListing:
    listing: Listing
    score: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.score, 2),
            "reasons": list(self.reasons),
            "listing": self.listing.to_dict(),
        }


class RealEstateSearchClient:
    """Create structured Israeli real-estate search plans for Yad2, Madlan, and Komo."""

    source_domains: dict[SourceName, str] = {
        "yad2": "https://www.yad2.co.il/realestate",
        "madlan": "https://www.madlan.co.il",
        "komo": "https://www.komo.co.il",
    }

    def __init__(self, environment: EnvironmentName | SearchEnvironment | str = "sandbox", timeout_seconds: float = 10.0) -> None:
        parsed = SearchEnvironment.parse(str(environment))
        self.environment: EnvironmentName = parsed.value  # type: ignore[assignment]
        self.timeout_seconds = float(timeout_seconds)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "RealEstateSearchClient":
        values = env or os_environ()
        return cls(
            environment=values.get("REAL_ESTATE_SEARCH_ENV", "sandbox"),
            timeout_seconds=float(values.get("REAL_ESTATE_SEARCH_TIMEOUT", "10")),
        )

    def normalize_city(self, city: str) -> str:
        normalized = _normalize_text(city)
        if not normalized:
            raise ClientError("city is required")
        return normalized

    def normalize_neighborhoods(self, neighborhoods: Iterable[str] | str | None) -> tuple[str, ...]:
        values = _split_values(neighborhoods)
        seen: set[str] = set()
        result: list[str] = []
        for item in values:
            normalized = _normalize_text(item)
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                result.append(normalized)
        return tuple(result)

    def normalize_criteria(self, criteria: SearchCriteria | Mapping[str, Any]) -> SearchCriteria:
        if not isinstance(criteria, SearchCriteria):
            criteria = SearchCriteria.from_mapping(criteria)
        normalized = SearchCriteria(
            city=self.normalize_city(criteria.city),
            deal_type=criteria.deal_type,
            neighborhoods=self.normalize_neighborhoods(criteria.neighborhoods),
            min_price=criteria.min_price,
            max_price=criteria.max_price,
            min_rooms=criteria.min_rooms,
            max_rooms=criteria.max_rooms,
            property_types=tuple(_normalize_text(x) for x in criteria.property_types if _normalize_text(x)),
            min_floor=criteria.min_floor,
            max_floor=criteria.max_floor,
            accessible=criteria.accessible,
            balcony=criteria.balcony,
            parking=criteria.parking,
            pets_allowed=criteria.pets_allowed,
            entry_date=_normalize_date(criteria.entry_date) if criteria.entry_date else None,
            max_commute_minutes=criteria.max_commute_minutes,
            sources=tuple(_coerce_source(s) for s in criteria.sources),
            notes=_optional_str(criteria.notes),
        )
        self.validate_criteria(normalized)
        return normalized

    def validate_criteria(self, criteria: SearchCriteria) -> None:
        if criteria.deal_type not in {"rent", "sale", "commercial_rent", "commercial_sale"}:
            raise ClientError("deal_type must be rent, sale, commercial_rent, or commercial_sale")
        if not criteria.sources:
            raise ClientError("at least one source is required")
        if len(set(criteria.sources)) != len(criteria.sources):
            raise ClientError("sources must not contain duplicates")
        if criteria.min_price is not None and criteria.min_price < 0:
            raise ClientError("min_price must be non-negative")
        if criteria.max_price is not None and criteria.max_price < 0:
            raise ClientError("max_price must be non-negative")
        if criteria.min_price is not None and criteria.max_price is not None and criteria.min_price > criteria.max_price:
            raise ClientError("min_price must not exceed max_price")
        if criteria.min_rooms is not None and criteria.min_rooms <= 0:
            raise ClientError("min_rooms must be positive")
        if criteria.max_rooms is not None and criteria.max_rooms <= 0:
            raise ClientError("max_rooms must be positive")
        if criteria.min_rooms is not None and criteria.max_rooms is not None and criteria.min_rooms > criteria.max_rooms:
            raise ClientError("min_rooms must not exceed max_rooms")
        if criteria.max_commute_minutes is not None and criteria.max_commute_minutes <= 0:
            raise ClientError("max_commute_minutes must be positive")
        if criteria.entry_date:
            _normalize_date(criteria.entry_date)

    def build_source_url(self, source: SourceName, criteria: SearchCriteria | Mapping[str, Any]) -> str:
        criteria = self.normalize_criteria(criteria)
        source = _coerce_source(source)
        query = self._query_values(criteria)
        if source == "yad2":
            if criteria.deal_type.startswith("commercial"):
                section = "commercial"
                query["dealType"] = 1 if criteria.deal_type == "commercial_rent" else 2
            else:
                section = "rent" if criteria.deal_type == "rent" else "forsale"
            return f"{self.source_domains[source]}/{section}?{urlencode(query, doseq=True)}"
        if source == "madlan":
            if criteria.deal_type == "commercial_rent":
                path = "commercial/for-rent"
            elif criteria.deal_type == "commercial_sale":
                path = "commercial/for-sale"
            else:
                path = "for-rent" if criteria.deal_type == "rent" else "for-sale"
            return f"{self.source_domains[source]}/{path}?{urlencode(query, doseq=True)}"
        if source == "komo":
            komo_query = self._komo_query_values(criteria)
            path = "apartments-for-rent.asp" if criteria.deal_type in {"rent", "commercial_rent"} else "apartments-for-sale.asp"
            return f"{self.source_domains[source]}/code/nadlan/{path}?{urlencode(komo_query, doseq=True)}"
        raise ClientError(f"unsupported source: {source}")

    def build_source_urls(self, criteria: SearchCriteria | Mapping[str, Any]) -> tuple[SourceLink, ...]:
        criteria = self.normalize_criteria(criteria)
        links: list[SourceLink] = []
        for source in criteria.sources:
            links.append(
                SourceLink(
                    source=source,
                    url=self.build_source_url(source, criteria),
                    label=f"{source} search for {criteria.city}",
                    manual_steps=self._manual_steps(source, criteria),
                )
            )
        return tuple(links)

    def build_search_plan(self, criteria: SearchCriteria | Mapping[str, Any]) -> SearchPlan:
        criteria = self.normalize_criteria(criteria)
        warnings = self._warnings(criteria)
        links = self.build_source_urls(criteria)
        plan_id = self.make_plan_id(criteria)
        return SearchPlan(
            plan_id=plan_id,
            environment=self.environment,
            created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            criteria=criteria,
            links=links,
            review_checklist=self.build_review_checklist(criteria),
            warnings=tuple(warnings),
        )

    async def abuild_search_plan(self, criteria: SearchCriteria | Mapping[str, Any]) -> SearchPlan:
        await asyncio.sleep(0)
        return self.build_search_plan(criteria)

    def make_plan_id(self, criteria: SearchCriteria | Mapping[str, Any]) -> str:
        criteria = self.normalize_criteria(criteria)
        raw = json.dumps(criteria.to_dict(), ensure_ascii=False, sort_keys=True)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
        return f"res-{digest}"

    def export_plan_json(self, plan: SearchPlan, path: str | Path) -> Path:
        output = Path(path)
        output.write_text(plan.to_json() + "\n", encoding="utf-8")
        return output

    def load_plan_json(self, path: str | Path) -> SearchPlan:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        criteria = SearchCriteria.from_mapping(payload["criteria"])
        return SearchPlan(
            plan_id=str(payload["plan_id"]),
            environment=SearchEnvironment.parse(payload.get("environment", self.environment)).value,  # type: ignore[assignment]
            created_at=str(payload.get("created_at") or ""),
            criteria=self.normalize_criteria(criteria),
            links=tuple(SourceLink(**link) for link in payload.get("links", [])),
            review_checklist=tuple(payload.get("review_checklist", [])),
            warnings=tuple(payload.get("warnings", [])),
        )

    def summarize_plan(self, plan: SearchPlan) -> str:
        c = plan.criteria
        neighborhoods = ", ".join(c.neighborhoods) if c.neighborhoods else "all requested neighborhoods"
        price = _range_label(c.min_price, c.max_price, "₪")
        rooms = _range_label(c.min_rooms, c.max_rooms, "rooms")
        return f"{plan.plan_id}: {c.deal_type} search in {c.city}, {neighborhoods}, {price}, {rooms}."

    def parse_listing_map(self, payload: Mapping[str, Any]) -> Listing:
        return Listing.from_mapping(payload)

    def compare_listings(self, listings: Sequence[Listing | Mapping[str, Any]], criteria: SearchCriteria | Mapping[str, Any]) -> list[RankedListing]:
        criteria = self.normalize_criteria(criteria)
        normalized = [item if isinstance(item, Listing) else Listing.from_mapping(item) for item in listings]
        ranked = [self.score_listing(item, criteria) for item in normalized]
        return sorted(ranked, key=lambda item: item.score, reverse=True)

    def rank_listings(self, listings: Sequence[Listing | Mapping[str, Any]], criteria: SearchCriteria | Mapping[str, Any]) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.compare_listings(listings, criteria)]

    def score_listing(self, listing: Listing, criteria: SearchCriteria) -> RankedListing:
        score = 50.0
        reasons: list[str] = []
        if listing.city and _normalize_text(listing.city).lower() == criteria.city.lower():
            score += 10
            reasons.append("city match")
        if criteria.neighborhoods and listing.neighborhood:
            if _normalize_text(listing.neighborhood).lower() in {n.lower() for n in criteria.neighborhoods}:
                score += 12
                reasons.append("neighborhood match")
        if listing.price is not None:
            if criteria.max_price is not None and listing.price <= criteria.max_price:
                score += 10
                reasons.append("within budget")
            elif criteria.max_price is not None:
                over = listing.price - criteria.max_price
                score -= min(25, over / max(criteria.max_price, 1) * 100)
                reasons.append("above budget")
            if criteria.min_price is not None and listing.price < criteria.min_price:
                score -= 5
                reasons.append("below expected price range")
        if listing.rooms is not None:
            if criteria.min_rooms is not None and listing.rooms >= criteria.min_rooms:
                score += 5
                reasons.append("meets room minimum")
            if criteria.max_rooms is not None and listing.rooms > criteria.max_rooms:
                score -= 8
                reasons.append("above room maximum")
        feature_map = {
            "parking": listing.parking,
            "balcony": listing.balcony,
            "accessible": listing.accessible,
            "pets_allowed": listing.pets_allowed,
        }
        for key, value in feature_map.items():
            requested = getattr(criteria, key)
            if requested is True and value is True:
                score += 4
                reasons.append(f"{key} confirmed")
            elif requested is True and value is False:
                score -= 6
                reasons.append(f"{key} missing")
        if listing.broker is False:
            score += 3
            reasons.append("direct owner listing")
        elif listing.broker is True:
            reasons.append("broker fee may apply")
        return RankedListing(listing=listing, score=max(0, min(100, score)), reasons=tuple(reasons))

    def estimate_monthly_cash_needed(
        self,
        listing: Listing | Mapping[str, Any],
        monthly_arnona: int = 0,
        monthly_vaad_bayit: int = 0,
        broker_fee_months: float = 0.0,
        deposit_months: float = 1.0,
    ) -> CostEstimate:
        listing = listing if isinstance(listing, Listing) else Listing.from_mapping(listing)
        rent = listing.price or 0
        broker_fee = int(round(rent * broker_fee_months))
        deposit = int(round(rent * deposit_months))
        recurring = rent + int(monthly_arnona) + int(monthly_vaad_bayit)
        first_month = recurring + broker_fee + deposit
        return CostEstimate(
            first_month_cash_needed=first_month,
            recurring_monthly_cost=recurring,
            components={
                "rent": rent,
                "arnona": int(monthly_arnona),
                "vaad_bayit": int(monthly_vaad_bayit),
                "broker_fee": broker_fee,
                "deposit": deposit,
            },
        )

    def build_review_checklist(self, criteria: SearchCriteria | Mapping[str, Any]) -> tuple[str, ...]:
        criteria = self.normalize_criteria(criteria)
        checklist = [
            "Confirm the exact street and building entrance before scheduling a visit.",
            "Compare the source listing with the advertiser message and save screenshots with dates.",
            "Ask whether the advertiser is the owner, tenant, or broker and document the answer.",
            "Check arnona classification, monthly building committee charge, and expected utility costs.",
            "Verify property condition, air conditioning, water pressure, noise, parking, and accessibility in person.",
        ]
        if criteria.deal_type in {"sale", "commercial_sale"}:
            checklist.extend(
                [
                    "Order a current land registry extract or rights confirmation before signing.",
                    "Check purchase tax, betterment levy exposure, building permits, liens, and mortgage constraints with licensed professionals.",
                    "Compare asking price to recent comparable transactions and neighborhood planning changes.",
                ]
            )
        else:
            checklist.extend(
                [
                    "Read the lease draft before transferring money and confirm guarantor, deposit, and exit terms.",
                    "Confirm pets, subletting, renewal option, repairs, and early termination terms in writing.",
                ]
            )
        if criteria.deal_type.startswith("commercial"):
            checklist.extend(
                [
                    "Verify permitted business use, signage, accessibility, licensing, loading access, and municipal classification.",
                    "Check VAT treatment, withholding documentation, and whether management fees are stated before VAT.",
                ]
            )
        return tuple(checklist)

    async def async_check_links(self, links: Sequence[SourceLink], fetch: bool = False) -> list[dict[str, Any]]:
        if not fetch:
            await asyncio.sleep(0)
            return [{"source": link.source, "url": link.url, "checked": False, "status_code": None} for link in links]
        if httpx is None:
            raise ClientError("httpx is required for fetch checks")
        results: list[dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:  # type: ignore[union-attr]
            for link in links:
                try:
                    response = await client.get(link.url)
                    results.append({"source": link.source, "url": link.url, "checked": True, "status_code": response.status_code})
                except Exception as exc:  # pragma: no cover - network dependent
                    results.append({"source": link.source, "url": link.url, "checked": True, "error": exc.__class__.__name__})
        return results

    def _komo_query_values(self, criteria: SearchCriteria) -> dict[str, Any]:
        query: dict[str, Any] = {"cityName": criteria.city}
        if criteria.deal_type == "commercial_rent":
            query["nehes"] = 28
        elif criteria.deal_type == "commercial_sale":
            query["nehes"] = 28
        else:
            query["nehes"] = 1
        if criteria.min_rooms is not None:
            query["fromRooms"] = _number_for_url(criteria.min_rooms)
        if criteria.max_rooms is not None:
            query["toRooms"] = _number_for_url(criteria.max_rooms)
        return query

    def _query_values(self, criteria: SearchCriteria) -> dict[str, Any]:
        query: dict[str, Any] = {
            "city": criteria.city,
            "deal_type": criteria.deal_type,
        }
        if criteria.neighborhoods:
            query["neighborhood"] = list(criteria.neighborhoods)
        if criteria.min_price is not None:
            query["min_price"] = criteria.min_price
        if criteria.max_price is not None:
            query["max_price"] = criteria.max_price
        if criteria.min_rooms is not None:
            query["min_rooms"] = _number_for_url(criteria.min_rooms)
        if criteria.max_rooms is not None:
            query["max_rooms"] = _number_for_url(criteria.max_rooms)
        if criteria.property_types:
            query["property_type"] = list(criteria.property_types)
        if criteria.min_floor is not None:
            query["min_floor"] = criteria.min_floor
        if criteria.max_floor is not None:
            query["max_floor"] = criteria.max_floor
        for key in ("accessible", "balcony", "parking", "pets_allowed"):
            value = getattr(criteria, key)
            if value is not None:
                query[key] = str(value).lower()
        if criteria.entry_date:
            query["entry_date"] = criteria.entry_date
        if criteria.max_commute_minutes:
            query["max_commute_minutes"] = criteria.max_commute_minutes
        return query

    def _manual_steps(self, source: SourceName, criteria: SearchCriteria) -> tuple[str, ...]:
        base = [
            f"Open the {source} link and confirm the city is {criteria.city}.",
            "Apply missing filters manually if the source ignores a query parameter.",
            "Sort by newest first, then save promising listing URLs in a comparison sheet.",
        ]
        if criteria.neighborhoods:
            base.append("Check that the neighborhood label matches the map location, not only advertiser text; for Komo, apply neighborhood filtering manually when a verified neighborhood id is not available.")
        if criteria.deal_type.startswith("commercial"):
            base.append("Confirm commercial zoning and municipal licensing fit before negotiating.")
        return tuple(base)

    def _warnings(self, criteria: SearchCriteria) -> list[str]:
        warnings: list[str] = []
        if self.environment == "production":
            warnings.append("Use source sites within their terms and robots rules; do not bypass access controls or rate limits.")
        if not criteria.neighborhoods:
            warnings.append("No neighborhood filter supplied; results may include broad city-level matches.")
        if criteria.max_price is None:
            warnings.append("No maximum price supplied; add one to avoid wasting review time.")
        if criteria.deal_type in {"sale", "commercial_sale"}:
            warnings.append("Tax, land registry, mortgage, and planning checks require official sources and licensed professionals.")
        return warnings


def os_environ() -> Mapping[str, str]:
    import os

    return os.environ


def _coerce_source(value: str) -> SourceName:
    normalized = str(value).strip().lower().replace("-", "_")
    if normalized not in {"yad2", "madlan", "komo"}:
        raise ClientError("source must be yad2, madlan, or komo")
    return normalized  # type: ignore[return-value]


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _normalize_date(value: str) -> str:
    raw = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            pass
    raise ClientError("entry_date must use YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY")


def _split_values(value: Iterable[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in re.split(r"[,|]", value) if part.strip()]
    return [str(part).strip() for part in value if str(part).strip()]


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(float(value))


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _optional_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _optional_bool(value: Any) -> bool | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise ClientError(f"invalid boolean value: {value}")


def _range_label(min_value: int | float | None, max_value: int | float | None, suffix: str) -> str:
    if min_value is not None and max_value is not None:
        return f"{min_value}-{max_value} {suffix}"
    if min_value is not None:
        return f"from {min_value} {suffix}"
    if max_value is not None:
        return f"up to {max_value} {suffix}"
    return f"no {suffix} range"


def _number_for_url(value: int | float) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _json_ready(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, float) and math.isnan(value):
        return None
    return value
