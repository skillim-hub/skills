from __future__ import annotations

import json
from datetime import datetime

import pytest

import crm_integration_agent as client


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, headers, json, timeout):
        self.calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return self.response


def sample_thread(**overrides):
    contact = client.Contact(full_name="דנה כהן", phone="050-123-4567", email="DANA@EXAMPLE.CO.IL", company="כהן עיצוב")
    messages = [client.ConversationMessage("wa-1", "2026-02-18T09:44:00+02:00", "inbound", "אפשר לקבל הצעת מחיר?")]
    data = {
        "source_channel": "whatsapp",
        "source_thread_id": "wa-thread-1",
        "subject": "הצעת מחיר",
        "contact": contact,
        "messages": messages,
        "consent": client.ConsentRecord(marketing_opt_in=False, evidence="פנייה יזומה של לקוחה"),
        "business_purpose": "sales",
    }
    data.update(overrides)
    return client.ConversationThread(**data)


def test_package_import_exports_client():
    assert client.CRMIntegrationClient.__name__ == "CRMIntegrationClient"


def test_normalize_israeli_mobile():
    assert client.normalize_israeli_phone("050-123-4567") == "+972501234567"


def test_normalize_israeli_landline():
    assert client.normalize_israeli_phone("03-555-1234") == "+97235551234"


def test_normalize_already_e164():
    assert client.normalize_israeli_phone("+972501234567") == "+972501234567"


def test_normalize_00_prefix():
    assert client.normalize_israeli_phone("00972501234567") == "+972501234567"


def test_invalid_phone_raises():
    with pytest.raises(client.ValidationError):
        client.normalize_israeli_phone("123")


def test_canonical_email():
    assert client.canonical_email(" DANA@EXAMPLE.CO.IL ") == "dana@example.co.il"


def test_invalid_email_raises():
    with pytest.raises(client.ValidationError):
        client.canonical_email("not-an-email")


def test_normalize_channel_aliases():
    assert client.normalize_channel("wa") == "whatsapp"
    assert client.normalize_channel("gmail") == "email"
    assert client.normalize_channel("text") == "sms"
    assert client.normalize_channel("מסרון") == "sms"


def test_parse_and_format_il_date():
    dt = client.parse_il_date("18/02/2026")
    assert client.format_il_date(dt) == "18/02/2026"


def test_parse_datetime_localized():
    assert client.parse_datetime("18/02/2026 09:44:00").year == 2026


def test_dedupe_key_prefers_external_id():
    assert client.build_dedupe_key(client.Contact("דנה כהן", phone="0501234567", external_id="cust-1")) == "external:cust-1"


def test_dedupe_key_prefers_phone_without_external_id():
    assert client.build_dedupe_key(client.Contact("דנה כהן", phone="0501234567", email="dana@example.co.il")) == "phone:+972501234567"


def test_contact_requires_identifier():
    with pytest.raises(client.ValidationError):
        client.Contact("דנה כהן").normalized()


def test_marketing_without_opt_in_blocks():
    cfg = client.ProviderConfig(provider="hubspot", api_token="token", dry_run=True)
    integration = client.CRMIntegrationClient(cfg)
    with pytest.raises(client.ConsentRequiredError):
        integration.sync_thread(sample_thread(), marketing_action=True)


def test_marketing_with_opt_in_requires_evidence():
    cfg = client.ProviderConfig(provider="hubspot", api_token="token", dry_run=True)
    integration = client.CRMIntegrationClient(cfg)
    thread = sample_thread(consent=client.ConsentRecord(marketing_opt_in=True))
    with pytest.raises(client.ConsentRequiredError):
        integration.sync_thread(thread, marketing_action=True)


def test_marketing_with_evidence_allowed():
    cfg = client.ProviderConfig(provider="hubspot", api_token="token", dry_run=True)
    integration = client.CRMIntegrationClient(cfg)
    thread = sample_thread(consent=client.ConsentRecord(marketing_opt_in=True, evidence="אני מאשרת לקבל מבצעים"))
    result = integration.sync_thread(thread, marketing_action=True)
    assert result.dry_run is True


