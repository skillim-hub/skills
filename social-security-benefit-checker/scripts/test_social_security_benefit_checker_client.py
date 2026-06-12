from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from social_security_benefit_checker import (
    ApplicantProfile,
    BenefitType,
    EmploymentStatus,
    HouseholdType,
    LocalProfileStore,
    SocialSecurityBenefitChecker,
    TerminationReason,
    check_file,
    check_profile,
    ils,
    parse_date,
)


def make_checker(tmp_path: Path) -> SocialSecurityBenefitChecker:
    store = LocalProfileStore(directory=tmp_path, environment="sandbox")
    return SocialSecurityBenefitChecker(environment="sandbox", store=store)


def base_profile(**overrides):
    data = {
        "age": 38,
        "resident": True,
        "employment_status": EmploymentStatus.UNEMPLOYED.value,
        "monthly_income": 8000,
        "children_count": 2,
        "household_type": HouseholdType.SINGLE_PARENT.value,
        "qualifying_months": 14,
        "termination_reason": TerminationReason.LAID_OFF.value,
        "registered_employment_service": True,
        "birth_dates": ["10/01/2017", "15/08/2020"],
    }
    data.update(overrides)
    return ApplicantProfile.from_mapping(data)


def test_profile_from_mapping_ignores_unknown_fields():
    profile = ApplicantProfile.from_mapping({"age": 30, "resident": True, "unknown": "ignored"})
    assert profile.age == 30
    assert profile.resident is True


def test_profile_children_alias():
    profile = ApplicantProfile.from_mapping({"age": 30, "resident": True, "children": 3})
    assert profile.children_count == 3


def test_profile_single_parent_alias():
    profile = ApplicantProfile.from_mapping({"age": 30, "resident": True, "single_parent": True})
    assert profile.household_type == HouseholdType.SINGLE_PARENT.value


def test_validation_rejects_bad_age():
    profile = base_profile(age=130)
    assert "AGE_OUT_OF_RANGE" in profile.validate()


def test_validation_rejects_negative_income():
    profile = base_profile(monthly_income=-1)
    assert "MONTHLY_INCOME_NEGATIVE" in profile.validate()


def test_validation_rejects_bad_percent():
    profile = base_profile(medical_disability_percent=130)
    assert "MEDICAL_DISABILITY_PERCENT_OUT_OF_RANGE" in profile.validate()


def test_parse_date_supports_israeli_slashes():
    assert parse_date("31/12/2025").day == 31


def test_parse_date_supports_iso():
    assert parse_date("2025-12-31").year == 2025


def test_parse_date_rejects_unknown():
    with pytest.raises(ValueError):
        parse_date("12.31.2025")


def test_ils_format():
    assert ils(12345) == "₪12,345"


def test_unemployment_likely_eligible(tmp_path):
    result = make_checker(tmp_path).check_unemployment(base_profile())
    assert result.status == "likely_eligible"
    assert result.eligible is True
    assert result.estimated_monthly_ils_max is not None


def test_unemployment_requires_residency(tmp_path):
    result = make_checker(tmp_path).check_unemployment(base_profile(resident=False))
    assert result.status == "not_likely"


def test_unemployment_missing_registration(tmp_path):
    result = make_checker(tmp_path).check_unemployment(base_profile(registered_employment_service=False))
    assert result.status == "insufficient_information"
    assert "EMPLOYMENT_SERVICE_REGISTRATION" in result.missing_info


def test_unemployment_self_employed_current_business_not_likely(tmp_path):
    result = make_checker(tmp_path).check_unemployment(
        base_profile(employment_status=EmploymentStatus.SELF_EMPLOYED.value, business_closed=False)
    )
    assert result.status == "not_likely"


def test_unemployment_business_closed_pathway(tmp_path):
    result = make_checker(tmp_path).check_unemployment(
        base_profile(
            employment_status=EmploymentStatus.SELF_EMPLOYED.value,
            business_closed=True,
            termination_reason=TerminationReason.BUSINESS_CLOSED.value,
        )
    )
    assert result.status == "likely_eligible"


def test_general_disability_missing_medical_info(tmp_path):
    result = make_checker(tmp_path).check_general_disability(base_profile())
    assert result.status == "insufficient_information"


def test_general_disability_likely(tmp_path):
    result = make_checker(tmp_path).check_general_disability(
        base_profile(medical_disability_percent=65, work_capacity_loss_percent=75)
    )
    assert result.status == "likely_eligible"
    assert result.estimated_monthly_ils_max is not None


def test_general_disability_capacity_too_low(tmp_path):
    result = make_checker(tmp_path).check_general_disability(
        base_profile(medical_disability_percent=70, work_capacity_loss_percent=20)
    )
    assert result.status == "not_likely"


def test_child_allowance_likely(tmp_path):
    result = make_checker(tmp_path).check_child_allowance(base_profile())
    assert result.status == "likely_eligible"
    assert result.estimated_monthly_ils_min == 392.0


