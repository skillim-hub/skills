from __future__ import annotations

import asyncio
import json
from pathlib import Path
from datetime import date
from decimal import Decimal

import pytest
from click.testing import CliRunner

from arnona_payment_reminder import (
    ArnonaBill,
    ArnonaPaymentReminderClient,
    ArnonaValidationError,
    MunicipalityProfile,
    format_date,
    is_valid_israeli_id_or_company,
    make_bill_id,
    money_nis,
    parse_date,
)
from arnona_payment_reminder.cli import cli

@pytest.fixture()
def bill_payload() -> dict[str, str]:
    return {
        "municipality": "Tel Aviv-Yafo",
        "account_reference": "123456789",
        "bill_number": "2026-ARN-000123",
        "taxpayer_name": "Sample Business Ltd.",
        "property_address": "Ibn Gabirol 1, Tel Aviv-Yafo",
        "period_start": "2026-01-01",
        "period_end": "2026-02-28",
        "issue_date": "2026-01-05",
        "due_date": "2026-02-28",
        "amount_nis": "1540.20",
        "status": "unpaid",
        "payer_id": "123456782",
    }


@pytest.fixture()
def client():
    return ArnonaPaymentReminderClient.with_default_profiles()


def test_parse_iso_date():
    assert parse_date("2026-02-28") == date(2026, 2, 28)


def test_parse_hebrew_date_with_dashes():
    assert parse_date("28-02-2026") == date(2026, 2, 28)


def test_parse_hebrew_date_with_slashes():
    assert parse_date("28/02/2026") == date(2026, 2, 28)


def test_parse_invalid_date_raises():
    with pytest.raises(ArnonaValidationError):
        parse_date("02-28-26")


def test_money_format_uses_shekel_symbol():
    assert money_nis("1540.2") == "₪1,540.20"


def test_hebrew_date_format():
    assert format_date(date(2026, 4, 5), "he") == "05/04/2026"