def test_redact_identity_number():
    assert "[REDACTED_ID]" in client.redact_sensitive_text("מספר תעודת זהות 123456789")


def test_redact_card_number():
    assert "[REDACTED_CARD]" in client.redact_sensitive_text("4580 1234 1234 1234")


def test_classify_business_purpose_sales():
    assert client.classify_business_purpose("אפשר לקבל הצעת מחיר?") == "sales"


def test_classify_business_purpose_support():
    assert client.classify_business_purpose("המוצר תקול ולא הגיע בזמן") == "support"


def test_opt_out_detection():
    assert client.is_opt_out_text("הסר")
    assert client.is_opt_out_text("STOP")


def test_explicit_opt_in_detection():
    assert client.is_explicit_opt_in_text("אני מאשרת לקבל עדכונים ומבצעים")


def test_dedupe_messages():
    messages = [
        client.ConversationMessage("a", "2026-02-18T09:00:00+02:00", "inbound", "one"),
        client.ConversationMessage("a", "2026-02-18T09:01:00+02:00", "inbound", "two"),
    ]
    assert len(client.dedupe_messages(messages)) == 1


def test_thread_normalizes_and_sorts_messages():
    messages = [
        client.ConversationMessage("b", "2026-02-18T10:00:00+02:00", "inbound", "second"),
        client.ConversationMessage("a", "2026-02-18T09:00:00+02:00", "inbound", "first"),
    ]
    thread = sample_thread(messages=messages).normalized()
    assert [m.source_message_id for m in thread.messages] == ["a", "b"]


def test_empty_message_rejected():
    thread = sample_thread(messages=[client.ConversationMessage("x", "2026-02-18T09:00:00+02:00", "inbound", "   ")])
    with pytest.raises(client.ValidationError):
        thread.normalized()


def test_monday_payload_contains_board_and_hebrew():
    cfg = client.ProviderConfig(provider="monday", api_token="token", dry_run=True, monday_board_id="123")
    payload = client.CRMIntegrationClient(cfg).build_payload(sample_thread())
    assert payload["variables"]["board"] == "123"
    assert "דנה כהן" == payload["variables"]["name"]


def test_hubspot_payload_properties():
    cfg = client.ProviderConfig(provider="hubspot", api_token="token", dry_run=True)
    payload = client.CRMIntegrationClient(cfg).build_payload(sample_thread())
    assert payload["properties"]["phone"] == "+972501234567"
    assert payload["properties"]["email"] == "dana@example.co.il"


def test_salesforce_payload_has_last_name_and_source():
    cfg = client.ProviderConfig(provider="salesforce", api_token="token", base_url="https://example.my.salesforce.com", dry_run=True)
    payload = client.CRMIntegrationClient(cfg).build_payload(sample_thread())
    assert payload["LastName"] == "כהן"
    assert payload["Source_Channel__c"] == "Whatsapp"


def test_dry_run_does_not_post():
    session = FakeSession(FakeResponse(200, {"id": "1"}))
    cfg = client.ProviderConfig(provider="hubspot", api_token="token", dry_run=True)
    result = client.CRMIntegrationClient(cfg, session=session).sync_thread(sample_thread())
    assert result.action == "planned_sync"
    assert session.calls == []


def test_live_post_extracts_hubspot_id():
    session = FakeSession(FakeResponse(201, {"id": "251"}))
    cfg = client.ProviderConfig(provider="hubspot", api_token="token", dry_run=False)
    result = client.CRMIntegrationClient(cfg, session=session).sync_thread(sample_thread())
    assert result.crm_object_id == "251"
    assert session.calls[0]["url"].endswith("/crm/objects/2026-03/contacts")


def test_live_post_extracts_monday_id():
    session = FakeSession(FakeResponse(200, {"data": {"create_item": {"id": "444"}}}))
    cfg = client.ProviderConfig(provider="monday", api_token="token", dry_run=False, monday_board_id="123")
    result = client.CRMIntegrationClient(cfg, session=session).sync_thread(sample_thread())
    assert result.crm_object_id == "444"


