from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from stock_options_tax_advisor import (
    AsyncStockOptionsTaxAdvisorClient,
    EquityScenario,
    HoldingPeriodAnchor,
    StockOptionsTaxAdvisorClient,
    TaxConstants,
    add_months,
    format_ils,
    incremental_income_tax,
    incremental_social_security_health,
    normalize_environment,
    parse_date,
)
from stock_options_tax_advisor.cli import main as cli_main

ROOT = Path(__file__).resolve().parents[1]


def scenario(**overrides):
    data = {
        "grant_type": "options",
        "track": "102_capital",
        "quantity": 50_000,
        "exercise_price": 1,
        "sale_price": 10,
        "grant_date": "15/03/2024",
        "sale_date": "02/01/2027",
        "other_annual_income": 360_000,
        "trustee_approved": True,
        "holding_period_anchor": "grant_year_end",
    }
    data.update(overrides)
    return EquityScenario.from_dict(data)


def test_capital_track_basic_values():
    result = StockOptionsTaxAdvisorClient().calculate(scenario())
    assert result.gross_proceeds == 500_000
    assert result.cost_basis == 50_000
    assert result.capital_gain == 450_000
    assert result.capital_gains_tax == 112_500


def test_holding_period_conservative_year_end():
    assert StockOptionsTaxAdvisorClient().earliest_preferred_sale_date(scenario()).isoformat() == "2026-12-31"


def test_holding_period_grant_date_anchor():
    assert StockOptionsTaxAdvisorClient().earliest_preferred_sale_date(scenario(holding_period_anchor="grant_date")).isoformat() == "2026-03-15"


def test_holding_period_trustee_deposit_anchor():
    s = scenario(holding_period_anchor="trustee_deposit_date", trustee_deposit_date="01/05/2024")
    assert StockOptionsTaxAdvisorClient().earliest_preferred_sale_date(s).isoformat() == "2026-05-01"


def test_early_sale_reclassifies_to_income():
    result = StockOptionsTaxAdvisorClient().calculate(scenario(sale_date="01/08/2025"))
    assert result.employment_income == 450_000
    assert result.capital_gain == 0
    assert any("EARLY_SALE_RISK" in w for w in result.warnings)


def test_rsu_zero_exercise_capital():
    s = scenario(grant_type="rsu", quantity=2_000, exercise_price=0, sale_price=100, other_annual_income=300_000)
    assert StockOptionsTaxAdvisorClient().calculate(s).capital_gains_tax == 50_000


def test_public_grant_split():
    s = scenario(grant_type="rsu", quantity=1_000, exercise_price=0, sale_price=65, fmv_at_grant=40, public_at_grant=True)
    result = StockOptionsTaxAdvisorClient().calculate(s)
    assert result.employment_income == 40_000
    assert result.capital_gain == 25_000


def test_income_track_split():
    s = scenario(track="102_income", quantity=5_000, exercise_price=10, fmv_at_exercise=50, sale_price=80)
    result = StockOptionsTaxAdvisorClient().calculate(s)
    assert result.employment_income == 200_000
    assert result.capital_gain == 150_000


def test_income_track_requires_fmv():
    with pytest.raises(ValueError, match="fmv_at_exercise"):
        StockOptionsTaxAdvisorClient().calculate(scenario(track="102_income"))


def test_3i_full_income():
    result = StockOptionsTaxAdvisorClient().calculate(scenario(track="3i", quantity=5_000, exercise_price=10, sale_price=80))
    assert result.employment_income == 350_000
    assert result.capital_gain == 0


def test_espp_non_102_split():
    s = scenario(grant_type="espp", track="3i", quantity=300, exercise_price=80, fmv_at_purchase=100, sale_price=120)
    result = StockOptionsTaxAdvisorClient().calculate(s)
    assert result.employment_income == 6_000
    assert result.capital_gain == 6_000


def test_espp_non_102_requires_purchase_fmv():
    with pytest.raises(ValueError, match="fmv_at_purchase"):
        StockOptionsTaxAdvisorClient().calculate(scenario(grant_type="espp", track="3i", quantity=300, exercise_price=80, sale_price=120))


def test_controlling_shareholder_rate():
    result = StockOptionsTaxAdvisorClient().calculate(scenario(is_controlling_shareholder=True))
    assert result.capital_gains_tax == 135_000
    assert any("CONTROLLING_HOLDER" in w for w in result.warnings)


def test_underwater_options_no_taxable_gain():
    result = StockOptionsTaxAdvisorClient().calculate(scenario(quantity=10_000, exercise_price=12, sale_price=8))
    assert result.total_gain == 0
    assert result.total_tax == 0


def test_surtax_applies_when_threshold_crossed():
    assert StockOptionsTaxAdvisorClient().calculate(scenario(other_annual_income=500_000, quantity=40_000, exercise_price=0, sale_price=10)).surtax > 0


