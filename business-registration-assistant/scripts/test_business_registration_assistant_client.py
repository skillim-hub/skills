from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

from business_registration_assistant import (
    BusinessIntake,
    BusinessRegistrationClient,
    RegistrationError,
    load_intake,
)


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
CLI_PATH = ROOT / "business-registration-assistant-cli.py"
CLIENT_SCRIPT = ROOT / "business_registration_assistant_client.py"


def subprocess_env() -> dict[str, str]:
    import os

    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(PROJECT_ROOT) + (os.pathsep + existing if existing else "")
    return env


def make_client() -> BusinessRegistrationClient:
    return BusinessRegistrationClient()


def test_tutor_below_ceiling_is_patur():
    intake = BusinessIntake("Private English tutoring", 72000, 5000, 122833)
    result = make_client().classify_status(intake)
    assert result.recommended_status == "osek_patur"
    assert any("within" in reason for reason in result.reasons)


def test_above_ceiling_is_murshe():
    intake = BusinessIntake("Software consulting", 220000, 12000, 122833)
    result = make_client().classify_status(intake)
    assert result.recommended_status == "osek_murshe"
    assert any(i.code == "TURNOVER_EXCEEDS_CEILING" for i in result.issues)


def test_regulated_profession_is_murshe():
    intake = BusinessIntake("Architecture services", 50000, 4000, 122833, regulated_profession=True)
    result = make_client().classify_status(intake)
    assert result.recommended_status == "osek_murshe"
    assert any(i.code == "REGULATED_PROFESSION" for i in result.issues)


def test_activity_keyword_detects_license():
    intake = BusinessIntake("Engineer consulting", 50000, 4000, 122833)
    result = make_client().classify_status(intake)
    assert result.recommended_status == "osek_murshe"


def test_clients_require_invoice_pushes_murshe():
    intake = BusinessIntake("Marketing services", 70000, 4000, 122833, clients_require_tax_invoice=True)
    result = make_client().classify_status(intake)
    assert result.recommended_status == "osek_murshe"
    assert any(i.code == "CLIENT_REQUIRES_TAX_INVOICE" for i in result.issues)


def test_large_vat_expenses_needs_review():
    intake = BusinessIntake("Video production", 90000, 6000, 122833, large_vat_bearing_expenses=True)
    result = make_client().classify_status(intake)
    assert result.recommended_status == "needs_review"
    assert any(i.code == "LARGE_VAT_EXPENSES" for i in result.issues)


def test_missing_threshold_needs_review():
    intake = BusinessIntake("Graphic design", 50000)
    result = make_client().classify_status(intake)
    assert result.recommended_status == "needs_review"
    assert any(i.code == "CURRENT_THRESHOLD_REQUIRED" for i in result.issues)


def test_foreign_clients_warning():
    intake = BusinessIntake("Copywriting", 90000, 5000, 122833, foreign_clients=True)
    result = make_client().classify_status(intake)
    assert any(i.code == "FOREIGN_CLIENT_VAT_COMPLEXITY" for i in result.issues)


def test_employee_warning():
    intake = BusinessIntake("Photography", 60000, 3000, 122833, currently_employee=True)
    result = make_client().classify_status(intake)
    assert any(i.code == "EMPLOYEE_PLUS_SELF_EMPLOYED" for i in result.issues)


def test_benefit_warning():
    intake = BusinessIntake("Translation", 30000, 2000, 122833, receives_benefits=True)
    result = make_client().classify_status(intake)
    assert any(i.code == "BENEFIT_INTERACTION" for i in result.issues)


def test_prior_file_warning():
    intake = BusinessIntake("Consulting", 30000, 2000, 122833, prior_self_employment_file=True)
    result = make_client().classify_status(intake)
    assert any(i.code == "PRIOR_FILE_REOPEN" for i in result.issues)


def test_late_registration_warning():
    intake = BusinessIntake(
        "Fitness coaching",
        30000,
        2000,
        122833,
        actual_start_date="15/04/2026",
        registration_date="01/06/2026",
    )
    result = make_client().classify_status(intake)
    assert any(i.code == "LATE_REGISTRATION" for i in result.issues)


