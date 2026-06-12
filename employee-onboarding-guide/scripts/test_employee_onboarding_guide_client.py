from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import employee_onboarding_guide_client as client


def profile(**kwargs):
    data = {
        "full_name": "Dana Levi",
        "start_date": "01-09-2026",
        "employment_type": "employee",
        "bank_details_received": True,
        "employment_notice_status": "drafted",
    }
    data.update(kwargs)
    return client.EmployeeProfile(**data)


def test_validate_hyphen_date():
    assert client.validate_date("01-09-2026")


def test_validate_slash_date():
    assert client.validate_date("01/09/2026")


def test_invalid_date_rejected():
    assert not client.validate_date("2026-09-01")


def test_invalid_calendar_date_rejected():
    assert not client.validate_date("31/02/2026")


def test_normalize_english_date():
    assert client.normalize_date("01/09/2026", "en") == "01-09-2026"


def test_normalize_hebrew_date():
    assert client.normalize_date("01-09-2026", "he") == "01/09/2026"


def test_days_until():
    assert client.days_until("05/06/2026", today=date(2026, 6, 1)) == 4


def test_employee_form_101_action():
    result = client.validate_profile(profile())
    assert any("within 7 days" in action for action in result.next_actions)


def test_supplier_warning():
    result = client.validate_profile(profile(employment_type="contractor"))
    assert any("do not request Form 101" in warning for warning in result.warnings)


def test_unknown_status_warning():
    result = client.validate_profile(profile(employment_type="unknown"))
    assert any("classification" in warning for warning in result.warnings)


def test_missing_name_error():
    result = client.validate_profile(profile(full_name=""))
    assert not result.ok
    assert "employee.full_name is required." in result.errors


def test_bad_start_date_error():
    result = client.validate_profile(profile(start_date="2026/09/01"))
    assert not result.ok


def test_other_employer_tax_warning():
    result = client.validate_profile(profile(has_other_employer=True))
    assert any("tax coordination" in warning for warning in result.warnings)


def test_other_employer_national_insurance_warning():
    result = client.validate_profile(profile(has_other_employer=True))
    assert any("National Insurance coordination" in warning for warning in result.warnings)


def test_active_pension_warning():
    result = client.validate_profile(profile(has_active_pension=True))
    assert any("Active pension arrangement" in warning for warning in result.warnings)


def test_active_pension_deadline_action():
    result = client.validate_profile(profile(has_active_pension=True, pension_fund_name="Example Fund"))
    assert any("first pension deposit deadline" in action for action in result.next_actions)


def test_no_active_pension_warning():
    result = client.validate_profile(profile(has_active_pension=False))
    assert any("neutral choice process" in warning for warning in result.warnings)


def test_hourly_without_timekeeping_warning():
    result = client.validate_profile(profile(salary_type="hourly"))
    assert any("timekeeping" in warning for warning in result.warnings)


def test_hourly_with_timekeeping_cleaner():
    result = client.validate_profile(profile(salary_type="hourly", timekeeping_method="digital timesheet"))
    assert not any("lacks timekeeping" in warning for warning in result.warnings)


def test_remote_warning():
    result = client.validate_profile(profile(remote=True))
    assert any("Remote employee" in warning for warning in result.warnings)


def test_foreign_worker_error():
    result = client.validate_profile(profile(foreign_worker=True))
    assert not result.ok
    assert any("Foreign worker" in error for error in result.errors)


def test_youth_warning():
    result = client.validate_profile(profile(youth=True))
    assert any("Youth employee" in warning for warning in result.warnings)


def test_student_warning():
    result = client.validate_profile(profile(student=True))
    assert any("Student status" in warning for warning in result.warnings)


def test_insecure_channel_warning():
    result = client.validate_profile(profile(secure_channel=False))
    assert any("Sensitive document channel" in warning for warning in result.warnings)


def test_missing_bank_warning():
    result = client.validate_profile(profile(bank_details_received=False))
    assert any("Bank details missing" in warning for warning in result.warnings)


def test_missing_terms_warning():
    result = client.validate_profile(profile(employment_notice_status="missing"))
    assert any("Employment notice" in warning for warning in result.warnings)


def test_equipment_warning():
    result = client.validate_profile(profile(equipment_required=True, equipment_form_signed=False))
    assert any("Equipment required" in warning for warning in result.warnings)


