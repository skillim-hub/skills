from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

import event_webinar_promoter as ewp


ROOT = Path(__file__).resolve().parents[1]


def sample(**overrides):
    data = ewp.sample_event()
    data.update(overrides)
    return data


def plan(**overrides):
    return ewp.EventWebinarPromoterClient().plan(sample(**overrides))


def test_parse_ddmmyyyy_valid():
    assert ewp.parse_ddmmyyyy("24-06-2026").isoformat() == "2026-06-24"


def test_display_date_slashes():
    assert ewp.display_date_slashes("24-06-2026") == "24/06/2026"


def test_parse_ddmmyyyy_invalid_format():
    with pytest.raises(ewp.EventValidationError) as exc:
        ewp.parse_ddmmyyyy("2026-06-24")
    assert exc.value.code == "INVALID_DATE_FORMAT"


def test_parse_hhmm_valid():
    assert ewp.parse_hhmm("20:00").hour == 20


def test_parse_hhmm_invalid():
    with pytest.raises(ewp.EventValidationError) as exc:
        ewp.parse_hhmm("8pm")
    assert exc.value.code == "INVALID_TIME_FORMAT"


def test_missing_event_name_raises():
    with pytest.raises(ewp.EventValidationError) as exc:
        ewp.EventWebinarPromoterClient().plan(sample(event_name=""))
    assert exc.value.code == "MISSING_EVENT_NAME"


def test_missing_audience_raises():
    with pytest.raises(ewp.EventValidationError) as exc:
        ewp.EventWebinarPromoterClient().plan(sample(audience=""))
    assert exc.value.code == "MISSING_AUDIENCE"


def test_timezone_is_asia_jerusalem():
    campaign = plan()
    assert campaign.timezone == "Asia/Jerusalem"
    assert campaign.starts_at.tzinfo is not None
    assert campaign.starts_at.isoformat().startswith("2026-06-24T20:00:00")


def test_end_time_uses_duration():
    campaign = plan(duration_minutes=90)
    assert campaign.ends_at.hour == 21
    assert campaign.ends_at.minute == 30


def test_runway_free_webinar_is_14_days():
    assert plan(price_nis=0, format="webinar").runway_days == 14


def test_runway_paid_workshop_is_30_days():
    assert plan(format="workshop", city="חיפה", price_nis=290).runway_days == 30


def test_channels_include_email_and_whatsapp_for_opt_in():
    campaign = plan(consent_status="opt_in")
    assert "email" in campaign.recommended_channels
    assert "whatsapp" in campaign.recommended_channels


def test_channels_avoid_direct_when_unknown():
    campaign = plan(consent_status="unknown")
    assert "organic_social" in campaign.recommended_channels
    assert "partner_posts" in campaign.recommended_channels


def test_paid_event_flags_terms_and_vat():
    campaign = plan(price_nis=290, format="workshop", city="חיפה", vat_included=None, cancellation_terms=None)
    joined = " ".join(campaign.compliance_flags)
    assert "cancellation" in joined
    assert "VAT" in joined


def test_unknown_consent_flag():
    campaign = plan(consent_status="unknown")
    assert any("Avoid promotional" in flag for flag in campaign.compliance_flags)


def test_saturday_warning():
    campaign = plan(date="27-06-2026")
    assert any("SATURDAY_EVENT" in warning for warning in campaign.warnings)


def test_friday_afternoon_warning():
    campaign = plan(date="26-06-2026", time="15:00")
    assert any("FRIDAY_AFTERNOON" in warning for warning in campaign.warnings)


def test_hebrew_copy_contains_price_and_slash_date():
    campaign = plan(price_nis=290, vat_included=True)
    landing = campaign.copy["landing_page"]
    assert "24/06/2026" in landing
    assert "₪290" in landing
    assert "כולל מע״מ" in landing


def test_copy_has_opt_in_whatsapp_reminder():
    campaign = plan()
    assert "להסרה" in campaign.copy["whatsapp_reminder_opt_in_only"]


def test_utm_builder_adds_params():
    url = ewp.build_utm_url(
        "https://example.co.il/register?x=1",
        source="Facebook Ads",
        medium="Paid Social",
        campaign="Pricing Webinar",
        content="Launch Post",
    )
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    assert params["x"] == ["1"]
    assert params["utm_source"] == ["facebook_ads"]
    assert params["utm_medium"] == ["paid_social"]
    assert params["utm_campaign"] == ["pricing_webinar"]
    assert params["utm_content"] == ["launch_post"]


def test_utm_invalid_url_raises():
    with pytest.raises(ewp.EventValidationError) as exc:
        ewp.build_utm_url("example/register", source="x", medium="y", campaign="z")
    assert exc.value.code == "INVALID_URL"


def test_plan_generates_utm_links_when_url_exists():
    campaign = plan(registration_url="https://example.co.il/register")
    assert campaign.utm_links
    assert all("utm_source=" in url for url in campaign.utm_links.values())


