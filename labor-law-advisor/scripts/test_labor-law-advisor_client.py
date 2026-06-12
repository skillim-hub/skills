from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from labor_law_advisor_client import (
    DEFAULT_MINIMUM_WAGE,
    AdvisoryCase,
    LaborLawAdvisor,
    RiskLevel,
    format_ils,
)


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "labor-law-advisor-cli.py"


@pytest.fixture()
def advisor() -> LaborLawAdvisor:
    return LaborLawAdvisor()


def test_default_minimum_wage_rate_date() -> None:
    assert DEFAULT_MINIMUM_WAGE.effective_date.isoformat() == "2026-04-01"


def test_monthly_minimum_wage_shortfall(advisor: LaborLawAdvisor) -> None:
    result = advisor.minimum_wage(monthly_salary=3000, position_fraction=0.5)
    assert result.required == 3221.93
    assert result.shortfall == 221.93
    assert result.compliant is False


def test_monthly_minimum_wage_compliant(advisor: LaborLawAdvisor) -> None:
    result = advisor.minimum_wage(monthly_salary=7000)
    assert result.compliant is True
    assert result.shortfall == 0


def test_hourly_minimum_wage_shortfall(advisor: LaborLawAdvisor) -> None:
    result = advisor.minimum_wage(hourly_wage=34, regular_hours=120)
    assert result.required == 4248.0
    assert result.actual == 4080.0
    assert result.shortfall == 168.0


def test_hourly_minimum_wage_single_hour_default(advisor: LaborLawAdvisor) -> None:
    result = advisor.minimum_wage(hourly_wage=35)
    assert result.required == 35.4
    assert result.shortfall == 0.4
    assert "regular_hours omitted" in " ".join(result.notes)


def test_minimum_wage_rejects_missing_salary(advisor: LaborLawAdvisor) -> None:
    with pytest.raises(ValueError):
        advisor.minimum_wage()


def test_minimum_wage_rejects_two_salary_modes(advisor: LaborLawAdvisor) -> None:
    with pytest.raises(ValueError):
        advisor.minimum_wage(monthly_salary=1, hourly_wage=1)


def test_minimum_wage_rejects_invalid_fraction(advisor: LaborLawAdvisor) -> None:
    with pytest.raises(ValueError):
        advisor.minimum_wage(monthly_salary=1, position_fraction=1.5)


def test_overtime_daily_example(advisor: LaborLawAdvisor) -> None:
    result = advisor.overtime(hourly_rate=40, daily_hours=11, daily_threshold=8.6)
    assert result.regular_hours == 8.6
    assert result.first_overtime_hours == 2
    assert result.additional_overtime_hours == 0.4
    assert result.total_pay == 468.0


def test_overtime_no_overtime(advisor: LaborLawAdvisor) -> None:
    result = advisor.overtime(hourly_rate=50, daily_hours=8, daily_threshold=8.6)
    assert result.first_overtime_hours == 0
    assert result.total_pay == 400


def test_overtime_rejects_negative(advisor: LaborLawAdvisor) -> None:
    with pytest.raises(ValueError):
        advisor.overtime(hourly_rate=40, daily_hours=-1)


def test_weekly_overtime(advisor: LaborLawAdvisor) -> None:
    assert advisor.weekly_overtime_hours(weekly_hours=46) == 4


def test_weekly_overtime_none(advisor: LaborLawAdvisor) -> None:
    assert advisor.weekly_overtime_hours(weekly_hours=40) == 0


def test_severance_example(advisor: LaborLawAdvisor) -> None:
    result = advisor.severance(monthly_salary=12000, years=3, months=4)
    assert result.estimated_statutory == 40000
    assert result.eligible_by_tenure is True
    assert result.tenure_years == pytest.approx(3.3333, rel=0.001)


def test_severance_section14_top_up(advisor: LaborLawAdvisor) -> None:
    result = advisor.severance(monthly_salary=12000, years=3, months=4, section14_balance=35000)
    assert result.covered_by_section14_balance == 35000
    assert result.possible_top_up == 5000


def test_severance_below_year_note(advisor: LaborLawAdvisor) -> None:
    result = advisor.severance(monthly_salary=10000, months=11)
    assert result.eligible_by_tenure is False
    assert any("below one year" in note for note in result.notes)


def test_severance_rejects_months_over_12(advisor: LaborLawAdvisor) -> None:
    with pytest.raises(ValueError):
        advisor.severance(monthly_salary=10000, months=12)


def test_sick_pay_five_days(advisor: LaborLawAdvisor) -> None:
    result = advisor.sick_pay(daily_wage=500, sick_days=5)
    assert result.paid_days_value == 1500.0
    assert result.breakdown[0]["rate"] == 0


def test_sick_pay_rejects_negative_days(advisor: LaborLawAdvisor) -> None:
    with pytest.raises(ValueError):
        advisor.sick_pay(daily_wage=500, sick_days=-1)


def test_sick_pay_respects_accrual(advisor: LaborLawAdvisor) -> None:
    result = advisor.sick_pay(daily_wage=500, sick_days=5, accrued_days=2)
    assert result.sick_days == 5
    assert result.paid_days_value == 250.0
    assert any("accrued" in note for note in result.notes)


def test_vacation_year_six_five_day_week(advisor: LaborLawAdvisor) -> None:
    result = advisor.vacation(years_of_service=6, workweek_days=5)
    assert result.gross_calendar_days == 18
    assert result.net_working_days == 14


