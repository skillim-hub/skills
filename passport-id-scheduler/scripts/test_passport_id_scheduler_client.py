from __future__ import annotations
import asyncio, json, subprocess, sys
from datetime import date, time
from pathlib import Path
import pytest

import passport_id_scheduler_client as client

def test_valid_teudat_zehut(): assert client.validate_teudat_zehut("123456782").valid
def test_teudat_zehut_rejects_all_zero(): assert client.validate_teudat_zehut("000000000").code == "ID_ALL_ZERO"
def test_teudat_zehut_rejects_letters(): assert client.validate_teudat_zehut("123A").code == "ID_NOT_DIGITS"
def test_teudat_zehut_rejects_too_long(): assert client.validate_teudat_zehut("1234567890").code == "ID_TOO_LONG"
def test_phone_normalizes_mobile():
    r = client.validate_israeli_phone("052-123-4567")
    assert r.valid and r.normalized == "0521234567" and r.kind == "mobile"
def test_phone_normalizes_international(): assert client.normalize_phone("+972 52 123 4567") == "0521234567"
def test_phone_rejects_short_code(): assert client.validate_israeli_phone("*3450").code == "PHONE_SHORT_CODE"
def test_phone_rejects_bad_prefix(): assert not client.validate_israeli_phone("0111234567").valid
def test_validate_email(): assert client.validate_email("person@example.co.il") and not client.validate_email("person.example.co.il")
def test_parse_service_alias_english(): assert client.parse_service("passport renewal") == client.ServiceType.PASSPORT_RENEWAL
def test_parse_service_alias_hebrew(): assert client.parse_service("חידוש דרכון") == client.ServiceType.PASSPORT_RENEWAL
def test_classify_service_text(): assert client.classify_service("Need first passport for child") == client.ServiceType.PASSPORT_NEW
def test_document_type_inferred():
    assert client.parse_document_type(None, "id_renewal") == client.DocumentType.ID_CARD
    assert client.parse_document_type(None, "passport_renewal") == client.DocumentType.PASSPORT
def test_mask_teudat_zehut(): assert client.mask_teudat_zehut("123456782") == "*****6782"
def test_date_display(): assert client.display_date(date(2026, 8, 15)) == "15/08/2026"
def test_invalid_date_window_raises():
    with pytest.raises(client.InvalidDateWindow):
        client.validate_date_window(date(2026, 9, 1), date(2026, 8, 1))
def test_service_checklist_passport(): assert "Current passport if available" in client.service_checklist("passport_renewal")
def test_hebrew_checklist_contains_natural_terms():
    joined = " ".join(client.hebrew_checklist("id_first", minor=True, business=True))
    assert "תעודת זהות" in joined and "אפוטרופוס" in joined and "רואה חשבון" in joined
def test_official_links_include_gov(): assert any("gov.il" in link["url"] for link in client.official_service_links("passport renewal"))
def test_official_source_detection():
    assert client.is_official_source("https://www.gov.il/he/departments/foo")
    assert client.is_official_source("https://govisit.gov.il/")
    assert not client.is_official_source("https://example.com/slots")

def test_build_plan_valid():
    request = client.AppointmentRequest(
        service="passport_renewal",
        applicants=[client.ApplicantProfile("Example", "123456782", "0521234567")],
        preference=client.AppointmentPreference("Tel Aviv-Yafo", date(2026,8,1), date(2026,8,31)),
    )
    plan = client.PassportIdSchedulerClient().build_plan(request)
    assert plan.valid and plan.service == client.ServiceType.PASSPORT_RENEWAL and "Ramat Gan" in plan.nearby_cities

def test_build_plan_invalid_applicant_returns_errors():
    request = client.AppointmentRequest(service="passport_renewal", applicants=[client.ApplicantProfile("Bad", "111", "0521234567")])
    plan = client.PassportIdSchedulerClient().build_plan(request)
    assert not plan.valid and plan.errors

def test_minor_plan_adds_warning():
    request = client.AppointmentRequest(service="id_first", applicants=[client.ApplicantProfile("Minor", "123456782", "0521234567", is_minor=True)])
    assert any("Minor workflow" in w for w in client.PassportIdSchedulerClient().build_plan(request).warnings)

def test_address_update_warns_online_first():
    assert any("online self-service" in w for w in client.PassportIdSchedulerClient().build_plan(client.AppointmentRequest(service="address_update")).warnings)

def test_rank_candidates_exact_city_wins():
    scheduler = client.PassportIdSchedulerClient()
    request = client.AppointmentRequest(service="passport_renewal", preference=client.AppointmentPreference("Haifa", date(2026,8,1), date(2026,8,31)))
    candidates = [
        client.AppointmentCandidate("Bureau B", "Krayot", date(2026,8,5), time(9), service="passport_renewal", source_url="https://govisit.gov.il/"),
        client.AppointmentCandidate("Bureau A", "Haifa", date(2026,8,10), time(9), service="passport_renewal", source_url="https://govisit.gov.il/"),
    ]
    ranked = scheduler.rank_candidates(request, candidates)
    assert ranked[0].city == "Haifa" and ranked[0].score is not None

