from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs
from zoneinfo import ZoneInfo

import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parent))

from appointment_reminder_noshow_cli import cli
from appointment_reminder_noshow_client import (
    Appointment,
    AppointmentReminderClient,
    AppointmentStatus,
    Channel,
    Customer,
    NoShowTracker,
    Provider,
    ReminderError,
    ReminderMessage,
    ReminderPolicy,
    appointment_from_dict,
    normalize_israeli_mobile,
    parse_datetime,
)

TZ = ZoneInfo("Asia/Jerusalem")


def customer(**overrides):
    data = {
        "id": "c1",
        "name": "יעל כהן",
        "phone_e164": "+972501234567",
        "preferred_language": "he",
        "consent_whatsapp": True,
        "consent_sms": True,
    }
    data.update(overrides)
    return Customer(**data)


def appointment(**overrides):
    data = {
        "id": "a1",
        "customer": customer(),
        "starts_at": datetime(2026, 6, 18, 15, 30, tzinfo=TZ),
        "business_name": "קליניקת אביב",
        "service_name": "פגישת המשך",
        "location": "רוטשילד 10, תל אביב",
        "price_ils": 250,
    }
    data.update(overrides)
    return Appointment(**data)


def test_normalize_israeli_mobile_local_number():
    assert normalize_israeli_mobile("050-123-4567") == "+972501234567"


def test_normalize_israeli_mobile_rejects_landline():
    with pytest.raises(ReminderError) as exc:
        normalize_israeli_mobile("03-555-5555")
    assert exc.value.code == "PHONE_INVALID"


def test_hebrew_reminder_uses_israeli_date_and_options():
    client = AppointmentReminderClient()
    body = client.render_reminder(appointment(), Channel.WHATSAPP)
    assert "18-06-2026" in body
    assert "15:30" in body
    assert "להגעה" in body
    assert "רוטשילד" in body


def test_english_reminder_uses_english_copy():
    appt = appointment(customer=customer(name="Yael Cohen", preferred_language="en"), business_name="Aviv Clinic")
    body = AppointmentReminderClient().render_reminder(appt, Channel.SMS)
    assert "Reminder:" in body
    assert "18-06-2026" in body
    assert "Reply 1" in body


def test_choose_channel_prefers_whatsapp_with_consent():
    client = AppointmentReminderClient()
    assert client.choose_channel(customer(consent_whatsapp=True, consent_sms=True)) == Channel.WHATSAPP


def test_choose_channel_falls_back_to_sms():
    client = AppointmentReminderClient()
    assert client.choose_channel(customer(consent_whatsapp=False, consent_sms=True)) == Channel.SMS


def test_choose_channel_requires_consent():
    client = AppointmentReminderClient()
    with pytest.raises(ReminderError) as exc:
        client.choose_channel(customer(consent_whatsapp=False, consent_sms=False))
    assert exc.value.code == "CONSENT_MISSING"


def test_plan_reminders_skips_past_times_and_sorts():
    client = AppointmentReminderClient(policy=ReminderPolicy(hours_before=(48, 24, 3)))
    now = datetime(2026, 6, 17, 14, 0, tzinfo=TZ)
    planned = client.plan_reminders([appointment()], now=now)
    assert [item.metadata["hours_before"] for item in planned] == [24, 3]
    assert planned[0].send_at < planned[1].send_at


def test_quiet_hours_adjustment_marks_metadata():
    appt = appointment(starts_at=datetime(2026, 6, 18, 7, 0, tzinfo=TZ))
    client = AppointmentReminderClient(policy=ReminderPolicy(hours_before=(3,)))
    planned = client.plan_reminders([appt], now=datetime(2026, 6, 17, 8, 0, tzinfo=TZ))
    assert planned[0].send_at.hour == 20
    assert planned[0].send_at.minute == 30
    assert planned[0].metadata["quiet_hours_adjusted"] is True


def test_mock_send_returns_success():
    msg = ReminderMessage("a1", "c1", Channel.SMS, datetime(2026, 6, 18, 12, 0, tzinfo=TZ), "hello", {"phone_e164": "+972501234567"})
    response = AppointmentReminderClient(provider=Provider.MOCK).send_message(msg)
    assert response.success is True
    assert response.status_code == 202
    assert response.provider_message_id.startswith("mock-a1")


def test_async_send_uses_same_provider_result():
    msg = ReminderMessage("a1", "c1", Channel.SMS, datetime(2026, 6, 18, 12, 0, tzinfo=TZ), "hello", {"phone_e164": "+972501234567"})
    response = asyncio.run(AppointmentReminderClient(provider=Provider.MOCK).send_message_async(msg))
    assert response.success is True


