from __future__ import annotations

import json
from decimal import Decimal

import pytest
from click.testing import CliRunner

from installment_calculator import (
    CURRENT_ISRAEL_VAT_RATE_PERCENT,
    InstallmentCalculationError,
    InstallmentClient,
    InstallmentRequest,
    add_months,
    async_calculate_plan,
    async_compare_plans,
    calculate_plan,
    compare_plans,
    estimate_refund,
    format_date_il,
    format_ils,
    gross_from_net,
    money,
    parse_date,
    request_from_mapping,
    statutory_cancellation_fee_cap,
    vat_components_from_gross,
)
from installment_calculator.cli import main


def test_zero_interest_six_payments_are_equal():
    plan = calculate_plan(InstallmentRequest(cash_price="1200", installments=6, first_due_date="15/07/2026"))
    assert [line.payment for line in plan.schedule] == [Decimal("200.00")] * 6
    assert plan.total_payments == Decimal("1200.00")


def test_interest_plan_has_interest_and_zero_final_balance():
    plan = calculate_plan(InstallmentRequest(cash_price="3600", installments=12, annual_interest_rate="7.5"))
    assert plan.total_interest > 0
    assert plan.schedule[-1].balance == Decimal("0.00")


def test_per_installment_fee_is_included_in_payment_and_total_fees():
    plan = calculate_plan(InstallmentRequest(cash_price="1200", installments=6, per_installment_fee="2.90"))
    assert plan.schedule[0].fee == Decimal("2.90")
    assert plan.regular_payment == Decimal("202.90")
    assert plan.total_fees == Decimal("17.40")


def test_upfront_fee_is_in_total_payments():
    plan = calculate_plan(InstallmentRequest(cash_price="1000", installments=2, upfront_fee="50"))
    assert plan.upfront_fee == Decimal("50.00")
    assert plan.total_payments == Decimal("1050.00")


def test_upfront_percent_fee():
    plan = calculate_plan(InstallmentRequest(cash_price="2000", installments=10, upfront_fee_percent="2.5"))
    assert plan.upfront_fee == Decimal("50.00")


def test_down_payment_reduces_financed_amount():
    plan = calculate_plan(InstallmentRequest(cash_price="9800", down_payment="2800", installments=4))
    assert plan.financed_amount == Decimal("7000.00")
    assert plan.total_payments == Decimal("9800.00")


def test_invalid_price_raises_code():
    with pytest.raises(InstallmentCalculationError) as err:
        calculate_plan(InstallmentRequest(cash_price="0", installments=1))
    assert err.value.code == "PRICE_MUST_BE_POSITIVE"


def test_invalid_installments_raises_code():
    with pytest.raises(InstallmentCalculationError) as err:
        calculate_plan(InstallmentRequest(cash_price="100", installments=0))
    assert err.value.code == "INSTALLMENTS_MUST_BE_POSITIVE"


def test_down_payment_equal_to_price_rejected():
    with pytest.raises(InstallmentCalculationError) as err:
        calculate_plan(InstallmentRequest(cash_price="100", down_payment="100", installments=1))
    assert err.value.code == "DOWN_PAYMENT_OUT_OF_RANGE"


def test_negative_rate_rejected():
    with pytest.raises(InstallmentCalculationError) as err:
        calculate_plan(InstallmentRequest(cash_price="100", installments=1, annual_interest_rate="-0.1"))
    assert err.value.code == "RATE_MUST_NOT_BE_NEGATIVE"


def test_negative_fee_rejected():
    with pytest.raises(InstallmentCalculationError) as err:
        calculate_plan(InstallmentRequest(cash_price="100", installments=1, per_installment_fee="-1"))
    assert err.value.code == "FEE_MUST_NOT_BE_NEGATIVE"


def test_invalid_date_rejected():
    with pytest.raises(InstallmentCalculationError) as err:
        parse_date("2026/31/12")
    assert err.value.code == "INVALID_DATE"


def test_slash_date_parses_and_formats():
    assert format_date_il(parse_date("15/07/2026")) == "15/07/2026"


def test_dash_date_parses_and_formats():
    assert format_date_il(parse_date("15-07-2026")) == "15/07/2026"


def test_iso_date_parses_and_formats():
    assert format_date_il(parse_date("2026-07-15")) == "15/07/2026"


def test_add_months_clips_month_end():
    start = parse_date("31/01/2026")
    assert format_date_il(add_months(start, 1)) == "28/02/2026"


def test_payment_day_clips_month_end():
    plan = calculate_plan(InstallmentRequest(cash_price="300", installments=3, first_due_date="31/01/2026", payment_day=31))
    assert [line.due_date.day for line in plan.schedule] == [31, 28, 31]


def test_compare_plans_sorts_by_total_paid():
    plans = compare_plans([
        InstallmentRequest(cash_price="1000", installments=12, annual_interest_rate="12"),
        InstallmentRequest(cash_price="1000", installments=4, annual_interest_rate="0"),
    ])
    assert plans[0].finance_charge == Decimal("0.00")


def test_refund_estimate_reports_remaining_principal():
    plan = calculate_plan(InstallmentRequest(cash_price="1200", installments=6))
    refund = estimate_refund(plan, installments_paid=2)
    assert refund["remaining_principal"] == "800.00"