def test_rank_candidates_deduplicates():
    scheduler = client.PassportIdSchedulerClient()
    candidate = client.AppointmentCandidate("Bureau", "Jerusalem", date(2026,8,10), time(9), service="passport_renewal", source_url="https://govisit.gov.il/")
    assert len(scheduler.rank_candidates(client.AppointmentRequest(service="passport_renewal"), [candidate, candidate])) == 1

def test_rank_candidates_rejects_unsafe_source():
    candidate = client.AppointmentCandidate("Unofficial", "Tel Aviv-Yafo", date(2026,8,10), time(9), source_url="https://example.com/slot")
    with pytest.raises(client.UnsafeSource):
        client.PassportIdSchedulerClient().rank_candidates(client.AppointmentRequest(service="passport_renewal"), [candidate])

def test_candidate_from_dict():
    c = client.candidate_from_dict({"city":"Jerusalem","date":"2026-08-15","start_time":"09:30","service":"id_renewal"})
    assert c.date == date(2026,8,15) and c.start_time == time(9,30)

def test_request_from_dict():
    r = client.request_from_dict({"service":"passport_renewal","preferred_city":"Jerusalem","date_from":"2026-08-01"})
    assert r.preference.preferred_city == "Jerusalem" and r.preference.date_from == date(2026,8,1)

def test_create_ics_contains_event():
    ics = client.PassportIdSchedulerClient().create_ics("Passport appointment", date(2026,8,15), time(9,30), location="Bureau")
    assert "BEGIN:VCALENDAR" in ics and "SUMMARY:Passport appointment" in ics and "DTSTART:20260815T093000" in ics

def test_write_ics(tmp_path: Path):
    target = tmp_path / "appointment.ics"
    written = client.PassportIdSchedulerClient().write_ics(target, "ID appointment", date(2026,8,15), time(10))
    assert written.exists() and "ID appointment" in written.read_text()

def test_async_client_build_plan():
    async def run():
        plan = await client.AsyncPassportIdSchedulerClient().build_plan(client.AppointmentRequest(service="passport_renewal"))
        assert plan.valid
    asyncio.run(run())

def test_plan_to_markdown():
    plan = client.PassportIdSchedulerClient().build_plan(client.AppointmentRequest(service="passport_renewal"))
    assert "Checklist:" in client.plan_to_markdown(plan)

def test_plan_to_markdown_hebrew():
    plan = client.PassportIdSchedulerClient().build_plan(client.AppointmentRequest(service="id_renewal"))
    text = client.plan_to_markdown(plan, lang="he")
    assert "שירות" in text and "תעודת זהות" in text

def test_cli_validate_id():
    cli = Path(__file__).with_name("passport_id_scheduler_cli.py")
    result = subprocess.run([sys.executable, str(cli), "validate-id", "123456782"], text=True, capture_output=True, check=True)
    assert json.loads(result.stdout)["valid"] is True

def test_cli_checklist_hebrew():
    cli = Path(__file__).with_name("passport_id_scheduler_cli.py")
    result = subprocess.run([sys.executable, str(cli), "checklist", "--service", "id_first", "--minor", "--lang", "he"], text=True, capture_output=True, check=True)
    assert "אפוטרופוס" in result.stdout


def test_create_request_record_has_stable_id():
    request = client.AppointmentRequest(
        service="passport_renewal",
        applicants=[client.ApplicantProfile("Example", "123456782", "0521234567")],
    )
    record = client.PassportIdSchedulerClient().create_request_record(request, environment="sandbox")
    assert record["id"].startswith("req_") and record["environment"] == "sandbox"


def test_request_to_dict_uses_iso_for_storage():
    request = client.AppointmentRequest(service="id_renewal", preference=client.AppointmentPreference(date_from=date(2026, 8, 1)))
    assert client.request_to_dict(request)["preference"]["date_from"] == "2026-08-01"


def test_cli_create_and_show_request(tmp_path: Path):
    cli = Path(__file__).with_name("passport_id_scheduler_cli.py")
    target = tmp_path / "request.json"
    created = subprocess.run(
        [
            sys.executable,
            str(cli),
            "create-request",
            "--service",
            "passport_renewal",
            "--city",
            "Jerusalem",
            "--output",
            str(target),
            "--env",
            "sandbox",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    request_id = json.loads(created.stdout)["id"]
    shown = subprocess.run(
        [sys.executable, str(cli), "show-request", "--input", str(target), "--request-id", request_id],
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(shown.stdout)["id"] == request_id
