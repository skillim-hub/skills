from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from freelancer_tax_calculator import (
    CalculatorError,
    FreelancerTaxCalculator,
    FreelancerTaxInput,
    TaxConfig,
    create_scenario,
    example_config,
    format_date_il,
    format_ils,
    gross_to_net_vat,
    load_environment_config,
    load_inputs,
    load_scenario,
    save_report,
)

CLI_PATH = ROOT / "scripts" / "freelancer-tax-calculator-cli.py"


def calc(config=None, *, environment="sandbox"):
    return FreelancerTaxCalculator(config, environment=environment)


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    merged_env["PYTHONPATH"] = str(ROOT) + os.pathsep + merged_env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, str(CLI_PATH), *args],
        cwd=ROOT,
        env=merged_env,
        check=True,
        capture_output=True,
        text=True,
    )


def test_osek_murshe_vat_without_input_vat():
    report = calc().calculate(FreelancerTaxInput("osek-murshe", "100000"))
    assert report.vat.output_vat == Decimal("18000.00")
    assert report.vat.vat_payable == Decimal("18000.00")


def test_osek_murshe_vat_with_input_vat():
    report = calc().calculate(FreelancerTaxInput("osek-murshe", "100000", input_vat_ils="3400"))
    assert report.vat.vat_payable == Decimal("14600.00")


def test_vat_refund_position():
    report = calc().calculate(FreelancerTaxInput("osek-murshe", "10000", input_vat_ils="3000"))
    assert report.vat.vat_payable == Decimal("0.00")
    assert report.vat.vat_refund_position == Decimal("1200.00")


def test_osek_patur_has_no_vat():
    report = calc().calculate(FreelancerTaxInput("osek-patur", "50000", input_vat_ils="1000"))
    assert report.vat.output_vat == Decimal("0.00")
    assert report.vat.input_vat_credit == Decimal("0.00")
    assert any("Input VAT is ignored" in warning for warning in report.warnings)


def test_osek_patur_near_threshold_warning():
    report = calc().calculate(FreelancerTaxInput("osek-patur", "111000"))
    assert any("near the configured osek patur ceiling" in warning for warning in report.warnings)


def test_osek_patur_above_threshold_warning():
    report = calc().calculate(FreelancerTaxInput("osek-patur", "130000"))
    assert any("exceeds the configured osek patur ceiling" in warning for warning in report.warnings)


def test_income_tax_advances_from_revenue_default():
    report = calc().calculate(FreelancerTaxInput("osek-murshe", "240000", "60000", income_tax_advance_rate="0.08"))
    assert report.income_tax_advances.base_method == "revenue"
    assert report.income_tax_advances.advance_base == Decimal("240000.00")
    assert report.income_tax_advances.annual_advance == Decimal("19200.00")


def test_income_tax_advances_from_profit_option():
    report = calc().calculate(FreelancerTaxInput("osek-murshe", "240000", "60000", income_tax_advance_rate="0.08", income_tax_advance_base="profit"))
    assert report.income_tax_advances.base_method == "profit"
    assert report.income_tax_advances.advance_base == Decimal("180000.00")
    assert report.income_tax_advances.annual_advance == Decimal("14400.00")


def test_zero_advance_rate_warning():
    report = calc().calculate(FreelancerTaxInput("osek-murshe", "100000"))
    assert any("advance rate is zero" in warning for warning in report.warnings)


def test_loss_sets_profit_zero():
    report = calc().calculate(FreelancerTaxInput("osek-murshe", "20000", "30000", income_tax_advance_rate="0.10", income_tax_advance_base="profit"))
    assert report.income_tax_advances.advance_base == Decimal("0.00")
    assert report.summary.estimated_profit == Decimal("0.00")


def test_national_insurance_reduced_tier_only():
    config = TaxConfig(national_insurance_reduced_threshold_annual=Decimal("100000"), national_insurance_annual_ceiling=Decimal("500000"), national_insurance_reduced_rate=Decimal("0.10"), national_insurance_regular_rate=Decimal("0.20"))
    report = calc(config).calculate(FreelancerTaxInput("osek-murshe", "50000"))
    assert report.national_insurance.annual_contribution == Decimal("5000.00")
    assert report.national_insurance.regular_tier_base == Decimal("0.00")


def test_national_insurance_regular_tier():
    config = TaxConfig(national_insurance_reduced_threshold_annual=Decimal("100000"), national_insurance_annual_ceiling=Decimal("500000"), national_insurance_reduced_rate=Decimal("0.10"), national_insurance_regular_rate=Decimal("0.20"))
    report = calc(config).calculate(FreelancerTaxInput("osek-murshe", "150000"))
    assert report.national_insurance.reduced_tier_base == Decimal("100000.00")
    assert report.national_insurance.regular_tier_base == Decimal("50000.00")
    assert report.national_insurance.annual_contribution == Decimal("20000.00")


