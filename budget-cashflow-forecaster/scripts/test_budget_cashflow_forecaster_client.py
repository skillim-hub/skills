from __future__ import annotations

import asyncio
from datetime import date

import pytest

import budget_cashflow_forecaster as client


def base_config(**updates):
    data = {
        "opening_balance": 10000,
        "start_month": "2026-01",
        "months": 3,
        "cash_in": [
            {"date": "2026-01-10", "amount": 11800, "description": "Revenue", "taxable": True, "gross": True}
        ],
        "cash_out": [
            {"date": "2026-01-05", "amount": 3000, "description": "Rent"}
        ],
        "tax_profile": {
            "vat_rate": 0.18,
            "vat_cadence": "monthly",
            "income_tax_advance_rate": 0.08,
            "bituach_leumi_rate": 0.12,
            "reviewed_on": "2026-01-01",
            "source_note": "verify before filing",
        },
        "buffer": 1000,
    }
    data.update(updates)
    return data


def test_month_sequence_crosses_year():
    assert client.month_sequence("2026-11", 4) == ["2026-11", "2026-12", "2027-01", "2027-02"]


def test_invalid_month_raises():
    with pytest.raises(client.ForecastError, match="INVALID_MONTH"):
        client.ForecastConfig.from_mapping(base_config(start_month="2026/01"))


def test_negative_months_raise():
    with pytest.raises(client.ForecastError, match="NEGATIVE_MONTHS"):
        client.ForecastConfig.from_mapping(base_config(months=0))


def test_too_long_raises():
    with pytest.raises(client.ForecastError, match="TOO_LONG"):
        client.ForecastConfig.from_mapping(base_config(months=61))


def test_parse_date_valid():
    assert client.parse_date("2026-01-31") == date(2026, 1, 31)


def test_parse_date_invalid():
    with pytest.raises(client.ForecastError, match="INVALID_DATE"):
        client.parse_date("31/01/2026")


def test_negative_amount_raises():
    cfg = base_config(cash_in=[{"date": "2026-01-01", "amount": -1, "description": "bad"}])
    with pytest.raises(client.ForecastError, match="NEGATIVE_AMOUNT"):
        client.ForecastConfig.from_mapping(cfg)


def test_unknown_cadence_raises():
    cfg = base_config(tax_profile={"vat_cadence": "quarterly"})
    with pytest.raises(client.ForecastError, match="UNKNOWN_CADENCE"):
        client.ForecastConfig.from_mapping(cfg)


def test_rate_over_one_raises():
    cfg = base_config(tax_profile={"vat_rate": 18})
    with pytest.raises(client.ForecastError, match="RATE_TOO_HIGH"):
        client.ForecastConfig.from_mapping(cfg)


def test_unknown_environment_raises():
    cfg = base_config(environment="staging")
    with pytest.raises(client.ForecastError, match="UNKNOWN_ENVIRONMENT"):
        client.ForecastConfig.from_mapping(cfg)


def test_forecast_has_three_rows():
    result = client.CashFlowForecaster().forecast(base_config())
    assert len(result.rows) == 3


def test_result_has_id_and_environment():
    result = client.CashFlowForecaster().forecast(base_config(environment="production"))
    assert result.forecast_id
    assert result.environment == "production"


def test_first_month_closing_balance():
    result = client.CashFlowForecaster().forecast(base_config())
    assert result.rows[0].closing_balance == 18800


def test_vat_reserve_from_gross():
    profile = client.TaxProfile.from_mapping({"vat_rate": 0.18, "vat_cadence": "monthly"})
    tx = client.Transaction.from_mapping({"date": "2026-01-01", "amount": 1180, "description": "gross", "gross": True})
    assert client.estimate_tax_reserve([tx], profile) == 180


def test_vat_reserve_from_net():
    profile = client.TaxProfile.from_mapping({"vat_rate": 0.18, "vat_cadence": "monthly"})
    tx = client.Transaction.from_mapping({"date": "2026-01-01", "amount": 1000, "description": "net", "gross": False})
    assert client.estimate_tax_reserve([tx], profile) == 180


def test_income_tax_reserve_added():
    profile = client.TaxProfile.from_mapping({"income_tax_advance_rate": 0.1})
    tx = client.Transaction.from_mapping({"date": "2026-01-01", "amount": 1000, "description": "income"})
    assert client.estimate_tax_reserve([tx], profile) == 100


def test_bituach_reserve_added():
    profile = client.TaxProfile.from_mapping({"bituach_leumi_rate": 0.12})
    tx = client.Transaction.from_mapping({"date": "2026-01-01", "amount": 1000, "description": "income"})
    assert client.estimate_tax_reserve([tx], profile) == 120


def test_non_taxable_excluded():
    profile = client.TaxProfile.from_mapping({"vat_rate": 0.18, "vat_cadence": "monthly", "income_tax_advance_rate": 0.1})
    tx = client.Transaction.from_mapping({"date": "2026-01-01", "amount": 1000, "description": "gift", "taxable": False})
    assert client.estimate_tax_reserve([tx], profile) == 0


def test_monthly_tax_paid_second_month():
    result = client.CashFlowForecaster().forecast(base_config())
    assert result.rows[1].tax_paid > 0


