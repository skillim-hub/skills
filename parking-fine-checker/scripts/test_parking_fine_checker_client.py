from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

import pytest

import parking_fine_checker as client


def test_normalize_vehicle_with_hyphens():
    assert client.normalize_vehicle_number("12-345-67") == "1234567"


def test_normalize_vehicle_with_spaces():
    assert client.normalize_vehicle_number(" 123 45 678 ") == "12345678"


def test_normalize_vehicle_rejects_short():
    with pytest.raises(client.ValidationError):
        client.normalize_vehicle_number("1234")


def test_mask_identifier():
    assert client.mask_identifier("123456789") == "*****6789"


def test_parse_iso_date():
    assert str(client.parse_israeli_date("2026-05-14")) == "2026-05-14"


def test_parse_hebrew_slash_date():
    assert str(client.parse_israeli_date("14/05/2026")) == "2026-05-14"


def test_parse_legacy_dash_date():
    assert str(client.parse_israeli_date("14-05-2026")) == "2026-05-14"


def test_format_he_date_uses_slash():
    assert client.format_he_date("2026-05-14") == "14/05/2026"


def test_money_str_rounds():
    assert client.money_str("10.555") == "10.56"


def test_money_rejects_negative():
    with pytest.raises(client.ValidationError):
        client.money_str("-1")


def test_build_case_id_contains_plate_and_notice():
    case_id = client.build_case_id("12-345-67", "1001", created_on="2026-06-02")
    assert case_id.startswith("20260602-1234567-1001-")


def test_create_case_returns_case_record():
    api = client.ParkingFineClient(base_url="mock://local")
    record = api.create_case(
        issuer_type="municipality",
        vehicle_number="12-345-67",
        notice_number="1001",
        amount_ils="250",
        notice_date="10/03/2026",
        due_date="08/06/2026",
    )
    assert record.case_id
    assert record.vehicle_number == "1234567"
    assert record.amount_ils == Decimal("250.00")


@pytest.mark.asyncio
async def test_async_create_case_returns_case_record():
    api = client.ParkingFineAsyncClient(base_url="mock://local")
    record = await api.create_case(
        issuer_type="municipality",
        vehicle_number="12-345-67",
        notice_number="1001",
        amount_ils="250",
        notice_date="10/03/2026",
        due_date="08/06/2026",
    )
    assert record.case_id
    assert record.vehicle_number == "1234567"


def test_lookup_request_payload_redacts_identifier():
    req = client.FineLookupRequest(
        issuer_type="municipality",
        vehicle_number="12-345-67",
        notice_number="1001",
        recipient_identifier="123456789",
        amount_ils="250",
        notice_date="10/03/2026",
        due_date="08/06/2026",
        case_id="case-1",
        environment="sandbox",
    )
    payload = req.to_payload(redact=True)
    assert payload["vehicle_number"] == "1234567"
    assert payload["recipient_identifier"] == "*****6789"
    assert payload["amount_ils"] == "250.00"
    assert payload["case_id"] == "case-1"


def test_lookup_request_rejects_due_before_notice():
    with pytest.raises(client.ValidationError):
        client.FineLookupRequest(
            issuer_type="municipality",
            vehicle_number="1234567",
            notice_number="1001",
            notice_date="10/03/2026",
            due_date="09/03/2026",
        )


def test_lookup_request_rejects_bad_environment():
    with pytest.raises(client.ValidationError):
        client.FineLookupRequest(
            issuer_type="municipality",
            vehicle_number="1234567",
            notice_number="1001",
            environment="staging",
        )


def test_result_from_payload():
    result = client.FineLookupResult.from_payload(
        {
            "case_id": "case-1",
            "status": "verified_unpaid",
            "vehicle_number": "12-345-67",
            "issuer_type": "municipality",
            "amount_ils": "250",
            "due_date": "08/06/2026",
            "payment_allowed": True,
        }
    )
    assert result.case_id == "case-1"
    assert result.vehicle_number == "1234567"
    assert result.amount_ils == Decimal("250.00")
    assert result.due_date.isoformat() == "2026-06-08"
    assert result.payment_allowed is True