def test_national_insurance_ceiling_caps_base():
    config = TaxConfig(national_insurance_reduced_threshold_annual=Decimal("100000"), national_insurance_annual_ceiling=Decimal("200000"), national_insurance_reduced_rate=Decimal("0.10"), national_insurance_regular_rate=Decimal("0.20"))
    report = calc(config).calculate(FreelancerTaxInput("osek-murshe", "500000"))
    assert report.national_insurance.capped_income_base == Decimal("200000.00")
    assert report.national_insurance.annual_contribution == Decimal("30000.00")


def test_micro_business_normative_expense():
    report = calc().calculate(FreelancerTaxInput("osek-patur", "100000", "12000", income_tax_advance_rate="0.06", income_tax_advance_base="profit", apply_micro_business_normative_expense=True))
    assert report.income_tax_advances.effective_expenses == Decimal("30000.00")
    assert report.income_tax_advances.expense_method == "micro_business_normative"
    assert report.income_tax_advances.annual_advance == Decimal("4200.00")


def test_micro_business_allows_low_revenue_murshe():
    report = calc().calculate(FreelancerTaxInput("osek-murshe", "100000", input_vat_ils="1000", income_tax_advance_rate="0.06", income_tax_advance_base="profit", apply_micro_business_normative_expense=True))
    assert report.income_tax_advances.effective_expenses == Decimal("30000.00")
    assert report.vat.output_vat == Decimal("18000.00")


def test_micro_business_rejects_above_ceiling():
    with pytest.raises(CalculatorError) as excinfo:
        calc().calculate(FreelancerTaxInput("osek-patur", "130000", apply_micro_business_normative_expense=True))
    assert excinfo.value.code == "micro_business_ineligible"


def test_negative_revenue_rejected():
    with pytest.raises(CalculatorError) as excinfo:
        calc().calculate(FreelancerTaxInput("osek-murshe", "-1"))
    assert excinfo.value.code == "negative_amount"


def test_invalid_decimal_rejected():
    with pytest.raises(CalculatorError) as excinfo:
        calc().calculate(FreelancerTaxInput("osek-murshe", "NaN"))
    assert excinfo.value.code == "invalid_decimal"


def test_invalid_business_type_rejected():
    with pytest.raises(CalculatorError) as excinfo:
        calc().calculate(FreelancerTaxInput("company", "100000"))
    assert excinfo.value.code == "invalid_business_type"


def test_invalid_rate_rejected():
    with pytest.raises(CalculatorError) as excinfo:
        calc().calculate(FreelancerTaxInput("osek-murshe", "100000", income_tax_advance_rate="8"))
    assert excinfo.value.code == "invalid_rate"


def test_invalid_advance_base_rejected():
    with pytest.raises(CalculatorError) as excinfo:
        calc().calculate(FreelancerTaxInput("osek-murshe", "100000", income_tax_advance_base="cash"))
    assert excinfo.value.code == "invalid_advance_base"


def test_config_override_vat_rate():
    config = TaxConfig(vat_rate=Decimal("0.17"))
    report = calc(config).calculate(FreelancerTaxInput("osek-murshe", "100000"))
    assert report.vat.output_vat == Decimal("17000.00")


def test_environment_config_override():
    config = load_environment_config("sandbox", {"FTC_VAT_RATE": "0.17", "FTC_CURRENCY": "ILS"})
    report = calc(config).calculate(FreelancerTaxInput("osek-murshe", "100000"))
    assert report.vat.output_vat == Decimal("17000.00")


def test_to_json_contains_sections():
    report = calc().calculate(FreelancerTaxInput("osek-murshe", "100000"))
    data = json.loads(report.to_json())
    assert {"vat", "income_tax_advances", "national_insurance", "summary"}.issubset(data)


def test_calculate_many_returns_reports():
    reports = calc().calculate_many([
        {"business_type": "osek-patur", "annual_revenue_ils": "50000"},
        {"business_type": "osek-murshe", "annual_revenue_ils": "100000"},
    ])
    assert len(reports) == 2
    assert reports[0].business_type.value == "osek-patur"


def test_async_calculate():
    report = asyncio.run(calc().calculate_async(FreelancerTaxInput("osek-murshe", "100000")))
    assert report.vat.output_vat == Decimal("18000.00")


