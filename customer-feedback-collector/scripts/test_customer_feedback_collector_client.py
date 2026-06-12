from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

import customer_feedback_collector as C

ROOT = Path(__file__).resolve().parent
CLI_PATH = ROOT / "customer_feedback_collector_cli.py"


def business(**overrides):
    base = dict(
        display_name="קליניקת הדר",
        google_place_id="ChIJexample",
        facebook_page_url="https://www.facebook.com/clinic.hadar",
        zap_url="https://www.zap.co.il/clientcard.aspx?siteid=123",
        easy_url="https://easy.co.il/page/123",
        midrag_url="https://www.midrag.co.il/business/123",
        b144_url="https://www.b144.co.il/b144_sip/123",
        custom_review_url="https://example.co.il/review",
        private_feedback_url="https://example.co.il/private-feedback",
    )
    base.update(overrides)
    return C.BusinessProfile(**base)


def contact(**overrides):
    base = dict(full_name="דנה כהן", phone="050-123-4567", email="dana@example.co.il")
    base.update(overrides)
    return C.Contact(**base)


def test_normalize_local_mobile():
    assert C.normalize_israeli_phone("050-123-4567") == "+972501234567"


def test_normalize_already_e164():
    assert C.normalize_israeli_phone("+972501234567") == "+972501234567"


def test_normalize_972_without_plus():
    assert C.normalize_israeli_phone("972501234567") == "+972501234567"


def test_invalid_phone_raises():
    with pytest.raises(C.InvalidPhoneNumber):
        C.normalize_israeli_phone("12345")


def test_mobile_detection_true():
    assert C.is_probable_israeli_mobile("0501234567") is True


def test_mobile_detection_false_for_landline():
    assert C.is_probable_israeli_mobile("03-1234567") is False


def test_google_review_url():
    url = C.build_review_url(C.ReviewPlatform.GOOGLE, business(google_place_id="ChIJ abc"))
    assert url.startswith("https://www.google.com/maps/search/?api=1")
    assert "query_place_id=ChIJ%20abc" in url
    assert "query=" in url


def test_facebook_review_url_appends_reviews():
    url = C.build_review_url("facebook", business())
    assert url.endswith("/reviews/")


def test_missing_google_place_id_raises():
    with pytest.raises(C.MissingReviewDestination):
        C.build_review_url("google", business(google_place_id=None))


def test_render_whatsapp_contains_hebrew_url_and_optout():
    msg = C.render_message(contact(), business(), platform="google", channel="whatsapp")
    assert "שלום דנה" in msg.body
    assert "www.google.com/maps/search/" in msg.body
    assert "להסרה" in msg.body
    assert msg.to == "+972501234567"


def test_render_email_has_subject_and_approval_text():
    msg = C.render_message(contact(), business(), platform="google", channel="email")
    assert msg.subject
    assert "לא תפורסם המלצה" in msg.body
    assert msg.to == "dana@example.co.il"


def test_render_sms_is_compact():
    msg = C.render_message(contact(), business(), platform="custom", channel="sms")
    assert msg.body.startswith("דנה")
    assert "להסרה" in msg.body


def test_private_first_uses_private_url():
    msg = C.render_message(contact(rating=2), business(), platform="google", channel="whatsapp")
    assert msg.review_url == "https://example.co.il/private-feedback"
    assert "פרטי" in msg.body


def test_classify_rating():
    assert C.classify_rating(5) == "promoter"
    assert C.classify_rating(4) == "passive"
    assert C.classify_rating(2) == "detractor"
    assert C.classify_rating(9, scale_max=10) == "promoter"


def test_detect_opt_out_hebrew_and_english():
    assert C.detect_opt_out("הסר") is True
    assert C.detect_opt_out("please STOP") is True
    assert C.detect_opt_out("תודה רבה") is False


def test_validate_message_flags_no_hebrew():
    msg = C.Message(channel=C.Channel.WHATSAPP, to="+972501234567", body="Please review us. unsubscribe")
    issues = C.validate_message(msg)
    assert any(issue.code == "NoHebrew" for issue in issues)


def test_validate_message_flags_missing_unsubscribe():
    msg = C.Message(channel=C.Channel.WHATSAPP, to="+972501234567", body="שלום דנה, אפשר להשאיר חוות דעת?")
    issues = C.validate_message(msg)
    assert any(issue.code == "UnsubscribeMissing" for issue in issues)


def test_validate_message_flags_incentive():
    msg = C.Message(
        channel=C.Channel.SMS,
        to="+972501234567",
        body="שלום, קבלו 10 ₪ הנחה על דירוג 5 כוכבים. להסרה: הסר",
    )
    issues = C.validate_message(msg)
    assert any(issue.code == "IncentiveRisk" for issue in issues)


def test_validate_message_flags_url_first():
    msg = C.Message(channel=C.Channel.WHATSAPP, to="+972501234567", body="https://x.co/rev שלום להסרה: הסר")
    issues = C.validate_message(msg)
    assert any(issue.code == "UrlFirst" for issue in issues)


def test_choose_channel_prefers_whatsapp_for_mobile():
    assert C.choose_channel(contact()) == C.Channel.WHATSAPP


def test_choose_channel_email_when_no_phone():
    assert C.choose_channel(contact(phone=None)) == C.Channel.EMAIL


