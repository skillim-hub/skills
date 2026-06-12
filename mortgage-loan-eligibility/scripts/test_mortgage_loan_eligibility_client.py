from __future__ import annotations

import asyncio
import json

import pytest

import mortgage_loan_eligibility_client as client


def base_request(**overrides):
    data = {
        "property_value": 2_400_000,
        "requested_loan_amount": 1_500_000,
        "property_status": "single_home",
        "net_monthly_income": 28_000,
        "existing_monthly_debt": 1_000,
        "annual_rate": 5.0,
        "term_years": 25,
    }
    data.update(overrides)
    return data


def test_monthly_payment_known_range():
    payment = client.monthly_payment(1_000_000, 0.05, 25)
    assert 5800 < payment < 5900


def test_monthly_payment_zero_interest():
    assert client.monthly_payment(120_000, 0, 10) == pytest.approx(1000)


def test_monthly_payment_zero_principal():
    assert client.monthly_payment(0, 5, 25) == 0


def test_negative_principal_rejected():
    with pytest.raises(client.EligibilityError):
        client.monthly_payment(-1, 5, 25)


def test_rate_percent_normalized():
    assert client.normalize_rate(5.25) == pytest.approx(0.0525)
    assert client.normalize_rate(0.0525) == pytest.approx(0.0525)


def test_ltv_limit_single_home():
    assert client.ltv_limit_for("single_home") == pytest.approx(0.75)


def test_ltv_limit_replacement_home():
    assert client.max_loan_by_ltv(2_000_000, "replacement_home") == pytest.approx(1_400_000)


def test_ltv_limit_investment_property():
    assert client.max_loan_by_ltv(2_000_000, "investment_property") == pytest.approx(1_000_000)


def test_eligible_first_home():
    result = client.calculate_eligibility(base_request())
    assert result.status in {client.EligibilityStatus.ELIGIBLE, client.EligibilityStatus.NEEDS_REVIEW}
    assert result.ltv < result.ltv_limit


def test_fail_ltv_for_investment_property():
    result = client.calculate_eligibility(base_request(property_status="investment_property"))
    assert result.status == client.EligibilityStatus.NOT_ELIGIBLE
    assert any("LTV" in reason for reason in result.reasons)


def test_fail_dsr_when_income_too_low():
    result = client.calculate_eligibility(base_request(net_monthly_income=9_000))
    assert result.status == client.EligibilityStatus.NOT_ELIGIBLE
    assert any("DSR" in reason for reason in result.reasons)


def test_needs_review_when_dsr_above_review_threshold():
    result = client.calculate_eligibility(base_request(net_monthly_income=22_000, requested_loan_amount=1_600_000))
    assert result.status == client.EligibilityStatus.NEEDS_REVIEW
    assert result.dsr > result.dsr_review_threshold


def test_cash_equity_shortfall_fails():
    result = client.calculate_eligibility(base_request(cash_equity=100_000))
    assert result.status == client.EligibilityStatus.NOT_ELIGIBLE
    assert result.binding_constraint == "cash_equity"


def test_cash_equity_sufficient_passes_equity_check():
    result = client.calculate_eligibility(base_request(cash_equity=900_000))
    assert "cash equity" not in " ".join(result.reasons).lower()


def test_income_records_average():
    records = [
        {"period": "2025-01", "net_income": 20_000},
        {"period": "2025-02", "net_income": 22_000},
    ]
    assert client.stabilize_net_income(records) == pytest.approx(21_000)


def test_income_records_weighted_average():
    records = [
        client.IncomeRecord("2025-01", 10_000, True, 1),
        client.IncomeRecord("2025-02", 20_000, True, 3),
    ]
    assert client.stabilize_net_income(records) == pytest.approx(17_500)


def test_unverified_income_records_ignored():
    records = [
        {"period": "2025-01", "net_income": 99_000, "verified": False},
        {"period": "2025-02", "net_income": 20_000, "verified": True},
    ]
    assert client.stabilize_net_income(records) == pytest.approx(20_000)


def test_trim_outlier_income_records():
    records = [
        {"period": f"2025-{month:02d}", "net_income": value}
        for month, value in enumerate([1_000, 20_000, 21_000, 22_000, 23_000, 100_000], start=1)
    ]
    assert client.stabilize_net_income(records, trim_outliers=True) == pytest.approx(21_500)


def test_no_verified_income_rejected():
    with pytest.raises(client.EligibilityError):
        client.stabilize_net_income([{"period": "2025-01", "net_income": 20_000, "verified": False}])


def test_from_mapping_invalid_status_rejected():
    with pytest.raises(client.EligibilityError):
        client.MortgageRequest.from_mapping(base_request(property_status="holiday_home"))