def test_cash_warning():
    intake = BusinessIntake("Home repairs", 65000, 4000, 122833, cash_payments=True)
    result = make_client().classify_status(intake)
    assert any(i.code == "CASH_ACTIVITY" for i in result.issues)


def test_business_license_warning():
    intake = BusinessIntake("Selling cakes from home", 40000, 2000, 122833, home_food_or_licensed_activity=True)
    result = make_client().classify_status(intake)
    assert any(i.code == "BUSINESS_LICENSE_REVIEW" for i in result.issues)


def test_bank_missing_in_checklist():
    intake = BusinessIntake("Tutoring", 20000, 1000, 122833, bank_ownership_confirmation=False)
    checklist = make_client().build_document_checklist(intake)
    assert "Bank ownership confirmation" in checklist.missing


def test_foreign_online_checklist_items():
    intake = BusinessIntake("Etsy jewelry", 95000, 4000, 122833, foreign_clients=True, online_sales=True)
    checklist = make_client().build_document_checklist(intake)
    joined = " ".join(checklist.conditional)
    assert "Foreign client contracts" in joined
    assert "Platform seller reports" in joined


def test_import_export_checklist_items():
    intake = BusinessIntake("Import accessories", 85000, 3000, 122833, import_export=True)
    checklist = make_client().build_document_checklist(intake)
    assert any("Import/export" in item for item in checklist.conditional)


def test_authority_plan_for_patur_mentions_receipts():
    intake = BusinessIntake("Private tutoring", 50000, 3000, 122833)
    plan = make_client().build_authority_plan(intake)
    assert any("receipts" in item.lower() for item in plan.vat)


def test_authority_plan_for_murshe_mentions_vat_returns():
    intake = BusinessIntake("Software consulting", 200000, 10000, 122833)
    classification = make_client().classify_status(intake)
    plan = make_client().build_authority_plan(intake, classification)
    assert any("VAT returns" in item for item in plan.vat)


def test_full_plan_contains_all_sections():
    intake = BusinessIntake("Graphic design", 80000, 5000, 122833)
    plan = make_client().build_full_plan(intake).to_dict()
    assert set(plan) == {"intake", "classification", "checklist", "authority_plan"}


def test_migration_needed_when_forecast_exceeds_ceiling():
    result = make_client().migration_checklist(110000, 40000, 122833)
    assert result["migration_needed"] is True
    assert result["forecast_total_nis"] == 150000


def test_migration_not_needed_when_below_ceiling():
    result = make_client().migration_checklist(50000, 20000, 122833)
    assert result["migration_needed"] is False


def test_accountant_handoff_has_questions():
    intake = BusinessIntake("Graphic design", 80000, 5000, 122833)
    handoff = make_client().accountant_handoff(intake)
    assert handoff["questions"]
    assert handoff["requested_or_recommended_vat_status"] == "osek_patur"


def test_from_mapping_supports_nested_business():
    intake = BusinessIntake.from_mapping({"business": {"activity": "Design", "turnover": 1000}})
    assert intake.activity_description == "Design"
    assert intake.expected_annual_turnover_nis == 1000


def test_from_mapping_rejects_missing_turnover():
    with pytest.raises(RegistrationError):
        BusinessIntake.from_mapping({"business": {"activity": "Design"}})


def test_from_mapping_rejects_negative_turnover():
    with pytest.raises(RegistrationError):
        BusinessIntake.from_mapping({"business": {"activity": "Design", "turnover": -1}})


def test_validation_vague_activity():
    intake = BusinessIntake("x", 1000, 100, 122833)
    result = make_client().classify_status(intake)
    assert result.recommended_status == "needs_review"
    assert any(i.code == "MISSING_ACTIVITY" for i in result.issues)


def test_async_classification():
    async def run():
        intake = BusinessIntake("Graphic design", 80000, 5000, 122833)
        return await make_client().aclassify_status(intake)

    result = asyncio.run(run())
    assert result.recommended_status == "osek_patur"


