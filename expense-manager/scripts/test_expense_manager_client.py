from __future__ import annotations

import asyncio
import csv
import json
import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

import expense_manager as client


def expense(vendor: str, amount: str = "117", description: str = "", **kwargs):
    return client.ExpenseInput(date=date(2026, 1, 15), vendor=vendor, amount=client.parse_decimal(amount), description=description, **kwargs)


def test_parse_decimal_currency():
    assert client.parse_decimal("₪1,234.50") == Decimal("1234.50")


def test_parse_decimal_parentheses_negative():
    assert client.parse_decimal("(99.90)") == Decimal("-99.90")


def test_parse_date_israeli_format():
    assert client.parse_date("31-12-2026") == date(2026, 12, 31)


def test_parse_date_iso_format():
    assert client.parse_date("2026-12-31") == date(2026, 12, 31)



def test_vat_rate_current_2026():
    assert client.VAT_RATE == Decimal("0.18")


def test_professional_services_full_deduction():
    r = client.classify_expense(expense("Roeh Heshbon CPA", description="accountant monthly retainer"))
    assert r.category == "professional_services"
    assert r.deductible_rate == Decimal("100.00")


def test_osek_patur_has_no_vat_reclaim():
    r = client.classify_expense(expense("Accountant", description="CPA"), client.BusinessConfig(entity_type=client.EntityType.OSEK_PATUR))
    assert r.reclaimable_vat_ils == Decimal("0.00")
    assert "Osek Patur" in r.rule_notes


def test_osek_murshe_vat_reclaim_full_for_services():
    r = client.classify_expense(expense("Accountant", description="CPA"), client.BusinessConfig(entity_type=client.EntityType.OSEK_MURSHE))
    assert r.input_vat_ils == Decimal("17.85")
    assert r.reclaimable_vat_ils == Decimal("17.85")


def test_private_consumer_zero_deduction():
    r = client.classify_expense(expense("Google Ads", description="advertising"), client.BusinessConfig(entity_type=client.EntityType.PRIVATE_CONSUMER))
    assert r.deductible_amount_ils == Decimal("0.00")
    assert r.reclaimable_vat_ils == Decimal("0.00")


def test_vehicle_uses_45_percent_income_tax_rate():
    r = client.classify_expense(expense("Paz fuel", amount="117", description="דלק לרכב"))
    assert r.category == "vehicle"
    assert r.deductible_rate == Decimal("45.00")


def test_phone_uses_80_percent_income_tax_rate():
    r = client.classify_expense(expense("Bezeq", amount="117", description="internet"))
    assert r.category == "phone_internet"
    assert r.deductible_rate == Decimal("80.00")


def test_home_office_uses_configured_percentage():
    r = client.classify_expense(expense("Home electricity", amount="117", description="home office"), client.BusinessConfig(home_office_percent=Decimal("12.5")))
    assert r.category == "home_office"
    assert r.deductible_rate == Decimal("12.50")


def test_home_office_without_percent_adds_blocker():
    r = client.classify_expense(expense("Home electricity", amount="117", description="home office"))
    assert any(f.code == "missing_home_office_percent" for f in r.review_flags)


def test_domestic_restaurant_is_zero():
    r = client.classify_expense(expense("Aroma", amount="117", description="coffee with client"))
    assert r.category == "domestic_hospitality"
    assert r.deductible_amount_ils == Decimal("0.00")


def test_foreign_guest_hospitality_requires_details():
    r = client.classify_expense(expense("Restaurant", description="foreign guest from Germany"))
    assert r.category == "foreign_guest_hospitality"
    assert any(f.code == "foreign_guest_details_required" for f in r.review_flags)


def test_capital_equipment_over_threshold_depreciates():
    r = client.classify_expense(expense("Apple", amount="5000", description="laptop computer"))
    assert r.category == "capital_equipment"
    assert r.depreciation_years == 3
    assert r.deductible_amount_ils == Decimal("0.00")


def test_capital_equipment_under_threshold_immediate():
    r = client.classify_expense(expense("KSP", amount="1000", description="monitor computer"))
    assert r.category == "capital_equipment"
    assert r.deductible_rate == Decimal("100.00")
    assert r.depreciation_years is None


def test_gift_cap_limits_deduction():
    r = client.classify_expense(expense("Gift shop", amount="480", description="client gift"))
    assert r.category == "gifts"
    assert r.deductible_amount_ils <= Decimal("240.00")


def test_uncategorized_adds_blocker():
    r = client.classify_expense(expense("Unknown Vendor", amount="100", description="mystery item"))
    assert r.category == "uncategorized_review"
    assert any(f.code == "uncategorized" for f in r.review_flags)


