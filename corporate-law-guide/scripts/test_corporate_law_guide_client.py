from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

from corporate_law_guide import CorporateLawGuideClient, WorkflowError


ROOT = Path(__file__).resolve().parent
CLI_PATH = ROOT / "corporate-law-guide-cli.py"


@pytest.fixture()
def client():
    return CorporateLawGuideClient(environment="sandbox")


def test_validate_company_number_valid(client):
    result = client.validate_company_number("516000000")
    assert result.valid
    assert result.normalized == "516000000"


def test_validate_company_number_strips_separators(client):
    result = client.validate_company_number("516-000-000")
    assert result.valid
    assert result.normalized == "516000000"


def test_validate_company_number_invalid(client):
    result = client.validate_company_number("123")
    assert not result.valid
    assert "9-digit" in result.message


def test_normalize_ddmmyyyy_slash(client):
    result = client.normalize_date("02/06/2026")
    assert result.valid
    assert result.normalized == "02/06/2026"


def test_normalize_ddmmyyyy_dash(client):
    result = client.normalize_date("02-06-2026")
    assert result.valid
    assert result.normalized == "02/06/2026"


def test_normalize_iso_to_israeli_date(client):
    result = client.normalize_date("2026-06-02")
    assert result.valid
    assert result.normalized == "02/06/2026"


def test_normalize_bad_date(client):
    result = client.normalize_date("31/02/2026")
    assert not result.valid


def test_create_case_returns_case_id(client):
    case = client.create_case("software platform", 2)
    assert case.case_id.startswith("clg_")
    assert case.environment == "sandbox"


def test_get_case_roundtrip(client):
    case = client.create_case("software platform", 2)
    loaded = client.get_case(case.case_id)
    assert loaded.business_activity == "software platform"


def test_create_case_invalid_company_number(client):
    with pytest.raises(WorkflowError):
        client.create_case("software", 1, company_number="123")


def test_classify_low_risk_individual(client):
    result = client.classify_entity_need("graphic design", 1, "low", False)
    assert result.recommendation == "individual_business"


def test_classify_high_risk_company(client):
    result = client.classify_entity_need("cybersecurity consulting", 1, "high", False)
    assert result.recommendation == "private_company_limited_by_shares"


def test_classify_fundraising_company(client):
    result = client.classify_entity_need("software", 2, "medium", True)
    assert result.recommendation == "private_company_limited_by_shares"


def test_classify_regulated_review(client):
    result = client.classify_entity_need("financial services", 1, "medium", False, regulated_activity=True)
    assert result.recommendation == "regulated_activity_review_required"
    assert result.warnings


def test_classify_non_profit(client):
    result = client.classify_entity_need("community education", 3, non_profit_purpose=True)
    assert result.recommendation == "non_profit_structure"


def test_classify_requires_owner(client):
    with pytest.raises(WorkflowError):
        client.classify_entity_need("software", 0)


def test_classify_requires_activity(client):
    with pytest.raises(WorkflowError):
        client.classify_entity_need("", 1)


def test_async_classify(client):
    result = asyncio.run(client.aclassify_entity_need("software", 2, fundraising_plan=True))
    assert result.recommendation == "private_company_limited_by_shares"


def test_async_create_case(client):
    case = asyncio.run(client.acreate_case("software", 2))
    assert case.case_id.startswith("clg_")


def test_incorporation_checklist_has_expected_steps(client):
    result = client.build_incorporation_checklist(2, "software")
    titles = [item.title for item in result.items]
    assert "Prepare company names" in titles
    assert any("Deadlock" in item for item in result.professional_review_triggers)


def test_incorporation_regulated_blocker(client):
    result = client.build_incorporation_checklist(1, "payments", regulated_activity=True)
    assert result.blockers


def test_annual_report_invalid_company_number_blocker(client):
    result = client.annual_report_checklist("123", 2026)
    assert result.blockers


def test_annual_report_with_changes_trigger(client):
    result = client.annual_report_checklist("516000000", 2026, has_changes=True)
    assert result.professional_review_triggers
    assert any("Reconcile changes" == item.title for item in result.items)


def test_share_transfer_seller_balance_blocker(client):
    result = client.share_transfer_checklist(10, 20)
    assert result.blockers


def test_share_transfer_tax_trigger(client):
    result = client.share_transfer_checklist(100, 10, tax_review_done=False)
    assert "Tax review before closing" in result.professional_review_triggers


def test_share_transfer_family_new_shareholder_triggers(client):
    result = client.share_transfer_checklist(100, 10, family_transfer=True, new_shareholder=True, tax_review_done=True)
    assert any("Permitted" in item for item in result.professional_review_triggers)
    assert any("adherence" in item.lower() for item in result.professional_review_triggers)


def test_director_change_bank_trigger(client):
    result = client.director_change_checklist("appoint", bank_signing_change=True)
    assert any("Bank" in item for item in result.professional_review_triggers)
    assert any(item.title == "Update bank authority" for item in result.items)


def test_director_change_invalid_action(client):
    with pytest.raises(WorkflowError):
        client.director_change_checklist("invalid")