def test_mock_lookup_found():
    transport = client.MockFineTransport(
        [
            {
                "status": "verified_unpaid",
                "vehicle_number": "1234567",
                "issuer_type": "municipality",
                "notice_number": "1001",
                "amount_ils": "250.00",
            }
        ]
    )
    api = client.ParkingFineClient(transport=transport)
    result = api.lookup_fine(
        client.FineLookupRequest(
            issuer_type="municipality",
            vehicle_number="12-345-67",
            notice_number="1001",
        )
    )
    assert result.status == "verified_unpaid"


def test_mock_lookup_not_found():
    api = client.ParkingFineClient(transport=client.MockFineTransport([]))
    result = api.lookup_fine(
        client.FineLookupRequest(
            issuer_type="municipality",
            vehicle_number="12-345-67",
            notice_number="missing",
        )
    )
    assert result.status == "lookup_not_found"


@pytest.mark.asyncio
async def test_async_lookup_found():
    transport = client.AsyncMockFineTransport(
        [
            {
                "status": "verified_unpaid",
                "vehicle_number": "1234567",
                "issuer_type": "municipality",
                "notice_number": "1001",
                "amount_ils": "250.00",
            }
        ]
    )
    api = client.ParkingFineAsyncClient(transport=transport)
    result = await api.lookup_fine(
        client.FineLookupRequest(
            issuer_type="municipality",
            vehicle_number="1234567",
            notice_number="1001",
        )
    )
    assert result.status == "verified_unpaid"


def test_prepare_payment_success():
    api = client.ParkingFineClient(transport=client.MockFineTransport([]))
    payment = api.prepare_payment("case-1", "250", status="approved_for_payment")
    assert payment.amount_ils == Decimal("250.00")
    assert payment.to_dict()["amount_ils"] == "250.00"


def test_prepare_payment_blocks_paid_status():
    api = client.ParkingFineClient(transport=client.MockFineTransport([]))
    with pytest.raises(client.DuplicatePaymentRiskError):
        api.prepare_payment("case-1", "250", status="verified_paid")


def test_prepare_payment_requires_verified_status():
    api = client.ParkingFineClient(transport=client.MockFineTransport([]))
    with pytest.raises(client.ValidationError):
        api.prepare_payment("case-1", "250", status="new")


def test_submit_appeal_success():
    api = client.ParkingFineClient(transport=client.MockFineTransport([]))
    appeal = api.submit_appeal(
        "case-1",
        "Paid parking app session covered the enforcement time.",
        evidence=[{"type": "receipt", "file_name": "receipt.pdf"}],
    )
    assert appeal.status == "appeal_submitted"
    assert appeal.to_dict()["appeal_reference"] == "APL-MOCK-001"


def test_submit_appeal_requires_grounds():
    api = client.ParkingFineClient(transport=client.MockFineTransport([]))
    with pytest.raises(client.ValidationError):
        api.submit_appeal("case-1", "  ")


def test_classify_hebrew_municipality():
    assert client.classify_issuer("עיריית תל אביב-יפו") == "municipality"


def test_classify_hebrew_toll():
    assert client.classify_issuer("כביש 6 חוב אגרה") == "toll"


def test_classify_police():
    assert client.classify_issuer("Israel Police traffic ticket") == "police"


def test_assess_police_escalates():
    assert (
        client.assess_case(
            issuer_type="police",
            status="verified_unpaid",
            has_points_or_court=True,
        )
        == "escalate"
    )


def test_assess_payment_app_contest():
    assert (
        client.assess_case(
            issuer_type="municipality",
            status="verified_unpaid",
            payment_app_matches=True,
        )
        == "contest"
    )


def test_assess_driver_known_transfer():
    assert (
        client.assess_case(
            issuer_type="municipality",
            status="verified_unpaid",
            driver_known=True,
        )
        == "transfer"
    )


