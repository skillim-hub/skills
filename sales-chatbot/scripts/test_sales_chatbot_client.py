from __future__ import annotations

import asyncio
import datetime as dt
import json
from decimal import Decimal

import pytest

import sales_chatbot_client as module


def make_client() -> module.SalesChatbotClient:
    return module.SalesChatbotClient(module.sample_catalog())


def test_format_ils_includes_symbol_and_vat():
    assert module.format_ils(249) == "₪249.00 כולל מע״מ"


def test_format_ils_without_vat_suffix():
    assert module.format_ils("249.5", include_vat=False) == "₪249.50"


def test_installments_cap_at_product_limit():
    text = module.installment_text(300, 10, 3)
    assert text is not None
    assert "עד 3 תשלומים" in text
    assert "₪100.00" in text


def test_installments_none_for_single_payment():
    assert module.installment_text(300, 1, 6) is None


def test_format_date_he_uses_dd_mm_yyyy_with_slashes():
    assert module.format_date_he(dt.date(2026, 6, 3)) == "03/06/2026"


def test_parse_context_date_dd_mm_yyyy_with_slashes():
    ctx = module.CustomerContext.from_mapping({"conversation_date": "03/06/2026"})
    assert ctx.conversation_date == dt.date(2026, 6, 3)


def test_parse_context_date_legacy_hyphen_still_supported():
    ctx = module.CustomerContext.from_mapping({"conversation_date": "03-06-2026"})
    assert ctx.conversation_date == dt.date(2026, 6, 3)


def test_classify_greeting():
    assert make_client().classify_intent("שלום, יש משהו לעסק?") == "greeting"


def test_classify_price():
    assert make_client().classify_intent("כמה עולה CRM בתשלומים?") == "price"


def test_classify_shipping():
    assert make_client().classify_intent("יש משלוח לחיפה?") == "shipping"


def test_classify_warranty():
    assert make_client().classify_intent("מה האחריות והחזרה?") == "warranty"


def test_classify_buy():
    assert make_client().classify_intent("אני רוצה להזמין עכשיו") == "buy"


def test_unsubscribe_handoff():
    response = make_client().recommend("נא להסיר אותי מהודעות")
    assert response.intent == "unsubscribe"
    assert response.handoff_required is True
    assert "הסר" in response.warnings[0]


def test_complaint_handoff():
    response = make_client().recommend("יש תקלה ואני מאוכזבת")
    assert response.intent == "complaint"
    assert response.handoff_required is True


def test_recommend_base_product_by_tag():
    response = make_client().recommend("מחפש CRM לעסק קטן", {"has_marketing_consent": True})
    assert response.offers[0].sku == "BASIC-CRM"


def test_cross_sell_items_are_added():
    response = make_client().recommend("מחפש CRM לעסק קטן", {"has_marketing_consent": True})
    relations = [offer.relation for offer in response.offers]
    assert "cross_sell" in relations


def test_upsell_respects_budget_when_allowed():
    response = make_client().recommend(
        "צריך CRM עם דוחות",
        {"has_marketing_consent": True, "budget_ils": "600"},
    )
    assert any(offer.sku == "PRO-CRM" for offer in response.offers)


def test_upsell_blocked_by_budget():
    response = make_client().recommend(
        "צריך CRM",
        {"has_marketing_consent": True, "budget_ils": "300"},
    )
    assert all(offer.sku != "PRO-CRM" for offer in response.offers)


def test_preferred_installments_appear_in_reply():
    response = make_client().recommend(
        "כמה עולה CRM?",
        {"has_marketing_consent": True, "preferred_installments": 3},
    )
    assert "תשלומים" in response.reply_he


def test_reply_does_not_duplicate_vat_suffix():
    response = make_client().recommend("כמה עולה CRM?", {"has_marketing_consent": True})
    assert "כולל מע״מ כולל מע״מ" not in response.reply_he


def test_marketing_consent_note_when_missing():
    response = make_client().recommend("כמה עולה CRM?")
    assert any("הסכמה" in note for note in response.compliance_notes)


@pytest.mark.asyncio
async def test_async_recommend_matches_sync_intent():
    client = make_client()
    sync = client.recommend("כמה עולה CRM?")
    async_response = await client.recommend_async("כמה עולה CRM?")
    assert async_response.intent == sync.intent


