from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

from lead_router import LeadRouterClient, default_config, normalize_language, normalize_phone

ROOT = Path(__file__).resolve().parents[1]
CLI_MODULE = "lead_router.cli"


def route(payload):
    return LeadRouterClient().route_lead(payload)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", CLI_MODULE, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )


def test_hebrew_language_detection():
    lang, warnings, counts = normalize_language(None, "צריך הצעת מחיר")
    assert lang == "HE" and counts["HE"] > 0


def test_arabic_language_detection():
    lang, warnings, counts = normalize_language(None, "مرحبا أحتاج خدمة")
    assert lang == "AR" and counts["AR"] > 0


def test_russian_language_detection():
    lang, warnings, counts = normalize_language(None, "Нужна поддержка")
    assert lang == "RU" and counts["RU"] > 0


def test_english_language_detection():
    lang, warnings, counts = normalize_language(None, "Need pricing for installation")
    assert lang == "EN"


def test_mixed_language_warns_and_prefers_strong_signal():
    lang, warnings, counts = normalize_language(None, "Hi צריך עזרה בהתקנה")
    assert lang == "HE"
    assert "LANGUAGE_MIXED" in warnings


def test_explicit_language_override():
    result = route({"phone": "0521234567", "language": "ru", "message": "Need help with invoice"})
    assert result.language == "RU"
    assert result.product_interest == "billing"


def test_phone_normalization_mobile():
    normalized, warnings, area = normalize_phone("052-123-4567")
    assert normalized == "+972521234567"
    assert area is None
    assert warnings == []


def test_phone_area_code_infers_jerusalem_weakly():
    result = route({"phone": "02-5555555", "message": "צריך לקבוע תור"})
    assert result.region == "JERUSALEM"
    assert "REGION_FROM_PHONE_WEAK" in result.warnings


def test_city_beats_phone_area_code():
    result = route({"phone": "03-5555555", "city": "באר שבע", "message": "צריך התקנה"})
    assert result.region == "SOUTH"


def test_mobile_does_not_infer_region():
    result = route({"phone": "0521234567", "message": "צריך מחיר"})
    assert result.region == "UNKNOWN"
    assert "UNKNOWN_REGION" in result.warnings


def test_hebrew_haifa_installation_routes_north_service():
    result = route({"phone": "0521234567", "message": "צריכה הצעת מחיר להתקנה באזור חיפה", "channel": "whatsapp"})
    assert result.language == "HE"
    assert result.region == "HAIFA"
    assert result.product_interest == "installation"
    assert result.assignee == "North Service Queue"
    assert result.priority == "high"


def test_hebrew_tel_aviv_sales_routes_center_sales():
    result = route({"phone": "0501112222", "message": "אשמח למחיר בתל אביב", "channel": "web_form"})
    assert result.language == "HE"
    assert result.region == "CENTER"
    assert result.product_interest == "sales"
    assert result.assignee == "Center Sales Queue"


def test_russian_support_routes_russian_queue():
    result = route({"phone": "+972541112222", "city": "חיפה", "message": "Устройство не работает, нужна помощь"})
    assert result.language == "RU"
    assert result.product_interest == "support"
    assert result.assignee == "Russian Support Queue"


def test_arabic_sales_nazareth_routes_arabic_queue():
    result = route({"phone": "0523334444", "city": "נצרת", "message": "مرحبا، أريد عرض سعر للخدمة"})
    assert result.language == "AR"
    assert result.region == "NORTH"
    assert result.product_interest == "sales"
    assert result.assignee == "Arabic Sales Queue"


def test_billing_request_routes_billing():
    result = route({"email": "noam@example.co.il", "message": "אפשר לקבל חשבונית מס קבלה?"})
    assert result.product_interest == "billing"
    assert result.department == "billing"
    assert result.assignee == "Billing Queue"


def test_appointment_jerusalem_routes_appointments():
    result = route({"phone": "025555555", "message": "מבקשת לקבוע תור בירושלים"})
    assert result.product_interest == "appointments"
    assert result.region == "JERUSALEM"
    assert result.department == "appointments"


def test_urgent_support_has_urgent_priority_and_short_sla():
    result = route({"phone": "0521234567", "message": "דחוף, השירות לא עובד עכשיו"})
    assert result.priority == "urgent"
    assert result.sla_minutes == 10


def test_enterprise_high_budget_routes_enterprise():
    result = route({"email": "ops@example.co.il", "message": "Need rollout for 12 branches across Israel", "budget": 120000})
    assert result.product_interest == "enterprise"
    assert result.assignee == "Enterprise Desk"
    assert result.priority == "high"


def test_high_budget_sales_routes_senior_sales():
    result = route({"email": "buyer@example.co.il", "message": "Need quote", "budget": 60000})
    assert result.product_interest == "sales"
    assert result.assignee == "Senior Sales Queue"


