from __future__ import annotations
import asyncio, datetime as dt, json
from pathlib import Path
import pytest
import pension_fund_tracker as module

def client(): return module.PensionFundTrackerClient()

def sample_rows():
    return [
        {"מספר קופה":"12345","שם קופה":"קרן א","שם גוף מנהל":"גוף א","תאריך דיווח":"31/12/2025","תשואה חודשית":"0.82%","תשואה 36 חודשים אחרונים":"18.2","דמי ניהול מהפקדה":"1.5","דמי ניהול מצבירה":"0.2",'נכסים במיליוני ש"ח':"1,234.56"},
        {"מספר קופה":"67890","שם קופה":"קרן ב","שם גוף מנהל":"גוף ב","תאריך דיווח":"31/12/2025","תשואה חודשית":"0.75","תשואה 36 חודשים אחרונים":"17.9","דמי ניהול מהפקדה":"1.2","דמי ניהול מצבירה":"0.24"},
        {"מספר קופה":"12345","שם קופה":"קרן א","שם גוף מנהל":"גוף א","תאריך דיווח":"30/11/2025","תשואה חודשית":"-0.2","תשואה 36 חודשים אחרונים":"17.0","דמי ניהול מהפקדה":"1.5","דמי ניהול מצבירה":"0.2"},
    ]

def test_parse_number_percent(): assert module.parse_number("0.20%") == pytest.approx(0.2)
def test_parse_number_decimal_comma(): assert module.parse_number("1,23") == pytest.approx(1.23)
def test_parse_number_thousands(): assert module.parse_number("1,234.56") == pytest.approx(1234.56)
def test_parse_number_currency(): assert module.parse_number("₪2,000") == pytest.approx(2000)
def test_parse_number_parentheses_negative(): assert module.parse_number("(1.5)") == pytest.approx(-1.5)
def test_parse_date_dd_mm_yyyy(): assert module.parse_date("31/12/2025") == dt.date(2025,12,31)
def test_parse_date_iso(): assert module.parse_date("2025-12-31") == dt.date(2025,12,31)
def test_parse_date_month_year(): assert module.parse_date("12/2025") == dt.date(2025,12,1)
def test_parse_date_yyyymm(): assert module.parse_date("202512") == dt.date(2025,12,1)

def test_normalize_hebrew_row():
    r = module.normalize_row(sample_rows()[0])
    assert r.fund_id == "12345" and r.fund_name == "קרן א" and r.provider == "גוף א"
    assert r.monthly_return_pct == pytest.approx(0.82)
    assert r.assets_millions_nis == pytest.approx(1234.56)

def test_normalize_english_row():
    r = module.normalize_row({"fund_id":"111","fund_name":"Fund","provider":"Provider","report_date":"2025-12-31","monthly_return_pct":"1.1"})
    assert r.fund_id == "111" and r.report_date == dt.date(2025,12,31) and r.monthly_return_pct == pytest.approx(1.1)

def test_strict_normalize_missing_raises():
    with pytest.raises(module.ValidationError): module.normalize_row({"שם קופה":"קרן"}, strict=True)

def test_load_csv_utf8_sig(tmp_path):
    p = tmp_path/"data.csv"; p.write_text("מספר קופה,שם קופה,תאריך דיווח\n1,קרן,31-12-2025\n", encoding="utf-8-sig")
    records = client().load_csv(p)
    assert len(records) == 1 and records[0].fund_id == "1"

def test_load_csv_semicolon(tmp_path):
    p = tmp_path/"data.csv"; p.write_text("fund_id;fund_name;report_date\n1;Fund;2025-12-31\n", encoding="utf-8")
    records = client().load_csv(p, encoding="utf-8")
    assert len(records) == 1 and records[0].fund_name == "Fund"

def test_load_json_list(tmp_path):
    p = tmp_path/"data.json"; p.write_text(json.dumps([{"fund_id":"1","fund_name":"Fund","report_date":"2025-12-31"}]), encoding="utf-8")
    assert client().load_json(p)[0].fund_id == "1"

def test_load_json_records_key(tmp_path):
    p = tmp_path/"data.json"; p.write_text(json.dumps({"records":[{"fund_id":"1","fund_name":"Fund","report_date":"2025-12-31"}]}), encoding="utf-8")
    assert client().load_json(p)[0].fund_name == "Fund"

def test_validate_missing_fields():
    issues = client().validate_records([module.PensionRecord(fund_id="", fund_name="", report_date=None)])
    codes = {i.code for i in issues}
    assert {"MISSING_FUND_ID","MISSING_FUND_NAME","MISSING_REPORT_DATE"} <= codes

