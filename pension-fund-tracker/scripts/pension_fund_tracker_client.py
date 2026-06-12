#!/usr/bin/env python3
"""Typed client for information-only Israeli pension fund return and fee analysis."""

from __future__ import annotations

import asyncio, csv, dataclasses, datetime as dt, io, json, math, re, urllib.parse, urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


class PensionTrackerError(Exception): pass
class DataSourceError(PensionTrackerError): pass
class ValidationError(PensionTrackerError): pass


@dataclass(frozen=True)
class PensionRecord:
    """Normalized public row. Return and fee numbers are percentage points, not fractions."""
    fund_id: str
    fund_name: str
    provider: str = ""
    report_date: dt.date | None = None
    fund_type: str = ""
    track_name: str = ""
    monthly_return_pct: float | None = None
    year_to_date_return_pct: float | None = None
    trailing_12m_return_pct: float | None = None
    trailing_36m_return_pct: float | None = None
    trailing_60m_return_pct: float | None = None
    management_fee_deposit_pct: float | None = None
    management_fee_assets_pct: float | None = None
    assets_millions_nis: float | None = None
    source: str = ""
    raw: Mapping[str, Any] = field(default_factory=dict, compare=False)


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    code: str
    message: str
    record_index: int | None = None
    fund_id: str | None = None


@dataclass(frozen=True)
class FeeImpactResult:
    monthly_contribution: float
    starting_balance: float
    years: int
    annual_return_pct: float
    deposit_fee_pct: float
    asset_fee_pct: float
    gross_no_fee_balance: float
    net_with_fees_balance: float
    estimated_fee_drag: float
    total_contributions: float


@dataclass(frozen=True)
class ScoreResult:
    fund_id: str
    fund_name: str
    provider: str
    report_date: dt.date | None
    score: float
    return_score: float | None
    fee_score: float | None
    caveats: tuple[str, ...]


COLUMN_ALIASES = {
    "fund_id": ("fund_id","fund id","fund number","fund_number","track id","track_id","מספר קופה","מספר מסלול","קוד קופה","קוד מסלול","מספר קרן"),
    "fund_name": ("fund_name","fund name","track name","track_name","שם קופה","שם מסלול","שם קרן","שם תכנית"),
    "provider": ("provider","managing company","manager","company","גוף מנהל","שם גוף מנהל","חברה מנהלת","שם חברה מנהלת"),
    "report_date": ("report_date","report date","reporting period","period","date","תאריך דיווח","חודש דיווח","תקופת דיווח","תאריך"),
    "fund_type": ("fund_type","fund type","product type","סוג קופה","סוג קרן","סוג מסלול"),
    "track_name": ("track_name","track","investment track","מסלול השקעה","מסלול"),
    "monthly_return_pct": ("monthly_return_pct","monthly return","month return","return month","תשואה חודשית","תשואה נומינלית חודשית","תשואה בחודש"),
    "year_to_date_return_pct": ("year_to_date_return_pct","ytd_return_pct","year to date return","ytd return","תשואה מצטברת מתחילת שנה","תשואה מתחילת השנה"),
    "trailing_12m_return_pct": ("trailing_12m_return_pct","12m return","12 month return","return 12 months","תשואה 12 חודשים אחרונים","תשואה לשנה אחרונה"),
    "trailing_36m_return_pct": ("trailing_36m_return_pct","36m return","3y return","return 36 months","תשואה 36 חודשים אחרונים","תשואה לשלוש שנים"),
    "trailing_60m_return_pct": ("trailing_60m_return_pct","60m return","5y return","return 60 months","תשואה 60 חודשים אחרונים","תשואה לחמש שנים"),
    "management_fee_deposit_pct": ("management_fee_deposit_pct","deposit fee","contribution fee","fee from deposit","fee from contribution","דמי ניהול מהפקדה","דמי ניהול מהפקדות"),
    "management_fee_assets_pct": ("management_fee_assets_pct","asset fee","accumulated balance fee","fee from assets","fee from balance","דמי ניהול מצבירה","דמי ניהול מנכסים","דמי ניהול מסך נכסים"),
    "assets_millions_nis": ("assets_millions_nis","assets","assets millions nis","total assets","aum","נכסים במיליוני שח",'נכסים במיליוני ש"ח',"סך נכסים","היקף נכסים"),
}
NUMERIC_FIELDS = {"monthly_return_pct","year_to_date_return_pct","trailing_12m_return_pct","trailing_36m_return_pct","trailing_60m_return_pct","management_fee_deposit_pct","management_fee_assets_pct","assets_millions_nis"}
RETURN_FIELDS = {"monthly_return_pct","year_to_date_return_pct","trailing_12m_return_pct","trailing_36m_return_pct","trailing_60m_return_pct"}
FEE_FIELDS = {"management_fee_deposit_pct","management_fee_assets_pct"}


