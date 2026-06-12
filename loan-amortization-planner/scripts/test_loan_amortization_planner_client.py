from __future__ import annotations

import asyncio
import csv
import json
from decimal import Decimal
from pathlib import Path

import pytest

import loan_amortization_planner as lap
from loan_amortization_planner.client import main


def scenario(**overrides):
    data = {
        "name": "base",
        "principal": "100000",
        "term_months": 60,
        "start_date": "2026-01-15",
        "annual_interest_rate": "0.06",
        "rate_type": "fixed",
    }
    data.update(overrides)
    return lap.LoanScenario.from_mapping(data)


def test_fixed_schedule_reaches_zero_balance():
    s = lap.build_schedule(scenario())
    assert s.summary.final_balance == Decimal("0.00")
    assert len(s.rows) == 60


def test_first_due_date_adds_one_month():
    s = lap.build_schedule(scenario(start_date="2026-01-31"))
    assert str(s.rows[0].due_date) == "2026-02-28"


def test_dd_mm_yyyy_date_parses():
    s = lap.build_schedule(scenario(start_date="31-01-2026"))
    assert str(s.rows[0].due_date) == "2026-02-28"


def test_dd_mm_yyyy_slash_date_parses():
    s = lap.build_schedule(scenario(start_date="31/01/2026"))
    assert str(s.rows[0].due_date) == "2026-02-28"


def test_zero_interest_payment_equals_principal_divided_by_term():
    s = lap.build_schedule(scenario(annual_interest_rate="0"))
    assert s.rows[0].total_payment == Decimal("1666.67")


def test_prime_requires_prime_rate():
    with pytest.raises(lap.AmortizationError):
        lap.build_schedule(scenario(rate_type="prime", prime_margin="0.015"))


def test_prime_rate_combines_base_and_margin():
    s = lap.build_schedule(scenario(rate_type="prime", prime_rate="0.06", prime_margin="0.015"))
    assert s.rows[0].interest_rate_annual == Decimal("0.0750")


def test_cpi_adjustment_positive_when_cpi_positive():
    s = lap.build_schedule(scenario(rate_type="cpi", annual_cpi_rate="0.03"))
    assert s.rows[0].cpi_adjustment > 0


def test_negative_cpi_adjustment_allowed():
    s = lap.build_schedule(scenario(rate_type="cpi", annual_cpi_rate="-0.01"))
    assert s.rows[0].cpi_adjustment < 0


def test_grace_period_has_no_principal_component():
    s = lap.build_schedule(scenario(grace_months=3))
    assert s.rows[0].principal == Decimal("0.00")
    assert s.rows[2].principal == Decimal("0.00")
    assert s.rows[3].principal > 0


def test_balloon_reduces_interim_payment():
    no_balloon = lap.build_schedule(scenario())
    balloon = lap.build_schedule(scenario(balloon_percent="0.2"))
    assert balloon.rows[0].total_payment < no_balloon.rows[0].total_payment


def test_extra_payment_reduces_total_interest():
    base_case = lap.build_schedule(scenario())
    with_extra = lap.build_schedule(scenario(extra_payments={"1": "50000"}))
    assert with_extra.summary.total_interest < base_case.summary.total_interest
    assert with_extra.summary.final_balance == Decimal("0.00")


def test_rate_change_applies_to_period():
    s = lap.build_schedule(scenario(rate_changes={"2": "0.10"}))
    assert s.rows[1].interest_rate_annual == Decimal("0.1000")


def test_quarterly_schedule_has_twenty_periods_for_sixty_months():
    s = lap.build_schedule(scenario(payment_frequency="quarterly"))
    assert len(s.rows) == 20


def test_quarterly_requires_divisible_by_three():
    with pytest.raises(lap.AmortizationError):
        lap.build_schedule(scenario(term_months=10, payment_frequency="quarterly"))


def test_negative_principal_rejected():
    with pytest.raises(lap.AmortizationError):
        lap.build_schedule(scenario(principal="-1"))


def test_grace_cannot_equal_term():
    with pytest.raises(lap.AmortizationError):
        lap.build_schedule(scenario(grace_months=60))


def test_invalid_balloon_rejected():
    with pytest.raises(lap.AmortizationError):
        lap.build_schedule(scenario(balloon_percent="1"))


def test_summary_includes_fees_in_effective_cost():
    s = lap.build_schedule(scenario(origination_fee="1000", early_payment_fee="500"))
    assert s.summary.fees == Decimal("1500.00")
    assert s.summary.effective_cash_cost == s.summary.total_paid + Decimal("1500.00") - s.summary.principal


def test_to_dict_contains_rows_and_summary():
    d = lap.build_schedule(scenario()).to_dict()
    assert "rows" in d and "summary" in d
    assert d["scenario"]["rate_type"] == "fixed"


def test_json_export(tmp_path):
    out = tmp_path / "schedule.json"
    lap.build_schedule(scenario()).to_json(out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["periods"] == 60


def test_csv_export(tmp_path):
    out = tmp_path / "schedule.csv"
    lap.build_schedule(scenario()).to_csv(out)
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert len(rows) == 60
    assert "total_payment" in rows[0]


def test_compare_scenarios_sorts_by_cost():
    cheap = scenario(name="cheap", annual_interest_rate="0.03")
    expensive = scenario(name="expensive", annual_interest_rate="0.09")
    result = lap.compare_scenarios([expensive, cheap])
    assert result[0]["name"] == "cheap"


def test_async_build_schedule():
    result = asyncio.run(lap.async_build_schedule(scenario()))
    assert result.summary.periods == 60


def test_async_compare_scenarios():
    result = asyncio.run(lap.async_compare_scenarios([scenario(name="a"), scenario(name="b")]))
    assert len(result) == 2


def test_load_scenario(tmp_path):
    path = tmp_path / "scenario.json"
    path.write_text(json.dumps({"principal": "10", "term_months": 1, "start_date": "2026-01-01"}), encoding="utf-8")
    loaded = lap.load_scenario(path)
    assert loaded.principal == Decimal("10")


def test_create_and_resolve_scenario_record(tmp_path):
    registry = tmp_path / "registry.json"
    record = lap.create_scenario_record(
        {"principal": "1000", "term_months": 12, "start_date": "01/07/2026", "annual_interest_rate": "0.05"},
        registry,
    )
    resolved = lap.resolve_scenario(record["id"], registry)
    assert resolved.principal == Decimal("1000.00")


def test_resolve_scenario_from_path(tmp_path):
    path = tmp_path / "scenario.json"
    path.write_text(json.dumps({"principal": "10", "term_months": 1, "start_date": "2026-01-01"}), encoding="utf-8")
    assert lap.resolve_scenario(path).term_months == 1


def test_public_api_names_contains_build_schedule():
    assert "build_schedule" in lap.public_api_names()


def test_main_returns_error_for_missing_required_key(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{}", encoding="utf-8")
    assert main([str(path)]) == 2

def test_current_prime_example_uses_verified_base_rate():
    s = scenario(rate_type="prime", prime_rate="0.0525", prime_margin="0.012")
    schedule = lap.build_schedule(s)
    assert schedule.rows[0].interest_rate_annual == Decimal("0.0645")