def test_refund_rejects_out_of_range_paid_count():
    plan = calculate_plan(InstallmentRequest(cash_price="1200", installments=6))
    with pytest.raises(InstallmentCalculationError) as err:
        estimate_refund(plan, installments_paid=7)
    assert err.value.code == "INSTALLMENTS_PAID_OUT_OF_RANGE"


@pytest.mark.asyncio
async def test_async_calculate_matches_sync():
    request = InstallmentRequest(cash_price="2400", installments=12, annual_interest_rate="6.5")
    sync_plan = calculate_plan(request)
    async_plan = await async_calculate_plan(request)
    assert async_plan.total_payments == sync_plan.total_payments


@pytest.mark.asyncio
async def test_async_compare_returns_sorted_plans():
    plans = await async_compare_plans([
        InstallmentRequest(cash_price="2400", installments=12, annual_interest_rate="8"),
        InstallmentRequest(cash_price="2400", installments=3, annual_interest_rate="0"),
    ])
    assert plans[0].request.installments == 3


def test_client_facade_environment_and_calculate():
    client = InstallmentClient(environment="sandbox")
    plan = client.calculate(InstallmentRequest(cash_price="100", installments=1))
    assert plan.total_payments == Decimal("100.00")


def test_client_rejects_invalid_environment():
    with pytest.raises(InstallmentCalculationError) as err:
        InstallmentClient(environment="dev")
    assert err.value.code == "INVALID_ENVIRONMENT"


def test_money_strips_shekel_and_commas():
    assert money("₪1,234.567") == Decimal("1234.57")


def test_format_ils():
    assert format_ils("1234.5") == "₪1,234.50"


def test_to_json_preserves_shekel_sign_when_used_in_payload():
    plan = calculate_plan(InstallmentRequest(cash_price="100", installments=1))
    payload = {"amount": format_ils(plan.total_payments), "plan": plan.to_dict()}
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    assert "₪100.00" in rendered


def test_request_from_mapping():
    request = request_from_mapping({"cash_price": "500", "installments": "5", "annual_rate": "3"})
    plan = calculate_plan(request)
    assert plan.request.installments == 5


def test_disclosure_checks_include_legal_review_for_consumer():
    plan = calculate_plan(InstallmentRequest(cash_price="1000", installments=3))
    assert any(check.code == "LEGAL_REVIEW" for check in plan.disclosure_checks)


def test_vat_excluded_warns():
    plan = calculate_plan(InstallmentRequest(cash_price="1000", installments=3, vat_included=False))
    assert any("VAT" in warning for warning in plan.warnings)


def test_long_plan_warns():
    plan = calculate_plan(InstallmentRequest(cash_price="1000", installments=48))
    assert any("Long installment" in warning for warning in plan.warnings)


def test_high_fee_warning():
    plan = calculate_plan(InstallmentRequest(cash_price="1000", installments=3, upfront_fee="120"))
    assert any("Upfront fee" in warning for warning in plan.warnings)


def test_fee_only_plan_has_effective_cost():
    plan = calculate_plan(InstallmentRequest(cash_price="1200", installments=6, per_installment_fee="1.50"))
    assert plan.finance_charge == Decimal("9.00")
    assert plan.effective_annual_cost_percent is not None


def test_custom_rounding_quantum():
    assert money("10.03", "0.05") == Decimal("10.05")


def test_cli_calculate_json():
    runner = CliRunner()
    result = runner.invoke(main, ["--env", "sandbox", "calculate", "--price", "1200", "--installments", "6", "--output", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["environment"] == "sandbox"
    assert payload["total_payments"] == "1200.00"


def test_cli_compare_table():
    runner = CliRunner()
    result = runner.invoke(main, ["compare", "--price", "1000", "--installments", "3", "--installments", "12", "--annual-rate", "0"])
    assert result.exit_code == 0
    assert "Rank" in result.output


def test_cli_refund_json():
    runner = CliRunner()
    result = runner.invoke(main, ["refund", "--price", "1200", "--installments", "6", "--paid", "2"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["remaining_principal"] == "800.00"


def test_error_to_dict():
    err = InstallmentCalculationError("X", "message")
    assert err.to_dict() == {"code": "X", "message": "message"}


def test_current_israel_vat_rate_constant():
    assert CURRENT_ISRAEL_VAT_RATE_PERCENT == Decimal("18")


def test_gross_from_net_uses_current_vat_rate():
    assert gross_from_net("100") == Decimal("118.00")


def test_vat_components_from_gross():
    components = vat_components_from_gross("118")
    assert components["net_price"] == "100.00"
    assert components["vat_amount"] == "18.00"


def test_statutory_cancellation_fee_cap_uses_lower_of_percent_or_100():
    assert statutory_cancellation_fee_cap("1000") == Decimal("50.00")
    assert statutory_cancellation_fee_cap("3000") == Decimal("100.00")


def test_cli_vat_json_from_gross():
    runner = CliRunner()
    result = runner.invoke(main, ["vat", "--gross", "118", "--rate", "18"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["net_price"] == "100.00"
    assert payload["vat_amount"] == "18.00"


def test_cli_cancellation_fee_cap_json():
    runner = CliRunner()
    result = runner.invoke(main, ["cancellation-fee-cap", "--total", "3000"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["cancellation_fee_cap"] == "100.00"