def test_plan_campaign_planned_and_skipped():
    contacts = [
        contact(full_name="דנה כהן"),
        contact(full_name="יוסי לוי", phone=None, email=None),
        contact(full_name="נועה", consent=False),
    ]
    plan = C.plan_campaign(contacts, business(), platform="google", channel="whatsapp")
    summary = C.summarize_plan(plan)
    assert summary["statuses"]["planned"] == 1
    assert summary["statuses"]["skipped"] == 2


def test_plan_campaign_suppression():
    plan = C.plan_campaign([contact()], business(), platform="google", channel="whatsapp", suppression_keys={"+972501234567"})
    assert plan[0].status == C.DeliveryStatus.SKIPPED
    assert plan[0].issues[0].code == "Suppressed"


def test_read_contacts_csv(tmp_path):
    path = tmp_path / "contacts.csv"
    path.write_text(
        "full_name,phone,email,consent,preferred_channel,tags,rating\n"
        "דנה כהן,0501234567,dana@example.co.il,true,whatsapp,clinic;vip,5\n",
        encoding="utf-8",
    )
    rows = C.read_contacts_csv(path)
    assert rows[0].full_name == "דנה כהן"
    assert rows[0].preferred_channel == C.Channel.WHATSAPP
    assert rows[0].tags == ("clinic", "vip")
    assert rows[0].rating == 5


def test_export_plan_json_preserves_hebrew(tmp_path):
    plan = C.plan_campaign([contact()], business(), platform="google", channel="whatsapp")
    output = tmp_path / "plan.json"
    text = C.export_plan_json(plan, output)
    assert "דנה" in text
    assert "דנה" in output.read_text(encoding="utf-8")


def test_quiet_time_friday_afternoon():
    assert C.is_quiet_time("2026-06-05T14:00:00+03:00") is True


def test_quiet_time_sunday_morning_safe():
    assert C.is_quiet_time("2026-06-07T10:00:00+03:00") is False


def test_next_safe_time_from_saturday_is_sunday():
    nxt = C.next_safe_send_time("2026-06-06T10:00:00+03:00")
    assert nxt.weekday() == 6
    assert nxt.hour == 9
    assert nxt.minute == 30


def test_client_send_sync_dry_run():
    msg = C.render_message(contact(), business(), platform="google", channel="whatsapp")
    client = C.FeedbackCollectorClient(business(), platform="google")
    result = client.send_sync([msg], dry_run=True)[0]
    assert result.status == C.DeliveryStatus.DRY_RUN
    assert result.message_id.startswith("dry_")


def test_client_send_sync_with_mock_transport():
    def transport(channel, payload):
        return {"status": "queued", "message_id": "abc123", "echo_to": payload["to"]}

    msg = C.render_message(contact(), business(), platform="google", channel="whatsapp")
    client = C.FeedbackCollectorClient(business(), platform="google", sync_transport=transport)
    result = client.send_sync([msg], dry_run=False)[0]
    assert result.status == C.DeliveryStatus.QUEUED
    assert result.message_id == "abc123"


def test_client_send_sync_failure_is_retryable():
    def transport(channel, payload):
        raise RuntimeError("429")

    msg = C.render_message(contact(), business(), platform="google", channel="whatsapp")
    client = C.FeedbackCollectorClient(business(), platform="google", sync_transport=transport)
    result = client.send_sync([msg], dry_run=False)[0]
    assert result.status == C.DeliveryStatus.FAILED
    assert result.retryable is True


def test_client_send_async_with_mock_transport():
    async def transport(channel, payload):
        return {"status": "accepted", "message_id": "async123"}

    msg = C.render_message(contact(), business(), platform="google", channel="whatsapp")
    client = C.FeedbackCollectorClient(business(), platform="google", async_transport=transport)
    result = asyncio.run(client.send_async([msg], dry_run=False))[0]
    assert result.status == C.DeliveryStatus.QUEUED
    assert result.message_id == "async123"


def test_cli_sample_message():
    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "sample-message",
            "--business-name",
            "קליניקת הדר",
            "--google-place-id",
            "ChIJexample",
            "--channel",
            "whatsapp",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    assert "שלום דנה" in result.stdout
    assert "www.google.com/maps/search/" in result.stdout


def test_cli_validate_message():
    result = subprocess.run(
        [sys.executable, str(CLI_PATH), "validate-message", "hello"],
        text=True,
        capture_output=True,
        check=True,
    )
    assert "NoHebrew" in result.stdout


def test_cli_plan_writes_json(tmp_path):
    contacts_csv = tmp_path / "contacts.csv"
    contacts_csv.write_text("full_name,phone,email,consent\nדנה כהן,0501234567,dana@example.co.il,true\n", encoding="utf-8")
    output = tmp_path / "plan.json"
    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "plan",
            "--contacts",
            str(contacts_csv),
            "--business-name",
            "קליניקת הדר",
            "--google-place-id",
            "ChIJexample",
            "--platform",
            "google",
            "--channel",
            "whatsapp",
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    assert output.exists()
    assert '"planned"' in result.stdout
    assert "דנה" in output.read_text(encoding="utf-8")


def test_cli_next_safe_time():
    result = subprocess.run(
        [sys.executable, str(CLI_PATH), "next-safe-time", "2026-06-06T10:00:00+03:00"],
        text=True,
        capture_output=True,
        check=True,
    )
    assert "2026-06-07T09:30:00" in result.stdout
