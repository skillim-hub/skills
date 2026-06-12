from __future__ import annotations

import json
import datetime as dt
from pathlib import Path

import pytest
from typer.testing import CliRunner

import healthcare_appointment_booker as client
from healthcare_appointment_booker.cli import app


def make_request(**overrides):
    data = dict(
        hmo="maccabi",
        service="skin mole check",
        city="Rishon LeZion",
        date_from="2026-07-01",
        date_to="2026-07-31",
        age_group="adult",
        urgency="routine",
        referral_status="unknown",
    )
    data.update(overrides)
    return client.build_request(**data)


def test_parse_iso_date():
    assert client.parse_date("2026-07-01") == dt.date(2026, 7, 1)


def test_parse_hebrew_slash_date():
    assert client.parse_date("01/07/2026") == dt.date(2026, 7, 1)


def test_parse_hebrew_dash_date():
    assert client.parse_date("01-07-2026") == dt.date(2026, 7, 1)


def test_invalid_date_rejected():
    with pytest.raises(ValueError):
        client.parse_date("07.01.2026")


def test_normalize_hmo_hebrew():
    assert client.normalize_hmo("כללית") == client.HMO.CLALIT


def test_normalize_hmo_english():
    assert client.normalize_hmo("Leumit") == client.HMO.LEUMIT


def test_unsupported_hmo_rejected():
    with pytest.raises(ValueError):
        client.normalize_hmo("private")


def test_build_request_rejects_reverse_dates():
    with pytest.raises(ValueError):
        make_request(date_from="2026-08-01", date_to="2026-07-01")


def test_authorization_required_for_helper():
    with pytest.raises(ValueError):
        make_request(patient_authorized_helper=False)


def test_dermatology_classification():
    assert client.classify_specialty("rash and skin mole") == "dermatology"


def test_pediatric_same_day_classification():
    req = make_request(service="child fever and ear pain", age_group="child", urgency="same_day")
    plan = client.HealthcareAppointmentBookerClient().plan(req)
    assert plan.specialty == "pediatrics"
    assert client.Channel.URGENT_CARE in plan.recommended_channels


def test_chest_pain_escalates():
    req = make_request(service="cardiologist for chest pain and shortness of breath", urgency="routine")
    plan = client.HealthcareAppointmentBookerClient().plan(req)
    assert plan.priority == "urgent_escalation"
    assert plan.recommended_channels == (client.Channel.EMERGENCY,)


def test_infant_fever_escalates():
    req = make_request(service="fever", age_group="infant")
    plan = client.HealthcareAppointmentBookerClient().plan(req)
    assert plan.specialty == "emergency"


def test_imaging_requires_order_or_verification():
    req = make_request(service="MRI knee", hmo="meuhedet", referral_status="has_referral")
    plan = client.HealthcareAppointmentBookerClient().plan(req)
    assert plan.specialty == "imaging"
    assert "order" in plan.referral_required


def test_lab_classification():
    req = make_request(service="blood test fasting", hmo="clalit", referral_status="has_referral")
    plan = client.HealthcareAppointmentBookerClient().plan(req)
    assert plan.specialty == "lab"
    assert any("lab order" in item.lower() for item in plan.instructions)


def test_admin_form_17_route():
    req = make_request(service="Form 17 approval for hospital outpatient", hmo="leumit")
    plan = client.HealthcareAppointmentBookerClient().plan(req)
    assert plan.specialty == "admin"
    assert client.Channel.ADMIN_APPROVALS in plan.recommended_channels


def test_sensitive_id_detection():
    assert client.contains_sensitive_secret("my id is 123456782")


def test_sensitive_password_detection():
    assert client.contains_sensitive_secret("password is secret123")


def test_safe_text_not_sensitive():
    assert not client.contains_sensitive_secret("dermatology in Haifa next month")


def test_no_adapter_requires_manual_action():
    req = make_request()
    result = client.HealthcareAppointmentBookerClient().book(req)
    assert result.status == "manual_action_required"


def test_emergency_booking_returns_escalated():
    req = make_request(service="sudden vision loss")
    result = client.HealthcareAppointmentBookerClient().book(req)
    assert result.status == "escalated"


def test_rank_options_prefers_city_and_accessibility():
    req = make_request(accessibility=("wheelchair",))
    later = client.AppointmentOption(
        provider_name="A",
        clinic_name="Clinic A",
        city="Tel Aviv",
        starts_at=dt.datetime(2026, 7, 2, 9, 0),
        channel=client.Channel.OFFICIAL_APP,
    )
    preferred = client.AppointmentOption(
        provider_name="B",
        clinic_name="Clinic B",
        city="Rishon LeZion",
        starts_at=dt.datetime(2026, 7, 5, 9, 0),
        channel=client.Channel.OFFICIAL_APP,
        accessibility=("wheelchair",),
    )
    ranked = client.HealthcareAppointmentBookerClient().rank_options(req, [later, preferred])
    assert ranked[0] is preferred


