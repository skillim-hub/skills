from __future__ import annotations

import csv
import json

import httpx
import pytest

import cbs_data_analyzer_client as client


SAMPLE_SERIES = {
    "month": [
        {
            "code": 120010,
            "name": "Consumer Price Index",
            "date": [
                {
                    "year": 2026,
                    "month": 4,
                    "monthDesc": "April",
                    "currBase": {"value": "106.4"},
                    "percent": "1.2",
                    "percentYear": "1.9",
                },
                {
                    "year": 2026,
                    "month": 3,
                    "monthDesc": "March",
                    "currBase": {"value": "105.2"},
                    "percent": "-0.1",
                    "percentYear": "1.7",
                },
                {
                    "year": 2025,
                    "month": 4,
                    "monthDesc": "April",
                    "currBase": {"value": "104.4"},
                    "percent": "0.4",
                    "percentYear": "2.2",
                },
            ],
        }
    ]
}

CATALOG = {
    "chapters": [
        {"mainCode": 120010, "chapterName": "Consumer Price Index - General"},
        {"mainCode": 40010, "chapterName": "מדד מחירי דירות"},
        {"mainCode": 170030, "chapterName": "Producer prices"},
    ]
}


def json_response(data, status_code=200):
    return httpx.Response(status_code, json=data)


def make_transport(handler):
    return httpx.MockTransport(handler)


def test_to_float_accepts_numbers_and_strings():
    assert client._to_float(10) == 10.0
    assert client._to_float("1,234.5") == 1234.5


def test_to_float_rejects_empty_bool_and_bad_text():
    assert client._to_float("") is None
    assert client._to_float(True) is None
    assert client._to_float("not-a-number") is None


def test_parse_price_series_basic_shape():
    series = client.parse_price_series(SAMPLE_SERIES, index_id=120010, source_url="source")
    assert series.code == 120010
    assert series.name == "Consumer Price Index"
    assert len(series.points) == 3


def test_parse_price_series_extracts_period_and_values():
    series = client.parse_price_series(SAMPLE_SERIES)
    point = series.points[0]
    assert point.period == "04-2026"
    assert point.year == 2026
    assert point.month == 4
    assert point.value == 106.4
    assert point.monthly_change == 1.2
    assert point.annual_change == 1.9


def test_latest_uses_chronological_max():
    payload = {
        "month": [
            {
                "code": 1,
                "name": "x",
                "date": [
                    {"year": 2025, "month": 12, "currBase": {"value": 10}},
                    {"year": 2026, "month": 1, "currBase": {"value": 11}},
                ],
            }
        ]
    }
    series = client.parse_price_series(payload)
    assert series.latest.period == "01-2026"


def test_recent_returns_newest_first():
    series = client.parse_price_series(SAMPLE_SERIES)
    recent = series.recent(2)
    assert [p.period for p in recent] == ["04-2026", "03-2026"]


def test_parse_missing_payload_returns_empty_series():
    series = client.parse_price_series({"unexpected": []}, index_id=999)
    assert series.code == 999
    assert series.points == []


def test_month_description_hebrew_is_parsed():
    payload = {"month": [{"name": "x", "date": [{"year": 2026, "monthDesc": "אפריל", "value": 1}]}]}
    series = client.parse_price_series(payload)
    assert series.points[0].month == 4
    assert series.points[0].period == "04-2026"


def test_calculate_indexation_increase():
    result = client.calculate_indexation(original_amount=5200, base_index=103.1, target_index=106.4)
    assert round(result.adjusted_amount, 2) == 5366.44
    assert round(result.percent_change, 2) == 3.20
    assert result.floor_applied is False


def test_calculate_indexation_decrease():
    result = client.calculate_indexation(original_amount=5200, base_index=106.4, target_index=103.1)
    assert result.adjusted_amount < 5200
    assert result.percent_change < 0


def test_calculate_indexation_floor_zero():
    result = client.calculate_indexation(
        original_amount=5200, base_index=106.4, target_index=103.1, floor_zero=True
    )
    assert result.adjusted_amount == 5200
    assert result.percent_change == 0
    assert result.floor_applied is True


