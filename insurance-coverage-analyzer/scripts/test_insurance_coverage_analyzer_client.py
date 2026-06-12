import asyncio
import json
from pathlib import Path

import pytest

import insurance_coverage_analyzer as client


def test_normalize_policy_type_health_hebrew():
    assert client.normalize_policy_type("ביטוח בריאות") == "health"


def test_normalize_policy_type_home_hebrew():
    assert client.normalize_policy_type("ביטוח דירה") == "home"


def test_normalize_policy_type_life_hebrew():
    assert client.normalize_policy_type("ריסק") == "life"


def test_unknown_policy_type():
    assert client.normalize_policy_type("travel") == "unknown"


def test_parse_money_shekel():
    assert client.parse_money("₪1,234.50") == 1234.50


def test_format_nis_integer():
    assert client.format_nis(120000) == "₪120,000"


def test_format_nis_decimal():
    assert client.format_nis(1200.5) == "₪1,200.50"


def test_normalize_date_iso():
    assert client.normalize_date("2026-06-02") == "02-06-2026"


def test_format_date_hebrew_uses_slashes():
    assert client.format_date_for_locale("2026-06-02", "he-IL") == "02/06/2026"


def test_ambiguous_short_date_rejected():
    assert client.normalize_date("01/02/26") is None


def test_sensitive_identifier_detection():
    assert client.has_sensitive_identifier("customer 123456789")


def test_redact_sensitive_identifier():
    assert "***REDACTED-ID***" in client.redact_sensitive_text("id 123456789")


def test_policy_from_raw_converts_monthly_to_annual():
    policy = client.Policy.from_raw({"policy_type": "health", "premium_monthly_nis": 100, "coverages": {"private_surgery_israel": True}})
    assert policy.premium_annual_nis == 1200


def test_policy_from_raw_converts_annual_to_monthly():
    policy = client.Policy.from_raw({"policy_type": "life", "premium_annual_nis": 1200, "coverages": {"death_benefit": True}})
    assert policy.premium_monthly_nis == 100


def test_coverage_from_bool():
    item = client.CoverageItem.from_raw(True)
    assert item.covered is True


def test_coverage_from_money_string():
    item = client.CoverageItem.from_raw("₪5,000")
    assert item.covered is True
    assert item.limit_nis == 5000


def test_exposure_from_percent():
    item = client.CoverageItem(covered=True, deductible_percent=10)
    assert item.exposure_nis(1250000) == 125000


def test_validate_unknown_type_invalid():
    analyzer = client.InsuranceCoverageAnalyzer()
    result = analyzer.validate([{"policy_type": "unknown-name", "coverages": {"x": True}}])
    assert result["valid"] is False


def test_duplicate_policy_ids_raise():
    analyzer = client.InsuranceCoverageAnalyzer()
    with pytest.raises(client.PolicyValidationError):
        analyzer.normalize([
            {"policy_id": "x", "policy_type": "health", "coverages": {"private_surgery_israel": True}},
            {"policy_id": "x", "policy_type": "health", "coverages": {"drugs_outside_basket": True}},
        ])


def test_compare_two_health_policies_has_diffs():
    analyzer = client.InsuranceCoverageAnalyzer()
    result = analyzer.compare([
        {"policy_id": "a", "policy_type": "health", "premium_monthly_nis": 180, "coverages": {"private_surgery_israel": {"covered": True, "limit_nis": 1000000}}},
        {"policy_id": "b", "policy_type": "health", "premium_monthly_nis": 145, "coverages": {"private_surgery_israel": {"covered": True, "limit_nis": 750000}}},
    ])
    assert result.diffs
    assert "Policy differences" in result.summary or "Coverage gaps" in result.summary


def test_compare_empty_rejected():
    with pytest.raises(client.PolicyValidationError):
        client.InsuranceCoverageAnalyzer().compare([])


def test_detect_health_gaps():
    policy = client.Policy.from_raw({"policy_id": "h", "policy_type": "health", "coverages": {"private_surgery_israel": True}})
    gaps = client.detect_gaps([policy])
    assert any("drugs_outside_basket" in item for item in gaps)


def test_detect_home_mortgage_gap():
    policy = client.Policy.from_raw({"policy_id": "home", "policy_type": "home", "coverages": {"contents": True}})
    gaps = client.detect_gaps([policy], {"mortgage": True})
    assert any("structure cover" in item for item in gaps)


def test_detect_domestic_worker_gap():
    policy = client.Policy.from_raw({"policy_id": "home", "policy_type": "home", "coverages": {"structure": True}})
    gaps = client.detect_gaps([policy], {"domestic_worker": True})
    assert any("employer liability" in item for item in gaps)


def test_detect_home_office_gap():
    policy = client.Policy.from_raw({"policy_id": "home", "policy_type": "home", "coverages": {"structure": True}})
    gaps = client.detect_gaps([policy], {"home_office": True})
    assert any("business equipment" in item for item in gaps)


def test_earthquake_exposure_gap():
    policy = client.Policy.from_raw({"policy_id": "home", "policy_type": "home", "coverages": {"structure": {"covered": True, "limit_nis": 1200000}, "earthquake": {"covered": True, "deductible_percent": 10}}})
    gaps = client.detect_gaps([policy])
    assert any("₪120,000" in item for item in gaps)


def test_life_mortgage_without_family_benefit_gap():
    policy = client.Policy.from_raw({"policy_id": "life", "policy_type": "life", "coverages": {"mortgage_life": True}})
    gaps = client.detect_gaps([policy])
    assert any("family death benefit" in item for item in gaps)


