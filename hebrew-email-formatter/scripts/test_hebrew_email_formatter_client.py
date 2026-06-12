from __future__ import annotations

import asyncio
import json

import pytest

from hebrew_email_formatter import (
    AsyncHebrewEmailFormatterClient,
    Contact,
    DraftStore,
    Formality,
    Gender,
    HebrewEmailError,
    HebrewEmailFormatterClient,
    Sender,
    SignatureStyle,
    build_signature,
    choose_greeting,
    format_date_il,
    format_ils,
    parse_environment,
    request_confirmation_phrase,
    vat_breakdown,
)


def test_format_ils_integer():
    assert format_ils("1234") == "1,234 ₪"


def test_format_ils_rounds_half_up():
    assert format_ils("1234.50") == "1,235 ₪"


def test_format_ils_agorot():
    assert format_ils("1234.5", include_agorot=True) == "1,234.50 ₪"


def test_vat_breakdown():
    result = vat_breakdown("1000")
    assert result["vat"] == "180 ₪"
    assert result["gross"] == "1,180 ₪"


def test_format_date_from_iso():
    assert format_date_il("2026-06-03") == "03/06/2026"


def test_format_date_from_dash():
    assert format_date_il("03-06-2026") == "03/06/2026"


def test_invalid_date_raises():
    with pytest.raises(HebrewEmailError):
        format_date_il("June 3")


def test_environment_validation():
    assert parse_environment("production") == "production"
    with pytest.raises(HebrewEmailError):
        parse_environment("dev")


def test_choose_warm_greeting():
    assert choose_greeting(Contact(name="דנה", gender=Gender.FEMALE), Formality.WARM) == "היי דנה,"


def test_choose_formal_company_greeting():
    assert choose_greeting(Contact(name="מחלקת שירות לקוחות", is_company=True), Formality.FORMAL) == "לכבוד מחלקת שירות לקוחות,"


def test_neutral_confirmation_phrase():
    assert request_confirmation_phrase(Gender.NEUTRAL) == "אשמח לקבל אישור"


def test_female_confirmation_phrase():
    assert request_confirmation_phrase(Gender.FEMALE) == "אשמח אם תוכלי לאשר"


def test_signature_business_contains_details():
    signature = build_signature(
        Sender(name="יואב לוי", business_name="יואב לוי סטודיו", phone="050-1234567"),
        "תודה,",
        SignatureStyle.BUSINESS,
    )
    assert "יואב לוי סטודיו" in signature
    assert "050-1234567" in signature


def test_payment_reminder_contains_invoice_amount_due_date():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "payment_reminder",
        "recipient": {"name": "דנה", "gender": "female"},
        "sender": {"name": "יואב לוי", "gender": "male"},
        "facts": {
            "invoice_number": "2026-041",
            "invoice_date": "2026-05-01",
            "due_date": "2026-05-31",
            "amount": "3500",
            "payment_terms": "שוטף + 30",
        },
    })
    assert draft.subject == "תזכורת לתשלום חשבונית 2026-041"
    assert "3,500 ₪" in draft.body
    assert "31/05/2026" in draft.body
    assert draft.id.startswith("hef_")


def test_firm_payment_reminder_mentions_previous_date():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "payment_reminder",
        "formality": "firm",
        "recipient": {"name": "חברת אלון", "is_company": True},
        "sender": {"name": "נועה", "gender": "female"},
        "facts": {
            "invoice_number": "9",
            "amount": "1200",
            "due_date": "01/05/2026",
            "previous_reminder_date": "20/05/2026",
            "requested_action_date": "06/06/2026",
        },
    })
    assert "בהמשך לתזכורת מיום 20/05/2026" in draft.body
    assert "נא לעדכן עד 06/06/2026" in draft.body


def test_missing_due_date_warning():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "payment_reminder",
        "recipient": {"name": "דנה", "gender": "female"},
        "sender": {"name": "יואב"},
        "facts": {"invoice_number": "1", "amount": "100"},
    })
    assert any("HEF007_INVOICE_MISSING_DUE_DATE" in warning for warning in draft.warnings)


def test_quote_includes_vat_warning_when_missing():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "quote",
        "recipient": {"name": "רכש", "is_company": True},
        "sender": {"name": "נועה", "gender": "female"},
        "facts": {"service": "עיצוב עמוד נחיתה", "amount": "4800", "valid_until": "20/06/2026"},
    })
    assert "4,800 ₪" in draft.body
    assert any("HEF006_VAT_STATUS_UNKNOWN" in warning for warning in draft.warnings)


def test_quote_uses_scope_bullets():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "quote",
        "recipient": {"name": "דנה"},
        "sender": {"name": "יואב"},
        "facts": {
            "service": "ייעוץ",
            "amount": "1000",
            "vat_status": "בתוספת מע\"מ כדין",
            "scope": ["פגישת אפיון", "סיכום כתוב"],
        },
    })
    assert "- פגישת אפיון" in draft.body
    assert "- סיכום כתוב" in draft.body


def test_invoice_sent_attachment_confirmed():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "invoice_sent",
        "recipient": {"name": "רועי"},
        "sender": {"name": "יואב"},
        "facts": {
            "invoice_number": "17",
            "document_type": "חשבונית מס/קבלה",
            "service": "ייעוץ",
            "amount": "2900",
            "due_date": "10/06/2026",
            "attachment_confirmed": True,
        },
    })
    assert "מצורפת חשבונית מס/קבלה 17" in draft.body


