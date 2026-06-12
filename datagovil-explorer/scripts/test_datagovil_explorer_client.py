from __future__ import annotations

import asyncio
import inspect
import json
import urllib.error
from typing import Any, List

import pytest
from click.testing import CliRunner

from datagovil_explorer import (
    AsyncDatagovClient,
    DatagovAPIError,
    DatagovClient,
    DatagovDecodeError,
    DatagovHTTPError,
    RequestConfig,
    base_url_for_env,
    extract_first_dataset_id,
    extract_first_resource_id,
    format_israeli_date,
    format_shekel,
    parse_filter_pairs,
)
from datagovil_explorer.cli import cli


class FakeResponse:
    def __init__(self, payload: Any):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        if isinstance(self.payload, bytes):
            return self.payload
        return json.dumps(self.payload, ensure_ascii=False).encode("utf-8")


class FakeOpener:
    def __init__(self, payloads: List[Any]):
        self.payloads = list(payloads)
        self.calls = []

    def open(self, request, timeout):
        self.calls.append((request, timeout))
        payload = self.payloads.pop(0)
        if isinstance(payload, BaseException):
            raise payload
        return FakeResponse(payload)


def ok(result):
    return {"success": True, "result": result}


def make_client(payloads, **config_kwargs):
    opener = FakeOpener(payloads)
    config = RequestConfig(**config_kwargs)
    client = DatagovClient(config=config, opener=opener, sleep=lambda _: None)
    return client, opener


def test_action_url_encodes_hebrew():
    client = DatagovClient(config=RequestConfig(base_url="https://example.test/api/3"))
    url = client.action_url("package_search", {"q": "רישוי עסקים", "rows": 5})
    assert "%D7%A8" in url
    assert "rows=5" in url
    assert url.startswith("https://example.test/api/3/action/package_search?")


def test_action_url_accepts_action_prefix():
    client = DatagovClient(config=RequestConfig(base_url="https://example.test/api/3/"))
    assert client.action_url("action/package_show", {"id": "abc"}).startswith("https://example.test/api/3/action/package_show")


def test_get_action_unwraps_result():
    client, opener = make_client([ok({"count": 1})])
    result = client.get_action("package_search", {"q": "x"})
    assert result == {"count": 1}
    assert opener.calls[0][1] == 30.0


def test_get_action_sets_headers():
    client, opener = make_client([ok({})])
    client.get_action("package_search", {"q": "x"})
    request = opener.calls[0][0]
    assert request.get_header("Accept") == "application/json"
    assert "datagovil-explorer" in request.get_header("User-agent")


def test_get_action_raises_api_error():
    client, _ = make_client([{"success": False, "error": {"message": "bad"}}])
    with pytest.raises(DatagovAPIError):
        client.get_action("package_show", {"id": "missing"})


def test_get_action_raises_decode_error_on_invalid_json():
    client, _ = make_client([b"not-json"])
    with pytest.raises(DatagovDecodeError):
        client.get_action("package_search")


def test_get_action_raises_http_error():
    err = urllib.error.HTTPError("https://x", 404, "Not Found", {}, None)
    client, _ = make_client([err])
    with pytest.raises(DatagovHTTPError) as exc:
        client.get_action("package_show")
    assert exc.value.status == 404


def test_retries_temporary_url_error_then_succeeds():
    err = urllib.error.URLError("temporary")
    client, opener = make_client([err, ok({"count": 2})])
    result = client.get_action("package_search")
    assert result["count"] == 2
    assert len(opener.calls) == 2


def test_package_search_parameters():
    client, opener = make_client([ok({"count": 0, "results": []})])
    client.package_search("חינוך", rows=7, start=3, fq="organization:ministry_of_education", sort="metadata_modified desc")
    url = opener.calls[0][0].full_url
    assert "rows=7" in url
    assert "start=3" in url
    assert "organization%3Aministry_of_education" in url
    assert "metadata_modified+desc" in url


