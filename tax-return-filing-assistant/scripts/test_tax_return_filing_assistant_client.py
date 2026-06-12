from __future__ import annotations

import asyncio
import json

import pytest
from click.testing import CliRunner

import tax_return_filing_assistant_cli as cli_mod
import tax_return_filing_assistant_client as client_mod


def make_profile(**overrides):
    data = {
        "tax_year": 2025,
        "taxpayer_type": "sole_proprietor",
        "salary_only": False,
        "wants_refund": False,
        "business_income": True,
        "annual_turnover_ils": 0,
        "has_employees": False,
        "paid_suppliers": False,
        "foreign_income": False,
        "capital_gains": False,
        "rental_income": False,
        "is_online": True,
        "represented_by_cpa": False,
    }
    data.update(overrides)
    return client_mod.FilingProfile(**data)


def test_form_parse_accepts_covered_form():
    assert client_mod.FormType.parse("1301") == client_mod.FormType.FORM_1301


def test_form_parse_rejects_unknown_form():
    with pytest.raises(client_mod.UnknownFormError):
        client_mod.FormType.parse("9999")


def test_format_date_dd_mm_yyyy_with_slashes():
    import datetime as dt

    assert client_mod.format_date(dt.date(2026, 6, 30)) == "30/06/2026"


def test_format_ils_integer():
    assert client_mod.format_ils(12345) == "₪12,345"


def test_profile_to_dict_round_trip():
    profile = make_profile(annual_turnover_ils=123)
    assert client_mod.FilingProfile.from_mapping(profile.to_dict()) == profile


def test_recommend_135_for_salary_only_refund():
    profile = make_profile(
        taxpayer_type="individual",
        salary_only=True,
        wants_refund=True,
        business_income=False,
    )
    rec = client_mod.TaxReturnAssistantClient().recommend_forms(profile)
    assert [form.value for form in rec.forms] == ["135"]


def test_recommend_1301_for_business_income():
    profile = make_profile(business_income=True)
    rec = client_mod.TaxReturnAssistantClient().recommend_forms(profile)
    assert "1301" in [form.value for form in rec.forms]


def test_recommend_6111_when_turnover_above_threshold():
    profile = make_profile(annual_turnover_ils=350000)
    rec = client_mod.TaxReturnAssistantClient().recommend_forms(profile)
    assert "6111" in [form.value for form in rec.forms]
    assert rec.warnings


def test_recommend_856_when_suppliers_paid():
    profile = make_profile(paid_suppliers=True)
    rec = client_mod.TaxReturnAssistantClient().recommend_forms(profile)
    assert "856" in [form.value for form in rec.forms]


def test_recommend_126_when_has_employees():
    profile = make_profile(has_employees=True, business_income=False, taxpayer_type="business")
    rec = client_mod.TaxReturnAssistantClient().recommend_forms(profile)
    assert "126" in [form.value for form in rec.forms]


def test_complex_salary_profile_warns_against_135():
    profile = make_profile(
        taxpayer_type="individual",
        salary_only=True,
        wants_refund=True,
        business_income=True,
    )
    rec = client_mod.TaxReturnAssistantClient().recommend_forms(profile)
    assert "1301" in [form.value for form in rec.forms]
    assert any("135" in warning for warning in rec.warnings)


def test_online_1301_deadline():
    profile = make_profile(is_online=True, represented_by_cpa=False)
    deadline = client_mod.DeadlineCalculator().deadline_for("1301", profile)
    assert deadline.to_dict()["due_date"] == "30/06/2026"
    assert deadline.requires_official_confirmation


def test_paper_1301_deadline():
    profile = make_profile(is_online=False, represented_by_cpa=False)
    deadline = client_mod.DeadlineCalculator().deadline_for("1301", profile)
    assert deadline.to_dict()["due_date"] == "29/05/2026"


def test_represented_deadline_placeholder():
    profile = make_profile(represented_by_cpa=True)
    deadline = client_mod.DeadlineCalculator().deadline_for("1301", profile)
    assert deadline.to_dict()["due_date"] == "30/06/2026"
    assert "extension" in deadline.notes.lower() or "verified" in deadline.notes.lower()


