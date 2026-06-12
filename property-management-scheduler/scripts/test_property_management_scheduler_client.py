from __future__ import annotations

from decimal import Decimal

import pytest

from property_management_scheduler import (
    BANK_OF_ISRAEL_SERIES_API_BASE,
    official_reference_values,
    ClientConfig,
    PropertyManagementScheduler,
    SchedulerError,
    format_israeli_date,
    money_to_str,
    month_add,
    parse_israeli_date,
    parse_money,
    validate_email,
    validate_phone,
)


def make_client(tmp_path):
    return PropertyManagementScheduler(tmp_path / "store.json", environment="sandbox")


def seed_lease(client):
    prop = client.create_property("הירקון 12", "תל אביב-יפו", "8")
    tenant = client.add_tenant(prop["id"], "דנה כהן", email="dana@example.com")
    lease = client.create_lease(prop["id"], tenant["id"], "01/01/2026", "31/12/2026", "5200", due_day=5, deposit_ils="10400")
    return prop, tenant, lease


def test_parse_israeli_date_slash():
    assert parse_israeli_date("05/01/2026").isoformat() == "2026-01-05"


def test_parse_israeli_date_dash():
    assert parse_israeli_date("05-01-2026").isoformat() == "2026-01-05"


def test_parse_israeli_date_iso():
    assert parse_israeli_date("2026-01-05").isoformat() == "2026-01-05"


def test_format_israeli_date():
    assert format_israeli_date("2026-02-09") == "09/02/2026"


def test_parse_money_accepts_shekel_symbol():
    assert parse_money("₪5,200.457") == Decimal("5200.46")


def test_money_to_str_rounds():
    assert money_to_str("10.005") == "10.01"


def test_month_add_clamps_day():
    assert month_add(parse_israeli_date("31/01/2026"), 1, 31).isoformat() == "2026-02-28"


def test_validate_phone_local():
    assert validate_phone("0501234567") == "0501234567"


def test_validate_phone_international():
    assert validate_phone("+972501234567") == "+972501234567"


def test_validate_email_rejects_invalid():
    with pytest.raises(SchedulerError):
        validate_email("missing-at")


def test_config_rejects_negative_grace_days():
    config = ClientConfig(payment_grace_days=-1)
    with pytest.raises(SchedulerError):
        config.validate()


def test_create_property(tmp_path):
    client = make_client(tmp_path)
    prop = client.create_property("הרצל 1", "חיפה")
    assert prop["id"].startswith("prop_")
    assert client.list_properties()[0]["city"] == "חיפה"


def test_create_property_requires_address(tmp_path):
    client = make_client(tmp_path)
    with pytest.raises(SchedulerError):
        client.create_property("", "חיפה")


def test_add_tenant_requires_property(tmp_path):
    client = make_client(tmp_path)
    with pytest.raises(SchedulerError):
        client.add_tenant("missing", "דנה", email="dana@example.com")


def test_add_tenant_email_channel_requires_email(tmp_path):
    client = make_client(tmp_path)
    prop = client.create_property("הרצל 1", "חיפה")
    with pytest.raises(SchedulerError):
        client.add_tenant(prop["id"], "דנה")


def test_create_lease(tmp_path):
    client = make_client(tmp_path)
    _, _, lease = seed_lease(client)
    assert lease["monthly_rent_ils"] == "5200.00"
    assert lease["due_day"] == 5


def test_create_lease_rejects_bad_due_day(tmp_path):
    client = make_client(tmp_path)
    prop = client.create_property("הרצל 1", "חיפה")
    tenant = client.add_tenant(prop["id"], "דנה", email="dana@example.com")
    with pytest.raises(SchedulerError):
        client.create_lease(prop["id"], tenant["id"], "01/01/2026", "31/12/2026", "1", due_day=31)


def test_schedule_rent_creates_monthly_charges(tmp_path):
    client = make_client(tmp_path)
    _, _, lease = seed_lease(client)
    charges = client.schedule_rent(lease["id"], "01/01/2026", months=3)
    assert [c["due_date"] for c in charges] == ["2026-01-05", "2026-02-05", "2026-03-05"]


def test_schedule_rent_avoids_duplicates(tmp_path):
    client = make_client(tmp_path)
    _, _, lease = seed_lease(client)
    client.schedule_rent(lease["id"], "01/01/2026", months=2)
    again = client.schedule_rent(lease["id"], "01/01/2026", months=2)
    assert again == []


def test_record_payment_marks_paid(tmp_path):
    client = make_client(tmp_path)
    _, _, lease = seed_lease(client)
    charge = client.schedule_rent(lease["id"], "01/01/2026", months=1)[0]
    paid = client.record_payment(charge["id"], "03/01/2026", "5200")
    assert paid["status"] == "paid"


