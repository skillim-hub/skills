"""Estimator for Israeli self-employed National Insurance and health-insurance contributions.

The default configuration is web-validated for 2026. This module deliberately has
no network calls and does not attempt to submit forms or call Israel Tax Authority
APIs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ContributionRates:
    """Contribution percentages for one statutory year."""

    national_insurance_reduced: float = 0.0447
    national_insurance_regular: float = 0.1283
    health_insurance_reduced: float = 0.0323
    health_insurance_regular: float = 0.0517
    deductible_national_insurance_share_for_basis: float = 0.52


@dataclass(frozen=True)
class ContributionThresholds:
    """Monthly income thresholds in Israeli shekels."""

    average_wage: float = 13_769.0
    reduced_rate_monthly_threshold: float = 7_703.0
    maximum_monthly_income: float = 51_910.0
    minimum_monthly_income: float = 3_442.0


@dataclass(frozen=True)
class EstimatorConfig:
    """Full configuration for the estimator."""

    year: int = 2026
    currency: str = "ILS"
    rates: ContributionRates = ContributionRates()
    thresholds: ContributionThresholds = ContributionThresholds()
    access_date: str = "2026-06-01"


@dataclass(frozen=True)
class ContributionBreakdown:
    """Detailed result of a contribution estimate."""

    year: int
    months: int
    gross_income: float
    contribution_basis: float
    reduced_band_basis: float
    regular_band_basis: float
    national_insurance_reduced: float
    national_insurance_regular: float
    health_insurance_reduced: float
    health_insurance_regular: float
    national_insurance_total: float
    health_insurance_total: float
    total_contributions: float
    currency: str = "ILS"
    notes: str = "Estimate only; binding amounts follow law and National Insurance records."

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary."""

        return asdict(self)


class BituachLeumiEstimator:
    """Estimator for a solely self-employed person aged 18 to pre-retirement."""

    def __init__(self, config: Optional[EstimatorConfig] = None) -> None:
        self.config = config or EstimatorConfig()

    def estimate(self, monthly_income: float, months: int = 1) -> ContributionBreakdown:
        """Estimate contributions for a monthly income over a number of months.

        Args:
            monthly_income: Monthly self-employed income/profit before the 52%
                National Insurance deduction adjustment.
            months: Number of months represented by the estimate.

        Returns:
            A contribution breakdown with National Insurance and health-insurance
            components separated.
        """

        if months < 1 or months > 12:
            raise ValueError("months must be between 1 and 12")
        if monthly_income < 0:
            raise ValueError("monthly_income must be non-negative")

        gross_income = float(monthly_income) * months
        basis = self.adjusted_contribution_basis(gross_income=gross_income, months=months)
        return self.breakdown_from_basis(gross_income=gross_income, basis=basis, months=months)

    def adjusted_contribution_basis(self, gross_income: float, months: int = 1) -> float:
        """Solve the Section 345 basis after the 52% National Insurance deduction.

        The implicit equation is:
            gross = basis + 0.52 * national_insurance_due(basis)

        The resulting basis is then bounded by the monthly minimum and maximum
        thresholds multiplied by `months`.
        """

        if gross_income < 0:
            raise ValueError("gross_income must be non-negative")
        t = self.config.thresholds
        max_basis = t.maximum_monthly_income * months
        min_basis = t.minimum_monthly_income * months

        if gross_income <= 0:
            return min_basis

        max_gross_representable = max_basis + self.config.rates.deductible_national_insurance_share_for_basis * self.national_insurance_due(max_basis, months)
        if gross_income >= max_gross_representable:
            return max_basis

        low, high = 0.0, max_basis
        for _ in range(80):
            mid = (low + high) / 2.0
            implied_gross = mid + self.config.rates.deductible_national_insurance_share_for_basis * self.national_insurance_due(mid, months)
            if implied_gross < gross_income:
                low = mid
            else:
                high = mid
        solved = (low + high) / 2.0
        return max(min_basis, min(max_basis, solved))

    def national_insurance_due(self, basis: float, months: int = 1) -> float:
        """Calculate only National Insurance due on a contribution basis."""

        reduced, regular = self.split_basis(basis, months)
        r = self.config.rates
        return reduced * r.national_insurance_reduced + regular * r.national_insurance_regular

    def health_insurance_due(self, basis: float, months: int = 1) -> float:
        """Calculate only health-insurance contributions on a contribution basis."""

        reduced, regular = self.split_basis(basis, months)
        r = self.config.rates
        return reduced * r.health_insurance_reduced + regular * r.health_insurance_regular

    def total_due(self, monthly_income: float, months: int = 1) -> float:
        """Return the total estimated contributions."""

        return self.estimate(monthly_income=monthly_income, months=months).total_contributions

    def split_basis(self, basis: float, months: int = 1) -> tuple[float, float]:
        """Split contribution basis into reduced and regular bands."""

        if basis < 0:
            raise ValueError("basis must be non-negative")
        threshold = self.config.thresholds.reduced_rate_monthly_threshold * months
        max_basis = self.config.thresholds.maximum_monthly_income * months
        bounded = min(float(basis), max_basis)
        reduced = min(bounded, threshold)
        regular = max(0.0, bounded - threshold)
        return reduced, regular

    def breakdown_from_basis(self, gross_income: float, basis: float, months: int = 1) -> ContributionBreakdown:
        """Build a detailed breakdown from an already calculated contribution basis."""

        reduced, regular = self.split_basis(basis, months)
        r = self.config.rates
        ni_reduced = reduced * r.national_insurance_reduced
        ni_regular = regular * r.national_insurance_regular
        hi_reduced = reduced * r.health_insurance_reduced
        hi_regular = regular * r.health_insurance_regular
        ni_total = ni_reduced + ni_regular
        hi_total = hi_reduced + hi_regular
        return ContributionBreakdown(
            year=self.config.year,
            months=months,
            gross_income=round(gross_income, 2),
            contribution_basis=round(basis, 2),
            reduced_band_basis=round(reduced, 2),
            regular_band_basis=round(regular, 2),
            national_insurance_reduced=round(ni_reduced, 2),
            national_insurance_regular=round(ni_regular, 2),
            health_insurance_reduced=round(hi_reduced, 2),
            health_insurance_regular=round(hi_regular, 2),
            national_insurance_total=round(ni_total, 2),
            health_insurance_total=round(hi_total, 2),
            total_contributions=round(ni_total + hi_total, 2),
            currency=self.config.currency,
        )