def test_to_dict_is_json_serializable():
    result = client.calculate_eligibility(base_request())
    json.dumps(result.to_dict(), ensure_ascii=False)


def test_track_sum_must_equal_loan_amount():
    data = base_request(tracks=[{"name": "a", "principal": 100_000, "annual_rate": 5, "term_years": 25}])
    with pytest.raises(client.EligibilityError):
        client.calculate_eligibility(data)


def test_multiple_tracks_payment_is_sum():
    data = base_request(
        requested_loan_amount=1_000_000,
        tracks=[
            {"name": "fixed", "principal": 500_000, "annual_rate": 4.8, "term_years": 25},
            {"name": "prime", "principal": 500_000, "annual_rate": 5.2, "term_years": 25},
        ],
    )
    result = client.calculate_eligibility(data)
    assert len(result.track_payments) == 2
    assert result.estimated_monthly_payment == pytest.approx(
        sum(row["monthly_payment"] for row in result.track_payments),
        abs=1,
    )


def test_principal_from_payment_inverts_monthly_payment():
    principal = 900_000
    payment = client.monthly_payment(principal, 0.047, 20)
    recovered = client.principal_from_payment(payment, 0.047, 20)
    assert recovered == pytest.approx(principal)


def test_existing_debt_reduces_max_loan_by_dsr():
    low_debt = client.calculate_eligibility(base_request(existing_monthly_debt=0))
    high_debt = client.calculate_eligibility(base_request(existing_monthly_debt=5_000))
    assert high_debt.max_loan_by_dsr < low_debt.max_loan_by_dsr


def test_ltv_boundary_passes():
    result = client.calculate_eligibility(base_request(requested_loan_amount=1_800_000))
    assert result.ltv == pytest.approx(result.ltv_limit)
    assert not any("exceeds the standard LTV cap" in reason for reason in result.reasons)


def test_dsr_boundary_passes():
    request = base_request(existing_monthly_debt=0, net_monthly_income=1)
    payment = client.monthly_payment(request["requested_loan_amount"], request["annual_rate"], request["term_years"])
    request["net_monthly_income"] = payment / client.DEFAULT_DSR_LIMIT
    result = client.calculate_eligibility(request)
    assert result.dsr == pytest.approx(result.dsr_limit)


def test_client_sync_calculate():
    mortgage_client = client.MortgageEligibilityClient(default_annual_rate=5.1)
    result = mortgage_client.calculate(base_request(annual_rate=5.1))
    assert result.requested_loan_amount == 1_500_000


def test_client_async_calculate():
    mortgage_client = client.MortgageEligibilityClient()
    result = asyncio.run(mortgage_client.acalculate(base_request()))
    assert result.property_value == 2_400_000


def test_calculate_file(tmp_path):
    path = tmp_path / "request.json"
    path.write_text(json.dumps(base_request()), encoding="utf-8")
    result = client.MortgageEligibilityClient().calculate_file(path)
    assert result.status in {client.EligibilityStatus.ELIGIBLE, client.EligibilityStatus.NEEDS_REVIEW}


def test_save_result(tmp_path):
    result = client.calculate_eligibility(base_request())
    path = tmp_path / "result.json"
    client.save_result(result, path)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["status"] == result.status.value


def test_format_nis():
    assert client.format_nis(1234567).startswith("₪1,234,567")


def test_interest_only_payment():
    assert client.interest_only_payment(1_200_000, 6) == pytest.approx(6000)


def test_interest_only_months_affect_payment():
    without_grace = client.monthly_payment(1_000_000, 5, 25)
    with_grace = client.monthly_payment(1_000_000, 5, 25, interest_only_months=24)
    assert with_grace > without_grace


def test_recommendations_present_on_review():
    result = client.calculate_eligibility(base_request(net_monthly_income=22_000, requested_loan_amount=1_600_000))
    assert result.recommendations


def test_importable_module_public_api():
    assert client.MortgageEligibilityClient().calculate(base_request()).status.value
    assert callable(client.calculate_eligibility)


def test_client_default_overrides_are_applied():
    local_client = client.MortgageEligibilityClient(default_annual_rate=4.5, default_term_years=20, default_dsr_limit=45)
    request = base_request()
    request.pop("annual_rate")
    request.pop("term_years")
    result = local_client.calculate(request)
    assert result.dsr_limit == pytest.approx(0.45)


def test_term_above_standard_cap_rejected():
    with pytest.raises(client.EligibilityError):
        client.calculate_eligibility(base_request(term_years=31))


def test_track_term_above_standard_cap_rejected():
    data = base_request(
        requested_loan_amount=1_000_000,
        tracks=[{"name": "long", "principal": 1_000_000, "annual_rate": 5, "term_years": 31}],
    )
    with pytest.raises(client.EligibilityError):
        client.calculate_eligibility(data)