def test_child_allowance_missing_birth_dates_is_possible(tmp_path):
    result = make_checker(tmp_path).check_child_allowance(base_profile(birth_dates=[]))
    assert result.status == "possibly_eligible"
    assert "CHILD_BIRTH_DATES" in result.missing_info


def test_child_allowance_no_children(tmp_path):
    result = make_checker(tmp_path).check_child_allowance(base_profile(children_count=0, birth_dates=[]))
    assert result.status == "not_likely"


def test_income_supplement_likely_for_low_income(tmp_path):
    profile = base_profile(monthly_income=1500, spouse_income=0, registered_employment_service=True)
    result = make_checker(tmp_path).check_income_supplement(profile)
    assert result.status == "likely_eligible"
    assert result.estimated_monthly_ils_max is None


def test_income_supplement_missing_work_test(tmp_path):
    profile = base_profile(monthly_income=1500, registered_employment_service=False)
    result = make_checker(tmp_path).check_income_supplement(profile)
    assert result.status == "insufficient_information"
    assert "EMPLOYMENT_SERVICE_REGISTRATION_OR_EXEMPTION" in result.missing_info



def test_general_disability_requires_single_impairment_path(tmp_path):
    result = make_checker(tmp_path).check_general_disability(
        base_profile(medical_disability_percent=50, highest_single_impairment_percent=20, work_capacity_loss_percent=65)
    )
    assert result.status == "not_likely"


def test_income_support_2026_single_parent_cap(tmp_path):
    profile = base_profile(monthly_income=9800, spouse_income=0, registered_employment_service=True)
    result = make_checker(tmp_path).check_income_supplement(profile)
    assert result.status == "likely_eligible"
    assert "₪9,865" in result.reasons[0]


def test_income_supplement_assets_block(tmp_path):
    result = make_checker(tmp_path).check_income_supplement(base_profile(assets_exceed_limit=True))
    assert result.status == "not_likely"


def test_check_all_returns_four_results(tmp_path):
    results = make_checker(tmp_path).check_all(base_profile())
    assert len(results) == 4


def test_check_benefit_dispatch(tmp_path):
    result = make_checker(tmp_path).check_benefit(BenefitType.CHILD_ALLOWANCE, base_profile())
    assert result.benefit == BenefitType.CHILD_ALLOWANCE.value


def test_check_benefit_unknown_raises(tmp_path):
    with pytest.raises(ValueError):
        make_checker(tmp_path).check_benefit("unknown", base_profile())


@pytest.mark.asyncio
async def test_async_check_all(tmp_path):
    results = await make_checker(tmp_path).async_check_all(base_profile())
    assert len(results) == 4


@pytest.mark.asyncio
async def test_async_check_benefit(tmp_path):
    result = await make_checker(tmp_path).async_check_benefit("child_allowance", base_profile())
    assert result.status == "likely_eligible"


def test_profile_store_create_and_check_chain(tmp_path):
    checker = make_checker(tmp_path)
    create_response = checker.create_profile(base_profile())
    assert create_response["created"] is True
    profile_id = create_response["profile_id"]
    checked = checker.check_profile_id(profile_id)
    assert checked["profile_id"] == profile_id
    assert len(checked["results"]) == 4


def test_list_profiles(tmp_path):
    checker = make_checker(tmp_path)
    checker.create_profile(base_profile(age=41))
    listed = checker.list_profiles()
    assert len(listed) == 1
    assert listed[0]["age"] == 41


def test_run_application_workflow(tmp_path):
    workflow = make_checker(tmp_path).run_application_workflow(base_profile())
    assert workflow["profile"]["created"] is True
    assert "child_allowance" in workflow["recommended_benefits"]


def test_documents_for(tmp_path):
    docs = make_checker(tmp_path).documents_for("unemployment")
    assert any("Employment Service" in item for item in docs)


def test_explain_contains_status(tmp_path):
    checker = make_checker(tmp_path)
    result = checker.check_child_allowance(base_profile())
    assert "likely_eligible" in checker.explain(result)


def test_check_profile_convenience_function():
    results = check_profile(base_profile().to_dict())
    assert len(results) == 4


def test_check_file_convenience_function(tmp_path):
    path = tmp_path / "profile.json"
    path.write_text(base_profile().to_json(), encoding="utf-8")
    payload = check_file(path, benefit="child_allowance")
    assert payload["results"][0]["benefit"] == "child_allowance"


def test_json_round_trip():
    profile = base_profile()
    loaded = ApplicantProfile.from_mapping(json.loads(profile.to_json()))
    assert loaded.age == profile.age


def test_script_underscored_client_imports():
    script_path = Path("scripts/social_security_benefit_checker_client.py")
    spec = importlib.util.spec_from_file_location("script_client", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["script_client"] = module
    spec.loader.exec_module(module)
    result = module.SocialSecurityBenefitChecker().check_child_allowance(base_profile())
    assert result.status in {"likely_eligible", "possibly_eligible"}