def vat_rate_for_date(transaction_date: date | str) -> float:
    """Return the standard Israeli VAT rate for a transaction date.

    The helper implements the verified 18% rate from 2025-01-01. It returns 17%
    for dates before 2025-01-01 for convenience in transition examples.
    """

    if isinstance(transaction_date, str):
        parsed = datetime.fromisoformat(transaction_date).date()
    else:
        parsed = transaction_date
    return 0.18 if parsed >= date(2025, 1, 1) else 0.17


def add_vat(net_amount: float, transaction_date: date | str = "2026-01-01") -> Dict[str, float]:
    """Add standard Israeli VAT to a net amount."""

    if net_amount < 0:
        raise ValueError("net_amount must be non-negative")
    rate = vat_rate_for_date(transaction_date)
    vat = net_amount * rate
    return {"net": round(net_amount, 2), "vat_rate": rate, "vat": round(vat, 2), "gross": round(net_amount + vat, 2)}


def estimate_monthly(monthly_income: float, months: int = 1) -> ContributionBreakdown:
    """Convenience wrapper using the default 2026 configuration."""

    return BituachLeumiEstimator().estimate(monthly_income=monthly_income, months=months)


def official_example_2026() -> ContributionBreakdown:
    """Return the official NII 2026 example: ₪12,000 monthly income for one quarter."""

    return estimate_monthly(monthly_income=12_000, months=3)


def load_default_config() -> EstimatorConfig:
    """Return the built-in web-validated 2026 configuration."""

    return EstimatorConfig()


__all__ = [
    "ContributionRates",
    "ContributionThresholds",
    "EstimatorConfig",
    "ContributionBreakdown",
    "BituachLeumiEstimator",
    "vat_rate_for_date",
    "add_vat",
    "estimate_monthly",
    "official_example_2026",
    "load_default_config",
]