def test_vacation_six_day_week(advisor: LaborLawAdvisor) -> None:
    result = advisor.vacation(years_of_service=6, workweek_days=6)
    assert result.net_working_days == 18


def test_vacation_rejects_workweek(advisor: LaborLawAdvisor) -> None:
    with pytest.raises(ValueError):
        advisor.vacation(years_of_service=1, workweek_days=4)


def test_convalescence_days_first_year(advisor: LaborLawAdvisor) -> None:
    assert advisor.convalescence_days(years_of_service=1) == 5


def test_convalescence_caps_table(advisor: LaborLawAdvisor) -> None:
    assert advisor.convalescence_days(years_of_service=25) == 10


def test_collective_check_high_risk(advisor: LaborLawAdvisor) -> None:
    result = advisor.collective_check(sector="cleaning contractor cleaner")
    assert result.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}
    assert any("extension order" in step for step in result.next_steps)


def test_collective_check_general(advisor: LaborLawAdvisor) -> None:
    result = advisor.collective_check(sector="software startup developer")
    assert result.risk_level == RiskLevel.LOW
    assert result.recommended_sources


def test_classification_risk_high(advisor: LaborLawAdvisor) -> None:
    result = advisor.classification_risk(
        integrated_in_business=True,
        fixed_schedule=True,
        uses_company_tools=True,
        single_client=True,
        can_send_substitute=False,
        invoices_with_vat=False,
    )
    assert result.risk_level == RiskLevel.HIGH
    assert result.employee_indicators >= 3


def test_classification_risk_low(advisor: LaborLawAdvisor) -> None:
    result = advisor.classification_risk(
        integrated_in_business=False,
        fixed_schedule=False,
        uses_company_tools=False,
        single_client=False,
        can_send_substitute=True,
        invoices_with_vat=True,
    )
    assert result.risk_level == RiskLevel.LOW
    assert result.contractor_indicators == 6


def test_parental_rights_critical(advisor: LaborLawAdvisor) -> None:
    result = advisor.parental_rights_triage(pregnant=True, employer_action="dismissal", months_employed=7)
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.permit_check_required is True


def test_parental_rights_medium(advisor: LaborLawAdvisor) -> None:
    result = advisor.parental_rights_triage(fertility_treatment=True, employer_action="none", months_employed=2)
    assert result.risk_level == RiskLevel.MEDIUM
    assert "fertility_treatment" in result.protected_statuses


def test_create_case_returns_identifier(advisor: LaborLawAdvisor) -> None:
    result = advisor.create_case(category="overtime", environment="sandbox", subject="April payroll")
    assert isinstance(result, AdvisoryCase)
    assert result.case_id.startswith("ll-")
    assert result.environment == "sandbox"


def test_case_summary_uses_created_case(advisor: LaborLawAdvisor) -> None:
    created = advisor.create_case(category="minimum-wage", inputs={"month": "2026-04"})
    summary = advisor.case_summary(case_id=created.case_id)
    assert summary.case_id == created.case_id
    assert summary.operation == "case_summary"


def test_case_summary_rejects_unknown(advisor: LaborLawAdvisor) -> None:
    with pytest.raises(ValueError):
        advisor.case_summary(case_id="ll-missing")


@pytest.mark.asyncio
async def test_async_minimum_wage(advisor: LaborLawAdvisor) -> None:
    result = await advisor.aminimum_wage(monthly_salary=7000)
    assert result.compliant is True


@pytest.mark.asyncio
async def test_async_case_creation(advisor: LaborLawAdvisor) -> None:
    result = await advisor.acreate_case(category="severance", environment="production")
    assert result.environment == "production"


def test_to_dict_serializes_date_and_enum(advisor: LaborLawAdvisor) -> None:
    result = advisor.parental_rights_triage(pregnant=True, employer_action="dismissal", months_employed=7).to_dict()
    assert result["risk_level"] == "critical"


def test_format_ils() -> None:
    assert format_ils(1234.5) == "₪1,234.50"


def test_cli_min_wage_outputs_json() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "min-wage",
            "--monthly-salary",
            "3000",
            "--position-fraction",
            "0.5",
            "--env",
            "sandbox",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(completed.stdout)
    assert data["operation"] == "minimum_wage"
    assert data["environment"] == "sandbox"


def test_cli_create_case_outputs_case_id() -> None:
    completed = subprocess.run(
        [sys.executable, str(CLI), "create-case", "--category", "overtime", "--env", "sandbox"],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(completed.stdout)
    assert data["operation"] == "create_case"
    assert data["case_id"].startswith("ll-")



def test_cli_create_and_summary_chain_uses_case_store(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["LABOR_LAW_ADVISOR_CASE_STORE"] = str(tmp_path / "cases.json")
    created = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "create-case",
            "--category",
            "overtime",
            "--env",
            "sandbox",
            "--subject",
            "April payroll",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    created_data = json.loads(created.stdout)
    summary = subprocess.run(
        [sys.executable, str(CLI), "case-summary", "--case-id", created_data["case_id"], "--env", "sandbox"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    summary_data = json.loads(summary.stdout)
    assert summary_data["operation"] == "case_summary"
    assert summary_data["case_id"] == created_data["case_id"]

def test_import_module_without_dynamic_hyphen_loader() -> None:
    import labor_law_advisor_client

    assert hasattr(labor_law_advisor_client, "LaborLawAdvisor")