def test_shareholder_scan_equal_deadlock(client):
    result = client.shareholder_agreement_scan(2, equal_holdings=True)
    assert any("deadlock" in item.lower() for item in result.professional_review_triggers)


def test_shareholder_scan_investor_trigger(client):
    result = client.shareholder_agreement_scan(3, investor_round=True)
    assert any("Investor" in item for item in result.professional_review_triggers)


def test_shareholder_scan_family_trigger(client):
    result = client.shareholder_agreement_scan(3, family_company=True)
    assert any("Inheritance" in item for item in result.professional_review_triggers)


def test_due_diligence_contains_intellectual_property(client):
    result = client.due_diligence_checklist()
    assert any("intellectual" in item.title.lower() or "intellectual" in item.details.lower() for item in result.items)


def test_dormant_cleanup(client):
    result = client.dormant_cleanup_checklist()
    assert result.action == "dormant_cleanup"
    assert result.professional_review_triggers


def test_case_checklist_for_incorporation(client):
    case = client.create_case("software platform", 2)
    result = client.checklist_for_case(case.case_id, "incorporation")
    assert result.case_id == case.case_id


def test_case_checklist_requires_company_number_for_annual(client):
    case = client.create_case("software platform", 2)
    with pytest.raises(WorkflowError):
        client.checklist_for_case(case.case_id, "annual_report", year=2026)


def test_markdown_render(client):
    result = client.director_change_checklist("resign")
    md = result.to_markdown()
    assert "# Director Change Checklist" in md
    assert "Update directors register" in md


def test_json_render_contains_hebrew_safe(client):
    result = client.validate_company_number("516000000")
    rendered = client.render_json(result)
    assert json.loads(rendered)["valid"] is True


def test_save_markdown(tmp_path, client):
    result = client.annual_report_checklist("516000000", 2026)
    path = client.save_markdown(result, tmp_path / "annual.md")
    assert path.exists()
    assert "Annual Report Checklist" in path.read_text(encoding="utf-8")


def test_cli_validate_company_number():
    output = subprocess.check_output(
        [sys.executable, str(CLI_PATH), "--env", "sandbox", "validate-company-number", "516000000"],
        text=True,
        cwd=ROOT.parent,
        timeout=10,
    )
    assert '"valid": true' in output


def test_cli_classify_company():
    output = subprocess.check_output(
        [
            sys.executable,
            str(CLI_PATH),
            "--env",
            "sandbox",
            "classify",
            "--owners",
            "2",
            "--liability-risk",
            "high",
            "--fundraising",
            "yes",
            "--activity",
            "software",
        ],
        text=True,
        cwd=ROOT.parent,
        timeout=10,
    )
    assert "private_company_limited_by_shares" in output


def test_cli_annual_report_markdown():
    output = subprocess.check_output(
        [
            sys.executable,
            str(CLI_PATH),
            "--env",
            "sandbox",
            "annual-report",
            "--company-number",
            "516000000",
            "--year",
            "2026",
            "--output",
            "markdown",
        ],
        text=True,
        cwd=ROOT.parent,
        timeout=10,
    )
    assert "Annual Report Checklist" in output


def test_cli_create_case_and_use_id():
    created = subprocess.check_output(
        [
            sys.executable,
            str(CLI_PATH),
            "--env",
            "sandbox",
            "create-case",
            "--owners",
            "2",
            "--activity",
            "software platform",
        ],
        text=True,
        cwd=ROOT.parent,
        timeout=10,
    )
    case_id = json.loads(created)["case_id"]
    output = subprocess.check_output(
        [
            sys.executable,
            str(CLI_PATH),
            "--env",
            "sandbox",
            "case-checklist",
            "--case-id",
            case_id,
            "--action",
            "incorporation",
            "--owners",
            "2",
            "--activity",
            "software platform",
        ],
        text=True,
        cwd=ROOT.parent,
        timeout=10,
    )
    assert case_id in output


def test_decision_to_dict(client):
    result = client.classify_entity_need("software", 2, fundraising_plan=True)
    payload = result.to_dict()
    assert "next_steps" in payload
    assert isinstance(payload["next_steps"], list)



def test_regulatory_facts_payload(client):
    payload = client.regulatory_facts_payload()
    assert payload["validated_on"] == "02/06/2026"
    assert payload["vat_standard_rate"] == 0.18
    assert payload["exempt_dealer_threshold_2026_ils"] == 122833
    assert payload["company_annual_fee_2026"]["regular_amount_ils"] == 1777


def test_get_regulatory_facts(client):
    facts = client.get_regulatory_facts()
    keys = {fact.key for fact in facts}
    assert "vat_standard_rate" in keys
    assert all(fact.validated_on == "02/06/2026" for fact in facts)


def test_cli_facts():
    output = subprocess.check_output(
        [sys.executable, str(CLI_PATH), "--env", "sandbox", "facts"],
        text=True,
        cwd=ROOT.parent,
        timeout=10,
    )
    payload = json.loads(output)
    assert payload["vat_standard_rate"] == 0.18
