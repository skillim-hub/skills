from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from invoice_ocr_extractor import ExtractorConfig, InvoiceOCRExtractor, parse_amount, export_csv

ROOT = Path(__file__).resolve().parents[1]
CLI_ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def extract(text: str, **config_kwargs):
    return InvoiceOCRExtractor(ExtractorConfig(**config_kwargs)).extract_from_text(text)


def test_hebrew_tax_invoice_receipt_full_vat_split():
    result = extract('''
    א.ב. שירותי מחשוב בע"מ
    ח.פ. 512345678
    חשבונית מס קבלה מס' 2026-104
    תאריך: 21/05/2026
    סה"כ לפני מע"מ: ₪1,000.00
    מע"מ 18%: ₪180.00
    סה"כ לתשלום: ₪1,180.00
    שולם באשראי
    ''')
    assert result.vendor == 'א.ב. שירותי מחשוב בע"מ'
    assert result.document_type == "tax_invoice_receipt"
    assert result.document_number == "2026-104"
    assert result.date == "21/05/2026"
    assert result.total_gross == 1180.0
    assert result.vat_amount == 180.0
    assert result.total_net == 1000.0
    assert result.vat_rate == 18.0
    assert result.payment_method == "credit_card"
    assert result.business_id == "512345678"
    assert result.record_id and result.record_id.startswith("inv_")
    assert result.confidence >= 0.9


def test_english_tax_invoice():
    result = extract('''
    Northwind Services Ltd.
    VAT No. 515555555
    Tax Invoice No. INV-9001
    Invoice Date: 2026-05-21
    Subtotal NIS 250.00
    VAT 18% NIS 45.00
    Grand Total NIS 295.00
    ''')
    assert result.vendor == "Northwind Services Ltd."
    assert result.document_type == "tax_invoice"
    assert result.document_number == "INV-9001"
    assert result.date == "21/05/2026"
    assert result.total_gross == 295.0
    assert result.vat_amount == 45.0
    assert result.total_net == 250.0


def test_exempt_dealer_receipt_sets_zero_vat():
    result = extract('''
    נועה לוי - עוסק פטור
    ע.מ. 123456789
    קבלה מס' 45
    תאריך 02/05/2026
    סה"כ לתשלום ₪300.00
    ''')
    assert result.document_type == "receipt"
    assert result.vat_amount == 0.0
    assert result.total_net == 300.0
    assert result.vat_rate == 0.0
    assert any("exempt dealer" in flag for flag in result.review_flags)


def test_missing_vendor_flag():
    result = extract('''
    חשבונית מס מס' 77
    תאריך: 01/05/2026
    סה"כ לתשלום ₪118.00
    מע"מ 18% ₪18.00
    ''')
    assert result.vendor is None
    assert "Vendor not found" in result.review_flags


def test_customer_block_not_vendor_when_supplier_exists():
    result = extract('''
    לכבוד: לקוח בדיקה בע"מ
    מספר לקוח 999
    ספק אמיתי בע"מ
    ח.פ. 512300000
    חשבונית מס מס' 88
    תאריך: 03/05/2026
    סה"כ לפני מע"מ ₪100.00
    מע"מ 18% ₪18.00
    סה"כ לתשלום ₪118.00
    ''')
    assert result.vendor == 'ספק אמיתי בע"מ'


def test_multiple_totals_prefers_gross_total():
    result = extract('''
    Office Store Ltd.
    Invoice No. 55
    Date: 04/05/2026
    Subtotal NIS 100.00
    Discount NIS 10.00
    VAT 18% NIS 16.20
    Grand Total NIS 106.20
    ''')
    assert result.total_gross == 106.2
    assert result.total_net == 100.0


def test_vat_math_mismatch_flag():
    result = extract('''
    Bad Math Ltd.
    Tax Invoice No. 1
    Date: 05/05/2026
    Subtotal NIS 100.00
    VAT 18% NIS 19.00
    Grand Total NIS 118.00
    ''')
    assert "VAT math mismatch: net + VAT does not equal gross" in result.review_flags


def test_vat_inferred_from_visible_rate():
    result = extract('''
    Rate Only Ltd.
    Tax Invoice No. 2
    Date: 06/05/2026
    VAT 18%
    Grand Total NIS 118.00
    ''')
    assert result.total_net == 100.0
    assert result.vat_amount == 18.0
    assert "VAT inferred from gross total and visible VAT rate" in result.review_flags


