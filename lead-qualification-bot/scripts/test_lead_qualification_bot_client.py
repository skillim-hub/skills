from __future__ import annotations

import asyncio
import json

import pytest
from typer.testing import CliRunner

from lead_qualification_bot import (
    LeadQualificationClient,
    detect_budget,
    detect_city,
    detect_service,
    detect_urgency,
    flatten_lead,
    is_opt_out,
    is_sensitive,
    normalize_phone,
)
from lead_qualification_bot.cli import app


def test_normalize_local_mobile():
    assert normalize_phone("050-123-4567") == "+972501234567"


def test_normalize_without_zero():
    assert normalize_phone("501234567") == "+972501234567"


def test_normalize_972():
    assert normalize_phone("972501234567") == "+972501234567"


def test_invalid_phone_raises():
    with pytest.raises(ValueError):
        normalize_phone("123")


@pytest.mark.parametrize(
    ("text", "city"),
    [
        ("אני בתא", "תל אביב"),
        ("שירות בראשלצ", "ראשון לציון"),
        ("צריך בפ״ת", "פתח תקווה"),
        ("בחיפה היום", "חיפה"),
    ],
)
def test_detect_city_aliases(text, city):
    assert detect_city(text) == city


def test_detect_budget_single_value():
    budget = detect_budget("תקציב 500 שח")
    assert budget is not None
    assert budget.min == 500
    assert budget.max == 500


def test_detect_budget_range():
    budget = detect_budget("בין 500 ל-700 שקל")
    assert budget is not None
    assert budget.min == 500
    assert budget.max == 700


def test_detect_service_plumbing():
    assert detect_service("יש נזילה בכיור") == "plumbing"


def test_detect_urgency_same_day():
    assert detect_urgency("דחוף להיום") == "same_day"


def test_detect_urgency_week():
    assert detect_urgency("אפשר שבוע הבא") == "this_week"


def test_opt_out_hebrew():
    assert is_opt_out("הסרה בבקשה")


def test_opt_out_english():
    assert is_opt_out("STOP")


def test_sensitive_legal():
    assert is_sensitive("פיטרו אותי צריך עורך דין", "legal")


def test_importable_package():
    from lead_qualification_bot import Lead

    lead = LeadQualificationClient().create_lead("נזילה היום בתא תקציב 500 שח", phone="0501234567")
    assert lead.__class__.__name__ == Lead.__name__


def test_qualify_hot_plumbing():
    lead = LeadQualificationClient().create_lead(
        "צריך תיקון נזילה היום בתל אביב תקציב 500 שח",
        phone="050-123-4567",
        name="דנה",
    )
    assert lead.qualification.tier == "hot"
    assert lead.customer.city == "תל אביב"
    assert lead.budget_ils is not None
    assert lead.budget_ils.max == 500


def test_qualify_unknown_price_is_not_hot():
    lead = LeadQualificationClient().create_lead("כמה עולה?", phone="0501234567")
    assert lead.qualification.tier in {"nurture", "low_fit"}
    assert "service_category" in lead.qualification.missing_fields


def test_qualify_opt_out_suppresses_marketing():
    lead = LeadQualificationClient().create_lead("הסרה", phone="0501234567")
    assert lead.opt_out is True
    assert lead.qualification.next_action == "suppress_marketing"


def test_qualify_support_refund():
    lead = LeadQualificationClient().create_lead("אני רוצה החזר כספי", phone="0501234567")
    assert lead.service_category == "support"
    assert lead.qualification.tier == "support"


def test_qualify_human_request():
    lead = LeadQualificationClient().create_lead("אפשר נציג?", phone="0501234567")
    assert lead.qualification.tier == "human"
    assert lead.qualification.next_action == "human_handoff"


def test_qualify_accounting_sensitive_tax():
    lead = LeadQualificationClient().create_lead("פתחתי עוסק כמה מס אשלם?", phone="0501234567")
    assert lead.service_category == "accounting"
    assert lead.qualification.tier == "human"


def test_qualify_clinic_minor_sensitive():
    lead = LeadQualificationClient().create_lead("כמה עולה טיפול לילד בן 8?", phone="0501234567")
    assert lead.qualification.tier == "human"


