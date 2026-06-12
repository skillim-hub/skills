from __future__ import annotations

import datetime as dt
import json

import pytest
from click.testing import CliRunner

from driving_license_booker import (
    Applicant,
    AsyncDrivingLicenseBookerClient,
    BookingKind,
    BookingStatus,
    DrivingLicenseBookerClient,
    LicenseClass,
    TimeWindow,
)
from driving_license_booker.cli import main


VALID_ID = "039456785"


def applicant(**kwargs):
    data = {"full_name": "Dana Levi", "national_id": VALID_ID, "phone": "0501234567", "license_number": "1234567"}
    data.update(kwargs)
    return Applicant(**data)


def test_validate_israeli_id_true():
    assert DrivingLicenseBookerClient().validate_israeli_id(VALID_ID)


def test_validate_israeli_id_false():
    assert not DrivingLicenseBookerClient().validate_israeli_id("123456789")


def test_normalize_israeli_id_pads_zero():
    assert DrivingLicenseBookerClient().normalize_israeli_id("39456785") == VALID_ID


def test_normalize_israeli_id_rejects_bad_checksum():
    with pytest.raises(ValueError):
        DrivingLicenseBookerClient().normalize_israeli_id("123456789")


def test_normalize_phone_local():
    assert DrivingLicenseBookerClient().normalize_phone("050-123-4567") == "0501234567"


def test_normalize_phone_country_code():
    assert DrivingLicenseBookerClient().normalize_phone("+972501234567") == "0501234567"


def test_normalize_phone_rejects_invalid():
    with pytest.raises(ValueError):
        DrivingLicenseBookerClient().normalize_phone("12345")


def test_format_local_date():
    assert DrivingLicenseBookerClient().format_local_date(dt.date(2026, 8, 31)) == "31/08/2026"


def test_business_day_deadline_skips_weekend():
    assert DrivingLicenseBookerClient().business_day_deadline(dt.date(2026, 6, 4), 2) == dt.date(2026, 6, 8)


def test_build_service_links_contains_validated_urls():
    links = DrivingLicenseBookerClient().build_service_links()
    assert links["license_renewal"] == "https://www.gov.il/he/service/driving_license_renewal"
    assert links["license_payment"] == "https://ecom.gov.il/voucherspa/input/209"
    assert links["practical_test_payment"] == "https://ecom.gov.il/voucherspa/input/427"
    assert links["licensing_bureau_appointment"].startswith("https://govisit.gov.il/")


def test_build_renewal_payload():
    payload = DrivingLicenseBookerClient().build_renewal_payload(applicant(), expiry_date="2026-08-31")
    assert payload["workflow"] == "license_renewal"
    assert payload["applicant"]["phone"] == "0501234567"


def test_readiness_with_blockers():
    client = DrivingLicenseBookerClient(now=dt.datetime(2026, 6, 4, tzinfo=dt.timezone.utc))
    result = client.check_renewal_readiness(
        applicant=applicant(license_number=None),
        expiry_date=dt.date(2026, 8, 31),
        has_paid_fee=False,
        medical_declaration_required=True,
        medical_declaration_done=False,
    )
    assert result["ready"] is False
    assert len(result["blockers"]) == 2
    assert result["warnings"] == ["license number is missing"]


def test_readiness_expired_warning():
    client = DrivingLicenseBookerClient(now=dt.datetime(2026, 6, 4, tzinfo=dt.timezone.utc))
    result = client.check_renewal_readiness(
        applicant=applicant(),
        expiry_date=dt.date(2026, 1, 1),
        has_paid_fee=True,
    )
    assert "license is already expired" in result["warnings"]


def test_bureau_payload_requires_window():
    with pytest.raises(ValueError):
        DrivingLicenseBookerClient().build_bureau_appointment_payload(applicant(), [])


def test_bureau_payload_accessibility():
    payload = DrivingLicenseBookerClient().build_bureau_appointment_payload(
        applicant(), [TimeWindow(dt.date(2026, 7, 15), city="Haifa")], service_city="Haifa", accessibility_needed=True
    )
    assert payload["accessibility_needed"] is True
    assert payload["windows"][0]["city"] == "Haifa"


def test_practical_payload_requires_teacher():
    with pytest.raises(ValueError):
        DrivingLicenseBookerClient().build_practical_test_payload(
            applicant(), [TimeWindow(dt.date(2026, 7, 20))], teacher_name=" ", teacher_phone="0521111111"
        )


def test_practical_payload_teacher_phone_validation():
    with pytest.raises(ValueError):
        DrivingLicenseBookerClient().build_practical_test_payload(
            applicant(), [TimeWindow(dt.date(2026, 7, 20))], teacher_name="Avi", teacher_phone="123"
        )


def test_practical_payload_ok():
    payload = DrivingLicenseBookerClient().build_practical_test_payload(
        applicant(license_class=LicenseClass.B),
        [TimeWindow(dt.date(2026, 7, 20), city="Rishon LeZion")],
        teacher_name="Avi",
        teacher_phone="0521111111",
        pickup_city="Rishon LeZion",
    )
    assert payload["teacher"]["phone"] == "0521111111"
    assert payload["vehicle_class"] == "B"


