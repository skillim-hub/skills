from __future__ import annotations

import asyncio
from datetime import date
import json
import os
from pathlib import Path
import subprocess
import sys

from emergency_contact_first_aid import (
    AsyncEmergencyInfoClient,
    DEFAULT_EMERGENCY_SERVICES,
    EmergencyInfoClient,
    make_starter_profile,
    normalize_israeli_phone,
    parse_local_date,
    profile_from_mapping,
    triage_first_aid,
    validate_profile,
)


ROOT = Path(__file__).resolve().parents[1]
SUBPROCESS_ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def sample_mapping():
    return {
        "id": "sample",
        "environment": "sandbox",
        "profile_name": "Dizengoff Studio - Front Desk",
        "last_reviewed": "04-06-2026",
        "site": {
            "address_line": "Dizengoff 100, entrance B, floor 2",
            "locality": "Tel Aviv-Yafo",
            "access_notes": "Intercom 22",
            "aed_location": "Ground floor",
            "first_aid_kit_location": "Reception",
        },
        "emergency_services": {
            "medical": "101",
            "police": "100",
            "fire_rescue": "102",
        },
        "contacts": [
            {"name": "Dana Cohen", "role": "Owner", "phone": "050-123-4567", "priority": 1},
            {"name": "Avi Levi", "role": "Maintenance", "phone": "052-222-3333", "priority": 2},
        ],
        "medical_notes": {
            "known_allergies": ["latex"],
            "regular_medications": [],
            "conditions_relevant_to_emergency": [],
            "mobility_needs": ["stairs difficult"],
        },
    }


def test_parse_hyphen_date():
    assert parse_local_date("04-06-2026").year == 2026


def test_parse_slash_date():
    assert parse_local_date("04/06/2026").month == 6


def test_parse_invalid_date():
    try:
        parse_local_date("2026-06-04")
    except ValueError as exc:
        assert "DD" in str(exc)
    else:
        raise AssertionError("expected failure")


def test_normalize_mobile_with_hyphens():
    assert normalize_israeli_phone("050-123-4567") == "+972501234567"


def test_normalize_mobile_without_hyphens():
    assert normalize_israeli_phone("0522223333") == "+972522223333"


def test_normalize_e164_kept():
    assert normalize_israeli_phone("+972501234567") == "+972501234567"


def test_normalize_00972():
    assert normalize_israeli_phone("00972501234567") == "+972501234567"


def test_short_code_supported():
    assert normalize_israeli_phone("101") == "101"


def test_invalid_phone_raises():
    try:
        normalize_israeli_phone("abc")
    except ValueError:
        assert True
    else:
        raise AssertionError("expected failure")


def test_profile_from_mapping():
    profile = profile_from_mapping(sample_mapping())
    assert profile.profile_name.startswith("Dizengoff")
    assert profile.site.locality == "Tel Aviv-Yafo"
    assert len(profile.contacts) == 2


def test_valid_profile_ok():
    result = validate_profile(sample_mapping(), today=date(2026, 6, 4))
    assert result.ok
    assert result.contacts_count == 2


def test_slash_date_profile_ok():
    data = sample_mapping()
    data["last_reviewed"] = "04/06/2026"
    assert validate_profile(data, today=date(2026, 6, 4)).ok


def test_missing_contact_fails():
    data = sample_mapping()
    data["contacts"] = []
    result = validate_profile(data, today=date(2026, 6, 4))
    assert not result.ok
    assert any("at least one" in item for item in result.errors)


def test_duplicate_priority_fails():
    data = sample_mapping()
    data["contacts"][1]["priority"] = 1
    result = validate_profile(data, today=date(2026, 6, 4))
    assert not result.ok
    assert any("unique" in item for item in result.errors)


def test_invalid_contact_phone_fails():
    data = sample_mapping()
    data["contacts"][0]["phone"] = "999"
    result = validate_profile(data, today=date(2026, 6, 4))
    assert not result.ok
    assert any("phone" in item for item in result.errors)


def test_stale_review_warns():
    data = sample_mapping()
    data["last_reviewed"] = "01-01-2026"
    result = validate_profile(data, today=date(2026, 6, 4))
    assert result.ok
    assert any("90 days" in item for item in result.warnings)


def test_future_review_warns():
    data = sample_mapping()
    data["last_reviewed"] = "10-06-2026"
    result = validate_profile(data, today=date(2026, 6, 4))
    assert result.ok
    assert any("future" in item for item in result.warnings)


def test_strict_privacy_detects_id_like_value():
    data = sample_mapping()
    data["notes"] = "ID 123456789"
    result = validate_profile(data, strict_privacy=True, today=date(2026, 6, 4))
    assert not result.ok
    assert any("ID" in item for item in result.errors)


def test_wallet_card_contains_key_fields():
    client = EmergencyInfoClient()
    profile = profile_from_mapping(sample_mapping())
    card = client.render_wallet_card(profile)
    assert "101" in card
    assert "Dana Cohen" in card
    assert "latex" in card


def test_redact_profile_removes_medical_notes():
    client = EmergencyInfoClient()
    redacted = client.redact_profile(sample_mapping())
    assert "medical_notes" not in redacted
    assert redacted["contacts"][0]["name"] == "Dana Cohen"


