from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from pathlib import Path

import pytest

import pension_contribution_calculator_client as client


def test_default_rate_table_year_and_average_wage():
    assert client.DEFAULT_RATES.tax_year == 2026
    assert client.DEFAULT_RATES.average_wage_monthly == 13769.0


def test_format_ils():
    assert client.format_ils(1234.5) == "₪1,234.50"


def test_negative_salary_rejected():
    with pytest.raises(client.ContributionInputError):
        client.employee_contributions(-1)


def test_pensionable_salary_cannot_exceed_gross():
    with pytest.raises(client.ContributionInputError):
        client.employee_contributions(10_000, pensionable_salary=10_001)


def test_invalid_product_rejected():
    with pytest.raises(client.ContributionInputError):
        client.employee_contributions(10_000, product="invalid")


def test_employee_basic_pension_split():
    result = client.employee_contributions(10_000)
    assert result.employee_pension == 600.00
    assert result.employer_pension == 650.00
    assert result.employer_severance == 600.00
    assert result.total_retirement_deposit == 1850.00


def test_employee_section14_full_severance():
    result = client.employee_contributions(10_000, section14_full=True)
    assert result.employer_severance == 833.00
    assert result.total_retirement_deposit == 2083.00


def test_employee_pensionable_salary_override():
    result = client.employee_contributions(15_000, pensionable_salary=12_000)
    assert result.employee_pension == 720.00
    assert result.pensionable_salary == 12_000.00
    assert "Pensionable salary is lower" in " ".join(result.notes)


def test_bituach_menahalim_routes_all_retirement_to_policy_bucket():
    result = client.employee_contributions(20_000, product="bituach_menahalim")
    assert result.comprehensive_pension_fund_deposit == 0.00
    assert result.supplemental_or_policy_deposit == result.total_retirement_deposit


def test_bituach_menahalim_adds_current_policy_warning():
    result = client.employee_contributions(20_000, product="bituach_menahalim")
    assert any("01/09/2023" in note for note in result.notes)


def test_pension_fund_cap_routes_excess():
    result = client.employee_contributions(40_000, product="pension_fund", section14_full=True)
    assert result.comprehensive_pension_fund_deposit == 5_645.29
    assert result.supplemental_or_policy_deposit > 0
    assert "exceeds the comprehensive" in " ".join(result.notes)


def test_hishtalmut_excluded_by_default():
    result = client.employee_contributions(10_000)
    assert result.total_hishtalmut == 0.00


def test_hishtalmut_employee_and_employer_split_under_cap():
    result = client.employee_contributions(10_000, include_hishtalmut=True)
    assert result.employee_hishtalmut == 250.00
    assert result.employer_hishtalmut == 750.00
    assert result.employer_hishtalmut_taxable == 0.00


def test_hishtalmut_taxable_employer_excess_above_cap():
    result = client.employee_contributions(20_000, include_hishtalmut=True)
    assert result.employer_hishtalmut == 1500.00
    assert result.employer_hishtalmut_tax_free == 1178.40
    assert result.employer_hishtalmut_taxable == 321.60


def test_total_employee_cash_outflow_includes_employee_training_fund():
    result = client.employee_contributions(10_000, include_hishtalmut=True)
    assert result.total_employee_cash_outflow == 850.00


def test_total_employer_cash_cost_includes_severance_and_training_fund():
    result = client.employee_contributions(10_000, include_hishtalmut=True)
    assert result.total_employer_cash_cost == 2000.00


def test_annualized_total_deposit():
    result = client.employee_contributions(10_000, include_hishtalmut=True)
    assert result.annualized_total_deposit == result.total_monthly_deposit * 12


def test_self_employed_low_income_obligation():
    result = client.self_employed_contributions(60_000, age=35, annual_hishtalmut_deposit=0)
    assert result.low_bracket_annual_income == 60_000.00
    assert result.high_bracket_annual_income == 0.00
    assert result.mandatory_pension_annual == 2670.00


def test_self_employed_average_wage_cap():
    result = client.self_employed_contributions(300_000, age=35, annual_hishtalmut_deposit=0)
    assert result.low_bracket_annual_income == 82_614.00
    assert result.high_bracket_annual_income == 82_614.00
    assert "average-wage ceiling" in " ".join(result.notes)


def test_self_employed_first_year_exemption():
    result = client.self_employed_contributions(120_000, age=35, first_year_business=True)
    assert result.mandatory_pension_annual == 0.00
    assert "First business year" in " ".join(result.notes)


