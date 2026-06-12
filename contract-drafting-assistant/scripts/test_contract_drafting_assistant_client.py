from __future__ import annotations

import asyncio
import json

import pytest

import contract_drafting_assistant_client as client
import contract_drafting_assistant_cli as cli_mod


def test_format_ils_integer():
    assert client.format_ils(12000) == "₪12,000"


def test_format_ils_decimal():
    assert client.format_ils(99.5) == "₪99.50"


def test_calculate_vat_default():
    assert client.calculate_vat(100)["vat"] == 18.0
    assert client.calculate_vat(100)["total"] == 118.0


def test_calculate_vat_custom_rate():
    assert client.calculate_vat(200, 0.1) == {"net": 200, "vat": 20.0, "total": 220.0, "rate": 0.1}


def test_calculate_vat_rejects_negative():
    with pytest.raises(ValueError):
        client.calculate_vat(-1)


def test_calculate_vat_rejects_bad_rate():
    with pytest.raises(ValueError):
        client.calculate_vat(100, 1.5)


def test_normalize_israeli_id_pads():
    assert client.normalize_israeli_id("12345678") == "012345678"


def test_validate_known_valid_id():
    assert client.validate_israeli_id("123456782") is True


def test_validate_known_invalid_id():
    assert client.validate_israeli_id("123456789") is False


def test_id_rejects_letters():
    with pytest.raises(ValueError, match="id_not_numeric"):
        client.normalize_israeli_id("12A")


def test_parse_ddmmyyyy_slash():
    assert client.format_date_ddmmyyyy("15/07/2026") == "15/07/2026"


def test_parse_iso_date_to_ddmmyyyy():
    assert client.format_date_ddmmyyyy("2026-07-15") == "15/07/2026"


def test_terms_from_dict():
    data = {
        "contract_type": "service_agreement",
        "language": "he",
        "parties": [{"name": "A"}, {"name": "B"}],
        "price_nis": "1000",
        "vat_included": "false",
    }
    terms = client.ContractTerms.from_dict(data)
    assert terms.contract_type == client.ContractType.SERVICE_AGREEMENT
    assert terms.price_nis == 1000.0
    assert terms.vat_included is False
    assert len(terms.parties) == 2


def test_missing_parties_high_risk():
    findings = client.scan_risks(client.ContractTerms())
    assert any(f.code == "missing_parties" and f.severity == "high" for f in findings)


def test_vat_ambiguous_risk():
    terms = client.ContractTerms(parties=[client.Party("A"), client.Party("B")], price_nis=1000)
    findings = client.scan_risks(terms)
    assert any(f.code == "vat_ambiguous" for f in findings)


def test_consumer_risk():
    terms = client.ContractTerms(
        contract_type=client.ContractType.CONSUMER_SERVICE,
        parties=[client.Party("A"), client.Party("B")],
        price_nis=650,
        vat_included=True,
    )
    findings = client.scan_risks(terms)
    assert any(f.code == "consumer_cancellation_review" for f in findings)


def test_privacy_sensitive_high():
    terms = client.ContractTerms(
        parties=[client.Party("A"), client.Party("B")],
        price_nis=1000,
        vat_included=False,
        personal_data=True,
        sensitive_data=True,
    )
    findings = client.scan_risks(terms)
    assert any(f.code == "privacy_schedule_required" and f.severity == "high" for f in findings)


def test_ip_ambiguous_for_software():
    terms = client.ContractTerms(
        parties=[client.Party("A"), client.Party("B")],
        description="software website development",
        price_nis=1000,
        vat_included=False,
    )
    findings = client.scan_risks(terms)
    assert any(f.code == "ip_ownership_ambiguous" for f in findings)


def test_worker_classification_risk_from_notes():
    terms = client.ContractTerms(
        contract_type=client.ContractType.FREELANCE_AGREEMENT,
        parties=[client.Party("A"), client.Party("B")],
        price_nis=1000,
        vat_included=False,
        notes=["fixed hours and company equipment"],
    )
    findings = client.scan_risks(terms)
    assert any(f.code == "worker_classification_risk" for f in findings)


def test_regulated_activity_high():
    terms = client.ContractTerms(
        parties=[client.Party("A"), client.Party("B")],
        price_nis=1000,
        vat_included=False,
        regulated_activity=True,
    )
    findings = client.scan_risks(terms)
    assert any(f.code == "regulated_activity" and f.severity == "high" for f in findings)


def test_hebrew_render_contains_vat_and_date():
    terms = client.sample_terms("freelance-design", "he")
    result = client.ContractDraftingClient().draft(terms)
    assert "₪12,000" in result.contract_markdown
    assert "02/06/2026" in result.contract_markdown
    assert "מע״מ" in result.contract_markdown


