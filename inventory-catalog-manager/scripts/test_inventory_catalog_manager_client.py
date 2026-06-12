from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

import inventory_catalog_manager_client as client

CLI_PATH = Path(__file__).with_name("inventory-catalog-manager-cli.py")


def sample_item(**overrides):
    data = {
        "sku": "COF-BNS-001",
        "name": "פולי קפה 1 ק״ג",
        "unit": "kg",
        "price_before_vat": "42.37",
        "vat_rate": "0.18",
        "stock_quantity": "18",
        "reorder_point": "5",
        "category": "coffee",
    }
    data.update(overrides)
    return client.CatalogItem(**data)


def test_price_with_vat_rounds_to_50():
    item = sample_item()
    assert item.price_with_vat == "50.00"


def test_calculate_price_before_vat_from_final_price():
    assert str(client.calculate_price_before_vat("100", "0.18")) == "84.75"


def test_sku_is_normalized():
    item = sample_item(sku="cof-bns-001")
    assert item.sku == "COF-BNS-001"


def test_invalid_sku_rejected():
    with pytest.raises(client.CatalogError):
        sample_item(sku="ספל/XL")


def test_invalid_barcode_rejected():
    with pytest.raises(client.CatalogError):
        sample_item(barcode="729-abc")


def test_vat_percent_string_is_parsed():
    assert client.validate_vat_rate("18%") == Decimal("0.1800")


def test_vat_out_of_range_rejected():
    with pytest.raises(client.CatalogError):
        sample_item(vat_rate="1.5")


def test_negative_price_rejected():
    with pytest.raises(client.CatalogError):
        sample_item(price_before_vat="-1")


def test_duplicate_sku_rejected():
    catalog = client.InventoryCatalog()
    catalog.add_item(sample_item())
    with pytest.raises(client.DuplicateSKUError):
        catalog.add_item(sample_item())


def test_replace_existing_item():
    catalog = client.InventoryCatalog()
    catalog.add_item(sample_item())
    catalog.add_item(sample_item(name="קפה חדש"), replace=True)
    assert catalog.get_item("COF-BNS-001").name == "קפה חדש"


def test_get_missing_item_raises():
    catalog = client.InventoryCatalog()
    with pytest.raises(client.ItemNotFoundError):
        catalog.get_item("NO-SUCH-001")


def test_adjust_stock_sale():
    catalog = client.InventoryCatalog(items=[sample_item()])
    movement = catalog.adjust_stock("COF-BNS-001", "-3", reason="sale", reference="INV-1")
    assert movement.reason == "sale"
    assert catalog.get_item("COF-BNS-001").stock_quantity == "15"


def test_adjust_stock_purchase():
    catalog = client.InventoryCatalog(items=[sample_item(stock_quantity="5")])
    catalog.adjust_stock("COF-BNS-001", "10", reason="purchase", reference="PO-1")
    assert catalog.get_item("COF-BNS-001").stock_quantity == "15"


def test_set_stock_from_count_no_change_returns_none():
    catalog = client.InventoryCatalog(items=[sample_item(stock_quantity="18")])
    assert catalog.set_stock_from_count("COF-BNS-001", "18", reference="COUNT-1") is None


def test_set_stock_from_count_creates_adjustment():
    catalog = client.InventoryCatalog(items=[sample_item(stock_quantity="18")])
    movement = catalog.set_stock_from_count("COF-BNS-001", "16", reference="COUNT-1")
    assert movement is not None
    assert movement.reason == "count_adjustment"
    assert catalog.get_item("COF-BNS-001").stock_quantity == "16"


def test_low_stock_includes_below_reorder():
    catalog = client.InventoryCatalog(items=[sample_item(stock_quantity="4", reorder_point="5")])
    assert [item.sku for item in catalog.low_stock()] == ["COF-BNS-001"]


def test_low_stock_excludes_inactive_by_default():
    catalog = client.InventoryCatalog(items=[sample_item(stock_quantity="4", reorder_point="5", active=False)])
    assert catalog.low_stock() == []


def test_retire_item_sets_inactive():
    catalog = client.InventoryCatalog(items=[sample_item()])
    retired = catalog.retire_item("COF-BNS-001", note="discontinued")
    assert retired.active is False
    assert "discontinued" in retired.notes


def test_barcode_conflict_rejected_for_active_items():
    catalog = client.InventoryCatalog()
    catalog.add_item(sample_item(barcode="7290000000000"))
    with pytest.raises(client.CatalogError):
        catalog.add_item(sample_item(sku="MUG-WHT-001", name="ספל", unit="unit", barcode="7290000000000"))


def test_json_save_and_load(tmp_path):
    path = tmp_path / "catalog.json"
    catalog = client.InventoryCatalog(items=[sample_item()])
    catalog.save_json(path)
    loaded = client.InventoryCatalog.load_json(path)
    assert loaded.get_item("COF-BNS-001").name == "פולי קפה 1 ק״ג"


def test_to_dict_has_price_with_vat():
    item = sample_item()
    assert item.to_dict()["price_with_vat"] == "50.00"


