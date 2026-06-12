from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

import household_budget_planner as hbp


def test_parse_israeli_date_ddmmyyyy():
    assert hbp.parse_israeli_date("04-06-2026") == date(2026, 6, 4)


def test_parse_israeli_date_slash():
    assert hbp.parse_israeli_date("04/06/2026") == date(2026, 6, 4)


def test_parse_israeli_date_iso():
    assert hbp.parse_israeli_date("2026-06-04") == date(2026, 6, 4)


def test_parse_israeli_date_invalid():
    with pytest.raises(hbp.BudgetValidationError):
        hbp.parse_israeli_date("2026/06/04")


def test_format_israeli_date_slash():
    assert hbp.format_israeli_date("2026-06-04", separator="/") == "04/06/2026"


def test_parse_month_dash_and_slash():
    assert hbp.parse_month("05-2026") == (5, 2026)
    assert hbp.parse_month("05/2026") == (5, 2026)


def test_format_shekel_integer():
    assert hbp.format_shekel(1234) == "₪1,234"


def test_format_shekel_decimal_and_negative():
    assert hbp.format_shekel(-1234.5) == "-₪1,234.50"


def test_extract_vat():
    result = hbp.extract_vat(1180, 0.18)
    assert result.net_before_vat == 1000
    assert result.vat_component == 180


def test_extract_vat_requires_positive_rate():
    with pytest.raises(hbp.BudgetValidationError):
        hbp.extract_vat(100, 0)


def test_category_alias_hebrew():
    assert hbp.normalize_category("ארנונה") == "arnona"


def test_add_transaction_and_summary_income_expense():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_transaction(date="01-05-2026", amount=10000, kind="income", category="salary")
    client.add_transaction(date="02-05-2026", amount=3000, kind="expense", category="housing")
    summary = client.summary(today=date(2026, 5, 1))
    assert summary.income_total == 10000
    assert summary.expense_total == 3000
    assert summary.net_cash_flow == 7000
    assert summary.budget_id.startswith("budget_")


def test_month_filtering_excludes_other_month():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_transaction(date="01-05-2026", amount=10000, kind="income", category="salary")
    client.add_transaction(date="01-06-2026", amount=999, kind="expense", category="food")
    assert client.summary(today=date(2026, 5, 1)).expense_total == 0


def test_normalize_bimonthly_arnona():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_transaction(date="05-05-2026", amount=900, kind="expense", category="arnona", normalize_months=2)
    assert client.summary(today=date(2026, 5, 1)).category_totals["arnona"] == 450


def test_category_breakdown_sorted():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_transaction(date="01-05-2026", amount=200, kind="expense", category="transport")
    client.add_transaction(date="02-05-2026", amount=100, kind="expense", category="food")
    assert list(client.category_breakdown().keys()) == ["food", "transport"]


def test_business_expense_total():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_transaction(date="01-05-2026", amount=150, kind="expense", category="business", is_business=True)
    summary = client.summary(today=date(2026, 5, 1))
    assert summary.business_expense_total == 150
    assert summary.household_expense_total == 0


def test_vat_component_total():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_transaction(date="01-05-2026", amount=1180, kind="expense", category="business", vat_included=True)
    assert client.summary(today=date(2026, 5, 1)).vat_component_total == 180


def test_savings_goal_progress():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_savings_goal(name="Emergency", target_amount=30000, current_amount=18000, due_date="31-12-2026")
    progress = client.goal_progress(today=date(2026, 5, 1))[0]
    assert progress.gap == 12000
    assert progress.months_remaining == 8
    assert progress.required_monthly_contribution == 1500


def test_savings_goal_complete():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_savings_goal(name="Done", target_amount=1000, current_amount=1200, due_date="31-12-2026")
    progress = client.goal_progress(today=date(2026, 5, 1))[0]
    assert progress.status == "complete"
    assert progress.required_monthly_contribution == 0


def test_savings_goal_past_due():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_savings_goal(name="Late", target_amount=1000, current_amount=0, due_date="01-01-2026")
    progress = client.goal_progress(today=date(2026, 5, 1))[0]
    assert progress.status == "past_due"


def test_validate_duplicate_detection():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    for _ in range(2):
        client.add_transaction(date="01-05-2026", amount=100, kind="expense", category="food", vendor="Shop", description="Milk")
    warnings = client.validate()
    assert any("DUPLICATE_TRANSACTION" in warning for warning in warnings)