def test_missing_contact_routes_data_quality():
    result = route({"message": "אשמח להצעת מחיר"})
    assert result.assignee == "Data Quality Queue"
    assert "MISSING_CONTACT" in result.warnings
    assert result.priority == "low"


def test_invalid_phone_with_email_warns_but_routes():
    result = route({"phone": "abc", "email": "lead@example.co.il", "message": "Need pricing"})
    assert "PHONE_INVALID" in result.warnings
    assert result.assignee != "Data Quality Queue"


def test_missing_marketing_consent_warning():
    result = route({"phone": "0521234567", "message": "אשמח להצעת מחיר", "consent_marketing": False})
    assert "MARKETING_CONSENT_MISSING" in result.warnings
    assert "Marketing follow-up is not allowed" in result.handoff_note


def test_duplicate_risk_warning():
    result = route({"phone": "0521234567", "message": "צריך מחיר", "metadata": {"duplicate_risk": True}})
    assert "DUPLICATE_RISK" in result.warnings


def test_unknown_language_routes_multilingual_or_qualification():
    result = route({"phone": "0521234567", "message": "Necesito precio para instalación"})
    assert result.language == "UNKNOWN"
    assert "UNSUPPORTED_LANGUAGE" in result.warnings
    assert result.assignee in {"Multilingual Intake Queue", "Qualification Queue"}


def test_eilat_region():
    result = route({"phone": "0521234567", "city": "אילת", "message": "צריך התקנה"})
    assert result.region == "EILAT"
    assert result.department == "installation"


def test_west_bank_region():
    result = route({"phone": "0521234567", "city": "אריאל", "message": "מבקש הצעת מחיר"})
    assert result.region == "WEST_BANK"
    assert result.product_interest == "sales"


def test_arabic_billing():
    result = route({"email": "client@example.co.il", "message": "أحتاج فاتورة للدفع"})
    assert result.language == "AR"
    assert result.product_interest == "billing"
    assert result.department == "billing"


def test_russian_billing():
    result = route({"email": "client@example.co.il", "message": "Нужен счет за оплату"})
    assert result.language == "RU"
    assert result.product_interest == "billing"


def test_explain_contains_scores_and_selected():
    explanation = LeadRouterClient().explain({"phone": "0521234567", "message": "צריך מחיר בחיפה"})
    assert "normalized" in explanation
    assert "rules" in explanation
    assert "selected" in explanation


@pytest.mark.asyncio
async def test_async_route_lead():
    result = await LeadRouterClient().aroute_lead({"phone": "0521234567", "message": "צריך מחיר בחיפה"})
    assert result.product_interest == "sales"


@pytest.mark.asyncio
async def test_async_route_many():
    results = await LeadRouterClient().aroute_many([
        {"phone": "0521234567", "message": "צריך מחיר בחיפה"},
        {"email": "a@example.com", "message": "Need invoice"},
    ])
    assert len(results) == 2
    assert results[1].department == "billing"


def test_validate_default_config():
    errors = LeadRouterClient.validate_config(default_config())
    assert errors == []


def test_invalid_config_reports_errors():
    errors = LeadRouterClient.validate_config({"rules": [{"name": "x"}]})
    assert errors


def test_route_result_json_roundtrip():
    result = route({"phone": "0521234567", "message": "צריך מחיר בחיפה"})
    data = json.loads(result.to_json())
    assert data["language"] == "HE"


def test_create_lead_and_route_stored(tmp_path):
    store = tmp_path / "leads.json"
    client = LeadRouterClient()
    created = client.create_lead({"phone": "0521234567", "message": "צריך מחיר בחיפה"}, store)
    assert created["lead_id"].startswith("lead_")
    result = client.route_stored_lead(created["lead_id"], store)
    assert result.product_interest == "sales"


def test_cli_route_json_smoke():
    completed = run_cli("route-json", '{"phone":"0521234567","message":"צריך מחיר בחיפה"}', "--env", "sandbox")
    data = json.loads(completed.stdout)
    assert data["language"] == "HE"
    assert data["product_interest"] == "sales"


def test_cli_create_then_route_stored(tmp_path):
    store = tmp_path / "leads.json"
    created = run_cli(
        "create",
        '{"phone":"0521234567","message":"צריך מחיר בחיפה"}',
        "--store",
        str(store),
        "--env",
        "sandbox",
    )
    create_data = json.loads(created.stdout)
    routed = run_cli("route-stored", "--id", create_data["lead_id"], "--store", str(store), "--env", "sandbox")
    route_data = json.loads(routed.stdout)
    assert route_data["product_interest"] == "sales"


def test_cli_default_config_smoke(tmp_path):
    output = tmp_path / "config.json"
    run_cli("default-config", "--output", str(output), "--env", "sandbox")
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["rules"]
