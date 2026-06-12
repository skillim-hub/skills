from __future__ import annotations

import asyncio
import csv
from decimal import Decimal
import json
from pathlib import Path

import bank_transaction_categorizer as btc


def make_csv(tmp_path: Path, rows: list[list[str]], name: str = "statement.csv") -> Path:
    path = tmp_path / name
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return path


def first_category(description: str, amount: str = "100", direction: str = "debit"):
    sign_amount = Decimal(amount)
    if direction == "debit":
        sign_amount = -abs(sign_amount)
    tx = btc.RawTransaction(date=btc.parse_israeli_date("01/01/2026"), description=description, amount=sign_amount)
    return btc.BankTransactionCategorizer().categorize(tx)


def test_parse_israeli_date_dash():
    assert btc.parse_israeli_date("31-01-2026").isoformat() == "2026-01-31"


def test_parse_israeli_date_slash():
    assert btc.parse_israeli_date("31/01/2026").isoformat() == "2026-01-31"


def test_parse_iso_date():
    assert btc.parse_israeli_date("2026-01-31").isoformat() == "2026-01-31"


def test_parse_amount_with_shekel_and_commas():
    assert btc.parse_israeli_amount("₪1,234.56") == Decimal("1234.56")


def test_parse_amount_european_decimal():
    assert btc.parse_israeli_amount("1.234,56") == Decimal("1234.56")


def test_parse_amount_comma_decimal():
    assert btc.parse_israeli_amount("123,45") == Decimal("123.45")


def test_parse_amount_parentheses_negative():
    assert btc.parse_israeli_amount("(120.00)") == Decimal("-120.00")


def test_detect_bank_hapoalim():
    assert btc.detect_bank("בנק הפועלים חשבון עסקי") == "Bank Hapoalim"


def test_detect_bank_leumi():
    assert btc.detect_bank("Leumi export") == "Bank Leumi"


def test_parse_csv_debit_credit_columns(tmp_path):
    path = make_csv(tmp_path, [["תאריך", "תיאור", "חובה", "זכות"], ["02/01/2026", 'מע"מ תקופתי', "1200", ""]])
    rows = btc.BankTransactionCategorizer().parse_csv(path)
    assert rows[0].amount == Decimal("-1200")


def test_parse_csv_credit_column(tmp_path):
    path = make_csv(tmp_path, [["תאריך", "תיאור", "חובה", "זכות"], ["03/01/2026", "העברה מלקוח חשבונית", "", "3500"]])
    rows = btc.BankTransactionCategorizer().parse_csv(path)
    assert rows[0].amount == Decimal("3500")


def test_vat_category():
    item = first_category('מע"מ תקופתי')
    assert item.category == "Taxes & Government"
    assert item.subcategory == "VAT"


def test_income_tax_category():
    assert first_category("מקדמות מס הכנסה").subcategory == "Income tax"


def test_national_insurance_priority_over_insurance():
    item = first_category("ביטוח לאומי")
    assert item.category == "Taxes & Government"


def test_municipal_tax_category():
    assert first_category("ארנונה עיריית תל אביב").subcategory == "Municipal tax"


def test_bank_fee_category():
    assert first_category("עמלת מסלול עסקים").category == "Bank Fees & Interest"


def test_card_settlement_debit_category():
    assert first_category("ישראכרט 02/2026").category == "Credit Card Settlement"


def test_card_settlement_credit_income():
    item = first_category("זיכוי ישראכרט סליקה", direction="credit")
    assert item.category == "Income"


def test_client_transfer_income():
    item = first_category("העברה מלקוח חשבונית 1042", direction="credit")
    assert item.category == "Income"


def test_software_category():
    assert first_category("ADOBE CREATIVE CLOUD").category == "Software & Cloud"


def test_marketing_category():
    assert first_category("Google Ads").category == "Marketing & Advertising"


def test_communications_category():
    item = first_category("סלקום עסקים")
    assert item.category == "Communications"
    assert item.tax_deductibility == "partial"


def test_fuel_category():
    assert first_category("פז תחנת דלק").category == "Travel & Fuel"


def test_food_category():
    assert first_category("WOLT").category == "Food & Meals"


def test_groceries_personal_review():
    item = first_category("שופרסל דיל")
    assert item.category == "Personal/Review"
    assert "needs-review" in item.flags


def test_rent_category():
    assert first_category("דמי שכירות משרד").category == "Rent & Facilities"


def test_professional_services_category():
    assert first_category("רואה חשבון כהן").category == "Professional Services"


