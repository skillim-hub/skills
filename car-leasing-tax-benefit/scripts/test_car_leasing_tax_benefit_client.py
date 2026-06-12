from __future__ import annotations

import asyncio
import csv
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from car_leasing_tax_benefit import (
    CarLeasingTaxBenefitClient,
    InputValidationError,
    RequestStore,
    RuleTableError,
    UnsupportedCategoryError,
)

ROOT = Path(__file__).resolve().parents[1]
CLIENT_SCRIPT = ROOT / "scripts" / "car_leasing_tax_benefit_client.py"


def test_available_years_include_2026():
    assert 2026 in CarLeasingTaxBenefitClient().available_years()


def test_categories_include_electric():
    assert "electric" in CarLeasingTaxBenefitClient().categories(2026)


def test_combustion_monthly_value():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "category": "private_combustion"})
    assert result.monthly_imputed_value_ils == Decimal("2480.00")


def test_combustion_annual_value():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "category": "private_combustion"})
    assert result.annual_imputed_value_ils == Decimal("29760.00")


def test_estimated_tax_cost():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "employee_marginal_tax_rate": "0.35"})
    assert result.estimated_monthly_tax_cost_ils == Decimal("868.00")


def test_electric_reduction_applied():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "200000", "category": "electric"})
    assert result.monthly_imputed_value_ils == Decimal("3580.00")


def test_plugin_hybrid_reduction_applied():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "200000", "category": "plugin_hybrid"})
    assert result.monthly_imputed_value_ils == Decimal("3810.00")


def test_hybrid_reduction_applied():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "200000", "category": "hybrid"})
    assert result.monthly_imputed_value_ils == Decimal("4380.00")


def test_monthly_never_negative():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "1000", "category": "electric"})
    assert result.monthly_imputed_value_ils == Decimal("0.00")


def test_partial_year():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "months_available": 3})
    assert result.annual_imputed_value_ils == Decimal("7440.00")


def test_private_use_ratio_planning_adjustment():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "private_use_ratio": "0.5"})
    assert result.monthly_imputed_value_ils == Decimal("1240.00")
    assert result.trace.warnings


def test_invalid_negative_price():
    with pytest.raises(InputValidationError):
        CarLeasingTaxBenefitClient().calculate({"original_price_ils": "-1"})


def test_invalid_tax_rate_too_high():
    with pytest.raises(InputValidationError):
        CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "employee_marginal_tax_rate": "1.2"})


def test_invalid_tax_rate_negative():
    with pytest.raises(InputValidationError):
        CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "employee_marginal_tax_rate": "-0.1"})


def test_invalid_private_use_ratio_high():
    with pytest.raises(InputValidationError):
        CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "private_use_ratio": "1.1"})


def test_invalid_months_zero():
    with pytest.raises(InputValidationError):
        CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "months_available": 0})


def test_invalid_months_over_12():
    with pytest.raises(InputValidationError):
        CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "months_available": 13})


def test_unknown_year():
    with pytest.raises(RuleTableError):
        CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "tax_year": 2035})


def test_unknown_category():
    with pytest.raises(UnsupportedCategoryError):
        CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "category": "spaceship"})


def test_motorcycle_category_rejected_for_linear_formula():
    with pytest.raises(UnsupportedCategoryError):
        CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "category": "motorcycle_l3"})


def test_to_dict_decimal_strings():
    payload = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000"}).to_dict()
    assert payload["monthly_imputed_value_ils"] == "2480.00"


def test_calculate_many_two_results():
    results = CarLeasingTaxBenefitClient().calculate_many([
        {"original_price_ils": "100000"},
        {"original_price_ils": "200000", "category": "electric"},
    ])
    assert len(results) == 2


@pytest.mark.asyncio
async def test_async_calculate_pytest_asyncio():
    result = await CarLeasingTaxBenefitClient().calculate_async({"original_price_ils": "100000"})
    assert result.monthly_imputed_value_ils == Decimal("2480.00")


def test_async_many():
    results = asyncio.run(CarLeasingTaxBenefitClient().calculate_many_async([
        {"original_price_ils": "100000"},
        {"original_price_ils": "100000", "category": "hybrid"},
    ]))
    assert len(results) == 2


def test_export_csv(tmp_path):
    client = CarLeasingTaxBenefitClient()
    path = tmp_path / "out.csv"
    client.export_csv([client.calculate({"original_price_ils": "100000"})], path)
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    assert rows[0]["monthly_imputed_value_ils"] == "2480.00"


def test_cli_json():
    proc = subprocess.run(
        [sys.executable, str(CLIENT_SCRIPT), "calculate", "--price", "100000", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["monthly_imputed_value_ils"] == "2480.00"


def test_categories_cli():
    proc = subprocess.run(
        [sys.executable, str(CLIENT_SCRIPT), "categories"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "electric" in proc.stdout


def test_create_then_calculate_request_id(tmp_path):
    store = tmp_path / "requests.json"
    create_proc = subprocess.run(
        [sys.executable, str(CLIENT_SCRIPT), "--store", str(store), "create", "--price", "100000"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    request_id = json.loads(create_proc.stdout)["id"]
    calc_proc = subprocess.run(
        [sys.executable, str(CLIENT_SCRIPT), "--store", str(store), "calculate", "--request-id", request_id, "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(calc_proc.stdout)
    assert payload["monthly_imputed_value_ils"] == "2480.00"


def test_request_store_round_trip(tmp_path):
    store = RequestStore(tmp_path / "requests.json")
    record = store.create({"original_price_ils": "100000"}, environment="sandbox")
    assert store.get(record["id"])["vehicle"]["original_price_ils"] == "100000"


def test_rule_table_has_source_note():
    assert "source_note" in CarLeasingTaxBenefitClient().tables


def test_high_price_warning():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "2500000"})
    assert result.trace.warnings


def test_employee_and_plate_preserved():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "100000", "employee_name": "Dana", "license_plate": "123"})
    assert result.employee_name == "Dana"
    assert result.license_plate == "123"


def test_importable_package_public_class():
    assert CarLeasingTaxBenefitClient.__name__ == "CarLeasingTaxBenefitClient"


def test_2026_price_ceiling_applied():
    result = CarLeasingTaxBenefitClient().calculate({"original_price_ils": "1000000", "category": "private_combustion", "tax_year": 2026})
    assert result.trace.capped_price_ils == Decimal("596860")
    assert result.monthly_imputed_value_ils == Decimal("14802.13")


def test_2026_reductions_are_web_validated():
    client = CarLeasingTaxBenefitClient()
    categories = client.categories(2026)
    assert categories["hybrid"]["monthly_reduction_ils"] == 580
    assert categories["plugin_hybrid"]["monthly_reduction_ils"] == 1150
    assert categories["electric"]["monthly_reduction_ils"] == 1380


def test_2025_reductions_are_web_validated():
    categories = CarLeasingTaxBenefitClient().categories(2025)
    assert categories["hybrid"]["monthly_reduction_ils"] == 560
    assert categories["plugin_hybrid"]["monthly_reduction_ils"] == 1130
    assert categories["electric"]["monthly_reduction_ils"] == 1350


def test_2024_reductions_are_web_validated():
    categories = CarLeasingTaxBenefitClient().categories(2024)
    assert categories["hybrid"]["monthly_reduction_ils"] == 540
    assert categories["plugin_hybrid"]["monthly_reduction_ils"] == 1090
    assert categories["electric"]["monthly_reduction_ils"] == 1310