def test_qualify_no_budget_still_warm_possible():
    lead = LeadQualificationClient().create_lead("צריך אתר תדמית עד סוף החודש בתל אביב", phone="0501234567")
    assert lead.service_category == "web_design"
    assert lead.qualification.tier in {"warm", "hot", "nurture"}


def test_async_create_lead():
    async def run():
        return await LeadQualificationClient().acreate_lead("נזילה היום בתא תקציב 500 שח", phone="0501234567")

    lead = asyncio.run(run())
    assert lead.customer.city == "תל אביב"


def test_json_serialization_contains_hebrew():
    client = LeadQualificationClient()
    lead = client.create_lead("נזילה היום בתא תקציב 500 שח", phone="0501234567")
    data = client.to_json(lead)
    assert "תל אביב" in data


def test_flatten_lead_has_score():
    lead = LeadQualificationClient().create_lead("נזילה היום בתא תקציב 500 שח", phone="0501234567")
    flat = flatten_lead(lead)
    assert "score" in flat
    assert flat["phone_e164"] == "+972501234567"


def test_batch_csv(tmp_path):
    input_path = tmp_path / "in.csv"
    output_path = tmp_path / "out.csv"
    input_path.write_text("message,phone,name\nנזילה היום בתא תקציב 500 שח,0501234567,דנה\n", encoding="utf-8")
    leads = LeadQualificationClient().batch_csv(input_path, output_path)
    assert len(leads) == 1
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8-sig")
    assert "תל אביב" in content


def test_cli_create_outputs_json():
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["create", "--message", "נזילה היום בתא תקציב 500 שח", "--phone", "0501234567", "--env", "sandbox"],
    )
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["customer"]["city"] == "תל אביב"
    assert parsed["environment"] == "sandbox"


def test_cli_qualify_async_outputs_json():
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["qualify", "--message", "נזילה היום בתא תקציב 500 שח", "--phone", "0501234567", "--async", "--env", "production"],
    )
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["environment"] == "production"


def test_cli_get_chains_create_response(tmp_path):
    runner = CliRunner()
    create_result = runner.invoke(
        app,
        ["create", "--message", "נזילה היום בתא תקציב 500 שח", "--phone", "0501234567"],
    )
    assert create_result.exit_code == 0
    data = json.loads(create_result.output)
    lead_id = data["lead_id"]
    lead_path = tmp_path / f"{lead_id}.json"
    lead_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    get_result = runner.invoke(app, ["get", "--lead-json", str(lead_path)])
    assert get_result.exit_code == 0
    assert lead_id in get_result.output


def test_cli_ask_next():
    runner = CliRunner()
    result = runner.invoke(app, ["ask-next", "--message", "כמה עולה?", "--phone", "0501234567"])
    assert result.exit_code == 0
    assert "מה בדיוק צריך" in result.output


def test_cli_batch(tmp_path):
    input_path = tmp_path / "in.csv"
    output_path = tmp_path / "out.csv"
    input_path.write_text("message,phone\nנזילה היום בתא תקציב 500 שח,0501234567\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["batch", "--input", str(input_path), "--output", str(output_path), "--env", "sandbox"])
    assert result.exit_code == 0
    assert output_path.exists()


def test_spam_low_score():
    lead = LeadQualificationClient().create_lead("זכית בקזינו לחץ כאן", phone="0501234567")
    assert lead.qualification.tier == "spam"


def test_eilat_out_of_area_reason():
    lead = LeadQualificationClient().create_lead("צריך נזילה היום באילת תקציב 500 שח", phone="0501234567")
    assert "possible_out_of_area" in lead.qualification.reasons


def test_underscored_client_module_importable():
    from scripts import lead_qualification_bot_client as compat

    assert hasattr(compat, "LeadQualificationClient")



def test_verified_2026_constants():
    import lead_qualification_bot as lqb

    assert lqb.DEFAULT_VAT_RATE == 0.18
    assert lqb.DEFAULT_EXEMPT_DEALER_THRESHOLD_ILS_2026 == 122_833
    assert lqb.ISRAEL_INVOICES_THRESHOLD_ILS_FROM_2026_06_01 == 5_000