def test_no_surtax_below_threshold():
    assert StockOptionsTaxAdvisorClient().calculate(scenario(other_annual_income=100_000, quantity=10_000, exercise_price=0, sale_price=10)).surtax == 0


def test_social_security_cap_reduces_increment():
    assert incremental_social_security_health(900_000, 200_000) == 0


def test_income_tax_increment_positive():
    assert incremental_income_tax(360_000, 100_000) > 0


def test_fx_conversion():
    result = StockOptionsTaxAdvisorClient().calculate(scenario(currency="USD", fx_rate_to_ils=3.7, quantity=100, exercise_price=1, sale_price=2))
    assert result.gross_proceeds == 740
    assert result.cost_basis == 370


def test_invalid_quantity():
    with pytest.raises(ValueError, match="quantity"):
        StockOptionsTaxAdvisorClient().calculate(scenario(quantity=0))


def test_compare_tracks_returns_three_cases():
    assert set(StockOptionsTaxAdvisorClient().compare_tracks(scenario(fmv_at_exercise=5))) == {"102_capital", "102_income", "3i"}


def test_async_client_calculate():
    async def run():
        return await AsyncStockOptionsTaxAdvisorClient().calculate(scenario())
    assert asyncio.run(run()).capital_gain == 450_000


def test_async_calculate_many():
    async def run():
        return await AsyncStockOptionsTaxAdvisorClient().calculate_many([scenario(), scenario(quantity=1_000)])
    assert len(asyncio.run(run())) == 2


def test_async_export_case():
    async def run():
        return await AsyncStockOptionsTaxAdvisorClient().export_case(scenario())
    assert "result" in asyncio.run(run())


def test_to_json_contains_net():
    data = json.loads(StockOptionsTaxAdvisorClient().calculate(scenario()).to_json())
    assert "net_proceeds" in data


def test_eligibility_notes_unknown_track():
    notes = StockOptionsTaxAdvisorClient().eligibility_notes(scenario(track="unknown"))
    assert any("track" in note.lower() for note in notes)


def test_cli_calculate_json():
    runner = CliRunner()
    result = runner.invoke(cli_main, [
        "calculate", "--grant-type", "options", "--track", "102_capital",
        "--quantity", "50000", "--exercise-price", "1", "--sale-price", "10",
        "--grant-date", "15/03/2024", "--sale-date", "02/01/2027",
        "--other-income", "360000", "--trustee-approved", "--json", "--env", "sandbox",
    ])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["result"]["capital_gain"] == 450_000
    assert payload["environment"] == "sandbox"


def test_cli_eligibility_json():
    runner = CliRunner()
    result = runner.invoke(cli_main, ["eligibility", "--grant-date", "15/03/2024", "--sale-date", "02/01/2027"])
    assert result.exit_code == 0
    assert json.loads(result.output)["earliest_preferred_sale_date"] == "2026-12-31"


def test_format_ils():
    assert format_ils(1234.4) == "₪1,234"


def test_date_parse_dd_mm_yyyy_and_slashes():
    assert parse_date("15-03-2024").isoformat() == "2024-03-15"
    assert parse_date("15/03/2024").isoformat() == "2024-03-15"


def test_add_months_leap_day():
    assert add_months(parse_date("29/02/2024"), 12).isoformat() == "2025-02-28"


def test_normalize_environment():
    assert normalize_environment("production") == "production"
    with pytest.raises(ValueError):
        normalize_environment("staging")


def test_create_scenario_validates():
    assert StockOptionsTaxAdvisorClient().create_scenario(scenario().to_dict()).quantity == 50_000


def test_export_case_shape():
    exported = StockOptionsTaxAdvisorClient().export_case(scenario())
    assert set(exported) == {"scenario", "result"}


def test_custom_constants_affect_capital_rate():
    constants = TaxConstants(capital_gains_rate=0.20)
    result = StockOptionsTaxAdvisorClient(constants).calculate(scenario())
    assert result.capital_gains_tax == 90_000


def test_script_cli_runs_after_installable_imports():
    script = ROOT / "scripts" / "stock-options-tax-advisor-cli.py"
    completed = subprocess.run([sys.executable, str(script), "eligibility", "--grant-date", "15/03/2024"], cwd=ROOT, text=True, capture_output=True, check=True)
    assert "2026-12-31" in completed.stdout


def test_2026_employee_social_security_health_low_rate():
    constants = TaxConstants()
    assert constants.social_security_low_rate == 0.0427
    assert incremental_social_security_health(0, 10_000, constants) == pytest.approx(427.0)


def test_2026_employee_social_security_health_high_rate_increment():
    constants = TaxConstants()
    base = constants.social_security_low_annual
    assert incremental_social_security_health(base, 10_000, constants) == pytest.approx(1217.0)
