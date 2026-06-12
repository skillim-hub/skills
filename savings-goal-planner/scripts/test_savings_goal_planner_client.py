from __future__ import annotations

import json
import math
import runpy
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from savings_goal_planner import (
    GoalRepository,
    GoalRequest,
    RetirementRequest,
    SavingsGoalError,
    SavingsGoalPlannerClient,
    VEHICLES,
    annuity_future_value_factor,
    build_goal_plan,
    build_retirement_plan,
    effective_annual_return,
    format_ils,
    future_target_amount,
    monthly_rate_from_annual,
    project_balance,
    recommend_vehicle_candidates,
    required_monthly_savings,
)
from savings_goal_planner.cli import main


def test_future_target_amount_inflates_today_terms() -> None:
    value = future_target_amount(1000, 12, 0.05, True)
    assert value == pytest.approx(1050)


def test_future_target_amount_keeps_future_nominal() -> None:
    value = future_target_amount(1000, 12, 0.05, False)
    assert value == pytest.approx(1000)


def test_monthly_rate_from_annual() -> None:
    assert monthly_rate_from_annual(0.12) == pytest.approx((1.12 ** (1 / 12)) - 1)


def test_effective_annual_return_applies_fee_and_tax() -> None:
    assert effective_annual_return(0.06, 0.01, 0.25) == pytest.approx(0.0375)


def test_effective_annual_return_does_not_tax_losses() -> None:
    assert effective_annual_return(-0.02, 0.01, 0.25) == pytest.approx(-0.03)


def test_annuity_factor_zero_rate() -> None:
    assert annuity_future_value_factor(0.0, 24) == pytest.approx(24)


def test_beginning_annuity_exceeds_end_when_rate_positive() -> None:
    end = annuity_future_value_factor(0.01, 24, "end")
    beginning = annuity_future_value_factor(0.01, 24, "beginning")
    assert beginning > end


def test_project_balance_without_return() -> None:
    assert project_balance(1000, 100, 12, 0.0) == pytest.approx(2200)


def test_required_monthly_zero_when_current_savings_cover_target() -> None:
    assert required_monthly_savings(1000, 12, current_savings=1200) == 0


def test_build_goal_plan_basic() -> None:
    result = build_goal_plan(GoalRequest(goal_name="Test", target_amount=12000, months=12))
    assert result.monthly_required == pytest.approx(1000)
    assert result.target_future_value == pytest.approx(12000)


def test_build_goal_plan_vehicle_attached() -> None:
    result = build_goal_plan(
        GoalRequest(goal_name="Deposit", target_amount=10000, months=12, vehicle_key="bank_deposit_fixed")
    )
    assert result.vehicle is not None
    assert result.vehicle.key == "bank_deposit_fixed"


def test_build_goal_plan_warns_for_short_equity_horizon() -> None:
    result = build_goal_plan(GoalRequest(goal_name="Risk", target_amount=10000, months=24, vehicle_key="equity_index_fund"))
    assert any("horizon" in warning or "volatile" in warning for warning in result.warnings)


def test_build_goal_plan_warns_for_training_fund_rules() -> None:
    result = build_goal_plan(GoalRequest(goal_name="Fund", target_amount=10000, months=36, vehicle_key="keren_hishtalmut"))
    assert any("eligibility" in warning for warning in result.warnings)


def test_build_goal_plan_warns_for_affordability() -> None:
    result = build_goal_plan(
        GoalRequest(goal_name="High", target_amount=100000, months=10, monthly_income=10000)
    )
    assert any("30% of monthly income" in warning for warning in result.warnings)


def test_build_goal_plan_invalid_vehicle() -> None:
    with pytest.raises(SavingsGoalError):
        build_goal_plan(GoalRequest(goal_name="Bad", target_amount=1, months=1, vehicle_key="missing"))


def test_build_goal_plan_rejects_negative_target() -> None:
    with pytest.raises(SavingsGoalError):
        build_goal_plan(GoalRequest(goal_name="Bad", target_amount=-1, months=1))


def test_build_goal_plan_rejects_zero_months() -> None:
    with pytest.raises(SavingsGoalError):
        build_goal_plan(GoalRequest(goal_name="Bad", target_amount=1, months=0))


def test_retirement_gap_positive() -> None:
    result = build_retirement_plan(
        RetirementRequest(
            current_age=42,
            retirement_age=67,
            life_expectancy=95,
            desired_monthly_spending_today=14000,
            expected_monthly_pension_today=7000,
            current_retirement_savings=180000,
        )
    )
    assert result.monthly_income_gap_today == 7000
    assert result.required_nest_egg_today > 0
    assert result.monthly_required_today > 0


def test_retirement_gap_zero_when_income_covers_spending() -> None:
    result = build_retirement_plan(
        RetirementRequest(
            current_age=42,
            retirement_age=67,
            life_expectancy=95,
            desired_monthly_spending_today=7000,
            expected_monthly_pension_today=8000,
        )
    )
    assert result.monthly_income_gap_today == 0
    assert result.monthly_required_today == 0


def test_retirement_rejects_invalid_age() -> None:
    with pytest.raises(SavingsGoalError):
        build_retirement_plan(
            RetirementRequest(current_age=70, retirement_age=67, life_expectancy=95, desired_monthly_spending_today=1)
        )