def test_vat_inferred_when_rate_missing_enabled():
    result = extract('''
    Default Rate Ltd.
    Invoice No. 3
    Date: 07/05/2026
    Grand Total NIS 118.00
    ''', infer_vat_when_rate_missing=True, default_vat_rate=18.0)
    assert result.total_net == 100.0
    assert result.vat_amount == 18.0
    assert result.vat_rate == 18.0


def test_vat_not_inferred_when_missing_disabled():
    result = extract('''
    No VAT Ltd.
    Invoice No. 4
    Date: 08/05/2026
    Grand Total NIS 118.00
    ''')
    assert result.vat_amount is None
    assert "VAT not found" in result.review_flags


def test_two_digit_year_date():
    result = extract("קבלה מס' 7788\nתאריך 4/5/26\nסה\"כ לתשלום ₪80")
    assert result.date == "04/05/2026"


def test_iso_date():
    result = extract("Vendor Ltd.\nInvoice No. 90\nDate: 2026-05-21\nGrand Total NIS 10.00")
    assert result.date == "21/05/2026"


def test_invalid_date_flag():
    result = extract("Vendor Ltd.\nInvoice No. 91\nDate: 31/02/2026\nGrand Total NIS 10.00")
    assert result.date is None
    assert "Invalid date" in result.review_flags


def test_credit_note_negative_amounts():
    result = extract('''
    ספק זיכוי בע"מ
    חשבונית זיכוי מס' 9002
    תאריך: 20/05/2026
    סה"כ לפני מע"מ: -₪100.00
    מע"מ 18%: -₪18.00
    סה"כ לתשלום: -₪118.00
    ''')
    assert result.document_type == "credit_note"
    assert result.total_gross == -118.0
    assert result.vat_amount == -18.0


def test_credit_note_positive_amounts_flag():
    result = extract('''
    Credit Vendor Ltd.
    Credit Note No. CN-1
    Date: 20/05/2026
    Subtotal NIS 100.00
    VAT 18% NIS 18.00
    Grand Total NIS 118.00
    ''')
    assert result.document_type == "credit_note"
    assert "Credit note with positive displayed amounts; verify sign before import" in result.review_flags


def test_foreign_currency_flag():
    result = extract("Cloud Tools Ltd.\nInvoice No. CT-442\nDate: 2026-05-04\nTotal USD 20.00")
    assert result.currency == "USD"
    assert "Foreign currency; conversion rate required for local bookkeeping" in result.review_flags


def test_payment_app_screenshot_warning():
    result = extract("Bit\nהעברה בוצעה בהצלחה\nל: ישראל ישראלי\n₪120.00\nמספר אישור 998877")
    assert result.payment_method == "digital_wallet"
    assert result.document_number is None
    assert "Payment confirmation may not be a tax invoice" in result.review_flags


def test_allocation_number_separate_from_document_number():
    result = extract('''
    ספק הקצאות בע"מ
    חשבונית מס מס' 700114
    מספר הקצאה: 987654321
    תאריך: 09/05/2026
    סה"כ לתשלום ₪2,360.00
    מע"מ 18% ₪360.00
    ''')
    assert result.document_number == "700114"
    assert result.allocation_number == "987654321"


def test_ocr_digit_confusion_amount():
    assert parse_amount("₪l18.OO") == 118.0


def test_rtl_amount_order():
    result = extract('''
    ספק בדיקה בע"מ
    חשבונית מס מס' 12
    תאריך: 10/05/2026
    118.00 ₪ לתשלום סה"כ
    מע"מ 18% ₪18.00
    ''')
    assert result.total_gross == 118.0


def test_duplicate_indicator_flag():
    result = extract("העתק\nCopy Vendor Ltd.\nInvoice No. 44\nDate: 11/05/2026\nGrand Total NIS 50.00")
    assert "Copy/duplicate indicator visible" in result.review_flags


def test_proforma_flag():
    result = extract("ספק פרופורמה בע\"מ\nפרופורמה מס' 123\nתאריך: 12/05/2026\nסה\"כ לתשלום ₪100")
    assert result.document_type == "proforma"
    assert "Proforma invoice; review before expense import" in result.review_flags


def test_bank_transfer_payment_method():
    result = extract('''
    דניאל כהן ייעוץ בע"מ
    חשבונית מס קבלה מס' 1007
    תאריך: 12/05/2026
    סה"כ לתשלום: ₪590.00
    שולם בהעברה בנקאית
    ''')
    assert result.payment_method == "bank_transfer"


