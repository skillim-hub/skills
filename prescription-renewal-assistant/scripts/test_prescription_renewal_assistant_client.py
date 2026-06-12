from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from prescription_renewal_assistant import (
    AssistantError,
    AsyncPrescriptionRenewalClient,
    ConsentMissingError,
    CredentialDataError,
    Fulfillment,
    PrescriptionRenewalClient,
    RecommendedPath,
    RenewalCase,
    Urgency,
    build_doctor_message,
    choose_recommended_path,
    classify_urgency,
    expense_record,
    format_ddmmyyyy,
    format_israeli_date,
    load_case_from_store,
    load_case_json,
    parse_date,
    pharmacy_checklist,
    redact_sensitive_text,
    save_case_json,
    store_case,
    triage_case,
)


def make_case(**kwargs):
    data = {
        "kupat_cholim": "Clalit",
        "medication_name": "as shown in portal",
        "supply_days": 10,
        "consent_confirmed": True,
    }
    data.update(kwargs)
    return RenewalCase(**data)


def test_routine_urgency():
    assert classify_urgency(7) == Urgency.ROUTINE


def test_soon_urgency():
    assert classify_urgency(6) == Urgency.SOON


def test_urgent_urgency():
    assert classify_urgency(2) == Urgency.URGENT


def test_emergency_urgency():
    assert classify_urgency(10, symptoms_or_distress=True) == Urgency.EMERGENCY


def test_negative_supply_rejected():
    with pytest.raises(AssistantError):
        make_case(supply_days=-1)


def test_negative_repeats_rejected():
    with pytest.raises(AssistantError):
        make_case(repeats_left=-1)


def test_invalid_date_format_rejected():
    with pytest.raises(AssistantError):
        make_case(valid_until="2026-06-22")


def test_slash_date_accepted():
    case = make_case(valid_until="22/06/2026")
    assert parse_date(case.valid_until) == date(2026, 6, 22)


def test_invalid_calendar_date_rejected():
    with pytest.raises(AssistantError):
        make_case(valid_until="31/02/2026")


def test_missing_consent_rejected_for_other_adult():
    with pytest.raises(ConsentMissingError):
        make_case(patient_alias="parent", consent_confirmed=False)


def test_child_allowed_with_guardian_context():
    case = make_case(patient_alias="child", consent_confirmed=False)
    assert case.patient_alias == "child"


def test_password_keyword_rejected():
    with pytest.raises(CredentialDataError):
        make_case(notes="password is secret")


def test_hebrew_code_keyword_rejected():
    with pytest.raises(CredentialDataError):
        make_case(notes="קוד חד פעמי 123456")


def test_expired_prescription_goes_to_doctor():
    case = make_case(repeats_left=3, valid_until="01-05-2026")
    assert choose_recommended_path(case, today=date(2026, 6, 18)) == RecommendedPath.DOCTOR_RENEWAL


def test_zero_repeats_goes_to_doctor():
    result = triage_case(make_case(repeats_left=0))
    assert result.recommended_path == RecommendedPath.DOCTOR_RENEWAL
    assert "No repeats remain." in result.warnings


def test_not_active_goes_to_doctor():
    result = triage_case(make_case(active_visible=False))
    assert result.recommended_path == RecommendedPath.DOCTOR_RENEWAL


def test_urgent_no_repeats_escalates():
    result = triage_case(make_case(supply_days=1, repeats_left=0))
    assert result.urgency == Urgency.URGENT
    assert result.recommended_path == RecommendedPath.URGENT_ESCALATION


def test_emergency_path():
    result = triage_case(make_case(symptoms_or_distress=True))
    assert result.recommended_path == RecommendedPath.EMERGENCY_CARE


def test_delivery_action_present():
    result = triage_case(make_case(preferred_fulfillment=Fulfillment.DELIVERY))
    assert any("delivery availability" in action for action in result.next_actions)


def test_pickup_action_present():
    result = triage_case(make_case(preferred_fulfillment=Fulfillment.PICKUP))
    assert any("branch stock" in action for action in result.next_actions)


def test_cold_chain_warning_present():
    result = triage_case(make_case(needs_cold_chain=True))
    assert "Confirm refrigerated handling before delivery." in result.warnings


def test_controlled_warning_present():
    result = triage_case(make_case(controlled_medication=True))
    assert any("controlled" in warning for warning in result.warnings)


def test_travel_action_present():
    result = triage_case(make_case(travel_date="28/06/2026"))
    assert any("28/06/2026" in action for action in result.next_actions)


def test_doctor_message_english():
    case = make_case(repeats_left=0, strength_form="10 mg tablets", last_dispensed="01-06-2026")
    draft = build_doctor_message(case, language="en")
    assert draft.subject == "Prescription renewal request"
    assert "10 mg tablets" in draft.body
    assert "no repeats left" in draft.body


def test_doctor_message_hebrew():
    case = make_case(repeats_left=0, strength_form="10 מ״ג טבליות", last_dispensed="01/06/2026")
    draft = build_doctor_message(case, language="he")
    assert draft.subject == "בקשה לחידוש מרשם"
    assert "ימי מלאי שנותרו" in draft.body


def test_pharmacy_checklist_delivery_and_price():
    result = pharmacy_checklist(pharmacy="Super-Pharm", fulfillment=Fulfillment.DELIVERY)
    assert any("delivery" in question.lower() for question in result.questions)
    assert any("₪" in question for question in result.questions)


