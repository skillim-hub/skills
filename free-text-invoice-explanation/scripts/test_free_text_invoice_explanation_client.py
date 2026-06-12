from __future__ import annotations

import json
from decimal import Decimal

import pytest
from typer.testing import CliRunner

from free_text_invoice_explanation import (
    ExplanationOptions,
    InvoiceContext,
    InvoiceExplanationClient,
    InvoiceLine,
    explain_invoice,
    explain_line,
)
from free_text_invoice_explanation.cli import app


def test_hebrew_line_contains_currency_and_vat():
    result = explain_line({"description": "ייעוץ עסקי", "unit_price": "1000"})
    assert "₪1,000.00" in result.plain_text
    assert "מע״מ" in result.plain_text


def test_english_line_contains_plain_description():
    result = explain_line(
        {"description": "Website maintenance", "unit_price": "250"},
        {"language": "en"},
        {"language": "en"},
    )
    assert "Website maintenance" in result.plain_text
    assert "VAT" in result.plain_text


def test_total_calculation_with_vat():
    result = explain_line({"description": "שירות", "quantity": "2", "unit_price": "100", "vat_rate": "18"})
    assert result.amount_before_vat == Decimal("200.00")
    assert result.vat_amount == Decimal("36.00")
    assert result.amount_after_vat == Decimal("236.00")


def test_exempt_dealer_zero_vat():
    result = explain_line(
        {"description": "שירות", "unit_price": "100", "vat_rate": "18"},
        {"business_type": "exempt_dealer", "language": "he"},
    )
    assert result.vat_amount == Decimal("0.00")
    assert "vat_exempt" in result.tags


def test_explicit_vat_exempt_line():
    result = explain_line({"description": "פטור", "unit_price": "100", "exempt_from_vat": True})
    assert result.amount_after_vat == Decimal("100.00")


def test_reverse_charge_zero_vat():
    result = explain_line({"description": "שירות חוץ", "unit_price": "100", "reverse_charge": True})
    assert result.vat_amount == Decimal("0.00")
    assert "reverse_charge" in result.tags


def test_reimbursement_tag_and_text():
    result = explain_line({"description": "אגרת שליחות", "unit_price": "50", "reimbursable": True})
    assert "reimbursement" in result.tags
    assert "החזר הוצאה" in result.plain_text


def test_credit_note_tag():
    result = explain_line(
        {"description": "החזר", "unit_price": "-25", "vat_rate": "18"},
        {"document_type": "credit_note", "language": "he"},
    )
    assert "credit" in result.tags
    assert result.amount_before_vat == Decimal("-25.00")


def test_negative_non_credit_warns():
    result = explain_line({"description": "הנחה", "unit_price": "-10"})
    codes = {issue.code for issue in result.issues}
    assert "negative_price" in codes


def test_receipt_warning():
    result = explain_line({"description": "תשלום", "unit_price": "100"}, {"document_type": "receipt"})
    assert any(issue.code == "receipt_vat_language" for issue in result.issues)


def test_invalid_vat_rate_error():
    result = explain_line({"description": "שירות", "unit_price": "100", "vat_rate": "150"})
    assert any(issue.severity == "error" for issue in result.issues)


def test_non_positive_quantity_error():
    result = explain_line({"description": "שירות", "quantity": "0", "unit_price": "100"})
    assert any(issue.code == "non_positive_quantity" for issue in result.issues)


def test_missing_description_error():
    result = explain_line({"description": "   ", "unit_price": "100"})
    assert any(issue.code == "missing_description" for issue in result.issues)


def test_uncommon_currency_info():
    result = explain_line({"description": "שירות", "unit_price": "100", "currency": "JPY"})
    assert any(issue.code == "uncommon_currency" for issue in result.issues)


def test_invoice_summary_totals():
    result = explain_invoice([
        {"description": "א", "unit_price": "100"},
        {"description": "ב", "unit_price": "200"},
    ])
    assert result["line_count"] == 2
    assert result["totals"]["amount_before_vat"] == "300.00"
    assert result["totals"]["vat_amount"] == "54.00"


def test_payload_explanation_from_json_string():
    client = InvoiceExplanationClient()
    payload = json.dumps({"lines": [{"description": "בדיקה", "unit_price": "10"}]}, ensure_ascii=False)
    result = client.explain_payload(payload)
    assert result["line_count"] == 1