def test_async_method_works_with_asyncio_run():
    client = make_client()
    response = asyncio.run(client.recommend_async("כמה עולה CRM?"))
    assert response.intent == "price"


def test_make_quote_contains_quote_id_and_date():
    client = make_client()
    response = client.recommend("כמה עולה CRM?", {"has_marketing_consent": True})
    quote = client.make_quote(response)
    assert response.quote_id in quote
    assert "תאריך:" in quote


def test_validate_catalog_missing_field():
    errors = module.validate_catalog_data([{"sku": "X"}])
    assert errors
    assert "Missing required" in errors[0]


def test_validate_catalog_bad_cross_sell_reference():
    data = [{
        "sku": "A",
        "name_he": "מוצר",
        "category": "קטגוריה",
        "price_ils": "10",
        "cross_sell": ["MISSING"],
    }]
    errors = module.validate_catalog_data(data)
    assert any("cross_sell" in error for error in errors)


def test_duplicate_sku_rejected():
    raw = module.sample_catalog()
    raw.append(dict(raw[0]))
    errors = module.validate_catalog_data(raw)
    assert any("duplicate" in error.lower() for error in errors)


def test_out_of_stock_sets_warning():
    product = {
        "sku": "OOS",
        "name_he": "מוצר חסר",
        "category": "בדיקה",
        "price_ils": "10",
        "tags": ["חסר"],
        "stock": 0,
    }
    client = module.SalesChatbotClient([product])
    response = client.recommend("חסר")
    assert response.handoff_required is True
    assert response.warnings


def test_age_confirmation_sets_warning():
    product = {
        "sku": "AGE",
        "name_he": "מוצר מוגבל",
        "category": "בדיקה",
        "price_ils": "10",
        "tags": ["מוגבל"],
        "requires_age_confirmation": True,
    }
    client = module.SalesChatbotClient([product])
    response = client.recommend("מוגבל", {"has_marketing_consent": True})
    assert any("גיל" in warning for warning in response.warnings)


def test_to_dict_has_expected_keys_and_string_prices():
    response = make_client().recommend("כמה עולה CRM?")
    data = response.to_dict()
    assert {"intent", "reply_he", "offers", "warnings", "handoff_required", "compliance_notes", "quote_id"} <= set(data)
    assert isinstance(data["offers"][0]["price"], str)


def test_empty_catalog_rejected():
    with pytest.raises(ValueError, match="Catalog"):
        module.SalesChatbotClient([])


def test_from_json_loads_products(tmp_path):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps({"products": module.sample_catalog()}, ensure_ascii=False), encoding="utf-8")
    client = module.SalesChatbotClient.from_json(path)
    assert "BASIC-CRM" in client.catalog


def test_load_catalog_returns_product_objects(tmp_path):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(module.sample_catalog(), ensure_ascii=False), encoding="utf-8")
    products = module.load_catalog(path)
    assert products[0].sku == "BASIC-CRM"


def test_environment_defaults_validate_env(monkeypatch):
    monkeypatch.setenv("SALES_CHATBOT_API_KEY", "secret")
    monkeypatch.setenv("SALES_CHATBOT_CHANNEL", "web")
    data = module.load_environment_defaults("production")
    assert data["env"] == "production"
    assert data["api_key_present"] == "true"
    assert data["default_channel"] == "web"


def test_environment_defaults_reject_bad_env():
    with pytest.raises(ValueError, match="sandbox"):
        module.load_environment_defaults("staging")


def test_offer_line_to_dict_serializes_decimal():
    response = make_client().recommend("כמה עולה CRM?")
    data = module.offer_line_to_dict(response.offers[0])
    assert data["price"] == "249"


def test_package_import_reexports_client():
    from sales_chatbot import SalesChatbotClient

    assert SalesChatbotClient is module.SalesChatbotClient

def test_default_vat_rate_matches_web_validated_rate():
    assert module.DEFAULT_VAT_RATE == Decimal("0.18")


def test_importable_package_exports_client():
    import sales_chatbot

    assert sales_chatbot.SalesChatbotClient is module.SalesChatbotClient
    assert sales_chatbot.format_date_he is module.format_date_he

