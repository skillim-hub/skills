from __future__ import annotations
import asyncio
from decimal import Decimal
import whatsapp_invoice_processor as client

CLEAR = """
א.ב. שירותים בע"מ
ח.פ. 516123456
חשבונית מס/קבלה מס' 8841
תאריך 14/02/2026
סה"כ לפני מע"מ 99.00 ₪
מע"מ 18% 18.00 ₪
סה"כ לתשלום 117.00 ₪
מספר הקצאה 987654321
"""

def test_classifies_tax_invoice_receipt(): assert client.parse_invoice_text(CLEAR).document_type == "חשבונית מס/קבלה"
def test_clear_invoice_accepted(): assert client.parse_invoice_text(CLEAR).status == "accepted"
def test_vendor(): assert client.parse_invoice_text(CLEAR).vendor_name == 'א.ב. שירותים בע"מ'
def test_tax_id(): assert client.parse_invoice_text(CLEAR).vendor_tax_id == "516123456"
def test_invoice_number(): assert client.parse_invoice_text(CLEAR).invoice_number == "8841"
def test_date_iso(): assert client.parse_invoice_text(CLEAR).issue_date == "2026-02-14"
def test_date_he(): assert client.format_date_he("2026-02-14") == "14/02/2026"
def test_amounts(): 
    r=client.parse_invoice_text(CLEAR)
    assert (r.amount_before_vat, r.vat_amount, r.total_amount)==(Decimal("99.00"), Decimal("18.00"), Decimal("117.00"))
def test_allocation(): assert client.parse_invoice_text(CLEAR).allocation_number == "987654321"
def test_reply_he(): 
    r=client.parse_invoice_text(CLEAR)
    assert "₪117.00" in r.chat_reply_he and "14/02/2026" in r.chat_reply_he
def test_decimal_comma(): assert client.parse_invoice_text("דנה\nקבלה מס' 1\nתאריך 03-01-2026\nסך הכול 750,50 ₪").total_amount == Decimal("750.50")
def test_thousands(): assert client.parse_invoice_text("לוי בעמ\nחשבונית מס 4421\nתאריך 18/01/2026\nסה\"כ לפני מע\"מ 1200.00 ₪\nמע\"מ 216.00 ₪\nסה\"כ לתשלום 1,416.00 ₪").total_amount == Decimal("1416.00")
def test_receipt_no_vat():
    r=client.parse_invoice_text("דנה עיצוב פנים\nעוסק פטור 123456789\nקבלה מס' 51\nתאריך 03-01-2026\nסך הכול שולם 750.00 ₪")
    assert r.status=="accepted" and r.vat_amount is None and "לא זוהה מע״מ" in r.chat_reply_he
def test_vat_mismatch():
    r=client.parse_invoice_text("כהן ייעוץ\nע.מ. 012345678\nחשבונית מס 1007\nתאריך 05/02/2026\nלפני מע\"מ 100.00 ₪\nמע\"מ 12.00 ₪\nסה\"כ 112.00 ₪")
    assert r.status=="needs_review" and "vat_mismatch" in r.warnings
def test_pro_forma():
    r=client.parse_invoice_text("לוי אספקה\nחשבונית פרופורמה 9001\nתאריך 02/02/2026\nסה\"כ 1,200.00 ₪")
    assert r.status=="unsupported" and "unsupported_document_type" in r.warnings
def test_missing_total():
    r=client.parse_invoice_text("משרד הדר\nחשבונית מס 2026-9\nתאריך 10/02/2026\nמע\"מ 18%")
    assert r.status=="needs_review" and "missing_total_amount" in r.warnings
def test_missing_number():
    r=client.parse_invoice_text("משרד הדר\nחשבונית מס\nתאריך 10/02/2026\nסה\"כ לפני מע\"מ 100.00 ₪\nמע\"מ 18.00 ₪\nסה\"כ לתשלום 118.00 ₪")
    assert r.status=="needs_review" and "missing_invoice_number" in r.warnings