def test_handle_rate_limit():
    with pytest.raises(client.RateLimitError):
        client.handle_response(FakeResponse(429, {"message": "rate"}))


def test_handle_non_json_error():
    with pytest.raises(client.ProviderError) as exc:
        client.handle_response(FakeResponse(500, ValueError("bad json"), text="server down"))
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_async_dry_run():
    cfg = client.ProviderConfig(provider="hubspot", api_token="token", dry_run=True)
    result = await client.CRMIntegrationClient(cfg).async_sync_thread(sample_thread())
    assert result.dry_run is True
    assert result.message_count == 1


def test_load_thread_from_mapping():
    thread = client.load_thread_from_mapping({
        "contact": {"full_name": "דנה כהן", "phone": "0501234567"},
        "thread": {
            "source_channel": "wa",
            "source_thread_id": "t1",
            "subject": "hello",
            "messages": [{"id": "m1", "sent_at": "2026-02-18T09:00:00+02:00", "body": "שלום"}],
        },
    })
    assert thread.normalized().contact.phone == "+972501234567"


def test_write_audit_events(tmp_path):
    path = tmp_path / "audit.jsonl"
    client.write_audit_events(path, [{"a": "ב"}])
    assert json.loads(path.read_text(encoding="utf-8")) == {"a": "ב"}


def test_business_hours_sunday_true_saturday_false():
    assert client.is_business_hours_il(datetime(2026, 2, 22, 9, 0)) is True
    assert client.is_business_hours_il(datetime(2026, 2, 21, 9, 0)) is False


def test_direction_inference():
    assert client.classify_message_direction("0501234567", ["0501234567"]) == "outbound"
    assert client.classify_message_direction("0522223333", ["0501234567"]) == "inbound"


def test_idempotency_key():
    thread = sample_thread().normalized()
    key = client.make_idempotency_key(thread, thread.messages[0], "hubspot")
    assert key == "whatsapp:wa-thread-1:wa-1:hubspot"


def test_audit_template_has_required_keys():
    template = client.audit_template(crm_object_id="251", provider="hubspot")
    assert template["crm_object_id"] == "251"
    assert {"idempotency_key", "source_channel", "crm_provider", "status"}.issubset(template)


def test_from_env_sandbox_allows_missing_token(monkeypatch):
    monkeypatch.delenv("HUBSPOT_API_TOKEN", raising=False)
    integration = client.CRMIntegrationClient.from_env("hubspot", environment="sandbox")
    assert integration.config.dry_run is True


def test_from_env_production_requires_token(monkeypatch):
    monkeypatch.delenv("HUBSPOT_API_TOKEN", raising=False)
    monkeypatch.delenv("HUBSPOT_API_TOKEN_PRODUCTION", raising=False)
    with pytest.raises(client.ValidationError):
        client.CRMIntegrationClient.from_env("hubspot", environment="production")


def test_create_response_summary():
    cfg = client.ProviderConfig(provider="hubspot", api_token="token", dry_run=True)
    integration = client.CRMIntegrationClient(cfg)
    result = integration.sync_thread(sample_thread())
    assert integration.create_response_summary(result)["message_count"] == 1


def test_provider_config_current_api_versions():
    hubspot_cfg = client.ProviderConfig(provider="hubspot", api_token="token", dry_run=True)
    salesforce_cfg = client.ProviderConfig(provider="salesforce", api_token="token", base_url="https://example.my.salesforce.com", dry_run=True)
    assert client.CRMIntegrationClient(hubspot_cfg)._endpoint().endswith("/crm/objects/2026-03/contacts")
    assert client.CRMIntegrationClient(salesforce_cfg)._endpoint().endswith("/services/data/v67.0/sobjects/Lead")


def test_provider_config_allows_custom_salesforce_version():
    cfg = client.ProviderConfig(provider="salesforce", api_token="token", base_url="https://example.my.salesforce.com", salesforce_api_version="66.0", dry_run=True)
    assert client.CRMIntegrationClient(cfg)._endpoint().endswith("/services/data/v66.0/sobjects/Lead")
