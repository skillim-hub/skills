from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

import event_scheduler_invitation as module
from event_scheduler_invitation.cli import app


def test_hyphenated_client_removed():
    assert not Path("scripts/event-scheduler-invitation-client.py").exists()


def test_parse_israeli_date_slash():
    assert module.parse_israeli_date("18/06/2026").isoformat() == "2026-06-18"


def test_parse_israeli_date_hyphen_backward_compatible():
    assert module.parse_israeli_date("18-06-2026").isoformat() == "2026-06-18"


def test_parse_israeli_date_iso():
    assert module.format_israeli_date("2026-06-18") == "18/06/2026"


def test_format_nis():
    assert module.format_nis(12345.4) == "₪12,345"


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("050-123-4567", "+972501234567"),
        ("+972 50 123 4567", "+972501234567"),
        ("972501234567", "+972501234567"),
        ("03-1234567", "+97231234567"),
    ],
)
def test_normalize_israeli_phone(raw, expected):
    assert module.normalize_israeli_phone(raw) == expected


def test_invalid_phone_raises():
    with pytest.raises(ValueError):
        module.normalize_israeli_phone("12345")


def test_map_hebrew_rsvp_status_confirmed():
    assert module.map_rsvp_status("מגיעים") == module.RSVPStatus.CONFIRMED


def test_map_hebrew_rsvp_status_declined():
    assert module.map_rsvp_status("לא מגיעים") == module.RSVPStatus.DECLINED


def test_map_hebrew_rsvp_status_tentative():
    assert module.map_rsvp_status("אולי") == module.RSVPStatus.TENTATIVE


def test_brit_milah_before_sunset():
    result = module.calculate_brit_milah_target_date("03/03/2026")
    assert result["target_date_display"] == "10/03/2026"


def test_brit_milah_after_sunset_shifts():
    result = module.calculate_brit_milah_target_date("03/03/2026", after_sunset=True)
    assert result["target_date_display"] == "11/03/2026"
    assert result["warnings"]


def test_create_wedding_plan_has_event_id():
    client = module.EventSchedulerClient()
    plan = client.create_plan(event_type="wedding", event_date="18/06/2026", title="חתונה", city="רחובות")
    assert plan.event_type == module.EventType.WEDDING
    assert plan.city == "רחובות"
    assert len(plan.event_id) == 32


def test_plan_response_can_be_chained():
    client = module.EventSchedulerClient()
    plan = client.create_plan(event_type="wedding", event_date="18/06/2026", title="חתונה")
    response = client.plan_response(plan, saved_path="plan.json")
    assert response["event_id"] == plan.event_id
    assert response["path"] == "plan.json"


def test_add_guest_and_require_event_id():
    client = module.EventSchedulerClient()
    plan = client.create_plan(event_type="customer_event", event_date="01/09/2026", title="אירוע לקוחות")
    client.require_event_id(plan, plan.event_id)
    client.add_guest(plan, module.Guest("דנה", status=module.RSVPStatus.CONFIRMED, party_size_confirmed=2))
    assert plan.guests[0].name == "דנה"
    with pytest.raises(ValueError):
        client.require_event_id(plan, "wrong")


def test_generate_wedding_timeline_contains_marriage_checkpoint():
    client = module.EventSchedulerClient()
    plan = client.create_plan(event_type="wedding", event_date="18/06/2026", title="חתונה")
    titles = [m.title for m in client.generate_timeline(plan)]
    assert any("marriage-file" in title for title in titles)


def test_generate_bar_mitzvah_timeline_contains_torah():
    client = module.EventSchedulerClient()
    plan = client.create_plan(event_type="bar_mitzvah", event_date="07/11/2026", title="בר מצווה")
    titles = [m.title for m in client.generate_timeline(plan)]
    assert any("Torah" in title for title in titles)


def test_budget_estimate():
    client = module.EventSchedulerClient()
    result = client.estimate_budget(guest_count=250, per_plate_nis=330, fixed_costs_nis=40000, contingency_rate=0.1)
    assert result["venue_total_nis"] == 82500
    assert result["estimated_total_nis"] == 134750


def test_budget_negative_rejected():
    client = module.EventSchedulerClient()
    with pytest.raises(ValueError):
        client.estimate_budget(guest_count=-1, per_plate_nis=330)


def test_rsvp_message_contains_hebrew_and_optout():
    client = module.EventSchedulerClient()
    msg = client.build_rsvp_message(name="דנה", event_title="חתונת מאיה ויונתן", event_date="18/06/2026")
    assert "אישור הגעה" in msg
    assert "הסר" in msg
    assert "18/06/2026" in msg