def test_calculate_indexation_round_to_shekel():
    result = client.calculate_indexation(
        original_amount=5200, base_index=103.1, target_index=106.4, round_to_shekel=True
    )
    assert result.adjusted_amount == 5366


@pytest.mark.parametrize(
    "kwargs",
    [
        {"original_amount": -1, "base_index": 100, "target_index": 101},
        {"original_amount": 1, "base_index": 0, "target_index": 101},
        {"original_amount": 1, "base_index": 100, "target_index": 0},
    ],
)
def test_calculate_indexation_validates_inputs(kwargs):
    with pytest.raises(ValueError):
        client.calculate_indexation(**kwargs)


def test_format_nis_localizes_shekel_amount():
    assert client.format_nis(5366.444) == "₪5,366.44"


def test_detect_trend_rising_falling_stable():
    rising = client.parse_price_series(
        {"month": [{"name": "x", "date": [{"year": 2026, "month": 1, "value": 100}, {"year": 2026, "month": 2, "value": 101}]}]}
    )
    falling = client.parse_price_series(
        {"month": [{"name": "x", "date": [{"year": 2026, "month": 1, "value": 101}, {"year": 2026, "month": 2, "value": 100}]}]}
    )
    stable = client.parse_price_series(
        {"month": [{"name": "x", "date": [{"year": 2026, "month": 1, "value": 100}, {"year": 2026, "month": 2, "value": 100.01}]}]}
    )
    assert client.detect_trend(rising.points) == "rising"
    assert client.detect_trend(falling.points) == "falling"
    assert client.detect_trend(stable.points) == "stable"


def test_build_market_brief_contains_limitations():
    series = client.parse_price_series(SAMPLE_SERIES)
    brief = client.build_market_brief(question="Open a café", geography="Haifa", series=series)
    assert brief["question"] == "Open a café"
    assert brief["geography"] == "Haifa"
    assert brief["latest_period"] == "04-2026"
    assert brief["limitations"]


def test_sync_get_catalog_and_search_catalog():
    def handler(request):
        assert request.url.path.endswith("/catalog/catalog")
        return json_response(CATALOG)

    c = client.CBSDataAnalyzerClient(transport=make_transport(handler))
    try:
        matches = c.search_catalog("דירות")
        assert len(matches) == 1
        assert matches[0]["mainCode"] == 40010
    finally:
        c.close()


def test_sync_search_catalog_empty_query_skips_request():
    c = client.CBSDataAnalyzerClient(transport=make_transport(lambda request: pytest.fail("no request expected")))
    try:
        assert c.search_catalog("   ") == []
    finally:
        c.close()


def test_sync_get_price_index_normalizes_response():
    def handler(request):
        assert request.url.path.endswith("/data/price")
        assert request.url.params["id"] == "120010"
        return json_response(SAMPLE_SERIES)

    c = client.CBSDataAnalyzerClient(transport=make_transport(handler))
    try:
        series = c.get_price_index(120010)
        assert series.latest.value == 106.4
        assert "id=120010" in series.source_url
    finally:
        c.close()


def test_get_known_index_uses_mapping():
    def handler(request):
        assert request.url.params["id"] == "120010"
        return json_response(SAMPLE_SERIES)

    c = client.CBSDataAnalyzerClient(transport=make_transport(handler))
    try:
        assert c.get_known_index("cpi").code == 120010
    finally:
        c.close()


def test_get_known_index_unknown_key_raises():
    c = client.CBSDataAnalyzerClient(transport=make_transport(lambda request: json_response({})))
    try:
        with pytest.raises(KeyError):
            c.get_known_index("unknown")
    finally:
        c.close()


def test_http_error_raises_structured_error():
    c = client.CBSDataAnalyzerClient(transport=make_transport(lambda request: httpx.Response(404, text="missing")))
    try:
        with pytest.raises(client.CBSAPIError) as exc:
            c.get_catalog()
        assert exc.value.status_code == 404
        assert "HTTP 404" in str(exc.value)
    finally:
        c.close()


def test_non_json_raises_structured_error():
    c = client.CBSDataAnalyzerClient(transport=make_transport(lambda request: httpx.Response(200, text="<html>")))
    try:
        with pytest.raises(client.CBSAPIError) as exc:
            c.get_catalog()
        assert "valid JSON" in str(exc.value)
    finally:
        c.close()


