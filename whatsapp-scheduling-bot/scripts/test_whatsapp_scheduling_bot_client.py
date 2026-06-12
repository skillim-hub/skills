from __future__ import annotations

import pytest

import whatsapp_scheduling_bot as bot_client


class FakeTransport:
    def __init__(self):
        self.calls = []

    def post(self, url, headers, json_body, timeout):
        self.calls.append({"url": url, "headers": headers, "json": json_body, "timeout": timeout})
        return {
            "messaging_product": "whatsapp",
            "contacts": [{"input": json_body["to"], "wa_id": json_body["to"]}],
            "messages": [{"id": f"wamid.{len(self.calls)}"}],
        }


def make_client():
    transport = FakeTransport()
    client = bot_client.WhatsAppSchedulingClient("token", "123", transport=transport)
    return client, transport


def make_appointment(client=None):
    if client is None:
        client, _ = make_client()
    return client.create_appointment(
        customer_name="דנה",
        customer_phone="054-123-4567",
        service_name="ייעוץ ראשוני",
        start_at="2026-06-18T10:30:00+03:00",
        duration_minutes=45,
        business_name="קליניקת הדוגמה",
        staff_name="נועה",
        price_ils=250,
        location="רחוב הרצל 10, תל אביב",
    )


def test_normalize_mobile_local():
    assert bot_client.normalize_israeli_phone("054-123-4567") == "972541234567"


def test_normalize_mobile_plus_972():
    assert bot_client.normalize_israeli_phone("+972 54 123 4567") == "972541234567"


def test_normalize_mobile_plain_972():
    assert bot_client.normalize_israeli_phone("972541234567") == "972541234567"


def test_normalize_landline():
    assert bot_client.normalize_israeli_phone("03-123-4567") == "97231234567"


def test_reject_short_phone():
    with pytest.raises(bot_client.PhoneValidationError):
        bot_client.normalize_israeli_phone("541234567")


def test_reject_letters_phone():
    with pytest.raises(bot_client.PhoneValidationError):
        bot_client.normalize_israeli_phone("054-abc-4567")


def test_display_israeli_phone():
    assert bot_client.display_israeli_phone("+972 54 123 4567") == "054-123-4567"


def test_price_format_integer():
    assert bot_client.format_price_ils(250) == "₪250"


def test_price_format_decimal():
    assert bot_client.format_price_ils(250.5) == "₪250.5"


def test_date_format_dd_mm_yyyy():
    dt = bot_client.parse_datetime("2026-06-18T10:30:00+03:00")
    assert bot_client.format_israeli_date(dt) == "18/06/2026"


def test_time_format_hh_mm():
    dt = bot_client.parse_datetime("2026-06-18T10:30:00+03:00")
    assert bot_client.format_israeli_time(dt) == "10:30"


def test_create_appointment_normalizes_phone_and_end_time():
    client, _ = make_client()
    appointment = make_appointment(client)
    assert appointment.customer_phone == "972541234567"
    assert appointment.end_at.hour == 11
    assert appointment.end_at.minute == 15


def test_confirmation_text_contains_hebrew_date_price_and_options():
    client, _ = make_client()
    appointment = make_appointment(client)
    text = client.build_confirmation_text(appointment)
    assert "18/06/2026" in text
    assert "₪250" in text
    assert "לאישור יש להשיב 1" in text


def test_reminder_text_contains_location():
    client, _ = make_client()
    appointment = make_appointment(client)
    text = client.build_reminder_text(appointment)
    assert "רחוב הרצל 10" in text
    assert "לאישור הגעה" in text


def test_template_parameters_count():
    client, _ = make_client()
    appointment = make_appointment(client)
    assert len(client.build_template_parameters(appointment)) == 7


def test_template_payload_language_he():
    client, _ = make_client()
    payload = client.template_payload("054-123-4567", "appointment_confirmation_he", ["דנה"], language="he")
    assert payload["template"]["language"]["code"] == "he"
    assert payload["to"] == "972541234567"


def test_text_payload_preview_false():
    client, _ = make_client()
    payload = client.text_payload("054-123-4567", "שלום")
    assert payload["text"]["preview_url"] is False
    assert payload["type"] == "text"


def test_send_text_uses_transport():
    client, transport = make_client()
    result = client.send_text("054-123-4567", "שלום")
    assert result.success is True
    assert result.provider_message_id == "wamid.1"
    assert transport.calls[0]["json"]["text"]["body"] == "שלום"


def test_send_template_uses_transport():
    client, transport = make_client()
    result = client.send_template("054-123-4567", "appointment_confirmation_he", ["דנה"])
    assert result.provider_message_id == "wamid.1"
    assert transport.calls[0]["json"]["template"]["name"] == "appointment_confirmation_he"