def test_sorted_contacts_by_priority():
    data = sample_mapping()
    data["contacts"][0]["priority"] = 2
    data["contacts"][1]["priority"] = 1
    client = EmergencyInfoClient()
    contacts = client.sorted_contacts(profile_from_mapping(data))
    assert contacts[0].name == "Avi Levi"


def test_cpr_no_breathing_red():
    result = triage_first_aid("cpr", conscious=False, breathing=False)
    assert result.priority == "red"
    assert any("chest" in item for item in result.actions)


def test_choking_infant_no_abdominal_thrusts():
    result = triage_first_aid("choking", age_group="infant")
    assert result.priority == "red"
    assert any("5 back blows" in item for item in result.actions)
    assert any("abdominal" in item for item in result.do_not)


def test_stroke_calls_101():
    result = triage_first_aid("stroke")
    assert result.emergency_call == "101"
    assert result.priority == "red"
    assert any("last-known-well" in item for item in result.actions)


def test_burn_has_cooling_instruction():
    result = triage_first_aid("burn")
    assert any("Cool" in item for item in result.actions)
    assert any("ice" in item for item in result.do_not)


def test_seizure_do_not_restrain():
    result = triage_first_aid("seizure")
    assert any("restrain" in item for item in result.do_not)


def test_unknown_scenario_safe_default():
    result = triage_first_aid("unknown")
    assert result.priority == "yellow"
    assert any("Call 101" in item for item in result.actions)


def test_make_starter_profile():
    profile = make_starter_profile("Shop", "Herzl 1", "Ramat Gan", "Noa", "050-111-2222")
    assert profile.profile_name == "Shop"
    assert profile.contacts[0].priority == 1


def test_client_save_and_load_roundtrip(tmp_path):
    client = EmergencyInfoClient()
    profile = profile_from_mapping(sample_mapping())
    out = tmp_path / "profile.json"
    client.save_profile(profile, out)
    loaded = client.load_profile(out)
    assert loaded.to_mapping() == profile.to_mapping()


def test_create_profile_returns_id_and_loads(tmp_path):
    client = EmergencyInfoClient()
    response = client.create_profile("Shop", "Herzl 1", "Ramat Gan", "Noa", "050-111-2222", tmp_path, "sandbox")
    assert response["ok"] is True
    loaded = client.load_profile_by_id(response["id"], tmp_path)
    assert loaded.profile_id == response["id"]


def test_async_client_validate():
    async def run():
        client = AsyncEmergencyInfoClient()
        return await client.validate_profile(sample_mapping(), today=date(2026, 6, 4))
    result = asyncio.run(run())
    assert result.ok


def test_argparse_validate_command(tmp_path):
    data_path = tmp_path / "profile.json"
    data_path.write_text(json.dumps(sample_mapping()), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "emergency_contact_first_aid_client.py"), "validate", str(data_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=SUBPROCESS_ENV,
    )
    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True


def test_argparse_create_then_validate_by_id(tmp_path):
    script = ROOT / "scripts" / "emergency_contact_first_aid_client.py"
    create = subprocess.run(
        [
            sys.executable,
            str(script),
            "create-profile",
            "--profile-name",
            "Shop",
            "--address",
            "Herzl 1",
            "--locality",
            "Ramat Gan",
            "--contact-name",
            "Noa",
            "--contact-phone",
            "050-111-2222",
            "--store-dir",
            str(tmp_path),
            "--env",
            "sandbox",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=SUBPROCESS_ENV,
    )
    assert create.returncode == 0
    profile_id = json.loads(create.stdout)["id"]
    validate = subprocess.run(
        [
            sys.executable,
            str(script),
            "validate",
            "--profile-id",
            profile_id,
            "--store-dir",
            str(tmp_path),
            "--env",
            "sandbox",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=SUBPROCESS_ENV,
    )
    assert validate.returncode == 0
    assert json.loads(validate.stdout)["ok"] is True


def test_argparse_triage_command():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "emergency_contact_first_aid_client.py"), "triage", "--scenario", "choking", "--age-group", "adult"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=SUBPROCESS_ENV,
    )
    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["scenario"] == "choking"
    assert payload["priority"] == "red"


def test_numbers_command_plain():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "emergency_contact_first_aid_client.py"), "numbers"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=SUBPROCESS_ENV,
    )
    assert completed.returncode == 0
    assert "medical: 101" in completed.stdout


def test_import_installable_module():
    import emergency_contact_first_aid
    assert hasattr(emergency_contact_first_aid, "EmergencyInfoClient")


def test_default_services_include_united_hatzalah_and_mda_text_access():
    assert DEFAULT_EMERGENCY_SERVICES["united_hatzalah"] == "1221"
    assert DEFAULT_EMERGENCY_SERVICES["mda_sms_whatsapp"] == "052-7000-101"


def test_example_profile_includes_verified_text_and_volunteer_numbers():
    example = json.loads((ROOT / "templates" / "emergency-profile.example.json").read_text(encoding="utf-8"))
    assert example["emergency_services"]["united_hatzalah"] == "1221"
    assert example["emergency_services"]["mda_sms_whatsapp"] == "052-7000-101"
