from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest
from typer.testing import CliRunner

from invoice_generator import (
    DocumentSpec,
    DocumentStore,
    LineItem,
    Party,
    ShaamClient,
    format_date_he,
    is_nine_digit_tax_id,
    is_valid_israeli_id,
    load_spec,
    money,
    normalize_tax_id,
    parse_date,
    render_hebrew_markdown,
    sample_credit_note,
    sample_export_zero_rate,
    sample_receipt_patur,
    sample_tax_invoice,
    sample_tax_invoice_receipt,
    shaam_threshold_for_date,
    vat_rate_for_date,
    write_json,
)
from invoice_generator.cli import app


def spec(data=None):
    return DocumentSpec.from_dict(data or sample_tax_invoice())


def test_parse_date_accepts_iso_dash_and_slash():
    assert parse_date("2026-06-15") == date(2026, 6, 15)
    assert parse_date("15-06-2026") == date(2026, 6, 15)
    assert parse_date("15/06/2026") == date(2026, 6, 15)


def test_hebrew_date_format_uses_slashes():
    assert format_date_he("15/06/2026") == "15/06/2026"


def test_vat_rate_before_and_after_2025():
    assert vat_rate_for_date("31/12/2024") == Decimal("0.17")
    assert vat_rate_for_date("01/01/2025") == Decimal("0.18")
    assert vat_rate_for_date("01/06/2026") == Decimal("0.18")


def test_money_rounds_half_up():
    assert money("1.005") == "1.01"


def test_tax_id_normalization_and_length():
    assert normalize_tax_id(" 123-456-789 ") == "123456789"
    assert is_nine_digit_tax_id("123-456-789") is True
    assert is_nine_digit_tax_id("123") is False


def test_israeli_id_checksum_known_valid():
    assert is_valid_israeli_id("000000018") is True
    assert is_valid_israeli_id("000000019") is False


def test_line_discount_amount_fixed_and_percent():
    line = LineItem(description="x", quantity=Decimal("2"), unit_price=Decimal("100"), discount=Decimal("10"), discount_percent=Decimal("5"))
    assert line.discount_amount() == Decimal("20")
    assert line.net() == Decimal("180")


def test_tax_invoice_totals_2026():
    totals = spec().calculate_totals()
    assert totals.subtotal == Decimal("18000.00")
    assert totals.vat == Decimal("3240.00")
    assert totals.total == Decimal("21240.00")


def test_receipt_has_zero_vat():
    totals = spec(sample_receipt_patur()).calculate_totals()
    assert totals.subtotal == Decimal("850.00")
    assert totals.vat == Decimal("0.00")
    assert totals.total == Decimal("850.00")


def test_credit_note_totals_are_negative():
    totals = spec(sample_credit_note()).calculate_totals()
    assert totals.subtotal == Decimal("-500.00")
    assert totals.vat == Decimal("-90.00")
    assert totals.total == Decimal("-590.00")


def test_allocation_required_for_2026_business_above_threshold():
    assert spec().requires_allocation() is True


def test_allocation_not_required_for_consumer():
    data = sample_tax_invoice()
    data["customer"]["customer_type"] = "consumer"
    assert spec(data).requires_allocation() is False


def test_allocation_not_required_below_threshold():
    data = sample_tax_invoice()
    data["lines"] = [{"description": "קטן", "quantity": "1", "unit_price": "100"}]
    assert spec(data).requires_allocation() is False


def test_allocation_not_required_when_amount_equals_threshold():
    data = sample_tax_invoice()
    data["issue_date"] = "01/06/2026"
    data["lines"] = [{"description": "בדיוק הסף", "quantity": "1", "unit_price": "5000"}]
    assert spec(data).requires_allocation() is False


def test_allocation_required_only_with_nonzero_vat_component():
    data = sample_tax_invoice()
    data["vat_rate"] = "0"
    data["zero_rate_basis"] = "עסקה בשיעור אפס בכפוף לאסמכתאות"
    assert spec(data).requires_allocation() is False


def test_allocation_threshold_schedule_uses_current_2026_rules():
    assert shaam_threshold_for_date("31/12/2024") == Decimal("25000")
    assert shaam_threshold_for_date("01/01/2025") == Decimal("20000")
    assert shaam_threshold_for_date("01/01/2026") == Decimal("10000")
    assert shaam_threshold_for_date("01/06/2026") == Decimal("5000")


def test_allocation_threshold_future_uses_latest():
    assert shaam_threshold_for_date("01/01/2030") == Decimal("5000")


def test_patur_cannot_issue_tax_invoice():
    data = sample_tax_invoice()
    data["issuer"]["status"] = "patur"
    result = spec(data).validate()
    assert not result.ok
    assert any("osek patur" in item for item in result.errors)


def test_receipt_requires_payment_details():
    data = sample_receipt_patur()
    data["payments"] = []
    result = spec(data).validate()
    assert not result.ok
    assert any("payment details" in item for item in result.errors)