def test_twilio_payload_uses_expected_endpoint_and_form_fields():
    calls = []

    def fake_request(url, method, headers, data):
        calls.append((url, method, headers, data))
        return 201, {"sid": "SM123"}

    msg = ReminderMessage("a1", "c1", Channel.SMS, datetime(2026, 6, 18, 12, 0, tzinfo=TZ), "שלום", {"phone_e164": "+972501234567"})
    client = AppointmentReminderClient(
        provider=Provider.TWILIO,
        credentials={"account_sid": "AC123", "from": "Clinic"},
        request_json=fake_request,
    )
    response = client.send_message(msg)
    assert response.success is True
    assert calls[0][0] == "https://api.twilio.com/2010-04-01/Accounts/AC123/Messages.json"
    assert parse_qs(calls[0][3].decode())["To"] == ["+972501234567"]


def test_whatsapp_cloud_payload_uses_graph_messages_endpoint():
    calls = []

    def fake_request(url, method, headers, data):
        calls.append((url, method, headers, json.loads(data.decode())))
        return 200, {"messages": [{"id": "wamid.1"}], "id": "wamid.1"}

    msg = ReminderMessage("a1", "c1", Channel.WHATSAPP, datetime(2026, 6, 18, 12, 0, tzinfo=TZ), "שלום", {"phone_e164": "+972501234567"})
    client = AppointmentReminderClient(
        provider=Provider.WHATSAPP_CLOUD,
        credentials={"token": "token", "phone_number_id": "123", "version": "v20.0"},
        request_json=fake_request,
    )
    response = client.send_message(msg)
    assert response.success is True
    assert calls[0][0] == "https://graph.facebook.com/v20.0/123/messages"
    assert calls[0][3]["to"] == "972501234567"


def test_no_show_tracker_stats_and_slots():
    tracker = NoShowTracker()
    tracker.record("a1", "c1", AppointmentStatus.ATTENDED, datetime(2026, 6, 18, 16, 0, tzinfo=TZ))
    tracker.record("a2", "c1", AppointmentStatus.NO_SHOW, datetime(2026, 6, 19, 16, 0, tzinfo=TZ))
    assert tracker.stats() == {"completed_or_missed": 2, "no_show_count": 1, "no_show_rate": 0.5}
    slots = tracker.suggest_rebooking_slots(datetime(2026, 6, 19, 16, 0, tzinfo=TZ), count=2)
    assert len(slots) == 2
    assert all(9 <= slot.hour < 17 for slot in slots)


def test_rebooking_message_is_non_promotional():
    appt = appointment()
    slots = [datetime(2026, 6, 19, 9, 0, tzinfo=TZ), datetime(2026, 6, 19, 13, 0, tzinfo=TZ)]
    body = AppointmentReminderClient().render_rebooking_message(appt, slots)
    assert "אפשר לקבוע מועד חדש" in body
    assert "הנחה" not in body


def test_appointment_from_dict_parses_customer_and_datetime():
    appt = appointment_from_dict(
        {
            "id": "a2",
            "starts_at": "2026-06-18T15:30:00+03:00",
            "business_name": "Clinic",
            "service_name": "Consultation",
            "customer": {"id": "c2", "name": "Yael", "phone": "0501234567", "preferred_language": "en", "consent_sms": True},
        }
    )
    assert appt.customer.phone_e164 == "+972501234567"
    assert appt.starts_at.hour == 15


def test_cli_validate_phone():
    result = CliRunner().invoke(cli, ["validate-phone", "050-123-4567"])
    assert result.exit_code == 0
    assert result.output.strip() == "+972501234567"


def test_cli_message_outputs_json():
    result = CliRunner().invoke(
        cli,
        [
            "message",
            "--name",
            "יעל כהן",
            "--phone",
            "050-123-4567",
            "--starts-at",
            "2026-06-18T15:30:00+03:00",
            "--business-name",
            "קליניקת אביב",
            "--service-name",
            "פגישת המשך",
            "--location",
            "רוטשילד 10, תל אביב",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["channel"] == "whatsapp"
    assert payload["metadata"]["phone_e164"] == "+972501234567"


def test_cli_plan_from_file(tmp_path):
    path = tmp_path / "appointments.json"
    path.write_text(
        json.dumps(
            [
                {
                    "id": "a1",
                    "starts_at": "2026-06-18T15:30:00+03:00",
                    "business_name": "Clinic",
                    "service_name": "Consultation",
                    "customer": {"id": "c1", "name": "Yael", "phone": "0501234567", "preferred_language": "en", "consent_sms": True},
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    result = CliRunner().invoke(cli, ["plan", "--input", str(path), "--now", "2026-06-16T08:00:00+03:00", "--hours-before", "24,3"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert len(payload) == 2
