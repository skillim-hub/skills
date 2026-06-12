from __future__ import annotations

import asyncio
import csv
import json
from datetime import date
from pathlib import Path

from click.testing import CliRunner

import bituach_leumi_payment_scheduler as client
from bituach_leumi_payment_scheduler.cli import cli


ROOT = Path(__file__).resolve().parents[1]


def make_profile(**kwargs):
    data = {"payer_name": "Dana", "business_type": client.BusinessType.SELF_EMPLOYED, "monthly_income_nis": 10000.0}
    data.update(kwargs)
    return client.BusinessProfile(**data)


def make_options(**kwargs):
    data = {"start_month": date(2026, 1, 1), "months": 3}
    data.update(kwargs)
    return client.ScheduleOptions(**data)


def test_parse_date_accepts_iso():
    assert client.parse_date("2026-01-31") == date(2026, 1, 31)


def test_parse_date_accepts_israeli_dash_format():
    assert client.parse_date("31-01-2026") == date(2026, 1, 31)


def test_parse_date_accepts_israeli_slash_format():
    assert client.parse_date("31/01/2026") == date(2026, 1, 31)


def test_parse_date_accepts_month():
    assert client.parse_date("2026-01") == date(2026, 1, 1)


def test_parse_business_type_alias_hebrew():
    assert client.parse_business_type("עצמאי") == client.BusinessType.SELF_EMPLOYED


def test_format_nis():
    assert client.format_nis(1234.5) == "₪1,234.50"


def test_next_business_day_adjusts_friday_to_sunday():
    assert client.adjust_business_day(date(2026, 5, 15), client.AdjustmentPolicy.NEXT_BUSINESS_DAY) == date(2026, 5, 17)


def test_next_business_day_adjusts_saturday_to_sunday():
    assert client.adjust_business_day(date(2026, 8, 15), client.AdjustmentPolicy.NEXT_BUSINESS_DAY) == date(2026, 8, 16)


def test_previous_business_day_adjusts_saturday_to_thursday():
    assert client.adjust_business_day(date(2026, 8, 15), client.AdjustmentPolicy.PREVIOUS_BUSINESS_DAY) == date(2026, 8, 13)


def test_keep_date_does_not_adjust():
    assert client.adjust_business_day(date(2026, 8, 15), client.AdjustmentPolicy.KEEP_DATE) == date(2026, 8, 15)


def test_holiday_adjustment_skips_custom_holiday():
    holidays = {date(2026, 6, 15)}
    assert client.adjust_business_day(date(2026, 6, 15), client.AdjustmentPolicy.NEXT_BUSINESS_DAY, holidays=holidays) == date(2026, 6, 16)


def test_due_for_period_is_following_month_15():
    assert client.statutory_due_for_period(date(2026, 1, 1)) == date(2026, 2, 15)


def test_options_reject_due_day_after_28():
    options = make_options(due_day=31)
    try:
        options.validate()
    except client.SchedulerError as exc:
        assert "due_day" in str(exc)
    else:
        raise AssertionError("Expected SchedulerError")


def test_profile_requires_income_for_self_employed():
    profile = client.BusinessProfile(payer_name="Dana", business_type=client.BusinessType.SELF_EMPLOYED)
    try:
        profile.validate()
    except client.SchedulerError as exc:
        assert "monthly_income_nis" in str(exc)
    else:
        raise AssertionError("Expected SchedulerError")


def test_estimate_self_employed_amount_uses_tiers():
    profile = make_profile(monthly_income_nis=10000.0)
    expected = round(7703 * 0.0770 + (10000 - 7703) * 0.1800, 2)
    assert client.estimate_monthly_amount(profile) == expected


def test_estimate_amount_override_wins():
    profile = make_profile(amount_override_nis=999.0)
    assert client.estimate_monthly_amount(profile) == 999.0


