from __future__ import annotations

import asyncio
import json
from decimal import Decimal

import pytest
from click.testing import CliRunner

from foreign_currency_invoicing_cli import main
from foreign_currency_invoicing_client import (
    ExchangeRate,
    InvoiceLine,
    InvoiceValidationError,
    RateLookupError,
    VatCategory,
    async_fetch_rate,
    build_boi_current_rate_url,
    build_boi_rate_url,
    calculate_invoice,
    decimal_to_str,
    default_vat_rate,
    format_il_date,
    generate_invoice_id,
    invoice_from_json_lines,
    load_invoice_result,
    normalize_currency,
    normalize_vat_category,
    parse_boi_rate_response,
    parse_date,
    quantize_money,
    render_invoice_disclaimer,
    resolve_rate_with_fallback,
    save_invoice_result,
    to_decimal,
)


def test_normalize_currency_uppercases() -> None:
    assert normalize_currency("usd") == "USD"


def test_normalize_currency_rejects_bad_code() -> None:
    with pytest.raises(InvoiceValidationError):
        normalize_currency("US")


def test_parse_date_accepts_israeli_slashes() -> None:
    assert parse_date("02/06/2026").isoformat() == "2026-06-02"


def test_parse_date_accepts_iso_timestamp() -> None:
    assert parse_date("2026-06-02T10:11:12").isoformat() == "2026-06-02"


def test_format_il_date_uses_slashes() -> None:
    assert format_il_date("2026-06-02") == "02/06/2026"


def test_default_vat_rate_2024_is_17_percent() -> None:
    assert default_vat_rate("31/12/2024") == Decimal("0.17")


def test_default_vat_rate_2025_is_18_percent() -> None:
    assert default_vat_rate("01/01/2025") == Decimal("0.18")


def test_invoice_line_validates_discount() -> None:
    with pytest.raises(InvoiceValidationError):
        InvoiceLine("Service", "1", "10", discount="11")


def test_vat_category_alias() -> None:
    assert normalize_vat_category("zero-rate") is VatCategory.ZERO


def test_quantize_money_rounds_half_up() -> None:
    assert quantize_money(Decimal("10.005")) == Decimal("10.01")


def test_decimal_to_str_trims_hash_places() -> None:
    assert decimal_to_str(Decimal("1.230000"), places="0.######") == "1.23"


def test_exchange_rate_unit_for_jpy() -> None:
    rate = ExchangeRate("JPY", "2.40", unit="100", date=parse_date("02/06/2026"))
    assert rate.ils_per_unit == Decimal("0.024000")


def test_build_rate_url_contains_sdmx_series_and_date() -> None:
    url = build_boi_rate_url("eur", "02/06/2026")
    assert "RER_EUR_ILS" in url
    assert "startPeriod=2026-06-02" in url
    assert "endPeriod=2026-06-02" in url
    assert "format=csv" in url


def test_build_current_rate_url_contains_key() -> None:
    url = build_boi_current_rate_url("usd", base_url="https://example.test/rate", as_xml=True)
    assert url == "https://example.test/rate?key=USD&asXml=true"


def test_parse_json_current_exchange_rate() -> None:
    payload = {"key": "USD", "currentExchangeRate": "3.7000", "unit": 1, "lastUpdate": "02/06/2026"}
    rate = parse_boi_rate_response(payload, "USD")
    assert rate.rate == Decimal("3.7000")
    assert rate.date.isoformat() == "2026-06-02"


def test_parse_nested_json_rate() -> None:
    payload = {"exchangeRates": [{"currencyCode": "EUR", "rate": "4.0", "unit": "1", "date": "2026-06-02"}]}
    rate = parse_boi_rate_response(json.dumps(payload), "EUR")
    assert rate.currency == "EUR"


def test_parse_xml_rate() -> None:
    payload = """
    <CURRENCIES><CURRENCY><CURRENCYCODE>GBP</CURRENCYCODE><RATE>4.7</RATE><UNIT>1</UNIT><LAST_UPDATE>02/06/2026</LAST_UPDATE></CURRENCY></CURRENCIES>
    """
    rate = parse_boi_rate_response(payload, "GBP")
    assert rate.rate == Decimal("4.7")


def test_parse_sdmx_csv_rate() -> None:
    payload = "TIME_PERIOD,OBS_VALUE,SERIES_CODE,BASE_CURRENCY,COUNTER_CURRENCY\n2026-06-02,3.7000,RER_USD_ILS,USD,ILS\n"
    rate = parse_boi_rate_response(payload, "USD")
    assert rate.rate == Decimal("3.7000")
    assert rate.source == "Bank of Israel SDMX"


def test_parse_empty_payload_rejected() -> None:
    with pytest.raises(RateLookupError):
        parse_boi_rate_response("", "USD")