def test_start_date_soon_warning():
    result = client.validate_profile(profile(start_date="05/06/2026"), today=date(2026, 6, 1))
    assert any("within 7 days" in warning for warning in result.warnings)


def test_english_checklist_contains_currency_and_payroll():
    text = client.generate_checklist(profile())
    assert "₪" in text
    assert "Payroll handoff" in text


def test_hebrew_checklist_localizes_date_and_terms():
    text = client.generate_hebrew_checklist(profile(start_date="01-09-2026", has_other_employer=True))
    assert "01/09/2026" in text
    assert "טופס 101" in text
    assert "תיאום מס" in text


def test_english_message():
    text = client.generate_employee_message("Dana", "25/08/2026", "en")
    assert "25-08-2026" in text
    assert "Completed Form 101" in text


def test_hebrew_message():
    text = client.generate_employee_message("דנה", "25-08-2026", "he")
    assert "25/08/2026" in text
    assert "טופס 101" in text


def test_profile_from_dict_nested():
    data = {
        "employee": {"full_name": "Dana", "start_date": "01/09/2026", "has_other_employer": True},
        "payroll": {"salary_type": "hourly", "hourly_rate_nis": 55},
        "documents": {"bank_details": "received", "employment_notice": "drafted"}
    }
    p = client.profile_from_dict(data)
    assert p.full_name == "Dana"
    assert p.salary_type == "hourly"
    assert p.hourly_rate_nis == 55


def test_create_and_load_record(tmp_path):
    p = profile()
    response = client.create_record(p, storage_dir=tmp_path)
    loaded = client.load_record(response["id"], storage_dir=tmp_path)
    assert loaded.full_name == "Dana Levi"


def test_async_validate_profile():
    result = asyncio.run(client.async_validate_profile(profile()))
    assert result.ok


def test_async_create_record(tmp_path):
    response = asyncio.run(client.async_create_record(profile(), storage_dir=tmp_path))
    assert response["ok"]


def test_async_generate_checklist():
    text = asyncio.run(client.async_generate_checklist(profile(language="en")))
    assert "Onboarding Checklist" in text


def test_cli_create_then_checklist_chain(tmp_path):
    env = os.environ.copy()
    env["ONBOARDING_DATA_DIR"] = str(tmp_path / "records")
    create_result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "employee-onboarding-guide-cli.py"),
            "create",
            "--name",
            "Dana Levi",
            "--start-date",
            "01-09-2026",
            "--other-employer",
            "--active-pension",
            "--bank-details-received",
            "--employment-notice-status",
            "drafted",
        ],
        cwd=str(tmp_path),
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(create_result.stdout)
    checklist_result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "employee-onboarding-guide-cli.py"),
            "checklist",
            "--id",
            payload["id"],
        ],
        cwd=str(tmp_path),
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "Onboarding Checklist: Dana Levi" in checklist_result.stdout
    assert "Tax coordination" in checklist_result.stdout


def test_cli_validate_failure(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"employee": {"full_name": "", "start_date": "2026-09-01"}}), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "employee-onboarding-guide-cli.py"), "validate", "--path", str(bad)],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 1
    assert "DD-MM-YYYY or DD/MM/YYYY" in result.stdout


def test_cli_message_hebrew():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "employee-onboarding-guide-cli.py"),
            "message",
            "--name",
            "דנה",
            "--due-date",
            "25-08-2026",
            "--language",
            "he",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    assert "25/08/2026" in result.stdout


def test_no_hyphenated_client_file():
    assert not (SCRIPT_DIR / "employee-onboarding-guide-client.py").exists()


def test_public_import_module_has_expected_api():
    assert hasattr(client, "EmployeeProfile")
    assert hasattr(client, "create_record")
    assert hasattr(client, "async_generate_checklist")


def test_message_mentions_form_101_seven_days():
    text = client.generate_employee_message("Dana", "25-08-2026", "en")
    assert "within 7 days" in text


def test_hebrew_message_mentions_form_101_seven_days():
    text = client.generate_employee_message("דנה", "25-08-2026", "he")
    assert "7 ימים" in text


def test_verification_log_exists_and_summarizes():
    log = (SCRIPT_DIR.parent / "references" / "verification-log.md").read_text(encoding="utf-8")
    assert "Total checks" in log
    assert "final ✗ count" in log