def test_validate_large_cash_review():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_transaction(date="01-05-2026", amount=1500, kind="expense", category="cash", payment_method="cash")
    warnings = client.validate()
    assert any("CASH_REVIEW" in warning for warning in warnings)


def test_validate_deficit_warning():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_transaction(date="01-05-2026", amount=1000, kind="income", category="salary")
    client.add_transaction(date="02-05-2026", amount=1500, kind="expense", category="food")
    assert "DEFICIT: expenses exceed income for the month." in client.summary(today=date(2026, 5, 1)).warnings


def test_debt_risk_warning():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_transaction(date="01-05-2026", amount=10000, kind="income", category="salary")
    client.add_transaction(date="02-05-2026", amount=3000, kind="expense", category="debt")
    assert any("DEBT_RISK" in warning for warning in client.summary(today=date(2026, 5, 1)).warnings)


def test_json_roundtrip(tmp_path):
    path = tmp_path / "budget.json"
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026", budget_id="budget_test123")
    client.add_transaction(date="01-05-2026", amount=100, kind="expense", category="food")
    client.to_json(path)
    loaded = hbp.HouseholdBudgetPlannerClient.from_json(path)
    assert loaded.plan.budget_id == "budget_test123"
    assert loaded.summary(today=date(2026, 5, 1)).expense_total == 100


def test_csv_import(tmp_path):
    path = tmp_path / "tx.csv"
    path.write_text("date,amount,kind,category\n01-05-2026,100,expense,food\n", encoding="utf-8")
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    assert client.load_csv(path) == 1
    assert client.summary(today=date(2026, 5, 1)).expense_total == 100


def test_csv_export(tmp_path):
    path = tmp_path / "tx.csv"
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    client.add_transaction(date="01-05-2026", amount=100, kind="expense", category="food")
    client.export_csv(path)
    assert "food" in path.read_text(encoding="utf-8")


def test_invalid_kind():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    with pytest.raises(hbp.BudgetValidationError):
        client.add_transaction(date="01-05-2026", amount=100, kind="bad", category="food")  # type: ignore[arg-type]


def test_zero_amount_rejected():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
    with pytest.raises(hbp.BudgetValidationError):
        client.add_transaction(date="01-05-2026", amount=0, kind="expense", category="food")


def test_text_summary_contains_shekel():
    client = hbp.create_sample_plan()
    text = client.render_text_summary()
    assert "₪" in text
    assert "Budget ID" in text


def test_summary_to_dict():
    client = hbp.create_sample_plan()
    data = client.summary(today=date(2026, 5, 1)).to_dict()
    assert data["month"] == "05-2026"
    assert data["budget_id"].startswith("budget_")
    assert isinstance(data["category_totals"], dict)


def test_async_client_summary():
    async def run():
        base = hbp.HouseholdBudgetPlannerClient.for_month("05-2026")
        async_client = hbp.AsyncHouseholdBudgetPlannerClient(base)
        await async_client.add_transaction(date="01-05-2026", amount=1000, kind="income", category="salary")
        return await async_client.summary()
    summary = asyncio.run(run())
    assert summary.income_total == 1000


def test_create_budget_returns_id_and_file(tmp_path):
    output = tmp_path / "budget.json"
    response = hbp.create_budget("05-2026", output)
    assert response["budget_id"].startswith("budget_")
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["budget_id"] == response["budget_id"]


def test_ensure_budget_id_mismatch_raises():
    client = hbp.HouseholdBudgetPlannerClient.for_month("05-2026", budget_id="budget_a")
    with pytest.raises(hbp.BudgetValidationError):
        hbp.ensure_budget_id(client, "budget_b")


def test_importable_after_install_style():
    assert hasattr(hbp, "HouseholdBudgetPlannerClient")


def test_cli_create_chain(tmp_path):
    output = tmp_path / "budget.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "household_budget_planner.cli",
            "create",
            "--month",
            "05-2026",
            "--output",
            str(output),
            "--env",
            "sandbox",
            "--json",
        ],
        text=True,
        capture_output=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    assert proc.returncode == 0, proc.stderr
    response = json.loads(proc.stdout)
    assert response["budget_id"].startswith("budget_")
    proc2 = subprocess.run(
        [
            sys.executable,
            "-m",
            "household_budget_planner.cli",
            "add",
            str(output),
            "--budget-id",
            response["budget_id"],
            "--date",
            "01-05-2026",
            "--amount",
            "15000",
            "--kind",
            "income",
            "--category",
            "salary",
        ],
        text=True,
        capture_output=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    assert proc2.returncode == 0, proc2.stderr
