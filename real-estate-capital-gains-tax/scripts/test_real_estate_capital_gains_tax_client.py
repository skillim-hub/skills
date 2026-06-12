from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

import real_estate_capital_gains_tax as client


def base_inputs(**overrides):
    data = dict(
        purchase_date=date(2010, 1, 1),
        sale_date=date(2025, 1, 1),
        purchase_price=1_000_000,
        sale_price=2_000_000,
        purchase_costs=0,
        sale_costs=0,
        improvements=0,
        depreciation_claimed=0,
        ownership_share=1,
        property_type=client.PropertyType.RESIDENTIAL_APARTMENT,
        is_qualifying_residential_apartment=True,
    )
    data.update(overrides)
    return client.TaxInputs(**data)


def test_basic_gain_positive():
    est = client.estimate_tax(base_inputs(is_qualifying_residential_apartment=False))
    assert est.gross_gain == 1_000_000
    assert est.estimated_tax == 250_000


def test_costs_reduce_gain():
    est = client.estimate_tax(base_inputs(purchase_costs=50_000, improvements=150_000, sale_costs=40_000, is_qualifying_residential_apartment=False))
    assert est.gross_gain == 760_000


def test_depreciation_increases_gain_by_lowering_basis():
    est = client.estimate_tax(base_inputs(depreciation_claimed=100_000, is_qualifying_residential_apartment=False))
    assert est.adjusted_basis == 900_000
    assert est.gross_gain == 1_100_000


def test_cpi_indexation_lowers_real_gain():
    est = client.estimate_tax(base_inputs(cpi_purchase=80, cpi_sale=100, is_qualifying_residential_apartment=False))
    assert est.indexed_basis == 1_250_000
    assert est.real_gain == 750_000


def test_linear_share_between_zero_and_one():
    est = client.estimate_tax(base_inputs())
    assert 0 < est.linear_taxable_share < 1
    assert est.taxable_real_gain < est.real_gain


def test_post_2014_purchase_linear_share_is_one():
    est = client.estimate_tax(base_inputs(purchase_date=date(2020, 1, 1), sale_date=date(2025, 1, 1)))
    assert est.linear_taxable_share == pytest.approx(1.0)


def test_pre_2014_sale_linear_share_zero():
    est = client.estimate_tax(base_inputs(purchase_date=date(2000, 1, 1), sale_date=date(2013, 12, 31)))
    assert est.linear_taxable_share == 0
    assert est.estimated_tax == 0


def test_non_residential_does_not_use_linear_relief():
    est = client.estimate_tax(base_inputs(property_type=client.PropertyType.LAND, is_qualifying_residential_apartment=True))
    assert est.taxable_real_gain == est.real_gain


def test_half_ownership_halves_taxable_gain():
    full = client.estimate_tax(base_inputs(is_qualifying_residential_apartment=False))
    half = client.estimate_tax(base_inputs(ownership_share=0.5, is_qualifying_residential_apartment=False))
    assert half.taxable_real_gain == full.taxable_real_gain / 2


def test_loss_has_zero_tax_and_warning():
    est = client.estimate_tax(base_inputs(purchase_price=2_000_000, sale_price=1_800_000))
    assert est.estimated_tax == 0
    assert any("loss" in w.lower() for w in est.warnings)


def test_sale_before_purchase_raises():
    with pytest.raises(ValueError, match="Sale date"):
        client.estimate_tax(base_inputs(purchase_date=date(2025, 1, 1), sale_date=date(2020, 1, 1)))


def test_same_day_raises():
    with pytest.raises(ValueError):
        client.estimate_tax(base_inputs(purchase_date=date(2025, 1, 1), sale_date=date(2025, 1, 1)))


def test_negative_amount_raises():
    with pytest.raises(ValueError, match="sale_costs"):
        client.estimate_tax(base_inputs(sale_costs=-1))


def test_invalid_share_raises():
    with pytest.raises(ValueError, match="Ownership"):
        client.estimate_tax(base_inputs(ownership_share=1.2))


def test_tax_rate_validation():
    with pytest.raises(ValueError, match="Tax rate"):
        client.estimate_tax(base_inputs(tax_rate=1.5))


def test_cpi_pair_required():
    with pytest.raises(ValueError, match="Both CPI"):
        client.estimate_tax(base_inputs(cpi_purchase=100))


def test_cpi_positive_required():
    with pytest.raises(ValueError, match="positive"):
        client.estimate_tax(base_inputs(cpi_purchase=0, cpi_sale=100))


def test_cpi_sale_lower_warning():
    est = client.estimate_tax(base_inputs(cpi_purchase=120, cpi_sale=100))
    assert any("same base" in w for w in est.warnings)


def test_foreign_resident_warning():
    est = client.estimate_tax(base_inputs(seller_residency=client.SellerResidency.FOREIGN_RESIDENT))
    assert any("Foreign-resident" in w for w in est.warnings)