def _canonical_key(value: str) -> str:
    text = str(value).strip().lower().replace("\ufeff", "")
    text = text.replace("ש״ח", "שח").replace('ש"ח', "שח")
    text = re.sub(r"[\s_\-–—:/\\().]+", " ", text)
    return text.strip()


ALIAS_LOOKUP = {_canonical_key(alias): canonical for canonical, aliases in COLUMN_ALIASES.items() for alias in aliases}


def parse_number(value: Any) -> float | None:
    """Parse Israeli/English numeric text into a float."""
    if value is None or isinstance(value, bool): return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value): return None
        return float(value)
    text = str(value).strip()
    if not text: return None
    text = text.replace("\u200f", "").replace("\u200e", "")
    text = text.replace("₪", "").replace("NIS", "").replace("nis", "")
    text = text.replace("%", "").replace("ש״ח", "").replace('ש"ח', "").replace("שח", "").strip()
    negative = text.startswith("(") and text.endswith(")")
    if negative: text = text[1:-1].strip()
    text = re.sub(r"[^\d,.\-+]", "", text)
    if not text or text in {"-","+",".",","}: return None
    if "," in text and "." not in text:
        parts = text.split(",")
        text = ".".join(parts) if len(parts) == 2 and 1 <= len(parts[1]) <= 2 else "".join(parts)
    elif "," in text and "." in text:
        text = text.replace(",", "")
    try:
        number = float(text)
    except ValueError as exc:
        raise ValidationError(f"Cannot parse numeric value: {value!r}") from exc
    return -number if negative else number


def parse_date(value: Any) -> dt.date | None:
    """Parse common Israeli and ISO dates."""
    if value is None: return None
    if isinstance(value, dt.datetime): return value.date()
    if isinstance(value, dt.date): return value
    text = str(value).strip()
    if not text: return None
    text = text.replace(".", "-").replace("/", "-")
    text = re.sub(r"\s+", "", text)
    if re.fullmatch(r"\d{6}", text):
        return dt.date(int(text[:4]), int(text[4:6]), 1)
    for pattern in ("%Y-%m-%d","%d-%m-%Y","%Y-%m","%m-%Y","%d-%m-%y"):
        try: return dt.datetime.strptime(text, pattern).date()
        except ValueError: pass
    if re.fullmatch(r"\d{5}", text):
        serial = int(text)
        if 20000 <= serial <= 60000:
            return dt.date(1899, 12, 30) + dt.timedelta(days=serial)
    raise ValidationError(f"Cannot parse date value: {value!r}")


def format_nis(value: float) -> str: return f"₪{value:,.0f}"
def format_pct(value: float | None) -> str: return "not reported" if value is None else f"{value:.2f}%"
def format_date_hebrew(value: dt.date | None) -> str: return "לא דווח" if value is None else value.strftime("%d/%m/%Y")


