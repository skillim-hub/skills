from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from import_export_tariff_advisor import LineItem, TariffAdvisorClient, TariffAdvisorError
from import_export_tariff_advisor import MoneyValidationError, RateValidationError, normalize_tariff_code

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "import-export-tariff-advisor-cli.py"


def client(**kwargs):
    return TariffAdvisorClient(**kwargs)


def test_normalize_tariff_code():
    assert normalize_tariff_code("85.18-30 0000") == "8518300000"


def test_normalize_empty_code():
    assert normalize_tariff_code(" -- ") is None


def test_consumer_headphones_vat():
    result = client().estimate(
        description="Bluetooth headphones",
        goods_value=120,
        shipping=20,
        exchange_rate_to_ils=3.70,
        vat_rate=0.18,
        non_tax_fees_ils=35,
    )
    assert result.customs_value == Decimal("518.00")
    assert result.vat == Decimal("93.24")
    assert result.landed_cost == Decimal("646.24")


def test_business_laptop():
    result = client().estimate(
        description="Laptop computer",
        goods_value=1000,
        shipping=60,
        exchange_rate_to_ils=3.70,
    )
    assert result.customs_value == Decimal("3922.00")
    assert result.vat == Decimal("705.96")


def test_purchase_tax_in_vat_base():
    result = client().estimate(
        description="Wine for resale",
        goods_value=12000,
        exchange_rate_to_ils=1,
        duty_rate=0.12,
        purchase_tax_rate=0.20,
        vat_rate=0.18,
    )
    assert result.customs_duty == Decimal("1440.00")
    assert result.purchase_tax == Decimal("2688.00")
    assert result.vat_base == Decimal("16128.00")
    assert result.vat == Decimal("2903.04")


def test_repair_example():
    result = client().estimate(
        description="Returned repaired item",
        goods_value=150,
        shipping=40,
        exchange_rate_to_ils=4,
        vat_rate=0.18,
    )
    assert result.customs_value == Decimal("760.00")
    assert result.vat == Decimal("136.80")


def test_reject_negative_goods():
    with pytest.raises(MoneyValidationError):
        client().estimate(description="Laptop", goods_value=-1)


def test_reject_zero_exchange_rate():
    with pytest.raises(MoneyValidationError):
        client().estimate(description="Laptop", goods_value=1, exchange_rate_to_ils=0)


def test_reject_rate_above_one():
    with pytest.raises(RateValidationError):
        client().estimate(description="Laptop", goods_value=1, vat_rate=18)


def test_reject_negative_rate():
    with pytest.raises(RateValidationError):
        client().estimate(description="Laptop", goods_value=1, duty_rate=-0.1)


def test_reject_short_description():
    with pytest.raises(TariffAdvisorError):
        client().estimate(description="x", goods_value=1)


def test_environment_validation():
    with pytest.raises(TariffAdvisorError):
        client().estimate(description="Laptop", goods_value=1, environment="staging")


def test_production_warning():
    result = client().estimate(description="Laptop", goods_value=100, environment="production")
    assert any("Production environment" in w for w in result.warnings)


def test_wireless_warning():
    result = client().estimate(description="Wi-Fi router", goods_value=90, shipping=10)
    assert any("Wireless" in w for w in result.warnings)


def test_food_warning():
    result = client().estimate(description="Vitamin supplement", goods_value=90)
    assert any("Food" in w for w in result.warnings)


def test_cosmetic_warning():
    result = client().estimate(description="Face cream cosmetic", goods_value=90)
    assert any("Cosmetics" in w for w in result.warnings)


def test_medical_warning():
    result = client().estimate(description="Medical blood pressure device", goods_value=90)
    assert any("Medical" in w for w in result.warnings)


def test_vehicle_warning():
    result = client().estimate(description="Car brake pads", goods_value=90)
    assert any("Vehicle" in w for w in result.warnings)


def test_origin_warning():
    result = client().estimate(description="Cotton shirts", goods_value=90, origin_country="TR")
    assert any("Origin supplied" in w for w in result.warnings)


def test_purchase_tax_warning():
    result = client().estimate(description="Wine", goods_value=90, purchase_tax_rate=0.2)
    assert any("Purchase tax applied" in w for w in result.warnings)


def test_missing_tariff_warning():
    result = client().estimate(description="Laptop", goods_value=90)
    assert any("No Israeli tariff code" in w for w in result.warnings)


def test_shipping_zero_warning():
    result = client().estimate(description="Laptop", goods_value=90)
    assert any("Shipping is zero" in w for w in result.warnings)


