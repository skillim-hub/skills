from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from benefit_perk_planner_client import (
    AsyncBenefitPlannerClient,
    BenefitPlannerClient,
    BenefitRequest,
    PlannerError,
    Severity,
    load_request,
    plan_from_dict,
    request_from_env,
    save_plan,
    VERIFIED_2026_CHECKPOINTS,
)
from benefit_perk_planner_cli import app


runner = CliRunner()


def test_employer_plan_contains_meal_benefit() -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="employer", monthly_budget_ils=15000, employee_count=12))
    assert any(item.name == "Meal benefit" for item in plan.recommended_package)


def test_plan_has_plan_id() -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="consumer", monthly_budget_ils=600))
    assert plan.plan_id.startswith("plan_")


def test_employer_plan_keeps_within_budget_after_scaling() -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="employer", monthly_budget_ils=1200, employee_count=8))
    assert plan.estimated_monthly_cost_ils <= 1200


def test_missing_pension_creates_compliance_issue() -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="employer", monthly_budget_ils=5000, employee_count=5))
    assert any(issue.code == "COMPLIANCE_FIRST" for issue in plan.issues)


def test_existing_pension_avoids_compliance_issue() -> None:
    plan = BenefitPlannerClient().plan(
        BenefitRequest(entity_type="employer", monthly_budget_ils=5000, employee_count=5, existing_benefits=["mandatory pension"])
    )
    assert not any(issue.code == "COMPLIANCE_FIRST" for issue in plan.issues)


def test_contractors_create_high_risk_issue() -> None:
    plan = BenefitPlannerClient().plan(
        BenefitRequest(entity_type="employer", monthly_budget_ils=5000, employee_count=5, includes_contractors=True)
    )
    issue = next(issue for issue in plan.issues if issue.code == "CONTRACTOR_RISK")
    assert issue.severity is Severity.HIGH


def test_keren_hishtalmut_added_for_retention_goal() -> None:
    plan = BenefitPlannerClient().plan(
        BenefitRequest(entity_type="employer", monthly_budget_ils=10000, employee_count=10, goals=["retention"])
    )
    assert any("Keren Hishtalmut" in item.name for item in plan.recommended_package)


def test_no_meals_option_excludes_meal_benefit() -> None:
    plan = BenefitPlannerClient().plan(
        BenefitRequest(entity_type="employer", monthly_budget_ils=5000, employee_count=5, wants_meal_benefit=False)
    )
    assert not any(item.name == "Meal benefit" for item in plan.recommended_package)


def test_no_wellness_option_excludes_wellness() -> None:
    plan = BenefitPlannerClient().plan(
        BenefitRequest(entity_type="employer", monthly_budget_ils=5000, employee_count=5, wants_wellness=False)
    )
    assert not any("wellness" in item.name.lower() for item in plan.recommended_package)


def test_freelancer_low_cash_buffer_issue() -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="freelancer", monthly_budget_ils=1500, cash_buffer_months=1))
    assert any(issue.code == "LOW_CASH_BUFFER" for issue in plan.issues)


def test_freelancer_without_budget_uses_income_percentage() -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="freelancer", monthly_income_ils=30000, cash_buffer_months=6))
    assert plan.estimated_monthly_cost_ils == pytest.approx(2400)


def test_consumer_plan_contains_usable_value() -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="consumer", monthly_budget_ils=600))
    assert any("Usable-value" in item.name for item in plan.recommended_package)


def test_employee_plan_compare_options() -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="employee", monthly_budget_ils=600))
    assert any(alt["option"] == "Take salary" for alt in plan.alternatives)


def test_negative_budget_invalid() -> None:
    with pytest.raises(PlannerError):
        BenefitPlannerClient().plan(BenefitRequest(entity_type="employer", monthly_budget_ils=-1))


def test_invalid_entity_type_invalid() -> None:
    with pytest.raises(PlannerError):
        BenefitPlannerClient().plan(BenefitRequest(entity_type="bad"))  # type: ignore[arg-type]


def test_invalid_environment_invalid() -> None:
    with pytest.raises(PlannerError):
        BenefitPlannerClient(environment="bad")  # type: ignore[arg-type]


def test_markdown_contains_currency() -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="consumer", monthly_budget_ils=600))
    assert "₪" in plan.to_markdown()


def test_to_dict_round_trips_json() -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="consumer", monthly_budget_ils=600))
    encoded = json.dumps(plan.to_dict(), ensure_ascii=False)
    assert "recommended_package" in encoded


def test_save_and_load_request(tmp_path: Path) -> None:
    input_path = tmp_path / "request.json"
    input_path.write_text(json.dumps({"entity_type": "consumer", "monthly_budget_ils": 600}), encoding="utf-8")
    request = load_request(input_path)
    plan = BenefitPlannerClient().plan(request)
    output = tmp_path / "plan.json"
    save_plan(plan, output, fmt="json")
    assert json.loads(output.read_text(encoding="utf-8"))["estimated_monthly_cost_ils"] == 600