def test_english_render_contains_governing_law():
    terms = client.sample_terms("freelance-design", "en")
    result = client.ContractDraftingClient().draft(terms)
    assert "State of Israel" in result.contract_markdown
    assert "Graphic Design Services Agreement" in result.contract_markdown


def test_draft_result_json():
    terms = client.sample_terms("consumer-repair", "he")
    result = client.ContractDraftingClient().draft(terms)
    parsed = json.loads(result.to_json())
    assert "contract_markdown" in parsed
    assert isinstance(parsed["findings"], list)


def test_risk_level_high_medium_low():
    high = [client.RiskFinding("x", "high", "m", "f")]
    medium = [client.RiskFinding("x", "medium", "m", "f")]
    assert client.classify_risk_level(high) == "high"
    assert client.classify_risk_level(medium) == "medium"
    assert client.classify_risk_level([]) == "info"


def test_save_and_load_json(tmp_path):
    data = {
        "contract_type": "service_agreement",
        "language": "en",
        "parties": [{"name": "Provider"}, {"name": "Customer"}],
        "price_nis": 500,
        "vat_included": True,
    }
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    terms = client.load_terms(path)
    result = client.ContractDraftingClient().draft(terms)
    out = tmp_path / "draft.md"
    client.save_draft(result, out)
    assert out.read_text(encoding="utf-8").startswith("## Assumptions")


def test_async_validate():
    terms = client.sample_terms("freelance-design", "he")
    findings = asyncio.run(client.ContractDraftingClient().async_validate(terms))
    assert isinstance(findings, list)


def test_async_draft():
    terms = client.sample_terms("nda", "en")
    result = asyncio.run(client.ContractDraftingClient().async_draft(terms))
    assert "Non-Disclosure" in result.contract_markdown


def test_scenario_names():
    assert {"freelance-design", "consumer-repair", "nda"}.issubset(set(client.scenario_names()))


def test_public_method_count_expected():
    public_methods = [name for name in dir(client.ContractDraftingClient) if not name.startswith("_")]
    assert len(public_methods) >= 5


def test_cli_vat_command():
    from typer.testing import CliRunner

    result = CliRunner().invoke(cli_mod.app, ["vat", "100"])
    assert result.exit_code == 0
    assert '"vat": 18.0' in result.stdout
    assert '"env": "sandbox"' in result.stdout


def test_cli_vat_command_env_production():
    from typer.testing import CliRunner

    result = CliRunner().invoke(cli_mod.app, ["vat", "100", "--env", "production"])
    assert result.exit_code == 0
    assert '"env": "production"' in result.stdout


def test_cli_scenario_command_hebrew():
    from typer.testing import CliRunner

    result = CliRunner().invoke(cli_mod.app, ["scenario", "consumer-repair", "--language", "he"])
    assert result.exit_code == 0
    assert "תיקון מקרר" in result.stdout
    assert "הוראות צרכניות" in result.stdout


def test_cli_rejects_bad_env():
    from typer.testing import CliRunner

    result = CliRunner().invoke(cli_mod.app, ["vat", "100", "--env", "staging"])
    assert result.exit_code == 2
    assert "env must be sandbox or production" in result.stdout


def test_cli_new_json_output(tmp_path):
    from typer.testing import CliRunner

    data = {
        "contract_type": "service_agreement",
        "language": "en",
        "parties": [{"name": "Provider"}, {"name": "Customer"}],
        "price_nis": 1000,
        "vat_included": False,
        "description": "consulting services",
    }
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = CliRunner().invoke(cli_mod.app, ["new", str(path), "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert "Service Agreement" in parsed["contract_markdown"]
    assert parsed["env"] == "sandbox"


def test_cli_validate_id_success():
    from typer.testing import CliRunner

    result = CliRunner().invoke(cli_mod.app, ["validate-id", "123456782"])
    assert result.exit_code == 0
    assert '"valid": true' in result.stdout


def test_cli_list_scenarios():
    from typer.testing import CliRunner

    result = CliRunner().invoke(cli_mod.app, ["list-scenarios"])
    assert result.exit_code == 0
    assert "freelance-design" in result.stdout


def test_cli_check_json_output(tmp_path):
    from typer.testing import CliRunner

    data = {
        "contract_type": "service_agreement",
        "language": "en",
        "parties": [{"name": "Provider"}, {"name": "Customer"}],
        "price_nis": 1000,
        "vat_included": None,
    }
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = CliRunner().invoke(cli_mod.app, ["check", str(path), "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["env"] == "sandbox"
    assert any(item["code"] == "vat_ambiguous" for item in parsed["findings"])