def test_classify_many_returns_all_rows():
    rows = [expense("Google Ads", description="advertising"), expense("Bezeq", description="internet")]
    assert len(client.classify_many(rows)) == 2


def test_async_classify_many_returns_results():
    rows = [expense("Google Ads", description="advertising"), expense("Bezeq", description="internet")]
    results = asyncio.run(client.async_classify_many(rows))
    assert [r.category for r in results] == ["marketing_advertising", "phone_internet"]


def test_read_expenses_csv_with_hebrew_headers(tmp_path):
    p = tmp_path / "input.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["תאריך", "ספק", "סכום", "תיאור"])
        writer.writeheader()
        writer.writerow({"תאריך": "15-01-2026", "ספק": "בזק", "סכום": "117", "תיאור": "אינטרנט"})
    rows = client.read_expenses_csv(p)
    assert rows[0].vendor == "בזק"


def test_write_results_csv(tmp_path):
    results = client.classify_many([expense("Google Ads", description="advertising")])
    out = client.write_results_csv(results, tmp_path / "out.csv")
    text = out.read_text(encoding="utf-8-sig")
    assert "marketing_advertising" in text


def test_summarize_results_totals():
    results = client.classify_many([expense("Accountant", amount="117", description="CPA"), expense("Aroma", amount="117", description="coffee with client")])
    summary = client.summarize_results(results)
    assert summary["total_rows"] == 2
    assert Decimal(summary["total_amount_ils"]) == Decimal("234.00")


def test_export_accountant_package_creates_zip(tmp_path):
    results = client.classify_many([expense("Google Ads", description="advertising")])
    zip_path = client.export_accountant_package(results, tmp_path, "pkg")
    assert zip_path.exists()
    assert zip_path.suffix == ".zip"


def test_classify_csv_file_roundtrip(tmp_path):
    inp = tmp_path / "in.csv"
    inp.write_text("date,vendor,amount,description\n15-01-2026,Google Ads,117,advertising\n", encoding="utf-8")
    out = tmp_path / "out.csv"
    results = client.classify_csv_file(inp, out)
    assert out.exists()
    assert results[0].category == "marketing_advertising"


def test_cli_single_outputs_json():
    cli_path = Path(__file__).with_name("expense-manager-cli.py")
    completed = subprocess.run([sys.executable, str(cli_path), "single", "--vendor", "Bezeq", "--amount", "117", "--date", "15-01-2026", "--description", "internet"], capture_output=True, text=True, check=True)
    assert "phone_internet" in completed.stdout


def test_invalid_date_raises():
    with pytest.raises(ValueError):
        client.parse_date("31/31/2026")


def test_strict_mode_adds_blocker_for_missing_receipt():
    r = client.classify_expense(expense("Google Ads", description="advertising"), client.BusinessConfig(strict=True))
    assert any(f.code == "strict_mode" for f in r.review_flags)



def test_create_expense_record_has_stable_id(tmp_path):
    e = expense("Bezeq", description="internet")
    out = tmp_path / "record.json"
    record = client.create_expense_record(e, out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert record["id"].startswith("exp_")
    assert loaded["id"] == record["id"]


def test_classify_expense_record_validates_id():
    e = expense("Bezeq", description="internet")
    record = client.expense_to_record(e)
    result = client.classify_expense_record(record, expected_id=record["id"])
    assert result.category == "phone_internet"


def test_classify_expense_record_rejects_wrong_id():
    e = expense("Bezeq", description="internet")
    record = client.expense_to_record(e)
    with pytest.raises(ValueError):
        client.classify_expense_record(record, expected_id="exp_wrong")


def test_expense_manager_client_facade_classifies():
    facade = client.ExpenseManagerClient(client.BusinessConfig(entity_type=client.EntityType.OSEK_MURSHE))
    result = facade.classify(expense("Google Ads", description="advertising"))
    assert result.category == "marketing_advertising"


def test_cli_create_then_classify_created(tmp_path):
    cli_path = Path(__file__).with_name("expense-manager-cli.py")
    record_path = tmp_path / "created.json"
    create = subprocess.run(
        [sys.executable, str(cli_path), "create", "--vendor", "Bezeq", "--amount", "117", "--date", "15/01/2026", "--description", "internet", "--output", str(record_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    expense_id = json.loads(create.stdout)["id"]
    classified = subprocess.run(
        [sys.executable, str(cli_path), "classify-created", str(record_path), "--id", expense_id],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "phone_internet" in classified.stdout