def test_in_memory_adapter_search_and_book():
    option = client.AppointmentOption(
        provider_name="Demo Doctor",
        clinic_name="Demo Clinic",
        city="Rishon LeZion",
        starts_at=dt.datetime(2026, 7, 3, 10, 0),
        channel=client.Channel.OFFICIAL_APP,
    )
    adapter = client.InMemoryAppointmentAdapter([option])
    req = make_request()
    booker = client.HealthcareAppointmentBookerClient(adapter)
    results = booker.search(req)
    assert results
    booked = booker.book(req, results[0])
    assert booked.status == "confirmed_demo"
    assert booked.confirmation_number.startswith("LOCAL-")


def test_in_memory_adapter_blocks_missing_referral():
    option = client.AppointmentOption(
        provider_name="Demo Doctor",
        clinic_name="Demo Clinic",
        city="Rishon LeZion",
        starts_at=dt.datetime(2026, 7, 3, 10, 0),
        channel=client.Channel.OFFICIAL_APP,
        requires_referral=True,
    )
    adapter = client.InMemoryAppointmentAdapter([option])
    req = make_request(referral_status="no_referral")
    result = client.HealthcareAppointmentBookerClient(adapter).book(req, option)
    assert result.status == "blocked"


def test_to_json_contains_hebrew():
    req = make_request()
    plan = client.HealthcareAppointmentBookerClient().plan(req)
    assert "שלום" in plan.to_json()


def test_render_hebrew_text():
    req = make_request(hmo="clalit", service="בדיקת דם", city="חיפה")
    plan = client.HealthcareAppointmentBookerClient().plan(req)
    rendered = client.render_text_plan(plan, hebrew=True)
    assert "תוכנית קביעת תור" in rendered


def test_plan_from_mapping():
    plan = client.plan_from_mapping(
        {
            "hmo": "maccabi",
            "service": "orthopedic knee pain",
            "city": "Ashdod",
            "date_from": "2026-07-01",
            "date_to": "2026-07-20",
        }
    )
    assert plan.specialty == "orthopedics"


@pytest.mark.asyncio
async def test_async_plan():
    req = make_request()
    plan = await client.AsyncHealthcareAppointmentBookerClient().plan(req)
    assert plan.request.hmo == client.HMO.MACCABI


@pytest.mark.asyncio
async def test_async_manual_book():
    req = make_request()
    result = await client.AsyncHealthcareAppointmentBookerClient().book(req)
    assert result.status == "manual_action_required"


def test_hebrew_date_format():
    assert client.format_he_date(dt.date(2026, 7, 1)) == "01/07/2026"


def test_unknown_service_warning():
    req = make_request(service="unclear custom service")
    plan = client.HealthcareAppointmentBookerClient().plan(req)
    assert plan.specialty == "unknown"
    assert plan.warnings


def test_ophthalmology_sudden_vision_loss_escalates():
    req = make_request(service="ophthalmology for sudden vision loss")
    plan = client.HealthcareAppointmentBookerClient().plan(req)
    assert plan.priority == "urgent_escalation"


def test_cli_create_show_chain(tmp_path: Path):
    runner = CliRunner()
    store = tmp_path / "plans.json"
    result = runner.invoke(
        app,
        [
            "create",
            "--hmo", "maccabi",
            "--service", "skin mole check",
            "--city", "Rishon LeZion",
            "--date-from", "2026-07-01",
            "--date-to", "2026-07-31",
            "--store", str(store),
        ],
    )
    assert result.exit_code == 0
    created = json.loads(result.output)
    plan_id = created["id"]
    result2 = runner.invoke(app, ["show", "--id", plan_id, "--store", str(store), "--format", "json"])
    assert result2.exit_code == 0
    shown = json.loads(result2.output)
    assert shown["id"] == plan_id


def test_compatibility_root_client_module_import():
    import healthcare_appointment_booker_client as root_client

    assert root_client.HealthcareAppointmentBookerClient is client.HealthcareAppointmentBookerClient


def test_docs_include_web_validated_vat_and_maccabi_caveat():
    root = Path(__file__).resolve().parents[1]
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    he = (root / "SKILL_HE.md").read_text(encoding="utf-8")
    verification = (root / "references" / "verification-log.md").read_text(encoding="utf-8")
    assert "Israeli VAT is 18%" in skill
    assert "שיעור המע״מ בישראל הוא 18%" in he
    assert "same-specialty continuity" in skill
    assert "רצף טיפולי במכבי" in he
    assert "✓✓" in verification
