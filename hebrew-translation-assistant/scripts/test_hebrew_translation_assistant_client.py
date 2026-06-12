from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from hebrew_translation_assistant import (
    Direction,
    Environment,
    HebrewTranslationAssistant,
    HelperError,
    Register,
    TranslationRequest,
    contains_nikud,
    detect_direction,
    get_reference_facts,
    localize_date,
    localize_dates_in_text,
)


@pytest.fixture()
def client(tmp_path: Path) -> HebrewTranslationAssistant:
    return HebrewTranslationAssistant(storage_dir=tmp_path)


def test_detect_direction_english() -> None:
    assert detect_direction("Refund within 7 business days") == Direction.EN_TO_HE


def test_detect_direction_hebrew() -> None:
    assert detect_direction("החזר כספי בתוך 7 ימי עסקים") == Direction.HE_TO_EN


def test_detect_direction_mixed_prefers_hebrew_when_dominant() -> None:
    assert detect_direction("נא לשלוח invoice היום") == Direction.HE_TO_EN


def test_empty_text_raises() -> None:
    with pytest.raises(HelperError) as exc:
        detect_direction("   ")
    assert exc.value.code == "EMPTY_TEXT"


def test_localize_iso_date() -> None:
    assert localize_date("2026-03-05") == "05/03/2026"


def test_localize_slash_date_passthrough() -> None:
    assert localize_date("05/03/2026") == "05/03/2026"


def test_localize_date_object() -> None:
    assert localize_date(date(2026, 3, 5)) == "05/03/2026"


def test_localize_dates_inside_text() -> None:
    assert "05/03/2026" in localize_dates_in_text("Pay by 2026-03-05.")


def test_localize_bad_date_raises() -> None:
    with pytest.raises(HelperError) as exc:
        localize_date("03-05-2026")
    assert exc.value.code == "DATE_PARSE"