def test_package_search_rejects_negative_rows():
    client, _ = make_client([])
    with pytest.raises(ValueError):
        client.package_search("x", rows=-1)


def test_package_show_calls_expected_action():
    client, opener = make_client([ok({"name": "abc"})])
    assert client.package_show("abc")["name"] == "abc"
    assert "/package_show?" in opener.calls[0][0].full_url


def test_resource_show_calls_expected_action():
    client, opener = make_client([ok({"id": "res"})])
    assert client.resource_show("res")["id"] == "res"
    assert "resource_show" in opener.calls[0][0].full_url


def test_datastore_search_encodes_filters_and_fields():
    client, opener = make_client([ok({"records": []})])
    client.datastore_search("res", limit=10, offset=5, fields=["שם_ישוב", "סכום"], filters={"שם_ישוב": "חיפה"}, sort="_id asc")
    url = opener.calls[0][0].full_url
    assert "resource_id=res" in url
    assert "limit=10" in url
    assert "offset=5" in url
    assert "%D7%A9%D7%9D_%D7%99%D7%A9%D7%95%D7%91" in url
    assert "_id+asc" in url


def test_datastore_search_uses_string_fields():
    client, opener = make_client([ok({"records": []})])
    client.datastore_search("res", fields="a,b")
    assert "fields=a%2Cb" in opener.calls[0][0].full_url


def test_datastore_search_rejects_negative_offset():
    client, _ = make_client([])
    with pytest.raises(ValueError):
        client.datastore_search("res", offset=-1)


def test_datastore_search_all_pages_until_short_page():
    client, _ = make_client([ok({"records": [{"_id": 1}, {"_id": 2}]}), ok({"records": [{"_id": 3}]})])
    rows = list(client.datastore_search_all("res", page_size=2))
    assert [row["_id"] for row in rows] == [1, 2, 3]


def test_datastore_search_all_respects_max_records():
    client, _ = make_client([ok({"records": [{"_id": 1}, {"_id": 2}, {"_id": 3}]})])
    rows = list(client.datastore_search_all("res", page_size=10, max_records=2))
    assert [row["_id"] for row in rows] == [1, 2]


def test_datastore_search_all_rejects_zero_page_size():
    client, _ = make_client([])
    with pytest.raises(ValueError):
        list(client.datastore_search_all("res", page_size=0))


def test_tabular_resources_prefers_datastore_and_files():
    dataset = {"resources": [
        {"id": "a", "datastore_active": True, "format": "TXT"},
        {"id": "b", "datastore_active": False, "format": "CSV"},
        {"id": "c", "datastore_active": False, "format": "PDF"},
    ]}
    assert [r["id"] for r in DatagovClient.tabular_resources(dataset)] == ["a", "b"]


def test_tabular_resources_handles_bad_resources():
    assert DatagovClient.tabular_resources({"resources": "bad"}) == []


def test_write_csv_writes_union_of_fields(tmp_path):
    path = tmp_path / "out.csv"
    count = DatagovClient.write_csv([{"a": 1}, {"b": "חיפה"}], path)
    assert count == 2
    text = path.read_text(encoding="utf-8-sig")
    assert "a,b" in text.splitlines()[0]
    assert "חיפה" in text


def test_parse_filter_pairs():
    assert parse_filter_pairs(["שם_ישוב=חיפה", "type=school"]) == {"שם_ישוב": "חיפה", "type": "school"}


def test_parse_filter_pairs_rejects_missing_equals():
    with pytest.raises(ValueError):
        parse_filter_pairs(["bad"])


def test_parse_filter_pairs_rejects_empty_key():
    with pytest.raises(ValueError):
        parse_filter_pairs([" =value"])


def test_format_israeli_date_from_date():
    assert format_israeli_date("2026-06-02") == "02/06/2026"


def test_format_israeli_date_from_timestamp():
    assert format_israeli_date("2026-06-02T10:00:00") == "02/06/2026"


