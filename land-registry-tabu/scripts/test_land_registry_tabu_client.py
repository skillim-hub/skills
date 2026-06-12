from __future__ import annotations

import asyncio
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from land_registry_tabu import (
    FileJsonTransport,
    LandRegistryTabuClient,
    ParcelId,
    TabuApiError,
    TabuClientConfig,
    TabuValidationError,
    extract_risk_flags,
    mask_identifier,
    normalize_date,
    normalize_right_type,
    normalize_share,
    parse_extract,
    parse_order,
    validate_israeli_id,
)
from land_registry_tabu.cli import cli


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).with_name("fixtures")


class FakeTransport:
    def __init__(self, payload, status_error=None):
        self.payload = payload
        self.status_error = status_error
        self.calls = []

    def request_json(self, method, url, *, headers, body, timeout):
        self.calls.append({"method": method, "url": url, "headers": dict(headers), "body": body, "timeout": timeout})
        if self.status_error:
            raise self.status_error
        return self.payload


@pytest.fixture()
def sample_payload():
    return {
        "property": {"block": 30001, "parcel": 12, "subparcel": 4, "address": "Example Street 10"},
        "retrieved_at": "2026-06-04T12:00:00Z",
        "rights": [
            {
                "owner_name": "Dana Cohen",
                "id": "123456782",
                "right_type": "ownership",
                "share": "50%",
                "deed_date": "2022-02-15",
                "deed_number": "1234/2022",
                "encumbrances": [
                    {
                        "type": "mortgage",
                        "beneficiary": "Example Bank Ltd.",
                        "amount_ils": "1,200,000",
                        "registered_date": "2022-02-15",
                    }
                ],
            }
        ],
        "warnings": [],
    }


def make_client(payload):
    return LandRegistryTabuClient(
        TabuClientConfig(base_url="https://adapter.example", api_key="secret", timeout_seconds=3),
        transport=FakeTransport(payload),
    )


def test_package_importable():
    module = importlib.import_module("land_registry_tabu")
    assert hasattr(module, "LandRegistryTabuClient")


def test_parcel_id_to_query_with_subparcel():
    assert ParcelId(30001, 12, 4).to_query() == {"block": 30001, "parcel": 12, "subparcel": 4}


def test_parcel_id_to_query_without_subparcel():
    assert ParcelId(30001, 12).to_query() == {"block": 30001, "parcel": 12}


@pytest.mark.parametrize("kwargs", [
    {"block": 0, "parcel": 1},
    {"block": 1, "parcel": 0},
    {"block": -1, "parcel": 1},
    {"block": 1, "parcel": 1, "subparcel": 0},
    {"block": 1000000, "parcel": 1},
])
def test_parcel_id_rejects_invalid_values(kwargs):
    with pytest.raises(TabuValidationError):
        ParcelId(**kwargs)


def test_display_he_includes_subparcel():
    assert ParcelId(30001, 12, 4).display_he() == "גוש 30001 חלקה 12 תת-חלקה 4"


def test_builds_parcel_url_and_auth_header(sample_payload):
    client = make_client(sample_payload)
    extract = client.get_by_parcel(ParcelId(30001, 12, 4))
    call = client.transport.calls[0]
    assert "block=30001" in call["url"]
    assert "parcel=12" in call["url"]
    assert "subparcel=4" in call["url"]
    assert call["headers"]["Authorization"] == "Bearer secret"
    assert extract.property_id.block == 30001


def test_search_by_address_builds_url(sample_payload):
    client = make_client(sample_payload)
    client.search_by_address(city="Tel Aviv-Yafo", street="Example Street", house=10)
    url = client.transport.calls[0]["url"]
    assert "/tabu/address?" in url
    assert "city=Tel+Aviv-Yafo" in url
    assert "street=Example+Street" in url
    assert "house=10" in url


def test_search_by_address_rejects_missing_city(sample_payload):
    client = make_client(sample_payload)
    with pytest.raises(TabuValidationError):
        client.search_by_address(city="", street="A", house=1)


def test_parse_extract_normalizes_owner_and_share(sample_payload):
    extract = parse_extract(sample_payload)
    assert extract.rights[0].owner_name == "Dana Cohen"
    assert extract.rights[0].share == "1/2"
    assert extract.rights[0].id_masked == "******782"


def test_parse_extract_normalizes_date(sample_payload):
    extract = parse_extract(sample_payload)
    assert extract.rights[0].deed_date == "15/02/2022"


def test_parse_extract_normalizes_encumbrance(sample_payload):
    extract = parse_extract(sample_payload)
    enc = extract.rights[0].encumbrances[0]
    assert enc.type == "mortgage"
    assert enc.amount_ils == 1200000.0
    assert enc.registered_date == "15/02/2022"