def test_company_warning():
    est = client.estimate_tax(base_inputs(seller_type=client.SellerType.COMPANY))
    assert any("Non-individual" in w for w in est.warnings)


def test_commercial_warning_and_depreciation_warning():
    est = client.estimate_tax(base_inputs(property_type=client.PropertyType.COMMERCIAL, is_qualifying_residential_apartment=False))
    assert any("Business" in w for w in est.warnings)
    assert any("depreciation" in w.lower() for w in est.warnings)


def test_exemption_warning_not_auto_applied():
    est = client.estimate_tax(base_inputs(exemption_code="single_apartment", is_qualifying_residential_apartment=False))
    assert est.estimated_tax > 0
    assert any("not automatically applied" in w for w in est.warnings)


def test_unsupported_exemption_raises():
    with pytest.raises(ValueError, match="Unsupported exemption"):
        client.estimate_tax(base_inputs(exemption_code="magic"))


def test_parse_hebrew_date_format():
    parsed = client.TaxInputs.parse_date("01/06/2025")
    assert parsed == date(2025, 6, 1)


def test_from_dict_parses_enums_and_dates():
    inputs = client.TaxInputs.from_dict({
        "purchase_date": "2010-01-01",
        "sale_date": "2025-01-01",
        "purchase_price": 1,
        "sale_price": 2,
        "property_type": "land",
        "seller_residency": "unknown",
        "seller_type": "individual",
    })
    assert inputs.property_type == client.PropertyType.LAND


def test_estimate_from_dict_json_friendly():
    out = client.estimate_from_dict({
        "purchase_date": "2010-01-01",
        "sale_date": "2025-01-01",
        "purchase_price": 1_000_000,
        "sale_price": 2_000_000,
    })
    assert isinstance(out, dict)
    assert out["estimated_tax"] > 0


def test_async_estimate():
    est = asyncio.run(client.estimate_tax_async(base_inputs(is_qualifying_residential_apartment=False)))
    assert est.estimated_tax == 250_000


def test_format_nis():
    assert client.format_nis(1234.5) == "₪1,234.50"


def test_summarize_contains_estimated_tax():
    est = client.estimate_tax(base_inputs(is_qualifying_residential_apartment=False))
    assert "Estimated Mas Shevach" in client.summarize(est)



def test_default_rate_surtax_warning():
    est = client.estimate_tax(base_inputs(is_qualifying_residential_apartment=False))
    assert any("Default 25%" in warning for warning in est.warnings)


def test_notes_urban_renewal_warning():
    est = client.estimate_tax(base_inputs(property_type=client.PropertyType.OTHER, notes="Tama 38 project"))
    assert any("Urban renewal" in w for w in est.warnings)


def test_create_and_estimate_case(tmp_path):
    record = client.create_case(base_inputs(is_qualifying_residential_apartment=False), case_dir=tmp_path, environment="sandbox")
    assert record.case_id
    loaded = client.load_case(record.case_id, case_dir=tmp_path, environment="sandbox")
    assert loaded.case_id == record.case_id
    est = client.estimate_case(record.case_id, case_dir=tmp_path, environment="sandbox")
    assert est.estimated_tax == 250_000


def test_invalid_environment_raises(tmp_path):
    with pytest.raises(ValueError, match="Environment"):
        client.create_case(base_inputs(), environment="staging", case_dir=tmp_path)


def test_cli_json_runs():
    cli_path = Path(__file__).with_name("real-estate-capital-gains-tax-cli.py")
    result = subprocess.run(
        [
            sys.executable, str(cli_path), "estimate",
            "--purchase-date", "2010-01-01",
            "--sale-date", "2025-01-01",
            "--purchase-price", "1000000",
            "--sale-price", "2000000",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    payload = json.loads(result.stdout)
    assert payload["estimated_tax"] > 0


def test_cli_create_then_estimate_case(tmp_path):
    cli_path = Path(__file__).with_name("real-estate-capital-gains-tax-cli.py")
    create_result = subprocess.run(
        [
            sys.executable, str(cli_path), "create",
            "--purchase-date", "2010-01-01",
            "--sale-date", "2025-01-01",
            "--purchase-price", "1000000",
            "--sale-price", "2000000",
            "--case-dir", str(tmp_path),
            "--env", "sandbox",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    case_id = json.loads(create_result.stdout)["case_id"]
    estimate_result = subprocess.run(
        [
            sys.executable, str(cli_path), "estimate-case",
            "--case-id", case_id,
            "--case-dir", str(tmp_path),
            "--env", "sandbox",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    payload = json.loads(estimate_result.stdout)
    assert payload["estimated_tax"] > 0


def test_import_compatibility_module():
    import real_estate_capital_gains_tax_client as compat

    assert compat.estimate_tax(base_inputs(is_qualifying_residential_apartment=False)).estimated_tax == 250_000