def test_en_to_he_invoice_terms(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text(
        "Please issue a tax invoice/receipt for ₪1,250 plus VAT.",
        direction=Direction.EN_TO_HE,
        register=Register.ACCOUNTING,
    )
    assert "חשבונית מס/קבלה" in result.translation
    assert "בתוספת מע״מ" in result.translation
    assert any("Accounting-sensitive" in warning for warning in result.warnings)


def test_en_to_he_refund_business_days(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text("Refund within 7 business days")
    assert "החזר כספי" in result.translation
    assert "7" in result.translation
    assert "ימי עסקים" in result.translation


def test_he_to_en_refund(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text("החזר כספי בתוך 7 ימי עסקים", direction=Direction.HE_TO_EN)
    assert "refund" in result.translation
    assert "business days" in result.translation
    assert result.quality_checks["numbers_preserved"]


def test_positive_idiom(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text(
        "השירות היה חבל על הזמן.",
        direction=Direction.HE_TO_EN,
        register=Register.CASUAL,
    )
    assert result.detected_terms["חבל על הזמן"] == "excellent"


def test_negative_idiom(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text("חבל על הזמן, לא שווה להתעסק עם זה.", direction=Direction.HE_TO_EN)
    assert result.detected_terms["חבל על הזמן"] == "not worth the time"


def test_al_hapanim_idiom(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text(
        "המוצר הגיע על הפנים ואני רוצה החזר כספי.",
        direction=Direction.HE_TO_EN,
        register=Register.SUPPORT,
    )
    assert "very poor" in result.translation
    assert "refund" in result.translation


def test_casual_sababa(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text("סבבה, נטפל בזה היום.", direction=Direction.HE_TO_EN, register=Register.CASUAL)
    assert result.detected_terms["סבבה"] == "Sounds good"


def test_business_sababa(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text(
        "סבבה, נטפל בזה היום.",
        direction=Direction.HE_TO_EN,
        register=Register.BUSINESS,
    )
    assert result.detected_terms["סבבה"] == "No problem"


def test_glossary_lookup_english(client: HebrewTranslationAssistant) -> None:
    matches = client.glossary_lookup("withholding tax")
    assert "withholding tax" in matches


def test_glossary_lookup_hebrew(client: HebrewTranslationAssistant) -> None:
    matches = client.glossary_lookup("חשבונית מס")
    assert "חשבונית מס" in matches


def test_glossary_missing_raises(client: HebrewTranslationAssistant) -> None:
    with pytest.raises(HelperError) as exc:
        client.glossary_lookup("not-a-known-term")
    assert exc.value.code == "TERM_NOT_FOUND"


def test_url_and_email_preserved(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text(
        "Send the invoice to billing@example.test and visit https://example.test/invoice.",
        direction=Direction.EN_TO_HE,
    )
    assert "billing@example.test" in result.translation
    assert "https://example.test/invoice" in result.translation


def test_preserve_terms(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text("Please translate the checkout copy.", preserve_terms=("Starter Plus",))
    assert "Starter Plus" in result.translation


def test_to_json_uses_hebrew(client: HebrewTranslationAssistant) -> None:
    result = client.translate_text("Please send the receipt.", direction=Direction.EN_TO_HE)
    payload = json.loads(result.to_json())
    assert payload["direction"] == "en-to-he"
    assert "קבלה" in payload["translation"]


def test_review_text_contains_checks(client: HebrewTranslationAssistant) -> None:
    review = client.review_text("נא לשלוח חשבונית מס/קבלה", register=Register.ACCOUNTING)
    assert review["direction"] == "he-to-en"
    assert review["quality_checks"]["no_nikud"]


def test_export_glossary(client: HebrewTranslationAssistant) -> None:
    glossary = client.export_glossary()
    assert "invoice" in glossary["en_to_he"]
    assert "חשבונית" in glossary["he_to_en"]


def test_validate_text_detects_nikud(client: HebrewTranslationAssistant) -> None:
    assert contains_nikud("שָׁלוֹם")
    assert client.validate_text("שָׁלוֹם")["contains_nikud"]


def test_create_and_get_request(client: HebrewTranslationAssistant) -> None:
    job = client.create_request("Refund within 7 business days", environment=Environment.SANDBOX)
    fetched = client.get_request(job.id)
    assert fetched["id"] == job.id
    assert fetched["environment"] == "sandbox"
    assert "החזר כספי" in fetched["result"]["translation"]


def test_list_requests(client: HebrewTranslationAssistant) -> None:
    client.create_request("Please send the invoice.")
    client.create_request("Refund within 7 business days.")
    assert len(client.list_requests()) == 2


@pytest.mark.asyncio
async def test_async_translate(client: HebrewTranslationAssistant) -> None:
    result = await client.atranslate_text("החזר כספי", direction=Direction.HE_TO_EN)
    assert "refund" in result.translation


@pytest.mark.asyncio
async def test_async_create_request(client: HebrewTranslationAssistant) -> None:
    job = await client.acreate_request("Please send the invoice.", environment="production")
    assert job.environment == Environment.PRODUCTION


def test_translation_request_object(client: HebrewTranslationAssistant) -> None:
    request = TranslationRequest(text="נא לשלוח חשבונית", direction=Direction.HE_TO_EN, register=Register.BUSINESS)
    result = client.translate_request(request)
    assert "invoice" in result.translation


def test_invalid_direction_raises(client: HebrewTranslationAssistant) -> None:
    with pytest.raises(HelperError) as exc:
        client.translate_text("text", direction="sideways")
    assert exc.value.code == "INVALID_DIRECTION"


def test_invalid_register_raises(client: HebrewTranslationAssistant) -> None:
    with pytest.raises(HelperError) as exc:
        client.translate_text("text", register="poetic")
    assert exc.value.code == "INVALID_REGISTER"


def test_invalid_environment_raises(client: HebrewTranslationAssistant) -> None:
    with pytest.raises(HelperError) as exc:
        client.create_request("text", environment="qa")
    assert exc.value.code == "INVALID_ENVIRONMENT"


def test_cli_translate_json(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["HEBREW_TRANSLATION_ASSISTANT_HOME"] = str(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "hebrew_translation_assistant.cli",
            "translate",
            "Refund within 7 business days",
            "--json",
        ],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["direction"] == "en-to-he"
    assert "החזר כספי" in payload["translation"]


def test_cli_create_show_chain(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["HEBREW_TRANSLATION_ASSISTANT_HOME"] = str(tmp_path)
    cwd = Path(__file__).resolve().parents[1]
    create_proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "hebrew_translation_assistant.cli",
            "create",
            "Please send the tax invoice.",
            "--env",
            "sandbox",
        ],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    created = json.loads(create_proc.stdout)
    show_proc = subprocess.run(
        [sys.executable, "-m", "hebrew_translation_assistant.cli", "show", created["id"]],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    shown = json.loads(show_proc.stdout)
    assert shown["id"] == created["id"]
    assert "חשבונית מס" in shown["result"]["translation"]


def test_reference_facts_are_current_for_release(client: HebrewTranslationAssistant) -> None:
    facts = client.reference_facts()
    assert facts["vat_rate_percent"] == "18"
    assert facts["invoice_allocation_threshold_before_vat"] == "5,000 ₪"
    assert facts == get_reference_facts()


def test_cli_facts_outputs_reference_payload(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["HEBREW_TRANSLATION_ASSISTANT_HOME"] = str(tmp_path)
    proc = subprocess.run(
        [sys.executable, "-m", "hebrew_translation_assistant.cli", "facts"],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["vat_rate_percent"] == "18"
    assert payload["invoice_allocation_threshold_effective_date"] == "01/06/2026"