def test_plan_without_url_has_no_utm_links():
    campaign = plan(registration_url=None)
    assert campaign.utm_links == {}


def test_reminders_are_sorted():
    campaign = plan()
    stamps = [reminder.send_at for reminder in campaign.reminders]
    assert stamps == sorted(stamps)


def test_reminders_include_two_hour_whatsapp_for_opt_in():
    campaign = plan(consent_status="opt_in")
    labels = [reminder.label for reminder in campaign.reminders]
    assert "2h" in labels


def test_reminders_skip_two_hour_whatsapp_without_opt_in():
    campaign = plan(consent_status="unknown")
    labels = [reminder.label for reminder in campaign.reminders]
    assert "2h" not in labels


def test_checklist_mentions_vat_for_paid():
    items = plan(price_nis=500).checklist
    assert any("VAT" in item for item in items)


def test_campaign_to_json_roundtrip():
    campaign = plan()
    data = json.loads(campaign.to_json())
    assert data["event"]["event_name"] == sample()["event_name"]
    assert data["timezone"] == "Asia/Jerusalem"


def test_load_and_dump_plan(tmp_path):
    event_path = tmp_path / "event.json"
    out_path = tmp_path / "plan.json"
    event_path.write_text(json.dumps(sample(), ensure_ascii=False), encoding="utf-8")
    payload = ewp.load_event(event_path)
    campaign = ewp.EventWebinarPromoterClient().plan(payload)
    ewp.dump_plan(campaign, out_path)
    assert out_path.exists()
    assert json.loads(out_path.read_text(encoding="utf-8"))["runway_days"] == 14


@pytest.mark.asyncio
async def test_async_plan():
    client = ewp.EventWebinarPromoterClient()
    campaign = await client.aplan(sample())
    assert campaign.event.event_name == sample()["event_name"]


@pytest.mark.asyncio
async def test_async_create(tmp_path):
    client = ewp.EventWebinarPromoterClient()
    response = await client.acreate(sample(), store_dir=tmp_path)
    assert response.event_id.startswith("evt_")
    assert Path(response.event_path).exists()


def test_create_and_load_created(tmp_path):
    client = ewp.EventWebinarPromoterClient()
    response = client.create(sample(), store_dir=tmp_path)
    loaded = client.load_created(response.event_id, store_dir=tmp_path)
    assert loaded["event_name"] == sample()["event_name"]


def test_validate_returns_missing_url_warning():
    warnings = ewp.EventWebinarPromoterClient().validate(sample(registration_url=None))
    assert any("MISSING_REGISTRATION_URL" in warning for warning in warnings)


def test_unsupported_format_raises():
    with pytest.raises(ewp.EventValidationError) as exc:
        ewp.EventWebinarPromoterClient().plan(sample(format="party"))
    assert exc.value.code == "UNSUPPORTED_FORMAT"


def test_capacity_claim_line_when_capacity_exists():
    campaign = plan(format="workshop", city="תל אביב", capacity=18)
    assert "18" in campaign.copy["landing_page"]


def test_price_text_free():
    profile = ewp.EventProfile.from_mapping(sample(price_nis=0))
    assert ewp.price_text(profile) == "ללא עלות"


def test_cli_sample_outputs_json():
    result = subprocess.run([sys.executable, "-m", "event_webinar_promoter.cli", "sample"], cwd=ROOT, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    assert data["format"] == "webinar"


def test_cli_create_then_plan_by_event_id(tmp_path):
    event_path = tmp_path / "event.json"
    store = tmp_path / "store"
    event_path.write_text(json.dumps(sample(), ensure_ascii=False), encoding="utf-8")

    create_result = subprocess.run(
        [sys.executable, "-m", "event_webinar_promoter.cli", "create", str(event_path), "--store", str(store)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    created = json.loads(create_result.stdout)
    assert created["event_id"].startswith("evt_")

    plan_result = subprocess.run(
        [sys.executable, "-m", "event_webinar_promoter.cli", "plan", "--event-id", created["event_id"], "--store", str(store)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(plan_result.stdout)
    assert data["event"]["event_name"] == sample()["event_name"]


def test_cli_validate(tmp_path):
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps(sample(), ensure_ascii=False), encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "event_webinar_promoter.cli", "validate", str(event_path)], cwd=ROOT, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    assert data["valid"] is True


def test_underscored_script_client_exists():
    assert (ROOT / "scripts" / "event_webinar_promoter_client.py").exists()
    assert not (ROOT / "scripts" / "event-webinar-promoter-client.py").exists()


def test_validated_tax_constants():
    assert ewp.STANDARD_VAT_RATE == 0.18
    assert ewp.STANDARD_VAT_RATE_EFFECTIVE_DATE == "2025-01-01"
    assert ewp.EXEMPT_DEALER_2026_TURNOVER_CEILING_NIS == 122_833
