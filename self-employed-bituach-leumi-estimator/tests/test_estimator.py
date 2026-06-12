from datetime import date

import pytest

from scripts.bituach_leumi_estimator import (
    BituachLeumiEstimator,
    add_vat,
    estimate_monthly,
    official_example_2026,
    vat_rate_for_date,
)


def test_official_2026_quarterly_example_matches_nii_rounding():
    result = official_example_2026()
    assert result.months == 3
    assert result.gross_income == 36_000
    assert result.contribution_basis == pytest.approx(34_690, abs=1)
    assert result.reduced_band_basis == pytest.approx(23_109, abs=1)
    assert result.regular_band_basis == pytest.approx(11_581, abs=1)
    assert result.national_insurance_total == pytest.approx(2_518.7, abs=2)
    assert result.health_insurance_total == pytest.approx(1_345.1, abs=2)
    assert result.total_contributions == pytest.approx(3_864, abs=2)


def test_minimum_income_floor_applies_for_zero_income_self_employed():
    result = estimate_monthly(0, months=1)
    assert result.contribution_basis == 3_442
    assert result.total_contributions > 0


def test_maximum_income_cap_applies():
    result = estimate_monthly(1_000_000, months=1)
    assert result.contribution_basis == 51_910
    assert result.regular_band_basis == 51_910 - 7_703


def test_vat_rate_transition():
    assert vat_rate_for_date(date(2024, 12, 31)) == 0.17
    assert vat_rate_for_date("2025-01-01") == 0.18
    assert vat_rate_for_date("2026-06-01") == 0.18


def test_add_vat_2026():
    assert add_vat(100, "2026-01-01") == {"net": 100, "vat_rate": 0.18, "vat": 18, "gross": 118}


def test_invalid_months_and_income_raise():
    est = BituachLeumiEstimator()
    with pytest.raises(ValueError):
        est.estimate(1000, months=0)
    with pytest.raises(ValueError):
        est.estimate(-1, months=1)
