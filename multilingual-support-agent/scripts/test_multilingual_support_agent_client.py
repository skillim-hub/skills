from __future__ import annotations

import pytest

from multilingual_support_agent import Environment, Language, Risk, SupportAgentClient, SupportContext, format_analysis


def test_detect_hebrew() -> None:
    assert SupportAgentClient().detect_language("שלום, איפה ההזמנה?") == Language.HE


def test_detect_arabic() -> None:
    assert SupportAgentClient().detect_language("مرحبا، أين الطلب؟") == Language.AR


def test_detect_russian() -> None:
    assert SupportAgentClient().detect_language("Здравствуйте, где заказ?") == Language.RU


def test_detect_english() -> None:
    assert SupportAgentClient().detect_language("Hello, where is the order?") == Language.EN


def test_detect_unknown() -> None:
    assert SupportAgentClient().detect_language("12345") == Language.UNKNOWN


def test_classify_delivery_hebrew() -> None:
    assert SupportAgentClient().classify_intent("איפה המשלוח שלי") == "delivery_status"


def test_classify_refund_english() -> None:
    assert SupportAgentClient().classify_intent("I want a refund") == "refund_request"


def test_classify_invoice_russian() -> None:
    assert SupportAgentClient().classify_intent("Мне нужен чек") == "invoice_request"


def test_classify_payment_arabic() -> None:
    assert SupportAgentClient().classify_intent("تم الخصم من البطاقة مرتين") == "payment_issue"


def test_classify_appointment_hebrew() -> None:
    assert SupportAgentClient().classify_intent("צריך להזיז תור") == "appointment"


def test_classify_privacy() -> None:
    assert SupportAgentClient().classify_intent("Delete data") == "privacy_request"


def test_classify_complaint_russian() -> None:
    assert SupportAgentClient().classify_intent("Это жалоба на плохой сервис") == "complaint"


def test_classify_general_support() -> None:
    assert SupportAgentClient().classify_intent("Good morning") == "general_support"


def test_high_risk_lawyer() -> None:
    assert SupportAgentClient().assess_risk("I will call my lawyer") == Risk.HIGH


def test_high_risk_privacy_hebrew() -> None:
    assert SupportAgentClient().assess_risk("מחקו את המידע האישי שלי", "privacy_request") == Risk.HIGH


def test_medium_risk_broken_item() -> None:
    assert SupportAgentClient().assess_risk("The item arrived broken") == Risk.MEDIUM


def test_medium_risk_payment_intent() -> None:
    assert SupportAgentClient().assess_risk("card issue", "payment_issue") == Risk.MEDIUM


def test_low_risk_general() -> None:
    assert SupportAgentClient().assess_risk("What are your opening hours?") == Risk.LOW


def test_required_fields_delivery() -> None:
    assert SupportAgentClient().required_fields("delivery_status") == ["order_id"]


def test_missing_order_id() -> None:
    result = SupportAgentClient().draft_reply("המשלוח מאחר")
    assert "order_id" in result.missing_fields


def test_no_missing_order_id_when_present() -> None:
    result = SupportAgentClient().draft_reply("המשלוח מאחר", SupportContext(order_id="IL-1"))
    assert "order_id" not in result.missing_fields


def test_reply_language_hebrew() -> None:
    result = SupportAgentClient().draft_reply("אני רוצה החזר", SupportContext(order_id="IL-1"))
    assert result.language == Language.HE
    assert "בקשת ההחזר" in result.reply


def test_reply_language_arabic() -> None:
    result = SupportAgentClient().draft_reply("أريد استرداد المبلغ")
    assert result.language == Language.AR
    assert "طلب الاسترداد" in result.reply


def test_reply_language_russian() -> None:
    result = SupportAgentClient().draft_reply("Я не получил чек", SupportContext(order_id="IL-1", email="a@example.com"))
    assert result.language == Language.RU
    assert "бухгалтерского документа" in result.reply


def test_reply_force_language() -> None:
    result = SupportAgentClient().draft_reply("שלום", force_language="en")
    assert result.language == Language.EN
    assert result.reply.startswith("Hello")


def test_escalation_for_high_risk() -> None:
    result = SupportAgentClient().draft_reply("I will file a lawsuit")
    assert result.risk == Risk.HIGH
    assert result.escalation is not None


def test_no_escalation_for_low_risk() -> None:
    result = SupportAgentClient().draft_reply("What time do you open?")
    assert result.risk == Risk.LOW
    assert result.escalation is None


def test_format_currency_integer() -> None:
    assert SupportAgentClient().format_currency(120) == "₪120"


def test_format_currency_decimal() -> None:
    assert SupportAgentClient().format_currency(120.5) == "₪120.50"


def test_format_date_dd_mm_yyyy() -> None:
    assert SupportAgentClient().format_date("2026-06-05") == "05/06/2026"


def test_create_case_contains_case_id() -> None:
    response = SupportAgentClient(environment=Environment.SANDBOX).create_case("I need help")
    assert response["case_id"].startswith("msa_")
    assert response["environment"] == "sandbox"


def test_add_message_requires_case_id() -> None:
    with pytest.raises(ValueError):
        SupportAgentClient().add_message("", "hello")


def test_add_message_keeps_case_id() -> None:
    response = SupportAgentClient().add_message("msa_existing", "I want a refund")
    assert response["case_id"] == "msa_existing"


@pytest.mark.asyncio
async def test_async_draft_reply() -> None:
    result = await SupportAgentClient().draft_reply_async("המשלוח מאחר")
    assert result.intent == "delivery_status"


@pytest.mark.asyncio
async def test_async_create_case() -> None:
    response = await SupportAgentClient().create_case_async("Delete all my personal data")
    assert response["analysis"]["risk"] == "high"


@pytest.mark.asyncio
async def test_async_add_message() -> None:
    response = await SupportAgentClient().add_message_async("msa_123", "Я не получил чек")
    assert response["case_id"] == "msa_123"
    assert response["analysis"]["language"] == "ru"


def test_format_analysis_mapping() -> None:
    assert format_analysis({"ok": True}) == {"ok": True}


def test_format_analysis_dataclass() -> None:
    result = SupportAgentClient().draft_reply("Hello")
    formatted = format_analysis(result)
    assert formatted["case_id"].startswith("msa_")