def test_form_135_limitation_deadline():
    profile = make_profile(tax_year=2020, taxpayer_type="individual", salary_only=True, wants_refund=True, business_income=False)
    deadline = client_mod.DeadlineCalculator().deadline_for("135", profile)
    assert deadline.to_dict()["due_date"] == "31/12/2026"


def test_126_deadline():
    deadline = client_mod.DeadlineCalculator().deadline_for("126", make_profile())
    assert deadline.to_dict()["due_date"] == "31/05/2026"


def test_856_deadline():
    deadline = client_mod.DeadlineCalculator().deadline_for("856", make_profile())
    assert deadline.to_dict()["due_date"] == "31/05/2026"


def test_6111_deadline_aligns_1301():
    profile = make_profile(is_online=True)
    deadline = client_mod.DeadlineCalculator().deadline_for("6111", profile)
    assert deadline.to_dict()["due_date"] == "30/06/2026"


def test_reminders_include_due_date_and_sorted():
    deadline = client_mod.DeadlineCalculator().deadline_for("1301", make_profile())
    reminders = deadline.reminders()
    assert reminders == sorted(reminders)
    assert deadline.due_date in reminders
    assert len(reminders) == 5


def test_missing_tax_year_validation_error():
    profile = make_profile(tax_year=None)
    issues = client_mod.TaxReturnAssistantClient().validate_profile(profile)
    assert any(issue.code == "TAX_YEAR_MISSING" and issue.severity == "error" for issue in issues)


def test_negative_turnover_validation_error():
    profile = make_profile(annual_turnover_ils=-1)
    issues = client_mod.TaxReturnAssistantClient().validate_profile(profile)
    assert any(issue.code == "NEGATIVE_TURNOVER" for issue in issues)


def test_sensitive_notes_warning():
    profile = make_profile(notes="ID 123456789 bank 12-345-678")
    issues = client_mod.TaxReturnAssistantClient().validate_profile(profile)
    assert any(issue.code == "PERSONAL_DATA_RISK" for issue in issues)


def test_field_help_list_1301_contains_business_income():
    fields = client_mod.TaxReturnAssistantClient().get_field_help("1301")
    ids = [field.field_id for field in fields]
    assert "business_income" in ids


def test_field_help_specific_856_withholding_rate():
    field = client_mod.TaxReturnAssistantClient().get_field_help("856", "withholding_rate")
    assert field.label_he == "שיעור ניכוי במקור"
    assert "certificate" in field.description.lower()


def test_unknown_field_raises():
    with pytest.raises(client_mod.UnknownFieldError):
        client_mod.TaxReturnAssistantClient().get_field_help("856", "shoe_size")


def test_checklist_adds_foreign_income_warning():
    profile = make_profile(foreign_income=True)
    checklists = client_mod.TaxReturnAssistantClient().build_checklist(profile, ["1301"])
    assert any("Foreign income" in item for item in checklists[0].items)
    assert checklists[0].warnings


def test_generate_report_contains_sections():
    report = client_mod.TaxReturnAssistantClient().generate_report(make_profile(paid_suppliers=True))
    assert set(report) >= {"profile", "recommendation", "deadlines", "checklists", "validation"}
    assert "856" in report["recommendation"]["forms"]


def test_save_and_load_profile(tmp_path):
    path = tmp_path / "profile.json"
    client_mod.save_json(path, make_profile().to_dict())
    assert client_mod.load_profile(path).tax_year == 2025


def test_local_profile_store_create_get_delete(tmp_path):
    store = client_mod.LocalProfileStore(tmp_path / "profiles.json")
    client = client_mod.TaxReturnAssistantClient(profile_store=store)
    stored = client.create_profile(make_profile(), "sandbox")
    assert stored.profile_id in client.list_profile_ids()
    assert client.get_profile(stored.profile_id).profile.tax_year == 2025
    assert client.delete_profile(stored.profile_id) is True
    assert client.delete_profile(stored.profile_id) is False


def test_generate_report_by_id_adds_id_and_environment(tmp_path):
    store = client_mod.LocalProfileStore(tmp_path / "profiles.json")
    client = client_mod.TaxReturnAssistantClient(profile_store=store)
    stored = client.create_profile(make_profile(), "production")
    report = client.generate_report_by_id(stored.profile_id)
    assert report["id"] == stored.profile_id
    assert report["environment"] == "production"