def test_pharmacy_checklist_cold_chain():
    result = pharmacy_checklist(needs_cold_chain=True)
    assert any("refrigeration" in question for question in result.questions)
    assert result.warnings


def test_pharmacy_checklist_controlled():
    result = pharmacy_checklist(controlled_medication=True)
    assert any("controlled" in warning for warning in result.warnings)


def test_redact_id_and_phone():
    redacted = redact_sensitive_text("ID 123456789 phone 050-1234567")
    assert "123456789" not in redacted
    assert "050-1234567" not in redacted
    assert "050-***4567" in redacted


def test_expense_record_format():
    record = expense_record(vendor="pharmacy", amount_nis=42.9, paid_on="18/06/2026")
    assert record["amount"] == "₪42.90"
    assert record["contains_medical_detail"] is False


def test_save_and_load_case(tmp_path):
    case = make_case(preferred_fulfillment=Fulfillment.PICKUP)
    path = tmp_path / "case.json"
    save_case_json(case, path)
    loaded = load_case_json(path)
    assert loaded.preferred_fulfillment == Fulfillment.PICKUP


def test_store_and_load_case(tmp_path):
    case = make_case()
    store = tmp_path / "store.json"
    case_id = store_case(case, store_path=store, case_id="RX-TEST")
    loaded = load_case_from_store(case_id, store_path=store)
    assert loaded.medication_name == case.medication_name


def test_sync_client_triage():
    result = PrescriptionRenewalClient().triage(make_case())
    assert result.urgency == Urgency.ROUTINE


def test_sync_client_create_and_load(tmp_path):
    client = PrescriptionRenewalClient()
    store = tmp_path / "cases.json"
    case_id = client.create_case(make_case(), store_path=store, case_id="RX-ABC")
    assert client.load_case(case_id, store_path=store).kupat_cholim == "Clalit"


def test_sync_client_redact():
    assert "*********" in PrescriptionRenewalClient().redact("123456789")


def test_async_client_triage():
    async def run():
        return await AsyncPrescriptionRenewalClient().triage(make_case(supply_days=2))

    assert asyncio.run(run()).urgency == Urgency.URGENT


def test_async_client_message():
    async def run():
        return await AsyncPrescriptionRenewalClient().doctor_message(make_case(), language="en")

    assert "Prescription" in asyncio.run(run()).subject


def test_date_formatters():
    value = parse_date("04/06/2026")
    assert format_ddmmyyyy(value) == "04-06-2026"
    assert format_israeli_date(value) == "04/06/2026"


def test_holiday_or_weekend_risk_moves_to_soon():
    assert triage_case(make_case(supply_days=10), holiday_or_weekend_risk=True).urgency == Urgency.SOON


def test_active_delivery_recommends_pharmacy_verification():
    case = make_case(
        repeats_left=2,
        valid_until="30-08-2026",
        preferred_fulfillment=Fulfillment.DELIVERY,
        active_visible=True,
    )
    assert choose_recommended_path(case, today=date(2026, 6, 18)) == RecommendedPath.PHARMACY_VERIFICATION


def test_package_import_exports():
    import prescription_renewal_assistant as pra

    assert pra.RenewalCase is RenewalCase
    assert callable(pra.triage_case)


def test_cli_create_message_chain(tmp_path):
    store = tmp_path / "cases.json"
    create_cmd = [
        sys.executable,
        "-m",
        "prescription_renewal_assistant.cli",
        "create",
        "--kupat-cholim",
        "Maccabi",
        "--medication-name",
        "as shown in portal",
        "--supply-days",
        "5",
        "--repeats-left",
        "0",
        "--consent-confirmed",
        "--store",
        str(store),
    ]
    created = subprocess.run(create_cmd, check=True, text=True, capture_output=True)
    payload = json.loads(created.stdout)
    assert payload["case_id"].startswith("RX-")

    msg_cmd = [
        sys.executable,
        "-m",
        "prescription_renewal_assistant.cli",
        "message",
        "--case-id",
        payload["case_id"],
        "--language",
        "en",
        "--store",
        str(store),
    ]
    message = subprocess.run(msg_cmd, check=True, text=True, capture_output=True)
    assert "Prescription renewal request" in message.stdout


def test_cli_checklist_from_case(tmp_path):
    store = tmp_path / "cases.json"
    client = PrescriptionRenewalClient()
    case_id = client.create_case(
        make_case(preferred_fulfillment=Fulfillment.DELIVERY, pharmacy="Be"),
        store_path=store,
        case_id="RX-CHECK",
    )
    cmd = [
        sys.executable,
        "-m",
        "prescription_renewal_assistant.cli",
        "checklist",
        "--case-id",
        case_id,
        "--store",
        str(store),
    ]
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    payload = json.loads(result.stdout)
    assert any("Be" in question for question in payload["questions"])


def test_docs_include_web_validated_corrections():
    root = Path(__file__).resolve().parents[1]
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    hebrew = (root / "SKILL_HE.md").read_text(encoding="utf-8")
    verification = (root / "references" / "verification-log.md").read_text(encoding="utf-8")
    assert "Be and Newpharm must be verified" in skill
    assert "לא אומתה תמיכה ישראלית עדכנית" in hebrew
    assert "18%" in verification
    assert "final ✗" in verification
