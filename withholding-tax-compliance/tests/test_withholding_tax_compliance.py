from datetime import date
from decimal import Decimal

import pytest

from scripts.withholding_tax_compliance import (
    ComplianceError,
    SupplierCertificate,
    SupplierPayment,
    build_form856_staging_rows,
    calculate_withholding,
    current_vat_rate,
    normalize_israeli_tax_id,
    summarize_by_supplier,
    validate_form856_submission_inputs,
    validate_rate_percent,
)


def cert(rate="7.50"):
    return SupplierCertificate(
        supplier_tax_id="123456789",
        rate_percent=Decimal(rate),
        valid_from=date(2026, 1, 1),
        valid_to=date(2027, 3, 31),
        certificate_reference="ITA-2026-001",
    )


def payment(amount="1000.00", vat="180.00"):
    return SupplierPayment(
        payment_id="P-001",
        supplier_tax_id="123456789",
        payment_date=date(2026, 5, 1),
        amount_before_vat_ils=Decimal(amount),
        vat_ils=Decimal(vat),
    )


def test_current_vat_rate_2026_is_18_percent():
    assert current_vat_rate(date(2026, 6, 1)) == Decimal("0.18")


def test_current_vat_rate_rejects_unvalidated_past_date():
    with pytest.raises(ComplianceError):
        current_vat_rate(date(2024, 12, 31))


def test_normalize_israeli_tax_id_zero_pads():
    assert normalize_israeli_tax_id("12345") == "000012345"


def test_validate_rate_percent_bounds():
    assert validate_rate_percent("25") == Decimal("25.00")
    with pytest.raises(ComplianceError):
        validate_rate_percent("100.01")


def test_calculate_withholding_excludes_vat_by_default():
    result = calculate_withholding(payment(), cert())
    assert result.withholding_base_ils == Decimal("1000.00")
    assert result.withheld_ils == Decimal("75.00")


def test_calculate_withholding_can_include_vat_when_explicit():
    result = calculate_withholding(payment(), cert(), include_vat_in_base=True)
    assert result.withholding_base_ils == Decimal("1180.00")
    assert result.withheld_ils == Decimal("88.50")


def test_certificate_must_be_valid_on_payment_date():
    stale = SupplierCertificate(
        supplier_tax_id="123456789",
        rate_percent=Decimal("7.5"),
        valid_from=date(2025, 1, 1),
        valid_to=date(2025, 12, 31),
    )
    with pytest.raises(ComplianceError):
        calculate_withholding(payment(), stale)


def test_build_staging_rows_and_validate():
    rows = build_form856_staging_rows([payment()], {"123456789": cert()})
    assert rows[0]["withheld_ils"] == "75.00"
    assert validate_form856_submission_inputs(rows) == []


def test_summary_by_supplier():
    r1 = calculate_withholding(payment("1000.00", "180.00"), cert("10"))
    r2 = calculate_withholding(
        SupplierPayment("P-002", "123456789", date(2026, 6, 1), Decimal("2000.00"), Decimal("360.00")),
        cert("10"),
    )
    summary = summarize_by_supplier([r1, r2])
    assert summary["123456789"]["payment_count"] == 2
    assert summary["123456789"]["withheld_ils"] == Decimal("300.00")