def test_beneficiary_gap():
    policy = client.Policy.from_raw({"policy_id": "life", "policy_type": "life", "coverages": {"death_benefit": True}})
    gaps = client.detect_gaps([policy])
    assert any("beneficiary" in item for item in gaps)


def test_detect_duplicates_same_key():
    policies = [
        client.Policy.from_raw({"policy_id": "a", "policy_type": "health", "coverages": {"serious_illness": True}}),
        client.Policy.from_raw({"policy_id": "b", "policy_type": "life", "coverages": {"serious_illness": True}}),
    ]
    duplicates = client.detect_duplicates(policies)
    assert any("serious_illness" in item for item in duplicates)


def test_detect_related_duplicate_group():
    policies = [
        client.Policy.from_raw({"policy_id": "a", "policy_type": "health", "coverages": {"private_surgery_israel": True}}),
        client.Policy.from_raw({"policy_id": "b", "policy_type": "health", "coverages": {"supplementary_surgery": True}}),
    ]
    duplicates = client.detect_duplicates(policies)
    assert any("Potential overlap" in item for item in duplicates)


def test_risk_flags_mixed_types():
    policies = [
        client.Policy.from_raw({"policy_id": "h", "policy_type": "health", "coverages": {"private_surgery_israel": True}}),
        client.Policy.from_raw({"policy_id": "l", "policy_type": "life", "coverages": {"death_benefit": True}}),
    ]
    flags = client.detect_risk_flags(policies)
    assert any("Mixed policy types" in item for item in flags)


def test_risk_flags_underwriting():
    policy = client.Policy.from_raw({"policy_id": "h", "policy_type": "health", "coverages": {"private_surgery_israel": True}, "requires_underwriting": True})
    flags = client.detect_risk_flags([policy])
    assert any("licensed review" in item for item in flags)


def test_recommend_actions_for_gaps():
    actions = client.recommend_actions([], [], [], ["gap"], [])
    assert any("gap" in item.lower() for item in actions)


def test_score_policy_returns_integer():
    policy = client.Policy.from_raw({"policy_id": "h", "policy_type": "health", "premium_monthly_nis": 100, "coverages": {"private_surgery_israel": True, "drugs_outside_basket": True, "transplants": True, "ambulatory": True}})
    scores = client.score_policies([policy])
    assert isinstance(scores["h"], int)


def test_to_markdown_hebrew_headings():
    result = client.InsuranceCoverageAnalyzer(locale="he-IL").compare([
        {"policy_id": "h", "policy_type": "health", "premium_monthly_nis": 100, "coverages": {"private_surgery_israel": True}}
    ])
    assert "תקציר" in result.to_markdown(locale="he-IL")


def test_load_json_list(tmp_path: Path):
    path = tmp_path / "policies.json"
    path.write_text(json.dumps([{"policy_id": "x", "policy_type": "health", "coverages": {"private_surgery_israel": True}}]), encoding="utf-8")
    policies, profile = client.load_policy_json(path)
    assert len(policies) == 1
    assert profile == {}


def test_load_json_object(tmp_path: Path):
    path = tmp_path / "policies.json"
    path.write_text(json.dumps({"profile": {"mortgage": True}, "policies": [{"policy_id": "x", "policy_type": "home", "coverages": {"structure": True}}]}), encoding="utf-8")
    policies, profile = client.load_policy_json(path)
    assert len(policies) == 1
    assert profile["mortgage"] is True


def test_load_csv(tmp_path: Path):
    path = tmp_path / "policies.csv"
    path.write_text("policy_id,policy_type,coverage_key,covered,limit_nis\nh,health,private_surgery_israel,true,1000000\n", encoding="utf-8")
    rows = client.load_policy_csv(path)
    assert rows[0]["coverages"]["private_surgery_israel"]["limit_nis"] == 1000000


def test_save_report_json(tmp_path: Path):
    result = client.InsuranceCoverageAnalyzer().compare([
        {"policy_id": "h", "policy_type": "health", "coverages": {"private_surgery_israel": True}}
    ])
    path = tmp_path / "report.json"
    client.save_report(result, path, "json")
    assert json.loads(path.read_text(encoding="utf-8"))["summary"]


def test_save_report_markdown(tmp_path: Path):
    result = client.InsuranceCoverageAnalyzer().compare([
        {"policy_id": "h", "policy_type": "health", "coverages": {"private_surgery_israel": True}}
    ])
    path = tmp_path / "report.md"
    client.save_report(result, path, "markdown")
    assert "Summary" in path.read_text(encoding="utf-8")


def test_sample_policies_compare():
    result = client.InsuranceCoverageAnalyzer().compare(client.sample_policies())
    assert result.scorecard


def test_create_and_load_analysis_record(tmp_path: Path):
    response = client.create_analysis_record(client.sample_policies(), store_dir=tmp_path)
    assert response["analysis_id"].startswith("ica-")
    record = client.load_analysis_record(response["analysis_id"], store_dir=tmp_path)
    assert record["analysis_id"] == response["analysis_id"]


@pytest.mark.asyncio
async def test_async_compare():
    result = await client.InsuranceCoverageAnalyzer().compare_async(client.sample_policies())
    assert result.diffs


@pytest.mark.asyncio
async def test_async_validate():
    result = await client.InsuranceCoverageAnalyzer().validate_async(client.sample_policies())
    assert result["policy_count"] == 2