def test_hebrew_payload_parses():
    payload = {
        "נכס": {"גוש": 7, "חלקה": 8, "תת-חלקה": 9, "כתובת": "רחוב הבדיקה 1"},
        "בעלי זכויות": [{"שם": "דנה כהן", "תעודת זהות": "123456782", "סוג זכות": "בעלות", "חלק": "50%"}],
        "אזהרות": ["בדקו מסמכים"],
    }
    extract = parse_extract(payload)
    assert extract.property_id.to_query() == {"block": 7, "parcel": 8, "subparcel": 9}
    assert extract.address == "רחוב הבדיקה 1"
    assert extract.rights[0].right_type == "ownership"
    assert extract.warnings == ("בדקו מסמכים",)


@pytest.mark.parametrize("value,expected", [
    ("50%", "1/2"),
    ("0.25", "1/4"),
    ("1/2", "1/2"),
    ("2/4", "1/2"),
    (1, "1/1"),
    ("unknown", "unknown"),
])
def test_normalize_share(value, expected):
    assert normalize_share(value) == expected


@pytest.mark.parametrize("value,expected", [
    ("2022-02-15", "15/02/2022"),
    ("15/02/2022", "15/02/2022"),
    ("15-02-2022", "15/02/2022"),
    ("not-a-date", "not-a-date"),
    (None, None),
])
def test_normalize_date(value, expected):
    assert normalize_date(value) == expected


@pytest.mark.parametrize("identifier,expected", [
    ("123456782", True),
    ("000000018", True),
    ("123456789", False),
    ("abc", False),
    ("1234567890", False),
])
def test_validate_israeli_id(identifier, expected):
    assert validate_israeli_id(identifier) is expected


def test_mask_identifier_masks_all_but_three():
    assert mask_identifier("123456782") == "******782"


def test_extract_risk_flags_for_mortgage(sample_payload):
    extract = parse_extract(sample_payload)
    flags = extract_risk_flags(extract)
    assert any("Mortgage requires" in flag for flag in flags)


def test_extract_risk_flags_for_missing_property_id():
    extract = parse_extract({"rights": []})
    flags = extract_risk_flags(extract)
    assert any("Property identifier" in flag for flag in flags)


def test_to_json_contains_property(sample_payload):
    extract = parse_extract(sample_payload)
    data = json.loads(extract.to_json())
    assert data["property_id"]["block"] == 30001


def test_raw_payload_retained(sample_payload):
    extract = parse_extract(sample_payload)
    assert extract.raw is sample_payload


def test_file_transport_reads_fixture():
    transport = FileJsonTransport(FIXTURES / "sample_parcel_response.json")
    payload = transport.request_json("GET", "https://example", headers={}, body=None, timeout=1)
    assert payload["property"]["block"] == 30001


def test_file_transport_order_fixture():
    transport = FileJsonTransport(FIXTURES / "sample_parcel_response.json", FIXTURES / "sample_order_response.json")
    payload = transport.request_json("GET", "https://example/tabu/extract-orders/ORD-SANDBOX-0001", headers={}, body=None, timeout=1)
    assert payload["order_id"] == "ORD-SANDBOX-0001"


def test_client_raises_transport_api_error(sample_payload):
    error = TabuApiError(401, "UNAUTHORIZED", "bad token")
    client = LandRegistryTabuClient(
        TabuClientConfig(base_url="https://adapter.example"),
        transport=FakeTransport(sample_payload, status_error=error),
    )
    with pytest.raises(TabuApiError) as caught:
        client.get_by_parcel(ParcelId(1, 2))
    assert caught.value.status_code == 401


def test_parse_without_rights_adds_warning():
    extract = parse_extract({"property": {"block": 1, "parcel": 2}})
    assert "No rights were parsed" in extract.warnings[0]


def test_has_encumbrances_true(sample_payload):
    assert parse_extract(sample_payload).has_encumbrances is True


def test_has_encumbrances_false():
    payload = {"property": {"block": 1, "parcel": 2}, "rights": [{"owner_name": "A", "right_type": "ownership"}]}
    assert parse_extract(payload).has_encumbrances is False


def test_async_get_by_parcel(sample_payload):
    client = make_client(sample_payload)
    extract = asyncio.run(client.async_get_by_parcel(ParcelId(30001, 12, 4)))
    assert extract.property_id.parcel == 12


def test_async_search_by_address(sample_payload):
    client = make_client(sample_payload)
    extract = asyncio.run(client.async_search_by_address(city="Tel Aviv-Yafo", street="Example", house=10))
    assert extract.address == "Example Street 10"


def test_invalid_fraction_raises():
    with pytest.raises(TabuValidationError):
        normalize_share("1/0")