def test_bimonthly_tax_paid_third_month():
    cfg = base_config(tax_profile={"vat_rate": 0.18, "vat_cadence": "bimonthly", "reviewed_on": "2026-01-01"})
    result = client.CashFlowForecaster().forecast(cfg)
    assert result.rows[0].tax_paid == 0
    assert result.rows[1].tax_paid == 0
    assert result.rows[2].tax_paid > 0


def test_buffer_warning():
    cfg = base_config(opening_balance=1000, cash_in=[], cash_out=[], tax_profile={}, buffer=2000)
    result = client.CashFlowForecaster().forecast(cfg)
    assert result.rows[0].status == "buffer_warning"


def test_negative_cash_status():
    cfg = base_config(opening_balance=1000, cash_in=[], cash_out=[{"date": "2026-01-01", "amount": 5000, "description": "large"}], tax_profile={}, buffer=0)
    result = client.CashFlowForecaster().forecast(cfg)
    assert result.rows[0].status == "negative_cash"


def test_summary_first_negative():
    cfg = base_config(opening_balance=1000, cash_in=[], cash_out=[{"date": "2026-01-01", "amount": 5000, "description": "large"}], tax_profile={}, buffer=0)
    result = client.CashFlowForecaster().forecast(cfg)
    assert result.summary["first_negative_month"] == "2026-01"


def test_warnings_for_no_buffer():
    cfg = base_config(buffer=0)
    result = client.CashFlowForecaster().forecast(cfg)
    assert any("NO_BUFFER" in w for w in result.warnings)


def test_warnings_for_unverified_tax_rate():
    cfg = base_config(tax_profile={"vat_rate": 0.18, "vat_cadence": "monthly"})
    result = client.CashFlowForecaster().forecast(cfg)
    assert any("UNVERIFIED_TAX_RATE" in w for w in result.warnings)


def test_production_review_warning():
    cfg = base_config(environment="production", tax_profile={"vat_rate": 0.18, "vat_cadence": "monthly", "reviewed_on": "2026-01-01"})
    result = client.CashFlowForecaster().forecast(cfg)
    assert any("PRODUCTION_REVIEW" in w for w in result.warnings)


def test_format_ils():
    assert client.format_ils(1234.5) == "₪1,234.50"


def test_format_he_date():
    assert client.format_he_date(date(2026, 6, 2)) == "02/06/2026"


def test_load_json(tmp_path):
    path = tmp_path / "forecast.json"
    path.write_text('{"opening_balance": 1, "start_month": "2026-01", "months": 1}', encoding="utf-8")
    assert client.load_json(path)["opening_balance"] == 1


def test_missing_json_file():
    with pytest.raises(client.ForecastError, match="MISSING_FILE"):
        client.load_json("does-not-exist.json")


def test_write_csv(tmp_path):
    result = client.CashFlowForecaster().forecast(base_config())
    out = tmp_path / "out.csv"
    client.write_csv(result, out)
    assert "closing_balance" in out.read_text(encoding="utf-8")


def test_load_csv_as_config(tmp_path):
    path = tmp_path / "tx.csv"
    path.write_text("date,amount,direction,description\n2026-01-01,100,in,Receipt\n2026-01-02,50,out,Payment\n", encoding="utf-8")
    cfg = client.load_csv_as_config(path, opening_balance=0, start_month="2026-01", months=1, environment="production")
    assert len(cfg["cash_in"]) == 1
    assert len(cfg["cash_out"]) == 1
    assert cfg["environment"] == "production"


def test_csv_schema_error(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("date,amount\n2026-01-01,100\n", encoding="utf-8")
    with pytest.raises(client.ForecastError, match="CSV_SCHEMA_ERROR"):
        client.load_csv_as_config(path, opening_balance=0, start_month="2026-01", months=1)


def test_compare_results():
    result = client.CashFlowForecaster().forecast(base_config())
    rows = client.compare_results({"base": result})
    assert rows[0]["scenario"] == "base"


def test_async_forecast_matches_sync_ignoring_generated_metadata():
    cfg = base_config()
    sync_result = client.CashFlowForecaster().forecast(cfg).as_dict()

    async def run():
        return await client.AsyncCashFlowForecaster().forecast(cfg)

    async_result = asyncio.run(run()).as_dict()
    for payload in (sync_result, async_result):
        payload.pop("id", None)
        payload.pop("created_at", None)
    assert async_result == sync_result


def test_reserve_mode_none():
    cfg = base_config(tax_profile={"vat_rate": 0.18, "vat_cadence": "monthly", "reserve_mode": "none"})
    result = client.CashFlowForecaster().forecast(cfg)
    assert result.rows[0].tax_reserved == 0


def test_cash_out_does_not_create_tax_reserve():
    cfg = base_config(cash_in=[], cash_out=[{"date": "2026-01-01", "amount": 1000, "description": "supplier"}])
    result = client.CashFlowForecaster().forecast(cfg)
    assert result.rows[0].tax_reserved == 0


def test_forecast_store_roundtrip(tmp_path):
    result = client.CashFlowForecaster().forecast(base_config())
    store = client.ForecastStore(tmp_path)
    forecast_id = store.save(result)
    loaded = store.load(forecast_id)
    assert loaded["id"] == forecast_id


def test_forecast_store_rejects_bad_id(tmp_path):
    store = client.ForecastStore(tmp_path)
    with pytest.raises(client.ForecastError, match="INVALID_ID"):
        store.load("../bad")


def test_importable_package_has_client():
    assert hasattr(client, "CashFlowForecaster")
