from __future__ import annotations

import asyncio
import csv
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from leave_sick_day_tracker import (
    EmployeeProfile,
    LeaveEvent,
    LeaveTrackerClient,
    LeaveTrackerError,
    UnknownEmployeeError,
    annual_accrual_between,
    annual_entitlement_days,
    completed_years_on,
    count_workdays,
    format_il_date,
    parse_date,
    seniority_year_index,
    sick_accrual_between,
    sick_pay_equivalent_days,
    write_template_csvs,
)
from leave_sick_day_tracker.cli import cli


def test_installable_import_exports_client():
    assert LeaveTrackerClient.__name__ == "LeaveTrackerClient"


def test_parse_iso_date():
    assert parse_date("2024-01-31").day == 31


def test_parse_il_dash_date():
    assert parse_date("31-01-2024").month == 1


def test_parse_il_slash_date():
    assert parse_date("31/01/2024").year == 2024


def test_invalid_date_raises():
    with pytest.raises(LeaveTrackerError):
        parse_date("31.01.2024")


def test_format_il_date_uses_slashes():
    assert format_il_date(parse_date("2024-12-05")) == "05/12/2024"


def test_count_workdays_five_day_israel_week():
    assert count_workdays("18/08/2024", "24/08/2024", 5) == 5.0


def test_count_workdays_six_day_israel_week():
    assert count_workdays("18/08/2024", "24/08/2024", 6) == 6.0


def test_count_workdays_rejects_invalid_week():
    with pytest.raises(LeaveTrackerError):
        count_workdays("18/08/2024", "24/08/2024", 7)


def test_completed_years_before_anniversary():
    assert completed_years_on(parse_date("2020-06-15"), parse_date("2024-06-14")) == 3


def test_completed_years_on_anniversary():
    assert completed_years_on(parse_date("2020-06-15"), parse_date("2024-06-15")) == 4


def test_seniority_year_index():
    assert seniority_year_index(parse_date("2020-06-15"), parse_date("2024-06-15")) == 5


def test_annual_entitlement_first_year_five_day():
    assert annual_entitlement_days("01/01/2024", "31/12/2024", 5) == 12.0



def test_annual_entitlement_twelve_year_six_day_corrected():
    assert annual_entitlement_days("01/01/2013", "31/12/2024", 6) == 23.0


def test_annual_entitlement_thirteen_year_six_day_cap():
    assert annual_entitlement_days("01/01/2012", "31/12/2024", 6) == 24.0


def test_annual_entitlement_fourteen_year_five_day_cap():
    assert annual_entitlement_days("01/01/2011", "31/12/2024", 5) == 20.0

def test_annual_entitlement_override():
    assert annual_entitlement_days("01/01/2024", "31/12/2024", 5, 22) == 22.0


def test_annual_accrual_half_year():
    assert annual_accrual_between("01/07/2024", "31/12/2024", 5) == 6.0


def test_sick_accrual_full_year():
    assert sick_accrual_between("01/01/2024", "31/12/2024") == 18.0


def test_sick_accrual_cap():
    assert sick_accrual_between("01/01/2010", "31/12/2024") == 90.0


def test_sick_pay_first_day_zero():
    assert sick_pay_equivalent_days(1) == 0.0


def test_sick_pay_three_days_equals_one():
    assert sick_pay_equivalent_days(3) == 1.0


def test_sick_pay_five_days_equals_three():
    assert sick_pay_equivalent_days(5) == 3.0


def test_add_employee_and_annual_event_balance():
    employee = EmployeeProfile("E1", "Dana", "01/01/2024", work_week_days=5)
    tracker = LeaveTrackerClient([employee])
    tracker.record_event(LeaveEvent("E1", "annual", "18/08/2024", "22/08/2024"))
    snapshot = tracker.balance("E1", "31/12/2024")
    assert snapshot.annual_used == 5.0
    assert snapshot.annual_balance == 7.0


def test_sick_event_deducts_sick_not_annual():
    employee = EmployeeProfile("E1", "Dana", "01/01/2024", work_week_days=5)
    tracker = LeaveTrackerClient([employee])
    tracker.record_event(LeaveEvent("E1", "sick", "01/09/2024", "03/09/2024"))
    snapshot = tracker.balance("E1", "31/12/2024")
    assert snapshot.annual_used == 0.0
    assert snapshot.sick_used == 3.0
    assert snapshot.sick_paid_equivalent_days == 1.0


def test_miluim_does_not_deduct_balances():
    employee = EmployeeProfile("E1", "Dana", "01/01/2024")
    tracker = LeaveTrackerClient([employee])
    tracker.record_event(LeaveEvent("E1", "miluim", "01/09/2024", "05/09/2024"))
    snapshot = tracker.balance("E1", "31/12/2024")
    assert snapshot.miluim_days == 5.0
    assert snapshot.annual_used == 0.0
    assert snapshot.sick_used == 0.0


