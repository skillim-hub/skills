from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from pathlib import Path

import pytest

import dental_treatment_planner as client

def base_plan():
    return {
        "context": {
            "provider": "private",
            "region": "center",
            "start_date": "01/07/2026",
            "insurance": {
                "name": "test",
                "discount_pct": 20,
                "annual_limit_ils": 2000,
                "used_annual_ils": 0,
                "waiting_period_met": True,
            },
        },
        "treatments": [{"code": "exam"}, {"code": "cleaning"}],
    }


def test_format_currency_uses_shekel_symbol():
    assert client.format_currency(1234.5) == "₪1,234.50"


def test_parse_israeli_date_accepts_dd_mm_yyyy():
    assert client.parse_israeli_date("31/12/2026").isoformat() == "2026-12-31"


def test_parse_israeli_date_accepts_iso():
    assert client.parse_israeli_date("2026-12-31").isoformat() == "2026-12-31"


def test_parse_israeli_date_rejects_bad_date():
    with pytest.raises(client.PlannerError):
        client.parse_israeli_date("31.12.2026")



def test_default_vat_rate_matches_2026_verified_rate():
    context = client.PatientContext.from_mapping({"include_vat": True})
    assert context.vat_rate == Decimal("0.18")
    assert client.CURRENT_ISRAEL_VAT_RATE_SOURCE_DATE == "04/06/2026"

def test_catalog_contains_core_treatments():
    catalog = client.treatment_catalog()
    assert "implant" in catalog
    assert catalog["cleaning"]["category"] == "preventive"


def test_sample_plan_is_estimable():
    estimate = client.DentalTreatmentPlannerClient().estimate(client.sample_plan())
    assert estimate.total_patient_ils > 0
    assert estimate.visits > 0


def test_unknown_treatment_raises_specific_error():
    plan = base_plan()
    plan["treatments"] = [{"code": "not_real"}]
    with pytest.raises(client.UnknownTreatmentCodeError):
        client.DentalTreatmentPlannerClient().estimate(plan)


def test_missing_treatments_raise_error():
    plan = base_plan()
    plan["treatments"] = []
    with pytest.raises(client.PlannerError):
        client.DentalTreatmentPlannerClient().estimate(plan)


def test_quantity_must_be_positive():
    plan = base_plan()
    plan["treatments"] = [{"code": "exam", "quantity": 0}]
    with pytest.raises(client.PlannerError):
        client.DentalTreatmentPlannerClient().estimate(plan)


def test_unsupported_provider_raises_error():
    plan = base_plan()
    plan["context"]["provider"] = "unknown"
    with pytest.raises(client.PlannerError):
        client.DentalTreatmentPlannerClient().estimate(plan)


def test_unsupported_region_raises_error():
    plan = base_plan()
    plan["context"]["region"] = "moon"
    with pytest.raises(client.PlannerError):
        client.DentalTreatmentPlannerClient().estimate(plan)


def test_insurance_discount_reduces_patient_total():
    with_insurance = client.DentalTreatmentPlannerClient().estimate(base_plan())
    no_insurance_plan = base_plan()
    no_insurance_plan["context"]["insurance"]["discount_pct"] = 0
    without_insurance = client.DentalTreatmentPlannerClient().estimate(no_insurance_plan)
    assert with_insurance.total_patient_ils < without_insurance.total_patient_ils


def test_annual_limit_caps_coverage():
    plan = base_plan()
    plan["context"]["insurance"]["annual_limit_ils"] = 50
    estimate = client.DentalTreatmentPlannerClient().estimate(plan)
    assert estimate.covered_ils == Decimal("50.00")


def test_waiting_period_blocks_coverage():
    plan = base_plan()
    plan["context"]["insurance"]["waiting_period_met"] = False
    estimate = client.DentalTreatmentPlannerClient().estimate(plan)
    assert estimate.covered_ils == Decimal("0.00")


def test_category_coverage_filters_discount():
    plan = base_plan()
    plan["context"]["insurance"]["covered_categories"] = ["diagnostic"]
    estimate = client.DentalTreatmentPlannerClient().estimate(plan)
    cleaning_line = [line for line in estimate.lines if line.code == "cleaning"][0]
    assert cleaning_line.covered_ils == Decimal("0.00")


def test_category_specific_discount_overrides_general_discount():
    plan = base_plan()
    plan["context"]["insurance"]["discount_pct"] = 10
    plan["context"]["insurance"]["category_discount_pct"] = {"preventive": 50}
    estimate = client.DentalTreatmentPlannerClient().estimate(plan)
    cleaning_line = [line for line in estimate.lines if line.code == "cleaning"][0]
    assert cleaning_line.covered_ils > Decimal("100.00")