def test_assess_duplicate_hold():
    assert (
        client.assess_case(
            issuer_type="municipality",
            status="verified_unpaid",
            duplicate_risk=True,
        )
        == "hold"
    )


def test_collection_without_breakdown_hold():
    assert (
        client.assess_case(
            issuer_type="collection",
            status="collection",
            collection_breakdown=False,
        )
        == "hold"
    )


def test_build_checklist_toll_has_itemization():
    items = client.build_checklist("toll")
    assert any("trip itemization" in item for item in items)


def test_build_checklist_business_vehicle_has_driver_step():
    items = client.build_checklist("municipality", business_vehicle=True)
    assert any("Identify driver" in item for item in items)


def test_approval_memo_formats_hebrew_date_and_money():
    memo = client.approval_memo(
        case_id="case-1",
        issuer_name="Example Municipality",
        vehicle_number="12-345-67",
        notice_number="1001",
        amount_ils="250",
        due_date="2026-06-08",
        approver="Office manager",
    )
    assert "Amount: ₪250.00" in memo
    assert "Due date: 08/06/2026" in memo
    assert "Vehicle: 1234567" in memo


def test_detect_duplicates():
    rows = [
        {"issuer_name": "City", "vehicle_number": "12-345-67", "notice_number": "A"},
        {"issuer_name": "city", "vehicle_number": "1234567", "notice_number": "A"},
        {"issuer_name": "City", "vehicle_number": "7654321", "notice_number": "B"},
    ]
    assert client.detect_duplicates(rows) == [("city", "1234567", "A")]


def test_load_cases_csv(tmp_path):
    path = tmp_path / "cases.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["issuer_name", "vehicle_number", "notice_number"])
        writer.writeheader()
        writer.writerow({"issuer_name": "City", "vehicle_number": "1234567", "notice_number": "A"})
    rows = client.load_cases_csv(path)
    assert rows[0]["notice_number"] == "A"


def test_redact_payload_removes_card():
    payload = client.redact_payload(
        {
            "recipient_identifier": "123456789",
            "card_number": "4111111111111111",
        }
    )
    assert payload["recipient_identifier"] == "*****6789"
    assert payload["card_number"] == "[removed]"


def test_save_json(tmp_path):
    path = tmp_path / "out.json"
    client.save_json(path, {"שלום": "עולם"})
    assert "שלום" in path.read_text(encoding="utf-8")


def test_default_client_mock_lookup():
    api = client.ParkingFineClient(base_url="mock://local")
    result = api.lookup_fine(
        client.FineLookupRequest(
            issuer_type="municipality",
            vehicle_number="1234567",
            notice_number="1001",
        )
    )
    assert result.status == "verified_unpaid"


@pytest.mark.asyncio
async def test_async_prepare_payment():
    api = client.ParkingFineAsyncClient(transport=client.AsyncMockFineTransport([]))
    payment = await api.prepare_payment("case-async", "42.8", status="verified_unpaid")
    assert payment.amount_ils == Decimal("42.80")


@pytest.mark.asyncio
async def test_async_submit_appeal():
    api = client.ParkingFineAsyncClient(transport=client.AsyncMockFineTransport([]))
    appeal = await api.submit_appeal("case-async", "Valid resident permit.")
    assert appeal.appeal_reference == "APL-MOCK-001"


def test_package_import_exposes_public_api():
    assert client.ParkingFineClient.__name__ == "ParkingFineClient"
    assert callable(client.normalize_vehicle_number)


def test_verification_log_exists():
    root = Path(__file__).resolve().parents[1]
    text = (root / "references" / "verification-log.md").read_text(encoding="utf-8")
    assert "Two-pass web validation" in text
    assert "Total checks | 28" in text
    assert "final ✗ could not be confirmed | 0" in text


def test_metadata_version_v3():
    root = Path(__file__).resolve().parents[1]
    data = __import__("json").loads((root / "metadata.json").read_text(encoding="utf-8"))
    assert data["version"] == "2.2.0"
