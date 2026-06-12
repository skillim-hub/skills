from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from privacy_compliance_checker import (
    AsyncPrivacyComplianceCheckerClient,
    LawfulBasis,
    PrivacyComplianceCheckerClient,
    SecurityLevel,
    assess,
    determine_gdpr_applicability,
    determine_security_level,
    get_scenario,
    list_scenarios,
)
from privacy_compliance_checker.cli import cli


def test_scenarios_list_contains_required_cases() -> None:
    names = list_scenarios()
    assert "customer-club" in names
    assert "clinic" in names
    assert len(names) >= 5


def test_get_scenario_returns_copy() -> None:
    first = get_scenario("customer-club")
    second = get_scenario("customer-club")
    first["business_name"] = "Changed"
    assert second["business_name"] != "Changed"


def test_unknown_scenario_raises() -> None:
    with pytest.raises(ValueError):
        get_scenario("missing")


def test_basic_security_for_small_freelancer() -> None:
    data = get_scenario("freelancer-crm")
    assert determine_security_level(PrivacyComplianceCheckerClient().assess(data).input) is SecurityLevel.BASIC


def test_medium_security_for_clinic_without_large_scale_trigger() -> None:
    data = get_scenario("clinic")
    result = PrivacyComplianceCheckerClient().assess(data)
    assert result.security_level is SecurityLevel.MEDIUM


def test_high_security_for_large_sensitive_database() -> None:
    data = get_scenario("clinic")
    data["record_count"] = 100000
    result = PrivacyComplianceCheckerClient().assess(data)
    assert result.security_level is SecurityLevel.HIGH


def test_high_security_for_many_authorized_users() -> None:
    data = get_scenario("clinic")
    data["authorized_users"] = 101
    result = PrivacyComplianceCheckerClient().assess(data)
    assert result.security_level is SecurityLevel.HIGH


def test_large_non_sensitive_database_is_not_medium_by_count_only() -> None:
    payload = {"business_name": "Large non-sensitive list", "record_count": 50000, "authorized_users": 3, "lawful_basis": "contract"}
    result = PrivacyComplianceCheckerClient().assess(payload)
    assert result.security_level is SecurityLevel.BASIC


def test_medium_security_for_marketing_database() -> None:
    payload = {
        "business_name": "Marketing list",
        "record_count": 9000,
        "authorized_users": 2,
        "direct_marketing": True,
        "purposes": ["offers"],
        "lawful_basis": "consent",
    }
    result = PrivacyComplianceCheckerClient().assess(payload)
    assert result.security_level is SecurityLevel.MEDIUM


def test_gdpr_applicable_for_eu_targeting() -> None:
    data = get_scenario("saas-transfer")
    result = PrivacyComplianceCheckerClient().assess(data)
    assert result.gdpr_applicable is True


def test_gdpr_not_applicable_for_local_only() -> None:
    data = get_scenario("freelancer-crm")
    assert determine_gdpr_applicability(PrivacyComplianceCheckerClient().assess(data).input) is False


def test_unknown_fields_raise() -> None:
    with pytest.raises(ValueError):
        PrivacyComplianceCheckerClient().assess({"business_name": "X", "extra": True})


def test_invalid_record_count_raises() -> None:
    with pytest.raises(ValueError):
        PrivacyComplianceCheckerClient().assess({"record_count": -1})


def test_invalid_lawful_basis_raises() -> None:
    with pytest.raises(ValueError):
        PrivacyComplianceCheckerClient().assess({"lawful_basis": "none"})


def test_validate_returns_warnings() -> None:
    response = PrivacyComplianceCheckerClient().validate({"business_name": "X"})
    assert response["valid"] is True
    assert response["warnings"]


def test_json_output_preserves_hebrew() -> None:
    result = PrivacyComplianceCheckerClient().assess({"business_name": "קליניקה", "lawful_basis": "consent"})
    assert "קליניקה" in result.to_json()


def test_markdown_contains_checklist() -> None:
    result = PrivacyComplianceCheckerClient().assess(get_scenario("customer-club"))
    markdown = result.to_markdown()
    assert "## Checklist" in markdown
    assert "DM-001" in markdown


def test_convenience_assess_function() -> None:
    result = assess(get_scenario("freelancer-crm"))
    assert result.input.lawful_basis is LawfulBasis.CONTRACT


def test_create_and_get_record(tmp_path: Path) -> None:
    client = PrivacyComplianceCheckerClient(state_dir=tmp_path)
    response = client.create(get_scenario("customer-club"))
    saved = client.get(response["id"])
    assert saved["id"] == response["id"]
    assert saved["input"]["business_name"] == "Neighborhood customer club"


def test_update_record(tmp_path: Path) -> None:
    client = PrivacyComplianceCheckerClient(state_dir=tmp_path)
    response = client.create(get_scenario("freelancer-crm"))
    updated = client.update(response["id"], {"direct_marketing": True})
    saved = client.get(updated["id"])
    codes = {finding["code"] for finding in saved["findings"]}
    assert "DM-001" in codes