def test_final_logistics_message():
    client = module.EventSchedulerClient()
    msg = client.build_rsvp_message(
        name="דנה",
        event_title="חתונת מאיה ויונתן",
        event_date="18/06/2026",
        final_logistics=True,
        venue_name="גן אירועים",
        address="רחובות",
        reception_time="19:00",
        ceremony_time="20:30",
        transport_note="חניה במקום",
        contact_name="יובל",
    )
    assert "גן אירועים" in msg
    assert "20:30" in msg


def test_venue_capacity_over_capacity():
    client = module.EventSchedulerClient()
    venue = module.Venue(name="אולם", capacity=100, minimum_guests=50, accessibility_confirmed=True)
    result = client.venue_capacity_check(expected_guests=120, venue=venue)
    assert result["status"] == "over_capacity"


def test_venue_capacity_below_minimum():
    client = module.EventSchedulerClient()
    venue = module.Venue(name="אולם", capacity=300, minimum_guests=200, accessibility_confirmed=True)
    result = client.venue_capacity_check(expected_guests=150, venue=venue)
    assert result["status"] == "below_minimum"


def test_deduplicate_guests_by_phone():
    client = module.EventSchedulerClient()
    guests = [
        module.Guest("דנה", phone="050-123-4567", party_size_invited=2),
        module.Guest("Dana", phone="+972501234567", party_size_invited=3),
    ]
    result = client.deduplicate_guests(guests)
    assert len(result["unique"]) == 1
    assert len(result["duplicates"]) == 1
    assert result["unique"][0].party_size_invited == 3


def test_rsvp_summary_counts():
    client = module.EventSchedulerClient()
    guests = [
        module.Guest("א", party_size_invited=2, party_size_confirmed=2, status=module.RSVPStatus.CONFIRMED),
        module.Guest("ב", party_size_invited=4, status=module.RSVPStatus.NO_RESPONSE),
        module.Guest("ג", party_size_invited=1, party_size_confirmed=1, status=module.RSVPStatus.TENTATIVE, needs_transport=True),
    ]
    result = client.rsvp_summary(guests)
    assert result["confirmed_people"] == 2
    assert result["no_response_households"] == 1
    assert result["transport_people"] == 1


def test_assign_tables():
    client = module.EventSchedulerClient()
    guests = [
        module.Guest("א", party_size_confirmed=5, status=module.RSVPStatus.CONFIRMED, group="משפחה"),
        module.Guest("ב", party_size_confirmed=6, status=module.RSVPStatus.CONFIRMED, group="משפחה"),
        module.Guest("ג", party_size_confirmed=2, status=module.RSVPStatus.DECLINED, group="חברים"),
    ]
    tables = client.assign_tables(guests, table_size=10)
    assert len(tables) == 2
    assert sum(t["people"] for t in tables) == 11


def test_assign_tables_rejects_zero_size():
    client = module.EventSchedulerClient()
    with pytest.raises(ValueError):
        client.assign_tables([], table_size=0)


def test_transport_manifest_recommends_buffer():
    client = module.EventSchedulerClient()
    guests = [
        module.Guest("א", party_size_confirmed=10, status=module.RSVPStatus.CONFIRMED, needs_transport=True),
        module.Guest("ב", party_size_confirmed=5, status=module.RSVPStatus.CONFIRMED, needs_transport=False),
    ]
    manifest = client.transport_manifest(guests, pickup_point="ירושלים")
    assert manifest["total_people"] == 10
    assert manifest["recommended_bus_seats"] == 11


def test_vendor_payment_schedule_warnings():
    client = module.EventSchedulerClient()
    vendor = module.Vendor(category="photo", name="צלם", quote_nis=10000, deposit_nis=2000, contract_signed=False)
    schedule = client.vendor_payment_schedule([vendor], event_date="18/06/2026")
    assert schedule[0]["balance_nis"] == 8000
    assert schedule[0]["due_date"] == "11/06/2026"
    assert schedule[0]["warnings"]


def test_privacy_risk_check_finds_sensitive_notes():
    client = module.EventSchedulerClient()
    guests = [module.Guest("דנה", notes="סכסוך משפחתי")]
    risks = client.privacy_risk_check(guests)
    assert risks


def test_message_compliance_check_warns_on_marketing_without_consent():
    client = module.EventSchedulerClient()
    warnings = client.message_compliance_check(message="מבצע מיוחד", contains_marketing=True, has_consent=False)
    assert any("Marketing" in warning for warning in warnings)


