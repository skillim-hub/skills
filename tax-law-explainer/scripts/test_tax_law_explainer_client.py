from __future__ import annotations

import json
from pathlib import Path

import pytest

from tax_law_explainer import (
    CURRENT_REFERENCE_VALUES,
    InvalidLanguageError,
    TaxLawExplainerClient,
    UnknownTopicError,
    UnknownWorkflowError,
    load_facts_json,
    scenario_payload,
)


def test_topics_count() -> None:
    assert len(TaxLawExplainerClient.topics()) == 10


def test_workflows_count() -> None:
    assert len(TaxLawExplainerClient.workflows()) == 10


def test_reference_values_exposed() -> None:
    values = TaxLawExplainerClient.reference_values()
    assert values["standard_vat_rate_percent"] == 18
    assert values["exempt_dealer_threshold_2026_nis"] == 122833


def test_reference_constant_matches_method() -> None:
    assert CURRENT_REFERENCE_VALUES["real_estate_declaration_deadline_days"] == TaxLawExplainerClient.reference_values()["real_estate_declaration_deadline_days"]


def test_installable_package_import() -> None:
    from tax_law_explainer import TaxLawExplainerClient as ImportedClient
    assert ImportedClient().topics()


def test_underscored_script_wrapper_exists() -> None:
    wrapper = Path(__file__).with_name("tax_law_explainer_client.py")
    assert wrapper.exists()
    assert "tax_law_explainer" in wrapper.read_text(encoding="utf-8")


def test_hyphenated_client_deleted() -> None:
    assert not Path(__file__).with_name("tax-law-explainer-client.py").exists()


def test_vat_registration_complete() -> None:
    facts = {"activity_type": "design", "profession": "designer", "annual_turnover": 90000, "start_date": "02/06/2026"}
    result = TaxLawExplainerClient().explain("vat-registration", facts=facts)
    assert result.missing_facts == []
    assert "VAT Law" in result.legal_areas


def test_vat_registration_missing_facts() -> None:
    result = TaxLawExplainerClient().explain("vat-registration", facts={"profession": "designer"})
    assert "annual_turnover" in result.missing_facts
    assert result.professional_help is True


def test_foreign_client_high_risk() -> None:
    facts = {"client_residence": "US", "beneficiary": "foreign company", "use_location": "outside Israel", "contract": "yes"}
    result = TaxLawExplainerClient().explain("foreign-client-vat", facts=facts)
    assert result.professional_help is True


def test_expense_deductibility_documents() -> None:
    result = TaxLawExplainerClient().explain("expense-deductibility", facts={"expense_type": "internet", "business_purpose": "work", "has_invoice": True})
    assert any("Allocation" in doc for doc in result.documents)


def test_hebrew_summary() -> None:
    result = TaxLawExplainerClient(default_language="he").explain("purchase-tax", facts={})
    assert "מס רכישה" in result.summary


def test_invalid_language_constructor() -> None:
    with pytest.raises(InvalidLanguageError):
        TaxLawExplainerClient(default_language="fr")


def test_invalid_language_call() -> None:
    with pytest.raises(InvalidLanguageError):
        TaxLawExplainerClient().explain("vat-registration", language="fr")


def test_unknown_topic() -> None:
    with pytest.raises(UnknownTopicError):
        TaxLawExplainerClient().explain("unknown")


def test_unknown_workflow() -> None:
    with pytest.raises(UnknownWorkflowError):
        TaxLawExplainerClient().checklist("unknown")


def test_validate_real_estate_missing() -> None:
    result = TaxLawExplainerClient().validate_facts("real-estate-sale", {"asset_type": "residential_apartment"})
    assert not result.valid
    assert "purchase_price" in result.missing


def test_validate_complete_purchase_tax() -> None:
    facts = {"asset_type": "apartment", "purchaser_status": "resident", "owns_other_apartment": False, "purchase_price": 2000000}
    assert TaxLawExplainerClient().validate_facts("purchase-tax", facts).valid


def test_checklist_freelancer() -> None:
    assert TaxLawExplainerClient().checklist("freelancer-onboarding")["steps"][0].startswith("Classify")


def test_checklist_hebrew() -> None:
    result = TaxLawExplainerClient(default_language="he").checklist("vat-documents")
    assert "מע״מ" in " ".join(result["steps"])


@pytest.mark.asyncio
async def test_async_explain() -> None:
    result = await TaxLawExplainerClient().aexplain("withholding-tax", facts={"payer": "A", "payee": "B", "payment_type": "services", "certificate_valid": True})
    assert result.topic == "withholding-tax"


@pytest.mark.asyncio
async def test_async_validate() -> None:
    result = await TaxLawExplainerClient().avalidate_facts("rental-income", {"property_type": "residential"})
    assert not result.valid


@pytest.mark.asyncio
async def test_async_checklist() -> None:
    result = await TaxLawExplainerClient().achecklist("annual-return")
    assert result["workflow"] == "annual-return"


def test_to_json_roundtrip() -> None:
    result = TaxLawExplainerClient().explain("rental-income", facts={"property_type": "residential", "monthly_rent": 5200, "owner_type": "individual"})
    assert json.loads(result.to_json())["topic"] == "rental-income"


def test_load_facts_json_inline() -> None:
    assert load_facts_json('{"a": 1}') == {"a": 1}


def test_load_facts_json_file(tmp_path: Path) -> None:
    path = tmp_path / "facts.json"
    path.write_text('{"b": 2}', encoding="utf-8")
    assert load_facts_json(path) == {"b": 2}


def test_load_facts_json_rejects_array() -> None:
    with pytest.raises(TypeError):
        load_facts_json("[1, 2]")


def test_scenario_payload_known() -> None:
    assert scenario_payload("foreign_client")["topic"] == "foreign-client-vat"


def test_scenario_payload_unknown() -> None:
    with pytest.raises(KeyError):
        scenario_payload("missing")


def test_export_scenario(tmp_path: Path) -> None:
    output = tmp_path / "scenario.json"
    path = TaxLawExplainerClient().export_scenario("rental_income", output)
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8"))["topic"] == "rental-income"


def test_compliance_warning() -> None:
    result = TaxLawExplainerClient().explain("expense-deductibility", facts={"backdating_requested": True})
    assert any("backdating" in warning.lower() for warning in result.warnings)


def test_all_required_fact_topics_have_legal_area() -> None:
    for topic in TaxLawExplainerClient.topics():
        assert TaxLawExplainerClient().explain(topic).legal_areas