def test_validate_implausible_return_and_fee():
    r = module.PensionRecord(fund_id="1", fund_name="Fund", report_date=dt.date(2025,12,31), monthly_return_pct=150, management_fee_assets_pct=25)
    codes = {i.code for i in client().validate_records([r])}
    assert "IMPLAUSIBLE_RETURN" in codes and "IMPLAUSIBLE_FEE" in codes

def test_validate_duplicate_record():
    r = module.PensionRecord(fund_id="1", fund_name="Fund", report_date=dt.date(2025,12,31))
    assert any(i.code == "DUPLICATE_RECORD" for i in client().validate_records([r,r]))

def test_latest_by_fund():
    records = [module.normalize_row(row) for row in sample_rows()]
    by_id = {r.fund_id: r for r in client().latest_by_fund(records)}
    assert by_id["12345"].report_date == dt.date(2025,12,31)

def test_rank_descending():
    ranked = client().rank([module.normalize_row(row) for row in sample_rows()], metric="trailing_36m_return_pct", top=2)
    assert ranked[0].fund_id == "12345"

def test_rank_ascending_fee():
    ranked = client().rank([module.normalize_row(row) for row in sample_rows()], metric="management_fee_assets_pct", top=2, ascending=True)
    assert ranked[0].fund_id == "12345"

def test_rank_unknown_metric_raises():
    with pytest.raises(ValueError): client().rank([], metric="unknown")

def test_compare_selected_funds():
    rows = client().compare([module.normalize_row(row) for row in sample_rows()], ["12345","67890","000"])
    assert rows[0]["fund_id"] == "12345" and rows[2]["missing"] is True

def test_filter_provider_and_dates():
    records = [module.normalize_row(row) for row in sample_rows()]
    rows = client().filter_records(records, provider="גוף א", start_date=dt.date(2025,12,1), end_date=dt.date(2025,12,31))
    assert len(rows) == 1 and rows[0].fund_id == "12345"

def test_fee_impact_no_fees_matches_gross():
    result = client().estimate_fee_impact(monthly_contribution=1000, years=1, annual_return_pct=5, deposit_fee_pct=0, asset_fee_pct=0, starting_balance=0)
    assert result.gross_no_fee_balance == pytest.approx(result.net_with_fees_balance)

def test_fee_impact_with_fees_lowers_balance():
    result = client().estimate_fee_impact(monthly_contribution=1000, years=10, annual_return_pct=5, deposit_fee_pct=1, asset_fee_pct=0.2, starting_balance=0)
    assert result.estimated_fee_drag > 0 and result.net_with_fees_balance < result.gross_no_fee_balance

def test_score_funds_returns_sorted_scores():
    scores = client().score_funds([module.normalize_row(row) for row in sample_rows()])
    assert scores[0].score >= scores[-1].score

def test_export_json_roundtrip(tmp_path):
    records = [module.normalize_row(row) for row in sample_rows()]
    p = tmp_path/"out.json"; client().export_json(records, p)
    loaded = client().load_json(p)
    assert len(loaded) == len(records) and loaded[0].fund_id == records[0].fund_id

def test_export_csv(tmp_path):
    p = tmp_path/"out.csv"; client().export_csv([module.normalize_row(row) for row in sample_rows()], p)
    text = p.read_text(encoding="utf-8-sig")
    assert "fund_id" in text and "12345" in text

def test_parse_ckan_payload_success():
    rows, total = client()._parse_ckan_payload({"success": True, "result": {"records": [{"fund_id":"1"}], "total": 1}})
    assert rows == [{"fund_id":"1"}] and total == 1

def test_parse_ckan_payload_failure():
    with pytest.raises(module.DataSourceError): client()._parse_ckan_payload({"success": False, "error": {"message": "bad"}})

def test_format_helpers():
    assert module.format_nis(2000) == "₪2,000"
    assert module.format_pct(0.2) == "0.20%"
    assert module.format_date_hebrew(dt.date(2025,12,31)) == "31/12/2025"

def test_async_load_csv(tmp_path):
    p = tmp_path/"data.csv"; p.write_text("fund_id,fund_name,report_date\n1,Fund,2025-12-31\n", encoding="utf-8")
    async def run():
        c = module.AsyncPensionFundTrackerClient()
        return await c.load_csv(p, encoding="utf-8")
    records = asyncio.run(run())
    assert records[0].fund_id == "1"