def test_self_employed_age_below_threshold():
    result = client.self_employed_contributions(120_000, age=20)
    assert result.mandatory_pension_annual == 0.00
    assert "below the mandatory" in " ".join(result.notes)


def test_self_employed_retirement_age_threshold():
    result = client.self_employed_contributions(120_000, age=67)
    assert result.mandatory_pension_annual == 0.00
    assert "retirement-age" in " ".join(result.notes)


def test_self_employed_actual_pension_below_mandatory_note():
    result = client.self_employed_contributions(120_000, age=35, annual_pension_deposit=100)
    assert "lower than the calculated mandatory" in " ".join(result.notes)


def test_self_employed_hishtalmut_caps():
    result = client.self_employed_contributions(200_000, age=35, annual_hishtalmut_deposit=25_000)
    assert result.hishtalmut_deductible_amount == 9_000.00
    assert result.hishtalmut_profit_exempt_deposit == 20_566.00
    assert "profit-exempt ceiling" in " ".join(result.notes)


def test_negative_self_employed_income_rejected():
    with pytest.raises(client.ContributionInputError):
        client.self_employed_contributions(-1, age=35)


def test_unrealistic_age_rejected():
    with pytest.raises(client.ContributionInputError):
        client.self_employed_contributions(100_000, age=131)


def test_compare_products_returns_both_products():
    result = client.compare_products(20_000, include_hishtalmut=True)
    assert result.pension_fund.product == "pension_fund"
    assert result.bituach_menahalim.product == "bituach_menahalim"
    assert result.cautions


def test_client_sync_methods():
    helper = client.PensionContributionCalculatorClient()
    assert helper.calculate_employee(10_000).employee_pension == 600.00
    assert helper.calculate_self_employed(60_000, age=35).mandatory_pension_annual == 2670.00
    assert helper.compare_products(10_000).headline


def test_client_async_methods():
    async def run():
        helper = client.PensionContributionCalculatorClient()
        emp = await helper.acalculate_employee(10_000)
        solo = await helper.acalculate_self_employed(60_000, age=35)
        comp = await helper.acompare_products(10_000)
        record = await helper.acreate_record("employee", emp, environment="sandbox")
        return emp, solo, comp, record

    emp, solo, comp, record = asyncio.run(run())
    assert emp.employee_pension == 600.00
    assert solo.mandatory_pension_annual == 2670.00
    assert comp.headline
    assert record["id"].startswith("pcc-sandbox-2026-")


def test_to_plain_dict_and_json_are_utf8_safe():
    result = client.employee_contributions(10_000)
    payload = client.to_plain_dict(result)
    text = client.to_json(result)
    assert payload["employee_pension"] == 600.00
    assert "₪" not in text
    assert json.loads(text)["tax_year"] == 2026


def test_record_creation_has_stable_id():
    result = client.employee_contributions(10_000)
    record_a = client.create_calculation_record("employee", result, environment="sandbox")
    record_b = client.create_calculation_record("employee", result, environment="sandbox")
    assert record_a["id"] == record_b["id"]
    assert record_a["result"]["gross_salary"] == 10_000.00


def test_record_rejects_invalid_environment():
    with pytest.raises(client.ContributionInputError):
        client.create_calculation_record("employee", client.employee_contributions(10_000), environment="dev")


def test_record_rejects_invalid_kind():
    with pytest.raises(client.ContributionInputError):
        client.create_calculation_record("unknown", client.employee_contributions(10_000))


def test_load_rates_from_json(tmp_path: Path):
    path = tmp_path / "rates.json"
    path.write_text(json.dumps({"tax_year": 2027, "employee_pension_rate": 0.07}), encoding="utf-8")
    rates = client.load_rates_from_json(str(path))
    assert rates.tax_year == 2027
    assert rates.employee_pension_rate == 0.07
    assert rates.employer_pension_rate == client.DEFAULT_RATES.employer_pension_rate


def test_load_rates_rejects_unknown_fields(tmp_path: Path):
    path = tmp_path / "rates.json"
    path.write_text(json.dumps({"bad": 1}), encoding="utf-8")
    with pytest.raises(client.ContributionInputError):
        client.load_rates_from_json(str(path))


def test_examples_exist_and_use_env_argument():
    examples = sorted((Path(__file__).parent / "examples").glob("*.py"))
    assert len(examples) >= 5
    for path in examples:
        text = path.read_text(encoding="utf-8")
        assert "--env" in text
        assert "os.getenv" in text
        assert "ensure_ascii=False" in text
        assert "indent=2" in text