def test_data_gov_search_uses_lamas_filter():
    observed = {}

    def handler(request):
        observed["url"] = str(request.url)
        return json_response({"success": True, "result": {"count": 0, "results": []}})

    c = client.CBSDataAnalyzerClient(transport=make_transport(handler))
    try:
        payload = c.search_data_gov("population", rows=5)
        assert payload["success"] is True
        assert "organization%3Alamas" in observed["url"]
        assert "rows=5" in observed["url"]
    finally:
        c.close()


def test_export_series_csv(tmp_path):
    series = client.parse_price_series(SAMPLE_SERIES)
    c = client.CBSDataAnalyzerClient(transport=make_transport(lambda request: json_response({})))
    try:
        target = c.export_series_csv(series, tmp_path / "series.csv")
        rows = list(csv.DictReader(target.open(encoding="utf-8")))
        assert len(rows) == 3
        assert rows[0]["period"] == "04-2026"
    finally:
        c.close()


@pytest.mark.asyncio
async def test_async_get_catalog_and_search():
    async def handler(request):
        return json_response(CATALOG)

    c = client.AsyncCBSDataAnalyzerClient(transport=httpx.MockTransport(handler))
    try:
        matches = await c.search_catalog("producer")
        assert matches[0]["mainCode"] == 170030
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_async_get_price_index():
    async def handler(request):
        assert request.url.params["id"] == "120010"
        return json_response(SAMPLE_SERIES)

    async with client.AsyncCBSDataAnalyzerClient(transport=httpx.MockTransport(handler)) as c:
        series = await c.get_price_index(120010)
    assert series.latest.period == "04-2026"


@pytest.mark.asyncio
async def test_async_data_gov_search():
    async def handler(request):
        assert "organization%3Alamas" in str(request.url)
        return json_response({"success": True, "result": {"count": 1, "results": [{"name": "demo"}]}})

    async with client.AsyncCBSDataAnalyzerClient(transport=httpx.MockTransport(handler)) as c:
        payload = await c.search_data_gov("locality")
    assert payload["result"]["count"] == 1


def test_series_to_dict_is_json_serializable():
    series = client.parse_price_series(SAMPLE_SERIES)
    dumped = json.dumps(series.to_dict(), ensure_ascii=False)
    assert "Consumer Price Index" in dumped


def test_error_keeps_response_text():
    c = client.CBSDataAnalyzerClient(transport=make_transport(lambda request: httpx.Response(503, text="maintenance")))
    try:
        with pytest.raises(client.CBSAPIError) as exc:
            c.get_catalog()
        assert exc.value.response_text == "maintenance"
    finally:
        c.close()


def test_get_price_index_passes_documented_optional_parameters():
    observed = {}

    def handler(request):
        observed["params"] = dict(request.url.params)
        return json_response(SAMPLE_SERIES)

    c = client.CBSDataAnalyzerClient(transport=make_transport(handler))
    try:
        series = c.get_price_index(
            120010,
            start_period="01-2025",
            end_period="04-2026",
            last=3,
            coef=True,
        )
        assert series.code == 120010
        assert observed["params"]["startPeriod"] == "01-2025"
        assert observed["params"]["endPeriod"] == "04-2026"
        assert observed["params"]["last"] == "3"
        assert observed["params"]["coef"] == "true"
        assert observed["params"]["download"] == "false"
    finally:
        c.close()


def test_get_price_index_rejects_non_positive_last():
    c = client.CBSDataAnalyzerClient(transport=make_transport(lambda request: json_response(SAMPLE_SERIES)))
    try:
        with pytest.raises(ValueError):
            c.get_price_index(120010, last=0)
    finally:
        c.close()


@pytest.mark.asyncio
async def test_async_get_price_index_passes_last_parameter():
    observed = {}

    async def handler(request):
        observed["params"] = dict(request.url.params)
        return json_response(SAMPLE_SERIES)

    async with client.AsyncCBSDataAnalyzerClient(transport=httpx.MockTransport(handler)) as c:
        series = await c.get_price_index(120010, last=2, coef=False)
    assert series.latest.value == 106.4
    assert observed["params"]["last"] == "2"
    assert observed["params"]["coef"] == "false"