def test_calculate_standard_vat() -> None:
    result = calculate_invoice([{"description": "Work", "quantity": "2", "unit_price": "100"}], "USD", "02/06/2026", "3.5")
    assert result.totals["net_foreign"] == Decimal("200.00")
    assert result.totals["vat_ils"] == Decimal("126.00")


def test_calculate_zero_vat_warns_without_note() -> None:
    result = calculate_invoice([{"description": "Export", "quantity": "1", "unit_price": "100", "vat_category": "zero"}], "USD", "02/06/2026", "3.5")
    assert result.totals["vat_ils"] == Decimal("0.00")
    assert result.warnings


def test_calculate_ils_without_rate() -> None:
    result = calculate_invoice([{"description": "Local", "quantity": "1", "unit_price": "100"}], "ILS", "02/06/2026")
    assert result.exchange_rate.ils_per_unit == Decimal("1.000000")


def test_calculate_requires_rate_for_usd() -> None:
    with pytest.raises(InvoiceValidationError):
        calculate_invoice([{"description": "Work", "quantity": "1", "unit_price": "100"}], "USD", "02/06/2026")


def test_invoice_from_json_lines() -> None:
    payload = '[{"description":"Work","quantity":"1","unit_price":"50"}]'
    result = invoice_from_json_lines(payload, "USD", "02/06/2026", "3.5")
    assert result.totals["total_foreign"] == Decimal("59.00")


def test_invoice_id_is_stable() -> None:
    payload = {"a": 1, "b": 2}
    assert generate_invoice_id(payload) == generate_invoice_id({"b": 2, "a": 1})


def test_save_and_load_invoice(tmp_path) -> None:
    result = calculate_invoice([{"description": "Work", "quantity": "1", "unit_price": "10"}], "USD", "02/06/2026", "3.5")
    save_invoice_result(result, tmp_path)
    loaded = load_invoice_result(result.invoice_id, tmp_path)
    assert loaded["id"] == result.invoice_id


def test_render_invoice_disclaimer_mentions_rate() -> None:
    result = calculate_invoice([{"description": "Work", "quantity": "1", "unit_price": "10"}], "USD", "02/06/2026", "3.5")
    assert "Exchange rate" in render_invoice_disclaimer(result)


def test_to_decimal_rejects_text() -> None:
    with pytest.raises(InvoiceValidationError):
        to_decimal("not-number")


def test_resolve_rate_with_fallback_uses_second_day() -> None:
    calls = []

    def fake_fetcher(url: str) -> str:
        calls.append(url)
        if len(calls) == 1:
            raise OSError("holiday")
        return json.dumps({"key": "USD", "currentExchangeRate": "3.6", "unit": 1, "lastUpdate": "01/06/2026"})

    rate = resolve_rate_with_fallback("USD", "02/06/2026", fetcher=fake_fetcher)
    assert rate.rate == Decimal("3.6")
    assert len(calls) == 2


def test_async_fetch_rate_with_async_fetcher() -> None:
    async def fake(url: str) -> str:
        return json.dumps({"key": "USD", "currentExchangeRate": "3.6", "unit": 1, "lastUpdate": "02/06/2026"})

    rate = asyncio.run(async_fetch_rate("USD", "02/06/2026", async_fetcher=fake))
    assert rate.rate == Decimal("3.6")


def test_cli_sample_lines() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["sample-lines", "--env", "sandbox"])
    assert result.exit_code == 0
    assert "Consulting services" in result.output


def test_cli_create_and_show_chained(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FCI_INVOICE_DIR", str(tmp_path))
    runner = CliRunner()
    create = runner.invoke(
        main,
        [
            "create",
            "--env",
            "sandbox",
            "--currency",
            "USD",
            "--issue-date",
            "02/06/2026",
            "--exchange-rate",
            "3.5",
            "--lines-json",
            '[{"description":"Work","quantity":"1","unit_price":"10"}]',
        ],
    )
    assert create.exit_code == 0
    invoice_id = json.loads(create.output)["id"]
    show = runner.invoke(main, ["show", "--env", "sandbox", invoice_id])
    assert show.exit_code == 0
    assert json.loads(show.output)["id"] == invoice_id


def test_cli_rate_url() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["rate-url", "--currency", "USD", "--as-of-date", "02/06/2026"])
    assert result.exit_code == 0
    assert "RER_USD_ILS" in result.output
    assert "startPeriod=2026-06-02" in result.output


def test_cli_env_lines_json(monkeypatch) -> None:
    monkeypatch.setenv("FCI_EXCHANGE_RATE", "3.5")
    monkeypatch.setenv("FCI_LINES_JSON", '[{"description":"Env","quantity":"1","unit_price":"10"}]')
    runner = CliRunner()
    result = runner.invoke(main, ["create", "--env", "sandbox", "--currency", "USD", "--issue-date", "02/06/2026", "--no-save"])
    assert result.exit_code == 0
    assert json.loads(result.output)["lines"][0]["description"] == "Env"