def test_parental_does_not_deduct_balances():
    employee = EmployeeProfile("E1", "Dana", "01/01/2024")
    tracker = LeaveTrackerClient([employee])
    tracker.record_event(LeaveEvent("E1", "parental", "01/09/2024", "05/09/2024"))
    snapshot = tracker.balance("E1", "31/12/2024")
    assert snapshot.parental_days == 5.0
    assert snapshot.annual_used == 0.0


def test_mourning_warns_over_limit():
    employee = EmployeeProfile("E1", "Dana", "01/01/2024", mourning_paid_days_limit=7)
    tracker = LeaveTrackerClient([employee])
    tracker.record_event(LeaveEvent("E1", "mourning", "01/09/2024", "12/09/2024", days=8))
    snapshot = tracker.balance("E1", "31/12/2024")
    assert snapshot.mourning_days == 8.0
    assert snapshot.warnings


def test_unknown_employee_event_raises():
    tracker = LeaveTrackerClient()
    with pytest.raises(UnknownEmployeeError):
        tracker.record_event(LeaveEvent("BAD", "annual", "01/01/2024", "02/01/2024"))


def test_negative_annual_balance_warns():
    employee = EmployeeProfile("E1", "Dana", "01/01/2024")
    tracker = LeaveTrackerClient([employee])
    tracker.record_event(LeaveEvent("E1", "annual", "01/01/2024", "31/01/2024", days=20))
    snapshot = tracker.balance("E1", "31/01/2024")
    assert snapshot.annual_balance < 0
    assert any("Annual" in warning for warning in snapshot.warnings)


def test_employee_to_dict_localizes_date():
    employee = EmployeeProfile("E1", "Dana", "2024-01-01")
    assert employee.to_dict()["hire_date"] == "01/01/2024"


def test_leave_event_to_dict_localizes_dates():
    event = LeaveEvent("E1", "annual", "2024-08-18", "2024-08-22")
    assert event.to_dict()["start_date"] == "18/08/2024"


def test_from_csv_loads_data(tmp_path):
    employees = tmp_path / "employees.csv"
    events = tmp_path / "events.csv"
    employees.write_text("employee_id,name,hire_date,work_week_days\nE1,Dana,01/01/2024,5\n", encoding="utf-8")
    events.write_text("employee_id,absence_type,start_date,end_date,days,approved\nE1,annual,18/08/2024,22/08/2024,,true\n", encoding="utf-8")
    tracker = LeaveTrackerClient.from_csv(employees, events)
    assert tracker.balance("E1", "31/12/2024").annual_used == 5.0


def test_export_balances_csv(tmp_path):
    employee = EmployeeProfile("E1", "Dana", "01/01/2024")
    tracker = LeaveTrackerClient([employee])
    output = tracker.export_balances_csv(tmp_path / "out.csv", "31/12/2024")
    assert output.exists()
    assert "annual_balance" in output.read_text(encoding="utf-8-sig")


def test_write_templates(tmp_path):
    employees, events = write_template_csvs(tmp_path)
    assert employees.exists()
    assert events.exists()
    assert "01/01/2024" in employees.read_text(encoding="utf-8-sig")


def test_async_balance():
    employee = EmployeeProfile("E1", "Dana", "01/01/2024")
    tracker = LeaveTrackerClient([employee])
    snapshot = asyncio.run(tracker.abalance("E1", "31/12/2024"))
    assert snapshot.employee_id == "E1"


def test_cli_sick_pay():
    runner = CliRunner()
    result = runner.invoke(cli, ["sick-pay", "--days", "5"])
    assert result.exit_code == 0
    assert json.loads(result.output)["paid_equivalent_days"] == 3.0


def test_cli_create_employee_and_add_event_chain():
    runner = CliRunner()
    created = runner.invoke(cli, ["create-employee", "--employee-id", "E17", "--name", "Dana", "--hire-date", "01/01/2024"])
    assert created.exit_code == 0
    employee_id = json.loads(created.output)["employee"]["employee_id"]
    event = runner.invoke(cli, ["add-event", "--employee-id", employee_id, "--absence-type", "annual", "--start-date", "18/08/2024", "--end-date", "22/08/2024"])
    assert event.exit_code == 0
    assert json.loads(event.output)["event"]["employee_id"] == "E17"


def test_cli_scenario():
    runner = CliRunner()
    result = runner.invoke(cli, ["scenario"])
    assert result.exit_code == 0
    assert "annual_balance" in result.output


def test_cli_template_and_summary(tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli, ["template", str(tmp_path)])
    assert result.exit_code == 0
    summary = runner.invoke(cli, ["summary", str(tmp_path / "employees.csv"), str(tmp_path / "events.csv"), "--as-of", "31/12/2024"])
    assert summary.exit_code == 0
    assert "E001" in summary.output


def test_cli_validate_data(tmp_path):
    employees, events = write_template_csvs(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-data", str(employees), str(events), "--as-of", "31/12/2024"])
    assert result.exit_code == 0
    assert json.loads(result.output)["employees"] == 1