def test_invoice_sent_no_attachment_claim_when_not_confirmed():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "invoice_sent",
        "recipient": {"name": "רועי"},
        "sender": {"name": "יואב"},
        "facts": {"invoice_number": "17", "service": "ייעוץ"},
    })
    assert "מצורפת" not in draft.body


def test_meeting_request_lists_slots():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "meeting_request",
        "recipient": {"name": "דנה", "gender": "female"},
        "sender": {"name": "יואב"},
        "facts": {"topic": "הפרויקט", "slots": ["יום א, 07/06/2026, 10:00", "יום ב, 08/06/2026, 12:00"]},
    })
    assert "- יום א, 07/06/2026, 10:00" in draft.body


def test_consumer_complaint_subject_and_resolution():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "consumer_complaint",
        "recipient": {"name": "שירות לקוחות", "is_company": True},
        "sender": {"name": "רונית", "gender": "female"},
        "facts": {
            "product": "מכונת קפה",
            "order_number": "A123",
            "purchase_date": "15/05/2026",
            "amount": "899",
            "problem": "המוצר הגיע תקול",
            "requested_resolution": "החלפה או החזר",
            "requested_action_date": "10/06/2026",
        },
    })
    assert draft.subject == "פנייה בנושא מכונת קפה – A123"
    assert "החלפה או החזר" in draft.body


def test_complaint_response_has_written_update_date():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "complaint_response",
        "recipient": {"name": "מאיה", "gender": "female"},
        "sender": {"name": "יואב"},
        "facts": {"topic": "איחור במשלוח", "requested_action_date": "12/06/2026"},
    })
    assert "נעדכן בכתב עד 12/06/2026" in draft.body


def test_apology_delay_male_sender():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "apology_delay",
        "recipient": {"name": "מאיה", "gender": "female"},
        "sender": {"name": "יואב", "gender": "male"},
        "facts": {"topic": "הקובץ", "new_delivery_date": "12/06/2026"},
    })
    assert "מתנצל על העיכוב" in draft.body


def test_apology_delay_female_sender():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "apology_delay",
        "recipient": {"name": "יואב", "gender": "male"},
        "sender": {"name": "נועה", "gender": "female"},
        "facts": {"topic": "הקובץ", "new_delivery_date": "12/06/2026"},
    })
    assert "מתנצלת על העיכוב" in draft.body


def test_cancellation_requests_written_confirmation():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "cancellation",
        "recipient": {"name": "שירות לקוחות", "is_company": True},
        "sender": {"name": "רונית"},
        "facts": {"service": "המנוי", "order_number": "7788", "cancellation_date": "30/06/2026"},
    })
    assert "אישור ביטול בכתב" in draft.body


def test_status_update_sections():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "status_update",
        "recipient": {"name": "אלון", "gender": "male"},
        "sender": {"name": "יואב"},
        "facts": {
            "project": "אתר",
            "completed": ["אפיון"],
            "next": ["עיצוב"],
            "attention": ["אישור טקסטים"],
        },
    })
    assert "הושלם:" in draft.body
    assert "בתכנון:" in draft.body
    assert "נקודות לתשומת לב:" in draft.body


def test_sensitive_data_warning():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "follow_up",
        "recipient": {"name": "מוקד"},
        "sender": {"name": "רונית"},
        "facts": {"topic": "פנייה", "sensitive_personal_data": True},
    })
    assert any("HEF010_PRIVACY_MINIMIZATION" in warning for warning in draft.warnings)


def test_marketing_content_warning():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "invoice_sent",
        "recipient": {"name": "לקוח"},
        "sender": {"name": "יואב"},
        "facts": {"marketing_content": True},
    })
    assert any("HEF011_MARKETING_CONSENT" in warning for warning in draft.warnings)


def test_draft_to_json_contains_id_and_subject():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "follow_up",
        "recipient": {"name": "דנה"},
        "sender": {"name": "יואב"},
        "facts": {"topic": "בדיקה"},
    })
    data = json.loads(draft.to_json())
    assert data["id"].startswith("hef_")
    assert data["subject"] == "מעקב בנושא בדיקה"


@pytest.mark.asyncio
async def test_async_client_matches_sync_subject():
    request = {
        "purpose": "meeting_request",
        "recipient": {"name": "דנה"},
        "sender": {"name": "יואב"},
        "facts": {"topic": "בדיקה"},
    }
    sync_draft = HebrewEmailFormatterClient().compose(request)
    async_draft = await AsyncHebrewEmailFormatterClient().compose(request)
    assert async_draft.subject == sync_draft.subject


def test_draft_store_save_load(tmp_path):
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "follow_up",
        "recipient": {"name": "דנה"},
        "sender": {"name": "יואב"},
        "facts": {"topic": "בדיקה"},
    })
    store = DraftStore(tmp_path)
    draft_id = store.save(draft)
    loaded = store.load(draft_id)
    assert loaded.subject == draft.subject
    assert draft_id in store.list_ids()


def test_render_includes_warnings():
    draft = HebrewEmailFormatterClient().compose({
        "purpose": "payment_reminder",
        "recipient": {"name": "דנה"},
        "sender": {"name": "יואב"},
        "facts": {"amount": "100"},
    })
    assert "הערות בדיקה:" in draft.render()


def test_package_import_exposes_client():
    module = __import__("hebrew_email_formatter")
    assert hasattr(module, "HebrewEmailFormatterClient")


def test_invoice_threshold_constant():
    import hebrew_email_formatter
    assert str(hebrew_email_formatter.ISRAEL_INVOICE_ALLOCATION_THRESHOLD_ILS) == "5000"