def test_save_markdown(tmp_path: Path) -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="employee", monthly_budget_ils=600))
    output = tmp_path / "plan.md"
    save_plan(plan, output, fmt="md")
    assert output.read_text(encoding="utf-8").startswith("## Benefit plan")


def test_save_unknown_format_raises(tmp_path: Path) -> None:
    plan = BenefitPlannerClient().plan(BenefitRequest(entity_type="consumer"))
    with pytest.raises(PlannerError):
        save_plan(plan, tmp_path / "x.txt", fmt="txt")  # type: ignore[arg-type]


def test_plan_from_dict() -> None:
    plan = plan_from_dict({"entity_type": "consumer", "monthly_budget_ils": 500})
    assert plan.estimated_monthly_cost_ils == 500


def test_request_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BENEFIT_PLANNER_BUDGET_ILS", "700")
    monkeypatch.setenv("BENEFIT_PLANNER_EMPLOYEE_COUNT", "3")
    request = request_from_env("employer")
    assert request.monthly_budget_ils == 700
    assert request.employee_count == 3


@pytest.mark.asyncio
async def test_async_client() -> None:
    plan = await AsyncBenefitPlannerClient().plan(BenefitRequest(entity_type="consumer", monthly_budget_ils=600))
    assert plan.estimated_monthly_cost_ils == 600


@pytest.mark.asyncio
async def test_async_create_get_plan(tmp_path: Path) -> None:
    client = AsyncBenefitPlannerClient()
    response = await client.create_plan(BenefitRequest(entity_type="consumer", monthly_budget_ils=600), store_dir=tmp_path)
    stored = await client.get_plan(response["plan_id"], store_dir=tmp_path)
    assert stored["plan_id"] == response["plan_id"]


def test_create_and_get_plan(tmp_path: Path) -> None:
    client = BenefitPlannerClient()
    response = client.create_plan(BenefitRequest(entity_type="consumer", monthly_budget_ils=600), store_dir=tmp_path)
    stored = client.get_plan(response["plan_id"], store_dir=tmp_path)
    assert stored["estimated_monthly_cost_ils"] == 600


def test_get_plan_rejects_unsafe_id(tmp_path: Path) -> None:
    with pytest.raises(PlannerError):
        BenefitPlannerClient().get_plan("../bad", store_dir=tmp_path)


def test_cli_plan_json() -> None:
    result = runner.invoke(app, ["plan", "--entity", "consumer", "--budget", "600", "--format", "json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["estimated_monthly_cost_ils"] == 600


def test_cli_plan_markdown() -> None:
    result = runner.invoke(app, ["plan", "--entity", "employer", "--budget", "5000", "--employees", "5"])
    assert result.exit_code == 0
    assert "Benefit plan" in result.stdout


def test_cli_from_file(tmp_path: Path) -> None:
    request_path = tmp_path / "request.json"
    request_path.write_text(json.dumps({"entity_type": "freelancer", "monthly_budget_ils": 1000}), encoding="utf-8")
    result = runner.invoke(app, ["from-file", str(request_path), "--format", "json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["estimated_monthly_cost_ils"] == 1000


def test_cli_compare_salary_benefit() -> None:
    result = runner.invoke(app, ["compare-salary-benefit", "--salary", "600", "--benefit", "600", "--utilization", "0.5"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["expected_usable_benefit_ils"] == 300


def test_cli_invalid_entity_exits_2() -> None:
    result = runner.invoke(app, ["plan", "--entity", "invalid"])
    assert result.exit_code == 2
    assert "unsupported entity_type" in result.output


def test_cli_create_show_chain(tmp_path: Path) -> None:
    create_result = runner.invoke(app, ["create", "--entity", "consumer", "--budget", "600", "--store-dir", str(tmp_path)])
    assert create_result.exit_code == 0
    plan_id = json.loads(create_result.stdout)["plan_id"]
    show_result = runner.invoke(app, ["show", "--plan-id", plan_id, "--store-dir", str(tmp_path)])
    assert show_result.exit_code == 0
    assert json.loads(show_result.stdout)["plan_id"] == plan_id


def test_cli_output_file(tmp_path: Path) -> None:
    out = tmp_path / "plan.md"
    result = runner.invoke(app, ["plan", "--entity", "consumer", "--budget", "600", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "Benefit plan" in out.read_text(encoding="utf-8")


def test_cli_async_plan() -> None:
    result = runner.invoke(app, ["async-plan", "--entity", "consumer", "--budget", "600"])
    assert result.exit_code == 0
    assert "Benefit plan" in result.stdout


def test_verified_2026_checkpoints_present() -> None:
    assert VERIFIED_2026_CHECKPOINTS["vat_rate"].startswith("18%")
    assert "webhooks" in VERIFIED_2026_CHECKPOINTS["api_webhooks"]