def test_right_type_hebrew_caveat():
    assert normalize_right_type("הערת אזהרה") == "caveat"


def test_optional_float_handles_shekel_text():
    payload = {
        "property": {"block": 1, "parcel": 2},
        "rights": [{
            "owner_name": "A",
            "right_type": "ownership",
            "encumbrances": [{"type": "mortgage", "amount": "₪2,500"}],
        }],
    }
    extract = parse_extract(payload)
    assert extract.rights[0].encumbrances[0].amount_ils == 2500.0


def test_create_extract_order_builds_body():
    client = LandRegistryTabuClient(TabuClientConfig(base_url="https://adapter.example"), transport=FakeTransport({
        "order_id": "ORD-1",
        "status": "created",
        "created_at": "2026-06-04T12:00:00Z",
        "property": {"block": 1, "parcel": 2, "subparcel": 3},
        "payment_reference": "PAY-1",
    }))
    order = client.create_extract_order(ParcelId(1, 2, 3), payment_reference="PAY-1", idempotency_key="idem")
    call = client.transport.calls[0]
    assert call["method"] == "POST"
    assert call["body"]["property_id"] == {"block": 1, "parcel": 2, "subparcel": 3}
    assert call["headers"]["Idempotency-Key"] == "idem"
    assert order.order_id == "ORD-1"


def test_async_create_extract_order():
    client = LandRegistryTabuClient(TabuClientConfig(base_url="https://adapter.example"), transport=FakeTransport({
        "order_id": "ORD-2",
        "status": "created",
        "created_at": "2026-06-04T12:00:00Z",
    }))
    order = asyncio.run(client.async_create_extract_order(ParcelId(1, 2)))
    assert order.order_id == "ORD-2"


def test_get_order_status_builds_url():
    client = LandRegistryTabuClient(TabuClientConfig(base_url="https://adapter.example"), transport=FakeTransport({
        "order_id": "ORD-3",
        "status": "ready",
        "created_at": "2026-06-04T12:00:00Z",
    }))
    order = client.get_order_status("ORD-3")
    assert client.transport.calls[0]["method"] == "GET"
    assert "/tabu/extract-orders/ORD-3" in client.transport.calls[0]["url"]
    assert order.status == "ready"


def test_parse_order_fallback_property():
    order = parse_order({"status": "created"}, fallback_property_id=ParcelId(1, 2))
    assert order.order_id.startswith("ORD-")
    assert order.property_id.parcel == 2


def test_cli_parcel_json():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--mock-file", str(FIXTURES / "sample_parcel_response.json"),
        "parcel", "--block", "30001", "--parcel", "12", "--subparcel", "4",
    ])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["property_id"]["block"] == 30001


def test_cli_create_order_and_status_chain():
    runner = CliRunner()
    common = [
        "--mock-file", str(FIXTURES / "sample_parcel_response.json"),
        "--order-mock-file", str(FIXTURES / "sample_order_response.json"),
    ]
    created = runner.invoke(cli, common + ["create-order", "--block", "30001", "--parcel", "12", "--subparcel", "4"])
    assert created.exit_code == 0
    order_id = json.loads(created.output)["order_id"]
    status = runner.invoke(cli, common + ["order-status", "--order-id", order_id])
    assert status.exit_code == 0
    assert json.loads(status.output)["order_id"] == order_id


def test_cli_env_option_production(monkeypatch):
    monkeypatch.setenv("TABU_PRODUCTION_BASE_URL", "https://prod.example")
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--env", "production",
        "--mock-file", str(FIXTURES / "sample_parcel_response.json"),
        "parcel", "--block", "30001", "--parcel", "12",
    ])
    assert result.exit_code == 0


def test_cli_validate_id():
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-id", "123456782"])
    assert result.output.strip() == "valid"


def test_underscored_script_compatibility_compiles():
    script = Path(__file__).with_name("land_registry_tabu_client.py")
    assert script.exists()
    assert "land_registry_tabu.client" in script.read_text(encoding="utf-8")


def test_hyphenated_client_removed():
    assert not Path(__file__).with_name("land-registry-tabu-client.py").exists()


def test_example_scripts_accept_env_and_use_json_dumps():
    for path in (Path(__file__).with_name("examples")).glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "--env" in text
        assert "os.getenv" in text
        assert "json.dumps" in text
        assert "ensure_ascii=False" in text
        assert "indent=2" in text


def test_example_fetch_runs_with_pythonpath(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    script = Path(__file__).with_name("examples") / "fetch_by_parcel_mock.py"
    proc = subprocess.run([sys.executable, str(script), "--env", "sandbox"], cwd=ROOT, env=env, text=True, capture_output=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["property_id"]["parcel"] == 12