def test_empty(): 
    r=client.parse_invoice_text("")
    assert r.status=="unsupported" and "empty_text" in r.warnings
def test_unsupported_ext(tmp_path):
    p=tmp_path/"x.heic"; p.write_text(CLEAR, encoding="utf-8")
    r=client.InvoiceProcessor().parse_file(p)
    assert r.status=="unsupported" and "unsupported_media_type" in r.warnings
def test_async_parse():
    async def run(): return await client.InvoiceProcessor().parse_text_async(CLEAR)
    assert asyncio.run(run()).status == "accepted"
def test_parse_file(tmp_path):
    p=tmp_path/"x.txt"; p.write_text(CLEAR, encoding="utf-8")
    assert client.InvoiceProcessor().parse_file(p).invoice_number == "8841"
def test_duplicate_seen():
    p=client.InvoiceProcessor(); a=p.parse_text(CLEAR); b=p.parse_text(CLEAR)
    assert a.status=="accepted" and b.status=="duplicate"
def test_duplicate_known():
    a=client.parse_invoice_text(CLEAR)
    b=client.InvoiceProcessor().parse_text(CLEAR, known_duplicate_keys=[a.dedupe_key])
    assert b.status=="duplicate"
def test_dedupe_stable(): assert client.parse_invoice_text(CLEAR).dedupe_key == client.parse_invoice_text(CLEAR).dedupe_key
def test_to_dict(): assert isinstance(client.parse_invoice_text(CLEAR).to_dict()["total_amount"], float)
def test_json_hebrew(): assert "א.ב. שירותים" in client.parse_invoice_text(CLEAR).to_json()
def test_usd_review():
    r=client.parse_invoice_text("Global Vendor Ltd\nTax Invoice 88\nDate 14/02/2026\nTotal $100.00\nVAT $0.00")
    assert r.currency=="USD" and r.status=="needs_review" and "non_ils_currency" in r.warnings
def test_allocation_missing():
    cfg=client.ProcessingConfig(allocation_policy_enabled=True, allocation_threshold_before_vat=Decimal("50"))
    r=client.InvoiceProcessor(cfg).parse_text("א.ב. שירותים בעמ\nחשבונית מס 111\nתאריך 14/02/2026\nסה\"כ לפני מע\"מ 99.00 ₪\nמע\"מ 18.00 ₪\nסה\"כ לתשלום 117.00 ₪")
    assert r.status=="needs_review" and "allocation_number_missing" in r.warnings
def test_low_confidence(): assert client.parse_invoice_text(CLEAR, ocr_confidence=0.2).status=="needs_review"
def test_credit_classification(): assert client.parse_invoice_text("ספק בעמ\nחשבונית זיכוי מס' Z-10\nתאריך 01/02/2026\nסה\"כ לתשלום -118.00 ₪\nמע\"מ -18.00 ₪").document_type=="חשבונית זיכוי"
def test_vendor_key(): assert client.normalize_vendor_for_key('א.ב. שירותים בע"מ')=="אבשירותיםבעמ"
def test_rounding(): assert client.money(Decimal("17.825")) == Decimal("17.83")

def test_allocation_threshold_2026_january(): assert client.allocation_threshold_for_date("2026-01-15") == Decimal("10000")
def test_allocation_threshold_2026_june(): assert client.allocation_threshold_for_date("2026-06-03") == Decimal("5000")
def test_production_env_allocation_threshold(monkeypatch):
    monkeypatch.setenv("WHATSAPP_INVOICE_ALLOCATION_REQUIRED", "true")
    monkeypatch.setenv("WHATSAPP_INVOICE_TODAY", "2026-06-03")
    cfg = client.ProcessingConfig.from_env(env="production")
    assert cfg.allocation_threshold_before_vat == Decimal("5000")