def test_async_batch_calculate():
    reports = asyncio.run(calc().calculate_many_async([
        {"business_type": "osek-patur", "annual_revenue_ils": "50000"},
        {"business_type": "osek-murshe", "annual_revenue_ils": "100000"},
    ]))
    assert len(reports) == 2


def test_threshold_assessment():
    result = calc().assess_osek_patur_threshold("116000")
    assert result["status"] == "near-threshold"


def test_gross_to_net_vat_helper():
    result = gross_to_net_vat("118")
    assert result["net_revenue_ils"] == "100.00"
    assert result["vat_component_ils"] == "18.00"


def test_format_helpers():
    assert format_ils(Decimal("1234.5")) == "₪1,234.50"
    assert format_date_il("2026-06-01") == "01/06/2026"


def test_example_config_is_json_friendly():
    data = example_config()
    assert data["currency"] == "ILS"
    assert data["vat_rate"] == "0.18"
    assert data["national_insurance_regular_rate"] == "0.18"


def test_web_validated_2026_default_national_insurance_config():
    config = TaxConfig()
    assert config.national_insurance_reduced_rate == Decimal("0.077")
    assert config.national_insurance_regular_rate == Decimal("0.18")
    assert config.national_insurance_reduced_threshold_annual == Decimal("92436")
    assert config.national_insurance_annual_ceiling == Decimal("622920")


def test_load_and_save_report(tmp_path):
    input_path = tmp_path / "input.json"
    report_path = tmp_path / "report.json"
    input_path.write_text(json.dumps({"business_type": "osek-murshe", "annual_revenue_ils": "100000"}), encoding="utf-8")
    payload = load_inputs(input_path)
    report = calc().calculate(payload)
    save_report(report, report_path)
    assert json.loads(report_path.read_text(encoding="utf-8"))["vat"]["output_vat"] == "18000.00"


def test_config_from_mapping_validates_rate():
    with pytest.raises(CalculatorError):
        TaxConfig.from_mapping({"vat_rate": "18"})


def test_config_from_mapping_loads_strings():
    config = TaxConfig.from_mapping({"vat_rate": "0.17", "currency": "ILS"})
    assert config.vat_rate == Decimal("0.17")


def test_create_and_load_scenario(tmp_path):
    record = create_scenario(FreelancerTaxInput("osek-murshe", "100000"), store_dir=tmp_path, environment="sandbox")
    loaded = load_scenario(record.scenario_id, store_dir=tmp_path)
    assert loaded.business_type == "osek-murshe"
    assert loaded.annual_revenue_ils == "100000.00"


def test_load_missing_scenario(tmp_path):
    with pytest.raises(CalculatorError) as excinfo:
        load_scenario("missing123", store_dir=tmp_path)
    assert excinfo.value.code == "scenario_not_found"


def test_invalid_environment_rejected():
    with pytest.raises(CalculatorError) as excinfo:
        FreelancerTaxCalculator(environment="staging")
    assert excinfo.value.code == "invalid_environment"


def test_cli_calculate_json():
    result = run_cli("calculate", "--business-type", "osek-murshe", "--revenue", "100000", "--input-vat", "3400", "--advance-rate", "0.08", "--json")
    data = json.loads(result.stdout)
    assert data["vat"]["vat_payable"] == "14600.00"


def test_cli_vat_command():
    result = run_cli("vat", "--business-type", "osek-murshe", "--revenue", "100000", "--input-vat", "3400")
    assert "VAT payable: ₪14,600.00" in result.stdout


def test_cli_create_run_chain(tmp_path):
    create_result = run_cli("create", "--business-type", "osek-murshe", "--revenue", "100000", "--store-dir", str(tmp_path), "--json")
    create_data = json.loads(create_result.stdout)
    run_result = run_cli("run", create_data["scenario_id"], "--store-dir", str(tmp_path), "--json")
    report = json.loads(run_result.stdout)
    assert report["vat"]["output_vat"] == "18000.00"


def test_cli_env_override():
    result = run_cli("calculate", "--business-type", "osek-murshe", "--revenue", "100000", "--json", env={"FTC_VAT_RATE": "0.17"})
    assert json.loads(result.stdout)["vat"]["output_vat"] == "17000.00"


def test_example_script_reads_env_and_outputs_json():
    script = ROOT / "scripts" / "examples" / "annual_summary_json.py"
    result = subprocess.run(
        [sys.executable, str(script), "--env", "sandbox"],
        cwd=ROOT,
        env={**os.environ, "FTC_REVENUE_ILS": "100000", "PYTHONPATH": str(ROOT) + os.pathsep + os.environ.get("PYTHONPATH", "")},
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert data["vat"]["output_vat"] == "18000.00"