def test_csv_import(tmp_path):
    csv_path = tmp_path / "guests.csv"
    csv_path.write_text(
        "name,phone,party_size_invited,party_size_confirmed,status,needs_transport\n"
        "דנה,050-123-4567,2,2,כן,כן\n",
        encoding="utf-8",
    )
    client = module.EventSchedulerClient()
    guests = client.import_guests_csv(csv_path)
    assert len(guests) == 1
    assert guests[0].status == module.RSVPStatus.CONFIRMED
    assert guests[0].needs_transport is True


def test_save_and_load_plan_keeps_event_id(tmp_path):
    client = module.EventSchedulerClient()
    plan = client.create_plan(event_type="customer_event", event_date="01/09/2026", title="אירוע לקוחות", city="תל אביב")
    plan.guests.append(module.Guest("דנה", phone="050-123-4567"))
    path = tmp_path / "plan.json"
    client.save_plan(plan, path)
    loaded = client.load_plan(path)
    assert loaded.title == plan.title
    assert loaded.event_id == plan.event_id
    assert loaded.guests[0].name == "דנה"


def test_async_client_roundtrip(tmp_path):
    async def run():
        async_client = module.AsyncEventSchedulerClient()
        plan = await async_client.create_plan(event_type="wedding", event_date="18/06/2026", title="חתונה")
        path = tmp_path / "async-plan.json"
        await async_client.save_plan(plan, path)
        loaded = await async_client.load_plan(path)
        return loaded.title

    assert asyncio.run(run()) == "חתונה"


def test_cli_create_plan_and_add_guest_chain(tmp_path):
    runner = CliRunner()
    plan_path = tmp_path / "plan.json"
    create = runner.invoke(app, [
        "create-plan",
        "--event-type", "wedding",
        "--date", "18/06/2026",
        "--title", "חתונה",
        "--output", str(plan_path),
    ])
    assert create.exit_code == 0, create.output
    response = json.loads(create.output)
    assert response["event_id"]
    add = runner.invoke(app, [
        "add-guest",
        "--plan", str(plan_path),
        "--event-id", response["event_id"],
        "--name", "דנה",
        "--party-size", "2",
        "--status", "מגיעים",
    ])
    assert add.exit_code == 0, add.output
    added = json.loads(add.output)
    assert added["guest_count"] == 1


def test_cli_budget_outputs_json():
    runner = CliRunner()
    result = runner.invoke(app, ["budget", "--guests", "10", "--per-plate", "100", "--fixed-costs", "500"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["estimated_total_display"] == "₪1,620"


def test_examples_run_with_sandbox_env():
    script = Path("scripts/examples/create_wedding_timeline.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    result = subprocess.run(
        [sys.executable, str(script), "--env", "sandbox"],
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    payload = json.loads(result.stdout)
    assert payload["env"] == "sandbox"
    assert payload["plan"]["event_id"]


def test_current_vat_rate_constant():
    assert module.CURRENT_ISRAEL_VAT_RATE == 0.18


def test_invoice_allocation_threshold_after_june_2026():
    assert module.israel_invoice_allocation_threshold("01/06/2026") == 5000


def test_invoice_allocation_threshold_before_june_2026():
    assert module.israel_invoice_allocation_threshold("31/05/2026") == 10000


def test_requires_invoice_allocation_after_june_2026():
    assert module.requires_israel_invoice_allocation(5001, "01/06/2026", vat_amount_nis=900) is True


def test_tax_documentation_check_flags_follow_up():
    client = module.EventSchedulerClient()
    result = client.tax_documentation_check(
        invoice_amount_before_vat_nis=6000,
        invoice_date="02/06/2026",
        vat_amount_nis=1080,
    )
    assert result["allocation_required_follow_up"] is True
    assert result["current_vat_rate_display"] == "18%"


def test_music_license_checkpoint_family_fee():
    client = module.EventSchedulerClient()
    result = client.music_license_checkpoint(event_type="wedding", event_date="18/06/2026")
    assert result["family_event_fee_nis"] == module.ACUM_FAMILY_EVENT_LICENSE_NIS
    assert result["deadline_buffer_hours"] == 72


def test_cli_tax_check_outputs_current_threshold():
    runner = CliRunner()
    result = runner.invoke(app, [
        "tax-check",
        "--amount-before-vat", "6000",
        "--invoice-date", "02/06/2026",
        "--vat-amount", "1080",
    ])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["allocation_threshold_before_vat_nis"] == 5000


def test_metadata_has_no_author_field():
    data = json.loads(Path("metadata.json").read_text(encoding="utf-8"))
    assert "author" not in data
    assert data["version"] == "2.2.0"
    assert data["date_format"] == "DD/MM/YYYY"