def test_equipment_category():
    assert first_category("KSP מחשב נייד").category == "Equipment & Office"


def test_cash_withdrawal_category():
    assert first_category("משיכת מזומן כספומט").category == "Cash Withdrawals"


def test_wallet_credit_flagged():
    item = first_category("BIT העברה", direction="credit")
    assert "confirm-business-income" in item.flags


def test_fallback_uncategorized():
    item = first_category("ספק לא מוכר 123")
    assert item.category == "Uncategorized Expense"
    assert "needs-review" in item.flags


def test_duplicate_detection_adds_flag():
    cat = btc.BankTransactionCategorizer()
    tx = btc.RawTransaction(date=btc.parse_israeli_date("01/01/2026"), description="ADOBE", amount=Decimal("-88"))
    rows = cat.categorize_transactions([tx, tx])
    assert "possible-duplicate" in rows[1].flags


def test_export_json(tmp_path):
    out = tmp_path / "out.json"
    item = first_category("ADOBE")
    btc.export_transactions([item], out, "json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data[0]["category"] == "Software & Cloud"


def test_export_csv(tmp_path):
    out = tmp_path / "out.csv"
    item = first_category("ADOBE")
    btc.export_transactions([item], out, "csv")
    assert "Software & Cloud" in out.read_text(encoding="utf-8-sig")


def test_custom_rule_wins(tmp_path):
    rules = [
        {
            "id": "custom_supplier",
            "category": "Custom Category",
            "subcategory": "Custom Sub",
            "patterns": ["ספק מיוחד"],
            "direction": "debit",
            "vat_relevant": True,
            "tax_deductibility": "likely",
            "confidence": 0.99,
            "priority": 999
        }
    ]
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(rules, ensure_ascii=False), encoding="utf-8")
    cat = btc.BankTransactionCategorizer.from_rule_file(path)
    tx = btc.RawTransaction(date=btc.parse_israeli_date("01/01/2026"), description="ספק מיוחד", amount=Decimal("-100"))
    assert cat.categorize(tx).category == "Custom Category"


def test_categorize_file_summary(tmp_path):
    path = make_csv(tmp_path, [["תאריך", "תיאור", "חובה", "זכות"], ["02/01/2026", "ADOBE", "88", ""], ["03/01/2026", "העברה מלקוח חשבונית", "", "3500"]])
    result = btc.BankTransactionCategorizer().categorize_file(path)
    assert result["count"] == 2
    assert result["summary"]["total_credit"] == "3500.00"


def test_async_categorize_file(tmp_path):
    path = make_csv(tmp_path, [["תאריך", "תיאור", "חובה", "זכות"], ["02/01/2026", "ADOBE", "88", ""]])
    result = asyncio.run(btc.BankTransactionCategorizer().acategorize_file(path))
    assert result["count"] == 1


def test_validate_file(tmp_path):
    path = make_csv(tmp_path, [["תאריך", "תיאור", "חובה", "זכות"], ["02/01/2026", "ADOBE", "88", ""]])
    result = btc.validate_file(path)
    assert result["valid"] is True
    assert result["count"] == 1


def test_missing_amount_raises(tmp_path):
    path = make_csv(tmp_path, [["תאריך", "תיאור"], ["02/01/2026", "ADOBE"]])
    try:
        btc.BankTransactionCategorizer().parse_csv(path)
    except btc.TransactionCategorizerError as exc:
        assert "missing-amount" in str(exc)
    else:
        raise AssertionError("expected parsing error")


def test_make_sample_csv(tmp_path):
    path = btc.make_sample_csv(tmp_path / "sample.csv")
    assert path.exists()
    assert "מע" in path.read_text(encoding="utf-8-sig")


def test_register_and_resolve_input_id(tmp_path):
    path = btc.make_sample_csv(tmp_path / "sample.csv")
    response = btc.register_input(path, environment="sandbox", base_dir=tmp_path / "state")
    assert response["id"].startswith("stmt_")
    resolved = btc.resolve_input_id(response["id"], environment="sandbox", base_dir=tmp_path / "state")
    assert resolved == path.resolve()


def test_create_sample_statement_returns_id(tmp_path):
    response = btc.create_sample_statement(tmp_path / "created.csv", environment="sandbox", base_dir=tmp_path / "state")
    assert response["id"].startswith("stmt_")
    assert Path(response["path"]).exists()


def test_import_package_public_api():
    assert btc.BankTransactionCategorizer is not None
    assert callable(btc.parse_israeli_amount)