def test_credit_note_requires_original_document():
    data = sample_credit_note()
    data["original_document_number"] = ""
    result = spec(data).validate()
    assert not result.ok
    assert any("original_document_number" in item for item in result.errors)


def test_zero_rate_export_has_no_vat_warning():
    result = spec(sample_export_zero_rate()).validate()
    assert result.ok
    assert all("zero_rate_basis" not in item for item in result.warnings)


def test_foreign_currency_without_exchange_note_warns():
    data = sample_export_zero_rate()
    data["notes"] = ""
    result = spec(data).validate()
    assert any("exchange-rate" in item for item in result.warnings)


def test_to_shaam_payload_contains_allocation_section():
    payload = spec().to_shaam_payload()
    assert payload["allocation"]["required"] is True
    assert payload["allocation"]["threshold"] == "5,000.00"
    assert payload["totals"]["total"] == "21,240.00"


def test_render_hebrew_markdown_uses_single_table_row_and_slash_date():
    text = render_hebrew_markdown(spec())
    assert "15/06/2026" in text
    assert text.count("ייעוץ אסטרטגי") == 1
    assert "₪18,000.00" in text


def test_document_to_dict_roundtrip():
    first = spec()
    second = DocumentSpec.from_dict(first.to_dict())
    assert second.calculate_totals().to_dict() == first.calculate_totals().to_dict()


def test_load_and_write_spec(tmp_path):
    path = tmp_path / "doc.json"
    write_json(sample_receipt_patur(), path)
    loaded = load_spec(path)
    assert loaded.document_number == "REC-2026-0011"


def test_document_store_create_and_load(tmp_path):
    store = DocumentStore(tmp_path)
    created = store.create(spec(), "sandbox")
    loaded = store.load(created.id, "sandbox")
    assert loaded.document_number == "INV-2026-0042"
    assert created.to_response()["id"] == created.id


def test_document_store_resolve_path_and_id(tmp_path):
    path = tmp_path / "doc.json"
    write_json(sample_receipt_patur(), path)
    store = DocumentStore(tmp_path / "store")
    created = store.create(spec(sample_receipt_patur()), "production")
    assert store.resolve(path, "production").document_number == "REC-2026-0011"
    assert store.resolve(created.id, "production").document_number == "REC-2026-0011"


def test_sync_shaam_client_posts_payload(monkeypatch):
    calls = {}

    class Response:
        def raise_for_status(self):
            calls["raised"] = True

        def json(self):
            return {"allocation_number": "123"}

    def fake_post(url, headers, json, timeout):
        calls.update({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return Response()

    import requests

    monkeypatch.setattr(requests, "post", fake_post)
    result = ShaamClient("https://example.test", "token").request_allocation(spec())
    assert result["allocation_number"] == "123"
    assert calls["url"] == "https://example.test/Invoices/v2/Approval"
    assert calls["headers"]["Authorization"] == "Bearer token"


@pytest.mark.asyncio
async def test_async_shaam_client_posts_payload(monkeypatch):
    calls = {}

    class Response:
        def raise_for_status(self):
            calls["raised"] = True

        def json(self):
            return {"allocation_number": "456"}

    class FakeAsyncClient:
        def __init__(self, timeout):
            calls["timeout"] = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, headers, json):
            calls.update({"url": url, "headers": headers, "json": json})
            return Response()

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    result = await ShaamClient("https://example.test", "token").request_allocation_async(spec())
    assert result["allocation_number"] == "456"
    assert calls["url"] == "https://example.test/Invoices/v2/Approval"


def test_cli_example_outputs_json():
    result = CliRunner().invoke(app, ["example", "--kind", "receipt"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["document_type"] == "receipt"


def test_cli_create_then_render_by_id(tmp_path):
    input_path = tmp_path / "invoice.json"
    store_dir = tmp_path / "store"
    write_json(sample_tax_invoice(), input_path)
    runner = CliRunner()
    created = runner.invoke(app, ["create", str(input_path), "--env", "sandbox", "--store-dir", str(store_dir)])
    assert created.exit_code == 0
    document_id = json.loads(created.stdout)["id"]
    rendered = runner.invoke(app, ["render", document_id, "--env", "sandbox", "--store-dir", str(store_dir)])
    assert rendered.exit_code == 0
    assert "חשבונית מס" in rendered.stdout


def test_cli_validate_path(tmp_path):
    path = tmp_path / "receipt.json"
    write_json(sample_receipt_patur(), path)
    result = CliRunner().invoke(app, ["validate", str(path)])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["ok"] is True


def test_tax_invoice_receipt_requires_payment_and_calculates():
    document = spec(sample_tax_invoice_receipt())
    assert document.validate().ok
    assert document.calculate_totals().total == Decimal("21240.00")