def test_invalid_environment_rejected(tmp_path):
    store = client_mod.LocalProfileStore(tmp_path / "profiles.json")
    client = client_mod.TaxReturnAssistantClient(profile_store=store)
    with pytest.raises(client_mod.TaxAssistantError):
        client.create_profile(make_profile(), "staging")  # type: ignore[arg-type]


def test_default_profile_uses_previous_year():
    profile = client_mod.default_profile()
    assert profile.business_income is True
    assert isinstance(profile.tax_year, int)


def test_async_client_recommend_forms():
    async def run():
        rec = await client_mod.AsyncTaxReturnAssistantClient().recommend_forms(make_profile())
        return rec

    assert "1301" in [form.value for form in asyncio.run(run()).forms]


def test_async_store_round_trip(tmp_path):
    async def run():
        store = client_mod.LocalProfileStore(tmp_path / "profiles.json")
        async_client = client_mod.AsyncTaxReturnAssistantClient(
            client_mod.TaxReturnAssistantClient(profile_store=store)
        )
        stored = await async_client.create_profile(make_profile(), "sandbox")
        report = await async_client.generate_report_by_id(stored.profile_id)
        return report

    assert asyncio.run(run())["environment"] == "sandbox"


def test_cli_create_profile_then_report_chains_id(tmp_path, monkeypatch):
    monkeypatch.setenv("TAX_ASSISTANT_STATE_PATH", str(tmp_path / "profiles.json"))
    runner = CliRunner()
    create_result = runner.invoke(
        cli_mod.cli,
        [
            "create-profile",
            "--tax-year",
            "2025",
            "--annual-turnover-ils",
            "420000",
            "--paid-suppliers",
            "--env",
            "sandbox",
        ],
    )
    assert create_result.exit_code == 0, create_result.output
    profile_id = json.loads(create_result.output)["id"]
    report_result = runner.invoke(cli_mod.cli, ["report", "--profile-id", profile_id])
    assert report_result.exit_code == 0, report_result.output
    report = json.loads(report_result.output)
    assert report["id"] == profile_id
    assert "1301" in report["recommendation"]["forms"]


def test_cli_fields_json_output():
    result = CliRunner().invoke(cli_mod.cli, ["fields", "856", "withholding_rate"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["label_he"] == "שיעור ניכוי במקור"


def test_cli_deadline_reads_env_year(monkeypatch):
    monkeypatch.setenv("TAX_ASSISTANT_TAX_YEAR", "2025")
    result = CliRunner().invoke(cli_mod.cli, ["deadline", "1301", "--env", "production"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["due_date"] == "30/06/2026"
    assert data["environment"] == "production"


def test_cli_init_profile_and_recommend(tmp_path):
    profile_path = tmp_path / "profile.json"
    runner = CliRunner()
    init_result = runner.invoke(cli_mod.cli, ["init-profile", "--output", str(profile_path), "--tax-year", "2025"])
    assert init_result.exit_code == 0, init_result.output
    rec_result = runner.invoke(cli_mod.cli, ["recommend", "--profile", str(profile_path)])
    assert rec_result.exit_code == 0, rec_result.output
    assert "1301" in json.loads(rec_result.output)["forms"]


def test_cli_export_report(tmp_path):
    profile_path = tmp_path / "profile.json"
    output_path = tmp_path / "report.json"
    client_mod.save_json(profile_path, make_profile(paid_suppliers=True).to_dict())
    result = CliRunner().invoke(cli_mod.cli, ["export-report", "--profile", str(profile_path), "--output", str(output_path)])
    assert result.exit_code == 0, result.output
    assert "856" in json.loads(output_path.read_text(encoding="utf-8"))["recommendation"]["forms"]


def test_cli_list_and_delete_profiles(tmp_path, monkeypatch):
    monkeypatch.setenv("TAX_ASSISTANT_STATE_PATH", str(tmp_path / "profiles.json"))
    runner = CliRunner()
    created = json.loads(runner.invoke(cli_mod.cli, ["create-profile", "--tax-year", "2025"]).output)
    listed = json.loads(runner.invoke(cli_mod.cli, ["list-profiles"]).output)
    assert created["id"] in listed["ids"]
    deleted = json.loads(runner.invoke(cli_mod.cli, ["delete-profile", created["id"]]).output)
    assert deleted["deleted"] is True
