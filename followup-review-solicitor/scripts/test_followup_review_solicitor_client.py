from __future__ import annotations

import asyncio
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

import followup_review_solicitor as client


def req(**overrides):
    data = {
        "business_name": "אור חשמל",
        "customer_name": "דנה",
        "event_type": client.EventType.SERVICE_COMPLETED,
        "event_date": "03/06/2026",
        "channel": client.Channel.WHATSAPP,
        "sentiment": client.Sentiment.UNKNOWN,
        "consent_status": client.ConsentStatus.TRANSACTIONAL,
        "now": datetime(2026, 6, 3, 15, 0, tzinfo=ZoneInfo("Asia/Jerusalem")),
    }
    data.update(overrides)
    return client.FollowupRequest(**data)


def plan(**overrides):
    return client.FollowupSolicitorClient().generate_plan(req(**overrides))


def test_format_ils_integer():
    assert client.format_ils(1250) == "₪1,250"


def test_format_ils_decimal():
    assert client.format_ils(1250.5) == "₪1,250.50"


def test_parse_valid_slash_date():
    assert client.parse_israeli_date("03/06/2026").day == 3


def test_parse_legacy_hyphen_date_supported():
    assert client.parse_israeli_date("03-06-2026").month == 6


def test_parse_invalid_date():
    with pytest.raises(ValueError):
        client.parse_israeli_date("2026-06-03")


def test_format_israeli_date_uses_slashes():
    assert client.format_israeli_date("03-06-2026") == "03/06/2026"


def test_normalize_local_mobile():
    assert client.normalize_israeli_mobile("050-123-4567") == "+972501234567"


def test_normalize_e164_mobile():
    assert client.normalize_israeli_mobile("+972 50 123 4567") == "+972501234567"


def test_invalid_phone_rejected():
    with pytest.raises(ValueError):
        client.normalize_israeli_mobile("12345")


def test_opt_out_hebrew():
    assert client.is_opt_out_text("הסר")


def test_opt_out_english():
    assert client.is_opt_out_text("STOP")


def test_service_checkin_message():
    p = plan()
    assert p.should_send is True
    assert "רציתי לוודא" in p.message_he
    assert "חוות דעת" not in p.message_he


def test_review_requires_positive_signal():
    p = plan(event_type=client.EventType.REVIEW_REQUEST, review_url="https://g.page/r/example/review")
    assert p.should_send is False
    assert "positive" in " ".join(p.compliance_notes).lower()


def test_review_requires_url():
    p = plan(event_type=client.EventType.REVIEW_REQUEST, sentiment=client.Sentiment.POSITIVE)
    assert p.should_send is False
    assert "Review URL" in " ".join(p.compliance_notes)


def test_positive_review_request_contains_url():
    p = plan(event_type=client.EventType.REVIEW_REQUEST, sentiment=client.Sentiment.POSITIVE, review_url="https://g.page/r/example/review")
    assert p.should_send is True
    assert "חוות דעת" in p.message_he
    assert "https://g.page/r/example/review" in p.message_he


def test_negative_sentiment_blocks_review():
    p = plan(event_type=client.EventType.REVIEW_REQUEST, sentiment=client.Sentiment.NEGATIVE, review_url="https://g.page/r/example/review")
    assert p.should_send is False
    assert p.fallback_action


def test_complaint_blocks_review():
    p = plan(event_type=client.EventType.REVIEW_REQUEST, sentiment=client.Sentiment.POSITIVE, review_url="https://g.page/r/example/review", complaint_open=True)
    assert p.should_send is False
    assert "complaint" in " ".join(p.compliance_notes).lower()


def test_opted_out_suppressed():
    p = plan(consent_status=client.ConsentStatus.OPTED_OUT)
    assert p.should_send is False
    assert p.message_he == ""


def test_promotional_requires_opt_in():
    p = plan(promotional_text=True, consent_status=client.ConsentStatus.UNKNOWN)
    assert p.should_send is False
    assert "Promotional" in " ".join(p.compliance_notes)


def test_promotional_sms_adds_opt_out():
    p = plan(promotional_text=True, consent_status=client.ConsentStatus.MARKETING_OPT_IN, channel=client.Channel.SMS)
    assert p.should_send is True
    assert "להסרה" in p.message_he


def test_invoice_message_formats_amount():
    p = plan(event_type=client.EventType.INVOICE_DUE, amount_ils=1250)
    assert p.should_send is True
    assert "₪1,250" in p.message_he
    assert "חשבונית מס/קבלה" in p.message_he