def test_csv_export_and_import_roundtrip(tmp_path):
    csv_path = tmp_path / "catalog.csv"
    catalog = client.InventoryCatalog(items=[sample_item()])
    catalog.export_csv(csv_path)
    imported = client.InventoryCatalog.import_csv(csv_path)
    assert imported.get_item("COF-BNS-001").price_with_vat == "50.00"


def test_csv_utf8_bom_export(tmp_path):
    csv_path = tmp_path / "catalog_bom.csv"
    catalog = client.InventoryCatalog(items=[sample_item()])
    catalog.export_csv(csv_path, utf8_bom=True)
    assert csv_path.read_bytes().startswith(b"\xef\xbb\xbf")


def test_import_csv_missing_header_rejected(tmp_path):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")
    with pytest.raises(client.CatalogError):
        client.InventoryCatalog.import_csv(csv_path)


def test_import_csv_row_error_includes_row_number(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("sku,name,unit,price_before_vat,vat_rate\nBAD SKU,Name,unit,1,0.18\n", encoding="utf-8")
    with pytest.raises(client.CatalogError) as excinfo:
        client.InventoryCatalog.import_csv(csv_path)
    assert "CSV row 2" in str(excinfo.value)


def test_consumer_export_sanitizes_columns():
    catalog = client.InventoryCatalog(items=[sample_item(supplier_name="Secret Supplier", supplier_sku="SUP-1")])
    row = client.consumer_export_rows(catalog)[0]
    assert "supplier_name" not in row
    assert row["price_with_vat"] == "50.00"


def test_b2b_export_contains_vat_details():
    catalog = client.InventoryCatalog(items=[sample_item()])
    row = client.b2b_export_rows(catalog)[0]
    assert row["price_before_vat"] == "42.37"
    assert row["vat_rate"] == "0.18"


def test_async_save_and_load(tmp_path):
    async def run():
        path = tmp_path / "async.json"
        async_catalog = client.AsyncInventoryCatalog(client.InventoryCatalog(items=[sample_item()]))
        await async_catalog.save_json(path)
        loaded = await client.AsyncInventoryCatalog.load_json(path)
        return loaded.catalog.get_item("COF-BNS-001").name
    assert asyncio.run(run()) == "פולי קפה 1 ק״ג"


@pytest.mark.asyncio
async def test_async_add_and_adjust_stock():
    async_catalog = client.AsyncInventoryCatalog()
    await async_catalog.add_item(sample_item(stock_quantity="1"))
    movement = await async_catalog.adjust_stock("COF-BNS-001", "2", reason="purchase", reference="PO-2")
    assert movement.quantity_delta == "2"
    assert async_catalog.catalog.get_item("COF-BNS-001").stock_quantity == "3"


def test_validate_duplicate_active_barcode_detects_manual_data():
    catalog = client.InventoryCatalog()
    item_a = sample_item(sku="AAA-001", barcode="7290000000000")
    item_b = sample_item(sku="BBB-001", barcode="7290000000000", name="ספל")
    catalog.items[item_a.sku] = item_a
    catalog.items[item_b.sku] = item_b
    errors = catalog.validate()
    assert any("barcode also used" in error for error in errors)


def test_merge_replace_updates_existing():
    first = client.InventoryCatalog(items=[sample_item(name="ישן")])
    second = client.InventoryCatalog(items=[sample_item(name="חדש")])
    first.merge(second, replace=True)
    assert first.get_item("COF-BNS-001").name == "חדש"


def test_decimal_from_shekel_and_comma_string():
    assert client.decimal_from("₪1,234.50") == Decimal("1234.50")


def test_cli_init_create_price_chain(tmp_path):
    path = tmp_path / "catalog.json"
    subprocess.run([sys.executable, str(CLI_PATH), "init", str(path)], check=True, text=True, capture_output=True)
    create = subprocess.run([
        sys.executable, str(CLI_PATH), "create-item", str(path),
        "--sku", "MUG-WHT-001",
        "--name", "ספל לבן",
        "--price-before-vat", "21.19",
        "--vat-rate", "0.18",
        "--stock", "34",
        "--reorder-point", "8",
    ], check=True, text=True, capture_output=True)
    item_id = json.loads(create.stdout)["id"]
    result = subprocess.run([sys.executable, str(CLI_PATH), "price", str(path), item_id], check=True, text=True, capture_output=True)
    payload = json.loads(result.stdout)
    assert payload["price_with_vat"] == "25.00"


def test_cli_low_stock(tmp_path):
    path = tmp_path / "catalog.json"
    subprocess.run([sys.executable, str(CLI_PATH), "init", str(path)], check=True, text=True, capture_output=True)
    subprocess.run([
        sys.executable, str(CLI_PATH), "add", str(path), "MUG-WHT-001", "ספל לבן",
        "--price-before-vat", "21.19", "--stock", "2", "--reorder-point", "8"
    ], check=True, text=True, capture_output=True)
    result = subprocess.run([sys.executable, str(CLI_PATH), "low-stock", str(path)], check=True, text=True, capture_output=True)
    rows = json.loads(result.stdout)
    assert rows[0]["sku"] == "MUG-WHT-001"