def test_payload_requires_lines():
    client = InvoiceExplanationClient()
    with pytest.raises(ValueError):
        client.explain_payload({"items": []})


def test_format_ils_money():
    client = InvoiceExplanationClient()
    assert client.format_money("1234.5") == "₪1,234.50"


def test_format_foreign_money():
    client = InvoiceExplanationClient()
    assert client.format_money("99.9", "USD") == "99.90 USD"


def test_format_date_localized():
    client = InvoiceExplanationClient()
    assert client.format_date("2026-03-07") == "07/03/2026"


def test_format_date_iso_option():
    client = InvoiceExplanationClient()
    assert client.format_date("07/03/2026", ExplanationOptions(date_format="YYYY-MM-DD")) == "2026-03-07"


@pytest.mark.asyncio
async def test_async_line():
    client = InvoiceExplanationClient()
    result = await client.async_explain_line({"description": "בדיקה", "unit_price": "15"})
    assert result.amount_after_vat == Decimal("17.70")


@pytest.mark.asyncio
async def test_async_invoice():
    client = InvoiceExplanationClient()
    result = await client.async_explain_invoice([{"description": "בדיקה", "unit_price": "15"}])
    assert result["line_count"] == 1


def test_detail_short_omits_issue_text():
    result = explain_line(
        {"description": "שירות", "quantity": "0", "unit_price": "100"},
        {"language": "en"},
        {"language": "en", "detail_level": "short"},
    )
    assert "Check required" not in result.plain_text


def test_detailed_adds_caveat():
    result = explain_line(
        {"description": "שירות", "unit_price": "100"},
        {"language": "en", "include_legal_caveat": True},
        {"language": "en", "detail_level": "detailed"},
    )
    assert "Verify classification" in result.plain_text


def test_without_amount_breakdown():
    result = explain_line(
        {"description": "שירות", "unit_price": "100"},
        None,
        {"include_amount_breakdown": False},
    )
    assert "הסכום לפני מע״מ" not in result.plain_text


def test_service_period_tag_and_text():
    result = explain_line({"description": "תחזוקה", "unit_price": "100", "service_period": "01/03/2026-31/03/2026"})
    assert "service_period" in result.tags
    assert "תקופת השירות" in result.plain_text


def test_cli_one_command():
    runner = CliRunner()
    result = runner.invoke(app, ["one", "ייעוץ", "--unit-price", "100"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["amount_after_vat"] == "118.00"


def test_cli_explain_from_file(tmp_path):
    runner = CliRunner()
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps({"lines": [{"description": "ייעוץ", "unit_price": "100"}]}, ensure_ascii=False), encoding="utf-8")
    result = runner.invoke(app, ["explain", "--input", str(payload)])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["line_count"] == 1


def test_cli_explain_output_file(tmp_path):
    runner = CliRunner()
    payload = tmp_path / "payload.json"
    output = tmp_path / "out.json"
    payload.write_text(json.dumps({"lines": [{"description": "ייעוץ", "unit_price": "100"}]}, ensure_ascii=False), encoding="utf-8")
    result = runner.invoke(app, ["explain", "--input", str(payload), "--output", str(output)])
    assert result.exit_code == 0
    assert json.loads(output.read_text(encoding="utf-8"))["totals"]["amount_after_vat"] == "118.00"


def test_title_for_credit_english():
    result = explain_line(
        {"description": "refund", "unit_price": "-10"},
        {"language": "en", "document_type": "credit_note"},
        {"language": "en"},
    )
    assert result.title.startswith("Credit for")


def test_to_json_uses_hebrew_without_ascii_escaping():
    result = explain_line({"description": "ייעוץ", "unit_price": "100"})
    assert "\\u" not in result.to_json()


def test_public_module_function():
    result = explain_invoice([InvoiceLine(description="ייעוץ", unit_price="10")])
    assert result["line_count"] == 1


def test_package_version_is_web_validated_minor_bump():
    import free_text_invoice_explanation

    assert free_text_invoice_explanation.__version__ == "2.1.0"


def test_default_vat_rate_remains_configurable_at_18_percent():
    client = InvoiceExplanationClient()
    result = client.explain_line({"description": "ייעוץ", "quantity": "1", "unit_price": "100"})

    assert result.vat_amount == Decimal("18.00")
    custom = client.explain_line({"description": "ייעוץ", "quantity": "1", "unit_price": "100", "vat_rate": "0"})
    assert custom.vat_amount == Decimal("0.00")
