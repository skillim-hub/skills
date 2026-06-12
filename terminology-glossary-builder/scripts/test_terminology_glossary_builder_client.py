from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from terminology_glossary_builder import (
    SOURCE_REGISTRY,
    GlossaryBuilder,
    GlossaryResult,
    GlossaryStore,
    build_glossary_json,
    build_sample_terms,
    detect_language,
    normalize_term,
    today_il,
    unique_preserve_order,
    validate_environment,
)
from terminology_glossary_builder.cli import app


def test_normalize_english_synonym() -> None:
    assert normalize_term("VAT") == "value added tax"


def test_normalize_hebrew_synonym() -> None:
    assert normalize_term("מע\"מ") == "value added tax"


def test_detect_language_english() -> None:
    assert detect_language("invoice") == "en"


def test_detect_language_hebrew() -> None:
    assert detect_language("חשבונית מס") == "he"


def test_detect_language_mixed() -> None:
    assert detect_language("VAT מע\"מ") == "mixed"


def test_unique_preserve_order_uses_normalized_keys() -> None:
    assert unique_preserve_order(["VAT", "מע\"מ", "Receipt"]) == ["VAT", "Receipt"]


def test_build_sample_terms_known_industry() -> None:
    assert "Withholding tax" in build_sample_terms("tax")


def test_build_sample_terms_unknown_industry_returns_general() -> None:
    assert build_sample_terms("unknown") == build_sample_terms("general")


def test_validate_environment_accepts_sandbox() -> None:
    assert validate_environment("sandbox") == "sandbox"


def test_validate_environment_rejects_invalid() -> None:
    with pytest.raises(ValueError):
        validate_environment("staging")


def test_source_registry_has_https_urls() -> None:
    assert all(source.url.startswith("https://") for source in SOURCE_REGISTRY.values())


def test_builder_validates_registry() -> None:
    assert GlossaryBuilder().validate_source_registry() == []


def test_parse_terms_from_comma_text() -> None:
    terms = GlossaryBuilder().parse_terms("VAT, receipt; withholding tax")
    assert terms == ["VAT", "receipt", "withholding tax"]


def test_resolve_known_term_has_sources() -> None:
    entry = GlossaryBuilder().resolve_term("VAT", industry="tax")
    assert entry.term_he == "מס ערך מוסף (מע\"מ)"
    assert entry.sources


def test_resolve_unknown_hebrew_term_marks_review() -> None:
    entry = GlossaryBuilder().resolve_term("דוגמה לא מוכרת", industry="consumer")
    assert entry.term_en == "Review translation"
    assert entry.warning_he


def test_sources_for_industry_fallback() -> None:
    sources = GlossaryBuilder().sources_for_industry("unknown")
    assert [source.key for source in sources] == ["govil"]


def test_build_glossary_sorts_terms() -> None:
    result = GlossaryBuilder().build_glossary(["Receipt", "VAT"], industry="tax")
    assert [entry.term_en for entry in result.entries] == ["Receipt", "Value Added Tax (VAT)"]


def test_build_glossary_max_terms() -> None:
    result = GlossaryBuilder().build_glossary(["VAT", "Receipt"], max_terms=1, sort_terms=False)
    assert result.entry_count == 1


def test_build_glossary_max_terms_rejects_zero() -> None:
    with pytest.raises(ValueError):
        GlossaryBuilder().build_glossary(["VAT"], max_terms=0)


@pytest.mark.asyncio
async def test_async_build_glossary() -> None:
    result = await GlossaryBuilder().abuild_glossary(["VAT"], industry="tax")
    assert result.entry_count == 1


def test_to_json_round_trip() -> None:
    builder = GlossaryBuilder()
    result = builder.build_glossary(["VAT"], industry="tax")
    payload = json.loads(builder.to_json(result))
    restored = GlossaryResult.from_dict(payload)
    assert restored.entries[0].term_en == "Value Added Tax (VAT)"


def test_to_markdown_english_contains_sources() -> None:
    markdown = GlossaryBuilder().to_markdown(GlossaryBuilder().build_glossary(["VAT"], industry="tax"))
    assert "Israel Tax Authority" in markdown
    assert "| English term | Hebrew term |" in markdown


def test_to_markdown_hebrew_contains_local_date_label() -> None:
    builder = GlossaryBuilder()
    markdown = builder.to_markdown(builder.build_glossary(["VAT"], industry="tax"), localization="he")
    assert "תאריך יצירה:" in markdown
    assert "| מונח בעברית |" in markdown


def test_to_csv_has_header_and_source_key() -> None:
    csv_text = GlossaryBuilder().to_csv(GlossaryBuilder().build_glossary(["VAT"], industry="tax"))
    assert "term_en,term_he" in csv_text
    assert "tax_authority" in csv_text


def test_quality_checks_warn_for_unknown_term() -> None:
    result = GlossaryBuilder().build_glossary(["Unknown specialist term"], industry="privacy")
    assert any("professional review" in warning for warning in result.warnings)


def test_store_create_get_and_list(tmp_path: Path) -> None:
    store_path = tmp_path / "store.json"
    builder = GlossaryBuilder()
    result = builder.build_glossary(["VAT"], industry="tax")
    response = GlossaryStore(store_path).create(result)
    assert response["id"] == result.id
    restored = GlossaryStore(store_path).get(result.id)
    assert restored.entry_count == 1
    assert GlossaryStore(store_path).list()[0]["id"] == result.id


def test_builder_create_and_export(tmp_path: Path) -> None:
    store_path = tmp_path / "store.json"
    builder = GlossaryBuilder()
    response = builder.create_glossary(["VAT"], store_path=store_path, industry="tax")
    exported = builder.export_glossary(response["id"], store_path=store_path, output_format="json")
    assert json.loads(exported)["id"] == response["id"]


def test_export_rejects_bad_format(tmp_path: Path) -> None:
    store_path = tmp_path / "store.json"
    builder = GlossaryBuilder()
    response = builder.create_glossary(["VAT"], store_path=store_path)
    with pytest.raises(ValueError):
        builder.export_glossary(response["id"], store_path=store_path, output_format="xml")  # type: ignore[arg-type]


def test_store_missing_id_raises(tmp_path: Path) -> None:
    with pytest.raises(KeyError):
        GlossaryStore(tmp_path / "store.json").get("missing")


def test_build_glossary_json_helper() -> None:
    payload = json.loads(build_glossary_json(["VAT"], industry="tax"))
    assert payload["entry_count"] == 1


def test_today_il_format() -> None:
    assert re.match(r"\d{2}/\d{2}/\d{4}", today_il())


def test_cli_create_then_export_chains_id(tmp_path: Path) -> None:
    runner = CliRunner()
    store_path = tmp_path / "store.json"
    create_result = runner.invoke(app, ["create", "VAT", "Receipt", "--industry", "tax", "--store", str(store_path)])
    assert create_result.exit_code == 0, create_result.output
    glossary_id = json.loads(create_result.output)["id"]
    export_result = runner.invoke(app, ["export", glossary_id, "--store", str(store_path), "--format", "json"])
    assert export_result.exit_code == 0, export_result.output
    assert json.loads(export_result.output)["id"] == glossary_id


def test_cli_build_json() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["build", "VAT", "--industry", "tax", "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["entries"][0]["term_he"] == "מס ערך מוסף (מע\"מ)"


def test_cli_validate() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "Validation passed" in result.output


def test_cli_sources_json() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["sources", "--json"])
    assert result.exit_code == 0
    assert "tax_authority" in json.loads(result.output)