def test_estimate_employer_uses_payroll():
    profile = client.BusinessProfile(payer_name="Company", business_type=client.BusinessType.EMPLOYER, monthly_payroll_nis=20000)
    amount = client.estimate_monthly_amount(profile)
    assert amount == round(7703 * 0.0878 + (20000 - 7703) * 0.1977, 2)


def test_estimate_consumer_default():
    profile = client.BusinessProfile(payer_name="Avi", business_type=client.BusinessType.CONSUMER)
    assert client.estimate_monthly_amount(profile) == 266.0


def test_default_policy_matches_web_validated_2026_values():
    policy = client.ContributionPolicy()
    assert policy.reduced_threshold_nis == 7703.0
    assert policy.self_employed_reduced_rate == 0.0770
    assert policy.self_employed_regular_rate == 0.1800
    assert policy.employer_combined_reduced_rate == 0.0878
    assert policy.employer_combined_regular_rate == 0.1977
    assert policy.consumer_monthly_default_nis == 266.0


def test_generate_payment_plan_month_count_and_periods():
    plan = client.generate_payment_plan(make_profile(), make_options(), today=date(2025, 12, 1))
    assert len(plan.obligations) == 3
    assert plan.obligations[0].period_start == date(2026, 1, 1)
    assert plan.obligations[-1].period_end == date(2026, 3, 31)


def test_generate_payment_plan_adjusts_due_date():
    plan = client.generate_payment_plan(make_profile(), make_options(months=1), today=date(2026, 1, 1))
    assert plan.obligations[0].statutory_due_date == date(2026, 2, 15)
    assert plan.obligations[0].adjusted_due_date == date(2026, 2, 15)


def test_reminders_are_generated():
    plan = client.generate_payment_plan(make_profile(), make_options(months=1), today=date(2026, 1, 1))
    reminders = plan.obligations[0].reminders
    assert [r.days_before_due for r in reminders] == [14, 7, 3, 1]
    assert reminders[0].date < plan.obligations[0].adjusted_due_date


def test_status_overdue():
    assert client.classify_status(date(2026, 1, 1), today=date(2026, 1, 2)) == client.PaymentStatus.OVERDUE


def test_status_due_today():
    assert client.classify_status(date(2026, 1, 1), today=date(2026, 1, 1)) == client.PaymentStatus.DUE_TODAY


def test_status_due_soon():
    assert client.classify_status(date(2026, 1, 7), today=date(2026, 1, 1)) == client.PaymentStatus.DUE_SOON


def test_next_due_obligation_returns_first_future():
    plan = client.generate_payment_plan(make_profile(), make_options(months=2), today=date(2026, 1, 1))
    due = client.next_due_obligation(plan, today=date(2026, 2, 16))
    assert due is not None
    assert due.period_start == date(2026, 2, 1)


def test_to_json_round_trips_and_preserves_hebrew():
    plan = client.generate_payment_plan(make_profile(payer_name="סטודיו"), make_options(months=1), today=date(2026, 1, 1))
    output = client.to_json(plan)
    assert "סטודיו" in output
    data = json.loads(output)
    assert data["obligations"][0]["currency"] == "ILS"


def test_to_csv_has_one_data_row():
    plan = client.generate_payment_plan(make_profile(), make_options(months=1), today=date(2026, 1, 1))
    rows = list(csv.DictReader(client.to_csv(plan).splitlines()))
    assert len(rows) == 1
    assert rows[0]["business_type"] == "self-employed"


def test_to_ics_contains_events_and_due_date():
    plan = client.generate_payment_plan(make_profile(), make_options(months=1), today=date(2026, 1, 1))
    ics = client.to_ics(plan)
    assert "BEGIN:VCALENDAR" in ics
    assert "BL-self-employed-2026-01" in ics
    assert "DTSTART;VALUE=DATE:20260215" in ics


def test_to_text_contains_payer_and_amount():
    plan = client.generate_payment_plan(make_profile(amount_override_nis=500), make_options(months=1), today=date(2026, 1, 1))
    text = client.to_text(plan)
    assert "Dana" in text
    assert "₪500.00" in text


