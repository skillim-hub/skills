from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import hr_compliance_advisor as hr


def cli_env() -> dict[str, str]:
    env = dict(os.environ)
    root = str(Path(__file__).resolve().parents[1])
    env["PYTHONPATH"] = root + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def codes(report):
    return {finding["code"] for finding in report["findings"]}


def test_hourly_minimum_wage_flag():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", hourly_rate_ils=31, weekly_hours=38))
    assert "MIN_WAGE_HOURLY" in codes(report)
    assert report["overall_risk"] == "critical"


def test_monthly_minimum_wage_flag():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=4000, part_time_ratio=1))
    assert "MIN_WAGE_MONTHLY" in codes(report)


def test_part_time_monthly_minimum_passes_when_adjusted():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=3300, part_time_ratio=0.5))
    assert "MIN_WAGE_MONTHLY" not in codes(report)



def test_2026_default_minimum_wage_values():
    config = hr.ComplianceConfig()
    assert config.minimum_monthly_wage_ils == 6443.85
    assert config.minimum_hourly_wage_ils == 35.40

def test_weekly_overtime_review():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, weekly_hours=45))
    assert "WEEKLY_OVERTIME_REVIEW" in codes(report)


def test_daily_overtime_review():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, daily_hours=9))
    assert "DAILY_OVERTIME_REVIEW" in codes(report)


def test_daily_cap_critical():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, daily_hours=13))
    assert "DAILY_HOURS_CAP" in codes(report)
    assert report["overall_risk"] == "critical"


def test_weekly_overtime_cap_critical():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, overtime_hours_weekly=20))
    assert "WEEKLY_OVERTIME_CAP" in codes(report)


def test_global_overtime_blanket_text():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9500, contract_text="Salary includes all overtime."))
    assert "GLOBAL_OVERTIME_BLANKET" in codes(report)


def test_overtime_waiver_text():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9500, contract_text="Employee is not entitled to overtime."))
    assert "OVERTIME_WAIVER" in codes(report)


def test_unpaid_training_text():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", hourly_rate_ils=40, contract_text="Mandatory unpaid training applies."))
    assert "UNPAID_TRAINING_TIME" in codes(report)


def test_unpaid_closing_text():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", hourly_rate_ils=40, contract_text="Closing time is unpaid."))
    assert "UNPAID_CLOSING_TIME" in codes(report)


def test_pension_missing_after_waiting_period():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, tenure_months=10, has_pension_arrangement=False))
    assert "PENSION_MISSING" in codes(report)


def test_pension_started_late():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, tenure_months=12, pension_start_month=8))
    assert "PENSION_STARTED_LATE" in codes(report)


def test_prior_pension_shorter_waiting_period():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, tenure_months=4, had_active_pension_before_start=True, has_pension_arrangement=False))
    assert "PENSION_MISSING" in codes(report)


def test_low_employer_pension_rate():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, employer_contribution_pension_pct=5))
    assert "PENSION_EMPLOYER_RATE_LOW" in codes(report)


def test_low_severance_deposit_rate():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, employer_contribution_severance_pct=4))
    assert "SEVERANCE_DEPOSIT_RATE_LOW" in codes(report)


def test_section_14_partial_flag():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, has_section_14=True, employer_contribution_severance_pct=6))
    assert "SECTION_14_PARTIAL" in codes(report)


def test_severance_waiver_text():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, contract_text="Employee waives severance rights."))
    assert "SEVERANCE_WAIVER" in codes(report)


def test_required_notice_monthly_after_year():
    assert hr.required_notice_days(13, monthly_employee=True) == 30


def test_notice_shortfall():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, tenure_months=30, termination_reason="termination", notice_days_given=7))
    assert "NOTICE_SHORTFALL" in codes(report)


def test_hearing_process_missing():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, tenure_months=4, termination_reason="Immediate dismissal without hearing."))
    assert "HEARING_PROCESS_MISSING" in codes(report)


def test_protected_status_adverse_action():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, is_parent_or_pregnant=True, contract_text="Reduce shifts after pregnancy disclosure."))
    assert "PROTECTED_STATUS_ADVERSE_ACTION" in codes(report)


def test_hiring_discrimination_question():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="candidate", contract_text="Interview question: are you pregnant or planning children?"))
    assert "HIRING_DISCRIMINATION_QUESTION" in codes(report)


def test_contractor_misclassification_by_score():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="contractor", contractor_controls=5, contract_text="Invoices monthly."))
    assert "CONTRACTOR_MISCLASSIFICATION" in codes(report)


def test_contractor_ambiguous_by_text():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="contractor", contract_text="Fixed hours and company email."))
    assert "CONTRACTOR_STATUS_AMBIGUOUS" in codes(report)


def test_sector_expansion_order_review():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, sector="cleaning"))
    assert "SECTOR_EXPANSION_ORDER_REVIEW" in codes(report)