def normalize_row(row: Mapping[str, Any], *, strict: bool = False, source: str = "") -> PensionRecord:
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        canonical = ALIAS_LOOKUP.get(_canonical_key(str(key)))
        if canonical: normalized[canonical] = value
    kwargs: dict[str, Any] = {}
    for field_name in PensionRecord.__dataclass_fields__:
        if field_name in {"raw", "source"}: continue
        raw = normalized.get(field_name)
        if field_name in NUMERIC_FIELDS:
            kwargs[field_name] = parse_number(raw)
        elif field_name == "report_date":
            kwargs[field_name] = parse_date(raw)
        elif field_name == "fund_id":
            text = "" if raw is None else str(raw).strip()
            if re.fullmatch(r"\d+\.0", text): text = text[:-2]
            kwargs[field_name] = text
        else:
            kwargs[field_name] = "" if raw is None else str(raw).strip()
    if strict:
        missing = [name for name in ("fund_id","fund_name","report_date") if not kwargs.get(name)]
        if missing: raise ValidationError(f"Missing required normalized fields: {', '.join(missing)}")
    return PensionRecord(source=source, raw=dict(row), **kwargs)


def records_to_dicts(records: Iterable[PensionRecord]) -> list[dict[str, Any]]:
    out = []
    for record in records:
        data = dataclasses.asdict(record)
        data["report_date"] = record.report_date.isoformat() if record.report_date else None
        out.append(data)
    return out


def records_from_dicts(rows: Iterable[Mapping[str, Any]]) -> list[PensionRecord]:
    records = []
    field_names = set(PensionRecord.__dataclass_fields__)
    for row in rows:
        data = {k: v for k, v in row.items() if k in field_names}
        if data.get("report_date"): data["report_date"] = parse_date(data["report_date"])
        if "raw" not in data or data["raw"] is None: data["raw"] = {}
        records.append(PensionRecord(**data))
    return records


def _minmax_scores(values: Mapping[str, float | None], *, higher_is_better: bool) -> dict[str, float | None]:
    present = {k: v for k, v in values.items() if v is not None}
    if not present: return {k: None for k in values}
    mn, mx = min(present.values()), max(present.values())
    if math.isclose(mn, mx): return {k: (100.0 if values[k] is not None else None) for k in values}
    out: dict[str, float | None] = {}
    for k, v in values.items():
        if v is None: out[k] = None
        elif higher_is_better: out[k] = (v - mn) / (mx - mn) * 100
        else: out[k] = (mx - v) / (mx - mn) * 100
    return out