def test_include_vat_adds_warning_and_tax():
    plan = base_plan()
    plan["context"]["include_vat"] = True
    estimate = client.DentalTreatmentPlannerClient().estimate(plan)
    assert estimate.vat_ils > 0
    assert any("VAT" in warning for warning in estimate.warnings)


def test_validation_warns_missing_requirement():
    plan = base_plan()
    plan["treatments"] = [{"code": "implant"}]
    warnings = client.DentalTreatmentPlannerClient().validate_plan(plan)
    assert any("panoramic_xray" in warning for warning in warnings)


def test_strict_validation_raises_on_warning():
    plan = base_plan()
    plan["context"]["strict"] = True
    plan["treatments"] = [{"code": "implant"}]
    with pytest.raises(client.ValidationError):
        client.DentalTreatmentPlannerClient().estimate(plan)


def test_compare_providers_sorts_by_patient_total():
    estimates = client.DentalTreatmentPlannerClient().compare_providers(base_plan())
    totals = [estimate.total_patient_ils for estimate in estimates]
    assert totals == sorted(totals)


def test_async_estimate_matches_sync_estimate():
    estimator = client.DentalTreatmentPlannerClient()
    sync_total = estimator.estimate(base_plan()).total_patient_ils
    async_total = asyncio.run(estimator.async_estimate(base_plan())).total_patient_ils
    assert async_total == sync_total


def test_schedule_uses_dd_mm_yyyy():
    estimate = client.DentalTreatmentPlannerClient().estimate(base_plan())
    assert estimate.schedule[0]["date"] == "01/07/2026"


def test_schedule_respects_monthly_limit():
    plan = base_plan()
    plan["context"]["max_visits_per_month"] = 1
    plan["treatments"] = [{"code": "orthodontic_consult"}, {"code": "aligner_case"}]
    estimate = client.DentalTreatmentPlannerClient().estimate(plan)
    months = [entry["date"][3:10] for entry in estimate.schedule[:3]]
    assert len(set(months)) == 3


def test_to_dict_converts_decimals_to_numbers():
    estimate = client.DentalTreatmentPlannerClient().estimate(base_plan())
    data = estimate.to_dict()
    assert isinstance(data["total_patient_ils"], float)


def test_to_markdown_contains_table_and_total():
    estimate = client.DentalTreatmentPlannerClient().estimate(base_plan())
    markdown = estimate.to_markdown()
    assert "| Code |" in markdown
    assert "Patient total" in markdown


def test_save_and_load_json_roundtrip(tmp_path):
    path = tmp_path / "plan.json"
    client.save_json(base_plan(), path)
    loaded = client.load_json(path)
    assert loaded["context"]["provider"] == "private"


def test_estimate_from_file(tmp_path):
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(base_plan()), encoding="utf-8")
    estimate = client.estimate_from_file(path)
    assert estimate.provider == "private"


def test_export_catalog_csv(tmp_path):
    output = tmp_path / "catalog.csv"
    client.DentalTreatmentPlannerClient().export_catalog_csv(output)
    text = output.read_text(encoding="utf-8")
    assert "code,description,category" in text
    assert "cleaning" in text


def test_override_price_changes_line_total():
    plan = base_plan()
    plan["treatments"] = [{"code": "exam", "override_price_ils": 1000}]
    estimate = client.DentalTreatmentPlannerClient().estimate(plan)
    assert estimate.lines[0].gross_ils > Decimal("1000.00")


def test_emergency_without_triage_warns():
    plan = base_plan()
    plan["treatments"] = [{"code": "extraction_simple", "urgency": "emergency"}]
    warnings = client.DentalTreatmentPlannerClient().validate_plan(plan)
    assert any("same-day" in warning for warning in warnings)


def test_max_visits_per_month_validation():
    plan = base_plan()
    plan["context"]["max_visits_per_month"] = 0
    with pytest.raises(client.PlannerError):
        client.DentalTreatmentPlannerClient().estimate(plan)


def test_parse_israeli_date_accepts_legacy_dash():
    assert client.parse_israeli_date("31-12-2026").isoformat() == "2026-12-31"


def test_create_plan_returns_plan_id_and_env():
    created = client.DentalTreatmentPlannerClient(environment="sandbox").create_plan(base_plan(), plan_id="plan-001")
    assert created["plan_id"] == "plan-001"
    assert created["environment"] == "sandbox"


def test_unsupported_environment_raises_error():
    with pytest.raises(client.PlannerError):
        client.DentalTreatmentPlannerClient(environment="qa")


def test_schedule_uses_dd_mm_yyyy_with_slashes():
    estimate = client.DentalTreatmentPlannerClient().estimate(base_plan())
    assert "/" in estimate.schedule[0]["date"]
    assert estimate.schedule[0]["date"] == "01/07/2026"