def test_async_full_plan():
    async def run():
        intake = BusinessIntake("Graphic design", 80000, 5000, 122833)
        return await make_client().abuild_full_plan(intake)

    result = asyncio.run(run())
    assert result.classification.recommended_status == "osek_patur"


def test_create_case_and_plan_for_case(tmp_path):
    store = tmp_path / "cases.json"
    intake = BusinessIntake("Private tutoring", 50000, 3000, 122833)
    created = make_client().create_case(intake, store)
    assert created["id"].startswith("case_")
    plan = make_client().build_plan_for_case(created["id"], store)
    assert plan.classification.recommended_status == "osek_patur"


def test_async_create_case_and_get_case(tmp_path):
    async def run():
        store = tmp_path / "cases.json"
        intake = BusinessIntake("Private tutoring", 50000, 3000, 122833)
        created = await make_client().acreate_case(intake, store)
        loaded = await make_client().aget_case(created["id"], store)
        return loaded

    loaded = asyncio.run(run())
    assert loaded.activity_description == "Private tutoring"


def test_case_not_found(tmp_path):
    with pytest.raises(RegistrationError):
        make_client().get_case("case_missing", tmp_path / "cases.json")


def test_cli_classify_runs():
    proc = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "classify",
            "--activity",
            "Private English tutoring",
            "--turnover",
            "72000",
            "--profit",
            "5000",
            "--ceiling",
            "122833",
        ],
        text=True,
        capture_output=True,
        check=True,
        env=subprocess_env(),
    )
    data = json.loads(proc.stdout)
    assert data["recommended_status"] == "osek_patur"


def test_cli_case_create_and_case_plan(tmp_path):
    intake_path = tmp_path / "intake.json"
    store_path = tmp_path / "cases.json"
    intake_path.write_text(
        json.dumps({"business": {"activity": "Private tutoring", "turnover": 50000, "ceiling": 122833}}),
        encoding="utf-8",
    )

    create_proc = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "case-create",
            "--input",
            str(intake_path),
            "--case-store",
            str(store_path),
        ],
        text=True,
        capture_output=True,
        check=True,
        env=subprocess_env(),
    )
    case_id = json.loads(create_proc.stdout)["id"]

    plan_proc = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "case-plan",
            "--case-id",
            case_id,
            "--case-store",
            str(store_path),
        ],
        text=True,
        capture_output=True,
        check=True,
        env=subprocess_env(),
    )
    data = json.loads(plan_proc.stdout)
    assert data["classification"]["recommended_status"] == "osek_patur"


def test_cli_migrate_runs():
    proc = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "migrate",
            "--ytd",
            "110000",
            "--forecast",
            "40000",
            "--ceiling",
            "122833",
        ],
        text=True,
        capture_output=True,
        check=True,
        env=subprocess_env(),
    )
    data = json.loads(proc.stdout)
    assert data["migration_needed"] is True


def test_underscored_client_script_runs():
    proc = subprocess.run(
        [
            sys.executable,
            str(CLIENT_SCRIPT),
            "classify",
            "--activity",
            "Graphic design",
            "--turnover",
            "80000",
            "--ceiling",
            "122833",
        ],
        text=True,
        capture_output=True,
        check=True,
        env=subprocess_env(),
    )
    assert json.loads(proc.stdout)["recommended_status"] == "osek_patur"


def test_load_intake_json(tmp_path):
    path = tmp_path / "intake.json"
    path.write_text(json.dumps({"business": {"activity": "Design", "turnover": 1000}}), encoding="utf-8")
    intake = load_intake(path)
    assert intake.activity_description == "Design"


def test_importable_package():
    import business_registration_assistant as bra

    assert hasattr(bra, "BusinessRegistrationClient")


def test_verified_2026_ceiling_allows_patur():
    intake = BusinessIntake("Private tutoring", 122833, 3000, 122833)
    result = make_client().classify_status(intake)
    assert result.recommended_status == "osek_patur"


def test_verified_2026_ceiling_exceeded_requires_murshe():
    intake = BusinessIntake("Private tutoring", 122834, 3000, 122833)
    result = make_client().classify_status(intake)
    assert result.recommended_status == "osek_murshe"