def test_missing_documents_uses_accounting_terms():
    p = plan(event_type=client.EventType.MISSING_DOCUMENTS, period_label="מאי 2026", due_date="10/06/2026", business_type="accountant")
    assert p.should_send is True
    assert "חשבוניות/קבלות" in p.message_he
    assert "10/06/2026" in p.message_he


def test_appointment_reminder():
    p = plan(event_type=client.EventType.APPOINTMENT_REMINDER, appointment_time="10:30")
    assert p.should_send is True
    assert "10:30" in p.message_he
    assert "תזכורת לפגישה" in p.message_he


def test_delivery_checkin():
    p = plan(event_type=client.EventType.DELIVERY_CHECKIN)
    assert p.should_send is True
    assert "המשלוח" in p.message_he


def test_customer_name_fallback():
    p = plan(customer_name=None)
    assert p.message_he.startswith("היי,")


def test_missing_business_name_blocks():
    p = plan(business_name="")
    assert p.should_send is False
    assert "business name" in " ".join(p.compliance_notes).lower()


def test_invalid_phone_blocks_plan():
    p = plan(phone="12345", channel=client.Channel.SMS)
    assert p.should_send is False
    assert "phone" in " ".join(p.compliance_notes).lower()


def test_saturday_moves_to_sunday():
    p = plan(now=datetime(2026, 6, 6, 10, 0, tzinfo=ZoneInfo("Asia/Jerusalem")))
    assert p.recommended_send_at.weekday() == 6
    assert p.recommended_send_at.hour == 9


def test_friday_after_cutoff_moves_to_sunday():
    p = plan(now=datetime(2026, 6, 5, 13, 0, tzinfo=ZoneInfo("Asia/Jerusalem")))
    assert p.recommended_send_at.weekday() == 6


def test_late_evening_moves_next_day():
    p = plan(now=datetime(2026, 6, 3, 21, 30, tzinfo=ZoneInfo("Asia/Jerusalem")))
    assert p.recommended_send_at.date().isoformat() == "2026-06-04"


def test_holiday_blackout_skipped():
    p = plan(
        now=datetime(2026, 6, 3, 8, 0, tzinfo=ZoneInfo("Asia/Jerusalem")),
        holiday_blackouts=("03/06/2026",),
    )
    assert p.recommended_send_at.strftime("%d/%m/%Y") == "04/06/2026"


def test_plan_serializes_to_json():
    p = plan()
    payload = json.loads(p.to_json())
    assert payload["should_send"] is True
    assert payload["timezone"] == "Asia/Jerusalem"


@pytest.mark.asyncio
async def test_async_plan():
    p = await client.FollowupSolicitorClient().async_generate_plan(req())
    assert p.should_send is True


def test_generate_many():
    plans = client.FollowupSolicitorClient().generate_many([req(), req(customer_name="יואב")])
    assert len(plans) == 2
    assert all(item.should_send for item in plans)


def test_no_unresolved_placeholders_in_rendered_message():
    p = plan(event_type=client.EventType.INVOICE_DUE, amount_ils=450)
    assert client.contains_unresolved_placeholders(p.message_he) is False


def test_sensitive_business_adds_risk_flag():
    p = plan(business_type="clinic", event_type=client.EventType.APPOINTMENT_REMINDER)
    assert p.should_send is True
    assert "sensitive_business_type" in p.risk_flags


def test_consumer_followup_without_business_name_allowed():
    p = plan(business_name="", event_type=client.EventType.CONSUMER_FOLLOWUP)
    assert p.should_send is True
    assert "עדכון" in p.message_he


def test_idempotency_includes_event_and_contact():
    p = plan(event_id="svc_1", contact_id="c_1")
    assert p.idempotency_key.startswith("svc_1:c_1:service_completed")


def test_create_and_load_request_record(tmp_path):
    request = req(event_id="svc_chain_1")
    created = client.create_request_record(request, directory=tmp_path)
    assert created["id"] == "svc_chain_1"
    loaded = client.load_request_record(created["id"], directory=tmp_path)
    assert loaded.business_name == "אור חשמל"


def test_package_import_exports_client():
    assert hasattr(client, "FollowupSolicitorClient")


def test_slug_underscored_script_exists():
    script = __import__("pathlib").Path(__file__).with_name("followup_review_solicitor_client.py")
    assert script.exists()