def test_record_payment_partial(tmp_path):
    client = make_client(tmp_path)
    _, _, lease = seed_lease(client)
    charge = client.schedule_rent(lease["id"], "01/01/2026", months=1)[0]
    paid = client.record_payment(charge["id"], "03/01/2026", "1000")
    assert paid["status"] == "partial"


def test_record_payment_rejects_overpayment(tmp_path):
    client = make_client(tmp_path)
    _, _, lease = seed_lease(client)
    charge = client.schedule_rent(lease["id"], "01/01/2026", months=1)[0]
    with pytest.raises(SchedulerError):
        client.record_payment(charge["id"], "03/01/2026", "9999")


def test_mark_overdue_after_grace_days(tmp_path):
    client = make_client(tmp_path)
    _, _, lease = seed_lease(client)
    client.schedule_rent(lease["id"], "01/01/2026", months=1)
    overdue = client.mark_overdue("10/01/2026")
    assert overdue[0]["status"] == "overdue"


def test_maintenance_priority_urgent(tmp_path):
    client = make_client(tmp_path)
    assert client.suggest_maintenance_priority("gas smell and electric sparks") == "urgent"


def test_create_maintenance_auto_priority(tmp_path):
    client = make_client(tmp_path)
    prop = client.create_property("הרצל 1", "חיפה")
    task = client.create_maintenance(prop["id"], "נזילה", "יש נזילה פעילה מתחת לכיור")
    assert task["severity"] in {"high", "urgent"}


def test_update_maintenance_completed_sets_timestamp(tmp_path):
    client = make_client(tmp_path)
    prop = client.create_property("הרצל 1", "חיפה")
    task = client.create_maintenance(prop["id"], "בדיקה", "בדיקה תקופתית של דוד")
    updated = client.update_maintenance_status(task["id"], "completed")
    assert updated["completed_at"].endswith("Z")


def test_generate_rent_message(tmp_path):
    client = make_client(tmp_path)
    _, _, lease = seed_lease(client)
    charge = client.schedule_rent(lease["id"], "01/01/2026", months=1)[0]
    message = client.generate_tenant_message("rent_reminder", charge_id=charge["id"])
    assert "₪5200.00" in message["body"]


def test_log_communication(tmp_path):
    client = make_client(tmp_path)
    prop, tenant, _ = seed_lease(client)
    log = client.log_communication(tenant["id"], prop["id"], "email", "נושא", "גוף", scheduled_for="10/01/2026")
    assert log["scheduled_for"] == "2026-01-10"


def test_build_daily_agenda(tmp_path):
    client = make_client(tmp_path)
    prop, tenant, lease = seed_lease(client)
    client.schedule_rent(lease["id"], "01/01/2026", months=1)
    client.log_communication(tenant["id"], prop["id"], "email", "נושא", "גוף", scheduled_for="05/01/2026")
    agenda = client.build_daily_agenda("05/01/2026")
    assert agenda["counts"]["rent_due"] == 1
    assert agenda["counts"]["communications_due"] == 1


def test_export_accounting_pack(tmp_path):
    client = make_client(tmp_path)
    _, _, lease = seed_lease(client)
    charge = client.schedule_rent(lease["id"], "01/01/2026", months=1)[0]
    client.record_payment(charge["id"], "03/01/2026", "5200")
    pack = client.export_accounting_pack("01/01/2026", "31/01/2026")
    assert pack["totals"]["paid_rent_ils"] == "5200.00"


def test_save_and_load(tmp_path):
    store = tmp_path / "store.json"
    client = PropertyManagementScheduler(store)
    client.create_property("הרצל 1", "חיפה")
    loaded = PropertyManagementScheduler(store)
    assert len(loaded.list_properties()) == 1


@pytest.mark.asyncio
async def test_async_create_property(tmp_path):
    client = make_client(tmp_path)
    prop = await client.acreate_property("הרצל 1", "חיפה")
    assert prop["city"] == "חיפה"


@pytest.mark.asyncio
async def test_async_agenda(tmp_path):
    client = make_client(tmp_path)
    agenda = await client.abuild_daily_agenda("01/01/2026")
    assert agenda["date"] == "2026-01-01"


def test_official_reference_values_after_june_2026():
    values = official_reference_values("01/06/2026")
    assert values["standard_vat_rate"] == "18%"
    assert values["israel_invoice_allocation_threshold_ils"] == "5000.00"
    assert values["bank_of_israel_series_api_base"] == BANK_OF_ISRAEL_SERIES_API_BASE


def test_official_reference_values_before_june_2026():
    values = official_reference_values("31/05/2026")
    assert values["israel_invoice_allocation_threshold_ils"] == "10000.00"


def test_bank_of_israel_host_uses_current_gov_domain():
    assert BANK_OF_ISRAEL_SERIES_API_BASE.startswith("https://edge.boi.gov.il/")
