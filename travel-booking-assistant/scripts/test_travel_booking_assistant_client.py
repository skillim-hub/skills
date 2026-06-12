from __future__ import annotations

import asyncio
import json
from decimal import Decimal

import pytest

from travel_booking_assistant import (
    BookingStatus,
    CostLine,
    Money,
    TravelBookingClient,
    TravelRequest,
    Traveler,
    TripType,
    calculate_fx,
    cancellation_request,
    detect_domestic_eilat,
    detect_shabbat_risk,
    duplicate_charge_triage,
    format_israeli_date,
    invoice_request_he,
    parse_israeli_date,
    redact_sensitive,
)


def make_domestic_request(**overrides):
    data = {
        "trip_type": TripType.DOMESTIC,
        "origin": "Tel Aviv",
        "destination": "Eilat",
        "start_date": "12/06/2026",
        "end_date": "14/06/2026",
        "travelers": [Traveler("adult", 1)],
    }
    data.update(overrides)
    return TravelRequest(**data)


def make_international_request(**overrides):
    data = {
        "trip_type": TripType.INTERNATIONAL,
        "origin": "Tel Aviv",
        "destination": "Berlin",
        "start_date": "03/09/2026",
        "end_date": "07/09/2026",
        "travelers": [Traveler("adult", 1)],
        "passport_expiry": "04/2027",
        "nationality": "Israel",
    }
    data.update(overrides)
    return TravelRequest(**data)


def test_parse_israeli_date_slash():
    assert parse_israeli_date("12/06/2026").year == 2026


def test_parse_israeli_date_legacy_hyphen_supported():
    assert parse_israeli_date("12-06-2026").month == 6


def test_parse_israeli_date_rejects_iso():
    with pytest.raises(ValueError):
        parse_israeli_date("2026-06-12")


def test_format_israeli_date():
    assert format_israeli_date(parse_israeli_date("12/06/2026")) == "12/06/2026"


def test_money_formats_ils():
    assert Money(Decimal("12.5"), "ILS").format() == "₪12.50"


def test_money_formats_foreign():
    assert Money(Decimal("12.5"), "eur").format() == "EUR 12.50"


def test_money_as_dict():
    assert Money(10, "ils").as_dict() == {"amount": "10", "currency": "ILS"}


def test_fx_conversion_with_markup():
    fx = calculate_fx(100, "EUR", 4, 2.5)
    assert fx.base_ils.amount == Decimal("400.00")
    assert fx.markup.amount == Decimal("10.00")
    assert fx.total_ils.amount == Decimal("410.00")


def test_fx_as_dict():
    payload = calculate_fx(10, "EUR", 4).as_dict()
    assert payload["supplier"]["currency"] == "EUR"


def test_client_default_fx_rate():
    c = TravelBookingClient(default_fx_rates={"EUR": 4.02})
    fx = c.convert_to_ils(10, "EUR")
    assert fx.total_ils.amount > Decimal("40")


def test_client_missing_fx_rate():
    c = TravelBookingClient()
    with pytest.raises(ValueError):
        c.convert_to_ils(10, "JPY")


def test_create_request_returns_id():
    created = TravelBookingClient().create_request(make_domestic_request())
    assert created["request_id"].startswith("tb-")
    assert created["status"] == "created"


def test_validate_invalid_date_range():
    req = make_domestic_request(start_date="14/06/2026", end_date="12/06/2026")
    issues = req.validate()
    assert any(i.code == "INVALID_DATE_RANGE" for i in issues)


def test_validate_invalid_format_message():
    req = make_domestic_request(start_date="2026/06/12")
    issues = req.validate()
    assert any(i.code == "INVALID_DATE_FORMAT" for i in issues)


def test_validate_missing_traveler():
    req = make_domestic_request(travelers=[])
    issues = req.validate()
    assert any(i.code == "MISSING_TRAVELER" for i in issues)


def test_validate_international_passport_prompt():
    req = make_international_request(passport_expiry=None)
    issues = req.validate()
    assert any(i.code == "MISSING_PASSPORT_PROMPT" for i in issues)


def test_validate_international_nationality_prompt():
    req = make_international_request(nationality=None)
    issues = req.validate()
    assert any(i.code == "MISSING_NATIONALITY" for i in issues)


def test_separate_ticket_warning():
    req = make_international_request(separate_tickets=True)
    issues = req.validate()
    assert any(i.code == "SEPARATE_TICKET_RISK" for i in issues)