def test_async_plan_matches_sync_shape():
    sync_plan = client.generate_payment_plan(make_profile(), make_options(months=1), today=date(2026, 1, 1))
    async_plan = asyncio.run(client.generate_payment_plan_async(make_profile(), make_options(months=1), today=date(2026, 1, 1)))
    assert len(async_plan.obligations) == len(sync_plan.obligations)
    assert async_plan.obligations[0].obligation_id == sync_plan.obligations[0].obligation_id


def test_plan_from_mapping():
    mapping = {
        "profile": {"payer_name": "Noa", "business_type": "self-employed", "monthly_income_nis": 8000},
        "options": {"start_month": "2026-01", "months": 1, "holidays": ["2026-02-15"]},
    }
    plan = client.plan_from_mapping(mapping, today=date(2026, 1, 1))
    assert plan.profile.payer_name == "Noa"
    assert plan.obligations[0].adjusted_due_date == date(2026, 2, 16)


def test_plan_record_save_load_round_trip(tmp_path):
    plan = client.generate_payment_plan(make_profile(), make_options(months=1), today=date(2026, 1, 1))
    path = client.save_plan_record(plan, tmp_path, environment="sandbox")
    assert path.exists()
    loaded = client.load_plan_record(client.make_plan_id(plan), tmp_path)
    rebuilt = client.plan_from_record(loaded, today=date(2026, 1, 1))
    assert rebuilt.profile.payer_name == "Dana"
    assert loaded["environment"] == "sandbox"


def test_plan_record_rejects_bad_environment():
    plan = client.generate_payment_plan(make_profile(), make_options(months=1), today=date(2026, 1, 1))
    try:
        client.plan_record(plan, environment="staging")
    except client.SchedulerError as exc:
        assert "environment" in str(exc)
    else:
        raise AssertionError("Expected SchedulerError")


def test_cli_plan_text_success():
    runner = CliRunner()
    result = runner.invoke(cli, ["plan", "--start-month", "2026-01", "--months", "1", "--income", "10000"])
    assert result.exit_code == 0, result.output
    assert "Payment plan" in result.output
    assert "2026-01-01" in result.output


def test_cli_plan_json_success():
    runner = CliRunner()
    result = runner.invoke(cli, ["--env", "production", "plan", "--start-month", "2026-01", "--months", "1", "--income", "10000", "--format", "json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert len(data["obligations"]) == 1


def test_cli_invalid_date_fails():
    runner = CliRunner()
    result = runner.invoke(cli, ["plan", "--start-month", "bad-date", "--months", "1", "--income", "10000"])
    assert result.exit_code != 0
    assert "date must" in result.output


def test_cli_validate_config(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"profile": {"payer_name": "Maya", "business_type": "consumer"}, "options": {"start_month": "2026-01", "months": 1}}), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "--config", str(config)])
    assert result.exit_code == 0, result.output
    assert "Valid:" in result.output


def test_cli_create_show_chain(tmp_path):
    runner = CliRunner()
    storage = tmp_path / "plans"
    create_result = runner.invoke(
        cli,
        [
            "--env", "sandbox", "create", "--storage-dir", str(storage), "--payer-name", "סטודיו", "--start-month", "2026-01", "--months", "1", "--income", "10000",
        ],
    )
    assert create_result.exit_code == 0, create_result.output
    response = json.loads(create_result.output)
    assert response["plan_id"]
    show_result = runner.invoke(cli, ["show", response["plan_id"], "--storage-dir", str(storage), "--format", "json"])
    assert show_result.exit_code == 0, show_result.output
    shown = json.loads(show_result.output)
    assert shown["plan_id"] == response["plan_id"]
    assert shown["environment"] == "sandbox"


def test_hyphenated_client_file_removed():
    assert not (ROOT / "scripts" / "bituach-leumi-payment-scheduler-client.py").exists()