class PensionFundTrackerClient:
    """Synchronous client for public pension fund data."""
    def normalize_row(self, row: Mapping[str, Any], *, strict: bool = False, source: str = "") -> PensionRecord:
        return normalize_row(row, strict=strict, source=source)

    def load_csv(self, path: str | Path, *, encoding: str = "utf-8-sig") -> list[PensionRecord]:
        p = Path(path)
        try: text = p.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            raise DataSourceError(f"Could not decode {p}. Try encoding='cp1255' or UTF-8 export.") from exc
        return self.load_csv_text(text, source=str(p))

    def load_csv_text(self, text: str, *, source: str = "") -> list[PensionRecord]:
        try: dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
        except csv.Error: dialect = csv.excel
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
        if not reader.fieldnames: raise DataSourceError("CSV file has no header row.")
        return [normalize_row(row, source=source) for row in reader]

    def load_json(self, path: str | Path) -> list[PensionRecord]:
        return self.load_json_data(json.loads(Path(path).read_text(encoding="utf-8")), source=str(path))

    def load_json_data(self, data: Any, *, source: str = "") -> list[PensionRecord]:
        if isinstance(data, dict) and "records" in data: data = data["records"]
        if isinstance(data, dict) and "result" in data and "records" in data["result"]: data = data["result"]["records"]
        if not isinstance(data, list): raise DataSourceError("JSON input must be a list or contain records.")
        if data and isinstance(data[0], Mapping) and set(PensionRecord.__dataclass_fields__).intersection(data[0]):
            try: return records_from_dicts(data)
            except TypeError: pass
        return [normalize_row(row, source=source) for row in data]

    def fetch_url(self, url: str, *, timeout: int = 30) -> list[PensionRecord]:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            content_type = response.headers.get("content-type", "")
            body = response.read()
        text = body.decode("utf-8-sig")
        if "json" in content_type or url.lower().endswith(".json"):
            return self.load_json_data(json.loads(text), source=url)
        return self.load_csv_text(text, source=url)

    def fetch_ckan(self, resource_id: str, *, base_url: str = "https://data.gov.il/api/3/action/datastore_search", limit: int = 1000, max_records: int | None = None, timeout: int = 30) -> list[PensionRecord]:
        if not resource_id: raise ValueError("resource_id is required")
        offset, rows = 0, []
        while True:
            url = f"{base_url}?{urllib.parse.urlencode({'resource_id': resource_id, 'limit': limit, 'offset': offset})}"
            with urllib.request.urlopen(url, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            page_rows, total = self._parse_ckan_payload(payload)
            rows.extend(page_rows)
            offset += limit
            if max_records is not None and len(rows) >= max_records:
                rows = rows[:max_records]; break
            if offset >= total or not page_rows: break
        return [normalize_row(row, source=f"ckan:{resource_id}") for row in rows]

    def _parse_ckan_payload(self, payload: Mapping[str, Any]) -> tuple[list[Mapping[str, Any]], int]:
        if not payload.get("success"):
            raise DataSourceError(f"CKAN API returned success=false: {payload.get('error', payload)}")
        result = payload.get("result")
        if not isinstance(result, Mapping): raise DataSourceError("CKAN response missing result object.")
        records = result.get("records", [])
        if not isinstance(records, list): raise DataSourceError("CKAN result.records is not a list.")
        return records, int(result.get("total") or len(records))

    def validate_records(self, records: Sequence[PensionRecord]) -> list[ValidationIssue]:
        issues, seen = [], set()
        for i, r in enumerate(records):
            if not r.fund_id: issues.append(ValidationIssue("critical","MISSING_FUND_ID","Missing fund ID.",i))
            if not r.fund_name: issues.append(ValidationIssue("critical","MISSING_FUND_NAME","Missing fund name.",i,r.fund_id))
            if r.report_date is None: issues.append(ValidationIssue("critical","MISSING_REPORT_DATE","Missing report date.",i,r.fund_id))
            key = (r.fund_id, r.fund_name, r.report_date.isoformat() if r.report_date else "")
            if key in seen: issues.append(ValidationIssue("warning","DUPLICATE_RECORD","Duplicate fund/date/name row.",i,r.fund_id))
            seen.add(key)
            for name in RETURN_FIELDS:
                v = getattr(r, name)
                if v is not None and (v > 100 or v < -80): issues.append(ValidationIssue("warning","IMPLAUSIBLE_RETURN",f"{name} looks implausible: {v}",i,r.fund_id))
            for name in FEE_FIELDS:
                v = getattr(r, name)
                if v is not None and (v < 0 or v > 10): issues.append(ValidationIssue("warning","IMPLAUSIBLE_FEE",f"{name} looks implausible: {v}",i,r.fund_id))
            if r.assets_millions_nis is not None and r.assets_millions_nis < 0:
                issues.append(ValidationIssue("warning","NEGATIVE_ASSETS","Assets cannot be negative.",i,r.fund_id))
        return issues

    def latest_by_fund(self, records: Sequence[PensionRecord]) -> list[PensionRecord]:
        latest: dict[str, PensionRecord] = {}
        for r in records:
            key = r.fund_id or f"__row_{len(latest)}"
            if key not in latest or (r.report_date or dt.date.min) >= (latest[key].report_date or dt.date.min): latest[key] = r
        return list(latest.values())

    def filter_records(self, records: Sequence[PensionRecord], *, provider: str | None = None, fund_type: str | None = None, start_date: dt.date | None = None, end_date: dt.date | None = None) -> list[PensionRecord]:
        out = []
        for r in records:
            if provider and provider.lower() not in r.provider.lower(): continue
            if fund_type and fund_type.lower() not in r.fund_type.lower(): continue
            if start_date and (r.report_date is None or r.report_date < start_date): continue
            if end_date and (r.report_date is None or r.report_date > end_date): continue
            out.append(r)
        return out

    def rank(self, records: Sequence[PensionRecord], *, metric: str, top: int = 10, ascending: bool = False, latest_only: bool = True) -> list[PensionRecord]:
        if metric not in PensionRecord.__dataclass_fields__: raise ValueError(f"Unknown metric: {metric}")
        selected = self.latest_by_fund(records) if latest_only else list(records)
        with_values = [r for r in selected if getattr(r, metric) is not None]
        without_values = [r for r in selected if getattr(r, metric) is None]
        with_values.sort(key=lambda r: float(getattr(r, metric)), reverse=not ascending)
        return (with_values + without_values)[:top]

    def compare(self, records: Sequence[PensionRecord], fund_ids: Sequence[str], *, metrics: Sequence[str] | None = None, latest_only: bool = True) -> list[dict[str, Any]]:
        metrics = metrics or ("monthly_return_pct","year_to_date_return_pct","trailing_12m_return_pct","trailing_36m_return_pct","trailing_60m_return_pct","management_fee_deposit_pct","management_fee_assets_pct")
        selected = self.latest_by_fund(records) if latest_only else list(records)
        by_id = {r.fund_id: r for r in selected}
        out = []
        for fund_id in fund_ids:
            r = by_id.get(str(fund_id))
            if r is None:
                out.append({"fund_id": str(fund_id), "missing": True}); continue
            row = {"fund_id": r.fund_id, "fund_name": r.fund_name, "provider": r.provider, "report_date": r.report_date.isoformat() if r.report_date else None}
            for m in metrics:
                if m not in PensionRecord.__dataclass_fields__: raise ValueError(f"Unknown metric: {m}")
                row[m] = getattr(r, m)
            out.append(row)
        return out

    def estimate_fee_impact(self, *, monthly_contribution: float, years: int, annual_return_pct: float, deposit_fee_pct: float = 0.0, asset_fee_pct: float = 0.0, starting_balance: float = 0.0) -> FeeImpactResult:
        if years < 0: raise ValueError("years cannot be negative")
        if monthly_contribution < 0 or starting_balance < 0: raise ValueError("balances and contributions cannot be negative")
        months = years * 12
        monthly_return = (1 + annual_return_pct / 100) ** (1/12) - 1
        monthly_asset_fee = asset_fee_pct / 100 / 12
        gross = net = starting_balance
        for _ in range(months):
            gross = gross * (1 + monthly_return) + monthly_contribution
            net = net * (1 + monthly_return)
            net *= (1 - monthly_asset_fee)
            net += monthly_contribution * (1 - deposit_fee_pct / 100)
        return FeeImpactResult(monthly_contribution, starting_balance, years, annual_return_pct, deposit_fee_pct, asset_fee_pct, round(gross,2), round(net,2), round(gross-net,2), round(monthly_contribution*months,2))

    def score_funds(self, records: Sequence[PensionRecord], *, return_weight: float = 0.65, fee_weight: float = 0.35) -> list[ScoreResult]:
        if return_weight < 0 or fee_weight < 0 or return_weight + fee_weight == 0: raise ValueError("invalid weights")
        selected = self.latest_by_fund(records)
        def avg(vals: Iterable[float | None]) -> float | None:
            present = [v for v in vals if v is not None]
            return None if not present else sum(present) / len(present)
        returns = {r.fund_id: avg((r.year_to_date_return_pct,r.trailing_12m_return_pct,r.trailing_36m_return_pct,r.trailing_60m_return_pct)) for r in selected}
        fees = {r.fund_id: avg((r.management_fee_deposit_pct,r.management_fee_assets_pct)) for r in selected}
        return_scores, fee_scores = _minmax_scores(returns, higher_is_better=True), _minmax_scores(fees, higher_is_better=False)
        total_weight, results = return_weight + fee_weight, []
        for r in selected:
            caveats, comps = [], []
            rs, fs = return_scores.get(r.fund_id), fee_scores.get(r.fund_id)
            if rs is None: caveats.append("missing return metrics")
            else: comps.append((rs, return_weight))
            if fs is None: caveats.append("missing fee metrics")
            else: comps.append((fs, fee_weight))
            score = 0.0 if not comps else sum(v*w for v,w in comps) / sum(w for _,w in comps) * sum(w for _,w in comps) / total_weight
            if not comps: caveats.append("no scoreable metrics")
            results.append(ScoreResult(r.fund_id,r.fund_name,r.provider,r.report_date,round(score,2),None if rs is None else round(rs,2),None if fs is None else round(fs,2),tuple(caveats)))
        return sorted(results, key=lambda x: x.score, reverse=True)

    def export_json(self, records: Sequence[PensionRecord], path: str | Path) -> None:
        Path(path).write_text(json.dumps(records_to_dicts(records), ensure_ascii=False, indent=2), encoding="utf-8")

    def export_csv(self, records: Sequence[PensionRecord], path: str | Path) -> None:
        fields = [n for n in PensionRecord.__dataclass_fields__ if n != "raw"]
        with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
            for r in records:
                row = dataclasses.asdict(r); row.pop("raw", None)
                row["report_date"] = r.report_date.isoformat() if r.report_date else None
                writer.writerow(row)


class AsyncPensionFundTrackerClient:
    """Async wrapper around the synchronous public-data client."""
    def __init__(self, sync_client: PensionFundTrackerClient | None = None) -> None:
        self.sync_client = sync_client or PensionFundTrackerClient()
    async def load_csv(self, path: str | Path, *, encoding: str = "utf-8-sig") -> list[PensionRecord]:
        return await asyncio.to_thread(self.sync_client.load_csv, path, encoding=encoding)
    async def load_json(self, path: str | Path) -> list[PensionRecord]:
        return await asyncio.to_thread(self.sync_client.load_json, path)
    async def fetch_url(self, url: str, *, timeout: int = 30) -> list[PensionRecord]:
        return await asyncio.to_thread(self.sync_client.fetch_url, url, timeout=timeout)
    async def fetch_ckan(self, resource_id: str, *, base_url: str = "https://data.gov.il/api/3/action/datastore_search", limit: int = 1000, max_records: int | None = None, timeout: int = 30) -> list[PensionRecord]:
        return await asyncio.to_thread(self.sync_client.fetch_ckan, resource_id, base_url=base_url, limit=limit, max_records=max_records, timeout=timeout)
    def validate_records(self, records: Sequence[PensionRecord]) -> list[ValidationIssue]: return self.sync_client.validate_records(records)
    def latest_by_fund(self, records: Sequence[PensionRecord]) -> list[PensionRecord]: return self.sync_client.latest_by_fund(records)
    def rank(self, records: Sequence[PensionRecord], *, metric: str, top: int = 10, ascending: bool = False) -> list[PensionRecord]: return self.sync_client.rank(records, metric=metric, top=top, ascending=ascending)
    def compare(self, records: Sequence[PensionRecord], fund_ids: Sequence[str]) -> list[dict[str, Any]]: return self.sync_client.compare(records, fund_ids)
    def estimate_fee_impact(self, **kwargs: Any) -> FeeImpactResult: return self.sync_client.estimate_fee_impact(**kwargs)