def test_create_get_persist(tmp_path):
    state = tmp_path / "state.json"
    client = DrivingLicenseBookerClient(state_path=state)
    response = client.create_booking({"kind": BookingKind.LICENSE_RENEWAL.value, "applicant": applicant().to_dict()})
    loaded = DrivingLicenseBookerClient(state_path=state).get_booking(response.request_id)
    assert loaded.request_id == response.request_id


def test_cancel_booking(tmp_path):
    client = DrivingLicenseBookerClient(state_path=tmp_path / "state.json")
    response = client.create_booking({"kind": BookingKind.LICENSE_RENEWAL.value, "applicant": applicant().to_dict()})
    cancelled = client.cancel_booking(response.request_id, "customer request")
    assert cancelled.status == BookingStatus.CANCELLED.value


def test_list_bookings_status_filter(tmp_path):
    client = DrivingLicenseBookerClient(state_path=tmp_path / "state.json")
    first = client.create_booking({"kind": BookingKind.LICENSE_RENEWAL.value, "applicant": applicant().to_dict()})
    client.create_booking({"kind": BookingKind.BUREAU_APPOINTMENT.value, "applicant": applicant().to_dict()})
    client.cancel_booking(first.request_id)
    cancelled = client.list_bookings(status=BookingStatus.CANCELLED)
    assert len(cancelled) == 1
    assert cancelled[0].request_id == first.request_id


def test_serialize_and_from_json(tmp_path):
    client = DrivingLicenseBookerClient(state_path=tmp_path / "state.json")
    response = client.create_booking({"kind": BookingKind.LICENSE_RENEWAL.value, "applicant": applicant().to_dict()})
    raw = client.serialize(response)
    assert client.from_json(raw).request_id == response.request_id


def test_parse_create_response_id_object():
    client = DrivingLicenseBookerClient()
    response = client.create_booking({"kind": BookingKind.LICENSE_RENEWAL.value, "applicant": applicant().to_dict()})
    assert client.parse_create_response_id(response) == response.request_id


def test_parse_create_response_id_mapping():
    assert DrivingLicenseBookerClient().parse_create_response_id({"id": "abc"}) == "abc"


def test_parse_create_response_id_json():
    assert DrivingLicenseBookerClient().parse_create_response_id('{"booking_id": "xyz"}') == "xyz"


def test_parse_create_response_id_rejects_missing():
    with pytest.raises(ValueError):
        DrivingLicenseBookerClient().parse_create_response_id({"status": "ok"})


def test_export_roster():
    roster = DrivingLicenseBookerClient().export_roster([applicant(), applicant(full_name="Moshe Cohen")])
    assert len(roster) == 2
    assert roster[0]["national_id"] == VALID_ID


def test_teacher_message_contains_hebrew_date():
    message = DrivingLicenseBookerClient().make_teacher_message(
        applicant=applicant(full_name="נועה ישראלי"),
        windows=[TimeWindow(dt.date(2026, 7, 20))],
        teacher_name="אבי",
        pickup_city="ראשון לציון",
    )
    assert "20/07/2026" in message
    assert "נא לאשר" in message


@pytest.mark.asyncio
async def test_async_create_get_cancel_list(tmp_path):
    client = AsyncDrivingLicenseBookerClient(state_path=tmp_path / "state.json")
    response = await client.create_booking({"kind": BookingKind.LICENSE_RENEWAL.value, "applicant": applicant().to_dict()})
    loaded = await client.get_booking(response.request_id)
    assert loaded.request_id == response.request_id
    cancelled = await client.cancel_booking(response.request_id)
    assert cancelled.status == BookingStatus.CANCELLED.value
    records = await client.list_bookings(status=BookingStatus.CANCELLED)
    assert len(records) == 1


def test_cli_service_links():
    result = CliRunner().invoke(main, ["service-links", "--env", "sandbox"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "license_renewal" in payload


def test_cli_create_get_chain(tmp_path):
    state = tmp_path / "state.json"
    runner = CliRunner()
    create = runner.invoke(
        main,
        [
            "create-renewal",
            "--env",
            "sandbox",
            "--state",
            str(state),
            "--name",
            "Dana Levi",
            "--national-id",
            VALID_ID,
            "--phone",
            "0501234567",
            "--license-number",
            "1234567",
            "--expiry-date",
            "2026-08-31",
        ],
    )
    assert create.exit_code == 0
    request_id = json.loads(create.output)["request_id"]
    get = runner.invoke(main, ["get", "--env", "sandbox", "--state", str(state), request_id])
    assert get.exit_code == 0
    assert json.loads(get.output)["request_id"] == request_id


def test_cli_readiness_not_paid():
    result = CliRunner().invoke(
        main,
        [
            "readiness",
            "--env",
            "sandbox",
            "--name",
            "Dana Levi",
            "--national-id",
            VALID_ID,
            "--phone",
            "0501234567",
            "--license-number",
            "1234567",
            "--expiry-date",
            "2026-08-31",
            "--not-paid",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.output)["ready"] is False


def test_cli_teacher_message_json():
    result = CliRunner().invoke(
        main,
        [
            "teacher-message",
            "--env",
            "sandbox",
            "--name",
            "נועה ישראלי",
            "--national-id",
            VALID_ID,
            "--phone",
            "0501234567",
            "--date",
            "2026-07-20",
            "--teacher-name",
            "אבי",
            "--pickup-city",
            "ראשון לציון",
        ],
    )
    assert result.exit_code == 0
    assert "ראשון לציון" in json.loads(result.output)["message"]