def test_travel_request_as_dict_contains_dates():
    payload = make_domestic_request().as_dict()
    assert payload["start_date"] == "12/06/2026"


def test_detect_eilat_english():
    assert detect_domestic_eilat("Eilat")


def test_detect_eilat_hebrew():
    assert detect_domestic_eilat("אילת")


def test_detect_shabbat_risk_friday():
    assert detect_shabbat_risk("12/06/2026") is True


def test_redact_sensitive_card():
    assert "[REDACTED]" in redact_sensitive("card 1234567812345678")


def test_invoice_request_he_contains_terms():
    text = invoice_request_he("ABC123", "Example", "123456789", "ops@example.com")
    assert "חשבונית מס/קבלה" in text
    assert "ABC123" in text


def test_cancellation_request_contains_refund():
    text = cancellation_request("ABC123", "Dana Levi", "12/06/2026")
    assert "refund amount" in text


def test_duplicate_charge_triage():
    result = duplicate_charge_triage([Money(10, "EUR"), Money(20, "EUR")], "Hotel")
    assert result["charge_count"] == 2
    assert result["totals"]["EUR"] == "30"


def test_domestic_eilat_recommendation_has_transfer():
    rec = TravelBookingClient().build_recommendation(make_domestic_request(business=True, needs_vat_invoice=True))
    assert any("Ramon" in item or "רמון" in item for item in rec.checklist)
    assert rec.total_ils.amount > 0


def test_domestic_non_eilat_estimate():
    rec = TravelBookingClient().build_recommendation(make_domestic_request(destination="Haifa"))
    assert any(line.label == "Rail / local transport" for line in rec.cost_lines)


def test_international_recommendation_has_fx_and_passport_check():
    rec = TravelBookingClient(default_fx_rates={"EUR": 4.02}).build_recommendation(make_international_request())
    assert any(line.fx is not None for line in rec.cost_lines)
    assert any("passport" in item.lower() for item in rec.checklist)


def test_quote_request_alias():
    rec = TravelBookingClient().quote_request(make_domestic_request(request_id="tb-test"))
    assert rec.request_id == "tb-test"


def test_failed_recommendation_on_blocker():
    rec = TravelBookingClient().build_recommendation(
        make_domestic_request(start_date="14/06/2026", end_date="12/06/2026")
    )
    assert rec.status == BookingStatus.FAILED


def test_markdown_english_contains_total():
    rec = TravelBookingClient().build_recommendation(make_domestic_request())
    assert "Total estimate" in rec.to_markdown()


def test_markdown_hebrew_contains_shekel():
    rec = TravelBookingClient().build_recommendation(make_domestic_request(locale="he"))
    assert "סה״כ" in rec.to_markdown(locale="he")


def test_async_build_recommendation():
    rec = asyncio.run(TravelBookingClient().async_build_recommendation(make_domestic_request()))
    assert rec.status == BookingStatus.QUOTE


def test_to_json_is_valid():
    rec = TravelBookingClient().build_recommendation(make_domestic_request())
    payload = TravelBookingClient().to_json(rec)
    assert json.loads(payload)["status"] == "quote"


def test_to_json_accepts_dict():
    payload = TravelBookingClient().to_json({"ok": True})
    assert json.loads(payload)["ok"] is True


def test_cost_line_non_ils_requires_fx():
    with pytest.raises(ValueError):
        CostLine("Hotel", Money(10, "EUR")).total_ils


def test_cost_line_as_dict():
    line = CostLine("Rail", Money(80, "ILS"))
    assert line.as_dict()["total_ils"]["currency"] == "ILS"


def test_business_invoice_checklist():
    rec = TravelBookingClient().build_recommendation(make_domestic_request(business=True, needs_vat_invoice=True))
    assert any("חשבונית" in item for item in rec.checklist)


def test_local_friday_adds_transport_warning():
    rec = TravelBookingClient().build_recommendation(make_domestic_request(start_date="12/06/2026"))
    assert any("Friday" in item or "Saturday" in item for item in rec.checklist)


def test_ils_conversion_has_no_markup():
    fx = TravelBookingClient().convert_to_ils(100, "ILS", card_markup_percent=99)
    assert fx.total_ils.amount == Decimal("100.00")


def test_vat_invoice_non_business_info_issue():
    req = make_domestic_request(business=False, needs_vat_invoice=True)
    assert any(i.code == "VAT_INVOICE_WITHOUT_BUSINESS" for i in req.validate())