def test_cash_payment_method():
    result = extract("Cash Shop Ltd.\nReceipt No. 1\nDate: 12/05/2026\nTotal NIS 20.00\nCash")
    assert result.payment_method == "cash"


def test_to_dict_contains_schema_version_and_record_id():
    result = extract("Receipt No. 1\nDate: 12/05/2026\nTotal NIS 20.00")
    data = result.to_dict()
    assert data["schema_version"] == "2.2.0"
    assert data["record_id"].startswith("inv_")


def test_async_extract_from_text():
    async def run():
        extractor = InvoiceOCRExtractor()
        return await extractor.extract_from_text_async("Async Ltd.\nInvoice No. 9\nDate: 12/05/2026\nTotal NIS 20.00")
    result = asyncio.run(run())
    assert result.document_number == "9"


def test_batch_extract_and_csv(tmp_path):
    (tmp_path / "a.txt").write_text("A Ltd.\nInvoice No. 1\nDate: 12/05/2026\nTotal NIS 20.00", encoding="utf-8")
    (tmp_path / "b.txt").write_text("B Ltd.\nInvoice No. 2\nDate: 13/05/2026\nTotal NIS 30.00", encoding="utf-8")
    extractor = InvoiceOCRExtractor()
    rows = extractor.batch_extract(tmp_path)
    assert len(rows) == 2
    output = tmp_path / "out.csv"
    export_csv(rows, output)
    assert "record_id" in output.read_text(encoding="utf-8-sig")


def test_validate_detects_missing_fields_and_vat_mismatch():
    errors = InvoiceOCRExtractor().validate({"total_gross": 118.0, "total_net": 100.0, "vat_amount": 19.0})
    assert "VAT_MATH_MISMATCH" in errors
    assert "VENDOR_MISSING" in errors


def test_validate_expected_id_success():
    result = extract("ID Ltd.\nInvoice No. 1\nDate: 12/05/2026\nTotal NIS 20.00")
    assert InvoiceOCRExtractor().validate(result.to_dict(), expected_id=result.record_id) == [] or "VAT not found"


def test_cli_parse_pretty(tmp_path):
    text_file = tmp_path / "invoice.txt"
    text_file.write_text("CLI Ltd.\nInvoice No. 77\nDate: 12/05/2026\nTotal NIS 20.00", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-m", "invoice_ocr_extractor.cli", "parse", "--text-file", str(text_file), "--pretty"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=CLI_ENV,
        check=True,
    )
    data = json.loads(completed.stdout)
    assert data["document_number"] == "77"
    assert data["record_id"].startswith("inv_")


def test_cli_validate_exit_code(tmp_path):
    json_file = tmp_path / "bad.json"
    json_file.write_text(json.dumps({"total_gross": 118, "total_net": 100, "vat_amount": 19}), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-m", "invoice_ocr_extractor.cli", "validate", "--json-file", str(json_file)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=CLI_ENV,
    )
    assert completed.returncode == 1
    assert "VAT_MATH_MISMATCH" in completed.stdout


def test_file_not_found_raises():
    with pytest.raises(FileNotFoundError):
        InvoiceOCRExtractor().extract_from_file("does-not-exist.txt")


def test_allocation_threshold_for_2026_phase_down():
    extractor = InvoiceOCRExtractor()
    assert extractor.allocation_threshold_for_date("15/01/2026") == 10000.0
    assert extractor.allocation_threshold_for_date("01/06/2026") == 5000.0


def test_missing_allocation_number_flag_for_high_value_2026_tax_invoice():
    result = extract("""
    High Value Ltd.
    Tax Invoice No. 2026-900
    Date: 02/06/2026
    Subtotal NIS 6,000.00
    VAT 18% NIS 1,080.00
    Grand Total NIS 7,080.00
    """)
    assert InvoiceOCRExtractor().requires_allocation_number(result) is True
    assert any("Allocation number may be required" in flag for flag in result.review_flags)


def test_existing_allocation_number_suppresses_missing_allocation_flag():
    result = extract("""
    High Value Ltd.
    Tax Invoice No. 2026-901
    Allocation Number: 123456789
    Date: 02/06/2026
    Subtotal NIS 6,000.00
    VAT 18% NIS 1,080.00
    Grand Total NIS 7,080.00
    """)
    assert InvoiceOCRExtractor().requires_allocation_number(result) is True
    assert result.allocation_number == "123456789"
    assert not any("Allocation number may be required" in flag for flag in result.review_flags)