def test_statutory_rights_waiver():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, contract_text="Employee waives all rights."))
    assert "STATUTORY_RIGHTS_WAIVER" in codes(report)


def test_wage_deduction_risk():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, contract_text="Employer may deduct damage and impose a fine."))
    assert "WAGE_DEDUCTION_RISK" in codes(report)


def test_vacation_forfeiture_risk():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", monthly_salary_ils=9000, contract_text="Unused vacation will forfeit at year end."))
    assert "VACATION_FORFEITURE_RISK" in codes(report)


def test_sync_client_review_dict():
    client = hr.HRComplianceClient()
    report = client.review_dict({"worker_type": "employee", "hourly_rate_ils": 31})
    assert "MIN_WAGE_HOURLY" in codes(report)


def test_async_client_review():
    async def run():
        client = hr.AsyncHRComplianceClient()
        return await client.review(hr.EmployeeFacts(worker_type="employee", hourly_rate_ils=31))
    report = asyncio.run(run())
    assert "MIN_WAGE_HOURLY" in codes(report)


def test_report_to_markdown_contains_findings():
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", hourly_rate_ils=31))
    markdown = hr.report_to_markdown(report)
    assert "Compliance snapshot" in markdown
    assert "MIN_WAGE_HOURLY" in markdown


def test_validation_rejects_negative_amount():
    with pytest.raises(hr.InputValidationError):
        hr.review_policy(hr.EmployeeFacts(worker_type="employee", hourly_rate_ils=-1))


def test_validation_rejects_bad_hours():
    with pytest.raises(hr.InputValidationError):
        hr.review_policy(hr.EmployeeFacts(worker_type="employee", weekly_hours=121))


def test_cli_validate_json(tmp_path):
    facts = tmp_path / "facts.json"
    facts.write_text(json.dumps({"worker_type": "employee", "hourly_rate_ils": 31}), encoding="utf-8")
    cli = Path(__file__).with_name("hr-compliance-advisor-cli.py")
    result = subprocess.run([sys.executable, str(cli), "validate-json", "--input", str(facts)], text=True, capture_output=True, env=cli_env())
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_cli_analyze_json(tmp_path):
    facts = tmp_path / "facts.json"
    facts.write_text(json.dumps({"worker_type": "employee", "hourly_rate_ils": 31}), encoding="utf-8")
    cli = Path(__file__).with_name("hr-compliance-advisor-cli.py")
    result = subprocess.run([sys.executable, str(cli), "analyze", "--input", str(facts), "--pretty"], text=True, capture_output=True, env=cli_env())
    assert result.returncode == 0, result.stderr
    assert "MIN_WAGE_HOURLY" in result.stdout


def test_package_import_exposes_client():
    assert hasattr(hr, "HRComplianceClient")
    assert hasattr(hr, "config_from_env")


def test_config_from_env_overrides_values():
    config = hr.config_from_env({"HR_COMPLIANCE_MIN_HOURLY_WAGE_ILS": "40"})
    report = hr.review_policy(hr.EmployeeFacts(worker_type="employee", hourly_rate_ils=39), config)
    assert "MIN_WAGE_HOURLY" in codes(report)


def test_create_and_review_case(tmp_path):
    client = hr.HRComplianceClient()
    created = client.create_case({"worker_type": "employee", "hourly_rate_ils": 31}, case_dir=tmp_path, environment="sandbox")
    assert created["case_id"]
    report = client.review_case(created["case_id"], case_dir=tmp_path)
    assert report["case_id"] == created["case_id"]
    assert "MIN_WAGE_HOURLY" in codes(report)


def test_async_create_and_review_case(tmp_path):
    async def run():
        client = hr.AsyncHRComplianceClient()
        created = await client.create_case({"worker_type": "employee", "hourly_rate_ils": 31}, case_dir=tmp_path, environment="production")
        return await client.review_case(created["case_id"], case_dir=tmp_path)
    report = asyncio.run(run())
    assert report["environment"] == "production"
    assert "MIN_WAGE_HOURLY" in codes(report)


def test_cli_create_then_review_case(tmp_path):
    facts = tmp_path / "facts.json"
    cases = tmp_path / "cases"
    facts.write_text(json.dumps({"worker_type": "employee", "hourly_rate_ils": 31}), encoding="utf-8")
    cli = Path(__file__).with_name("hr-compliance-advisor-cli.py")
    create = subprocess.run([sys.executable, str(cli), "create-case", "--input", str(facts), "--case-dir", str(cases), "--env", "sandbox"], text=True, capture_output=True, env=cli_env())
    assert create.returncode == 0, create.stderr
    case_id = json.loads(create.stdout)["case_id"]
    review = subprocess.run([sys.executable, str(cli), "review-case", case_id, "--case-dir", str(cases), "--pretty"], text=True, capture_output=True, env=cli_env())
    assert review.returncode == 0, review.stderr
    assert "MIN_WAGE_HOURLY" in review.stdout