def test_estimate_lines_mixed():
    items = [
        LineItem.create(description="Cotton T-shirts", goods_value=500, shipping=40, exchange_rate_to_ils=3.7, duty_rate=0.06, quantity=50),
        LineItem.create(description="Bluetooth power banks", goods_value=800, shipping=60, exchange_rate_to_ils=3.7, duty_rate=0, quantity=20),
    ]
    result = client().estimate_lines(items)
    assert result.line_count == 2
    assert any("Mixed shipment" in w for w in result.warnings)


def test_empty_lines_rejected():
    with pytest.raises(TariffAdvisorError):
        client().estimate_lines([])


def test_to_dict_numeric_float():
    result = client().estimate(description="Laptop", goods_value=100)
    data = result.to_dict()
    assert isinstance(data["customs_value"], float)


def test_to_json_parseable():
    result = client().estimate(description="Laptop", goods_value=100)
    assert json.loads(result.to_json())["currency"] == "ILS"


@pytest.mark.asyncio
async def test_async_estimate_pytest_asyncio():
    result = await client().estimate_async(description="Laptop", goods_value=100)
    assert result.currency == "ILS"


def test_async_estimate_with_asyncio_run():
    result = asyncio.run(client().estimate_async(description="Laptop", goods_value=100))
    assert result.currency == "ILS"


def test_estimate_from_mapping():
    result = client().estimate_from_mapping({"description": "Laptop", "goods_value": 100})
    assert result.customs_value == Decimal("100.00")


def test_estimate_from_json_file(tmp_path):
    p = tmp_path / "input.json"
    p.write_text(json.dumps({"description": "Laptop", "goods_value": 100}), encoding="utf-8")
    result = client().estimate_from_json_file(p)
    assert result.customs_value == Decimal("100.00")


def test_estimate_from_json_line_items(tmp_path):
    p = tmp_path / "input.json"
    p.write_text(json.dumps({"line_items": [{"description": "Laptop", "goods_value": 100}, {"description": "Mouse", "goods_value": 50}]}), encoding="utf-8")
    result = client().estimate_from_json_file(p)
    assert result.line_count == 2
    assert result.customs_value == Decimal("150.00")


def test_create_and_get_estimate(tmp_path):
    store = tmp_path / "store.json"
    c = client(store_path=store)
    created = c.create_estimate(description="Laptop", goods_value=100)
    assert created.estimate_id
    loaded = c.get_estimate(created.estimate_id)
    assert loaded.estimate_id == created.estimate_id


@pytest.mark.asyncio
async def test_create_and_get_async(tmp_path):
    store = tmp_path / "store.json"
    c = client(store_path=store)
    created = await c.create_estimate_async(description="Laptop", goods_value=100)
    loaded = await c.get_estimate_async(created.estimate_id)
    assert loaded.landed_cost == created.landed_cost


def test_cli_json_output():
    completed = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "estimate",
            "--description",
            "Bluetooth headphones",
            "--goods-value",
            "120",
            "--shipping",
            "20",
            "--exchange-rate-to-ils",
            "3.70",
            "--env",
            "sandbox",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(completed.stdout)
    assert data["customs_value"] == 518.0


def test_cli_create_show_chain(tmp_path):
    store = tmp_path / "store.json"
    created = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "create",
            "--description",
            "Laptop",
            "--goods-value",
            "100",
            "--store",
            str(store),
            "--env",
            "sandbox",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    estimate_id = json.loads(created.stdout)["estimate_id"]
    shown = subprocess.run(
        [sys.executable, str(CLI), "show", estimate_id, "--store", str(store), "--json"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert json.loads(shown.stdout)["estimate_id"] == estimate_id


def test_cli_template():
    completed = subprocess.run([sys.executable, str(CLI), "template", "consumer"], cwd=ROOT, check=True, text=True, capture_output=True)
    data = json.loads(completed.stdout)
    assert data["description"] == "Bluetooth headphones"


def test_underscored_script_importable():
    completed = subprocess.run(
        [sys.executable, "-c", "from scripts.import_export_tariff_advisor_client import TariffAdvisorClient; print(TariffAdvisorClient.__name__)"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "TariffAdvisorClient" in completed.stdout


def test_personal_threshold_warning():
    result = client().estimate(description="Bluetooth headphones", goods_value=100, use_type="personal")
    assert any("Personal-import relief thresholds" in w for w in result.warnings)