def test_format_shekel_integer():
    assert format_shekel("12345") == "₪12,345"


def test_format_shekel_decimal():
    assert format_shekel("12345.5") == "₪12,345.50"


def test_extract_first_dataset_id():
    assert extract_first_dataset_id({"results": [{"name": "dataset-a"}]}) == "dataset-a"


def test_extract_first_dataset_id_handles_empty():
    assert extract_first_dataset_id({"results": []}) is None


def test_extract_first_resource_id_prefers_datastore():
    dataset = {"resources": [{"id": "file"}, {"id": "store", "datastore_active": True}]}
    assert extract_first_resource_id(dataset) == "store"


def test_extract_first_resource_id_any_resource():
    dataset = {"resources": [{"id": "file"}, {"id": "store", "datastore_active": True}]}
    assert extract_first_resource_id(dataset, prefer_datastore=False) == "file"


def test_base_url_for_env_uses_env(monkeypatch):
    monkeypatch.setenv("DATAGOVIL_SANDBOX_BASE_URL", "https://sandbox.example/api/3/")
    assert base_url_for_env("sandbox") == "https://sandbox.example/api/3"


def test_base_url_for_env_rejects_unknown():
    with pytest.raises(ValueError):
        base_url_for_env("qa")


def test_async_package_search():
    client, _ = make_client([ok({"count": 4})])
    async_client = AsyncDatagovClient(client)
    result = asyncio.run(async_client.package_search("תחבורה", rows=1))
    assert result["count"] == 4


def test_async_datastore_search_all_returns_list():
    client, _ = make_client([ok({"records": [{"_id": 1}]}), ok({"records": []})])
    async_client = AsyncDatagovClient(client)
    rows = asyncio.run(async_client.datastore_search_all("res", page_size=1))
    assert rows == [{"_id": 1}]


def test_async_org_and_tags():
    client, _ = make_client([ok({"org": True}), ok(["a", "b"])])
    async_client = AsyncDatagovClient(client)
    assert asyncio.run(async_client.organization_list(all_fields=True))["org"] is True
    assert asyncio.run(async_client.tag_list()) == {"value": ["a", "b"]}


def test_list_endpoints_wrap_list_result():
    client, _ = make_client([{"success": True, "result": ["a", "b"]}])
    result = client.organization_list()
    assert result == {"value": ["a", "b"]}


def test_custom_timeout_and_base_url():
    client, opener = make_client([ok({})], base_url="https://example.test/api/3", timeout=7.5)
    client.get_action("tag_list")
    assert opener.calls[0][1] == 7.5
    assert opener.calls[0][0].full_url.startswith("https://example.test/api/3/action/tag_list")


def test_cli_search_json_with_fake_client(monkeypatch):
    class LocalClient:
        def __init__(self, *args, **kwargs):
            pass
        def package_search(self, query, **kwargs):
            return {"count": 1, "results": [{"name": "abc", "title": "ABC"}]}
    monkeypatch.setattr("datagovil_explorer.cli.DatagovClient", LocalClient)
    result = CliRunner().invoke(cli, ["search", "תחבורה", "--json-output"])
    assert result.exit_code == 0
    assert '"count": 1' in result.output


def test_cli_first_dataset_id_with_fake_client(monkeypatch):
    class LocalClient:
        def __init__(self, *args, **kwargs):
            pass
        def package_search(self, query, **kwargs):
            return {"results": [{"name": "abc"}]}
    monkeypatch.setattr("datagovil_explorer.cli.DatagovClient", LocalClient)
    result = CliRunner().invoke(cli, ["first-dataset-id", "תחבורה"])
    assert result.exit_code == 0
    assert result.output.strip() == "abc"


def test_public_method_count_is_stable():
    names = [name for name, value in inspect.getmembers(DatagovClient, predicate=inspect.isfunction) if not name.startswith("_")]
    assert len(names) >= 10