def test_dry_run_does_not_use_transport():
    client, transport = make_client()
    result = client.send_text("054-123-4567", "שלום", dry_run=True)
    assert result.provider_message_id == "dry-run"
    assert transport.calls == []


def test_due_reminders_returns_due_only():
    client, _ = make_client()
    appointment = make_appointment(client)
    due = client.due_reminders("2026-06-17T10:31:00+03:00")
    assert (appointment, appointment.reminders[0]) in due
    assert all(reminder.offset_minutes != 120 for _, reminder in due)


def test_send_due_reminders_sets_idempotency():
    client, transport = make_client()
    appointment = make_appointment(client)
    results1 = client.send_due_reminders("2026-06-17T10:31:00+03:00")
    results2 = client.send_due_reminders("2026-06-17T10:32:00+03:00")
    assert len(results1) == 1
    assert len(results2) == 0
    assert len(transport.calls) == 1
    assert appointment.reminders[0].status == "sent"


def test_cancelled_appointment_has_no_due_reminders():
    client, _ = make_client()
    appointment = make_appointment(client)
    client.update_appointment_status(appointment.appointment_id, "cancelled")
    assert client.due_reminders("2026-06-17T10:31:00+03:00") == []
    assert appointment.reminders[0].status == "skipped"


def test_reschedule_recalculates_reminders():
    client, _ = make_client()
    appointment = make_appointment(client)
    client.send_due_reminders("2026-06-17T10:31:00+03:00", dry_run=True)
    client.reschedule_appointment(appointment.appointment_id, "2026-06-19T13:00:00+03:00")
    assert appointment.start_at.day == 19
    assert all(reminder.status == "pending" for reminder in appointment.reminders)


def test_invalid_status_raises():
    client, _ = make_client()
    appointment = make_appointment(client)
    with pytest.raises(bot_client.AppointmentValidationError):
        client.update_appointment_status(appointment.appointment_id, "bad")


def test_webhook_verify_success():
    assert bot_client.WhatsAppSchedulingClient.verify_webhook("subscribe", "secret", "123", "secret") == (200, "123")


def test_webhook_verify_failure():
    assert bot_client.WhatsAppSchedulingClient.verify_webhook("subscribe", "bad", "123", "secret") == (403, "Forbidden")


def test_parse_webhook_text_message():
    client, _ = make_client()
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [{"wa_id": "972541234567", "profile": {"name": "דנה"}}],
                            "messages": [
                                {
                                    "from": "972541234567",
                                    "id": "wamid.abc",
                                    "timestamp": "1718700000",
                                    "type": "text",
                                    "text": {"body": "אפשר תור?"},
                                }
                            ],
                        }
                    }
                ]
            }
        ]
    }
    events = client.parse_webhook_payload(payload)
    assert events[0].text == "אפשר תור?"
    assert events[0].customer_name == "דנה"


def test_classify_reply_confirm():
    client, _ = make_client()
    assert client.classify_reply("1") == "confirm"


def test_classify_reply_cancel():
    client, _ = make_client()
    assert client.classify_reply("בטלי לי") == "cancel"


def test_classify_reply_opt_out():
    client, _ = make_client()
    assert client.classify_reply("הסר") == "opt_out"


def test_classify_reply_human_sensitive():
    client, _ = make_client()
    assert client.classify_reply("ייעוץ רפואי דחוף") == "human"


def test_business_time_rejects_friday_by_default():
    assert bot_client.is_business_time("2026-06-19T10:00:00+03:00") is False


def test_business_time_allows_friday_when_enabled():
    assert bot_client.is_business_time("2026-06-19T10:00:00+03:00", allow_friday=True) is True


def test_business_time_rejects_saturday_by_default():
    assert bot_client.is_business_time("2026-06-20T10:00:00+03:00") is False


def test_business_time_rejects_after_hours():
    assert bot_client.is_business_time("2026-06-18T22:00:00+03:00") is False


@pytest.mark.asyncio
async def test_async_send_text():
    client, _ = make_client()
    async_client = bot_client.AsyncWhatsAppSchedulingClient(client)
    result = await async_client.send_text("054-123-4567", "שלום")
    assert result.success is True


@pytest.mark.asyncio
async def test_async_send_due_reminders():
    client, _ = make_client()
    make_appointment(client)
    async_client = bot_client.AsyncWhatsAppSchedulingClient(client)
    results = await async_client.send_due_reminders("2026-06-17T10:31:00+03:00")
    assert len(results) == 1


def test_hebrew_b_prefix_drops_definite_article():
    assert bot_client.prefix_hebrew_b("העסק לדוגמה") == "בעסק לדוגמה"
    assert bot_client.prefix_hebrew_b("קליניקת הדוגמה") == "בקליניקת הדוגמה"


def test_default_api_version_is_web_validated():
    assert bot_client.DEFAULT_API_VERSION == "v25.0"
    client, _ = make_client()
    assert client.api_version == "v25.0"