def test_recommend_vehicle_candidates_orders_low_risk() -> None:
    candidates = recommend_vehicle_candidates(12, risk_tolerance="very_low", liquidity_need="same_day")
    assert candidates[0]["key"] in {"cash_bank", "bank_deposit_fixed"}


def test_recommend_vehicle_candidates_rejects_invalid_liquidity() -> None:
    with pytest.raises(SavingsGoalError):
        recommend_vehicle_candidates(12, liquidity_need="soon")  # type: ignore[arg-type]


def test_client_facade_calculates_goal() -> None:
    result = SavingsGoalPlannerClient().calculate_goal(GoalRequest(goal_name="Facade", target_amount=24000, months=24))
    assert result.monthly_required == pytest.approx(1000)


@pytest.mark.asyncio
async def test_client_async_goal() -> None:
    result = await SavingsGoalPlannerClient().calculate_goal_async(
        GoalRequest(goal_name="Async", target_amount=12000, months=12)
    )
    assert result.monthly_required == pytest.approx(1000)


@pytest.mark.asyncio
async def test_client_async_retirement() -> None:
    result = await SavingsGoalPlannerClient().calculate_retirement_async(
        RetirementRequest(current_age=42, retirement_age=67, life_expectancy=95, desired_monthly_spending_today=1000)
    )
    assert result.required_nest_egg_today > 0


def test_goal_repository_create_get_list_delete(tmp_path: Path) -> None:
    store = tmp_path / "goals.json"
    repo = GoalRepository(store, "sandbox")
    stored = repo.create_goal(GoalRequest(goal_name="Stored", target_amount=12000, months=12))
    assert stored.id
    assert repo.get_goal(stored.id).id == stored.id
    assert len(repo.list_goals()) == 1
    assert repo.delete_goal(stored.id) is True
    assert repo.list_goals() == []


def test_goal_repository_missing(tmp_path: Path) -> None:
    with pytest.raises(SavingsGoalError):
        GoalRepository(tmp_path / "goals.json", "sandbox").get_goal("missing")


def test_goal_repository_corrupt_json(tmp_path: Path) -> None:
    store = tmp_path / "bad.json"
    store.write_text("{bad", encoding="utf-8")
    with pytest.raises(SavingsGoalError):
        GoalRepository(store, "sandbox").list_goals()


@pytest.mark.asyncio
async def test_client_async_create_goal(tmp_path: Path) -> None:
    store = tmp_path / "async.json"
    stored = await SavingsGoalPlannerClient().create_goal_async(
        GoalRequest(goal_name="Async stored", target_amount=12000, months=12),
        store,
        "sandbox",
    )
    assert stored.id
    assert SavingsGoalPlannerClient().get_goal(stored.id, store, "sandbox").id == stored.id


def test_format_ils() -> None:
    assert format_ils(1234.5) == "₪1,234.50"


def test_vehicles_include_expected_keys() -> None:
    assert {"cash_bank", "bank_deposit_fixed", "money_market_fund", "pension_fund"}.issubset(VEHICLES)


def test_cli_goal_json() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["goal", "--target", "12000", "--months", "12", "--format", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["monthly_required"] == pytest.approx(1000)


def test_cli_create_show_chain(tmp_path: Path) -> None:
    runner = CliRunner()
    store = tmp_path / "goals.json"
    create = runner.invoke(
        main,
        [
            "create-goal",
            "--target",
            "12000",
            "--months",
            "12",
            "--store",
            str(store),
            "--env",
            "sandbox",
            "--format",
            "json",
        ],
    )
    assert create.exit_code == 0
    goal_id = json.loads(create.output)["id"]
    show = runner.invoke(main, ["show-goal", "--id", goal_id, "--store", str(store), "--env", "sandbox", "--format", "json"])
    assert show.exit_code == 0
    assert json.loads(show.output)["id"] == goal_id


def test_cli_recommend_json() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["recommend-vehicles", "--months", "72", "--format", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert isinstance(payload, list)
    assert payload


def test_cli_invalid_vehicle_returns_error() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["goal", "--target", "1", "--months", "1", "--vehicle", "missing"])
    assert result.exit_code != 0
    assert "unknown vehicle_key" in result.output


def test_example_script_outputs_json(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("SGP_TARGET", "13000")
    monkeypatch.setattr(sys, "argv", ["01_major_purchase_car.py", "--env", "sandbox"])
    runpy.run_path("scripts/examples/01_major_purchase_car.py", run_name="__main__")
    payload = json.loads(capsys.readouterr().out)
    assert payload["environment"] == "sandbox"
    assert payload["result"]["target_amount_input"] == 13000


def test_script_client_entry_outputs_vehicle_keys() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/savings_goal_planner_client.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert "cash_bank" in payload["vehicles"]


def test_cli_retirement_expected_pension_option() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "retirement",
            "--current-age",
            "42",
            "--retirement-age",
            "67",
            "--life-expectancy",
            "95",
            "--monthly-spending",
            "14000",
            "--expected-pension",
            "7000",
            "--current-savings",
            "180000",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["monthly_income_gap_today"] == 7000


def test_cli_retirement_state_pension_alias_still_works() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "retirement",
            "--current-age",
            "42",
            "--retirement-age",
            "67",
            "--life-expectancy",
            "95",
            "--monthly-spending",
            "14000",
            "--state-pension",
            "6500",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["monthly_income_gap_today"] == 7500