def test_bill_from_dict_converts_dates_and_decimal(bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    assert bill.due_date == date(2026, 2, 28)
    assert bill.amount_nis == Decimal("1540.20")


def test_missing_required_field_raises(bill_payload):
    del bill_payload["bill_number"]
    with pytest.raises(ArnonaValidationError):
        ArnonaBill.from_dict(bill_payload)


def test_negative_amount_raises(client, bill_payload):
    bill_payload["amount_nis"] = "-1.00"
    bill = ArnonaBill.from_dict(bill_payload)
    with pytest.raises(ArnonaValidationError):
        client.validate_bill(bill)


def test_zero_amount_raises(client, bill_payload):
    bill_payload["amount_nis"] = "0"
    bill = ArnonaBill.from_dict(bill_payload)
    with pytest.raises(ArnonaValidationError):
        client.validate_bill(bill)


def test_issue_after_due_raises(client, bill_payload):
    bill_payload["issue_date"] = "2026-03-01"
    bill = ArnonaBill.from_dict(bill_payload)
    with pytest.raises(ArnonaValidationError):
        client.validate_bill(bill)


def test_period_start_after_end_raises(client, bill_payload):
    bill_payload["period_start"] = "2026-03-01"
    bill = ArnonaBill.from_dict(bill_payload)
    with pytest.raises(ArnonaValidationError):
        client.validate_bill(bill)


def test_short_references_warn(client, bill_payload):
    bill_payload["account_reference"] = "12"
    bill_payload["bill_number"] = "ab"
    bill = ArnonaBill.from_dict(bill_payload)
    warnings = client.validate_bill(bill)
    assert len(warnings) == 2


def test_invalid_payer_id_warns(client, bill_payload):
    bill_payload["payer_id"] = "123456789"
    bill = ArnonaBill.from_dict(bill_payload)
    warnings = client.validate_bill(bill)
    assert any("Payer identifier" in item for item in warnings)


def test_malformed_payment_url_warns(client, bill_payload):
    bill_payload["payment_url"] = "not-a-url"
    bill = ArnonaBill.from_dict(bill_payload)
    warnings = client.validate_bill(bill)
    assert any("Payment URL" in item for item in warnings)


def test_classify_upcoming(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    assert client.classify_bill(bill, "2026-02-01") == "upcoming"


def test_classify_due_soon(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    assert client.classify_bill(bill, "2026-02-24") == "due_soon"


def test_classify_due_today(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    assert client.classify_bill(bill, "2026-02-28") == "due_today"


def test_classify_overdue(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    assert client.classify_bill(bill, "2026-03-01") == "overdue"


def test_paid_bill_has_no_events(client, bill_payload):
    bill_payload["status"] = "paid"
    bill = ArnonaBill.from_dict(bill_payload)
    plan = client.build_reminder_plan(bill, as_of="2026-02-01")
    assert plan.status == "paid"
    assert plan.events == []


def test_build_plan_filters_past_events(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    plan = client.build_reminder_plan(bill, as_of="2026-02-20")
    assert all(event.send_on >= date(2026, 2, 20) for event in plan.events)
    assert {event.severity for event in plan.events} >= {"warning", "urgent"}


def test_build_plan_include_past_events(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    plan = client.build_reminder_plan(bill, as_of="2026-02-20", include_past=True)
    assert any(event.send_on < date(2026, 2, 20) for event in plan.events)


def test_overdue_immediate_event_after_followup_passed(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    plan = client.build_reminder_plan(bill, as_of="2026-03-10")
    assert len(plan.events) == 1
    assert plan.events[0].severity == "overdue"
    assert plan.events[0].send_on == date(2026, 3, 10)


def test_hebrew_plan_contains_hebrew_terms(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    plan = client.build_reminder_plan(bill, as_of="2026-02-20", language="he")
    assert "ארנונה" in plan.instructions.summary
    assert "₪1,540.20" in plan.instructions.summary


def test_payment_instructions_have_required_steps(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    instructions = client.payment_instructions(bill)
    assert len(instructions.steps) >= 6
    assert any("receipt" in item.lower() for item in instructions.steps + instructions.warnings)


def test_next_due_dates_bimonthly(client):
    assert client.next_due_dates("31-01-2026", count=3) == [
        date(2026, 1, 31),
        date(2026, 3, 31),
        date(2026, 5, 31),
    ]


def test_next_due_dates_clamps_month_end(client):
    assert client.next_due_dates("31-08-2026", count=2) == [
        date(2026, 8, 31),
        date(2026, 10, 31),
    ]


def test_next_due_dates_invalid_count(client):
    with pytest.raises(ArnonaValidationError):
        client.next_due_dates("2026-01-01", count=0)


def test_export_ics_contains_calendar(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    plan = client.build_reminder_plan(bill, as_of="2026-02-20")
    ics = client.export_ics(plan)
    assert "BEGIN:VCALENDAR" in ics
    assert ics.count("BEGIN:VEVENT") == len(plan.events)


def test_plan_to_json_is_valid(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    plan = client.build_reminder_plan(bill, as_of="2026-02-24")
    parsed = json.loads(plan.to_json())
    assert parsed["status"] == "due_soon"
    assert "instructions" in parsed


def test_async_plan_matches_sync(client, bill_payload):
    bill = ArnonaBill.from_dict(bill_payload)
    sync_plan = client.build_reminder_plan(bill, as_of="2026-02-20")
    async_plan = asyncio.run(client.async_build_reminder_plan(bill, as_of="2026-02-20"))
    assert async_plan.to_dict()["events"] == sync_plan.to_dict()["events"]


def test_israeli_id_validation():
    assert is_valid_israeli_id_or_company("123456782") is True
    assert is_valid_israeli_id_or_company("123456789") is False


def test_profile_fallback(client):
    profile = client.profile_for("Some Regional Council")
    assert profile.name == "Some Regional Council"


def test_register_profile(client):
    profile = MunicipalityProfile(name="Example", hebrew_name="דוגמה")
    client.register_profile("Example", profile)
    assert client.profile_for("Example").hebrew_name == "דוגמה"


def test_cli_validate_success(tmp_path, bill_payload):
    bill_path = tmp_path / "bill.json"
    bill_path.write_text(json.dumps(bill_payload), encoding="utf-8")
    result = CliRunner().invoke(cli, ["validate", str(bill_path)])
    assert result.exit_code == 0
    assert '"valid": true' in result.output


def test_cli_plan_json_success(tmp_path, bill_payload):
    bill_path = tmp_path / "bill.json"
    bill_path.write_text(json.dumps(bill_payload), encoding="utf-8")
    result = CliRunner().invoke(
        cli,
        ["plan", str(bill_path), "--as-of", "2026-02-24", "--format", "json"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "due_soon"


def test_cli_due_dates_hebrew():
    result = CliRunner().invoke(
        cli,
        ["due-dates", "31-01-2026", "--count", "2", "--language", "he"],
    )
    assert result.exit_code == 0
    assert "31/01/2026" in result.output


def test_cli_export_ics(tmp_path, bill_payload):
    bill_path = tmp_path / "bill.json"
    output_path = tmp_path / "out.ics"
    bill_path.write_text(json.dumps(bill_payload), encoding="utf-8")
    result = CliRunner().invoke(
        cli,
        ["export-ics", str(bill_path), str(output_path), "--as-of", "2026-02-20"],
    )
    assert result.exit_code == 0
    assert output_path.exists()
    assert "BEGIN:VCALENDAR" in output_path.read_text(encoding="utf-8")


def test_make_bill_id_is_stable(bill_payload):
    first = make_bill_id(ArnonaBill.from_dict(bill_payload))
    second = make_bill_id(ArnonaBill.from_dict(bill_payload))
    assert first == second
    assert len(first) == 36


def test_cli_create_then_plan_id_chains(tmp_path, bill_payload):
    store_dir = tmp_path / "store"
    result = CliRunner().invoke(
        cli,
        [
            "--env",
            "sandbox",
            "create",
            "--municipality",
            bill_payload["municipality"],
            "--account-reference",
            bill_payload["account_reference"],
            "--bill-number",
            bill_payload["bill_number"],
            "--taxpayer-name",
            bill_payload["taxpayer_name"],
            "--property-address",
            bill_payload["property_address"],
            "--period-start",
            bill_payload["period_start"],
            "--period-end",
            bill_payload["period_end"],
            "--issue-date",
            bill_payload["issue_date"],
            "--due-date",
            bill_payload["due_date"],
            "--amount-nis",
            bill_payload["amount_nis"],
            "--payer-id",
            bill_payload["payer_id"],
            "--store-dir",
            str(store_dir),
        ],
    )
    assert result.exit_code == 0, result.output
    created = json.loads(result.output)
    assert created["id"]
    followup = CliRunner().invoke(
        cli,
        [
            "plan-id",
            created["id"],
            "--store-dir",
            str(store_dir),
            "--as-of",
            "2026-02-24",
        ],
    )
    assert followup.exit_code == 0, followup.output
    payload = json.loads(followup.output)
    assert payload["status"] == "due_soon"


def test_default_profiles_use_specific_official_urls(client):
    tel_aviv = client.profile_for("Tel Aviv-Yafo")
    jerusalem = client.profile_for("Jerusalem")
    haifa = client.profile_for("Haifa")
    assert tel_aviv.payment_url == "https://tlvpay.tel-aviv.gov.il/he/s/arnona"
    assert "jerusalem.muni.il" in (jerusalem.payment_url or "")
    assert haifa.payment_url == "https://www.haifa.muni.il/resident-service/arnona/tax-payment/"


def test_verification_log_documents_no_uniform_api():
    text = Path("references/verification-log.md").read_text(encoding="utf-8")
    assert "No uniform national Arnona payment API" in text
    assert "18%" in text