def test_list_records(tmp_path: Path) -> None:
    client = PrivacyComplianceCheckerClient(state_dir=tmp_path)
    client.create(get_scenario("customer-club"))
    client.create(get_scenario("clinic"))
    records = client.list_records()
    assert len(records) == 2


def test_delete_record(tmp_path: Path) -> None:
    client = PrivacyComplianceCheckerClient(state_dir=tmp_path)
    response = client.create(get_scenario("breach"))
    assert client.delete(response["id"])["deleted"] is True
    with pytest.raises(FileNotFoundError):
        client.get(response["id"])


def test_export_report_markdown(tmp_path: Path) -> None:
    client = PrivacyComplianceCheckerClient(state_dir=tmp_path)
    response = client.create(get_scenario("saas-transfer"))
    report = client.export_report(response["id"], "markdown")
    assert "Privacy compliance assessment" in report


def test_make_checklist_returns_items() -> None:
    items = PrivacyComplianceCheckerClient().make_checklist(get_scenario("clinic"))
    assert any(item["area"] == "security" for item in items)


@pytest.mark.asyncio
async def test_async_assess() -> None:
    result = await AsyncPrivacyComplianceCheckerClient().assess(get_scenario("customer-club"))
    assert result.score <= 100


@pytest.mark.asyncio
async def test_async_create_and_get(tmp_path: Path) -> None:
    client = AsyncPrivacyComplianceCheckerClient(state_dir=tmp_path)
    response = await client.create(get_scenario("clinic"))
    saved = await client.get(response["id"])
    assert saved["security_level"] == "medium"


@pytest.mark.asyncio
async def test_async_update_and_list(tmp_path: Path) -> None:
    client = AsyncPrivacyComplianceCheckerClient(state_dir=tmp_path)
    response = await client.create(get_scenario("freelancer-crm"))
    await client.update(response["id"], {"uses_tracking": True})
    records = await client.list_records()
    assert len(records) == 1


def test_cli_template_outputs_json() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["template", "--scenario", "clinic"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["sector"] == "clinic"


def test_cli_assess_scenario_markdown() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["assess", "--scenario", "customer-club", "--format", "markdown"])
    assert result.exit_code == 0
    assert "Privacy compliance assessment" in result.output


def test_cli_create_then_get_chained(tmp_path: Path) -> None:
    runner = CliRunner()
    create = runner.invoke(cli, ["--state-dir", str(tmp_path), "create", "--scenario", "customer-club"])
    assert create.exit_code == 0
    assessment_id = json.loads(create.output)["id"]
    get = runner.invoke(cli, ["--state-dir", str(tmp_path), "get", assessment_id, "--format", "json"])
    assert get.exit_code == 0
    assert json.loads(get.output)["id"] == assessment_id


def test_cli_validate_file(tmp_path: Path) -> None:
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(get_scenario("freelancer-crm")), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", str(path)])
    assert result.exit_code == 0
    assert json.loads(result.output)["valid"] is True


def test_cli_checklist_json(tmp_path: Path) -> None:
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(get_scenario("clinic")), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(cli, ["checklist", str(path), "--format", "json"])
    assert result.exit_code == 0
    assert isinstance(json.loads(result.output), list)


def test_cross_border_finding_for_non_adequate_destination() -> None:
    result = PrivacyComplianceCheckerClient().assess(
        {
            "business_name": "Transfer case",
            "record_count": 100,
            "lawful_basis": "contract",
            "purposes": ["support"],
            "cross_border": True,
            "destinations": ["United States"],
            "eu_data_subjects": True,
        }
    )
    finding = next(item for item in result.findings if item.code == "XFER-001")
    assert finding.severity.value == "critical"


def test_breach_scenario_has_incident_item() -> None:
    result = PrivacyComplianceCheckerClient().assess(get_scenario("breach"))
    assert result.checklist[0].id == "IR-010"


def test_processor_contract_warning() -> None:
    result = PrivacyComplianceCheckerClient().assess(get_scenario("clinic"))
    assert any(finding.code == "PROC-001" for finding in result.findings)


def test_retention_recommendation_mentions_months() -> None:
    result = PrivacyComplianceCheckerClient().assess(get_scenario("customer-club"))
    assert "36 months" in result.retention_recommendation


def test_export_json_round_trip(tmp_path: Path) -> None:
    client = PrivacyComplianceCheckerClient(state_dir=tmp_path)
    response = client.create(get_scenario("customer-club"))
    exported = client.export_report(response["id"], "json")
    assert json.loads(exported)["id"] == response["id"]


def test_invalid_environment_raises() -> None:
    with pytest.raises(ValueError):
        PrivacyComplianceCheckerClient(environment="staging")


def test_public_imports_work() -> None:
    import privacy_compliance_checker as pcc

    assert hasattr(pcc, "PrivacyComplianceCheckerClient")
    assert callable(pcc.assess)
